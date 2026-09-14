#!/usr/bin/env python3
"""The events of every year, 1500 to today, from Wikidata (CC0).

"Important" is the same proxy this project uses everywhere else: how many Wikipedia
editions and sister projects carry an article about the thing. The ranking is the
work of Wikipedia's editors, not mine.

What the shape of the query has to avoid:

  * `wdt:P31/wdt:P279*` from "occurrence" is the textbook filter and it times out at
    60 s on a single decade. A flat `VALUES` list of classes answers in ten.
  * The class list is derived, not remembered: ask Wikidata what it calls Apollo 11,
    the Cuban Missile Crisis, the COVID-19 pandemic and the September 11 attacks, and
    use the classes that come back - `human spaceflight`, `conflict`, `political
    crisis`, `pandemic`, `terrorist attack`. Guessing the QIDs by hand gave a list
    that quietly returned a person and a time zone.
  * Dates hide in three properties: `P585` (point in time) for things that happened
    on a day, `P580` (start time) for things that began, and `P619` (time of
    spacecraft launch). Apollo 11 carries neither of the first two - a date query
    without P619 returns a 1969 with no Moon landing in it, and nothing complains.
  * Every year has an article about itself - the item labelled "1969" has more
    sitelinks than anything that happened in 1969 - so drop labels that are only
    digits.
  * One query per decade, not per year: 53 requests instead of 526.

Coverage is honest but partial: an event Wikidata has not typed as an event will not
appear however famous it is. The file says how many it found.

Usage:
    python3 fetch_events.py [first-year] [last-year] > events.json
"""
import json
import re
import subprocess
import sys
import time
import urllib.parse

# war, battle, treaty, election, disaster, natural disaster, earthquake, flood,
# revolution, coup, conflict, political crisis, historical event, occurrence, event,
# human spaceflight, space mission, pandemic, disease outbreak, terrorist attack,
# suicide attack, massacre, genocide, festival, summit, recurring sporting event
CLASSES = ("wd:Q198 wd:Q178561 wd:Q131569 wd:Q40231 wd:Q3839081 wd:Q8065 wd:Q7944 "
           "wd:Q8068 wd:Q10931 wd:Q45382 wd:Q180684 wd:Q3002772 wd:Q13418847 "
           "wd:Q1190554 wd:Q1656682 wd:Q752783 wd:Q2133344 wd:Q12184 wd:Q3241045 "
           "wd:Q2223653 wd:Q217327 wd:Q750215 wd:Q41397 wd:Q132241 wd:Q625298 "
           "wd:Q18608583 wd:Q7283 wd:Q37501 wd:Q2334719 wd:Q124757")

QUERY = """
SELECT ?item ?itemLabel ?date ?links WHERE {
  { ?item wdt:P585 ?date } UNION { ?item wdt:P580 ?date }
  UNION { ?item wdt:P619 ?date }
  FILTER(YEAR(?date) >= %d && YEAR(?date) <= %d)
  ?item wikibase:sitelinks ?links . FILTER(?links >= %d)
  ?item wdt:P31 ?cls . VALUES ?cls { %s }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
}
ORDER BY DESC(?links) LIMIT 400
"""


def ask(first, last, floor, attempts=3):
    q = QUERY % (first, last, floor, CLASSES)
    url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"query": q})
    for attempt in range(attempts):
        out = subprocess.run(
            ["curl", "-sS", "--max-time", "240",
             "-H", "Accept: application/sparql-results+json",
             "-H", "User-Agent: DotWorld-data/1.0 (github.com/fablab503-collab/openstreetmap-dot)",
             url], capture_output=True, text=True).stdout
        try:
            return json.loads(out)["results"]["bindings"]
        except Exception:
            time.sleep(5 * (attempt + 1))
    print(f"  {first}-{last}: gave up", file=sys.stderr)
    return []


def main():
    first = int(sys.argv[1]) if len(sys.argv) > 1 else 1500
    last = int(sys.argv[2]) if len(sys.argv) > 2 else time.gmtime().tm_year
    years = {}
    for start in range(first, last + 1, 10):
        end = min(start + 9, last)
        # older centuries have far less written about them; drop the bar for them
        floor = 12 if start < 1800 else (20 if start < 1900 else 30)
        best = {}
        for r in ask(start, end, floor):
            label = r["itemLabel"]["value"]
            if re.fullmatch(r"[\d\s]{1,6}(s| BC)?", label) or re.fullmatch(r"Q\d+", label):
                continue
            key = label.lower()
            links = int(r["links"]["value"])
            date = r["date"]["value"][:10]
            if key not in best or links > best[key][1]:
                best[key] = (label, links, date, r["item"]["value"].rsplit("/", 1)[-1])
        for label, links, date, qid in best.values():
            years.setdefault(date[:4], []).append([date, label, links, qid])
        print(f"  {start}-{end}: {len(best)}", file=sys.stderr)
        time.sleep(1)

    out = {}
    for y, rows in years.items():
        rows.sort(key=lambda r: -r[2])
        out[y] = [{"d": r[0], "t": r[1], "n": r[2], "q": r[3]} for r in rows[:4]]
    json.dump({"from": first, "to": last, "years": out}, sys.stdout, ensure_ascii=False,
              separators=(",", ":"))
    print(f"\n{sum(len(v) for v in out.values())} events across {len(out)} years",
          file=sys.stderr)


if __name__ == "__main__":
    main()
