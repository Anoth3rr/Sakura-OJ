#!/usr/bin/env python3
"""Exercise the native linteractive binary with official testlib and real lrun."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--runtime', type=Path, default=REPO / 'runtime')
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    if os.getuid() == 0:
        parser.error('Run as the dedicated judge account, not root.')
    binary, runtime, output = args.binary.resolve(), args.runtime.resolve(), args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    records = []
    summary = dict(backend='REAL_LRUN', kernel=os.uname().release, binary=str(binary),
                   binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(), results=records)
    try:
        with tempfile.TemporaryDirectory(prefix='linteractive-testlib-') as tmp:
            root = Path(tmp)
            config = root / 'config'
            (config / '_default').mkdir(parents=True)
            header = HERE.parent / 'etc/ljudge/_default/testlib.h'
            shutil.copyfile(header, config / '_default/testlib.h')
            summary['testlib_sha256'] = hashlib.sha256(header.read_bytes()).hexdigest()
            # Same real mirror as the configured runtime; no substitute sandbox.
            mirror = (runtime / 'mirrorfs.conf').read_text()
            for language in ('cpp', 'py3'):
                folder = config / language
                folder.mkdir()
                files = {
                    'compile.mirrorfs': mirror, 'run.mirrorfs': mirror,
                    'version.cmd_list': 'g++\n--version\n' if language == 'cpp' else 'python3\n--version\n',
                    'compile.cmd_list': 'g++\n-std=c++17\n-O2\n-pipe\n-o\n$exe\n$src\n' if language == 'cpp' else '',
                    'run.cmd_list': './$exe\n' if language == 'cpp' else 'python3\n$src\n',
                }
                for name, content in files.items():
                    (folder / name).write_text(content)
            env = dict(os.environ, PATH=str(runtime / 'bin') + ':/usr/local/bin:/usr/bin:/bin', HOME=str(root))
            template = (HERE / 'fixtures/contestant.cpp').read_text()
            template = '#include <fstream>\n' + template.replace('int main() {', '''int main() {
    // The contestant must not see hidden input, answer or transcript.
    if (std::ifstream("input") || std::ifstream("output") || std::ifstream("transcript")) return 90;
''')

            def run(name, mode=0, expected='ACCEPTED', count=1, threads=1,
                    empty_answer=False, bad_answer=False, python=False,
                    transcript_limit=False, real_problem=False):
                run_dir = root / name
                run_dir.mkdir()
                candidate = run_dir / 'contestant.cpp'
                candidate.write_text(f'#define MODE {mode}\n' + template)
                interactor = HERE / 'fixtures/testlib_interactor.cpp'
                if python:
                    candidate = HERE / 'fixtures/contestant.py3'
                if real_problem:
                    candidate = REPO / 'ljudge/examples/number-bomb/std.cpp'
                    interactor = REPO / 'ljudge/examples/number-bomb/interactor.cpp'
                command = [str(binary), '--etc-dir', str(config), '--cache-dir', str(run_dir / 'cache'),
                           '--solution-code', str(candidate), '--user-code', str(interactor),
                           '--threads', str(threads), '--keep-stderr',
                           '--max-cpu-time', '1', '--max-real-time', '2', '--max-memory', '128m',
                           '--max-checker-cpu-time', '2', '--max-checker-real-time', '4',
                           '--max-checker-output', '1024' if transcript_limit else '1m',
                           '--max-compiler-cpu-time', '30', '--max-compiler-real-time', '45']
                hashes = {}
                for i in range(count):
                    inp, answer = run_dir / f'{i}.in', run_dir / f'{i}.out'
                    secret = (37+i*17) % 100 + 1
                    judge_mode = 2 if transcript_limit else 1 if empty_answer else 0
                    inp.write_text(f'{secret} {judge_mode}\n')
                    answer.write_text('' if empty_answer else f'{secret + int(bad_answer)}\n')
                    if real_problem:
                        inp.write_text('6\n1 1\n2 1\n2 2\n666 373\n1000 1000\n999998329 1\n')
                        answer.write_text('')
                    hashes[str(inp)] = hashlib.sha256(inp.read_bytes()).hexdigest()
                    hashes[str(answer)] = hashlib.sha256(answer.read_bytes()).hexdigest()
                    command += ['--testcase', '--input', str(inp), '--output', str(answer)]
                started = time.monotonic()
                result = subprocess.run(command, env=env, capture_output=True, text=True, timeout=90)
                (output / (name + '.json')).write_text(result.stdout)
                (output / (name + '.stderr.log')).write_text(result.stderr)
                try:
                    report = json.loads(result.stdout)
                except json.JSONDecodeError:
                    report = {}
                actual = [case.get('result') for case in report.get('testcases', [])]
                unchanged = all(hashlib.sha256(Path(path).read_bytes()).hexdigest() == value
                                for path, value in hashes.items())
                cleaned = not any((run_dir / 'cache/tmp').glob('*/transcript-*'))
                passed = (result.returncode == 0 and report.get('userCompilation', {}).get('success')
                          and report.get('judgeCompilation', {}).get('success')
                          and actual == [expected]*count and unchanged and cleaned)
                item = dict(name=name, passed=bool(passed), expected=expected, actual=actual,
                            inputs_unchanged=unchanged, transcript_cleaned=cleaned,
                            seconds=round(time.monotonic()-started, 3))
                records.append(item)
                print(json.dumps(item), flush=True)
                if not passed:
                    print(result.stdout[-6000:], result.stderr[-2000:], flush=True)
                    raise AssertionError(name)

            run('testlib_ac')
            run('testlib_empty_answer', empty_answer=True)
            run('testlib_wa', mode=1, expected='WRONG_ANSWER')
            run('testlib_pe', mode=6, expected='PRESENTATION_ERROR')
            run('testlib_missing_flush', mode=2, expected='TIME_LIMIT_EXCEEDED')
            run('testlib_bad_answer_file', bad_answer=True, expected='INTERNAL_ERROR')
            run('testlib_transcript_output_limit', transcript_limit=True, expected='INTERNAL_ERROR')
            run('testlib_python_contestant', python=True)
            run('testlib_sequential_cases', count=12)
            run('testlib_parallel_cases', count=12, threads=4)
            run('number_bomb_unmodified_sources', real_problem=True)
    finally:
        summary.update(passed=sum(r['passed'] for r in records), total=len(records))
        (output / 'results.json').write_text(json.dumps(summary, indent=2)+'\n')


if __name__ == '__main__':
    main()
