#!/usr/bin/env python3
"""Every city in the world with its population, as GeoJSON, from GeoNames (CC BY 4.0).

The France layer came from Wikidata, one query per country's worth of communes. That
does not scale to the planet: the same query worldwide times out, and Wikidata's
population statements are uneven between countries - some cities carry a census
figure, some an estimate, some nothing at all.

GeoNames publishes one file instead: `cities15000.txt`, every settlement over 15,000
people, with coordinates, country and population, maintained as one dataset. 34,136
cities, tab separated, no API key, CC BY 4.0 - so the credit has to stay visible.

  * Download with curl, not urllib: the sandbox proxy truncates large responses.
  * Keep the UTF-8 name (column 1), not the ASCII one (column 2), so Zürich and
    São Paulo read properly.
  * Coordinates to 3 decimals (about 110 m). A city is a dot here; 110 m is far
    under one dot of the lattice at the zoom this layer is drawn.
  * Sorted by population ascending, so the biggest cities are last in the file and
    therefore drawn on top of the small ones.
  * Written as `[lon, lat, pop]` triples, not GeoJSON. The layer draws circles and
    never reads a name, and GeoJSON's per-feature scaffolding costs more than the
    data: 5.1 MB against 762 KB for the same 34,091 cities (303 KB gzipped). The app
    builds the GeoJSON from this in a single pass at load.

Usage:
    python3 fetch_world_population.py [min-population] > world-population.json
"""
import json
import os
import subprocess
import sys
import tempfile
import zipfile

SRC = "https://download.geonames.org/export/dump/cities15000.zip"


def main():
    floor = int(sys.argv[1]) if len(sys.argv) > 1 else 15000
    with tempfile.TemporaryDirectory() as tmp:
        zp = os.path.join(tmp, "cities.zip")
        subprocess.run(["curl", "-sSL", "-o", zp, SRC], check=True)
        rows = zipfile.ZipFile(zp).read("cities15000.txt").decode("utf-8").splitlines()

    cities = []
    for r in rows:
        f = r.split("\t")
        try:
            pop = int(f[14] or 0)
            lat, lon = float(f[4]), float(f[5])
        except (ValueError, IndexError):
            continue
        if pop < floor:
            continue
        cities.append((pop, f[1], f[8], round(lon, 3), round(lat, 3)))

    cities.sort()                      # ascending: the biggest are drawn last, on top
    json.dump({"floor": floor, "count": len(cities),
               "cities": [[lon, lat, pop] for pop, name, cc, lon, lat in cities]},
              sys.stdout, separators=(",", ":"))

    # Names go in their own file, in the same order, joined by index. The map never
    # needs them to draw - only to answer a click - so they are fetched then and not
    # before, and they cost nothing to the visit that never clicks.
    if len(sys.argv) > 2:
        with open(sys.argv[2], "w", encoding="utf-8") as fh:
            json.dump({"count": len(cities),
                       "names": [name for _, name, _, _, _ in cities],
                       "cc": [cc for _, _, cc, _, _ in cities]},
                      fh, ensure_ascii=False, separators=(",", ":"))
        print(f"names written to {sys.argv[2]}", file=sys.stderr)
    print(f"{len(rows)} rows -> {len(cities)} cities at {floor}+; "
          f"largest {cities[-1][1]} {cities[-1][0]:,}", file=sys.stderr)


if __name__ == "__main__":
    main()
