"""GreenNode footer key visual: the pixel claw lifting a sensitive workload out of
a pile of workload blocks that crumbles into pixels at its top edge.

Writes footer-kv-<theme>.svg (1440 x 480). Rasterise to PNG with render.sh.
Run:  python generate_claw.py [seed]
"""
import sys, os, json, random

OUT = os.path.dirname(os.path.abspath(__file__))
ICONS = json.load(open(os.path.join(OUT, 'icons.json')))
W, H = 1440, 480
SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 3

PITCH, TILE, R = 80, 70, 10          # workload block grid (px)
PX = TILE / 5                        # crumb pixel = 1/5 of a block
NCOL = W // PITCH + 1                # 19 columns, last one bleeds off the right edge
X0 = (W - (NCOL - 1) * PITCH - TILE) / 2 + PITCH / 2 - PITCH / 2  # centred grid
FLOOR = H                            # bottom row sits flush with the bottom edge (bleeds slightly)

# claw (pixel version from hyper/story.js, 20 x 24 px)
CLAW_PAL = {'W': '#ffffff', 'L': '#d4ffe4', 'M': '#b4ffd0', 'D': '#0a602a', 'K': '#00210d'}
PX_TOP = ['........KKKK........', '........KWLK........', '.....KKKKKKKKKK.....', '....KWWWWWWWWWLK....',
          '....KWMMMMMMMMLK....', '....KWMKMKMKMMLK....', '....KLLLLLLLLLLK....', '.....KKKKKKKKKK.....',
          '.......KWWLLK.......', '....KKWWWWWLLLKK....', '...LW..........WL...', '..LW............WL..', '.LW..............WL.']
PX_CLOSED = ['.KK..............KK.', '.KK..............KK.', '.LW..............WL.', '.LW..............WL.', '.LW..............WL.',
             '.LW..............WL.', '.LW..............WL.', '..LW............WL..', '...LW..........WL...', '....LWD......DWL....']
PX_OPEN = ['KK................KK', 'KK................KK', 'LW................WL', 'LW................WL', 'LW................WL',
           'LW................WL', 'LW................WL', 'LW................WL', 'DW................WD']

THEMES = {
    # board green (the KV "Vietnam zone"), teal workload pile = global cloud
    'green': dict(bg='#0cc050', dots='#0aa043', rail='#ffffff', cable='#ffffff',
                  gen=['#0f3b3b', '#1a4d4b', '#22605c', '#2c716c'], gen_ic='#cfe9e4', crumb_extra='#0a602a'),
    # dark global-cloud teal
    'dark': dict(bg='#0b2b2b', dots='#164343', rail='#d4ffe4', cable='#d4ffe4',
                  gen=['#1a4d4b', '#22605c', '#2c716c', '#3c8580'], gen_ic='#cfe9e4', crumb_extra='#0cc050'),
    # light page footer
    'light': dict(bg='#f4f6f2', dots='#dfe5dd', rail='#0f3b3b', cable='#0f3b3b',
                  gen=['#0f3b3b', '#1a4d4b', '#22605c', '#2c716c'], gen_ic='#cfe9e4', crumb_extra='#0cc050',
                  sens_shadow='#cfd8cc'),
}

SENSITIVE = ['db', 'pay', 'kyc', 'ai']
GENERAL_IC = ['cdn', 'media', 'web', 'dev']


def icon(key, x, y, size, colour, cut):
    """Icon with explicit fills/strokes (no CSS classes or variables) so it imports cleanly into Figma."""
    s = size / 24
    body = (ICONS[key]
            .replace('class="gs"', f'fill="none" stroke="{colour}" stroke-linecap="round" stroke-linejoin="round"')
            .replace('class="cs"', f'fill="none" stroke="{cut}" stroke-linecap="round" stroke-linejoin="round"')
            .replace('class="g"', f'fill="{colour}" stroke="{colour}" stroke-width=".9" stroke-linejoin="round"')
            .replace('class="c"', f'fill="{cut}" stroke="{cut}" stroke-width=".6" stroke-linejoin="round"'))
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.4f})">{body}</g>'


def block(x, y, fill, ic=None, ic_col=None, lock=False, shadow=None):
    out = []
    if shadow:
        out.append(f'<rect x="{x}" y="{y+8}" width="{TILE}" height="{TILE}" rx="{R}" fill="{shadow}"/>')
    out.append(f'<rect x="{x}" y="{y}" width="{TILE}" height="{TILE}" rx="{R}" fill="{fill}"/>')
    if ic:
        out.append(icon(ic, x + (TILE - 32) / 2, y + (TILE - 32) / 2, 32, ic_col, fill))
    if lock:
        cx, cy = x + TILE - 2, y + 2
        out.append(f'<circle cx="{cx}" cy="{cy}" r="11" fill="#ffffff"/><circle cx="{cx}" cy="{cy}" r="9.5" fill="#0db14b"/>')
        out.append(icon('lockClosed', cx - 7, cy - 7, 14, '#ffffff', '#0db14b'))
    return ''.join(out)


def claw_px(x, y, s, rows):
    out = []
    for j, row in enumerate(rows):
        i = 0
        while i < len(row):
            ch = row[i]
            if ch == '.':
                i += 1; continue
            k = i
            while k + 1 < len(row) and row[k + 1] == ch:
                k += 1
            out.append(f'<rect x="{x+i*s}" y="{y+j*s}" width="{(k-i+1)*s}" height="{s}" fill="{CLAW_PAL[ch]}"/>')
            i = k + 1
    return ''.join(out)


def build(theme, name, claw_col, lifted='db', grip='closed'):
    t = THEMES[theme]
    rnd = random.Random(SEED * 31 + len(name))
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" shape-rendering="crispEdges">',
         f'<rect width="{W}" height="{H}" fill="{t["bg"]}"/>',
         '<g id="Dot grid">' + ''.join(f'<rect x="{x+11}" y="{y+11}" width="2" height="2" fill="{t["dots"]}"/>'
                                      for y in range(0, H, 24) for x in range(0, W, 24)) + '</g>']

    # ---- pile height per column: a soft hill with a dip under the claw ----
    xs = [X0 + c * PITCH for c in range(NCOL)]
    claw_c = min(range(NCOL), key=lambda c: abs(xs[c] + TILE / 2 - claw_col))
    heights = []
    for c in range(NCOL):
        u = c / (NCOL - 1)
        h = 1.6 + 1.5 * (0.5 + 0.5 * __import__('math').sin(u * 5.2 + 0.6)) + rnd.uniform(-0.5, 0.5)
        heights.append(max(1, min(3, round(h))))
    heights[claw_c] = max(1, heights[claw_c])

    # pick some sensitive (white) blocks inside the pile, never two side by side on one row
    sens_slots = set()
    pool = SENSITIVE[:] * 2
    rnd.shuffle(pool)
    for c in rnd.sample(range(NCOL), 5):
        if c == claw_c:
            continue
        sens_slots.add((c, rnd.randrange(heights[c])))

    crumbs = []
    ic_cycle = GENERAL_IC[:] * 4
    rnd.shuffle(ic_cycle)
    for c in range(NCOL):
        x = xs[c]
        top_y = None
        for r in range(heights[c]):
            y = FLOOR - (r + 1) * PITCH + (PITCH - TILE)
            is_top = r == heights[c] - 1
            if c == claw_c and is_top:
                # the slot the claw just emptied: dashed socket
                p.append(f'<rect x="{x+1}" y="{y+1}" width="{TILE-2}" height="{TILE-2}" rx="{R}" fill="none" '
                         f'stroke="{t["rail"]}" stroke-opacity=".6" stroke-width="2" stroke-dasharray="6 5"/>')
                top_y = y
                continue
            if (c, r) in sens_slots:
                p.append(block(x, y, '#ffffff', pool.pop(), '#0db14b', lock=True, shadow=t.get('sens_shadow')))
            elif is_top and rnd.random() < 0.4:
                # top block breaking up into pixels (5 x 5 sub-grid, upper rows erode)
                col = rnd.choice(t['gen'])
                for j in range(5):
                    for i in range(5):
                        keep = rnd.random() < (0.35 + j * 0.17)
                        if keep:
                            p.append(f'<rect x="{x+i*PX:.1f}" y="{y+j*PX:.1f}" width="{PX:.1f}" height="{PX:.1f}" fill="{col}"/>')
            else:
                col = rnd.choice(t['gen'])
                ic = ic_cycle.pop() if rnd.random() < 0.3 and ic_cycle else None
                p.append(block(x, y, col, ic, t['gen_ic']))
            top_y = y
        # crumbs floating above the column, thinning out upward
        for k in range(rnd.randint(2, 7)):
            cy = top_y - PX * (1 + int(rnd.expovariate(0.55)))
            cx = x + PX * rnd.randrange(5)
            if cy > 150:
                crumbs.append((cx, cy, rnd.choice(t['gen'] + [t['crumb_extra']])))
    for cx, cy, col in crumbs:
        p.append(f'<rect x="{cx:.1f}" y="{cy:.1f}" width="{PX:.1f}" height="{PX:.1f}" fill="{col}"/>')

    # ---- rail ----
    ry = 44
    p.append(f'<rect x="64" y="{ry-1}" width="{W-128}" height="2" fill="{t["rail"]}"/>')
    p.append(f'<rect x="58" y="{ry-6}" width="12" height="12" rx="3" fill="{t["rail"]}"/>')
    p.append(f'<rect x="{W-70}" y="{ry-6}" width="12" height="12" rx="3" fill="{t["rail"]}"/>')

    # ---- claw holding the lifted workload ----
    s = 6
    cw = 20 * s
    cx = xs[claw_c] + TILE / 2 - cw / 2
    cy = 92
    for yy in range(ry + 1, int(cy), 7):        # dashed cable
        p.append(f'<rect x="{cx+cw/2-1.5}" y="{yy}" width="3" height="4" fill="{t["cable"]}"/>')
    arms = PX_CLOSED if grip == 'closed' else PX_OPEN
    tile_y = cy + 13 * s - 4
    p.append(block(cx + (cw - TILE) / 2, tile_y, '#ffffff', lifted, '#0db14b', lock=True, shadow='#0a602a'))
    p.append(claw_px(cx, cy, s, PX_TOP + arms))
    p.append('</svg>')
    path = os.path.join(OUT, f'footer-kv-{name}.svg')
    open(path, 'w').write('\n'.join(p))
    return path


def web_edge(name, bg, band=240, px=16):
    """Website version: same art pushed down by `band`, whose top dissolves into loose pixels
    (dense at the bottom, sparse at the top) so it blends into the light section above."""
    rnd = random.Random(SEED * 7 + 1)
    src = open(os.path.join(OUT, f'footer-kv-{name}.svg')).read()
    body = src.split('>', 1)[1].rsplit('</svg>', 1)[0]
    H2 = H + band
    rows = band // px
    accents = ['#1a4d4b', '#22605c', '#0cc050']
    cells = []
    for r in range(rows + 1):                         # last row overlaps the scene top to break its straight edge
        dens = (r + 0.6) / (rows + 0.6)
        dens = dens ** 3.2                            # tall band: very sparse at the top, dense near the scene
        for x in range(0, W, px):
            if r == rows:
                if rnd.random() < 0.12:               # a few notches cut into the scene edge
                    cells.append((x, r * px, None))
                continue
            if rnd.random() < dens:
                a = rnd.random()
                col = bg if a > 0.12 else rnd.choice(accents)
                cells.append((x, r * px, col))
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H2}" width="{W}" height="{H2}" shape-rendering="crispEdges">',
           f'<g id="Scene" transform="translate(0 {band})">{body}</g>', '<g id="Dissolve">']
    for x, y, col in cells:
        out.append(f'<rect x="{x}" y="{y}" width="{px}" height="{px}" fill="{col or "#f5f5f5"}"/>')
    out.append('</g></svg>')
    open(os.path.join(OUT, f'footer-kv-{name}-web.svg'), 'w').write(''.join(out))


if __name__ == '__main__':
    build('green', 'green', W * 0.62, 'db')
    build('dark', 'dark', W * 0.5, 'ai')
    build('light', 'light', W * 0.3, 'pay')
    web_edge('dark', THEMES['dark']['bg'])
    print('done')
