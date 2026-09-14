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
| World population, birth/death rates, urban share, land area, and the population of a chosen country | [World Bank Open Data](https://data.worldbank.org/) | CC BY 4.0 |
| Population of every city over 15,000 people (34,091 of them) | [GeoNames](https://www.geonames.org/) `cities15000` | CC BY 4.0 |
| The IANA time zone of each of the 195 capitals | [GeoNames](https://www.geonames.org/) `cities15000` | CC BY 4.0 |
| Population of 644 French communes (the layer this replaced, Sep 2026) | [Wikidata](https://www.wikidata.org/) (P1082) | CC0 1.0 |
| 195 national capitals, their populations and ISO 3166-1 alpha-2 codes | [Wikidata](https://www.wikidata.org/) (P36, P625, P1082, P297) | CC0 1.0 |
| Country outlines for the 195 | [Natural Earth](https://www.naturalearthdata.com/) 1:50m admin 0 | public domain |
| Population by country by year, 1960–2050 | [World Bank Open Data](https://data.worldbank.org/) (estimates, and source 40 projections) | CC BY 4.0 |
| Historical borders, 1500–1994 | [Historical Basemaps](https://github.com/aourednik/historical-basemaps), Andreas Ourednik | GPL-3.0 |
| The events of each year, 1500 onward | [Wikidata](https://www.wikidata.org/) (P585, P580, P619, sitelink counts) | CC0 1.0 |
| Sizes, masses, spins, tilts, orbits and temperatures of the Sun, the eight planets, the Moon and Pluto | [NASA NSSDC Planetary Fact Sheet](https://nssdc.gsfc.nasa.gov/planetary/factsheet/) | public domain |
| Each body's precise figures — sidereal year and rotation, equatorial and polar radius, flattening, surface acceleration at equator and pole, J2, solar irradiance, the Moon's recession rate | [NASA NSSDC](https://nssdc.gsfc.nasa.gov/planetary/factsheet/) per-body sheets (`earthfact.html` and the rest) | public domain |
| How fast the day is lengthening: +2.4 ms/century from the Moon's orbit, +1.72 ± 0.03 observed over 2,700 years | [English Wikipedia, "Tidal acceleration"](https://en.wikipedia.org/wiki/Tidal_acceleration) | CC BY-SA 4.0 |
| Where each planet sits on its orbit at J2000 — mean anomaly, argument of perihelion, longitude of the ascending node | [English Wikipedia](https://en.wikipedia.org/) infoboxes | CC BY-SA 4.0 |
| The Moon's phase — days since the new moon of 11 August 1999, modulo a mean synodic month of 29.53059 days | [English Wikipedia, "Lunar phase"](https://en.wikipedia.org/wiki/Lunar_phase), citing Seidelmann 1992 | CC BY-SA 4.0 |
| Montpellier monuments + ranking | [Wikidata](https://www.wikidata.org/) & [OpenStreetMap](https://www.openstreetmap.org/) | CC0 1.0 / ODbL |
| The best-known monuments of all 195 capitals | [Wikidata](https://www.wikidata.org/) (P625 + sitelink counts) | CC0 1.0 |
| The outline of each of those monuments | [OpenStreetMap](https://www.openstreetmap.org/copyright) via [Overpass](https://overpass-api.de/) | ODbL 1.0 |

The historical borders are **fetched from the project's own CDN at the moment you
ask for them, never copied into this repository**: the dataset is GPL-3.0 and DotWorld's
own code is MIT, and mixing those licences by redistribution is not something a map
should do quietly. They are approximations drawn for illustration, not a legal record
of any border.

The solar system is drawn from **two-body Kepler orbits**. That is the standard
approximation and it is good to a fraction of a degree from 1800 to 2050; outside
that it drifts, and the panel says so rather than letting the picture imply a
precision it does not have. Nothing is perturbed by anything else, so the Moon is
the roughest of them - its node and its perigee really do move, and here they do
not. **This is a picture to think with, not an ephemeris.** For real positions use
[JPL Horizons](https://ssd.jpl.nasa.gov/horizons/).

Monument ranking counts how many Wikipedia editions and sister projects cover each
site — so the ordering is really the work of **Wikipedia's editors**. Montpellier's
ten count Wikipedia editions only; the capitals' three count every sitelink, which is
cheaper to ask for and is applied the same way to every candidate.

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
