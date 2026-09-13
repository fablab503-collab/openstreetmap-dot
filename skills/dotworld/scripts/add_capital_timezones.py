#!/usr/bin/env python3
"""Add each capital's IANA time zone to world-capitals.geojson, from GeoNames (CC BY 4.0).

A clock needs a zone, and a zone cannot be guessed from longitude: China runs one
zone across sixty degrees, India is half an hour off the hour, Spain keeps Berlin's
time. Nor is it worth shipping the tz boundary polygons - they are tens of megabytes
for 195 points.

GeoNames' `cities15000.txt` already carries the IANA zone for every city, and every
capital either is one of those cities or sits beside one. So: nearest city **in the
same country**, which is what stops Vienna borrowing Bratislava's zone 55 km away or
a capital near a border taking its neighbour's. Where a country has no city in the
file at all (Vatican City, Ngerulmud), fall back to the nearest city anywhere - the
Vatican is inside Rome, and Palau's zone is Palau's whichever town you land on.

Writes the file back with a `tz` on every capital. DST is not baked in: the browser
applies it from the zone name, which is the whole reason for storing a name rather
than an offset.

Usage:
    python3 add_capital_timezones.py ../../../data/world-capitals.geojson
"""
import json
import math
import os
import subprocess
import sys
import tempfile
import zipfile

SRC = "https://download.geonames.org/export/dump/cities15000.zip"


def metres(lon1, lat1, lon2, lat2):
    x = (lon2 - lon1) * math.cos(math.radians((lat1 + lat2) / 2))
    return math.hypot(x, lat2 - lat1) * 111_320


def main():
    path = sys.argv[1]
    with tempfile.TemporaryDirectory() as tmp:
        zp = os.path.join(tmp, "cities.zip")
        subprocess.run(["curl", "-sSL", "-o", zp, SRC], check=True)
        rows = zipfile.ZipFile(zp).read("cities15000.txt").decode("utf-8").splitlines()

    cities = []
    for r in rows:
        f = r.split("\t")
        try:
            cities.append((float(f[5]), float(f[4]), f[8], f[17], f[1]))   # lon lat cc tz name
        except (ValueError, IndexError):
            continue

    doc = json.load(open(path, encoding="utf-8"))
    far, borrowed = [], []
    for feat in doc["features"]:
        lon, lat = feat["geometry"]["coordinates"]
        cc = feat["properties"].get("cc", "")
        same = [c for c in cities if c[2] == cc]
        pool = same or cities
        best = min(pool, key=lambda c: metres(lon, lat, c[0], c[1]))
        d = metres(lon, lat, best[0], best[1])
        feat["properties"]["tz"] = best[3]
        if not same:
            borrowed.append((feat["properties"]["name"], best[4], best[3]))
        if d > 120_000:
            far.append((feat["properties"]["name"], best[4], round(d / 1000)))

    json.dump(doc, open(path, "w", encoding="utf-8"), ensure_ascii=False)
    zones = {f["properties"]["tz"] for f in doc["features"]}
    print(f"{len(doc['features'])} capitals, {len(zones)} distinct zones", file=sys.stderr)
    print(f"no city in their own country ({len(borrowed)}): {borrowed}", file=sys.stderr)
    print(f"nearest city over 120 km away ({len(far)}): {far}", file=sys.stderr)


if __name__ == "__main__":
    main()
