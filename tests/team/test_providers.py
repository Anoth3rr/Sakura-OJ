from __future__ import annotations

from pathlib import Path

from app.team.config import settings
from app.team.db import init_db
from app.team.providers import sync_codeforces
from app.team.repository import create_member


def test_codeforces_provider_parses_and_persists(monkeypatch, tmp_path: Path):
    original_db = settings.database_path
    settings.database_path = tmp_path / "provider.sqlite3"
    init_db()
    member = create_member({"name": "Provider Test", "cf_handle": "tester"})

    def fake_json(url: str):
        if "user.info" in url:
            return {"status": "OK", "result": [{"rating": 1800, "maxRating": 1900, "rank": "expert"}]}
        if "user.status" in url:
            return {"status": "OK", "result": [{"id": 99, "contestId": 1, "creationTimeSeconds": 1760000000, "verdict": "OK", "programmingLanguage": "GNU C++17", "timeConsumedMillis": 12, "memoryConsumedBytes": 2048, "problem": {"index": "A", "name": "A + B", "tags": ["math"]}}]}
        return {
            "status": "OK",
            "result": [{
                "contestId": 1,
                "contestName": "Round 1",
                "rank": 12,
                "oldRating": 1700,
                "newRating": 1800,
                "ratingUpdateTimeSeconds": 1760000000,
            }],
        }

    monkeypatch.setattr("app.team.providers._get_json", fake_json)
    try:
        result = sync_codeforces(member)
        assert result["rating"] == 1800
        assert result["contests"] == 1
        assert result["submissions"] == 1
    finally:
        settings.database_path = original_db
