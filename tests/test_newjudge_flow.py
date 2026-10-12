"""Opt-in end-to-end tests; all code executes in real lrun as a non-root user."""
import json
import os
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.studio.templates import candidate
from app.team.config import settings as team_settings
from .newjudge_programs import candidate as managed_candidate, java_main

pytestmark = pytest.mark.skipif(os.getenv('SAKURA_REAL_JUDGE') != '1', reason='需要真实 Linux lrun 环境')


def wait(client, url, state_key, end_states, timeout=160):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        response = client.get(url)
        assert response.status_code == 200, response.text
        result = response.json()
        if result[state_key] in end_states:
            return result
        time.sleep(0.1)
    raise AssertionError(result)


@pytest.fixture(scope='module')
def merged(tmp_path_factory):
    root = tmp_path_factory.mktemp('sakura-real')
    changes = dict(database_path=root/'oj.sqlite3', runtime_dir=root/'local', newjudge_work=root/'sandbox',
                   studio_root=root/'studio', judge_mode='newjudge', auth_required=True,
                   admin_username='integration-admin', admin_password='integration-pass')
    before = {k: getattr(settings, k) for k in changes}
    before_team = team_settings._database_path
    for k,v in changes.items():
        setattr(settings,k,v)
    team_settings._database_path = root/'team.sqlite3'
    try:
        with TestClient(app) as client:
            assert client.get('/health').json()['judge']['ready']
            def login(role='admin'):
                name = 'integration-admin' if role=='admin' else 'integration-student'
                assert client.post('/api/auth/login', json={'username': name, 'password':'integration-pass'}).status_code==200
            assert client.post('/api/auth/register', json={'username':'integration-student','password':'integration-pass'}).status_code==201
            login()
            member = client.post('/api/team/members', json={'name':'自动归属测试','oj_username':'integration-student'}).json()
            headers = {'X-CSRF-Token':client.get('/api/studio/bootstrap').json()['csrf']}
            yield client, headers, login, member
    finally:
        team_settings._database_path = before_team
        for k,v in before.items():
            setattr(settings,k,v)


def test_legacy_problem_can_be_edited_trialed_republished_and_judged(merged):
    client, headers, login, _ = merged
    login()
    response = client.post('/api/problems', json={
        'slug': 'legacy-catalog-roundtrip', 'title': '原有两数和',
        'statement_markdown': '输出两数之和。', 'input_format': '两个整数。', 'output_format': '它们的和。',
        'test_cases': [
            {'name': '公开样例', 'input_data': '1 2\n', 'expected_output': '\n  3 \t\r\n', 'is_sample': True, 'weight': 3},
            {'name': '隐藏数据', 'input_data': '100 23\n', 'expected_output': '123\n', 'weight': 7},
        ],
    })
    assert response.status_code == 201, response.text
    original = response.json()
    entry = client.get('/api/problem-bank', params={'search': original['problem_code']}).json()['items'][0]
    p = client.get('/api/studio/problems/' + entry['studio_id']).json()
    assert p['data_ready'] and not p['programs']
    p.update(title='原有题目更新', time_ms=1200)
    saved = client.put('/api/studio/problems/' + p['id'], json=p, headers=headers)
    assert saved.status_code == 200, saved.text
    p = saved.json()
    assert p['data_ready']
    correct = '#include <iostream>\nint main(){long long a,b;std::cin>>a>>b;std::cout<<a+b<<"\\n";}'
    wrong = '#include <iostream>\nint main(){std::cout<<-123;}'
    for code, verdict in ((correct, 'AC'), (wrong, 'WA')):
        response = client.post(f"/api/studio/problems/{p['id']}/submit", json={
            'revision': p['revision'], 'solution': {'name': 'main.cpp', 'content': code, 'language': 'cpp'},
        }, headers=headers)
        assert response.status_code == 200, response.text
        trial = wait(client, '/api/studio/jobs/' + response.json()['id'], 'state', ('done', 'failed'))
        assert trial['state'] == 'done' and trial['verdict'] == verdict, trial
        assert len(trial['cases']) == 2
    published = client.post(f"/api/studio/problems/{p['id']}/publish", json={'revision': p['revision']}, headers=headers)
    assert published.status_code == 200, published.text
    problem = published.json()['problem']
    for key in ('id', 'problem_code', 'slug', 'difficulty'):
        assert problem[key] == original[key]
    assert len(problem['test_cases']) == 1 and problem['test_cases'][0]['name'] == '公开样例'
    login('student')
    for code, verdict in ((correct, 'ACCEPTED'), (wrong, 'WRONG_ANSWER')):
        submitted = client.post('/api/submissions', json={'problem_id': problem['id'], 'language': 'cpp', 'source_code': code})
        assert submitted.status_code == 202, submitted.text
        result = wait(client, '/api/submissions/' + submitted.json()['id'], 'status', ('COMPLETED',))
        assert result['verdict'] == verdict, result
        assert len(result['results']) == 2


@pytest.mark.parametrize('mode', ['normal','interactive','communication'])
def test_author_generate_publish_student_judge_team(merged, mode):
    client, headers, login, member = merged
    login()
    response = client.post('/api/studio/problems', json={'template':mode}, headers=headers)
    assert response.status_code==200, response.text
    p=response.json()
    p['generation']='3 100 1\n7 1000 2'
    if mode=='interactive':
        del p['programs']['checker']
        del p['programs']['reference']
    p=client.put('/api/studio/problems/'+p['id'], json=p, headers=headers).json()
    response=client.post(f"/api/studio/problems/{p['id']}/generate",json={'revision':p['revision']},headers=headers)
    assert response.status_code==200,response.text
    job=wait(client,'/api/studio/jobs/'+response.json()['id'],'state',('done','failed'))
    assert job['state']=='done',job
    published=client.post(f"/api/studio/problems/{p['id']}/publish",json={'revision':p['revision'],'slug':'real-'+mode},headers=headers)
    assert published.status_code==200,published.text
    problem=published.json()['problem']
    assert problem['judge_mode']==mode
    assert problem['test_cases']==[]
    login('student')
    assert client.get('/api/studio/problems/'+p['id']).status_code==403
    response=client.post('/api/submissions',json={'problem_slug':problem['slug'],'language':'cpp','source_code':candidate(mode)['content']})
    assert response.status_code==202,response.text
    result=wait(client,'/api/submissions/'+response.json()['id'],'status',('COMPLETED',))
    assert result['verdict']=='ACCEPTED',result
    assert len(result['results'])==2
    assert result['memory_kb']>0
    if mode=='communication':
        assert all(0<r['message_bytes']<=32 for r in result['results'])
    login()
    team=client.get('/api/team/submissions',params={'member_id':member['id'],'platform':'oj'}).json()
    assert any(r['external_id']==result['id'] and r['verdict']=='ACCEPTED' for r in team['items']),team
    # Mutating the draft invalidates its data but not the released OJ snapshot.
    draft=client.get('/api/studio/problems/'+p['id']).json()
    draft['time_ms']=1200
    client.put('/api/studio/problems/'+p['id'],json=draft,headers=headers)
    assert client.post(f"/api/studio/problems/{p['id']}/publish",json={'revision':draft['revision']+1},headers=headers).status_code==409
    from app import repository
    assert json.loads(repository.get_problem_by_id(problem['id'],include_hidden=True)['judge_config'])['time_ms']==1000


@pytest.mark.parametrize('language,source', [('python','a,b=map(int,input().split()); print(a+b)'),
    ('pypy','import sys; assert sys.implementation.name == "pypy"; a,b=map(int,input().split()); print(a+b)'),
    ('java',java_main('java.util.Scanner s=new java.util.Scanner(System.in); System.out.println(s.nextLong()+s.nextLong());')),
    ('c','#include <stdio.h>\nint main(){long long a,b;scanf("%lld%lld",&a,&b);printf("%lld\\n",a+b);}'),
    ('cpp','#include <iostream>\nint main(){long long a,b;std::cin>>a>>b;std::cout<<a+b;}')])
def test_existing_ordinary_problem_uses_newjudge(merged,language,source):
    client,_,login,_=merged
    login('student')
    created=client.post('/api/submissions',json={'problem_slug':'sum-two','language':language,'source_code':source})
    assert created.status_code==202,created.text
    result=wait(client,'/api/submissions/'+created.json()['id'],'status',('COMPLETED',))
    assert result['verdict']=='ACCEPTED',result


@pytest.mark.parametrize('slug,source,expected', [
    ('real-normal','print(0)','WRONG_ANSWER'),
    ('real-interactive','while True: pass','TIME_LIMIT_EXCEEDED'),
    ('real-interactive','input(); a=list(map(int,input().split())); print(sum(a),flush=True); raise RuntimeError("after answer")','RUNTIME_ERROR'),
    ('real-communication','print("x"*33)','COMMUNICATION_LIMIT_EXCEEDED'),
    ('sum-two','def broken(:','COMPILE_ERROR'),
])
def test_failure_verdicts_reach_oj(merged,slug,source,expected):
    client,_,login,_=merged
    login('student')
    response=client.post('/api/submissions',json={'problem_slug':slug,'language':'python','source_code':source})
    assert response.status_code==202,response.text
    result=wait(client,'/api/submissions/'+response.json()['id'],'status',('COMPLETED',))
    assert result['verdict']==expected,result


@pytest.mark.parametrize('language', ['pypy', 'java'])
@pytest.mark.parametrize('mode', ['normal', 'interactive', 'communication'])
def test_managed_languages_authoring_to_student(merged, language, mode):
    client, headers, login, member = merged
    login()
    catalog = {entry['id']: entry for entry in client.get('/api/languages').json()}
    assert catalog[language]['available']
    p = client.post('/api/studio/problems', json={'template': mode}, headers=headers).json()
    p['generation'] = '3 100 1\n7 1000 2'
    # Reference generation and Studio trial must retain PyPy instead of inferring CPython from .py.
    p['programs']['reference'] = managed_candidate(language, mode)
    response = client.put('/api/studio/problems/' + p['id'], json=p, headers=headers)
    assert response.status_code == 200, response.text
    p = response.json()
    assert p['programs']['reference']['language'] == language
    response = client.post(f"/api/studio/problems/{p['id']}/generate", json={'revision': p['revision']}, headers=headers)
    assert response.status_code == 200, response.text
    generated = wait(client, '/api/studio/jobs/' + response.json()['id'], 'state', ('done', 'failed'))
    assert generated['state'] == 'done', generated
    solution = managed_candidate(language, mode)
    response = client.post(f"/api/studio/problems/{p['id']}/submit",
                           json={'revision': p['revision'], 'solution': solution}, headers=headers)
    assert response.status_code == 200, response.text
    trial = wait(client, '/api/studio/jobs/' + response.json()['id'], 'state', ('done', 'failed'))
    assert trial['verdict'] == 'AC', trial
    assert len(trial['cases']) == 2
    if mode == 'communication':
        # Independent receiver can use a different language from the sender.
        other = 'java' if language == 'pypy' else 'pypy'
        response = client.post(f"/api/studio/problems/{p['id']}/submit", json={
            'revision': p['revision'], 'solution': solution, 'receiver': managed_candidate(other, mode)}, headers=headers)
        mixed = wait(client, '/api/studio/jobs/' + response.json()['id'], 'state', ('done', 'failed'))
        assert mixed['verdict'] == 'AC', mixed
    slug = f'managed-{language}-{mode}'
    published = client.post(f"/api/studio/problems/{p['id']}/publish",
                            json={'revision': p['revision'], 'slug': slug}, headers=headers)
    assert published.status_code == 200, published.text
    login('student')
    response = client.post('/api/submissions', json={'problem_slug': slug, 'language': language, 'source_code': solution['content']})
    assert response.status_code == 202, response.text
    result = wait(client, '/api/submissions/' + response.json()['id'], 'status', ('COMPLETED',))
    assert result['verdict'] == 'ACCEPTED', result
    assert len(result['results']) == 2 and result['memory_kb'] > 0
    if mode == 'communication':
        assert all(0 < r['message_bytes'] <= 32 for r in result['results'])
    login()
    team = client.get('/api/team/submissions', params={'member_id': member['id'], 'platform': 'oj'}).json()
    assert any(r['external_id'] == result['id'] and r['verdict'] == 'ACCEPTED' for r in team['items'])


@pytest.mark.parametrize('language,source,slug,expected', [
    ('pypy', 'def broken(:', 'sum-two', 'COMPILE_ERROR'),
    ('pypy', 'return 42', 'sum-two', 'COMPILE_ERROR'),
    ('java', 'public class Main { broken }', 'sum-two', 'COMPILE_ERROR'),
    ('java', 'class WrongName {}', 'sum-two', 'COMPILE_ERROR'),
    ('pypy', 'raise RuntimeError("managed error")', 'sum-two', 'RUNTIME_ERROR'),
    ('java', java_main('throw new RuntimeException("managed error");'), 'sum-two', 'RUNTIME_ERROR'),
    ('pypy', 'print(0)', 'sum-two', 'WRONG_ANSWER'),
    ('java', java_main('System.out.println(0);'), 'sum-two', 'WRONG_ANSWER'),
    ('pypy', 'while True: pass', 'real-interactive', 'TIME_LIMIT_EXCEEDED'),
    ('java', java_main('while (true) {}'), 'real-interactive', 'TIME_LIMIT_EXCEEDED'),
    ('pypy', 'input(); a=list(map(int,input().split())); print(sum(a),flush=True); raise RuntimeError("after answer")', 'real-interactive', 'RUNTIME_ERROR'),
    ('java', java_main('java.util.Scanner in=new java.util.Scanner(System.in); int n=in.nextInt(); long s=0; while(n-->0)s+=in.nextLong(); System.out.println(s); System.out.flush(); throw new RuntimeException("after answer");'), 'real-interactive', 'RUNTIME_ERROR'),
    ('pypy', 'print("x" * 33)', 'real-communication', 'COMMUNICATION_LIMIT_EXCEEDED'),
    ('java', java_main('System.out.println("x".repeat(33));'), 'real-communication', 'COMMUNICATION_LIMIT_EXCEEDED'),
    ('pypy', 'a=[]\nwhile True: a.append(bytearray(1024*1024))', 'sum-two', 'MEMORY_LIMIT_EXCEEDED'),
    ('java', java_main('java.util.List<byte[]> a=new java.util.ArrayList<>(); while(true) a.add(new byte[1024*1024]);'), 'sum-two', 'MEMORY_LIMIT_EXCEEDED'),
    ('pypy', 'while True: print("x"*65536)', 'sum-two', 'OUTPUT_LIMIT_EXCEEDED'),
    ('java', java_main('String s="x".repeat(65536); while(true)System.out.println(s);'), 'sum-two', 'OUTPUT_LIMIT_EXCEEDED'),
])
def test_managed_failure_verdicts(merged, language, source, slug, expected):
    client, _, login, _ = merged
    login('student')
    response = client.post('/api/submissions', json={'problem_slug': slug, 'language': language, 'source_code': source})
    assert response.status_code == 202, response.text
    result = wait(client, '/api/submissions/' + response.json()['id'], 'status', ('COMPLETED',))
    assert result['verdict'] == expected, result


@pytest.mark.parametrize('language,source', [
    ('pypy', '''import socket
from pathlib import Path
assert not Path('/etc/sakura.env').exists()
assert not Path('/srv/sakura-private/oj.sqlite3').exists()
try:
    socket.create_connection(('127.0.0.1', 8000), 1)
except OSError:
    print('isolated')
else:
    raise AssertionError('network accessible')
'''),
    ('java', java_main('''if (java.nio.file.Files.exists(java.nio.file.Path.of("/etc/sakura.env"))) throw new AssertionError("host file");
        try { new java.net.Socket().connect(new java.net.InetSocketAddress("127.0.0.1", 8000), 1000); throw new AssertionError("network accessible"); }
        catch(java.io.IOException e) { System.out.println("isolated"); }''')),
])
def test_managed_sandbox_isolation(merged, language, source):
    engine = merged[0].app.state.studio.engine
    program = engine.compile(dict(language=language, content=source), 'isolation test')
    result = engine.run(program)
    assert result['verdict'] == 'OK', result
    assert result['output'].strip() == b'isolated'


def test_sandbox_cleanup(merged):
    engine=merged[0].app.state.studio.engine.engine
    assert not list(engine.work.iterdir())
    assert not list(engine.control.iterdir())
