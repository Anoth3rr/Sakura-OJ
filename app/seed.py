from __future__ import annotations

from . import repository


def seed_demo_data() -> None:
    if repository.get_problem_by_slug("sum-two", include_hidden=True):
        return
    repository.create_problem(
        {
            "slug": "sum-two",
            "title": "两数之和",
            "description": (
                "给定两个整数 a 和 b，请计算它们的和。"
                "\n\n这是 Sakura OJ 的演示题，用来验证从提交到判题结果的完整链路。"
            ),
            "statement_markdown": (
                "给定两个整数 **a** 和 **b**，请计算它们的和。"
                "\n\n这是 Sakura OJ 的演示题，用来验证从提交到判题结果的完整链路。"
            ),
            "input_format": "一行输入两个整数 a、b，以空格分隔。\n\n数据范围：-10^9 <= a, b <= 10^9",
            "output_format": "输出 a + b 的结果，并换行。",
            "difficulty": "入门",
            "time_limit_ms": 1_000,
            "memory_limit_mb": 256,
            "test_cases": [
                {
                    "name": "样例 1",
                    "input_data": "1 2\n",
                    "expected_output": "3\n",
                    "is_sample": True,
                    "weight": 1,
                },
                {
                    "name": "样例 2",
                    "input_data": "-5 8\n",
                    "expected_output": "3\n",
                    "is_sample": True,
                    "weight": 1,
                },
                {
                    "name": "边界 1",
                    "input_data": "0 0\n",
                    "expected_output": "0\n",
                    "is_sample": False,
                    "weight": 1,
                },
                {
                    "name": "边界 2",
                    "input_data": "1000000000 -1000000000\n",
                    "expected_output": "0\n",
                    "is_sample": False,
                    "weight": 1,
                },
                {
                    "name": "随机 1",
                    "input_data": "123456 789012\n",
                    "expected_output": "912468\n",
                    "is_sample": False,
                    "weight": 1,
                },
            ],
        }
    )

    repository.create_problem(
        {
            "slug": "max-of-three",
            "title": "三个数的最大值",
            "description": "输入三个整数，输出其中的最大值。",
            "statement_markdown": "输入三个整数，输出其中的 **最大值**。",
            "input_format": "一行输入三个整数 x、y、z，以空格分隔。\n\n数据范围：-10^9 <= x, y, z <= 10^9",
            "output_format": "输出三个数中的最大值，并换行。",
            "difficulty": "入门",
            "time_limit_ms": 1_000,
            "memory_limit_mb": 256,
            "test_cases": [
                {
                    "name": "样例 1",
                    "input_data": "4 9 2\n",
                    "expected_output": "9\n",
                    "is_sample": True,
                    "weight": 1,
                },
                {
                    "name": "样例 2",
                    "input_data": "-3 -1 -8\n",
                    "expected_output": "-1\n",
                    "is_sample": True,
                    "weight": 1,
                },
                {
                    "name": "重复值",
                    "input_data": "7 7 1\n",
                    "expected_output": "7\n",
                    "is_sample": False,
                    "weight": 1,
                },
            ],
        }
    )
