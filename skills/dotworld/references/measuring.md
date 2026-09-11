# Measuring a dot renderer

## Numbers measured on DotWorld

M2 Pro, WebKit (Claude's in-app Browser pane), 2026-09-11.

| What | Result |
|---|---|
| Canvas2D `arc()` paths, synthetic 14k / 45k / 180k dots | 4.6 / 7.7 / **29.9 ms** |
| Canvas2D arcs, real content, z17, 111k cells | **18.3 ms** |
| CPU anti-aliased mask stamping into `ImageData`, 14k–180k dots | 50–102 ms — the full-frame clear and `putImageData` dominate |
| WebGL2 shader, synthetic 4112×2316, upload + mipmap + draw | 1.5–1.8 ms (shader alone 0.6 ms) |
| WebGL2 in-page draw with `gl.finish()`, real content | **0.1–0.5 ms** |
| `texImage2D` from MapLibre's WebGL canvas | ~0 ms, including the first upload after a fresh frame |
| `drawImage` + `getImageData` readback of the map frame | 1.2 ms in one run, 18–21 ms in another, ~55 ms in a third |
| `getImageData` on a plain 2D canvas, 894×504 | 0.86 ms |
| Per-cell count loop, ~133k cells | 3.8–5.4 ms |
| Labels: 195 capitals projected, measured and drawn | 0.1–0.3 ms |

Only WebKit was measured. An independent pass warned that some browsers copy a WebGL
canvas source through the CPU — about 22 MB per frame at high DPI. Measure Chrome and
Firefox before relying on near-zero uploads.

## Traps that produced wrong numbers

- **Hidden or background tab.** `requestAnimationFrame` ran about 2 frames per
  800 ms, timers clamped to ≥ 1 s, CSS transitions stayed at frame 0, and the map
  style sometimes never finished loading. Sampling real frames returned the same
  stale value thirteen times (52.3 ms).
- **Black source frames flatter everything.** With no map content, the Canvas2D path
  draws nothing and looks fast. Check content before timing.
- **Order and neighbours matter.** The same readback cost 56 ms right after GL work
  in the GPU tab and 4 ms in the CPU tab. A "first access after a new frame is
  expensive" theory was then tested directly — upload 0 ms, read 1.2 ms — and was
  wrong. Test each explanation before stacking another on top of it.
- **A median hides spikes.** A stats pass at 2.5 Hz with a 50 ms stall still hitches
  even if the median frame is 1 ms.
- **Stale paint after a filter change.** `queryRenderedFeatures` a second after
  `setFilter` returned the old count; after 4 s it was right.
- **One-off outliers.** Labels once measured 9.7 ms; four repeats gave 0.1–0.2 ms.
  Repeat before optimising.

## Synchronous bench hook

```js
window.__bench = (n = 20) => {
  const src = map.getCanvas();
  const zoom = map.getZoom(), step = pitchFor(zoom) * DPR;
  const cols = Math.max(1, Math.ceil(dots.width / step));
  const rows = Math.max(1, Math.ceil(dots.height / step));
  const time = fn => { const a = performance.now(); fn(); return performance.now() - a; };
  const draw = [], read = [], loop = [], text = [];
  for (let i = 0; i < n; i++) {
    let px = null;
    read.push(time(() => { px = sampleCells(src, cols, rows); }));
    loop.push(time(() => { measureCells(px, cols, rows, step); }));
    draw.push(time(() => {
      if (gl && glr) { drawGL(src, step); gl.finish(); }   // finish: include GPU time
      else if (ctx) drawCPU(px, cols, rows, step);
    }));
    text.push(time(() => { lctx.clearRect(0, 0, labels.width, labels.height); drawCapitals(); }));
  }
  const med = a => +[...a].sort((x, y) => x - y)[a.length >> 1].toFixed(2);
  return { renderer: window.__renderer, zoom: +zoom.toFixed(2), cells: cols * rows,
           drawMs: med(draw), readbackMs: med(read), countLoopMs: med(loop), labelsMs: med(text) };
};
```

## Quick checks that settle a question

```js
// Does the source frame have content?
const t = document.createElement('canvas'); t.width = t.height = 64;
const x = t.getContext('2d'); x.drawImage(map.getCanvas(), 0, 0, 64, 64);
let max = 0; const d = x.getImageData(0, 0, 64, 64).data;
for (let i = 0; i < d.length; i += 4) max = Math.max(max, d[i], d[i+1], d[i+2]);

// Is the tab even rendering?
({ visibility: document.visibilityState, w: innerWidth, h: innerHeight,
   style: map.isStyleLoaded() });
```

- In a script that waits, race every animation-frame wait against a timeout, and keep
  the whole script well under the tool's time limit — hidden tabs stall rAF forever.
- To see a real frame from Claude's Browser pane, take a screenshot: it composites once.
- Measure layout overlaps numerically (`getBoundingClientRect`) rather than by eye.
- When a pane refuses to emulate narrow widths (it clamped to 980 px here), say the
  breakpoint is untested rather than claiming it works.
