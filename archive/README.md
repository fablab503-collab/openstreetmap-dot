# Archive

Earlier stages of DotWorld, kept for the history. Nothing here is used by the live site.

| Folder | What it was |
|---|---|
| `prototype-canvas2d/` | The first working dot map (2026-09-09): Montpellier only, halftone drawn with Canvas2D `arc()` paths. Its vendored MapLibre files were dropped — they were the same 6.9.0 build now in `vendor/` — so to run it, copy `vendor/*` next to its `index.html` and fix the import paths. |
| `skill-dots-v1/` | The first skill, written the same day as the prototype. Superseded by `skills/dotworld/`, which covers the GPU renderer, data layers, colour rules, measuring and publishing. |

Why the prototype was replaced: at street zoom its Canvas2D arcs took 18.3 ms a frame
(about 30 ms with 180k dots), too slow for 60 fps. The WebGL2 shader takes 0.1–0.5 ms.
See `CHANGELOG.md`.
