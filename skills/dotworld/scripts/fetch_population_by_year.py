#!/usr/bin/env python3
"""Population by country by year, 1960 to 2050, from World Bank Open Data (CC BY 4.0).

This is what lets the map travel in time: every city is scaled by its own country's
trajectory rather than by a single world figure, because the trajectories are not
alike - Japan in 2050 is smaller than Japan today while Nigeria is three times
bigger, and a world-average scale would hide exactly the thing worth seeing.

  * Estimates come from the default source (1960 to the present) and projections
    from source 40, "Population estimates and projections" (to 2050). The file
    records where the estimates stop, so the app can say "estimate" or "projection"
    rather than implying the same confidence for both.
  * One request per year, not per country: 91 requests instead of 200-odd, each
    returning every country at once.
  * Values are stored in thousands. A person is not the unit anybody reads at this
    scale, and it takes a third off the file.
  * Aggregates (the World Bank's "ARB", "EUU", income groups) are dropped except
    WLD, which the live counter uses.

Usage:
    python3 fetch_population_by_year.py > population-by-year.json
"""
import json
import subprocess
import sys
import time

FIRST, LAST = 1960, 2050
EST_LAST = 2025          # after this the numbers are projections


def fetch(year, source=None):
    url = ("https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL"
           f"?format=json&per_page=400&date={year}")
    if source:
        url += f"&source={source}"
    for attempt in range(3):
        out = subprocess.run(["curl", "-sS", url], capture_output=True, text=True).stdout
        try:
            j = json.loads(out)
            return j[1] or []
        except Exception:
            time.sleep(2 * (attempt + 1))
    print(f"  {year}: gave up", file=sys.stderr)
    return []


def main():
    series, years = {}, list(range(FIRST, LAST + 1))
    for y in years:
        rows = fetch(y) if y <= EST_LAST else fetch(y, source=40)
        got = 0
        for r in rows:
            cc = (r.get("country") or {}).get("id", "")
            # The world's own row is id "1W", not "WLD" - that is the alpha-3 code,
            # and looking for it in the wrong field silently drops the one series the
            # live counter needs. Store it under WLD, which is what the app asks for.
            if r.get("countryiso3code") == "WLD":
                cc = "WLD"
            # Otherwise ISO 3166-1 alpha-2 only; the World Bank's aggregates use
            # digits or invented pairs like ZH, and none are places on this map.
            elif not (len(cc) == 2 and cc.isalpha() and cc.isupper()):
                continue
            if r.get("value") is None:
                continue
            series.setdefault(cc, {})[y] = round(r["value"] / 1000)
            got += 1
        print(f"  {y}: {got}", file=sys.stderr)
        time.sleep(0.2)

    out = {"from": FIRST, "to": LAST, "estimatesTo": EST_LAST, "unit": "thousands",
           "cc": {cc: [vals.get(y, 0) for y in years] for cc, vals in sorted(series.items())}}
    json.dump(out, sys.stdout, separators=(",", ":"))
    wld = out["cc"].get("WLD", [])
    print(f"\n{len(out['cc'])} countries x {len(years)} years; "
          f"world {wld[0]/1e6:.2f} B in {FIRST} -> {wld[-1]/1e6:.2f} B in {LAST}",
          file=sys.stderr)


if __name__ == "__main__":
    main()
