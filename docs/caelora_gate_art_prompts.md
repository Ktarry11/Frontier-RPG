# Caelora's gates and doors: art prompt (sheet CG1)

Kyle, 22 Nov 2026: "Do you need new gates and things for Caelora as a lot of the vertical and horizontal gates are wooden
etc (for zone transitions)". Yes. Measured the same day: every way in and out on Caelora was framed with ground art
(`world/exit_frames.py` falls through to its default): log gates and plain stone pillars on the roads, the dwarven vault
on the Golem Vault, crypt stairs as the way out of every sky cave. This sheet replaces all of it, and gives the five
Caelora towns (Lenswatch, Halcyon Rest, Keelstone, Dawnspear Wreck, Lastlight) a gate each in the one Aetherian style
with each town's own touch.

| Sheet | What | Image | Grid (cell) | Key |
|---|---|---|---|---|
| CG1 | 36 Caelora gates: road gates, side posts, town gates, skiff landings, cave doors in and out | 2048x2048 | 6 x 6 (about 341 x 341) | magenta |

Paste the block below and nothing else.

---

## SHEET CG1: CAELORA'S GATES AND DOORS (paste this whole block)

Generate ONE sprite sheet image, 2048x2048, a 6 columns x 6 rows grid = 36 separate props (each cell about 341x341).
Flat pure #FF00FF magenta background everywhere. Each prop is centred in its own cell with a wide margin, not touching or
overlapping its neighbours or the image edge. Painterly semi-realistic World of Warcraft Classic style, 3/4 top-down view
as used for a top-down RPG map, consistent soft lighting from the top-left, soft dark outline, chunky readable shapes.
No ground plane, no cast ground shadow, no text, no letters, no labels, no grid lines, no frames or borders, no people
or creatures. Never use magenta or pink anywhere on a prop.

Setting: CAELORA, the AETHERIANS' continent of floating islands above an endless sea of cloud under a huge golden sun.
The Aetherians build in pale white marble trimmed with gold, with luminous sky-blue and teal crystal, bronze fittings and
deep royal blue cloth. Their oldest works are thousands of years old, worn and beautiful. Their military, the
ASCENDANCY, adds bronze plate, riveted bands and blue banners. The KHARAD are cloud giants who carved huge rune-cut grey
stone long ago. The dying heart of the sky, the FADING FIRMAMENT, is grey, cracked, its crystals gone dark, lit violet
from below. Nothing from our modern world appears anywhere.

Every gate in rows 1, 3 and 4 faces the camera with a clear walkable OPENING in the middle at ground level. Every prop in
row 2 is ONE single free-standing gatepost: a tall upright pillar about twice as tall as it is wide, base at the bottom
of the cell, NOT a gate, NOT an arch, no crossbeam and no opening, just one side of a gateway. Every door in rows 5 and 6
is a doorway or opening with a clear dark or bright way through it.

Row 1, road gates facing the camera:
1. a graceful white marble arch with gold trim along its curve and a small sky-blue crystal lamp hanging from the keystone
2. a second white marble arch, lower and wider, with two gold-capped columns and blue cloth banners hanging either side
3. two tall slender white marble pylons topped with glowing sky-blue crystals, a soft ribbon of blue light curving between their tops
4. an Ascendancy checkpoint gate: bronze-plated marble towers either side, a raised bronze portcullis over the opening, blue banners
5. a cracked grey marble arch from the Fading Firmament, its crystals dark and dead, faint violet light glowing from the cracks
6. a massive ancient Kharad gate of rune-carved grey stone blocks, a giant's doorway, weathered, faint teal runes

Row 2, single gateposts, two of each style (A then B, small differences in detail):
7. A: a white marble pillar with a gold capital and a sky-blue crystal lamp on top
8. B: the same kind of white marble pillar with a gold finial and a short blue cloth pennant
9. A: an Ascendancy pillar of marble wrapped in riveted bronze bands, a blue banner hanging from it
10. B: the same kind of Ascendancy pillar with a bronze storm-lantern glowing cyan on top
11. A: a cracked grey marble pillar from the Firmament, a dead dark crystal on top
12. B: the same kind of cracked grey pillar, split down one side, violet light leaking from the split

Row 3, town gates facing the camera, all Aetherian white marble and gold, each with its town's own touch:
13. HALCYON REST, a garden waystation: a marble arch wound with silver-leafed vines, small gold bells hanging from it, a warm lamp at each side
14. KEELSTONE, the town of the Anchor-Wardens: two heavy marble posts with great bronze chains slung between them and a carved anchor emblem on each post (no writing)
15. DAWNSPEAR WRECK, a town built from a crashed warship: a gateway made of the ship's bronze-sheathed bow and curved hull ribs, blue sail-cloth and lanterns hung across it
16. LASTLIGHT, the last lit shrine in a dying sky: a cracked grey marble gateway with a single bright crystal lantern still burning gold over the opening, everything else dim
17. LENSWATCH, the scholars' survey camp: two marble posts with a large brass ring holding a glass lens set above the opening
18. a white marble gate with a gold sun disc over the opening and two crystal braziers, a grand ceremonial gate

Row 4, skiff landings and gangways (where a sky-ship ties up), facing the camera:
19. the end of a white marble landing stage with two bronze mooring posts and a crystal beacon on a pole
20. the head of a pale wooden gangway with gold-trimmed rails and bronze posts, blue cloth on the rails
21. an Ascendancy military berth: a bronze mooring clamp on a marble block and a blue war banner
22. a broken Firmament landing: cracked grey stone, snapped mooring chains hanging off, one dim lantern
23. a Kharad stone landing: a giant's stone step-pier with a rune-cut mooring ring
24. a small round marble skiff platform with a gold rail and a hanging sky-blue crystal lamp

Row 5, doors going IN or DOWN into the islands' rock (cave and dungeon entrances):
25. a huge Kharad vault door of rune-carved grey stone set into the rock, half open, teal runes glowing
26. a white marble stairway going down into the island under a gold-trimmed arch, darkness below
27. Ascendancy foundry blast doors of riveted bronze set into stone, steam curling out, blue banner over them
28. a round bronze-and-crystal engine hatch set into the rock, open, cyan light glowing from inside
29. a Kharad forge mouth cut into the rock, a giant's archway with orange firelight and soot round the edge
30. a grotto mouth lined with glowing pale-blue crystal, clear water trickling over the lip

Row 6, the way OUT, seen from inside a cave or dungeon looking back toward daylight:
31. a Kharad stone stair going up, worn giant's steps, bright daylight at the top
32. a white marble stair going up toward golden daylight, gold trim on the steps
33. the inside of bronze foundry doors standing open, bright sky beyond them
34. a bronze ladder up through an open round engine hatch, daylight above
35. a soot-black stone flue stair going up toward daylight
36. a crystal grotto opening from inside, mist and bright daylight beyond the crystals

---

## Slicing map

All go to `assets/tiles/cave_entrances/` (`tools/slice_building_sheet.py`, set `caelora_gates`); the `ent_` prefix is what
lets a sprite stand over a portal tile. `world/exit_frames.py` picks them by name.

| # | File | Used for |
|---|---|---|
| 1-3 | ent_gate_ae_marble_arch, ent_gate_ae_marble_arch_b, ent_gate_ae_crystal_pylons | Caelora's roads (north and south) |
| 4 | ent_gate_ascendancy | roads into and out of the Ascendant Bastions |
| 5 | ent_gate_firmament | roads into and out of the Fading Firmament |
| 6 | ent_gate_kharad | the Celestial Expanse's Kharad country |
| 7-12 | ent_side_ae_marble_a/b, ent_side_ascendancy_a/b, ent_side_firmament_a/b | roads leaving east or west |
| 13-17 | ent_town_halcyon_gate, ent_town_keelstone_gate, ent_town_dawnspear_gate, ent_town_lastlight_gate, ent_town_lenswatch_gate | each town's own gate, both sides |
| 18 | ent_town_ae_ceremonial_gate | Aurelion's ways out where no gate is hand-placed |
| 19-24 | ent_dock_ae_landing, ent_dock_ae_gangway, ent_dock_ascendancy, ent_dock_firmament, ent_dock_kharad, ent_dock_ae_skiff_platform | skiff landings and gangways |
| 25-30 | ent_door_kharad_vault, ent_door_ae_stair_down, ent_door_foundry, ent_door_engine_hatch, ent_door_forge_flue, ent_door_wellstone | ways in: the Golem Vault and the Keel; the Ascendant Spire; the Gravity Foundry; the Hollow Engine; the Hearthdeep; the Wellspring |
| 31-36 | ent_exit_kharad_stair, ent_exit_ae_stair_up, ent_exit_foundry, ent_exit_engine_hatch, ent_exit_forge_flue, ent_exit_wellstone | the way out of each of those |
