# Data

Reproducible versions of these fetches are in `scripts/`. Run them from the repo's
`data/` folder; they print GeoJSON or JSON to stdout and a summary to stderr.

## What the tiles give you

OpenFreeMap serves the OpenMapTiles schema.

| Layer | Useful fields | Not there |
|---|---|---|
| `place` | `capital`, `class`, `iso_a2`, `name`, `rank` | **population** |
| `poi` | `class`, `subclass`, `name`, `rank` | notability, rankings |
| `boundary` | `admin_level`, `adm0_l`, `adm0_r` (country code on each side) | — |
| `building` | `render_height`, `render_min_height` | — |

`adm0_l`/`adm0_r` are what light up one country's border:

```js
map.setFilter('country-glow', ['all', ['==', ['get', 'admin_level'], 2],
  ['any', ['==', ['get', 'adm0_l'], cc], ['==', ['get', 'adm0_r'], cc]]]);
```

## World statistics — World Bank Open Data (CC BY 4.0)

`https://api.worldbank.org/v2/country/WLD/indicator/<ID>?format=json&mrv=1`

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
- Result used: **644 communes**, Paris 2,103,778 down to 15,023.
- **Official alternative:** INSEE legal populations via API Géo —
  `https://geo.api.gouv.fr/communes?fields=nom,code,population,centre` — about 670
  communes of 15k+ including Paris (75056). Credit "Insee, populations légales".

## The 195 capitals — Wikidata (CC0)

```sparql
SELECT ?country ?countryLabel ?capLabel ?coord (MAX(?p) AS ?pop) WHERE {
  { ?country p:P463 ?m . ?m ps:P463 wd:Q1065 . FILTER NOT EXISTS { ?m pq:P582 ?end } }
  UNION { VALUES ?country { wd:Q237 wd:Q219060 } }
  ?country wdt:P31 wd:Q3624078 ; wdt:P36 ?cap .
  ?cap wdt:P625 ?coord .
  FILTER NOT EXISTS { ?country wdt:P576 ?dissolved }
  OPTIONAL { ?cap wdt:P1082 ?p }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
}
GROUP BY ?country ?countryLabel ?capLabel ?coord
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
- 194 of 195 have a population; **Ngerulmud (Palau)** has none.
- Range 747 (Yaren District, Nauru) to 21,893,095 (Beijing) — use a log scale.
- Some figures are the city proper, others the whole municipality (Beijing, Tokyo),
  so cross-country comparisons are rough. Put that in the legend.
- "Country count" is definitional: 195 here; ISO 3166 lists 249 codes.

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

## Geocoding — Nominatim (OpenStreetMap Foundation)

- Search: `https://nominatim.openstreetmap.org/search?format=jsonv2&limit=6&q=…`,
  debounced ~450 ms — the usage policy allows about one request a second.
- Frame results with `boundingbox` when present; otherwise `flyTo` the point.
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
 "properties":{"name":"Beijing","country":"People's Republic of China","pop":21893095,"seats":1}}

{"type":"Feature","geometry":{"type":"Point","coordinates":[3.88019,43.61174]},
 "properties":{"name":"musée Fabre","cat":"museum","rank":1,"wikis":25}}
```
