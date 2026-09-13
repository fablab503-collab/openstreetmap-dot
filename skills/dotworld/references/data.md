# Data

Reproducible versions of these fetches are in `scripts/`. Run them from the repo's
`data/` folder; they print GeoJSON or JSON to stdout and a summary to stderr.

## What the tiles give you

OpenFreeMap serves the OpenMapTiles schema.

| Layer | Useful fields | Not there |
|---|---|---|
| `place` | `capital`, `class`, `iso_a2`, `name`, `rank` | **population** |
| `poi` | `class`, `subclass`, `name`, `rank` | notability, rankings |
| `boundary` | `admin_level`, `disputed`, `maritime` always; `adm0_l`/`adm0_r` (country code each side) **only from z5** | country polygons |
| `building` | `render_height`, `render_min_height` | — |

`adm0_l`/`adm0_r` are what light up one country's border:

```js
map.setFilter('country-glow', ['all', ['==', ['get', 'admin_level'], 2],
  ['any', ['==', ['get', 'adm0_l'], cc], ['==', ['get', 'adm0_r'], cc]]]);
```

**But only from zoom 5.** The TileJSON lists `adm0_l`/`adm0_r` for z0-14, which is
the schema, not the data. Decode a tile and look: at z3 and z4 the boundary features
carry `admin_level`, `disputed` and `maritime` and nothing else, so that filter
matches nothing — and a country framed whole sits at z2-z7. Check it without a
browser:

```bash
curl -sS https://tiles.openfreemap.org/planet            # -> tiles URL template
curl -sS --compressed -o t.pbf ".../5/16/11.pbf"          # a tile over the border
python3 -c "import re;print(set(re.findall(rb'adm0_[lr]', open('t.pbf','rb').read())))"
```

A vector tile stores its property names as plain strings, so grepping the
decompressed bytes answers "is this field in this tile" in one line.

There are **no country polygons in the tiles at all**, at any zoom. To fill or
outline a whole country you have to bring your own - see *Country outlines* below.

## World statistics — World Bank Open Data (CC BY 4.0)

`https://api.worldbank.org/v2/country/WLD/indicator/<ID>?format=json&mrv=1`

Swap `WLD` for an ISO 3166-1 alpha-2 code to get one country:
`…/country/FR/indicator/SP.POP.TOTL?format=json&mrv=1`. Not every code has a figure
(Vatican City has none), so treat a missing `value` as "no figure", not an error.

| Indicator | Meaning | Value used (year) |
|---|---|---|
| `SP.POP.TOTL` | population | 8,215,424,893 (2025) |
| `SP.DYN.CBRT.IN` | births per 1,000 a year | 16.273 (2024) |
| `SP.DYN.CDRT.IN` | deaths per 1,000 a year | 7.551 (2024) |
| `SP.URB.TOTL.IN.ZS` | urban share, % | 57.8 (2025) |
| `AG.LND.TOTL.K2` | land area, km² | 129,763,686 (2023) |

The counter is a **projection**. Annual figures are mid-year estimates, so anchor to
1 July and compound the net rate:

```js
const YEAR_MS = 365.2425 * 86400 * 1000;
const years = (Date.now() - Date.UTC(popYear, 6, 1)) / YEAR_MS;
const pop = basePop * Math.pow(1 + (birth - death) / 1000, years);
const bornPerSec = pop * (birth / 1000) / (YEAR_MS / 1000);     // ≈ 4.28/s
const diedPerSec = pop * (death / 1000) / (YEAR_MS / 1000);     // ≈ 1.99/s, net ≈ +2.29/s
```

Refetch at load and keep baked-in constants as the fallback — and show which one is
in use (green "WORLD BANK 2025" vs amber "CACHED").

## Population of the whole world — GeoNames (CC BY 4.0)

`scripts/fetch_world_population.py`. One file, no API: `cities15000.txt` inside
https://download.geonames.org/export/dump/cities15000.zip is every settlement over
15,000 people with coordinates, country and population — **34,091 cities**, Shanghai
(24,874,500) down to 15,001.

- **Wikidata does not scale to this.** The commune query below works for one
  country; worldwide it times out, and population statements are uneven between
  countries — a census figure here, an estimate there, nothing at all elsewhere.
- **Ship `[lon, lat, pop]` triples, not GeoJSON**, when the layer draws circles and
  never reads a name: 5.1 MB against **762 KB (303 KB gzipped)** for the same 34,091
  cities. Build the GeoJSON client-side in one `map()` and hand it to `setData`.
- Keep the UTF-8 name column, not the ASCII one, if you do need names.
- Sort ascending by population so the biggest cities are last in the file and
  therefore drawn on top.
- **Space colour stops by a constant ratio.** City sizes cover three orders of
  magnitude; DotWorld's world ramp is 15k, 44k, 128k, 373k, 1.09M, 3.18M, 9.3M, 25M
  against the eight reversed YlOrRd steps. Even spacing paints everything under a
  million the same dark red.
- CC BY 4.0: the credit has to stay visible.

## Population of French communes — Wikidata (CC0)

```sparql
SELECT ?itemLabel ?coord (MAX(?p) AS ?pop) WHERE {
  { ?item wdt:P31 wd:Q484170 } UNION { VALUES ?item { wd:Q90 } }
  ?item wdt:P1082 ?p ; wdt:P625 ?coord .
  FILTER(?p > 15000)
  SERVICE wikibase:label { bd:serviceParam wikibase:language "fr,en" }
}
GROUP BY ?itemLabel ?coord
ORDER BY DESC(?pop)
```

- **Why the union:** `wdt:` returns only an item's best-ranked statements. Paris's
  "commune of France" statement is **normal rank and ended on 2018-12-31**, while
  "territorial collectivity of France with special status" (Q22923920) is
  **preferred, since 2019-01-01** (checked 2026-09-11) — so `wdt:P31 wd:Q484170`
  alone silently drops the country's largest city and Marseille comes out on top. Adding Q22923920 as a class also pulls in the
  Métropole de Lyon, Aix-Marseille, Corsica and old Paris districts.
- `MAX(?p)` collapses towns with several population statements. A stricter version
  takes the statement with the latest `pq:P585` date and de-duplicates by INSEE code
  (`P374`).
- Filter to metropolitan France with a bounding box (lon −5.5…10, lat 41…51.5).
- Result used: **644 communes**, Paris 2,103,778 down to 15,023. This was DotWorld's
  population layer until 2026-09-14, when the whole world replaced it.
- **Official alternative:** INSEE legal populations via API Géo —
  `https://geo.api.gouv.fr/communes?fields=nom,code,population,centre` — about 670
  communes of 15k+ including Paris (75056). Credit "Insee, populations légales".

## The 195 capitals — Wikidata (CC0)

```sparql
SELECT ?country ?countryLabel ?cc ?capLabel ?coord (MAX(?p) AS ?pop) WHERE {
  { ?country p:P463 ?m . ?m ps:P463 wd:Q1065 . FILTER NOT EXISTS { ?m pq:P582 ?end } }
  UNION { VALUES ?country { wd:Q237 wd:Q219060 } }
  ?country wdt:P31 wd:Q3624078 ; wdt:P36 ?cap .
  ?cap wdt:P625 ?coord .
  FILTER NOT EXISTS { ?country wdt:P576 ?dissolved }
  OPTIONAL { ?cap wdt:P1082 ?p }
  OPTIONAL { ?country wdt:P297 ?cc }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,mul,en-gb,fr,es" }
}
GROUP BY ?country ?countryLabel ?cc ?capLabel ?coord
ORDER BY ?countryLabel
```

- **A truthy `wdt:P463 wd:Q1065` includes historical memberships.** It returns ~229
  countries, and even after restricting to undissolved sovereign states it still
  lets in **Taiwan**, whose UN seat passed to the People's Republic of China in 1971.
  DotWorld shipped that version for a day: Taiwan in, **Vatican City** missing — and
  the total was still 195, so the count hid the error. Check the *set*, not the size.
- **"No end date" alone is not enough either.** Filtering to membership statements
  without `pq:P582` gives 203 — about ten predecessor entities (Kingdom of Laos,
  Third Hellenic Republic, realm of the United Kingdom, …) have open-ended
  statements. The query above needs **both** filters, plus Vatican (Q237) and
  Palestine (Q219060): exactly **195**, verified against current membership.
- 205 rows, but only **7 states have several distinct seats** — Bolivia, Eswatini,
  Pakistan, Palestine, South Africa, Sri Lanka, Yemen. Jordan and Syria return the
  *same* capital twice as separate items; count distinct names, not rows. DotWorld
  shows the most populous seat (South Africa → Cape Town) — a rule, not a fact.
- **Store P297, the ISO 3166-1 alpha-2 code**, if you ever want to light one
  country: that is exactly what the tiles put in `adm0_l`/`adm0_r`. One UN member
  has none of its own — the member is the *Kingdom of Denmark* (Q756617) while DK
  belongs to *Denmark* (Q35), its European part. Fill that one in by hand.
- 194 of 195 have a population; **Ngerulmud (Palau)** has none.
- **Ask the label service for `"en,mul,..."`, never `"en"` alone.** Wikidata is
  moving names that read the same in every language to the `mul` code. St. John's
  (Q36262), capital of Antigua and Barbuda, has no English label at all any more, so
  the service returned the string "Q36262" — and DotWorld drew that on the map.
- Range 747 (Yaren District, Nauru) to 21,893,095 (Beijing) — use a log scale.
- Some figures are the city proper, others the whole municipality (Beijing, Tokyo),
  so cross-country comparisons are rough. Put that in the legend.
- "Country count" is definitional: 195 here; ISO 3166 lists 249 codes.

## Country outlines — Natural Earth (public domain)

`scripts/build_countries.py` turns Natural Earth's admin-0 set into one polygon per
country, keyed by ISO 3166-1 alpha-2 so it joins the capitals file and the tiles.

- **Use 1:50m, not 1:110m.** 110m is half the size and drops 29 of the 195: every
  small island state, plus Singapore, Malta, Monaco and Vatican City. 50m has all 195.
- **Match on `ISO_A2_EH`.** Plain `ISO_A2` is `-99` for France, Norway and others.
  Fall back to `ISO_A2`, then `WB_A2`.
- Raw it is 2.9 MB. Simplified (Ramer-Douglas-Peucker at 0.02 degrees) and rounded to
  2 decimals it is **780 KB, 225 KB gzipped, 47k points** - fetched only when someone
  picks a country. 0.01 degrees is under a pixel at z7, which is as far in as this
  layer is drawn.
- Simplification can erase a country: a ring that survives with fewer than 4 points
  keeps its original shape, or Tuvalu, Nauru and the Maldives vanish.
- Draw it as a translucent fill (the lattice lifts inside the country) plus a line
  that fades out by z6, where the tiles' own sharper border takes over.
- For a *building*, draw edges rather than a fill, and in 3D draw them as geometry:
  **MapLibre 6.9 has no elevated lines** (`line-z-offset` is not in the build), so a
  line cannot sit at roof height; and an extruded slab of the footprint shows its
  cap, which fills the building in again as soon as the camera tilts. Turn the
  outline into a ribbon of quads instead - one per edge, a few metres wide - and
  extrude that: from the ground it fences the foot, at roof height it fences the
  roofline, and a ribbon has no cap to fill anything. Corners can overlap; mitring
  them costs more than it shows.

## Ranking a city's monuments

Neither source is complete on its own. For Montpellier, OpenStreetMap had the
cathedral and the Arc de Triomphe but no Musée Fabre tagged `tourism=museum`;
Wikidata had Musée Fabre and Place de la Comédie but not the cathedral.

1. **Wikidata:** items located in the city (`wdt:P131* wd:<city>`), with coordinates,
   whose type is a monument-like class.
2. **OpenStreetMap (Overpass):** `historic=*`, `tourism=attraction|museum`,
   `building=cathedral` and `amenity=place_of_worship`, each with a `wikidata` tag,
   scoped to the city's own boundary with `area["wikidata"="<city>"]`. Traps:
   - a **bounding box leaks neighbouring towns** — around Montpellier it pulled in
     the archaeological site of Lattara, which is in Lattes;
   - Montpellier's cathedral is tagged **`building=cathedral`**, not `historic`;
   - an area query with a case-insensitive **name regex** timed out after 79 s;
   - responses sometimes arrive truncated or drop the connection — retry.
3. Count **Wikipedia** sitelinks for every candidate in one SPARQL query, so both
   sources are ranked on the same measure. DotWorld's first run did not: it counted
   Wikipedia-only links for Wikidata items but *all* sitelinks (Commons, Wikivoyage…)
   for OSM items.
4. Merge by Wikidata id, else by normalised name; exclude non-monuments (a stadium
   topped the list at 36 wikis); sort by the count.

**Notability proxy:** the number of Wikipedia language editions covering an item.
The ordering is really the work of Wikipedia's editors — credit it that way.

Montpellier as shipped on the site (first run, mixed measures): musée Fabre 25 ·
Cathédrale Saint-Pierre 17 · Porte du Peyrou 15 · Place de la Comédie 7 · Tour de la
Babote 7 · Opéra Comédie 7 · Notre-Dame des Tables 5 · Château de Flaugergues 5 ·
Lycée Joffre 5 · promenade du Peyrou 4.

`rank_monuments.py Q6441` on 2026-09-11 (one measure, city boundary): musée Fabre 25 ·
Cathédrale Saint-Pierre 16 · Porte du Peyrou 14 · Place de la Comédie 7 · Mosquée
Avicenne 6 · Opéra Comédie 6 · tour de la Babotte 6 · Notre-Dame des Tables 5 ·
Lycée Joffre 4 · château de Flaugergues 4. The mosque came in through
`amenity=place_of_worship`; the promenade du Peyrou dropped out. The site still shows
the first list — switching is an editorial decision for the owner.

The two runs spell one tower two ways ("Tour de la Babote" as shipped, "tour de la
Babotte" from the script) — which is why the Wikidata id is the merge key and a
name match is only the fallback for items without one.

Categories are assigned by hand after ranking.

## The best-known monuments of a capital — Wikidata (CC0)

`scripts/fetch_capital_monuments.py`, one query per capital. The shape below is the
third attempt; the first two timed out or returned empires instead of buildings.

```sparql
SELECT ?item ?itemLabel ?links ?typeLabel ?coord WHERE {
  SERVICE wikibase:around {
    ?item wdt:P625 ?coord .
    bd:serviceParam wikibase:center "Point(2.3522 48.8567)"^^geo:wktLiteral .
    bd:serviceParam wikibase:radius "25" .
  }
  ?item wikibase:sitelinks ?links . FILTER(?links >= 12)
  ?item wdt:P31 ?type .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
}
ORDER BY DESC(?links) LIMIT 150
```

- **Do not walk `wdt:P31/wdt:P279*`.** Against "architectural structure" it is the
  only correct-looking way to catch an amphitheatre, a city gate and a mausoleum —
  and it returns 504 on Paris, Rome and Cairo. Ask for `wdt:P31` and sort the types
  out in your own code, where it costs nothing.
- **`wikibase:sitelinks` instead of counting `schema:about`.** One indexed number
  per item versus a join that made the query minutes long. It counts Commons and
  Wikivoyage too; that is fine as long as every candidate is counted that way.
- **`wikibase:around`, not `wdt:P131*`.** Administrative hierarchies differ from
  country to country; a radius does not. 25 km reaches Versailles from Paris.
- **The row limit is not an item limit.** Every P31 an item has is another row, so
  150 rows may be 30 items. At 60, Rome came back without the Colosseum.
- **Match type keywords on word boundaries.** "arch" inside *constitutional
  monarchy* put Antigua and Barbuda itself on the map; "villa" inside *village*
  added a hamlet called Bolans.
- **A block list must not beat a strong match.** The Colosseum is typed `stadium`
  as well as `Roman amphitheatre` and `archaeological site`; blocking stadiums to
  keep football grounds out buried Rome's most-linked monument (148 sitelinks).
  Modern stadiums have no strong type, so they still go.
- **"historical country" contains "historic".** With that in the keep list, Rome
  returned the Roman Empire, Tokyo the Tokugawa shogunate and London the Kingdom of
  Great Britain — each out-linking the buildings those cities are known for.
- **Give a monument to the nearest capital.** Vatican City is 4 km from Rome and
  Brazzaville 5 km from Kinshasa, so a radius query hands the same item to both.
- A city's own item always tops its list (Paris: 366 sitelinks), as do its language,
  its region and any Olympics held there.
- Sanity check on the result, not on the count: Paris → Eiffel Tower, Louvre,
  Notre-Dame. Rome → Colosseum, St. Peter's, Sistine Chapel. Athens → Parthenon,
  Acropolis. Moscow → Red Square, Kremlin, St. Basil's.

## Time zones — GeoNames (CC BY 4.0)

`scripts/add_capital_timezones.py` writes an IANA zone name onto each capital.

- **A zone cannot be derived from longitude.** China runs one zone across sixty
  degrees, India is half an hour off the hour, Spain keeps Berlin's time, Kathmandu
  is +05:45. Nepal is not an edge case you can round away.
- The tz boundary polygons are tens of megabytes; `cities15000.txt` already carries
  a zone per city, so the nearest city gives the capital its zone for free.
- **Nearest city *in the same country*.** Otherwise Vienna borrows Bratislava's zone
  55 km away. Fall back to the nearest city anywhere only when the country has no
  city in the file — Vatican City takes Rome's, which is correct.
- **Store the name, never the offset.** `Europe/Paris` lets the browser apply
  daylight saving; `+02:00` is wrong for half the year.
- For the user's own zone, `Intl.DateTimeFormat().resolvedOptions().timeZone` needs
  no permission and no lookup at all.
- Offsets: round-trip `toLocaleString` through UTC and the zone rather than parsing
  `timeZoneName: 'longOffset'` — same answer to the minute, works in every engine.

## Monument footprints — OpenStreetMap via Overpass (ODbL)

`scripts/fetch_monument_shapes.py`. A dot at a coordinate says something is there;
the building's outline says what it is, and in a dot lattice the shape is the whole
point — the Colosseum's ellipse, the Capitol's wings.

- **The tiles cannot help.** Their `building` layer carries `render_height` and
  `render_min_height` and nothing else: no name, no id, no wikidata tag. There is no
  way to ask them for one particular building.
- **Match by position, not by id.** Wikidata gives you a point; OSM has the polygon.
  Ask Overpass for every way and relation with a `wikidata` tag within 150 m of the
  point and keep the nearest centroid inside 200 m, so two monuments on one street
  cannot swap outlines.
- **Batch the `around` clauses**: 40 monuments per query is 13 queries for 491
  rather than 491. Expect HTTP errors and truncated reads anyway — retry.
- **Assemble relations yourself.** `out geom` returns a multipolygon's outer ways as
  separate strips, unordered and sometimes reversed. Join them end to end into
  closed rings or the biggest monuments come out as scribbles.
- **Simplify.** Westminster Abbey arrives with 547 points. Ramer-Douglas-Peucker at
  0.00002 degrees (~2 m, far under one dot even at street zoom) leaves 108 and takes
  the file from 400 KB to 220 KB (44 KB gzipped).
- Coverage: **355 of 491 monuments (72%), in 162 capitals.** The rest have no
  wikidata-tagged way near the point — the marker still shows, it just has no shape.

## Geocoding — Nominatim (OpenStreetMap Foundation)

- Search: `https://nominatim.openstreetmap.org/search?format=jsonv2&limit=6&q=…`,
  debounced ~450 ms — the usage policy allows about one request a second.
- Frame results with `boundingbox` when present; otherwise `flyTo` the point.
- **Do not frame a country from a geocoder box.** Nominatim returns everything the
  country owns: Portugal's box reaches the Azores, France's spans the planet because
  of French Polynesia, and Fiji's is the whole world because it crosses the
  antimeridian. If you have the country's outline, frame the biggest ring of it and
  skip any ring whose longitude span is over 180 degrees; it is more accurate and it
  costs no request at all.
- Reverse for "illuminate my country":
  `…/reverse?format=jsonv2&zoom=3&lat=…&lon=…` → `address.country_code`.
- Privacy: request location only on a button press, round coordinates to 2 decimal
  places (~1 km) before sending, and frame the country rather than the person so the
  position never lands in a shareable URL.

## GeoJSON shapes the app reads

```json
{"type":"Feature","geometry":{"type":"Point","coordinates":[2.3522,48.8567]},
 "properties":{"name":"Paris","pop":2103778}}

{"type":"Feature","geometry":{"type":"Point","coordinates":[116.3913,39.9057]},
 "properties":{"name":"Beijing","country":"People's Republic of China","cc":"CN",
               "pop":21893095,"seats":1}}

{"type":"Feature","geometry":{"type":"Point","coordinates":[3.88019,43.61174]},
 "properties":{"name":"musée Fabre","cat":"museum","rank":1,"wikis":25}}
```
