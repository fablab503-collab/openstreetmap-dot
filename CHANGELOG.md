# Changelog

Every change to DotWorld, with the reasons and the measured numbers behind it.
Newest first. Data sources and licences are in [CREDITS.md](CREDITS.md).

---

## 2026-09-11 — The lattice moves to the GPU; capitals get populations

### Improved

- **The dot lattice is now a WebGL2 fragment shader.** Each cell samples the mip
  level of the map frame whose texels are one cell wide (that mip *is* the cell's
  average) and turns its brightness into a dot. Measured on an M2 Pro:

  | Renderer | Street zoom, real content | Notes |
  |---|---|---|
  | Canvas2D arc paths (before) | **18.3 ms** / frame | ~30 ms with 180k dots — over the 16.7 ms budget for 60 fps |
  | CPU pixel stamping (tried, rejected) | 50–100 ms | clearing and pushing a full-frame buffer is itself expensive |
  | WebGL2 shader (now) | **0.1–0.5 ms** / frame | same cost however many dots are on screen |

- **Canvas2D kept as a fallback** for browsers without WebGL2. Add `?renderer=cpu`
  to the URL to force it and compare.
- **Dot count and lit area are now counted only when the map is at rest.**
  Counting means reading the frame back off the GPU, and that readback measured
  anywhere from ~1 ms to ~55 ms depending on what the GPU was still doing. Doing
  it on a timer while moving produced a hitch a few times a second. Zoom, dot
  pitch and frame time still update live.
- **FRAME readout** in the HUD: median main-thread cost of the last 30 redraws.
- **`window.__bench(n)`** in the console times the redraw stage by stage
  (draw, readback, count loop, labels), forcing the GPU to finish each frame.
- **Capitals show their population** beside the name. Marker colour *and* size
  carry it, on a log scale from 1 K to 22 M using the same reversed YlOrRd as
  France — capitals run from 747 people (Yaren, Nauru) to 21.9 M (Beijing), so a
  linear ramp would have painted almost all of them the same red. The number is
  set in neutral ink; only the marker carries the colour. New legend entry.
- **Labels have their own canvas layer** above the lattice.

### Fixed

- **Crash when the capitals data arrived before the map style.**
  `map.getProjection()` is `undefined` until the style loads, and the code read
  `.type` straight off it. The local capitals file often wins that race.
- **One exception in the draw loop stopped rendering for good.** The loop re-armed
  `requestAnimationFrame` *after* drawing, so a throw never re-armed it. It now
  re-arms first.
- The `file://` error message pointed at an old folder path.

### Data

- Capital populations: Wikidata `P1082`. Some countries' figure is the city
  proper, others the whole municipality (Beijing is the municipality), so compare
  loosely — the legend says so. Ngerulmud (Palau) has no figure.

### Not yet verified

- Smoothness was measured per frame, not watched in motion: the preview pane used
  during development stayed hidden, which throttles animation.

---

## 2026-09-10 — Credits, licence, launch

- **Launched on GitHub Pages** at https://fablab503-collab.github.io/openstreetmap-dot/.
  Added `.nojekyll` so Pages serves the files as they are.
- **CREDITS.md**: every data source, library, typeface and colour scheme with its
  licence, plus links to support the upstream projects.
- **LICENSE**: MIT for the original code only, stating explicitly that it cannot
  relicense the ODbL map data, CC BY statistics, CC0 datasets or bundled libraries.
- **In-app *credits & disclaimer* panel**: a fun personal experiment built with
  Claude, not affiliated with or endorsed by any upstream project, and taking
  nothing away from them.

---

## 2026-09-10 — DotWorld

Renamed from OpenStreetMap Dot, and most of the app arrived here.

### Added

- **Globe projection** (`WORLD: ROUND` / `PLATE`), **WHOLE EARTH**, **ORBIT**,
  **TILT**, **BEARING**, **RESET NORTH**, **3D DOT VIEW**.
- **SUNLIGHT** with a direction dial — lit building faces become larger dots.
- **16 dot colours**, ordered warm to cool (roughly cheapest to most expensive on OLED).
- **Place search** via Nominatim, debounced to respect its one-request-a-second policy.
- **SETTINGS** panel, **HIDE PANELS** (slides every panel off and back), equal
  240 px panels in two columns so nothing can overlap.
- **Live world statistics** from World Bank Open Data: population projected from
  the latest estimate at the net birth/death rate, births and deaths today, urban
  share, land area. The counter is labelled as a projection.
- **Population — France**: 644 communes over 15,000 people (Paris 2,103,778 to
  15,023), coloured with ColorBrewer's YlOrRd reversed for a dark ground.
- **MIN POPULATION** slider, logarithmic (15 K – 2.1 M).
- **Monuments — Montpellier**: top 10 ranked by number of Wikipedia language
  editions, merged from Wikidata and OpenStreetMap (neither was complete alone);
  five categorical colours that pass a colour-vision-deficiency check.
- **ILLUMINATE MY COUNTRY**: lights the border of the country you are in.
  Location only on request, coordinates rounded to ~1 km, map frames the country
  not the person.
- **All 195 capital names** (193 UN members + Vatican and Palestine), de-cluttered,
  far side of the globe culled.
- **Typography**: Dotwork wordmark, Space Mono readouts — Nothing-inspired, without
  Nothing's own licence-restricted Ndot typeface.
- **Data colour** mode: grey basemap cells take the chosen dot colour, saturated
  data cells keep their hue, and the basemap is dimmed while data is shown.

### Fixed

- **Screen went completely black over the sea** (and nearly so over open country
  at high zoom): water and ground were pure black, leaving nothing to light a dot.
  Both now keep a faint floor; building outlines added from z15.
- **Search bar drew on top of the readouts** — both pinned to the same position.
- **A duplicate element id silently filtered out every French commune**: the
  slider shared `s-pop` with the population counter, so the filter read `NaN`.
- **Temporal dead zone on `showCapitals`** killed the first frame.
- **ORBIT cancelled itself**: MapLibre fires `rotatestart` for programmatic camera
  moves too; the handler now reacts only to real gestures.
- **A map started in a zero-size container never re-framed** once it had a size.
- **Paris was missing** from the population data: its "commune of France"
  statement is not a truthy Wikidata statement, so the query silently dropped it.
- **The first two monument palettes failed** colour-vision checks (green and gold
  were ΔE 2.5 apart for protanopia); the shipped one passes all six checks.

---

## 2026-09-09 — First version, as "OpenStreetMap Dot"

- MapLibre renders an OpenFreeMap basemap offscreen; the visible canvas is a dot
  lattice where each cell's brightness sets a dot's radius.
- Basemap authored as a **luminance budget** for OLED: what matters is bright,
  everything else stays dark.
- Dot pitch follows zoom — coarse far out, fine up close.
- Views addressable with openstreetmap.org's `#map=zoom/lat/lon` hash.

### Fixed while getting it to run at all

- **cdnjs ships no MapLibre JavaScript**, only CSS — the library is now vendored.
- **MapLibre v6 is ESM-only with named exports** — imported as `import * as maplibregl`.
- **Frames read back all black**: in MapLibre v6 `preserveDrawingBuffer` moved
  under `canvasContextAttributes`, and the old top-level option is silently ignored.
