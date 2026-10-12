import io
import json
import zipfile

import pytest

from app.config import settings


@pytest.mark.parametrize('language,name,content', [
    ('pypy', 'reference.py', 'import sys\nassert sys.implementation.name == "pypy"\nprint(42)'),
    ('java', 'uploaded.java', 'public class Main { public static void main(String[] args) {} }'),
])
def test_reference_language_survives_save_and_export(client, language, name, content):
    headers = manager_headers(client)
    p = client.post('/api/studio/problems', json={'template': 'normal'}, headers=headers).json()
    p['programs']['reference'] = dict(name=name, language=language, content=content)
    saved = client.put('/api/studio/problems/' + p['id'], json=p, headers=headers)
    assert saved.status_code == 200, saved.text
    assert saved.json()['programs']['reference']['language'] == language
    with zipfile.ZipFile(io.BytesIO(client.get(f"/api/studio/problems/{p['id']}/export").content)) as archive:
        metadata = json.loads(archive.read('problem.json'))
        assert metadata['program_languages']['reference'] == language
        path = metadata['programs']['reference']
        assert archive.read(path).decode() == content
        if language == 'java':
            assert path.endswith('/Main.java')
    p = saved.json()
    p['programs']['checker'] = p['programs']['reference']
    assert client.put('/api/studio/problems/' + p['id'], json=p, headers=headers).status_code == 400


def test_source_language_matches_extension_and_legacy_python_default():
    from app.studio.models import source, ProblemError
    assert source(dict(name='old.py', content='print(42)'))['language'] == 'python'
    assert source(dict(name='Main.java', content='class Main {}'))['language'] == 'java'
    with pytest.raises(ProblemError):
        source(dict(name='main.cpp', language='java', content='class Main {}'))


def test_cleared_team_submissions_stay_cleared_and_new_submissions_sync(client):
    from app import repository as oj
    from app.team import repository as team
    from app.team.integration import sync_all_local, sync_submission
    from app.team.db import init_db
    problem = oj.get_problem_by_slug('sum-two')
    old_id, new_id = 'team-cleared-submission', 'team-new-submission'
    for sid in (old_id, new_id):
        oj.create_submission(submission_id=sid, problem_id=problem['id'], language='cpp', source_code='int main(){}')
    assert sync_submission(old_id)
    with team.connection() as db:
        db.execute('INSERT INTO submission_sync_exclusions VALUES (?,?)', ('oj', old_id))
        db.execute('DELETE FROM submissions WHERE id=?', ('oj-' + old_id,))
    init_db()  # Same migration and backfill order used on a service restart.
    sync_all_local()
    assert team.get_submission('oj-' + old_id) is None
    assert team.get_submission('oj-' + new_id) is not None
    assert oj.get_submission(old_id) is not None
    assert not sync_submission(old_id)


def manager_headers(client):
    bootstrap = client.get('/api/studio/bootstrap')
    assert bootstrap.status_code == 200
    return {'X-CSRF-Token': bootstrap.json()['csrf']}


def test_communication_protocol_save_export_and_data_compatibility(client):
    from app.studio.models import DOMJUDGE_COMMUNICATION, fingerprint, validate
    from app.studio.templates import example

    legacy = example('communication')
    assert fingerprint(legacy) == fingerprint(validate(legacy))
    normal = example('normal')
    assert fingerprint(normal) == fingerprint(validate(normal))
    headers = manager_headers(client)
    created = client.post('/api/studio/problems', json={'template': 'multipass'}, headers=headers)
    assert created.status_code == 200, created.text
    p = created.json()
    assert p['communication_protocol'] == DOMJUDGE_COMMUNICATION
    before = fingerprint(p)
    p['validation_passes'] = 3
    assert fingerprint(p) != before
    saved = client.put('/api/studio/problems/' + p['id'], json=p, headers=headers)
    assert saved.status_code == 200, saved.text
    with zipfile.ZipFile(io.BytesIO(client.get(f"/api/studio/problems/{p['id']}/export").content)) as archive:
        metadata = json.loads(archive.read('problem.json'))
        assert metadata['communication_protocol'] == DOMJUDGE_COMMUNICATION
        assert metadata['validation_passes'] == 3
    p = saved.json()
    for value in (0, 33, 1.5, True):
        p['validation_passes'] = value
        assert client.put('/api/studio/problems/' + p['id'], json=p, headers=headers).status_code == 400


def test_testlib_communication_export_and_protocol_change_invalidate_old_data(client):
    from app.studio.models import TESTLIB_COMMUNICATION, LEGACY_COMMUNICATION, fingerprint
    headers = manager_headers(client)
    created = client.post('/api/studio/problems', json={'template':'testlib-communication'}, headers=headers)
    assert created.status_code == 200, created.text
    p = created.json()
    assert p['communication_protocol'] == TESTLIB_COMMUNICATION
    with zipfile.ZipFile(io.BytesIO(client.get(f"/api/studio/problems/{p['id']}/export").content)) as archive:
        metadata = json.loads(archive.read('problem.json'))
        assert metadata['communication_protocol'] == TESTLIB_COMMUNICATION
        assert archive.read(metadata['programs']['interactor']).decode() == p['programs']['interactor']['content']
    p['communication_protocol'] = LEGACY_COMMUNICATION
    p = client.put('/api/studio/problems/'+p['id'],json=p,headers=headers).json()
    store = client.app.state.studio.store
    dataset = dict(id='old-import',fingerprint=fingerprint(p),revision=p['revision'],cases=[],created=1,bytes=0,origin='oj')
    assert store.attach_dataset(p['id'],dataset)
    assert store.get(p['id'])['data_ready']
    p['communication_protocol'] = TESTLIB_COMMUNICATION
    saved = client.put('/api/studio/problems/'+p['id'],json=p,headers=headers)
    assert saved.status_code == 200, saved.text
    assert not saved.json()['data_ready']
    p = saved.json()
    p['communication_protocol'] = 'unknown-v1'
    assert client.put('/api/studio/problems/'+p['id'],json=p,headers=headers).status_code == 400


def test_module_routes_and_authoring_lifecycle(client):
    assert client.get('/studio/').status_code == 200
    assert client.get('/team/').status_code == 200
    assert '/studio/assets/app.js' in client.get('/studio/').text
    assert '/team/assets/app.js' in client.get('/team/').text
    headers = manager_headers(client)
    assert client.post('/api/studio/problems', json={}).status_code == 403
    assert client.post('/api/studio/problems', json={}, headers={**headers, 'Origin': 'https://foreign.example'}).status_code == 403
    created = client.post('/api/studio/problems', json={'template': 'interactive'}, headers=headers)
    assert created.status_code == 200
    p = created.json()
    p['title'] = '融合测试题'
    saved = client.put('/api/studio/problems/' + p['id'], json=p, headers=headers)
    assert saved.status_code == 200
    assert client.put('/api/studio/problems/' + p['id'], json=p, headers=headers).status_code == 409
    p = saved.json()
    assert client.post(f"/api/studio/problems/{p['id']}/publish", json={'revision': p['revision']}, headers=headers).status_code == 409
    export = client.get(f"/api/studio/problems/{p['id']}/export")
    with zipfile.ZipFile(io.BytesIO(export.content)) as archive:
        assert archive.read('statement.md')
        assert json.loads(archive.read('problem.json'))['mode'] == 'interactive'
    deleted = client.post(f"/api/studio/problems/{p['id']}/trash", json={'revision': p['revision']}, headers=headers).json()
    assert client.get('/api/studio/problems/' + p['id']).status_code == 410
    assert client.post(f"/api/studio/problems/{p['id']}/restore", json={'revision': deleted['revision']}, headers=headers).status_code == 200


def test_shared_role_boundaries(client, monkeypatch):
    monkeypatch.setattr(settings, 'auth_required', True)
    client.cookies.clear()


    assert client.get('/api/studio/problems').status_code == 401
    assert client.get('/api/team/members').status_code == 401
    assert client.get('/studio/', follow_redirects=False).status_code == 303
    from app import repository
    for role, studio, team in [('teacher', 403, 200), ('problem_admin', 200, 403), ('student', 403, 403), ('admin', 200, 200)]:
        name = 'unified-' + role
        repository.create_user(username=name, password='integration-pass', display_name=name, role=role)
        assert client.post('/api/auth/login', json={'username': name, 'password': 'integration-pass'}).status_code == 200
        assert client.get('/api/studio/problems').status_code == studio
        assert client.get('/api/team/members').status_code == team
    client.cookies.clear()


def test_student_submission_ownership(client, monkeypatch):
    from app import repository
    monkeypatch.setattr(settings, 'auth_required', True)
    user = repository.create_user(username='owner-test', password='ownership-pass', role='student')
    problem = repository.get_problem_by_slug('sum-two')
    repository.create_submission(submission_id='owner-only',problem_id=problem['id'],language='cpp',source_code='int main(){}',user_id=user.id)
    assert client.get('/api/submissions/owner-only').status_code==401
    client.post('/api/auth/register', json={'username':'another-student','password':'ownership-pass'})
    assert client.get('/api/submissions/owner-only').status_code==403
    assert all(x['id']!='owner-only' for x in client.get('/api/submissions').json()['items'])
    client.post('/api/auth/login',json={'username':'owner-test','password':'ownership-pass'})
    assert client.get('/api/submissions/owner-only').status_code==200
    client.cookies.clear()


def test_publication_snapshots_preserve_previous_results(client):
    from app import repository
    from app.db import connection
    from app.studio.models import fingerprint
    headers = manager_headers(client)
    p = client.post('/api/studio/problems', json={'template': 'normal'}, headers=headers).json()
    service = client.app.state.studio
    dataset = {'id': 'snapshot-test', 'fingerprint': fingerprint(p), 'cases': [{'id': '001'}]}
    directory = service.jobs.root / dataset['id']
    directory.mkdir()
    (directory / '001.in').write_text('1\n7\n')
    (directory / '001.ans').write_text('7\n')
    assert service.store.attach_dataset(p['id'], dataset)
    published = client.post(f"/api/studio/problems/{p['id']}/publish", json={'revision': p['revision'], 'slug': 'snapshot-publication'}, headers=headers)
    assert published.status_code == 200, published.text
    problem = published.json()['problem']
    assert problem['test_cases'] == []
    assert 'judge_config' not in problem
    before = repository.get_test_cases(problem['id'])
    submission = repository.create_submission(submission_id='snapshot-submission', problem_id=problem['id'], language='cpp', source_code='int main(){}')
    repository.replace_submission_results(submission['id'], [dict(test_case_id=before[0]['id'], verdict='ACCEPTED')])
    assert client.post(f"/api/studio/problems/{p['id']}/publish", json={'revision': p['revision']}, headers=headers).status_code == 200
    after = repository.get_test_cases(problem['id'])
    assert after[0]['id'] != before[0]['id']
    old = repository.get_submission(submission['id'])
    assert old['results'][0]['test_case_id'] == before[0]['id']
    assert json.loads(old['judge_snapshot'])['case_ids'] == [before[0]['id']]
    # The private checker code is not part of the public statement response.
    assert 'registerTestlibCmd' not in client.get('/api/problems/snapshot-publication').text
