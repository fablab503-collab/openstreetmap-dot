# DotWorld

**A fun personal experiment, built in a conversation with
[Claude](https://claude.com/claude-code). Nothing here is my achievement alone.**

Not affiliated with, endorsed by, or connected to OpenStreetMap, the OpenStreetMap
Foundation, OpenFreeMap, OpenMapTiles, MapLibre, the World Bank, the Wikimedia Foundation,
ColorBrewer or Nothing. No claim is made over any of their work.

This project exists **only because those projects gave their work away**. It points
at them — it does not compete with them, replace them, or take anything from them.
The map data, the tiles and most of the code underneath belong to the people
credited in **[CREDITS.md](CREDITS.md)**. If you like what you see, the credit is
theirs — and [please support them](CREDITS.md#please-support-the-upstream-projects).

Live: <https://fablab503-collab.github.io/openstreetmap-dot/> ·
Changes: [CHANGELOG.md](CHANGELOG.md)

---

A world map rendered entirely as dots, on a globe.

A vector basemap is drawn offscreen, then resampled onto a lattice where each
cell's brightness becomes a dot radius. The result is light on black — built for
OLED panels, where an unlit pixel costs no power.

![Montpellier at zoom 12](shots/montpellier-z12.png)

## Run it

Must be served over HTTP. Opening `index.html` from the filesystem will not work:
MapLibre decodes tiles in Web Workers, and browsers refuse to create workers on a
`file://` origin.

```bash
python3 -m http.server 8732
```

Then open <http://localhost:8732>. No build step, no package manager, no API key.

## How it works

**The lattice is the compression.** A viewport can never hold more than
`viewport ÷ dot pitch` dots, however much map lies underneath.

**Dot pitch follows zoom** — coarse when you look at a country, tight in the streets.

**Tiles stream by territory.** Vector tiles are fetched per tile per viewport, so
moving into new ground loads it and staying put loads nothing.

**The lattice is drawn on the GPU.** A WebGL2 fragment shader samples, for every
cell, the mip level of the map frame whose texels are one cell wide — which is the
cell's average — and turns that brightness into a dot. Measured on an M2 Pro at
street zoom, it costs **0.1–0.5 ms a frame, however many dots are on screen**.
The previous Canvas2D version took 18.3 ms on the same view (about 30 ms with
180k dots). Canvas2D remains as a fallback where WebGL2 is missing; add
`?renderer=cpu` to the URL to compare.

**Data keeps its colour.** The basemap is authored in greys and the data layers are
the only saturated things on screen. Grey cells take the chosen dot colour;
saturated cells keep their own hue, which is how population and monument colours
survive the lattice. While data is shown, basemap dots are dimmed so the data reads.

**Text sits on top of the lattice, not in it.** Letterforms can't survive a dot
grid, so capital names are drawn on their own layer above it.

**The style is a luminance budget, not a colour scheme:**

| Feature | Value | Result |
| --- | --- | --- |
| Sea | `#0f0f0f` | faint texture — never a black void |
| Land | `#242424` → `#151515` as you zoom in | faint field; the coastline is its edge |
| Buildings | `#333333`, `#8a8a8a` outlines from z15 | small dots with readable edges |
| Minor roads and paths → secondary roads | `#5a5a5a` → `#9a9a9a` | mid dots |
| Motorway, trunk, primary | `#ffffff` | full dots |

Sea and ground keep a faint floor on purpose: pure black made open water a total
void that looked like a broken app. Raise `CUTOFF` to take them back to nothing.
LIT AREA and PIXELS DARK in the HUD show the power cost for the current view.

## Data on the map

| Layer | What it shows | Source |
| --- | --- | --- |
| World statistics | Population projected from the latest estimate at the net birth/death rate; born and died today; urban share; land area | World Bank Open Data |
| Population — France | 644 communes over 15,000 people, from Paris (2,103,778) down to 15,023 | Wikidata |
| Capitals | All 195 — 193 UN members plus Vatican and Palestine — with population | Wikidata |
| Monuments — Montpellier | Top 10, ranked by number of Wikipedia language editions | Wikidata + OpenStreetMap |

**Colour follows the job.**

- **Population** uses ColorBrewer's YlOrRd, the standard ramp for population —
  reversed, because on black the published light-to-dark order would make the
  biggest places the dimmest. France is stepped across 15 K – 2.1 M. Capitals use a
  log scale across 1 K – 22 M, because they run from 747 people (Yaren, Nauru) to
  21.9 M (Beijing). Marker size carries population too, so it never rests on
  colour alone.
- **Monuments** use five categorical hues that pass a colour-vision-deficiency check.

**Caveats, plainly:**

- The population counter is a projection. Nobody counts people in real time.
- Capital populations mix city-proper and whole-municipality figures depending on
  the country (Beijing's is the municipality), so compare them loosely.
  Ngerulmud (Palau) has no figure.
- Where a state has more than one capital, the most populous is shown — South
  Africa shows Cape Town.

## Controls

| Control | Effect |
| --- | --- |
| `SEARCH A PLACE` | Search by name; countries and regions frame to their bounds |
| `SETTINGS` | Show or hide the control panel |
| `HIDE PANELS` | Slide every panel off the map and back |
| `DOT SCALE` / `GAIN` / `CUTOFF` | Lattice pitch, brightness response, unlit threshold |
| `TILT` / `BEARING` | 0–85°, 0–359° |
| `SUN` / `SUNLIGHT` | Light direction for 3D buildings — lit faces become bigger dots |
| `DOT COLOUR` | 16 colours, warm to cool: roughly cheapest to most expensive on OLED |
| `MIN POPULATION` | Hide places below a threshold (log scale, 15 K – 2.1 M) |
| `CAPITAL NAMES` | The 195 capitals with their populations |
| `DATA COLOUR` | Show or hide the data layers and their colours |
| `ILLUMINATE MY COUNTRY` | Light up the border of the country you are in |
| `WORLD: ROUND` / `PLATE` | Globe or flat map |
| `WHOLE EARTH` | Pull back to see the whole globe |
| `3D DOT VIEW` | Buildings as extrusions |
| `ORBIT` | Turn the camera, one revolution a minute |
| `RESET NORTH` | Ease back to north |

Drag to pan, scroll to zoom, right-drag to turn and tilt. A drag takes over from an
orbit. Defaults are calibrated by eye: `DOT SCALE 0.65`, `GAIN 2.05`, `CUTOFF 0.03`.

## Readouts

- **ZOOM, DOT PITCH, FRAME** update while you move. FRAME is the median
  main-thread cost of the last 30 redraws.
- **DOTS LIT, LIT AREA, PIXELS DARK** update once the map comes to rest. Counting
  dots means reading the frame back off the GPU, which measured anywhere from
  ~1 ms to ~55 ms — doing it while moving caused visible hitches.
- `window.__bench(20)` in the browser console times each stage of a redraw.

## Sharing a view

The URL carries the view in openstreetmap.org's own hash format and updates as you
move:

```
#map=12.40/43.61190/3.87720
```

Bookmark it, send it, or paste a link copied from openstreetmap.org. With no hash
the map frames metropolitan France.

## Privacy

Your location is requested only when you press **ILLUMINATE MY COUNTRY** — never on
load. The coordinates are rounded to about 1 km before being sent to Nominatim to
find the country, and the map then frames the country rather than your position,
so your location never ends up in the shareable URL.

## Typography

Set in the Nothing visual language:

- **Dotwork** for the wordmark — a 5×7 dot face carrying Ndot 57's metrics
- **Space Mono** for every readout, label and control

Dot faces are display-only; their cells visibly merge below about 24 px, so nothing
you actually read sits in one.

**On Ndot:** Nothing's own dot typeface is licensed solely for Nothing brand
materials, and its EULA forbids serving the files publicly. This repo therefore
ships Dotwork, which is metrically compatible and carries no such restriction.

## Known limits

- **Few labels.** The lattice destroys text, so only capital names are shown, drawn
  on top — at most 55 at once, biggest first.
- **The filter does not reduce data.** A full map still renders underneath; this
  buys the look and the OLED saving, nothing else.
- **Orbit costs power** — continuous rotation means continuous redraw. It pauses
  automatically in a hidden tab.
- **Free community services.** Tiles, search and statistics come from free services
  with fair-use expectations.

## This repository

| Path | What it is |
| --- | --- |
| `index.html` | The whole app — style, shader, interface, data plumbing |
| `vendor/`, `fonts/`, `data/`, `shots/` | MapLibre GL JS 6.9.0, typefaces, datasets, screenshots |
| `skills/dotworld/` | A [Claude Code](https://claude.com/claude-code) skill capturing how DotWorld was built: architecture, shader, measured numbers and the traps behind them, data queries, colour rules, publishing and credits |
| `skills/dotworld/scripts/` | Scripts that rebuild the datasets from Wikidata and OpenStreetMap |
| `archive/` | The first Canvas2D prototype and the first skill, kept for the history |
| `install.sh` | Copies `skills/*` into `~/.claude/skills` |
| `CHANGELOG.md` | Every change, with the reasons and the measured numbers |

Install or update the skill:

```bash
sh install.sh
```

Rebuild a dataset — for example the capitals:

```bash
python3 skills/dotworld/scripts/fetch_capitals.py > data/world-capitals.geojson
```

## Credits and licensing

Everything this is built on — map data, tiles, renderer, geocoder, statistics,
colour schemes and typefaces — is credited with its licence in
**[CREDITS.md](CREDITS.md)**, and in the app under *credits & disclaimer*.
The original code here is MIT licensed (see `LICENSE`), scoped so that it
relicenses none of that work.
