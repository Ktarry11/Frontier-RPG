# Feralas art prompts (sheets 1 to 9)

For `docs/feralas_brief.md`. Kyle, 19 Nov 2026, picked new art for Feralas: three open-world maps (the High Wilderness,
the Forgotten Coast, the Twin Colossals), two towns (Camp Mojache, Feathermoon Stronghold) and the Zukk'ash Hive.

Every prompt below is complete on its own: paste one block and nothing else. Each states the image size, the grid and
cell size, the background, the margin, the style, the camera, the scale rule, the negatives, the never-magenta line,
the Earth line, and every cell numbered row by row.

**The Earth line.** Feralas's Integration touch is the Pacific Northwest rainforest grafted into the giant forest, so
Earth's TREES, PLANTS and ANIMALS are fine where a cell names them. Nothing BUILT from Earth: no buildings, roads,
fences, machines or tools of our world. The settlers' cabins are hand-built from local timber.

| Sheet | What | Image | Grid (cell) | Key |
|---|---|---|---|---|
| 1 | 48 ground, water and wall tiles | 2048x1536 | 8 x 6 (256 x 256) | **NO magenta**: tiles run flush to their edges |
| 2 | 36 nature props: Feralas's giant trees, the Fog Groves, river, coast | 2048x2048 | 6 x 6 (about 341 x 341) | magenta |
| 3 | 36 Camp Mojache buildings and props | 2048x2048 | 6 x 6 (about 341 x 341) | magenta |
| 4 | 36 Feathermoon Stronghold buildings and props | 2048x2048 | 6 x 6 (about 341 x 341) | magenta |
| 5 | 36 wild camps and ruins: ogres, gnolls, naga, Highborne, settlers, the dig | 2048x2048 | 6 x 6 (about 341 x 341) | magenta |
| 6 | 9 giant landmarks | 2048x2048 | 3 x 3 (about 682 x 682) | magenta |
| 7 | 36 creatures | 2048x2048 | 6 x 6 (about 341 x 341) | magenta |
| 8 | 48 Zukk'ash Hive cave tiles | 2048x1536 | 8 x 6 (256 x 256) | **NO magenta** |
| 9 | 36 Zukk'ash Hive cave props | 2048x2048 | 6 x 6 (about 341 x 341) | magenta |

**Priority:** sheet 1 first (the ground is most of the look), then 2, 3 and 6. The towns, creatures and the cave can
follow while the maps are built.

**Already in the game, so not asked for again:** the Grimtotem (Stonetalon's six Grimtotem looks and their tents,
drums, totems and palisade), mountain giants, yetis, two gnolls, two ogres, the naga, sprite darters, stags, wolves,
bears and great cats, a cliff hippogryph, and the silithid workers. Sheets 5 and 7 add Feralas's own.

**Style references to attach (at most 3 per sheet):**
- Sheet 1: `assets/tiles/ashenvale/materials/av_forest_floor.png`, `assets/tiles/stonetalon/materials/st_fog_duff.png`, `assets/tiles/stonetalon/materials/st_canopy_floor.png`
- Sheet 2: `assets/tiles/ashenvale/props/large_canopy_tree.png`, `assets/tiles/stonetalon/props/st_redwood_giant.png`, `assets/tiles/stonetalon/props/st_ferns_big.png`
- Sheet 3: `assets/buildings/mg_tauren_lodge.png`, `assets/buildings/taurajo_lodge.png`, `assets/buildings/mg_tauren_totem.png`
- Sheet 4: `assets/buildings/fw_sentinel_hall.png`, `assets/buildings/fw_sentinel_tower.png`, `assets/buildings/nightelf_house_medium.png`
- Sheet 5: `assets/buildings/dw_ogre_gate.png`, `assets/tiles/felwood/props/fw_highborne_arch.png`, `assets/tiles/stonetalon/props/st_grim_tent.png`
- Sheet 6: `assets/tiles/felwood/props/fw_highborne_arch.png`, `assets/tiles/stonetalon/props/st_redwood_giant.png`, `assets/buildings/mg_shrine_of_remulos.png`
- Sheet 7: `assets/creatures/ogre_1.png`, `assets/creatures/gnoll_1.png`, `assets/creatures/naga_myrmidon_1.png`
- Sheet 8: `assets/tiles/stonetalon/materials/st_beetle_galleries.png`, `assets/tiles/stonetalon/materials/st_dark_seep.png`, `assets/tiles/stonetalon/materials/st_canopy_floor.png`
- Sheet 9: `assets/creatures/silithid_worker_1.png`, `assets/tiles/stonetalon/props/st_lava_tube_mouth.png`, `assets/tiles/stonetalon/props/st_moss_boulder.png`

---

## SHEET 1: 48 ground, water and wall tiles (NO magenta)

```
Generate ONE texture sheet image, 2048x1536, laid out as a strict 8 columns x 6 rows grid = 48 separate seamless ground, water and wall textures, each cell exactly 256x256. Each cell is COMPLETELY FILLED by its texture, edge to edge, touching its neighbours with no gap. No border, no background colour, no magenta, no frames, no gutters, no grid lines, no text, no labels, no numbers. Every texture must TILE SEAMLESSLY with itself on all four sides: no single large feature that would obviously repeat, no emblem, rune or pattern repeated in every tile, no lighting gradient across the cell, flat even illumination, no vignette, no baked shadows, no objects or props standing on the ground. Straight top-down view, no perspective. Nothing built by people from our world: no roads, paving or machines from Earth.

Match the attached reference tiles EXACTLY in style, scale of detail and level of saturation: they are from the same set. Painterly semi-realistic WoW Classic ground texture style, rich but slightly muted, readable at small size, not too busy.

Setting: FERALAS, a vast ancient forest of giant trees on Kalimdor's wet west coast: deep green, humid and old, mossy, misty, with rivers running to a wild grey-green sea. Where our world bled in, part of the forest is now a Pacific Northwest rainforest: coast redwood duff, sword ferns, deep wet moss and fog. Palette: deep forest greens, dark loam browns, moss green, rust-red redwood needles, misty grey-greens; river greens and brown; pale sand and grey-green sea; grey granite; pale night elf stone; and in the last row the raw earth and amber resin of a silithid dig.

Tiles are numbered row by row, left to right, top to bottom:

Row 1 - THE GIANT FOREST: 1 deep green forest floor of moss and fallen leaves, the main ground; 2 dark rich loam threaded with thin roots; 3 lush deep green grass, soft and thick; 4 ground covered in low ferns pressed flat; 5 a thick carpet of wet green moss; 6 leaf litter of huge dark fallen leaves; 7 a muddy forest trail, soft and puddled; 8 deep-shade forest floor, nearly black-green.

Row 2 - THE FOG GROVES (a Pacific Northwest rainforest): 9 coast redwood duff, a deep layer of rust-red needles; 10 sword fern understory pressed flat over damp earth; 11 thick wet moss with small clover-like redwood sorrel; 12 fog-damp grey-green needle duff; 13 soft red-brown rotting wood fibre from fallen nurse logs; 14 mossy small stones in dark soil; 15 a footpath of packed earth and needles worn by feet; 16 cold wet ground of moss and needles silvered by mist.

Row 3 - RIVERS AND THE LOWER WILDS: 17 soft dark river mud; 18 marsh grass, tall and wet; 19 shallow murky green-brown river water over mud; 20 deep slow river water, dark green; 21 reedy marsh water with floating weed; 22 river gravel of rounded grey stones; 23 a fast clear stream running over stones; 24 white foam water at the foot of a waterfall.

Row 4 - THE FORGOTTEN COAST: 25 pale grey-gold beach sand; 26 wet dark sand at the waterline with small shells; 27 shallow clear sea water over sand, grey-green and turquoise; 28 deeper sea water, cold blue-green; 29 deep open ocean, dark grey-blue; 30 tide-pool rock, dark and wet with weed; 31 a shingle beach of grey pebbles; 32 a grey sea cliff face with weed and barnacles near its foot, seen straight on (a wall).

Row 5 - STONE, RUINS AND THE HIGHLANDS: 33 grey granite bedrock, smooth and weathered; 34 a granite cliff face with moss and small ferns in its cracks, seen straight on (a wall); 35 cracked pale Highborne marble paving, overgrown with moss in the joints; 36 old pale paving with faded blue inlay broken and half buried in grass (no repeating symbol); 37 bare trampled dirt with scattered bones, an ogre camp's ground; 38 dry dirt with straw and scraps, a gnoll camp's ground; 39 damp dark cave-mouth stone with grit; 40 open highland meadow grass with small blue and yellow wildflowers.

Row 6 - THE DIG, THE DREAM AND THE TOWNS: 41 raw churned earth freshly dug up by giant insects, dark and lumpy; 42 a hard crust of amber silithid resin over earth; 43 dry dark grey-black sand spilled up from far below; 44 grass dying grey around a dig, patchy and sick; 45 grass touched by the Emerald Dream, green-gold and faintly glowing; 46 a carpet of pale green-gold dream flowers; 47 packed earth of a tauren camp with scraps of hide and straw; 48 pale silver-grey night elf stone paving with moss in the joints.
```

### Slice order (`assets/tiles/feralas/ground/`)

| row | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| 1 | fe_forest_floor | fe_loam_roots | fe_lush_grass | fe_fern_floor | fe_moss | fe_leaf_litter | fe_mud_trail | fe_deep_shade |
| 2 | fe_redwood_duff | fe_swordfern | fe_sorrel_moss | fe_fog_duff | fe_nurse_rot | fe_moss_stones | fe_needle_path | fe_mist_moss |
| 3 | fe_river_mud | fe_marsh_grass | fe_river_shallow | fe_river_deep | fe_reed_water | fe_river_gravel | fe_stream | fe_falls_foam |
| 4 | fe_beach_sand | fe_wet_sand | fe_sea_shallow | fe_sea_mid | fe_sea_deep | fe_tide_rock | fe_shingle | fe_sea_cliff |
| 5 | fe_granite | fe_granite_cliff | fe_marble_moss | fe_inlay_ruin | fe_ogre_dirt | fe_gnoll_dirt | fe_cave_grit | fe_highland_meadow |
| 6 | fe_dug_earth | fe_resin_crust | fe_deep_sand | fe_blight_grass | fe_dream_grass | fe_dream_flowers | fe_camp_earth | fe_elven_paving |

---

## SHEET 2: 36 nature props (MAGENTA KEY)

```
Generate ONE sprite sheet image, 2048x2048, a 6 columns x 6 rows grid = 36 separate sprites, each cell about 341x341. Flat pure #FF00FF magenta background everywhere. Each sprite is ONE single object, centred in its own cell with a wide margin, not touching or overlapping its neighbours or the image edge. No ground, no grass patch, no dirt patch, no water puddle under it unless the prompt puts the water inside the object itself, no cast shadow, no glow halo bleeding onto the background, no text, no labels, no numbers, no grid lines, no frames, no borders. Never use magenta or pink anywhere on the objects themselves.

Match the attached reference props EXACTLY in style, camera angle, outline and level of detail: they are from the same set. Painterly semi-realistic WoW Classic style: strong readable silhouette, soft dark outline, chunky simple shapes legible at small size, consistent soft lighting from the top-left.

Camera: isometric three-quarter view elevated about 45 degrees. EVERY object is turned the same way, front face toward the lower-right. Trees stand upright with the trunk base at the bottom of the cell and the crown at the top, so a character can walk past the trunk with the crown overhead. Consistency of angle across all 36 is critical.

Setting: FERALAS, a vast ancient forest of giant trees on Kalimdor's wet west coast, mossy and misty, with rivers and a wild grey-green sea. Part of it is now a Pacific Northwest rainforest from our world: coast redwoods, Sitka spruce, western red cedar, bigleaf maples hung with moss, sword ferns and nurse logs. Earth's trees and plants are fine here; nothing built. Palette: deep forest greens, dark bark, moss green, rust-red redwood bark, misty grey-greens, river browns, pale sand and grey stone; amber resin and raw earth for the silithid dig; soft green-gold for the Dream.

Objects keep their RELATIVE scale: the giant Feralas trees and the coast redwood are the largest sprites on the sheet; a fern clump, a mushroom cluster and a skull are small. Do not blow each one up to fill its own cell.

Props are numbered row by row, left to right, top to bottom:

Row 1 - FERALAS'S GIANT TREES: 1 a colossal Feralas tree with huge buttress roots and a vast dark green canopy; 2 the same kind of giant tree with a great hollow in its trunk; 3 a tall straight giant tree wrapped in thick vines; 4 an ancient tree whose roots arch high above the ground like a bridge; 5 a giant tree hung with long curtains of grey-green moss; 6 a fallen giant tree, a huge mossy log lying on its side.

Row 2 - THE FOG GROVES: 7 a towering coast redwood with deep rust-red fibrous bark; 8 a tall Sitka spruce, dark blue-green; 9 a western red cedar with drooping lacy fronds; 10 a bigleaf maple draped heavily in moss and small ferns; 11 a big clump of sword ferns; 12 a nurse log with young saplings growing out of its back.

Row 3 - THE UNDERSTORY: 13 a tree fern with a crown of huge fronds; 14 a dense bush of enormous glossy leaves; 15 a tangle of hanging vines and creepers; 16 a cluster of giant forest mushrooms with brown caps; 17 a big mossy boulder; 18 a flowering shrub with orange and white flowers.

Row 4 - RIVER AND COAST: 19 a bed of tall reeds and cattails; 20 a group of round river boulders, wet; 21 a small waterfall over mossy rocks into a little pool (the water drawn inside the rocks); 22 a pile of grey driftwood; 23 a small sea stack of dark rock with a few gulls' nests; 24 tide-pool rocks with starfish and anemones.

Row 5 - THE HIGHLANDS: 25 a weathered granite outcrop; 26 a patch of blue and yellow highland wildflowers; 27 a tall dead snag, silver and bare; 28 a hippogryph nest of branches and feathers on a rock ledge; 29 a rock pile with ferns growing through it; 30 an old stump with shelf fungus on it.

Row 6 - THE DIG AND THE DREAM: 31 a small mound of freshly dug earth with a dark hole in it, made by a giant insect; 32 a dead tree crusted with amber resin; 33 a drift of dark grey-black sand spilled up from below; 34 a patch of softly glowing green-gold dream flowers; 35 a young tree that grew out of the Dream, pale green-gold and faintly shining; 36 an elk skull with great antlers lying in the moss.
```

### Slice order (`assets/tiles/feralas/props/`)

| row | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 1 | fe_giant_tree | fe_giant_tree_hollow | fe_vine_giant | fe_root_bridge_tree | fe_moss_curtain_tree | fe_fallen_giant |
| 2 | fe_coast_redwood | fe_sitka_spruce | fe_red_cedar | fe_bigleaf_maple | fe_swordferns | fe_nurse_log |
| 3 | fe_tree_fern | fe_bigleaf_bush | fe_vine_tangle | fe_giant_mushrooms | fe_moss_boulder | fe_flower_shrub |
| 4 | fe_reeds | fe_river_boulders | fe_small_falls | fe_driftwood | fe_sea_stack | fe_tide_pool |
| 5 | fe_granite_outcrop | fe_highland_flowers | fe_dead_snag | fe_hippogryph_nest | fe_fern_rocks | fe_shelf_stump |
| 6 | fe_dig_mound | fe_resin_tree | fe_dark_sand_drift | fe_dream_flowers | fe_dream_sapling | fe_elk_skull |

---

## SHEET 3: 36 Camp Mojache buildings and props (MAGENTA KEY)

```
Generate ONE sprite sheet image, 2048x2048, a 6 columns x 6 rows grid = 36 separate sprites, each cell about 341x341. Flat pure #FF00FF magenta background everywhere. Each sprite is ONE single building or object, centred in its own cell with a wide margin, not touching or overlapping its neighbours or the image edge. No ground, no grass patch, no dirt patch, no cast shadow, no glow halo bleeding onto the background, no people, no animals, no text, no labels, no numbers, no grid lines, no frames, no borders. Never use magenta or pink anywhere on the buildings or objects themselves.

Match the attached reference buildings EXACTLY in style, camera angle, palette, outline and level of detail: they are from the same set. Painterly semi-realistic WoW Classic style: strong readable silhouette, soft dark outline, chunky simple shapes legible at small size, consistent soft lighting from the top-left.

Camera: isometric three-quarter view elevated about 45 degrees. EVERY building and object is turned the same way, front face toward the lower-right and one side wall toward the lower-left, so two faces of each building are visible. Doors and gates are on the front face. Consistency of angle across all 36 is critical.

Setting: CAMP MOJACHE, a tauren camp in a clearing of the giant Feralas forest that has grown big and crowded since Thunder Bluff fell: the refugees who walked out of Mulgore came here. The OLD CAMP is classic tauren: big hide tents and lodges on tall wooden poles, painted hides in red, ochre, cream and turquoise, carved and painted totems with wings and animal heads, kodo bone and leather. The NEW PART is rougher: lean-tos and patched tents put up in a hurry from mismatched hides, carried things, mourning poles for those left behind. Keep both readable.

Palette: weathered hide cream and tan, painted red, ochre and turquoise, dark timber poles, kodo bone, leather browns, smoke grey; moss and forest green only where the forest touches the wood. Muted, not neon.

Objects keep their RELATIVE scale: the inn longhouse and the chieftain's lodge are the largest sprites on the sheet; a basket, a lantern pole and a water skin rack are small. Do not blow each one up to fill its own cell.

Sprites are numbered row by row, left to right, top to bottom:

Row 1 - THE CAMP'S GREAT TENTS: 1 the inn, a great long tauren hide lodge with a painted door flap and smoke holes; 2 the chieftain's lodge, tall, with painted wings above the door; 3 a big tauren tent-lodge on tall poles; 4 a medium tauren tent painted with bands of red and turquoise; 5 a small round tauren tent; 6 a refugee lean-to of mismatched patched hides on rough poles.

Row 2 - THE CAMP'S TRADES: 7 a wind rider roost: a tall timber platform with a perch, a feed trough and painted hides; 8 a trader's stall under a hide awning with baskets and bundles; 9 a tauren forge of stacked stone with a hide canopy and an anvil; 10 a leatherworker's frame with stretched hides and tools; 11 an herbalist's tent with drying herbs hanging from it; 12 a trainer's open-sided shelter with a weapon rack and a hide mat.

Row 3 - TOTEMS AND SPIRITS: 13 Mojache's great totem, tall and carved with eagle, kodo and wolf, wings spread at the top; 14 a pair of smaller painted totems; 15 a memorial pole for Thunder Bluff hung with carved tokens, feathers and braided hair; 16 a spirit fire in a stone ring; 17 a circle of four big drums around a log seat; 18 a kodo pen of rough timber rails with a water trough.

Row 4 - THE REFUGEES: 19 a cluster of bedrolls and blankets around a small fire; 20 a cooking fire with clay pots on a stone ring; 21 a stack of travel packs and bundles; 22 a kodo travois loaded with belongings; 23 a rack of water skins and gourds; 24 a stack of woven baskets.

Row 5 - THE CAMP'S DEFENCES: 25 a straight section of tall timber palisade with painted hides hung on it; 26 a palisade corner; 27 the camp gate, two great painted totems with a hide lintel; 28 a timber watchtower with a hide roof; 29 a barricade of sharpened stakes; 30 a hunter's trophy rack with an ogre's tusk, gnoll pelts and antlers.

Row 6 - SMALL PIECES: 31 a tauren-style mailbox, a carved post with a hide pouch and a little painted roof; 32 a well of stacked stone with a timber frame and a bucket; 33 a pile of split firewood; 34 a frame of hides drying; 35 a lantern pole with a hide-shaded lantern; 36 a set of wind chimes of bone and feathers on a carved post.
```

### Slice order (`assets/buildings/`)

| row | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 1 | moj_inn | moj_chief_lodge | moj_tent_lodge | moj_tent_medium | moj_tent_small | moj_lean_to |
| 2 | moj_windrider_roost | moj_trader_stall | moj_forge | moj_leather_frame | moj_herbalist_tent | moj_trainer_shelter |
| 3 | moj_great_totem | moj_totem_pair | moj_memorial_pole | moj_spirit_fire | moj_drum_circle | moj_kodo_pen |
| 4 | moj_bedrolls | moj_cookfire | moj_packs | moj_travois | moj_water_skins | moj_baskets |
| 5 | moj_palisade | moj_palisade_corner | moj_gate | moj_watchtower | moj_stakes | moj_trophy_rack |
| 6 | moj_mailbox | moj_well | moj_firewood | moj_hide_frame | moj_lantern_pole | moj_wind_chimes |

---

## SHEET 4: 36 Feathermoon Stronghold buildings and props (MAGENTA KEY)

```
Generate ONE sprite sheet image, 2048x2048, a 6 columns x 6 rows grid = 36 separate sprites, each cell about 341x341. Flat pure #FF00FF magenta background everywhere. Each sprite is ONE single building or object, centred in its own cell with a wide margin, not touching or overlapping its neighbours or the image edge. No ground, no grass patch, no dirt patch, no water under it unless the prompt puts the water inside the object itself, no cast shadow, no glow halo bleeding onto the background, no people, no animals, no text, no labels, no numbers, no grid lines, no frames, no borders. Never use magenta or pink anywhere on the buildings or objects themselves (violet and lavender are fine).

Match the attached reference buildings EXACTLY in style, camera angle, palette, outline and level of detail: they are from the same set. Painterly semi-realistic WoW Classic style: strong readable silhouette, soft dark outline, chunky simple shapes legible at small size, consistent soft lighting from the top-left.

Camera: isometric three-quarter view elevated about 45 degrees. EVERY building and object is turned the same way, front face toward the lower-right and one side wall toward the lower-left, so two faces of each building are visible. Doors and gates are on the front face. Consistency of angle across all 36 is critical.

Setting: FEATHERMOON STRONGHOLD, the night elf Sentinels' island fortress off the coast of Feralas: a walled stronghold of pale silver-grey stone and dark curved wood, with sweeping crescent rooftops, violet and deep blue cloth, silver moon lanterns, owl and moon carvings, and living trees growing through it. It is a military post, disciplined and quiet, with a harbour for the boats from the mainland.

Palette: pale silver-grey stone, dark purple-brown curved wood, deep violet and midnight blue cloth, silver trim, soft white-blue moonlight from the lanterns, moss green. Muted, not neon.

Objects keep their RELATIVE scale: the great hall, the tall sentinel tower and the crossing boat are the largest sprites on the sheet; a lantern, a bench and a weapon rack are small. Do not blow each one up to fill its own cell.

Sprites are numbered row by row, left to right, top to bottom:

Row 1 - THE FORTRESS: 1 the great hall of the Sentinels, pale stone with a sweeping crescent roof; 2 a tall slender sentinel tower with a lookout at the top; 3 a straight section of pale stone fortress wall with a crescent crenellation; 4 a round wall tower for the corners; 5 the stronghold's grand gate, a tall arch with carved owls; 6 a long barracks of stone and curved wood.

Row 2 - THE SERVICES: 7 the inn, a night elf house of curved wood and stone with a lantern by the door; 8 a hippogryph roost: a raised round platform with perches and a feather-trimmed canopy; 9 a moonwell, a round basin of pale stone with glowing blue-white water inside its rim; 10 an armoury with glaives and shields on its wall; 11 a bowyer's workshop with bows and arrow bundles; 12 the quartermaster's pavilion under violet cloth.

Row 3 - THE HARBOUR: 13 a straight section of pier of dark wood on pale stone posts; 14 the end of a pier with a tall moon lantern; 15 a small night elf boat with a curved prow, moored; 16 the crossing boat, a larger night elf vessel with a single crescent sail; 17 a stack of cargo crates and barrels with violet cloth; 18 a boathouse of curved wood over the water's edge.

Row 4 - ELVEN LIFE: 19 a silver moon lantern on a tall curved post; 20 a small night elf house built around a living tree; 21 a garden bed of moon-lilies and herbs in a stone border; 22 a statue of a Sentinel huntress with a bow; 23 a statue of an owl on a tall pillar; 24 an archery range of three straw targets on wooden stands.

Row 5 - THE GARRISON: 25 a weapon rack of moon glaives; 26 a rack of bows and quivers; 27 a nightsaber stable with a curved roof and a water trough; 28 a Sentinel field tent of violet cloth; 29 a brazier burning with a pale silver flame; 30 a tall banner of Feathermoon in violet and silver showing a crescent moon and a feather (no text).

Row 6 - SMALL PIECES: 31 an elven mailbox, a slender curved post with a silver box; 32 a curved wooden bench; 33 a stone well with a crescent arch over it; 34 an arch of living vines with small white flowers; 35 a lookout platform built into the branches of a tree; 36 a stack of bundled arrows and supply chests.
```

### Slice order (`assets/buildings/`)

| row | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 1 | fm_great_hall | fm_sentinel_tower | fm_wall | fm_wall_tower | fm_gate | fm_barracks |
| 2 | fm_inn | fm_hippogryph_roost | fm_moonwell | fm_armoury | fm_bowyer | fm_quartermaster |
| 3 | fm_pier | fm_pier_end | fm_small_boat | fm_crossing_boat | fm_cargo | fm_boathouse |
| 4 | fm_moon_lantern | fm_tree_house | fm_moon_garden | fm_huntress_statue | fm_owl_pillar | fm_archery_range |
| 5 | fm_glaive_rack | fm_bow_rack | fm_nightsaber_stable | fm_field_tent | fm_silver_brazier | fm_banner |
| 6 | fm_mailbox | fm_bench | fm_well | fm_vine_arch | fm_tree_lookout | fm_arrow_supplies |

---

## SHEET 5: 36 wild camps and ruins (MAGENTA KEY)

```
Generate ONE sprite sheet image, 2048x2048, a 6 columns x 6 rows grid = 36 separate sprites, each cell about 341x341. Flat pure #FF00FF magenta background everywhere. Each sprite is ONE single building or object, centred in its own cell with a wide margin, not touching or overlapping its neighbours or the image edge. No ground, no grass patch, no dirt patch, no water under it unless the prompt puts the water inside the object itself, no cast shadow, no glow halo bleeding onto the background, no people, no creatures, no text, no labels, no numbers, no grid lines, no frames, no borders. Never use magenta or pink anywhere on the objects themselves (coral is pale peach and white, never magenta).

Match the attached reference props EXACTLY in style, camera angle, outline and level of detail: they are from the same set. Painterly semi-realistic WoW Classic style: strong readable silhouette, soft dark outline, chunky simple shapes legible at small size, consistent soft lighting from the top-left.

Camera: isometric three-quarter view elevated about 45 degrees. EVERY object is turned the same way, front face toward the lower-right and one side toward the lower-left. Doors and openings are on the front face. Consistency of angle across all 36 is critical.

Setting: the wild places of FERALAS, a giant mossy forest on a wild coast. Row 1 is the GORDUNNI OGRES' camps: huge, crude and filthy, logs, hides, bones, rusted iron and looted Highborne stone. Row 2 is the WOODPAW GNOLLS' camps: small, ramshackle, branches, straw, bones and feathers. Row 3 is the NAGA of the Forgotten Coast: coral, shells, kelp and wet stone, pale teal glows, and Highborne relics they have dug up. Row 4 is the ancient HIGHBORNE ruins: pale marble and faded blue, ten thousand years old, cracked and swallowed by moss. Row 5 is the TRANSPLANT SETTLERS of the Fog Groves: people from our world living under the redwoods in cabins they built by hand from local timber, simple and honest, nothing manufactured. Row 6 is the SILITHID DIG breaking the surface: raw earth, amber resin, chitin and dark sand.

Objects keep their RELATIVE scale: the ogre hut, the naga shrine and the large hive mound are the largest sprites on the sheet; a snare, a skull pile and a chopping block are small. Do not blow each one up to fill its own cell.

Sprites are numbered row by row, left to right, top to bottom:

Row 1 - THE GORDUNNI: 1 a big ogre hut of rough logs and stitched hides with tusks over the door; 2 a crude ogre tent of hides on thick poles; 3 a big ogre bonfire in a ring of boulders; 4 an ogre cooking spit with a whole roasting boar; 5 an ogre totem of stacked skulls and a broken Highborne statue head; 6 an ogre camp gate of tree trunks lashed with chains.

Row 2 - THE WOODPAW: 7 a gnoll hut of bent branches and straw; 8 a small gnoll tent of ragged hides; 9 a gnoll totem with feathers, beads and a hyena skull; 10 a pile of gnawed bones; 11 a gnoll snare of rope and a bent sapling; 12 a rickety gnoll lookout platform on stilts.

Row 3 - THE NAGA: 13 a naga shrine grown out of coral on old wet stone, glowing pale teal; 14 a naga tent of kelp and shells over whalebone; 15 a giant clam-shell basin holding glowing water (the water drawn inside the shell); 16 a naga coral totem with a pearl at the top; 17 a pile of dug-up Highborne crates, urns and statue pieces; 18 a naga brazier of coral with a pale teal flame.

Row 4 - THE HIGHBORNE RUINS: 19 a broken Highborne arch of pale marble, one side fallen; 20 a toppled marble column lying in pieces; 21 a standing marble column wrapped in ivy; 22 the giant head of a Highborne statue lying in the moss; 23 a broken marble stair going nowhere; 24 a ruined wall section with an empty arched window.

Row 5 - THE SETTLERS: 25 a log cabin built by hand with a shake roof and a stone chimney; 26 a small one-room cabin with smoke rising from its chimney; 27 a short rail fence of split logs; 28 a woodpile with a chopping block and an axe stuck in it; 29 a small vegetable garden in a log-edged bed; 30 a hand-built smokehouse of logs with fish hanging inside the open door.

Row 6 - THE DIG: 31 a large hive mound of dug earth and amber resin with a dark tunnel opening in its front; 32 a tall spire of hardened amber resin; 33 a cluster of silithid eggs half sunk in resin; 34 the broken edge of a trench dug through the forest floor, roots hanging into it; 35 a dead tree being pulled down into a sinking hole; 36 a shed silithid husk, empty and translucent amber.
```

### Slice order (`assets/tiles/feralas/props/`)

| row | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 1 | fe_ogre_hut | fe_ogre_tent | fe_ogre_bonfire | fe_ogre_spit | fe_ogre_skull_totem | fe_ogre_gate |
| 2 | fe_gnoll_hut | fe_gnoll_tent | fe_gnoll_totem | fe_bone_pile | fe_gnoll_snare | fe_gnoll_lookout |
| 3 | fe_naga_shrine | fe_naga_tent | fe_clam_basin | fe_coral_totem | fe_dug_relics | fe_coral_brazier |
| 4 | fe_highborne_arch | fe_fallen_column | fe_ivy_column | fe_statue_head | fe_broken_stair | fe_ruin_window |
| 5 | fe_cabin | fe_small_cabin | fe_rail_fence | fe_woodpile | fe_garden_bed | fe_smokehouse |
| 6 | fe_hive_mound | fe_resin_spire | fe_egg_cluster | fe_trench_edge | fe_sinking_tree | fe_shed_husk |

---

## SHEET 6: 9 giant landmarks (MAGENTA KEY)

```
Generate ONE sprite sheet image, 2048x2048, a 3 columns x 3 rows grid = 9 separate landmark sprites, each cell about 682x682. Flat pure #FF00FF magenta background everywhere. Each landmark is ONE single structure, centred in its own cell with a wide margin, not touching or overlapping its neighbours or the image edge. No ground plane beyond the landmark's own base, no cast shadow, no glow halo bleeding onto the background, no people, no creatures, no text, no labels, no numbers, no grid lines, no frames, no borders. Never use magenta or pink anywhere on the landmarks themselves.

Match the attached references EXACTLY in style, camera angle, outline and level of detail: they are from the same set. Painterly semi-realistic WoW Classic style: strong readable silhouette, soft dark outline, chunky shapes legible at small size, consistent soft lighting from the top-left.

Camera: isometric three-quarter view elevated about 45 degrees. EVERY landmark is turned the same way, front face toward the lower-right. Entrances and doorways are on the front face and clearly readable as a way in. Consistency of angle across all 9 is critical.

Setting: FERALAS, a vast ancient forest of giant trees on Kalimdor's wet west coast, with Highborne ruins swallowed by moss, a wild grey-green sea, ogres, naga and giants, a silithid hive digging under the forest, and a great tree whose roots reach into the Emerald Dream. Nothing built by people from our world.

These are the zone's giant set pieces: each one fills most of its cell.

Landmarks are numbered row by row, left to right, top to bottom:

Row 1: 1 one of the TWIN COLOSSALS, a vast natural arch of grey granite rising out of the forest, moss and small trees on its top and waterfalls running down its legs; 2 the great gate of DIRE MAUL, a towering Highborne gateway of pale stone in a ruined fortress wall, crudely barricaded by ogres with tree trunks, chains and skulls, the doorway dark; 3 the mouth of the ZUKK'ASH HIVE, a huge hive mound of dug earth and amber resin pushed up through the forest floor, giant roots torn and bent around it, a wide dark tunnel opening in its front.

Row 2: 4 the DREAM BOUGH, a colossal ancient tree whose great roots arch over a hollow glowing soft green-gold, the shimmering way into the Dream between them, dream flowers all around its base; 5 THE WAY DOWN FROM THE ASPENS, a mountain pass opening out of grey Rocky Mountain cliffs, golden aspens growing on the rock above and giant dark green Feralas trees beginning at its foot, a trail running out of it toward the viewer; 6 FEATHERMOON LANDING, a night elf gatehouse and pier on the mainland shore, pale silver stone and dark curved wood with a moon lantern, where the boats leave for the island.

Row 3: 7 the cave mouth of RAGE SCAR HOLD, a dark wide cave opening in a mossy granite hillside, gnawed bones and torn earth outside it, claw marks on the rock; 8 a ruined HIGHBORNE TOWER on the Isle of Dread, broken off halfway up, pale marble streaked with dark stains, great chimaera nests of branches and bones on its top; 9 the broken dome of the RUINS OF ISILDIEN, a vast cracked pale marble dome half fallen in, ivy and moss pouring over it, a dark doorway in its front.
```

### Slice order (`assets/buildings/`)

| row | 1 | 2 | 3 |
|---|---|---|---|
| 1 | fe_twin_colossal | fe_dire_maul_gate | fe_writhing_deep_mouth |
| 2 | fe_dream_bough | fe_aspen_pass | fe_feathermoon_landing |
| 3 | fe_rage_scar_mouth | fe_dread_tower | fe_isildien_dome |

---

## SHEET 7: 36 Feralas creatures (MAGENTA KEY)

```
Generate ONE sprite sheet image, 2048x2048, a 6 columns x 6 rows grid = 36 separate creature sprites, each cell about 341x341. Flat pure #FF00FF magenta background everywhere. Each creature is ONE single figure, centred in its own cell with a wide margin, not touching or overlapping its neighbours or the image edge. No ground, no dirt patch, no water under it, no cast shadow, no glow halo bleeding onto the background, no text, no labels, no numbers, no grid lines, no frames, no borders. Never use magenta or pink anywhere on the creatures themselves.

Match the attached reference creatures EXACTLY in style, camera angle, outline and level of detail: they are from the same set. Painterly semi-realistic WoW Classic style: strong readable silhouette, soft dark outline, chunky simple shapes legible at small size, consistent soft lighting from the top-left.

Camera: every creature faces three-quarters toward the lower-right, full body, feet, tail or base included and nothing cropped. Flying creatures hover with their lowest point near the bottom of the cell. Consistency of angle across all 36 is critical.

Setting: FERALAS, a vast ancient forest of giant trees on Kalimdor's wet west coast, with Highborne ruins, a wild grey-green sea, and a silithid hive digging under it all. Part of the forest is now a Pacific Northwest rainforest from our world, so a few of Earth's animals live in it. Palette: ogre grey-blue and tan skin with dirty leather and rusted iron; gnoll mangy brown and grey; naga teal, sea green and coral; granite grey and moss for the giants; yeti red-brown; tawny gold and grey for the beasts; amber, black and brown chitin for the silithids.

Creatures keep their RELATIVE scale: a silithid swarmer and a wolf are small, an ogre and a yeti are big, the giants and the hive's queen are the largest sprites on the sheet. Do not blow each one up to fill its own cell.

Creatures are numbered row by row, left to right, top to bottom:

Row 1 - THE GORDUNNI OGRES: 1 a Gordunni brute with a tree-trunk club and a hide loincloth; 2 a two-headed Gordunni ogre mage in ragged robes, one head reading a stolen book; 3 a Gordunni shaman with a staff of skulls and feathers; 4 a Gordunni warlord in mismatched looted Highborne armour with a great axe; 5 a Gordunni mauler, huge and chained, with iron knuckles; 6 a Gordunni ogre lord, the largest ogre on the sheet, crowned with a bent Highborne circlet.

Row 2 - THE WOODPAW GNOLLS: 7 a Woodpaw reaver with a crude axe; 8 a Woodpaw trapper with a net and a coil of rope; 9 a Woodpaw mystic with a feathered headdress and a bone rattle; 10 a Woodpaw alpha, bigger and scarred, with a spiked club; 11 a Woodpaw brute with a log shield; 12 a lean spotted hyena that runs with the gnolls.

Row 3 - THE NAGA OF THE FORGOTTEN COAST: 13 a naga wave-raider with a barbed harpoon; 14 a naga ruin-digger with a pick and a sack of relics; 15 a naga tide priestess with a coral staff and swirling water; 16 a three-headed coastal hydra, scaly and dripping; 17 a makrura, a lobster-like sea creature walking on its tail claws; 18 a naga coral guardian in coral armour with a shield.

Row 4 - THE GIANTS, THE ISLE AND THE HIGHLANDS: 19 a forest giant, huge, made of granite and moss with a small tree growing from its shoulder; 20 a sea giant, tall and barnacled, with weed hanging from it; 21 a chimaera, a two-headed winged beast with scaled hide; 22 a chimaera matriarch, bigger, darker, with torn wings; 23 a Frayfeather skystalker, a tawny and white hippogryph; 24 a Frayfeather windwing, a grey-blue hippogryph with long tail feathers.

Row 5 - THE WILD: 25 a Rage Scar yeti, shaggy red-brown with long arms; 26 a Rage Scar matriarch, bigger with grey streaks; 27 a lean grey longtooth wolf; 28 an ironfur bear, big and dark brown with a silver back; 29 a Feralas stalker, a big green-striped forest cat; 30 a Roosevelt elk from the Fog Groves, a huge bull elk with great antlers (an animal from our world).

Row 6 - THE SILITHIDS OF THE ZUKK'ASH HIVE: 31 a silithid tunneler with huge digging forelimbs caked in earth; 32 a silithid hive warrior, armoured in black and amber chitin; 33 a winged silithid swarmer, small and fast; 34 a silithid ravager with scything blade-arms; 35 a silithid resin-spitter, swollen and dripping amber; 36 the Deep Mother, an enormous silithid queen with digging mandibles and a swollen egg sac, the largest figure on the sheet.
```

The boss and rare names are working names for the art.

### Slice order (`assets/creatures/`)

| row | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 1 | fe_gordunni_brute | fe_gordunni_mage | fe_gordunni_shaman | fe_gordunni_warlord | fe_gordunni_mauler | fe_gordunni_lord |
| 2 | fe_woodpaw_reaver | fe_woodpaw_trapper | fe_woodpaw_mystic | fe_woodpaw_alpha | fe_woodpaw_brute | fe_hyena |
| 3 | fe_naga_raider | fe_naga_digger | fe_naga_priestess | fe_coast_hydra | fe_makrura | fe_naga_guardian |
| 4 | fe_forest_giant | fe_sea_giant | fe_chimaera | fe_chimaera_matriarch | fe_skystalker | fe_windwing |
| 5 | fe_rage_scar_yeti | fe_rage_scar_matriarch | fe_longtooth_wolf | fe_ironfur_bear | fe_feralas_stalker | fe_roosevelt_elk |
| 6 | fe_silithid_tunneler | fe_silithid_warrior | fe_silithid_swarmer | fe_silithid_ravager | fe_resin_spitter | fe_boss_deep_mother |

---

## SHEET 8: 48 Zukk'ash Hive cave tiles (NO magenta)

```
Generate ONE texture sheet image, 2048x1536, laid out as a strict 8 columns x 6 rows grid = 48 separate seamless cave floor, wall and water textures, each cell exactly 256x256. Each cell is COMPLETELY FILLED by its texture, edge to edge, touching its neighbours with no gap. No border, no background colour, no magenta, no frames, no gutters, no grid lines, no text, no labels, no numbers. Every texture must TILE SEAMLESSLY with itself on all four sides: no single large feature that would obviously repeat, no emblem or pattern repeated in every tile, no lighting gradient across the cell, flat even illumination, no vignette, no baked shadows, no objects or props standing on the ground. Straight top-down view, no perspective.

Match the attached reference tiles EXACTLY in style, scale of detail and level of saturation: they are from the same set. Painterly semi-realistic WoW Classic cave texture style, dark and moody but readable at small size, not too busy.

Setting: THE ZUKK'ASH HIVE, a silithid hive dug under the giant forest of Feralas. Near the top it is wet forest earth, giant roots and moss coming through the walls; in the middle it is the hive, raw dug earth, amber resin, chitin and eggs; at the very back it is a long tunnel the silithids are still digging, where the wet earth gives way to dry dark grey-black sand, pale glowing fungus and old buried stone, the ground of the deep underground they are digging toward. Palette: dark wet loam, root brown, moss green; amber resin and honey-gold glows, black and brown chitin; dry grey-black sand, pale blue-white and violet fungus glows, ash grey stone.

Tiles are numbered row by row, left to right, top to bottom:

Row 1 - THE UPPER BURROWS: 1 dark wet forest earth, the main cave floor; 2 earth threaded with thick giant roots; 3 damp earth with moss creeping in from above; 4 packed burrow floor worn smooth by many legs; 5 earth littered with broken chitin; 6 muddy earth with shallow puddles; 7 a wall of dark earth and stone with roots hanging out of it (a cave wall); 8 a wall of earth crusted with resin (a cave wall).

Row 2 - THE HIVE: 9 a hard floor of amber resin over earth; 10 resin floor with small glowing honey-gold pools set in it; 11 a floor of silithid eggs half sunk in resin; 12 resin webbing stretched over the floor; 13 soft dug soil heaped in ridges; 14 a chitin-paved floor of shed plates pressed into resin; 15 a hive wall of layered resin and earth, honeycombed (a cave wall); 16 a dark hive wall of black chitin and resin (a cave wall).

Row 3 - THE QUEEN'S CHAMBER: 17 a floor of thick old resin, dark amber, polished; 18 resin floor with veins of glowing gold running through it; 19 a floor of cracked egg shells; 20 a floor of pale larval slime over resin; 21 earth stained dark and wet; 22 a floor of bones and chitin half buried; 23 a high chamber wall of resin pillars fused together (a cave wall); 24 a deep dark pit edge of crumbling earth (seen from above, falling away).

Row 4 - WATER AND SEEP: 25 shallow dark water over earth; 26 deep black water; 27 water with a film of amber resin floating on it; 28 a seep of muddy water through roots; 29 wet stone glistening; 30 a mossy wet stone floor; 31 a wall of wet rock with water running down it (a cave wall); 32 stagnant green water with scum.

Row 5 - THE TUNNEL: 33 a raw freshly dug tunnel floor, loose earth and gouges; 34 dug earth giving way to dry grey sand; 35 dry dark grey-black sand; 36 dark sand with small pale glowing mushrooms; 37 dark sand with buried pale stone blocks showing through; 38 compacted sand marked by giant clawed tracks; 39 a tunnel wall of dug earth with claw gouges (a cave wall); 40 a tunnel wall of dark packed sand and stone (a cave wall).

Row 6 - THE DEEP END: 41 black sand with patches of pale blue-white glowing fungus; 42 black sand with violet glowing fungus; 43 ash grey stone floor, old and smooth; 44 cracked ash grey stone with fungus in the cracks; 45 a floor of glowing fungal mat, blue-white and soft; 46 dark sand with fallen resin chunks; 47 a wall of dark stone with glowing fungus growing on it (a cave wall); 48 a wall of black sand and buried ancient stone (a cave wall).
```

### Slice order (`assets/tiles/feralas/writhing_deep/`)

| row | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| 1 | wd_earth | wd_root_earth | wd_moss_earth | wd_burrow | wd_chitin_earth | wd_mud | wd_root_wall | wd_resin_wall |
| 2 | wd_resin | wd_resin_pools | wd_egg_floor | wd_webbing | wd_dug_ridges | wd_chitin_floor | wd_honeycomb_wall | wd_chitin_wall |
| 3 | wd_old_resin | wd_gold_veins | wd_egg_shells | wd_larval_slime | wd_stained_earth | wd_bone_floor | wd_pillar_wall | wd_pit_edge |
| 4 | wd_water_shallow | wd_water_deep | wd_resin_water | wd_seep | wd_wet_stone | wd_moss_stone | wd_wet_wall | wd_scum_water |
| 5 | wd_tunnel_dug | wd_earth_to_sand | wd_dark_sand | wd_sand_mushrooms | wd_sand_blocks | wd_claw_tracks | wd_gouged_wall | wd_sand_wall |
| 6 | wd_blue_fungus_sand | wd_violet_fungus_sand | wd_ash_stone | wd_cracked_ash | wd_fungal_mat | wd_resin_chunks | wd_fungus_wall | wd_buried_wall |

---

## SHEET 9: 36 Zukk'ash Hive cave props (MAGENTA KEY)

```
Generate ONE sprite sheet image, 2048x2048, a 6 columns x 6 rows grid = 36 separate sprites, each cell about 341x341. Flat pure #FF00FF magenta background everywhere. Each sprite is ONE single object, centred in its own cell with a wide margin, not touching or overlapping its neighbours or the image edge. No ground, no floor patch, no water under it unless the prompt puts the water inside the object itself, no cast shadow, no glow halo bleeding onto the background, no people, no creatures, no text, no labels, no numbers, no grid lines, no frames, no borders. Never use magenta or pink anywhere on the objects themselves.

Match the attached references EXACTLY in style, camera angle, outline and level of detail: they are from the same set. Painterly semi-realistic WoW Classic style: strong readable silhouette, soft dark outline, chunky simple shapes legible at small size, consistent soft lighting from the top-left.

Camera: isometric three-quarter view elevated about 45 degrees. EVERY object is turned the same way, front face toward the lower-right. Openings face the front. Consistency of angle across all 36 is critical.

Setting: THE ZUKK'ASH HIVE, a silithid hive dug under the giant forest of Feralas: wet earth and giant roots near the top, amber resin, chitin and eggs in the hive, and at the back a long tunnel being dug toward the deep underground, where the earth turns to dry dark sand, pale glowing fungus and old buried stone. Palette: dark loam and root brown, moss green, amber resin with honey-gold glows, black and brown chitin, dry grey-black sand, pale blue-white and violet fungus glows.

Objects keep their RELATIVE scale: the resin pillar, the queen's egg throne and the tunnel mouth are the largest sprites on the sheet; an egg, a mushroom and a husk are small. Do not blow each one up to fill its own cell.

Props are numbered row by row, left to right, top to bottom:

Row 1 - ROOTS AND EARTH: 1 a giant tree root pushing out of a cave wall and down into the floor; 2 a curtain of thin roots hanging down; 3 a heap of loose dug earth; 4 a boulder half dug out of the earth; 5 a mossy stone with a trickle of water; 6 a collapsed burrow, earth and roots fallen in.

Row 2 - THE HIVE: 7 a thick pillar of amber resin from floor to ceiling; 8 a smaller resin column, drippy; 9 a cluster of silithid eggs in resin; 10 a single large glowing egg; 11 a resin cocoon holding a wrapped forest animal; 12 a pile of shed chitin plates.

Row 3 - THE HIVE'S WORK: 13 a mound of honey-gold resin with a glowing pool on top (the pool inside the mound); 14 a resin vat-like basin holding larvae (the larvae inside the basin); 15 a heap of gnawed bones and a broken ogre club; 16 a trail of resin webbing strung between two stalks; 17 a resin node pulsing with gold light; 18 a broken resin wall section.

Row 4 - THE QUEEN'S CHAMBER: 19 the Deep Mother's egg throne, a great mound of resin and eggs; 20 a ring of fused resin spires; 21 a giant cast-off carapace of an earlier queen; 22 a resin pool of glowing gold (the pool drawn inside its rim); 23 a heap of cracked giant eggs; 24 a tall chitin totem of stacked plates.

Row 5 - THE TUNNEL: 25 a dug tunnel support of packed earth and resin; 26 a sand drift banked against rock; 27 a cluster of pale blue-white glowing mushrooms; 28 a cluster of violet glowing mushrooms; 29 an old buried stone block half uncovered, carved with worn lines; 30 a giant claw-scored boulder.

Row 6 - THE WAY THROUGH: 31 the tunnel's dug mouth into the deep, a wide hole in dark sand and stone, dry wind coming out of it; 32 a resin-sealed side passage, a round plug of amber in the wall; 33 a mound of dark sand with fungus growing on it; 34 a broken silithid digging limb, huge, left behind; 35 a small rock basin of still black water (the water inside the rim); 36 a heap of glowing fungus and old bones.
```

### Slice order (`assets/tiles/feralas/writhing_deep_props/`)

| row | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 1 | wd_wall_root | wd_root_curtain | wd_dirt_heap | wd_dug_boulder | wd_trickle_stone | wd_collapsed_burrow |
| 2 | wd_resin_pillar | wd_resin_column | wd_egg_cluster | wd_glow_egg | wd_cocoon | wd_chitin_pile |
| 3 | wd_resin_mound | wd_larva_basin | wd_bone_heap | wd_web_strands | wd_resin_node | wd_broken_resin_wall |
| 4 | wd_egg_throne | wd_spire_ring | wd_old_carapace | wd_gold_pool | wd_cracked_eggs | wd_chitin_totem |
| 5 | wd_tunnel_support | wd_sand_drift | wd_blue_mushrooms | wd_violet_mushrooms | wd_buried_block | wd_scored_boulder |
| 6 | wd_tunnel_mouth | wd_sealed_passage | wd_fungus_sand_mound | wd_digging_limb | wd_black_basin | wd_fungus_bones |
