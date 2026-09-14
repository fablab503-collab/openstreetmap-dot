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
| Ocean | `midnightblue` at a third | reads as sea, at the brightness the old grey had |
| Lake, pond, river, canal, stream, dock, pool | `darkslateblue` … `royalblue` | nine named blues, dimmer the more screen they cover |
| Land | `#242424` → `#151515` as you zoom in | faint field; the coastline is its edge |
| Buildings | `#333333`, `#8a8a8a` outlines from z15 | small dots with readable edges |
| Minor roads and paths → secondary roads | `#5a5a5a` → `#9a9a9a` | mid dots |
| Motorway, trunk, primary | `#ffffff` | full dots |

Every kind of water has a blue of its own — the tiles carry a class per body and per
channel — and anything that dries up for part of the year is drawn faint.

Sea and ground keep a faint floor on purpose: pure black made open water a total
void that looked like a broken app. Raise `CUTOFF` to take them back to nothing.
LIT AREA and PIXELS DARK in the HUD show the power cost for the current view.

## Data on the map

| Layer | What it shows | Source |
| --- | --- | --- |
| World statistics | Population projected from the latest estimate at the net birth/death rate; born and died today; urban share; land area; the population of any country you pick | World Bank Open Data |
| The world, on average | Density, life expectancy, children per woman, GDP per person, the age split and town against country | World Bank Open Data |
| Cities by size | How the 34,091 cities fall across the eight bands, with the median and the mean | GeoNames |
| The 195 capitals | Biggest, smallest, how many over a million, and which hour of the world each keeps | Wikidata + GeoNames zones |
| Best known places | The ten monuments the world writes about most, of all 195 capitals | Wikidata |
| Time | The clock where you are — or in the capital you picked — with how far ahead of the world's first capital and behind its last you are | GeoNames zones, your browser |
| Population — world | Every city over 15,000 people, 34,091 of them, in eight named bands from `darkred` to `gold` | GeoNames |
| Capitals | All 195 — 193 UN members plus Vatican and Palestine — with population and ISO country code | Wikidata |
| The country you pick | Its outline lit over the lattice, at any zoom | Natural Earth (1:50m) |
| Monuments — capitals | The three best-known places in each of the 195 capitals, by Wikipedia coverage | Wikidata |
| Land | Wood, scrub, grass, farmland, wetland, sand, ice, and what people build on it — residential to stadium — each a named colour, kept dim | OpenStreetMap |
| Monument outlines | The building's own edges from z12.5 — a contour round its foot, and round its roofline in 3D | OpenStreetMap (Overpass) |
| Monuments — Montpellier | Top 10, ranked by number of Wikipedia language editions | Wikidata + OpenStreetMap |
| The solar system | The Sun, eight planets, the Moon and Pluto: size, mass, spin, tilt, orbit, moons and temperature, with gravity worked out from the masses | NASA NSSDC fact sheet + Wikipedia J2000 angles |
| What each body looks like | A colour map per body, sampled per dot — ocean, desert, forest and ice where they actually are — and the Earth's night lights | Solar System Scope textures (CC BY 4.0), downsampled |

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
| `WHERE AM I` (bottom centre) | Marks where you are, rounded to about a kilometre, and flies there |
| The story line | The headline of whichever year the bar is on, with month and day. Click it for everything from the Big Bang to that year | Wikidata + linked articles |
| `YEAR` bar (bottom centre) | Take the map back to 1500 or forward to 2050. Cities are scaled by their own country's trajectory, and below 1995 the borders are the ones of that era |
| `COLOURS` | How many colours the map may use, 1 to 43. Each step hands a group its own hues — water, population, monuments, land, built land, transport — and turning it down costs less power |
| `ZOOM` bar (bottom centre) | Drag to go from a street to the whole globe in one gesture; it follows the map too, and slides away with the panels |
| `SEARCH A PLACE` | Search by name; countries and regions frame to their bounds |
| `SETTINGS` | Show or hide the control panel |
| `HIDE PANELS` | Slide every panel off the map and back |
| `DOT SCALE` / `GAIN` / `CUTOFF` | Lattice pitch (0.01 to 2 - past about 0.05 the dots are finer than a screen pixel and the map goes continuous), brightness response, unlit threshold |
| `TILT` / `BEARING` | 0–85°, 0–359° — or hold **shift** (or the right button) and drag the map |
| `SUN` / `SUNLIGHT` | Light direction for 3D buildings — lit faces become bigger dots |
| `DOT COLOUR` | 16 colours, warm to cool: roughly cheapest to most expensive on OLED |
| `MIN POPULATION` | Hide places below a threshold (log scale, 15 K – 2.1 M) |
| `ALL DATA` | Everything the map can show, in one switch |
| `CAPITAL NAMES` | The 195 capitals with their populations |
| `CAPITAL MONUMENTS` | The best-known places of every capital, in cyan; the top one from the world view, all three and their names as you zoom in |
| `FIND A COUNTRY` | Any of the 195, by name or by typing a few letters: the map frames it, a light runs round its border, and the panel reads out its capital and its population |
| Click a capital | Same thing, straight from the map |
| `DATA COLOUR` | Show or hide the data layers and their colours |
| `ILLUMINATE MY COUNTRY` | Light up the border of the country you are in |
| `WORLD: ROUND` / `PLATE` | Globe or flat map |
| `WHOLE EARTH` | Pull back to see the whole globe |
| `3D DOT VIEW` | Buildings as extrusions |
| `ORBIT` | Turn the camera, one revolution a minute |
| `RESET NORTH` | Ease back to north |
| `LEAVE EARTH` | Step off the map into the solar system: the Sun, the eight planets, the Moon and Pluto, all drawn as dots |
| In space: `LOOKING AT` | Fly to any of them — or click one |
| In space: `TIME` | Paused, real time, or up to a year a second. The year bar still works: set 20 July 1969 and the Earth and Moon stand where Apollo 11 found them |
| In space: `DEPTH OF FIELD` | How much a lens blurs what is off the plane you are looking at. 0 turns it off |
| In space: `GRAVITY WELL` | The pull, drawn as the pit it makes |
| In space: `TRUE SCALE` | Stop squashing distances and sizes. Worth doing once |

Drag to pan, scroll to zoom, right-drag to turn and tilt. A drag takes over from an
orbit. Defaults are calibrated by eye: `DOT SCALE 0.65`, `GAIN 2.05`, `CUTOFF 0.03`.

## Space

`LEAVE EARTH` puts the camera three Earth radii up and hands it the rest of the
solar system. Everything is still dots.

Three invisible things are drawn:

- **Gravity**, as a real number: the sum of GM/r² from every body at wherever the
  camera is. It starts at the Earth, where it reads 9.8 m/s² on the surface, and
  falls with the square of the distance as you pull back — 2.45 at two radii out,
  1.09 at three. The sheet under the planets is the same sum drawn as a potential
  well; it is not a picture of bent space.
- **Depth of field**, because a lens has one: anything off the plane you are
  looking at spreads into a bigger, fainter disc. On a screen with no parallax it
  is the only thing that says which of two dots is further away.
- **Grab a planet and spin it.** Drag the body itself rather than the empty sky and
  it turns under your finger; let go and it keeps the rate you gave it, because
  nothing out there is touching it. The panel then reads the consequences: the new
  day length, the angular momentum as a multiple of its own, the energy you put in,
  how fat the spin makes it, and — since the only brake anyone has measured is the
  tide — how long the spin would take to bleed off, which comes out in billions of
  years. A hand is far too strong for a planet, so the spin is held at the rate where
  the equator would fly off (one turn every 1 h 24 m for the Earth); that line is
  physics, not a setting. `GIVE THE SPINS BACK` undoes it, which nothing in space
  would.
- **Real colour, and real light.** Every body carries a small map of its own true
  colour and the dots sample it: the Earth comes out with blue ocean, sand where the
  Sahara is, green where the forests are, white ice. The night side is the real
  night-lights imagery, so a dot over Tokyo is bright because Tokyo is bright.
  Sunlight is the colour of a 5772 K body — `(255, 240, 234)`, white with the
  faintest warm cast, worked out from the Sun's own temperature through the
  Planckian locus. The orange Sun everyone draws is what our air does to it; from
  out here it is white. `realism` mixes between the flat house colour and the real
  one; `lights` switches the night side between the real imagery, the map's own
  population dots, and off.
- **Spin**, with the numbers under it. The Earth turns once a sidereal day —
  **23 h 56 m 04.2 s** — under a Sun that stands over the longitude matching the
  hour, so at noon UTC Greenwich faces it. The panel reads out, live: how far it has
  turned since midnight, where the Sun is overhead (longitude from the clock,
  latitude from the tilt — that one is the declination that gives us summer), the
  ground speed at the equator (**1,674 km/h**) and under wherever the camera is,
  how much of the pull the spin cancels there (0.0339 m/s² at the equator, 0.34% —
  nothing at the poles), what you would actually weigh on that spot from NASA's own
  measured ends (9.780 m/s² at the equator, 9.832 at the pole), how far the spin has
  squashed the planet (21.4 km fatter than tall, 1/298), and that the day is getting
  longer by +1.72 ms a century while the Moon backs away 3.8 cm a year. The night
  side is made of the Earth's own cities, in the same population colours the map
  uses. The Moon keeps one face toward us, marked, because it turns exactly once
  per orbit.

**Scale is true by default.** From three Earth radii up the Sun is 0.531° across and
the Moon is 0.518° — which is why total eclipses work at all — while Venus is 0.010°
and Jupiter 0.009°, points of light, because that is what they are. Squashing the
distances to fit a screen is what made the Sun loom and put Venus next to the Moon:
once orbits are crushed, no size mapping can put both right. `SQUASHED SCALE` brings
that diagram back — a square root, not a log, or Venus would be as wide as the gap to
the Earth — and the panel says which one is on.

Bodies hide what is behind them: dots here are added to the frame like light, with no
depth test, so they are drawn furthest first and each punches its own silhouette.

Positions are two-body Kepler orbits from the NASA fact sheet and J2000 angles.
Good to a fraction of a degree from 1800 to 2050 and drifting outside it. For real
positions, use [JPL Horizons](https://ssd.jpl.nasa.gov/horizons/).

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
