"""Publish immutable judging material into the shared OJ, preserving old results."""
import json
import re
import sqlite3

from .. import repository
from ..db import connection, utc_now
from .models import ProblemError, fingerprint, LEGACY_COMMUNICATION, is_multipass, is_testlib_communication, uses_interactor
from ..catalog import decorate, problem_code


def publication(pid):
    with connection() as db:
        row = db.execute('''SELECT s.*, p.slug, p.is_public, p.difficulty, c.id AS catalog_id FROM studio_publications s
            JOIN problems p ON p.id=s.problem_id JOIN problem_catalog c ON c.problem_id=p.id
            WHERE s.studio_id=?''', (pid,)).fetchone()
    return dict(row, problem_code=problem_code(row['catalog_id'])) if row else None


def publish(service, problem, data):
    problem = decorate(problem)
    if not problem['data_ready']:
        raise ProblemError('请先为当前配置生成并验证测试数据', 409)
    existing = publication(problem['id'])
    slug = str(data.get('slug') or (existing['slug'] if existing else problem['problem_code'].lower()))
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) or not 2 <= len(slug) <= 80:
        raise ProblemError('题目 slug 需为 2～80 位小写字母、数字或连字符')
    difficulty = data.get('difficulty', existing['difficulty'] if existing else '进阶')
    if not isinstance(difficulty, str) or not 1 <= len(difficulty.strip()) <= 20:
        raise ProblemError('难度名称需为 1～20 个字符')
    cases = []
    for entry in problem['dataset']['cases']:
        try:
            inp = service.jobs.case_path(problem, entry['id'], 'in').read_bytes().decode('utf-8')
            ans = service.jobs.case_path(problem, entry['id'], 'ans').read_bytes().decode('utf-8')
        except (OSError, UnicodeError) as exc:
            raise ProblemError('测试文件缺失或不是 UTF-8，请重新生成数据', 409) from exc
        cases.append((entry.get('name', entry['id']), inp, ans,
                      int(entry.get('is_sample', False)), entry.get('weight', 1)))
    config = {k: problem[k] for k in ('mode', 'time_ms', 'memory_mb', 'output_kb', 'message_bytes')}
    config.update(communication_protocol=problem.get('communication_protocol', LEGACY_COMMUNICATION),
                  validation_passes=problem.get('validation_passes', 2))
    judge_roles = ('checker', 'interactor') if uses_interactor(problem) else ('checker',)
    config['programs'] = {k: v for k, v in problem['programs'].items() if k in judge_roles}
    config['studio_id'] = problem['id']
    config['revision'] = problem['revision']
    now = utc_now()
    description = {'normal': '请根据题面要求编写程序。',
                   'interactive': '交互题：请遵循题面的交互协议，并及时刷新输出。',
                   'communication': ('testlib 两轮通信题：首轮交互，次轮读取消息并输出答案。' if is_testlib_communication(problem)
                                     else f"多阶段通信题：最多 {problem.get('validation_passes', 2)} 轮。" if is_multipass(problem)
                                     else f"run-twice 通信题：消息上限 {problem['message_bytes']} 字节。")}[problem['mode']]
    try:
        with connection() as db:
            db.execute('BEGIN IMMEDIATE')
            link = db.execute('SELECT * FROM studio_publications WHERE studio_id=?', (problem['id'],)).fetchone()
            values = (slug, problem['title'], description, problem['statement'],
                      '见题面中的输入与交互协议。', '见题面中的输出与交互协议。', difficulty.strip(),
                      problem['time_ms'], problem['memory_mb'], problem['mode'], json.dumps(config), now)
            if link:
                problem_id = link['problem_id']
                db.execute('''UPDATE problems SET slug=?,title=?,description=?,statement_markdown=?,
                    input_format=?,output_format=?,difficulty=?,time_limit_ms=?,memory_limit_mb=?,
                    judge_mode=?,judge_config=?,updated_at=?,is_public=1 WHERE id=?''', (*values, problem_id))
                db.execute('UPDATE test_cases SET active=0 WHERE problem_id=?', (problem_id,))
            else:
                # Accommodate the oldest OJ schema's NOT NULL constraints column.
                legacy = 'constraints' in {r['name'] for r in db.execute('PRAGMA table_info(problems)')}
                cursor = db.execute('''INSERT INTO problems (slug,title,description,statement_markdown,
                    input_format,output_format,difficulty,time_limit_ms,memory_limit_mb,judge_mode,
                    judge_config,updated_at,created_at''' + (',constraints' if legacy else '') + ''')
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?''' + (",''" if legacy else '') + ')', (*values, now))
                problem_id = cursor.lastrowid
            db.execute('UPDATE problem_catalog SET problem_id=? WHERE studio_id=?', (problem_id, problem['id']))
            for order, (name, inp, ans, is_sample, weight) in enumerate(cases):
                db.execute('''INSERT INTO test_cases
                    (problem_id,name,input_data,expected_output,is_sample,weight,order_index,active)
                    VALUES (?,?,?,?,?,?,?,1)''', (problem_id, name, inp, ans, is_sample, weight, order))
            db.execute('''INSERT INTO studio_publications VALUES (?,?,?,?,?)
                ON CONFLICT(studio_id) DO UPDATE SET revision=excluded.revision,
                fingerprint=excluded.fingerprint,published_at=excluded.published_at''',
                (problem['id'], problem_id, problem['revision'], fingerprint(problem), now))
    except sqlite3.IntegrityError as exc:
        raise ProblemError('slug 已被其他题目使用，请修改后重试', 409) from exc
    return dict(problem=repository.get_problem_by_id(problem_id), publication=publication(problem['id']),
                url='/#problem/' + slug)
