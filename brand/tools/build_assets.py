#!/usr/bin/env python3
"""Build the refreshed Strateon logo asset set into an output directory.

Usage:  python3 build_assets.py <out-dir>

Rebuilds the SVG set (logo/ + icons/). PNG exports are a separate step
(headless chromium screenshots; see brand/README.md).

The wordmark lockups need the Inter OTFs (Inter-Bold.otf, Inter-SemiBold.otf).
Font lookup order:
  1. $INTER_OTF_DIR
  2. <this script's dir>/fonts/
  3. <this script's dir>/inter_font/extras/otf/   (layout of the Inter release zip)
If the fonts are missing, marks/icons/favicon still build; lockups are skipped
with a warning. Requires: fontTools (pip install fonttools) for lockups only.
"""
import os, sys, math
from markgen import build, fmt

HERE = os.path.dirname(os.path.abspath(__file__))

# --- brand colors (unchanged, from the brandbook palette) ---
GOLD   = "#D2A24E"   # Strategic Gold
GOLD2  = "#B98632"   # Antique Gold
NAVY   = "#061D2E"   # Strateon Navy
IVORY  = "#F7F3EA"   # Warm Ivory
WHITE  = "#FFFFFF"

# --- final locked geometry ---
GEO = dict(WoverR=0.75, DoverR=0.5, t=22.5, c=24.0, g=14.0, tip_x=5.0)

def find_fonts():
    candidates = []
    if os.environ.get("INTER_OTF_DIR"):
        candidates.append(os.environ["INTER_OTF_DIR"])
    candidates.append(os.path.join(HERE, "fonts"))
    candidates.append(os.path.join(HERE, "inter_font", "extras", "otf"))
    for d in candidates:
        b = os.path.join(d, "Inter-Bold.otf")
        s = os.path.join(d, "Inter-SemiBold.otf")
        if os.path.isfile(b) and os.path.isfile(s):
            return b, s
    return None, None

def grad(gid):
    """Palette-only gold gradient with a per-file unique id."""
    return (f'<linearGradient id="{gid}" x1="0" y1="0" x2="0.55" y2="1">'
            f'<stop offset="0" stop-color="{GOLD}"/>'
            f'<stop offset="1" stop-color="{GOLD2}"/></linearGradient>')

def mark_polys(fill_ref, scale=1.0, dx=0.0, dy=0.0):
    m = build(R=100.0, **GEO)
    def tx(pts):
        return [(x * scale + dx, y * scale + dy) for x, y in pts]
    return (f'<polygon points="{fmt(tx(m["upper"]))}" fill="{fill_ref}"/>'
            f'<polygon points="{fmt(tx(m["lower"]))}" fill="{fill_ref}"/>'), m

def svg(w, h, body, x0=0, y0=0):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:g} {y0:g} {w:g} {h:g}" '
            f'width="{w:g}" height="{h:g}">{body}</svg>')

def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print("  ", path)

def build_marks(out):
    m = build(R=100.0, **GEO)
    W, R = m["W"], m["R"]
    def one(fill_ref, defs=""):
        body = (defs + f'<polygon points="{fmt(m["upper"])}" fill="{fill_ref}"/>'
                       f'<polygon points="{fmt(m["lower"])}" fill="{fill_ref}"/>')
        return (f'<svg xmlns="http://www.w3.org/2000/svg" '
                f'viewBox="{-W:g} {-R:g} {2*W:g} {2*R:g}">{body}</svg>')
    write(f"{out}/logo/strateon-mark-gold.svg", one(GOLD))
    write(f"{out}/logo/strateon-mark-gold-gradient.svg",
          one("url(#au-mark)", f"<defs>{grad('au-mark')}</defs>"))
    write(f"{out}/logo/strateon-mark-white.svg", one(WHITE))
    write(f"{out}/logo/strateon-mark-navy.svg", one(NAVY))

def build_lockup_h(out, tp_b, tp_s, dark=True):
    """Horizontal lockup: mark | divider | STRATEON / -- TRADING FZCO --
    Text block and divider are optically centered on the mark axis (y=100)."""
    word_color = WHITE if dark else NAVY
    gid = f"au-h-{'dark' if dark else 'light'}"
    mx, my = 75.0, 100.0
    gap = 52.0
    div_x = 150.0 + gap
    tx0 = div_x + gap
    cap1, cap2 = 62.0, 24.0
    block_h = cap1 + (166.0 - 96.0)          # cap1 + (base2 - base1) spacing, see below
    base1 = 96.0                              # STRATEON baseline -> block spans 34..166
    base2 = 166.0                             # tagline baseline
    d1, w1 = tp_b.text_path("STRATEON", cap1, x=tx0, y=base1, tracking_em=0.30)
    d2, w2 = tp_s.text_path("TRADING FZCO", cap2, x=0, y=base2, tracking_em=0.42)
    sub_x = tx0 + (w1 - w2) / 2
    d2, _ = tp_s.text_path("TRADING FZCO", cap2, x=sub_x, y=base2, tracking_em=0.42)
    ry = base2 - cap2 / 2 + 1
    rule_w, rpad = 34.0, 22.0
    rules = (f'<rect x="{sub_x - rpad - rule_w:g}" y="{ry - 1.25:g}" width="{rule_w}" height="2.5" fill="{GOLD}"/>'
             f'<rect x="{sub_x + w2 + rpad:g}" y="{ry - 1.25:g}" width="{rule_w}" height="2.5" fill="{GOLD}"/>')
    marks, _ = mark_polys(f"url(#{gid})", 1.0, mx, my)
    # divider spans exactly the text block (34..166), centered on y=100
    body = (f'<defs>{grad(gid)}</defs>' + marks +
            f'<rect x="{div_x - 2:g}" y="34" width="3.5" height="132" fill="{GOLD}"/>'
            f'<path d="{d1}" fill="{word_color}"/>'
            f'<path d="{d2}" fill="{GOLD}"/>' + rules)
    name = "dark" if dark else "light"
    write(f"{out}/logo/strateon-logo-horizontal-{name}.svg", svg(tx0 + w1 + 6, 200, body))

def build_lockup_h_compact(out, tp_b, dark=True):
    """Compact horizontal lockup (no tagline) for widths below ~220 px."""
    word_color = WHITE if dark else NAVY
    gid = f"au-hc-{'dark' if dark else 'light'}"
    mx, my = 75.0, 100.0
    gap = 52.0
    div_x = 150.0 + gap
    tx0 = div_x + gap
    cap1 = 62.0
    base1 = 100.0 + cap1 / 2                 # cap-height block centered on y=100
    d1, w1 = tp_b.text_path("STRATEON", cap1, x=tx0, y=base1, tracking_em=0.30)
    marks, _ = mark_polys(f"url(#{gid})", 1.0, mx, my)
    body = (f'<defs>{grad(gid)}</defs>' + marks +
            f'<rect x="{div_x - 2:g}" y="56" width="3.5" height="88" fill="{GOLD}"/>'
            f'<path d="{d1}" fill="{word_color}"/>')
    name = "dark" if dark else "light"
    write(f"{out}/logo/strateon-logo-horizontal-compact-{name}.svg", svg(tx0 + w1 + 6, 200, body))

def build_lockup_stacked(out, tp_b, tp_s, dark=True):
    word_color = WHITE if dark else NAVY
    gid = f"au-s-{'dark' if dark else 'light'}"
    W = 560.0
    cx = W / 2
    marks, _ = mark_polys(f"url(#{gid})", 1.0, cx, 105.0)
    cap1, base1 = 54.0, 306.0
    d1, w1 = tp_b.text_path("STRATEON", cap1, x=0, y=base1, tracking_em=0.30)
    d1, _ = tp_b.text_path("STRATEON", cap1, x=cx - w1 / 2, y=base1, tracking_em=0.30)
    cap2, base2 = 21.0, 356.0
    d2, w2 = tp_s.text_path("TRADING FZCO", cap2, x=0, y=base2, tracking_em=0.42)
    sub_x = cx - w2 / 2
    d2, _ = tp_s.text_path("TRADING FZCO", cap2, x=sub_x, y=base2, tracking_em=0.42)
    ry = base2 - cap2 / 2 + 1
    rule_w, rpad = 30.0, 20.0
    rules = (f'<rect x="{sub_x - rpad - rule_w:g}" y="{ry - 1.1:g}" width="{rule_w}" height="2.2" fill="{GOLD}"/>'
             f'<rect x="{sub_x + w2 + rpad:g}" y="{ry - 1.1:g}" width="{rule_w}" height="2.2" fill="{GOLD}"/>')
    body = (f'<defs>{grad(gid)}</defs>' + marks +
            f'<path d="{d1}" fill="{word_color}"/>'
            f'<path d="{d2}" fill="{GOLD}"/>' + rules)
    name = "dark" if dark else "light"
    # viewBox trimmed to content: mark top at y=5, tagline baseline 356 + 5 pad
    write(f"{out}/logo/strateon-logo-stacked-{name}.svg", svg(W, 361, body))

def build_favicon(out):
    # app icon: mark at 68% of tile height for small-size presence
    marks, _ = mark_polys("url(#au-app)", 1.75, 256, 256)
    body = (f'<defs>{grad("au-app")}</defs>'
            f'<rect width="512" height="512" rx="96" fill="{NAVY}"/>' + marks)
    write(f"{out}/logo/strateon-appicon.svg", svg(512, 512, body))
    # plain favicon (bare mark - use this on navy surfaces)
    marks2, _ = mark_polys(GOLD, 1.0, 75, 100)
    write(f"{out}/logo/strateon-favicon.svg",
          f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 150 200">{marks2}</svg>')

ICONS = {
  # 48x48 grid, stroke-only, geometric; hexagonal accents echo the monogram
  "oil-products": '<path d="M24 7 C29 15 35 21.5 35 29 a11 11 0 0 1 -22 0 C13 21.5 19 15 24 7 Z"/><path d="M19 30 a5.5 5.5 0 0 0 5 5.5" stroke-width="1.6" opacity="0.85"/>',
  "gas": '<path d="M24 6 C26 12 33 16 33 25 a9.5 9.5 0 0 1 -19 0 C14 18 21 13 24 6 Z"/><path d="M24 22 c3 3.2 4.5 5 4.5 8 a4.5 4.5 0 0 1 -9 0 c0 -3 1.5 -4.8 4.5 -8 Z" stroke-width="1.6"/>',
  "metals": '<path d="M8.4 22.2 H19.2 L22.2 31.2 H5.4 Z"/><path d="M28.8 22.2 H39.6 L42.6 31.2 H25.8 Z"/><path d="M18.6 9.8 H29.4 L32.4 18.8 H15.6 Z"/>',
  "fertilizers": '<path d="M24 34 V22"/><path d="M24 26 C24 20 19 17 13.5 17 C13.5 23 18 26 24 26 Z"/><path d="M24 23 C24 17.5 28.5 14.5 34.5 14.5 C34.5 20.5 30 23.5 24 23.5 Z"/><path d="M10 39 h28" stroke-width="1.8"/><circle cx="16.5" cy="35" r="1.3" fill="currentColor" stroke="none"/><circle cx="31.5" cy="35" r="1.3" fill="currentColor" stroke="none"/>',
  "chemicals": '<path d="M20.5 7.5 h7 M26 7.5 V17 l7.8 17.6 a2.8 2.8 0 0 1 -2.56 3.9 H16.76 a2.8 2.8 0 0 1 -2.56 -3.9 L22 17 V7.5" fill="none"/><path d="M18.4 29.5 h11.2" stroke-width="1.8"/><circle cx="22.5" cy="34" r="1.2" fill="currentColor" stroke="none"/><circle cx="26.8" cy="32.6" r="0.9" fill="currentColor" stroke="none"/>',
  "solid-fuels": '<path d="M18 14 l6 -3.5 6 3.5 v7 l-6 3.5 -6 -3.5 Z"/><path d="M11 26 l6 -3.5 6 3.5 v7 L17 37 l-6 -3.5 Z"/><path d="M25 26 l6 -3.5 6 3.5 v7 L31 37 l-6 -3.5 Z"/>',
}

def build_icons(out):
    for name, inner in ICONS.items():
        body = (f'<g fill="none" stroke="{GOLD}" stroke-width="2.1" '
                f'stroke-linejoin="round" stroke-linecap="round" color="{GOLD}">{inner}</g>')
        write(f"{out}/icons/icon-{name}.svg",
              f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">{body}</svg>')

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "assets"
    build_marks(out)
    build_favicon(out)
    build_icons(out)
    fb, fs = find_fonts()
    if fb:
        from textpaths import TextPather
        tp_b, tp_s = TextPather(fb), TextPather(fs)
        build_lockup_h(out, tp_b, tp_s, dark=True)
        build_lockup_h(out, tp_b, tp_s, dark=False)
        build_lockup_h_compact(out, tp_b, dark=True)
        build_lockup_h_compact(out, tp_b, dark=False)
        build_lockup_stacked(out, tp_b, tp_s, dark=True)
        build_lockup_stacked(out, tp_b, tp_s, dark=False)
    else:
        print("WARN: Inter OTFs not found (set $INTER_OTF_DIR or put Inter-Bold.otf "
              "and Inter-SemiBold.otf in tools/fonts/) - lockups skipped.")
    print("done")
