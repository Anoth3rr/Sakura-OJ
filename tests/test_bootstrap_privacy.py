"""A clean checkout must not create an administrator with a shared password."""
import pytest

from app import repository
from app.config import settings
from app.db import connection, init_db


@pytest.mark.parametrize("auth_required", [False, True])
def test_fresh_database_requires_explicit_bootstrap_password(tmp_path, monkeypatch, auth_required):
    monkeypatch.setattr(settings, "database_path", tmp_path / "empty.sqlite3")
    monkeypatch.setattr(settings, "admin_username", "test-admin")
    monkeypatch.setattr(settings, "admin_password", "")
    monkeypatch.setattr(settings, "auth_required", auth_required)
    init_db()
    if auth_required:
        with pytest.raises(RuntimeError, match="OJ_ADMIN_PASSWORD"):
            repository.ensure_default_admin()
    else:
        repository.ensure_default_admin()
    with connection() as conn:
        assert conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0


def test_existing_admin_is_preserved_without_bootstrap_password(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "database_path", tmp_path / "existing.sqlite3")
    monkeypatch.setattr(settings, "admin_username", "test-admin")
    monkeypatch.setattr(settings, "admin_password", "test-only-bootstrap-password")
    monkeypatch.setattr(settings, "auth_required", True)
    init_db()
    repository.ensure_default_admin()
    with connection() as conn:
        original = dict(conn.execute("SELECT * FROM users").fetchone())
    monkeypatch.setattr(settings, "admin_password", "")
    repository.ensure_default_admin()
    with connection() as conn:
        assert dict(conn.execute("SELECT * FROM users").fetchone()) == original
