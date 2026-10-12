from __future__ import annotations

from collections.abc import Callable

from fastapi import HTTPException, Request, status

from . import repository
from .auth import AuthUser, ROLE_ADMIN, ROLE_PROBLEM_ADMIN, ROLE_STUDENT, ROLE_TEACHER
from .config import settings


def optional_current_user(request: Request) -> AuthUser | None:
    return repository.get_user_by_session(request.cookies.get(settings.session_cookie))


def current_user(request: Request) -> AuthUser:
    user = optional_current_user(request)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="请先登录")
    return user


def require_roles(*roles: str, allow_legacy: bool = False) -> Callable[[Request], AuthUser]:
    allowed = set(roles)

    def dependency(request: Request) -> AuthUser:
        user = optional_current_user(request)
        if user is None:
            if allow_legacy and not settings.auth_required:
                # Keep the original local MVP usable while deployments can set
                # OJ_AUTH_REQUIRED=true to enforce account checks.
                return AuthUser(
                    id=0,
                    username="legacy-local",
                    display_name="本地开发",
                    role=next(iter(allowed)),
                )
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="请先登录")
        if user.role not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="当前账号没有执行此操作的权限")
        return user

    return dependency


require_admin = require_roles(ROLE_ADMIN)
require_problem_manager = require_roles(
    ROLE_ADMIN, ROLE_PROBLEM_ADMIN, allow_legacy=True
)
require_coach = require_roles(ROLE_ADMIN, ROLE_TEACHER, allow_legacy=True)


def require_submission_user(request: Request) -> AuthUser:
    user = optional_current_user(request)
    if user is not None:
        return user
    if not settings.auth_required:
        return AuthUser(
            id=0,
            username="legacy-local",
            display_name="本地开发",
            role=ROLE_STUDENT,
        )
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="请先登录")
