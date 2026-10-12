from __future__ import annotations

import json
import sqlite3
from contextlib import nullcontext
from datetime import datetime, timedelta, timezone
from typing import Any

from .analytics import build_profile, recompute_fit_rows
from .db import connection, utc_now


def _row(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row is not None else None


def _rows(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]


def count_members() -> int:
    with connection() as conn:
        return int(conn.execute("SELECT COUNT(*) FROM members").fetchone()[0])


def create_member(data: dict[str, Any]) -> dict[str, Any]:
    now = utc_now()
    fields = {
        "name": str(data.get("name", "")).strip(),
        "student_id": str(data.get("student_id", "")).strip(),
        "team_group": str(data.get("team_group", "算法组")).strip() or "算法组",
        "status": str(data.get("status", "active")).strip() or "active",
        "color": str(data.get("color", "#2dd4bf")).strip() or "#2dd4bf",
        "cf_handle": str(data.get("cf_handle", "")).strip(),
        "atcoder_handle": str(data.get("atcoder_handle", "")).strip(),
        "nowcoder_handle": str(data.get("nowcoder_handle", "")).strip(),
        "nowcoder_uid": str(data.get("nowcoder_uid", "")).strip(),
        "oj_username": str(data.get("oj_username", "")).strip(),
        "email": str(data.get("email", "")).strip(),
        "note": str(data.get("note", "")).strip(),
    }
    if not fields["name"]:
        raise ValueError("成员姓名不能为空")
    with connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO members
              (name, student_id, team_group, status, color, cf_handle, atcoder_handle,
               nowcoder_handle, nowcoder_uid, oj_username, email, note, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (*fields.values(), now, now),
        )
        member_id = int(cursor.lastrowid)
    return get_member(member_id)  # type: ignore[return-value]


def update_member(member_id: int, data: dict[str, Any]) -> dict[str, Any] | None:
    allowed = {
        "name",
        "student_id",
        "team_group",
        "status",
        "color",
        "cf_handle",
        "atcoder_handle",
        "nowcoder_handle",
        "nowcoder_uid",
        "oj_username",
        "email",
        "note",
    }
    updates = [(key, value) for key, value in data.items() if key in allowed and value is not None]
    if not updates:
        return get_member(member_id)
    assignments = ", ".join(f"{key} = ?" for key, _ in updates)
    with connection() as conn:
        conn.execute("BEGIN IMMEDIATE")
        previous = conn.execute("SELECT nowcoder_uid FROM members WHERE id = ?", (member_id,)).fetchone()
        cursor = conn.execute(
            f"UPDATE members SET {assignments}, updated_at = ? WHERE id = ?",
            [value for _, value in updates] + [utc_now(), member_id],
        )
        if cursor.rowcount == 0:
            return None
        if data.get("nowcoder_uid") is not None and data["nowcoder_uid"] != previous["nowcoder_uid"]:
            conn.execute("DELETE FROM platform_ratings WHERE member_id = ? AND platform = 'nowcoder'", (member_id,))
            conn.execute("""DELETE FROM contest_results WHERE member_id = ? AND contest_id IN
                          (SELECT id FROM contests WHERE platform = 'nowcoder')""", (member_id,))
    return get_member(member_id)


def delete_member(member_id: int) -> bool:
    with connection() as conn:
        cursor = conn.execute("DELETE FROM members WHERE id = ?", (member_id,))
    return cursor.rowcount > 0


def _rating_map(conn: sqlite3.Connection, member_ids: list[int] | None = None) -> dict[int, list[dict[str, Any]]]:
    query = "SELECT * FROM platform_ratings"
    params: list[Any] = []
    if member_ids:
        placeholders = ",".join("?" for _ in member_ids)
        query += f" WHERE member_id IN ({placeholders})"
        params.extend(member_ids)
    rows = conn.execute(query, params).fetchall()
    result: dict[int, list[dict[str, Any]]] = {}
    for row in rows:
        result.setdefault(int(row["member_id"]), []).append(dict(row))
    return result


def _member_card(row: sqlite3.Row, ratings: list[dict[str, Any]]) -> dict[str, Any]:
    ratings_by_platform = {item["platform"]: item for item in ratings}
    values = [int(item.get("rating") or 0) for item in ratings]
    fitted = max(values, default=1200)
    peak = max([int(item.get("peak_rating") or 0) for item in ratings] + [fitted])
    changes = [int(item.get("rating_change") or 0) for item in ratings]
    return {
        **dict(row),
        "ratings": ratings_by_platform,
        "current_rating": fitted,
        "peak_rating": peak,
        "rating_change": sum(changes),
        "platform_count": len(ratings),
        "fitted_rating": None,
    }


def list_members(*, search: str = "", team_group: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
    clauses = ["1 = 1"]
    params: list[Any] = []
    if search:
        clauses.append("(m.name LIKE ? OR m.student_id LIKE ? OR m.cf_handle LIKE ? OR m.atcoder_handle LIKE ? OR m.nowcoder_handle LIKE ? OR m.nowcoder_uid LIKE ?)")
        needle = f"%{search}%"
        params.extend([needle] * 6)
    if team_group:
        clauses.append("m.team_group = ?")
        params.append(team_group)
    if status:
        clauses.append("m.status = ?")
        params.append(status)
    with connection() as conn:
        rows = conn.execute(
            f"SELECT m.* FROM members m WHERE {' AND '.join(clauses)} ORDER BY m.status = 'active' DESC, m.name COLLATE NOCASE",
            params,
        ).fetchall()
        ratings = _rating_map(conn, [int(row["id"]) for row in rows])
        member_ids = [int(row["id"]) for row in rows]
        fitted_rows = conn.execute(
            """
            SELECT cr.member_id, cr.fitted_rating
            FROM contest_results cr JOIN contests c ON c.id = cr.contest_id
            JOIN (
              SELECT cr2.member_id, MAX(c2.contest_time) AS latest_time
              FROM contest_results cr2 JOIN contests c2 ON c2.id = cr2.contest_id
              WHERE cr2.member_id IN (%s)
              GROUP BY cr2.member_id
            ) latest ON latest.member_id = cr.member_id AND latest.latest_time = c.contest_time
            """ % ",".join("?" for _ in member_ids),
            member_ids,
        ).fetchall() if member_ids else []
        fitted_map = {int(item["member_id"]): int(item["fitted_rating"] or 0) for item in fitted_rows}
    cards = []
    for row in rows:
        card = _member_card(row, ratings.get(int(row["id"]), []))
        card["fitted_rating"] = fitted_map.get(int(row["id"])) or card["current_rating"]
        cards.append(card)
    return cards


def get_member(member_id: int) -> dict[str, Any] | None:
    with connection() as conn:
        row = conn.execute("SELECT * FROM members WHERE id = ?", (member_id,)).fetchone()
        if row is None:
            return None
        ratings = _rating_map(conn, [member_id]).get(member_id, [])
        result_rows = conn.execute(
            """
            SELECT cr.*, c.platform, c.external_id, c.name AS contest_name, c.contest_time,
                   c.participant_count
            FROM contest_results cr JOIN contests c ON c.id = cr.contest_id
            WHERE cr.member_id = ? ORDER BY c.contest_time, cr.id
            """,
            (member_id,),
        ).fetchall()
        submission_rows = conn.execute(
            "SELECT * FROM submissions WHERE member_id = ? ORDER BY submitted_at DESC LIMIT 500",
            (member_id,),
        ).fetchall()
    member = _member_card(row, ratings)
    results = _rows(result_rows)
    submissions = _rows(submission_rows)
    profile = build_profile(member=member, ratings=ratings, contest_results=results, submissions=submissions)
    member.update(
        {
            "profile": profile,
            "contest_results": results,
            "submissions": submissions,
            "rating_history": _rating_history(results, ratings),
        }
    )
    return member


def _rating_history(results: list[dict[str, Any]], ratings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    history = [
        {
            "date": item.get("contest_time"),
            "platform": item.get("platform"),
            "label": item.get("contest_name"),
            "rating": item["new_rating"] if item.get("new_rating") is not None else item.get("fitted_rating"),
            "fitted_rating": item.get("fitted_rating"),
            "performance_rating": item.get("performance_rating"),
        }
        for item in results
    ]
    if history:
        return history
    return [
        {
            "date": item.get("fetched_at"),
            "platform": item.get("platform"),
            "label": "当前 rating",
            "rating": item.get("rating"),
            "fitted_rating": item.get("rating"),
            "performance_rating": item.get("rating"),
        }
        for item in ratings
    ]


def upsert_platform_rating(
    *,
    member_id: int,
    platform: str,
    rating: int,
    peak_rating: int = 0,
    rank_title: str = "",
    contest_count: int = 0,
    rating_change: int = 0,
    source: str = "sync",
    _conn: sqlite3.Connection | None = None,
) -> dict[str, Any]:
    now = utc_now()
    with nullcontext(_conn) if _conn is not None else connection() as conn:
        conn.execute(
            """
            INSERT INTO platform_ratings
              (member_id, platform, rating, peak_rating, rank_title, contest_count,
               rating_change, fetched_at, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(member_id, platform) DO UPDATE SET
              rating = excluded.rating, peak_rating = excluded.peak_rating,
              rank_title = excluded.rank_title, contest_count = excluded.contest_count,
              rating_change = excluded.rating_change, fetched_at = excluded.fetched_at,
              source = excluded.source
            """,
            (member_id, platform, rating, peak_rating, rank_title, contest_count, rating_change, now, source),
        )
        row = conn.execute(
            "SELECT * FROM platform_ratings WHERE member_id = ? AND platform = ?",
            (member_id, platform),
        ).fetchone()
    return dict(row)


def upsert_contest_result(
    *,
    member_id: int,
    platform: str,
    external_id: str,
    name: str,
    contest_time: str,
    participant_count: int,
    rank: int,
    score: float | None = None,
    max_score: float | None = None,
    solved: int | None = None,
    penalty: int | None = None,
    old_rating: int | None = None,
    new_rating: int | None = None,
    rating_change: int | None = None,
    source: str = "sync",
    _conn: sqlite3.Connection | None = None,
) -> dict[str, Any]:
    from .analytics import fit_performance

    performance = fit_performance(rank, participant_count, score=score, max_score=max_score, solved=solved)
    with nullcontext(_conn) if _conn is not None else connection() as conn:
        now = utc_now()
        conn.execute(
            """
            INSERT INTO contests (platform, external_id, name, contest_time, participant_count, source, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(platform, external_id) DO UPDATE SET
              name = excluded.name, contest_time = excluded.contest_time,
              participant_count = max(contests.participant_count, excluded.participant_count)
            """,
            (platform, str(external_id), name, contest_time, participant_count, source, now),
        )
        contest = conn.execute(
            "SELECT id FROM contests WHERE platform = ? AND external_id = ?",
            (platform, str(external_id)),
        ).fetchone()
        contest_id = int(contest["id"])
        previous = conn.execute(
            """
            SELECT cr.fitted_rating FROM contest_results cr JOIN contests c ON c.id = cr.contest_id
            WHERE cr.member_id = ? AND c.platform = ? AND c.contest_time < ?
            ORDER BY c.contest_time DESC LIMIT 1
            """,
            (member_id, platform, contest_time),
        ).fetchone()
        prior = int(previous["fitted_rating"]) if previous and previous["fitted_rating"] else 1200
        target = performance if new_rating is None else 0.68 * int(new_rating) + 0.32 * performance
        fitted = int(round(0.66 * prior + 0.34 * target))
        conn.execute(
            """
            INSERT INTO contest_results
              (contest_id, member_id, rank, participants, score, max_score, solved, penalty,
               old_rating, new_rating, performance_rating, fitted_rating, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(contest_id, member_id) DO UPDATE SET
              rank = excluded.rank, participants = excluded.participants, score = excluded.score,
              max_score = excluded.max_score, solved = excluded.solved, penalty = excluded.penalty,
              old_rating = excluded.old_rating, new_rating = excluded.new_rating,
              performance_rating = excluded.performance_rating, fitted_rating = excluded.fitted_rating,
              source = excluded.source
            """,
            (contest_id, member_id, rank, participant_count, score, max_score, solved, penalty, old_rating, new_rating, performance, fitted, source),
        )
        row = conn.execute(
            """
            SELECT cr.*, c.platform, c.external_id, c.name AS contest_name, c.contest_time,
                   c.participant_count
            FROM contest_results cr JOIN contests c ON c.id = cr.contest_id
            WHERE cr.contest_id = ? AND cr.member_id = ?
            """,
            (contest_id, member_id),
        ).fetchone()
    return dict(row)


def recompute_member_results(member_id: int, platform: str | None = None, *, _conn: sqlite3.Connection | None = None) -> int:
    with nullcontext(_conn) if _conn is not None else connection() as conn:
        clauses = ["cr.member_id = ?"]
        params: list[Any] = [member_id]
        if platform:
            clauses.append("c.platform = ?")
            params.append(platform)
        rows = conn.execute(
            f"SELECT cr.*, c.platform, c.contest_time FROM contest_results cr JOIN contests c ON c.id = cr.contest_id WHERE {' AND '.join(clauses)} ORDER BY c.contest_time, cr.id",
            params,
        ).fetchall()
        updated = recompute_fit_rows(_rows(rows))
        for item in updated:
            conn.execute(
                "UPDATE contest_results SET performance_rating = ?, fitted_rating = ? WHERE id = ?",
                (item["performance_rating"], item["fitted_rating"], item["id"]),
            )
    return len(updated)


def save_nowcoder_sync(member_id: int, uid: str, snapshot: dict[str, Any]) -> None:
    """Commit the complete fetch atomically, only while the same UID is bound."""
    with connection() as conn:
        conn.execute("BEGIN IMMEDIATE")
        member = conn.execute("SELECT nowcoder_uid FROM members WHERE id = ?", (member_id,)).fetchone()
        if member is None or member["nowcoder_uid"] != uid:
            raise ValueError("成员已删除或牛客 UID 已变更，请重新同步")
        conn.execute("""DELETE FROM contest_results WHERE member_id = ? AND source = 'nowcoder'
                      AND contest_id IN (SELECT id FROM contests WHERE platform = 'nowcoder')""", (member_id,))
        for item in snapshot["history"]:
            upsert_contest_result(member_id=member_id, platform="nowcoder", source="nowcoder", _conn=conn, **item)
        upsert_platform_rating(
            member_id=member_id, platform="nowcoder", source="nowcoder", _conn=conn,
            **{key: snapshot[key] for key in ("rating", "peak_rating", "rank_title", "contest_count", "rating_change")},
        )
        recompute_member_results(member_id, "nowcoder", _conn=conn)
        if snapshot.get("nickname"):
            conn.execute("UPDATE members SET nowcoder_handle = ?, updated_at = ? WHERE id = ?",
                         (snapshot["nickname"], utc_now(), member_id))


def list_contests(*, platform: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
    limit = max(1, min(200, limit))
    clauses = ["1 = 1"]
    params: list[Any] = []
    if platform:
        clauses.append("c.platform = ?")
        params.append(platform)
    with connection() as conn:
        rows = conn.execute(
            f"""
            SELECT c.*, COUNT(cr.id) AS result_count,
                   AVG(cr.performance_rating) AS avg_performance,
                   MAX(cr.performance_rating) AS top_performance
            FROM contests c LEFT JOIN contest_results cr ON cr.contest_id = c.id
            WHERE {' AND '.join(clauses)}
            GROUP BY c.id ORDER BY c.contest_time DESC LIMIT ?
            """,
            [*params, limit],
        ).fetchall()
    return _rows(rows)


def import_contest(payload: dict[str, Any]) -> dict[str, Any]:
    results = payload.get("results") or []
    imported: list[dict[str, Any]] = []
    member_ids: set[int] = set()
    for result in results:
        member_ids.add(int(result["member_id"]))
        imported.append(
            upsert_contest_result(
                member_id=int(result["member_id"]),
                platform=str(payload.get("platform", "manual")),
                external_id=str(payload.get("external_id") or payload.get("name") or "manual"),
                name=str(payload.get("name") or "未命名比赛"),
                contest_time=str(payload.get("contest_time") or utc_now()),
                participant_count=int(result.get("participants") or payload.get("participant_count") or 0),
                rank=int(result.get("rank") or 0),
                score=result.get("score"),
                max_score=result.get("max_score"),
                solved=result.get("solved"),
                penalty=result.get("penalty"),
                old_rating=result.get("old_rating"),
                new_rating=result.get("new_rating"),
                source="manual",
            )
        )
    for member_id in member_ids:
        recompute_member_results(member_id)
    return {"contest": payload, "imported": len(imported), "results": imported}


def list_submissions(*, member_id: int | None = None, platform: str | None = None, verdict: str | None = None, limit: int = 100) -> tuple[list[dict[str, Any]], int]:
    limit = max(1, min(500, limit))
    clauses = ["1 = 1"]
    params: list[Any] = []
    if member_id is not None:
        clauses.append("s.member_id = ?")
        params.append(member_id)
    if platform:
        clauses.append("s.platform = ?")
        params.append(platform)
    if verdict:
        clauses.append("s.verdict = ?")
        params.append(verdict)
    with connection() as conn:
        total = int(conn.execute(f"SELECT COUNT(*) FROM submissions s WHERE {' AND '.join(clauses)}", params).fetchone()[0])
        rows = conn.execute(
            f"""
            SELECT s.*, m.name AS member_name FROM submissions s LEFT JOIN members m ON m.id = s.member_id
            WHERE {' AND '.join(clauses)} ORDER BY s.submitted_at DESC LIMIT ?
            """,
            [*params, limit],
        ).fetchall()
    return _rows(rows), total


def get_submission(submission_id: str) -> dict[str, Any] | None:
    with connection() as conn:
        row = conn.execute(
            "SELECT s.*, m.name AS member_name FROM submissions s LEFT JOIN members m ON m.id = s.member_id WHERE s.id = ?",
            (submission_id,),
        ).fetchone()
    return _row(row)


def upsert_submission(data: dict[str, Any]) -> dict[str, Any]:
    submission_id = str(data.get("id") or data.get("external_id") or f"manual-{utc_now()}")
    external_id = str(data.get("external_id") or submission_id)
    with connection() as conn:
        conn.execute(
            """
            INSERT INTO submissions
              (id, member_id, platform, external_id, problem_id, problem_name, verdict, language,
               submitted_at, runtime_ms, memory_kb, code_length, source, url, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
              member_id = excluded.member_id, platform = excluded.platform,
              external_id = excluded.external_id, problem_id = excluded.problem_id,
              problem_name = excluded.problem_name, verdict = excluded.verdict,
              language = excluded.language, submitted_at = excluded.submitted_at,
              runtime_ms = excluded.runtime_ms, memory_kb = excluded.memory_kb,
              code_length = excluded.code_length, source = excluded.source,
              url = excluded.url, tags = excluded.tags
            """,
            (
                submission_id,
                data.get("member_id"),
                str(data.get("platform") or "oj"),
                external_id,
                str(data.get("problem_id") or ""),
                str(data.get("problem_name") or "未命名题目"),
                str(data.get("verdict") or "PENDING"),
                str(data.get("language") or ""),
                str(data.get("submitted_at") or utc_now()),
                data.get("runtime_ms"),
                data.get("memory_kb"),
                data.get("code_length"),
                str(data.get("source") or "manual"),
                str(data.get("url") or ""),
                json.dumps(data.get("tags") or [], ensure_ascii=False) if isinstance(data.get("tags"), list) else str(data.get("tags") or ""),
            ),
        )
    return get_submission(submission_id)  # type: ignore[return-value]


def seed_demo_data() -> None:
    if count_members() > 0:
        return
    members = [
        ("林墨", "S24001", "算法组", "#2dd4bf", "tourist", "LynnM", "linmo", ""),
        ("周屿", "S24008", "算法组", "#fb7185", "zhouyu_cf", "ZhouYu", "zhouyu", ""),
        ("许安", "S24015", "图论组", "#fbbf24", "anxu", "AnXu", "anxu", ""),
        ("沈砚", "S23022", "图论组", "#60a5fa", "shenyu", "ShenYan", "shenyu", ""),
        ("顾遥", "S24031", "新秀组", "#a78bfa", "guyao", "GuYao", "guyao", ""),
        ("唐梨", "S23009", "新秀组", "#34d399", "tangli", "TangLi", "tangli", ""),
        ("季川", "S22004", "教练组", "#f97316", "jichuan", "JiChuan", "jichuan", ""),
    ]
    ids: list[int] = []
    with connection() as conn:
        now = datetime.now(timezone.utc)
        for name, student_id, group, color, cf, atcoder, nowcoder, note in members:
            cursor = conn.execute(
                """
                INSERT INTO members (name, student_id, team_group, status, color, cf_handle,
                  atcoder_handle, nowcoder_handle, note, created_at, updated_at)
                VALUES (?, ?, ?, 'active', ?, ?, ?, ?, ?, ?, ?)
                """,
                (name, student_id, group, color, cf, atcoder, nowcoder, note, now.isoformat(), now.isoformat()),
            )
            ids.append(int(cursor.lastrowid))
    # Ratings are intentionally varied so the dashboard communicates useful states on first run.
    rating_values = [
        (ids[0], [("codeforces", 2186, 2310, "Candidate Master", 74, 46), ("atcoder", 1830, 1924, "6 kyu", 42, 25), ("nowcoder", 2050, 2140, "优胜", 31, 18)]),
        (ids[1], [("codeforces", 1942, 2011, "Expert", 58, 82), ("atcoder", 1670, 1788, "7 kyu", 38, 60), ("nowcoder", 1870, 1930, "进阶", 22, 45)]),
        (ids[2], [("codeforces", 1764, 1830, "Expert", 41, -12), ("atcoder", 1512, 1620, "8 kyu", 29, 34), ("nowcoder", 1620, 1705, "进阶", 16, 6)]),
        (ids[3], [("codeforces", 1610, 1760, "Pupil", 34, 120), ("atcoder", 1420, 1500, "8 kyu", 20, 76), ("nowcoder", 1510, 1580, "稳定", 12, 51)]),
        (ids[4], [("codeforces", 1432, 1510, "Pupil", 26, 96), ("atcoder", 1325, 1410, "9 kyu", 18, 55), ("nowcoder", 1380, 1450, "基础", 9, 32)]),
        (ids[5], [("codeforces", 1318, 1402, "Newbie", 19, 44), ("atcoder", 1190, 1280, "10 kyu", 12, 38), ("nowcoder", 1260, 1320, "基础", 8, 28)]),
        (ids[6], [("codeforces", 2320, 2440, "Master", 91, -18), ("atcoder", 2050, 2180, "5 kyu", 67, 12), ("nowcoder", 2210, 2300, "优胜", 48, 20)]),
    ]
    for member_id, values in rating_values:
        for platform, rating, peak, title, count, change in values:
            upsert_platform_rating(member_id=member_id, platform=platform, rating=rating, peak_rating=peak, rank_title=title, contest_count=count, rating_change=change, source="demo")
    _seed_contests(ids)
    _seed_submissions(ids)


def _seed_contests(ids: list[int]) -> None:
    names = [
        ("codeforces", "CF-Round-971", "Codeforces Round 971", 22),
        ("atcoder", "ABC-368", "AtCoder Beginner Contest 368", 18),
        ("nowcoder", "NC-159", "牛客周赛 Round 159", 16),
        ("codeforces", "CF-Round-969", "Codeforces Round 969", 20),
        ("atcoder", "ARC-183", "AtCoder Regular Contest 183", 12),
        ("nowcoder", "NC-157", "牛客小白月赛 Round 137", 14),
        ("codeforces", "CF-Edu-170", "Educational Codeforces Round 170", 19),
        ("atcoder", "ABC-367", "AtCoder Beginner Contest 367", 15),
    ]
    base = datetime.now(timezone.utc) - timedelta(days=112)
    for index, (platform, external_id, name, field) in enumerate(names):
        contest_time = (base + timedelta(days=index * 14)).isoformat()
        # Each member participates in a realistic subset of contests.
        for offset, member_id in enumerate(ids):
            if (index + offset) % 4 == 3:
                continue
            rank = 2 + ((index * 11 + offset * 17) % max(4, field - 1))
            if member_id == ids[6]:
                rank = 1 + (index * 3) % 5
            solved = max(1, 5 - ((rank + index) % 4))
            old = 1200 + ((offset * 120 + index * 47) % 900)
            new = old + (field - rank) * 5 - 30
            upsert_contest_result(
                member_id=member_id,
                platform=platform,
                external_id=external_id,
                name=name,
                contest_time=contest_time,
                participant_count=field * 100,
                rank=rank,
                score=float(solved * 100),
                max_score=500,
                solved=solved,
                penalty=300 + rank * 7,
                old_rating=old,
                new_rating=max(800, min(2800, new)),
                source="demo",
            )


def _seed_submissions(ids: list[int]) -> None:
    problems = [
        ("P1001", "区间最大值", "ACCEPTED", "C++17"),
        ("P1002", "最短路计数", "ACCEPTED", "C++17"),
        ("P1003", "树上背包", "WRONG_ANSWER", "C++17"),
        ("P1004", "字符串哈希", "ACCEPTED", "Python"),
        ("P1005", "费用流", "TIME_LIMIT_EXCEEDED", "C++17"),
        ("P1006", "二维前缀和", "ACCEPTED", "Java"),
        ("P1007", "括号序列", "COMPILE_ERROR", "C++17"),
        ("P1008", "动态规划优化", "ACCEPTED", "C++17"),
    ]
    base = datetime.now(timezone.utc) - timedelta(days=38)
    index = 0
    for day in range(38):
        for member_offset, member_id in enumerate(ids):
            if (day * 3 + member_offset) % 5 == 0:
                continue
            problem_id, problem_name, verdict, language = problems[(day + member_offset) % len(problems)]
            if (day + member_offset) % 6 == 0:
                verdict = "WRONG_ANSWER"
            elif (day + member_offset) % 11 == 0:
                verdict = "TIME_LIMIT_EXCEEDED"
            timestamp = (base + timedelta(days=day, minutes=member_offset * 23)).isoformat()
            upsert_submission(
                {
                    "id": f"demo-{index:04d}",
                    "member_id": member_id,
                    "platform": "oj",
                    "external_id": f"demo-{index:04d}",
                    "problem_id": problem_id,
                    "problem_name": problem_name,
                    "verdict": verdict,
                    "language": language,
                    "submitted_at": timestamp,
                    "runtime_ms": 48 + ((day + member_offset) * 13) % 430,
                    "memory_kb": 1024 + ((day + member_offset) * 521) % 18000,
                    "code_length": 180 + ((day + member_offset) * 31) % 920,
                    "source": "demo",
                    "tags": ["图论"] if "路" in problem_name else ["基础"] if "前缀" in problem_name else [],
                }
            )
            index += 1


def overview() -> dict[str, Any]:
    members = list_members()
    with connection() as conn:
        contest_count = int(conn.execute("SELECT COUNT(*) FROM contests").fetchone()[0])
        submission_count = int(conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0])
        accepted_count = int(conn.execute("SELECT COUNT(*) FROM submissions WHERE verdict IN ('ACCEPTED', 'AC')").fetchone()[0])
        active_days = int(conn.execute("SELECT COUNT(DISTINCT substr(submitted_at, 1, 10)) FROM submissions").fetchone()[0])
        result_rows = conn.execute(
            """
            SELECT cr.member_id, cr.fitted_rating, cr.performance_rating, cr.rank, cr.participants,
                   c.platform, c.contest_time, c.name AS contest_name, m.name AS member_name, m.color
            FROM contest_results cr JOIN contests c ON c.id = cr.contest_id JOIN members m ON m.id = cr.member_id
            ORDER BY c.contest_time, cr.id
            """
        ).fetchall()
        recent_submissions = conn.execute(
            """
            SELECT s.*, m.name AS member_name, m.color FROM submissions s
            LEFT JOIN members m ON m.id = s.member_id ORDER BY s.submitted_at DESC LIMIT 8
            """
        ).fetchall()
    results = _rows(result_rows)
    recent = _rows(recent_submissions)
    current_scores: dict[int, int] = {}
    for item in results:
        current_scores[int(item["member_id"])] = int(item.get("fitted_rating") or 0)
    leaderboard = []
    for member in members:
        fitted = current_scores.get(int(member["id"]), int(member.get("fitted_rating") or 0))
        official = int(member.get("current_rating") or 0)
        # A modest anchor to the latest platform rating prevents a sparse or
        # unusually small contest sample from dominating the team leaderboard.
        score = round(0.8 * fitted + 0.2 * official) if fitted else official
        member = dict(member)
        member["fitted_rating"] = score
        member["tier"] = _tier(score)
        leaderboard.append(member)
    leaderboard.sort(key=lambda item: item["fitted_rating"], reverse=True)
    trend = _overview_trend(results)
    platform_summary = _platform_summary(members)
    acceptance_rate = round(accepted_count / submission_count * 100, 1) if submission_count else 0.0
    return {
        "metrics": {
            "member_count": len(members),
            "active_member_count": sum(1 for member in members if member.get("status") == "active"),
            "average_rating": round(sum(item["fitted_rating"] for item in leaderboard) / len(leaderboard)) if leaderboard else 0,
            "rating_delta": _rating_delta(results),
            "contest_count": contest_count,
            "submission_count": submission_count,
            "accepted_count": accepted_count,
            "acceptance_rate": acceptance_rate,
            "active_days": active_days,
        },
        "leaderboard": leaderboard,
        "trend": trend,
        "platforms": platform_summary,
        "recent_submissions": recent,
        "insights": _insights(leaderboard, results, acceptance_rate),
    }


def aggregate_rating_trend(platform: str | None = None) -> list[dict[str, Any]]:
    """Return team-average fitted rating points, optionally for one platform."""

    with connection() as conn:
        if platform:
            rows = conn.execute(
                """
                SELECT cr.fitted_rating, c.contest_time
                FROM contest_results cr JOIN contests c ON c.id = cr.contest_id
                WHERE c.platform = ? ORDER BY c.contest_time, cr.id
                """,
                (platform,),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT cr.fitted_rating, c.contest_time
                FROM contest_results cr JOIN contests c ON c.id = cr.contest_id
                ORDER BY c.contest_time, cr.id
                """
            ).fetchall()
    return _overview_trend(_rows(rows))


def _tier(score: int) -> str:
    if score >= 2200:
        return "竞赛级"
    if score >= 1800:
        return "进阶"
    if score >= 1500:
        return "稳步上升"
    return "基础期"


def _overview_trend(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[str, list[int]] = {}
    for item in results:
        date = str(item.get("contest_time") or "")[:10]
        if date:
            buckets.setdefault(date, []).append(int(item.get("fitted_rating") or 0))
    return [{"date": key, "rating": round(sum(values) / len(values)), "count": len(values)} for key, values in sorted(buckets.items())]


def _rating_delta(results: list[dict[str, Any]]) -> int:
    if not results:
        return 0
    dates = sorted({str(item.get("contest_time") or "")[:10] for item in results})
    if len(dates) < 2:
        return 0
    first = [int(item.get("fitted_rating") or 0) for item in results if str(item.get("contest_time") or "")[:10] == dates[0]]
    last = [int(item.get("fitted_rating") or 0) for item in results if str(item.get("contest_time") or "")[:10] == dates[-1]]
    return round(sum(last) / len(last) - sum(first) / len(first)) if first and last else 0


def _platform_summary(members: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output = []
    for platform, label, color in [
        ("codeforces", "Codeforces", "#f97316"),
        ("atcoder", "AtCoder", "#60a5fa"),
        ("nowcoder", "NowCoder", "#2dd4bf"),
    ]:
        ratings = [item["ratings"].get(platform) for item in members if item.get("ratings", {}).get(platform)]
        values = [int(item["rating"]) for item in ratings]
        output.append({
            "platform": platform,
            "label": label,
            "color": color,
            "members": len(values),
            "average": round(sum(values) / len(values)) if values else 0,
            "peak": max([int(item.get("peak_rating") or 0) for item in ratings] + [0]),
            "change": sum(int(item.get("rating_change") or 0) for item in ratings),
        })
    return output


def _insights(leaderboard: list[dict[str, Any]], results: list[dict[str, Any]], acceptance_rate: float) -> list[dict[str, Any]]:
    if not leaderboard:
        return []
    top = leaderboard[0]
    rising = sorted(leaderboard, key=lambda item: int(item.get("rating_change") or 0), reverse=True)[0]
    return [
        {"tone": "mint", "label": "队伍峰值", "value": str(top["fitted_rating"]), "text": f"{top['name']} 当前拟合 rating 最高"},
        {"tone": "amber", "label": "上升最快", "value": f"+{max(0, int(rising.get('rating_change') or 0))}", "text": f"{rising['name']} 平台合计增幅领先"},
        {"tone": "coral", "label": "复盘提示", "value": f"{100 - acceptance_rate:.1f}%", "text": "提交未一次通过，建议按题型拆分复盘"},
    ]


def record_sync(scope: str, status: str, message: str, started_at: str, finished_at: str | None = None) -> None:
    with connection() as conn:
        conn.execute(
            "INSERT INTO sync_runs (scope, status, message, started_at, finished_at) VALUES (?, ?, ?, ?, ?)",
            (scope, status, message, started_at, finished_at),
        )


def latest_syncs(limit: int = 8) -> list[dict[str, Any]]:
    with connection() as conn:
        rows = conn.execute("SELECT * FROM sync_runs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return _rows(rows)


def integration_status() -> dict[str, Any]:
    with connection() as conn:
        oj_count = int(conn.execute("SELECT COUNT(*) FROM submissions WHERE source = 'sakura-oj'").fetchone()[0])
        latest = conn.execute("SELECT * FROM sync_runs ORDER BY id DESC LIMIT 1").fetchone()
    from .config import settings

    return {
        "oj_database_exists": _path_exists(),
        "oj_imported_submissions": oj_count,
        "oj_base_url": settings.oj_base_url,
        "latest_sync": _row(latest),
    }


def _path_exists() -> bool:
    from .config import settings

    return settings.oj_database_path.exists()
