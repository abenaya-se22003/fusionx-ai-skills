#!/usr/bin/env python3
"""Sync canonical shared skill guidance into each installable skill."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "shared" / "browser-session.md"
TARGETS = [
    ROOT / "skills" / "functional-testing" / "references" / "browser-session.md",
    ROOT / "skills" / "user-manual-update" / "references" / "browser-session.md",
]


def main() -> int:
    check_only = "--check" in sys.argv
    source = SOURCE.read_text(encoding="utf-8")
    drift = []

    for target in TARGETS:
        current = target.read_text(encoding="utf-8") if target.exists() else None
        if current != source:
            drift.append(target.relative_to(ROOT))
            if not check_only:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(source, encoding="utf-8")

    if drift and check_only:
        print("Shared browser-session contract is out of sync:")
        for path in drift:
            print(f"  - {path}")
        print("Run: python scripts/sync-shared.py")
        return 1

    if drift:
        print("Synced shared browser-session contract:")
        for path in drift:
            print(f"  - {path}")
    else:
        print("Shared browser-session contract is already in sync.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
