# Colour and luminance

## The basemap is a luminance budget

Every value is a brightness decision: bright becomes a big dot, near-black stays an
unlit pixel. Build it dark-first — halftoning a normal light basemap lights most of
an OLED panel, the opposite of the goal.

| Feature | Value | Becomes |
|---|---|---|
| Background (land) | `#242424` z4 → `#181818` z8 → `#151515` z14 | faint field; the coastline is its edge |
| Water | `#0f0f0f` | faint texture |
| Landcover (wood, grass) | `#0d0d0d` | near nothing |
| Waterways | `#2c2c2c` | thin lines |
| Buildings | `#333333`, from z13 | small dots |
| Building outlines | `#8a8a8a`, 0.4 → 1.4 px, from z15 | readable edges at street zoom |
| Minor roads, service, track, path, footway | `#5a5a5a` | mid dots |
| Secondary, tertiary | `#9a9a9a` | larger dots |
| Motorway, trunk, primary | `#ffffff` | full dots |
| Admin boundaries ≤ level 4 | `#4a4a4a` dashed | faint |
| 3D buildings | `render_height` 0 → 60 m mapped `#242424` → `#f0f0f0` | skyline as relief |

### Floors, not voids

With water and ground at pure `#000000`, open sea rendered 0 dots at every zoom and
open country at z18 reached a maximum channel of 13. The screen looked broken. Keep
a floor; raising CUTOFF still removes it.

A floor must also clear the **minimum radius cull** (`r < 0.35` device px). With
cutoff 0.03, gain 2.05 and a 2.3 px pitch at DPR 2, a cell needs luma ≈ 0.057
(`#0f0f0f`) to survive. An earlier land value of `#131313` sat just above the cutoff,
produced ~0.06 px dots, and silently vanished.

```text
r = ((L - cutoff) / (1 - cutoff)) ^ (1 / gain) × pitch × DPR / 2
```

## Keeping data colour through the lattice

- Author the basemap only in greys, so saturation alone marks data.
- Per cell: `chroma = (max − min) / max`. Above **0.28** → data: keep the hue,
  normalised to full brightness (`rgb / max`), minimum radius 0.9 px. Otherwise →
  basemap: draw in the chosen dot colour.
- While data is shown, draw basemap dots at **38%** opacity. Hiding colour alone was
  not enough: an evenly lit lattice drowned a few hundred data points.
- **Averaging costs chroma.** A cell's colour is the mean of everything under it, so
  a small data circle is diluted by the grey ground around it. Worked through
  arithmetically, not yet observed on screen: a `#ffeda0` circle covering 9% of a
  `#242424` cell averages to chroma ≈ 0.15, below the 0.28 threshold, so it is drawn
  as a grey basemap dot. That is the reversed YlOrRd's **top** stop — the one the
  biggest places get. Large circles fill their cells and survive; the risk is a high
  value drawn small (zoomed far out). `#FDE725` (viridis) at the same 9% keeps chroma
  ≈ 0.35. Mitigations: keep data radii ≥ one pitch; prefer ramps whose top stops
  stay saturated; or give data circles a black stroke so edge cells mix with black
  (same hue, smaller dot) rather than grey.
- Text never takes the series colour. The marker carries the colour; names stay
  white and numbers neutral grey.

## Population ramps on a black ground

### Reversed YlOrRd (what DotWorld ships)

YlOrRd is ColorBrewer's standard sequential ramp for population, and the one
Leaflet's choropleth example uses. As published it runs light → dark, correct on
white paper (more ink = more) but inverted on black:

| Published order (low → high) | Luminance |
|---|---|
| `#FFEDA0` | 0.844 |
| `#FED976` | 0.720 |
| `#FEB24C` | 0.534 |
| `#FD8D3C` | 0.403 |
| `#FC4E2A` | 0.263 |
| `#E31A1C` | 0.172 |
| `#BD0026` | 0.110 |
| `#800026` | 0.047 |

Reverse it so luminance rises monotonically with the value:
`#800026 #bd0026 #e31a1c #fc4e2a #fd8d3c #feb24c #fed976 #ffeda0`.

- **France** — stops at 15k, 25k, 40k, 70k, 120k, 250k, 600k, 2.1M; circle radius
  grows with population too.
- **Capitals** — log scale across 1 K – 22 M:
  `t = clamp((log10(pop) − 3) / (log10(22e6) − 3), 0, 1)`; marker radius
  `1.8 + 3.2t` px; missing population → grey `#6a6a6a`, radius 1.6.

### Viridis (a valid alternative)

Viridis already rises in lightness. Skip its darkest start (`#440154` nearly
disappears on black) and use t = 0.3 → 1.0:
`#355F8D #2A788E #21918C #22A884 #44BF70 #7AD151 #BDDF26 #FDE725`.

Whichever ramp: check that luminance rises with value on the actual background, and
use a log scale whenever the range spans orders of magnitude.

## Categorical palettes: validate, don't eyeball

Run a colour-vision validator on the palette **in adjacency order**. For dark mode
DotWorld used the dataviz skill's `validate_palette.js --mode dark`.

| Attempt | Result |
|---|---|
| `#ff7a1a #ffd400 #38e04b #ff3ad2 #ff3b30 #a86bff` | FAIL — green vs gold ΔE 2.5 under protanopia; four outside the lightness band |
| `#d95926 #c98500 #199e70 #d55181 #9085e9 #e66767` | FAIL — magenta vs aqua ΔE 1.6 (deuteranopia); orange vs yellow ΔE 10.6 even for normal vision |
| **`#d95926 #199e70 #c98500 #9085e9 #d55181`** | **PASS all six checks** — worst CVD ΔE 8.4 |

Six categories could not be separated safely, so gate and castle merged into
"fortification". The shipped mapping: museum `#d95926`, fortification `#199e70`,
religious `#c98500`, theatre `#9085e9`, square `#d55181`. Blue stayed reserved for
nothing in particular — avoid reusing a hue that a sequential ramp already uses.

## Sixteen dot colours for OLED

Ordered warm to cool, which is roughly cheapest to most expensive on an OLED — amber
and red leave the blue subpixel dark, white drives all three:

WHITE `#ffffff` · BONE `#f0e6d2` · GOLD `#ffd400` · AMBER `#ffb000` · ORANGE `#ff7a1a`
· RED `#ff3b30` · ROSE `#ff4d8d` · MAGENTA `#ff3ad2` · VIOLET `#a86bff` · INDIGO
`#6b7bff` · BLUE `#2f9bff` · SKY `#35c8ff` · CYAN `#22e0d6` · MINT `#2ee6a8` · GREEN
`#38e04b` · LIME `#b4f13a`

## Measured power proxy

The HUD reports LIT AREA = Σπr² ÷ canvas area. Measured before the floors were added:
3.4% lit at z12.4, 0.9% at z18.5, 5.3% in 3D at z16.4 (Montpellier). Re-measure after
any style change rather than quoting old figures.
