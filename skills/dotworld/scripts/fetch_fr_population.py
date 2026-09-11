#!/usr/bin/env python3
"""French communes above a population threshold, as GeoJSON, from Wikidata (CC0).

Paris is unioned in explicitly. Its "commune of France" (Q484170) statement is not
truthy — since 2019 it is a territorial collectivity with special status
(Q22923920) — so a plain `wdt:P31 wd:Q484170` query silently drops the largest city
in the country.

The query asks for CSV, not JSON. The JSON result is ~300 KB and was cut off at
exactly 262,144 bytes on every attempt through a proxy — a hard cap that retries
cannot get past — while the CSV is a fraction of the size.

Usage:
    python3 fetch_fr_population.py [min_population] > fr-population.geojson

Default threshold 15000. Keeps metropolitan France only. Summary on stderr.
"""
import csv
import http.client
import io
import json
import re
import sys
import time
import urllib.parse
import urllib.request

MIN_POP = int(sys.argv[1]) if len(sys.argv) > 1 else 15000
UA = "DotWorld-data/1.0 (https://github.com/fablab503-collab/openstreetmap-dot)"

QUERY = """
SELECT ?itemLabel ?coord (MAX(?p) AS ?pop) WHERE {
  { ?item wdt:P31 wd:Q484170 } UNION { VALUES ?item { wd:Q90 } }
  ?item wdt:P1082 ?p ; wdt:P625 ?coord .
  FILTER(?p > %d)
  SERVICE wikibase:label { bd:serviceParam wikibase:language "fr,en" }
}
GROUP BY ?itemLabel ?coord
ORDER BY DESC(?pop)
""" % MIN_POP


def sparql_csv(query, attempts=4):
    """Run a SPARQL query and return rows as dicts. Retries, because responses
    sometimes arrive truncated (http.client.IncompleteRead) or time out."""
    url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"query": query})
    req = urllib.request.Request(url, headers={"Accept": "text/csv", "User-Agent": UA})
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(req, timeout=170) as resp:
                text = resp.read().decode("utf-8")
            return list(csv.DictReader(io.StringIO(text)))
        except (http.client.HTTPException, OSError, ValueError) as exc:
            if attempt == attempts:
                raise
            print(f"attempt {attempt} failed ({exc.__class__.__name__}), retrying",
                  file=sys.stderr)
            time.sleep(3 * attempt)


def main():
    rows = sparql_csv(QUERY)
    features, seen = [], set()
    for r in rows:
        name = r["itemLabel"]
        # An unlabelled item comes back as its bare Q-id; skip it and duplicates.
        if name in seen or re.fullmatch(r"Q\d+", name):
            continue
        m = re.match(r"Point\(([-\d.]+) ([-\d.]+)\)", r["coord"])
        if not m:
            continue
        lon, lat = float(m.group(1)), float(m.group(2))
        if not (-5.5 < lon < 10 and 41 < lat < 51.5):      # metropolitan France
            continue
        seen.add(name)
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [round(lon, 4), round(lat, 4)]},
            "properties": {"name": name, "pop": int(float(r["pop"]))},
        })

    json.dump({"type": "FeatureCollection", "features": features},
              sys.stdout, ensure_ascii=False)
    pops = sorted(f["properties"]["pop"] for f in features)
    has_paris = any(f["properties"]["name"] == "Paris" for f in features)
    print(f"{len(rows)} rows -> {len(features)} communes, "
          f"{pops[0]:,}..{pops[-1]:,}, Paris included: {has_paris}", file=sys.stderr)


if __name__ == "__main__":
    main()
