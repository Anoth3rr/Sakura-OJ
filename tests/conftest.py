from __future__ import annotations

import shutil

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


@pytest.fixture(scope="module")
def client(tmp_path_factory: pytest.TempPathFactory):
    root = tmp_path_factory.mktemp("sakura-oj")
    original_database = settings.database_path
    original_runtime = settings.runtime_dir
    original_c_compiler = settings.c_compiler
    original_cpp_compiler = settings.cpp_compiler
    original_pypy = settings.pypy
    original_javac = settings.javac
    original_java = settings.java
    original_judge_mode = settings.judge_mode
    original_docker_cli = settings.docker_cli
    original_docker_image = settings.docker_image
    original_auth_required = settings.auth_required
    original_admin_password = settings.admin_password
    settings.database_path = root / "test.sqlite3"
    settings.runtime_dir = root / "runtime"
    settings.c_compiler = shutil.which("gcc") or shutil.which("clang") or original_c_compiler
    settings.cpp_compiler = shutil.which("g++") or shutil.which("clang++") or original_cpp_compiler
    settings.judge_mode = "local"
    settings.auth_required = False
    settings.admin_password = "test-only-bootstrap-password"
    settings.ensure_directories()
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        settings.database_path = original_database
        settings.runtime_dir = original_runtime
        settings.c_compiler = original_c_compiler
        settings.cpp_compiler = original_cpp_compiler
        settings.pypy = original_pypy
        settings.javac = original_javac
        settings.java = original_java
        settings.judge_mode = original_judge_mode
        settings.docker_cli = original_docker_cli
        settings.docker_image = original_docker_image
        settings.auth_required = original_auth_required
        settings.admin_password = original_admin_password
