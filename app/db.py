from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Iterator

from .config import settings


SCHEMA = """
CREATE TABLE IF NOT EXISTS problems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    input_format TEXT NOT NULL,
    output_format TEXT NOT NULL,
    statement_markdown TEXT NOT NULL DEFAULT '',
    difficulty TEXT NOT NULL DEFAULT '入门',
    time_limit_ms INTEGER NOT NULL DEFAULT 1000,
    memory_limit_mb INTEGER NOT NULL DEFAULT 256,
    is_public INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS test_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id INTEGER NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    input_data TEXT NOT NULL,
    expected_output TEXT NOT NULL,
    is_sample INTEGER NOT NULL DEFAULT 0,
    weight INTEGER NOT NULL DEFAULT 1,
    order_index INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS submissions (
    id TEXT PRIMARY KEY,
    problem_id INTEGER NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
    language TEXT NOT NULL,
    source_code TEXT NOT NULL,
    status TEXT NOT NULL,
    verdict TEXT NOT NULL,
    score INTEGER NOT NULL DEFAULT 0,
    compile_output TEXT NOT NULL DEFAULT '',
    error_message TEXT NOT NULL DEFAULT '',
    runtime_ms INTEGER,
    memory_kb INTEGER,
    created_at TEXT NOT NULL,
    started_at TEXT,
    finished_at TEXT
);

CREATE TABLE IF NOT EXISTS submission_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    submission_id TEXT NOT NULL REFERENCES submissions(id) ON DELETE CASCADE,
    test_case_id INTEGER NOT NULL REFERENCES test_cases(id) ON DELETE CASCADE,
    verdict TEXT NOT NULL,
    score INTEGER NOT NULL DEFAULT 0,
    runtime_ms INTEGER,
    output TEXT NOT NULL DEFAULT '',
    error_message TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
    display_name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'student'
        CHECK (role IN ('admin', 'problem_admin', 'teacher', 'student')),
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token_hash TEXT NOT NULL UNIQUE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    expires_at TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_problems_public ON problems(is_public, id);
CREATE INDEX IF NOT EXISTS idx_test_cases_problem ON test_cases(problem_id, order_index);
CREATE INDEX IF NOT EXISTS idx_submissions_problem ON submissions(problem_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_submission_results_submission ON submission_results(submission_id);
CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token_hash);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect() -> sqlite3.Connection:
    settings.ensure_directories()
    connection = sqlite3.connect(
        settings.database_path,
        timeout=30,
        check_same_thread=False,
    )
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    return connection


@contextmanager
def connection() -> Iterator[sqlite3.Connection]:
    conn = _connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with connection() as conn:
        conn.executescript(SCHEMA)
        additions = {
            'problems': {'judge_mode': "TEXT NOT NULL DEFAULT 'normal'", 'judge_config': "TEXT NOT NULL DEFAULT '{}'"},
            'test_cases': {'active': 'INTEGER NOT NULL DEFAULT 1'},
            'submissions': {'user_id': 'INTEGER REFERENCES users(id)', 'judge_snapshot': "TEXT NOT NULL DEFAULT '{}'"},
            'submission_results': {'memory_kb': 'INTEGER', 'message_bytes': 'INTEGER'},
            'users': {'deleted_at': 'TEXT'},
        }
        for table, fields in additions.items():
            existing = {r['name'] for r in conn.execute(f'PRAGMA table_info({table})')}
            for name, declaration in fields.items():
                if name not in existing:
                    conn.execute(f'ALTER TABLE {table} ADD COLUMN {name} {declaration}')
        conn.execute('''CREATE TABLE IF NOT EXISTS studio_publications (
            studio_id TEXT PRIMARY KEY, problem_id INTEGER NOT NULL UNIQUE REFERENCES problems(id),
            revision INTEGER NOT NULL, fingerprint TEXT NOT NULL, published_at TEXT NOT NULL)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS problem_catalog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            studio_id TEXT UNIQUE,
            problem_id INTEGER UNIQUE REFERENCES problems(id),
            created_at TEXT NOT NULL,
            CHECK (studio_id IS NOT NULL OR problem_id IS NOT NULL))''')
        # Existing OJ problems and their Studio drafts must share the same public ID.
        conn.execute('''INSERT INTO problem_catalog (studio_id, problem_id, created_at)
            SELECT s.studio_id, p.id, p.created_at FROM problems p
            LEFT JOIN studio_publications s ON s.problem_id=p.id
            WHERE NOT EXISTS (SELECT 1 FROM problem_catalog c WHERE c.problem_id=p.id)
            ORDER BY p.id''')
        # Keep databases created by the first MVP version readable without a
        # destructive migration.
        columns = {
            row["name"] for row in conn.execute("PRAGMA table_info(problems)").fetchall()
        }
        if "statement_markdown" not in columns:
            conn.execute(
                "ALTER TABLE problems ADD COLUMN statement_markdown TEXT NOT NULL DEFAULT ''"
            )
        # Older versions stored the range in a separate column. Preserve it by
        # appending it to input_format, then clear the legacy value so this
        # migration is idempotent.
        if "constraints" in columns:
            legacy_rows = conn.execute(
                "SELECT id, input_format, constraints FROM problems "
                "WHERE TRIM(COALESCE(constraints, '')) <> ''"
            ).fetchall()
            for row in legacy_rows:
                input_format = (row["input_format"] or "").rstrip()
                constraints = (row["constraints"] or "").strip()
                merged = f"{input_format}\n\n数据范围：{constraints}" if input_format else constraints
                conn.execute(
                    "UPDATE problems SET input_format = ?, constraints = '' WHERE id = ?",
                    (merged, row["id"]),
                )
