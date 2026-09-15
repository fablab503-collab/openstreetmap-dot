# Changelog

Every change to DotWorld, with the reasons and the measured numbers behind it.
Newest first. Data sources and licences are in [CREDITS.md](CREDITS.md).

---

## 2026-09-15 — A jump with a thumb on it, and roofs to land on

Daniel: "add the real gravity and jump. it needs to jump really high in base of how long
do you press the space bar. it's allowed to jump and go on buildings."

### Changed

- **The jump has a thumb on it now.** The push off the ground is the same every time;
  holding the key keeps pushing, at 900 px/s², for up to four tenths of a second. Gravity
  is 900 px/s² throughout. Measured: a tap peaks at **46 px**, a held key at **140 px** -
  three times the height, from the same key.
- **A wall only stops what is shorter than it.** Every building carries its own height in
  the tiles (`render_height`, in metres), and metres become pixels through the map's own
  scale, so a jump that clears a four-storey building at street zoom does not clear a
  continent at country zoom. Over the roofline you walk on.
- **Roofs are ground.** Land on one and you stand on it; walk across it and off the far
  side and you fall to the street. Measured: blocked by a wall at 0 m, a held jump over
  it crossing 41.6 m, and a shorter hop settling at **26.2 px** - a building of about
  eight metres - then walking off it and coming down to 0.
- **On a roof you are not hidden by the building you are on.** The occlusion test now
  asks how high you are before deciding you are behind something.

### Measured

- 8.3 ms between frames with all of it running, the label canvas 0.5 ms. The height
  questions are `queryRenderedFeatures` on the footprint layer, a handful a frame.

---

## 2026-09-15 — The game, after watching it played

Daniel played it and sent a list. All of it is in.

### Changed

- **No Pac-Man ball.** He asked for the figures that were already there - ghost, person,
  car, whatever `T` is on - and for the game to be its own thing rather than a copy. The
  wedge-mouthed model is gone; you play as whoever is in `WHO FLOATS`.
- **The dots are rare now**, 150 px apart instead of 58, and smaller. The pickup reach
  went the other way, 15 px to 24: on a 150 px grid a 15 px reach meant threading a
  needle rather than walking past something.
- **The figures are smaller and quieter** - 22 px instead of 34, the glow down from .30
  to .16, the shadow and the tether fainter with them.

### Added

- **A solid blocks the sight of what is behind it.** Nothing can ever stand inside a
  building, so if a figure's point on screen lands on a drawn extrusion, the only thing
  that can mean is the building is between it and the eye - so it is not drawn, and
  neither are the dots behind it. It is not a depth buffer and it is wrong about a figure
  on the far pavement of a narrow street, but it is right about a whole solid in the way.
  **The player keeps a dashed ring** when it is hidden: you should not see through a
  wall, but losing yourself entirely is a bug, not a rule.
- **Being caught comes apart.** 46 of its own pixels, thrown out and falling under the
  same gravity the jump uses, settling on the ground and going out over 900 ms - then it
  starts again from where it started. Measured: caught after 5.7 s of standing still,
  46 pixels, three lives down to two.
- **Somewhere to go.** A destination every time, and a new one when you reach it: 62% of
  the time round the corner, 28% across the city or out of it, 8% another region or
  country, 2% anywhere on Earth up to 13,500 km. The panel gives the distance and the
  compass point; an arrow at the edge of the view points at it when it is off screen.
  Seen in testing: 491 m SE, then 21.3 km SE.
- **Coins that make you faster.** One dot in eleven is orange and worth 100 instead of
  10, and each one is a step up the ladder: 5% faster, then 10, 15, 25, 50, 100 - so the
  sixth is the one you remember.
- **The footprint is still queryable in 3D.** It used to be hidden, and a hidden layer
  is not rendered and cannot be asked anything, so in 3D the walls were being read off
  the extrusion's drawn shape - which covers the ground behind a building as well as the
  ground under it. It stays rendered at zero opacity now: the footprint answers "is there
  a wall", the extrusion answers "is something in the way".
- **A foe that gets itself stuck** in a courtyard with no way out is put back in play
  after 3 seconds, and they now start 220-700 px away rather than anywhere at all - on a
  wide window they used to begin a full screen away and take a minute to become a game.

### Not verified

The coin's speed step. Coins are laid (11 of the 85 dots in one run) and drawn, and the
award is the same branch as an ordinary dot, but I never managed to land on one while
testing: the browser I test in kept zooming the map between runs, which spreads a 150 px
grid to 4,800 px and ends the run. Worth a look the first time you play.

---

## 2026-09-15 — Pac-Man, on the real streets

Daniel: "add a little section called GAME, and when you press PLAY GAME it's gonna start
a game of Pac-Man... in the area of Montpellier. It's gonna be the biggest game ever of
Pac-Man, but make it really simple, that doesn't use any big data or anything at all."

### Added

- **A maze nobody drew and nobody loaded.** The buildings the map has already rendered
  ARE the maze - the streets are the gaps between them - so the game needs no data of its
  own at all and would work over any city you point it at. The dots go on a grid across
  the view and any that land indoors are thrown away; what is left is a dot in every
  street. Montpellier, from above, because that is where this whole thing started.
- **Four of them, chasing.** Red, pink, cyan and orange, each walking the one rule the
  player walks by: go on until a wall says no, then take a turn that is open - preferring,
  if it is one of the four, the turn that closes the gap, with enough noise in the choice
  that they do not all take the same corner. 92 px/s against the player's 135, or it
  would not be a game.
- **Pac-Man himself**, a ball with a wedge missing: the sweep stops short of the full
  circle and two flat faces close the gap. `pacGap` opens and shuts it about three times
  a second, so he chomps. Yellow, which is the one colour nobody needs told.
- **Three lives, ten a dot**, caught sends you back to the start and scatters them again,
  and every dot eaten wins it.

### Keys, in and out of the game

- `W A S D` **and the arrows** — half of everyone reaches for one and half for the other.
- `SPACE` jumps, **and a held key jumps further than a tap**: the push is the same either
  way, and letting go while it is still rising cuts the rise short. That is how a platform
  game has done variable height since 1985, and it plays far better than timing the press
  and only then leaving the ground.
- `P` pause · `R` start over · `T` change shape · `SHIFT + A` walk itself.
  **A on its own is already left**, which is a clash in the asking, so walking itself took
  the shift.

### Not built, on purpose

Daniel: "it could transform maybe one day in the game of Pac-Man in real life, where you
are Pac-Man and there are other people... but not for now, but saving the memory." Saved,
not started. What would be needed is the position of real people, which means consent, a
server, and a way to stop someone being tracked - none of which this app has, and all of
which come before the code.

---

## 2026-09-15 — W A S D, and space to jump

Daniel: "add some command to make it move through the maps using W for forward S back A
for left and D for right on the keyboard. add the functionality to move it through the
map but don't make it pass through the 3D objects like buildings and stuff. use space to
make it jump in the case."

### Added

- **W A S D walks it, at 135 screen pixels a second.** Across the screen, not across the
  compass: W is away from you whichever way the map is turned, which is the only version
  that stays predictable once you have rotated the map. A diagonal is not faster than a
  straight. It faces the way it is being pushed, and keeps facing that way when you let
  go rather than snapping back.
- **It does not walk through buildings.** The wall test asks the map itself -
  `queryRenderedFeatures` on whichever of the flat `building` layer and the extruded
  `building-3d` is switched on, since a hidden layer is not rendered and cannot answer.
  Blocked head-on it tries each axis on its own before giving up, so it slides along a
  wall instead of sticking to it. Measured: **0 metres** in 0.9 s of pushing into one.
- **Space jumps, and in the air it goes over the roof.** 210 px/s up against 560 px/s²
  down, which is 39 px high and about three quarters of a second; measured peak 39.8 px,
  back down to 0. Pushing into the same wall while airborne: **20.9 m in 0.5 s**.
- **The map comes along.** Within 90 px of an edge it pans by the overshoot, so it
  cannot be walked off the screen.
- **W with nothing dropped starts it in the middle of the view**, or the keys would do
  nothing at all and look broken. And they do nothing while you are typing in the search
  box - measured, 0 metres with W and D held in the field.

### Found by driving it

- **A search lands on a building more often than not** - a named place usually IS a
  building - so the first version put it inside one and it could never leave: 0 metres
  in any direction, forever. A wall only stops something that is not already in it.

---

## 2026-09-15 — Out: the wandering

Daniel, on seeing it drive off: "the model should be static and not move."

### Removed

- **The walking.** The road query, the way-to-way wander, the 340 m leash, the ghost's
  drift, and the heading that turned the model along the street - all of it. A marker
  that wanders off is no longer marking the place it was put there to mark, which was
  the point of it.
- **The slow yaw sway** went with it. A thing asked to hold still should hold still; the
  angle is fixed now and turns only with the map's bearing, so it stays part of the
  world.

Kept: the breathing, which is what was asked for in the first place. Measured after the
cut - **0 metres** over 8 seconds on the ground, and the drawn figure still rises and
falls 2 px in 0.7 s.

---

## 2026-09-15 — LOADING TILES… over a map that had already loaded

Daniel sent a screenshot of the boot line sitting there. It was telling the truth about
the wrong thing.

### Fixed

- **The line waited for `idle`, which means every tile in the viewport has arrived.**
  One slow tile out of forty and it sat there over a map that was already drawn. It goes
  on `load` now - the style ready and the first frame rendered, which is when there is
  something to look at - and `idle` is kept as a second chance.
- **And it now says what it is waiting for.** After 10 seconds: STILL WAITING FOR
  OPENFREEMAP. After 25: that OpenFreeMap is a free service, is sometimes down, and to
  try again in a minute. Staring at LOADING TILES with no idea whether it is your
  connection, the app, or the tile server is the worst of the three. Capped at
  `min(88vw, 560px)` so the longer line wraps on a phone instead of running off it.

---

## 2026-09-15 — And it goes about its business

Daniel: "so he can move a bit like slow but just between the buildings, just in the area
or the street map for the bikes, person or highways."

### Added

- **It takes the ways it belongs on.** The ways come out of the tiles already on screen -
  the same `transportation` layer the map draws its roads from - so a car and a bus keep
  to motorway through service, a bicycle adds tracks and paths, and a person or a dog
  walk the footways. It enters a way at the corner it is nearest to, walks to the end,
  and takes whatever other way touches that spot; at a dead end it turns round. Below
  zoom 12 the tiles carry no minor roads, so there is nothing to walk on and it simply
  hangs where it was put.
- **A ghost owes nothing to anybody** and drifts through the buildings instead, on two
  slow waves that never quite repeat, around forty metres of courtyard.
- **It faces where it is going.** A compass bearing shows on screen turned by itself
  minus the map's own bearing, and the model's nose is at -z, which is up the screen, so
  the yaw that points the nose along the way is the difference between the two. Standing
  still, it goes back to the corner view.
- **It stays in the area.** Past 340 m from where it landed, only the ways that lead back
  are on offer. Measured over 12 s of driving: furthest from the drop, **203 m**.

### Measured

- Speeds, over the ground, from the marker's own position: person **1.3 m/s**, dog 1.7,
  bicycle 4.4, car 9.9 over 7 s of real streets, bus 6.5 (turns cost displacement).
- The ghost's first draft crossed the square at **4.3 m/s** - a ghost late for something.
  Its speed is set by the wave frequencies, not by the speed table; at 0.024 and 0.041
  it drifts at **0.77 m/s**.
- Still no map redraws: 3 seconds, 433 browser frames of a car driving, **0** halftone
  passes. The whole label canvas is 0.3 ms.

---

## 2026-09-15 — Someone floats over the place you looked for

Daniel asked for a small 3D figure hanging a millimetre or two above the map, breathing
up and down, in a colour the map does not already use, appearing where a search lands -
a ghost by default, changeable in the settings to a person, a car, a van, a bus, a
motorbike, a bicycle, a dog. Detailed, but not complex.

### Added

- **Eight small solids, built from three primitives.** A box, a cylinder and a sphere,
  placed against each other in a box one unit tall: ghost (a lathe with a hem that goes
  up and down around the circle, a dome and two dark eyes), person, dog, bicycle,
  motorbike, car, van, bus - or NOBODY. `WHO FLOATS OVER A PLACE YOU FIND` in the
  settings, and it changes what is already hanging there.
- **Its own renderer, about 30-75 faces.** Painter's order, back faces dropped by the
  sign of the screen-space cross product, flat shading from one light. It turns with
  the map's bearing and holds its size at every zoom, because a marker is a thing you
  look at, not a thing that scales with the ground. A shadow that tightens as it comes
  down and a dotted line back to the exact point say the height is real.
- **An ice blue nothing else uses:** `#eaf4ff` down to `#3d4f6e`, lit by `#9dc4ff`.
  Every layer here already owns a hue - YlOrRd for people, silver for the chosen
  country, amber for the border light, cyan for monuments - so the one who floats
  needed its own or it would read as another measurement.

### Measured

- **The bob costs no map redraws at all.** The label canvas was split out of
  `halftone()` into `paintLabels()`, and the marker asks for that alone: over 2 seconds
  and 289 browser frames with the ghost breathing, the halftone ran **0 times**. The
  whole label canvas, ghost included, is 0.4 ms.
- `window.__marker` gives `.at`, `.kind`, `.faces` and `.size(px)` - blowing it up to
  170 px is how the wireframe-globe sphere and the eyes on the wrong side were found.

### Found by looking at it

- Edges drawn on every face turned a 74-face sphere into a wireframe globe. Flat-sided
  parts are stroked dark now; curved ones are stroked in their own colour, only to close
  the hairline the filler leaves between faces.
- At 15° above the horizon and nose-on, a car is a rectangle. 32° and a 36° turn made it
  a car; a face is turned much less, because the ghost at 36° showed one eye and gazed
  off past your shoulder.

---

## 2026-09-15 — And then its ten biggest cities, one by one

Daniel: "in the same way but a bit smaller make appear for 5 seconds after the country
name also 10 biggest cities in order of inhabitants 1 by 1 and make them disappear
after 10 seconds."

### Added

- **The country's ten biggest cities, biggest first.** The moment the country's own
  name has flashed out, they arrive one every 500 ms - so all ten are there at five
  seconds - each decoded the same way in 350 ms, at 11 px against the country's 34.
  They stand until ten seconds and then leave together in a 400 ms fade. The rank
  carries the order in the border light's amber, `#ffeda0`; the name is white; a small
  amber ring marks the city itself. Measured on the clock: 1 city at 0.2 s, 3 at 1.2 s,
  6 at 2.7 s, all 10 by 4.8 s, still 10 at 9.8 s, gone by 10.6 s.
- **Ordered by the population on file, not the one the year bar shows.** A year scales
  every city in a country by the same factor, so it can change what the figure says but
  never who is biggest. Italy comes out Rome, Milan, Naples, Turin, Palermo, Genoa,
  Bologna, Florence, Bari, Catania; Spain: Madrid, Barcelona, Valencia, Zaragoza,
  Sevilla, Málaga, Murcia, Palma, Las Palmas de Gran Canaria, Alicante.
- **The list dodges the labels already on the canvas.** The capital is usually its
  country's biggest city and its label is already drawn there, so `drawCapitals` now
  shares the boxes it placed; a city that would land on one drops a line, twice, then
  takes the spot anyway - a name the reader is waiting for beats a tidy frame.

### Fixed

- **Picking a new country left the old one still talking.** The reveal only starts when
  the camera arrives, so between the pick and the arrival the previous country's cities
  went on decoding over a map already on its way somewhere else. Picking anything now
  stops whatever was being said.

---

## 2026-09-15 — The country says its own name

Daniel: "once i tap the capital and it's zooming in the country add the name of the
country in the center of the country for a couple of seconds like the matrix movement
and then disappear with a little flash."

### Added

- **The country's name, decoded across the middle of it.** Pick a country - tap its
  capital, choose it in the picker, or press WHERE AM I - and once the camera has
  stopped, the name is written over the land: each letter cycles through a scramble of
  glyphs and locks into place left to right over 900 ms, holds for 1.7 s, then goes in
  a 300 ms flash with a ring leaving the middle of the word. 2.9 s in all, which ends
  before the border trace does at 3.2 s - the name introduces the country, the light
  finishes drawing it. Locked letters are white, unlocked ones the same amber as the
  border light, `#ffeda0`.
- **It is placed where the country is widest, not at the centre of its box.** A
  bounding-box centre lands outside anything bent: Azerbaijan's falls in Armenia and
  Norway's in Sweden. This is the pole of inaccessibility, crudely - of a 24 x 24 grid
  of points inside the mainland ring, the one furthest from the border. The ring is
  thinned to 600 points first, which turns about 6 million distance tests into 350
  thousand and costs a little accuracy on a fjord. Measured placements: Azerbaijan
  47.13 E 40.37 N, Russia 106.86 E 61.68 N (central Siberia), Mongolia 104.49 E
  46.20 N.
- **Sized to the country it names.** The name takes about half the country's width on
  screen, clamped to 12-34 CSS px, so it reads as a label on the land rather than a
  banner across the window, and Russia does not arrive in letters a hand high.

### Measured

- Median frame during the reveal: **0.4 ms**, max 0.7 ms over 40 frames - it is text on
  the label canvas, which was already being cleared and redrawn every frame.
- The border trace still runs underneath it: lit area 13.1% while the light is on the
  border, 12.5% once it has faded.
- `window.__nameFX` carries the text, its position and its start time while the reveal
  is on screen, and is null the rest of the time.

---

## 2026-09-14 — The black when you zoom in: three faults, one symptom

Daniel: "there is a black matter coming when zooming in." Three separate things
were making it, and the third made the planet disappear outright.

### Fixed

- **The blur was worked out per dot, against the body's centre.** On a close planet
  the near cap sits a long way off that plane in relative terms, so the middle of the
  Earth smeared into soft blobs while its rim stayed sharp. A body is one object at
  one distance now: one blur for the whole of it, taken from its centre - which also
  means whatever you are looking at is always sharp, since its own distance *is* the
  focal distance.
- **Dim dots quantised to pure black.** Colours are packed to sixteen levels a channel
  to keep the painter batching, and the packing truncated: every channel under 16 fell
  to level zero. So the unlit half of a planet came out #000000 - invisible - and the
  ambient floor did nothing. It rounds now, and the floor went from 0.07 to 0.16.
- **A near-plane guard in display units, and true scale falls under it.** A display
  unit is ten billion metres at true scale, so standing 1.4 Earth radii up puts the
  whole planet at z = 0.0009 - under the `z > 0.001` the draw loop used to decide what
  is in front of the camera. **Below about 1.57 radii the Earth was simply dropped
  from the frame.** It is a named constant now, `NEAR = 1e-12`, in all five places
  that guard depth. Coverage across the zoom, measured: 1.02 radii 100% of the screen
  and 11,745 dots, 1.1 → 98.7%, 1.4 → 77.4%, 2 → 48.4%, 3.2 → 19.3%, 20 → 89 dots,
  1000 → one point of light.

### Added

- `window.__space.dbg` - what the renderer actually did with each body last frame:
  its distance, its screen radius, the lattice pitch and how many dots it drew. None
  of this is reachable from outside the module, and three rounds of guessing at this
  bug is what it cost to not have it.

---

## 2026-09-14 — Out: the night lights and the hand spin

Daniel called both of them bugs and asked for them out. They are out.

### Removed

- **The night lights.** The whole night-side illumination: the real night-lights
  map, the `lights` parameter and the population-dot alternative with it. The dark
  half of a planet is now just its own colour at an ambient floor, which is what the
  rest of the bodies always did. `data/planet-colours.json` lost its 288x144 night
  map with them and is 169 KB instead of 224.
- **Grabbing a planet to spin it.** The hand spin, the flattening it drew, the
  `bulge` parameter, the SPUN BY HAND readouts and `GIVE THE SPINS BACK`. Dragging
  turns the camera again, wherever you start it, and a body is a circle again.

### Kept

- Real colour per body, real sunlight at 5772 K, and the `realism` parameter.
- Every body still turns at its own rate, and THE SPIN still reads out the facts:
  the sidereal day against the solar one and why they differ, where the Sun stands
  overhead, the ground speed by latitude, what the spin cancels of the pull, the
  21.4 km bulge and the day lengthening by 1.72 ms a century. Those are measurements,
  not the interaction that was removed.

### Fixed on the way

- Cutting the hand-spin block took the tidal rows out with it, so the panel threw on
  every frame. They are back where they belong.

---

## 2026-09-14 — The black ovals, and four times the speed

Daniel: something is off with the spin, and zooming makes black spots and oval
shapes — check the code, make it lighter and simpler.

### Fixed

- **The black ovals were the silhouettes.** Each body punches its own outline before
  its dots go down, so it can hide what is behind it. Two things made that read as a
  hole in the sky rather than a planet: it was filled in pure **black**, so an unlit
  body — where every dot is culled — left nothing but the hole; and the projected
  radius was **unclamped**, so the moment the camera came close it ran to several
  screens wide and swallowed everything. The fill is now the body's own darkest
  shade, which reads as a planet with its lights out, and the radius is held to twice
  the screen.

### Changed — four times faster, and less code doing it

- **An orbit is a fixed ellipse and was being solved from scratch sixty times a
  second.** Ten bodies × 150 points × six Newton iterations, every frame, to redraw
  exactly the same rings. They are worked out once now and only projected per frame;
  the Moon's ring is kept as offsets from the Earth.
- **The gravity well was summing eleven bodies at 3,312 lattice points every frame**
  — 36,000 distances. It is rebuilt at most twice a second, which is finer than the
  planets can move, and the grid is 36 × 60 rather than 46 × 72.
- The per-body dot budget came down from 22,000 to 12,000, which is still finer than
  the lattice a screen can show.
- Measured, median frame time on the same machine: **33 ms before, 8.3 ms after** —
  and now the same at the Earth, across the whole system, squashed, or with the
  camera nearly on the surface, where it used to be worst.

---

## 2026-09-14 — Real colour, real lights, real sunlight, and a panel that is a config

### Added

- **Every body is its own colour now, sampled per dot.** `data/planet-colours.json`
  carries a small map for each: the Earth at 224x112 in colour, its night lights at
  288x144 in single-byte brightness, everything else at 64x32. The Earth comes out
  with blue ocean, sand across the Sahara, green through the tropics and white ice -
  read off a real map rather than painted. Source: the Solar System Scope texture
  set, CC BY 4.0, heavily downsampled; `skills/dotworld/scripts/fetch_planet_colours.py`
  rebuilds it.
- **The night side is the real lights.** A dot over Tokyo is bright because Tokyo is
  bright. The `lights` parameter switches between that, the map's own 34,091
  population dots, and off.
- **Sunlight is the colour of 5772 K**, the Sun's effective temperature from NASA,
  put through Kim et al.'s fit of the Planckian locus and the sRGB matrix:
  `(255, 240, 234)` - white with the faintest warm cast. Every lit dot is multiplied
  by it. The Sun itself is drawn white for the same reason; its texture is used only
  for the mottling. The orange Sun everybody paints is what our air does on the way
  down.
- **`realism`, a parameter from 0 to 100%**, mixing the flat house colour against the
  body's own. It ships at 100.
- **The space controls are one small block of parameters** rather than a stack of
  shouting buttons: `look at`, `time`, `realism`, `lights`, `depth of field`,
  `bulge`, `scale`, `gravity well`, `orbits`, `hand spin`. Name on the left, the
  thing that changes it on the right. It reads like a config, which is what it is.

### Fixed

- **A flick spun a planet to break-up every time**, and a planet at break-up is a
  squashed lozenge - real physics, but it reads as a bug. The gearing is gentler now:
  a moderate flick lands around four times its own spin, which is a 5% bulge and
  clearly turning; a hard one reaches twenty. Break-up is still the ceiling, and
  `bulge` turns the drawn flattening down without touching the figures.
- **The night map lit the whole dark side like a lamp.** Of its 41,472 pixels, 38,433
  sit in one low bucket - airglow over empty ground, not towns - and the brightest
  city only reaches 150 of 255. Stretching from that floor to that peak is what turns
  a brown smear back into cities.
- **Ten thousand colours a frame cost more than drawing them.** The first pass built
  a colour string per dot. It is quantised to sixteen levels a channel, packed into
  an integer and cached, which is invisible on a two-pixel dot.

---

## 2026-09-14 — Grab a planet and spin it

### Added

- **Drag a body and it turns under your hand; let go and it keeps going.** There is
  nothing out there to rub against, so angular momentum is conserved and the spin
  simply continues - on the same clock as everything else, so at "a day a second" it
  whips round and paused it holds still. Drag the empty sky instead and you still
  turn the camera.
- **What the panel says once you have spun something:** the new day length, the
  angular momentum in kg·m²/s and as a multiple of its own, the energy you added in
  joules, how flat the spin makes it, how close that is to break-up, and **how long
  the spin lasts** - the change in day length divided by the only measured brake
  there is, the tide, at the Earth's own +1.72 ms per century. A good flick comes out
  at billions of years, which is the honest answer to "does it keep spinning".
- **It goes fat as it spins.** The drawn body is squashed along its axis by the
  Maclaurin flattening, 1.25 ω²r³/GM - which gives the real Earth 0.0043 against its
  measured 0.0034 - so spinning it up visibly bulges it, and seen pole-on it stays a
  circle, as an oblate body does. The city lights and the Moon's near-side marker are
  placed on that same shape; the first build left them floating off a squashed Earth.
- **The spin is held at break-up.** Past ω²r = GM/r² the equator is in orbit and the
  body comes apart: one turn every 1 h 24 m for the Earth. A hand is far too strong
  for a planet - a normal flick asks for ten thousand times its own spin - so that
  limit is where it stops. `GIVE THE SPINS BACK` resets, which nothing in space would.
- Every body now turns at its own rate rather than sitting still: Jupiter goes round
  in 9 h 55 m, Venus backwards in 5,832 h.

---

## 2026-09-14 — The spin, with the physics on the panel

### Added

- **THE SPIN**, a block of the space panel that works the Earth's rotation out live
  rather than quoting it. It turns once in **23 h 56 m 04.2 s** but a day lasts
  24 h 00 m, and the panel says why: by the time it has turned all the way round it
  has moved along its orbit, so it has to turn a little further to bring the Sun
  back overhead. Then, live: how far it has turned since midnight (of 360.9856°,
  a solar day's worth of turning); **where the Sun is overhead**, longitude from the
  clock and latitude from the tilt — 3.1° N today, the same declination that gives
  us summer; the **ground speed at the equator, 1,674 km/h**, and under wherever the
  camera is (cos of the latitude); how much of the pull the spin cancels there —
  **0.0339 m/s², 0.34%**, at the equator and nothing at the poles; what you would
  weigh standing on that spot; how much the spin has squashed the planet, **21.4 km
  fatter than tall, 1/298**; and that the day is lengthening by **+1.72 ms a
  century** while the Moon backs off **3.8 cm a year**, which is the same handshake.
- Every body's own NASA sheet is fetched now, not just the summary table, so the
  spin rows work for Mars and Jupiter too — and Venus turns out to have ground that
  moves at 6.5 km/h, slower than walking.

### Fixed

- **The summary table rounds, and it mattered.** It prints the Earth's year as 365.2
  days and its spin as 23.9 hours. Over the twenty-six years since J2000 a year
  rounded like that is a day and a half of drift — a degree and a half of sky — and
  the rounded spin printed a sidereal day of 23 h 54 m, two minutes out. The
  per-body sheets carry 365.256 and 23.9345, and using them moved the computed
  solar declination from 2.5° to 3.1° against a real 3.2°.
- **A planet's sheet also lists its moons, with the same row labels.** Mars's sheet
  handed over Phobos's 0.319-day orbit as the Martian year. A precise figure is now
  kept only when it agrees with the rounded one from the summary table to within 2%,
  which is what a second source is for.

---

## 2026-09-14 — Space, made honest: real proportions, real shading, real occlusion

Daniel looked at the first build and said the fades, the Moon and the dot scale were
wrong or in the wrong place, and that the lighting should be deeper and truer to the
colours already on screen. All four were fair.

### Fixed

- **Things behind other things were visible through them.** Nothing out here is
  depth-tested - every dot is added to the frame like light - so the Moon shone
  straight through the Earth. Bodies are now drawn furthest first, each punching its
  own silhouette in black before its dots go down, and a name disappears with the
  body it names. The Moon behind the Earth is gone now, label and all.
- **The blur was on the wrong things.** A lens focused close really does soften its
  subject's own near edge, but on screen that reads as a mistake: the front of the
  Earth went soft while its edge stayed sharp. The blur circle now has a flat middle
  - nothing within a bit over half the focal distance blurs at all - so whatever you
  are looking at is sharp all over and only plainly distant things spread and fade.
- **`DOT SCALE` did nothing out here.** The space lattice is the map's own pitch now,
  the same slider, so the dots on a planet match the dots on the ground. The
  area-based budget is only a floor under it.
- **The lighting was one flat colour at varying opacity.** Each body now has an
  eight-step ramp built from the colour it already has: nearly black where the Sun
  does not reach, its own colour where it is fully lit, and a push toward white at
  the top, because sunlight is white and a flat lit face reads as paint. The
  terminator wraps a little on the worlds that have air - most on Venus - and not at
  all on the airless ones.

### Changed

- **True scale is the default now.** Squashed distances were the reason the Sun
  loomed over an Earth view and Venus sat next to the Moon: once the orbits are
  crushed to fit a screen, no size mapping can put both right. At true scale, from
  three Earth radii up, the Sun is 0.531° across and the Moon is 0.518° - which is
  why eclipses work - Venus is 0.010° and Jupiter 0.009°. `SQUASHED SCALE` keeps the
  old diagram, and the panel says which one is on and that the squashed one is a
  diagram, not the sky.
- The wheel moves in bigger steps, since true scale spans a planet's surface to
  Neptune; distant planets are drawn as points of light rather than fading out; and
  labels that would land on each other are dropped rather than stacked.
- A moon keeps its true distance until the camera is 200 radii out instead of 30, so
  the Moon stops sliding inward while you are anywhere near the Earth.
- The Moon's near-side marker is lit like the ground it sits on; it used to glow on
  the dark half like a spacecraft.

---

## 2026-09-14 — Leave the Earth: gravity, depth of field, and the whole solar system

### Added

- **`LEAVE EARTH`.** The camera steps off the map to three Earth radii up and the
  rest of the solar system comes with it: the Sun, all eight planets, the Moon and
  Pluto, every one of them drawn as dots on its own canvas. Click a body or pick
  it from `LOOKING AT` to fly to it; drag turns the camera, the wheel changes how
  far away it is.
- **Gravity as a number, not a mood.** The panel sums GM/r² from every body at
  wherever the camera is: 9.8 m/s² on the Earth's surface, 2.45 two radii out,
  1.09 at three, 1.1 × 10⁻⁴ out by Jupiter's orbit. It also prints what fraction
  of that comes from which body, the speed needed to stay in orbit there, and the
  speed needed to leave. G is CODATA's 6.674 30 × 10⁻¹¹ and the masses are NASA's,
  so G·M⊕/R⊕² lands on 9.82 - a check that the fact sheet was read correctly.
- **Gravity as a shape.** A lattice on the plane of the planets, pushed down by
  the potential and squashed logarithmically so the Sun's pit and a planet's
  dimple fit in one picture. The interface says what it is: the number given a
  shape, not a picture of bent space.
- **Depth of field.** A thin-lens blur circle: the further a dot is off the plane
  you are looking at, the bigger and fainter it goes. On a flat screen with no
  parallax it is the only cue that says which of two points of light is further
  away. `DEPTH OF FIELD 0` turns it off.
- **The Earth turning, and made of its own cities.** The Sun stands over the
  longitude that matches the hour, so at noon UTC Greenwich faces it, and the
  terminator is real. The night side is the 34,091 cities the map already carries,
  lit in the same population colours - city lights from orbit.
- **The Moon, and why it never turns away.** Real distance, real 27.3-day period,
  with the middle of its near side marked: it keeps one face toward us because it
  turns exactly once per orbit, and an unmarked grey ball cannot show that.
- **Saturn has rings**, drawn as dots in its own tilted equatorial plane.
- **The year bar drives the sky.** Set 20 July 1969 and the Earth and the Moon
  stand where Apollo 11 found them. `TIME` runs from paused to a year a second.
- **`data/solar-system.json`**, 5,104 bytes, built by
  `skills/dotworld/scripts/fetch_solar_system.py` from the NASA NSSDC planetary
  fact sheet (public domain) and English Wikipedia infoboxes (CC BY-SA 4.0).

### Why it looks the way it does

- **Square root, not logarithm.** A log fits Mercury and Neptune on one screen and
  then crushes them together: in log units the whole run from Mercury to Neptune is
  shorter than a planet is wide, and the first build had a Venus as wide as the gap
  to the Earth. A square root keeps the order and the spread - Mercury 62 units,
  Earth 100, Jupiter 228, Neptune 548 - with a flatter curve for sizes so the Sun
  stays biggest without swallowing the inner orbits.
- **Close in, the squashing switches off.** Inside about 30 radii of whatever you
  are looking at, distances are exact: three radii up looks like three radii up and
  the Moon sits at the sixty Earth radii it really keeps. Back off and the exponent
  eases to 0.55 and pulls a moon inward, because at true proportions the Moon's
  orbit is wider than the Earth's own squashed orbit. `TRUE SCALE` turns the lot
  off and shows why nobody draws it that way.
- **Brightness rides the dot's size**, the same halftone rule the map uses. The
  first build varied only alpha, and a planet filling the screen came out as an
  empty screen.

### Honest limits

- Two-body Kepler orbits: good to a fraction of a degree from 1800 to 2050, and
  drifting outside that. Nothing perturbs anything, so the Moon is the roughest -
  its node really does come round in 18.61 years and here it does not move at all.
  Its phase is anchored to a cited new moon and a mean synodic month, which is a
  date without a time, so the phase can be half a day out.
- The day/night line ignores the equation of time: a quarter of an hour at worst,
  about 4° of longitude.
- This is a picture to think with. For real positions use JPL Horizons.

### Fixed on the way

- A body filling the screen asked for a lattice millions of dots wide and threw
  `RangeError: Invalid array length`. The lattice is now only walked where it can
  land on screen, and its pitch opens up as the body grows, so a planet you are
  standing on costs the same few thousand dots as one the size of a coin.
- A million kilometres is 10⁹ metres, not 10⁶. The readout called a camera three
  Earth radii up "20.1 M KM", which is past the Moon.

---

## 2026-09-14 — Coming back from a past year says the right year again

### Fixed

- **The source line kept the year you left.** Drag the bar to 1969 and the counter
  correctly reads `WORLD BANK 1969`; drag it back to now and the counter starts
  ticking again, but the line under it still said 1969 - a live 2026 figure
  labelled with a year from half a century ago. Only the "not now" branch wrote
  that label, so nothing ever wrote it back. The live branch sets it too now,
  `WORLD BANK <estimate year>`, or `CACHED <year>` when the World Bank call failed
  and the baked-in baseline is in use. Seen on the live site while looking at the
  map with Daniel, not in a test.

---

## 2026-09-14 — A story line over the dials, and the whole story behind it

### Added

- **The headline of the year, above the zoom bar.** Move the year and the line
  changes: *20 JUL 1969 — Apollo 11*. It comes from Wikidata — what it classes as an
  event, ranked by how many Wikipedia editions carry it, which is Wikipedia's
  editors' judgement of importance rather than mine.
- **Month and day** beside the year. Setting them picks whichever event of that year
  falls closest to the date you asked for. A Wikidata date of 1 January usually means
  "some time that year", so it is shown as a year rather than as New Year's Day.
- **Click the line for the whole story**: fifteen chapters from the Big Bang to
  1500 — first stars, the Sun, Earth, the Moon, the first life, the oxygen
  catastrophe, the Cambrian, the Permian extinction, the asteroid, the split from
  chimpanzees, Homo sapiens, farming, writing — each a rounded consensus figure
  **linked to its own article**, so nobody has to take my word for a number. Then the
  events of the year the bar is on, each linked to its Wikidata item.
- `data/events.json`, built by `skills/dotworld/scripts/fetch_events.py`.

### Notes

- Coverage is partial and the interface says so: an event Wikidata has not typed as
  an event will not appear however famous it was.
- **Apollo 11 carries neither `P585` nor `P580`** — a spaceflight stores its launch
  under `P619`. The first build produced a 1969 with no Moon landing in it and
  nothing complained; the query asks for all three properties now, which also brings
  in Sputnik, Vostok 1 and the Shuttle.
- What it took: the textbook filter (`P31/P279*` from "occurrence") times out at 60 s
  on a single decade, so the class list is flat — and it was **derived** by asking
  Wikidata what Apollo 11 and the Cuban Missile Crisis actually are, after a
  hand-written list of QIDs returned a person and a time zone.

---

## 2026-09-14 — A year bar: 1500 to 2050

### Added

- **The map can show another year.** A second bar at the bottom, from **1500 to
  2050**, and two different things happen on the way.
- **Population, 1960 to 2050.** Every city is scaled by **its own country's**
  trajectory, not by one world figure — between 1960 and 2050 France goes 47 M to
  70 M, Japan 93 M to 105 M *after peaking*, Nigeria 45 M to 359 M, and a world
  average would erase all three. Estimates to 2025, projections after, and the
  readout says which. The live counter switches to that year's figure and stops
  pretending to tick.
- **Borders, 1500 to 1994**, from the Historical Basemaps project: the map draws the
  borders of the nearest era at or before the year you chose. They are fetched from
  the project's own CDN when you ask for them and never copied into this repo — the
  dataset is GPL-3.0 and this code is MIT.
- **What the map refuses to show in an old year**: nothing before 1960 has
  population here, so the city dots come off rather than being invented; and below
  1995 the capitals and their monuments come off too, because the ones on file are
  today's. Berlin's monuments over the borders of 1789 would be a lie told
  confidently.
- `data/population-by-year.json`: 243 countries x 91 years, 117 KB, fetched the
  first time the year bar moves.

### Notes

- Historical borders are drawn over **today's** coastlines and roads: the tiles only
  know now. What changes is who claimed what.

---

## 2026-09-14 — Scroll down for the rest of it

### Added

- **The readouts column scrolls, with a topic strip that stays put at the top**:
  View, Live, World, Cities, Capitals, Monuments, Colours. There is more to say
  than fits a screen, so jumping beats hunting.
- **THE WORLD, ON AVERAGE** — density per square kilometre of land, life expectancy,
  children per woman, GDP per person, the age split (under 15 / 15–64 / 65 and over)
  and town against country. Six more indicators from World Bank Open Data, each
  carrying the year it is from: "life expectancy" with no year is not a fact.
- **CITIES BY SIZE** — how all 34,091 cities fall across the eight bands, drawn in
  the band colours, with the count, the **median** city and the mean. The median is
  the middle city rather than the average, because a handful of megacities pull the
  mean well above where most people actually live.
- **THE 195 CAPITALS** — biggest, smallest, how many are over a million, the median,
  and a chart of **which hour of the world each capital keeps**, which moves with
  daylight saving.
- **BEST KNOWN PLACES** — the ten monuments with the widest Wikipedia coverage of
  all 195 capitals, plus how many have an OpenStreetMap outline.

### Notes

- Every chart is computed in the page from files the map already holds — no second
  fetch, no server doing sums, nothing new on the wire.

---

## 2026-09-14 — Colour for everything the tiles know, and a dial for how much

### Added

- **Land has categories now too.** Wood and forest `darkgreen`, scrub `olivedrab`,
  grass and meadow `darkolivegreen`, park `forestgreen`, farmland `olive`, wetland
  `darkseagreen`, sand `darkkhaki`, ice and glacier `lightsteelblue`. What people
  build on it gets the purple and brown families, which nothing else uses:
  residential `dimgray`, commercial `rosybrown`, industrial `sienna`, military
  `indigo`, cemetery `rebeccapurple`, hospital `orchid`, school and university
  `mediumpurple`, stadium `purple`, quarry and pier `tan`, railway `thistle`.
  All dim: these are the widest areas on the map and area is what costs.
- **A COLOURS dial**, 0 to 6. Each step hands one group its own colours — water,
  population, monuments, land, built land, transport — and the readout says how many
  colours are live, from **one** (everything in the dot colour) to **43**. Turning it
  down is not only quieter: fewer hues is fewer lit subpixels.
- **An information meter** in the readouts: how many places are on screen and how
  many people those dots stand for, on a bar that runs logarithmically to a
  **milliard**. A world view is billions, a village is thousands, and nothing linear
  shows both. Tiles hand the same city back once per tile it touches, so the index
  each dot carries is what stops it being counted twice.

### Notes

- Roads stay white and grey on purpose. They are what makes a city legible at street
  zoom, and a hue there costs power without adding anything you did not already know.

---

## 2026-09-14 — Every kind of water gets its own blue

### Changed

- **Water was one flat grey; it is nine categories now**, each a named CSS blue:
  `midnightblue` ocean, `darkslateblue` lake, `steelblue` pond, `cadetblue` river
  and canal, `lightslategray` stream, `darkslategray` drain and ditch, `slategray`
  dock, `royalblue` swimming pool. The tiles carried all of this already — the
  `water` layer has a class per body and `waterway` has one per channel — the map
  simply painted them the same colour.
- Anything the tiles mark as **intermittent** — a river that dries up for part of
  the year — is drawn faint.
- **Brightness follows how much screen each one covers.** The ocean is most of a
  world view, so it is held to a third of `midnightblue`: drawn, that is luma 0.06,
  the same as the grey it replaces. A swimming pool is four pixels and gets full
  strength.
- Honest cost: the sea is no brighter, but blue is the expensive subpixel, so the
  power proxy over open water roughly doubles (0.06 to 0.12). Water is worth it;
  nothing else that covers this much screen would be.

---

## 2026-09-14 — Colours that mean one thing, and have a name

### Changed

- **Population is banded, and every band is a CSS named colour.** Eight of them:
  `darkred` under 25 K, `firebrick` to 50 K, `crimson` to 100 K, `orangered` to
  250 K, `chocolate` to 500 K, `darkorange` to 1 M, `orange` to 5 M, `gold` above.
  A colour on the map is now a fact you can look up in the W3C list — not a shade
  from the middle of a gradient. The legend lists every band with its name and
  range, and is written from the same table the map draws from.
- **One ramp, one meaning.** Cities and capitals share the population colours; a
  capital is told apart by a **white ring**, not by a hue. Hue could not do the job:
  green capitals against the warm city ramp measure **deltaE 0.6** apart under
  deuteranopia — no difference at all for about one man in twelve. Warm against
  turquoise measures 19.2, which is why monuments keep a hue of their own.
- **The country highlight is `silver` now**, not `#ffeda0` — which was the old
  ramp's top step, so a lit country read as a 20-million city.
- **The ramp stops at `gold` rather than white.** Measured against the screen's own
  subpixels, near-white costs about 0.90 of full power against gold's 0.48, and the
  top band is the one every big city lights.

### Added

- **Click anything for what it is**: a city gives its name, exact population, band
  and colour name; a capital adds its country and how many seats it has; a monument
  gives how many Wikipedia editions cover it and where it ranks in its capital.
- City names ship in their **own file, joined by index**, and are fetched only when
  someone clicks a city — 593 KB that a visit which never clicks never pays for.
  The map needs no names to draw.

---

## 2026-09-14 — Monuments drawn as edges, not as solids

### Changed

- **A monument is now its contour**: a bright line round the foot of the building
  and, in 3D, another round its roofline, leaving the building itself to the
  lattice. It replaces the solid cyan fill and the solid cyan volume.
- In 3D both contours are **ribbons of thin walls**, one quad per edge of the
  outline, three metres wide: extruded from the ground they fence the foot,
  extruded at roof height they fence the roofline. Two dead ends came first.
  MapLibre 6.9 has no elevated lines at all — `line-z-offset` is not in this build —
  so a line cannot be put at roof height; and an extruded slab of the footprint
  shows its cap, which fills the building in again the moment the camera tilts. A
  ribbon has no cap. Heights are OpenStreetMap's where the building has one (110 of
  the 355), 25 m otherwise.

---

## 2026-09-14 — Shift-drag to turn and tilt

### Added

- **Hold shift and drag** to turn and tilt, alongside right-drag. MapLibre has no
  option for it — shift-drag is its box zoom — so the box-zoom handler is off and
  drag-pan is suspended for the length of the gesture, or the map would pan
  underneath the turn. Bearing and pitch are set per mouse-move rather than eased,
  so the camera follows the hand exactly, and the TILT and BEARING sliders follow
  the camera as always.
- It turns the way right-drag turns: like a wheel, not a slider. MapLibre's own
  handler negates the rotation above the screen centre, so pulling right along the
  bottom spins the map one way and along the top the other; the sign is taken where
  the drag starts, so it stays steady if you cross the middle mid-turn. Tilt is
  0.5° per pixel, the same as MapLibre's.

---

## 2026-09-14 — A clock, one switch for everything, and a tidier panel

### Added

- **The time where you are**, in the statistics panel: the clock, the UTC offset,
  and how many hours you are **ahead of** the world's first capital and **behind**
  its last. Pick a country and the clock becomes that capital's, with how far ahead
  of or behind you it is.
- Every capital now carries its **IANA time zone** (`Europe/Paris`, not `+02:00`),
  taken from the nearest GeoNames city in the same country — so the browser applies
  daylight saving, and Kathmandu shows +05:45 rather than a rounded hour. Your own
  zone comes from the browser and needs no permission.
- The two ends of the day are worked out from the capitals themselves rather than
  from UTC-12 and UTC+14: they are real places on this map, and the pair moves with
  daylight saving, so it is recomputed every quarter of an hour.
- **ALL DATA**, one switch that turns every layer on or off instead of four.

### Changed

- **Montpellier's monument categories are out of the panel.** They were a leftover
  from when the map was one city; the layer still colours them when you are there.

---

## 2026-09-14 — A dot scale that goes all the way down

### Changed

- **DOT SCALE now starts at 0.01, not 0.4**, in steps of 0.01. At 0.05 the lattice
  is about two device pixels across at world zoom; below that the dots are finer
  than a screen pixel and the map goes continuous, which is as far as any screen can
  take it.

### Fixed

- **A fine lattice used to go black.** The minimum-radius cull was a fixed 0.35
  device pixels, so once the pitch came near a pixel the largest possible dot was
  already under the threshold and every single one was culled. The cull follows the
  pitch now — `min(0.35, step * 0.22)` in the shader, the same rule on the CPU path.

### Notes

- The shader does not care how fine the lattice is: it costs one texture read per
  *pixel*, not per dot. The other two paths do, so they have floors it does not
  need — the Canvas2D fallback draws one arc per cell (millions a frame below two
  device pixels), and the lit-area count builds a cell grid, which under one device
  pixel is a canvas of hundreds of millions of cells that cannot be allocated. The
  HUD reports the pitch each path actually drew.

---

## 2026-09-14 — A light that runs round the border

### Added

- **Picking a country now draws its border.** The map frames the country, then a
  light runs round the outline and leaves it lit behind it — the whole border in
  **3.2 seconds**, however big the country is. Islands trace alongside the mainland
  rather than queueing after them, and the light fades once the outline is complete.
- **Click a capital on the map to pick its country**, instead of going through the
  list. The pointer changes over a capital, so you can tell it is clickable.

### Changed

- **A country is framed from its own outline now, not from a geocoder's box.**
  Nominatim answers with everything a country owns: asking for Portugal framed
  900 km of Atlantic because of the Azores, and France's box spans the planet
  because of French Polynesia. The mainland is the biggest ring of the outline the
  map already holds — rings that wrap the antimeridian are skipped rather than
  fitted. One less network call, too.

### Notes

- The light is a `line-gradient` travelling along the outline, not a crawling dash:
  a bright head, the lit border behind it, nothing ahead of it yet. It needs
  `lineMetrics: true` on the source — without that `line-progress` does not exist
  and the gradient is ignored silently.
- Each ring is its own feature, so progress runs 0 to 1 along every piece of a
  country at once. The duration is fixed rather than the speed, so Russia and
  Monaco take the same 3.2 seconds.
- It starts on `moveend`. Drawn during the flight, it is a smear.

---

## 2026-09-14 — The whole world's population, and a button that finds you

### Changed

- **The population layer is the world now, not France.** Every city over 15,000
  people — **34,091 of them**, Shanghai (24.9 M) down to 15,001 — from GeoNames,
  which publishes the lot as one maintained file. Wikidata, which gave France its
  644 communes, does not scale to this: the same query worldwide times out, and its
  population statements are uneven from country to country. `MIN POPULATION` now
  runs 15 K to 25 M.
- The colour stops are spaced by a constant ratio (15k, 44k, 128k, 373k, 1.09M,
  3.18M, 9.3M, 25M) rather than evenly. City sizes cover three orders of magnitude,
  and even spacing paints everything under a million the same dark red.
- The file ships as `[lon, lat, pop]` triples, not GeoJSON: the layer draws circles
  and never reads a name, and GeoJSON's scaffolding costs 5.1 MB against **762 KB**
  (303 KB over the wire) for the same cities. The app builds the GeoJSON in one pass
  at load.
- `data/fr-population.geojson` is gone from the working tree; it stays in the
  history, and `fetch_fr_population.py` still documents the Wikidata approach.

### Added

- **WHERE AM I**, under the zoom bar at the bottom centre. It marks where you are
  and flies there, and the button names the town it found so you can see it worked.
  Your fix is rounded to 2 decimals — about a kilometre — **before** anything is
  done with it: that rounded point is what the map flies to, what the marker is
  drawn from and what the geocoder is asked about, so nothing sharper than a
  kilometre exists in the page, in the URL hash or in any request.

---

## 2026-09-13 — Monuments drawn as the buildings they are

### Added

- **Every capital monument now has its own outline**, taken from OpenStreetMap:
  from z12.5 the cyan circle gives way to the building's footprint, so the lattice
  fills the Colosseum's ellipse, the Capitol's wings and the Forbidden City's
  rectangles instead of a blob. **355 of the 491 monuments (72%), across 162
  capitals**, 220 KB — 44 KB over the wire — fetched only once you are close enough
  for an outline to be more than a speck. The rest keep the marker; OSM has no
  wikidata-tagged building near their point.
- `skills/dotworld/scripts/fetch_monument_shapes.py` builds it through Overpass.
- **In 3D the monument rises as a cyan volume.** A flat fill at ground level is
  hidden under the tiles' own extruded building however late it is drawn - the
  extrusion writes depth - so the monument has to be a volume too. Heights are
  OpenStreetMap's where the building has one (110 of the 355), 25 m otherwise,
  which clears what the tiles guess: they give the Colosseum a 1 m extrusion.

### Notes

- The vector tiles cannot do this: their building layer carries render heights and
  no name or id, so there is no way to ask them for one particular building.
- Matched by position — every OSM way or relation with a `wikidata` tag within
  150 m, nearest centroid inside 200 m wins — so two monuments on the same street
  cannot swap outlines.
- A relation's outer ways come back from Overpass unordered and sometimes reversed;
  they are joined end to end into rings here, or the Louvre draws as a scribble.
- Simplified at ~2 m, which is far under one dot of the lattice even at street
  zoom: Westminster Abbey goes from 547 points to 108, the file from 400 KB to 220.

---

## 2026-09-13 — A zoom bar you can throw

### Added

- **A zoom bar across the bottom centre.** Drag it and the map follows the handle
  frame by frame, so a street becomes the whole globe in one gesture. It reads the
  map's own minimum and maximum zoom rather than hard-coded numbers, shows the
  level to two decimals, stops ORBIT like every other camera control, and slides
  away with **HIDE PANELS**. World, country, city and street are marked at the
  zoom each word actually means: the scale runs -2 to 22, so spacing them evenly
  would have put "city" at z14, which is a rooftop.
- Dragging is a **scrub, not a flight**: each input jumps the camera with no
  animation. Easing every step would queue hundreds of eased moves and the lattice
  would arrive late; jumping lets it redraw as fast as it can.

---

## 2026-09-13 — The best-known monument of every capital

### Added

- **Capital monuments.** Next to each capital's name, what that capital is known
  for: its three best-known places, ranked by how many Wikipedia editions and
  sister projects cover them. They have a colour of their own — cyan, the only hue
  left that stays clear of the population ramp, the country glow and all five
  Montpellier categories (worst colour-vision deltaE 13.7, measured with the same
  checker as the Montpellier palette, not chosen by eye). The best-known one shows
  from the world view, the other two and all the names from z6 and z8, and
  **CAPITAL MONUMENTS** in settings turns the lot off.
- **`data/capital-monuments.geojson`**, built by
  `skills/dotworld/scripts/fetch_capital_monuments.py`: one Wikidata query per
  capital, monuments within 25 km ranked by sitelinks. **491 places for 192 of the
  195 capitals** (105 KB). Three have none: Ciudad de la Paz has nothing notable
  nearby in Wikidata, Brazzaville's only candidate is nearer to Kinshasa, and
  Luxembourg's response was truncated on every attempt through this proxy.
  Spot checks: Paris → Eiffel Tower, Louvre, Notre-Dame; Rome → Colosseum,
  Pantheon, Roman Forum; Cairo → Great Pyramid of Giza; Washington → the White
  House, the Library of Congress, the Capitol; East Jerusalem → Al-Aqsa Mosque,
  Dome of the Rock.

### Fixed

- **One capital was drawn as "Q36262".** St. John's, the capital of Antigua and
  Barbuda, no longer has an English label on Wikidata — the name moved to the
  multilingual `mul` code — and a label service asked for `"en"` alone hands back
  the bare item id. The query now asks for `"en,mul,en-gb,fr,es"`.

### What it took to get a list worth showing

- Walking `wdt:P31/wdt:P279*` from "architectural structure" is the obvious way to
  catch an amphitheatre, a city gate and a mausoleum. It returns 504 on Paris, Rome
  and Cairo. Types are filtered here instead, where it is free.
- Keyword matching on type labels has to respect word boundaries: "arch" inside
  *constitutional monarchy* put Antigua and Barbuda itself on the map, and "villa"
  inside *village* added a hamlet called Bolans.
- "historical country" contains "historic", so Rome first returned the Roman Empire,
  Tokyo the Tokugawa shogunate and London the Kingdom of Great Britain.
- The Colosseum is typed `stadium` as well as `Roman amphitheatre`. Blocking
  stadiums to keep football grounds out buried Rome's most-linked monument.
- Vatican City is 4 km from Rome, Brazzaville 5 km from Kinshasa: each monument
  goes to the capital it is nearest to, so nothing is drawn twice.

---

## 2026-09-13 — Find any of the 195 countries and light it up

### Added

- **A country picker, in the statistics panel under COUNTRIES.** All 195 in one
  list; type a few letters to jump to one. Choosing a country lights its border on
  the map, frames it, keeps its capital's name on screen even when labels are
  crowded or switched off, and reads out that capital's population beside the
  country's own, from World Bank Open Data. Choosing the empty entry puts
  everything back.
- **ISO 3166-1 alpha-2 codes in the capitals file** (Wikidata P297). That is the
  code the tiles' boundary layer carries in `adm0_l`/`adm0_r`, so it is what makes
  a single country's border light up. One UN member carries no code of its own:
  the member is the *Kingdom of Denmark*, while DK belongs to *Denmark*, its
  European part — filled in by the script and documented there.
- **The country's own outline**, from Natural Earth's 1:50m set, lit over the
  lattice. The tiles have no country polygons, and their boundary lines only name
  the countries either side from zoom 5 up — checked by decoding tiles — so at the
  zoom where you look at a whole country there was nothing to light. The outline
  file is 780 KB (225 KB over the wire) and is fetched only when someone picks a
  country. It fades out as you zoom past 6, where the tiles' own sharper border
  takes over.
- **Every earlier version is now tagged on GitHub**, `v0.1.0` (2026-09-09) through
  `v0.4.0`, with `v0.5.0-beta` published as a release.

### Notes

- Framing costs one Nominatim lookup per country, cached for the session. A country
  that crosses the antimeridian — Fiji, Kiribati, Russia — comes back with a box
  spanning the whole planet, so those fall back to flying to the capital.
- **ILLUMINATE MY COUNTRY** and the picker now agree: finding your own country
  also sets the picker, so the panel says what the map is showing.

---

## 2026-09-11 — A new home, a skill, and corrections to what the site claimed

### Fixed

- **The capitals list included Taiwan and left out Vatican City.** The Wikidata
  query matched any "member of the United Nations" statement, including historical
  ones, so it picked up Taiwan — whose UN seat passed to the People's Republic of
  China in 1971 — and it missed Vatican City. The total still came to 195, which is
  why the count never revealed it. The query now requires a membership statement
  with no end date *and* a current, undissolved sovereign state, and the result was
  checked against Wikidata's current membership: the 193 members plus the two
  observer states, Vatican City and Palestine.
- **Seven states have more than one seat, not nine.** Jordan and Syria each return
  the same capital twice as separate Wikidata items; that is not a second seat.
  `seats` now counts distinct capitals.
- **The map's credit left out OpenMapTiles.** The on-map attribution now uses
  OpenFreeMap's own required wording, read from its TileJSON: "OpenFreeMap
  © OpenMapTiles Data from © OpenStreetMap contributors". OpenMapTiles is also
  credited in the in-app panel, CREDITS.md and the README.
- **MapLibre's full BSD-3-Clause licence now ships with the vendored bundles**
  (`vendor/LICENSE-maplibre-gl.txt`). The bundles carried only a one-line header
  and a link.

### Added

- **`skills/dotworld/`** — a Claude Code skill capturing how DotWorld was built: the
  two ways to get a MapLibre frame into a dot pass and what each costs, the shader,
  the measured numbers and the traps that produced wrong ones, the data queries, the
  colour rules, and publishing and credits. Install with `sh install.sh`.
  It was tested before it shipped: an agent given a DotWorld task without it got the
  basics right but repeated the black-background bug, quoted frame times it had not
  measured, and missed the crash, lifecycle and licensing traps. The skill was
  written around those gaps, then the task was run again by a fresh agent with it.
- **`skills/dotworld/scripts/`**, run against the live sources on 2026-09-11:
  - `fetch_capitals.py` rebuilt the corrected capitals file.
  - `fetch_fr_population.py` returned 645 communes: the shipped 644 plus Quimper,
    which the earlier run did not return (not investigated). No population changed.
  - `rank_monuments.py` ranks a city's monuments; see *Not changed* below.
  All three retry. The France query asks for CSV, because its JSON result was cut
  off at exactly 262,144 bytes on every attempt through a proxy.
- **`archive/`** — the first Canvas2D prototype, its screenshots, and the first skill.

### Changed

- The working copy moved to a new home with its full history. The GitHub
  repository and the live URL are unchanged.

### Not changed, on purpose

- **Montpellier's monuments.** Ranked with one consistent measure — Wikipedia
  language editions for every candidate, inside the city's own boundary — the top 10
  swaps the promenade du Peyrou (4) for the Mosquée Avicenne (6). The shipped list
  counted all sitelinks for OpenStreetMap-sourced items but Wikipedia-only links for
  Wikidata items. Which list to show is an editorial choice, so the site keeps its
  current list until that is decided.

---

## 2026-09-11 — The lattice moves to the GPU; capitals get populations

### Improved

- **The dot lattice is now a WebGL2 fragment shader.** Each cell samples the mip
  level of the map frame whose texels are one cell wide (that mip *is* the cell's
  average) and turns its brightness into a dot. Measured on an M2 Pro:

  | Renderer | Street zoom, real content | Notes |
  |---|---|---|
  | Canvas2D arc paths (before) | **18.3 ms** / frame | ~30 ms with 180k dots — over the 16.7 ms budget for 60 fps |
  | CPU pixel stamping (tried, rejected) | 50–100 ms | clearing and pushing a full-frame buffer is itself expensive |
  | WebGL2 shader (now) | **0.1–0.5 ms** / frame | same cost however many dots are on screen |

- **Canvas2D kept as a fallback** for browsers without WebGL2. Add `?renderer=cpu`
  to the URL to force it and compare.
- **Dot count and lit area are now counted only when the map is at rest.**
  Counting means reading the frame back off the GPU, and that readback measured
  anywhere from ~1 ms to ~55 ms depending on what the GPU was still doing. Doing
  it on a timer while moving produced a hitch a few times a second. Zoom, dot
  pitch and frame time still update live.
- **FRAME readout** in the HUD: median main-thread cost of the last 30 redraws.
- **`window.__bench(n)`** in the console times the redraw stage by stage
  (draw, readback, count loop, labels), forcing the GPU to finish each frame.
- **Capitals show their population** beside the name. Marker colour *and* size
  carry it, on a log scale from 1 K to 22 M using the same reversed YlOrRd as
  France — capitals run from 747 people (Yaren, Nauru) to 21.9 M (Beijing), so a
  linear ramp would have painted almost all of them the same red. The number is
  set in neutral ink; only the marker carries the colour. New legend entry.
- **Labels have their own canvas layer** above the lattice.

### Fixed

- **Crash when the capitals data arrived before the map style.**
  `map.getProjection()` is `undefined` until the style loads, and the code read
  `.type` straight off it. The local capitals file often wins that race.
- **One exception in the draw loop stopped rendering for good.** The loop re-armed
  `requestAnimationFrame` *after* drawing, so a throw never re-armed it. It now
  re-arms first.
- The `file://` error message pointed at an old folder path.

### Data

- Capital populations: Wikidata `P1082`. Some countries' figure is the city
  proper, others the whole municipality (Beijing is the municipality), so compare
  loosely — the legend says so. Ngerulmud (Palau) has no figure.

### Not yet verified

- Smoothness was measured per frame, not watched in motion: the preview pane used
  during development stayed hidden, which throttles animation.

---

## 2026-09-10 — Credits, licence, launch

- **Launched on GitHub Pages** at https://fablab503-collab.github.io/openstreetmap-dot/.
  Added `.nojekyll` so Pages serves the files as they are.
- **CREDITS.md**: every data source, library, typeface and colour scheme with its
  licence, plus links to support the upstream projects.
- **LICENSE**: MIT for the original code only, stating explicitly that it cannot
  relicense the ODbL map data, CC BY statistics, CC0 datasets or bundled libraries.
- **In-app *credits & disclaimer* panel**: a fun personal experiment built with
  Claude, not affiliated with or endorsed by any upstream project, and taking
  nothing away from them.

---

## 2026-09-10 — DotWorld

Renamed from OpenStreetMap Dot, and most of the app arrived here.

### Added

- **Globe projection** (`WORLD: ROUND` / `PLATE`), **WHOLE EARTH**, **ORBIT**,
  **TILT**, **BEARING**, **RESET NORTH**, **3D DOT VIEW**.
- **SUNLIGHT** with a direction dial — lit building faces become larger dots.
- **16 dot colours**, ordered warm to cool (roughly cheapest to most expensive on OLED).
- **Place search** via Nominatim, debounced to respect its one-request-a-second policy.
- **SETTINGS** panel, **HIDE PANELS** (slides every panel off and back), equal
  240 px panels in two columns so nothing can overlap.
- **Live world statistics** from World Bank Open Data: population projected from
  the latest estimate at the net birth/death rate, births and deaths today, urban
  share, land area. The counter is labelled as a projection.
- **Population — France**: 644 communes over 15,000 people (Paris 2,103,778 to
  15,023), coloured with ColorBrewer's YlOrRd reversed for a dark ground.
- **MIN POPULATION** slider, logarithmic (15 K – 2.1 M).
- **Monuments — Montpellier**: top 10 ranked by number of Wikipedia language
  editions, merged from Wikidata and OpenStreetMap (neither was complete alone);
  five categorical colours that pass a colour-vision-deficiency check.
- **ILLUMINATE MY COUNTRY**: lights the border of the country you are in.
  Location only on request, coordinates rounded to ~1 km, map frames the country
  not the person.
- **All 195 capital names** (193 UN members + Vatican and Palestine), de-cluttered,
  far side of the globe culled.
- **Typography**: Dotwork wordmark, Space Mono readouts — Nothing-inspired, without
  Nothing's own licence-restricted Ndot typeface.
- **Data colour** mode: grey basemap cells take the chosen dot colour, saturated
  data cells keep their hue, and the basemap is dimmed while data is shown.

### Fixed

- **Screen went completely black over the sea** (and nearly so over open country
  at high zoom): water and ground were pure black, leaving nothing to light a dot.
  Both now keep a faint floor; building outlines added from z15.
- **Search bar drew on top of the readouts** — both pinned to the same position.
- **A duplicate element id silently filtered out every French commune**: the
  slider shared `s-pop` with the population counter, so the filter read `NaN`.
- **Temporal dead zone on `showCapitals`** killed the first frame.
- **ORBIT cancelled itself**: MapLibre fires `rotatestart` for programmatic camera
  moves too; the handler now reacts only to real gestures.
- **A map started in a zero-size container never re-framed** once it had a size.
- **Paris was missing** from the population data: its "commune of France"
  statement is not a truthy Wikidata statement, so the query silently dropped it.
- **The first two monument palettes failed** colour-vision checks (green and gold
  were ΔE 2.5 apart for protanopia); the shipped one passes all six checks.

---

## 2026-09-09 — First version, as "OpenStreetMap Dot"

- MapLibre renders an OpenFreeMap basemap offscreen; the visible canvas is a dot
  lattice where each cell's brightness sets a dot's radius.
- Basemap authored as a **luminance budget** for OLED: what matters is bright,
  everything else stays dark.
- Dot pitch follows zoom — coarse far out, fine up close.
- Views addressable with openstreetmap.org's `#map=zoom/lat/lon` hash.

### Fixed while getting it to run at all

- **cdnjs ships no MapLibre JavaScript**, only CSS — the library is now vendored.
- **MapLibre v6 is ESM-only with named exports** — imported as `import * as maplibregl`.
- **Frames read back all black**: in MapLibre v6 `preserveDrawingBuffer` moved
  under `canvasContextAttributes`, and the old top-level option is silently ignored.
