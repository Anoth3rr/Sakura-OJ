import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import zipfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[4]))
from app.studio.engine import Engine
from app.studio.models import source

PID = '3a2cab3dde51'


def main():
    parser = argparse.ArgumentParser(description='Reproduce the historical r8 issue from an explicitly exported problem ZIP.')
    parser.add_argument('--archive', type=Path, required=True)
    args = parser.parse_args()
    archive = zipfile.ZipFile(args.archive)
    p = json.loads(archive.read('problem.json'))
    if p['revision'] != 8:
        raise SystemExit('Problem revision changed; inspect it before continuing.')
    original = archive.read(p['programs']['interactor']).decode()
    (HERE / 'interactor_original.cpp').write_text(original, encoding='utf-8')
    fixed = original.replace('if (x != n)', 'if (c != x)')
    fixed = fixed.replace('if (x == n) p = 1;', 'if (c == x) p = 1;')
    fixed = fixed.replace('else if (x < n) p = 0;', 'else if (c < x) p = 0;')
    fixed = fixed.replace('else if (x > n) p = 2;', 'else if (c > x) p = 2;')
    fixed = fixed.replace('incorrect guess in test %d', 'incorrect guess in test %lld')
    (HERE / 'interactor_fixed.cpp').write_text(fixed, encoding='utf-8')
    records = []
    report = dict(problem_id=PID, revision=p['revision'], checks=records)
    report['input_hashes'] = {entry['id']: entry['sha256'] for entry in p['testcases']}
    report['sources'] = {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in HERE.glob('*.cpp')}
    try:
        with tempfile.TemporaryDirectory(prefix='number-bomb-review-') as tmp:
            root = Path(tmp)
            engine = Engine(root, '/opt/sakura/runtime', HERE.parents[2] / 'vendor/testlib.h')
            engine.prepare()
            programs = {}
            for name in ('std_original', 'std_fixed', 'interactor_original', 'interactor_fixed'):
                code = (HERE / (name + '.cpp')).read_text()
                programs[name] = engine.compile(source(dict(name=name+'.cpp', content=code)), name)
            inp, ans = root / 'input', root / 'answer'
            ans.write_bytes(b'')

            def check(name, contestant, interactor, data, expected):
                inp.write_bytes(data)
                result = engine.judge(programs[contestant], None, dict(input=inp, answer=ans), p, programs[interactor])
                item = dict(name=name, expected=expected, passed=result['verdict']==expected, result=result)
                records.append(item)
                print(json.dumps(item, ensure_ascii=False), flush=True)
                if not item['passed']:
                    raise AssertionError(name)

            first = archive.read('tests/001.in')
            report['first_hidden_lines'] = first.decode().splitlines()[:3]
            check('original_pair_reproduces_TLE', 'std_original', 'interactor_original', first, 'TLE')
            check('only_std_fixed_still_WA', 'std_fixed', 'interactor_original', first, 'WA')
            check('only_interactor_fixed_still_WA', 'std_original', 'interactor_fixed', first, 'WA')
            check('missing_final_on_n1_causes_deadlock', 'std_original', 'interactor_fixed', b'2\n1 1\n2 2\n', 'TLE')
            for entry in p['testcases']:
                data = archive.read(f'tests/{entry["id"]}.in')
                check('both_fixed_current_case_' + entry['id'], 'std_fixed', 'interactor_fixed', data, 'AC')
            data = b'6\n1 1\n2 1\n2 2\n666 373\n1000 1000\n999998329 1\n'
            check('both_fixed_boundary_cases', 'std_fixed', 'interactor_fixed', data, 'AC')
    finally:
        (HERE / 'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
