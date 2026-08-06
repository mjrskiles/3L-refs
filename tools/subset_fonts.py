#!/usr/bin/env python3
"""Subset self-hosted IBM Plex (OFL) into static/fonts/ (handoff decision 3).

Downloads pinned per-family releases from github.com/IBM/plex, extracts the
needed TTFs, subsets them to the glyph ranges the site actually uses, and emits
woff2. Run rarely (make fonts); outputs are committed.
"""
import io
import sys
import tempfile
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

from fontTools.subset import main as pyftsubset

# family release tag -> TTFs to pull out of its zip
PINNED = {
    "@ibm/plex-sans@1.1.0": ["IBMPlexSans-Regular.ttf", "IBMPlexSans-SemiBold.ttf"],
    "@ibm/plex-sans-condensed@2.0.0": [
        "IBMPlexSansCondensed-SemiBold.ttf",
        "IBMPlexSansCondensed-Bold.ttf",
    ],
    "@ibm/plex-mono@2.5.0": ["IBMPlexMono-Regular.ttf", "IBMPlexMono-SemiBold.ttf"],
    "@ibm/plex-serif@2.0.0": ["IBMPlexSerif-Italic.ttf"],
}

# Latin + Latin ext, Greek (φ θ ψ π), punctuation, sub/superscripts (₀₂₃),
# arrows (→ ⇒ ↑), math operators (≤ √ ∞ −), geometric shapes (▸), dingbats (✗)
UNICODES = "U+0000-024F,U+0370-03FF,U+2000-206F,U+2070-209F,U+2190-21FF,U+2200-22FF,U+25A0-25FF,U+2700-27BF"

# No --layout-features override: IBM Plex has no `tnum` feature because its
# default figures are already tabular (every digit is 600 units). Asking for
# tnum would retain a feature that does not exist. If a future family needs an
# opt-in feature, add it with '+=' — a plain '=' REPLACES the default set and
# would silently drop kerning and ligatures.

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "static" / "fonts"


def zip_url(tag: str) -> str:
    # tag "@ibm/plex-sans@1.1.0" -> asset "ibm-plex-sans.zip"
    asset = "ibm-plex-" + tag.split("plex-")[1].split("@")[0] + ".zip"
    return (
        "https://github.com/IBM/plex/releases/download/"
        + urllib.parse.quote(tag, safe="")
        + "/"
        + asset
    )


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    force = "--force" in sys.argv

    wanted = [t for ttfs in PINNED.values() for t in ttfs]
    existing = {p.name for p in OUT.glob("*.woff2")}
    if not force and all(t.replace(".ttf", ".woff2") in existing for t in wanted):
        print("subset_fonts: all outputs present (use --force to regenerate)")
        return 0

    for tag, ttfs in PINNED.items():
        url = zip_url(tag)
        print(f"fetching {tag} ...")
        with urllib.request.urlopen(url) as resp:
            zf = zipfile.ZipFile(io.BytesIO(resp.read()))
        names = zf.namelist()
        for ttf in ttfs:
            match = [n for n in names if n.endswith("/" + ttf) or n == ttf]
            if not match:
                print(f"  ERROR: {ttf} not found in {tag} zip", file=sys.stderr)
                return 1
            # Stage the TTF in a temp dir, never in static/fonts/ — a failure
            # mid-subset would otherwise leave a stray 200KB TTF in shipped output.
            with tempfile.TemporaryDirectory() as tmp:
                src = Path(tmp) / ttf
                src.write_bytes(zf.read(match[0]))
                dest = OUT / ttf.replace(".ttf", ".woff2")
                pyftsubset(
                    [
                        str(src),
                        f"--unicodes={UNICODES}",
                        "--flavor=woff2",
                        "--no-hinting",
                        "--desubroutinize",
                        f"--output-file={dest}",
                    ]
                )
            print(f"  {dest.relative_to(ROOT)}  {dest.stat().st_size // 1024} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
