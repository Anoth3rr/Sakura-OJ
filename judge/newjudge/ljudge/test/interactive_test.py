#!/usr/bin/env python3
"""Trusted-fixture regression tests, NOT sandbox acceptance tests.

sudo unshare --mount --propagation private -- python3 interactive_test.py \
    --binary /absolute/path/to/linteractive --output-dir /tmp/interactive-results

Requires g++, Python 3 and a private Linux mount namespace. No third-party Python
packages are needed. The sandbox adapter is scoped to this test's child PATH.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import signal
import subprocess
import tempfile
import time

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--binary', type=Path, required=True)
parser.add_argument('--output-dir', type=Path, required=True)
parser.add_argument('--case', action='append', default=[])
args = parser.parse_args()
binary, output = args.binary.resolve(), args.output_dir.resolve()
if os.geteuid() != 0:
    parser.error('Run in a private mount namespace as root; fixture processes are dropped to nobody.')
# Refuse to replace /run/lrun in the caller's ordinary mount namespace.
if os.readlink('/proc/self/ns/mnt') == os.readlink('/proc/1/ns/mnt'):
    parser.error('Use unshare --mount --propagation private before running this test.')
output.mkdir(parents=True, exist_ok=True)
work = Path(tempfile.mkdtemp(prefix='linteractive-regression-'))
work.chmod(0o755)
for subdir in ('bin', 'config/cpp', 'config/py3', 'fixtures', 'runs'):
    (work / subdir).mkdir(parents=True, exist_ok=True)
shutil.copyfile(HERE / 'fake_lrun.py', work / 'bin/lrun')
(work / 'bin/lrun').chmod(0o755)
mirror = '# regression test adapter only: ' + str(work) + '\n'
for language in ('cpp', 'py3'):
    config = work / 'config' / language
    for name, content in {
        'compile.mirrorfs': mirror, 'run.mirrorfs': mirror,
        'version.cmd_list': 'g++\n--version\n' if language == 'cpp' else 'python3\n--version\n',
        'compile.cmd_list': 'g++\n-std=c++17\n-O2\n-o\n$exe\n$src\n' if language == 'cpp' else '',
        'run.cmd_list': './$exe\n' if language == 'cpp' else 'python3\n$src\n',
    }.items():
        (config / name).write_text(content)
shutil.copytree(HERE / 'fixtures', work / 'fixtures', dirs_exist_ok=True)
template = (HERE / 'fixtures/contestant.cpp').read_text()
cases = [
    ('correct_answer', 0, 0, 'ACCEPTED'),
    ('wrong_answer', 1, 0, 'WRONG_ANSWER'),
    ('bad_protocol', 6, 0, 'WRONG_ANSWER'),
    ('missing_flush', 2, 0, 'TIME_LIMIT_EXCEEDED'),
    ('nonzero_after_answer', 3, 0, 'NON_ZERO_EXIT_CODE'),
    ('segfault_after_answer', 4, 0, 'SEGMENTATION_FAULT'),
    ('cpu_timeout_after_answer', 5, 0, 'TIME_LIMIT_EXCEEDED'),
    ('wait_for_contestant_eof', 0, 1, 'ACCEPTED'),
    ('exit_without_answer', 7, 0, 'WRONG_ANSWER'),
    ('two_testcases', 0, 0, 'ACCEPTED'),
    ('interactor_segfault', 0, 2, 'INTERNAL_ERROR'),
    ('interactor_own_wall_limit', 0, 3, 'ACCEPTED'),
    ('interactor_cpu_timeout', 0, 4, 'INTERNAL_ERROR'),
    ('interactor_failure', 0, 5, 'INTERNAL_ERROR'),
    ('presentation_error', 0, 6, 'PRESENTATION_ERROR'),
    ('sigpipe_after_rejection', 8, 0, 'WRONG_ANSWER'),
    ('python_contestant', 0, 0, 'ACCEPTED'),
    ('python_interactor', 0, 0, 'ACCEPTED'),
    ('both_python', 0, 0, 'ACCEPTED'),
    ('incomplete_sandbox_report', 0, 0, 'INTERNAL_ERROR'),
    ('sandbox_launch_error', 0, 0, 'INTERNAL_ERROR'),
    ('wait_for_sandbox_cleanup', 0, 0, 'ACCEPTED'),
    ('many_cases_low_fd_limit', 0, 1, 'ACCEPTED'),
    ('parallel_cases', 0, 1, 'ACCEPTED'),
]
if args.case:
    cases = [case for case in cases if case[0] in args.case]
    if not cases:
        parser.error('No matching test cases')


def unprivileged():
    os.setgroups([])
    os.setgid(65534)
    os.setuid(65534)
    resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))


run_root = Path('/run/lrun')
created_run_root = not run_root.exists()
run_root.mkdir(exist_ok=True)
subprocess.run(['mount', '-t', 'tmpfs', '-o', 'size=1m,mode=0755', 'tmpfs', str(run_root)], check=True)
(run_root / 'mirrorfs' / hashlib.sha1(mirror.encode()).hexdigest()).mkdir(parents=True)
results = []
try:
    for name, mode, judge_mode, expected in cases:
        run = work / 'runs' / name
        run.mkdir()
        os.chown(run, 65534, 65534)
        contestant = work / 'fixtures' / (name + '.cpp')
        contestant.write_text('#define MODE ' + str(mode) + '\n' + template)
        interactor = work / 'fixtures/interactor.cpp'
        if name in ('python_contestant', 'both_python'):
            contestant = work / 'fixtures/contestant.py3'
        if name in ('python_interactor', 'both_python'):
            interactor = work / 'fixtures/interactor.py3'
        env = os.environ.copy()
        backend_log = run / 'backend.jsonl'
        env.update(PATH=str(work / 'bin') + ':/usr/bin:/bin', HOME=str(run),
                   TEST_BACKEND_LOG=str(backend_log), TEST_RUN_DIR=str(run))
        if name == 'incomplete_sandbox_report':
            env['TEST_BAD_REPORT'] = '1'
        if name == 'wait_for_sandbox_cleanup':
            env['TEST_CLEANUP_DELAY'] = '0.15'
        count = {'two_testcases': 2, 'many_cases_low_fd_limit': 30, 'parallel_cases': 12}.get(name, 1)
        threads = '4' if name == 'parallel_cases' else '1'
        command = [str(binary), '--etc-dir', str(work / 'config'), '--cache-dir', str(run / 'cache'),
                   '--threads', threads, '--keep-stderr', '--solution-code', str(contestant),
                   '--user-code', str(interactor), '--max-cpu-time', '0.3',
                   '--max-real-time', '1.5', '--max-checker-cpu-time', '0.2',
                   '--max-checker-real-time', '3', '--max-memory', '134217728']
        if name == 'interactor_own_wall_limit':
            command += ['--max-real-time', '0.15']
        if name == 'sandbox_launch_error':
            command += ['--user-stderr', str(run / 'missing-directory/stderr.log')]
        for i in range(count):
            data, answer = run / (str(i) + '.in'), run / (str(i) + '.out')
            secret = (37 + i * 17) % 100 + 1
            data.write_text(f'{secret} {judge_mode}\n')
            answer.write_text(f'{secret}\n')
            command += ['--testcase', '--input', str(data), '--output', str(answer)]
        started = time.monotonic()
        with (output / (name + '.stderr.log')).open('w') as stderr:
            child = subprocess.Popen(command, env=env, stdout=subprocess.PIPE, stderr=stderr,
                                     text=True, preexec_fn=unprivileged, start_new_session=True)
            timed_out = False
            try:
                stdout, _ = child.communicate(timeout=20)
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(child.pid, signal.SIGKILL)
                stdout, _ = child.communicate()
        (output / (name + '.json')).write_text(stdout)
        records = [json.loads(line) for line in backend_log.read_text().splitlines()] if backend_log.exists() else []
        (output / (name + '.backend.jsonl')).write_text('\n'.join(json.dumps(x) for x in records) + '\n')
        try:
            report = json.loads(stdout)
        except json.JSONDecodeError:
            report = {}
        actual = [case.get('result') for case in report.get('testcases', [])]
        completed = {record['cleanup_complete'] for record in records if 'cleanup_complete' in record}
        launched = {record['pid'] for record in records if 'pid' in record}
        cleanup_ok = launched == completed and bool(launched)
        stderr_ok = all('CONTESTANT' in case.get('stderr', '') and 'INTERACTOR' not in case.get('stderr', '')
                        and 'INTERACTOR' in case.get('judgeStderr', '')
                        and 'CONTESTANT' not in case.get('judgeStderr', '') for case in report.get('testcases', []))
        if name == 'sandbox_launch_error':
            stderr_ok = all(not case.get('stderr') and 'INTERACTOR' in case.get('judgeStderr', '')
                            for case in report.get('testcases', []))
        live = []
        for pid in launched:
            stat = Path(f'/proc/{pid}/stat')
            if stat.exists():
                live.append(pid)
        passed = (not timed_out and child.returncode == 0 and actual == [expected] * count
                  and cleanup_ok and stderr_ok and not live)
        result = dict(name=name, expected=expected, actual=actual, passed=passed,
                      cleanup_complete=cleanup_ok, separate_stderr=stderr_ok, remaining_pids=live,
                      outer_timeout=timed_out, seconds=round(time.monotonic() - started, 3))
        results.append(result)
        print(json.dumps(result), flush=True)
        # Test-only cleanup on failures; never use this as the success criterion.
        try:
            os.killpg(child.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
finally:
    subprocess.run(['umount', str(run_root)], check=True)
    if created_run_root:
        run_root.rmdir()
    shutil.rmtree(work)

(output / 'results.json').write_text(json.dumps({
    'backend': 'TEST_ADAPTER_NO_SANDBOX', 'binary': str(binary), 'results': results,
    'passed': sum(case['passed'] for case in results), 'total': len(results),
}, indent=2) + '\n')
raise SystemExit(0 if all(case['passed'] for case in results) else 1)
