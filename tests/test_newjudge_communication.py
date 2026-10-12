"""Real testlib two-pass workflows, from source preparation to OJ submission."""
import json
import os
from pathlib import Path
import subprocess

import pytest

from app.config import settings
from app.studio.models import TESTLIB_COMMUNICATION
from app.studio.templates import TESTLIB_COMMUNICATION_SOLUTION, testlib_communication_example as communication_example
from .test_newjudge_flow import merged, wait
from .newjudge_programs import java_main

pytestmark = pytest.mark.skipif(os.getenv('SAKURA_REAL_JUDGE') != '1', reason='需要真实 Linux lrun 环境')

PYTHON = '''import sys
phase=input().strip()
if phase=='send':
    n=int(input()); a=list(map(int,input().split())); assert len(a)==n
    print(sum(a),flush=True)
else:
    print(int(input()),flush=True)
'''
SOLUTIONS = {
    'cpp': TESTLIB_COMMUNICATION_SOLUTION,
    'c': '#include <stdio.h>\n#include <string.h>\nint main(){char phase[16];int n;long long x,sum=0;scanf("%15s",phase);if(!strcmp(phase,"send")){scanf("%d",&n);while(n--){scanf("%lld",&x);sum+=x;}}else scanf("%lld",&sum);printf("%lld\\n",sum);fflush(stdout);}',
    'python': PYTHON,
    'pypy': 'import sys\nassert sys.implementation.name=="pypy"\n' + PYTHON,
    'java': java_main('java.util.Scanner s=new java.util.Scanner(System.in);String p=s.next();long sum=0;if(p.equals("send")){int n=s.nextInt();while(n-->0)sum+=s.nextLong();}else sum=s.nextLong();System.out.println(sum);System.out.flush();'),
}


def test_testlib_communication_authoring_publication_and_languages(merged):
    client, headers, login, _ = merged
    login()
    created = client.post('/api/studio/problems', json={'template':'testlib-communication'}, headers=headers)
    assert created.status_code == 200, created.text
    p = created.json()
    p['generation'] = '5 100 1\n7 1000 2'
    for role in ('interactor','checker'):
        absent = p['programs'].pop(role)
        saved = client.put('/api/studio/problems/'+p['id'], json=p, headers=headers)
        assert saved.status_code == 200, saved.text
        p = saved.json()
        rejected = client.post(f"/api/studio/problems/{p['id']}/generate", json={'revision':p['revision']}, headers=headers)
        assert rejected.status_code == 400 and role in rejected.text
        p['programs'][role] = absent
    p = client.put('/api/studio/problems/'+p['id'], json=p, headers=headers).json()
    generated = client.post(f"/api/studio/problems/{p['id']}/generate", json={'revision':p['revision']}, headers=headers)
    assert generated.status_code == 200, generated.text
    job = wait(client,'/api/studio/jobs/'+generated.json()['id'],'state',('done','failed'))
    assert job['state'] == 'done', job
    assert all(c['answer_bytes'] > 0 for c in job['cases'])
    body = {'revision':p['revision'],'solution':{'name':'main.cpp','content':SOLUTIONS['cpp']}}
    rejected = client.post(f"/api/studio/problems/{p['id']}/submit", json={**body,'receiver':body['solution']}, headers=headers)
    assert rejected.status_code == 400 and 'Receiver' in rejected.text
    trial = client.post(f"/api/studio/problems/{p['id']}/submit", json=body, headers=headers)
    assert trial.status_code == 200, trial.text
    job = wait(client,'/api/studio/jobs/'+trial.json()['id'],'state',('done','failed'))
    assert job['state'] == 'done' and job['verdict'] == 'AC', job
    assert all(c['passes']==2 and len(c['phases'])==2 for c in job['cases'])
    assert all(c['phases'][1]['checker']['verdict']=='AC' for c in job['cases'])
    published = client.post(f"/api/studio/problems/{p['id']}/publish",json={'revision':p['revision'],'slug':'testlib-two-pass'},headers=headers)
    assert published.status_code == 200, published.text
    from app import repository
    configuration = json.loads(repository.get_problem_by_slug('testlib-two-pass',include_hidden=True)['judge_config'])
    assert configuration['communication_protocol'] == TESTLIB_COMMUNICATION
    assert set(configuration['programs']) == {'checker','interactor'}
    login('student')
    for language, code in SOLUTIONS.items():
        accepted = client.post('/api/submissions',json={'problem_slug':'testlib-two-pass','language':language,'source_code':code})
        assert accepted.status_code == 202, accepted.text
        result = wait(client,'/api/submissions/'+accepted.json()['id'],'status',('COMPLETED',))
        assert result['verdict']=='ACCEPTED', (language,result)
        assert all(c['message_bytes'] > 0 for c in result['results'])


@pytest.fixture
def protocol_case(merged, tmp_path):
    engine = merged[0].app.state.studio.engine
    p = communication_example()
    inp, ans = tmp_path/'input', tmp_path/'answer'
    inp.write_text('3\n10 20 12\n')
    ans.write_text('42\n')
    return engine,p,{'input':inp,'answer':ans}


@pytest.mark.parametrize('mutation,expected,passes', [
    ('wrong-message','WA',2), ('bad-protocol','WA',1), ('first-crash','RE',1),
    ('second-crash','RE',2), ('first-loop','TLE',1), ('second-loop','TLE',2),
    ('second-overflow','OLE',2), ('checker-failure','IE',2),
])
def test_two_pass_failures_preserve_stage_verdict(protocol_case,mutation,expected,passes):
    engine,p,files=protocol_case
    code=PYTHON
    if mutation=='wrong-message': code=code.replace('print(sum(a),flush=True)','print(0,flush=True)')
    if mutation=='bad-protocol': code=code.replace('print(sum(a),flush=True)','print("invalid",flush=True)')
    if mutation=='first-crash': code=code.replace('print(sum(a),flush=True)','print(sum(a),flush=True); raise RuntimeError("first")')
    if mutation=='second-crash': code=code.replace('print(int(input()),flush=True)','raise RuntimeError("second")')
    if mutation=='first-loop': code=code.replace('print(sum(a),flush=True)','exec("while True: pass")')
    if mutation=='second-loop': code=code.replace('print(int(input()),flush=True)','exec("while True: pass")')
    if mutation=='second-overflow': code=code.replace('print(int(input()),flush=True)','print("x"*2000000)')
    if mutation=='checker-failure': p['programs']['checker']['content']=p['programs']['checker']['content'].replace('registerTestlibCmd(argc, argv);','registerTestlibCmd(argc, argv); quitf(_fail, "broken judge");')
    program=engine.compile({'language':'python','content':code},'solution')
    judges={r:engine.compile(p['programs'][r],r) for r in ('interactor','checker')}
    result=engine.judge(program,judges['checker'],files,p,judges['interactor'])
    assert result['verdict']==expected and result['passes']==passes,result


def test_two_pass_files_isolated_and_original_inputs_readonly(protocol_case):
    engine,p,files=protocol_case
    code=PYTHON.replace('phase=input().strip()', '''from pathlib import Path
assert not Path('input').exists() and not Path('answer').exists()
phase=input().strip()
if phase=='send': Path('private-state').write_text('secret')
else: assert not Path('private-state').exists()
''')
    checker=r'''#include "testlib.h"
#include <fstream>
int main(int argc,char** argv){registerTestlibCmd(argc,argv);
for(int i=1;i<=3;++i){std::ofstream f(argv[i],std::ios::app); if(f.is_open())quitf(_fail,"writable judge file");}
int n=inf.readInt();long long sum=0;while(n--)sum+=inf.readLong();
if(ans.readLong()!=sum)quitf(_fail,"wrong original answer");
if(ouf.readLong()!=sum)quitf(_wa,"wrong final output");quitf(_ok,"isolated");}
'''
    program=engine.compile({'language':'python','content':code},'solution')
    judges={r:engine.compile(p['programs'][r],r) for r in ('interactor','checker')}
    judges['checker']=engine.compile({'language':'cpp','content':checker},'checker')
    result=engine.judge(program,judges['checker'],files,p,judges['interactor'])
    assert result['verdict']=='AC' and result['passes']==2,result
    assert files['input'].read_text()=='3\n10 20 12\n' and files['answer'].read_text()=='42\n'
    assert not list(engine.engine.work.iterdir()) and not list(engine.engine.control.iterdir())


def test_standalone_compilation_then_native_execution(protocol_case,tmp_path):
    _,p,files=protocol_case
    root=Path(__file__).resolve().parents[1]
    runtime=settings.newjudge_runtime
    for role,code in [('main',SOLUTIONS['cpp']),('interactor',p['programs']['interactor']['content']),('checker',p['programs']['checker']['content'])]:
        (tmp_path/(role+'.cpp')).write_text(code)
    command=['bash',str(root/'judge/newjudge/script/compile-communication.sh'),
        '--runtime',str(runtime),'--etc-dir',str(runtime/'etc/ljudge'),
        '--cache-dir',str(tmp_path/'cache'),'--request-dir',str(tmp_path/'requests'),
        '--user-code',str(tmp_path/'main.cpp'),'--interactor-code',str(tmp_path/'interactor.cpp'),
        '--checker-code',str(tmp_path/'checker.cpp'),'--input',str(files['input']),'--output',str(files['answer'])]
    compiled=subprocess.run(command,text=True,capture_output=True,timeout=100)
    assert compiled.returncode==0,compiled.stdout+compiled.stderr
    report=json.loads(compiled.stdout)
    assert report['success'] and report['status']=='PREPARED' and len(report['requests'])==1
    result=subprocess.run([str(runtime/'bin/lworkflow'),'--request',report['requests'][0],'--output',str(tmp_path/'actual')],text=True,capture_output=True,timeout=40)
    assert result.returncode==0,result.stderr
    judged=json.loads(result.stdout)
    assert judged['verdict']=='AC' and judged['passes']==2,judged
    assert (tmp_path/'actual').read_text().strip()=='42'


def test_small_output_limit_excludes_sandbox_supervisor_bytes(merged):
    engine=merged[0].app.state.studio.engine
    code='#include <stdlib.h>\n#include <unistd.h>\nint main(int argc,char**argv){int n=atoi(argv[1]);write(1,"xxx",n);usleep(40000);}'
    program=engine.compile({'language':'c','content':code},'output boundary')
    for size in (0,2,3):
        result=engine.run(program,args=[str(size)],output=2)
        assert result['verdict']==('OLE' if size>2 else 'OK'),result
