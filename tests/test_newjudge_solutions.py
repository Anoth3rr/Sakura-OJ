"""Real sandbox tests for Main Correct, selected invocations and labeled failures."""
import hashlib
import os

import pytest

from app.studio.templates import candidate, MULTIPASS_SOLUTION, TESTLIB_COMMUNICATION_SOLUTION
from .test_newjudge_flow import merged, wait

pytestmark = pytest.mark.skipif(os.getenv('SAKURA_REAL_JUDGE') != '1', reason='需要真实 Linux lrun 环境')


def save(client, headers, p):
    response = client.put('/api/studio/problems/'+p['id'], json=p, headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


def run(client, headers, p, kind, **body):
    response = client.post(f"/api/studio/problems/{p['id']}/{kind}", json=dict(revision=p['revision'], **body), headers=headers)
    assert response.status_code == 200, response.text
    return wait(client, '/api/studio/jobs/'+response.json()['id'], 'state', ('done','failed'))


def test_selected_and_all_solutions_with_real_failure_verdicts(merged):
    client, headers, login, _ = merged
    login()
    p = client.post('/api/studio/problems', json={'template':'normal'}, headers=headers).json()
    std = p['programs'].pop('reference')
    p.update(generation='3 100 1\n5 100 2', time_ms=300, memory_mb=64, output_kb=8)
    p['solutions'] = [dict(std, tag='main-correct')]
    failures = [('wrong','print(-1)'), ('time-limit','while True: pass'),
                ('memory-limit','a=[]\nwhile True: a.append(bytearray(1024*1024))'),
                ('runtime-error','raise RuntimeError("expected error")'),
                ('output-limit','while True: print("x"*65536)'), ('compile-error','def broken(:')]
    for tag, code in failures:
        p['solutions'].append(dict(name=tag+'.py', language='python', content=code, tag=tag))
    # A deliberately mislabeled correct solution must be flagged as a mismatch.
    p['solutions'].append(dict(std, name='not_wrong.cpp', tag='wrong'))
    p = save(client,headers,p)
    generated = run(client,headers,p,'generate')
    assert generated['state'] == 'done', generated
    p = client.get('/api/studio/problems/'+p['id']).json()
    assert p['data_ready'] and all(c['answer_bytes'] for c in p['dataset']['cases'])
    for ids in ([], ['unknown'], [p['solutions'][0]['id']]*2, None, [True]):
        bad = client.post(f"/api/studio/problems/{p['id']}/invoke", json={'revision':p['revision'],'solution_ids':ids}, headers=headers)
        assert bad.status_code == 400, bad.text
    selected = [s['id'] for s in p['solutions'][:2]]
    job = run(client,headers,p,'invoke',solution_ids=selected)
    assert job['state']=='done' and job['verdict']=='MATCH', job
    assert [r['solution_id'] for r in job['runs']] == selected
    assert [r['verdict'] for r in job['runs']] == ['AC','WA']
    assert all(len(r['cases'])==2 for r in job['runs'])
    all_job = run(client,headers,p,'invoke',solution_ids='all')
    assert all_job['state']=='done' and all_job['verdict']=='MISMATCH', all_job
    assert [r['verdict'] for r in all_job['runs']] == ['AC','WA','TLE','MLE','RE','OLE','CE','AC']
    assert all_job['matched_count']==7
    assert all_job['runs'][-1]['matches_expected'] is False
    before = all_job['runs'][1]['source_sha256']
    p['solutions'][1]['content'] = 'print(-2)'
    p = save(client,headers,p)
    assert p['data_ready']
    old = client.get('/api/studio/jobs/'+all_job['id']).json()
    assert old['runs'][1]['source_sha256']==before==hashlib.sha256(b'print(-1)').hexdigest()
    assert old['dataset_id'] == p['dataset']['id']


@pytest.mark.parametrize('mode', ['interactive','communication','multipass','testlib-communication'])
def test_main_correct_uses_complete_protocol(merged, mode):
    client,headers,login,_=merged
    login()
    p=client.post('/api/studio/problems',json={'template':mode},headers=headers).json()
    code = (MULTIPASS_SOLUTION if mode=='multipass' else TESTLIB_COMMUNICATION_SOLUTION if mode=='testlib-communication'
            else candidate(mode)['content'])
    p['solutions']=[dict(name='std.cpp', language='cpp', content=code, tag='main-correct')]
    if mode=='interactive':
        del p['programs']['reference']
        del p['programs']['checker']
    if mode in ('multipass','communication'):
        del p['programs']['reference']
    p['generation']='3 100 1'
    p=save(client,headers,p)
    generated=run(client,headers,p,'generate')
    assert generated['state']=='done',generated
    if mode in ('interactive','testlib-communication'):
        assert any('Main Correct 完整流程自检通过' in line for line in generated['log'])
    p=client.get('/api/studio/problems/'+p['id']).json()
    job=run(client,headers,p,'invoke',solution_ids='all')
    assert job['verdict']=='MATCH' and job['runs'][0]['verdict']=='AC',job
    if mode=='interactive':
        p['solutions'][0]['content']='#include <iostream>\nint main(){std::cout<<-1<<std::endl;}'
        p=save(client,headers,p)
        assert not p['data_ready']
        failed=run(client,headers,p,'generate')
        assert failed['state']=='failed' and 'Main Correct 自检失败' in failed['error']
        assert not client.get('/api/studio/problems/'+p['id']).json()['data_ready']


def test_main_correct_with_independent_receiver_and_message_limit(merged):
    client,headers,login,_=merged
    login()
    p=client.post('/api/studio/problems',json={'template':'communication'},headers=headers).json()
    p['programs'].pop('reference')
    p.update(generation='3 100 1', solutions=[
        dict(name='send.py',language='pypy',content='input(); print(sum(map(int,input().split())))',tag='main-correct',
             receiver=dict(name='receive.py',language='python',content='print(int(input()))')),
        dict(name='too_long.py',language='python',content='print("x"*33)',tag='communication-limit')])
    p=save(client,headers,p)
    generated=run(client,headers,p,'generate')
    assert generated['state']=='done',generated
    p=client.get('/api/studio/problems/'+p['id']).json()
    job=run(client,headers,p,'invoke',solution_ids='all')
    assert job['verdict']=='MATCH' and [r['verdict'] for r in job['runs']]==['AC','CLE'],job
