#!/usr/bin/env python3
"""Build data/solar-system.json: the numbers DotWorld needs to draw the solar system.

Two sources, both quoted rather than remembered:

  1. NASA NSSDC Planetary Fact Sheet (public domain) - mass, diameter, surface
     gravity, rotation period, distance from the Sun, perihelion and aphelion,
     orbital period and speed, inclination, eccentricity, obliquity, moons, rings.
     https://nssdc.gsfc.nasa.gov/planetary/factsheet/

  2. English Wikipedia infoboxes (CC BY-SA 4.0) - the three angles the fact sheet
     does not carry, all at epoch J2000: mean anomaly, argument of perihelion and
     longitude of the ascending node. Without them a planet has the right orbit
     and the wrong place on it.

Writing the angles down from memory is how the events file ended up with a person
and a time zone in its class list. Everything here is fetched.

Run:  python3 fetch_solar_system.py          (writes ../../../data/solar-system.json)
"""
import json
import os
import re
import subprocess
import sys
import urllib.parse

FACTSHEET = 'https://nssdc.gsfc.nasa.gov/planetary/factsheet/'
WIKI = 'https://en.wikipedia.org/w/api.php'
UA = {'User-Agent': 'DotWorld/0.5 (https://github.com/fablab503-collab/openstreetmap-dot)'}

# The fact sheet's column order. Pluto is on the sheet and is a dwarf planet, not a
# planet - it is carried with that label rather than dropped, because "and Pluto?" is
# the first thing anyone asks.
COLUMNS = ['mercury', 'venus', 'earth', 'moon', 'mars', 'jupiter', 'saturn',
           'uranus', 'neptune', 'pluto']

# The fact-sheet row label -> the key it becomes. Only the rows the map uses.
ROWS = {
    'Mass (1024kg)':                'mass_1e24kg',
    'Diameter (km)':                'diameter_km',
    'Gravity (m/s2)':               'surface_gravity',
    'Rotation Period (hours)':      'rotation_h',
    'Length of Day (hours)':        'day_h',
    'Distance from Sun (106 km)':   'a_1e6km',
    'Perihelion (106 km)':          'perihelion_1e6km',
    'Aphelion (106 km)':            'aphelion_1e6km',
    'Orbital Period (days)':        'period_d',
    'Orbital Velocity (km/s)':      'speed_kms',
    'Orbital Inclination (degrees)': 'inclination',
    'Orbital Eccentricity':         'eccentricity',
    'Obliquity to Orbit (degrees)': 'obliquity',
    'Mean Temperature (C)':         'temp_c',
    'Number of Moons':              'moons',
    'Ring System?':                 'rings',
}

WIKI_TITLES = {
    'mercury': 'Mercury (planet)', 'venus': 'Venus', 'earth': 'Earth',
    'mars': 'Mars', 'jupiter': 'Jupiter', 'saturn': 'Saturn',
    'uranus': 'Uranus', 'neptune': 'Neptune', 'pluto': 'Pluto', 'moon': 'Moon',
}

# Colour per body: a CSS named colour, the same rule the rest of the map follows, so
# every colour on screen has a name you can look up. Picked to sit near the body's
# real appearance while staying apart from the population ramp, which is warm.
COLOURS = {
    'sun':     ('gold',            '#ffd700'),
    'mercury': ('darkgray',        '#a9a9a9'),
    'venus':   ('palegoldenrod',   '#eee8aa'),
    'earth':   ('mediumturquoise', '#48d1cc'),
    'moon':    ('gainsboro',       '#dcdcdc'),
    'mars':    ('indianred',       '#cd5c5c'),
    'jupiter': ('peru',            '#cd853f'),
    'saturn':  ('burlywood',       '#deb887'),
    'uranus':  ('powderblue',      '#b0e0e6'),
    'neptune': ('royalblue',       '#4169e1'),
    'pluto':   ('rosybrown',       '#bc8f8f'),
}


def get(url):
    """curl, not urllib: Python's TLS fails through this machine's proxy, curl does not."""
    out = subprocess.run(['curl', '-sS', '--max-time', '60', '-A', UA['User-Agent'], url],
                         capture_output=True, text=True)
    if out.returncode != 0 or not out.stdout:
        sys.exit('fetch failed: ' + url + ' ' + out.stderr.strip())
    return out.stdout


def number(s):
    """'12,104' -> 12104.0 ; '-5832.5' -> -5832.5 ; 'Unknown*' -> None."""
    s = s.replace(',', '').replace('*', '').strip()
    m = re.match(r'^-?\d+(\.\d+)?([eE]-?\d+)?$', s)
    return float(s) if m else None


def fact_sheet():
    """Read the table row by row: label cell, then one cell per body.

    Tags cannot simply become newlines here - the row labels carry <sub> and <sup>,
    so "Mass (10^24 kg)" would arrive as four separate lines. Rows and cells are
    marked first, then the rest of the tags are removed, not replaced.
    """
    # The source puts every cell on its own source line, so its newlines have to go
    # before rows and cells can be marked with newlines and tabs of our own.
    html = get(FACTSHEET).replace('\n', ' ')
    html = re.sub(r'</tr\s*>', '\n', html, flags=re.I)
    html = re.sub(r'</t[dh]\s*>', '\t', html, flags=re.I)
    html = re.sub(r'<[^>]*>', '', html).replace('&nbsp;', ' ')
    out = {k: {} for k in COLUMNS}
    seen = 0
    for line in html.split('\n'):
        cells = [c.strip() for c in line.split('\t')]
        if not cells:
            continue
        key = ROWS.get(re.sub(r'\s+', ' ', cells[0]).strip())
        if not key:
            continue
        values = [c for c in cells[1:] if c][:len(COLUMNS)]
        if len(values) < len(COLUMNS):
            print('  short row:', cells[0], len(values), file=sys.stderr)
            continue
        seen += 1
        for body, raw in zip(COLUMNS, values):
            n = number(raw)
            out[body][key] = raw if n is None else n
    print('  rows read:', seen, 'of', len(ROWS))
    return out


def wiki_angles(title):
    """Mean anomaly, argument of perihelion and ascending node at J2000."""
    url = WIKI + '?' + urllib.parse.urlencode({
        'action': 'query', 'prop': 'revisions', 'rvprop': 'content',
        'rvslots': 'main', 'format': 'json', 'titles': title})
    page = list(json.loads(get(url))['query']['pages'].values())[0]
    text = page['revisions'][0]['slots']['main']['*']
    got = {}
    for field, key in (('mean_anomaly', 'M0'), ('arg_peri', 'peri'), ('asc_node', 'node')):
        m = re.search(r'\|\s*' + field + r'\s*=\s*([^\n]{0,160})', text)
        if not m:
            got[key] = None
            continue
        # Values arrive in several shapes: "174.796°", "{{val|358.617|u=°}}",
        # "{{val|-11.26064|u=°}} - J2000 ecliptic<ref .../>". Take the line, drop
        # the references, and read the first number - which is the value in every
        # one of those shapes. A value that is prose rather than a number (the
        # Moon's node, which regresses) has no number before the first letter and
        # is left as None on purpose.
        raw = m.group(1).replace('−', '-')
        raw = re.sub(r'<ref[^>]*>.*?</ref>|<ref[^>]*/>', '', raw)
        raw = raw.replace('{{val|', '').replace('{{', '').replace('}}', '')
        if re.match(r'\s*(longitem|Regress|Progress)', raw, re.I):
            got[key] = None
            continue
        n = re.search(r'-?\d+(\.\d+)?', raw)
        got[key] = float(n.group(0)) if n else None
    return got


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.normpath(os.path.join(here, '..', '..', '..', 'data', 'solar-system.json'))

    print('NASA planetary fact sheet…')
    facts = fact_sheet()
    missing = [b for b in COLUMNS if 'diameter_km' not in facts[b]]
    if missing:
        sys.exit('fact sheet parsed short for: ' + ', '.join(missing))

    bodies = {}
    for body in COLUMNS:
        print('  Wikipedia:', WIKI_TITLES[body])
        f = dict(facts[body])
        f.update(wiki_angles(WIKI_TITLES[body]))
        name, hexv = COLOURS[body]
        f['colour'] = name
        f['hex'] = hexv
        f['kind'] = ('moon' if body == 'moon'
                     else 'dwarf' if body == 'pluto' else 'planet')
        f['parent'] = 'earth' if body == 'moon' else 'sun'
        bodies[body] = f

    # The Sun is not on the planetary fact sheet; these are its own NSSDC sheet's
    # figures (https://nssdc.gsfc.nasa.gov/planetary/factsheet/sunfact.html).
    bodies['sun'] = {
        'mass_1e24kg': 1988500.0, 'diameter_km': 1392700.0, 'surface_gravity': 274.0,
        'rotation_h': 609.12, 'kind': 'star', 'parent': None,
        'colour': COLOURS['sun'][0], 'hex': COLOURS['sun'][1],
        'temp_c': 5504.0, 'moons': 0, 'rings': 'No',
    }

    # The Moon's infobox carries no fixed angles, and honestly so: its node regresses
    # once in 18.61 years and its perigee runs round in 8.85, so there is nothing to
    # put there. What does pin the Moon down for a picture is its phase, and English
    # Wikipedia's "Lunar phase" gives a cited way to get it: count the days since a
    # known new moon - it names 11 August 1999 - modulo the mean synodic month of
    # 29.53059 days (Seidelmann 1992, Explanatory Supplement, p. 577). That places the
    # Moon along the Sun-Earth line, which is exactly what anyone looking at the
    # picture is checking. The anchor is a date without a time, so the phase can be
    # out by up to half a day, about 6 degrees.
    bodies['moon']['synodic_d'] = 29.53059
    bodies['moon']['new_moon_epoch'] = '1999-08-11T00:00:00Z'
    bodies['moon']['distance_km'] = 384400.0

    doc = {
        'epoch': 'J2000',
        'sources': {
            'facts': 'NASA NSSDC Planetary Fact Sheet, public domain — ' + FACTSHEET,
            'angles': 'English Wikipedia infoboxes, CC BY-SA 4.0 — mean anomaly, '
                      'argument of perihelion and longitude of the ascending node at J2000',
            'moon': 'English Wikipedia, "Lunar phase", CC BY-SA 4.0 — days since the '
                    'new moon of 11 August 1999, modulo a mean synodic month of '
                    '29.53059 days (Seidelmann 1992, p. 577)',
        },
        'note': 'Two-body Keplerian elements. Good to a fraction of a degree from '
                '1800 to 2050 and drifting outside that; the map says so when the '
                'year bar is outside it. No perturbations, so the Moon is the '
                'roughest of them.',
        'bodies': bodies,
    }
    with open(out_path, 'w') as fh:
        json.dump(doc, fh, separators=(',', ':'), sort_keys=True)
    print('wrote', out_path, os.path.getsize(out_path), 'bytes,', len(bodies), 'bodies')


if __name__ == '__main__':
    main()
