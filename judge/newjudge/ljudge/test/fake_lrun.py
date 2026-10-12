#!/usr/bin/python3
"""TEST ADAPTER ONLY. Runs trusted fixtures; provides NO sandbox isolation.

Keep inherited pipe endpoints open in the parent, as the repository lrun does.
Child stdin/stdout are real pipes, and exit/signal/elapsed-time reports are real.
This is solely for exercising linteractive orchestration and verdicts.
It cannot validate the real sandbox, seccomp, memory accounting or production use.
"""
import json
import os
from pathlib import Path
import resource
import shutil
import signal
import subprocess
import sys
import tempfile
import time

args = sys.argv[1:]
split = args.index('--')
options, command = args[:split], args[split + 1:]
binds, values = [], {}
i = 0
while i < len(options):
    key = options[i]
    if key in ('--bindfs', '--bindfs-ro', '--env'):
        if key != '--env':
            binds.append((options[i + 1], options[i + 2]))
        i += 3
    else:
        values[key] = options[i + 1]
        i += 2

dest = next(Path(source) for target, source in binds if target.endswith('/tmp'))
role = 'judge' if 'judge' in dest.parts else 'user'
is_compile = command[0] == 'g++'
private_dir = None
if not is_compile:
    # Emulate per-process bind mounts without writing testcase data into the
    # shared build directory. This permits independent concurrent testcases.
    private_dir = tempfile.TemporaryDirectory(prefix='fixture-', dir=os.environ['TEST_RUN_DIR'])
    shutil.copytree(dest, private_dir.name, dirs_exist_ok=True)
    dest = Path(private_dir.name)
for target, source in binds:
    if target.endswith('/tmp/input') or target.endswith('/tmp/output'):
        shutil.copyfile(source, dest / Path(target).name)

stdin_fd = int(values.get('--stdin-fd', '0'))
stdout_fd = int(values.get('--stdout-fd', '1'))
wall_limit = float(values.get('--max-real-time', '10'))
cpu_limit = float(values.get('--max-cpu-time', '10'))
resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
started = time.monotonic()
child = subprocess.Popen(command, cwd=dest, stdin=stdin_fd, stdout=stdout_fd,
                         stderr=2, close_fds=True)
ticks = os.sysconf('SC_CLK_TCK')
exceed = 'none'
while True:
    pid, status, usage = os.wait4(child.pid, os.WNOHANG)
    if pid:
        break
    try:
        stat = Path('/proc/' + str(child.pid) + '/stat').read_text()
        fields = stat[stat.rfind(')') + 2:].split()
        cpu = (int(fields[11]) + int(fields[12])) / ticks
    except FileNotFoundError:
        continue
    if cpu_limit > 0 and cpu > cpu_limit:
        exceed = 'CPU_TIME'
    elif wall_limit > 0 and time.monotonic() - started > wall_limit:
        exceed = 'REAL_TIME'
    if exceed != 'none':
        child.kill()
        _, status, usage = os.wait4(child.pid, 0)
        break
    time.sleep(0.005)
child.returncode = os.waitstatus_to_exitcode(status)
report = {
    'MEMORY': usage.ru_maxrss * 1024,
    'CPUTIME': usage.ru_utime + usage.ru_stime,
    'REALTIME': time.monotonic() - started,
    'SIGNALED': int(os.WIFSIGNALED(status)),
    'EXITCODE': os.WEXITSTATUS(status),
    'TERMSIG': os.WTERMSIG(status),
    'EXCEED': exceed,
}
record = {'backend': 'TEST_ADAPTER_NO_SANDBOX', 'command': command, 'role': role,
          'pid': os.getpid(), 'is_compile': is_compile, 'options': values, **report}
logfd = os.open(os.environ['TEST_BACKEND_LOG'], os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
os.write(logfd, (json.dumps(record) + '\n').encode())
os.close(logfd)
payload = ''.join(f'{key:<9}{value}\n' for key, value in report.items())
if not is_compile and role == 'judge' and os.environ.get('TEST_BAD_REPORT'):
    payload = 'EXITCODE 0\nEXCEED none\n'
os.write(3, payload.encode())
os.close(3)
if private_dir:
    private_dir.cleanup()
time.sleep(float(os.environ.get('TEST_CLEANUP_DELAY', '0')))
logfd = os.open(os.environ['TEST_BACKEND_LOG'], os.O_WRONLY | os.O_APPEND)
os.write(logfd, (json.dumps({'cleanup_complete': os.getpid()}) + '\n').encode())
os.close(logfd)
sys.exit(report['EXITCODE'] if values.get('--pass-exitcode') == 'true' else 0)
