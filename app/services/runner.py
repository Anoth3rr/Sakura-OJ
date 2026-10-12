from __future__ import annotations

import os
import json
import shutil
import signal
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from ..config import Settings, settings


COMPILE_OUTPUT_LIMIT = 64 * 1024
RESULT_OUTPUT_LIMIT = 20 * 1024


@dataclass(frozen=True)
class LanguageSpec:
    id: str
    label: str
    source_name: str
    compiler_setting: str | None = None
    runtime_setting: str | None = None


LANGUAGE_SPECS = (
    LanguageSpec("c", "C 17", "main.c", compiler_setting="c_compiler"),
    LanguageSpec("cpp", "C++ 17", "main.cpp", compiler_setting="cpp_compiler"),
    LanguageSpec("python", "Python 3", "main.py", runtime_setting="python"),
    LanguageSpec("pypy", "PyPy 3", "main.py", runtime_setting="pypy"),
    LanguageSpec("java", "Java", "Main.java", compiler_setting="javac", runtime_setting="java"),
)

_DOCKER_ENV_KEYS = (
    "DOCKER_HOST",
    "DOCKER_CONTEXT",
    "DOCKER_CONFIG",
    "DOCKER_CERT_PATH",
    "DOCKER_TLS_VERIFY",
    "HOME",
    "USERPROFILE",
)
DOCKER_REPORT_OUTPUT_LIMIT = 64 * 1024 * 1024


@dataclass
class ProcessResult:
    return_code: int | None
    timed_out: bool
    output_limited: bool
    stdout: str
    stderr: str
    runtime_ms: int


def _resolve_executable(command: str | None) -> str | None:
    if not command:
        return None
    resolved = shutil.which(command)
    if resolved:
        return resolved
    path = Path(command)
    return str(path) if path.exists() else None


def language_catalog(runner_settings: Settings = settings) -> list[dict]:
    if runner_settings.judge_mode == 'newjudge':
        from ..studio.toolchains import language_catalog as sandbox_languages
        ready = os.name == 'posix' and (runner_settings.newjudge_runtime / 'bin/lrun').exists()
        return [dict(s, available=ready and s['available']) for s in sandbox_languages()]
    if (runner_settings.judge_mode or "").strip().lower() == "docker":
        docker_available = _resolve_executable(runner_settings.docker_cli) is not None
        return [
            {"id": spec.id, "label": spec.label, "available": docker_available}
            for spec in LANGUAGE_SPECS
        ]
    result = []
    for spec in LANGUAGE_SPECS:
        compiler = (
            _resolve_executable(getattr(runner_settings, spec.compiler_setting))
            if spec.compiler_setting
            else None
        )
        runtime = (
            _resolve_executable(getattr(runner_settings, spec.runtime_setting))
            if spec.runtime_setting
            else None
        )
        available = bool(compiler or runtime)
        if spec.id == "java":
            available = bool(compiler and runtime)
        result.append({"id": spec.id, "label": spec.label, "available": available})
    return result


def _safe_environment(
    work_dir: Path, *, extra_keys: Iterable[str] = ()
) -> dict[str, str]:
    # Keep only toolchain/runtime variables; user submissions never inherit secrets.
    environment = {
        "PATH": os.environ.get("PATH", ""),
        "TEMP": str(work_dir),
        "TMP": str(work_dir),
    }
    for key in ("SystemRoot", "SystemDrive", "WINDIR", "LANG", "LC_ALL"):
        if os.environ.get(key):
            environment[key] = os.environ[key]
    for key in extra_keys:
        if os.environ.get(key):
            environment[key] = os.environ[key]
    return environment


def _kill_process_tree(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    try:
        if os.name == "nt":
            # Kill the direct process immediately. The asynchronous taskkill
            # handles descendants without making the judge wait on shell startup.
            try:
                process.kill()
            except OSError:
                pass
            subprocess.Popen(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        else:
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
    except (OSError, subprocess.SubprocessError):
        try:
            process.kill()
        except OSError:
            pass


def _read_text(path: Path, limit: int) -> str:
    try:
        data = path.read_bytes()[:limit]
    except OSError:
        return ""
    return data.decode("utf-8", errors="replace")


def run_process(
    command: Iterable[str],
    *,
    cwd: Path,
    input_data: str = "",
    timeout_ms: int,
    output_limit: int,
    environment: dict[str, str] | None = None,
) -> ProcessResult:
    """Run a process with file-backed streams and wall-clock/output limits."""
    cwd.mkdir(parents=True, exist_ok=True)
    input_fd, input_name = tempfile.mkstemp(prefix="stdin-", dir=cwd)
    os.close(input_fd)
    input_path = Path(input_name)
    stdout_fd, stdout_name = tempfile.mkstemp(prefix="stdout-", suffix=".log", dir=cwd)
    stderr_fd, stderr_name = tempfile.mkstemp(prefix="stderr-", suffix=".log", dir=cwd)
    os.close(stdout_fd)
    os.close(stderr_fd)
    stdout_path = Path(stdout_name)
    stderr_path = Path(stderr_name)
    input_path.write_text(input_data, encoding="utf-8")
    process: subprocess.Popen[bytes] | None = None
    timed_out = False
    output_limited = False
    started = time.perf_counter()
    try:
        with (
            input_path.open("rb") as input_file,
            stdout_path.open("wb") as stdout_file,
            stderr_path.open("wb") as stderr_file,
        ):
            kwargs: dict[str, object] = {
                "cwd": str(cwd),
                "stdin": input_file,
                "stdout": stdout_file,
                "stderr": stderr_file,
                "env": environment or _safe_environment(cwd),
                "shell": False,
            }
            if os.name == "nt":
                kwargs["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            else:
                kwargs["start_new_session"] = True
            try:
                process = subprocess.Popen(list(command), **kwargs)  # type: ignore[arg-type]
            except OSError as exc:
                return ProcessResult(
                    return_code=None,
                    timed_out=False,
                    output_limited=False,
                    stdout="",
                    stderr=str(exc),
                    runtime_ms=max(0, round((time.perf_counter() - started) * 1000)),
                )

            deadline = started + max(1, timeout_ms) / 1000
            while process.poll() is None:
                try:
                    output_size = stdout_path.stat().st_size + stderr_path.stat().st_size
                except OSError:
                    output_size = 0
                if output_size > output_limit:
                    output_limited = True
                    _kill_process_tree(process)
                    break
                if time.perf_counter() >= deadline:
                    timed_out = True
                    _kill_process_tree(process)
                    break
                time.sleep(0.01)
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                _kill_process_tree(process)
                try:
                    process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    pass
            try:
                if stdout_path.stat().st_size + stderr_path.stat().st_size > output_limit:
                    output_limited = True
            except OSError:
                pass

        runtime_ms = max(0, round((time.perf_counter() - started) * 1000))
        return ProcessResult(
            return_code=process.returncode,
            timed_out=timed_out,
            output_limited=output_limited,
            stdout=_read_text(stdout_path, output_limit),
            stderr=_read_text(stderr_path, output_limit),
            runtime_ms=runtime_ms,
        )
    finally:
        for path in (input_path, stdout_path, stderr_path):
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass


def normalize_output(value: str) -> str:
    normalized_lines = value.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return "\n".join(line.rstrip() for line in normalized_lines).strip()


def _report(
    verdict: str,
    *,
    compile_output: str = "",
    error_message: str = "",
    runtime_ms: int | None = None,
    results: list[dict] | None = None,
) -> dict:
    return {
        "verdict": verdict,
        "score": 0,
        "compile_output": compile_output,
        "error_message": error_message,
        "runtime_ms": runtime_ms,
        "memory_kb": None,
        "results": results or [],
    }


class LocalCodeRunner:
    def __init__(self, runner_settings: Settings = settings):
        self.settings = runner_settings

    def run(
        self,
        *,
        submission_id: str,
        source_code: str,
        language: str,
        test_cases: list[dict],
        time_limit_ms: int,
        memory_limit_mb: int,
    ) -> dict:
        normalized_language = "cpp" if language == "cpp17" else language
        spec = next((item for item in LANGUAGE_SPECS if item.id == normalized_language), None)
        if spec is None:
            return _report("SYSTEM_ERROR", error_message=f"不支持的语言: {language}")
        if not test_cases:
            return _report("SYSTEM_ERROR", error_message="题目没有可判定的测试用例")
        if Path(submission_id).name != submission_id:
            return _report("SYSTEM_ERROR", error_message="提交编号非法")

        work_dir = self.settings.runtime_dir / submission_id
        source_path = work_dir / spec.source_name
        executable_name = "main.exe" if os.name == "nt" else "main"
        executable_path = work_dir / executable_name
        compile_output = ""
        compile_runtime = None
        runtime_command: list[str]
        try:
            work_dir.mkdir(parents=True, exist_ok=False)
            source_path.write_text(source_code, encoding="utf-8")

            if spec.id in ("pypy", "python"):
                runtime = _resolve_executable(getattr(self.settings, spec.id))
                if runtime is None:
                    return _report("SYSTEM_ERROR", error_message="未找到 PyPy 3 运行时")
                runtime_command = [runtime, str(source_path)]
            elif spec.id == "java":
                compiler = _resolve_executable(self.settings.javac)
                runtime = _resolve_executable(self.settings.java)
                if compiler is None or runtime is None:
                    return _report("SYSTEM_ERROR", error_message="未找到完整的 Java/Javac 工具链")
                compile_result = run_process(
                    [compiler, "-encoding", "UTF-8", "-d", str(work_dir), str(source_path)],
                    cwd=work_dir,
                    timeout_ms=self.settings.compile_timeout_ms,
                    output_limit=COMPILE_OUTPUT_LIMIT,
                )
                compile_runtime = compile_result.runtime_ms
                compile_output = "\n".join(
                    part for part in (compile_result.stdout, compile_result.stderr) if part
                ).strip()
                if compile_result.timed_out:
                    return _report(
                        "SYSTEM_ERROR",
                        compile_output=compile_output,
                        error_message="Java 编译进程超时",
                        runtime_ms=compile_runtime,
                    )
                if compile_result.return_code is None:
                    return _report(
                        "SYSTEM_ERROR",
                        compile_output=compile_output,
                        error_message=compile_result.stderr or "无法启动 javac",
                        runtime_ms=compile_runtime,
                    )
                if compile_result.return_code != 0:
                    return _report(
                        "COMPILE_ERROR",
                        compile_output=compile_output[-COMPILE_OUTPUT_LIMIT:],
                        error_message="Java 编译失败，请确保入口类名为 Main",
                        runtime_ms=compile_runtime,
                    )
                runtime_command = [
                    runtime,
                    f"-Xmx{max(16, int(memory_limit_mb))}m",
                    "-cp",
                    str(work_dir),
                    "Main",
                ]
            else:
                compiler_name = getattr(self.settings, spec.compiler_setting or "", "")
                compiler = _resolve_executable(compiler_name)
                if compiler is None:
                    return _report(
                        "SYSTEM_ERROR",
                        error_message=f"未找到 {spec.label} 编译器",
                    )
                standard = "-std=c17" if spec.id == "c" else "-std=c++17"
                compile_result = run_process(
                    [
                        compiler,
                        standard,
                        "-O2",
                        "-pipe",
                        str(source_path),
                        "-o",
                        str(executable_path),
                    ],
                    cwd=work_dir,
                    timeout_ms=self.settings.compile_timeout_ms,
                    output_limit=COMPILE_OUTPUT_LIMIT,
                )
                compile_runtime = compile_result.runtime_ms
                compile_output = "\n".join(
                    part for part in (compile_result.stdout, compile_result.stderr) if part
                ).strip()
                if compile_result.timed_out:
                    return _report(
                        "SYSTEM_ERROR",
                        compile_output=compile_output,
                        error_message="编译进程超时",
                        runtime_ms=compile_runtime,
                    )
                if compile_result.return_code is None:
                    return _report(
                        "SYSTEM_ERROR",
                        compile_output=compile_output,
                        error_message=compile_result.stderr or f"无法启动 {spec.label} 编译器",
                        runtime_ms=compile_runtime,
                    )
                if compile_result.return_code != 0:
                    return _report(
                        "COMPILE_ERROR",
                        compile_output=compile_output[-COMPILE_OUTPUT_LIMIT:],
                        error_message="编译失败，请检查代码和语言标准",
                        runtime_ms=compile_runtime,
                    )
                runtime_command = [str(executable_path)]

            results: list[dict] = []
            total_weight = sum(max(1, int(case.get("weight", 1))) for case in test_cases) or 1
            earned_weight = 0
            max_runtime = 0
            final_verdict = "ACCEPTED"
            final_error = ""
            for case in test_cases:
                process_result = run_process(
                    runtime_command,
                    cwd=work_dir,
                    input_data=case.get("input_data", ""),
                    timeout_ms=time_limit_ms,
                    output_limit=self.settings.max_output_bytes,
                )
                measured_runtime = (
                    min(process_result.runtime_ms, time_limit_ms)
                    if process_result.timed_out
                    else process_result.runtime_ms
                )
                max_runtime = max(max_runtime, measured_runtime)
                if process_result.timed_out:
                    verdict = "TIME_LIMIT_EXCEEDED"
                    error_message = f"运行超过 {time_limit_ms} ms"
                elif process_result.output_limited:
                    verdict = "OUTPUT_LIMIT_EXCEEDED"
                    error_message = "输出超过限制"
                elif process_result.return_code not in (0, None):
                    verdict = "RUNTIME_ERROR"
                    error_message = (process_result.stderr or "进程异常退出").strip()[-2_000:]
                elif process_result.return_code is None:
                    verdict = "SYSTEM_ERROR"
                    error_message = process_result.stderr or "无法启动运行进程"
                elif normalize_output(process_result.stdout) != normalize_output(
                    case.get("expected_output", "")
                ):
                    verdict = "WRONG_ANSWER"
                    error_message = "输出与标准答案不一致"
                else:
                    verdict = "ACCEPTED"
                    error_message = ""
                    earned_weight += max(1, int(case.get("weight", 1)))

                if verdict != "ACCEPTED" and final_verdict == "ACCEPTED":
                    final_verdict = verdict
                    final_error = error_message
                results.append(
                    {
                        "test_case_id": case["id"],
                        "verdict": verdict,
                        "score": 100 if verdict == "ACCEPTED" else 0,
                        "runtime_ms": measured_runtime,
                        "output": process_result.stdout[:RESULT_OUTPUT_LIMIT],
                        "error_message": error_message,
                    }
                )
            score = round(earned_weight / total_weight * 100)
            return {
                "verdict": final_verdict,
                "score": score,
                "compile_output": compile_output,
                "error_message": final_error,
                "runtime_ms": max_runtime,
                "memory_kb": None,
                "results": results,
            }
        except Exception as exc:  # The worker must persist a terminal result on infrastructure errors.
            return _report(
                "SYSTEM_ERROR",
                compile_output=compile_output,
                error_message=f"判题服务异常: {exc}",
                runtime_ms=compile_runtime,
            )
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)


# Keep the original public name for callers that explicitly request local execution.
CodeRunner = LocalCodeRunner


def _docker_environment(work_dir: Path) -> dict[str, str]:
    return _safe_environment(work_dir, extra_keys=_DOCKER_ENV_KEYS)


def _cleanup_docker_container(
    docker_cli: str, container_name: str, environment: dict[str, str]
) -> None:
    try:
        kwargs: dict[str, object] = {
            "stdin": subprocess.DEVNULL,
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
            "env": environment,
            "timeout": 8,
            "check": False,
        }
        if os.name == "nt":
            kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        subprocess.run([docker_cli, "rm", "-f", container_name], **kwargs)
    except (OSError, subprocess.SubprocessError):
        pass


class DockerCodeRunner:
    """Run the local judge worker inside an ephemeral Docker container."""

    def __init__(self, runner_settings: Settings = settings):
        self.settings = runner_settings

    def run(
        self,
        *,
        submission_id: str,
        source_code: str,
        language: str,
        test_cases: list[dict],
        time_limit_ms: int,
        memory_limit_mb: int,
    ) -> dict:
        normalized_language = "cpp" if language == "cpp17" else language
        if not any(spec.id == normalized_language for spec in LANGUAGE_SPECS):
            return _report("SYSTEM_ERROR", error_message=f"不支持的语言: {language}")
        if not test_cases:
            return _report("SYSTEM_ERROR", error_message="题目没有可判定的测试用例")
        if Path(submission_id).name != submission_id:
            return _report("SYSTEM_ERROR", error_message="提交编号非法")

        docker_cli = _resolve_executable(self.settings.docker_cli)
        if docker_cli is None:
            return _report(
                "SYSTEM_ERROR",
                error_message="判题需要 Docker，请安装 Docker Desktop 并确保 docker 在 PATH 中",
            )
        image = (self.settings.docker_image or "").strip()
        if not image:
            return _report("SYSTEM_ERROR", error_message="未配置 Docker 判题镜像")

        safe_id = "".join(
            character if character.isalnum() or character in "-_" else "-"
            for character in submission_id
        )
        container_name = f"sakura-judge-{safe_id[:48]}"
        container_memory_mb = max(64, int(memory_limit_mb))
        total_timeout_ms = (
            max(1, int(self.settings.compile_timeout_ms))
            + max(1, int(time_limit_ms)) * len(test_cases)
            + max(0, int(self.settings.docker_grace_ms))
        )
        report_limit = min(
            DOCKER_REPORT_OUTPUT_LIMIT,
            max(
                256 * 1024,
                COMPILE_OUTPUT_LIMIT
                + len(test_cases) * (RESULT_OUTPUT_LIMIT * 2 + 1_024),
            ),
        )
        command = [
            docker_cli,
            "run",
            "--rm",
            "--interactive",
            "--name",
            container_name,
            "--user",
            "10001:10001",
            "--workdir",
            "/app",
            "--network",
            "none",
            "--read-only",
            "--tmpfs",
            "/tmp:rw,noexec,nosuid,nodev,size=256m",
            "--tmpfs",
            "/sandbox:rw,nosuid,nodev,uid=10001,gid=10001,mode=700,size=256m",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges",
            "--pids-limit",
            "128",
            "--memory",
            f"{container_memory_mb}m",
            "--memory-swap",
            f"{container_memory_mb}m",
            "--cpus",
            "1",
            "--env",
            f"OJ_MAX_OUTPUT_BYTES={max(1, int(self.settings.max_output_bytes))}",
            "--env",
            f"OJ_COMPILE_TIMEOUT_MS={max(1, int(self.settings.compile_timeout_ms))}",
            "--env",
            "OJ_DATABASE_PATH=/sandbox/oj.sqlite3",
            "--env",
            "OJ_RUNTIME_DIR=/sandbox",
            "--pull",
            "never",
            image,
            "python",
            "-m",
            "app.services.docker_worker",
        ]
        job = json.dumps(
            {
                "submission_id": submission_id,
                "source_code": source_code,
                "language": normalized_language,
                "test_cases": test_cases,
                "time_limit_ms": int(time_limit_ms),
                "memory_limit_mb": int(memory_limit_mb),
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
        environment = _docker_environment(self.settings.runtime_dir)
        try:
            process_result = run_process(
                command,
                cwd=self.settings.runtime_dir,
                input_data=job,
                timeout_ms=total_timeout_ms,
                output_limit=report_limit,
                environment=environment,
            )
            if process_result.timed_out:
                return _report(
                    "SYSTEM_ERROR",
                    error_message="Docker 判题容器超时，可能是 Docker 服务未响应",
                    runtime_ms=process_result.runtime_ms,
                )
            if process_result.output_limited:
                return _report(
                    "SYSTEM_ERROR",
                    error_message="Docker 判题返回结果超过大小限制",
                    runtime_ms=process_result.runtime_ms,
                )
            if process_result.return_code is None:
                return _report(
                    "SYSTEM_ERROR",
                    error_message=process_result.stderr or "无法启动 Docker 判题容器",
                    runtime_ms=process_result.runtime_ms,
                )
            if process_result.return_code != 0:
                detail = (process_result.stderr or process_result.stdout).strip()[-2_000:]
                return _report(
                    "SYSTEM_ERROR",
                    error_message=f"Docker 判题容器启动失败{(': ' + detail) if detail else ''}",
                    runtime_ms=process_result.runtime_ms,
                )
            try:
                report = json.loads(process_result.stdout)
            except json.JSONDecodeError:
                detail = (process_result.stderr or process_result.stdout).strip()[-2_000:]
                return _report(
                    "SYSTEM_ERROR",
                    error_message=f"Docker 判题返回无效结果{(': ' + detail) if detail else ''}",
                    runtime_ms=process_result.runtime_ms,
                )
            if not isinstance(report, dict) or not isinstance(report.get("verdict"), str):
                return _report(
                    "SYSTEM_ERROR",
                    error_message="Docker 判题返回结果格式错误",
                    runtime_ms=process_result.runtime_ms,
                )
            return report
        except (TypeError, ValueError) as exc:
            return _report("SYSTEM_ERROR", error_message=f"Docker 判题参数无效: {exc}")
        finally:
            _cleanup_docker_container(docker_cli, container_name, environment)


def build_runner(runner_settings: Settings = settings):
    mode = (runner_settings.judge_mode or "docker").strip().lower()
    if mode == "docker":
        return DockerCodeRunner(runner_settings)
    if mode == "local":
        return LocalCodeRunner(runner_settings)
    if mode == 'newjudge':
        from .newjudge import NewjudgeRunner
        return NewjudgeRunner(runner_settings=runner_settings)
    raise ValueError(f"不支持的判题模式: {runner_settings.judge_mode}")
