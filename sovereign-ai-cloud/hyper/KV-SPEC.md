# KV · Hyper-Targeted claw machine: spec for an LLM or developer

Give your LLM `design-tokens.json` (same folder) plus this file. The Figma source is section "KV · Hyper-Targeted claw", block "5 · Design tokens".

## What it is
A pixel-style claw machine that carries 4 sensitive workloads (Customer data, Payments, eKYC, AI training) from the Global cloud (dark teal, bottom) into two Vietnam data-centre pedestals (green, top), HAN and HCM. General workloads (CDN, Media, Website, Dev / Test and unlabeled tiles) stay in the Global cloud.

## Rules to follow
1. Use only the tokens in `design-tokens.json`. Never invent colours. CSS variable names are in `color.semantic[*].css` (`--kv-*`).
2. Every length is in board units: a board is 400 × 670, and in CSS each unit is `calc(var(--sov-u) * N)` with `--sov-u = boardWidth / 400`.
3. All KV text is JetBrains Mono Bold at the sizes in `geometry`.
4. Corners: tile 66 → radius 10, pedestal top 12 / front 9, lock badge and LED are round. The claw is the only pixel-art element (20 × 24 grid, 4.5 units per pixel, `crispEdges`).
5. Icons: 24 × 24 grid, filled and rounded. The glyph uses `currentColor`; cut-outs are holes showing the surface colour (`--ic-cut`).
6. A sensitive tile has 4 states: Hidden → Tagged → Crossed → Home. State colours are in `components["Workload tile"].states`.
7. Positions: use `geometry.globalGrid`, `geometry.pedestal` and `geometry.homeTile.slots` exactly; do not re-derive them.

## Build order
1. Colour variables → 2. Icons and claw (3 grips) → 3. Parts: Global tile, Workload tile, Lock badge, LED, DC pedestal, Zone label, Claw rail, Border → 4. Boards (01 Classify, 03 Carry, 06 Sealed, 07 Sealed) composed only from the parts → 5. Footer KV (1440 × 480).

## Motion (only if asked to animate)
Follow `story.beats`. Progress `T` is a pure function of scroll, so scrolling up reverses the story. Hero autoplays in 7 s with `data-mode="c"`. Enable only at min-width 992 px, min-height 480 px and without `prefers-reduced-motion`.

## Reference implementation
`hyper/story.js` (behaviour), `hyper/claw.css` (look), `hyper/story.css` (section 2 and outro), `hyper/footer-kv.css` (footer).
