from __future__ import annotations

import copy
import sqlite3
from urllib.parse import parse_qs, urlsplit

import pytest

from app.team import providers, repository
from app.team.config import settings
from app.team.db import SCHEMA, connection, init_db


UID = "123456789"


@pytest.fixture
def member(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "database_path", tmp_path / "team.sqlite3")
    monkeypatch.setattr(settings, "nowcoder_api_url", "")
    init_db()
    return repository.create_member({"name": "测试队员", "nowcoder_uid": UID, "nowcoder_handle": "旧昵称"})


@pytest.fixture
def official(monkeypatch):
    # Shapes captured from the two public APIs used by the official profile page.
    payloads = {
        "rating-basic": {"code": 0, "msg": "OK", "data": {
            "uid": int(UID), "nickname": "测试昵称", "hasRating": True, "rating": 1400.0,
            "ratedCount": 2, "teamRatedCount": 10, "allRatedCount": 12, "contestCount": 20,
        }},
        "rating-history": {"code": 0, "msg": "OK", "data": [
            {"contestId": 1100, "contestName": "比赛一", "rating": 1500.0,
             "changeValue": 500.0, "rank": 10, "time": 1572345000000},
            {"contestId": 1101, "contestName": "比赛二", "rating": 1400.0,
             "changeValue": -100.0, "rank": 100, "time": 1572517800000},
        ]},
    }

    def fetch(url):
        parsed = urlsplit(url)
        assert parsed.hostname == "ac.nowcoder.com"
        assert parse_qs(parsed.query) == {"uid": [UID]}
        return copy.deepcopy(payloads[parsed.path.rsplit("/", 1)[1]])

    monkeypatch.setattr(providers, "_get_json", fetch)
    return payloads


def test_official_uid_sync_is_complete_and_idempotent(member, official):
    # Ordering must come from contest time, not an assumed API order.
    official["rating-history"]["data"].reverse()
    for _ in range(2):
        result = providers.sync_nowcoder(member)
        assert result == {"platform": "nowcoder", "uid": UID, "nickname": "测试昵称",
                          "rating": 1400, "peak_rating": 1500, "contests": 2}
    stored = repository.get_member(member["id"])
    assert stored["nowcoder_handle"] == "测试昵称"
    snapshot = stored["ratings"]["nowcoder"]
    assert (snapshot["rating"], snapshot["peak_rating"], snapshot["rating_change"], snapshot["contest_count"]) == (1400, 1500, -100, 2)
    history = stored["contest_results"]
    assert len(history) == 2
    assert history[0]["contest_time"] == "2019-10-29T10:30:00+00:00"
    assert (history[0]["old_rating"], history[1]["old_rating"]) == (1000, 1500)
    assert all(item["participants"] == 0 for item in history)  # Unknown, not fabricated.
    assert [item["rating"] for item in stored["rating_history"]] == [1500, 1400]


@pytest.mark.parametrize("failure", ["missing_user", "api_error", "incomplete", "invalid_time", "inconsistent", "bad_json", "duplicate"])
def test_failed_fetch_keeps_previous_snapshot(member, official, failure):
    providers.sync_nowcoder(member)
    before = repository.get_member(member["id"])
    if failure == "missing_user":
        official["rating-basic"]["data"] = {"followingCount": 0, "followedCount": 0}
    elif failure == "api_error":
        official["rating-history"] = {"code": 999, "msg": "请稍后重试"}
    elif failure == "incomplete":
        official["rating-history"]["data"].pop()
    elif failure == "invalid_time":
        official["rating-history"]["data"][1]["time"] = "not-a-date"
    elif failure == "inconsistent":
        official["rating-basic"]["data"]["rating"] = 1600
    elif failure == "duplicate":
        official["rating-history"]["data"][1]["contestId"] = 1100
    else:
        official["rating-history"] = []
    with pytest.raises(providers.ProviderError):
        providers.sync_nowcoder(member)
    after = repository.get_member(member["id"])
    assert after["ratings"] == before["ratings"]
    assert after["contest_results"] == before["contest_results"]
    assert after["nowcoder_handle"] == before["nowcoder_handle"]


def test_network_failure_keeps_previous_rating(member, official, monkeypatch):
    providers.sync_nowcoder(member)
    before = repository.get_member(member["id"])["ratings"]

    def failed(_):
        raise providers.ProviderError("请求超时")

    monkeypatch.setattr(providers, "_get_json", failed)
    result = providers.sync_member(member, ["nowcoder"])
    assert result["errors"] == [{"platform": "nowcoder", "message": "请求超时"}]
    assert repository.get_member(member["id"])["ratings"] == before


def test_zero_rating_is_not_missing_or_fitted(member, official):
    official["rating-basic"]["data"].update(rating=0, ratedCount=1)
    official["rating-history"]["data"] = [dict(official["rating-history"]["data"][0], rating=0, changeValue=-1000)]
    assert providers.sync_nowcoder(member)["rating"] == 0
    stored = repository.get_member(member["id"])
    assert stored["ratings"]["nowcoder"]["rating_change"] == -1000
    assert stored["rating_history"][0]["rating"] == 0


def test_unrated_account_is_successful(member, official):
    official["rating-basic"]["data"].update(hasRating=False, ratedCount=0)
    official["rating-basic"]["data"].pop("rating")
    official["rating-history"]["data"] = []
    assert providers.sync_nowcoder(member)["contests"] == 0
    assert repository.get_member(member["id"])["ratings"]["nowcoder"]["rank_title"] == "未定级"


def test_rebinding_only_clears_nowcoder_and_rejects_stale_fetch(member, official):
    providers.sync_nowcoder(member)
    repository.upsert_platform_rating(member_id=member["id"], platform="codeforces", rating=1234)
    repository.update_member(member["id"], {"nowcoder_uid": "56"})
    with pytest.raises(providers.ProviderError, match="UID 已变更"):
        providers.sync_nowcoder(member)
    stored = repository.get_member(member["id"])
    assert stored["nowcoder_uid"] == "56"
    assert "nowcoder" not in stored["ratings"]
    assert stored["ratings"]["codeforces"]["rating"] == 1234
    assert stored["contest_results"] == []


def test_database_failure_rolls_back_entire_sync(member, official, monkeypatch):
    providers.sync_nowcoder(member)
    before = repository.get_member(member["id"])
    original = repository.upsert_contest_result

    def fail_second(**kwargs):
        if kwargs["external_id"] == "1101":
            raise sqlite3.OperationalError("test write failure")
        return original(**kwargs)

    monkeypatch.setattr(repository, "upsert_contest_result", fail_second)
    with pytest.raises(sqlite3.OperationalError):
        providers.sync_nowcoder(member)
    after = repository.get_member(member["id"])
    assert after["ratings"] == before["ratings"]
    assert after["contest_results"] == before["contest_results"]


def test_custom_endpoint_uses_uid_and_preserves_zero(member, monkeypatch):
    monkeypatch.setattr(settings, "nowcoder_api_url", "https://example.test/rating?key=public")

    def fetch(url):
        assert parse_qs(urlsplit(url).query) == {"uid": [UID], "key": ["public"]}
        return {"data": {"rating": 0, "maxRating": 1500, "ratingChange": 0, "contestCount": 0, "history": []}}

    monkeypatch.setattr(providers, "_get_json", fetch)
    assert providers.sync_nowcoder(member)["rating"] == 0
    assert repository.get_member(member["id"])["ratings"]["nowcoder"]["peak_rating"] == 1500


def test_all_sync_only_queries_configured_accounts(member, official):
    result = providers.sync_all()
    assert result["results"][0]["errors"] == []
    assert len(result["results"][0]["synced"]) == 1


def test_missing_uid_does_not_query_nickname(member, monkeypatch):
    member = repository.update_member(member["id"], {"nowcoder_uid": ""})

    def unexpected(_):
        pytest.fail("Should not send a nickname to the API")

    monkeypatch.setattr(providers, "_get_json", unexpected)
    with pytest.raises(providers.ProviderError, match="未配置牛客 UID"):
        providers.sync_nowcoder(member)


def test_numeric_legacy_handles_migrate_once(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "database_path", tmp_path / "old.sqlite3")
    with connection() as conn:
        conn.executescript(SCHEMA.replace("    nowcoder_uid TEXT NOT NULL DEFAULT '',\n", ""))
        for handle in [" 00123456 ", "nickname", "123abc", "0", "", "１２３"]:
            conn.execute("INSERT INTO members (name, nowcoder_handle, created_at, updated_at) VALUES (?, ?, '', '')", (handle, handle))
    init_db()
    with connection() as conn:
        rows = conn.execute("SELECT id, nowcoder_handle, nowcoder_uid FROM members ORDER BY id").fetchall()
    assert [item["nowcoder_uid"] for item in rows] == ["123456", "", "", "", "", ""]
    repository.update_member(rows[0]["id"], {"nowcoder_uid": ""})
    init_db()
    assert repository.get_member(rows[0]["id"])["nowcoder_uid"] == ""
