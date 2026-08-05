#!/usr/bin/env python3
"""Convert a string to SVG path data using a font (fontTools), with tracking."""
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform

class TextPather:
    def __init__(self, font_path):
        self.font = TTFont(font_path)
        self.upm = self.font['head'].unitsPerEm
        try:
            self.cap = self.font['OS/2'].sCapHeight
        except Exception:
            self.cap = int(self.upm * 0.72)
        self.glyphset = self.font.getGlyphSet()
        self.cmap = self.font.getBestCmap()

    def text_path(self, text, cap_height, x=0.0, y=0.0, tracking_em=0.0):
        """Returns (path_d, total_width). y = baseline. tracking_em: extra advance
        per letter as a fraction of em (applied between letters, not after last)."""
        scale = cap_height / self.cap
        track_units = tracking_em * self.upm
        pen_cmds = []
        cursor = 0.0
        for i, ch in enumerate(text):
            gname = self.cmap.get(ord(ch))
            if gname is None:
                cursor += self.upm * 0.3
                continue
            glyph = self.glyphset[gname]
            spen = SVGPathPen(self.glyphset)
            # flip y (font y-up -> svg y-down), scale, translate
            t = Transform(scale, 0, 0, -scale, x + cursor * scale, y)
            glyph.draw(TransformPen(spen, t))
            d = spen.getCommands()
            if d:
                pen_cmds.append(d)
            cursor += glyph.width + (track_units if i < len(text) - 1 else 0)
        return " ".join(pen_cmds), cursor * scale
