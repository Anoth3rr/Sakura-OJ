from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.team.config import settings
from app.main import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    from app.config import settings as oj_settings
    monkeypatch.setattr(oj_settings, 'database_path', tmp_path / 'oj.sqlite3')
    monkeypatch.setattr(oj_settings, 'judge_mode', 'local')
    original_db = settings.database_path
    original_seed = settings.seed_demo
    settings.database_path = tmp_path / "team.sqlite3"
    settings.seed_demo = True
    settings.ensure_directories()
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        settings.database_path = original_db
        settings.seed_demo = original_seed

