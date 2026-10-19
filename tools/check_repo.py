#!/usr/bin/env python3
"""Bounded source/provenance/secret-pattern checks; never connects to a service."""

import ast
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "outputs",
        "inputs", "private", "jobs", "logs", "build", "dist"}
FORBIDDEN_NAMES = {"auth.json", "authorized_keys", "known_hosts", "id_rsa", "id_ed25519"}
FORBIDDEN_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".gwbk", ".zip", ".tar", ".gz", ".bin", ".db", ".sqlite", ".jsonl"}
PATTERNS = [
    re.compile(r"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----"),
    re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{24,}"),
    re.compile(r"\bticket-[A-Za-z0-9]{32,}"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{40,}"),
    re.compile(r"\bAKIA[A-Z0-9]{16}\b"),
]


def main() -> int:
    errors = []
    checked = 0
    for path in sorted(ROOT.rglob("*")):
        relative = path.relative_to(ROOT)
        if any(part in SKIP or part.endswith(".egg-info") for part in relative.parts):
            continue
        if path.is_symlink():
            errors.append(f"Symlink requires review: {relative}")
            continue
        if not path.is_file():
            continue
        checked += 1
        if (path.name in FORBIDDEN_NAMES or path.suffix in FORBIDDEN_SUFFIXES or
                (path.name.startswith(".env") and path.name != ".env.example")):
            errors.append(f"Private/generated file type: {relative}")
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeError:
            errors.append(f"Unexpected non-text file: {relative}")
            continue
        for number, line in enumerate(text.splitlines(), 1):
            if any(pattern.search(line) for pattern in PATTERNS):
                errors.append(f"Possible credential: {relative}:{number}")
        try:
            if path.suffix == ".py":
                ast.parse(text, filename=str(relative))
            elif path.suffix == ".json":
                json.loads(text)
        except (SyntaxError, ValueError):
            errors.append(f"Invalid source syntax: {relative}")
        if path.suffix == ".md":
            for target in re.findall(r"\[[^\]\n]+\]\(([^)\n]+)\)", text):
                if target.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                target = target.split("#", 1)[0]
                if not (path.parent / target).is_file():
                    errors.append(f"Missing local link: {relative} -> {target}")
    manifest = json.loads((ROOT / "source-manifest.json").read_text())
    for entry in manifest["files"]:
        path = ROOT / entry["destination"]
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != entry["copied_sha256"]:
            errors.append(f"Imported source hash mismatch: {entry['destination']}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Checked {checked} text files: imported hashes, Python/JSON syntax, local links and credential patterns passed.")
    print("This is a bounded content check; review Git history and future inputs before publishing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
