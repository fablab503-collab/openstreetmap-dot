#!/usr/bin/env python3
"""The 195 national capitals with population, as GeoJSON, from Wikidata (CC0).

195 = the 193 UN member states + the two observer states, Vatican City (Q237) and
Palestine (Q219060).

Two traps in "member of United Nations" (P463 = Q1065):

  * A truthy `wdt:P463` also matches HISTORICAL memberships. It lets in Taiwan,
    whose UN seat passed to the People's Republic of China in 1971. An earlier
    version of this list shipped Taiwan and left out Vatican City — and still
    happened to total 195, so the count alone did not reveal it. Require a
    membership statement with no end date (`pq:P582`).
  * No end date alone is not enough: about ten predecessor entities (Kingdom of
    Laos, Third Hellenic Republic, …) carry open-ended membership statements. Also
    require a current sovereign state that has not been dissolved.

Seven states list several distinct seats (Bolivia, Eswatini, Pakistan, Palestine,
South Africa, Sri Lanka, Yemen). Jordan and Syria return the same capital twice as
separate items; that is not a second seat. The most populous seat is kept — a rule,
not a fact — and `seats` records how many distinct seats there were.

Usage:
    python3 fetch_capitals.py > world-capitals.geojson
"""
import http.client
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import defaultdict

UA = "DotWorld-data/1.0 (https://github.com/fablab503-collab/openstreetmap-dot)"

QUERY = """
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
"""


def sparql(query, attempts=4):
    """Run a SPARQL query, retrying: large responses sometimes arrive truncated
    (http.client.IncompleteRead) or time out, especially through a proxy."""
    url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"query": query})
    req = urllib.request.Request(url, headers={
        "Accept": "application/sparql-results+json", "User-Agent": UA})
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(req, timeout=170) as resp:
                return json.load(resp)["results"]["bindings"]
        except (http.client.HTTPException, OSError, ValueError) as exc:
            if attempt == attempts:
                raise
            print(f"attempt {attempt} failed ({exc.__class__.__name__}), retrying",
                  file=sys.stderr)
            time.sleep(3 * attempt)


def main():
    rows = sparql(QUERY)
    by_country = defaultdict(list)
    for r in rows:
        m = re.match(r"Point\(([-\d.]+) ([-\d.]+)\)", r["coord"]["value"])
        if not m:
            continue
        by_country[r["countryLabel"]["value"]].append({
            "cap": r["capLabel"]["value"],
            "lon": round(float(m.group(1)), 4),
            "lat": round(float(m.group(2)), 4),
            "pop": int(float(r["pop"]["value"])) if "pop" in r else 0,
        })

    features, multi = [], []
    for country, caps in sorted(by_country.items()):
        seats = len({c["cap"] for c in caps})      # Jordan and Syria repeat one capital
        if seats > 1:
            multi.append(country)
        best = max(caps, key=lambda c: c["pop"])
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [best["lon"], best["lat"]]},
            "properties": {"name": best["cap"], "country": country,
                           "pop": best["pop"], "seats": seats},
        })

    json.dump({"type": "FeatureCollection", "features": features},
              sys.stdout, ensure_ascii=False)
    missing = [f["properties"]["name"] for f in features if not f["properties"]["pop"]]
    print(f"{len(rows)} rows -> {len(features)} capitals; several seats ({len(multi)}): "
          f"{multi}; no population: {missing}", file=sys.stderr)
    if len(features) != 195:
        print(f"WARNING: expected 195 capitals, got {len(features)} — "
              "re-check the membership filter", file=sys.stderr)


if __name__ == "__main__":
    main()
