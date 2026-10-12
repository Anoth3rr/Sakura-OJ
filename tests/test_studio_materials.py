"""Persistence, compatibility, permissions and ordered authoring bundles."""
import io
import json
import zipfile
from types import SimpleNamespace

import pytest

from app.config import settings
from app.studio.models import ProblemError, Store, effective_programs, fingerprint, validate
from app.studio.templates import example
from .test_unified import manager_headers


def solution(tag='correct', code='print(0)', **values):
    return dict(name='main.py', language='python', content=code, tag=tag, **values)


def test_main_correct_and_extra_solutions_have_different_data_dependencies(tmp_path):
    store = Store(tmp_path)
    p = store.create(example('normal'))
    original = fingerprint(p)
    std = dict(p['programs']['reference'], tag='main-correct')
    p['solutions'] = [std, solution('wrong')]
    p = store.save(p['id'], p)
    assert fingerprint(p) == original  # Migrating the same std preserves already generated data.
    dataset = dict(id='snapshot', fingerprint=original, cases=[], revision=p['revision'], bytes=0, created=1)
    assert store.attach_dataset(p['id'], dataset)
    p['solutions'][1].update(content='print(-1)', tag='time-limit')
    p = store.save(p['id'], p)
    assert p['data_ready']
    p['solutions'][0]['content'] += '\n// new std\n'
    p = store.save(p['id'], p)
    assert not p['data_ready']
    assert effective_programs(p)['reference']['content'] == p['solutions'][0]['content']
    assert Store(tmp_path).get(p['id'])['solutions'] == p['solutions']


@pytest.mark.parametrize('change', ['duplicate-id', 'two-main', 'bad-tag', 'bad-id', 'too-many', 'bad-language', 'bad-receiver'])
def test_rejects_invalid_solution_lists(change):
    p = example('normal')
    p['solutions'] = [solution(id='a'*12), solution(id='b'*12)]
    if change == 'duplicate-id':
        p['solutions'][1]['id'] = 'a'*12
    elif change == 'two-main':
        for s in p['solutions']:
            s['tag'] = 'main-correct'
    elif change == 'bad-tag':
        p['solutions'][0]['tag'] = 'accepted-maybe'
    elif change == 'bad-id':
        p['solutions'][0]['id'] = '../solution'
    elif change == 'too-many':
        p['solutions'] = [solution() for _ in range(33)]
    elif change == 'bad-language':
        p['solutions'][0]['language'] = 'java'
    elif change == 'bad-receiver':
        p['solutions'][0]['receiver'] = solution()
    with pytest.raises(ProblemError):
        validate(p)


def test_solution_languages_labels_receiver_save_export(client):
    headers = manager_headers(client)
    p = client.post('/api/studio/problems', json={'template':'communication'}, headers=headers).json()
    p['solutions'] = [dict(name='send.py', content='print(1)', language='pypy', tag='main-correct',
                           receiver=dict(name='uploaded.java', language='java', content='public class Main {}')),
                      solution('wrong')]
    response = client.put('/api/studio/problems/'+p['id'], json=p, headers=headers)
    assert response.status_code == 200, response.text
    saved = response.json()
    assert len({s['id'] for s in saved['solutions']}) == 2
    assert saved['solutions'][0]['receiver']['language'] == 'java'
    stale = client.put('/api/studio/problems/'+p['id'], json=p, headers=headers)
    assert stale.status_code == 409
    with zipfile.ZipFile(io.BytesIO(client.get(f"/api/studio/problems/{p['id']}/export").content)) as archive:
        metadata = json.loads(archive.read('problem.json'))
        item = metadata['solutions'][0]
        assert item['language'] == 'pypy' and item['tag'] == 'main-correct'
        assert archive.read(item['path']).decode() == 'print(1)'
        assert item['receiver']['path'].endswith('/Main.java')
        assert archive.read(item['receiver']['path']).decode() == 'public class Main {}'
        assert 'content' not in item


@pytest.mark.parametrize('mode', ['normal','interactive','communication','multipass','testlib-communication'])
def test_generation_requires_main_correct_once_solutions_are_added(client, monkeypatch, mode):
    headers = manager_headers(client)
    p = client.post('/api/studio/problems', json={'template':mode}, headers=headers).json()
    assert p['programs'].get('reference')
    p['solutions'] = [solution('wrong')]
    p = client.put('/api/studio/problems/'+p['id'], json=p, headers=headers).json()
    monkeypatch.setattr(client.app.state.studio.jobs, 'engine', SimpleNamespace(health=lambda:dict(ready=True)))
    response = client.post(f"/api/studio/problems/{p['id']}/generate", json={'revision':p['revision']}, headers=headers)
    assert response.status_code == 400 and 'Main Correct' in response.text


def test_paper_order_codes_preview_export_delete_and_concurrent_edits(client):
    headers = manager_headers(client)
    problems = [client.post('/api/studio/problems', json={'template':m}, headers=headers).json()
                for m in ('normal', 'interactive')]
    response = client.post('/api/studio/papers', json={'title':'第一套训练卷', 'description':'## 说明\n逐题完成',
                                                    'problem_codes':[p['problem_code'] for p in problems]}, headers=headers)
    assert response.status_code == 200, response.text
    paper = response.json()
    assert paper['problem_ids'] == [p['id'] for p in problems]
    assert paper['problems'][0]['problem_code'] == problems[0]['problem_code']
    paper['problem_ids'].reverse()
    response = client.put('/api/studio/papers/'+paper['id'], json=paper, headers=headers)
    assert response.status_code == 200, response.text
    assert client.put('/api/studio/papers/'+paper['id'], json=paper, headers=headers).status_code == 409
    paper = response.json()
    assert client.get('/api/studio/papers/'+paper['id']).json()['problem_ids'] == paper['problem_ids']
    p = problems[1]
    p.update(title='题目修改后整卷同步', statement='# 最新题面\n内容')
    assert client.put('/api/studio/problems/'+p['id'], json=p, headers=headers).status_code == 200
    preview = client.get('/api/studio/papers/'+paper['id']+'/preview').json()
    assert preview['problems'][0]['title'] == p['title']
    assert 'programs' not in preview['problems'][0]
    exported = client.get('/api/studio/papers/'+paper['id']+'/export')
    assert exported.status_code == 200, exported.text
    with zipfile.ZipFile(io.BytesIO(exported.content)) as archive:
        metadata = json.loads(archive.read('paper.json'))
        assert [x['id'] for x in metadata['problems']] == paper['problem_ids']
        assert metadata['problems'][0]['path'].startswith('01-')
        assert archive.read(metadata['problems'][0]['path']+'statement.md').decode() == p['statement']
        assert '# 最新题面' in archive.read('statement.md').decode()
    deleted = client.post('/api/studio/papers/'+paper['id']+'/delete', json={'revision':paper['revision']}, headers=headers)
    assert deleted.status_code == 200
    assert client.get('/api/studio/papers/'+paper['id']).status_code == 404
    assert all(client.get('/api/studio/problems/'+p['id']).status_code == 200 for p in problems)


def test_paper_rejects_duplicates_missing_deleted_and_tracks_restore(client):
    headers = manager_headers(client)
    p = client.post('/api/studio/problems', json={}, headers=headers).json()
    for body in ({'problem_ids':[p['id']]*2}, {'problem_codes':['999999999999']}, {'problem_codes':['../x']},
                 {'problem_ids':['f'*12]}, {'title':''}):
        assert client.post('/api/studio/papers', json=body, headers=headers).status_code in (400,409)
    paper = client.post('/api/studio/papers', json={'problem_ids':[p['id']]}, headers=headers).json()
    trash = client.post('/api/studio/problems/'+p['id']+'/trash', json={'revision':p['revision']}, headers=headers).json()
    read = client.get('/api/studio/papers/'+paper['id']).json()
    assert read['problems'][0]['deleted_at']
    assert client.get('/api/studio/papers/'+paper['id']+'/export').status_code == 410
    assert client.put('/api/studio/papers/'+paper['id'], json=paper, headers=headers).status_code == 409
    assert client.post('/api/studio/problems/'+p['id']+'/restore', json={'revision':trash['revision']}, headers=headers).status_code == 200
    assert client.get('/api/studio/papers/'+paper['id']+'/export').status_code == 200


def test_materials_manager_permission_and_csrf(client, monkeypatch):
    headers = manager_headers(client)
    assert client.post('/api/studio/papers', json={}).status_code == 403
    monkeypatch.setattr(settings, 'auth_required', True)
    client.cookies.clear()
    assert client.get('/api/studio/papers').status_code == 401
    from app import repository
    repository.create_user(username='materials-student', password='materials-pass', display_name='Student', role='student')
    assert client.post('/api/auth/login', json={'username':'materials-student','password':'materials-pass'}).status_code == 200
    for path, method in (('/api/studio/papers','GET'), ('/api/studio/papers','POST'),
                         ('/api/studio/problems/'+'a'*12+'/invoke','POST')):
        assert client.request(method,path,json={} if method=='POST' else None,headers=headers).status_code == 403
    client.cookies.clear()
