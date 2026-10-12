#!/usr/bin/env python3
"""Verify this example through Studio's real lrun engine, using temporary data."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3]))
from app.studio.engine import Engine, MIB
from app.studio.models import generation_lines, new_problem, source


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', default='/opt/sakura/runtime')
    parser.add_argument('--report', default=str(HERE / 'verification.json'))
    parser.add_argument('--full-scale', action='store_true')
    args = parser.parse_args()
    if os.getuid() == 0:
        raise SystemExit('Run as the dedicated sakura user, not root.')
    records, observations = [], []

    def record(name, passed, detail=None):
        item = dict(name=name, passed=bool(passed), detail=detail)
        records.append(item)
        print(json.dumps(item, ensure_ascii=False), flush=True)
        if not passed:
            raise AssertionError(name)

    def observe(name, detail):
        item = dict(name=name, detail=detail)
        observations.append(item)
        print(json.dumps(item, ensure_ascii=False), flush=True)

    report = dict(checks=records, observations=observations)
    try:
        with tempfile.TemporaryDirectory(prefix='number-bomb-') as tmp:
            root = Path(tmp)
            runtime = Path(args.runtime)
            engine = Engine(root, runtime, HERE.parent.parent / 'vendor/testlib.h')
            engine.prepare()
            report['environment'] = engine.health()
            report['sources'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in HERE.glob('*.cpp')}
            programs = {}
            for role in ('gen', 'val', 'interactor', 'std'):
                path = HERE / (role + '.cpp')
                programs[role] = engine.compile(source(dict(name=path.name, content=path.read_text()), role), role)
                record('compile_' + role, True)
            p = dict(new_problem(), mode='interactive', time_ms=2000, memory_mb=256, output_kb=8192)
            inp, ans = root / 'input', root / 'answer'
            ans.write_bytes(b'')

            def validate(data):
                return engine.run(programs['val'], data=data, cpu=5, wall=8)

            def judge(data, program=None, settings=None):
                inp.write_bytes(data)
                return engine.judge(program or programs['std'], None, dict(input=inp, answer=ans),
                                    settings or p, programs['interactor'])

            def contestant(code):
                return engine.compile(source(dict(name='solution.py', content=code)), 'solution')

            lines = generation_lines((HERE / 'gen_params.txt').read_text())
            for i, params in enumerate(lines, 1):
                result = engine.run(programs['gen'], args=params, cpu=3, wall=8, output=4*MIB)
                data = result['output']
                record(f'generate_{i}', result['verdict'] == 'OK', dict(args=params, bytes=len(data)))
                values = list(map(int, data.split()))
                record(f'budget_{i}', len(values) == 1+2*int(params[0]) and sum(values[1::2]) <= int(params[1]),
                       dict(sum_n=sum(values[1::2]), budget=int(params[1])))
                checked = validate(data)
                record(f'validate_{i}', checked['verdict'] == 'OK', checked['stderr'])
                verdict = judge(data)
                record(f'std_{i}', verdict['verdict'] == 'AC', verdict)
                if i == 3:
                    again = engine.run(programs['gen'], args=params, cpu=3, wall=8)
                    record('generator_reproducible', again['verdict'] == 'OK' and again['output'] == data)

            pairs = [(n, x) for n in range(1, 101) for x in range(1, n+1)]
            data = (str(len(pairs)) + '\n' + ''.join(f'{n} {x}\n' for n, x in pairs)).encode()
            result = judge(data)
            record('exhaustive_n_1_to_100', result['verdict'] == 'AC', result)

            malformed = {
                'zero_T': b'0\n', 'large_T': b'200001\n',
                'zero_n': b'1\n0 1\n', 'large_n': b'1\n1000000001 1\n',
                'zero_x': b'1\n10 0\n', 'large_x': b'1\n10 11\n',
                'missing_round': b'2\n1 1\n', 'extra_round': b'1\n1 1\n1 1\n',
                'extra_space': b'1\n10  7\n', 'missing_eol': b'1\n10 7',
                'sum_n_too_large': b'2\n1000000000 1\n1 1\n',
            }
            for name, data in malformed.items():
                result = validate(data)
                record('validator_rejects_' + name, result['verdict'] != 'OK', result['stderr'])

            prefix = 'import sys\nT=int(input())\nn=int(input())\n'
            cases = [
                ('reply_mapping', b'1\n10 7\n', prefix +
                 "for x,expected in [(1,0),(7,1),(10,2)]:\n print('?',x,flush=True)\n assert int(input())==expected\nprint('! 7',flush=True)\n", 'AC'),
                ('correct_without_queries', b'1\n1 1\n', prefix + "print('! 1',flush=True)\n", 'AC'),
                ('wrong_final', b'1\n10 7\n', prefix + "print('! 6',flush=True)\n", 'WA'),
                ('exactly_100_queries', b'1\n10 7\n', prefix +
                 "for _ in range(100):\n print('? 1',flush=True)\n input()\nprint('! 7',flush=True)\n", 'AC'),
                ('over_100_queries', b'1\n10 7\n', prefix +
                 "for _ in range(101):\n print('? 1',flush=True)\n if not sys.stdin.readline(): break\n", 'WA'),
                ('reset_limit_and_no_final_ack', b'2\n10 7\n20 7\n',
                 "T=int(input())\nfor tc in range(T):\n assert int(input())==[10,20][tc]\n for _ in range(100):\n  print('? 1',flush=True)\n  assert int(input())==0\n print('! 7',flush=True)\n", 'AC'),
                ('wrong_second_case', b'2\n10 7\n10 7\n', prefix +
                 "print('! 7',flush=True)\ninput()\nprint('! 6',flush=True)\n", 'WA'),
                ('invalid_command', b'1\n10 7\n', prefix + "print('# 7',flush=True)\n", 'PE'),
                ('non_integer', b'1\n10 7\n', prefix + "print('? hello',flush=True)\n", 'PE'),
                ('queries_outside_hidden_range', b'1\n10 7\n', prefix +
                 "for x,expected in [(-9223372036854775808,0),(0,0),(11,2),(9223372036854775807,2)]:\n print('?',x,flush=True)\n assert int(input())==expected\nprint('! 7',flush=True)\n", 'AC'),
                ('premature_eof', b'1\n10 7\n', prefix, 'PE'),
                ('extra_output', b'1\n10 7\n', prefix + "print('! 7\\nextra',flush=True)\n", 'PE'),
                ('no_flush', b'1\n10 7\n', prefix + "sys.stdout.write('? 1\\n')\nsys.stdin.readline()\n", 'TLE'),
                ('nonzero_after_correct_answer', b'1\n10 7\n', prefix +
                 "print('! 7',flush=True)\nsys.exit(7)\n", 'RE'),
            ]
            for name, data, code, expected in cases:
                result = judge(data, contestant(code))
                record('protocol_' + name, result['verdict'] == expected, result)
                if name == 'wrong_second_case':
                    record('setTestCase_diagnostic', 'test case 2' in result['judge_stderr'], result['judge_stderr'])

            large = None
            for i, params in enumerate(generation_lines((HERE / 'gen_stress_params.txt').read_text()), 1):
                result = engine.run(programs['gen'], args=params, cpu=3, wall=8, output=4*MIB)
                record(f'generate_stress_{i}', result['verdict'] == 'OK', dict(args=params, bytes=len(result['output'])))
                checked = validate(result['output'])
                record(f'validate_stress_{i}', checked['verdict'] == 'OK', engine.summary(checked))
                if params[2] == '3':
                    large = result['output']

            if args.full_scale:
                limits = dict(p, time_ms=10000)
                trivial = b'200000\n' + b'1 1\n'*200000
                result = judge(trivial, settings=limits)
                observe('current_web_T200000_n1', result)
                result = judge(large, settings=limits)
                observe('current_web_T200000_n5000_sum1e9', result)

    finally:
        Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
