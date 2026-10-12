from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Iterator

from .config import settings


SCHEMA = """
CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    student_id TEXT NOT NULL DEFAULT '',
    team_group TEXT NOT NULL DEFAULT '算法组',
    status TEXT NOT NULL DEFAULT 'active',
    color TEXT NOT NULL DEFAULT '#2dd4bf',
    cf_handle TEXT NOT NULL DEFAULT '',
    atcoder_handle TEXT NOT NULL DEFAULT '',
    nowcoder_handle TEXT NOT NULL DEFAULT '',
    nowcoder_uid TEXT NOT NULL DEFAULT '',
    oj_username TEXT NOT NULL DEFAULT '',
    email TEXT NOT NULL DEFAULT '',
    note TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS platform_ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    platform TEXT NOT NULL,
    rating INTEGER NOT NULL DEFAULT 0,
    peak_rating INTEGER NOT NULL DEFAULT 0,
    rank_title TEXT NOT NULL DEFAULT '',
    contest_count INTEGER NOT NULL DEFAULT 0,
    rating_change INTEGER NOT NULL DEFAULT 0,
    fetched_at TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'manual',
    UNIQUE(member_id, platform)
);

CREATE TABLE IF NOT EXISTS contests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,
    external_id TEXT NOT NULL,
    name TEXT NOT NULL,
    contest_time TEXT NOT NULL,
    participant_count INTEGER NOT NULL DEFAULT 0,
    source TEXT NOT NULL DEFAULT 'manual',
    created_at TEXT NOT NULL,
    UNIQUE(platform, external_id)
);

CREATE TABLE IF NOT EXISTS contest_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contest_id INTEGER NOT NULL REFERENCES contests(id) ON DELETE CASCADE,
    member_id INTEGER NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    rank INTEGER NOT NULL DEFAULT 0,
    participants INTEGER NOT NULL DEFAULT 0,
    score REAL,
    max_score REAL,
    solved INTEGER,
    penalty INTEGER,
    old_rating INTEGER,
    new_rating INTEGER,
    performance_rating INTEGER NOT NULL DEFAULT 0,
    fitted_rating INTEGER NOT NULL DEFAULT 0,
    source TEXT NOT NULL DEFAULT 'manual',
    UNIQUE(contest_id, member_id)
);

CREATE TABLE IF NOT EXISTS submissions (
    id TEXT PRIMARY KEY,
    member_id INTEGER REFERENCES members(id) ON DELETE SET NULL,
    platform TEXT NOT NULL DEFAULT 'oj',
    external_id TEXT NOT NULL DEFAULT '',
    problem_id TEXT NOT NULL DEFAULT '',
    problem_name TEXT NOT NULL DEFAULT '',
    verdict TEXT NOT NULL DEFAULT 'PENDING',
    language TEXT NOT NULL DEFAULT '',
    submitted_at TEXT NOT NULL,
    runtime_ms INTEGER,
    memory_kb INTEGER,
    code_length INTEGER,
    source TEXT NOT NULL DEFAULT 'manual',
    url TEXT NOT NULL DEFAULT '',
    tags TEXT NOT NULL DEFAULT '',
    UNIQUE(platform, external_id)
);

CREATE TABLE IF NOT EXISTS sync_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scope TEXT NOT NULL,
    status TEXT NOT NULL,
    message TEXT NOT NULL DEFAULT '',
    started_at TEXT NOT NULL,
    finished_at TEXT
);

CREATE TABLE IF NOT EXISTS submission_sync_exclusions (
    platform TEXT NOT NULL,
    external_id TEXT NOT NULL,
    PRIMARY KEY(platform, external_id)
);

CREATE INDEX IF NOT EXISTS idx_ratings_member ON platform_ratings(member_id);
CREATE INDEX IF NOT EXISTS idx_results_member_time ON contest_results(member_id, contest_id);
CREATE INDEX IF NOT EXISTS idx_submissions_member_time ON submissions(member_id, submitted_at DESC);
CREATE INDEX IF NOT EXISTS idx_submissions_verdict ON submissions(verdict);
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect(path=None) -> sqlite3.Connection:
    target = path or settings.database_path
    if hasattr(target, "parent"):
        target.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(target, timeout=30, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    return connection


@contextmanager
def connection(path=None) -> Iterator[sqlite3.Connection]:
    conn = _connect(path)
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
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(members)").fetchall()}
        # These additions keep a database created by an early prototype usable.
        migrations = {
            "student_id": "TEXT NOT NULL DEFAULT ''",
            "team_group": "TEXT NOT NULL DEFAULT '算法组'",
            "status": "TEXT NOT NULL DEFAULT 'active'",
            "color": "TEXT NOT NULL DEFAULT '#2dd4bf'",
            "cf_handle": "TEXT NOT NULL DEFAULT ''",
            "atcoder_handle": "TEXT NOT NULL DEFAULT ''",
            "nowcoder_handle": "TEXT NOT NULL DEFAULT ''",
            "nowcoder_uid": "TEXT NOT NULL DEFAULT ''",
            "oj_username": "TEXT NOT NULL DEFAULT ''",
            "email": "TEXT NOT NULL DEFAULT ''",
            "note": "TEXT NOT NULL DEFAULT ''",
        }
        for name, definition in migrations.items():
            if name not in columns:
                conn.execute(f"ALTER TABLE members ADD COLUMN {name} {definition}")
        if "nowcoder_uid" not in columns:
            # Only migrate once: clearing a UID later must not rebind it at startup.
            conn.execute("""
                UPDATE members SET nowcoder_uid = ltrim(trim(nowcoder_handle), '0')
                WHERE trim(nowcoder_handle) <> ''
                  AND trim(nowcoder_handle) NOT GLOB '*[^0-9]*'
                  AND length(ltrim(trim(nowcoder_handle), '0')) BETWEEN 1 AND 19
            """)
