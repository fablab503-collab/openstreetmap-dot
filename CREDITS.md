# Credits, data sources and licences

**DotWorld is a fun personal experiment, built in conversation with Claude
(Anthropic's Claude Code). Nothing here is my achievement alone.**

It is **not affiliated with, endorsed by, or connected to** OpenStreetMap, the
OpenStreetMap Foundation, OpenFreeMap, OpenMapTiles, MapLibre, the World Bank, the Wikimedia
Foundation, ColorBrewer, or Nothing. No claim is made over any of their work.

This project exists **only because those projects gave their work away**. It is
meant to point at them, not to compete with them, replace them, or take anything
from them. Every piece of map data, every tile, and most of the code underneath
belongs to the people credited below. **If you like what you see here, the credit
is theirs.** Please go and support them — links at the bottom.

---

## Map data

**© OpenStreetMap contributors**, licensed under the
[Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/).
Every road, coastline, building and monument outline in this map is their work,
contributed by hundreds of thousands of volunteers over two decades.

Attribution must remain visible in any deployment. This app renders it itself,
because the opaque dot canvas covers MapLibre's own attribution control.

<https://www.openstreetmap.org/copyright>

## Vector tiles

**[OpenFreeMap](https://openfreemap.org/)** — free, open vector tiles served
without an API key or sign-up, created and paid for by **Zsolt Ero**. Tiles
follow the **[OpenMapTiles](https://openmaptiles.org/) schema**, which requires its own
visible, linked credit.

The attribution shown on the map is OpenFreeMap's own required string, taken from
its TileJSON: *"OpenFreeMap © OpenMapTiles Data from © OpenStreetMap contributors"*.
The first published version credited OpenStreetMap and OpenFreeMap but left out
OpenMapTiles.

Running a planet-wide tile server for free is an act of generosity. This project
would not exist without it, and any real traffic should be met with a donation
rather than a free ride.

## Map renderer

**[MapLibre GL JS](https://maplibre.org/)** — BSD-3-Clause. Vendored in
`vendor/` so this page has no CDN dependency. MapLibre does all the genuinely
hard work here: tile fetching, projection, the globe, camera handling and
WebGL rendering. The dot lattice is a thin pass on top of their output.

## Geocoding

**[Nominatim](https://nominatim.org/)**, run by the **OpenStreetMap Foundation** —
used for place search and for the country lookup behind "illuminate my country".
Data ODbL, subject to the
[Nominatim usage policy](https://operations.osmfoundation.org/policies/nominatim/).
Requests are debounced to respect their one-per-second guidance.

## Statistics and datasets

| Data | Source | Licence |
|---|---|---|
| World population, birth/death rates, urban share, land area | [World Bank Open Data](https://data.worldbank.org/) | CC BY 4.0 |
| Population of 644 French communes | [Wikidata](https://www.wikidata.org/) (P1082) | CC0 1.0 |
| 195 national capitals and their populations | [Wikidata](https://www.wikidata.org/) (P36, P625, P1082) | CC0 1.0 |
| Montpellier monuments + ranking | [Wikidata](https://www.wikidata.org/) & [OpenStreetMap](https://www.openstreetmap.org/) | CC0 1.0 / ODbL |

Monument ranking uses the number of Wikipedia language editions covering each
site — so the ordering is really the work of **Wikipedia's editors**.

## Colour

**[ColorBrewer](https://colorbrewer2.org/)** — colour schemes by **Cynthia
Brewer, Mark Harrower and The Pennsylvania State University**, Apache 2.0.
The population ramp is their **YlOrRd**, reversed so luminance rises with
population on a dark ground. Reference implementation seen in
[Leaflet's choropleth example](https://leafletjs.com/examples/choropleth/).

## Typefaces

| Face | Used for | Licence |
|---|---|---|
| **Dotwork** | the DOTWORLD wordmark | SIL Open Font License 1.1 (`fonts/Dotwork-OFL.txt`) |
| **Space Mono** | every readout, label and control | SIL Open Font License 1.1 |
| **Space Grotesk** | bundled, reserved for headings | SIL Open Font License 1.1 |

The dot-matrix look is inspired by **Nothing**'s visual language. Nothing's own
**Ndot** typeface is licensed strictly for Nothing brand materials and is
deliberately **not** used or shipped here; Dotwork is the openly licensed
substitute. No association with Nothing is claimed or implied.

## Built with

**[Claude Code](https://claude.com/claude-code)** (Anthropic) — the whole thing
was designed and written in a conversation, including the bugs and the fixes.

---

## Please support the upstream projects

Everything above is given away for free by people and organisations who pay real
costs to do it. If this project is worth anything to you, send it upstream:

- **OpenStreetMap Foundation** — <https://supporting.openstreetmap.org/>
- **OpenFreeMap** — <https://openfreemap.org/> (sponsorship / donation)
- **MapLibre** — <https://opencollective.com/maplibre>
- **Wikimedia Foundation** — <https://donate.wikimedia.org/>

## This project's own code

The original code in this repository — the halftone lattice, the UI, the data
plumbing — is released under the **MIT Licence** (see `LICENSE`). That covers
only the code written here. It does **not** and cannot relicense any of the data
or libraries above, which stay under their own terms.
