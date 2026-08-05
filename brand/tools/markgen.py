#!/usr/bin/env python3
"""Parametric generator for the Strateon S-in-hexagon monogram.

Geometry model (math coords, y down, origin at optical center):
  Elongated pointy-top hexagon: half-width W, half-height R, slant drop D.
  Vertical walls at x = +-W spanning y in [-(R-D), R-D].
  Spine: two parallel bands at the slant angle (direction u = (W?, D?) -> normalized
  along slant of TR/BL edges), rotationally symmetric (180 deg) about origin.
  Upper piece  = top chevron + left wall (long) + right wall stub + spine band
                 descending to a tip below-right of center.
  Lower piece  = 180 deg rotation of upper piece.
All cut faces are parallel to the spine; tip cut is vertical (echoes the walls).
"""
import math

def line_x(p, u, x):
    """Point on line (p + s*u) with given x."""
    s = (x - p[0]) / u[0]
    return (x, p[1] + s * u[1])

def isect(p1, u1, p2, u2):
    """Intersection of two lines given as point+direction."""
    d = u1[0] * u2[1] - u1[1] * u2[0]
    s = ((p2[0] - p1[0]) * u2[1] - (p2[1] - p1[1]) * u2[0]) / d
    return (p1[0] + s * u1[0], p1[1] + s * u1[1])

def rot180(pts):
    return [(-x, -y) for (x, y) in pts]

def fmt(pts, nd=2):
    return " ".join(f"{round(x, nd):g},{round(y, nd):g}" for x, y in pts)

def build(R=100.0, WoverR=0.75, DoverR=0.5, t=22.5, c=22.5, g=15.0,
          tip_x=None):
    """Returns dict with polygon point lists for upper piece and lower piece.
    tip_x: x of the vertical tip cut (default: c*0.25)."""
    W = R * WoverR
    D = R * DoverR
    if tip_x is None:
        tip_x = c * 0.25
    L = math.hypot(W, D)
    u = (W / L, D / L)                     # spine/slant direction (down-right)
    n = (u[1], -u[0])                      # normal, points up-right
    a_sin, a_cos = u[1], u[0]              # sin/cos of slant angle

    # outer hexagon vertices
    Vt, Vtr, Vbr = (0, -R), (W, -R + D), (W, R - D)
    Vb, Vbl, Vtl = (0, R), (-W, R - D), (-W, -R + D)

    # inner edge lines (offset inward by t, perpendicular)
    TLp = (Vt[0] + t * D / L, Vt[1] + t * W / L)     # TL inner: point + dir (-W, D)
    TLu = (-W, D)
    TRp = (Vt[0] - t * D / L, Vt[1] + t * W / L)     # TR inner: dir (W, D)
    TRu = (W, D)

    # spine boundary lines for the UPPER piece (band on lower-left of center):
    # near boundary at perp c/2, far at c/2+t along (-n)
    def perp_pt(d, side):   # side=+1: up-right (n), -1: down-left
        return (side * d * n[0], side * d * n[1])
    Uup_p = perp_pt(c / 2, -1)          # near boundary (faces the counter)
    Ulo_p = perp_pt(c / 2 + t, -1)      # far boundary
    # right wall stub cut face (upper piece): parallel to spine at perp c/2+t+g up-right
    Cr_p = perp_pt(c / 2 + t + g, +1)

    # --- assemble upper piece, clockwise ---
    P_vt  = Vt
    P_vtr = Vtr
    P_rw_cut_out = line_x(Cr_p, u, W)        # cut meets right wall outer face
    P_rw_cut_in  = line_x(Cr_p, u, W - t)    # cut meets right wall inner face
    P_tr_in_rw = isect(TRp, TRu, (W - t, 0), (0, 1))   # TR inner  x  RW inner
    P_apex_in = isect(TLp, TLu, TRp, TRu)              # inner chevron apex
    P_tl_in_lw = isect(TLp, TLu, (-W + t, 0), (0, 1))  # TL inner  x  LW inner
    P_j1 = line_x(Uup_p, u, -W + t)          # spine near-boundary leaves LW inner
    P_tip_up = line_x(Uup_p, u, tip_x)       # tip cut (vertical) on near boundary
    P_tip_lo = line_x(Ulo_p, u, tip_x)       # tip cut on far boundary
    P_k = line_x(Ulo_p, u, -W)               # spine far-boundary crosses LW outer
    P_vtl = Vtl

    upper = [P_vt, P_vtr, P_rw_cut_out, P_rw_cut_in, P_tr_in_rw,
             P_apex_in, P_tl_in_lw, P_j1, P_tip_up, P_tip_lo, P_k, P_vtl]
    lower = rot180(upper)
    return {"upper": upper, "lower": lower, "W": W, "R": R}

def svg_mark(fill="#D2A24E", pad=0.0, defs="", fill_attr=None, **kw):
    m = build(**kw)
    W, R = m["W"], m["R"]
    x0, y0 = -W - pad, -R - pad
    w, h = 2 * (W + pad), 2 * (R + pad)
    f = fill_attr if fill_attr else f'fill="{fill}"'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:g} {y0:g} {w:g} {h:g}">'
            f'{defs}'
            f'<polygon points="{fmt(m["upper"])}" {f}/>'
            f'<polygon points="{fmt(m["lower"])}" {f}/></svg>')

if __name__ == "__main__":
    import sys, json, itertools, os
    out = sys.argv[1] if len(sys.argv) > 1 else "variants"
    os.makedirs(out, exist_ok=True)
    # variant grid for visual comparison
    variants = {
        "v1_asorig":   dict(WoverR=0.773, DoverR=0.496, t=22.7, c=26.4, g=13.7, tip_x=2.5),
        "v2_rational": dict(WoverR=0.75, DoverR=0.5, t=22.5, c=22.5, g=15.0, tip_x=5.6),
        "v3_airy":     dict(WoverR=0.75, DoverR=0.5, t=22.0, c=25.0, g=14.0, tip_x=6.0),
        "v4_regular":  dict(WoverR=math.sqrt(3)/2, DoverR=0.5, t=24.0, c=24.0, g=15.0, tip_x=6.0),
        "v5_bold":     dict(WoverR=0.75, DoverR=0.5, t=24.5, c=21.0, g=13.0, tip_x=5.0),
    }
    for name, kw in variants.items():
        with open(f"{out}/{name}.svg", "w") as fh:
            fh.write(svg_mark(**kw))
    print("wrote", len(variants), "variants to", out)
