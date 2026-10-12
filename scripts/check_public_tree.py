#!/usr/bin/env python3
"""Check staged Git blobs before publishing; never print matching secret values.

This is a preventative check, not a guarantee that arbitrary personal data can
be recognized automatically. Review the diff as well. Use --revision HEAD to
check a committed snapshot, including in CI.
"""
from __future__ import annotations

import argparse
import fnmatch
import io
from pathlib import PurePosixPath
import re
import subprocess
import sys


PRIVATE_PARTS = {
    "data", "runtime", "backups", "test-results", ".venv", "venv", "__pycache__",
    ".pytest_cache", "node_modules", ".ssh", ".aws", ".vscode", ".idea",
}
PRIVATE_NAMES = (
    ".env", ".env.*", "*.env", "*.env.*", "*.local", "*.local.*", "*.sqlite*",
    "*.db", "*.db-*", "*.log", "*.dump", "*.pem", "*.key", "*.p12", "*.pfx",
    "*.keystore", "id_rsa*", "id_ed25519*", "*.pyc", "*.gch", "*.class",
    "*.o", "*.obj", "*.a", "*.so", "*.dll", "*.exe", "*.zip", "*.7z",
    "*.tar", "*.tar.gz", "*.tgz", "*.bak", "verification.json",
)
RULES = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY-----"),
    "GitHub token": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{25,})"),
    "cloud key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "API token": re.compile(r"\bsk-(?:proj-|ant-)?[A-Za-z0-9_-]{25,}"),
    "credential in URL": re.compile(r"[a-zA-Z][\w+.-]*://[^\s/:@]+:[^\s/@]+@"),
    "personal Windows path": re.compile(r"(?i)\b[a-z]:[\\/](?:Users|WorkSpace|Documents and Settings)[\\/]"),
    "personal WSL path": re.compile(r"(?i)/mnt/[a-z]/(?:Users|WorkSpace)/"),
    "old host path": re.compile(r"/home/" + r"web/"),
    "private network address": re.compile(
        r"(?<![\d.])(?:10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|"
        r"172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2})(?![\d.])"
    ),
}
BINARY_SUFFIXES = {".woff", ".woff2", ".ttf", ".png", ".jpg", ".jpeg", ".gif", ".ico"}


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], stderr=subprocess.PIPE)


def entries(revision: str | None) -> list[tuple[str, str, str]]:
    if revision:
        commit = git("rev-parse", "--verify", "--end-of-options", revision + "^{commit}").decode().strip()
        records = git("ls-tree", "-r", "-z", commit).split(b"\0")
    else:
        records = git("ls-files", "--stage", "-z").split(b"\0")
    result = []
    for record in records:
        if not record:
            continue
        metadata, filename = record.split(b"\t", 1)
        mode, second, third = metadata.decode("ascii").split()
        if not revision and third != "0":
            raise ValueError("Resolve merge conflicts before checking the public tree.")
        oid = third if revision else second
        result.append((filename.decode("utf-8"), mode, oid))
    return result


def check_blob(name: str, mode: str, blob: bytes) -> list[str]:
    path = PurePosixPath(name)
    parts = {part.lower() for part in path.parts}
    # A legacy language is named 'data'; it is source configuration, not a dump.
    if name.startswith("judge/newjudge/ljudge/etc/ljudge/data/"):
        parts.discard("data")
    issues = []
    if parts & PRIVATE_PARTS or any(part.startswith("results-") for part in parts):
        issues.append("private or generated directory")
    if name != ".env.example" and any(fnmatch.fnmatchcase(path.name.lower(), pattern) for pattern in PRIVATE_NAMES):
        issues.append("private or generated filename")
    if mode not in {"100644", "100755"}:
        issues.append("non-regular file; review separately")
    if blob.startswith((b"SQLite format 3", b"\x7fELF", b"MZ", b"PK\x03\x04", b"\x1f\x8b")):
        issues.append("database, executable or archive content")
    try:
        content = blob.decode("utf-8-sig")
    except UnicodeDecodeError:
        if path.suffix.lower() not in BINARY_SUFFIXES:
            issues.append("unreviewed binary content")
        return issues
    for label, pattern in RULES.items():
        for match in pattern.finditer(content):
            line = content.count("\n", 0, match.start()) + 1
            issues.append(f"line {line}: {label}")
    if name == ".env.example":
        for line in content.splitlines():
            if re.match(r"\s*OJ_ADMIN_PASSWORD\s*=\s*\S", line):
                issues.append("example contains a bootstrap password")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", help="Check a committed revision instead of the staging area.")
    args = parser.parse_args()
    try:
        selected = entries(args.revision)
        if not selected:
            raise ValueError("No files selected. Stage source files with git add first.")
        blobs = subprocess.check_output(
            ["git", "cat-file", "--batch"],
            input="".join(oid + "\n" for _, _, oid in selected).encode("ascii"),
            stderr=subprocess.PIPE,
        )
        stream = io.BytesIO(blobs)
        failures = 0
        for name, mode, oid in selected:
            header = stream.readline().split()
            if len(header) != 3 or header[1] != b"blob":
                raise ValueError("An entry is not a readable blob.")
            blob = stream.read(int(header[2]))
            if stream.read(1) != b"\n":
                raise ValueError("Invalid Git object response.")
            for issue in check_blob(name, mode, blob):
                print(f"{name}: {issue}")
                failures += 1
        if failures:
            print(f"Public-tree check failed: {failures} finding(s). Matched values were not printed.")
            return 1
        print(f"Public-tree check passed: {len(selected)} Git blobs inspected.")
        return 0
    except (OSError, subprocess.CalledProcessError, ValueError) as exc:
        # Git stderr may contain local paths or authentication context.
        print(f"Unable to check public tree ({type(exc).__name__}).", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
