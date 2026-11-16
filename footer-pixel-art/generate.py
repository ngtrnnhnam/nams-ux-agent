"""GreenNode pixel footer art generator.

Builds 5 footer illustrations on a square-pixel grid (1440 x 400 logical px,
16 px cells -> 90 x 25 grid) and writes each as SVG (crisp, editable in Figma)
and PNG @2x. Run:  python generate.py  [seed]
"""
import sys, os
import numpy as np
from PIL import Image, ImageDraw

OUT = os.path.dirname(os.path.abspath(__file__))
W, H, CELL = 1440, 400, 16
COLS, ROWS = W // CELL, H // CELL
SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 7

# GreenNode palette (from the KV board)
INK = '#00210d'      # near-black green
TEAL = '#0f3b3b'     # global-zone teal
TEAL2 = '#2c716c'
DEEP = '#0a602a'
G700 = '#0a8538'
G500 = '#0db14b'
BRAND = '#0cc050'
G300 = '#3ad574'
MINT = '#b4ffd0'
MINT2 = '#d4ffe4'
WHITE = '#ffffff'
PAPER = '#f4f6f2'

BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16 + 1 / 32


def rng(k):
    return np.random.default_rng(SEED * 101 + k)


def fbm(cols, rows, r, octaves=4, base=6):
    """Smooth value noise in [0,1] on a cols x rows grid."""
    out = np.zeros((rows, cols))
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        n = base * 2 ** o
        gw, gh = n + 2, max(2, int(n * rows / cols) + 2)
        g = r.random((gh, gw))
        ys = np.linspace(0, gh - 1.001, rows)
        xs = np.linspace(0, gw - 1.001, cols)
        y0, x0 = ys.astype(int), xs.astype(int)
        ty, tx = ys - y0, xs - x0
        ty, tx = ty * ty * (3 - 2 * ty), tx * tx * (3 - 2 * tx)
        a = g[y0][:, x0]; b = g[y0][:, x0 + 1]
        c = g[y0 + 1][:, x0]; d = g[y0 + 1][:, x0 + 1]
        top = a + (b - a) * tx; bot = c + (d - c) * tx
        out += amp * (top + (bot - top) * ty[:, None])
        tot += amp; amp *= 0.5
    out /= tot
    return (out - out.min()) / (out.max() - out.min())


def bayer(cols, rows):
    return np.tile(BAYER4, (rows // 4 + 1, cols // 4 + 1))[:rows, :cols]


# ---------- writers ----------
def write(name, grid, bg, shape=None, gridline=None, dots=None):
    """grid: rows x cols array of colour strings (None = background).
    shape: optional rows x cols array of 'sq' / 'ci' per cell (default square).
    gridline: colour of hairline grid drawn over everything (ref: heat map).
    dots: (colour, step) faint dot pattern on the background."""
    rows, cols = grid.shape
    # SVG -- merge horizontal runs of equal squares to keep files small
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" shape-rendering="crispEdges">',
             f'<rect width="{W}" height="{H}" fill="{bg}"/>']
    if dots:
        dc, st = dots
        parts.append(f'<defs><pattern id="d" width="{st}" height="{st}" patternUnits="userSpaceOnUse">'
                     f'<circle cx="{st/2}" cy="{st/2}" r="1.5" fill="{dc}"/></pattern></defs>'
                     f'<rect width="{W}" height="{H}" fill="url(#d)"/>')
    for y in range(rows):
        x = 0
        while x < cols:
            c = grid[y, x]
            if c is None:
                x += 1; continue
            if shape is not None and shape[y, x] == 'ci':
                parts.append(f'<circle cx="{x*CELL+CELL/2}" cy="{y*CELL+CELL/2}" r="{CELL/2-1}" fill="{c}" shape-rendering="auto"/>')
                x += 1; continue
            x2 = x
            while x2 + 1 < cols and grid[y, x2 + 1] == c and (shape is None or shape[y, x2 + 1] != 'ci'):
                x2 += 1
            parts.append(f'<rect x="{x*CELL}" y="{y*CELL}" width="{(x2-x+1)*CELL}" height="{CELL}" fill="{c}"/>')
            x = x2 + 1
    if gridline:
        p = ''.join(f'M{x*CELL} 0V{H}' for x in range(1, cols)) + ''.join(f'M0 {y*CELL}H{W}' for y in range(1, rows))
        parts.append(f'<path d="{p}" stroke="#ffffff" stroke-opacity="{gridline[3]/255:.2f}" stroke-width="1" fill="none"/>')
    parts.append('</svg>')
    with open(os.path.join(OUT, name + '.svg'), 'w') as f:
        f.write('\n'.join(parts))

    # PNG @2x
    s = 2
    im = Image.new('RGB', (W * s, H * s), bg)
    dr = ImageDraw.Draw(im)
    if dots:
        dc, st = dots
        for yy in range(0, H, st):
            for xx in range(0, W, st):
                cx, cy = (xx + st / 2) * s, (yy + st / 2) * s
                dr.ellipse([cx - 1.5 * s, cy - 1.5 * s, cx + 1.5 * s, cy + 1.5 * s], fill=dc)
    for y in range(rows):
        for x in range(cols):
            c = grid[y, x]
            if c is None:
                continue
            box = [x * CELL * s, y * CELL * s, (x + 1) * CELL * s - 1, (y + 1) * CELL * s - 1]
            if shape is not None and shape[y, x] == 'ci':
                dr.ellipse([box[0] + s, box[1] + s, box[2] - s, box[3] - s], fill=c)
            else:
                dr.rectangle(box, fill=c)
    if gridline:
        ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        for x in range(1, cols):
            od.line([(x * CELL * s, 0), (x * CELL * s, H * s)], fill=gridline, width=s)
        for y in range(1, rows):
            od.line([(0, y * CELL * s), (W * s, y * CELL * s)], fill=gridline, width=s)
        im = Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB')
    im.save(os.path.join(OUT, name + '@2x.png'), optimize=True)


def empty():
    return np.full((ROWS, COLS), None, dtype=object)


# ---------- 01 · Rising tide: brand green floor dissolving up into white (ref 4) ----------
def v1():
    r = rng(1)
    n = fbm(COLS, ROWS, r, 3, 4)
    yy = np.linspace(0, 1, ROWS)[:, None]
    # coastline height wanders across the width
    h = 0.34 + 0.22 * (fbm(COLS, 1, rng(11), 3, 3)[0] - 0.5) * 2
    field = (yy - (1 - h)[None, :]) * 2.4 + (n - 0.5) * 0.7      # >0 -> inside the green
    g = empty()
    noise = r.random((ROWS, COLS))
    inside = field > 0
    g[inside] = BRAND
    # ragged edge: stray pixels above, holes below
    above = (field > -0.6) & ~inside & (noise < (0.6 + field) ** 2 * 1.4)
    g[above] = BRAND
    holes = inside & (field < 0.25) & (noise < 0.18)
    g[holes] = None
    # a few mint highlights inside the mass
    g[inside & (noise > 0.94)] = MINT
    write('footer-01-rising-tide', g, WHITE)


# ---------- 02 · Heat map: thermal field in the green scale, hairline grid (ref 2) ----------
def v2():
    r = rng(2)
    n = fbm(COLS, ROWS, r, 3, 2)
    n = n * n * (3 - 2 * n)                               # push towards the extremes
    n = n * n * (3 - 2 * n)
    d = bayer(COLS, ROWS)
    levels = [INK, TEAL, DEEP, G500, BRAND, MINT, WHITE]
    q = n * (len(levels) - 1) + (d - 0.5) * 0.7          # ordered dither between neighbouring bands
    q = np.clip(np.round(q), 0, len(levels) - 1).astype(int)
    g = np.vectorize(lambda i: levels[i], otypes=[object])(q)
    # flecks where two bands meet (like the red specks in the reference)
    nb = np.zeros_like(q, bool)
    for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        nb |= np.roll(q, (dy, dx), (0, 1)) != q
    fl = nb & (r.random((ROWS, COLS)) < 0.08)
    g[fl & (q >= 4)] = G700
    g[fl & (q <= 2)] = G300
    write('footer-02-heat-map', g, WHITE, gridline=(255, 255, 255, 90))


# ---------- 03 · Twin mounds on dark: square pixels left, round pixels right (ref 3) ----------
def v3():
    r = rng(3)
    g, shp = empty(), np.full((ROWS, COLS), 'sq', dtype=object)
    xs = np.arange(COLS)
    noise = r.random((ROWS, COLS))
    tone = r.random((ROWS, COLS))
    for side in ('L', 'R'):
        if side == 'L':
            dist = xs / (COLS * 0.32)                           # 0 at left edge
        else:
            dist = (COLS - 1 - xs) / (COLS * 0.30)
        top = ROWS * (0.12 + 0.88 * np.clip(dist, 0, 1.2) ** 1.4)  # column height
        top += (fbm(COLS, 1, rng(30 + (side == 'R')), 3, 5)[0] - 0.5) * 6
        for x in range(COLS):
            if dist[x] > 1.15:
                continue
            for y in range(ROWS):
                depth = y - top[x]
                if depth > 0 or (depth > -3 and noise[y, x] < 0.25 + depth * 0.08):
                    t = tone[y, x]
                    c = MINT2 if t > 0.86 else MINT if t > 0.62 else G300 if t > 0.25 else BRAND
                    if side == 'R':
                        c = MINT2 if t > 0.85 else G300 if t > 0.3 else G500
                        shp[y, x] = 'ci'
                    g[y, x] = c
    write('footer-03-twin-mounds', g, INK, shape=shp, dots=('#1d4a30', 24))


# ---------- 04 · Ribbon: a fat dithered band sweeping across paper (ref 1) ----------
def v4():
    r = rng(4)
    g = empty()
    yy, xx = np.mgrid[0:ROWS, 0:COLS]
    u = np.arange(COLS) / (COLS - 1)
    centre = ROWS * (1.05 - 1.05 * u + 0.28 * np.sin(np.pi * u * 2.2)) + (fbm(COLS, 1, rng(41), 2, 2)[0] - 0.5) * 3
    half = 5.2 + 1.0 * np.sin(u * 6)
    dist = np.abs(yy - centre[None, :]) - half[None, :]
    noise = r.random((ROWS, COLS))
    band = (dist < 0) | ((dist < 1.4) & (noise < 0.45 - dist * 0.25))
    # colour runs along the band: teal -> brand -> mint, blended with Bayer dither
    d = bayer(COLS, ROWS)
    seg = (fbm(COLS, 1, rng(42), 2, 2)[0] * 0.5 + u * 0.5)[None, :].repeat(ROWS, 0)
    stops = [TEAL, DEEP, BRAND, MINT]
    q = np.clip(np.floor(seg * len(stops) + (d - 0.5) * 1.3), 0, len(stops) - 1).astype(int)
    for (y, x) in zip(*np.nonzero(band)):
        c = stops[q[y, x]]
        # checker texture inside the dark segment, sparse light flecks in the bright one
        if c == DEEP and (x + y) % 2 == 0 and noise[y, x] < 0.55:
            c = INK
        if c == BRAND and noise[y, x] > 0.9:
            c = MINT2
        g[y, x] = c
    # offset print shadow: a 1-cell blue-green misregistration under the band edge
    sh = np.zeros_like(band); sh[1:, 1:] = band[:-1, :-1]       # shift down-right without wrapping
    sh &= ~band & (noise < 0.6)
    g[sh] = G300
    write('footer-04-ribbon', g, PAPER)


# ---------- 05 · Skyline: solid deep floor breaking into a pixel edge, cross marks (ref 4, inverted) ----------
def v5():
    r = rng(5)
    g = empty()
    edge = 9 + (fbm(COLS, 1, rng(51), 4, 6)[0] - 0.5) * 7
    noise = r.random((ROWS, COLS))
    for x in range(COLS):
        for y in range(ROWS):
            depth = y - edge[x]
            if depth >= 0:
                g[y, x] = TEAL
                if depth < 2 and noise[y, x] < 0.22:
                    g[y, x] = None
            elif depth > -6 and noise[y, x] < 0.5 + depth * 0.09:
                g[y, x] = TEAL if depth > -2 else G500 if noise[y, x] < 0.12 else TEAL
    # a few brand-green "workload" pixels inside the floor
    floor = np.array([[c == TEAL for c in row] for row in g])
    g[floor & (noise > 0.975)] = BRAND
    write('footer-05-skyline', g, WHITE)
    # draw the ✛ marks directly into the files (thin strokes, like ref 4)
    for ext in ('.svg',):
        p = os.path.join(OUT, 'footer-05-skyline' + ext)
        s = open(p).read()
        marks = ''.join(f'<path d="M{x} {y-12}V{y+12}M{x-12} {y}H{x+12}" stroke="{TEAL}" stroke-width="2.5"/>'
                        for (x, y) in [(136, 56), (720, 40), (1304, 56)])
        open(p, 'w').write(s.replace('</svg>', marks + '</svg>'))
    p = os.path.join(OUT, 'footer-05-skyline@2x.png')
    im = Image.open(p); dr = ImageDraw.Draw(im)
    for (x, y) in [(136, 56), (720, 40), (1304, 56)]:
        dr.line([(x * 2, (y - 12) * 2), (x * 2, (y + 12) * 2)], fill=TEAL, width=5)
        dr.line([((x - 12) * 2, y * 2), ((x + 12) * 2, y * 2)], fill=TEAL, width=5)
    im.save(p, optimize=True)


for f in (v1, v2, v3, v4, v5):
    f()
print('done ->', OUT)
