from __future__ import annotations

import sqlite3
import json
from typing import Any

from .auth import ROLE_LABELS, AuthUser, hash_password, hash_session_token, new_session_token
from .config import settings
from .db import connection, utc_now
from .markdown import render_markdown
from .catalog import problem_code


def _problem_summary(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "problem_code": problem_code(row["catalog_id"]),
        "slug": row["slug"],
        "title": row["title"],
        "difficulty": row["difficulty"],
        "time_limit_ms": row["time_limit_ms"],
        "memory_limit_mb": row["memory_limit_mb"],
        "submission_count": row["submission_count"] if "submission_count" in row.keys() else 0,
        "accepted_count": row["accepted_count"] if "accepted_count" in row.keys() else 0,
        "created_at": row["created_at"],
        "judge_mode": row["judge_mode"],
    }


def create_problem(data: dict[str, Any]) -> dict[str, Any]:
    now = utc_now()
    with connection() as conn:
        values = (
            data["slug"],
            data["title"],
            data.get("description") or data.get("statement_markdown") or "",
            data.get("statement_markdown") or data.get("description") or "",
            data["input_format"],
            data["output_format"],
            data.get("difficulty", "入门"),
            data.get("time_limit_ms", 1000),
            data.get("memory_limit_mb", 256),
            now,
            now,
        )
        columns = {
            row["name"] for row in conn.execute("PRAGMA table_info(problems)").fetchall()
        }
        if "constraints" in columns:
            # Very old schemas may keep a NOT NULL legacy column without a default.
            cursor = conn.execute(
                """
                INSERT INTO problems
                    (slug, title, description, statement_markdown, input_format, output_format,
                     constraints, difficulty, time_limit_ms, memory_limit_mb, is_public,
                     created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, '', ?, ?, ?, 1, ?, ?)
                """,
                values,
            )
        else:
            cursor = conn.execute(
                """
                INSERT INTO problems
                    (slug, title, description, statement_markdown, input_format, output_format,
                     difficulty, time_limit_ms, memory_limit_mb, is_public, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
                """,
                values,
            )
        problem_id = cursor.lastrowid
        conn.execute("INSERT INTO problem_catalog (problem_id, created_at) VALUES (?,?)", (problem_id, now))
        for index, test_case in enumerate(data["test_cases"]):
            conn.execute(
                """
                INSERT INTO test_cases
                    (problem_id, name, input_data, expected_output, is_sample, weight, order_index)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    problem_id,
                    test_case["name"],
                    test_case["input_data"],
                    test_case["expected_output"],
                    int(test_case.get("is_sample", False)),
                    test_case.get("weight", 1),
                    index,
                ),
            )
    return get_problem_by_id(int(problem_id), include_hidden=True)  # type: ignore[arg-type]


def list_problems(
    *,
    search: str = "",
    difficulty: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[dict[str, Any]], int]:
    page = max(1, page)
    page_size = min(100, max(1, page_size))
    clauses = ["p.is_public = 1"]
    params: list[Any] = []
    if search:
        clauses.append("(p.title LIKE ? OR p.slug LIKE ? OR printf('%04d', pc.id) LIKE ? OR printf('P%06d', pc.id) LIKE ?)")
        needle = f"%{search}%"
        params.extend([needle, needle, needle, needle])
    if difficulty:
        clauses.append("p.difficulty = ?")
        params.append(difficulty)
    where = " AND ".join(clauses)
    with connection() as conn:
        total = conn.execute(f"SELECT COUNT(*) FROM problems p JOIN problem_catalog pc ON pc.problem_id=p.id WHERE {where}", params).fetchone()[0]
        rows = conn.execute(
            f"""
            SELECT p.*, pc.id AS catalog_id,
                   COUNT(s.id) AS submission_count,
                   COALESCE(SUM(CASE WHEN s.verdict = 'ACCEPTED' THEN 1 ELSE 0 END), 0)
                       AS accepted_count
            FROM problems p
            JOIN problem_catalog pc ON pc.problem_id=p.id
            LEFT JOIN submissions s ON s.problem_id = p.id
            WHERE {where}
            GROUP BY p.id
            ORDER BY p.id DESC
            LIMIT ? OFFSET ?
            """,
            [*params, page_size, (page - 1) * page_size],
        ).fetchall()
    return [_problem_summary(row) for row in rows], int(total)


def _get_problem_row(conn: sqlite3.Connection, *, problem_id: int | None = None, slug: str | None = None):
    query = "SELECT p.*, pc.id AS catalog_id FROM problems p JOIN problem_catalog pc ON pc.problem_id=p.id"
    if problem_id is not None:
        return conn.execute(query + " WHERE p.id = ?", (problem_id,)).fetchone()
    return conn.execute(query + " WHERE p.slug = ?", (slug,)).fetchone()


def get_problem_by_id(problem_id: int, *, include_hidden: bool = False) -> dict[str, Any] | None:
    with connection() as conn:
        row = _get_problem_row(conn, problem_id=problem_id)
        if row is None:
            return None
        test_rows = conn.execute(
            """
            SELECT id, name, input_data, expected_output, is_sample, weight
            FROM test_cases WHERE problem_id = ? AND active = 1 ORDER BY order_index, id
            """,
            (problem_id,),
        ).fetchall()
        submission_stats = conn.execute(
            """
            SELECT COUNT(*) AS submission_count,
                   COALESCE(SUM(CASE WHEN verdict = 'ACCEPTED' THEN 1 ELSE 0 END), 0)
                       AS accepted_count
            FROM submissions WHERE problem_id = ?
            """,
            (problem_id,),
        ).fetchone()
    problem_data = dict(row)
    problem_data["problem_code"] = problem_code(problem_data.pop("catalog_id"))
    legacy_constraints = problem_data.pop("constraints", "")
    input_format = problem_data.get("input_format", "")
    if legacy_constraints:
        input_format = f"{input_format.rstrip()}\n\n数据范围：{legacy_constraints.strip()}" if input_format else legacy_constraints.strip()
    result = {
        **problem_data,
        "input_format": input_format,
        "input_format_html": render_markdown(input_format),
        "statement_markdown": row["statement_markdown"] or row["description"],
        "statement_html": render_markdown(row["statement_markdown"] or row["description"]),
        "output_format_html": render_markdown(problem_data.get("output_format", "")),
        "submission_count": int(submission_stats["submission_count"]),
        "accepted_count": int(submission_stats["accepted_count"]),
        "test_cases": [
            {
                "id": test_row["id"],
                "name": test_row["name"],
                "input_data": test_row["input_data"],
                "expected_output": test_row["expected_output"],
                "is_sample": bool(test_row["is_sample"]),
                "weight": test_row["weight"],
            }
            for test_row in test_rows
            if include_hidden or test_row["is_sample"]
        ],
    }
    if not include_hidden:
        result.pop('judge_config', None)
    return result


def replace_test_cases(problem_id: int, test_cases: list[dict[str, Any]]) -> dict[str, Any] | None:
    now = utc_now()
    with connection() as conn:
        if conn.execute("SELECT 1 FROM problems WHERE id = ?", (problem_id,)).fetchone() is None:
            return None
        conn.execute("UPDATE test_cases SET active = 0 WHERE problem_id = ?", (problem_id,))
        for index, test_case in enumerate(test_cases):
            conn.execute(
                """
                INSERT INTO test_cases
                    (problem_id, name, input_data, expected_output, is_sample, weight, order_index)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    problem_id,
                    test_case["name"],
                    test_case["input_data"],
                    test_case["expected_output"],
                    int(test_case.get("is_sample", False)),
                    max(1, int(test_case.get("weight", 1))),
                    index,
                ),
            )
        conn.execute("UPDATE problems SET updated_at = ? WHERE id = ?", (now, problem_id))
    return get_problem_by_id(problem_id, include_hidden=True)


def get_problem_by_slug(slug: str, *, include_hidden: bool = False) -> dict[str, Any] | None:
    with connection() as conn:
        row = _get_problem_row(conn, slug=slug)
        if row is None:
            return None
        problem_id = int(row["id"])
    return get_problem_by_id(problem_id, include_hidden=include_hidden)


def get_test_cases(problem_id: int) -> list[dict[str, Any]]:
    with connection() as conn:
        rows = conn.execute(
            """
            SELECT id, name, input_data, expected_output, is_sample, weight
            FROM test_cases WHERE problem_id = ? AND active = 1 ORDER BY order_index, id
            """,
            (problem_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def create_submission(
    *,
    submission_id: str,
    problem_id: int,
    language: str,
    source_code: str,
    user_id: int | None = None,
) -> dict[str, Any]:
    now = utc_now()
    with connection() as conn:
        conn.execute('BEGIN IMMEDIATE')
        row = conn.execute('SELECT * FROM problems WHERE id = ? AND is_public=1', (problem_id,)).fetchone()
        if row is None:
            raise ValueError('题目不存在或已移出题库')
        problem = dict(row)
        snapshot = {k: problem[k] for k in ('time_limit_ms', 'memory_limit_mb', 'judge_mode', 'judge_config')}
        snapshot['case_ids'] = [r[0] for r in conn.execute('SELECT id FROM test_cases WHERE problem_id=? AND active=1 ORDER BY order_index,id', (problem_id,))]
        conn.execute(
            """
            INSERT INTO submissions
                (id, problem_id, language, source_code, status, verdict, score, created_at, user_id, judge_snapshot)
            VALUES (?, ?, ?, ?, 'QUEUED', 'PENDING', 0, ?, ?, ?)
            """,
            (submission_id, problem_id, language, source_code, now, user_id, json.dumps(snapshot)),
        )
    return get_submission(submission_id)  # type: ignore[return-value]


def update_submission(submission_id: str, **fields: Any) -> None:
    allowed = {
        "status",
        "verdict",
        "score",
        "compile_output",
        "error_message",
        "runtime_ms",
        "memory_kb",
        "started_at",
        "finished_at",
    }
    updates = [(key, value) for key, value in fields.items() if key in allowed]
    if not updates:
        return
    assignments = ", ".join(f"{key} = ?" for key, _ in updates)
    with connection() as conn:
        conn.execute(
            f"UPDATE submissions SET {assignments} WHERE id = ?",
            [value for _, value in updates] + [submission_id],
        )


def replace_submission_results(submission_id: str, results: list[dict[str, Any]]) -> None:
    now = utc_now()
    with connection() as conn:
        conn.execute("DELETE FROM submission_results WHERE submission_id = ?", (submission_id,))
        for result in results:
            conn.execute(
                """
                INSERT INTO submission_results
                    (submission_id, test_case_id, verdict, score, runtime_ms, output,
                     error_message, created_at, memory_kb, message_bytes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    submission_id,
                    result["test_case_id"],
                    result["verdict"],
                    result.get("score", 0),
                    result.get("runtime_ms"),
                    result.get("output", ""),
                    result.get("error_message", ""),
                    now,
                    result.get('memory_kb'),
                    result.get('message_bytes'),
                ),
            )


def get_submission(submission_id: str) -> dict[str, Any] | None:
    with connection() as conn:
        row = conn.execute(
            """
            SELECT s.*, p.slug AS problem_slug, p.title AS problem_title
            FROM submissions s JOIN problems p ON p.id = s.problem_id
            WHERE s.id = ?
            """,
            (submission_id,),
        ).fetchone()
        if row is None:
            return None
        result_rows = conn.execute(
            """
            SELECT r.test_case_id, t.name AS test_case_name, r.verdict, r.score,
                   r.runtime_ms, r.output, r.error_message, r.memory_kb, r.message_bytes
            FROM submission_results r JOIN test_cases t ON t.id = r.test_case_id
            WHERE r.submission_id = ? ORDER BY t.order_index, t.id
            """,
            (submission_id,),
        ).fetchall()
    return {
        **dict(row),
        "results": [dict(result_row) for result_row in result_rows],
    }


def list_submissions(
    *, problem_id: int | None = None, limit: int = 30, offset: int = 0, user_id: int | None = None
) -> tuple[list[dict[str, Any]], int]:
    limit = min(100, max(1, limit))
    offset = max(0, offset)
    clauses = []
    params: list[Any] = []
    if problem_id is not None:
        clauses.append("s.problem_id = ?")
        params.append(problem_id)
    if user_id is not None:
        clauses.append('s.user_id = ?')
        params.append(user_id)
    where = 'WHERE ' + ' AND '.join(clauses) if clauses else ''
    with connection() as conn:
        total = conn.execute(f"SELECT COUNT(*) FROM submissions s {where}", params).fetchone()[0]
        rows = conn.execute(
            f"""
            SELECT s.id, s.problem_id, p.slug AS problem_slug, s.language, s.status,
                   s.verdict, s.score, s.created_at
            FROM submissions s JOIN problems p ON p.id = s.problem_id
            {where}
            ORDER BY s.created_at DESC
            LIMIT ? OFFSET ?
            """,
            [*params, limit, offset],
        ).fetchall()
    return [dict(row) for row in rows], int(total)


def stats() -> dict[str, Any]:
    with connection() as conn:
        problem_count = conn.execute("SELECT COUNT(*) FROM problems WHERE is_public = 1").fetchone()[0]
        submission_count = conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0]
        accepted_count = conn.execute(
            "SELECT COUNT(*) FROM submissions WHERE verdict = 'ACCEPTED'"
        ).fetchone()[0]
    rate = round((accepted_count / submission_count * 100) if submission_count else 0.0, 1)
    return {
        "problem_count": int(problem_count),
        "submission_count": int(submission_count),
        "accepted_count": int(accepted_count),
        "acceptance_rate": rate,
    }


def _auth_user(row: sqlite3.Row | None) -> AuthUser | None:
    if row is None:
        return None
    return AuthUser(
        id=int(row["id"]),
        username=str(row["username"]),
        display_name=str(row["display_name"]),
        role=str(row["role"]),
        is_active=bool(row["is_active"]),
    )


def ensure_default_admin() -> None:
    """Create the configured bootstrap administrator without changing existing accounts."""

    username = (settings.admin_username or "admin").strip()
    password = settings.admin_password
    if not username:
        return
    with connection() as conn:
        exists = conn.execute(
            "SELECT 1 FROM users WHERE username = ? COLLATE NOCASE", (username,)
        ).fetchone()
        if exists is None:
            if not password:
                if settings.auth_required:
                    raise RuntimeError("Set OJ_ADMIN_PASSWORD before creating the initial administrator.")
                return
            now = utc_now()
            conn.execute(
                "INSERT INTO users "
                "(username, display_name, password_hash, role, is_active, created_at, updated_at) "
                "VALUES (?, ?, ?, 'admin', 1, ?, ?)",
                (username, username, hash_password(password), now, now),
            )


def create_user(
    *, username: str, password: str, display_name: str | None = None, role: str = "student"
) -> AuthUser:
    now = utc_now()
    username = username.strip()
    display_name = (display_name or username).strip() or username
    with connection() as conn:
        cursor = conn.execute(
            "INSERT INTO users "
            "(username, display_name, password_hash, role, is_active, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, 1, ?, ?)",
            (username, display_name, hash_password(password), role, now, now),
        )
        row = conn.execute("SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return _auth_user(row)  # type: ignore[return-value]


def get_user_by_username(username: str, *, include_inactive: bool = False) -> AuthUser | None:
    with connection() as conn:
        query = "SELECT * FROM users WHERE username = ? COLLATE NOCASE AND deleted_at IS NULL"
        params: list[Any] = [username.strip()]
        if not include_inactive:
            query += " AND is_active = 1"
        row = conn.execute(query, params).fetchone()
    return _auth_user(row)


def get_user_by_id(user_id: int, *, include_inactive: bool = False) -> AuthUser | None:
    with connection() as conn:
        query = "SELECT * FROM users WHERE id = ? AND deleted_at IS NULL"
        if not include_inactive:
            query += " AND is_active = 1"
        row = conn.execute(query, (user_id,)).fetchone()
    return _auth_user(row)


def get_user_password_hash(username: str) -> str | None:
    with connection() as conn:
        row = conn.execute(
            "SELECT password_hash FROM users WHERE username = ? COLLATE NOCASE AND is_active = 1 AND deleted_at IS NULL",
            (username.strip(),),
        ).fetchone()
    return str(row["password_hash"]) if row else None


def create_session(user_id: int) -> str:
    token, token_hash, expires_at = new_session_token(settings.session_ttl_seconds)
    now = utc_now()
    with connection() as conn:
        conn.execute("DELETE FROM sessions WHERE expires_at <= ?", (now,))
        conn.execute(
            "INSERT INTO sessions (token_hash, user_id, expires_at, created_at) VALUES (?, ?, ?, ?)",
            (token_hash, user_id, expires_at, now),
        )
    return token


def get_user_by_session(token: str | None) -> AuthUser | None:
    if not token:
        return None
    now = utc_now()
    token_hash = hash_session_token(token)
    with connection() as conn:
        row = conn.execute(
            "SELECT u.* FROM sessions s JOIN users u ON u.id = s.user_id "
            "WHERE s.token_hash = ? AND s.expires_at > ? AND u.is_active = 1 AND u.deleted_at IS NULL",
            (token_hash, now),
        ).fetchone()
    return _auth_user(row)


def delete_session(token: str | None) -> None:
    if not token:
        return
    with connection() as conn:
        conn.execute("DELETE FROM sessions WHERE token_hash = ?", (hash_session_token(token),))


def list_users() -> list[dict[str, Any]]:
    with connection() as conn:
        rows = conn.execute(
            "SELECT id, username, display_name, role, is_active, created_at, updated_at "
            "FROM users WHERE deleted_at IS NULL ORDER BY id"
        ).fetchall()
    return [
        {**dict(row), "role_label": ROLE_LABELS.get(str(row["role"]), str(row["role"]))}
        for row in rows
    ]


def update_user(
    user_id: int,
    *,
    role: str | None = None,
    display_name: str | None = None,
    password: str | None = None,
    is_active: bool | None = None,
    actor_id: int | None = None,
) -> AuthUser | None:
    fields: list[str] = []
    values: list[Any] = []
    if role is not None:
        fields.append("role = ?")
        values.append(role)
    if display_name is not None:
        fields.append("display_name = ?")
        values.append(display_name.strip())
    if password is not None:
        fields.append("password_hash = ?")
        values.append(hash_password(password))
    if is_active is not None:
        fields.append("is_active = ?")
        values.append(int(is_active))
    if not fields:
        return get_user_by_id(user_id, include_inactive=True)
    fields.append("updated_at = ?")
    values.append(utc_now())
    values.append(user_id)
    with connection() as conn:
        conn.execute("BEGIN IMMEDIATE")
        target = conn.execute("SELECT * FROM users WHERE id=? AND deleted_at IS NULL", (user_id,)).fetchone()
        if target is None:
            return None
        next_role = role if role is not None else target["role"]
        next_active = is_active if is_active is not None else bool(target["is_active"])
        if user_id == actor_id and (not next_active or next_role != "admin"):
            raise ValueError("不能停用当前登录账号或移除当前管理员权限")
        if target["role"] == "admin" and target["is_active"] and (next_role != "admin" or not next_active):
            _require_another_admin(conn)
        conn.execute(f"UPDATE users SET {', '.join(fields)} WHERE id = ?", values)
        if password is not None or is_active is False:
            conn.execute("DELETE FROM sessions WHERE user_id=?", (user_id,))
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return _auth_user(row)


def count_active_admins() -> int:
    with connection() as conn:
        return int(
            conn.execute(
                "SELECT COUNT(*) FROM users WHERE role = 'admin' AND is_active = 1 AND deleted_at IS NULL"
            ).fetchone()[0]
        )


def update_user_role(user_id: int, *, role: str, is_active: bool | None = None) -> AuthUser | None:
    return update_user(user_id, role=role, is_active=is_active)


def _require_another_admin(conn: sqlite3.Connection) -> None:
    count = conn.execute("SELECT COUNT(*) FROM users WHERE role='admin' AND is_active=1 AND deleted_at IS NULL").fetchone()[0]
    if count <= 1:
        raise ValueError("系统至少需要一个启用中的管理员")


def delete_user(user_id: int, *, actor_id: int) -> bool:
    # Keep identity and submission FKs, reserve the username, remove credentials
    # and sessions. This prevents a new account inheriting the deleted user's work.
    with connection() as conn:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute("SELECT * FROM users WHERE id=? AND deleted_at IS NULL", (user_id,)).fetchone()
        if row is None:
            return False
        if user_id == actor_id:
            raise ValueError("不能删除当前登录账号")
        if row["role"] == "admin" and row["is_active"]:
            _require_another_admin(conn)
        now = utc_now()
        conn.execute("UPDATE users SET deleted_at=?, updated_at=?, is_active=0, password_hash='' WHERE id=?", (now, now, user_id))
        conn.execute("DELETE FROM sessions WHERE user_id=?", (user_id,))
    return True
