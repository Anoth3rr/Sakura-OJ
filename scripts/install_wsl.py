#!/usr/bin/env python3
"""Install Sakura's own sandbox, non-root service and unified FastAPI runtime."""
import argparse
import os
from pathlib import Path
import pwd
import secrets
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.studio.engine import MIRROR
from app.studio.toolchains import JAVA, JAVAC, java_options, language_catalog


def run(*args, **kwargs):
    subprocess.run(list(args), check=True, **kwargs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skip-build', action='store_true')
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    if os.getuid() != 0:
        raise SystemExit('请使用 sudo python3 scripts/install_wsl.py')
    if not Path('/sys/fs/cgroup/memory/memory.limit_in_bytes').exists():
        raise SystemExit('当前内核缺少 cgroup v1 memory 控制器；参见 README.md')
    if not 1 <= args.port <= 65535:
        raise SystemExit('端口无效')
    missing = [item['label'] for item in language_catalog() if not item['available']]
    if missing:
        raise SystemExit('缺少工具链：' + '、'.join(missing) +
                         '\n请先 apt-get install build-essential python3 pypy3 openjdk-21-jdk-headless')
    try:
        account = pwd.getpwnam('sakura')
    except KeyError:
        run('useradd', '--system', '--user-group', '--home-dir', '/var/lib/sakura',
            '--shell', '/usr/sbin/nologin', 'sakura')
        account = pwd.getpwnam('sakura')
    runtime = Path('/opt/sakura/runtime')
    (runtime / 'bin').mkdir(parents=True, exist_ok=True)
    if not args.skip_build:
        with tempfile.TemporaryDirectory(prefix='sakura-build-') as tmp:
            source = Path(tmp) / 'newjudge'
            shutil.copytree(ROOT / 'judge/newjudge', source,
                            ignore=shutil.ignore_patterns('*.o', '__pycache__', 'results-*'))
            build = source / 'lrun'
            # Do not reuse binaries copied from a Windows checkout or an older build.
            for binary in (build / 'src/lrun', build / 'utils/mirrorfs/mirrorfs',
                           source / 'ljudge/src/ljudge', source / 'ljudge/src/linteractive', source / 'ljudge/src/lworkflow'):
                binary.unlink(missing_ok=True)
            link = build / 'utils/mirrorfs/utils'
            if link.is_file() or link.is_symlink():
                link.unlink()
            if not link.exists():
                shutil.copytree(build / 'src/utils', link)
            run('rake', '-j', '4', cwd=build / 'src', env=dict(os.environ, NDEBUG='1'))
            run('make', '-j', '4', cwd=build / 'utils/mirrorfs')
            run('make', '-j', '4', 'NDEBUG=1', cwd=source / 'ljudge/src')
            binaries = {'lrun': build / 'src/lrun', 'lrun-mirrorfs': build / 'utils/mirrorfs/mirrorfs',
                        'ljudge': source / 'ljudge/src/ljudge', 'linteractive': source / 'ljudge/src/linteractive',
                        'lworkflow': source / 'ljudge/src/lworkflow'}
            for name, binary in binaries.items():
                staged = runtime / 'bin' / (name + '.new')
                shutil.copyfile(binary, staged)
                os.chown(staged, 0, account.pw_gid)
                staged.chmod(0o4550 if name.startswith('lrun') else 0o750)
                staged.replace(runtime / 'bin' / name)
    for name in ('lrun', 'lrun-mirrorfs', 'ljudge', 'linteractive', 'lworkflow'):
        if not (runtime / 'bin' / name).is_file():
            raise SystemExit('请先构建运行环境，缺少 ' + name)
    (runtime / 'mirrorfs.conf').write_text(MIRROR)
    shutil.copyfile(ROOT / 'app/studio/vendor/testlib.h', runtime / 'testlib.h')
    profiles = runtime / 'etc/ljudge'
    (profiles / '_default').mkdir(parents=True, exist_ok=True)
    shutil.copyfile(runtime / 'testlib.h', profiles / '_default/testlib.h')
    commands = {
        'cpp': ('g++\n-std=c++17\n-O2\n-pipe\n-DONLINE_JUDGE\n-o\n$exe\n$src\n', './$exe\n', 'g++\n--version\n'),
        'c': ('gcc\n-std=c17\n-O2\n-o\n$exe\n$src\n-lm\n', './$exe\n', 'gcc\n--version\n'),
        'py3': ('', 'python3\n$src\n', 'python3\n--version\n'),
        'pypy': ('/usr/bin/pypy3\n-B\n-c\nimport sys; compile(open(sys.argv[1], encoding="utf-8").read(), sys.argv[1], "exec"); open(sys.argv[2], "wb").close()\n$src\n$exe\n',
                 '/usr/bin/pypy3\n-B\n$src\n', '/usr/bin/pypy3\n--version\n'),
        'java': ('\n'.join([JAVAC, *['-J' + opt for opt in java_options(512 * 1024 * 1024)],
                            '-encoding', 'UTF-8', '-proc:none', '$src']) + '\n',
                 '\n'.join([JAVA, '-Xmx$jvmmemory', *java_options(256 * 1024 * 1024)[1:], '-cp', '.', 'Main']) + '\n',
                 JAVA + '\n--version\n'),
    }
    for language, (compile_command, run_command, version) in commands.items():
        profile = profiles / language
        profile.mkdir(exist_ok=True)
        for name, contents in {'compile.cmd_list': compile_command, 'run.cmd_list': run_command,
                               'version.cmd_list': version, 'compile.mirrorfs': MIRROR,
                               'run.mirrorfs': MIRROR}.items():
            (profile / name).write_text(contents)
    (profiles / 'java/compile.src_name').write_text('Main.java\n')
    (profiles / 'java/compile.exe_name').write_text('Main.class\n')
    for alias, language in {'cc':'cpp', 'cxx':'cpp', 'py':'py3', 'pypy3':'pypy'}.items():
        path = profiles / alias
        if not path.exists():
            path.symlink_to(language, target_is_directory=True)
    # Isolate mutable compiler artifacts on Linux's filesystem, not the source checkout.
    work = Path('/var/lib/sakura/judge')
    work.mkdir(parents=True, exist_ok=True)
    os.chown(work, account.pw_uid, account.pw_gid)
    work.chmod(0o700)
    native = work / 'native'
    native.mkdir(exist_ok=True)
    os.chown(native, account.pw_uid, account.pw_gid)
    native.chmod(0o700)
    venv = Path('/opt/sakura/venv')
    if not (venv / 'bin/pip').exists():
        run(sys.executable, '-m', 'venv', str(venv))
    run(str(venv / 'bin/pip'), 'install', '-r', str(ROOT / 'requirements.txt'))
    Path('/etc/tmpfiles.d/sakura.conf').write_text('d /run/lrun 0755 root root -\nd /run/lrun/mirrorfs 0755 root root -\n')
    run('systemd-tmpfiles', '--create', '/etc/tmpfiles.d/sakura.conf')
    # Environment overrides are kept outside the checkout and never overwritten.
    env = Path('/etc/sakura.env')
    if not env.exists():
        # Create with restricted permissions from the first write; never log the
        # generated password or store it in the checkout.
        descriptor = os.open(env, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, 'w', encoding='utf-8') as config:
            config.write('OJ_AUTH_REQUIRED=true\nOJ_JUDGE_MODE=newjudge\nSAKURA_SEED_DEMO=false\n'
                         'OJ_ADMIN_USERNAME=admin\nOJ_ADMIN_PASSWORD=' + secrets.token_urlsafe(32) + '\n')
        print('Initial administrator credentials were created in /etc/sakura.env (root only).')
    # A fresh Linux checkout is commonly owned by the installing user. Give the
    # service its own writable state directories without changing source ownership.
    for directory in (ROOT / 'data', ROOT / 'runtime'):
        if not directory.exists():
            directory.mkdir(mode=0o700)
            os.chown(directory, account.pw_uid, account.pw_gid)
    unit = f'''[Unit]
Description=Sakura OJ, team management and newjudge
After=local-fs.target

[Service]
User=sakura
Group=sakura
WorkingDirectory={ROOT}
EnvironmentFile=/etc/sakura.env
Environment=PYTHONUNBUFFERED=1
Environment=PATH=/opt/sakura/runtime/bin:/opt/sakura/venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/opt/sakura/venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port {args.port}
Restart=on-failure
RestartSec=3
UMask=0077
KillMode=control-group
TimeoutStopSec=120

[Install]
WantedBy=multi-user.target
'''
    Path('/etc/systemd/system/sakura.service').write_text(unit)
    run('systemctl', 'daemon-reload')
    run('systemctl', 'enable', 'sakura.service')
    run('systemctl', 'restart', 'sakura.service')
    print(f'Sakura: http://localhost:{args.port}; journalctl -u sakura')


if __name__ == '__main__':
    main()
