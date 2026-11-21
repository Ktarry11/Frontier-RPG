# The Ascendant Bastions: art prompts (sheets AB1 to AB4)


**Delivered 21 Nov 2026, all five sheets.** Sources in `tools/building_sheets/bastions_ab*.png` and
`tools/tile_sheets/bastions_ab4_tiles.png` (the art-sources branch). Sliced by `tools/slice_building_sheet.py`
(bastions_ab1, ab2, ab3, ab5) and `tools/slice_tile_sheet.py` (bastions_ab4). AB5's row 2 came back as four pieces all
running down to the right, so they're `ab_wall_36r_1` to `_4` and the 36l pieces are their mirrors. AB3's names are in
the slicer's set.
Kyle, 21 Nov 2026: "For the Bastion, let's have a 'Hellfire Citadel' like style. We can have a lvl 56-58 and a lvl 60
dungeon. Both into one mega structure but different entrances. Each dungeon will have around 8-9 bosss over two
floors", then "if you need any specific art let me know".

What's already in the game covers the open zone and most of the dungeon floors: SK6 (the Ascendancy's buildings), SK9
(siege props), SK12 (the Ascendancy's soldiers and constructs), SK17 and SK17B (forge floors, engine plates, pipe and
gear walls, marble halls), SK19 (warships). The citadel is composed from SK6's keep, walls and towers for now. These
four sheets are what would make it special:

| Sheet | What | Image | Grid (cell) | Key | Priority |
|---|---|---|---|---|---|
| AB1 | the citadel itself, one mega-structure, and its two gates | 2048x2048 | one piece + two gates | magenta | 1 |
| AB2 | 18 dungeon bosses, nine for each dungeon | 2048x1024 | 6 x 3 (about 341 x 341) | magenta | 1 |
| AB3 | 36 dungeon props: the Foundry and the Spire | 2048x2048 | 6 x 6 (about 341 x 341) | magenta | 2 |
| AB4 | 24 dungeon floors and walls the stock doesn't have | 2048x1536 | 8 x 6 (256 x 256), 24 used | **NO magenta** | 3 |
| AB5 | 16 angled curtain walls, towers and gates, from the SK6 wall | 2048x2048 | 4 x 4 (512 x 512) | magenta | 1 |

**References to attach:** for AB1, `assets/buildings/ae_fortress_keep.png`, `assets/buildings/ae_wall_tower.png` and
`assets/buildings/ae_aurelion_spire.png`; for AB2, `assets/creatures/ae_high_commander.png`,
`assets/creatures/ae_construct_titan.png` and `assets/creatures/ae_inquisitor.png`; for AB3, `assets/buildings/ae_sky_forge.png`
and `assets/buildings/ae_crystal_engine.png`; for AB4, `assets/tiles/sky/ground/ae_forge_floor.png` and
`assets/tiles/sky/ground/ae_palace_marble.png`.

---------------------------------------------------------------------
## SHEET AB1: THE CITADEL (paste this whole block)

```
Generate ONE image, 2048x2048, flat pure #FF00FF magenta background everywhere. A top-down game asset in WoW Classic style with a slight 3/4 top-down camera angle, matching the attached Aetherian buildings exactly: painterly semi-realistic, lighting from the top-left, crisp clean edges, no magenta in the art.

Setting: the sky above a fantasy world, where the AETHERIANS (tall imperial sky-people) build in white marble and pale stone trimmed with gold, with deep royal blue banners, bronze gears and glowing sky-blue crystal. Their military, the ASCENDANCY, has turned an ancient scholars' college into a fortress.

THE CITADEL OF ASCENT, one enormous fortress seen from above at the 3/4 angle, filling most of the image (about 1700 px across): a MEGA-STRUCTURE like a fortress-city, dense and imposing, built on a PENTAGON of high curtain walls with a great round tower at each of the five corners. Inside the walls it is packed solid: barracks halls with blue slate roofs, forge buildings with tall bronze chimneys venting grey smoke and orange glow, lancer hangars with open doors, slender watch spires with blue crystal tips, storm-collector masts crackling with lightning, all crowded together and climbing toward the middle, where the great KEEP rises highest: a tall white-and-gold citadel tower with a glowing blue crystal crown and a gold Ascendancy sigil. Banners of deep blue and silver on every tower. Two gates are clearly visible: a broad, heavy SOUTH GATE at the bottom edge of the walls, bronze doors with molten orange light spilling from the forges inside and rails or tracks running out of it (the foundry); and a tall, narrow, elegant NORTH GATE at the top corner, white and gold with blue crystal lanterns (the command spire). The base of the walls sits flat on the ground; no ground, no island rock, no shadow under it, no text.

Then, separately, in the corners of the image with a wide margin around each, two smaller pieces: bottom-left, the SOUTH GATE alone (about 400 px wide), the same heavy bronze foundry gate set in a short stretch of wall; bottom-right, the NORTH GATE alone (about 300 px wide), the same tall white-and-gold gate in a short stretch of wall.
```

Slices to `assets/buildings/ab_citadel.png`, `ab_foundry_gate.png`, `ab_spire_gate.png`.

---------------------------------------------------------------------
## SHEET AB2: THE 18 BOSSES (paste this whole block)

```
Generate ONE sprite sheet image, 2048x1024, a grid of 6 columns x 3 rows = 18 separate full-body character sprites. Flat pure #FF00FF magenta background everywhere. Each figure stands fully inside its own cell with a wide margin and does NOT touch or overlap neighbours or the image edge. Every figure faces the viewer (front view, "facing down" on a top-down game map), in a menacing idle pose, slight 3/4 top-down camera angle. Big constructs and elementals may fill more of their cell than the people do. No ground shadow, no text, no labels, no grid lines. Painterly semi-realistic, WoW Classic art style matching the attached references, lighting from the top-left, crisp clean edges, no pink or magenta in the characters.

THE PEOPLE: the ASCENDANCY, the military of the AETHERIANS, tall imperial sky-people with pale blue-grey or warm bronze skin, softly glowing eyes and natural crystal growths at the brow, cheeks, shoulders or hands. Armour is fitted bronze and white enamel with deep blue cloth and silver insignia; weapons are tipped with blue crystal. Their constructs are bronze, pale stone and blue crystal, with glowing cores.

Row 1, THE GRAVITY FOUNDRY, floor one (molten orange and bronze, soot and sparks):
1 INTAKE-WARDEN BRANNOC TEAL: a heavy-set Ascendancy officer in a soot-stained bronze coat, a crystal-tipped rod, a bronze construct hound at his heel.
2 THE SLAG COLOSSUS: a huge hunched elemental of cooling crystal slag, molten orange glowing through black cracks, drips of liquid crystal.
3 POURMASTER ILKA: a tall Aetherian woman smith in a leather apron over bronze plate, holding a long glowing crucible ladle, crystal growths glowing hot.
4 POURMASTER DOV: her twin brother, broad, in the same apron and plate, a great forge hammer over his shoulder, ice-blue quenching mist rising from his gauntlets.
5 PROTOTYPE NINE: an experimental construct, taller than a man, bronze and white plating half finished with exposed crystal cables, one huge arm a reflecting crystal shield.
6 FOUNDRY-MASTER CASSOR VANE: an older Aetherian engineer in an ornate bronze harness with floating gravity stones circling him and a gravity hammer with a blue crystal head.

Row 2, THE GRAVITY FOUNDRY, floor two (the Keelworks), and the first of the SPIRE:
7 GANTRY-CHIEF DESSA MARN: an Aetherian woman engineer on small hovering bronze boots, goggles of blue crystal, a satchel of bomb-crystals, a tiny bomber construct at her shoulder.
8 THE CORELESS: an unfinished warship engine core, a great sphere of bronze rings around an unstable, flickering blue crystal heart, arcs of energy leaping off it.
9 GRAVITY-WRIGHT ISELLE VARR: a slender Aetherian woman caster in deep blue robes, rubble and broken plating floating around her hands, her hair lifted as if underwater.
10 THE WARHEART: the first warship's engine heart awakened, a towering construct of bronze ribs and ship's timber around a blazing crystal core, cannon barrels on its shoulders.
11 DRILLMASTER KAINE VORR (the Spire): a scarred Aetherian veteran in heavy white-and-bronze plate, a tall tower shield and a drill baton, mouth open shouting orders.
12 LANCE-COMMANDER ARIS THANE: an Aetherian knight mounted on a bronze construct steed with crystal wings folded, a very long crystal-tipped lance.

Row 3, THE ASCENDANT SPIRE (white marble, gold and blue, the command):
13 THE STORM CHOIR: three Aetherian storm callers in blue and silver robes standing close together as one figure group, lightning arcing between their raised staves.
14 HIGH INQUISITOR SEREN VASH: a gaunt Aetherian in a mask of white enamel with a gold sigil, long grey-white robes, a censer of blue fire on a chain.
15 ARCHIVIST-CENSOR MALLEN ROE: a hunched old Aetherian archivist in ash-grey robes, a burning book in one hand and a quill of crystal in the other, glowing embers of pages swirling around him.
16 THE AEGIS ENGINE: a defensive construct, a tall bronze pylon on four legs projecting a dome of blue light, small shield drones orbiting it.
17 WARMARSHAL DRAVIN KELL: a powerful Aetherian commander in ornate gold-and-bronze armour with a crested helm under one arm and a command baton, a gunnery spyglass at his belt.
18 EXARCH LUCAN THESSALY: the general's right hand, tall and severe, in gleaming white-and-gold armour and a long deep-blue cloak, a halo of crystal shards around his head like a crown, a sword of pure blue crystal. Clearly the most important figure on the sheet.

Keep every figure fully separated in its own cell. Before you finish, check there are 18 separate figures on flat magenta.
```

Slices to `assets/creatures/ab_<name>.png`, in this order: `ab_intake_warden, ab_slag_colossus, ab_pourmaster_ilka,
ab_pourmaster_dov, ab_prototype_nine, ab_foundry_master, ab_gantry_chief, ab_coreless, ab_gravity_wright, ab_warheart,
ab_drillmaster, ab_lance_commander, ab_storm_choir, ab_high_inquisitor, ab_archivist_censor, ab_aegis_engine,
ab_warmarshal, ab_exarch`.

---------------------------------------------------------------------
## SHEET AB3: 36 DUNGEON PROPS (paste this whole block)

```
Generate ONE image, 2048x2048, a grid of 6 columns x 6 rows = 36 separate props, flat pure #FF00FF magenta background, each fully inside its own cell with a wide margin, no shadows, no text, no grid lines. Top-down game props in WoW Classic style with a slight 3/4 top-down angle, painterly semi-realistic, lighting from the top-left, matching the attached Aetherian buildings: white marble and pale stone, gold trim, bronze machinery, glowing sky-blue crystal; in the foundry, soot, molten orange light and sparks.

Rows 1 to 3, THE GRAVITY FOUNDRY (the Ascendancy's construct works): 1 a great crucible on a bronze frame pouring a stream of molten orange crystal; 2 a casting mould in the floor shaped like a construct's torso, glowing; 3 a conveyor rail section with half-built construct limbs on it; 4 a bronze assembly cradle holding an unfinished construct upright; 5 a rack of construct heads and arms; 6 a quenching tank of steaming blue water; 7 a tall bellows-furnace with an open glowing door; 8 a pile of crystal ore in a cart on rails; 9 a crane arm of bronze with a hook and chain; 10 a workbench covered in tools and blueprints (no readable text); 11 a stack of bronze ship ribs; 12 a warship engine core on a test stand, crackling; 13 a gantry walkway support pillar of bronze; 14 a coil of heavy chain; 15 a cooling slag heap glowing faintly; 16 a crystal-cutting lathe; 17 a bin of rivets and bolts; 18 a broken construct slumped against a wall.

Rows 4 to 6, THE ASCENDANT SPIRE (the Ascendancy's command): 19 a war-table with a glowing map of floating islands (no text); 20 a weapon rack of crystal-tipped lances; 21 a tall standard of deep blue and silver; 22 an officer's high-backed chair; 23 a rack of armour on stands; 24 a training dummy of bronze; 25 an inquisitor's interrogation chair with crystal restraints; 26 a brazier of blue fire with ash and half-burned scrolls; 27 a cage of bronze bars, empty; 28 a lectern with a great book; 29 shelves of scrolls and stone plates; 30 a sealed vault door of white stone and gold; 31 a storm-calling pillar crackling with lightning; 32 a shield pylon projecting a small blue dome; 33 a great window frame of crystal looking onto the sky; 34 a statue of an armoured Aetherian with a sword; 35 a long banquet table set for officers; 36 a throne-like command seat on a dais, blue and gold.
```

Slices to `assets/tiles/sky/props/ab_<name>.png` (the names are listed with the slicer when the sheet lands).

---------------------------------------------------------------------
## SHEET AB4: 24 DUNGEON FLOORS AND WALLS (paste this whole block)

```
Generate ONE image, 2048x1536, a grid of 8 columns x 6 rows of seamless square textures, only the first 24 cells (rows 1 to 3) filled, the rest left plain grey. Each cell is a seamless, tileable, top-down texture filling its whole cell edge to edge with no border, no frame, no perspective, no text. Painterly semi-realistic, WoW Classic style, even lighting.

Row 1, THE FOUNDRY FLOORS: 1 soot-black iron floor plates with rivets; 2 floor grating over a glowing orange forge pit; 3 rail tracks set in dark stone; 4 cracked stone floor with molten orange veins; 5 bronze floor with a hazard pattern of gold and black chevrons (no text); 6 scorched stone with slag spatter; 7 a channel of flowing molten crystal, orange and gold; 8 a pool of cooling blue quench water.
Row 2, THE SPIRE FLOORS: 9 white marble with a gold Ascendancy inlay; 10 deep blue carpet with silver edging; 11 polished parade-ground flagstones, pale grey; 12 dark slate inquisition floor with a faint blue rune circle; 13 archive floor of worn wooden boards strewn with ash; 14 gold-veined black marble; 15 crystal glass floor showing the sky below; 16 a storm-scorched balcony floor, pale stone with lightning burns.
Row 3, WALLS (seamless, as seen from above, the top of a wall): 17 foundry wall of soot-stained bronze plates and pipes; 18 foundry wall of dark brick with glowing vents; 19 white marble wall with gold banding; 20 blue-tiled wall with silver trim; 21 inquisition wall of black stone; 22 archive wall of shelves; 23 a wall of glowing crystal; 24 a wall of heavy bronze gearwork.
```

Slices to `assets/tiles/sky/ground/ab_<name>.png`.

---------------------------------------------------------------------
## SHEET AB5: ANGLED CURTAIN WALLS (paste this whole block)

Kyle, 21 Nov 2026: "Why don't I get angled wall art using the reference wall". The citadel's curtain is a pentagon,
so its walls run at five angles on screen: flat across the south, about 36 degrees down to the right on the north-east
and down to the left on the north-west, and steep, about 72 degrees, down the east and west sides. Right now every
wall is the flat SK6 wall, stepped along the slope, which is why the sides look stacked. Attach
`assets/buildings/ae_fortress_wall.png` and `assets/buildings/ae_wall_tower.png` as the reference.

```
Generate ONE image, 2048x2048, a grid of 4 columns x 4 rows = 16 separate pieces, flat pure #FF00FF magenta background, each piece fully inside its own cell with a wide margin, no shadows, no ground, no text, no grid lines. Top-down game art in WoW Classic style with the same slight 3/4 top-down camera angle as the attached wall, matching it EXACTLY in stone, colour, height, thickness, battlements, gold trim, deep blue banners and blue crystal lamps: white marble and pale stone trimmed with gold. Lighting from the top-left on every piece.

Every wall piece is a straight run of that same fortress wall, the same height and thickness in every cell, drawn running at the angle given, as it would look on a map seen from slightly above and south. Both ends of every wall piece are cut off cleanly and squarely along the wall's line, so that two pieces of the same angle placed end to end join into one continuous wall with no gap and no overlap. Keep the wall's top walkway, its battlements and its front face visible at every angle.

Row 1: 1 the wall running straight left to right (flat), plain; 2 the same flat wall with a buttress and a hanging blue banner; 3 the wall running straight away from the viewer (top to bottom of the cell, seen end-on at the 3/4 angle), plain; 4 the same top-to-bottom wall with a buttress.
Row 2: 5 the wall running diagonally DOWN TO THE RIGHT at about 36 degrees below horizontal, plain; 6 the same 36-degree wall with a banner; 7 the wall running diagonally DOWN TO THE LEFT at about 36 degrees, plain; 8 the same with a banner.
Row 3: 9 the wall running steeply DOWN TO THE RIGHT at about 72 degrees below horizontal, plain; 10 the same 72-degree wall with a buttress; 11 the wall running steeply DOWN TO THE LEFT at about 72 degrees, plain; 12 the same with a buttress.
Row 4: 13 a great round corner tower, taller than the wall, made to stand where two walls meet at an angle; 14 the same tower with a blue crystal beacon on top; 15 a short flat wall section with a grand arched gate in it, bronze doors; 16 a short section of the 36-degree wall with a tall narrow gate in it.
```

Slices to `assets/buildings/ab_wall_flat_1.png`, `ab_wall_flat_2`, `ab_wall_deep_1`, `ab_wall_deep_2`,
`ab_wall_36r_1`, `ab_wall_36r_2`, `ab_wall_36l_1`, `ab_wall_36l_2`, `ab_wall_72r_1`, `ab_wall_72r_2`, `ab_wall_72l_1`,
`ab_wall_72l_2`, `ab_corner_tower`, `ab_corner_tower_lit`, `ab_gate_flat`, `ab_gate_36`. The citadel lays them end to
end along each curtain, one angle a side.
