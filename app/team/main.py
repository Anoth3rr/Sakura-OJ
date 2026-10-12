from __future__ import annotations

import csv
import io
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse

from . import repository
from .config import settings
from .db import init_db, utc_now
from .providers import ProviderError, import_oj_http, sync_all, sync_member
from .schemas import ContestImport, MemberCreate, MemberUpdate, OJSyncRequest, RatingImport, SubmissionImport, SyncRequest


from ..dependencies import require_coach

router = APIRouter(prefix='/api/team', tags=['训练队'], dependencies=[Depends(require_coach)])


def initialize():
    settings.ensure_directories()
    init_db()
    if settings.seed_demo:
        repository.seed_demo_data()


@router.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": "0.2.0",
        "members": repository.count_members(),
        "oj_database": str(settings.oj_database_path),
    }


@router.get("/capabilities")
def capabilities() -> dict[str, Any]:
    return {
        "platforms": [
            {"id": "codeforces", "label": "Codeforces", "mode": "live"},
            {"id": "atcoder", "label": "AtCoder", "mode": "live"},
            {"id": "nowcoder", "label": "NowCoder", "mode": "configured" if settings.nowcoder_api_url else "live", "account_field": "nowcoder_uid"},
        ],
        "oj": {
            "mode": "http" if settings.oj_base_url else "sqlite",
            "base_url": settings.oj_base_url,
            "database": str(settings.oj_database_path),
        },
        "fit_method": "percentile + field-size correction + exponentially smoothed official rating",
    }


@router.get("/overview")
def get_overview() -> dict[str, Any]:
    return repository.overview()


@router.get("/members")
def get_members(
    search: str = Query(default="", max_length=80),
    team_group: str | None = Query(default=None, max_length=40),
    status: str | None = Query(default=None, max_length=20),
) -> dict[str, Any]:
    items = repository.list_members(search=search.strip(), team_group=team_group, status=status)
    return {"items": items, "total": len(items)}


@router.post("/members", status_code=201)
def create_member(payload: MemberCreate) -> dict[str, Any]:
    try:
        return repository.create_member(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/members/{member_id}")
def get_member(member_id: int) -> dict[str, Any]:
    member = repository.get_member(member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="成员不存在")
    return member


@router.patch("/members/{member_id}")
def patch_member(member_id: int, payload: MemberUpdate) -> dict[str, Any]:
    try:
        member = repository.update_member(member_id, payload.model_dump(exclude_unset=True))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if member is None:
        raise HTTPException(status_code=404, detail="成员不存在")
    return member


@router.delete("/members/{member_id}", status_code=204)
def remove_member(member_id: int) -> None:
    if not repository.delete_member(member_id):
        raise HTTPException(status_code=404, detail="成员不存在")


@router.post("/members/{member_id}/sync", status_code=202)
def sync_one_member(member_id: int, payload: SyncRequest, background_tasks: BackgroundTasks) -> dict[str, Any]:
    member = repository.get_member(member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="成员不存在")
    background_tasks.add_task(_sync_member_job, member, payload.platforms)
    return {"status": "queued", "member_id": member_id, "platforms": payload.platforms}


@router.post("/sync/all", status_code=202)
def sync_everything(payload: SyncRequest, background_tasks: BackgroundTasks) -> dict[str, Any]:
    background_tasks.add_task(_sync_all_job, payload.platforms)
    return {"status": "queued", "platforms": payload.platforms}


def _sync_member_job(member: dict[str, Any], platforms: list[str]) -> None:
    started = utc_now()
    try:
        result = sync_member(member, platforms)
        status = "partial" if result["errors"] and result["synced"] else "error" if result["errors"] else "success"
        message = "；".join(
            [f"{item['platform']} Rating {item['rating']}，{item['contests']} 场比赛" for item in result["synced"]]
            + [f"{item['platform']}：{item['message']}" for item in result["errors"]]
        )
    except Exception as exc:
        status, message = "error", str(exc)
    repository.record_sync("member:%s" % member["id"], status, message, started, utc_now())


def _sync_all_job(platforms: list[str]) -> None:
    started = utc_now()
    try:
        result = sync_all(platforms)
        errors = sum(len(item["errors"]) for item in result["results"])
        synced = sum(len(item["synced"]) for item in result["results"])
        status = "partial" if errors and synced else "error" if errors else "success"
        message = f"同步 {synced} 项，{errors} 项失败"
        if errors:
            details = [f"成员 {item['member_id']} / {error['platform']}：{error['message']}"
                       for item in result["results"] for error in item["errors"]]
            message += "；" + "；".join(details[:3])
    except Exception as exc:
        status, message = "error", str(exc)
    repository.record_sync("all", status, message, started, utc_now())


@router.get("/ratings/trend")
def rating_trend(
    member_id: int | None = Query(default=None, ge=1),
    platform: str | None = Query(default=None, max_length=30),
) -> dict[str, Any]:
    if member_id is not None:
        member = repository.get_member(member_id)
        if member is None:
            raise HTTPException(status_code=404, detail="成员不存在")
        history = member["rating_history"]
        if platform:
            history = [item for item in history if item.get("platform") == platform]
        return {"member_id": member_id, "series": history}
    return {"member_id": None, "series": repository.aggregate_rating_trend(platform)}


@router.post("/ratings/recompute")
def recompute_ratings() -> dict[str, Any]:
    members = repository.list_members()
    updated = 0
    for member in members:
        updated += repository.recompute_member_results(int(member["id"]))
    return {"updated_results": updated, "members": len(members)}


@router.post("/ratings/import", status_code=201)
def import_rating(payload: RatingImport) -> dict[str, Any]:
    if repository.get_member(payload.member_id) is None:
        raise HTTPException(status_code=404, detail="成员不存在")
    return repository.upsert_platform_rating(
        member_id=payload.member_id,
        platform=payload.platform,
        rating=payload.rating,
        peak_rating=payload.peak_rating or payload.rating,
        rank_title=payload.rank_title,
        contest_count=payload.contest_count,
        rating_change=payload.rating_change,
        source="manual",
    )


@router.get("/contests")
def get_contests(
    platform: str | None = Query(default=None, max_length=30),
    limit: int = Query(default=50, ge=1, le=200),
) -> dict[str, Any]:
    return {"items": repository.list_contests(platform=platform, limit=limit)}


@router.post("/contests/import", status_code=201)
def import_contest(payload: ContestImport) -> dict[str, Any]:
    for result in payload.results:
        if repository.get_member(result.member_id) is None:
            raise HTTPException(status_code=404, detail=f"成员 {result.member_id} 不存在")
    return repository.import_contest(payload.model_dump())


@router.get("/submissions")
def get_submissions(
    member_id: int | None = Query(default=None, ge=1),
    platform: str | None = Query(default=None, max_length=30),
    verdict: str | None = Query(default=None, max_length=40),
    limit: int = Query(default=100, ge=1, le=500),
) -> dict[str, Any]:
    items, total = repository.list_submissions(member_id=member_id, platform=platform, verdict=verdict, limit=limit)
    counts: dict[str, int] = {}
    for item in items:
        key = str(item.get("verdict") or "UNKNOWN")
        counts[key] = counts.get(key, 0) + 1
    return {"items": items, "total": total, "verdict_counts": counts}


@router.get("/submissions/{submission_id}")
def get_submission(submission_id: str) -> dict[str, Any]:
    item = repository.get_submission(submission_id)
    if item is None:
        raise HTTPException(status_code=404, detail="提交不存在")
    return item


@router.post("/submissions/import", status_code=201)
def import_submissions(payload: SubmissionImport) -> dict[str, Any]:
    if payload.member_id is not None and repository.get_member(payload.member_id) is None:
        raise HTTPException(status_code=404, detail="成员不存在")
    imported = 0
    for item in payload.items:
        data = dict(item)
        data["platform"] = payload.platform
        data["member_id"] = payload.member_id if payload.member_id is not None else data.get("member_id")
        data["source"] = data.get("source") or payload.platform
        repository.upsert_submission(data)
        imported += 1
    return {"imported": imported, "platform": payload.platform, "member_id": payload.member_id}


@router.post("/integrations/oj/sync")
def sync_oj(payload: OJSyncRequest) -> dict[str, Any]:
    started = utc_now()
    try:
        result = import_oj_http(member_id=payload.member_id)
        repository.record_sync("sakura-oj", "success", str(result), started, utc_now())
        return result
    except ProviderError as exc:
        repository.record_sync("sakura-oj", "error", str(exc), started, utc_now())
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/integrations/status")
def integration_status() -> dict[str, Any]:
    return {**repository.integration_status(), "syncs": repository.latest_syncs()}


@router.get("/export")
def export_data(format: str = Query(default="json", pattern="^(json|csv)$")):
    members = repository.list_members()
    if format == "json":
        return JSONResponse({"generated_at": utc_now(), "members": members, "overview": repository.overview()})
    output = io.StringIO()
    output.write("\ufeff")
    writer = csv.writer(output)
    writer.writerow(["姓名", "学号", "组别", "拟合 rating", "Codeforces", "AtCoder", "NowCoder", "牛客 UID", "牛客昵称", "状态"])
    for member in members:
        ratings = member.get("ratings", {})
        writer.writerow([
            member.get("name"), member.get("student_id"), member.get("team_group"), member.get("current_rating"),
            ratings.get("codeforces", {}).get("rating", ""), ratings.get("atcoder", {}).get("rating", ""),
            ratings.get("nowcoder", {}).get("rating", ""), member.get("nowcoder_uid"), member.get("nowcoder_handle"), member.get("status"),
        ])
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=sakura-team.csv"},
    )


