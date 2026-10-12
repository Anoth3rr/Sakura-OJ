"""Three judging workflows backed by this repository's real lrun sandbox."""
from dataclasses import dataclass
import hashlib
import json
import math
import os
import platform
from pathlib import Path
import shutil
import signal
import stat
import subprocess
import tempfile
from .languages import Languages, LanguageError, Profile, expand
from .models import is_multipass, is_testlib_communication
from .toolchains import language_catalog

MIB = 1024 * 1024
MIRROR = '''# newjudge studio v2
mkdir /work/
mkdir /tmp/
mkdir /dev/
mkdir /proc/
mirror /usr/
mirror /bin/
mirror /lib/
mirror /lib64/
mirror /etc/ld.so.cache
mirror /etc/alternatives/
mirror /etc/java-21-openjdk/
touch /etc/passwd
'''
BLOCK_SYSCALLS = '!ptrace,unshare,setns,mount,umount2,bpf,kexec_load,init_module,finit_module,delete_module,reboot'


class JudgeError(Exception):
    pass


class CompileError(JudgeError):
    pass


@dataclass
class Program:
    path: Path
    language: str
    profile: Profile


@dataclass
class Running:
    process: subprocess.Popen
    control: Path
    wall: float
    output_limit: int


def text(path, limit=16384):
    try:
        with Path(path).open('rb') as f:
            return f.read(limit).decode('utf-8', errors='replace')
    except FileNotFoundError:
        return ''


class Engine:
    def __init__(self, root, runtime, testlib, etc_dir=None, workflow=None):
        self.root, self.runtime, self.testlib = Path(root), Path(runtime), Path(testlib)
        self.cache = self.root / 'compiled'
        self.work = self.root / 'sandbox-work'
        self.control = self.root / 'sandbox-control'
        self.cache.mkdir(parents=True, exist_ok=True)
        self.work.mkdir(parents=True, exist_ok=True)
        self.control.mkdir(parents=True, exist_ok=True)
        self.mirrors = self.root / 'mirror-config'
        self.mirrors.mkdir(parents=True, exist_ok=True)
        self.languages = Languages(etc_dir or self.runtime / 'etc/ljudge')
        self.workflow = Path(workflow or os.environ.get('NEWJUDGE_WORKFLOW') or self.runtime / 'bin/lworkflow')
        self.header_hash = hashlib.sha256(self.testlib.read_bytes()).hexdigest()
        self.mirror_name = hashlib.sha1(MIRROR.encode()).hexdigest()
        self.chroot = Path('/run/lrun/mirrorfs') / self.mirror_name

    def prepare(self):
        if os.getuid() == 0:
            raise JudgeError('评测服务必须使用专用非 root 账户启动')
        config = self.runtime / 'mirrorfs.conf'
        if config.read_text() != MIRROR:
            raise JudgeError('沙箱文件系统配置与服务版本不一致，请重新安装运行环境')
        if not self.chroot.exists():
            proc = subprocess.run([str(self.runtime / 'bin/lrun-mirrorfs'), '--name', self.mirror_name,
                                   '--setup', str(config)], capture_output=True, text=True, timeout=15, umask=0o022)
            if proc.returncode:
                raise JudgeError('准备沙箱失败：' + proc.stderr[-2000:])
        if not Path('/sys/fs/cgroup/memory/memory.limit_in_bytes').exists():
            raise JudgeError('当前内核没有挂载 cgroup v1 memory 控制器')
        if not self.languages.catalog():
            raise JudgeError(f'没有语言配置，请将 --etc-dir 指向原生 ljudge 的配置目录：{self.languages.directory}')
        if not self.workflow.is_file() or not os.access(self.workflow, os.X_OK):
            raise JudgeError(f'缺少原生流程执行器，请构建/安装 lworkflow：{self.workflow}')

    def health(self):
        languages = self.languages.catalog()
        try:
            ready = bool(languages) and self.workflow.is_file() and os.access(self.workflow, os.X_OK) and self.chroot.exists() and Path('/sys/fs/cgroup/memory/memory.limit_in_bytes').exists()
        except OSError:
            ready = False
        return dict(ready=ready, backend='newjudge / lrun', kernel=platform.release(),
                    languages=[item['label'] for item in language_catalog() if item['available']], profiles=languages, workflow=str(self.workflow), etc_dir=str(self.languages.directory),
                    testlib=self.header_hash[:12])

    def _profile_chroot(self, profile, stage):
        content = profile.contents.get(stage + '.mirrorfs')
        if content is None:
            raise JudgeError(f'{profile.id} 缺少 {stage}.mirrorfs 配置')
        # Native programs work in /tmp. /work is an alias retained for Studio's
        # checker arguments. Each invocation binds its own fresh directory.
        content += '\nmkdir /work/\nmkdir /tmp/\nmkdir /dev/\nmkdir /proc/\ntouch /etc/passwd\n'
        name = hashlib.sha1(content.encode()).hexdigest()
        chroot = Path('/run/lrun/mirrorfs') / name
        if not chroot.exists():
            config = self.mirrors / (name + '.conf')
            config.write_text(content)
            proc = subprocess.run([str(self.runtime / 'bin/lrun-mirrorfs'), '--name', name,
                                   '--setup', str(config)], capture_output=True, text=True, timeout=15, umask=0o022)
            if proc.returncode:
                raise JudgeError(f'{profile.id} 沙箱准备失败：' + proc.stderr[-2000:])
        return chroot

    @staticmethod
    def _mappings(profile, directory, chroot, memory):
        return dict(src=profile.src, exe=profile.exe, dir=str(directory), chroot=str(chroot),
                    jvmmemory=str(memory))

    def _sandbox_command(self, directory, command, *, cpu=2, wall=5,
                         memory=256 * MIB, output=8 * MIB, files=None, phase=None,
                         profile=None, stage='run', feedback=None):
        d = Path(directory)
        chroot = self._profile_chroot(profile, stage) if profile else self.chroot
        mappings = self._mappings(profile, d, chroot, memory) if profile else {}
        command = expand(command, mappings) if profile else command
        args = [str(self.runtime / 'bin/lrun'), '--reset-env', 'true', '--network', 'false',
                '--basic-devices', 'true', '--remount-dev', 'true', '--isolate-process', 'true',
                '--chroot', str(chroot), '--bindfs', str(chroot / 'work'), str(d),
                '--bindfs', str(chroot / 'tmp'), str(d), '--chdir', '/tmp', '--max-cpu-time', str(cpu),
                '--max-real-time', str(wall), '--max-memory', str(memory), '--max-output', str(output),
                '--max-nprocess', '64', '--max-nfile', '128',
                '--no-new-privs', 'true', '--syscalls', BLOCK_SYSCALLS,
                '--env', 'PATH', '/usr/bin:/bin:/etc/alternatives:/usr/local/bin', '--env', 'HOME', '/tmp',
                '--env', 'LANG', 'C.UTF-8', '--env', 'ONLINE_JUDGE', '1']
        if os.environ.get('JAVA_HOME'):
            args += ['--env', 'JAVA_HOME', os.environ['JAVA_HOME']]
        if profile:
            args += profile.lrun_args(stage, mappings)
            if profile.value(stage + 'fake_passwd', 'true') == 'true':
                passwd = self.mirrors / 'passwd'
                if not passwd.exists():
                    passwd.write_text(f'nobody:x:{os.getuid()}:{os.getgid()}::/tmp:/bin/false\n')
                args += ['--bindfs-ro', str(chroot / 'etc/passwd'), str(passwd)]
            overrides = profile.paths.get(stage + '.fs_override')
            for entry in sorted(overrides.iterdir()) if overrides else ():
                target = chroot / entry.name.replace('__', '/').lstrip('/')
                if target.exists():
                    args += ['--bindfs-ro', str(target), str(entry)]
        for name, path in (files or {}).items():
            assert name in ('input', 'output', 'answer')
            path = str(path) if str(path).startswith('@') else str(Path(path).resolve())
            for location in ('work', 'tmp'):
                args += ['--bindfs-ro', str(chroot / location / name), path]
        if feedback is not None:
            for location in ('work', 'tmp'):
                args += ['--bindfs', str(chroot / location / 'feedback'), str(feedback)]
        if phase:
            args += ['--env', 'JUDGE_PHASE', phase]
        args += ['--'] + command
        return args

    def _spawn(self, directory, command, *, stdin=None, stdout=None, **limits):
        for name in limits.get('files') or {}:
            (Path(directory) / name).touch()
        args = self._sandbox_command(directory, command, **limits)
        control = Path(tempfile.mkdtemp(dir=self.control))
        # Positional arguments are never evaluated as shell code. This opens the
        # sandbox status descriptor without unsafe preexec_fn in a threaded server.
        launch = ['/bin/sh', '-c', 'exec 3>"$1"; shift; exec "$@"', 'lrun-status', str(control / 'status')] + args
        owned = []
        try:
            if stdin is None:
                stdin = open(os.devnull, 'rb')
                owned.append(stdin)
            if stdout is None:
                stdout = (control / 'stdout').open('wb')
                owned.append(stdout)
            stderr = (control / 'stderr').open('wb')
            owned.append(stderr)
            process = subprocess.Popen(launch, stdin=stdin, stdout=stdout, stderr=stderr, close_fds=True)
            return Running(process, control, limits.get('wall', 5), limits.get('output', 8 * MIB))
        except BaseException:
            shutil.rmtree(control)
            raise
        finally:
            for f in owned:
                f.close()

    def _finish(self, running):
        try:
            code = running.process.wait(timeout=running.wall + 12)
        except subprocess.TimeoutExpired as exc:
            # lrun normally enforces its own finite wall limit and reaps its
            # namespace. Never fabricate a contestant verdict on supervisor failure.
            raise JudgeError('沙箱监督进程未正常退出，请检查评测机日志') from exc
        stderr = text(running.control / 'stderr')
        status = text(running.control / 'status')
        output_path = running.control / 'stdout'
        payload = b''
        if output_path.exists():
            with output_path.open('rb') as f:
                payload = f.read(running.output_limit + 1)
        shutil.rmtree(running.control)
        fields = {}
        try:
            for line in status.splitlines():
                k, v = line.split()
                if k in fields:
                    raise ValueError('duplicate status field')
                fields[k] = v
            if set(fields) != {'MEMORY', 'CPUTIME', 'REALTIME', 'SIGNALED', 'EXITCODE', 'TERMSIG', 'EXCEED'}:
                raise ValueError('missing status fields')
            memory, cpu, wall = int(fields['MEMORY']), float(fields['CPUTIME']), float(fields['REALTIME'])
            if memory < 0 or not all(math.isfinite(x) and x >= 0 for x in (cpu, wall)):
                raise ValueError('invalid resource measurement')
            sig, exitcode, termsig = int(fields['SIGNALED']), int(fields['EXITCODE']), int(fields['TERMSIG'])
            if sig not in (0, 1) or not 0 <= exitcode <= 255 or not 0 <= termsig < signal.NSIG:
                raise ValueError('invalid process status')
            exceed = fields['EXCEED']
            if exceed not in ('none', 'MEMORY', 'CPU_TIME', 'REAL_TIME', 'OUTPUT'):
                raise ValueError('invalid limit')
        except (ValueError, KeyError) as exc:
            raise JudgeError('沙箱状态报告不完整：' + stderr[-2000:]) from exc
        if code != 0:
            raise JudgeError(f'沙箱启动失败（{code}）：{stderr[-2000:]}')
        verdict = {'MEMORY': 'MLE', 'CPU_TIME': 'TLE', 'REAL_TIME': 'TLE', 'OUTPUT': 'OLE'}.get(exceed, 'OK')
        if verdict == 'OK' and (sig or exitcode):
            verdict = 'RE'
        return dict(verdict=verdict, time_ms=round(cpu * 1000, 3), wall_ms=round(wall * 1000, 3),
                    memory_kb=round(memory / 1024), exit_code=exitcode, signal=termsig if sig else 0,
                    exceed=exceed, stderr=stderr, output=payload)

    def compile(self, item, role):
        try:
            profile = self.languages.resolve(item['language'])
        except LanguageError as exc:
            raise CompileError(str(exc)) from exc
        key = hashlib.sha256(('profiles-v1\0' + item['language'] + '\0' + item['content'] +
                              self.header_hash + profile.fingerprint).encode()).hexdigest()
        dest = self.cache / key
        if dest.is_dir():
            return Program(dest, item['language'], profile)
        with tempfile.TemporaryDirectory(dir=self.work, prefix='compile-') as tmp:
            d = Path(tmp)
            (d / profile.src).write_text(item['content'])
            shutil.copyfile(self.testlib, d / 'testlib.h')
            command = profile.command('compile')
            stage = 'compile'
            # Preserve the old Studio Python alias's syntax-error-as-CE behavior,
            # using the configured interpreter, including its sandbox and limits.
            if not command and item['language'] == 'python':
                command = [part for token in profile.command('run')
                           for part in (['-m', 'py_compile', '$src'] if token == '$src' else [token])]
                stage = 'run'
            if command:
                report = self._finish(self._spawn(d, command, cpu=30, wall=45,
                    memory=1024 * MIB, output=64 * MIB, profile=profile, stage=stage))
                if report['verdict'] != 'OK' or (stage == 'compile' and not (d / profile.exe).is_file()):
                    raise CompileError(f'{role} 编译失败（{report["verdict"]}）\n{report["stderr"]}' +
                                       report['output'].decode(errors='replace')[:16384])
            # Java/Scala/Kotlin and similar languages produce multiple files.
            # Cache the complete tree; reject links/devices before copying anything
            # out of the sandbox. Runs always receive independent writable copies.
            size, count = 0, 0
            for entry in d.rglob('*'):
                info = entry.lstat()
                if not (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)):
                    raise CompileError(f'{role} 编译产物只能包含普通文件和目录')
                size += info.st_size
                count += 1
                if size > 64 * MIB or count > 4096:
                    raise CompileError(f'{role} 编译产物超过 64 MiB 或 4096 个文件')
            # A rename publishes only complete caches, even if compilation fails.
            with tempfile.TemporaryDirectory(dir=self.cache, prefix='.pending-') as pending:
                tree = Path(pending) / 'files'
                shutil.copytree(d, tree)
                try:
                    tree.rename(dest)
                except OSError:
                    if not dest.is_dir():
                        raise
        return Program(dest, item['language'], profile)

    def stage(self, program, directory, args=()):
        d = Path(directory)
        shutil.copytree(program.path, d, dirs_exist_ok=True)
        return program.profile.command('run') + list(args)

    def run(self, program, *, data=b'', args=(), files=None, cpu=2, wall=5,
            memory=256 * MIB, output=8 * MIB, phase=None):
        with tempfile.TemporaryDirectory(dir=self.work, prefix='run-') as tmp:
            d = Path(tmp)
            cmd = self.stage(program, d, args)
            (d / '.stdin').write_bytes(data)
            with (d / '.stdin').open('rb') as inp:
                running = self._spawn(d, cmd, stdin=inp, cpu=cpu, wall=wall, memory=memory,
                                      output=output, files=files, phase=phase, profile=program.profile)
                result = self._finish(running)
            return result

    @staticmethod
    def limits(p):
        return dict(cpu=p['time_ms'] / 1000, wall=max(2, p['time_ms'] / 1000 * 3),
                    memory=p['memory_mb'] * MIB, output=p['output_kb'] * 1024)

    def _native_program(self, program, *, args=(), files=None, feedback=False, **limits):
        return dict(artifacts=str(program.path.resolve()),
                    command=self._sandbox_command('@WORK@', program.profile.command('run') + list(args),
                        profile=program.profile, files=files, feedback='@FEEDBACK@' if feedback else None, **limits),
                    files=list(files or {}), directories=['feedback'] if feedback else [],
                    wall_limit=limits.get('wall', 5), output_limit=limits.get('output', 8 * MIB))

    def _workflow(self, mode, *, input_path=None, answer_path=None, data=None, **specs):
        # Python serializes a request. Native lworkflow owns process lifetimes,
        # pipes, fresh execution directories, pass transitions and verdicts.
        with tempfile.TemporaryDirectory(dir=self.control, prefix='workflow-') as tmp:
            d = Path(tmp)
            if input_path is None:
                input_path = d / 'input'
                input_path.write_bytes(data or b'')
            if answer_path is None:
                answer_path = d / 'answer'
                answer_path.write_bytes(b'')
            request = dict(version=1, mode=mode, work_root=str(self.work.resolve()),
                           input=str(Path(input_path).resolve()), answer=str(Path(answer_path).resolve()), **specs)
            manifest, output = d / 'request.json', d / 'output'
            manifest.write_text(json.dumps(request))
            walls = sum(v.get('wall_limit', 0) + 15 for v in specs.values() if isinstance(v, dict))
            timeout = walls * specs.get('validation_passes', 1) + 15
            try:
                proc = subprocess.run([str(self.workflow), '--request', str(manifest), '--output', str(output)],
                                      capture_output=True, timeout=timeout)
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise JudgeError('原生流程执行器未正常结束：' + str(exc)) from exc
            if proc.returncode:
                raise JudgeError(proc.stderr.decode(errors='replace')[-16384:])
            try:
                result = json.loads(proc.stdout)
                if not isinstance(result, dict) or result.get('backend') != 'lworkflow / lrun':
                    raise ValueError('invalid workflow report')
            except (ValueError, UnicodeDecodeError) as exc:
                raise JudgeError('原生流程执行器返回无效报告') from exc
            result['output'] = output.read_bytes()
            return result

    def twice(self, program, data, p, receiver=None):
        limits = self.limits(p)
        send_limits = dict(limits, output=max(MIB, p['message_bytes'] + 1))
        return self._workflow('run-twice', data=data, message_bytes=p['message_bytes'],
            program=self._native_program(program, args=['send'], phase='send', **send_limits),
            receiver=self._native_program(receiver or program, args=['receive'], phase='receive', **limits))

    def interaction(self, program, interactor, input_path, answer_path, p):
        return self._workflow('interactive', input_path=input_path, answer_path=answer_path,
            program=self._native_program(program, **self.limits(p)),
            interactor=self._native_program(interactor, args=['/work/input', '/work/transcript', '/work/answer'],
                files={'input': '@INPUT@', 'answer': '@ANSWER@'}, cpu=5,
                wall=max(5, p['time_ms'] / 1000 * 3 + 2), memory=512 * MIB))

    def multipass(self, program, validator, input_path, answer_path, p):
        return self._workflow('multipass', input_path=input_path, answer_path=answer_path,
            validation_passes=p.get('validation_passes', 2),
            program=self._native_program(program, **self.limits(p)),
            validator=self._native_program(validator, args=['/work/input', '/work/answer', '/work/feedback'],
                files={'input': '@INPUT@', 'answer': '@ANSWER@'}, feedback=True, cpu=5, wall=8, memory=512 * MIB))

    def communication(self, program, interactor, checker, input_path, answer_path, p):
        if interactor is None or checker is None:
            raise JudgeError('testlib 两轮通信题必须提供 interactor 和 checker')
        return self._workflow('communication', input_path=input_path, answer_path=answer_path,
            program=self._native_program(program, **self.limits(p)),
            interactor=self._native_program(interactor, args=['/work/input', '/work/transcript', '/work/answer'],
                files={'input': '@INPUT@', 'answer': '@ANSWER@'}, cpu=5,
                wall=max(5, p['time_ms'] / 1000 * 3 + 2), memory=512 * MIB),
            checker=self._native_program(checker, args=['/work/input', '/work/output', '/work/answer'],
                files={'input': '@INPUT@', 'output': '@OUTPUT@', 'answer': '@ANSWER@'},
                cpu=5, wall=8, memory=512 * MIB))

    def check(self, checker, input_path, answer_path, candidate):
        with tempfile.TemporaryDirectory(dir=self.work, prefix='check-') as tmp:
            out = Path(tmp) / 'candidate'
            out.write_bytes(candidate)
            result = self.run(checker, args=['/work/input', '/work/output', '/work/answer'],
                              files={'input': input_path, 'output': out, 'answer': answer_path}, cpu=5, wall=8)
        if result['exceed'] != 'none' or result['signal']:
            return dict(verdict='IE', message='checker 运行异常：' + result['stderr'])
        return dict(verdict={0: 'AC', 1: 'WA', 2: 'PE'}.get(result['exit_code'], 'IE'),
                    message=result['stderr'].strip() or result['output'].decode(errors='replace')[:2000])

    def judge(self, program, checker, case, p, interactor=None, receiver=None):
        if checker is None and p['mode'] != 'interactive':
            raise JudgeError('普通题和通信题必须提供 checker')
        data, inp, ans = case['input'].read_bytes(), case['input'], case['answer']
        if is_testlib_communication(p):
            if receiver is not None:
                raise JudgeError('testlib 两轮通信每轮运行同一份程序，不使用独立 Receiver')
            return self.summary(self.communication(program, interactor, checker, inp, ans, p))
        if is_multipass(p):
            if receiver is not None:
                raise JudgeError('DOMjudge 多阶段协议每轮运行同一份程序，不使用独立 Receiver')
            return self.summary(self.multipass(program, checker, inp, ans, p))
        if p['mode'] == 'interactive':
            result = self.interaction(program, interactor, inp, ans, p)
        elif p['mode'] == 'communication':
            result = self.twice(program, data, p, receiver)
        else:
            result = self.run(program, data=data, **self.limits(p))
        if result['verdict'] == 'OK':
            if checker is not None:
                result.update(self.check(checker, inp, ans, result['output']))
            else:
                result.update(verdict='AC', message=result['judge_stderr'].strip() or 'interactor accepted')
        return self.summary(result)

    @staticmethod
    def summary(result):
        return {**{k: v for k, v in result.items() if k != 'output'},
                'output_preview': result.get('output', b'')[:2000].decode('utf-8', errors='replace')}
