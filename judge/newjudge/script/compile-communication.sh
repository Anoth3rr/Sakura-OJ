#!/usr/bin/env bash
# File A: compile sources and write requests. Never invoke lworkflow here.
set -euo pipefail
communication_root="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 -B - "$communication_root" "$@" <<'PY'
import argparse
import json
import math
import os
from pathlib import Path
import re
import sys

repo = Path(sys.argv.pop(1))
sys.path.insert(0, str(repo / 'lib'))
from newjudge.compiler import CompileError, Compiler, JudgeError, MIB
from newjudge.source import ProblemError, source


def seconds(value):
    try:
        number = float(value)
        if math.isfinite(number) and 0.01 <= number <= 3600:
            return number
    except ValueError:
        pass
    raise argparse.ArgumentTypeError('时间必须为 0.01～3600 秒')


def byte_count(value):
    match = re.fullmatch(r'(\d+)([kmg]?)(?:b)?', value, re.IGNORECASE)
    if match:
        number = int(match[1]) * 1024 ** ('', 'k', 'm', 'g').index(match[2].lower())
        if number > 0:
            return number
    raise argparse.ArgumentTypeError('请使用正整数字节数或 k/m/g 后缀，例如 512m')


parser = argparse.ArgumentParser(prog='compile-communication.sh', allow_abbrev=False,
    description='只编译选手和裁判，生成供 lworkflow 使用的 JSON 清单；不运行判题。支持 DOMjudge validator 或 testlib interactor + checker。')
parser.add_argument('--user-code', '-u', required=True, type=Path)
judges = parser.add_mutually_exclusive_group(required=True)
judges.add_argument('--validator-code', '-c', type=Path, help='DOMjudge 多轮 output validator')
judges.add_argument('--interactor-code', type=Path, help='testlib 首轮 interactor，tout 作为第二轮输入')
parser.add_argument('--checker-code', type=Path, help='testlib 第二轮 checker；与 --interactor-code 配对')
parser.add_argument('--language', help='选手语言配置名；默认按原生源码后缀选择')
parser.add_argument('--validator-language', help='validator 语言配置名')
parser.add_argument('--interactor-language', help='interactor 语言配置名')
parser.add_argument('--checker-language', help='checker 语言配置名')
parser.add_argument('--etc-dir', type=Path, default=Path('/etc/ljudge'))
parser.add_argument('--cache-dir', type=Path, default=Path.home() / '.cache/lcommunication')
parser.add_argument('--runtime', type=Path, default=Path(os.environ.get('NEWJUDGE_RUNTIME', repo / 'runtime')))
parser.add_argument('--testlib', type=Path, help='默认 runtime/testlib.h')
parser.add_argument('--request-dir', type=Path, required=True, help='保存清单的新目录，必须尚不存在')
parser.add_argument('--validation-passes', type=int, default=2)
parser.add_argument('--max-cpu-time', type=seconds, default=2.0)
parser.add_argument('--max-real-time', type=seconds, default=6.0)
parser.add_argument('--max-memory', type=byte_count, default=512 * MIB)
parser.add_argument('--max-output', type=byte_count, default=8 * MIB)
for judge_role in ('validator', 'interactor', 'checker'):
    parser.add_argument(f'--max-{judge_role}-cpu-time', type=seconds, default=5.0)
    parser.add_argument(f'--max-{judge_role}-real-time', type=seconds, default=8.0)
    parser.add_argument(f'--max-{judge_role}-memory', type=byte_count, default=512 * MIB)
    parser.add_argument(f'--max-{judge_role}-output', type=byte_count, default=8 * MIB)
parser.add_argument('--testcase', action='store_true', help='可重复的测试点分隔标记')
parser.add_argument('--input', '-i', action='append', type=Path, required=True)
parser.add_argument('--output', '-o', action='append', type=Path, required=True,
                    help='标准答案文件；不使用答案时传入已有空文件')
args = parser.parse_args()
if bool(args.interactor_code) != bool(args.checker_code):
    parser.error('--interactor-code 与 --checker-code 必须一起提供；不能与 --validator-code 混用')
if len(args.input) != len(args.output):
    parser.error('--input 与 --output 必须按顺序一一对应')
if not 1 <= args.validation_passes <= 32:
    parser.error('--validation-passes 必须在 1～32 之间')
if args.interactor_code and args.validation_passes != 2:
    parser.error('interactor + checker 通信模式固定运行两轮，--validation-passes 必须为 2')
if any(getattr(args, key) > 64 * MIB for key in
       ('max_output', 'max_validator_output', 'max_interactor_output', 'max_checker_output')):
    parser.error('输出上限不能超过 64m')
if os.path.lexists(args.request_dir):
    parser.error('--request-dir 必须指定不存在的新目录，避免覆盖已有清单')
sources = [('program', args.user_code, args.language)]
if args.validator_code:
    sources.append(('validator', args.validator_code, args.validator_language))
else:
    sources += [('interactor', args.interactor_code, args.interactor_language),
                ('checker', args.checker_code, args.checker_language)]
for path in [*(item[1] for item in sources), *args.input, *args.output]:
    if not path.is_file():
        parser.error(f'文件不存在或不是普通文件：{path}')

report = dict(success=False, status='ERROR', compilation={}, requests=[])
role = None
try:
    runtime = args.runtime.resolve()
    engine = Compiler(args.cache_dir.resolve(), runtime,
                    (args.testlib or runtime / 'testlib.h').resolve(), args.etc_dir.resolve())
    # Compiling only needs lrun and the language tools. The native judging
    # executable can be built/installed later, before the separate judging step.
    engine.prepare()
    programs = {}
    for role, path, language in sources:
        if language is None:
            language = 'v8js' if path.name.startswith('mainv8.js') else path.name.partition('.')[2]
        item = source(dict(name=path.name, language=language, content=path.read_text(encoding='utf-8')))
        programs[role] = engine.compile(item, role)
        report['compilation'][role] = dict(success=True, artifacts=str(programs[role].path.resolve()))
    role = None
    specs = dict(program=engine.native_program(programs['program'], cpu=args.max_cpu_time,
        wall=args.max_real_time, memory=args.max_memory, output=args.max_output))
    def judge_spec(name, **options):
        return engine.native_program(programs[name],
            cpu=getattr(args, f'max_{name}_cpu_time'), wall=getattr(args, f'max_{name}_real_time'),
            memory=getattr(args, f'max_{name}_memory'), output=getattr(args, f'max_{name}_output'), **options)
    if args.validator_code:
        mode = 'multipass'
        specs['validation_passes'] = args.validation_passes
        specs['validator'] = judge_spec('validator',
            args=['/work/input', '/work/answer', '/work/feedback'],
            files={'input': '@INPUT@', 'answer': '@ANSWER@'}, feedback=True)
    else:
        mode = 'communication'
        specs['interactor'] = judge_spec('interactor',
            args=['/work/input', '/work/transcript', '/work/answer'],
            files={'input': '@INPUT@', 'answer': '@ANSWER@'})
        specs['checker'] = judge_spec('checker',
            args=['/work/input', '/work/output', '/work/answer'],
            files={'input': '@INPUT@', 'output': '@OUTPUT@', 'answer': '@ANSWER@'})
    directory = args.request_dir.resolve()
    directory.mkdir(parents=True)
    for index, (inp, ans) in enumerate(zip(args.input, args.output), 1):
        request = dict(version=1, mode=mode, work_root=str(engine.work.resolve()),
                       input=str(inp.resolve()), answer=str(ans.resolve()), **specs)
        target = directory / f'{index:03d}.request.json'
        target.write_text(json.dumps(request, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        report['requests'].append(str(target))
    report.update(success=True, status='PREPARED')
except (CompileError, JudgeError, ProblemError, OSError, UnicodeError) as exc:
    report['error'] = str(exc)
    if role:
        report['compilation'][role] = dict(success=False, log=str(exc))
    if isinstance(exc, CompileError):
        report['status'] = 'COMPILE_ERROR'
print(json.dumps(report, ensure_ascii=False, indent=2))
sys.exit(0 if report['success'] else 1)
PY
