#!/usr/bin/env python3
"""Contrast check over the design system's role map (brief §8, plan D17).

Promised since P0 and never written. Resolves the role map for real — following
var() indirection and evaluating color-mix(in oklab, …) the way a browser does —
then measures WCAG contrast against each theme's own ground.

Floors are the design system's (AA), per D17:
  prose / body / links     >= 4.5:1
  large text and headings  >= 3:1
  non-text UI (focus)      >= 3:1   [reported, not enforced — see below]

The focus ring currently measures 2.35:1 on the light ground, which fails SC
1.4.11. Fixing it means changing a tuned design-system colour, which is Michael's
call, so it is reported as a warning rather than failing the build. Everything
else is enforced.

Usage: check_contrast.py [repo-root]
Exit 1 if an enforced floor is breached.
"""
import math
import re
import sys
from pathlib import Path

DS = "assets/css/ds"

# role -> (floor, enforced). Ground for every one of these is --surface.
FLOORS = {
    "ink": (4.5, True),
    "ink-muted": (4.5, True),
    "heading": (3.0, True),      # display sizes only; site.css never uses it small
    "link": (4.5, True),
    # SC 1.4.11. Fixed upstream as 3L-design decision 17 (turquoise 70% into Paynes,
    # 3.47:1). FLIP THIS TO True in the same change that re-vendors that commit —
    # until then the vendored roles.css still carries the raw stick at 2.35:1.
    "focus": (3.0, False),
}


def strip_comments(css: str) -> str:
    return re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)


def srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


# The role map mixes toward plain `white` for the light ground; keep the few CSS
# named colours the system actually uses rather than pulling in a colour library.
NAMED = {"white": "#ffffff", "black": "#000000", "gray": "#808080", "grey": "#808080"}


def parse_hex(h: str):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    return tuple(srgb_to_linear(int(h[i : i + 2], 16) / 255) for i in (0, 2, 4))


def lin_to_oklab(rgb):
    r, g, b = rgb
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = (math.copysign(abs(x) ** (1 / 3), x) for x in (l, m, s))
    return (
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    )


def oklab_to_lin(lab):
    L, a, b = lab
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_**3, m_**3, s_**3
    return (
        4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    )


def split_top(s: str, sep: str = ","):
    """Split on `sep` at paren depth zero."""
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == sep and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    out.append(cur)
    return [p.strip() for p in out]


def resolve(expr: str, env: dict):
    """Evaluate a CSS colour expression to linear sRGB, or None if not a colour."""
    expr = expr.strip()
    if expr.lower() in NAMED:
        return parse_hex(NAMED[expr.lower()])
    if expr.startswith("#"):
        return parse_hex(expr)
    m = re.fullmatch(r"var\(\s*(--[\w-]+)\s*\)", expr)
    if m:
        return resolve(env[m.group(1)], env) if m.group(1) in env else None
    m = re.fullmatch(r"color-mix\((.*)\)", expr, re.DOTALL)
    if m:
        parts = split_top(m.group(1))
        if len(parts) != 3 or "oklab" not in parts[0]:
            return None
        def side(p):
            pm = re.search(r"(\d+(?:\.\d+)?)%\s*$", p)
            pct = float(pm.group(1)) if pm else None
            return p[: pm.start()].strip() if pm else p.strip(), pct
        ca, pa = side(parts[1])
        cb, pb = side(parts[2])
        if "transparent" in (ca, cb):
            return None  # alpha mix; not a contrast question
        ra, rb = resolve(ca, env), resolve(cb, env)
        if ra is None or rb is None:
            return None
        t = (pa if pa is not None else (100 - pb if pb is not None else 50)) / 100
        A, B = lin_to_oklab(ra), lin_to_oklab(rb)
        return oklab_to_lin(tuple(A[i] * t + B[i] * (1 - t) for i in range(3)))
    return None


def luminance(lin):
    r, g, b = (max(0.0, min(1.0, c)) for c in lin)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg, bg):
    a, b = luminance(fg), luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def decls(block: str) -> dict:
    out = {}
    for line in block.split(";"):
        if ":" in line:
            k, v = line.split(":", 1)
            k = k.strip()
            if k.startswith("--"):
                out[k] = v.strip()
    return out


def block_for(css: str, selector: str) -> str:
    m = re.search(re.escape(selector) + r"\s*\{", css)
    if not m:
        sys.exit(f"check_contrast: no `{selector}` block in ds/roles.css")
    depth, i = 1, m.end()
    while i < len(css) and depth:
        depth += {"{": 1, "}": -1}.get(css[i], 0)
        i += 1
    return css[m.end() : i - 1]


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    tokens = strip_comments((root / DS / "tokens.css").read_text())
    roles = strip_comments((root / DS / "roles.css").read_text())

    base = decls(block_for(tokens, ":root"))
    themes = {
        "light": decls(block_for(roles, ".theme-light")),
        "dark": decls(block_for(roles, ".theme-dark")),
    }

    failures, warnings, rows = [], [], []
    for theme, block in themes.items():
        env = {**base, **block}
        ground = resolve(env["--surface"], env)
        if ground is None:
            sys.exit(f"check_contrast: could not resolve --surface for {theme}")
        for role, (floor, enforced) in FLOORS.items():
            val = env.get(f"--{role}")
            if val is None:
                continue
            col = resolve(val, env)
            if col is None:
                continue
            ratio = contrast(col, ground)
            ok = ratio >= floor
            rows.append((theme, role, ratio, floor, ok, enforced))
            if not ok:
                (failures if enforced else warnings).append(
                    f"{theme}/{role}: {ratio:.2f}:1 < {floor}:1"
                )

    width = max(len(r[1]) for r in rows)
    for theme in ("light", "dark"):
        print(f"  [{theme}]")
        for t, role, ratio, floor, ok, enforced in rows:
            if t != theme:
                continue
            mark = "ok " if ok else ("FAIL" if enforced else "warn")
            print(f"    {mark} {role:<{width}} {ratio:6.2f}:1  floor {floor}")

    for w in warnings:
        print(f"  WARNING (not enforced): {w}")
    if failures:
        print(f"CONTRAST CHECK FAILED ({len(failures)}):")
        for f in failures:
            print(f"  {f}")
        return 1
    print("check_contrast: OK — all enforced floors met in both themes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
