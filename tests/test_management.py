import io
import json
import sqlite3
import uuid
import zipfile
from concurrent.futures import ThreadPoolExecutor

import pytest

from app import catalog, repository
from app.config import settings
from app.db import SCHEMA, connection, init_db
from app.studio.models import fingerprint


@pytest.fixture
def admin(client, monkeypatch):
    monkeypatch.setattr(settings, "auth_required", True)
    client.cookies.clear()
    response = client.post("/api/auth/login", json={"username": settings.admin_username, "password": settings.admin_password})
    assert response.status_code == 200
    yield response.json()["user"]
    client.cookies.clear()


def draft(client, mode="normal"):
    csrf = client.get("/api/studio/bootstrap").json()["csrf"]
    headers = {"X-CSRF-Token": csrf}
    response = client.post("/api/studio/problems", json={"template": mode}, headers=headers)
    assert response.status_code == 200
    return response.json(), headers


def attach_validated_fixture(client, problem):
    service = client.app.state.studio
    dataset = {"id": "management-" + uuid.uuid4().hex, "fingerprint": fingerprint(problem), "cases": [{"id": "001"}]}
    root = service.jobs.root / dataset["id"]
    root.mkdir()
    (root / "001.in").write_text("1\n7\n", encoding="utf-8")
    (root / "001.ans").write_text("7\n", encoding="utf-8")
    assert service.store.attach_dataset(problem["id"], dataset)


def test_stable_id_created_before_publication_and_survives_edit_restore_export(client, admin):
    p, headers = draft(client)
    code = p["problem_code"]
    assert code.isascii() and code.isdigit() and len(code) == 4
    p.update(title="唯一编号测试", problem_code="P999999")
    saved = client.put("/api/studio/problems/" + p["id"], json=p, headers=headers).json()
    assert saved["problem_code"] == code
    assert client.get("/api/problems", params={"search": code}).json()["total"] == 0
    candidates = client.get("/api/problem-bank", params={"search": code}).json()["items"]
    assert len(candidates) == 1 and not candidates[0]["can_add"]
    deleted = client.post(f"/api/studio/problems/{p['id']}/trash", json={"revision": saved["revision"]}, headers=headers).json()
    assert deleted["problem_code"] == code
    restored = client.post(f"/api/studio/problems/{p['id']}/restore", json={"revision": deleted["revision"]}, headers=headers).json()
    assert restored["problem_code"] == code
    with zipfile.ZipFile(io.BytesIO(client.get(f"/api/studio/problems/{p['id']}/export").content)) as archive:
        assert json.loads(archive.read("problem.json"))["problem_code"] == code
    init_db()
    assert client.get("/api/studio/problems/" + p["id"]).json()["problem_code"] == code


@pytest.mark.parametrize("mode", ["normal", "interactive", "communication"])
def test_add_by_id_requires_verified_data_then_publishes_once(client, admin, mode):
    p, _ = draft(client, mode)
    code = p["problem_code"]
    assert client.post("/api/problem-bank", json={"problem_code": code}).status_code == 409
    attach_validated_fixture(client, p)
    assert client.get("/api/problem-bank", params={"search": code}).json()["items"][0]["can_add"]
    response = client.post("/api/problem-bank", json={"problem_code": code.lower()})
    assert response.status_code == 200, response.text
    published = response.json()["problem"]
    assert published["problem_code"] == code and published["judge_mode"] == mode
    assert "judge_config" not in published and published["test_cases"] == []
    case_ids = [item["id"] for item in repository.get_test_cases(published["id"])]
    again = client.post("/api/problem-bank", json={"problem_code": str(int(code))}).json()["problem"]
    assert again["id"] == published["id"]
    assert [item["id"] for item in repository.get_test_cases(published["id"])] == case_ids
    assert client.get("/api/problems", params={"search": code}).json()["total"] == 1
    legacy_code = f"P{int(code):06d}"
    legacy = client.post("/api/problem-bank", json={"problem_code": legacy_code}).json()["problem"]
    assert legacy["id"] == published["id"] and legacy["problem_code"] == code
    assert client.get("/api/problems", params={"search": legacy_code}).json()["total"] == 1
    assert client.get("/api/problem-bank", params={"search": legacy_code}).json()["items"][0]["problem_code"] == code
    assert client.get("/api/studio/problems/" + p["id"]).json()["publication"]["problem_code"] == code


def test_remove_blocks_access_and_submit_but_preserves_history_and_readd(client, admin):
    p, headers = draft(client)
    attach_validated_fixture(client, p)
    published = client.post("/api/problem-bank", json={"problem_code": p["problem_code"]}).json()["problem"]
    cases = repository.get_test_cases(published["id"])
    sid = "removed-bank-" + uuid.uuid4().hex
    repository.create_submission(submission_id=sid, problem_id=published["id"], language="cpp", source_code="int main(){}", user_id=admin["id"])
    repository.replace_submission_results(sid, [{"test_case_id": cases[0]["id"], "verdict": "ACCEPTED"}])
    before = repository.get_submission(sid)
    assert client.delete("/api/problem-bank/" + p["problem_code"]).status_code == 204
    assert client.get("/api/problems/" + published["slug"]).status_code == 404
    assert client.get("/api/problems", params={"search": p["problem_code"]}).json()["total"] == 0
    for selector in ({"problem_id": published["id"]}, {"problem_slug": published["slug"]}):
        assert client.post("/api/submissions", json={**selector, "source_code": "int main(){}", "language": "cpp"}).status_code == 404
    # Also enforce visibility inside the submission transaction to close removal races.
    with pytest.raises(ValueError):
        repository.create_submission(submission_id="race-removed", problem_id=published["id"], language="cpp", source_code="int main(){}")
    assert client.get("/api/submissions/" + sid).status_code == 200
    assert repository.get_submission(sid) == before
    # A deleted/changed draft must not prevent restoring the last published snapshot.
    assert client.post(f"/api/studio/problems/{p['id']}/trash", json={"revision": p["revision"]}, headers=headers).status_code == 200
    restored = client.post("/api/problem-bank", json={"problem_code": p["problem_code"]})
    assert restored.status_code == 200
    assert restored.json()["problem"]["id"] == published["id"]
    assert repository.get_test_cases(published["id"]) == cases
    assert repository.get_submission(sid) == before


def test_unknown_invalid_and_trashed_ids_are_rejected(client, admin):
    assert client.post("/api/problem-bank", json={"problem_code": "P999999999"}).status_code == 404
    assert client.post("/api/problem-bank", json={"problem_code": "../../etc"}).status_code == 422
    p, headers = draft(client)
    client.post(f"/api/studio/problems/{p['id']}/trash", json={"revision": p["revision"]}, headers=headers)
    assert client.post("/api/problem-bank", json={"problem_code": p["problem_code"]}).status_code == 410


def test_bank_and_account_deletion_permissions(client, admin):
    code = client.get("/api/problems").json()["items"][0]["problem_code"]
    client.cookies.clear()
    assert client.get("/api/problem-bank").status_code == 401
    assert client.delete("/api/users/99999").status_code == 401
    for role in ("teacher", "student", "problem_admin"):
        name = "manage-permission-" + role
        repository.create_user(username=name, password="test-permission-pass", role=role)
        client.post("/api/auth/login", json={"username": name, "password": "test-permission-pass"})
        assert client.delete("/api/users/99999").status_code == 403
        expected = 200 if role == "problem_admin" else 403
        assert client.get("/api/problem-bank").status_code == expected
        assert client.post("/api/problem-bank", json={"problem_code": code}).status_code == expected
        if role != "problem_admin":
            assert client.delete("/api/problem-bank/" + code).status_code == 403


def test_delete_account_revokes_sessions_keeps_submissions_and_reserves_name(client, admin):
    created = client.post("/api/users", json={"username": "delete-me", "password": "delete-test-pass", "role": "student"})
    assert created.status_code == 201
    user = created.json()
    token = repository.create_session(user["id"])
    pid = client.get("/api/problems").json()["items"][0]["id"]
    repository.create_submission(submission_id="deleted-user-work", problem_id=pid, language="cpp", source_code="int main(){}", user_id=user["id"])
    assert client.delete(f"/api/users/{user['id']}").status_code == 204
    assert repository.get_user_by_session(token) is None
    assert repository.get_submission("deleted-user-work")["user_id"] == user["id"]
    assert all(item["id"] != user["id"] for item in client.get("/api/users").json())
    assert client.get("/api/submissions/deleted-user-work").status_code == 200
    assert client.patch(f"/api/users/{user['id']}", json={"is_active": True}).status_code == 404
    assert client.delete(f"/api/users/{user['id']}").status_code == 404
    assert client.post("/api/auth/login", json={"username": "delete-me", "password": "delete-test-pass"}).status_code == 401
    assert client.post("/api/auth/register", json={"username": "DELETE-ME", "password": "delete-test-pass"}).status_code == 409
    assert client.delete(f"/api/users/{admin['id']}").status_code == 400
    with connection() as db:
        row = db.execute("SELECT deleted_at, password_hash FROM users WHERE id=?", (user["id"],)).fetchone()
        assert row["deleted_at"] and row["password_hash"] == ""
        assert db.execute("SELECT COUNT(*) FROM sessions WHERE user_id=?", (user["id"],)).fetchone()[0] == 0


def test_concurrent_ids_are_unique_and_allocation_is_idempotent(client, admin):
    docs = [client.app.state.studio.store.create() for _ in range(8)]
    with ThreadPoolExecutor(max_workers=4) as pool:
        result = list(pool.map(catalog.decorate, docs + docs))
    assert len({item["problem_code"] for item in result}) == 8
    assert [item["problem_code"] for item in result[:8]] == [item["problem_code"] for item in result[8:]]


def test_legacy_migration_shares_published_and_draft_id(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "database_path", tmp_path / "legacy.sqlite3")
    with sqlite3.connect(settings.database_path) as db:
        db.executescript(SCHEMA)
        db.execute("INSERT INTO problems (slug,title,description,input_format,output_format,created_at,updated_at) VALUES ('legacy','旧题','','','','','')")
        db.execute("CREATE TABLE studio_publications (studio_id TEXT PRIMARY KEY, problem_id INTEGER UNIQUE, revision INTEGER, fingerprint TEXT, published_at TEXT)")
        db.execute("INSERT INTO studio_publications VALUES ('abcdef123456',1,1,'old','')")
    init_db()
    code = repository.get_problem_by_id(1)["problem_code"]
    assert catalog.decorate({"id": "abcdef123456"})["problem_code"] == code
    init_db()
    with connection() as db:
        assert db.execute("SELECT COUNT(*) FROM problem_catalog").fetchone()[0] == 1
        assert "deleted_at" in {row["name"] for row in db.execute("PRAGMA table_info(users)")}


def test_last_admin_survives_concurrent_deletions(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "database_path", tmp_path / "admins.sqlite3")
    init_db()
    a = repository.create_user(username="admin-a", password="test-admin-pass", role="admin")
    b = repository.create_user(username="admin-b", password="test-admin-pass", role="admin")

    def remove(pair):
        target, actor = pair
        try:
            return repository.delete_user(target, actor_id=actor)
        except ValueError:
            return False

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(remove, [(a.id, b.id), (b.id, a.id)]))
    assert sorted(outcomes) == [False, True]
    assert repository.count_active_admins() == 1
