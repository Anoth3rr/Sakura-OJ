"""Problem documents and an atomic, versioned local SQLite repository."""
import hashlib
import json
import re
from pathlib import Path
from contextlib import contextmanager
import shlex
import sqlite3
import time
import uuid

MODES = ('normal', 'interactive', 'communication')
ROLES = ('gen', 'val', 'checker', 'interactor', 'reference')
MAX_SOURCE = 512 * 1024
MAX_SOLUTIONS = 32
SOLUTION_TAGS = ('main-correct', 'correct', 'wrong', 'time-limit', 'memory-limit',
                 'runtime-error', 'output-limit', 'communication-limit', 'compile-error')
EXPECTED_VERDICTS = dict(zip(SOLUTION_TAGS, ('AC', 'AC', 'WA', 'TLE', 'MLE', 'RE', 'OLE', 'CLE', 'CE')))
LEGACY_COMMUNICATION = 'send-receive-stdin-v1'
DOMJUDGE_COMMUNICATION = 'domjudge-multipass-v1'
TESTLIB_COMMUNICATION = 'testlib-communication-v1'


def is_multipass(p):
    return p['mode'] == 'communication' and p.get('communication_protocol', LEGACY_COMMUNICATION) == DOMJUDGE_COMMUNICATION


def is_testlib_communication(p):
    return p['mode'] == 'communication' and p.get('communication_protocol', LEGACY_COMMUNICATION) == TESTLIB_COMMUNICATION


def uses_interactor(p):
    return p['mode'] == 'interactive' or is_testlib_communication(p)


class ProblemError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def new_problem():
    return dict(title='未命名题目', statement='', mode='normal', time_ms=1000,
                memory_mb=256, output_kb=1024, message_bytes=1024,
                generation='10 100 1\n100 1000 2\n1000 1000000 3', programs={}, solutions=[])


def source(value, role='solution'):
    if not isinstance(value, dict):
        raise ProblemError('程序文件格式不正确')
    name = str(value.get('name', 'main.cpp'))
    code = value.get('content', '')
    if not isinstance(code, str) or not code.strip() or len(code.encode()) > MAX_SOURCE or '\0' in code:
        raise ProblemError('源码不能为空，且不能超过 512 KiB')
    suffix = Path(name).suffix.lower()
    allowed = {'.cpp': ('cpp',), '.cc': ('cpp',), '.cxx': ('cpp',), '.c': ('c',),
               '.py': ('python', 'pypy'), '.java': ('java',)}.get(suffix, ())
    language = value.get('language') or (allowed[0] if allowed else None)
    if language not in allowed or (role in ('gen', 'val', 'checker', 'interactor') and language != 'cpp'):
        raise ProblemError('testlib 组件须为 C++；标程和提交支持 C/C++、Python 3、PyPy 3、Java（Main 类）')
    return dict(name=Path(name.replace('\\', '/')).name[:100], content=code, language=language)


def generation_lines(text):
    lines = []
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        try:
            args = shlex.split(line)
        except ValueError as exc:
            raise ProblemError('生成参数引号不匹配') from exc
        if args and args[0] == 'gen':
            args = args[1:]
        if len(args) > 50 or any(len(x) > 200 or '\0' in x for x in args):
            raise ProblemError('生成器参数过长')
        lines.append(args)
    if not 1 <= len(lines) <= 100:
        raise ProblemError('请填写 1～100 行生成参数，每行生成一个测试点')
    return lines


def main_solution(problem):
    return next((s for s in problem.get('solutions', []) if s['tag'] == 'main-correct'), None)


def effective_programs(problem):
    programs = dict(problem['programs'])
    main = main_solution(problem)
    if main and not uses_interactor(problem):
        programs['reference'] = source(main)
    return programs


def validate_solutions(values, problem):
    if not isinstance(values, list) or len(values) > MAX_SOLUTIONS:
        raise ProblemError(f'每题最多保存 {MAX_SOLUTIONS} 份解法')
    result, ids, mains, total = [], set(), 0, 0
    for value in values:
        item = source(value)
        sid = value.get('id') or uuid.uuid4().hex[:12]
        if not isinstance(sid, str) or not re.fullmatch('[0-9a-f]{12}', sid) or sid in ids:
            raise ProblemError('解法 ID 无效或重复')
        tag = value.get('tag', 'correct')
        if tag not in SOLUTION_TAGS:
            raise ProblemError('未知解法标记')
        item.update(id=sid, tag=tag)
        if value.get('receiver'):
            if problem['mode'] != 'communication' or is_multipass(problem) or is_testlib_communication(problem):
                raise ProblemError('只有 Sender / Receiver 通信协议支持独立 Receiver')
            item['receiver'] = source(value['receiver'])
        total += len(item['content'].encode()) + len(item.get('receiver', {}).get('content', '').encode())
        ids.add(sid)
        mains += tag == 'main-correct'
        result.append(item)
    if mains > 1:
        raise ProblemError('每题只能指定一份 Main Correct 标程')
    if total > 4 * 1024 * 1024:
        raise ProblemError('解法源码总大小不能超过 4 MiB')
    return result


def validate(data):
    if not isinstance(data, dict):
        raise ProblemError('题目格式不正确')
    p = new_problem()
    for key in ('title', 'statement', 'mode', 'generation'):
        value = data.get(key, p[key])
        if not isinstance(value, str):
            raise ProblemError(f'{key} 必须是文本')
        p[key] = value
    p['title'] = p['title'].strip() or '未命名题目'
    if len(p['title']) > 120 or len(p['statement'].encode()) > 512 * 1024:
        raise ProblemError('标题或题面过长')
    if p['mode'] not in MODES:
        raise ProblemError('未知判题方式')
    p['communication_protocol'] = data.get('communication_protocol', LEGACY_COMMUNICATION)
    if p['communication_protocol'] not in (LEGACY_COMMUNICATION, DOMJUDGE_COMMUNICATION, TESTLIB_COMMUNICATION):
        raise ProblemError('未知通信协议')
    for key, low, high in (('time_ms', 100, 30000), ('memory_mb', 16, 2048),
                           ('output_kb', 1, 8192), ('message_bytes', 1, 1048576), ('validation_passes', 1, 32)):
        value = data.get(key, p.get(key, 2))
        if type(value) is not int or not low <= value <= high:
            raise ProblemError(f'{key} 必须在 {low}～{high} 之间')
        p[key] = value
    if len(p['generation']) > 30000:
        raise ProblemError('生成参数过长')
    programs = data.get('programs', {})
    if not isinstance(programs, dict) or any(k not in ROLES for k in programs):
        raise ProblemError('未知程序类型')
    p['programs'] = {role: source(value, role) for role, value in programs.items() if value}
    p['solutions'] = validate_solutions(data.get('solutions', []), p)
    return p


def fingerprint(problem):
    keys = ('mode', 'time_ms', 'memory_mb', 'output_kb', 'message_bytes', 'generation', 'programs')
    payload = {k: problem[k] for k in keys}
    payload['programs'] = effective_programs(problem)
    main = main_solution(problem)
    if main and uses_interactor(problem):
        payload['main_solution'] = source(main)
    if main and main.get('receiver'):
        payload['reference_receiver'] = main['receiver']
    if is_multipass(problem):
        payload.update(communication_protocol=DOMJUDGE_COMMUNICATION, validation_passes=problem.get('validation_passes', 2))
    elif is_testlib_communication(problem):
        payload['communication_protocol'] = TESTLIB_COMMUNICATION
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


class Store:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.db = self.root / 'studio.sqlite3'
        with self.connect() as db:
            db.executescript('''
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS problems (
                  id TEXT PRIMARY KEY, document TEXT NOT NULL, revision INTEGER NOT NULL,
                  created REAL NOT NULL, updated REAL NOT NULL, dataset TEXT, deleted_at REAL);
                CREATE TABLE IF NOT EXISTS jobs (
                  id TEXT PRIMARY KEY, problem_id TEXT NOT NULL, kind TEXT NOT NULL,
                  state TEXT NOT NULL, created REAL NOT NULL, updated REAL NOT NULL,
                  payload TEXT NOT NULL);
            ''')
            if 'deleted_at' not in {r['name'] for r in db.execute('PRAGMA table_info(problems)')}:
                db.execute('ALTER TABLE problems ADD COLUMN deleted_at REAL')
            db.execute("UPDATE jobs SET state='failed', payload=? WHERE state IN ('queued','running')",
                       (json.dumps(dict(error='服务重启，任务已中断，请重新运行', log=[])),))

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.db, timeout=20)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    @staticmethod
    def require_active(row):
        if row is None:
            raise ProblemError('题目不存在', 404)
        if row['deleted_at'] is not None:
            raise ProblemError('题目已移入回收站，请先恢复', 410)

    @staticmethod
    def document(row):
        p = json.loads(row['document'])
        p.setdefault('solutions', [])
        dataset = json.loads(row['dataset']) if row['dataset'] else None
        return dict(p, id=row['id'], revision=row['revision'], created=row['created'], updated=row['updated'],
                    deleted_at=row['deleted_at'],
                    dataset=dataset, data_ready=bool(dataset and dataset['fingerprint'] == fingerprint(p)))

    def get(self, pid):
        with self.connect() as db:
            row = db.execute('SELECT * FROM problems WHERE id=?', (pid,)).fetchone()
        self.require_active(row)
        return self.document(row)

    def list(self, trashed=False):
        with self.connect() as db:
            rows = db.execute('SELECT * FROM problems WHERE deleted_at IS ' +
                              ('NOT NULL ORDER BY deleted_at DESC' if trashed else 'NULL ORDER BY updated DESC')).fetchall()
        return [{k: p[k] for k in ('id', 'title', 'mode', 'revision', 'updated', 'deleted_at', 'data_ready', 'dataset')}
                for p in map(self.document, rows)]

    def create(self, document=None):
        p, pid, now = validate(document or new_problem()), uuid.uuid4().hex[:12], time.time()
        with self.connect() as db:
            db.execute('INSERT INTO problems (id,document,revision,created,updated) VALUES (?,?,?,?,?)',
                       (pid, json.dumps(p), 1, now, now))
        return self.get(pid)

    def save(self, pid, document):
        p = validate(document)
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT * FROM problems WHERE id=?', (pid,)).fetchone()
            self.require_active(row)
            previous = json.loads(row['document'])
            # Import provenance is server-owned and cannot be forged by a client.
            for key in ('origin_problem_id', 'legacy_text_comparison'):
                if key in previous:
                    p[key] = previous[key]
            dataset = json.loads(row['dataset']) if row['dataset'] else None
            if (dataset and dataset.get('origin') == 'oj'
                    and dataset['fingerprint'] == fingerprint(previous)
                    and all(p[key] == previous[key] for key in ('mode', 'generation'))
                    and effective_programs(p) == effective_programs(previous)
                    and main_solution(p) == main_solution(previous)
                    and is_multipass(p) == is_multipass(previous)
                    and is_testlib_communication(p) == is_testlib_communication(previous)
                    and (not is_multipass(p) or p['validation_passes'] == previous.get('validation_passes', 2))):
                # Existing input/answer pairs do not need generators to change
                # their statement or execution limits.
                dataset.update(fingerprint=fingerprint(p), revision=row['revision'] + 1)
            cur = db.execute('UPDATE problems SET document=?, dataset=?, revision=revision+1, updated=? WHERE id=? AND revision=?',
                             (json.dumps(p), json.dumps(dataset) if dataset else None, time.time(), pid, document.get('revision')))
            if cur.rowcount != 1:
                raise ProblemError('题目已在另一个窗口修改，请重新加载后保存', 409)
        return self.get(pid)

    def set_trashed(self, pid, revision, trashed):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT * FROM problems WHERE id=?', (pid,)).fetchone()
            if row is None:
                raise ProblemError('题目不存在', 404)
            if row['revision'] != revision or (row['deleted_at'] is not None) == trashed:
                raise ProblemError('题目状态已更新，请刷新后重试', 409)
            if trashed and db.execute("SELECT 1 FROM jobs WHERE problem_id=? AND state IN ('queued','running') LIMIT 1", (pid,)).fetchone():
                raise ProblemError('题目还有排队或运行中的任务，请等待结束后删除', 409)
            now = time.time()
            db.execute('UPDATE problems SET deleted_at=?, revision=revision+1, updated=? WHERE id=?',
                       (now if trashed else None, now, pid))
            result = self.document(db.execute('SELECT * FROM problems WHERE id=?', (pid,)).fetchone())
        return result

    def attach_dataset(self, pid, dataset):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT document FROM problems WHERE id=? AND deleted_at IS NULL', (pid,)).fetchone()
            if row is None or fingerprint(json.loads(row[0])) != dataset['fingerprint']:
                return False
            db.execute('UPDATE problems SET dataset=?, updated=? WHERE id=?',
                       (json.dumps(dataset), time.time(), pid))
        return True

    def add_job(self, pid, kind, revision):
        jid, now = uuid.uuid4().hex, time.time()
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT revision, deleted_at FROM problems WHERE id=?', (pid,)).fetchone()
            self.require_active(row)
            if row['revision'] != revision:
                raise ProblemError('题目版本已更新，请先重新加载', 409)
            db.execute('INSERT INTO jobs VALUES (?,?,?,?,?,?,?)',
                       (jid, pid, kind, 'queued', now, now, json.dumps(dict(log=[], progress=0))))
        return jid

    def update_job(self, jid, state=None, **values):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT * FROM jobs WHERE id=?', (jid,)).fetchone()
            payload = json.loads(row['payload'])
            payload.update(values)
            db.execute('UPDATE jobs SET state=?, updated=?, payload=? WHERE id=?',
                       (state or row['state'], time.time(), json.dumps(payload), jid))

    def job(self, jid):
        with self.connect() as db:
            row = db.execute('SELECT * FROM jobs WHERE id=?', (jid,)).fetchone()
        if row is None:
            raise ProblemError('任务不存在', 404)
        return dict(json.loads(row['payload']), id=jid, problem_id=row['problem_id'], kind=row['kind'],
                    state=row['state'], created=row['created'], updated=row['updated'])

    def jobs(self, pid):
        with self.connect() as db:
            ids = [r[0] for r in db.execute('SELECT id FROM jobs WHERE problem_id=? ORDER BY created DESC LIMIT 20', (pid,))]
        return [self.job(jid) for jid in ids]
