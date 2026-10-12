"""Ordered papers reference Studio problems, without duplicating their contents."""
import json
import time
import uuid

from .models import ProblemError
from ..catalog import decorate_documents, lookup


class Papers:
    def __init__(self, store):
        self.store = store
        with store.connect() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS papers (
                id TEXT PRIMARY KEY, document TEXT NOT NULL, revision INTEGER NOT NULL,
                created REAL NOT NULL, updated REAL NOT NULL)''')

    def validate(self, data):
        title, description = data.get('title', '未命名试卷'), data.get('description', '')
        if not isinstance(title, str) or not title.strip() or len(title) > 120:
            raise ProblemError('试卷名称须为 1～120 个字符')
        if not isinstance(description, str) or len(description.encode()) > 32768:
            raise ProblemError('试卷说明不能超过 32 KiB')
        ids = data.get('problem_ids', [])
        if 'problem_codes' in data:
            codes = data['problem_codes']
            if not isinstance(codes, list) or len(codes) > 100:
                raise ProblemError('每套试卷最多包含 100 道题')
            ids = []
            for code in codes:
                try:
                    row = lookup(code)
                except ValueError as exc:
                    raise ProblemError(str(exc)) from exc
                if not row or not row['studio_id']:
                    raise ProblemError(f'题目 ID {code} 不存在')
                ids.append(row['studio_id'])
        if not isinstance(ids, list) or len(ids) > 100 or not all(isinstance(i, str) for i in ids):
            raise ProblemError('每套试卷最多包含 100 道题')
        if len(ids) != len(set(ids)):
            raise ProblemError('同一套试卷不能重复添加题目')
        return dict(title=title.strip(), description=description, problem_ids=ids)

    @staticmethod
    def active_ids(db, ids):
        for pid in ids:
            row = db.execute('SELECT deleted_at FROM problems WHERE id=?', (pid,)).fetchone()
            if row is None or row['deleted_at'] is not None:
                raise ProblemError('试卷中有不存在或已删除的题目，请先恢复或移除', 409)

    def document(self, row):
        if row is None:
            raise ProblemError('试卷不存在', 404)
        paper = dict(json.loads(row['document']), id=row['id'], revision=row['revision'],
                     created=row['created'], updated=row['updated'])
        items = []
        with self.store.connect() as db:
            for pid in paper['problem_ids']:
                problem = db.execute('SELECT * FROM problems WHERE id=?', (pid,)).fetchone()
                if problem is None:
                    items.append(dict(id=pid, title='题目不存在', missing=True, data_ready=False))
                else:
                    p = self.store.document(problem)
                    items.append({k: p[k] for k in ('id', 'title', 'mode', 'revision', 'data_ready', 'deleted_at')})
        paper['problems'] = decorate_documents(items)
        return paper

    def list(self):
        with self.store.connect() as db:
            rows = db.execute('SELECT * FROM papers ORDER BY updated DESC').fetchall()
        return [self.document(row) for row in rows]

    def get(self, pid):
        with self.store.connect() as db:
            row = db.execute('SELECT * FROM papers WHERE id=?', (pid,)).fetchone()
        return self.document(row)

    def create(self, data):
        document, pid, now = self.validate(data), uuid.uuid4().hex[:12], time.time()
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            self.active_ids(db, document['problem_ids'])
            db.execute('INSERT INTO papers VALUES (?,?,?,?,?)', (pid, json.dumps(document), 1, now, now))
        return self.get(pid)

    def save(self, pid, data):
        document = self.validate(data)
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            if not db.execute('SELECT 1 FROM papers WHERE id=?', (pid,)).fetchone():
                raise ProblemError('试卷不存在', 404)
            self.active_ids(db, document['problem_ids'])
            changed = db.execute('UPDATE papers SET document=?, revision=revision+1, updated=? WHERE id=? AND revision=?',
                                 (json.dumps(document), time.time(), pid, data.get('revision')))
            if changed.rowcount != 1:
                raise ProblemError('试卷已在另一个窗口修改，请重新加载后保存', 409)
        return self.get(pid)

    def delete(self, pid, revision):
        with self.store.connect() as db:
            if db.execute('DELETE FROM papers WHERE id=? AND revision=?', (pid, revision)).rowcount != 1:
                raise ProblemError('试卷状态已更新，请刷新后重试', 409)
        return dict(deleted=True)
