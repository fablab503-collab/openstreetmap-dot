#!/usr/bin/env python3
"""Rank a city's monuments by Wikipedia coverage, merging Wikidata and OpenStreetMap.

Neither source is complete alone: in Montpellier, OSM had the cathedral and the Arc
de Triomphe but no Musée Fabre tagged tourism=museum; Wikidata had Musée Fabre but
not the cathedral. The notability measure is the number of Wikipedia language
editions covering each item — credit the ordering to Wikipedia's editors.

Traps this script avoids:
  * A bounding box leaks neighbouring towns (it pulled in Lattes' archaeological
    site). Scope OSM to the city's own boundary: area["wikidata"="<QID>"].
  * An Overpass area query with a case-insensitive name regex timed out (79 s).
  * OSM tags Montpellier's cathedral building=cathedral, not historic=*.
  * Count the SAME thing for every candidate: Wikipedia sitelinks only, for items
    from both sources. (The first run counted all sitelinks — Commons, Wikivoyage —
    for the OSM items only.)

Usage:
    python3 rank_monuments.py <city-QID> [top]
    python3 rank_monuments.py Q6441 10

Prints a JSON list (name, kind, wikis, lat, lon, q) to stdout. Assign display
categories by hand afterwards.
"""
import http.client
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request

UA = "DotWorld-data/1.0 (https://github.com/fablab503-collab/openstreetmap-dot)"
EXCLUDE = ("stade", "stadium")      # a stadium topped Montpellier's list at 36 wikis

# Monument-like classes: church building, cathedral, museum, castle, château, house,
# aqueduct, mansion, religious building, square, tower, art museum, mill,
# archaeological site, fortification, historic house museum.
TYPES = ("wd:Q16970 wd:Q2977 wd:Q33506 wd:Q23413 wd:Q751876 wd:Q3947 wd:Q474 "
         "wd:Q1802963 wd:Q24398318 wd:Q174782 wd:Q12518 wd:Q207694 wd:Q44494 "
         "wd:Q839954 wd:Q57821 wd:Q2087181")


def http_json(url, data=None, headers=None, timeout=170, attempts=4):
    """Fetch JSON, retrying: Wikidata and Overpass responses sometimes arrive
    truncated (http.client.IncompleteRead) or drop the connection."""
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA, **(headers or {})})
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.load(resp)
        except (http.client.HTTPException, OSError, ValueError) as exc:
            if attempt == attempts:
                raise
            print(f"attempt {attempt} failed ({exc.__class__.__name__}), retrying",
                  file=sys.stderr)
            time.sleep(3 * attempt)


def sparql(query):
    url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"query": query})
    return http_json(url, headers={"Accept": "application/sparql-results+json"})["results"]["bindings"]


def wikidata_items(city):
    q = f"""
    SELECT DISTINCT ?item ?itemLabel ?coord ?typeLabel WHERE {{
      ?item wdt:P131* wd:{city} ; wdt:P625 ?coord ; wdt:P31 ?type .
      VALUES ?type {{ {TYPES} }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "fr,en" }}
    }}"""
    out = []
    for b in sparql(q):
        m = re.match(r"Point\(([-\d.]+) ([-\d.]+)\)", b["coord"]["value"])
        if m:
            out.append({"name": b["itemLabel"]["value"], "kind": b["typeLabel"]["value"],
                        "q": b["item"]["value"].rsplit("/", 1)[-1],
                        "lon": round(float(m.group(1)), 5), "lat": round(float(m.group(2)), 5)})
    return out


def osm_items(city):
    ql = f"""[out:json][timeout:90];
    area["wikidata"="{city}"]->.a;
    ( nwr["historic"]["wikidata"](area.a);
      nwr["tourism"~"^(attraction|museum)$"]["wikidata"](area.a);
      nwr["building"="cathedral"]["wikidata"](area.a);
      nwr["amenity"="place_of_worship"]["wikidata"](area.a); );
    out center tags;"""
    body = urllib.parse.urlencode({"data": ql}).encode()
    d = {}
    for _ in range(3):                      # a server-side timeout comes back as a remark
        d = http_json("https://overpass-api.de/api/interpreter", data=body)
        if not d.get("remark"):
            break
        time.sleep(5)
    out = []
    for e in d.get("elements", []):
        t = e.get("tags", {})
        lat = e.get("lat") or (e.get("center") or {}).get("lat")
        lon = e.get("lon") or (e.get("center") or {}).get("lon")
        if t.get("name") and t.get("wikidata") and lat is not None:
            kind = t.get("historic") or t.get("tourism") or t.get("building") or t.get("amenity") or "?"
            out.append({"name": t["name"], "kind": kind, "q": t["wikidata"].split(";")[0],
                        "lat": round(lat, 5), "lon": round(lon, 5)})
    return out


def wikipedia_counts(qids):
    """Wikipedia-only sitelink counts, the same measure for every candidate."""
    counts = {}
    qids = [q for q in dict.fromkeys(qids) if re.fullmatch(r"Q\d+", q)]
    for i in range(0, len(qids), 80):
        values = " ".join("wd:" + q for q in qids[i:i + 80])
        q = f"""
        SELECT ?item (COUNT(DISTINCT ?sl) AS ?wikis) WHERE {{
          VALUES ?item {{ {values} }}
          OPTIONAL {{ ?sl schema:about ?item ; schema:isPartOf/wikibase:wikiGroup "wikipedia" }}
        }} GROUP BY ?item"""
        for b in sparql(q):
            counts[b["item"]["value"].rsplit("/", 1)[-1]] = int(b["wikis"]["value"])
    return counts


def norm(s):
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower())


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    city = sys.argv[1]
    top = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    wd = wikidata_items(city)
    osm = osm_items(city)
    counts = wikipedia_counts([i["q"] for i in wd + osm])

    merged = {}
    for item in wd + osm:                   # Wikidata first: its labels and classes win ties
        item["wikis"] = counts.get(item["q"], 0)
        key = item["q"] or norm(item["name"])
        merged.setdefault(key, item)

    ranked = sorted((m for m in merged.values()
                     if not any(x in (m["kind"] + " " + m["name"]).lower() for x in EXCLUDE)),
                    key=lambda m: (-m["wikis"], m["name"]))[:top]
    json.dump(ranked, sys.stdout, ensure_ascii=False, indent=1)
    print(f"\nwikidata {len(wd)} + osm {len(osm)} -> {len(merged)} candidates -> top {len(ranked)}",
          file=sys.stderr)


if __name__ == "__main__":
    main()
