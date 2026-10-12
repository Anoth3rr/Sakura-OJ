from __future__ import annotations

from app.config import settings


def test_role_catalog_has_four_account_types(client):
    response = client.get("/api/auth/roles")
    assert response.status_code == 200
    assert {item["id"] for item in response.json()} == {
        "admin",
        "problem_admin",
        "teacher",
        "student",
    }


def test_register_login_and_admin_user_management(client):
    old_required = settings.auth_required
    old_admin_username = settings.admin_username
    old_admin_password = settings.admin_password
    settings.auth_required = True
    settings.admin_username = "bootstrap-admin"
    settings.admin_password = "bootstrap-pass-123"
    try:
        # The fixture lifespan has already run; create the configured admin for
        # this isolated database explicitly.
        from app import repository

        repository.ensure_default_admin()
        response = client.post(
            "/api/auth/login",
            json={"username": "bootstrap-admin", "password": "bootstrap-pass-123"},
        )
        assert response.status_code == 200
        assert response.json()["user"]["role"] == "admin"
        admin_id = response.json()["user"]["id"]

        response = client.post(
            "/api/users",
            json={
                "username": "teacher-account",
                "password": "teacher-pass-123",
                "role": "teacher",
            },
        )
        assert response.status_code == 201
        assert response.json()["role"] == "teacher"
        assert client.get("/api/users").json()[0]["role_label"] == "管理员"

        spare_admin = client.post(
            "/api/users",
            json={
                "username": "spare-admin",
                "password": "spare-admin-pass-123",
                "role": "admin",
            },
        )
        assert spare_admin.status_code == 201
        spare_admin_id = spare_admin.json()["id"]
        assert client.patch(f"/api/users/{spare_admin_id}", json={"is_active": False}).status_code == 200
        assert client.post(
            "/api/auth/login",
            json={"username": "spare-admin", "password": "spare-admin-pass-123"},
        ).status_code == 401
        assert client.patch(f"/api/users/{admin_id}", json={"role": "teacher"}).status_code == 400

        response = client.post(
            "/api/auth/register",
            json={"username": "student-account", "password": "student-pass-123"},
        )
        assert response.status_code == 201
        assert response.json()["user"]["role"] == "student"

        # Registration changes the session to student; account management must
        # remain administrator-only.
        assert client.get("/api/users").status_code == 403
    finally:
        client.cookies.clear()
        settings.auth_required = old_required
        settings.admin_username = old_admin_username
        settings.admin_password = old_admin_password


def test_auth_required_blocks_anonymous_submission(client):
    old_required = settings.auth_required
    settings.auth_required = True
    try:
        response = client.post(
            "/api/submissions",
            json={
                "problem_slug": "sum-two",
                "language": "cpp",
                "source_code": "int main(){}",
            },
        )
        assert response.status_code == 401
    finally:
        settings.auth_required = old_required
