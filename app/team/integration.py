"""Propagate OJ outcomes into team profiles using the existing oj_username field."""
from .. import repository as oj
from . import repository


def sync_submission(submission_id):
    # Keep records explicitly cleared from the team out of automatic backfills.
    # The original OJ submission remains available in the OJ module.
    with repository.connection() as db:
        if db.execute('SELECT 1 FROM submission_sync_exclusions WHERE platform=? AND external_id=?',
                      ('oj', submission_id)).fetchone():
            return False
    submission = oj.get_submission(submission_id)
    if not submission:
        return False
    user = oj.get_user_by_id(submission['user_id'], include_inactive=True) if submission.get('user_id') else None
    existing = repository.get_submission('oj-' + submission_id)
    member_id = existing.get('member_id') if existing else None
    if user:
        with repository.connection() as db:
            matches = db.execute('SELECT id FROM members WHERE oj_username=? COLLATE NOCASE', (user.username,)).fetchall()
        if len(matches) == 1:
            member_id = matches[0]['id']
    repository.upsert_submission(dict(id='oj-' + submission_id, external_id=submission_id,
        member_id=member_id, platform='oj', problem_id=submission['problem_slug'],
        problem_name=submission['problem_title'], verdict=submission['verdict'],
        language=submission['language'], submitted_at=submission['created_at'],
        runtime_ms=submission['runtime_ms'], memory_kb=submission['memory_kb'],
        code_length=len(submission['source_code']), source='sakura-oj', url='/#submission/' + submission_id))
    return True


def sync_all_local():
    from ..db import connection
    with connection() as db:
        ids = [r[0] for r in db.execute('SELECT id FROM submissions')]
    imported = sum(bool(sync_submission(submission_id)) for submission_id in ids)
    return dict(imported=imported, source='Sakura OJ')
