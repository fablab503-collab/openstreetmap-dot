#!/usr/bin/env python3
"""Country outlines for the 195 capitals, as GeoJSON, from Natural Earth (public domain).

The vector tiles carry no country polygons - only boundary LINES, and those only
name the countries either side (`adm0_l`/`adm0_r`) from zoom 5 up. Below z5 there is
nothing to filter on, so a border cannot be lit at the zoom where you look at a whole
country. Natural Earth's 1:50m admin-0 set fixes both: it is a polygon per country
and it is the same at every zoom.

  * 1:110m is half the size but drops 29 of the 195 - every small island state,
    Singapore, Malta, Monaco, Vatican City. 1:50m has all 195.
  * Match on ISO_A2_EH, not ISO_A2: the plain field is "-99" for France, Norway and
    a few others. Fall back to ISO_A2 then WB_A2.
  * The raw set is 2.9 MB. Every ring is simplified (Ramer-Douglas-Peucker, 0.02
    degrees) and rounded to 2 decimals (~1.1 km), which is under a pixel at zoom 7 -
    the furthest in this layer is drawn before the tiles' own border takes over.
    Rings that survive with fewer than 4 points keep their original shape, so a
    country made of specks (Tuvalu, Maldives) does not lose them.

Usage:
    python3 build_countries.py ../../../data/world-capitals.geojson > countries.geojson
"""
import json
import math
import subprocess
import sys

SRC = ("https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/"
       "geojson/ne_50m_admin_0_countries.geojson")
ROUND = 2
TOL = 0.02          # degrees, Ramer-Douglas-Peucker


def code(props):
    for key in ("ISO_A2_EH", "ISO_A2", "WB_A2"):
        v = (props.get(key) or "").strip()
        if v and v not in ("-99", "99"):
            return v
    return ""


def rdp(points, tol):
    """Ramer-Douglas-Peucker, iterative so a 10,000-point coastline cannot blow
    the recursion limit."""
    if len(points) < 3:
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
    return [p for p, k in zip(points, keep) if k]


def ring(points):
    """Simplify one ring, round it, and drop points that land on the one before."""
    small = rdp([tuple(p[:2]) for p in points], TOL)
    if len(small) < 4:
        small = [tuple(p[:2]) for p in points]         # a speck stays a speck
    out = []
    for x, y in small:
        p = [round(x, ROUND), round(y, ROUND)]
        if not out or p != out[-1]:
            out.append(p)
    if len(out) < 4:
        out = [[round(x, ROUND), round(y, ROUND)] for x, y in small]
    if out[0] != out[-1]:
        out.append(out[0])
    return out


def thin(coords, depth=0):
    """Walk down to the rings (depth 2 for Polygon, 3 for MultiPolygon)."""
    if coords and isinstance(coords[0], (list, tuple)) and coords[0] \
       and isinstance(coords[0][0], (int, float)):
        return ring(coords)
    return [thin(c, depth + 1) for c in coords]


def main():
    wanted = None
    if len(sys.argv) > 1:
        caps = json.load(open(sys.argv[1], encoding="utf-8"))["features"]
        wanted = {f["properties"]["cc"] for f in caps if f["properties"].get("cc")}

    # curl, not urllib: the sandbox proxy truncates large responses to python.
    raw = subprocess.run(["curl", "-sSL", SRC], capture_output=True, check=True).stdout
    src = json.loads(raw)

    features, seen = [], set()
    for f in src["features"]:
        cc = code(f["properties"])
        if not cc or (wanted and cc not in wanted) or cc in seen:
            continue
        seen.add(cc)
        features.append({"type": "Feature",
                         "geometry": {"type": f["geometry"]["type"],
                                      "coordinates": thin(f["geometry"]["coordinates"])},
                         "properties": {"cc": cc}})

    json.dump({"type": "FeatureCollection", "features": features},
              sys.stdout, ensure_ascii=False)
    missing = sorted(wanted - seen) if wanted else []
    print(f"{len(src['features'])} source features -> {len(features)} countries; "
          f"missing: {missing}", file=sys.stderr)


if __name__ == "__main__":
    main()
