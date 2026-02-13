#!/usr/bin/env python3
"""Audit merge conflict state: unmerged paths + marker scan."""

from pathlib import Path
import subprocess
import sys

MARKERS = ("<<<<<<< ", "=======", ">>>>>>> ")


def run(cmd):
    return subprocess.check_output(cmd, text=True).strip()


def tracked_files():
    out = run(["git", "ls-files"])
    return [Path(line) for line in out.splitlines() if line]


def unmerged_files():
    out = run(["git", "diff", "--name-only", "--diff-filter=U"])
    return [line for line in out.splitlines() if line]


def is_text(path: Path) -> bool:
    try:
        return b"\x00" not in path.read_bytes()
    except OSError:
        return False


def marker_hits():
    hits = []
    for path in tracked_files():
        if not path.exists() or not is_text(path):
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for i, line in enumerate(lines, start=1):
            if line.startswith(MARKERS):
                hits.append((str(path), i, line[:40]))
    return hits


def main() -> int:
    unresolved = unmerged_files()
    markers = marker_hits()

    if unresolved:
        print("Unmerged files in index:")
        for f in unresolved:
            print(f"  {f}")
    else:
        print("No unmerged files in index.")

    if markers:
        print("Conflict markers found in tracked files:")
        for p, ln, preview in markers:
            print(f"  {p}:{ln}: {preview}")
    else:
        print("No conflict markers found in tracked files.")

    if unresolved or markers:
        print("\nResolve all above items, then re-run this script.")
        return 1

    print("\nConflict audit passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
