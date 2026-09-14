#!/usr/bin/env python3
"""Build data/planet-colours.json: what each body actually looks like.

Source: the Solar System Scope texture set, https://www.solarsystemscope.com/textures/,
distributed under Attribution 4.0 International (CC BY 4.0) - "You may use, adapt, and
share these textures for any purpose, even commercially." Their own maps are built from
NASA elevation and imagery. What ships here is a heavy downsample of them:

  earth_day    224 x 112, three bytes a pixel
  earth_night  288 x 144, ONE byte a pixel - the lights are warm white anyway, and one
               byte at twice the width beats three bytes at half of it
  every other  64 x 32, three bytes a pixel (the Sun 32 x 16)

Why a downsample rather than the image: a dot on screen is two pixels wide, and the map
is sampled per dot. 224 x 112 is more than the lattice can ever show, and the whole file
is about 220 KB instead of four megabytes.

**This script needs a browser to do the resizing.** There is no image library on the
machine it was written for (no PIL, no numpy, and `sips` cannot write files from inside
the sandbox), so the fetch is here and the resampling step is the snippet printed at the
end: serve the repo, open it, paste, save the result. It is written out in full so the
file can be rebuilt by anybody without guessing what was done.

Run:  python3 fetch_planet_colours.py          (downloads into ../../../.tex/)
"""
import os
import subprocess
import sys

BASE = 'https://www.solarsystemscope.com/textures/download/'
FILES = {
    'earth_day': '2k_earth_daymap.jpg', 'earth_night': '2k_earth_nightmap.jpg',
    'mercury': '2k_mercury.jpg', 'venus': '2k_venus_atmosphere.jpg',
    'mars': '2k_mars.jpg', 'jupiter': '2k_jupiter.jpg', 'saturn': '2k_saturn.jpg',
    'uranus': '2k_uranus.jpg', 'neptune': '2k_neptune.jpg', 'moon': '2k_moon.jpg',
    'sun': '2k_sun.jpg',
}
SIZES = {'earth_day': (224, 112), 'earth_night': (288, 144), 'sun': (32, 16)}

SNIPPET = '''
// Serve the repo (the .tex folder has to be reachable) and run this in the page,
// then save what it returns as data/planet-colours.json.
const jobs = %s;
const grab = async (file, w, h) => {
  const img = new Image(); img.src = '/.tex/' + file; await img.decode();
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  const x = c.getContext('2d');
  x.imageSmoothingEnabled = true; x.imageSmoothingQuality = 'high';
  x.drawImage(img, 0, 0, w, h);
  return x.getImageData(0, 0, w, h).data;
};
const maps = {};
for (const [key, file, w, h] of jobs) {
  const d = await grab(file, w, h);
  if (key === 'earth_night') {
    let bin = '', peak = 0;
    for (let i = 0; i < d.length; i += 4) {
      const v = Math.max(d[i], d[i+1], d[i+2]);
      if (v > peak) peak = v;
      bin += String.fromCharCode(v);
    }
    maps[key] = { w, h, lum: btoa(bin), peak, floor: 28 };
  } else {
    let bin = '', sr = 0, sg = 0, sb = 0, n = 0;
    for (let i = 0; i < d.length; i += 4) {
      bin += String.fromCharCode(d[i], d[i+1], d[i+2]);
      sr += d[i]; sg += d[i+1]; sb += d[i+2]; n++;
    }
    maps[key] = { w, h, rgb: btoa(bin),
                  mean: [Math.round(sr/n), Math.round(sg/n), Math.round(sb/n)] };
  }
}
return { note: 'Equirectangular. Row 0 is the north pole, column 0 is longitude -180.',
         source: 'Solar System Scope textures (https://www.solarsystemscope.com/textures/), CC BY 4.0, downsampled',
         maps };
'''


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.normpath(os.path.join(here, '..', '..', '..', '.tex'))
    os.makedirs(out, exist_ok=True)
    jobs = []
    for key, name in FILES.items():
        path = os.path.join(out, name)
        print('  ', name)
        r = subprocess.run(['curl', '-sS', '--max-time', '120', '-o', path, BASE + name])
        if r.returncode != 0 or not os.path.getsize(path):
            sys.exit('fetch failed: ' + name)
        w, h = SIZES.get(key, (64, 32))
        jobs.append([key, name, w, h])
    print('\nDownloaded to', out)
    print('The floor of 28 on the night map is not a taste call: of its 41,472 pixels,')
    print('38,433 sit in one low bucket, which is airglow over empty ground, and the')
    print('brightest city only reaches 150. Stretching from 28 to 150 is what turns a')
    print('brown smear back into cities.\n')
    print('Now run this in a browser page served from the repo root:')
    print(SNIPPET % jobs)


if __name__ == '__main__':
    main()
