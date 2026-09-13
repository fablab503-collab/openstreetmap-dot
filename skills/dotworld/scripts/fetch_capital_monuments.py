#!/usr/bin/env python3
"""The best-known monuments of every capital, as GeoJSON, from Wikidata (CC0).

"Best known" is the proxy DotWorld uses everywhere: how many Wikipedia editions and
sister projects link to the item (`wikibase:sitelinks`). The ranking is really the
work of Wikipedia's editors - credit it that way.

One query per capital; a single query over 195 cities times out. What the shape of
the query has to avoid:

  * `wdt:P31/wdt:P279*` against "architectural structure" times out (504) on Paris,
    Rome and Cairo - the subclass closure is enormous. Ask for `wdt:P31` only and
    sort out the types here, where it is free.
  * Counting Wikipedia sitelinks by joining `schema:about` is what made it slow.
    `wikibase:sitelinks` is one indexed number per item. It counts Commons and
    Wikivoyage too, which is fine as long as EVERY candidate is counted that way.
  * `wikibase:around` rather than `wdt:P131*`: administrative hierarchies differ
    from country to country, a radius does not. 25 km reaches Versailles from Paris
    without reaching the next city.
  * A city's own item tops its list (Paris has 366 sitelinks), as do its language,
    its region and any Olympics held there. Keep only items with a monument-like
    P31, and drop anything typed as a settlement, language, school, airport and so
    on. Whitelist first, then block: "city gate" must survive a block on "city".
  * Vatican City sits inside Rome's radius, Brazzaville inside Kinshasa's: each
    monument is given to the capital it is nearest to, so nothing is drawn twice.
  * The row limit is not an item limit: every P31 an item has is another row, so 60
    rows can be a dozen items and Rome came back without the Colosseum. 150 rows.
  * Small capitals have nothing above the sitelink floor, so the floor drops and the
    query runs again rather than leaving the capital blank.
  * Whitelisting on a keyword inside a type label needs the label read whole:
    "historical country" contains "historic", which put the Roman Empire, the
    Tokugawa shogunate and the Kingdom of Great Britain above the buildings those
    cities are actually known for.

Usage:
    python3 fetch_capital_monuments.py ../../../data/world-capitals.geojson [top] \
        [only]  > capital-monuments.geojson
"""
import http.client
import json
import math
import re
import sys
import time
import urllib.parse
import urllib.request

UA = "DotWorld-data/1.0 (https://github.com/fablab503-collab/openstreetmap-dot)"
RADIUS_KM = 25
PAUSE = 0.6
FLOORS = (12, 2)        # sitelink floors to try, in order

# Matched on word boundaries, not as bare substrings: "arch" inside "constitutional
# monarchy" put Antigua and Barbuda itself on the map, and "villa" inside "village"
# put a hamlet called Bolans next to it.
KEEP = ("museum", "gallery", "tower", "cathedral", "basilica", "church", "chapel",
        "abbey", "monastery", "convent", "mosque", "synagogue", "temple", "shrine",
        "pagoda", "stupa", "palace", "château", "chateau", "castle", "fortress",
        "fort", "citadel", "gate", "monument", "memorial", "mausoleum", "tomb",
        "pyramid", "obelisk", "statue", "arch", "bridge", "square", "plaza",
        "park", "garden", "theatre", "theater", "opera", "library", "landmark",
        "archaeological", "ruin", "amphitheat", "lighthouse", "town hall",
        "capitol", "parliament building", "cemetery", "aqueduct", "wall",
        "heritage site", "historic site", "historic building", "historic house",
        "listed building", "villa", "fountain", "observatory",
        "residence", "cultural centre", "cultural center", "zoo")

BLOCK_EXACT = {"city", "big city", "megacity", "metropolis", "global city",
               "national capital", "largest city", "capital city", "municipality",
               "commune of france", "human settlement", "city or town",
               "administrative territorial entity", "port city", "island"}
# A type label can carry a keyword and still not be a monument: "historical
# country" reads as historic, so the Roman Empire, the Tokugawa shogunate and the
# Kingdom of Great Britain all out-linked the buildings they are famous for.
BLOCK_PART = ("sovereign state", "island country", "country", "monarchy", "realm",
              "village", "town", "hamlet", "suburb", "neighborhood", "neighbourhood",
              "borough", "district", "region", "province", "territory",
              "historical country", "former country", "empire", "dynasty",
              "civilization", "civilisation", "shogunate", "mandate", "kingdom",
              "wikimedia list", "wikimedia category", "historical period", "war",
              "treaty", "ethnic group", "aspect of history",
              "language", "university", "business school", "grande école", "airport",
              "stadium", "railway station", "metro station", "olympic", "human",
              "organization", "organisation", "specialized agency", "political party",
              "hospital", "hotel", "shopping", "company", "football", "enterprise",
              "television", "newspaper", "record label", "sports", "brand")

# A block must not beat a strong match: the Colosseum is typed "stadium" as well as
# "Roman amphitheatre" and "archaeological site", and blocking stadiums buried Rome's
# most linked monument (148 sitelinks). Modern stadiums have no strong type, so they
# still go.
STRONG = ("amphitheat", "archaeological", "ruin", "monument", "heritage site",
          "cathedral", "basilica", "temple", "pyramid", "mausoleum", "palace",
          "castle", "fortress", "citadel", "obelisk", "triumphal arch",
          "historic site", "abbey", "mosque", "shrine", "pagoda")

KEEP_RE = re.compile(r"\b(" + "|".join(re.escape(k) for k in KEEP) + r")")
STRONG_RE = re.compile(r"\b(" + "|".join(re.escape(k) for k in STRONG) + r")")

QUERY = """
SELECT ?item ?itemLabel ?links ?typeLabel ?coord WHERE {
  SERVICE wikibase:around {
    ?item wdt:P625 ?coord .
    bd:serviceParam wikibase:center "Point(%LON% %LAT%)"^^geo:wktLiteral .
    bd:serviceParam wikibase:radius "%RAD%" .
  }
  ?item wikibase:sitelinks ?links . FILTER(?links >= %FLOOR%)
  ?item wdt:P31 ?type .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
}
ORDER BY DESC(?links) LIMIT 150
"""


def sparql(query, attempts=3, timeout=180):
    url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"query": query})
    req = urllib.request.Request(url, headers={
        "Accept": "application/sparql-results+json", "User-Agent": UA})
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.load(resp)["results"]["bindings"]
        except (http.client.HTTPException, OSError, ValueError) as exc:
            if attempt == attempts:
                raise
            print(f"  attempt {attempt} failed ({exc.__class__.__name__}), retrying",
                  file=sys.stderr)
            time.sleep(4 * attempt)


def monuments(lon, lat, city, top):
    """Ask for the best-linked things near a capital, then keep the monuments."""
    for floor in FLOORS:
        rows = sparql(QUERY.replace("%LON%", str(lon)).replace("%LAT%", str(lat))
                           .replace("%RAD%", str(RADIUS_KM)).replace("%FLOOR%", str(floor)))
        items = {}
        for r in rows:
            q = r["item"]["value"].rsplit("/", 1)[-1]
            it = items.setdefault(q, {"name": r["itemLabel"]["value"],
                                      "links": int(r["links"]["value"]),
                                      "coord": r["coord"]["value"], "types": []})
            it["types"].append(r["typeLabel"]["value"].lower())

        out = []
        for q, it in sorted(items.items(), key=lambda kv: -kv[1]["links"]):
            if re.fullmatch(r"Q\d+", it["name"]) or it["name"] == city:
                continue
            if not any(KEEP_RE.search(t) for t in it["types"]):
                continue
            blocked = (any(t in BLOCK_EXACT for t in it["types"])
                       or any(b in t for t in it["types"] for b in BLOCK_PART))
            if blocked and not any(STRONG_RE.search(t) for t in it["types"]):
                continue
            m = re.match(r"Point\(([-\d.]+) ([-\d.]+)\)", it["coord"])
            if not m:
                continue
            out.append({"name": it["name"], "wikis": it["links"], "q": q,
                        "lon": round(float(m.group(1)), 5),
                        "lat": round(float(m.group(2)), 5)})
            if len(out) == top:
                break
        if out:
            return out
    return []


def haversine(lat1, lon1, lat2, lon2):
    r = math.radians
    a = (math.sin(r(lat2 - lat1) / 2) ** 2
         + math.cos(r(lat1)) * math.cos(r(lat2)) * math.sin(r(lon2 - lon1) / 2) ** 2)
    return 6371 * 2 * math.asin(min(1, math.sqrt(a)))


def main():
    caps = json.load(open(sys.argv[1], encoding="utf-8"))["features"]
    top = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    only = set(sys.argv[3].split(",")) if len(sys.argv) > 3 else None

    todo = [c for c in caps if not only
            or c["properties"]["country"] in only or c["properties"]["name"] in only]
    found, empty = {}, []
    for i, c in enumerate(todo, 1):
        p = c["properties"]
        lon, lat = c["geometry"]["coordinates"]
        try:
            best = monuments(lon, lat, p["name"], top + 3)   # spares for the de-dupe
        except Exception as exc:                 # one city must not sink the run
            print(f"{i:3}/{len(todo)} {p['name']}: FAILED {exc}", file=sys.stderr)
            best = []
        found[p["country"]] = {"p": p, "lon": lon, "lat": lat, "mons": best}
        print(f"{i:3}/{len(todo)} {p['name']:<16} "
              + ", ".join(f"{m['name']} ({m['wikis']})" for m in best[:top]),
              file=sys.stderr)
        time.sleep(PAUSE)

    # Vatican City is 4 km from Rome and Brazzaville 5 km from Kinshasa, so a radius
    # query hands the same monument to both. Each one belongs to whichever capital
    # it is actually nearest.
    owner = {}
    for country, e in found.items():
        for m in e["mons"]:
            d = haversine(e["lat"], e["lon"], m["lat"], m["lon"])
            if m["q"] not in owner or d < owner[m["q"]][1]:
                owner[m["q"]] = (country, d)

    features = []
    for country, e in sorted(found.items()):
        mine = [m for m in e["mons"] if owner.get(m["q"], (None,))[0] == country][:top]
        if not mine:
            empty.append(e["p"]["name"])
        for rank, m in enumerate(mine, 1):
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [m["lon"], m["lat"]]},
                "properties": {"name": m["name"], "city": e["p"]["name"],
                               "country": country, "cc": e["p"].get("cc", ""),
                               "wikis": m["wikis"], "rank": rank}})

    json.dump({"type": "FeatureCollection", "features": features},
              sys.stdout, ensure_ascii=False)
    print(f"\n{len(features)} monuments for {len(todo) - len(empty)} of {len(todo)} "
          f"capitals; nothing found for {len(empty)}: {empty}", file=sys.stderr)

if __name__ == "__main__":
    main()
