"""Give every OJ problem an editable Studio document without republishing it."""
import hashlib
import json
import re
import time
import uuid

from markdown_it import MarkdownIt

from ..db import connection, utc_now
from .models import fingerprint, new_problem, validate


def _fence(content, label):
    fence = '`' * max([3] + [len(run) + 1 for run in re.findall(r'`+', content)])
    return f'{fence}text {label}\n{content}' + ('' if content.endswith('\n') else '\n') + fence


def _statement(row, cases):
    statement = row['statement_markdown'] or row['description'] or ''
    tokens = MarkdownIt().parse(statement)
    headings = {tokens[i + 1].content.strip().rstrip('：:') for i, token in enumerate(tokens[:-1])
                if token.type == 'heading_open'}
    parts = [statement]
    for title, field, aliases in (
        ('输入格式', 'input_format', {'输入格式', '输入描述'}),
        ('输出格式', 'output_format', {'输出格式', '输出描述'}),
    ):
        text = row[field].strip()
        if text and not headings.intersection(aliases) and text not in (
            '见题面中的输入与交互协议。', '见题面中的输出与交互协议。',
        ):
            parts.append(f'## {title}\n\n{text}')
    fences = {token.info.strip(): token.content for token in tokens if token.type == 'fence'}
    examples = []
    for index, case in enumerate((c for c in cases if c['is_sample']), 1):
        for kind, field in (('input', 'input_data'), ('output', 'expected_output')):
            label = f'{kind}:#{index}'
            content = case[field]
            if fences.get('text ' + label) != content + ('' if content.endswith('\n') else '\n'):
                examples.append(_fence(content, label))
    if examples:
        parts.append('## 输入输出样例\n\n' + '\n\n'.join(examples))
    return '\n\n'.join(part for part in parts if part.strip())


def ensure_oj_documents(store):
    """Idempotently link missing drafts, including unlisted problems.

    Both catalog and document inserts share one SQLite transaction. Data files are
    immutable and written first; an interrupted import can retry without changing
    any existing draft, OJ problem, test-case ID, or submission snapshot.
    """
    imported = []
    with connection() as db:
        db.execute('ATTACH DATABASE ? AS studio_db', (str(store.db),))
        db.execute('BEGIN IMMEDIATE')
        rows = db.execute('''SELECT p.*, c.studio_id, c.id AS catalog_id,
                             s.revision AS published_revision, s.published_at
            FROM problems p JOIN problem_catalog c ON c.problem_id=p.id
            LEFT JOIN studio_publications s ON s.problem_id=p.id
            LEFT JOIN studio_db.problems d ON d.id=c.studio_id
            WHERE d.id IS NULL ORDER BY p.id''').fetchall()
        for row in rows:
            pid = row['studio_id'] or uuid.uuid4().hex[:12]
            revision = row['published_revision'] or 1
            cases = db.execute('''SELECT * FROM test_cases WHERE problem_id=? AND active=1
                                  ORDER BY order_index,id''', (row['id'],)).fetchall()
            config = json.loads(row['judge_config'] or '{}')
            document = new_problem()
            document.update(title=row['title'], statement=_statement(row, cases), mode=row['judge_mode'],
                            time_ms=row['time_limit_ms'], memory_mb=row['memory_limit_mb'], generation='',
                            output_kb=config.get('output_kb', 1024), message_bytes=config.get('message_bytes', 1024),
                            communication_protocol=config.get('communication_protocol', 'send-receive-stdin-v1'),
                            validation_passes=config.get('validation_passes', 2),
                            programs=config.get('programs', {}))
            document = validate(document)
            document['origin_problem_id'] = row['id']
            document['legacy_text_comparison'] = document['mode'] == 'normal' and not document['programs'].get('checker')
            now = time.time()
            dataset = None
            if cases:
                jid = uuid.uuid4().hex
                directory = store.root / 'datasets' / jid
                directory.mkdir(parents=True)
                entries, total = [], 0
                for index, case in enumerate(cases, 1):
                    name = f'{index:03d}'
                    inp, ans = case['input_data'].encode('utf-8'), case['expected_output'].encode('utf-8')
                    (directory / (name + '.in')).write_bytes(inp)
                    (directory / (name + '.ans')).write_bytes(ans)
                    total += len(inp) + len(ans)
                    entries.append(dict(id=name, name=case['name'], is_sample=bool(case['is_sample']),
                                        weight=case['weight'], input_bytes=len(inp), answer_bytes=len(ans),
                                        args=[], sha256=hashlib.sha256(inp).hexdigest(), validated=False))
                dataset = dict(id=jid, origin='oj', fingerprint=fingerprint(document), revision=revision,
                               cases=entries, created=now, bytes=total)
            db.execute('''INSERT INTO studio_db.problems
                (id,document,revision,created,updated,dataset) VALUES (?,?,?,?,?,?)''',
                (pid, json.dumps(document), revision, now, now, json.dumps(dataset) if dataset else None))
            db.execute('UPDATE problem_catalog SET studio_id=? WHERE id=?', (pid, row['catalog_id']))
            db.execute('''INSERT INTO studio_publications VALUES (?,?,?,?,?)
                ON CONFLICT(studio_id) DO UPDATE SET revision=excluded.revision, fingerprint=excluded.fingerprint''',
                (pid, row['id'], revision, fingerprint(document), row['published_at'] or row['updated_at'] or utc_now()))
            imported.append(pid)
    return imported
