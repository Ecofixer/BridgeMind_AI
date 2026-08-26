#!/usr/bin/env python3
"""Fail CI when tracked text files contain common credential patterns."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


MAX_FILE_SIZE = 5 * 1024 * 1024
SKIPPED_PATHS = {
    Path("scripts/scan_secrets.py"),
}
SKIPPED_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip",
    ".gz", ".tar", ".pyc", ".sqlite", ".sqlite3",
}

# Patterns are assembled so this source file does not flag itself.
PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "private key",
        re.compile("-----BEGIN " + r"(?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"),
    ),
    (
        "GitHub token",
        re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}\b|\bgithub_pat_[A-Za-z0-9_]{40,}\b"),
    ),
    (
        "OpenAI-style key",
        re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    ),
    (
        "AWS access key",
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    ),
)

# Only uppercase environment-style assignments are considered here. Python fields such as
# `openai_api_key: str | None` or local variables must not be treated as embedded secrets.
ASSIGNMENT = re.compile(
    r"(?m)^\s*([A-Z][A-Z0-9_]*(?:SECRET|TOKEN|PASSWORD|PRIVATE_KEY|API_KEY)[A-Z0-9_]*)"
    r"\s*=\s*['\"]?([^'\"#\r\n]*)"
)
PLACEHOLDERS = {
    "",
    "changeme",
    "change-me",
    "example",
    "placeholder",
    "test",
    "your-key-here",
    "your_key_here",
}


def tracked_files() -> list[Path]:
    output = subprocess.check_output(["git", "ls-files", "-z"])
    return [Path(raw.decode("utf-8")) for raw in output.split(b"\0") if raw]


def read_text(path: Path) -> str | None:
    if path in SKIPPED_PATHS or path.suffix.lower() in SKIPPED_SUFFIXES:
        return None
    try:
        if path.stat().st_size > MAX_FILE_SIZE:
            return None
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def scan(path: Path, text: str) -> list[str]:
    findings: list[str] = []
    for label, pattern in PATTERNS:
        if pattern.search(text):
            findings.append(label)

    for match in ASSIGNMENT.finditer(text):
        value = match.group(2).strip()
        normalized = value.lower()
        if normalized in PLACEHOLDERS:
            continue
        if value.startswith("${{") or value.startswith("${"):
            continue
        findings.append(f"non-empty sensitive assignment: {match.group(1)}")

    return sorted(set(findings))


def main() -> int:
    failures: list[tuple[Path, list[str]]] = []
    for path in tracked_files():
        text = read_text(path)
        if text is None:
            continue
        findings = scan(path, text)
        if findings:
            failures.append((path, findings))

    if not failures:
        print("Tracked-file secret scan passed.")
        return 0

    print("Potential secrets detected in tracked files:")
    for path, findings in failures:
        print(f"- {path}: {', '.join(findings)}")
    print("Remove the value, rotate the credential if real, and use GitHub secrets instead.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
