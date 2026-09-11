# DotWorld — project facts

## Where things are

| What | Where |
|---|---|
| Master copy (git) | `/Volumes/Volume1/SecondBrain/dotworld/` |
| GitHub | https://github.com/fablab503-collab/openstreetmap-dot |
| Live site | https://fablab503-collab.github.io/openstreetmap-dot/ (Pages, `main`, root) |
| Vault note | `Projects/DotWorld.md` |
| This skill | `skills/dotworld/` in the repo; install with `sh install.sh` |
| Change history | `CHANGELOG.md` in the repo |

The repo was first built inside `fablab-tools/openstreetmap-dot` (2026-09-09/11) and
moved to SecondBrain with its history on 2026-09-11. The GitHub remote and the live
URL did not change.

## Repo layout

| Path | What |
|---|---|
| `index.html` | the whole app — style, shader, UI, data plumbing |
| `vendor/` | MapLibre GL JS 6.9.0 `.mjs` bundles + CSS |
| `fonts/` | Dotwork (+ OFL), Space Mono, Space Grotesk |
| `data/fr-population.geojson` | 644 French communes over 15k |
| `data/world-capitals.geojson` | 195 capitals with population and seat count |
| `data/montpellier-monuments.geojson` | top-10 Montpellier monuments with category |
| `shots/` | screenshots used in the README |
| `skills/dotworld/` | this skill |
| `archive/` | the first Canvas2D prototype and the first `dots` skill |
| `memory/` | local snapshot of Claude's project memory — gitignored, never pushed |
| `README.md`, `CREDITS.md`, `CHANGELOG.md`, `LICENSE` | docs; updated with every push |

## Run it locally

```bash
cd /Volumes/Volume1/SecondBrain/dotworld && python3 -m http.server 8732
```

Open http://localhost:8732. `?renderer=cpu` forces the Canvas2D fallback;
`#map=zoom/lat/lon` opens a view; `window.__bench(20)` times a redraw.

## Defaults

- `DOT SCALE 0.65`, `GAIN 2.05`, `CUTOFF 0.03` — calibrated by eye on a 3D street view.
- Dot pitch `clamp(18 − (zoom − 3), 3.5, 18) × scale` CSS px; overlay DPR capped at 2.
- No `#map=` hash → fit metropolitan France `[[-5.15, 41.33], [9.56, 51.09]]`.
- Globe projection on; `maxPitch` 85; orbit 0.12°/frame (one turn a minute).
- Capital labels: up to 55, biggest population first.

## Controls

SEARCH A PLACE · SETTINGS · HIDE PANELS · DOT SCALE · GAIN · CUTOFF · TILT ·
BEARING · SUN · SUNLIGHT · DOT COLOUR (16) · MIN POPULATION (log 15 K–2.1 M) ·
CAPITAL NAMES · DATA COLOUR · ILLUMINATE MY COUNTRY · WORLD: ROUND / PLATE ·
WHOLE EARTH · 3D DOT VIEW · ORBIT · RESET NORTH. Right-drag turns and tilts.

HUD: ZOOM, DOT PITCH, FRAME live; DOTS LIT, LIT AREA, PIXELS DARK when the map is at
rest. World statistics panel: projected population, people per second, born and died
today, countries, urban share, land area.

## Standing rules

- Every update goes live on GitHub with README, CREDITS and CHANGELOG updated in the
  same commit.
- Credit every upstream author and data source.
- Keep the OLED power budget in mind for every visual change.
- This skill ships in a public repo: keep personal notes and private memory out of
  it (`memory/` is gitignored; the vault note `Projects/DotWorld.md` is private).

## Open items (2026-09-11)

- **World population:** France is done; "next week with the world" — drop the France
  filter and handle the scale (population by country or by city worldwide).
- **Smoothness not watched in motion** — measured per frame only.
- **ILLUMINATE MY COUNTRY success path untested** — the Browser pane denied location.
- **Narrow-screen layout (< 900 px) untested** — the pane clamped to 980 px.
- **Async readback** (PBO + `fenceSync`) would keep the dot count live while moving.
- Consider **INSEE API Géo** as the French population source.
