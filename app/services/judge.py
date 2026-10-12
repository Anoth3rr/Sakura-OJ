from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import logging

from .. import repository
from ..config import Settings, settings
from ..db import connection
from .runner import CodeRunner, DockerCodeRunner, build_runner


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class JudgeService:
    def __init__(
        self,
        runner: CodeRunner | DockerCodeRunner | None = None,
        runner_settings: Settings = settings,
    ):
        self.runner = runner or build_runner(runner_settings)
        self.executor = ThreadPoolExecutor(
            max_workers=runner_settings.worker_count,
            thread_name_prefix="sakura-judge",
        )

    def enqueue(self, submission_id: str) -> None:
        self.executor.submit(self._judge, submission_id)

    def _judge(self, submission_id: str) -> None:
        submission = repository.get_submission(submission_id)
        if submission is None:
            return
        started_at = _now()
        repository.update_submission(
            submission_id,
            status="COMPILING",
            verdict="PENDING",
            started_at=started_at,
            error_message="",
        )
        try:
            problem = repository.get_problem_by_id(int(submission["problem_id"]), include_hidden=True)
            if problem is None:
                raise RuntimeError("题目不存在")
            test_cases = repository.get_test_cases(int(problem["id"]))
            snapshot = json.loads(submission.get('judge_snapshot') or '{}')
            if snapshot:
                problem.update(snapshot)
                ids = snapshot['case_ids']
                with connection() as db:
                    test_cases = [dict(row) for row in db.execute(
                        'SELECT * FROM test_cases WHERE problem_id=? AND id IN (' + ','.join('?' for _ in ids) + ') ORDER BY order_index,id',
                        [problem['id'], *ids])] if ids else []
            repository.update_submission(submission_id, status="RUNNING")
            config = json.loads(problem.get('judge_config') or '{}')
            run = self.runner.run
            extra = {}
            if hasattr(self.runner, 'run_problem'):
                run = self.runner.run_problem
                extra['config'] = config
            elif config or problem.get('judge_mode', 'normal') != 'normal':
                raise RuntimeError('testlib 题目需要 OJ_JUDGE_MODE=newjudge')
            report = run(
                submission_id=submission_id,
                source_code=submission["source_code"],
                language=submission["language"],
                test_cases=test_cases,
                time_limit_ms=int(problem["time_limit_ms"]),
                memory_limit_mb=int(problem["memory_limit_mb"]),
                **extra,
            )
            repository.replace_submission_results(submission_id, report["results"])
            repository.update_submission(
                submission_id,
                status="COMPLETED",
                verdict=report["verdict"],
                score=report["score"],
                compile_output=report["compile_output"],
                error_message=report["error_message"],
                runtime_ms=report["runtime_ms"],
                memory_kb=report["memory_kb"],
                finished_at=_now(),
            )
        except Exception as exc:
            repository.update_submission(
                submission_id,
                status="COMPLETED",
                verdict="SYSTEM_ERROR",
                score=0,
                error_message=f"判题服务异常: {exc}",
                finished_at=_now(),
            )
        finally:
            try:
                from ..team.integration import sync_submission
                sync_submission(submission_id)
            except Exception:
                logging.exception('Unable to sync OJ submission into team analytics')

    def shutdown(self) -> None:
        self.executor.shutdown(wait=True)
