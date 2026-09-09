# OpenStreetMap Dot

A world map rendered entirely as dots.

A normal vector map is drawn offscreen, then resampled onto a lattice where each
cell's brightness becomes a dot radius. Nothing else is ever drawn. The result is
a map made of light on black — built for OLED panels, where an unlit pixel costs
no power.

![Montpellier at zoom 12](shots/montpellier-z12.png)

## Run it

It must be served over HTTP. Opening `index.html` from the filesystem will not
work: MapLibre decodes tiles in Web Workers, and browsers refuse to create
workers on a `file://` origin.

```bash
python3 -m http.server 8731
```

Then open <http://localhost:8731>.

No build step, no package manager, no API key. MapLibre is vendored in
`vendor/`, so the only network traffic is map tiles.

## How it works

**The lattice is the compression.** A viewport can never hold more than
`viewport ÷ dot pitch` dots, however much map lies underneath. At 8px pitch a
1600×900 view is ~22,000 dots whether it sits over a city or over open ocean.

**Dot pitch follows zoom** — 18px when you are looking at a region, 3.5px down
in the streets. Zoom out and dots grow coarse; zoom in and they tighten as finer
detail resolves.

**Tiles stream by territory.** Vector tiles are fetched per tile per viewport, so
moving into new ground loads it and staying put loads nothing.

**The style is a luminance budget, not a colour scheme.** Brightness is spent
only on what makes a map legible:

| Feature | Value | Result |
| --- | --- | --- |
| Background, empty land | `#000000` | unlit — no power |
| Water | `#101010` | faint texture |
| Buildings | `#333333` | small dots |
| Minor → secondary roads | `#5a5a5a` → `#9a9a9a` | mid dots |
| Motorway, trunk, primary | `#ffffff` | full dots |

Measured on a 2056×1158 viewport at default settings:

| View | Dot pitch | Dots lit | Lit area | Pixels dark |
| --- | --- | --- | --- | --- |
| z12.4, wide | 8.6 px | 4,022 / 32,400 | 3.4% | 96.6% |
| z18.5, street | 3.5 px | 99,605 / 194,628 | 0.9% | 99.1% |
| z16.4, 3D at 58° | — | 118,307 / 176,085 | 5.3% | 94.7% |

The HUD reports lit area live, so the power goal stays a number you can tune
against rather than a judgement call.

## Sharing a view

The URL carries the view in openstreetmap.org's own hash format:

```
#map=12.40/43.61190/3.87720
```

It updates as you move, so any view can be bookmarked or sent to someone. A link
copied from openstreetmap.org opens the same place here.

## Controls

| Control | Effect |
| --- | --- |
| `DOT SCALE` | Multiplies dot pitch — coarser or finer lattice |
| `GAIN` | Response curve from brightness to dot size |
| `CUTOFF` | Brightness below which a cell stays unlit |
| `3D DOT VIEW` | Buildings as extrusions, height driving brightness |
| `AMBER` | Amber instead of white — cheaper on OLED, blue subpixel stays dark |

## Known limits

- **Not a labelled map.** A dot lattice destroys text and fine geometry by
  design. Labelling belongs in surrounding UI.
- **The filter does not reduce data.** A full map still renders underneath. This
  buys the look and the OLED saving, nothing else. A genuinely low-data version
  would rasterise raw vector-tile geometry directly, with no basemap render.
- **Cannot run as a published Claude Artifact** — that sandbox blocks tile
  requests.

## Attribution and licensing

Map data © [OpenStreetMap](https://www.openstreetmap.org/copyright)
contributors, available under the Open Database License (ODbL). Attribution must
stay visible in any deployment — the app renders it itself, since the opaque dot
canvas hides MapLibre's own attribution control.

Tiles served by [OpenFreeMap](https://openfreemap.org/), free and without an API
key.

[MapLibre GL JS](https://maplibre.org/) is vendored under `vendor/` and is
BSD-3-Clause licensed.
