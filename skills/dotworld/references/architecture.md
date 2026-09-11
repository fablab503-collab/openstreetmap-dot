# Architecture

## A — the overlay pipeline DotWorld ships

```
#map     MapLibre (WebGL)  tiles, globe, camera, data layers — never seen directly
           │  on every 'render': texImage2D(map.getCanvas())
           ▼
#dots    WebGL2 canvas     one full-screen strip + the dot shader
           ▼
#labels  2D canvas         capital markers and names, redrawn each frame
           ▼
DOM panels
```

Both overlay canvases are `pointer-events: none`, so drags and scrolls reach the map.

### MapLibre

```js
import * as maplibregl from './vendor/maplibre-gl.mjs';   // v6: ESM, named exports

const map = new maplibregl.Map({
  container: 'map',
  style,                                   // style root: projection: { type: 'globe' }
  attributionControl: false,               // hidden under the overlay — render your own
  maxPitch: 85,
  canvasContextAttributes: {               // v6 location; top-level is ignored
    preserveDrawingBuffer: true,
    antialias: false                       // the lattice resamples anyway
  }
});
map.on('render', () => { dirty = true; }); // redraw only when MapLibre made a frame
```

### The dot shader

```glsl
#version 300 es
precision highp float;
uniform sampler2D u_src;
uniform vec2  u_res;
uniform float u_step, u_texScale, u_cut, u_gain, u_neutralA;
uniform vec3  u_dot;
uniform bool  u_data;
out vec4 o;
void main() {
  vec2 f   = gl_FragCoord.xy;
  vec2 ctr = (floor(f / u_step) + 0.5) * u_step;
  // The mip level whose texels are one cell wide holds the cell's average.
  vec3 c  = textureLod(u_src, ctr / u_res, max(0.0, log2(u_step * u_texScale))).rgb;
  float L = dot(c, vec3(0.299, 0.587, 0.114));
  o = vec4(0.0, 0.0, 0.0, 1.0);
  if (L <= u_cut) return;
  float r = pow((L - u_cut) / (1.0 - u_cut), 1.0 / u_gain) * u_step * 0.5;
  if (r < 0.35) return;
  float mx = max(c.r, max(c.g, c.b));
  float mn = min(c.r, min(c.g, c.b));
  vec3 col = u_dot;
  float alpha = u_neutralA;
  if (u_data && mx > 0.0 && (mx - mn) / mx > 0.28) {
    r = max(r, 0.9); col = c / mx; alpha = 1.0;
  }
  o = vec4(col * clamp(r - distance(f, ctr) + 0.5, 0.0, 1.0) * alpha, 1.0);
}
```

| Uniform | Value |
|---|---|
| `u_step` | lattice pitch in device px: `pitchFor(zoom) * DPR` |
| `u_texScale` | `src.width / dots.width` — MapLibre uses the real devicePixelRatio, the overlay caps DPR at 2 |
| `u_cut`, `u_gain` | CUTOFF (0.03) and GAIN (2.05) |
| `u_neutralA` | 0.38 while data is shown, else 1 |
| `u_dot` | chosen dot colour as 0–1 RGB |
| `u_data` | whether data keeps its hue |

Upload with `UNPACK_FLIP_Y_WEBGL = true` (GL's y axis points up), texture
`LINEAR_MIPMAP_LINEAR`, `CLAMP_TO_EDGE`, and `generateMipmap` after every upload.

```js
function pitchFor(zoom) { return clamp(18 - (zoom - 3), 3.5, 18) * scale; }   // CSS px

function drawGL(src, step) {
  gl.viewport(0, 0, dots.width, dots.height);
  gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, src);
  gl.generateMipmap(gl.TEXTURE_2D);
  // …set the uniforms above…
  gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
}
```

### The same rule on the CPU (counting and the fallback)

```js
const CELL = { r: 0, data: false, mx: 0 };        // reused: no allocation per cell
function cellDot(r8, g8, b8, rMax) {
  const L = (r8 * 0.299 + g8 * 0.587 + b8 * 0.114) / 255;
  if (L <= cutoff) return null;
  let r = Math.pow((L - cutoff) / (1 - cutoff), 1 / gain) * rMax;
  if (r < 0.35) return null;
  const mx = Math.max(r8, g8, b8), mn = Math.min(r8, g8, b8);
  const data = dataColour && mx > 0 && (mx - mn) / mx > 0.28;
  if (data) r = Math.max(r, 0.9);
  CELL.r = r; CELL.data = data; CELL.mx = mx;
  return CELL;
}
```

Keep the shader and `cellDot` identical line for line — the HUD's lit-area number
is only honest if both apply the same rule.

### Fallback and context loss

- Try `canvas.getContext('webgl2')`. If the shader then fails to compile, **clone
  the canvas element** before falling back: a canvas that has handed out a WebGL
  context can never give a 2D one.
- `webglcontextlost` → `preventDefault()` and drop GL resources;
  `webglcontextrestored` → rebuild them and mark dirty.
- `?renderer=cpu` forces the Canvas2D path, for comparison.

### Render loop

```js
(function loop() {
  requestAnimationFrame(loop);          // re-arm FIRST: a throw below must not end rendering
  if (dirty) { dirty = false; halftone(); }
})();
```

Every module-level `let` that `halftone()` reads must be declared **above** this
loop — it runs its first frame immediately, and a `let` still in its temporal dead
zone throws.

### Counting lit dots without stutter

```js
let statsTimer = null;
function countWhenStill() {
  clearTimeout(statsTimer);
  statsTimer = setTimeout(() => {
    if (map.isMoving() || orbitRAF) { countWhenStill(); return; }
    const src = map.getCanvas();
    const zoom = map.getZoom(), pitch = pitchFor(zoom), step = pitch * DPR;
    const cols = Math.ceil(dots.width / step), rows = Math.ceil(dots.height / step);
    small.width = cols; small.height = rows;                   // one pixel per cell
    sctx.drawImage(src, 0, 0, cols, rows);
    const px = sctx.getImageData(0, 0, cols, rows).data;
    // loop cellDot() over px, sum lit cells and PI*r*r, update the HUD
  }, 250);
}
```

The GPU path calls `countWhenStill()` after drawing and performs no readback of its
own. While moving, only zoom, pitch and frame time update.

**Better, not yet built:** WebGL2 asynchronous readback — render one pixel per cell
into a small framebuffer, `readPixels` into a `PIXEL_PACK_BUFFER`, create a
`fenceSync`, poll `clientWaitSync(sync, 0, 0)` on later frames, then
`getBufferSubData` into a reused array. The readout stays live and never blocks.
Measure it before replacing `countWhenStill`.

### Labels on the overlay

- Load the capitals once; sort by population so the biggest win space.
- Each frame: `project()` each capital, skip off-screen points, greedy rectangle
  collision against already placed labels, stop at 55.
- **On the globe `project()` still returns points on the far side** — cull by
  angular distance from the map centre (> 82°).
- Guard the projection read: `const p = map.getProjection && map.getProjection();
  const onGlobe = !!p && p.type === 'globe';`
- The marker carries colour and size; the text stays neutral ink (white name,
  grey number) over an 85%-black backing box.

### Other lifecycle traps

| Trap | Fix |
|---|---|
| `rotatestart` / `dragstart` also fire for your own `easeTo` | Treat only events with `e.originalEvent` as user gestures |
| An ease and a per-frame `setBearing` orbit fight | Start the orbit on `map.once('moveend')` |
| `moveend` fires every orbit frame | Skip `history.replaceState` while orbiting |
| Map built in a 0×0 container frames against nothing | On first real size, `map.resize()` and re-fit |
| Canvas sized from `innerWidth` once | Measure the element; `ResizeObserver` |
| `getLayer`/`getStyle` before the style loads | Check `map.isStyleLoaded()` |

## B — custom layer inside MapLibre (not built, unverified)

An independent design pass proposed drawing the dots **inside** MapLibre's own WebGL2
context with a `custom` layer:

1. In the layer's `render()`, `copyTexSubImage2D` the current frame into a texture
   and `generateMipmap`.
2. Draw one pixel per cell at mip level `log2(pitch)`, clear, then draw the dot shader.
3. Put a `symbol` layer for labels **after** the custom layer — sharp text, MapLibre
   collision handling, globe far-side culling, and a working attribution control.

Caveats it raised itself: it relies on MapLibre restoring GL state after `render()`,
which is internal behaviour rather than a documented promise; terrain renders into a
texture and breaks the copy; antialiasing must be off. Prototype and measure it on
every target browser before choosing it over A.
