#!/usr/bin/env python3
"""No-external-origins check (handoff decision 3).

Scans the built site for anything that would make a browser fetch from a
third-party origin: href/src/srcset/action attributes, CSS url() and @import.
XML namespaces (xmlns=) are identifiers, not fetches, and are not flagged.

Usage: check_origins.py <public-dir> [allowed-host ...]
Exit 1 on any finding.
"""
import re
import sys
from pathlib import Path

ALLOWED_DEFAULT = {"refs.threelakes.music"}

FETCH_ATTR = re.compile(
    r"""(?:href|src|srcset|action|poster|data)\s*=\s*["'](https?://[^"']+)""",
    re.IGNORECASE,
)
CSS_URL = re.compile(r"""url\(\s*["']?(https?://[^"')]+)""", re.IGNORECASE)
CSS_IMPORT = re.compile(r"""@import\s+["'](https?://[^"']+)""", re.IGNORECASE)

SCAN_SUFFIXES = {".html", ".css", ".js", ".svg", ".xml"}


def host_of(url: str) -> str:
    return url.split("//", 1)[1].split("/", 1)[0].split(":", 1)[0].lower()


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    public = Path(sys.argv[1])
    allowed = ALLOWED_DEFAULT | {h.lower() for h in sys.argv[2:]}
    if not public.is_dir():
        print(f"check_origins: {public} is not a directory (build first)")
        return 2

    findings = []
    for f in sorted(public.rglob("*")):
        if f.suffix.lower() not in SCAN_SUFFIXES or not f.is_file():
            continue
        text = f.read_text(errors="replace")
        for pattern in (FETCH_ATTR, CSS_URL, CSS_IMPORT):
            for m in pattern.finditer(text):
                url = m.group(1)
                if host_of(url) not in allowed:
                    findings.append((f.relative_to(public), url))

    if findings:
        print(f"EXTERNAL ORIGINS FOUND ({len(findings)}):")
        for path, url in findings:
            print(f"  {path}: {url}")
        return 1
    print("check_origins: OK — no external origins in built output")
    return 0


if __name__ == "__main__":
    sys.exit(main())
