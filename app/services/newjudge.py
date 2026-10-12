"""Adapt the shared lrun sandbox and testlib workflows to Sakura OJ reports."""
import tempfile
from pathlib import Path

from ..config import settings
from ..studio.engine import CompileError, JudgeError
from ..studio.service import Sandbox
from ..studio.toolchains import LANGUAGES
from .runner import _report, normalize_output


VERDICTS = {'AC': 'ACCEPTED', 'WA': 'WRONG_ANSWER', 'PE': 'PRESENTATION_ERROR',
            'CE': 'COMPILE_ERROR', 'RE': 'RUNTIME_ERROR', 'TLE': 'TIME_LIMIT_EXCEEDED',
            'MLE': 'MEMORY_LIMIT_EXCEEDED', 'OLE': 'OUTPUT_LIMIT_EXCEEDED',
            'CLE': 'COMMUNICATION_LIMIT_EXCEEDED', 'IE': 'SYSTEM_ERROR'}


class NewjudgeRunner:
    def __init__(self, sandbox=None, runner_settings=settings):
        self.sandbox = sandbox or Sandbox(runner_settings)

    def run(self, **kwargs):
        return self.run_problem(config={}, **kwargs)

    def run_problem(self, *, submission_id, source_code, language, test_cases,
                    time_limit_ms, memory_limit_mb, config):
        language = 'cpp' if language == 'cpp17' else language
        if language not in LANGUAGES:
            return _report('SYSTEM_ERROR', error_message='newjudge 支持 C17、C++17、Python 3、PyPy 3 和 Java 21')
        if not test_cases:
            return _report('SYSTEM_ERROR', error_message='题目没有有效测试数据')
        engine = self.sandbox
        with engine.lock:
            try:
                program = engine.compile(dict(language=language, content=source_code), '参赛程序')
            except CompileError as exc:
                return _report('COMPILE_ERROR', compile_output=str(exc), error_message='编译失败')
            except (JudgeError, OSError) as exc:
                return _report('SYSTEM_ERROR', error_message=str(exc))
            p = dict(mode='normal', time_ms=time_limit_ms, memory_mb=memory_limit_mb,
                     output_kb=1024, message_bytes=1024, **{k: v for k, v in config.items()
                     if k not in ('mode', 'time_ms', 'memory_mb', 'output_kb', 'message_bytes')})
            p.update(config)
            try:
                tools = p.get('programs', {})
                checker = engine.compile(tools['checker'], 'checker') if tools.get('checker') else None
                interactor = engine.compile(tools['interactor'], 'interactor') if tools.get('interactor') else None
                results, overall, earned = [], 'ACCEPTED', 0
                total = sum(max(1, c.get('weight', 1)) for c in test_cases)
                max_time = max_memory = 0
                for case in test_cases:
                    if not tools and p['mode'] == 'normal':
                        r = engine.run(program, data=case['input_data'].encode(), **engine.limits(p))
                        if r['verdict'] == 'OK':
                            output = r['output'].decode('utf-8', errors='replace')
                            r['verdict'] = 'AC' if normalize_output(output) == normalize_output(case['expected_output']) else 'WA'
                        r = engine.summary(r)
                    else:
                        with tempfile.TemporaryDirectory() as tmp:
                            inp, ans = Path(tmp)/'input', Path(tmp)/'answer'
                            inp.write_bytes(case['input_data'].encode())
                            ans.write_bytes(case['expected_output'].encode())
                            r = engine.judge(program, checker, dict(input=inp, answer=ans), p, interactor)
                    verdict = VERDICTS.get(r['verdict'], 'SYSTEM_ERROR')
                    if verdict == 'ACCEPTED':
                        earned += max(1, case.get('weight', 1))
                    elif overall == 'ACCEPTED':
                        overall = verdict
                    elapsed = round(r.get('time_ms', 0))
                    memory = r.get('memory_kb', 0)
                    max_time, max_memory = max(max_time, elapsed), max(max_memory, memory)
                    # Hidden-case checker/interactor diagnostics may contain secrets.
                    # Full diagnostics remain in the manager-only Studio trial UI.
                    diagnostic = '' if verdict == 'ACCEPTED' else verdict
                    if verdict == 'RUNTIME_ERROR':
                        diagnostic = r.get('stderr', '')[-2000:] or verdict
                    results.append(dict(test_case_id=case['id'], verdict=verdict,
                        score=100 if verdict == 'ACCEPTED' else 0, runtime_ms=elapsed,
                        memory_kb=memory, message_bytes=r.get('message_bytes'),
                        output=r.get('output_preview', '') if p['mode']=='normal' else '',
                        error_message=diagnostic))
                return dict(verdict=overall, score=round(earned/total*100), compile_output='',
                            error_message='' if overall=='ACCEPTED' else overall,
                            runtime_ms=max_time, memory_kb=max_memory, results=results)
            except (JudgeError, OSError) as exc:
                return _report('SYSTEM_ERROR', error_message='评测配置或沙箱异常，请联系题目管理员')
