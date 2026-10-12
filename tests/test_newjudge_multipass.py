"""Exercise the deployed native multi-pass controller through Studio and OJ."""
import os

import pytest

from .test_newjudge_flow import merged, wait
from .newjudge_programs import java_main
from app.studio.templates import MULTIPASS_SOLUTION

pytestmark = pytest.mark.skipif(os.getenv('SAKURA_REAL_JUDGE') != '1', reason='需要真实 Linux lrun 环境')

SOLUTIONS = {
    'cpp': MULTIPASS_SOLUTION,
    'c': '#include <stdio.h>\n#include <string.h>\nint main(){char phase[16];int n;long long sum=0,x;scanf("%15s",phase);if(!strcmp(phase,"send")){scanf("%d",&n);while(n--){scanf("%lld",&x);sum+=x;}}else scanf("%lld",&sum);printf("%lld\\n",sum);}',
    'python': 'import sys\na=sys.stdin.read().split();print(sum(map(int,a[2:])) if a[0]=="send" else int(a[1]))',
    'pypy': 'import sys\nassert sys.implementation.name=="pypy"\na=sys.stdin.read().split();print(sum(map(int,a[2:])) if a[0]=="send" else int(a[1]))',
    'java': java_main('java.util.Scanner s=new java.util.Scanner(System.in); String phase=s.next(); long sum=0; if(phase.equals("send")){int n=s.nextInt();while(n-->0)sum+=s.nextLong();}else sum=s.nextLong();System.out.println(sum);'),
}


def test_multipass_authoring_native_trial_publication_and_languages(merged):
    client, headers, login, _ = merged
    login()
    created = client.post('/api/studio/problems', json={'template': 'multipass'}, headers=headers)
    assert created.status_code == 200, created.text
    p = created.json()
    p['generation'] = '5 100 1'
    p = client.put('/api/studio/problems/' + p['id'], json=p, headers=headers).json()
    generated = client.post(f"/api/studio/problems/{p['id']}/generate", json={'revision': p['revision']}, headers=headers)
    assert generated.status_code == 200, generated.text
    job = wait(client, '/api/studio/jobs/' + generated.json()['id'], 'state', ('done', 'failed'))
    assert job['state'] == 'done', job
    assert job['cases'][0]['answer_bytes'] == 0
    trial = client.post(f"/api/studio/problems/{p['id']}/submit", json={
        'revision': p['revision'], 'solution': {'name': 'main.cpp', 'content': MULTIPASS_SOLUTION},
    }, headers=headers)
    assert trial.status_code == 200, trial.text
    job = wait(client, '/api/studio/jobs/' + trial.json()['id'], 'state', ('done', 'failed'))
    assert job['state'] == 'done' and job['verdict'] == 'AC', job
    assert job['cases'][0]['backend'] == 'lworkflow / lrun'
    assert job['cases'][0]['passes'] == 2
    assert len(job['cases'][0]['phases']) == 2
    assert all(x['validator']['verdict'] == 'AC' for x in job['cases'][0]['phases'])
    published = client.post(f"/api/studio/problems/{p['id']}/publish", json={
        'revision': p['revision'], 'slug': 'native-multipass'}, headers=headers)
    assert published.status_code == 200, published.text
    assert 'judge_config' not in published.json()['problem']
    login('student')
    for language, code in SOLUTIONS.items():
        submitted = client.post('/api/submissions', json={
            'problem_slug': 'native-multipass', 'language': language, 'source_code': code})
        assert submitted.status_code == 202, submitted.text
        result = wait(client, '/api/submissions/' + submitted.json()['id'], 'status', ('COMPLETED',))
        assert result['verdict'] == 'ACCEPTED', (language, result)
        assert result['results'][0]['message_bytes'] > 0
    submitted = client.post('/api/submissions', json={
        'problem_slug': 'native-multipass', 'language': 'python', 'source_code': 'print(0)'})
    result = wait(client, '/api/submissions/' + submitted.json()['id'], 'status', ('COMPLETED',))
    assert result['verdict'] == 'WRONG_ANSWER', result
    login()
    p = client.get('/api/studio/problems/' + p['id']).json()
    p['validation_passes'] = 1
    p = client.put('/api/studio/problems/' + p['id'], json=p, headers=headers).json()
    assert not p['data_ready']
    generated = client.post(f"/api/studio/problems/{p['id']}/generate", json={'revision': p['revision']}, headers=headers)
    job = wait(client, '/api/studio/jobs/' + generated.json()['id'], 'state', ('done', 'failed'))
    assert job['state'] == 'failed' and 'validation_passes' in job['error'], job
    del p['programs']['reference']
    p['validation_passes'] = 2
    p = client.put('/api/studio/problems/' + p['id'], json=p, headers=headers).json()
    generated = client.post(f"/api/studio/problems/{p['id']}/generate", json={'revision': p['revision']}, headers=headers)
    assert generated.status_code == 200, generated.text
    job = wait(client, '/api/studio/jobs/' + generated.json()['id'], 'state', ('done', 'failed'))
    assert job['state'] == 'done', job
    engine = client.app.state.studio.engine.engine
    assert not list(engine.work.iterdir()) and not list(engine.control.iterdir())


def test_interactive_cpu_limit_does_not_turn_into_output_limit(merged, tmp_path):
    from app.studio.templates import INTERACTOR
    engine = merged[0].app.state.studio.engine
    program = engine.compile(dict(language='python', content='while True: pass'), 'busy loop')
    interactor = engine.compile(dict(language='cpp', content=INTERACTOR), 'interactor')
    inp, ans = tmp_path / 'input', tmp_path / 'answer'
    inp.write_text('3\n1 2 3\n')
    ans.write_text('')
    p = dict(mode='interactive', time_ms=1000, memory_mb=256, output_kb=1024)
    # Tick-based RLIMIT_CPU and the cgroup counter previously raced near 1 s;
    # a kernel core dump could be counted as > 1 MiB of contestant output.
    for _ in range(8):
        result = engine.interaction(program, interactor, inp, ans, p)
        assert result['verdict'] == 'TLE', result
        assert result['exceed'] == 'CPU_TIME', result


@pytest.mark.parametrize('language', ['python', 'pypy'])
def test_caught_output_limit_and_exact_boundary(merged, language):
    engine = merged[0].app.state.studio.engine
    limit = 1024 * 1024
    code = 'import sys\nn=int(sys.argv[1])\ntry: sys.stdout.buffer.write(b"x"*n); sys.stdout.buffer.flush()\nexcept OSError: pass'
    program = engine.compile(dict(language=language, content=code), 'output boundary')
    result = engine.run(program, args=[str(limit)], output=limit)
    assert result['verdict'] == 'OK' and len(result['output']) == limit, result
    for _ in range(3):
        result = engine.run(program, args=[str(limit + 65536)], output=limit)
        assert result['verdict'] == 'OLE' and result['exceed'] == 'OUTPUT', result
