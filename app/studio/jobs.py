"""Serial background jobs: versioned data generation and real sandbox judging."""
import hashlib
from pathlib import Path
import queue
import threading
import time
import traceback

from .engine import CompileError, JudgeError, MIB
from .models import (ProblemError, fingerprint, generation_lines, source, is_multipass,
                     is_testlib_communication, uses_interactor, main_solution,
                     effective_programs, EXPECTED_VERDICTS)
from ..services.runner import normalize_output


class Jobs:
    def __init__(self, store, engine):
        self.store, self.engine = store, engine
        self.root = store.root / 'datasets'
        self.root.mkdir(exist_ok=True)
        self.queue = queue.Queue(maxsize=12)
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self.worker, name='studio-worker', daemon=True)
        self.thread.start()

    def shutdown(self):
        self.queue.join()
        self.queue.put(None)
        self.thread.join()

    def submit(self, problem, kind, body):
        if not self.engine.health()['ready']:
            raise ProblemError('评测机未就绪，请检查 cgroup、lrun、lworkflow 和语言配置', 503)
        if kind == 'generate':
            if problem.get('solutions') and not main_solution(problem):
                raise ProblemError('请先将一份正确解法指定为 Main Correct 标程')
            needed = ['gen', 'val']
            if is_testlib_communication(problem):
                needed += ['interactor', 'checker']
            else:
                needed += ['interactor'] if problem['mode'] == 'interactive' else ['checker'] if is_multipass(problem) else ['checker', 'reference']
            missing = [x for x in needed if x not in effective_programs(problem)]
            if missing:
                raise ProblemError('请先上传并保存：' + '、'.join(missing))
            generation_lines(problem['generation'])
            extra = {}
        else:
            if not problem['data_ready']:
                raise ProblemError('请先为当前评测配置生成并验证数据', 409)
            if kind == 'invoke':
                solutions = problem.get('solutions', [])
                ids = body.get('solution_ids')
                if ids == 'all':
                    ids = [s['id'] for s in solutions]
                if (not isinstance(ids, list) or not ids or not all(isinstance(x, str) for x in ids)
                        or len(ids) != len(set(ids)) or not set(ids) <= {s['id'] for s in solutions}):
                    raise ProblemError('请选择至少一份已保存的解法，解法 ID 不能重复或不存在')
                extra = dict(solutions=[s for s in solutions if s['id'] in ids])
            elif kind == 'submit':
                extra = dict(solution=source(body.get('solution')))
            else:
                raise ProblemError('未知任务类型')
            if kind == 'submit' and body.get('receiver'):
                if problem['mode'] != 'communication':
                    raise ProblemError('只有通信题支持独立 Receiver')
                if is_multipass(problem) or is_testlib_communication(problem):
                    raise ProblemError('当前通信协议每轮运行同一份程序，不使用独立 Receiver')
                extra['receiver'] = source(body['receiver'])
        with self.lock:
            if self.queue.full():
                raise ProblemError('评测队列已满，请稍后再试', 429)
            jid = self.store.add_job(problem['id'], kind, problem['revision'])
            self.store.update_job(jid, revision=problem['revision'], mode=problem['mode'],
                                  dataset_id=(problem.get('dataset') or {}).get('id'),
                                  solution_ids=[s['id'] for s in extra.get('solutions', [])])
            self.queue.put_nowait((jid, problem, kind, extra))
        return self.store.job(jid)

    def worker(self):
        while True:
            task = self.queue.get()
            if task is None:
                self.queue.task_done()
                return
            jid, p, kind, extra = task
            log = []

            def report(line, progress=None, **values):
                log.append(time.strftime('%H:%M:%S') + '  ' + line)
                if progress is not None:
                    values['progress'] = progress
                self.store.update_job(jid, log=log, **values)

            try:
                self.store.update_job(jid, state='running', revision=p['revision'], mode=p['mode'])
                report(f'使用题目版本 r{p["revision"]} · newjudge / lrun')
                if kind == 'generate':
                    self.generate(jid, p, report)
                elif kind == 'invoke':
                    self.invoke(p, extra['solutions'], report)
                else:
                    self.judge(p, extra, report)
                self.store.update_job(jid, state='done', progress=100)
            except (JudgeError, ProblemError) as exc:
                report(str(exc))
                self.store.update_job(jid, state='failed', error=str(exc), verdict='IE')
            except Exception:
                traceback.print_exc()
                report('服务内部异常，详细信息已写入服务日志')
                self.store.update_job(jid, state='failed', error='服务内部异常，请检查日志', verdict='IE')
            finally:
                self.queue.task_done()

    def compile_roles(self, p, report):
        compiled = {}
        for role, item in effective_programs(p).items():
            if role == 'interactor' and not uses_interactor(p):
                continue
            report(f'编译 {role} · {item["name"]}')
            compiled[role] = self.engine.compile(item, role)
        return compiled

    def generate(self, jid, p, report):
        compiled = self.compile_roles(p, report)
        main = main_solution(p)
        main_program = self.engine.compile(main, 'Main Correct') if main and uses_interactor(p) else None
        receiver = self.engine.compile(main['receiver'], 'Main Correct Receiver') if main and main.get('receiver') else None
        lines = generation_lines(p['generation'])
        directory = self.root / jid
        directory.mkdir()
        cases, total = [], 0
        for index, args in enumerate(lines, 1):
            name = f'{index:03d}'
            last_step = ('多阶段标程自检' if 'reference' in compiled else '保存输入') if is_multipass(p) else '标准答案'
            report(f'#{name} · gen → val → {last_step}', 10 + int(85 * (index - 1) / len(lines)))
            generated = self.engine.run(compiled['gen'], args=args, cpu=3, wall=8, output=4 * MIB)
            if generated['verdict'] != 'OK':
                raise JudgeError(f'#{name} gen 失败：{generated["verdict"]}\n{generated["stderr"]}')
            data = generated['output']
            validated = self.engine.run(compiled['val'], data=data, cpu=5, wall=8)
            if validated['verdict'] != 'OK':
                raise JudgeError(f'#{name} val 拒绝数据\n{validated["stderr"]}')
            answer = b''
            if 'reference' in compiled and not is_multipass(p):
                result = (self.engine.twice(compiled['reference'], data, p, receiver)
                          if p['mode'] == 'communication' and not is_testlib_communication(p) else
                          self.engine.run(compiled['reference'], data=data, **self.engine.limits(p)))
                if result['verdict'] != 'OK':
                    raise JudgeError(f'#{name} 标程失败：{result["verdict"]}\n{result["stderr"]}')
                answer = result['output']
            inp, ans = directory / (name + '.in'), directory / (name + '.ans')
            inp.write_bytes(data)
            ans.write_bytes(answer)
            if is_multipass(p) and 'reference' in compiled:
                checked = self.engine.multipass(compiled['reference'], compiled['checker'], inp, ans, p)
                if checked['verdict'] != 'AC':
                    raise JudgeError(f'#{name} 标程多阶段自检失败：{checked["verdict"]}\n{checked.get("message", "")}')
            elif p['mode'] != 'interactive' and not is_multipass(p) and (not is_testlib_communication(p) or 'reference' in compiled):
                checked = self.engine.check(compiled['checker'], inp, ans, answer)
                if checked['verdict'] != 'AC':
                    raise JudgeError(f'#{name} checker 自检失败：{checked["verdict"]}\n{checked["message"]}')
            if main_program:
                checked = self.engine.judge(main_program, compiled.get('checker'), dict(input=inp, answer=ans),
                                            p, compiled['interactor'])
                if checked['verdict'] != 'AC':
                    raise JudgeError(f'#{name} Main Correct 自检失败：{checked["verdict"]}\n{checked.get("message", "")}')
                report(f'#{name} · Main Correct 完整流程自检通过')
            total += len(data) + len(answer)
            if total > 256 * MIB:
                raise JudgeError('本次数据包超过 256 MiB，请减少测试点或数据大小')
            cases.append(dict(id=name, input_bytes=len(data), answer_bytes=len(answer), args=args,
                              sha256=hashlib.sha256(data).hexdigest(), validated=True))
            report(f'#{name} · val 通过 · 输入 {len(data)} B / 答案 {len(answer)} B', cases=cases)
        dataset = dict(id=jid, fingerprint=fingerprint(p), revision=p['revision'], cases=cases,
                       created=time.time(), bytes=total)
        if not self.store.attach_dataset(p['id'], dataset):
            raise JudgeError('生成期间评测配置已修改。本次数据未启用，请按最新配置重新生成')
        report(f'{len(cases)} 个测试点已生成并验证，数据包已启用', 100, dataset=dataset)

    def judge(self, p, extra, report):
        report('编译参赛程序', 5)
        try:
            solution = self.engine.compile(extra['solution'], '参赛程序')
            receiver = self.engine.compile(extra['receiver'], 'Receiver') if extra.get('receiver') else None
        except CompileError as exc:
            result = dict(verdict='CE', cases=[], message=str(exc), max_time_ms=0, max_memory_kb=0)
            report(str(exc), 100, **result)
            return result
        checker_source = p['programs'].get('checker')
        checker = self.engine.compile(checker_source, 'checker') if checker_source else None
        interactor = (self.engine.compile(p['programs']['interactor'], 'interactor')
                      if uses_interactor(p) else None)
        if is_testlib_communication(p):
            report('两轮通信：interactor 与选手交互 → tout 作为第二轮输入 → checker 判定')
        if p['mode'] == 'interactive':
            report('交互判定：interactor + checker（检查 tout）' if checker else
                   '交互判定：interactor + 选手运行状态（未上传 checker）')
        cases, overall = [], 'AC'
        entries = p['dataset']['cases']
        directory = self.root / p['dataset']['id']
        for index, entry in enumerate(entries, 1):
            name = entry['id']
            report(f'评测 #{name}', 10 + int(85 * (index - 1) / len(entries)))
            files = dict(input=directory / (name + '.in'), answer=directory / (name + '.ans'))
            if p['mode'] == 'normal' and checker is None and p.get('legacy_text_comparison'):
                result = self.engine.run(solution, data=files['input'].read_bytes(), **self.engine.limits(p))
                if result['verdict'] == 'OK':
                    actual = result['output'].decode('utf-8', errors='replace')
                    expected = files['answer'].read_text(encoding='utf-8')
                    result['verdict'] = 'AC' if normalize_output(actual) == normalize_output(expected) else 'WA'
                result = self.engine.summary(result)
            else:
                result = self.engine.judge(solution, checker, files, p, interactor, receiver)
            cases.append(dict(result, id=name))
            if result['verdict'] != 'AC' and overall == 'AC':
                overall = result['verdict']
            report(f'#{name} · {result["verdict"]} · {result["time_ms"]:.1f} ms · {result["memory_kb"]} KiB',
                   cases=cases, verdict=overall)
        result = dict(verdict=overall, cases=cases,
                      max_time_ms=max((c['time_ms'] for c in cases), default=0),
                      max_memory_kb=max((c['memory_kb'] for c in cases), default=0))
        report(f'评测结束 · {overall}', 100, **result)
        return result

    def invoke(self, p, solutions, report):
        # A batch owns a saved problem/dataset/source snapshot, even if the draft is edited later.
        runs = [dict(solution_id=s['id'], name=s['name'], language=s['language'], tag=s['tag'],
                     source_sha256=hashlib.sha256(s['content'].encode()).hexdigest(),
                     expected_verdict=EXPECTED_VERDICTS[s['tag']], state='queued', cases=[])
                for s in solutions]
        report(f'本次运行 {len(runs)} 份解法', 0, runs=runs)
        for index, item in enumerate(solutions):
            current = runs[index]
            current['state'] = 'running'

            def progress(line, value=None, **values):
                current.update(values)
                overall = (index * 100 + (value if value is not None else current.get('progress', 0))) / len(runs)
                if value is not None:
                    current['progress'] = value
                report(f'{item["name"]} · {line}', int(overall), runs=runs)

            result = self.judge(p, dict(solution=item, receiver=item.get('receiver')), progress)
            verdicts = {c['verdict'] for c in result['cases']} or {result['verdict']}
            expected = current['expected_verdict']
            matched = (verdicts == {'AC'} if expected == 'AC' else
                       bool(verdicts & ({'WA', 'PE'} if expected == 'WA' else {expected})))
            current.update(result, state='done', progress=100,
                           matches_expected=matched and 'IE' not in verdicts)
            report(f'{item["name"]} · {"符合预期" if current["matches_expected"] else "不符合预期"}',
                   int((index + 1) * 100 / len(runs)), runs=runs)
        matched_count = sum(r['matches_expected'] for r in runs)
        report(f'{matched_count} / {len(runs)} 份解法符合预期', 100, runs=runs,
               verdict='MATCH' if matched_count == len(runs) else 'MISMATCH', matched_count=matched_count)

    def case_path(self, p, case_id, suffix):
        if not p['dataset'] or case_id not in {x['id'] for x in p['dataset']['cases']}:
            raise ProblemError('测试点不存在', 404)
        return self.root / p['dataset']['id'] / (case_id + '.' + suffix)
