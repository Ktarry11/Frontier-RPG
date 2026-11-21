# Caelora's links: art prompt (sheet LK1)

**Status (21 Nov 2026): delivered and sliced the same day** (`tools/slice_building_sheet.py`, set caelora_lk1; the currents are also turned in 30-degree steps, and the violet ones hue-corrected after the soft key). See `docs/art_status.md` for every sheet.

Kyle, 21 Nov 2026: "Can we do little short range portals that link islands instead of bridges? Like a new system", "If so
it could open a lot of cool shit... this zone where all the islands are broken and you use wind currents to move
between them", "Give me prompts bro. Maybe about 24 unique ones", "I mean prompts for Caelum links, not everything".

A **link** joins two places on the same map without a bridge: you stand on one end, press interact, and you're beside
the other end. No loading, no zone change. Caelora's links are the Aetherians' old **skip-stones**, the sky's **wind
currents**, **gravity lifts** up to higher ground, **light-bridges** of hard light, and **chain lines** a skiff runs
along. This sheet is the art for both ends of each kind, the marker that shows where one is, and the ribbons and spans
drawn over the gap between them (drawn, not walked). Until it lands, the pads use the teal rune circle already in the
game (`sk_rune_circle_teal`).

| Sheet | What | Image | Grid (cell) | Key |
|---|---|---|---|---|
| LK1 | 24 Caelora link pieces: skip-stones, wind currents, gravity lifts, light-bridges, chain lines | 2048x1366 | 6 x 4 (about 341 x 341) | magenta |

**References to attach:** `assets/tiles/sky/props/sk_rune_circle_teal.png`, `assets/buildings/ae_gravity_lift.png`,
`assets/buildings/ae_light_bridge.png` and `assets/tiles/sky/props/sk_cloud_wisp.png`.

Slices to `assets/tiles/sky/props/lk_*.png`, named in the slicer's set. The diagonal ribbons are drawn running down to
the right only; their down-left twins are mirrored in code.

---------------------------------------------------------------------
## SHEET LK1: CAELORA'S LINKS (paste this whole block)

```
Generate ONE sprite sheet image, 2048x1366, a 6 columns x 4 rows grid = 24 separate sprites, each cell about 341x341. Flat pure #FF00FF magenta background everywhere. Each sprite is ONE single object, centred in its own cell with a wide margin, not touching or overlapping its neighbours or the image edge. No ground patch under anything unless the prompt asks for one. No text, no labels, no grid lines, no magenta or pink anywhere in the art.

Match the attached references EXACTLY in style, camera angle, outline and level of detail: they are from the same set. Painterly semi-realistic WoW Classic style: strong readable silhouette, soft dark outline, chunky simple shapes legible at small size, consistent soft lighting from the top-left. Camera: isometric three-quarter view elevated about 45 degrees, every object turned the same way, front face toward the lower-right.

Setting: CAELORA, the AETHERIANS' continent of floating islands above an endless sea of cloud under a huge golden sun. The Aetherians build in pale white marble trimmed with gold, with luminous sky-blue and teal crystal, bronze fittings and deep royal blue cloth. Their oldest works are thousands of years old, worn and beautiful. Their military, the ASCENDANCY, adds bronze plate, chain and blue banners. The dying heart of the sky, the FADING FIRMAMENT, is grey, cracked and lit violet from below.

These are LINKS: ways across the gaps between floating islands without a bridge. Each pad is a flat round platform a person steps onto, seen from the 3/4 angle, about the size of a cart; the ribbons and spans are long flat shapes meant to be laid over an empty gap between two islands. Wind and light are painted as OPAQUE soft-edged streaks and glows, never transparent, so nothing shows the magenta through it.

Objects keep their RELATIVE scale: the ribbons and spans are the widest sprites on the sheet and run edge to edge of their cell with a margin; the pads are about two thirds of a cell; the markers and posts are tall and narrow.

Props are numbered row by row, left to right, top to bottom:

Row 1, SKIP-STONES, the Aetherians' oldest links: 1 A SKIP-STONE: a round white-marble pad inlaid with three thin gold rings, a teal crystal set in its centre, a ring of softly glowing teal runes round the rim. 2 A FAILING SKIP-STONE of the Firmament: the same pad gone grey and cracked across, its crystal flickering violet, small chips of it floating up off the edge. 3 A GRAND SKIP-STONE of the city: the same pad on a low dais with a slender gold arch over it, blue crystal set in the arch's keystone. 4 AN OVERGROWN SKIP-STONE: an ancient pad half buried in golden moss and pale roots, its runes still faintly lit through the moss. 5 AN ASCENDANCY SKIP-STONE: the pad refitted in riveted bronze plate with a low chain rail round it and a small royal blue banner on a post. 6 A SKIP-STONE MARKER: a tall narrow white-marble obelisk with a teal crystal tip, gold bands, and a faint teal glow at its foot, the kind that stands beside a pad so travellers can find it.

Row 2, WIND CURRENTS, the sky's own links: 7 AN UPDRAFT VENT: a ring of carved white stone set into the rock at an island's edge, a spiral of pale wind rising out of it, golden leaves caught spinning in the spiral. 8 A WIND LANDING: a round patch of golden grass flattened in a swirl, golden leaves and a few white feathers settling on it. 9 A WIND CURRENT, horizontal: a long flat ribbon of pale white-blue wind streaming from left to right, soft streaks and curls, golden leaves and sparkling motes carried along it, about 320 px long and 90 px wide. 10 A WIND CURRENT, vertical: the same ribbon streaming from top to bottom, about 90 px wide and 320 px tall. 11 A WIND CURRENT, diagonal: the same ribbon streaming from the top-left corner of its cell to the bottom-right corner. 12 A DUSK CURRENT, horizontal: the same ribbon in failing violet and grey, ash and dim violet sparks carried along it, for the dying Firmament.

Row 3, WIND MARKERS AND GRAVITY LIFTS: 13 A STORM CURRENT, horizontal: the same ribbon as dark storm-blue wind with small white lightning crackles along it. 14 A WIND-CHIME POST: a tall slender bronze post with gold wind-chimes and long royal blue pennants streaming sideways, marking where a current runs. 15 A GRAVITY LIFT: a round gold-inlaid marble pad with a broad gold ring floating above it at head height, a column of teal light and drifting motes rising from the pad up through the ring. 16 A GRAVITY LIFT LANDING: a smaller pad with a smaller gold ring hovering just over it, motes settling down onto it. 17 A LIGHT-BRIDGE PYLON: a tall white-and-gold pylon with a bright teal crystal at its top, a fan of gold light spreading from it toward the right, the head of a bridge of light. 18 A LIGHT-BRIDGE SPAN, horizontal: a long flat walkway of solid gold-and-teal light running left to right, faint gold rune bands crossing it, crisp edges, about 320 px long and 90 px wide.

Row 4, LIGHT-BRIDGES AND CHAIN LINES: 19 A LIGHT-BRIDGE SPAN, vertical: the same walkway of light running top to bottom, about 90 px wide and 320 px tall. 20 A CHAIN-SKIFF DOCK: a small round marble landing with a bronze winch post, a heavy chain running off to the right, and a small one-person sky-skiff with a white sail-fin hooked to the chain. 21 A CHAIN LINE, horizontal: a heavy taut bronze chain running left to right across the cell, small glowing crystal lanterns hung along it at intervals. 22 CLOUD-STEPS: four flat round stepping stones of white marble floating in a gentle arc with a little space under each, wisps of cloud trailing beneath them. 23 A TETHER POST: a short thick bronze post on a marble base with a gold cap, a chain wound round it and running off to the right. 24 A DEAD SKIP-STONE: a skip-stone broken in three pieces, its crystal gone dark and grey, its runes unlit, a few pieces tilted up at the edges; scenery, no longer works.
```

Slices, row by row: `lk_skipstone`, `lk_skipstone_failing`, `lk_skipstone_grand`, `lk_skipstone_overgrown`,
`lk_skipstone_ascendancy`, `lk_skipstone_marker`; `lk_updraft`, `lk_wind_landing`, `lk_wind_h`, `lk_wind_v`,
`lk_wind_d`, `lk_dusk_wind_h`; `lk_storm_wind_h`, `lk_wind_chime_post`, `lk_gravity_lift`, `lk_gravity_landing`,
`lk_lightbridge_pylon`, `lk_lightbridge_h`; `lk_lightbridge_v`, `lk_chain_dock`, `lk_chain_h`, `lk_cloud_steps`,
`lk_tether_post`, `lk_skipstone_dead`.
