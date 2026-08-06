#!/usr/bin/env python3
"""Tag-registry check (plan D5).

Every tag used in content frontmatter must exist in data/tags.yaml, and every
registry entry must carry a name and a one-line charter. Also validates the
status field against the allowed vocabulary (plan D1).

Usage: check_tags.py [repo-root]   (defaults to this script's parent's parent)
Exit 1 on violations.
"""
import sys
from pathlib import Path

import yaml

VALID_STATUS = {"draft", "prelim", "current"}


def frontmatter(md: Path) -> dict:
    text = md.read_text()
    if not text.startswith("---"):
        return {}
    try:
        _, fm, _ = text.split("---", 2)
    except ValueError:
        return {}
    return yaml.safe_load(fm) or {}


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    registry_file = root / "data" / "tags.yaml"
    registry = yaml.safe_load(registry_file.read_text()) or {}

    errors = []
    for slug, entry in registry.items():
        if not isinstance(entry, dict) or not entry.get("name") or not entry.get("charter"):
            errors.append(f"registry: tag {slug!r} must have a name and a charter")

    for md in sorted((root / "content").rglob("*.md")):
        fm = frontmatter(md)
        rel = md.relative_to(root)
        for tag in fm.get("tags") or []:
            if tag not in registry:
                errors.append(f"{rel}: unregistered tag {tag!r} — add it to data/tags.yaml with a charter")
        status = fm.get("status")
        if status is not None and status not in VALID_STATUS:
            errors.append(f"{rel}: invalid status {status!r} (allowed: {sorted(VALID_STATUS)})")

        # `status` is our vocabulary; `draft` is Hugo's. Only `draft: true` actually
        # withholds a page from a production build, so a status:draft ref would
        # otherwise ship. Plan D1 says drafts live in the repo unshipped — enforce it.
        if status == "draft" and fm.get("draft") is not True:
            errors.append(
                f"{rel}: status: draft requires `draft: true` as well, or the page "
                f"ships in a production build"
            )

    if errors:
        print(f"TAG CHECK FAILED ({len(errors)}):")
        for e in errors:
            print(f"  {e}")
        return 1
    print("check_tags: OK — all tags registered, statuses valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
