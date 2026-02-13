#!/usr/bin/env python3
"""Fail if unresolved git merge conflict markers exist in tracked text files."""

from pathlib import Path
import subprocess
import sys

MARKERS = ("<<<<<<< ", "=======", ">>>>>>> ")


def tracked_files():
    out = subprocess.check_output(["git", "ls-files"], text=True)
    return [Path(line.strip()) for line in out.splitlines() if line.strip()]


def is_probably_text(path: Path) -> bool:
    try:
        data = path.read_bytes()
    except OSError:
        return False
    return b"\x00" not in data


def main() -> int:
    offenders = []
    for path in tracked_files():
        if not path.exists() or not is_probably_text(path):
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for idx, line in enumerate(lines, start=1):
            if line.startswith(MARKERS):
                offenders.append((str(path), idx, line[:40]))

    if offenders:
        print("Unresolved merge markers detected:")
        for p, ln, preview in offenders:
            print(f"  {p}:{ln}: {preview}")
        return 1

    print("No unresolved merge markers found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
