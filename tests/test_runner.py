from __future__ import annotations

import json
import shutil
from dataclasses import replace

import pytest

from app.config import settings
from app.services import runner as runner_module
from app.services.runner import (
    CodeRunner,
    DockerCodeRunner,
    ProcessResult,
    build_runner,
    language_catalog,
    normalize_output,
)


def test_normalize_output_ignores_line_endings_and_trailing_spaces():
    assert normalize_output("1  2  \r\n\r\n") == "1  2"
    assert normalize_output("a\nb\n") == "a\nb"


@pytest.mark.skipif(
    not (shutil.which("g++") or shutil.which("clang++")),
    reason="no C++ compiler available",
)
def test_runner_executes_cpp17(tmp_path):
    original_runtime = settings.runtime_dir
    original_compiler = settings.cpp_compiler
    settings.runtime_dir = tmp_path / "runtime"
    settings.cpp_compiler = shutil.which("g++") or shutil.which("clang++") or original_compiler
    settings.ensure_directories()
    try:
        report = CodeRunner(settings).run(
            submission_id="unit-run",
            source_code=(
                "#include <iostream>\n"
                "int main(){ long long a,b; std::cin>>a>>b; std::cout<<a+b<<'\\n'; }\n"
            ),
            language="cpp",
            test_cases=[
                {
                    "id": 1,
                    "input_data": "2 5\n",
                    "expected_output": "7\n",
                    "weight": 1,
                }
            ],
            time_limit_ms=1_000,
            memory_limit_mb=256,
        )
        assert report["verdict"] == "ACCEPTED"
        assert report["results"][0]["verdict"] == "ACCEPTED"
    finally:
        settings.runtime_dir = original_runtime
        settings.cpp_compiler = original_compiler


@pytest.mark.skipif(
    not (shutil.which("g++") or shutil.which("clang++")),
    reason="no C++ compiler available",
)
def test_runner_stops_infinite_loop(tmp_path):
    original_runtime = settings.runtime_dir
    original_compiler = settings.cpp_compiler
    settings.runtime_dir = tmp_path / "runtime"
    settings.cpp_compiler = shutil.which("g++") or shutil.which("clang++") or original_compiler
    settings.ensure_directories()
    try:
        report = CodeRunner(settings).run(
            submission_id="unit-tle",
            source_code="int main(){ for (;;) {} }\n",
            language="cpp",
            test_cases=[{"id": 1, "input_data": "", "expected_output": "", "weight": 1}],
            time_limit_ms=150,
            memory_limit_mb=256,
        )
        assert report["verdict"] == "TIME_LIMIT_EXCEEDED"
        assert report["results"][0]["runtime_ms"] <= 150
    finally:
        settings.runtime_dir = original_runtime
        settings.cpp_compiler = original_compiler


@pytest.mark.skipif(
    not (shutil.which("gcc") or shutil.which("clang")),
    reason="no C compiler available",
)
def test_runner_executes_c17(tmp_path):
    original_runtime = settings.runtime_dir
    original_compiler = settings.c_compiler
    settings.runtime_dir = tmp_path / "runtime"
    settings.c_compiler = shutil.which("gcc") or shutil.which("clang") or original_compiler
    settings.ensure_directories()
    try:
        report = CodeRunner(settings).run(
            submission_id="unit-c",
            source_code="#include <stdio.h>\nint main(){int a,b;scanf(\"%d%d\",&a,&b);printf(\"%d\\n\",a+b);}\n",
            language="c",
            test_cases=[{"id": 1, "input_data": "2 5\n", "expected_output": "7\n", "weight": 1}],
            time_limit_ms=1_000,
            memory_limit_mb=256,
        )
        assert report["verdict"] == "ACCEPTED"
    finally:
        settings.runtime_dir = original_runtime
        settings.c_compiler = original_compiler


@pytest.mark.skipif(
    not (shutil.which("javac") and shutil.which("java")),
    reason="no Java toolchain available",
)
def test_runner_executes_java(tmp_path):
    original_runtime = settings.runtime_dir
    original_javac = settings.javac
    original_java = settings.java
    settings.runtime_dir = tmp_path / "runtime"
    settings.javac = shutil.which("javac") or original_javac
    settings.java = shutil.which("java") or original_java
    settings.ensure_directories()
    try:
        report = CodeRunner(settings).run(
            submission_id="unit-java",
            source_code=(
                "import java.util.*;\n"
                "public class Main { public static void main(String[] args) { "
                "Scanner s = new Scanner(System.in); System.out.println(s.nextInt() + s.nextInt()); } }\n"
            ),
            language="java",
            test_cases=[{"id": 1, "input_data": "2 5\n", "expected_output": "7\n", "weight": 1}],
            time_limit_ms=2_000,
            memory_limit_mb=256,
        )
        assert report["verdict"] == "ACCEPTED"
    finally:
        settings.runtime_dir = original_runtime
        settings.javac = original_javac
        settings.java = original_java


@pytest.mark.skipif(
    not (shutil.which("pypy3") or shutil.which("pypy")),
    reason="no PyPy runtime available",
)
def test_runner_executes_pypy(tmp_path):
    original_runtime = settings.runtime_dir
    original_pypy = settings.pypy
    settings.runtime_dir = tmp_path / "runtime"
    settings.pypy = shutil.which("pypy3") or shutil.which("pypy") or original_pypy
    settings.ensure_directories()
    try:
        report = CodeRunner(settings).run(
            submission_id="unit-pypy",
            source_code="a, b = map(int, input().split())\nprint(a + b)\n",
            language="pypy",
            test_cases=[{"id": 1, "input_data": "2 5\n", "expected_output": "7\n", "weight": 1}],
            time_limit_ms=1_000,
            memory_limit_mb=256,
        )
        assert report["verdict"] == "ACCEPTED"
    finally:
        settings.runtime_dir = original_runtime
        settings.pypy = original_pypy


def test_language_catalog_contains_all_requested_languages():
    ids = {item["id"] for item in language_catalog(settings)}
    assert {"c", "cpp", "pypy", "java"} <= ids


def test_build_runner_uses_docker_mode_by_default():
    docker_settings = replace(settings, judge_mode="docker")
    assert isinstance(build_runner(docker_settings), DockerCodeRunner)


def test_docker_runner_reports_missing_docker(tmp_path):
    docker_settings = replace(
        settings,
        runtime_dir=tmp_path / "runtime",
        docker_cli="sakura-command-that-does-not-exist",
        judge_mode="docker",
    )
    report = DockerCodeRunner(docker_settings).run(
        submission_id="docker-missing",
        source_code="int main(){}",
        language="cpp",
        test_cases=[{"id": 1, "input_data": "", "expected_output": "", "weight": 1}],
        time_limit_ms=1000,
        memory_limit_mb=128,
    )
    assert report["verdict"] == "SYSTEM_ERROR"
    assert "Docker" in report["error_message"]


def test_docker_runner_sends_isolated_job_to_worker(monkeypatch, tmp_path):
    captured = {}
    docker_settings = replace(
        settings,
        runtime_dir=tmp_path / "runtime",
        docker_cli="docker",
        docker_image="judge:test",
        judge_mode="docker",
    )
    expected_report = {
        "verdict": "ACCEPTED",
        "score": 100,
        "compile_output": "",
        "error_message": "",
        "runtime_ms": 4,
        "memory_kb": None,
        "results": [],
    }

    monkeypatch.setattr(runner_module, "_resolve_executable", lambda command: command)

    def fake_run_process(command, **kwargs):
        captured["command"] = command
        captured["job"] = json.loads(kwargs["input_data"])
        return ProcessResult(
            return_code=0,
            timed_out=False,
            output_limited=False,
            stdout=json.dumps(expected_report),
            stderr="",
            runtime_ms=4,
        )

    monkeypatch.setattr(runner_module, "run_process", fake_run_process)
    monkeypatch.setattr(runner_module, "_cleanup_docker_container", lambda *args: None)
    report = DockerCodeRunner(docker_settings).run(
        submission_id="docker-job",
        source_code="int main(){}",
        language="cpp17",
        test_cases=[{"id": 7, "input_data": "1", "expected_output": "1", "weight": 2}],
        time_limit_ms=1000,
        memory_limit_mb=128,
    )

    assert report == expected_report
    assert captured["job"]["language"] == "cpp"
    assert captured["job"]["test_cases"][0]["id"] == 7
    assert "--network" in captured["command"]
    assert "none" in captured["command"]
    assert "/sandbox:rw,nosuid,nodev,uid=10001,gid=10001,mode=700,size=256m" in captured["command"]
    assert captured["command"][captured["command"].index("--pull") + 1] == "never"
    assert "judge:test" in captured["command"]
    assert captured["command"][-2:] == ["-m", "app.services.docker_worker"]
