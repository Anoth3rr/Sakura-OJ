"""Private authoring bundles, including labeled solutions and ordered papers."""
import io
import json
from pathlib import Path
import zipfile

from fastapi.responses import Response

from .models import LEGACY_COMMUNICATION, ProblemError
from ..catalog import decorate


def write_problem(archive, service, problem, prefix=''):
    p = problem
    metadata = {k: v for k, v in p.items() if k not in ('programs', 'solutions', 'statement', 'dataset')}
    metadata['format'] = 'sakura-studio-v2'
    metadata['programs'] = {r: (f'programs/{r}/Main.java' if v['language'] == 'java' else
                                f'programs/{r}{Path(v["name"]).suffix.lower()}') for r, v in p['programs'].items()}
    metadata['program_languages'] = {r: v['language'] for r, v in p['programs'].items()}
    metadata['communication_protocol'] = p.get('communication_protocol', LEGACY_COMMUNICATION)
    metadata['solutions'] = []
    for s in p.get('solutions', []):
        filename = 'Main.java' if s['language'] == 'java' else s['name']
        path = f'solutions/{s["id"]}/{filename}'
        entry = {k: v for k, v in s.items() if k not in ('content', 'receiver')}
        entry['path'] = path
        archive.writestr(prefix + path, s['content'])
        if s.get('receiver'):
            receiver = s['receiver']
            path = f'solutions/{s["id"]}/receiver/' + ('Main.java' if receiver['language'] == 'java' else receiver['name'])
            archive.writestr(prefix + path, receiver['content'])
            entry['receiver'] = dict(name=receiver['name'], language=receiver['language'], path=path)
        metadata['solutions'].append(entry)
    if p['data_ready']:
        metadata['testcases'] = p['dataset']['cases']
        for entry in p['dataset']['cases']:
            for suffix in ('in', 'ans'):
                f = service.jobs.case_path(p, entry['id'], suffix)
                archive.write(f, prefix + 'tests/' + f.name)
    archive.writestr(prefix + 'problem.json', json.dumps(metadata, ensure_ascii=False, indent=2))
    archive.writestr(prefix + 'statement.md', p['statement'])
    for role, item in p['programs'].items():
        archive.writestr(prefix + metadata['programs'][role], item['content'])


def bundle(service, problem=None, paper=None):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        if problem:
            write_problem(archive, service, problem)
            filename = 'problem-' + problem['id']
        else:
            if not paper['problem_ids']:
                raise ProblemError('请先向试卷添加题目')
            metadata = {k: v for k, v in paper.items() if k != 'problems'}
            metadata.update(format='sakura-paper-v1', problems=[])
            statement = [f'# {paper["title"]}', paper['description']]
            for index, pid in enumerate(paper['problem_ids'], 1):
                p = decorate(service.store.get(pid))
                prefix = f'{index:02d}-{p["problem_code"]}/'
                write_problem(archive, service, p, prefix)
                metadata['problems'].append(dict(id=pid, problem_code=p['problem_code'], title=p['title'],
                                                 revision=p['revision'], data_ready=p['data_ready'], path=prefix))
                statement += ['---', f'## 第 {index} 题 · {p["title"]}', p['statement']]
            archive.writestr('paper.json', json.dumps(metadata, ensure_ascii=False, indent=2))
            archive.writestr('statement.md', '\n\n'.join(statement))
            filename = 'paper-' + paper['id']
    return Response(buffer.getvalue(), media_type='application/zip',
                    headers={'Content-Disposition': f'attachment; filename="{filename}.zip"'})
