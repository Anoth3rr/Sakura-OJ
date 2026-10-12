from __future__ import annotations

import io
import time
import zipfile

from app import repository


def wait_for_completion(client, submission_id: str, timeout: float = 15.0) -> dict:
    deadline = time.time() + timeout
    latest = {}
    while time.time() < deadline:
        latest = client.get(f"/api/submissions/{submission_id}").json()
        if latest.get("status") == "COMPLETED":
            return latest
        time.sleep(0.15)
    raise AssertionError(f"submission did not complete: {latest}")


def test_health_and_seeded_problems(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    response = client.get("/api/problems")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] >= 2
    assert {item["slug"] for item in payload["items"]} >= {"sum-two", "max-of-three"}


def test_get_problem_only_exposes_samples(client):
    response = client.get("/api/problems/sum-two")
    assert response.status_code == 200
    problem = response.json()
    assert len(problem["test_cases"]) == 2
    assert all("expected_output" in case for case in problem["test_cases"])
    assert problem["statement_html"]
    assert "constraints" not in problem
    assert "数据范围" in problem["input_format"]
    assert "数据范围" in problem["input_format_html"]
    assert problem["output_format_html"]


def test_correct_submission_reaches_accepted(client):
    response = client.post(
        "/api/submissions",
        json={
            "problem_slug": "sum-two",
            "language": "cpp17",
            "source_code": (
                "#include <bits/stdc++.h>\n"
                "using namespace std;\n"
                "int main(){long long a,b;cin>>a>>b;cout<<a+b<<'\\n';}\n"
            ),
        },
    )
    assert response.status_code == 202
    submission = wait_for_completion(client, response.json()["id"])
    assert submission["verdict"] == "ACCEPTED"
    assert submission["score"] == 100
    assert len(submission["results"]) == 5


def test_compile_error_is_reported(client):
    response = client.post(
        "/api/submissions",
        json={
            "problem_slug": "sum-two",
            "language": "cpp17",
            "source_code": "int main( {",
        },
    )
    assert response.status_code == 202
    submission = wait_for_completion(client, response.json()["id"])
    assert submission["verdict"] == "COMPILE_ERROR"
    assert submission["compile_output"]


def test_source_size_limit(client):
    response = client.post(
        "/api/submissions",
        json={
            "problem_slug": "sum-two",
            "language": "cpp17",
            "source_code": "x" * 100_001,
        },
    )
    assert response.status_code == 413


def _archive() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("sample-01.in", "2 3\n")
        archive.writestr("sample-01.out", "5\n")
        archive.writestr("hidden-01.in", "100 23\n")
        archive.writestr("hidden-01.out", "123\n")
    return buffer.getvalue()


def test_create_problem_with_markdown(client):
    response = client.post(
        "/api/problems",
        json={
            "slug": "markdown-problem",
            "title": "Markdown 题面",
            "statement_markdown": "# 计算\n\n输出 **结果**。\n\n<script>alert(1)</script>",
            "input_format": "输入两个整数。",
            "output_format": "输出它们的和。",
            "constraints": "整数范围不超过 1000。",
            "difficulty": "进阶",
            "time_limit_ms": 1200,
            "memory_limit_mb": 128,
            "test_cases": [
                {"name": "sample-01", "input_data": "2 3\n", "expected_output": "5\n", "is_sample": True},
                {"name": "hidden-01", "input_data": "100 23\n", "expected_output": "123\n"},
            ],
        },
    )
    assert response.status_code == 201
    problem = response.json()
    assert problem["slug"] == "markdown-problem"
    assert "<h1>计算</h1>" in problem["statement_html"]
    assert "<script>" not in problem["statement_html"]
    assert len(problem["test_cases"]) == 1
    assert problem["test_cases"][0]["name"] == "sample-01"


def test_zip_import_endpoints_are_removed(client):
    paths = client.get("/openapi.json").json()["paths"]
    assert "/api/problems/record" not in paths
    assert "/api/problems/{slug}/testcases/upload" not in paths
    before = client.get("/api/problems").json()
    problem = client.get("/api/problems/sum-two").json()
    cases = repository.get_test_cases(problem["id"])

    response = client.post(
        "/api/problems/record",
        data={
            "slug": "zip-record",
            "title": "已移除的 ZIP 录题",
            "statement_markdown": "输出两数之和。",
            "input_format": "两个整数。",
            "output_format": "它们的和。",
        },
        files={"data_file": ("cases.zip", _archive(), "application/zip")},
    )
    assert response.status_code == 405
    assert client.get("/api/problems/zip-record").status_code == 404
    assert client.get("/api/problems").json() == before

    response = client.post(
        "/api/problems/sum-two/testcases/upload",
        files={"data_file": ("replacement.zip", _archive(), "application/zip")},
    )
    assert response.status_code == 404
    assert repository.get_test_cases(problem["id"]) == cases


def test_language_catalog_exposes_requested_languages(client):
    response = client.get("/api/languages")
    assert response.status_code == 200
    languages = {item["id"]: item for item in response.json()}
    assert {"c", "cpp", "pypy", "java"} <= languages.keys()
