import io
import json
import uuid
import zipfile
from concurrent.futures import ThreadPoolExecutor

import pytest

from app import catalog, repository
from app.config import settings
from app.db import connection
from app.studio.catalog_sync import ensure_oj_documents
from app.studio.engine import Engine


@pytest.fixture
def manager(client, monkeypatch):
    monkeypatch.setattr(settings, 'auth_required', True)
    client.cookies.clear()
    response = client.post('/api/auth/login', json={
        'username': settings.admin_username, 'password': settings.admin_password,
    })
    assert response.status_code == 200
    headers = {'X-CSRF-Token': client.get('/api/studio/bootstrap').json()['csrf']}
    yield headers
    client.cookies.clear()


def create_legacy(client, **changes):
    payload = dict(slug='legacy-' + uuid.uuid4().hex[:10], title='原有题目',
                   statement_markdown='请输出答案。', input_format='一行输入。', output_format='一行输出。',
                   difficulty='入门', time_limit_ms=1000, memory_limit_mb=256,
                   test_cases=[
                       dict(name='公开样例', input_data='1 2\r\n', expected_output='\n3 \t\r\n', is_sample=True, weight=3),
                       dict(name='隐藏数据', input_data='100 23\n', expected_output='123\n', weight=7),
                   ])
    payload.update(changes)
    response = client.post('/api/problems', json=payload)
    assert response.status_code == 201, response.text
    problem = response.json()
    entry = catalog.lookup(problem['problem_code'])
    draft = client.get('/api/studio/problems/' + entry['studio_id']).json()
    return problem, draft


def test_admin_can_edit_every_bank_problem_and_read_original_data(client, manager):
    bank = client.get('/api/problem-bank').json()['items']
    drafts = client.get('/api/studio/problems').json()['problems']
    by_code = {draft['problem_code']: draft for draft in drafts}
    for entry in bank:
        if entry['problem_id'] is None:
            continue
        assert entry['studio_url']
        assert entry['problem_code'] in by_code
        draft = client.get('/api/studio/problems/' + entry['studio_id']).json()
        original = repository.get_problem_by_id(entry['problem_id'], include_hidden=True)
        assert draft['publication']['problem_id'] == original['id']
        assert draft['problem_code'] == original['problem_code']
        assert draft['data_ready']
        assert '输入格式' in draft['statement'] and '输出格式' in draft['statement']
        for case, entry in zip(original['test_cases'], draft['dataset']['cases'], strict=True):
            assert entry['is_sample'] == case['is_sample'] and entry['weight'] == case['weight']
            for suffix, field in (('in', 'input_data'), ('ans', 'expected_output')):
                response = client.get(f"/api/studio/problems/{draft['id']}/cases/{entry['id']}.{suffix}?download=1")
                assert response.content == case[field].encode()


def test_late_created_problem_is_linked_and_sync_never_overwrites_edits(client, manager):
    original, draft = create_legacy(client, time_limit_ms=30000, memory_limit_mb=16)
    draft.update(title='管理员修改后的草稿', time_ms=25000, memory_mb=32,
                 origin_problem_id=999999, legacy_text_comparison=False)
    saved = client.put('/api/studio/problems/' + draft['id'], json=draft, headers=manager).json()
    assert saved['title'] == draft['title'] and saved['data_ready']
    assert saved['origin_problem_id'] == original['id'] and saved['legacy_text_comparison']
    before = client.app.state.studio.store.list()
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: ensure_oj_documents(client.app.state.studio.store), range(8)))
    assert all(result == [] for result in results)
    assert client.app.state.studio.store.list() == before
    assert client.get('/api/studio/problems/' + draft['id']).json() == saved
    assert client.get('/api/problems/' + original['slug']).json() == original


def test_republish_preserves_identity_difficulty_samples_weights_and_history(client, manager):
    original, draft = create_legacy(client)
    old_cases = repository.get_test_cases(original['id'])
    sid = 'legacy-snapshot-' + uuid.uuid4().hex
    repository.create_submission(submission_id=sid, problem_id=original['id'], language='cpp', source_code='int main(){}')
    before_submission = repository.get_submission(sid)
    draft.update(title='原题更新', statement=draft['statement'] + '\n\n## 说明\n更新说明。', time_ms=1200)
    saved = client.put('/api/studio/problems/' + draft['id'], json=draft, headers=manager).json()
    assert saved['data_ready']
    response = client.post(f"/api/studio/problems/{draft['id']}/publish", json={'revision': saved['revision']}, headers=manager)
    assert response.status_code == 200, response.text
    published = response.json()['problem']
    assert published['title'] == '原题更新' and published['time_limit_ms'] == 1200
    for key in ('id', 'slug', 'problem_code', 'difficulty'):
        assert published[key] == original[key]
    new_cases = repository.get_test_cases(original['id'])
    assert [{k: v for k, v in case.items() if k != 'id'} for case in new_cases] == [
        {k: v for k, v in case.items() if k != 'id'} for case in old_cases]
    assert len(published['test_cases']) == 1 and published['test_cases'][0]['name'] == '公开样例'
    after_submission = repository.get_submission(sid)
    assert after_submission['problem_title'] == published['title']
    assert {k: v for k, v in after_submission.items() if k != 'problem_title'} == {
        k: v for k, v in before_submission.items() if k != 'problem_title'}
    with connection() as db:
        snapshot = json.loads(db.execute('SELECT judge_snapshot FROM submissions WHERE id=?', (sid,)).fetchone()[0])
        assert snapshot['case_ids'] == [case['id'] for case in old_cases]
        assert all(db.execute('SELECT active FROM test_cases WHERE id=?', (case['id'],)).fetchone()[0] == 0 for case in old_cases)
    exported = client.get(f"/api/studio/problems/{draft['id']}/export")
    with zipfile.ZipFile(io.BytesIO(exported.content)) as archive:
        assert archive.read('tests/001.in') == old_cases[0]['input_data'].encode()
        assert archive.read('tests/001.ans') == old_cases[0]['expected_output'].encode()


def test_unlisting_and_trashing_do_not_remove_admin_access_or_recreate_drafts(client, manager):
    original, draft = create_legacy(client)
    assert client.delete('/api/problem-bank/' + original['problem_code']).status_code == 204
    assert any(p['id'] == draft['id'] for p in client.get('/api/studio/problems').json()['problems'])
    assert client.get('/api/problems/' + original['slug']).status_code == 404
    trashed = client.post(f"/api/studio/problems/{draft['id']}/trash", json={'revision': draft['revision']}, headers=manager).json()
    assert ensure_oj_documents(client.app.state.studio.store) == []
    assert all(p['id'] != draft['id'] for p in client.get('/api/studio/problems').json()['problems'])
    assert any(p['id'] == draft['id'] for p in client.get('/api/studio/trash').json()['problems'])
    restored = client.post(f"/api/studio/problems/{draft['id']}/restore", json={'revision': trashed['revision']}, headers=manager).json()
    assert restored['problem_code'] == original['problem_code'] and restored['data_ready']


def test_import_does_not_grant_student_or_teacher_access_to_hidden_data(client, manager):
    _, draft = create_legacy(client)
    for role in ('student', 'teacher'):
        username = 'catalog-' + role
        assert client.post('/api/users', json={'username': username, 'password': 'catalog-test-pass', 'role': role}).status_code == 201
    for role in ('student', 'teacher', None):
        client.cookies.clear()
        if role:
            assert client.post('/api/auth/login', json={'username': 'catalog-' + role, 'password': 'catalog-test-pass'}).status_code == 200
        for path in ('/api/problem-bank', '/api/studio/problems', '/api/studio/problems/' + draft['id'],
                     f"/api/studio/problems/{draft['id']}/cases/002.ans", f"/api/studio/problems/{draft['id']}/export"):
            assert client.get(path).status_code == (403 if role else 401)


def test_legacy_comparison_preserves_spaces_and_requires_regeneration_for_program_changes(client, manager, monkeypatch):
    _, draft = create_legacy(client, test_cases=[dict(name='空白比较', input_data='x', expected_output='\u20031  2 \t\r\n\r\n')])
    jobs = client.app.state.studio.jobs

    class Runner:
        output = b'1  2\n'
        def compile(self, *args): return object()
        def limits(self, *args): return {}
        def run(self, *args, **kwargs): return dict(verdict='OK', output=self.output, time_ms=1, memory_kb=1)
        summary = staticmethod(Engine.summary)

    runner = Runner()
    monkeypatch.setattr(jobs, 'engine', runner)
    for output, expected in ((b'1  2\n', 'AC'), (b'1 2\n', 'WA')):
        runner.output = output
        reports = []
        jobs.judge(draft, {'solution': {}}, lambda *args, **values: reports.append(values))
        assert reports[-1]['verdict'] == expected
    draft['generation'] = '100 1'
    saved = client.put('/api/studio/problems/' + draft['id'], json=draft, headers=manager).json()
    assert not saved['data_ready']
    saved['title'] = '只改题面也不能使失效数据重新有效'
    saved = client.put('/api/studio/problems/' + draft['id'], json=saved, headers=manager).json()
    assert not saved['data_ready']
    created = client.post('/api/studio/problems', json={'problem': {'title': '伪造来源', 'origin_problem_id': 1, 'legacy_text_comparison': True}}, headers=manager).json()
    assert 'origin_problem_id' not in created and 'legacy_text_comparison' not in created
