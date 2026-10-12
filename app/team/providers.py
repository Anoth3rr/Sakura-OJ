from __future__ import annotations

import json
import gzip
import re
import sqlite3
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from .config import settings
from . import repository


class ProviderError(RuntimeError):
    pass


def _get_json(url: str) -> Any:
    request = Request(url, headers={"User-Agent": "Sakura-Team/0.1 (+local)"})
    try:
        with urlopen(request, timeout=settings.request_timeout_seconds) as response:
            raw = response.read()
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise ProviderError(str(exc)) from exc
    try:
        if raw.startswith(b"\x1f\x8b"):
            raw = gzip.decompress(raw)
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, OSError, EOFError) as exc:
        raise ProviderError("平台返回了无法解析的 JSON") from exc


def sync_codeforces(member: dict[str, Any]) -> dict[str, Any]:
    handle = str(member.get("cf_handle") or "").strip()
    if not handle:
        raise ProviderError("未配置 Codeforces handle")
    encoded = quote(handle, safe="")
    info_payload = _get_json(f"https://codeforces.com/api/user.info?handles={encoded}")
    if info_payload.get("status") != "OK" or not info_payload.get("result"):
        raise ProviderError(str(info_payload.get("comment") or "Codeforces 用户不存在"))
    info = info_payload["result"][0]
    rating = int(info.get("rating") or 0)
    peak = int(info.get("maxRating") or rating)
    history_payload = _get_json(f"https://codeforces.com/api/user.rating?handle={encoded}")
    history = history_payload.get("result") if history_payload.get("status") == "OK" else []
    for item in history or []:
        contest_time = datetime.fromtimestamp(int(item.get("ratingUpdateTimeSeconds") or 0), timezone.utc).isoformat()
        repository.upsert_contest_result(
            member_id=int(member["id"]),
            platform="codeforces",
            external_id=str(item.get("contestId") or item.get("contestName") or "cf"),
            name=str(item.get("contestName") or "Codeforces Contest"),
            contest_time=contest_time,
            participant_count=max(100, int(item.get("rank") or 1) * 2),
            rank=int(item.get("rank") or 0),
            old_rating=int(item.get("oldRating") or 0),
            new_rating=int(item.get("newRating") or 0),
            rating_change=int(item.get("newRating") or 0) - int(item.get("oldRating") or 0),
            source="codeforces",
        )
    submission_count = 0
    try:
        submission_payload = _get_json(f"https://codeforces.com/api/user.status?handle={encoded}&from=1&count=500")
        submissions = submission_payload.get("result") if submission_payload.get("status") == "OK" else []
        for item in submissions or []:
            problem = item.get("problem") or {}
            verdict = _cf_verdict(item.get("verdict"))
            created = datetime.fromtimestamp(int(item.get("creationTimeSeconds") or 0), timezone.utc).isoformat()
            repository.upsert_submission(
                {
                    "id": f"cf-{item.get('id')}",
                    "external_id": str(item.get("id")),
                    "member_id": int(member["id"]),
                    "platform": "codeforces",
                    "problem_id": f"{item.get('contestId', '')}{problem.get('index', '')}",
                    "problem_name": str(problem.get("name") or "Codeforces Problem"),
                    "verdict": verdict,
                    "language": str(item.get("programmingLanguage") or ""),
                    "submitted_at": created,
                    "runtime_ms": item.get("timeConsumedMillis"),
                    "memory_kb": round(int(item.get("memoryConsumedBytes") or 0) / 1024) if item.get("memoryConsumedBytes") else None,
                    "source": "codeforces",
                    "url": f"https://codeforces.com/contest/{item.get('contestId')}/submission/{item.get('id')}",
                    "tags": problem.get("tags") or [],
                }
            )
            submission_count += 1
    except ProviderError:
        # user.status is a useful enhancement, but rating sync should remain
        # available when the endpoint is rate-limited.
        pass
    repository.upsert_platform_rating(
        member_id=int(member["id"]),
        platform="codeforces",
        rating=rating,
        peak_rating=peak,
        rank_title=str(info.get("rank") or "未定级"),
        contest_count=len(history or []),
        rating_change=(int(history[-1].get("newRating") or 0) - int(history[-1].get("oldRating") or 0)) if history else 0,
        source="codeforces",
    )
    repository.recompute_member_results(int(member["id"]), "codeforces")
    return {"platform": "codeforces", "handle": handle, "rating": rating, "peak_rating": peak, "contests": len(history or []), "submissions": submission_count}


def _atcoder_history(handle: str) -> list[dict[str, Any]]:
    encoded = quote(handle, safe="")
    payload = _get_json(f"https://atcoder.jp/users/{encoded}/history/json")
    if not isinstance(payload, list):
        raise ProviderError("AtCoder history 返回格式异常")
    return payload


def sync_atcoder(member: dict[str, Any]) -> dict[str, Any]:
    handle = str(member.get("atcoder_handle") or "").strip()
    if not handle:
        raise ProviderError("未配置 AtCoder handle")
    history = _atcoder_history(handle)
    rated = [item for item in history if item.get("IsRated", True) is not False]
    if not rated:
        raise ProviderError("AtCoder 没有可用的 rated 比赛记录")
    for item in rated:
        contest_time = _parse_atcoder_time(item.get("EndTime"))
        rank = _to_int(item.get("Place"), 0)
        old_rating = _to_int(item.get("OldRating"), 0)
        new_rating = _to_int(item.get("NewRating"), 0)
        repository.upsert_contest_result(
            member_id=int(member["id"]),
            platform="atcoder",
            external_id=str(item.get("ContestScreenName") or item.get("ContestName") or contest_time),
            name=str(item.get("ContestName") or "AtCoder Contest"),
            contest_time=contest_time,
            participant_count=max(100, rank * 2),
            rank=rank,
            old_rating=old_rating,
            new_rating=new_rating,
            source="atcoder",
        )
    current = _to_int(rated[-1].get("NewRating"), 0)
    peak = max(_to_int(item.get("NewRating"), 0) for item in rated)
    change = current - _to_int(rated[-1].get("OldRating"), current)
    repository.upsert_platform_rating(
        member_id=int(member["id"]),
        platform="atcoder",
        rating=current,
        peak_rating=peak,
        rank_title=_atcoder_rank(current),
        contest_count=len(rated),
        rating_change=change,
        source="atcoder",
    )
    repository.recompute_member_results(int(member["id"]), "atcoder")
    return {"platform": "atcoder", "handle": handle, "rating": current, "peak_rating": peak, "contests": len(rated)}


def sync_nowcoder(member: dict[str, Any]) -> dict[str, Any]:
    uid = str(member.get("nowcoder_uid") or "").strip()
    if not uid:
        raise ProviderError("未配置牛客 UID，请在队员档案中填写个人主页 URL 中的数字 ID")
    if not re.fullmatch(r"[1-9][0-9]{0,18}", uid):
        raise ProviderError("牛客 UID 必须是 1～19 位正整数，不能填写昵称")
    if settings.nowcoder_api_url:
        separator = "&" if "?" in settings.nowcoder_api_url else "?"
        payload = _get_json(f"{settings.nowcoder_api_url}{separator}{urlencode({'uid': uid})}")
        if isinstance(payload, dict) and payload.get("code", 0) != 0:
            raise ProviderError(f"牛客接口失败：{payload.get('msg') or payload.get('message') or payload['code']}")
        normalized = _normalize_nowcoder(payload)
    else:
        normalized = _fetch_nowcoder_official(uid)
    snapshot = _nowcoder_snapshot(normalized)
    try:
        repository.save_nowcoder_sync(int(member["id"]), uid, snapshot)
    except ValueError as exc:
        raise ProviderError(str(exc)) from exc
    return {"platform": "nowcoder", "uid": uid, "nickname": snapshot.get("nickname", ""),
            "rating": snapshot["rating"], "peak_rating": snapshot["peak_rating"], "contests": len(snapshot["history"])}


def _nowcoder_data(endpoint: str, uid: str) -> Any:
    payload = _get_json(f"https://ac.nowcoder.com/acm/contest/{endpoint}?{urlencode({'uid': uid})}")
    if not isinstance(payload, dict) or "code" not in payload:
        raise ProviderError("牛客返回格式异常，请稍后重试")
    if payload["code"] != 0:
        raise ProviderError(f"牛客接口失败：{payload.get('msg') or payload['code']}")
    if "data" not in payload:
        raise ProviderError("牛客返回格式异常，请稍后重试")
    return payload["data"]


def _nowcoder_int(value: Any, field: str, minimum: int | None = None) -> int:
    try:
        number = float(value)
        result = int(number)
        if isinstance(value, bool) or number != result or (minimum is not None and result < minimum):
            raise ValueError
        return result
    except (TypeError, ValueError, OverflowError) as exc:
        raise ProviderError(f"牛客返回的 {field} 缺失或格式异常") from exc


def _fetch_nowcoder_official(uid: str) -> dict[str, Any]:
    # Same public endpoints as the contest profile page. rating-history returns
    # the complete personal (or team, for a team UID) rated series, without paging.
    basic = _nowcoder_data("rating-basic", uid)
    if not isinstance(basic, dict) or str(basic.get("uid")) != uid:
        raise ProviderError("无法获取该 UID 的牛客竞赛资料，请检查账号是否存在并已开通竞赛主页")
    rated_count = _nowcoder_int(basic.get("ratedCount"), "ratedCount", 0)
    rating = 0 if basic.get("hasRating") is False else _nowcoder_int(basic.get("rating"), "rating", 0)
    history = _nowcoder_data("rating-history", uid)
    if not isinstance(history, list) or len(history) != rated_count:
        raise ProviderError("牛客 Rating 历史不完整，请稍后重新同步")
    normalized_history = []
    for item in history:
        if not isinstance(item, dict):
            raise ProviderError("牛客 Rating 历史格式异常")
        new_rating = _nowcoder_int(item.get("rating"), "history.rating", 0)
        change = _nowcoder_int(item.get("changeValue"), "history.changeValue")
        normalized_history.append({
            "contest_id": str(_nowcoder_int(item.get("contestId"), "contestId", 1)),
            "name": item.get("contestName"), "time": item.get("time"),
            "rank": item.get("rank"), "old_rating": new_rating - change, "new_rating": new_rating,
        })
    return {"rating": rating, "nickname": str(basic.get("nickname") or ""),
            "contest_count": rated_count, "rank_title": "未定级" if basic.get("hasRating") is False else "",
            "history": normalized_history, "official": True}


def _nowcoder_snapshot(normalized: dict[str, Any]) -> dict[str, Any]:
    rating = _nowcoder_int(normalized.get("rating"), "rating", 0)
    history = []
    seen = set()
    for item in normalized.get("history") or []:
        contest_id = str(item.get("contest_id") or item.get("id") or "")
        if not contest_id or contest_id in seen or not item.get("name"):
            raise ProviderError("牛客比赛记录缺少 ID / 名称，或存在重复记录")
        seen.add(contest_id)
        try:
            raw_time = item["time"]
            if isinstance(raw_time, (int, float)):
                date = datetime.fromtimestamp(raw_time / 1000, timezone.utc)
            else:
                date = datetime.fromisoformat(str(raw_time).replace("Z", "+00:00"))
                if date.tzinfo is None:
                    raise ValueError
            contest_time = date.astimezone(timezone.utc).isoformat()
        except (KeyError, TypeError, ValueError, OverflowError, OSError) as exc:
            raise ProviderError("牛客比赛时间格式异常，需要毫秒时间戳或含时区的 ISO 时间") from exc
        history.append({
            "external_id": contest_id, "name": str(item["name"]), "contest_time": contest_time,
            "participant_count": _nowcoder_int(item.get("participants") or 0, "participants", 0),
            "rank": _nowcoder_int(item.get("rank"), "rank", 1),
            "old_rating": _nowcoder_int(item["old_rating"], "old_rating") if item.get("old_rating") is not None else None,
            "new_rating": _nowcoder_int(item["new_rating"], "new_rating", 0) if item.get("new_rating") is not None else None,
            "score": item.get("score"), "max_score": item.get("max_score"), "solved": item.get("solved"),
        })
    history.sort(key=lambda item: (item["contest_time"], item["external_id"]))
    if normalized.get("official") and history and history[-1]["new_rating"] != rating:
        raise ProviderError("牛客当前 Rating 与历史记录暂不一致，请稍后重新同步")
    peak = max([rating] + [item["new_rating"] for item in history if item["new_rating"] is not None])
    change = 0
    if history and history[-1]["old_rating"] is not None and history[-1]["new_rating"] is not None:
        change = history[-1]["new_rating"] - history[-1]["old_rating"]
    reported_peak = normalized.get("peak_rating")
    if reported_peak is not None:
        peak = max(peak, _nowcoder_int(reported_peak, "peak_rating", 0))
    return {"rating": rating, "peak_rating": peak,
            "rating_change": _nowcoder_int(normalized["rating_change"], "rating_change") if normalized.get("rating_change") is not None else change,
            "rank_title": str(normalized.get("rank_title") or ""),
            "contest_count": _nowcoder_int(normalized["contest_count"], "contest_count", 0) if normalized.get("contest_count") is not None else len(history),
            "nickname": str(normalized.get("nickname") or "")[:80], "history": history}


def _normalize_nowcoder(payload: Any) -> dict[str, Any]:
    def first(item: dict[str, Any], *keys: str) -> Any:
        return next((item[key] for key in keys if item.get(key) is not None), None)
    if isinstance(payload, dict):
        for key in ("data", "result", "user", "profile"):
            if isinstance(payload.get(key), dict):
                merged = dict(payload)
                merged.update(payload[key])
                payload = merged
                break
    if not isinstance(payload, dict):
        return {}
    history = payload.get("history") or payload.get("contests") or payload.get("contest_history") or []
    if isinstance(history, dict):
        history = history.get("items") or history.get("list") or []
    if not isinstance(history, list):
        raise ProviderError("牛客 Rating 历史格式异常")
    normalized_history = []
    for item in history:
        if not isinstance(item, dict):
            raise ProviderError("牛客 Rating 历史格式异常")
        normalized_history.append(
            {
                "id": item.get("id") or item.get("contestId"),
                "contest_id": item.get("contest_id") or item.get("contestId"),
                "name": item.get("name") or item.get("contestName"),
                "time": item.get("time") or item.get("contestTime") or item.get("date"),
                "rank": item.get("rank") or item.get("place"),
                "participants": item.get("participants") or item.get("total"),
                "score": item.get("score"),
                "max_score": item.get("max_score") or item.get("maxScore"),
                "solved": item.get("solved") or item.get("solvedCount"),
                "old_rating": first(item, "old_rating", "oldRating"),
                "new_rating": first(item, "new_rating", "newRating"),
            }
        )
    return {
        "rating": first(payload, "rating", "nowcoder_rating", "score"),
        "peak_rating": first(payload, "peak_rating", "maxRating", "highest_rating"),
        "rank_title": payload.get("rank_title") or payload.get("rank") or payload.get("level"),
        "contest_count": first(payload, "contest_count", "contestCount"),
        "rating_change": first(payload, "rating_change", "ratingChange"),
        "nickname": payload.get("nickname"),
        "history": normalized_history,
    }


def sync_member(member: dict[str, Any], platforms: list[str]) -> dict[str, Any]:
    handlers = {"codeforces": sync_codeforces, "atcoder": sync_atcoder, "nowcoder": sync_nowcoder}
    synced: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for platform in platforms:
        handler = handlers.get(platform)
        if handler is None:
            errors.append({"platform": platform, "message": "不支持的平台"})
            continue
        try:
            synced.append(handler(member))
        except ProviderError as exc:
            errors.append({"platform": platform, "message": str(exc)})
        except Exception as exc:  # keep one provider failure from aborting the whole sync
            errors.append({"platform": platform, "message": f"同步失败：{exc}"})
    return {"member_id": member["id"], "synced": synced, "errors": errors}


def sync_all(platforms: list[str] | None = None) -> dict[str, Any]:
    platforms = platforms or ["codeforces", "atcoder", "nowcoder"]
    members = repository.list_members(status="active")
    account_fields = {"codeforces": "cf_handle", "atcoder": "atcoder_handle", "nowcoder": "nowcoder_uid"}
    results = [sync_member(member, [platform for platform in platforms if member.get(account_fields.get(platform, ""))])
               for member in members]
    return {"members": len(members), "results": results}


def import_oj_sqlite(*, member_id: int | None = None) -> dict[str, Any]:
    from .config import settings

    from ..config import settings as oj_settings
    if settings.oj_database_path.resolve() == oj_settings.database_path.resolve() and member_id is None:
        from .integration import sync_all_local
        return sync_all_local()
    path = settings.oj_database_path
    if not path.exists():
        raise ProviderError(f"找不到 OJ 数据库：{path}")
    try:
        with repository.connection(path) as conn:
            rows = conn.execute(
                """
                SELECT s.id, s.problem_id, p.slug AS problem_slug, p.title AS problem_name,
                       s.verdict, s.language, s.created_at, s.runtime_ms, s.memory_kb,
                       length(s.source_code) AS code_length
                FROM submissions s LEFT JOIN problems p ON p.id = s.problem_id
                ORDER BY s.created_at DESC LIMIT 2000
                """
            ).fetchall()
    except sqlite3.Error as exc:  # type: ignore[name-defined]
        raise ProviderError(f"读取 OJ 数据库失败：{exc}") from exc
    imported = 0
    for row in rows:
        repository.upsert_submission(
            {
                "id": f"oj-{row['id']}",
                "external_id": str(row["id"]),
                "member_id": member_id,
                "platform": "oj",
                "problem_id": row["problem_slug"] or row["problem_id"] or "",
                "problem_name": row["problem_name"] or "未命名题目",
                "verdict": row["verdict"],
                "language": row["language"],
                "submitted_at": row["created_at"],
                "runtime_ms": row["runtime_ms"],
                "memory_kb": row["memory_kb"],
                "code_length": row["code_length"],
                "source": "sakura-oj",
                "url": f"{settings.oj_base_url}/#submission/{row['id']}" if settings.oj_base_url else "",
            }
        )
        imported += 1
    return {"imported": imported, "source": str(path)}


def import_oj_http(*, member_id: int | None = None) -> dict[str, Any]:
    if not settings.oj_base_url:
        return import_oj_sqlite(member_id=member_id)
    payload = _get_json(f"{settings.oj_base_url}/api/submissions?limit=200")
    items = payload.get("items") if isinstance(payload, dict) else payload
    if not isinstance(items, list):
        raise ProviderError("OJ submissions 返回格式异常")
    imported = 0
    for item in items:
        repository.upsert_submission(
            {
                "id": f"oj-{item.get('id')}",
                "external_id": str(item.get("id")),
                "member_id": member_id,
                "platform": "oj",
                "problem_id": item.get("problem_slug") or item.get("problem_id"),
                "problem_name": item.get("problem_slug") or "未命名题目",
                "verdict": item.get("verdict"),
                "language": item.get("language"),
                "submitted_at": item.get("created_at"),
                "source": "sakura-oj",
                "url": f"{settings.oj_base_url}/#submission/{item.get('id')}",
            }
        )
        imported += 1
    return {"imported": imported, "source": settings.oj_base_url}


def _to_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _cf_verdict(value: Any) -> str:
    mapping = {
        "OK": "ACCEPTED",
        "WRONG_ANSWER": "WRONG_ANSWER",
        "TIME_LIMIT_EXCEEDED": "TIME_LIMIT_EXCEEDED",
        "MEMORY_LIMIT_EXCEEDED": "MEMORY_LIMIT_EXCEEDED",
        "RUNTIME_ERROR": "RUNTIME_ERROR",
        "COMPILATION_ERROR": "COMPILE_ERROR",
        "TESTING": "PENDING",
    }
    raw = str(value or "PENDING").upper()
    return mapping.get(raw, raw)


def _parse_atcoder_time(value: Any) -> str:
    if isinstance(value, str):
        text = value.strip()
        if text:
            try:
                return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc).isoformat()
            except ValueError:
                return text
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, timezone.utc).isoformat()
    return datetime.now(timezone.utc).isoformat()


def _atcoder_rank(rating: int) -> str:
    if rating >= 2800:
        return "红"
    if rating >= 2400:
        return "橙"
    if rating >= 2000:
        return "黄"
    if rating >= 1600:
        return "蓝"
    if rating >= 1200:
        return "青"
    return "灰"


