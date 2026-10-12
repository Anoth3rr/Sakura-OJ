"""Public release checks must inspect the staged snapshot and redact findings."""
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from scripts.check_public_tree import check_blob


@pytest.mark.parametrize("name,content", [
    ("data/oj.sqlite3", b"empty"),
    ("data/backups/users.json", b"{}"),
    (".env.production", b"CONFIG=value"),
    ("private/server.key", b"key material"),
    ("innocent.txt", b"SQLite format 3\x00"),
    ("innocent.txt", b"\x7fELF"),
    (".env.example", b"OJ_ADMIN_PASSWORD=test-only-value"),
])
def test_rejects_private_paths_and_disguised_artifacts(name, content):
    assert check_blob(name, "100644", content)


def test_allows_empty_environment_template_and_copyright():
    assert not check_blob(".env.example", "100644", b"OJ_ADMIN_PASSWORD=\n")
    assert not check_blob("vendor/LICENSE", "100644", b"Copyright Example <author@example.org>")


@pytest.mark.skipif(not shutil.which("git"), reason="requires git")
def test_checks_staged_bytes_even_after_worktree_is_cleaned(tmp_path):
    script = Path(__file__).resolve().parents[1] / "scripts/check_public_tree.py"
    subprocess.run(["git", "init", "--quiet"], cwd=tmp_path, check=True)
    # A synthetic token, built at runtime so the fixture itself is publishable.
    token = "gh" + "p_" + "x" * 36
    candidate = tmp_path / "sample.txt"
    candidate.write_text(token, encoding="utf-8")
    subprocess.run(["git", "add", "sample.txt"], cwd=tmp_path, check=True)
    candidate.write_text("public source", encoding="utf-8")
    result = subprocess.run([sys.executable, str(script)], cwd=tmp_path, text=True, capture_output=True)
    assert result.returncode == 1
    assert "GitHub token" in result.stdout
    assert token not in result.stdout + result.stderr
    subprocess.run(["git", "add", "sample.txt"], cwd=tmp_path, check=True)
    result = subprocess.run([sys.executable, str(script)], cwd=tmp_path, text=True, capture_output=True)
    assert result.returncode == 0, result.stdout + result.stderr
