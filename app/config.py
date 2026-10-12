from __future__ import annotations

import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _path_from_env(name: str, default: Path) -> Path:
    value = os.getenv(name)
    if not value:
        return default
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


@dataclass
class Settings:
    app_name: str = os.getenv("OJ_APP_NAME", "Sakura Online Judge")
    database_path: Path = _path_from_env("OJ_DATABASE_PATH", PROJECT_ROOT / "data" / "oj.sqlite3")
    runtime_dir: Path = _path_from_env("OJ_RUNTIME_DIR", PROJECT_ROOT / "runtime")
    c_compiler: str = (
        os.getenv("OJ_C_COMPILER") or shutil.which("gcc") or shutil.which("clang") or "gcc"
    )
    cpp_compiler: str = (
        os.getenv("OJ_CPP_COMPILER")
        or os.getenv("OJ_COMPILER")
        or shutil.which("g++")
        or shutil.which("clang++")
        or "g++"
    )
    pypy: str = os.getenv("OJ_PYPY") or shutil.which("pypy3") or shutil.which("pypy") or "pypy3"
    javac: str = os.getenv("OJ_JAVAC") or shutil.which("javac") or "javac"
    java: str = os.getenv("OJ_JAVA") or shutil.which("java") or "java"
    judge_mode: str = os.getenv("OJ_JUDGE_MODE", "newjudge").strip().lower()
    python: str = os.getenv("OJ_PYTHON", sys.executable)
    newjudge_runtime: Path = Path(os.getenv("SAKURA_JUDGE_RUNTIME", "/opt/sakura/runtime"))
    newjudge_work: Path = _path_from_env("SAKURA_JUDGE_WORK", Path("/var/lib/sakura/judge") if os.name != "nt" else PROJECT_ROOT / "runtime" / "judge")
    studio_root: Path | None = Path(os.environ["SAKURA_STUDIO_DATA"]) if os.getenv("SAKURA_STUDIO_DATA") else None

    @property
    def studio_directory(self) -> Path:
        return self.studio_root or self.database_path.parent / "studio"
    docker_cli: str = os.getenv("OJ_DOCKER_CLI", "docker")
    docker_image: str = os.getenv("OJ_DOCKER_IMAGE", "sakura-oj-judge:local")
    docker_grace_ms: int = int(os.getenv("OJ_DOCKER_GRACE_MS", "5000"))
    session_cookie: str = os.getenv("OJ_SESSION_COOKIE", "sakura_session")
    session_ttl_seconds: int = int(os.getenv("OJ_SESSION_TTL_SECONDS", str(7 * 24 * 60 * 60)))
    auth_required: bool = os.getenv("OJ_AUTH_REQUIRED", "false").strip().lower() not in {
        "0",
        "false",
        "no",
        "off",
    }
    admin_username: str = os.getenv("OJ_ADMIN_USERNAME", "admin")
    # Bootstrap credentials belong to deployment configuration, never to source.
    admin_password: str = os.getenv("OJ_ADMIN_PASSWORD", "")
    max_source_bytes: int = int(os.getenv("OJ_MAX_SOURCE_BYTES", "100000"))
    max_output_bytes: int = int(os.getenv("OJ_MAX_OUTPUT_BYTES", str(1024 * 1024)))
    compile_timeout_ms: int = int(os.getenv("OJ_COMPILE_TIMEOUT_MS", "10000"))
    worker_count: int = max(1, int(os.getenv("OJ_WORKER_COUNT", "1")))

    @property
    def compiler(self) -> str:
        """Backward-compatible alias for the original C++ compiler setting."""
        return self.cpp_compiler

    @compiler.setter
    def compiler(self, value: str) -> None:
        self.cpp_compiler = value

    def ensure_directories(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.runtime_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_directories()
