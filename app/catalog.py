"""Stable public problem IDs spanning authoring drafts and the OJ problem bank."""
import re

from .db import connection, utc_now


def problem_code(catalog_id: int) -> str:
    return f"{catalog_id:04d}"


def parse_code(value: str) -> int:
    text = str(value).strip().upper()
    if not re.fullmatch(r"P?[0-9]{1,12}", text):
        raise ValueError("请填写有效题目 ID，例如 0001")
    number = int(text.removeprefix("P"))
    if number < 1:
        raise ValueError("题目 ID 必须大于 0")
    return number


def decorate_documents(documents: list[dict]) -> list[dict]:
    """Allocate once in the shared DB; editing or restoring a draft never changes its ID."""
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        result = []
        for document in documents:
            row = db.execute("SELECT id FROM problem_catalog WHERE studio_id=?", (document["id"],)).fetchone()
            if row is None:
                cursor = db.execute("INSERT INTO problem_catalog (studio_id, created_at) VALUES (?,?)",
                                    (document["id"], utc_now()))
                catalog_id = cursor.lastrowid
            else:
                catalog_id = row["id"]
            result.append(dict(document, problem_code=problem_code(catalog_id)))
    return result


def decorate(document: dict) -> dict:
    return decorate_documents([document])[0]


def entries(store, search: str = "") -> list[dict]:
    from .studio.catalog_sync import ensure_oj_documents
    ensure_oj_documents(store)
    documents = decorate_documents(store.list() + store.list(trashed=True))
    by_studio = {item["id"]: item for item in documents}
    with connection() as db:
        rows = db.execute("""SELECT c.*, p.title, p.slug, p.judge_mode, p.is_public, p.difficulty,
                           (SELECT COUNT(*) FROM submissions sub WHERE sub.problem_id=p.id) AS submission_count,
                           (SELECT COUNT(*) FROM submissions sub WHERE sub.problem_id=p.id AND sub.verdict='ACCEPTED') AS accepted_count,
                           s.revision AS published_revision
                           FROM problem_catalog c LEFT JOIN problems p ON p.id=c.problem_id
                           LEFT JOIN studio_publications s ON s.studio_id=c.studio_id
                           ORDER BY c.id DESC""").fetchall()
    result = []
    needle = search.strip().casefold()
    for row in rows:
        draft = by_studio.get(row["studio_id"])
        if draft is None and row["problem_id"] is None:
            continue
        code = problem_code(row["id"])
        title = row["title"] or (draft["title"] if draft else "")
        if needle and not any(needle in str(value or "").casefold() for value in (code, f"P{row['id']:06d}", title, row["slug"], draft and draft["title"])):
            continue
        listed = bool(row["is_public"])
        trashed = bool(draft and draft["deleted_at"] is not None)
        ready = bool(draft and draft["data_ready"] and not trashed)
        result.append(dict(
            problem_code=code, title=title, mode=row["judge_mode"] or (draft["mode"] if draft else "normal"),
            studio_id=row["studio_id"], problem_id=row["problem_id"], listed=listed,
            difficulty=row["difficulty"], submission_count=row["submission_count"], accepted_count=row["accepted_count"],
            data_ready=ready, trashed=trashed, published_revision=row["published_revision"],
            can_add=not listed and (row["problem_id"] is not None or ready),
            url="/#problem/" + row["slug"] if row["slug"] else None,
            studio_url="/studio/#" + row["studio_id"] + "/statement" if draft and not trashed else None,
        ))
    return result


def lookup(code: str) -> dict | None:
    with connection() as db:
        row = db.execute("SELECT * FROM problem_catalog WHERE id=?", (parse_code(code),)).fetchone()
    return dict(row) if row else None


def set_listed(code: str, listed: bool) -> int | None:
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("SELECT problem_id FROM problem_catalog WHERE id=?", (parse_code(code),)).fetchone()
        if row is None or row["problem_id"] is None:
            return None
        db.execute("UPDATE problems SET is_public=?, updated_at=? WHERE id=?", (int(listed), utc_now(), row["problem_id"]))
        return row["problem_id"]
