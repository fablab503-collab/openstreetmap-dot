# Publishing and credits

## DotWorld's standing rule

Every update is committed and pushed straight away, with **README** (features,
controls, readouts), **CREDITS.md** (every source, with licence) and **CHANGELOG.md**
(fixes and improvements, with measured numbers) updated in the same commit. No need
to ask first. Then confirm the new content is actually live.

## GitHub Pages

| Need | Why |
|---|---|
| `.nojekyll` at the root | Pages runs Jekyll by default, which drops files and folders it dislikes |
| Relative asset paths | A project site lives under `/<repo>/` |
| `.mjs` served as `text/javascript` | A wrong MIME type breaks ES module loading entirely — check with `curl -sI` |
| HTTPS for every external call | Pages is HTTPS; mixed content is blocked |
| Verify the new content, not the push | Pages rebuilds in ~30–60 s and caches HTML briefly |

Enable Pages through the API:

```bash
TOKEN=$(gh auth token)          # never print it
curl -sS -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/<owner>/<repo>/pages \
  -d '{"source":{"branch":"main","path":"/"}}'
```

Confirm it is live by content, with a cache-busting query:

```bash
curl -sS "https://<owner>.github.io/<repo>/index.html?v=$(date +%s)" | grep -q 'a string only the new build has'
```

If a browser still shows the old build, hard-refresh (⇧⌘R).

### On this Mac's Claude sandbox

- `git push` works; `fatal: failed to store: 100001` is only the keychain store step
  failing after a successful push.
- `gh api` fails on the sandbox proxy's TLS (`x509: OSStatus -26276`) and
  `gh auth status` wrongly calls the token invalid — but `gh auth token` + `curl`
  works.
- `git init` under `fablab-tools` is blocked (cannot write `.git/config`); on
  `/Volumes/Volume1` it works.
- The sandbox cannot bind a port; the user runs `python3 -m http.server 8732`.
- Stage files by name — never `git add -A` in a folder with a local `.claude/`.

## Credits DotWorld gives

| Source | Used for | Licence |
|---|---|---|
| © OpenStreetMap contributors | all map data | ODbL 1.0 — attribution must stay visible |
| OpenFreeMap (Zsolt Ero) | vector tiles | free, no API key. Required on-map credit, from its TileJSON `attribution`: "OpenFreeMap © OpenMapTiles Data from OpenStreetMap" — DotWorld's first version left out © OpenMapTiles |
| © OpenMapTiles | the vector tile schema | credit must be visible and linked |
| MapLibre GL JS | rendering, globe, camera | BSD-3-Clause (vendored) |
| Nominatim, OpenStreetMap Foundation | search, country lookup | ODbL data, usage policy |
| World Bank Open Data | world statistics | CC BY 4.0 |
| Wikidata | commune and capital populations, capitals, monuments | CC0 1.0 |
| Wikipedia editors | monument ranking by language coverage | — |
| ColorBrewer (Cynthia Brewer, Mark Harrower, Penn State) | YlOrRd | Apache 2.0 |
| Dotwork, Space Mono, Space Grotesk | typography | SIL OFL 1.1 |

Where the credits appear: an attribution line always visible on the map (MapLibre's
own control is hidden under the overlay canvas, so render it yourself), a *credits &
disclaimer* panel in the app, `CREDITS.md`, and the README.

### Licence scoping

- MIT covers only the original code. State in the licence file that it **cannot
  relicense** the ODbL map data, CC BY statistics, CC0 datasets or bundled libraries.
- **Ndot** (Nothing's dot typeface) is licensed solely for Nothing brand materials and
  forbids serving the files publicly. For a public repo ship **Dotwork** (OFL, same
  5×7 grid and Ndot 57 metrics). Acknowledge the inspiration; claim no association.
- The disclaimer DotWorld carries: a fun personal experiment built with Claude; not
  affiliated with or endorsed by any upstream project; exists because they gave their
  work away; takes nothing from them. Plus links to support the OSMF, OpenFreeMap,
  MapLibre and Wikimedia.

## Privacy

Geolocation only on a button press; coordinates rounded to ~1 km before reverse
geocoding; the map frames the country, not the person, so a position never lands in
the shareable `#map=` hash.

## Free community services

Tiles, search and statistics come from free services with fair-use expectations.
Debounce search, cache what you can, and send a real `User-Agent` with scripted
Wikidata queries.
