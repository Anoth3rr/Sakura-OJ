from __future__ import annotations

import csv
import io

import pytest


def test_health_and_overview(client):
    response = client.get("/api/team/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    overview = client.get("/api/team/overview")
    assert overview.status_code == 200
    payload = overview.json()
    assert payload["metrics"]["member_count"] >= 7
    assert payload["leaderboard"]
    assert payload["trend"]


def test_member_profile_and_create(client):
    members = client.get("/api/team/members").json()["items"]
    profile = client.get(f"/api/team/members/{members[0]['id']}")
    assert profile.status_code == 200
    assert profile.json()["profile"]["tags"]
    created = client.post("/api/team/members", json={"name": "测试队员", "student_id": "T-01"})
    assert created.status_code == 201
    assert created.json()["name"] == "测试队员"


def test_import_contest_and_submission_filters(client):
    member_id = client.get("/api/team/members").json()["items"][0]["id"]
    result = client.post(
        "/api/team/contests/import",
        json={
            "platform": "manual",
            "external_id": "demo-extra",
            "name": "训练赛 Extra",
            "contest_time": "2026-09-01T12:00:00+00:00",
            "participant_count": 100,
            "results": [{"member_id": member_id, "rank": 3, "participants": 100, "solved": 4}],
        },
    )
    assert result.status_code == 201
    submissions = client.get("/api/team/submissions?verdict=ACCEPTED").json()
    assert submissions["total"] > 0
    assert all(item["verdict"] in {"ACCEPTED", "AC"} for item in submissions["items"])


def test_rating_trend_respects_platform(client):
    all_points = client.get("/api/team/ratings/trend").json()["series"]
    cf_points = client.get("/api/team/ratings/trend?platform=codeforces").json()["series"]
    assert all_points
    assert cf_points
    assert len(cf_points) <= len(all_points)


def test_submission_import_endpoint(client):
    member_id = client.get("/api/team/members").json()["items"][0]["id"]
    response = client.post(
        "/api/team/submissions/import",
        json={
            "platform": "atcoder",
            "member_id": member_id,
            "items": [{"id": "abc-test-1", "problem_id": "abc-test-a", "problem_name": "A", "verdict": "ACCEPTED", "language": "C++", "submitted_at": "2026-09-05T01:00:00Z"}],
        },
    )
    assert response.status_code == 201
    assert response.json()["imported"] == 1


def test_nowcoder_uid_crud_search_export_and_sync(client, monkeypatch):
    response = client.post("/api/team/members", json={"name": "UID 测试", "nowcoder_uid": 123456789, "nowcoder_handle": "昵称"})
    assert response.status_code == 201
    member = response.json()
    assert member["nowcoder_uid"] == "123456789"
    assert client.get("/api/team/members?search=123456789").json()["items"][0]["id"] == member["id"]
    exported = client.get("/api/team/export").json()["members"]
    assert next(item for item in exported if item["id"] == member["id"])["nowcoder_uid"] == "123456789"
    rows = list(csv.DictReader(io.StringIO(client.get("/api/team/export?format=csv").text.lstrip("\ufeff"))))
    assert next(item for item in rows if item["姓名"] == "UID 测试")["牛客 UID"] == "123456789"
    updated = client.patch(f"/api/team/members/{member['id']}", json={"nowcoder_uid": " 56 "})
    assert updated.json()["nowcoder_uid"] == "56"

    def fetch(url):
        assert "uid=56" in url and "handle=" not in url
        if "rating-basic" in url:
            return {"code": 0, "data": {"uid": 56, "rating": 1200, "ratedCount": 1, "nickname": "新昵称", "hasRating": True}}
        return {"code": 0, "data": [{"contestId": 123, "contestName": "比赛", "rating": 1200, "changeValue": 200, "rank": 50, "time": 1572345000000}]}

    monkeypatch.setattr("app.team.providers._get_json", fetch)
    synced = client.post(f"/api/team/members/{member['id']}/sync", json={"platforms": ["nowcoder"]})
    assert synced.status_code == 202
    profile = client.get(f"/api/team/members/{member['id']}").json()
    assert profile["ratings"]["nowcoder"]["rating"] == 1200
    assert profile["nowcoder_handle"] == "新昵称"
    capabilities = client.get("/api/team/capabilities").json()
    assert next(item for item in capabilities["platforms"] if item["id"] == "nowcoder")["mode"] == "live"


@pytest.mark.parametrize("uid", ["nickname", "-1", "0", "1.2", "１２３", "123?uid=56", "https://ac.nowcoder.com/123", True])
def test_nowcoder_uid_rejects_non_numeric_accounts(client, uid):
    response = client.post("/api/team/members", json={"name": "无效 UID", "nowcoder_uid": uid})
    assert response.status_code == 422
