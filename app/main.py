from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

import sqlite3
from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response, status
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from . import repository
from . import catalog
from .auth import ROLE_ADMIN, ROLE_STUDENT, AuthUser, role_catalog, verify_password
from .config import settings
from .db import init_db
from .schemas import (
    ProblemCreate,
    ProblemBankAdd,
    ProblemDetail,
    ProblemListResponse,
    ProblemSummary,
    LanguageInfo,
    StatsResponse,
    SubmissionAccepted,
    SubmissionCreate,
    SubmissionDetail,
    SubmissionListResponse,
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    UserCreateRequest,
    UserResponse,
    UserUpdateRequest,
)
from .dependencies import current_user, optional_current_user, require_admin, require_problem_manager, require_submission_user
from .seed import seed_demo_data
from .services.judge import JudgeService
from .services.runner import language_catalog
from .studio.service import StudioService
from .studio.catalog_sync import ensure_oj_documents
from .studio.api import router as studio_router
from .team.main import router as team_router, initialize as initialize_team
from .team.integration import sync_all_local
from .services.newjudge import NewjudgeRunner


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.ensure_directories()
    init_db()
    repository.ensure_default_admin()
    seed_demo_data()
    initialize_team()
    sync_all_local()
    app.state.studio = StudioService(settings)
    ensure_oj_documents(app.state.studio.store)
    catalog.decorate_documents(app.state.studio.store.list() + app.state.studio.store.list(trashed=True))
    runner = NewjudgeRunner(app.state.studio.engine) if settings.judge_mode == 'newjudge' else None
    app.state.judge_service = JudgeService(runner=runner)
    try:
        yield
    finally:
        app.state.judge_service.shutdown()
        app.state.studio.shutdown()


app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="Sakura OJ · 集训队管理 · testlib 录题与 newjudge 评测",
    lifespan=lifespan,
)
app.include_router(team_router)
app.include_router(studio_router)


@app.middleware('http')
async def same_origin_writes(request: Request, call_next):
    if request.method not in ('GET', 'HEAD', 'OPTIONS'):
        origin = request.headers.get('origin')
        expected = str(request.base_url).rstrip('/')
        if origin and origin.rstrip('/') != expected:
            return JSONResponse({'detail': '不允许跨站写入'}, status_code=403)
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'same-origin'
    if request.url.path.startswith(('/api/', '/studio/')):
        response.headers['Cache-Control'] = 'no-store'
    elif request.url.path in ('/', '/assets/styles.css', '/assets/app.js'):
        # Revalidate the OJ shell and its assets after management UI upgrades.
        response.headers['Cache-Control'] = 'no-cache'
    return response


def _judge_service(request: Request) -> JudgeService:
    service = getattr(request.app.state, "judge_service", None)
    if service is None:
        raise HTTPException(status_code=503, detail="判题服务尚未启动")
    return service


@app.get("/health")
def health(request: Request) -> dict:
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": app.version,
        "auth_required": settings.auth_required,
        "modules": ['oj', 'team', 'studio', 'newjudge'],
        "judge": request.app.state.studio.engine.health(),
    }


def _user_response(user: AuthUser) -> dict:
    return user.as_dict()


@app.post("/api/auth/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, response: Response):
    try:
        user = repository.create_user(
            username=payload.username,
            password=payload.password,
            display_name=payload.display_name,
            role=ROLE_STUDENT,
        )
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="用户名已存在")
    token = repository.create_session(user.id)
    response.set_cookie(
        settings.session_cookie,
        token,
        max_age=max(60, settings.session_ttl_seconds),
        httponly=True,
        samesite="lax",
        path="/",
    )
    return {"user": _user_response(user)}


@app.post("/api/auth/login", response_model=AuthResponse)
def login(payload: LoginRequest, response: Response):
    user = repository.get_user_by_username(payload.username)
    password_hash = repository.get_user_password_hash(payload.username)
    if user is None or password_hash is None or not verify_password(payload.password, password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = repository.create_session(user.id)
    response.set_cookie(
        settings.session_cookie,
        token,
        max_age=max(60, settings.session_ttl_seconds),
        httponly=True,
        samesite="lax",
        path="/",
    )
    return {"user": _user_response(user)}


@app.post("/api/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response):
    repository.delete_session(request.cookies.get(settings.session_cookie))
    response.delete_cookie(settings.session_cookie, path="/")


@app.get("/api/auth/me", response_model=UserResponse)
def me(user: AuthUser = Depends(current_user)):
    return _user_response(user)


@app.get("/api/users", response_model=list[UserResponse])
def list_users(_: AuthUser = Depends(require_admin)):
    return repository.list_users()


@app.post("/api/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreateRequest, _: AuthUser = Depends(require_admin)):
    try:
        user = repository.create_user(
            username=payload.username,
            password=payload.password,
            display_name=payload.display_name,
            role=payload.role,
        )
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="用户名已存在")
    return _user_response(user)


@app.patch("/api/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    payload: UserUpdateRequest,
    actor: AuthUser = Depends(require_admin),
):
    target = repository.get_user_by_id(user_id, include_inactive=True)
    if target is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    next_role = payload.role if payload.role is not None else target.role
    next_active = payload.is_active if payload.is_active is not None else target.is_active
    if user_id == actor.id and not next_active:
        raise HTTPException(status_code=400, detail="不能停用当前登录账号")
    if user_id == actor.id and next_role != ROLE_ADMIN:
        raise HTTPException(status_code=400, detail="不能移除当前管理员权限")
    if (
        target.role == ROLE_ADMIN
        and target.is_active
        and (next_role != ROLE_ADMIN or not next_active)
        and repository.count_active_admins() <= 1
    ):
        raise HTTPException(status_code=400, detail="系统至少需要一个启用中的管理员")
    try:
        updated = repository.update_user(
            user_id, role=payload.role, display_name=payload.display_name,
            password=payload.password, is_active=payload.is_active, actor_id=actor.id,
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    if updated is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return _user_response(updated)


@app.delete("/api/users/{user_id}", status_code=204)
def delete_user(user_id: int, actor: AuthUser = Depends(require_admin)):
    try:
        if not repository.delete_user(user_id, actor_id=actor.id):
            raise HTTPException(404, "用户不存在或已删除")
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@app.get("/api/auth/roles")
def get_roles():
    return role_catalog()


@app.get("/api/stats", response_model=StatsResponse)
def get_stats():
    return repository.stats()


@app.get("/api/languages", response_model=list[LanguageInfo])
def get_languages():
    return language_catalog(settings)


@app.get("/api/problems", response_model=ProblemListResponse)
def list_problems(
    search: str = Query(default="", max_length=80),
    difficulty: str | None = Query(default=None, max_length=20),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    items, total = repository.list_problems(
        search=search.strip(),
        difficulty=difficulty.strip() if difficulty else None,
        page=page,
        page_size=page_size,
    )
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@app.get("/api/problem-bank")
def manage_problem_bank(request: Request, search: str = Query(default="", max_length=120),
                        _: AuthUser = Depends(require_problem_manager)):
    items = catalog.entries(request.app.state.studio.store, search)
    return {"items": items[:200], "total": len(items)}


@app.post("/api/problem-bank")
def add_to_problem_bank(payload: ProblemBankAdd, request: Request,
                        _: AuthUser = Depends(require_problem_manager)):
    from .studio.models import ProblemError
    from .studio.publishing import publish
    try:
        entry = catalog.lookup(payload.problem_code)
        if entry is None:
            raise HTTPException(404, "题目 ID 不存在，请先在录题工作台创建题目")
        if entry["problem_id"] is not None:
            pid = catalog.set_listed(payload.problem_code, True)
            problem = repository.get_problem_by_id(pid)
            return {"problem": problem, "url": "/#problem/" + problem["slug"]}
        service = request.app.state.studio
        return publish(service, service.store.get(entry["studio_id"]), {})
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    except ProblemError as exc:
        raise HTTPException(exc.status, str(exc)) from exc


@app.delete("/api/problem-bank/{problem_code}", status_code=204)
def remove_from_problem_bank(problem_code: str, _: AuthUser = Depends(require_problem_manager)):
    try:
        if catalog.set_listed(problem_code, False) is None:
            raise HTTPException(404, "题目尚未加入题库")
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@app.post("/api/problems", response_model=ProblemDetail, status_code=status.HTTP_201_CREATED)
def create_problem(payload: ProblemCreate, request: Request, _: AuthUser = Depends(require_problem_manager)):
    try:
        problem = repository.create_problem(payload.model_dump())
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="slug 已存在")
    ensure_oj_documents(request.app.state.studio.store)
    return repository.get_problem_by_id(int(problem["id"]), include_hidden=False)


@app.get("/api/problems/{slug}", response_model=ProblemDetail)
def get_problem(slug: str):
    problem = repository.get_problem_by_slug(slug, include_hidden=False)
    if problem is None or not problem['is_public']:
        raise HTTPException(status_code=404, detail="题目不存在")
    return problem


@app.get("/api/submissions", response_model=SubmissionListResponse)
def list_submissions(
    problem_id: int | None = Query(default=None, ge=1),
    limit: int = Query(default=30, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    actor: AuthUser = Depends(require_submission_user),
):
    user_id = actor.id if actor.id and actor.role == 'student' else None
    items, total = repository.list_submissions(problem_id=problem_id, limit=limit, offset=offset, user_id=user_id)
    return {"items": items, "total": total}


@app.post(
    "/api/submissions",
    response_model=SubmissionAccepted,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_submission(
    payload: SubmissionCreate,
    request: Request,
    actor: AuthUser = Depends(require_submission_user),
):
    source_bytes = len(payload.source_code.encode("utf-8"))
    if source_bytes > settings.max_source_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"源代码不能超过 {settings.max_source_bytes // 1000} KB",
        )
    problem = (
        repository.get_problem_by_id(payload.problem_id, include_hidden=True)
        if payload.problem_id is not None
        else repository.get_problem_by_slug(payload.problem_slug or "", include_hidden=True)
    )
    if problem is None or not problem['is_public']:
        raise HTTPException(status_code=404, detail="题目不存在")
    submission_id = uuid4().hex
    try:
        submission = repository.create_submission(
            submission_id=submission_id, problem_id=int(problem["id"]), language=payload.language,
            source_code=payload.source_code, user_id=actor.id or None,
        )
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    _judge_service(request).enqueue(submission_id)
    return submission


@app.get("/api/submissions/{submission_id}", response_model=SubmissionDetail)
def get_submission(submission_id: str, actor: AuthUser = Depends(require_submission_user)):
    submission = repository.get_submission(submission_id)
    if submission is None:
        raise HTTPException(status_code=404, detail="提交记录不存在")
    if actor.id and actor.role == 'student' and submission.get('user_id') != actor.id:
        raise HTTPException(status_code=403, detail='只能查看自己的提交')
    return submission


STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/assets", StaticFiles(directory=STATIC_DIR), name="assets")
app.mount('/team/assets', StaticFiles(directory=STATIC_DIR.parent / 'team/static'), name='team-assets')
app.mount('/studio/assets', StaticFiles(directory=STATIC_DIR.parent / 'studio/static'), name='studio-assets')


@app.get('/team', include_in_schema=False)
@app.get('/team/', include_in_schema=False)
def team_page(request: Request):
    return module_page(request, 'team', ('admin', 'teacher'))


@app.get('/studio', include_in_schema=False)
@app.get('/studio/', include_in_schema=False)
def studio_page(request: Request):
    return module_page(request, 'studio', ('admin', 'problem_admin'))


def module_page(request, module, roles):
    user = optional_current_user(request)
    if user is None and settings.auth_required:
        return RedirectResponse('/?next=/' + module + '/#login', status_code=303)
    if user is not None and user.role not in roles:
        raise HTTPException(403, '当前账号没有此模块的权限')
    return FileResponse(STATIC_DIR.parent / module / 'static/index.html')


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC_DIR / "index.html")
