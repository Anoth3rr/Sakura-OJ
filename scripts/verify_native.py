#!/usr/bin/env python3
"""Smoke-test the installed standalone ljudge/linteractive binaries as sakura."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import sys

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = Path('/opt/sakura/runtime')
sys.path.insert(0, str(ROOT))
from tests.newjudge_programs import PYPY_SUM, JAVA_SUM
from app.studio.templates import INTERACTOR


def main():
    if os.getuid() == 0:
        raise SystemExit('Run this script as sakura, not root.')
    env = dict(os.environ, PATH=str(RUNTIME / 'bin') + ':/usr/local/bin:/usr/bin:/bin')
    with tempfile.TemporaryDirectory(prefix='sakura-native-') as temp:
        work = Path(temp)
        common = ['--etc-dir', str(RUNTIME / 'etc/ljudge'), '--cache-dir', str(work / 'cache'),
                  '--threads', '1', '--max-cpu-time', '2', '--max-real-time', '5',
                  '--max-memory', '256m', '--max-compiler-cpu-time', '20',
                  '--max-compiler-real-time', '30']
        source, inp, answer = work/'sum.cpp', work/'sum.in', work/'sum.out'
        source.write_text('#include <iostream>\nint main(){long long a,b;std::cin>>a>>b;std::cout<<a+b;}')
        inp.write_text('17 25\n')
        answer.write_text('42\n')
        result = subprocess.run([str(RUNTIME/'bin/ljudge'), *common, '--user-code', str(source),
                                 '--testcase', '--input', str(inp), '--output', str(answer)],
                                env=env, text=True, capture_output=True, check=True, timeout=60)
        normal = json.loads(result.stdout)
        assert normal['testcases'][0]['result'] == 'ACCEPTED', normal
        print(json.dumps({'normal': normal}, ensure_ascii=False), flush=True)
        example = ROOT / 'app/studio/examples/number-bomb'
        inp.write_text('4\n1 1\n10 7\n10 1\n100000000 100000000\n')
        answer.write_text('')
        result = subprocess.run([str(RUNTIME/'bin/linteractive'), *common,
                                 '--solution-code', str(example/'std.cpp'),
                                 '--user-code', str(example/'interactor.cpp'), '--keep-stderr',
                                 '--testcase', '--input', str(inp), '--output', str(answer)],
                                env=env, text=True, capture_output=True, check=True, timeout=60)
        interactive = json.loads(result.stdout)
        assert interactive['testcases'][0]['result'] == 'ACCEPTED', interactive
        print(json.dumps({'interactive': interactive}, ensure_ascii=False), flush=True)
        # Both entry points must preserve all Java classes and select actual PyPy.
        interactor = work / 'interactor.cpp'
        interactor.write_text(INTERACTOR)
        inp.write_text('3\n10 20 12\n')
        answer.write_text('42\n')
        for suffix, code in [('pypy', PYPY_SUM), ('java', JAVA_SUM)]:
            source = work / ('candidate.' + suffix)
            source.write_text(code)
            for command in ('ljudge', 'linteractive'):
                arguments = (['--user-code', str(source)] if command == 'ljudge' else
                             ['--solution-code', str(source), '--user-code', str(interactor)])
                result = subprocess.run([str(RUNTIME / 'bin' / command), *common, *arguments,
                                         '--keep-stderr', '--testcase', '--input', str(inp), '--output', str(answer)],
                                        env=env, text=True, capture_output=True, check=True, timeout=60)
                report = json.loads(result.stdout)
                assert report['testcases'][0]['result'] == 'ACCEPTED', report
                print(json.dumps({suffix + '-' + command: report}, ensure_ascii=False), flush=True)
            source.write_text('return 42' if suffix == 'pypy' else 'public class Main { broken }')
            result = subprocess.run([str(RUNTIME / 'bin/ljudge'), *common, '--user-code', str(source),
                                     '--testcase', '--input', str(inp), '--output', str(answer)],
                                    env=env, text=True, capture_output=True, check=True, timeout=60)
            report = json.loads(result.stdout)
            assert not report['compilation']['success'], report
            print(json.dumps({suffix + '-compile-error': report}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
