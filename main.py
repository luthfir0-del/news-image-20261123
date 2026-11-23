#!/usr/bin/env python3
"""news-image-20261123: draw the 23 Nov 2026 world-news cover.

Stdlib only, no network, deterministic: two runs write identical bytes.
Writes a 1024x1024 PNG to $MAKEFUN_OUTPUT_DIR/entry.png (default /output).
Layout: Economist-style cover -- red masthead, huge condensed title,
red date line, 3-line italic subtitle, and a large 12-slice clock wheel
(RIM 350), one slice per verified story of Monday 23 November 2026.
Each slice carries a big two-line headline plus one short fact line,
all sized to stay readable when the image is viewed at 300px.
"""
import os
import struct
import sys
import zlib
from math import cos, pi, sin, sqrt

W = H = 1024
CREAM = (245, 240, 230)
INK = (17, 17, 17)
RED = (227, 6, 19)
WHITE = (255, 255, 255)

# ---------------------------------------------------------------- canvas
buf = bytearray(W * H * 3)
for _i in range(W * H):
    buf[3 * _i] = CREAM[0]
    buf[3 * _i + 1] = CREAM[1]
    buf[3 * _i + 2] = CREAM[2]


def put(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        o = 3 * (y * W + x)
        buf[o] = c[0]
        buf[o + 1] = c[1]
        buf[o + 2] = c[2]


def hline(x0, x1, y, c):
    if y < 0 or y >= H:
        return
    x0 = max(0, x0)
    x1 = min(W - 1, x1)
    if x1 < x0:
        return
    o = 3 * (y * W + x0)
    n = x1 - x0 + 1
    buf[o:o + 3 * n] = bytes(c) * n


def fill_rect(x0, y0, x1, y1, c):
    for y in range(max(0, y0), min(H, y1 + 1)):
        hline(x0, x1, y, c)


def line(x0, y0, x1, y1, c, w=1):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    half = w // 2
    while True:
        for a in range(-half, half + 1):
            for b in range(-half, half + 1):
                put(x0 + a, y0 + b, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def circle(cx, cy, r, c, w=1):
    x = 0
    y = r
    d = 3 - 2 * r
    while x <= y:
        for (px, py) in ((cx + x, cy + y), (cx - x, cy + y),
                         (cx + x, cy - y), (cx - x, cy - y),
                         (cx + y, cy + x), (cx - y, cy + x),
                         (cx + y, cy - x), (cx - y, cy - x)):
            for a in range(-(w // 2), w // 2 + 1):
                put(px + a, py, c)
                put(px, py + a, c)
        if d < 0:
            d += 4 * x + 6
        else:
            d += 4 * (x - y) + 10
            y -= 1
        x += 1


def fill_circle(cx, cy, r, c):
    r = int(r)
    for dy in range(-r, r + 1):
        dx = int(sqrt(max(0, r * r - dy * dy)))
        hline(cx - dx, cx + dx, cy + dy, c)


def poly(points, c):
    """Fill a polygon given as [(x, y), ...] via scanlines."""
    if not points:
        return
    ys = [p[1] for p in points]
    for y in range(max(0, min(ys)), min(H - 1, max(ys)) + 1):
        xs = []
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                t = (y - y0) / (y1 - y0)
                xs.append(x0 + t * (x1 - x0))
        if len(xs) >= 2:
            xs.sort()
            hline(int(round(xs[0])), int(round(xs[-1])), y, c)


def poly_line(points, c, w=1):
    for i in range(len(points) - 1):
        line(points[i][0], points[i][1], points[i + 1][0], points[i + 1][1], c, w)


def star4(cx, cy, r, c):
    k = 0.28
    poly([(cx, cy - r), (cx + int(r * k), cy - int(r * k)), (cx + r, cy),
          (cx + int(r * k), cy + int(r * k)), (cx, cy + r),
          (cx - int(r * k), cy + int(r * k)), (cx - r, cy),
          (cx - int(r * k), cy - int(r * k))], c)

# ---------------------------------------------------------------- font
# One 5x7 bitmap font, designed here from scratch. Each glyph is 8 rows
# of 5 bits (rows 0-6 carry caps, row 7 carries descenders). Monospace
# advance: 6 units per character, including the space.
FONT = {
    'A': (0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001, 0),
    'B': (0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110, 0),
    'C': (0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110, 0),
    'D': (0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110, 0),
    'E': (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111, 0),
    'F': (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000, 0),
    'G': (0b01110, 0b10001, 0b10000, 0b10111, 0b10001, 0b10001, 0b01111, 0),
    'H': (0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001, 0),
    'I': (0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110, 0),
    'J': (0b00111, 0b00010, 0b00010, 0b00010, 0b00010, 0b10010, 0b01100, 0),
    'K': (0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001, 0),
    'L': (0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111, 0),
    'M': (0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001, 0),
    'N': (0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001, 0b10001, 0),
    'O': (0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110, 0),
    'P': (0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000, 0),
    'Q': (0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101, 0),
    'R': (0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001, 0),
    'S': (0b01111, 0b10000, 0b10000, 0b01110, 0b00001, 0b00001, 0b11110, 0),
    'T': (0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0),
    'U': (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110, 0),
    'V': (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100, 0),
    'W': (0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b11011, 0b10001, 0),
    'X': (0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001, 0),
    'Y': (0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100, 0),
    'Z': (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111, 0),
    '0': (0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110, 0),
    '1': (0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110, 0),
    '2': (0b01110, 0b10001, 0b00001, 0b00110, 0b01000, 0b10000, 0b11111, 0),
    '3': (0b11111, 0b00010, 0b00100, 0b00010, 0b00001, 0b10001, 0b01110, 0),
    '4': (0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010, 0),
    '5': (0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110, 0),
    '6': (0b00110, 0b01000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110, 0),
    '7': (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000, 0),
    '8': (0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110, 0),
    '9': (0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b01100, 0),
    'a': (0, 0, 0b01110, 0b00001, 0b01111, 0b10001, 0b01111, 0),
    'b': (0b10000, 0b10000, 0b11110, 0b10001, 0b10001, 0b10001, 0b11110, 0),
    'c': (0, 0, 0b01110, 0b10001, 0b10000, 0b10001, 0b01110, 0),
    'd': (0b00001, 0b00001, 0b01111, 0b10001, 0b10001, 0b10001, 0b01111, 0),
    'e': (0, 0, 0b01110, 0b10001, 0b11111, 0b10000, 0b01110, 0),
    'f': (0b00110, 0b01001, 0b01000, 0b11110, 0b01000, 0b01000, 0b01000, 0),
    'g': (0, 0, 0b01111, 0b10001, 0b10001, 0b01111, 0b00001, 0b01110),
    'h': (0b10000, 0b10000, 0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0),
    'i': (0b00100, 0, 0b01100, 0b00100, 0b00100, 0b00100, 0b01110, 0),
    'j': (0b00010, 0, 0b00110, 0b00010, 0b00010, 0b10010, 0b01100, 0),
    'k': (0b10000, 0b10000, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0),
    'l': (0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110, 0),
    'm': (0, 0, 0b11010, 0b10101, 0b10101, 0b10101, 0b10101, 0),
    'n': (0, 0, 0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0),
    'o': (0, 0, 0b01110, 0b10001, 0b10001, 0b10001, 0b01110, 0),
    'p': (0, 0, 0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000),
    'q': (0, 0, 0b01111, 0b10001, 0b10001, 0b01111, 0b00001, 0b00001),
    'r': (0, 0, 0b10110, 0b11001, 0b10000, 0b10000, 0b10000, 0),
    's': (0, 0, 0b01111, 0b10000, 0b01110, 0b00001, 0b11110, 0),
    't': (0b00100, 0b00100, 0b11111, 0b00100, 0b00100, 0b00100, 0b00110, 0),
    'u': (0, 0, 0b10001, 0b10001, 0b10001, 0b10001, 0b01111, 0),
    'v': (0, 0, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0),
    'w': (0, 0, 0b10001, 0b10001, 0b10101, 0b10101, 0b11011, 0),
    'x': (0, 0, 0b10001, 0b10001, 0b01010, 0b10001, 0b10001, 0),
    'y': (0, 0, 0b10001, 0b10001, 0b10001, 0b01111, 0b00001, 0b01110),
    'z': (0, 0, 0b11111, 0b00001, 0b00110, 0b01000, 0b11111, 0),
    ' ': (0, 0, 0, 0, 0, 0, 0, 0),
    '.': (0, 0, 0, 0, 0, 0b01100, 0b01100, 0),
    ',': (0, 0, 0, 0, 0b01100, 0b00100, 0b01000, 0),
    '-': (0, 0, 0, 0b01110, 0, 0, 0, 0),
    "'": (0b00100, 0b00100, 0b01000, 0, 0, 0, 0, 0),
    '%': (0b11001, 0b11010, 0b00010, 0b00100, 0b01000, 0b01011, 0b10011, 0),
    ':': (0, 0b01100, 0b01100, 0, 0b01100, 0b01100, 0, 0),
    ';': (0, 0b01100, 0b01100, 0, 0b01100, 0b00100, 0b01000, 0),
    '/': (0b00001, 0b00010, 0b00010, 0b00100, 0b01000, 0b01000, 0b10000, 0),
    '(': (0b00010, 0b00100, 0b01000, 0b01000, 0b01000, 0b00100, 0b00010, 0),
    ')': (0b01000, 0b00100, 0b00010, 0b00010, 0b00010, 0b00100, 0b01000, 0),
    '&': (0b01100, 0b10010, 0b10100, 0b01000, 0b10101, 0b10010, 0b01101, 0),
    '\u00b7': (0, 0, 0b01100, 0b01100, 0, 0, 0, 0),
    '$': (0b00100, 0b01111, 0b10100, 0b01110, 0b00101, 0b11110, 0b00100, 0),
    '!': (0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0, 0b00100, 0),
    '?': (0b01110, 0b10001, 0b00001, 0b00110, 0b00100, 0, 0b00100, 0),
    '"': (0b01010, 0b01010, 0b01010, 0, 0, 0, 0, 0),
    '+': (0, 0b00100, 0b00100, 0b11111, 0b00100, 0b00100, 0, 0),
    '=': (0, 0, 0b11111, 0, 0b11111, 0, 0, 0),
    '_': (0, 0, 0, 0, 0, 0, 0b11111, 0),
}

ADV = 6  # advance, font units per character (monospace contexts)

# Proportional advances for body copy, font units per character.
# Narrow glyphs take 3-4 units, normal ones 5, wide ones 6.
ADV_PROP = {
    ' ': 3, '.': 3, ',': 3, ':': 3, ';': 3, '!': 3, "'": 3, '-': 3,
    '\u00b7': 3,
    'i': 4, 'l': 4, 'j': 4, 't': 4, 'f': 4, 'r': 4, '1': 4, '/': 4,
    '(': 4, ')': 4,
    'm': 6, 'w': 6,
}
for _ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
    ADV_PROP[_ch] = 6
ADV_PROP['$'] = 6
ADV_PROP['&'] = 6
ADV_PROP['%'] = 6


def _adv(ch, mono):
    if mono:
        return ADV
    return ADV_PROP.get(ch, 5)


def text_width(s, sx, mono=True):
    return sum(_adv(ch, mono) for ch in s) * sx


def text(s, x, y, sx, sy, c, bold=False, italic=False, mono=True):
    """Draw string s with top-left corner at (x, y)."""
    gx = x
    shear = 0.30 * sx if italic else 0.0
    bold_dx = max(1, round(sx * 0.3)) if bold else 0
    for ch in s:
        glyph = FONT.get(ch)
        if glyph is None:
            glyph = FONT['?']
        for rep in range(2 if bold_dx else 1):
            ox = gx + rep * bold_dx
            for row in range(8):
                bits = glyph[row]
                if not bits:
                    continue
                shift = int(round((7 - row) * shear))
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        px0 = int(round(ox + shift + col * sx))
                        px1 = int(round(ox + shift + (col + 1) * sx))
                        py0 = int(round(y + row * sy))
                        py1 = int(round(y + (row + 1) * sy))
                        fill_rect(px0, py0, max(px0, px1 - 1), max(py0, py1 - 1), c)
        gx += _adv(ch, mono) * sx


def text_c(s, cx, y, sx, sy, c, bold=False, italic=False, mono=True):
    """Draw string s centred on cx, top at y."""
    text(s, cx - text_width(s, sx, mono) / 2, y, sx, sy, c, bold, italic, mono)

# ---------------------------------------------------------------- wedges
CX, CY = 512, 644
RIM = 350
ROSETTE = 60
NUM_R = 366
NUM_CIRCLE_R = 16


def _deg2rad(a):
    return a * pi / 180.0


def _ray_x(dy, a):
    """x where the ray at angle a (deg, clockwise from top) crosses y=CY+dy.

    Returns None when the ray does not cross that row in the forward
    direction (it points away from the row, or is horizontal). The old
    tan-based version returned a huge sentinel with the wrong sign for
    the 270-degree ray, which mirrored the spans of the 240-270 and
    270-300 wedges onto the wrong side of the wheel.
    """
    c = cos(_deg2rad(a))
    if abs(c) < 1e-9:
        return None
    t = -dy / c
    if t < 0:
        return None
    return CX + sin(_deg2rad(a)) * t


def wedge_span(a1, a2, y):
    """Horizontal interval of the wedge [a1, a2] at canvas row y, or None.

    Angles in degrees clockwise from top. Intersects the angular span
    with the circle of radius RIM around (CX, CY).
    """
    dy = y - CY
    if abs(dy) >= RIM:
        return None
    dx = sqrt(RIM * RIM - dy * dy)
    lo = CX - dx
    hi = CX + dx
    x1 = _ray_x(dy, a1)
    x2 = _ray_x(dy, a2)
    if x1 is None and x2 is None:
        return None
    if x1 is None:
        # wedge extends from the x2 crossing toward a1's direction
        if sin(_deg2rad(a1)) > 0:
            lo = max(lo, x2)
        else:
            hi = min(hi, x2)
    elif x2 is None:
        if sin(_deg2rad(a2)) > 0:
            lo = max(lo, x1)
        else:
            hi = min(hi, x1)
    else:
        lo = max(lo, min(x1, x2))
        hi = min(hi, max(x1, x2))
    if hi <= lo:
        return None
    return (lo, hi)


def fit_span(a1, a2, y_top, height):
    """Intersection of wedge spans at y_top+2, middle, bottom-2."""
    spans = []
    for y in (y_top + 2, y_top + height // 2, y_top + height - 2):
        s = wedge_span(a1, a2, y)
        if s is None:
            return None
        spans.append(s)
    lo = max(s[0] for s in spans)
    hi = min(s[1] for s in spans)
    if hi <= lo:
        return None
    return (lo, hi)


def line_cx(top, height, a1, a2, bx, w):
    """Centre x for a line so it sits inside its wedge span.

    The wedge span shifts sideways across a line's rows (diagonal
    spokes), so a line centred on the block centre can clip a spoke
    even when its width fits. Keep the block centre when the line
    fits there, and shift it only as far as needed to clear the span.
    """
    span = fit_span(a1, a2, top, height)
    if span is None:
        return bx
    lo, hi = span
    return min(max(bx, lo + w / 2), hi - w / 2)


def check_line(label, s, y_top, height, sx, a1, a2, tol=0, mono=True):
    """Warn when a line is wider than its wedge span (plus tolerance)."""
    span = fit_span(a1, a2, y_top, height)
    w = text_width(s, sx, mono)
    if span is None:
        print("WARN %s: no span at y=%d" % (label, y_top), file=sys.stderr)
        return
    if w > (span[1] - span[0]) + tol:
        print("WARN %s: line %.0fpx vs span %.0fpx at y=%d"
              % (label, w, span[1] - span[0], y_top), file=sys.stderr)


def polar(r, angle_deg):
    a = _deg2rad(angle_deg)
    return (CX + r * sin(a), CY - r * cos(a))


# ---------------------------------------------------------------- pictograms
# Each draws a small black icon with a red accent, centred at (cx, cy),
# about 30px across. Coordinates are relative to the centre.


def pic_shield(cx, cy):
    pts = [(-11, -12), (11, -12), (11, 0), (0, 13), (-11, 0)]
    poly_line(pts + [pts[0]], INK, 2)
    poly_line([(-6, 0), (-1, 5), (8, -7)], RED, 2)


def pic_building(cx, cy):
    fill_rect(cx - 12, cy - 10, cx + 12, cy + 12, INK)
    for wx in (-8, -2, 4):
        for wy in (-6, 0, 6):
            fill_rect(cx + wx, cy + wy, cx + wx + 2, cy + wy + 2, CREAM)
    fill_rect(cx - 2, cy + 8, cx + 2, cy + 12, RED)


def pic_chart(cx, cy):
    line(cx - 12, cy - 12, cx - 12, cy + 10, INK, 2)
    line(cx - 12, cy + 10, cx + 12, cy + 10, INK, 2)
    poly_line([(cx - 10, cy + 2), (cx - 3, cy - 4), (cx + 4, cy + 2),
               (cx + 11, cy - 8)], RED, 2)


def pic_tanker(cx, cy):
    poly([(cx - 14, cy + 2), (cx + 14, cy + 2), (cx + 11, cy + 10),
          (cx - 11, cy + 10)], INK)
    fill_rect(cx + 2, cy - 8, cx + 10, cy + 2, INK)
    fill_rect(cx - 14, cy + 6, cx + 14, cy + 8, RED)


def pic_flask(cx, cy):
    fill_rect(cx - 3, cy - 12, cx + 3, cy - 4, INK)
    poly([(cx - 10, cy + 10), (cx + 10, cy + 10), (cx + 4, cy - 4),
          (cx - 4, cy - 4)], INK)
    fill_rect(cx - 6, cy + 4, cx + 6, cy + 9, RED)


def pic_globe(cx, cy):
    circle(cx, cy, 12, INK, 2)
    line(cx, cy - 12, cx, cy + 12, INK, 1)
    line(cx - 12, cy, cx + 12, cy, INK, 1)
    poly_line([(cx + 3, cy - 11), (cx + 9, cy - 6), (cx + 11, cy),
               (cx + 9, cy + 6), (cx + 3, cy + 11)], RED, 2)


def pic_megaphone(cx, cy):
    poly([(cx - 12, cy - 6), (cx + 8, cy - 12), (cx + 8, cy + 12),
          (cx - 12, cy + 6)], INK)
    fill_rect(cx - 12, cy + 6, cx - 8, cy + 13, INK)
    poly_line([(cx + 12, cy - 8), (cx + 15, cy), (cx + 12, cy + 8)], RED, 2)


def pic_capitol(cx, cy):
    poly([(cx - 13, cy - 2), (cx, cy - 12), (cx + 13, cy - 2)], INK)
    for col in (-9, -2, 5):
        fill_rect(cx + col, cy - 2, cx + col + 3, cy + 8, INK)
    fill_rect(cx - 13, cy + 8, cx + 13, cy + 11, INK)
    fill_rect(cx - 2, cy - 8, cx + 2, cy - 2, RED)


def pic_rocket(cx, cy):
    poly([(cx - 4, cy - 13), (cx + 4, cy - 13), (cx + 5, cy + 4),
          (cx - 5, cy + 4)], INK)
    poly([(cx - 5, cy + 2), (cx - 11, cy + 9), (cx - 5, cy + 6)], INK)
    poly([(cx + 5, cy + 2), (cx + 11, cy + 9), (cx + 5, cy + 6)], INK)
    poly([(cx - 3, cy + 5), (cx + 3, cy + 5), (cx, cy + 12)], RED)


def pic_coin(cx, cy):
    circle(cx, cy, 12, INK, 2)
    circle(cx, cy, 7, INK, 1)
    fill_circle(cx, cy, 2, RED)


def pic_book(cx, cy):
    fill_rect(cx - 12, cy - 9, cx + 12, cy + 9, INK)
    fill_rect(cx - 9, cy - 6, cx + 9, cy + 6, CREAM)
    line(cx, cy - 6, cx, cy + 6, INK, 1)
    for dy in (-3, 1):
        line(cx - 8, cy + dy, cx - 2, cy + dy, INK, 1)
        line(cx + 2, cy + dy, cx + 8, cy + dy, INK, 1)


def pic_factory(cx, cy):
    fill_rect(cx - 13, cy - 2, cx + 13, cy + 10, INK)
    fill_rect(cx - 10, cy - 12, cx - 6, cy - 2, INK)
    fill_rect(cx - 2, cy - 12, cx + 2, cy - 2, INK)
    fill_rect(cx + 6, cy + 2, cx + 10, cy + 6, RED)


PICS = {
    'shield': pic_shield, 'building': pic_building, 'chart': pic_chart,
    'tanker': pic_tanker, 'flask': pic_flask, 'globe': pic_globe,
    'megaphone': pic_megaphone, 'capitol': pic_capitol,
    'rocket': pic_rocket, 'coin': pic_coin, 'book': pic_book,
    'factory': pic_factory,
}

# ---------------------------------------------------------------- layout
# One slice per story. mid = (k-0.5)*30 degrees clockwise from top.
# The text block is centred at polar(BLOCK_R, mid) and laid out in
# screen coordinates: two big headline lines, then one short fact line.
# Offsets are screen-y pixels from the block centre. The pictogram sits
# on the mid-ray inside the text block (toward the rosette), clear of
# the text boxes.
BLOCK_R = 280
HEAD_OFF = (-34, -2)
BODY_OFF = (36,)
PIC_R = 190

SLICES = [
    # (headline 2 lines, one short fact line, pictogram)
    (["NATO", "ON POLAND"],
     ["3 MISSILES"],
     'shield'),
    (["DYMER", "TOLL 11"],
     ["BOY 7 ALIVE"],
     'building'),
    (["NIKKEI", "FALLS 5%"],
     ["AI SELL-OFF"],
     'chart'),
    (["IRAN", "ALL MEANS"],
     ["DEAL IN 2027"],
     'tanker'),
    (["GAZA", "99% TOXIC"],
     ["POLLUTION"],
     'flask'),
    (["ZELENSKYY", "SEEKS TALKS"],
     ["4-WAY TALKS"],
     'globe'),
    (["BELGIUM", "SHUTDOWN"],
     ["FLIGHTS CUT"],
     'megaphone'),
    (["INDIA", "AIDS NEPAL"],
     ["$1.6BN AID"],
     'capitol'),
    (["MERCURY", "ARRIVAL"],
     ["8-YEAR TRIP"],
     'rocket'),
    (["PENNY", "ENDS"],
     ["232-YEAR RUN"],
     'coin'),
    (["SEOUL", "RESIGNS"],
     ["EXAM SCANDAL"],
     'book'),
    (["YEMEN", "OIL STRIKE"],
     ["REFINERY HIT"],
     'factory'),
]

SUBTITLE = [
    "NATO over Poland missiles \u00b7 Dymer toll 11 \u00b7 Nikkei -5.06%",
    "Iran vows all means \u00b7 Gaza 99% toxic \u00b7 Zelenskyy talks",
    "Belgium airports shut \u00b7 India gives Nepal $1.6bn aid",
]


def _boxes_overlap(a, b):
    return a[0] <= b[2] and b[0] <= a[2] and a[1] <= b[3] and b[1] <= a[3]


def pic_offset(k, head, body, bx, by):
    """Pick the pictogram angle (mid-ray, or shifted) that clears the text.

    The pictogram box must not touch any headline/content line box, and
    the pictogram centre must stay >= 39px from the number-circle centre.
    """
    mid = (k - 0.5) * 30
    a1 = (k - 1) * 30
    a2 = k * 30
    boxes = []
    for i, h in enumerate(head):
        w = text_width(h, 1.9)
        lcx = line_cx(by + HEAD_OFF[i], 28, a1, a2, bx, w)
        boxes.append((lcx - w / 2 - 3, by + HEAD_OFF[i] - 3,
                      lcx + w / 2 + 3, by + HEAD_OFF[i] + 31))
    for j, ln in enumerate(body):
        w = text_width(ln, 1.6, mono=False)
        lcx = line_cx(by + BODY_OFF[j], 24, a1, a2, bx, w)
        boxes.append((lcx - w / 2 - 3, by + BODY_OFF[j] - 3,
                      lcx + w / 2 + 3, by + BODY_OFF[j] + 27))
    nx, ny = polar(NUM_R, mid)
    for off in (0, -14, 14, -24, 24):
        px, py = polar(PIC_R, mid + off)
        pb = (px - 16, py - 16, px + 16, py + 16)
        if any(_boxes_overlap(pb, b) for b in boxes):
            continue
        if ((px - nx) ** 2 + (py - ny) ** 2) ** 0.5 < 39:
            continue
        if off != 0:
            print("pic %d: offset %+d deg" % (k, off), file=sys.stderr)
        return off
    print("pic %d: no clear offset, using 0" % k, file=sys.stderr)
    return 0


def draw_slice(k, head, body, pic):
    mid = (k - 0.5) * 30
    a1 = (k - 1) * 30
    a2 = k * 30
    bx, by = polar(BLOCK_R, mid)
    bx, by = int(round(bx)), int(round(by))
    # pictogram (angle chosen to clear text and the number circle)
    off = pic_offset(k, head, body, bx, by)
    px, py = polar(PIC_R, mid + off)
    PICS[pic](int(round(px)), int(round(py)))
    # headlines, bold monospace, centred inside their wedge span
    for i, h in enumerate(head):
        top = by + HEAD_OFF[i]
        check_line("slice %d head %d" % (k, i + 1), h, top, 28, 1.9, a1, a2)
        text_c(h, line_cx(top, 28, a1, a2, bx, text_width(h, 1.9)), top, 1.9, 3.4, INK, bold=True)
    # one short fact line, proportional
    for j, ln in enumerate(body):
        top = by + BODY_OFF[j]
        check_line("slice %d body %d" % (k, j + 1), ln, top, 24, 1.6, a1, a2,
                   mono=False)
        text_c(ln, line_cx(top, 24, a1, a2, bx, text_width(ln, 1.6, mono=False)), top, 1.6, 3.0, INK, mono=False)
    # red sparkles, scattered inside the wedge
    for (r, ang) in ((330, mid - 13), (120, mid + 14)):
        sxp, syp = polar(r, ang)
        star4(int(round(sxp)), int(round(syp)), 7, RED)


def draw():
    # masthead
    fill_rect(437, 20, 587, 68, RED)
    text_c("The World", 512, 25, 1.8, 1.8, WHITE, bold=True)
    text_c("In One Day", 512, 45, 1.8, 1.8, WHITE, bold=True)
    # title, date, subtitle
    text_c("THE WORLD IN ONE DAY", 512, 84, 7, 8.5, INK, bold=True)
    text_c("MONDAY \u00b7 23 NOVEMBER 2026", 512, 162, 10 / 3, 3.2, RED, bold=True)
    for i, ln in enumerate(SUBTITLE):
        text_c(ln, 512, 190 + i * 28, 1.8, 3.1, INK, italic=True, mono=False)
    # wheel: rim and spokes first, text and icons on top
    circle(CX, CY, RIM, INK, 3)
    for k in range(12):
        a = _deg2rad(k * 30)
        x0 = CX + 62 * sin(a)
        y0 = CY - 62 * cos(a)
        x1 = CX + 348 * sin(a)
        y1 = CY - 348 * cos(a)
        line(int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1)),
             INK, 2)
    # number circles
    for k in range(1, 13):
        mid = (k - 0.5) * 30
        nx, ny = polar(NUM_R, mid)
        nx, ny = int(round(nx)), int(round(ny))
        fill_circle(nx, ny, NUM_CIRCLE_R, WHITE)
        circle(nx, ny, NUM_CIRCLE_R, INK, 2)
        text_c(str(k), nx, ny - 9, 2.2, 2.2, INK, bold=True)
    # rosette
    fill_circle(CX, CY, ROSETTE, RED)
    fill_circle(CX, CY, ROSETTE - 3, INK)
    text_c("23", CX, CY - 24, 6, 7, WHITE, bold=True)
    # slices
    for k, (head, body, pic) in enumerate(SLICES, start=1):
        draw_slice(k, head, body, pic)


# ---------------------------------------------------------------- png
def png_bytes():
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw.extend(buf[y * W * 3:(y + 1) * W * 3])
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff))

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


def main():
    draw()
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "entry.png")
    with open(path, "wb") as f:
        f.write(png_bytes())
    print("wrote %s (%d bytes)" % (path, os.path.getsize(path)))


if __name__ == "__main__":
    main()
