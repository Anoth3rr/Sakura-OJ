"""Manager-only authoring API, served by Sakura's existing FastAPI process."""
import hmac
import json
import re

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, Response
from starlette.concurrency import run_in_threadpool

from ..dependencies import require_problem_manager
from .models import MODES, SOLUTION_TAGS, ProblemError
from .templates import example, candidate, multipass_example, testlib_communication_example
from .publishing import publish, publication
from .catalog_sync import ensure_oj_documents
from .exporting import bundle
from ..catalog import decorate, decorate_documents

router = APIRouter(prefix='/api/studio', tags=['录题'], dependencies=[Depends(require_problem_manager)])
PID, JID = r'([0-9a-f]{12})', r'([0-9a-f]{32})'
MAX_BODY = 6 * 1024 * 1024


@router.api_route('/{path:path}', methods=['GET', 'POST', 'PUT'])
async def endpoint(path: str, request: Request):
    service = request.app.state.studio
    try:
        data = {}
        if request.method != 'GET':
            token = request.headers.get('x-csrf-token', '')
            if not hmac.compare_digest(token, service.csrf):
                raise ProblemError('会话已更新，请刷新页面', 403)
            if request.headers.get('content-type', '').split(';')[0] != 'application/json':
                raise ProblemError('请求必须使用 application/json', 415)
            body = bytearray()
            async for chunk in request.stream():
                body.extend(chunk)
                if len(body) > MAX_BODY:
                    raise ProblemError('上传内容超过 6 MiB', 413)
            try:
                data = json.loads(body)
            except (ValueError, UnicodeError):
                raise ProblemError('JSON 格式不正确')
            if not isinstance(data, dict):
                raise ProblemError('请求内容必须是对象')
        return await run_in_threadpool(dispatch, service, path, request.method, data, request.query_params)
    except ProblemError as exc:
        return JSONResponse(dict(error=str(exc)), status_code=exc.status)


def dispatch(service, path, verb, data, query):
    if path == 'bootstrap' and verb == 'GET':
        return dict(csrf=service.csrf, health=service.engine.health(), modes=list(MODES),
                    version='2.2', solution_tags=list(SOLUTION_TAGS), templates={m: candidate(m) for m in MODES})
    if path == 'papers':
        if verb == 'GET':
            return dict(papers=service.papers.list())
        if verb == 'POST':
            return service.papers.create(data)
    if match := re.fullmatch('papers/' + PID, path):
        if verb == 'GET':
            return service.papers.get(match[1])
        if verb == 'PUT':
            return service.papers.save(match[1], data)
    if match := re.fullmatch('papers/' + PID + '/(delete|export|preview)', path):
        pid, action = match.groups()
        if verb == 'POST' and action == 'delete':
            return service.papers.delete(pid, data.get('revision'))
        paper = service.papers.get(pid)
        if verb == 'GET' and action == 'export':
            return bundle(service, paper=paper)
        if verb == 'GET' and action == 'preview':
            problems = [service.store.get(i) for i in paper['problem_ids']]
            return dict(paper=paper, problems=[{k: p[k] for k in ('title', 'statement', 'mode', 'time_ms', 'memory_mb')}
                                               for p in problems])
    if path == 'problems':
        if verb == 'GET':
            ensure_oj_documents(service.store)
            return dict(problems=decorate_documents(service.store.list()))
        if verb == 'POST':
            template = data.get('template')
            if template is not None and template not in (*MODES, 'multipass', 'testlib-communication'):
                raise ProblemError('未知示例题')
            problem = (testlib_communication_example() if template == 'testlib-communication' else
                       multipass_example() if template == 'multipass' else example(template) if template else data.get('problem'))
            return decorate(service.store.create(problem))
    if path == 'trash' and verb == 'GET':
        return dict(problems=decorate_documents(service.store.list(trashed=True)))
    if match := re.fullmatch('problems/' + PID + '/(trash|restore)', path):
        if verb == 'POST':
            pid, action = match.groups()
            return decorate(service.store.set_trashed(pid, data.get('revision'), action == 'trash'))
    if match := re.fullmatch('problems/' + PID, path):
        pid = match[1]
        if verb == 'GET':
            return dict(decorate(service.store.get(pid)), publication=publication(pid))
        if verb == 'PUT':
            return dict(decorate(service.store.save(pid, data)), publication=publication(pid))
    if match := re.fullmatch('problems/' + PID + '/(generate|submit|invoke|jobs|export|publish)', path):
        pid, action = match.groups()
        p = decorate(service.store.get(pid))
        if verb == 'POST' and action in ('generate', 'submit', 'invoke', 'publish'):
            if data.get('revision') != p['revision']:
                raise ProblemError('题目版本已更新，请先重新加载', 409)
            if action == 'publish':
                return publish(service, p, data)
            return service.jobs.submit(p, action, data)
        if verb == 'GET' and action == 'jobs':
            return dict(jobs=service.store.jobs(pid))
        if verb == 'GET' and action == 'export':
            return bundle(service, problem=p)
    if match := re.fullmatch('problems/' + PID + r'/cases/([0-9]{3})\.(in|ans)', path):
        if verb == 'GET':
            pid, name, suffix = match.groups()
            p = service.store.get(pid)
            f = service.jobs.case_path(p, name, suffix)
            if query.get('download') == '1':
                return Response(f.read_bytes(), media_type='application/octet-stream',
                                headers={'Content-Disposition': f'attachment; filename="{f.name}"'})
            with f.open('rb') as content:
                preview = content.read(65536)
            return dict(name=f.name, content=preview.decode('utf-8', errors='replace'),
                        bytes=f.stat().st_size, truncated=f.stat().st_size > len(preview))
    if match := re.fullmatch('jobs/' + JID, path):
        if verb == 'GET':
            return service.store.job(match[1])
    raise ProblemError('接口不存在', 404)
