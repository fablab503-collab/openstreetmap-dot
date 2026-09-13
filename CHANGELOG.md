# Changelog

Every change to DotWorld, with the reasons and the measured numbers behind it.
Newest first. Data sources and licences are in [CREDITS.md](CREDITS.md).

---

## 2026-09-14 — Shift-drag to turn and tilt

### Added

- **Hold shift and drag** to turn and tilt, alongside right-drag. MapLibre has no
  option for it — shift-drag is its box zoom — so the box-zoom handler is off and
  drag-pan is suspended for the length of the gesture, or the map would pan
  underneath the turn. Bearing and pitch are set per mouse-move rather than eased,
  so the camera follows the hand exactly, and the TILT and BEARING sliders follow
  the camera as always.

---

## 2026-09-14 — A clock, one switch for everything, and a tidier panel

### Added

- **The time where you are**, in the statistics panel: the clock, the UTC offset,
  and how many hours you are **ahead of** the world's first capital and **behind**
  its last. Pick a country and the clock becomes that capital's, with how far ahead
  of or behind you it is.
- Every capital now carries its **IANA time zone** (`Europe/Paris`, not `+02:00`),
  taken from the nearest GeoNames city in the same country — so the browser applies
  daylight saving, and Kathmandu shows +05:45 rather than a rounded hour. Your own
  zone comes from the browser and needs no permission.
- The two ends of the day are worked out from the capitals themselves rather than
  from UTC-12 and UTC+14: they are real places on this map, and the pair moves with
  daylight saving, so it is recomputed every quarter of an hour.
- **ALL DATA**, one switch that turns every layer on or off instead of four.

### Changed

- **Montpellier's monument categories are out of the panel.** They were a leftover
  from when the map was one city; the layer still colours them when you are there.

---

## 2026-09-14 — A dot scale that goes all the way down

### Changed

- **DOT SCALE now starts at 0.01, not 0.4**, in steps of 0.01. At 0.05 the lattice
  is about two device pixels across at world zoom; below that the dots are finer
  than a screen pixel and the map goes continuous, which is as far as any screen can
  take it.

### Fixed

- **A fine lattice used to go black.** The minimum-radius cull was a fixed 0.35
  device pixels, so once the pitch came near a pixel the largest possible dot was
  already under the threshold and every single one was culled. The cull follows the
  pitch now — `min(0.35, step * 0.22)` in the shader, the same rule on the CPU path.

### Notes

- The shader does not care how fine the lattice is: it costs one texture read per
  *pixel*, not per dot. The other two paths do, so they have floors it does not
  need — the Canvas2D fallback draws one arc per cell (millions a frame below two
  device pixels), and the lit-area count builds a cell grid, which under one device
  pixel is a canvas of hundreds of millions of cells that cannot be allocated. The
  HUD reports the pitch each path actually drew.

---

## 2026-09-14 — A light that runs round the border

### Added

- **Picking a country now draws its border.** The map frames the country, then a
  light runs round the outline and leaves it lit behind it — the whole border in
  **3.2 seconds**, however big the country is. Islands trace alongside the mainland
  rather than queueing after them, and the light fades once the outline is complete.
- **Click a capital on the map to pick its country**, instead of going through the
  list. The pointer changes over a capital, so you can tell it is clickable.

### Changed

- **A country is framed from its own outline now, not from a geocoder's box.**
  Nominatim answers with everything a country owns: asking for Portugal framed
  900 km of Atlantic because of the Azores, and France's box spans the planet
  because of French Polynesia. The mainland is the biggest ring of the outline the
  map already holds — rings that wrap the antimeridian are skipped rather than
  fitted. One less network call, too.

### Notes

- The light is a `line-gradient` travelling along the outline, not a crawling dash:
  a bright head, the lit border behind it, nothing ahead of it yet. It needs
  `lineMetrics: true` on the source — without that `line-progress` does not exist
  and the gradient is ignored silently.
- Each ring is its own feature, so progress runs 0 to 1 along every piece of a
  country at once. The duration is fixed rather than the speed, so Russia and
  Monaco take the same 3.2 seconds.
- It starts on `moveend`. Drawn during the flight, it is a smear.

---

## 2026-09-14 — The whole world's population, and a button that finds you

### Changed

- **The population layer is the world now, not France.** Every city over 15,000
  people — **34,091 of them**, Shanghai (24.9 M) down to 15,001 — from GeoNames,
  which publishes the lot as one maintained file. Wikidata, which gave France its
  644 communes, does not scale to this: the same query worldwide times out, and its
  population statements are uneven from country to country. `MIN POPULATION` now
  runs 15 K to 25 M.
- The colour stops are spaced by a constant ratio (15k, 44k, 128k, 373k, 1.09M,
  3.18M, 9.3M, 25M) rather than evenly. City sizes cover three orders of magnitude,
  and even spacing paints everything under a million the same dark red.
- The file ships as `[lon, lat, pop]` triples, not GeoJSON: the layer draws circles
  and never reads a name, and GeoJSON's scaffolding costs 5.1 MB against **762 KB**
  (303 KB over the wire) for the same cities. The app builds the GeoJSON in one pass
  at load.
- `data/fr-population.geojson` is gone from the working tree; it stays in the
  history, and `fetch_fr_population.py` still documents the Wikidata approach.

### Added

- **WHERE AM I**, under the zoom bar at the bottom centre. It marks where you are
  and flies there, and the button names the town it found so you can see it worked.
  Your fix is rounded to 2 decimals — about a kilometre — **before** anything is
  done with it: that rounded point is what the map flies to, what the marker is
  drawn from and what the geocoder is asked about, so nothing sharper than a
  kilometre exists in the page, in the URL hash or in any request.

---

## 2026-09-13 — Monuments drawn as the buildings they are

### Added

- **Every capital monument now has its own outline**, taken from OpenStreetMap:
  from z12.5 the cyan circle gives way to the building's footprint, so the lattice
  fills the Colosseum's ellipse, the Capitol's wings and the Forbidden City's
  rectangles instead of a blob. **355 of the 491 monuments (72%), across 162
  capitals**, 220 KB — 44 KB over the wire — fetched only once you are close enough
  for an outline to be more than a speck. The rest keep the marker; OSM has no
  wikidata-tagged building near their point.
- `skills/dotworld/scripts/fetch_monument_shapes.py` builds it through Overpass.
- **In 3D the monument rises as a cyan volume.** A flat fill at ground level is
  hidden under the tiles' own extruded building however late it is drawn - the
  extrusion writes depth - so the monument has to be a volume too. Heights are
  OpenStreetMap's where the building has one (110 of the 355), 25 m otherwise,
  which clears what the tiles guess: they give the Colosseum a 1 m extrusion.

### Notes

- The vector tiles cannot do this: their building layer carries render heights and
  no name or id, so there is no way to ask them for one particular building.
- Matched by position — every OSM way or relation with a `wikidata` tag within
  150 m, nearest centroid inside 200 m wins — so two monuments on the same street
  cannot swap outlines.
- A relation's outer ways come back from Overpass unordered and sometimes reversed;
  they are joined end to end into rings here, or the Louvre draws as a scribble.
- Simplified at ~2 m, which is far under one dot of the lattice even at street
  zoom: Westminster Abbey goes from 547 points to 108, the file from 400 KB to 220.

---

## 2026-09-13 — A zoom bar you can throw

### Added

- **A zoom bar across the bottom centre.** Drag it and the map follows the handle
  frame by frame, so a street becomes the whole globe in one gesture. It reads the
  map's own minimum and maximum zoom rather than hard-coded numbers, shows the
  level to two decimals, stops ORBIT like every other camera control, and slides
  away with **HIDE PANELS**. World, country, city and street are marked at the
  zoom each word actually means: the scale runs -2 to 22, so spacing them evenly
  would have put "city" at z14, which is a rooftop.
- Dragging is a **scrub, not a flight**: each input jumps the camera with no
  animation. Easing every step would queue hundreds of eased moves and the lattice
  would arrive late; jumping lets it redraw as fast as it can.

---

## 2026-09-13 — The best-known monument of every capital

### Added

- **Capital monuments.** Next to each capital's name, what that capital is known
  for: its three best-known places, ranked by how many Wikipedia editions and
  sister projects cover them. They have a colour of their own — cyan, the only hue
  left that stays clear of the population ramp, the country glow and all five
  Montpellier categories (worst colour-vision deltaE 13.7, measured with the same
  checker as the Montpellier palette, not chosen by eye). The best-known one shows
  from the world view, the other two and all the names from z6 and z8, and
  **CAPITAL MONUMENTS** in settings turns the lot off.
- **`data/capital-monuments.geojson`**, built by
  `skills/dotworld/scripts/fetch_capital_monuments.py`: one Wikidata query per
  capital, monuments within 25 km ranked by sitelinks. **491 places for 192 of the
  195 capitals** (105 KB). Three have none: Ciudad de la Paz has nothing notable
  nearby in Wikidata, Brazzaville's only candidate is nearer to Kinshasa, and
  Luxembourg's response was truncated on every attempt through this proxy.
  Spot checks: Paris → Eiffel Tower, Louvre, Notre-Dame; Rome → Colosseum,
  Pantheon, Roman Forum; Cairo → Great Pyramid of Giza; Washington → the White
  House, the Library of Congress, the Capitol; East Jerusalem → Al-Aqsa Mosque,
  Dome of the Rock.

### Fixed

- **One capital was drawn as "Q36262".** St. John's, the capital of Antigua and
  Barbuda, no longer has an English label on Wikidata — the name moved to the
  multilingual `mul` code — and a label service asked for `"en"` alone hands back
  the bare item id. The query now asks for `"en,mul,en-gb,fr,es"`.

### What it took to get a list worth showing

- Walking `wdt:P31/wdt:P279*` from "architectural structure" is the obvious way to
  catch an amphitheatre, a city gate and a mausoleum. It returns 504 on Paris, Rome
  and Cairo. Types are filtered here instead, where it is free.
- Keyword matching on type labels has to respect word boundaries: "arch" inside
  *constitutional monarchy* put Antigua and Barbuda itself on the map, and "villa"
  inside *village* added a hamlet called Bolans.
- "historical country" contains "historic", so Rome first returned the Roman Empire,
  Tokyo the Tokugawa shogunate and London the Kingdom of Great Britain.
- The Colosseum is typed `stadium` as well as `Roman amphitheatre`. Blocking
  stadiums to keep football grounds out buried Rome's most-linked monument.
- Vatican City is 4 km from Rome, Brazzaville 5 km from Kinshasa: each monument
  goes to the capital it is nearest to, so nothing is drawn twice.

---

## 2026-09-13 — Find any of the 195 countries and light it up

### Added

- **A country picker, in the statistics panel under COUNTRIES.** All 195 in one
  list; type a few letters to jump to one. Choosing a country lights its border on
  the map, frames it, keeps its capital's name on screen even when labels are
  crowded or switched off, and reads out that capital's population beside the
  country's own, from World Bank Open Data. Choosing the empty entry puts
  everything back.
- **ISO 3166-1 alpha-2 codes in the capitals file** (Wikidata P297). That is the
  code the tiles' boundary layer carries in `adm0_l`/`adm0_r`, so it is what makes
  a single country's border light up. One UN member carries no code of its own:
  the member is the *Kingdom of Denmark*, while DK belongs to *Denmark*, its
  European part — filled in by the script and documented there.
- **The country's own outline**, from Natural Earth's 1:50m set, lit over the
  lattice. The tiles have no country polygons, and their boundary lines only name
  the countries either side from zoom 5 up — checked by decoding tiles — so at the
  zoom where you look at a whole country there was nothing to light. The outline
  file is 780 KB (225 KB over the wire) and is fetched only when someone picks a
  country. It fades out as you zoom past 6, where the tiles' own sharper border
  takes over.
- **Every earlier version is now tagged on GitHub**, `v0.1.0` (2026-09-09) through
  `v0.4.0`, with `v0.5.0-beta` published as a release.

### Notes

- Framing costs one Nominatim lookup per country, cached for the session. A country
  that crosses the antimeridian — Fiji, Kiribati, Russia — comes back with a box
  spanning the whole planet, so those fall back to flying to the capital.
- **ILLUMINATE MY COUNTRY** and the picker now agree: finding your own country
  also sets the picker, so the panel says what the map is showing.

---

## 2026-09-11 — A new home, a skill, and corrections to what the site claimed

### Fixed

- **The capitals list included Taiwan and left out Vatican City.** The Wikidata
  query matched any "member of the United Nations" statement, including historical
  ones, so it picked up Taiwan — whose UN seat passed to the People's Republic of
  China in 1971 — and it missed Vatican City. The total still came to 195, which is
  why the count never revealed it. The query now requires a membership statement
  with no end date *and* a current, undissolved sovereign state, and the result was
  checked against Wikidata's current membership: the 193 members plus the two
  observer states, Vatican City and Palestine.
- **Seven states have more than one seat, not nine.** Jordan and Syria each return
  the same capital twice as separate Wikidata items; that is not a second seat.
  `seats` now counts distinct capitals.
- **The map's credit left out OpenMapTiles.** The on-map attribution now uses
  OpenFreeMap's own required wording, read from its TileJSON: "OpenFreeMap
  © OpenMapTiles Data from © OpenStreetMap contributors". OpenMapTiles is also
  credited in the in-app panel, CREDITS.md and the README.
- **MapLibre's full BSD-3-Clause licence now ships with the vendored bundles**
  (`vendor/LICENSE-maplibre-gl.txt`). The bundles carried only a one-line header
  and a link.

### Added

- **`skills/dotworld/`** — a Claude Code skill capturing how DotWorld was built: the
  two ways to get a MapLibre frame into a dot pass and what each costs, the shader,
  the measured numbers and the traps that produced wrong ones, the data queries, the
  colour rules, and publishing and credits. Install with `sh install.sh`.
  It was tested before it shipped: an agent given a DotWorld task without it got the
  basics right but repeated the black-background bug, quoted frame times it had not
  measured, and missed the crash, lifecycle and licensing traps. The skill was
  written around those gaps, then the task was run again by a fresh agent with it.
- **`skills/dotworld/scripts/`**, run against the live sources on 2026-09-11:
  - `fetch_capitals.py` rebuilt the corrected capitals file.
  - `fetch_fr_population.py` returned 645 communes: the shipped 644 plus Quimper,
    which the earlier run did not return (not investigated). No population changed.
  - `rank_monuments.py` ranks a city's monuments; see *Not changed* below.
  All three retry. The France query asks for CSV, because its JSON result was cut
  off at exactly 262,144 bytes on every attempt through a proxy.
- **`archive/`** — the first Canvas2D prototype, its screenshots, and the first skill.

### Changed

- The working copy moved to a new home with its full history. The GitHub
  repository and the live URL are unchanged.

### Not changed, on purpose

- **Montpellier's monuments.** Ranked with one consistent measure — Wikipedia
  language editions for every candidate, inside the city's own boundary — the top 10
  swaps the promenade du Peyrou (4) for the Mosquée Avicenne (6). The shipped list
  counted all sitelinks for OpenStreetMap-sourced items but Wikipedia-only links for
  Wikidata items. Which list to show is an editorial choice, so the site keeps its
  current list until that is decided.

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
