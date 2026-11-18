# Azshara art prompts (sheets 1 to 6)

For `docs/azshara_brief.md`. Kyle, 17 Nov 2026: "we can get up to 6 art sheets!", split as he approved: ground tiles,
props and Highborne ruins, Talrendis Landing, Timbermaw Hold, creatures, the two dungeons.

Rewritten the same day. Kyle: "redo the art prompts and make them with the rules baked into each one! Dont skip steps
please". Every prompt below is complete on its own: paste one block and nothing else. Each one states the image size,
the grid and the cell size, the background, the margin, the style, the camera, the scale rule, the full negative
list, the never-magenta line, and every cell numbered row by row.

| Sheet | What | Image | Grid (cell) | Key |
|---|---|---|---|---|
| 1 | 48 ground and wall tiles | 2048x1536 | 8 x 6 (256 x 256) | **NO magenta**: tiles run flush to their edges |
| 2 | 36 open-world props, trees and Highborne ruins | 2048x2048 | 6 x 6 (about 341 x 341) | magenta |
| 3 | 36 Talrendis Landing buildings and props | 2048x2048 | 6 x 6 (about 341 x 341) | magenta |
| 4 | 36 Timbermaw Hold buildings and props | 2048x2048 | 6 x 6 (about 341 x 341) | magenta |
| 5 | 36 creatures | 2048x2048 | 6 x 6 (about 341 x 341) | magenta |
| 6 | 24 dungeon set pieces and 12 bosses | 2048x2048 | 6 x 6 (about 341 x 341) | magenta |

**Priority for the first playable slice (West Azshara, Talrendis Landing, Timbermaw Hold):** sheets 1, 3 and 4
first, then 2. Creatures and dungeons can come while the slice is built.

**Already in the game, so not asked for again:**
- **Buildings:** the blood elf set (`be_*`) and the orc town sets (`orc_*`). Sheet 3 is only the salvage camp's own
  mixed pieces.
- **Timbermaw:** the Timbermaw lodge and totem (`fw_timbermaw_*`), the Ashenvale furbolg lodge, bonfire, totem and den
  mouth, and six furbolg NPC looks. Sheet 4 is the caldera city's bigger pieces.
- **Creatures:** Felwood's satyrs, felguard and infernal; three naga, a mana wyrm, an arcane elemental, dragon whelps
  and two Plaguelands ghosts. Sheet 5 adds Azshara's own.

**Style references to attach (at most 3 per sheet):**
- Sheet 1: `av_forest_floor.png`, `av_elven_paving.png`, `st_ash_plain.png`
- Sheet 2: `large_canopy_tree.png`, `fw_highborne_arch.png`, `fw_fallen_statue.png`
- Sheet 3: `orc_inn.png`, `be_pavilion.png`, `orc_quartermaster_post.png`
- Sheet 4: `fw_timbermaw_lodge.png`, `fw_timbermaw_totem.png`, `ash_furbolg_lodge.png`
- Sheet 5: `fw_satyr_trickster.png`, `naga_myrmidon_1.png`, `fw_deadwood_shaman.png`
- Sheet 6: `fw_boss_demon_lord.png`, `fw_fel_mushrooms.png`, `naga_warrior.png`

---

## SHEET 1: 48 ground and wall tiles (NO magenta)

```
Generate ONE texture sheet image, 2048x1536, laid out as a strict 8 columns x 6 rows grid = 48 separate seamless ground and wall textures, each cell exactly 256x256. Each cell is COMPLETELY FILLED by its texture, edge to edge, touching its neighbours with no gap. No border, no background colour, no magenta, no frames, no gutters, no grid lines, no text, no labels, no numbers. Every texture must TILE SEAMLESSLY with itself on all four sides: no single large feature that would obviously repeat, no lighting gradient across the cell, flat even illumination, no vignette, no baked shadows, no objects or props standing on the ground. Straight top-down view, no perspective.

Match the attached reference tiles EXACTLY in style, scale of detail and level of saturation: they are from the same set. Painterly semi-realistic WoW Classic ground texture style, muted and slightly desaturated, readable at small size, not too busy.

Setting: AZSHARA, the ancient night elf coast, forever in autumn, where the drowned Highborne city of Zin-Azshari is rising out of the sea. Rows 1 to 3 palette: warm red, rust, burnt orange and gold leaves over dark loam, grey mountain stone, mossy greens kept low. Rows 4 to 6 palette: pale cream marble with gold, then the drowned city's wet white marble, silver, pale teal, verdigris and coral pink, and dark sea-teal water.

Tiles are numbered row by row, left to right, top to bottom:

Row 1 - THE AUTUMN FOREST: 1 forest floor thick with red and orange fallen leaves (the main ground); 2 the same floor with gold leaves and dark loam showing through; 3 autumn grass, gold-tinted; 4 autumn grass trampled with bare dirt; 5 dark wet loam with a few scattered red leaves; 6 a carpet of low crimson undergrowth seen from above; 7 pine-needle floor with orange leaves; 8 mossy autumn floor with tiny white mushrooms.

Row 2 - THE MOUNTAINS AND THE TIMBERMAW: 9 rocky hillside, grey stone with orange grass in the gaps; 10 grey mountain scree; 11 grey stone covered in orange and green lichen; 12 dry gold mountain grass; 13 packed earth trail; 14 a furbolg-trodden path of dark earth and wood chips; 15 honey-gold clay ground; 16 grey granite cliff face with cracks, moss and orange lichen, seen straight on (a wall).

Row 3 - THE CURSE AND THE DIG: 17 satyr-cursed ground, dark violet-black soil with faint thin green fel veins; 18 scorched earth with grey ash; 19 fel-rot soil, black with sickly green moss; 20 the salvage dig's churned brown earth with pale stone chips; 21 wooden plank walkway over mud, the planks running top to bottom so it tiles along its length; 22 excavated pale sand with small marble fragments; 23 leyline ground, autumn grass crossed by faint glowing pale blue lines; 24 crystal-glass ground, the earth itself turning to pale blue crystal.

Row 4 - HIGHBORNE STONE: 25 Highborne paving of pale cream marble slabs with fine gold inlay lines; 26 the same paving, cracked and overgrown with red leaves; 27 Highborne mosaic floor with a faint crescent-moon pattern, subtle and not one emblem per tile; 28 moss-covered ancient flagstone; 29 a worn white marble road; 30 a broken marble terrace with grass in the cracks; 31 faded Highborne violet-and-silver tile; 32 a ruined plaza of large pale slabs with dark seams.

Row 5 - THE DROWNED CITY: 33 wet white marble with a thin sheen of water; 34 marble crusted with barnacles and green verdigris; 35 drowned mosaic, teal and silver, cracked; 36 coral-encrusted stone, pink and white coral; 37 marble strewn with dark seaweed; 38 silt and crushed-shell sand, grey-white; 39 tide-pool rock, dark and wet with tiny pools; 40 wet black sea-cave rock with barnacles and a sheen of seawater, seen straight on (a wall).

Row 6 - WATER AND SHORES: 41 deep sea water, dark teal, gentle ripples; 42 clear shallow coastal water over white sand; 43 teal shallows over drowned marble, the pale stone visible under the water; 44 calm blue lake water; 45 wet dark sand beach; 46 pale shell beach; 47 storm-churned surf, grey-teal water streaked with foam; 48 glowing pale blue arcane water.
```

Re-roll any cell with a visible seam, a lighting gradient or an object standing on it. The failure mode for row 1 is
"green forest with a few orange dots"; it should read as autumn first.

### Slice order (`tools/slice_tile_sheet.py azshara`, to `assets/tiles/azshara/ground/`)

**Delivered 17 Nov 2026** from the first version of this prompt (1254x1254), so cell 16 is a snow-dusted rock
(`az_snow_rock`) and cell 40 a kelp-tangled floor (`az_kelp_floor`); the two wall tiles above are for a re-roll if the
caldera or the grotto needs them. Its rows drift (209/209/209/190/195/242), so the slicer cuts on measured row lines:
Kyle caught a strip of row 4 across the top of row 5 and of marble across the top of the water on the first cut.

| row | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| 1 | az_leaf_floor | az_leaf_gold | az_grass_gold | az_grass_trod | az_loam | az_crimson_brush | az_needle_leaf | az_moss_shroom |
| 2 | az_rock_hill | az_scree | az_lichen_stone | az_mountain_grass | az_trail | az_furbolg_path | az_honey_clay | az_snow_rock |
| 3 | az_cursed_soil | az_scorched | az_felrot_soil | az_dig_earth | az_plank_walk | az_dig_sand | az_leyline_grass | az_crystal_glass |
| 4 | az_highborne_paving | az_paving_leaves | az_moon_mosaic | az_mossy_flag | az_marble_road | az_marble_terrace | az_violet_tile | az_plaza_slab |
| 5 | az_wet_marble | az_barnacle_marble | az_drowned_mosaic | az_coral_stone | az_seaweed_marble | az_shell_silt | az_tidepool_rock | az_kelp_floor |
| 6 | az_sea_deep | az_sea_shallow | az_drowned_shallows | az_lake_water | az_wet_sand | az_shell_beach | az_storm_surf | az_arcane_water |

The ground follows "less is more": a map uses a handful of these, a dozen at most.

---

## SHEET 2: 36 open-world props, trees and Highborne ruins (MAGENTA KEY)

```
Generate ONE sprite sheet image, 2048x2048, a 6 columns x 6 rows grid = 36 separate sprites, each cell about 341x341. Flat pure #FF00FF magenta background everywhere. Each sprite is ONE single object, centred in its own cell with a wide margin, not touching or overlapping its neighbours or the image edge. No ground, no grass patch, no dirt patch, no water puddle under it, no cast shadow, no glow halo bleeding onto the background, no text, no labels, no numbers, no grid lines, no frames, no borders. Never use magenta or pink anywhere on the objects themselves (coral is pale pink-white and peach, never magenta).

Match the attached reference props EXACTLY in style, camera angle, outline and level of detail: they are from the same set. Painterly semi-realistic WoW Classic style: strong readable silhouette, soft dark outline, chunky simple shapes legible at small size, consistent soft lighting from the top-left.

Camera: isometric three-quarter view elevated about 45 degrees. EVERY object is turned the same way, front face toward the lower-right. Trees stand upright with the trunk base at the bottom of the cell and the crown at the top, so a character can walk past the trunk with the crown overhead. Consistency of angle across all 36 is critical.

Setting: AZSHARA, the ancient night elf coast, forever in autumn: red, orange and gold forests over grey mountains, the pale marble ruins of the Highborne everywhere, and out at sea the drowned city of Zin-Azshari rising wet from the water. Palette: autumn red, rust, burnt orange and gold; pale cream marble with gold trim and faded violet; wet white marble, silver, teal, verdigris and coral; arcane pale blue; satyr violet and fel green used sparingly.

Objects keep their RELATIVE scale: the tall autumn tree and the broken spire are the largest sprites on the sheet; a mushroom cluster and survey stakes are small. Do not blow each one up to fill its own cell.

Sprites are numbered row by row, left to right, top to bottom:

Row 1 - THE AUTUMN FOREST: 1 a tall Azshara tree with a broad crown of red and orange leaves and a dark trunk; 2 a smaller tree with a crown of gold leaves; 3 a cluster of three slim pale-barked birches with yellow leaves; 4 a fallen autumn log with red moss and a few leaves on it; 5 a crimson-leaved bush; 6 a mossy grey boulder with orange lichen.

Row 2 - HIGHBORNE RUINS: 7 a broken Highborne spire, tall and slender, pale marble with gold trim, its violet roof half gone; 8 a toppled white marble column lying in pieces; 9 a ruined archway carved with crescent moons, overgrown with red leaves; 10 a cracked statue of a Highborne noblewoman with one arm missing; 11 a crumbling section of marble wall with a gold moon emblem; 12 a dry, broken Highborne fountain.

Row 3 - THE RISING CITY: 13 a drowned spire, wet, hung with seaweed and barnacles, standing as if just risen from the sea; 14 a barnacle-covered marble statue of a Highborne sorceress; 15 an archway grown over with pale coral; 16 a toppled drowned obelisk with glowing pale blue runes; 17 a cluster of pale peach and white coral; 18 a giant clam shell, open, a pearl inside.

Row 4 - THE SALVAGE: 19 a wooden excavation scaffold with ropes and a pulley; 20 an open crate of salvaged Highborne relics, gold pieces, marble fragments and a glowing orb; 21 an arcane containment pylon of blood elf red and gold, crackling with pale blue light; 22 an orc dig cart full of rubble; 23 a bundle of marked survey stakes leaning on a brass tripod; 24 a canvas-covered find roped off on four posts.

Row 5 - THE LEYLINES AND THE BLUES: 25 a tall formation of pale blue arcane crystals; 26 a leyline node, a small ring of standing stones glowing blue; 27 a tree half turned to pale blue crystal, autumn leaves on one side and glass on the other; 28 a heap of shed blue dragon scales; 29 a broken Highborne mana tower, pale and slender, still glowing at the top; 30 a small cluster of glowing blue mushrooms.

Row 6 - THE CURSE AND THE COAST: 31 a satyr totem of horns and skulls hung with violet cloth; 32 a satyr bonfire burning green fel flame in a ring of stones; 33 a cursed tree, twisted and black with violet leaves; 34 the prow of a wrecked ship half sunk in sand; 35 a naga banner of scaled teal cloth on a coral pole; 36 a naga tide-altar of coral, shells and pearl.
```

Re-roll any tree that comes back green; these must read as autumn at a glance.

### Slice order (`tools/slice_building_sheet.py azshara_props tools/building_sheets/azshara_props.png`, to `assets/tiles/azshara/props/`). Delivered and sliced 17 Nov 2026.

| row | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 1 | az_autumn_tree | az_gold_tree | az_birch_trio | az_autumn_log | az_crimson_bush | az_lichen_boulder |
| 2 | az_broken_spire | az_toppled_column | az_moon_arch | az_noble_statue | az_ruin_wall | az_dry_fountain |
| 3 | az_drowned_spire | az_barnacle_statue | az_coral_arch | az_drowned_obelisk | az_coral_cluster | az_giant_clam |
| 4 | az_dig_scaffold | az_relic_crate | az_containment_pylon | az_dig_cart | az_survey_stakes | az_covered_find |
| 5 | az_arcane_crystal | az_leyline_node | az_crystal_tree | az_scale_pile | az_mana_tower | az_glow_shrooms |
| 6 | az_satyr_totem | az_fel_bonfire | az_cursed_tree | az_wreck_prow | az_naga_banner | az_tide_altar |

---

## SHEET 3: 36 Talrendis Landing buildings and props (MAGENTA KEY)

```
Generate ONE sprite sheet image, 2048x2048, a 6 columns x 6 rows grid = 36 separate sprites, each cell about 341x341. Flat pure #FF00FF magenta background everywhere. Each sprite is ONE single building or object, centred in its own cell with a wide margin, not touching or overlapping its neighbours or the image edge. No ground, no grass patch, no dirt patch, no cast shadow, no glow halo bleeding onto the background, no people, no text, no labels, no numbers, no grid lines, no frames, no borders. Never use magenta or pink anywhere on the buildings or objects themselves.

Match the attached reference buildings EXACTLY in style, camera angle, palette, outline and level of detail: they are from the same set. Painterly semi-realistic WoW Classic style: strong readable silhouette, soft dark outline, chunky simple shapes legible at small size, consistent soft lighting from the top-left.

Camera: isometric three-quarter view elevated about 45 degrees. EVERY building and object is turned the same way, front face toward the lower-right and one side wall toward the lower-left, so two faces of each building are visible. Doors and gates are on the front face. Consistency of angle across all 36 is critical.

Setting: TALRENDIS LANDING, a Horde salvage camp on an old night elf point on the autumn coast of Azshara, where orcs and blood elves dig magic out of Highborne ruins together and don't trust each other. The ORCS build in rough dark timber, hide and black iron with red-brown Horde cloth and tusks. The BLOOD ELVES build in red, gold and white with slender curves and arcane fittings that glow pale gold or pale blue. Here they build TOGETHER, badly: orc timber frames with blood elf gold trim bolted on, elf pavilions held down with orc rope and iron stakes. Keep BOTH styles readable in every mixed piece.

Palette: dark weathered timber, hide brown, black iron, Horde red-brown; blood elf crimson, gold and cream; pale marble salvage; small pale blue and gold arcane glows. Muted, not neon.

Sprites keep their RELATIVE scale: the command hall and the inn are the biggest sprites on the sheet, a signpost or a notice board is visibly far smaller than a house, a cook fire smaller still. Do not blow each one up to fill its own cell.

Sprites are numbered row by row, left to right, top to bottom:

Row 1 - THE LANDING'S HEART (buildings): 1 a mixed command hall, an orc longhouse frame with a blood elf gold-and-red roof spire rising from its middle; 2 the inn, an orc timber lodge with a blood elf red awning and hanging gold lanterns; 3 a gatehouse of orc timber with blood elf banners and a gold arch over the open gate; 4 a wind rider roost, a tall orc timber platform with perches and a blood elf crystal beacon on top; 5 a quartermaster's store, a timber shed with crates and a red-and-gold canopy; 6 a short dock and jetty of heavy orc timber posts and planks.

Row 2 - THE ORC SIDE: 7 an orc salvage barracks of dark timber and hide; 8 an orc forge under a timber roof with an anvil and a chimney; 9 a war tent with Horde banners; 10 a lumber stack and a sawpit; 11 a crane of lashed orc timber with a rope and a hook for lifting stone; 12 a watchtower of lashed logs with a lookout platform.

Row 3 - THE BLOOD ELF SIDE: 13 a magister's pavilion of red and gold silk; 14 an arcane research tent with two small glowing orbs floating above it; 15 a blood elf ward-pylon, a slim gold pillar crackling with pale light; 16 a small portable spire, slender, gold-capped; 17 a scribes' canopy over a table of scrolls; 18 a rack of glowing gold mana cells.

Row 4 - THE SALVAGE YARD: 19 a sorting shed with marble pieces stacked inside; 20 a cage of gold bars holding a glowing Highborne relic; 21 a short cart rail with a stone-loaded cart on it; 22 a heavy wooden stone sledge with a marble block on it; 23 a pile of salvaged marble columns; 24 an iron-bound vault crate stamped with blood elf seals.

Row 5 - WHERE THEY ARGUE: 25 a half-built wall, orc timber on its left half and elf stone on its right half, meeting badly in the middle; 26 a notice board with orc notices and elegant elf notices pinned over each other; 27 a cook fire with an orc iron pot and an elf kettle side by side; 28 a small sparring ring of posts and rope; 29 a long shared mess table with benches under an awning; 30 a signpost with crude orc arrows and elegant elf arrows.

Row 6 - THE SHORE AND THE DIG: 31 an orc longboat pulled up out of the water; 32 a blood elf skiff with a gold prow; 33 a dig trench entrance, a timber-framed opening going down into the earth; 34 a survey tower with a spyglass platform; 35 a stack of sandbags; 36 a cairn of stones the Earth transplants built, with ribbons and small carved keepsakes tied to it.
```

Re-roll any piece that comes back all orc or all elf; the mix is the point.

### Slice order (`tools/slice_building_sheet.py talrendis tools/building_sheets/talrendis.png`, all 36 to `assets/buildings/`). Delivered and sliced 17 Nov 2026; the Landing is dressed with it.

| row | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 1 | tl_command_hall | tl_inn | tl_gatehouse | tl_wind_rider_roost | tl_quartermaster | tl_dock |
| 2 | tl_orc_barracks | tl_orc_forge | tl_war_tent | tl_lumber_stack | tl_stone_crane | tl_log_watchtower |
| 3 | tl_magister_pavilion | tl_research_tent | tl_ward_pylon | tl_field_spire | tl_scribes_canopy | tl_mana_cell_rack |
| 4 | tl_sorting_shed | tl_relic_cage | tl_rail_cart | tl_stone_sledge | tl_column_pile | tl_vault_crate |
| 5 | tl_split_wall | tl_notice_board | tl_shared_fire | tl_sparring_ring | tl_mess_table | tl_signpost |
| 6 | tl_orc_longboat | tl_elf_skiff | tl_dig_entrance | tl_survey_tower | tl_sandbags | tl_cairn |

---

## SHEET 4: 36 Timbermaw Hold buildings and props (MAGENTA KEY)

```
Generate ONE sprite sheet image, 2048x2048, a 6 columns x 6 rows grid = 36 separate sprites, each cell about 341x341. Flat pure #FF00FF magenta background everywhere. Each sprite is ONE single building or object, centred in its own cell with a wide margin, not touching or overlapping its neighbours or the image edge. No ground, no grass patch, no dirt patch, no cast shadow, no glow halo bleeding onto the background, no people, no text, no labels, no numbers, no grid lines, no frames, no borders. Never use magenta or pink anywhere on the buildings or objects themselves.

Match the attached reference buildings EXACTLY in style, camera angle, palette, outline and level of detail: they are from the same set. Painterly semi-realistic WoW Classic style: strong readable silhouette, soft dark outline, chunky simple shapes legible at small size, consistent soft lighting from the top-left.

Camera: isometric three-quarter view elevated about 45 degrees. EVERY building and object is turned the same way, front face toward the lower-right and one side wall toward the lower-left, so two faces of each building are visible. Doors and gates are on the front face. Consistency of angle across all 36 is critical.

Setting: TIMBERMAW HOLD, the home city of the Timbermaw furbolgs (bear-people), built inside the huge hollow of a mountain, open to the sky, with lodges and terraces climbing the inside walls. Timbermaw work is sturdy honey-brown timber, thatch, hide and carved bear totems, with green and gold beadwork, painted bear-paw marks, and honey everywhere. It is older and grander than the attached Timbermaw lodge, the way a capital is grander than a camp. Row 6 is the one dark row: the sealed gate over the rot below the city.

Palette: honey-brown and dark timber, straw thatch, warm hide, moss green, Timbermaw green and gold, amber honey, grey mountain stone; sickly fel green ONLY in row 6.

Sprites keep their RELATIVE scale: the Elders' Great Lodge is the biggest sprite on the sheet, the sealed gate and the great totem nearly as big; a candle stand or a smoke pot is visibly far smaller than a lodge. Do not blow each one up to fill its own cell.

Sprites are numbered row by row, left to right, top to bottom:

Row 1 - THE GREAT LODGES (buildings): 1 the Elders' Great Lodge, a huge longhouse of honey timber with a carved bear-head gable and totem posts at the door; 2 a Timbermaw inn, a warm lodge with a hanging honeycomb sign; 3 a long communal hall with smoke holes in the roof; 4 a two-storey lodge built against a rock face; 5 a round den house of timber and thatch; 6 a carvers' hall with half-finished totems leaning against its front.

Row 2 - THE TERRACES AND THE WALLS: 7 a timber terrace platform with a railing, built out from a rock face; 8 a wooden stair-ramp climbing a rock; 9 a section of rope-and-timber bridge; 10 a lodge built into a cave mouth in a cliff; 11 a lookout platform on tall stilts; 12 a carved timber gate between two bear totems.

Row 3 - HONEY AND HIVES: 13 a great hive-tree, a hollow trunk with wild bee combs; 14 a row of three tall straw skep hives on a bench; 15 a honey store, a hut stacked with clay honey jars; 16 a honey press with a barrel; 17 wax candles on a carved wooden stand; 18 a beekeepers' smoke pot on a tripod.

Row 4 - TOTEMS AND THE SACRED: 19 a giant Timbermaw totem pole of stacked carved bears, painted green and gold; 20 an ancestor shrine with offerings and antlers; 21 a sacred spring pool rimmed with mossy stones, the clean blue water drawn inside the rim; 22 a great bonfire pit ringed with logs for seats; 23 a carved standing stone with bear-paw prints; 24 a drum circle of hide drums.

Row 5 - THE HOLD AT WORK: 25 a furbolg smithy with a stone forge and bear-shaped bellows; 26 a tannery with hides stretched on frames; 27 a carved wooden market stall selling honey and herbs; 28 a woodpile with a splitting block and an axe; 29 an herb-drying rack; 30 a supply cache of baskets and bundles.

Row 6 - THE DEEP GATE AND THE ROT: 31 the sealed lower gate, a massive timber-and-iron door set flat into the stone floor, bound with heavy chains and carved wards; 32 a guard post with a rack of spears beside it; 33 a warning totem, its paint scratched, green stains creeping up from its base; 34 a rockfall of grey boulders; 35 a cracked floor stone seeping faint green fel light; 36 a furbolg war banner of green and gold on a carved pole.
```

Re-roll any lodge that comes back as a plain log cabin; these should read as furbolg, with bear carving and honey.

### Slice order (`tools/slice_building_sheet.py timbermaw_hold tools/building_sheets/timbermaw_hold.png`, all 36 to `assets/buildings/`). Delivered and sliced 17 Nov 2026.

| row | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 1 | tm_elders_great_lodge | tm_inn | tm_long_hall | tm_cliff_lodge | tm_round_den | tm_carvers_hall |
| 2 | tm_cliff_terrace | tm_stair_ramp | tm_rope_bridge | tm_cave_lodge | tm_lookout | tm_totem_gate |
| 3 | tm_hive_tree | tm_skep_row | tm_honey_store | tm_honey_press | tm_candle_stand | tm_smoke_pot |
| 4 | tm_great_totem | tm_ancestor_shrine | tm_sacred_spring | tm_bonfire_pit | tm_paw_stone | tm_drum_circle |
| 5 | tm_smithy | tm_tannery | tm_market_stall | tm_woodpile | tm_herb_rack | tm_supply_cache |
| 6 | tm_deep_gate | tm_gate_guard_post | tm_warning_totem | tm_rockfall | tm_fel_crack | tm_war_banner |

---

## SHEET 5: 36 Azshara creatures (MAGENTA KEY)

```
Generate ONE sprite sheet image, 2048x2048, a 6 columns x 6 rows grid = 36 separate creature sprites, each cell about 341x341. Flat pure #FF00FF magenta background everywhere. Each creature is ONE single figure, centred in its own cell with a wide margin, not touching or overlapping its neighbours or the image edge. No ground, no dirt patch, no water under it, no cast shadow, no glow halo bleeding onto the background, no text, no labels, no numbers, no grid lines, no frames, no borders. Never use magenta or pink anywhere on the creatures themselves.

Match the attached reference creatures EXACTLY in style, camera angle, outline and level of detail: they are from the same set. Painterly semi-realistic WoW Classic style: strong readable silhouette, soft dark outline, chunky simple shapes legible at small size, consistent soft lighting from the top-left.

Camera: every creature faces three-quarters toward the lower-right, full body, feet, tail or base included and nothing cropped. Ghosts and floating things hover with their lowest point near the bottom of the cell. Consistency of angle across all 36 is critical.

Setting: AZSHARA, the ancient night elf coast in endless autumn, where the drowned Highborne city of Zin-Azshari is rising out of the sea. Palette: naga teal, sea green and coral; ghostly pale blue and silver; satyr violet and Highborne gold; arcane sapphire blue; fel green only for the fel rot; autumn red and gold for the wild animals.

Creatures keep their RELATIVE scale: a blue whelp and a shore crab are small, a naga brute and a doomguard are tall, the blue drake is the largest sprite on the sheet. Do not blow each one up to fill its own cell.

Creatures are numbered row by row, left to right, top to bottom:

Row 1 - THE NAGA OF ZIN-AZSHARI: 1 a naga siren, slender, four arms, teal scales and a coral crown; 2 a naga tidehunter with a trident and a net; 3 a naga sea witch with a pearl staff and swirling glowing water; 4 a naga royal guard in barnacled gold armour; 5 a naga brute, heavy and hunched, with a stone club; 6 a snap-jawed sea serpent hatchling.

Row 2 - THE HIGHBORNE GHOSTS (translucent pale blue, ten thousand years dead and still proud): 7 a Highborne noble's ghost in elegant robes, haughty; 8 a Highborne arcanist ghost with books floating around it; 9 a Highborne palace guard's ghost with a glaive; 10 a Highborne handmaiden's ghost, sad, fading at the edges; 11 a ghostly court hound; 12 a Highborne ghost twisted by madness, clawing at itself.

Row 3 - AZSHARA'S SATYRS AND THE OLD LEGION: 13 a cursed Azshara satyr, violet fur, still wearing gold Highborne jewellery; 14 a satyr sorcerer only half changed, half elf and half satyr; 15 a satyr hound-master with a whip and a chain; 16 a felhound with violet crystals growing from its back; 17 an eredar warlock robed in Highborne violet; 18 a doomguard sentinel, tall, ancient and winged.

Row 4 - THE BLUE DRAGONFLIGHT: 19 a blue drake, sleek and sapphire, wings half open; 20 a blue dragonspawn guard with a polearm; 21 a blue whelp; 22 a mana wyrm swarm-leader, a long glowing serpent of arcane light; 23 an arcane construct of floating blue crystals around a bright core; 24 a ley-beast, a deer-like grazer with a back of pale blue crystal.

Row 5 - THE FEL ROT (the Timbermaw's enemy below the Hold): 25 a fel-rot furbolg, a bear-person gone green and twisted, moss and fel crystals in its fur; 26 a fel-rot furbolg shaman holding a glowing green totem; 27 a rot-beast, a bear fused with fel fungus; 28 a drifting fel spore cloud with a glowing eye in it; 29 a root horror of black roots threaded with green light; 30 a satyr rot-tender carrying a watering can of green ooze.

Row 6 - THE WILD: 31 a timber wolf with autumn-red fur; 32 a coastal thunder lizard, a big two-legged reptile; 33 a giant barnacled shore crab; 34 a cliff hippogryph with gold and red feathers; 35 an autumn treant with a crown of red and orange leaves; 36 a wild boar with dark russet bristles.
```

Re-roll any naga that comes back as a mermaid, and any ghost that comes back solid.

### Slice order (`tools/slice_building_sheet.py azshara_creatures tools/building_sheets/azshara_creatures.png`, to `assets/creatures/_src/azshara/`). Delivered and sliced 17 Nov 2026.

| row | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 1 | az_naga_siren | az_naga_tidehunter | az_naga_sea_witch | az_naga_royal_guard | az_naga_brute | az_serpent_hatchling |
| 2 | az_ghost_noble | az_ghost_arcanist | az_ghost_guard | az_ghost_handmaiden | az_ghost_hound | az_ghost_tormented |
| 3 | az_satyr_cursed | az_satyr_sorcerer | az_satyr_houndmaster | az_felhound | az_eredar_warlock | az_doomguard_sentinel |
| 4 | az_blue_drake | az_blue_dragonspawn | az_blue_whelp | az_mana_wyrm_leader | az_arcane_construct | az_ley_beast |
| 5 | az_rot_furbolg | az_rot_shaman | az_rot_beast | az_spore_cloud | az_root_horror | az_rot_tender |
| 6 | az_timber_wolf | az_thunder_lizard | az_shore_crab | az_cliff_hippogryph | az_autumn_treant | az_russet_boar |

---

## SHEET 6: the two dungeons, 24 set pieces and 12 bosses (MAGENTA KEY)

```
Generate ONE sprite sheet image, 2048x2048, a 6 columns x 6 rows grid = 36 separate sprites, each cell about 341x341. Flat pure #FF00FF magenta background everywhere. Each sprite is ONE single object or figure, centred in its own cell with a wide margin, not touching or overlapping its neighbours or the image edge. No ground, no floor patch, no water under it unless the prompt puts the water inside the object's own rim, no cast shadow, no glow halo bleeding onto the background, no text, no labels, no numbers, no grid lines, no frames, no borders. Never use magenta or pink anywhere on the sprites themselves.

Match the attached references EXACTLY in style, camera angle, outline and level of detail: they are from the same set. Painterly semi-realistic WoW Classic style: strong readable silhouette, soft dark outline, chunky simple shapes legible at small size, consistent soft lighting from the top-left.

Camera: rows 1 to 4 are dungeon set pieces in isometric three-quarter view elevated about 45 degrees, EVERY one turned the same way, front face toward the lower-right. Rows 5 and 6 are bosses, full body, facing three-quarters toward the lower-right, nothing cropped. Consistency of angle across the sheet is critical.

Setting: two dungeons in AZSHARA. Rows 1 and 2 and row 5 are THE FEL ROT, the dark halls under the furbolg city of Timbermaw Hold: furbolg timber and stone, black roots, fel-green fungus and violet satyr magic. Rows 3 and 4 and row 6 are THE VAULT OF ZIN-AZSHARI, Queen Azshara's drowned palace: wet white marble, gold, violet, coral, seawater and moonlight.

Sprites keep their RELATIVE scale: bosses are drawn LARGER than ordinary creatures, and the two last bosses (cells 29 and 36) are the largest figures on the sheet; a book shelf or a mushroom cluster is visibly far smaller than a throne. Do not blow each one up to fill its own cell.

Sprites are numbered row by row, left to right, top to bottom:

Row 1 - THE FEL ROT, the upper halls: 1 a furbolg burial niche in rock, overgrown with green fel fungus; 2 a cluster of giant glowing green fel mushrooms; 3 a collapsed timber support beam, rotten; 4 a vein of fel-green crystal bursting out of a rock; 5 a corrupted Timbermaw totem, bent and dripping green; 6 a rock basin holding a pool of fel ooze, the ooze drawn inside the rim.

Row 2 - THE FEL ROT, deeper: 7 a satyr ritual circle of violet runes on a round stone slab; 8 a section of wall made of black roots threaded with green light; 9 a demonic gateway half grown over with fungus; 10 a cage of roots holding a captured furbolg; 11 a fel-spore vent in rock puffing green mist; 12 a throne of roots and skulls.

Row 3 - THE VAULT, the flooded halls: 13 a section of drowned Highborne colonnade, three columns standing in a shallow marble basin of water; 14 a flooded grand staircase of white marble; 15 a coral-encrusted throne of a lesser noble; 16 a fallen chandelier of gold and crystal; 17 a naga war-shrine built into Highborne marble; 18 a drowned library shelf with swollen, ruined books.

Row 4 - THE VAULT, Azshara's own: 19 a vault door of gold and violet with a great moon seal; 20 a pedestal holding a glowing artifact under a dome of arcane light; 21 a tall mirror of dark water in a gold frame; 22 a Highborne treasure pile of gold, gems and relics; 23 an ancient arcane well, cracked and leaking pale light; 24 Queen Azshara's empty throne, huge, gold and violet, untouched by the water.

Row 5 - THE FEL ROT'S BOSSES: 25 Old Mossjaw, a giant fel-rot furbolg chieftain with a crown of fungus; 26 Mother Sporeheart, a bloated fungal horror covered in spore sacs; 27 Rotwarden Kaz'thul, a satyr warden with chains and a green lamp; 28 Thornblight, a root horror the size of a tree; 29 Xavras the Gloomtender, a Highborne-turned satyr lord, regal and rotting, the last boss and the biggest of this row; 30 a fel-rot furbolg elite in crude bone armour, the bosses' bodyguard.

Row 6 - THE VAULT'S BOSSES: 31 Lady Ssiriss, a naga siren queen with four arms and a pearl crown; 32 Tidelord Vashj'ren, a huge naga warlord in coral armour with a trident; 33 the Drowned Chamberlain, a Highborne ghost steward with a ring of keys and a ledger; 34 Magistrix Elaria the Undying, a Highborne sorceress ghost wreathed in blue fire; 35 the Moonguard Revenant, a drowned Highborne knight in silver armour, seaweed in its joints; 36 the Echo of the Queen, a towering spectral Highborne queen made of moonlight and water, the last boss and the largest figure on the sheet.
```

The boss names are working names for the art. Kyle settles the dungeons' names and rosters later.

### Slice order (`tools/slice_building_sheet.py azshara_dungeons tools/building_sheets/azshara_dungeons.png` to `assets/creatures/_src/azshara/`; the 24 set pieces then moved to `assets/tiles/dungeon_props/`). Delivered and sliced 17 Nov 2026.

| row | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 1 | fr_burial_niche | fr_fel_mushrooms | fr_rotten_beam | fr_crystal_vein | fr_corrupt_totem | fr_ooze_pool |
| 2 | fr_ritual_circle | fr_root_wall | fr_fungus_gate | fr_root_cage | fr_spore_vent | fr_root_throne |
| 3 | vz_drowned_colonnade | vz_flooded_stair | vz_coral_throne | vz_fallen_chandelier | vz_naga_shrine | vz_drowned_shelf |
| 4 | vz_vault_door | vz_artifact_pedestal | vz_water_mirror | vz_treasure_pile | vz_ancient_well | vz_queens_throne |
| 5 | fr_boss_mossjaw | fr_boss_sporeheart | fr_boss_kazthul | fr_boss_thornblight | fr_boss_xavras | fr_elite_guard |
| 6 | vz_boss_ssiriss | vz_boss_vashjren | vz_boss_chamberlain | vz_boss_elaria | vz_boss_revenant | vz_boss_echo_queen |
