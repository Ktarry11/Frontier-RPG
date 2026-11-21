# Moonglade art prompts (sheets 1 to 4)

**Status (21 Nov 2026): delivered and sliced.** See `docs/art_status.md` for every sheet.

For `docs/moonglade_brief.md`. Kyle, 18 Nov 2026: "Get that mystical druid look for moonglade, we should have the lush
tiles, trees, and brillian beautiful water!" He picked new art before the build.

Every prompt below is complete on its own: paste one block and nothing else. Each states the image size, the grid and
cell size, the background, the margin, the style, the camera, the scale rule, the negatives, the never-magenta line,
the nothing-from-Earth line, and every cell numbered row by row. Moonglade has no enemies yet, so there's no creature
sheet.

| Sheet | What | Image | Grid (cell) | Key |
|---|---|---|---|---|
| 1 | 48 ground, path, shore and water tiles | 2048x1536 | 8 x 6 (256 x 256) | **NO magenta**: tiles run flush to their edges |
| 2 | 36 nature props: trees, flowers, the lake's edge | 2048x2048 | 6 x 6 (about 341 x 341) | magenta |
| 3 | 36 town buildings and props: Nighthaven (night elf and tauren) and the Wakened | 2048x2048 | 6 x 6 (about 341 x 341) | magenta |
| 4 | 9 giant landmarks: the Shrine, the three dungeon doors, the roost, the great moonwell | 2048x2048 | 3 x 3 (about 682 x 682) | magenta |

**Priority:** sheet 1 first (the ground and the water are most of the look), then 4, 2 and 3.

**Style references to attach (at most 3 per sheet):**
- Sheet 1: `assets/tiles/azshara/ground/az_leyline_grass.png`, `az_lake_water.png`, `az_moss_shroom.png`
- Sheet 2: `assets/tiles/ashenvale/props/ash_giant_ash_tree.png`, `ash_glow_mushroom_ring.png`, `ash_nightbloom_bush.png`
- Sheet 3: `assets/buildings/fw_druid_treehouse.png`, `fw_sentinel_hall.png`, `fw_timbermaw_lodge.png`
- Sheet 4: `assets/buildings/fw_moonwell_shrine.png`, `assets/tiles/ashenvale/props/ash_living_gate_arch.png`,
  `assets/buildings/fw_hippogryph_roost.png`

---

## SHEET 1: 48 ground, path, shore and water tiles (NO magenta)

```
Generate ONE texture sheet image, 2048x1536, laid out as a strict 8 columns x 6 rows grid = 48 separate seamless ground and water textures, each cell exactly 256x256. Each cell is COMPLETELY FILLED by its texture, edge to edge, touching its neighbours with no gap. No border, no background colour, no magenta, no frames, no gutters, no grid lines, no text, no labels, no numbers. Every texture must TILE SEAMLESSLY with itself on all four sides: no single large feature that would obviously repeat, no emblem, rune or pattern repeated in every tile, no lighting gradient across the cell, flat even illumination, no vignette, no baked shadows, no objects or props standing on the ground. Straight top-down view, no perspective. Nothing modern or from the real world.

Match the attached reference tiles EXACTLY in style, scale of detail and level of saturation: they are from the same set. Painterly semi-realistic WoW Classic ground texture style, rich and lush but readable at small size, not too busy.

Setting: MOONGLADE, a sacred druid valley under permanent soft moonlight, ringed by mountains around a great clear lake. Mystical, peaceful and alive: deep lush greens, moonlit silver-blue, soft violet, and small points of glowing white and pale blue light from flowers and moss. The WATER is the most important part of this sheet: it must be clear, luminous and beautiful, the kind of water you want to stand beside.

Tiles are numbered row by row, left to right, top to bottom:

Row 1 - THE GLADE: 1 lush deep-green grass, soft and thick, faintly silvered by moonlight (the main ground); 2 the same grass a shade darker and longer; 3 grass scattered with tiny glowing white star-shaped flowers; 4 grass with small violet and blue wildflowers; 5 soft green moss over dark loam; 6 moss with a faint blue bioluminescent glow in its fibres; 7 clover and low herbs; 8 meadow grass silvered almost white by the moon.

Row 2 - THE WOODS: 9 forest floor of dark loam and fallen silver-green leaves; 10 forest floor with ferns flattened into it and pine needles; 11 mossy roots threading through dark earth; 12 a carpet of fallen violet petals over grass; 13 dark rich loam, freshly turned (a garden bed); 14 grass with small pale glowing mushrooms; 15 leaf litter with faint blue light caught in the dew; 16 deep shade forest floor, nearly black-green with moss.

Row 3 - PATHS AND STONE: 17 a winding footpath of packed pale earth worn into the grass; 18 old pale moonstone flagstones with grass and moss in the joints; 19 a path of round river stones set in moss; 20 smooth pale stone, slightly worn, with faint silver flecks; 21 dark grey mountain rock with lichen; 22 a grey cliff face with moss and small ferns in the cracks, seen straight on (a wall); 23 loose scree of grey and pale stones; 24 a plank boardwalk of silver-grey weathered wood, boards running one way.

Row 4 - THE SHORE: 25 fine pale silver-white lake sand; 26 wet sand darkened at the water's edge with tiny shells; 27 smooth pebbles, wet and gleaming; 28 shallow water over pale sand, very clear, the sand visible through it; 29 shallow water over smooth stones, clear, with soft moonlight caustics; 30 reeds and rushes growing thick out of the shallows; 31 lily pads with small white and pale-violet water lilies on clear dark water; 32 muddy shore with moss and reeds starting.

Row 5 - LAKE ELUNE'ARA: 33 clear lake water, mid-depth, luminous silver-blue with soft moonlight ripples; 34 the same water a little deeper and darker, still clear; 35 deep lake water, rich deep blue with faint silver light far down; 36 the deepest water, deep indigo with a faint glow from below; 37 calm water with a soft mirror sheen of moonlight; 38 water with a gentle breeze ripple; 39 water over a pale moonstone floor, glowing faintly through; 40 moonwell water: pale glowing blue-white, luminous and magical.

Row 6 - THE DREAM AND THE BARROWS: 41 grass touched by the Emerald Dream, green-gold and soft, faintly glowing; 42 a carpet of pale dream flowers glowing soft green; 43 dark barrow earth with roots and moss, damp and old; 44 worn ancient barrow flagstones carved with faint lines, mossy (no repeating symbol); 45 a living floor of woven roots, smooth with age; 46 thorny bramble earth, dark green and brown; 47 pale ash-white sand with faint silver glints, the island's ground; 48 still dark water that reflects nothing, flat and black-blue with a faint ring of light.
```

---

## SHEET 2: 36 nature props (magenta)

```
Generate ONE sprite sheet image, 2048x2048, laid out as a strict 6 columns x 6 rows grid = 36 separate game props, each in its own cell of about 341x341. Flat pure #FF00FF magenta background everywhere. Each prop sits fully inside its own cell with a wide margin and does NOT touch or overlap neighbours or the image edge. No ground shadow, no ground plane, no grass patch under the prop unless the prop is a ground cover, no text, no labels, no grid lines. NEVER use magenta, pink or purple-pink in the props themselves (violet and blue are fine).

Match the attached references EXACTLY in style: painterly semi-realistic WoW Classic props, seen from a slight 3/4 top-down camera angle, consistent soft moonlight from the top-left, crisp clean edges. Objects keep their RELATIVE scale: a flower patch is far smaller than a great tree; do not blow each one up to fill its cell. Nothing modern or from the real world.

Setting: MOONGLADE, a sacred druid valley under permanent soft moonlight around a great clear lake. Lush, mystical and alive: deep greens, silver bark, blue-violet and silver leaves, small points of glowing white and pale blue light.

Props are numbered row by row, left to right, top to bottom:

Row 1 - GREAT TREES: 1 an ancient giant oak with silver bark and a vast canopy of deep green leaves touched with silver; 2 a towering silver-barked tree with a blue-violet canopy; 3 a moonlit willow, long trailing silver-green fronds; 4 a slender silver birch-like tree with pale leaves; 5 a tall dark pine, lush and full; 6 an ancient twisted tree whose roots arch above the ground.

Row 2 - SMALL TREES AND SHRUBS: 7 a young silver sapling; 8 a flowering tree with pale white-blue blossoms; 9 a round bush of dark leaves with glowing blue berries; 10 a fern clump, large and lush; 11 a hedge of flowering shrubs, white and violet; 12 a mossy fallen log with ferns and small mushrooms growing from it.

Row 3 - FLOWERS AND GLOW: 13 a patch of glowing white star-flowers; 14 a cluster of tall blue-violet flowers like lupins; 15 a ring of pale glowing blue mushrooms; 16 a cluster of large glowing mushrooms, silver caps; 17 moon-lilies: tall white flowers that glow at the centre; 18 a patch of night-blooming flowers open and shining.

Row 4 - THE LAKE'S EDGE: 19 a tall reed bed with cattails; 20 a floating cluster of water lilies with white flowers; 21 smooth shore boulders, wet, with moss at the waterline; 22 a group of stepping stones in shallow water (stones only, water drawn under them); 23 a small cascade falling over mossy rocks into a pool (water drawn inside); 24 a half-sunken ancient carved stone, mossy, in shallow water.

Row 5 - STONE AND MOON: 25 a tall pale standing moonstone with faint silver runes; 26 a ring of three small moonstones; 27 a mossy boulder with a shallow cup of glowing water in its top; 28 a cluster of pale blue moon crystals growing from rock; 29 an overgrown old elven pillar with vines and flowers; 30 a mossy rock outcrop with ferns.

Row 6 - DREAM AND WILD: 31 a patch of green-gold dream flowers glowing softly; 32 a small cloud of floating green-gold motes of light over a flower (no figure); 33 a thorny bramble thicket with dark green leaves and white blossoms; 34 a stag's shed antlers lying in moss with flowers growing through them; 35 an owl perched on a mossy stump, silver and white; 36 a pair of white rabbits sitting in grass.
```

---

## SHEET 3: 36 town buildings and props (magenta)

```
Generate ONE sprite sheet image, 2048x2048, laid out as a strict 6 columns x 6 rows grid = 36 separate game buildings and props, each in its own cell of about 341x341. Flat pure #FF00FF magenta background everywhere. Each item sits fully inside its own cell with a wide margin and does NOT touch or overlap neighbours or the image edge. No ground shadow, no ground plane, no text, no letters, no labels, no grid lines. NEVER use magenta, pink or purple-pink in the art (violet is fine).

Match the attached references EXACTLY in style: painterly semi-realistic WoW Classic buildings and props, seen from a slight 3/4 top-down camera angle, consistent soft moonlight from the top-left, crisp clean edges. Objects keep their RELATIVE scale: a lantern is far smaller than a house, a house far smaller than a hall; do not blow each one up to fill its cell. Nothing modern or from the real world: no metal sheeting, no glass windows, no signs with writing, no Earth objects at all.

Setting: MOONGLADE, a sacred druid valley under permanent soft moonlight. Three styles live side by side: NIGHT ELF druid work (graceful curved living wood, silver-blue and violet leaf roofs, moon-blue lanterns, owl and crescent carvings); TAUREN druid work (hide, carved honey-brown timber, painted totems, earth tones, feathers and woven blankets); and THE WAKENED, people who arrived from far away and had to learn to build here (honest timber longhouses, plank walls, thatch, rope, careful but clearly amateur work, flower gardens).

Items are numbered row by row, left to right, top to bottom:

Row 1 - NIGHTHAVEN, NIGHT ELF: 1 a night elf house of curved living wood with a leaf roof; 2 a smaller night elf cottage grown from a tree trunk; 3 the Cenarion Circle's hall, a long graceful building of living wood with an arching leaf roof; 4 a night elf inn with an open porch and blue lanterns; 5 a druid's tree house grown into a living trunk; 6 a moon-blue lantern on a curved wooden post.

Row 2 - NIGHTHAVEN, TAUREN: 7 a large tauren lodge of hide over carved timber poles, painted with earth-toned designs; 8 a smaller tauren tent with woven blankets over the door; 9 a tall tauren totem of carved animal faces, painted; 10 a tauren cooking fire with a big clay pot on a tripod; 11 a hide drying rack with blankets; 12 a tauren memorial of stacked stones and feathers for the ones lost in their homeland.

Row 3 - TRADES AND SERVICES: 13 an herbalist's open stall of living wood hung with drying herbs; 14 an alchemist's table with glowing vials and a mortar; 15 a leatherworker's frame with a stretched hide; 16 a wooden fishing pier section with posts and a moored small boat; 17 a market stall with a leaf awning and baskets of fruit; 18 a wooden stable pen for nightsabers and kodo, with straw.

Row 4 - THE WAKENED: 19 a timber longhouse with a thatched roof, honest and a little crooked; 20 a smaller plank cabin with a flower box; 21 an infirmary of timber with clean linen hung on a line outside; 22 a long timber wall carved all over with small pictures and marks (no letters, no words); 23 a vegetable and flower garden in raised wooden beds; 24 a wash house with a water trough and buckets.

Row 5 - THE WAKENED, SMALL THINGS: 25 a wooden bench under a small shelter with blankets folded on it; 26 a rope-and-plank footbridge section; 27 a stack of firewood and an axe in a stump; 28 a rain barrel and a hand pump made of wood; 29 a quiet cot under a canopy with a sleeping blanket (no person); 30 a wooden meeting-house porch with lanterns.

Row 6 - THE CIRCLE AND THE FACTIONS: 31 a Cenarion Circle banner pole, green and silver with a leaf emblem; 32 a Wakened banner pole, pale blue cloth with an open eye emblem; 33 a moonwell basin, small, ringed with white stones and glowing water; 34 a druid's stone altar with a bowl of glowing seeds; 35 a living thorn barrier, a wall of dark thorns and white blossoms; 36 a warden's post of living wood with a glaive rack.
```

---

## SHEET 4: 9 giant landmarks (magenta)

```
Generate ONE sprite sheet image, 2048x2048, laid out as a strict 3 columns x 3 rows grid = 9 separate giant landmark sprites, each in its own cell of about 682x682. Flat pure #FF00FF magenta background everywhere. Each landmark sits fully inside its own cell with a wide margin and does NOT touch or overlap neighbours or the image edge. No ground plane beyond the landmark's own base, no text, no letters, no labels, no grid lines. NEVER use magenta, pink or purple-pink in the art (violet is fine).

Match the attached references EXACTLY in style: painterly semi-realistic WoW Classic, highly detailed, seen from a slight 3/4 top-down camera angle, consistent soft moonlight from the top-left, crisp clean edges. These are the biggest and most important things in the zone: each must be beautiful and instantly recognisable. Nothing modern or from the real world.

Setting: MOONGLADE, a sacred druid valley under permanent soft moonlight around a great clear lake. Lush, mystical and alive: deep greens, silver bark, silver-blue and violet light, glowing water.

Landmarks are numbered row by row, left to right, top to bottom:

1 THE SHRINE OF REMULOS: a colossal ancient tree on a point of mossy land, its roots forming an open sanctum around a moonwell at its foot, standing stones around it, glowing flowers, the canopy vast and silver-green.
2 THE GREAT MOONWELL OF NIGHTHAVEN: a large circular moonwell of carved pale stone, its water glowing brilliant blue-white, crescent carvings round the rim, flowers and moss at its base, a soft column of light rising from it.
3 THE FLIGHT ROOST: a tall roost of curved living wood with perches and nests for hippogryphs on one side and a sturdy carved timber perch for wind riders on the other, hung with green and silver cloth.
4 THE STORMRAGE BARROW DENS: a great door set into a grassy hillside, framed by huge carved stone and old roots, the stone carved with a sleeping druid's face; the door is closed and grown over by a living ward of dark thorns with white blossoms.
5 THE DREAMING ARCH: a tall arch of pale stone carved with sleeping faces, standing alone in a ring of glowing green-gold flowers; the space inside the arch shimmers faintly green, like heat haze; its stones look warm.
6 THE ISLAND: a small island of pale sand and moss, ringed by tall moonstones, with a still round pool at its centre that is dark and reflects nothing, and a broken stone stair going down into that pool.
7 THE CENARION CIRCLE'S HALL: a grand night elf hall of living wood, its roof a great arch of silver-blue leaves, open sides with carved columns, moon lanterns, the Circle's green and silver banners.
8 THE WAKENED'S LONGHOUSE: the largest building the Wakened have built, a long timber hall with a thatched roof, honest and handmade, lanterns at the door, gardens in front, and a long wall beside it carved with small pictures (no letters).
9 THE FALLS OF ELUNE'ARA: a broad waterfall coming down a mossy cliff into the lake, the water bright silver-blue in the moonlight, mist and small rainbows of moonlight, ferns and flowers on the rocks.
```
