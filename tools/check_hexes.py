#!/usr/bin/env python3
"""No-literal-color check (3L-design DECISIONS #9).

The design system's hardest constraint: `tokens.css` is the ONLY file permitted to
state a hex. Everything else derives from those tokens via var() and color-mix(),
so correcting a provisional stick hex re-derives the whole system. A literal
colour anywhere else silently opts out of that.

Scans CSS sources and templates. The vendored tokens.css is the sole exemption.

Usage: check_hexes.py [repo-root]
Exit 1 on any finding.
"""
import re
import sys
from pathlib import Path

EXEMPT = {"assets/css/ds/tokens.css"}

# #abc / #aabbcc / #aabbccdd, plus the functional colour notations that would
# equally bypass the token layer.
HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")
FUNC = re.compile(r"\b(?:rgba?|hsla?|hwb|lab|lch|oklch)\s*\(", re.IGNORECASE)

SCAN = ("assets/**/*.css", "layouts/**/*.html", "static/**/*.css")


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    findings = []

    for pattern in SCAN:
        for f in sorted(root.glob(pattern)):
            rel = f.relative_to(root).as_posix()
            if rel in EXEMPT:
                continue
            text = f.read_text(errors="replace")
            # Comments may legitimately quote a hex while explaining a decision.
            text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
            text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
            for m in HEX.finditer(text):
                line = text[: m.start()].count("\n") + 1
                findings.append((rel, line, m.group(0)))
            for m in FUNC.finditer(text):
                line = text[: m.start()].count("\n") + 1
                findings.append((rel, line, m.group(0) + "…)"))

    if findings:
        print(f"LITERAL COLOR FOUND ({len(findings)}) — only ds/tokens.css may state one:")
        for rel, line, tok in findings:
            print(f"  {rel}:{line}: {tok}")
        print("  Use var(--role) or color-mix() on stick tokens instead.")
        return 1
    print("check_hexes: OK — no literal color outside ds/tokens.css")
    return 0


if __name__ == "__main__":
    sys.exit(main())
