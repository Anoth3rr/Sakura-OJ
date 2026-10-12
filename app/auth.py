from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


ROLE_ADMIN = "admin"
ROLE_PROBLEM_ADMIN = "problem_admin"
ROLE_TEACHER = "teacher"
ROLE_STUDENT = "student"
ROLES = (ROLE_ADMIN, ROLE_PROBLEM_ADMIN, ROLE_TEACHER, ROLE_STUDENT)
ROLE_LABELS = {
    ROLE_ADMIN: "管理员",
    ROLE_PROBLEM_ADMIN: "题目管理员",
    ROLE_TEACHER: "老师",
    ROLE_STUDENT: "学生",
}
ROLE_DESCRIPTIONS = {
    ROLE_ADMIN: "管理账号、角色和全部题目资源",
    ROLE_PROBLEM_ADMIN: "录入题目、维护题面和测试数据",
    ROLE_TEACHER: "布置练习并查看教学相关提交",
    ROLE_STUDENT: "练习题目并提交代码",
}

PASSWORD_ITERATIONS = 600_000
SESSION_TTL_SECONDS = 7 * 24 * 60 * 60


@dataclass(frozen=True)
class AuthUser:
    id: int
    username: str
    display_name: str
    role: str
    is_active: bool = True

    @property
    def role_label(self) -> str:
        return ROLE_LABELS.get(self.role, self.role)

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "username": self.username,
            "display_name": self.display_name,
            "role": self.role,
            "role_label": self.role_label,
            "is_active": self.is_active,
        }


def role_catalog() -> list[dict[str, str]]:
    return [
        {"id": role, "label": ROLE_LABELS[role], "description": ROLE_DESCRIPTIONS[role]}
        for role in ROLES
    ]


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS
    )
    return "pbkdf2_sha256${}${}${}".format(
        PASSWORD_ITERATIONS,
        salt.hex(),
        digest.hex(),
    )


def verify_password(password: str, encoded: str) -> bool:
    try:
        scheme, iterations, salt_hex, digest_hex = encoded.split("$", 3)
        if scheme != "pbkdf2_sha256":
            return False
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
        actual = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, int(iterations)
        )
    except (TypeError, ValueError):
        return False
    return hmac.compare_digest(actual, expected)


def new_session_token(ttl_seconds: int = SESSION_TTL_SECONDS) -> tuple[str, str, str]:
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    expires_at = (datetime.now(timezone.utc) + timedelta(seconds=max(60, int(ttl_seconds)))).isoformat()
    return token, token_hash, expires_at


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
