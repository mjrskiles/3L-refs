#!/usr/bin/env python3
"""
Logarithmic-spiral drawing templates + carving-field layouts, for 8.5x11 print.
Produces a print-ready PDF (true scale) and a static-SVG HTML preview.
All geometry in inches; the SVG viewBox is 8.5 x 11 so 1 user unit = 1 inch.
"""
import math

PHI = (1 + 5 ** 0.5) / 2
INK, GRAY, LIGHT, ACCENT = "#111111", "#8a8a8a", "#c4c4c4", "#1B4B8F"
MONO = "IBM Plex Mono, ui-monospace, Menlo, Consolas, monospace"

# ---------- spiral math ----------
def b_of(k): return math.log(k) / (math.pi / 2)

def raw_spiral(k, decay=100.0, dth=0.02):
    b = b_of(k); th = 0.0; tmax = math.log(decay) / b; pts = []
    while th <= tmax:
        r = math.exp(-b * th)
        pts.append((r * math.cos(th), r * math.sin(th)))
        th += dth
    return pts

def bbox(pts):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)

# ---------- svg helpers (strings) ----------
def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def line(x1, y1, x2, y2, stroke=INK, w=1.0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.4f}" y1="{y1:.4f}" x2="{x2:.4f}" y2="{y2:.4f}" '
            f'stroke="{stroke}" stroke-width="{w}" stroke-linecap="round"{d}/>')

def circle(cx, cy, r, fill="none", stroke=None, w=1.0):
    s = f' stroke="{stroke}" stroke-width="{w}"' if stroke else ""
    return f'<circle cx="{cx:.4f}" cy="{cy:.4f}" r="{r}" fill="{fill}"{s}/>'

def rect(x, y, w, h, stroke=INK, sw=1.0, fill="none"):
    return (f'<rect x="{x:.4f}" y="{y:.4f}" width="{w:.4f}" height="{h:.4f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

def text(x, y, s, size=0.12, anchor="start", color=INK):
    return (f'<text x="{x:.4f}" y="{y:.4f}" font-family="{MONO}" font-size="{size}" '
            f'text-anchor="{anchor}" fill="{color}">{esc(s)}</text>')

def path(d, stroke=INK, w=1.3, fill="none"):
    # fill="none" is explicit and non-negotiable: this is what prevents the blob.
    return (f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}" '
            f'stroke-linejoin="round" stroke-linecap="round"/>')

# ---------- composite pieces ----------
def spiral_cell(k, size_in, cx, cy, title, weight=1.3):
    pts = raw_spiral(k)
    x0, y0, x1, y1 = bbox(pts)
    w, h = x1 - x0, y1 - y0
    s = size_in / max(w, h)
    bx, by = (x0 + x1) / 2, (y0 + y1) / 2
    MX = lambda x: cx + (x - bx) * s
    MY = lambda y: cy - (y - by) * s
    d = "".join(("M" if i == 0 else "L") + f"{MX(px):.4f} {MY(py):.4f} "
                for i, (px, py) in enumerate(pts))
    out = [path(d, INK, weight)]
    ph = 0.09
    px, py = MX(0), MY(0)
    out += [line(px - ph, py, px + ph, py, ACCENT, 0.9),
            line(px, py - ph, px, py + ph, ACCENT, 0.9),
            circle(px, py, 0.03, "none", ACCENT, 0.8),
            circle(MX(pts[0][0]), MY(pts[0][1]), 0.035, ACCENT)]
    b = b_of(k); psi = math.degrees(math.atan(1 / b))
    cap_y = cy + h * s / 2 + 0.22
    kstr = "phi" if abs(k - PHI) < 1e-9 else f"{k:.2f}"
    out += [text(cx, cap_y, title, 0.13, "middle", INK),
            text(cx, cap_y + 0.18,
                 f"k={kstr} - x{k**4:.2f}/turn - psi={psi:.1f} deg - outer~{size_in:.2f} in",
                 0.10, "middle", GRAY)]
    return "".join(out)

def field(fx0, fy0, fw, fh, armature=True):
    """A 2:3 cartoon field: light armature + black crop marks + center reg."""
    fx1, fy1 = fx0 + fw, fy0 + fh
    cx, cy = fx0 + fw / 2, fy0 + fh / 2
    out = [rect(fx0, fy0, fw, fh, LIGHT, 0.8)]
    if armature:
        out += [line(fx0, fy0, fx1, fy1, "#dcdcdc", 0.6),
                line(fx1, fy0, fx0, fy1, "#dcdcdc", 0.6),
                line(fx0, fy0 + fh / 3, fx1, fy0 + fh / 3, "#d2d2d2", 0.6),
                line(fx0, fy0 + 2 * fh / 3, fx1, fy0 + 2 * fh / 3, "#d2d2d2", 0.6),
                line(cx, fy0, cx, fy1, "#e8e8e8", 0.5)]
        a, b9 = 4 / 13, 9 / 13
        for ex, ey in [(a, a), (b9, a), (a, b9), (b9, b9)]:
            out.append(circle(fx0 + fw * ex, fy0 + fh * ey, 0.028, ACCENT))
    # crop marks
    g, m = 0.09, 0.24
    def crop(px, py, sx, sy):
        return (line(px + sx * g, py, px + sx * (g + m), py, INK, 1.0) +
                line(px, py + sy * g, px, py + sy * (g + m), INK, 1.0))
    out += [crop(fx0, fy0, -1, -1), crop(fx1, fy0, 1, -1),
            crop(fx0, fy1, -1, 1), crop(fx1, fy1, 1, 1)]
    # edge center registration ticks + center crosshair
    t = 0.18
    out += [line(cx, fy0 - g, cx, fy0 - g - t, INK, 1.0),
            line(cx, fy1 + g, cx, fy1 + g + t, INK, 1.0),
            line(fx0 - g, cy, fx0 - g - t, cy, INK, 1.0),
            line(fx1 + g, cy, fx1 + g + t, cy, INK, 1.0),
            line(cx - 0.1, cy, cx + 0.1, cy, ACCENT, 0.8),
            line(cx, cy - 0.1, cx, cy + 0.1, ACCENT, 0.8)]
    return "".join(out)

def hbar(rx, ry, n=5):
    out = [line(rx, ry, rx + n, ry, INK, 1.0)]
    for i in range(n + 1):
        out.append(line(rx + i, ry, rx + i, ry - 0.12, INK, 1.0))
        out.append(text(rx + i, ry + 0.16, f'{i}"', 0.10, "middle", INK))
        if i < n:
            out.append(line(rx + i + 0.5, ry, rx + i + 0.5, ry - 0.07, INK, 0.7))
    out.append(text(rx, ry - 0.2, "CALIBRATION H - must measure exactly 5 inches", 0.10, "start", INK))
    return "".join(out)

def vbar(rx, ry0, n=5):
    out = [line(rx, ry0, rx, ry0 + n, INK, 1.0)]
    for i in range(n + 1):
        out.append(line(rx, ry0 + i, rx + 0.12, ry0 + i, INK, 1.0))
        out.append(text(rx - 0.05, ry0 + i + 0.035, f'{i}"', 0.10, "end", INK))
        if i < n:
            out.append(line(rx, ry0 + i + 0.5, rx + 0.07, ry0 + i + 0.5, INK, 0.7))
    out.append(text(rx + 0.16, ry0 - 0.06, "CAL V", 0.10, "start", INK))
    return "".join(out)

def header(title, sub):
    return text(0.5, 0.62, title, 0.20, "start", INK) + text(0.5, 0.86, sub, 0.11, "start", GRAY)

def sheet(*body):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 8.5 11" '
            'width="8.5in" height="11in">'
            '<rect x="0" y="0" width="8.5" height="11" fill="#ffffff"/>'
            + "".join(body) + "</svg>")

# ---------- 2x2 carving layout inside a 6x8 blank outline ----------
def carving_2x2(fw, fh, title, sub):
    BW, BH = 6.0, 8.0                      # blank, portrait
    bx0, by0 = (8.5 - BW) / 2, 1.35        # centered horizontally; nudged up for title
    bx1, by1 = bx0 + BW, by0 + BH
    # symmetric margins & gutter that make 2x2 fit the blank
    gx = BW - 2 * fw                       # leftover width shared by 2 outer + 1 gutter
    gy = BH - 2 * fh
    mo_x = gx / 3.0; gut_x = gx / 3.0      # equal outer margin and gutter
    mo_y = gy / 3.0; gut_y = gy / 3.0
    xs = [bx0 + mo_x, bx0 + mo_x + fw + gut_x]
    ys = [by0 + mo_y, by0 + mo_y + fh + gut_y]
    body = [header(title, sub)]
    body.append(rect(bx0, by0, BW, BH, GRAY, 1.2))           # the wood blank edge
    body.append(text(bx1 - 0.02, by0 - 0.08, "BLANK 6 x 8", 0.10, "end", GRAY))
    for yy in ys:
        for xx in xs:
            body.append(field(xx, yy, fw, fh))
    body.append(text((bx0 + bx1) / 2, by1 + 0.28,
                     f"4 up - field {fw:.3f} x {fh:.3f} in (2:3) - "
                     f"margin {mo_x:.2f}/{mo_y:.2f} in - gutter {gut_x:.2f}/{gut_y:.2f} in",
                     0.10, "middle", GRAY))
    body.append(hbar(1.75, 10.35))
    body.append(vbar(0.6, 2.6))
    return sheet(*body)

# ---------- spiral picks at sticker scale ----------
def spiral_picks():
    body = [header("Spiral Picks - sticker scale",
                   "drop one into a field - pole = crosshair - golden unless noted")]
    grid = [
        (PHI, 2.1, 2.55, 2.55, "GOLDEN 2.1\""),
        (PHI, 1.6, 5.95, 2.55, "GOLDEN 1.6\""),
        (PHI, 1.1, 2.55, 5.65, "GOLDEN 1.1\""),
        (1.30, 1.9, 5.95, 5.65, "TIGHT k=1.30"),
        (2.00, 1.9, 2.55, 8.6,  "OPEN k=2.00"),
        (1.45, 1.9, 5.95, 8.6,  "k=1.45"),
    ]
    for k, size, cx, cy, title in grid:
        body.append(spiral_cell(k, size, cx, cy, title))
    body.append(hbar(0.5, 10.6))
    return sheet(*body)

# ---------- build ----------
PAGES = [
    ("picks", spiral_picks()),
    ("roomy", carving_2x2(2.25, 3.375,
        "Carving Layout - 2x2 - roomy",
        "field 2.25 x 3.375 (2:3) - generous margin + gutter - recommended for a first carve")),
    ("max", carving_2x2(2.5, 3.75,
        "Carving Layout - 2x2 - max sticker",
        "field 2.5 x 3.75 (2:3) - thin margins, no room to spare - crop marks touch")),
]

if __name__ == "__main__":
    import cairosvg
    from pypdf import PdfWriter
    import io

    # static HTML preview (same SVG that goes to PDF)
    html = ['<!DOCTYPE html><html><head><meta charset="utf-8">',
            '<title>Spiral + Carving Templates</title>',
            '<style>body{margin:0;background:#525659}',
            '.p{background:#fff;margin:0.25in auto;box-shadow:0 2px 14px rgba(0,0,0,.4);width:8.5in;height:11in}',
            'svg{display:block}@media print{body{background:#fff}.p{margin:0;box-shadow:none;page-break-after:always}}',
            '@page{size:letter;margin:0}</style></head><body>']
    for _, svg in PAGES:
        html.append('<div class="p">' + svg + '</div>')
    html.append('</body></html>')
    with open("/home/claude/spiral-templates.html", "w") as f:
        f.write("".join(html))

    # PDF: one page per sheet, merged
    writer = PdfWriter()
    for name, svg in PAGES:
        buf = io.BytesIO()
        cairosvg.svg2pdf(bytestring=svg.encode(), write_to=buf,
                         output_width=8.5 * 96, output_height=11 * 96)
        buf.seek(0)
        from pypdf import PdfReader
        writer.append(PdfReader(buf))
    with open("/home/claude/spiral-templates.pdf", "wb") as f:
        writer.write(f)

    # PNGs for verification only
    for name, svg in PAGES:
        cairosvg.svg2png(bytestring=svg.encode(),
                         write_to=f"/home/claude/_verify_{name}.png",
                         output_width=850, output_height=1100)
    print("built: html, pdf, verify PNGs")
