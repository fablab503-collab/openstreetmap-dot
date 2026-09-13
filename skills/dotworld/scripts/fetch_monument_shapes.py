#!/usr/bin/env python3
"""The footprint of every capital monument, as GeoJSON, from OpenStreetMap (ODbL).

A dot at a monument's coordinate says "something is here". The building's own outline
says what it is: at street zoom the lattice fills the Colosseum's ellipse, the
Pentagon's pentagon, the Forbidden City's rectangles.

The vector tiles cannot do this. Their `building` layer carries render heights and
nothing else - no name, no wikidata tag - so there is no way to ask them for one
particular building. Overpass can.

  * Matched by position, not by id: `capital-monuments.geojson` stores coordinates,
    and every OSM way or relation with a `wikidata` tag within 150 m is a candidate.
    The nearest centroid inside 200 m wins, so two monuments on the same street do
    not swap outlines.
  * Batched: one query per 40 monuments, each an `around` clause. 491 monuments is
    13 queries rather than 491.
  * Relations are assembled by hand. `out geom` returns a multipolygon's outer ways
    as separate, unordered, sometimes reversed strips; they have to be joined
    end to end into rings or the biggest monuments (the Louvre, the Kremlin) come
    out as scribbles.
  * Coordinates rounded to 5 decimals (about 1 m) - far finer than a dot lattice can
    show, and it still halves the file.

Usage:
    python3 fetch_monument_shapes.py ../../../data/capital-monuments.geojson \
        > capital-monument-shapes.geojson
"""
import http.client
import json
import math
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

UA = "DotWorld-data/1.0 (https://github.com/fablab503-collab/openstreetmap-dot)"
OVERPASS = "https://overpass-api.de/api/interpreter"
BATCH = 40
AROUND_M = 150        # how far to look for a tagged outline
MAX_M = 200           # how far a match may be from the monument's own point
PAUSE = 3             # Overpass is free; do not hammer it


def overpass(query, attempts=4):
    data = urllib.parse.urlencode({"data": query}).encode()
    req = urllib.request.Request(OVERPASS, data=data, headers={"User-Agent": UA})
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                return json.load(resp)["elements"]
        except (http.client.HTTPException, OSError, ValueError) as exc:
            if attempt == attempts:
                raise
            print(f"  attempt {attempt} failed ({exc.__class__.__name__}), retrying",
                  file=sys.stderr)
            time.sleep(6 * attempt)


def rings_from_relation(el):
    """Join a relation's outer ways end to end. Overpass hands them back in any
    order and any direction, so a naive concatenation draws a scribble."""
    strips = [[(p["lon"], p["lat"]) for p in m.get("geometry") or []]
              for m in el.get("members", [])
              if m.get("type") == "way" and m.get("role") in ("outer", "")]
    strips = [s for s in strips if len(s) > 1]
    rings = []
    while strips:
        cur = strips.pop(0)
        changed = True
        while changed and cur[0] != cur[-1]:
            changed = False
            for i, s in enumerate(strips):
                if s[0] == cur[-1]:
                    cur += s[1:]; strips.pop(i); changed = True; break
                if s[-1] == cur[-1]:
                    cur += s[::-1][1:]; strips.pop(i); changed = True; break
                if s[-1] == cur[0]:
                    cur = s[:-1] + cur; strips.pop(i); changed = True; break
                if s[0] == cur[0]:
                    cur = s[::-1][:-1] + cur; strips.pop(i); changed = True; break
        if len(cur) >= 4:
            if cur[0] != cur[-1]:
                cur.append(cur[0])            # close what OSM left open
            rings.append(cur)
    return rings


def geometry_of(el):
    if el["type"] == "way":
        pts = [(p["lon"], p["lat"]) for p in el.get("geometry") or []]
        if len(pts) < 4:
            return None
        if pts[0] != pts[-1]:
            pts.append(pts[0])
        return {"type": "Polygon", "coordinates": [pts]}
    rings = rings_from_relation(el)
    if not rings:
        return None
    if len(rings) == 1:
        return {"type": "Polygon", "coordinates": [rings[0]]}
    return {"type": "MultiPolygon", "coordinates": [[r] for r in rings]}


def centroid(geom):
    pts = []
    if geom["type"] == "Polygon":
        pts = geom["coordinates"][0]
    else:
        for poly in geom["coordinates"]:
            pts += poly[0]
    return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))


def metres(lon1, lat1, lon2, lat2):
    x = (lon2 - lon1) * math.cos(math.radians((lat1 + lat2) / 2))
    return math.hypot(x, lat2 - lat1) * 111_320


def rdp(points, tol):
    """Ramer-Douglas-Peucker on a ring, iterative. Westminster Abbey comes back with
    547 points; at a 2 m tolerance it keeps its shape at a third of the size, and
    2 m is far under one dot of the lattice even at street zoom."""
    if len(points) < 5:
        return points
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        i, j = stack.pop()
        if j <= i + 1:
            continue
        ax, ay = points[i]
        bx, by = points[j]
        dx, dy = bx - ax, by - ay
        den = math.hypot(dx, dy)
        best, bi = -1.0, -1
        for k in range(i + 1, j):
            px, py = points[k]
            d = (abs(dx * (ay - py) - (ax - px) * dy) / den if den
                 else math.hypot(px - ax, py - ay))
            if d > best:
                best, bi = d, k
        if best > tol:
            keep[bi] = True
            stack.append((i, bi))
            stack.append((bi, j))
    out = [p for p, k in zip(points, keep) if k]
    return out if len(out) >= 4 else points


def simplify(geom, tol=0.00002):          # ~2 m
    def ring(r):
        out = rdp([tuple(p) for p in r], tol)
        if out[0] != out[-1]:
            out.append(out[0])
        return [list(p) for p in out]
    if geom["type"] == "Polygon":
        return {"type": "Polygon", "coordinates": [ring(r) for r in geom["coordinates"]]}
    return {"type": "MultiPolygon",
            "coordinates": [[ring(r) for r in poly] for poly in geom["coordinates"]]}


def round_geom(geom, nd=5):
    def r(c):
        if isinstance(c[0], (int, float)):
            return [round(c[0], nd), round(c[1], nd)]
        return [r(x) for x in c]
    return {"type": geom["type"], "coordinates": r(geom["coordinates"])}


def main():
    mons = json.load(open(sys.argv[1], encoding="utf-8"))["features"]
    out, hit = [], 0
    for start in range(0, len(mons), BATCH):
        chunk = mons[start:start + BATCH]
        clauses = "".join(
            f'way(around:{AROUND_M},{c["geometry"]["coordinates"][1]},'
            f'{c["geometry"]["coordinates"][0]})["wikidata"];'
            f'rel(around:{AROUND_M},{c["geometry"]["coordinates"][1]},'
            f'{c["geometry"]["coordinates"][0]})["wikidata"];'
            for c in chunk)
        try:
            els = overpass(f"[out:json][timeout:240];({clauses});out geom;")
        except Exception as exc:
            print(f"batch {start}-{start + len(chunk)}: FAILED {exc}", file=sys.stderr)
            continue

        cands = []
        for el in els:
            g = geometry_of(el)
            if g:
                cands.append((g, centroid(g), el.get("tags", {})))

        for c in chunk:
            lon, lat = c["geometry"]["coordinates"]
            best, bestd = None, MAX_M
            for g, (clon, clat), tags in cands:
                d = metres(lon, lat, clon, clat)
                if d < bestd:
                    best, bestd = (g, tags), d
            if not best:
                continue
            hit += 1
            props = dict(c["properties"])
            props["osm"] = best[1].get("wikidata", "")
            out.append({"type": "Feature",
                        "geometry": round_geom(simplify(best[0])),
                        "properties": props})
        print(f"{start + len(chunk):4}/{len(mons)} monuments, {hit} with an outline",
              file=sys.stderr)
        time.sleep(PAUSE)

    json.dump({"type": "FeatureCollection", "features": out},
              sys.stdout, ensure_ascii=False)
    print(f"\n{hit} outlines for {len(mons)} monuments "
          f"({hit * 100 // max(1, len(mons))}%)", file=sys.stderr)


if __name__ == "__main__":
    main()
