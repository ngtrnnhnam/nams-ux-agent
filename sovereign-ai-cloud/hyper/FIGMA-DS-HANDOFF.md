# Handoff: GreenNode design system (website + KV) for the Figma agent

Goal: organise and complete one coherent design system in Figma from what has already been built. Work from the existing assets first, and add only what is missing.

## 1. Where everything is

- **Figma file:** `ufc1A7ncZxBWHDe0v335z1` (campaign file "nhà mới")
- **Local code:** `/Applications/Test Claude/sovereign-ai-cloud/`
  - `hyper.html`: the live page, with the hero that autoplays and the new footer
  - `hyper-c.html`: a comparison copy of the same hero
  - `hyper/story.js`, `hyper/claw.css`, `hyper/story.css`: the KV scene and scroll story
  - `hyper/footer-kv.css`: footer graphic
  - `hyper/design-tokens.json`: KV tokens for LLMs
  - `hyper/KV-SPEC.md`: KV build spec
  - `styles.css`: the original website CSS (source of website tokens)
- **Scratch state:** `/private/tmp/claude-501/-Users-lap16105--claude-spares-spare-hg33HW/2083fee4-19c7-46d7-8bf4-702f8fc950fe/scratchpad/ds-website-state.json`

## 2. Figma pages and IDs

| Page | ID | Contents |
|---|---|---|
| Campaign Sovereign LDP | `2382:10747` | KV section `5208:6199` (claw, pixel art, parts, boards, footer KV, tokens block) |
| GreenNode / Local Design System | `4465:223179` | existing GN tokens (Primitives, Semantic, Layout) and text styles |
| Website Design System | `5322:6868` | foundations specimen (colours, type, radius, shadows, spacing) |
| Website Components | `5329:6868` | Actions, Navigation and cards, Sections (15 components) |
| Finalize GreenNode Design System | `4453:65570` | pre-existing; check before changing |

## 3. Existing variables (do not overwrite)

**GN (pre-existing, from the GreenNode file):**
- `GN / Primitives` (94 vars, one mode). Brand green `color/green/brand = #0DB14B`.
- `GN / Semantic` (44 vars, Light / Dark)
- `GN / Compatibility` (11 vars)
- `GN / Layout` (10 vars, Mobile / Tablet / Desktop): container 735, section 48, gutter 16

**Website (created in this session):**
- `GN / Website Primitives` (`VariableCollectionId:5321:7599`, 61 colours). Hues: primary, dark, light, darker, darkest, secondary, orange, green, status, info, neutral, text, alpha. Each carries its CSS name in WEB code syntax, e.g. `var(--v-primary-color)`.
- `GN / Website Semantic` (`5321:7661`, 40 aliases, scopes set). Groups: text/*, surface/*, border/*, action/* (primary, secondary, accent), feedback/error, pagination/inactive. Aliases point to Primitives.
- `GN / Website Dimension` (`5321:7702`, 20 vars, modes Mobile / Tablet / Desktop). Container padding, section padding, layout spacing, topbar/navbar height, radius (4, 6, 8, 10, 12, 15, 16, 24, 48, pill), breakpoints (576, 768, 992, 1200, 1600, 1920), `space/*`.

**KV (created earlier, bound in the KV section):**
- `GN / KV Claw` (`5208:6149`, 47 vars): `primitive/*` plus semantic `zone/*`, `tile/*`, `content/*`, `pedestal/*`, `led/*`, `lock/*`, `claw/*`. Each has WEB code syntax `var(--kv-*)`.
- `GN / KV Icon tone` (`5222:9120`, modes Protected / Exposed / Muted)

## 4. Text and effect styles

- `GN / Documentation / *` (Title, Section, Body, Caption) is used for doc headings.
- `GN / KV / *` (Tile label, Zone label, Pedestal label) is used by the KV.
- `GN / Typography / *` and `GN / Website / Typography / *` (18 Inter styles) are the website ramp. Names: Heading 54 / 46 / 45 / 36 / 28 / 24 / 22 / 20, Body 20 / 18 / 16 / 15 / 14, Caption 12.
- `GN / Website / Shadow / XS, SM, MD, LG, XL` (5 effect styles, from the site's box-shadow values)
- `GN / Effects / Focus ring / Light | Dark` and `GN / Website / Elevation / *` (pre-existing)

## 5. Components built

### KV (page `2382:10747`)
- **Claw** (`5211:6728`, Grip = Open | Half | Closed), pixel art, 20 × 24 px grid at 5 px per pixel
- **Claw / Head** (`5211:6153`)
- **Icons** (filled + rounded, 24 grid): KV Icon / Customer data `5211:6729`, Payments `5211:6794`, eKYC `5211:6853`, AI training `5211:6913`, Website `5211:6974`, CDN `5211:7043`, Dev-Test `5211:7113`, Media `5211:7132`
- **Glyphs:** Lock open `5211:7188`, Lock closed `5211:7235`, Shield `5211:7283`, Cloud `5211:7327`
- **Lock badge** (`5212:6578`, State = Open | Closed), **LED** (`5212:6581`, State = Off | On)
- **Workload tile** (`5212:6995`, State = Hidden | Tagged | Crossed | Home; Icon swap; Name)
- **Global tile** (`5212:7280`, Tone = 1–4; Show label; Icon swap; Name)
- **DC pedestal** (`5212:7281`), **Zone label** (`5212:7360`, Zone = Vietnam | Global; Protected), **Claw rail** (`5212:7361`), **Border dither** (`5212:7365`, older; the current border is the merlon row in frame `5292:93214`, unnamed)
- **Boards:** 01 Classify `5213:7034`, 03 Carry `5213:8601`, 06 Sealed `5213:10131`, 07 Sealed (current) `5273:92499`
- **Footer KV / Dark** (`5306:7599`, 1440 × 480)
- **5 · Design tokens** block (`5325:6869`) is a table, not a component

### Website (page `5329:6868`)
- **Actions:** Button / CTA `5329:6875` (State = Default | Hover | Active; Label). Button / Arrow CTA `5329:6884` (State = Default | Hover; Label). Tab / Pill `5329:6891` (State = Active | Inactive; Label). Nav link `5329:6892` (Label; Dropdown).
- **Navigation and cards** (section `5331:6922`):
  - Header / Topbar `5331:6868`, Navigation / Header `5331:6875`, Button / Pinned icon `5331:6899` (Kind = Top | Call), Section / Heading `5331:6906` (Align = Left | Center)
  - Card / Capability tile `5331:6907`, Card / Trust `5331:6912`, Card / Testimonial `5331:6917`
- **Sections and content cards** (section `5332:6973`):
  - Section / Capability panel `5332:6940` (tab bar + 3 tiles)
  - Card / Resource `5332:6906`, Card / Ebook `5332:6912`, Section / CTA band `5332:6921`, Section / Footer card `5332:6928`

## 6. Known gaps and things to fix

1. **Placeholders:** the logo (text "GREENNODE"), the Vietnamese Sovereign badge (black box), and all artwork (green squares) are placeholders. Replace them with the real assets from `assets/` in the code folder: `green_node_logo_color.svg`, `greennode_campaign_sovereign_footer_logo_*.svg`, `greennode_campaign_sovereign_*` icons and banners.
2. **Icons** in the website components are text glyphs (↑ ↗ → ✆), not vectors. Use the icon SVGs from `assets/` or the Tabler set.
3. **Not yet built:** FAQ / accordion, dropdown menu, form fields, toast, partner logo strip, pinned call button shape details, mobile breakpoints for each component.
4. **Hover / Active states** are inferred from CSS colour tokens, not checked on the live page.
5. **Section / Heading:** the Left and Center variants were built as separate components, but the set currently shows them side by side. Convert to one component with an Align property.
6. **Duplicate KV components:** "Border dither" (`5212:7365`) and the merlon row (`5292:93214`, unnamed) overlap. Keep the merlon row and retire the old one.
7. **Naming:** the frame `5292:93214` has no name. Rename it "Global border merlon".
8. **Footer KV SVG** is 123 KB and the vn map is 540 KB. Export smaller files before production.
9. **Mobile:** nothing has been checked below 992 px.
10. **Content** on KV is a draft; Content and Legal still need to approve it.

## 7. Decisions already made (keep them)

- New website tokens go in new collections (`GN / Website *`). Existing GN collections are not changed.
- Components bind to variables (fills, strokes, radius, padding, gap). No raw hex in components.
- The website is the source of truth for the website components; the KV board is the source for the KV components.
- Figma → website sync is done by asking Claude to read the Figma file, not by manual edits. Sync rules are in `hyper/KV-SPEC.md`.

## 8. What the Figma agent should do

1. Read this file, then read the page IDs above before changing anything.
2. Audit the three website collections for duplicates against GN / Semantic. Propose merges; do not merge without approval.
3. Group the 15 website components into one library page ("Website Components") with a clear section for each family: Actions, Navigation, Cards, Sections. Keep the names as they are now.
4. Add the missing components listed in section 6, item 3, only after the user approves each one.
5. Replace placeholder logos and badges with the real assets.
6. Rename unnamed frames and retire duplicates (section 6, items 6–7).
7. Re-run the validation: variable counts, the WEB code syntax, and that every component is bound to a variable, not raw colour.
8. Do not change the KV board's pixel art or tile positions. They are checked against `hyper/design-tokens.json`.

## 9. Source files for reference

- `styles.css`: website CSS (colours, type, radius, shadow, breakpoints). Search it for `--v-*` variables.
- `hyper/design-tokens.json`: KV tokens (colours, geometry, components, story timing).
- `hyper/KV-SPEC.md`: KV build order and motion rules.
