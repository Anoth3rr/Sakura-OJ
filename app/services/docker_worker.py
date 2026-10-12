"""Container entrypoint for one isolated judge job.

The API process sends a JSON job on stdin. This module intentionally delegates
the actual compiler/runtime work to LocalCodeRunner so the host never executes
submission code directly when Docker mode is enabled.
"""

from __future__ import annotations

import json
import sys
from typing import Any

from .runner import LocalCodeRunner


def _error(message: str) -> dict[str, Any]:
    return {
        "verdict": "SYSTEM_ERROR",
        "score": 0,
        "compile_output": "",
        "error_message": message,
        "runtime_ms": None,
        "memory_kb": None,
        "results": [],
    }


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            raise ValueError("任务必须是 JSON 对象")
        required = ("submission_id", "source_code", "language", "test_cases")
        if any(key not in payload for key in required):
            raise ValueError("任务缺少必要字段")
        report = LocalCodeRunner().run(
            submission_id=str(payload["submission_id"]),
            source_code=str(payload["source_code"]),
            language=str(payload["language"]),
            test_cases=list(payload["test_cases"]),
            time_limit_ms=int(payload.get("time_limit_ms", 1_000)),
            memory_limit_mb=int(payload.get("memory_limit_mb", 256)),
        )
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        report = _error(f"容器内任务格式错误: {exc}")
    except Exception as exc:  # Keep stdout valid JSON for the host worker.
        report = _error(f"容器内判题异常: {exc}")
    sys.stdout.write(json.dumps(report, ensure_ascii=False, separators=(",", ":")))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
