# Deadwind Pass art prompts (sheets 1 to 8)

For `docs/deadwind_brief.md`. Kyle, 17 Nov 2026: "Can you give me about 8 sheets for this", then "So we want deadwind to
be a disgusting mix of mutation, radiation, HORROR!!!!!" and "Make it dark and disgusting". He picked **grotesque, not
gory** (tumours, extra limbs, fused bodies, sores, glowing pustules) so the generator will draw it, and **"JUST the
wheel"**: the Ferris wheel on sheet 8 is the only Earth object. Every other sprite is Azerothian.

Every prompt below is complete on its own: paste one block and nothing else. Each one states the image size, the grid
and cell size, the background, the margin, the style, the camera, the scale rule, the full negative list, the
never-magenta line, the no-Earth line, and every cell numbered row by row.

| Sheet | What | Image | Grid (cell) | Key |
|---|---|---|---|---|
| 1 | 48 open-zone ground, water and cave tiles | 2048x1536 | 8 x 6 (256 x 256) | **NO magenta**: tiles run flush to their edges |
| 2 | 36 props: the dead forest, Morgan's Plot, the ogres, the road, the liquidators' marks | 2048x2048 | 6 x 6 (about 341 x 341) | magenta |
| 3 | 36 anomalies: stopped time, echoes, the fallout, mutated growth, the rupture's edge | 2048x2048 | 6 x 6 (about 341 x 341) | magenta |
| 4 | 36 outpost buildings and props (the liquidators and the Forsaken) | 2048x2048 | 6 x 6 (about 341 x 341) | magenta |
| 5 | 36 creatures | 2048x2048 | 6 x 6 (about 341 x 341) | magenta |
| 6 | 48 dungeon floor and wall tiles (the Fallout Zone) | 2048x1536 | 8 x 6 (256 x 256) | **NO magenta** |
| 7 | 24 dungeon set pieces, 6 dungeon bosses, 2 cave bosses and 4 rares | 2048x2048 | 6 x 6 (about 341 x 341) | magenta |
| 8 | 9 giant landmarks (the wheel, Karazhan, the stopped avalanche...) | 2048x2048 | 3 x 3 (about 682 x 682) | magenta |

**Priority:** sheets 1, 2, 3 and 8 make the open zone; 4 the outpost; 5 the creatures; 6 and 7 the dungeon.

**Delivered 18 Nov 2026, all eight** (Kyle: "somehow....chatGPT didn't stop me!"), saved unsliced in
`tools/building_sheets/deadwind_*.png` until the build: ground (1536x1024), props, anomalies (two copies came back:
`deadwind_anomalies.png` is the one to slice, `deadwind_anomalies_alt.png` the spare), outpost, creatures, dungeon
tiles (1448x1086), dungeon pieces and bosses, landmarks. The tile sheets came back smaller than asked, so measure the
row lines before slicing (as with Azshara's ground).

**Style references to attach (at most 3 per sheet):**
- Sheet 1: `pl_ash_soil.png`, `pl_blight_mud.png`, `pl_corpse_pit.png`
- Sheet 2: `pl_dead_oak.png`, `pl_plaguewood_tree.png`, `pl_ruin_arch.png`
- Sheet 3: `pl_runoff_pool.png`, `pl_necro_obelisk.png`, `pl_plague_mushrooms.png`
- Sheet 4: `pf_field_tent.png`, `sc_war_tent.png`, `pl_bone_barricade.png`
- Sheet 5: `pl_frenzied_ghoul.png`, `pl_plaguewood_spider.png`, `pl_flesh_golem.png`
- Sheet 6: `pl_corpse_pit.png`, `pl_blight_mud.png`, `pl_ash_soil.png`
- Sheet 7: `pl_boss_abom_butcher.png`, `pl_boss_brood_queen.png`, `pl_runoff_pool.png`
- Sheet 8: `pl_windmill_broken.png`, `pl_necro_obelisk.png`, `pl_dead_oak.png`

---

## SHEET 1: 48 open-zone ground, water and cave tiles (NO magenta)

```
Generate ONE texture sheet image, 2048x1536, laid out as a strict 8 columns x 6 rows grid = 48 separate seamless ground and wall textures, each cell exactly 256x256. Each cell is COMPLETELY FILLED by its texture, edge to edge, touching its neighbours with no gap. No border, no background colour, no magenta, no frames, no gutters, no grid lines, no text, no labels, no numbers. Every texture must TILE SEAMLESSLY with itself on all four sides: no single large feature that would obviously repeat, no emblem or pattern repeated in every tile, no lighting gradient across the cell, flat even illumination, no vignette, no baked shadows, no objects or props standing on the ground. Straight top-down view, no perspective. Nothing modern or from the real world: no concrete, no asphalt, no paint lines, no metal sheeting.

Match the attached reference tiles EXACTLY in style, scale of detail and level of saturation: they are from the same set. Painterly semi-realistic WoW Classic ground texture style, dark and desaturated, readable at small size, not too busy.

Setting: DEADWIND PASS, a dead mountain pass where something went horribly wrong: time broke, and a sickly glowing fallout leaked out of the ground and mutated everything it touched. Dark, grim and disgusting. Palette: dead grey-brown, black rock, grey ash, rust, bruise purple, wet grey-pink, and a SICKLY GLOWING GREEN-YELLOW used as the accent; broken time is shown with cold violet-white light. No healthy green anywhere.

Tiles are numbered row by row, left to right, top to bottom:

Row 1 - THE DEAD FOREST: 1 dead forest floor of grey-brown dead leaves over dark soil (the main ground); 2 the same floor with grey ash drifted over it; 3 dead grass, colourless and flattened; 4 bare black soil threaded with dead roots; 5 mouldering leaf litter with pale grey fungus threads; 6 dead rust-brown pine needles; 7 cracked dry grey earth; 8 a trampled path of dark mud.

Row 2 - THE PASS AND THE GRAVES: 9 dark grey-black rock with gravel; 10 loose black scree; 11 gorge floor of dark stones and grit; 12 a dark wet rock face with cracks, seen straight on (a wall); 13 an old broken cobble road with dead weeds in the cracks; 14 a cart track of two ruts in grey mud; 15 dark turned grave earth with small bone fragments; 16 old graveyard flagstones, cracked, with dead moss.

Row 3 - THE FALLOUT: 17 dark ground split by thin cracks of glowing green-yellow seep; 18 fine grey ash fall with a faint green glow underneath; 19 a crust of glassy glowing yellow-green slag; 20 soil stained in dried rings of yellow, green and rust where the seep evaporated; 21 glowing green-yellow ooze puddled over black mud; 22 dead ground blistered with small glowing pustules; 23 rust-orange sludge; 24 ground grown over with a pale, wet, fleshy fungal mat in grey-pink.

Row 4 - THE GROUND GOING WRONG: 25 a mat of grey-pink flesh-like growth with darker veins; 26 black veins spreading through grey soil like roots; 27 bruise-purple mould over dark soil; 28 a bone-white crust with dark pores; 29 dark, wet, sick moss gone black-green; 30 a tangle of black glossy roots threaded with faint green light; 31 grey spider silk spread over dead leaves; 32 dead leaves and webbing studded with small pale translucent egg sacs glowing faint green.

Row 5 - BROKEN TIME AND THE OUTPOST: 33 rock cracked like shattered glass, each shard a slightly different shade of the same stone, as if from different moments; 34 mottled ground of ancient grey dust and fresh dark soil in patches; 35 a water surface stopped dead mid-ripple, grey and glassy, not ice; 36 dark rock threaded with thin cracks of cold violet-white light; 37 grey ground covered in faint pale overlapping ghostly footprints; 38 black glass with violet light deep inside it; 39 a neat path of dark grey stone blocks (Forsaken masonry); 40 camp mud mixed with ash and boot prints.

Row 6 - WATER AND CAVES: 41 black, still, oily pond water; 42 glowing green-yellow toxic water; 43 shallow brackish water over black mud; 44 a dead stream bed of grey pebbles; 45 rust-red stagnant water; 46 damp dark cave floor stone; 47 cave floor with glowing seep and small pale fungus; 48 a dark wet cave wall streaked with glowing green-yellow seep, seen straight on (a wall).
```

Re-roll any cell with a visible seam, a lighting gradient, an object standing on it, or any healthy green. The failure
mode is "the Plaguelands again"; Deadwind should read as darker and wronger, with the glow as its own colour.

### Slice order (`tools/slice_tile_sheet.py deadwind`, to `assets/tiles/deadwind/ground/`; the set is added when the sheet arrives)

| row | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| 1 | dw_dead_floor | dw_ash_floor | dw_dead_grass | dw_root_soil | dw_mould_litter | dw_dead_needles | dw_cracked_earth | dw_mud_path |
| 2 | dw_black_rock | dw_scree | dw_gorge_floor | dw_rock_wall | dw_broken_cobble | dw_cart_ruts | dw_grave_earth | dw_grave_flags |
| 3 | dw_seep_cracks | dw_glow_ash | dw_slag_crust | dw_stain_rings | dw_ooze_mud | dw_pustule_ground | dw_rust_sludge | dw_flesh_mat |
| 4 | dw_flesh_growth | dw_black_veins | dw_bruise_mould | dw_bone_crust | dw_sick_moss | dw_glow_roots | dw_web_floor | dw_egg_floor |
| 5 | dw_shattered_time | dw_aged_dust | dw_stopped_water | dw_rift_rock | dw_echo_prints | dw_black_glass | dw_forsaken_path | dw_camp_mud |
| 6 | dw_black_pond | dw_toxic_water | dw_brackish | dw_dead_streambed | dw_rust_water | dw_cave_floor | dw_cave_seep | dw_cave_wall |

---

## SHEET 2: 36 props: the dead forest, Morgan's Plot, the ogres, the road (MAGENTA KEY)

```
Generate ONE sprite sheet image, 2048x2048, a 6 columns x 6 rows grid = 36 separate sprites, each cell about 341x341. Flat pure #FF00FF magenta background everywhere. Each sprite is ONE single object, centred in its own cell with a wide margin, not touching or overlapping its neighbours or the image edge. No ground, no grass patch, no dirt patch, no puddle under it, no cast shadow, no glow halo bleeding onto the background, no people, no text, no labels, no numbers, no grid lines, no frames, no borders. Never use magenta or pink anywhere on the objects themselves. Nothing modern or from the real world: no concrete, no plastic, no machines, no signs with writing.

Match the attached reference props EXACTLY in style, camera angle, outline and level of detail: they are from the same set. Painterly semi-realistic WoW Classic style: strong readable silhouette, soft dark outline, chunky simple shapes legible at small size, consistent soft lighting from the top-left.

Camera: isometric three-quarter view elevated about 45 degrees. EVERY object is turned the same way, front face toward the lower-right. Trees stand upright with the trunk base at the bottom of the cell and the branches at the top, so a character can walk past the trunk with the branches overhead. Consistency of angle across all 36 is critical.

Setting: DEADWIND PASS, a dead mountain pass where time broke and a sickly glowing fallout leaked out of the ground, mutating everything it touched. Dark, grim, grotesque and disgusting, but not gory. Palette: dead grey-brown, black, grey ash, rust, bruise purple, wet grey-pink growths, and a SICKLY GLOWING GREEN-YELLOW as the accent. No healthy green anywhere.

Objects keep their RELATIVE scale: the tall dead tree and the crypt are the largest sprites on the sheet; a gravestone, an egg-sac cluster and a sample crate are small. Do not blow each one up to fill its own cell.

Sprites are numbered row by row, left to right, top to bottom:

Row 1 - THE DEAD FOREST: 1 a tall dead Deadwind tree, black and leafless, its branches twisted like claws; 2 a dead tree whose trunk is swollen with pale lumpy tumours and small glowing pustules; 3 a cluster of three dead grey birches with peeling bark; 4 a fallen grey log furred with pale fungus; 5 a black dead thornbush; 6 a dark boulder streaked with glowing green-yellow seep.

Row 2 - MORGAN'S PLOT: 7 a leaning cracked gravestone; 8 a cluster of three old sunken graves with worn headstones; 9 a small stone crypt with a broken iron door; 10 a section of rusted iron cemetery fence; 11 an open grave with the earth thrown back and nothing in it; 12 a weeping stone angel statue whose face has rotted away.

Row 3 - THE OGRE COMPOUND, GONE WRONG: 13 a sagging ogre hut of rotten hides and bones on poles; 14 an ogre totem of stacked skulls, one skull sprouting a pale tumour; 15 a big ogre cookpot over a dead fire, a stained cloth thrown over it; 16 a section of crude ogre palisade of sharpened logs, black with rot; 17 a torn and stained ogre war banner on a pole; 18 a heap of gnawed bones.

Row 4 - THE ROAD AND KARAZHAN'S GROUNDS: 19 an overturned broken wagon; 20 the skeleton of a draft horse still in its harness; 21 a road signpost with its boards rotted away; 22 a ruined dark stone stable wall; 23 a broken lamp post of dark iron in an old noble style; 24 a cracked stone well full of black water.

Row 5 - THE CROWS AND THE WEBS: 25 a dead branch on a post hung with ragged black feathers, a crow perch; 26 a mass of thick grey spider web stretched between two dead stumps; 27 a web cocoon hanging from a dead branch with a deer-shaped thing inside; 28 a cluster of pale translucent spider egg sacs glowing faint green; 29 a big nest of twigs and small bones; 30 a dead tree split open and oozing thick black sap.

Row 6 - THE LIQUIDATORS' MARKS (put out in the pass by the camp): 31 a quarantine stake with a green glass lantern and a bone ward tied to it; 32 a warning cairn of stones topped with a cracked beaked plague mask; 33 an unlit pyre of stacked logs; 34 a burned-out pyre of ash and charred bones; 35 an open wooden crate of corked glass vials glowing green; 36 a rope barrier on posts hung with bone wards and rags.
```

Re-roll any tree with leaves on it, and any sprite that comes back with gore instead of wrongness.

### Slice order (`tools/slice_building_sheet.py deadwind_props <sheet.png>`, to `assets/tiles/deadwind/props/`)

| row | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 1 | dw_dead_tree | dw_tumour_tree | dw_dead_birches | dw_fungus_log | dw_thornbush | dw_seep_boulder |
| 2 | dw_gravestone | dw_graves | dw_crypt | dw_iron_fence | dw_open_grave | dw_rotted_angel |
| 3 | dw_ogre_hut | dw_skull_totem | dw_ogre_cookpot | dw_ogre_palisade | dw_ogre_banner | dw_bone_heap |
| 4 | dw_wagon_wreck | dw_horse_skeleton | dw_rotted_signpost | dw_stable_ruin | dw_iron_lamp | dw_black_well |
| 5 | dw_crow_perch | dw_web_mass | dw_web_cocoon | dw_egg_sacs | dw_bone_nest | dw_split_tree |
| 6 | dw_quarantine_stake | dw_warning_cairn | dw_pyre_unlit | dw_pyre_burned | dw_sample_crate | dw_rope_barrier |

---

## SHEET 3: 36 anomalies: stopped time, echoes, the fallout, mutated growth (MAGENTA KEY)

```
Generate ONE sprite sheet image, 2048x2048, a 6 columns x 6 rows grid = 36 separate sprites, each cell about 341x341. Flat pure #FF00FF magenta background everywhere. Each sprite is ONE single object or phenomenon, centred in its own cell with a wide margin, not touching or overlapping its neighbours or the image edge. No ground patch under it unless the prompt puts it inside the object's own rim, no cast shadow, no glow halo bleeding onto the background (glow stays inside the object), no people, no text, no labels, no numbers, no grid lines, no frames, no borders. Never use magenta or pink anywhere on the sprites themselves. Nothing modern or from the real world: no clocks, no machines, no concrete.

Match the attached reference props EXACTLY in style, camera angle, outline and level of detail: they are from the same set. Painterly semi-realistic WoW Classic style: strong readable silhouette, soft dark outline, chunky simple shapes legible at small size, consistent soft lighting from the top-left.

Camera: isometric three-quarter view elevated about 45 degrees. EVERY object is turned the same way, front face toward the lower-right. Consistency of angle across all 36 is critical.

Setting: DEADWIND PASS, where time broke and a sickly glowing fallout leaked out of the ground. These are the WRONG things in the pass. Two kinds of wrongness: BROKEN TIME, shown with cold grey stillness and violet-white light (things stopped mid-motion, overlapping copies of the same thing at different moments); and THE FALLOUT, shown with a sickly glowing green-yellow and grotesque mutation (tumours, swollen growth, sores, glowing pustules, flesh where flesh shouldn't be). Grotesque and disgusting, not gory. Palette: black, dead grey, rust, bruise purple, wet grey-pink, sickly glowing green-yellow, cold violet-white.

Sprites keep their RELATIVE scale: the stopped rockslide, the aged tree and the tear in the air are the largest; a mushroom cluster and a pustule pod are small. Do not blow each one up to fill its own cell.

Sprites are numbered row by row, left to right, top to bottom:

Row 1 - STOPPED TIME: 1 a rockslide stopped in mid-air, a cluster of boulders hanging above a slope with dust frozen around them; 2 a crow stuck mid-wingbeat inside a shard of grey glassy stopped air; 3 a small waterfall stopped dead, the water hanging from a rock lip like grey glass; 4 a campfire stopped mid-flame, its flames grey, still and colourless; 5 a tree aged a thousand years in an instant, grey and crumbling to dust, beside the green-less sapling it once was; 6 a dead tree with a storm of falling leaves frozen around it, every leaf hanging still.

Row 2 - ECHOES: 7 three pale translucent overlapping copies of the same wagon crashing, at three moments of the crash; 8 a ruined doorway in a broken wall, a faint different-coloured light showing through it as if from another time; 9 a dark puddle in a stone rim that reflects a living forest that isn't there; 10 a carved stone sundial whose shadow points three ways at once; 11 a stretch of wooden fence repeated three times, overlapping and slightly offset; 12 the faint flickering ghostly outline of a cottage where nothing stands.

Row 3 - THE FALLOUT: 13 a pool of glowing green-yellow seep in a ring of crusted rock, the glow kept inside the rim; 14 a cluster of jagged glowing yellow-green slag crystals; 15 a vent in the ground breathing glowing green-yellow fumes; 16 a heap of grey ash with glowing embers that never cool; 17 a dead deer half dissolved into glowing slime; 18 a rusted ogre cauldron overflowing with glowing ooze.

Row 4 - MUTATED GROWTH: 19 a tumour tree, its trunk swollen with pale lumpy growths and glowing pustules; 20 a cluster of mushrooms with half-closed eyes in their caps; 21 a fleshy pod plant, grey-pink pods splitting open with glowing seeds; 22 a mass of veined grey-pink flesh-like growth climbing a rock; 23 a bruise-purple flower with far too many petals arranged like teeth; 24 a tangle of black glossy roots whose tips end in small pale grasping hand-like shapes.

Row 5 - THE RUPTURE'S EDGE: 25 a crack in the ground glowing cold violet-white, the light rising from it like steam; 26 a chunk of rock floating over a crack, turning slowly; 27 a black glass spire grown out of the ground with violet light trapped inside; 28 a ring of cracked standing stones, one of them stopped mid-fall; 29 a formation where animal skeletons have grown into the rock and the rock into them; 30 a tear in the air, a man-sized vertical slit of violet-white light with black edges.

Row 6 - THE DEAD AND THE ROT: 31 a heap of mutated animal carcasses under a rough sackcloth, limbs at wrong angles poking out; 32 the skeleton of something huge with far too many ribs; 33 a rotting ogre carcass fused into a dead tree trunk; 34 a web-wrapped ogre cocoon with glowing egg sacs bursting out of it; 35 a small crater glowing green at its bottom, the glow inside the rim; 36 a heap of shed, swollen skin glowing faintly, as if something huge moulted.
```

Re-roll anything that reads as pretty or magical instead of wrong; the glow should feel sick, not enchanted.

### Slice order (`tools/slice_building_sheet.py deadwind_anomalies <sheet.png>`, to `assets/tiles/deadwind/props/`)

| row | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 1 | dw_stopped_rockslide | dw_stopped_crow | dw_stopped_waterfall | dw_stopped_fire | dw_aged_tree | dw_frozen_leaves |
| 2 | dw_echo_wagon | dw_time_doorway | dw_false_reflection | dw_sundial | dw_echo_fence | dw_echo_cottage |
| 3 | dw_seep_pool | dw_slag_crystals | dw_fume_vent | dw_ember_ash | dw_dissolved_deer | dw_ooze_cauldron |
| 4 | dw_tumour_growth | dw_eye_mushrooms | dw_flesh_pods | dw_flesh_mass | dw_teeth_flower | dw_hand_roots |
| 5 | dw_rift_crack | dw_floating_rock | dw_glass_spire | dw_broken_stones | dw_bone_rock | dw_air_tear |
| 6 | dw_carcass_heap | dw_many_ribs | dw_fused_ogre_tree | dw_ogre_cocoon | dw_glow_crater | dw_shed_skin |

---

## SHEET 4: 36 outpost buildings and props: the liquidators and the Forsaken (MAGENTA KEY)

```
Generate ONE sprite sheet image, 2048x2048, a 6 columns x 6 rows grid = 36 separate sprites, each cell about 341x341. Flat pure #FF00FF magenta background everywhere. Each sprite is ONE single building or object, centred in its own cell with a wide margin, not touching or overlapping its neighbours or the image edge. No ground, no grass patch, no dirt patch, no cast shadow, no glow halo bleeding onto the background, no people, no text, no labels, no numbers, no grid lines, no frames, no borders. Never use magenta or pink anywhere on the buildings or objects themselves. Nothing modern or from the real world: no concrete, no corrugated metal, no plastic, no machines, no hazard signs, no warning stripes, no gas masks (masks are beaked plague-doctor masks of leather).

Match the attached reference buildings EXACTLY in style, camera angle, outline and level of detail: they are from the same set. Painterly semi-realistic WoW Classic style: strong readable silhouette, soft dark outline, chunky simple shapes legible at small size, consistent soft lighting from the top-left.

Camera: isometric three-quarter view elevated about 45 degrees. EVERY building and object is turned the same way, front face toward the lower-right and one side wall toward the lower-left, so two faces of each building are visible. Consistency of angle across all 36 is critical.

Setting: a grim quarantine camp at the edge of a poisoned mountain pass, run by volunteers who hold the line against a glowing fallout and the mutated things it makes, together with the undead Forsaken (gaunt, practical, the rot barely touches them). Forsaken style: dark grey stone, black iron, dark timber, slate roofs, sickly green lanterns, bone wards, beaked leather plague masks. Everything sealed, scrubbed and patched. Palette: dark grey, black iron, dark timber, grey canvas, sickly green lantern light, milky blue for the washing water, and ONE warm colour: the orange of the great pyre.

Buildings keep their RELATIVE scale: the inn, the infirmary and the command house are the largest; a tent is smaller; a bucket rack or a signpost is small. Do not blow each one up to fill its own cell.

Sprites are numbered row by row, left to right, top to bottom:

Row 1 - THE MAIN BUILDINGS: 1 the camp inn, a two-storey dark stone-and-timber house with sealed shutters, a green lantern by the door and a smoking chimney; 2 the infirmary, long and low, iron-bound, with sealed doors and green-lit windows; 3 the command house, a tall dark stone building with a lookout on its roof and a beaked-mask sign over the door; 4 the apothecary laboratory with copper vats, pipes and a glowing glass tank on the roof; 5 the flight roost, a tall dark timber tower with a high platform for giant bats; 6 the camp gatehouse of heavy timber and black iron, a long stone wash trough in front of it.

Row 2 - SMALLER BUILDINGS: 7 a barracks of dark timber with a slate roof; 8 a quartermaster's store with crates under a canvas awning; 9 a sealed stone-and-iron storehouse half sunk into the ground; 10 a dark timber watchtower with a green signal lantern; 11 a smithy shed with a forge and an anvil; 12 a patched grey canvas tent with a beaked-mask emblem.

Row 3 - DECONTAMINATION: 13 a long stone wash trough of milky blue water with scrubbing brushes on its rim; 14 a scrub station, a wooden frame with buckets, brushes and a hanging oilcloth curtain; 15 a rack of hanging oilcloth coats and beaked leather plague masks; 16 a barrel of faintly glowing blue neutralising salts; 17 an iron bin of burning clothes, smoking; 18 a sealed iron coffer for samples with a bone ward chained to its lid.

Row 4 - THE DEAD: 19 the great pyre, a stone-ringed bonfire burning warm orange, the one warm light in the camp; 20 a handcart of sacked bodies; 21 a row of covered stretchers; 22 a pile of body sacks; 23 a stone ossuary wall of niches; 24 an apothecary's examination table under a hanging lamp, with instruments laid out, empty.

Row 5 - THE WORK: 25 a rack of glass sample vials glowing green; 26 a copper still with coiled pipes and a glowing glass tank; 27 a map table with a big hand-drawn map of the pass pinned with markers; 28 a wooden board nailed full of paper notes, the names of the missing and the dead; 29 a section of quarantine fence of black iron posts and chain hung with bone wards; 30 a gate in that fence, chained shut.

Row 6 - LIVING THERE: 31 a mess table with tin plates and a cookpot; 32 a lean-to shelter with bedrolls; 33 a stack of supply crates and barrels; 34 a wooden water tank on legs; 35 a dark wooden signpost with blank boards; 36 a small shrine of candles and keepsakes left for the dead.
```

Re-roll any sprite with a gas mask, a hazard stripe or anything that looks like it came from Earth.

### Slice order (`tools/slice_building_sheet.py deadwind_outpost <sheet.png>`, to `assets/buildings/`)

| row | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 1 | dw_inn | dw_infirmary | dw_command_house | dw_laboratory | dw_bat_roost | dw_gatehouse |
| 2 | dw_barracks | dw_quartermaster | dw_sealed_store | dw_watchtower | dw_smithy | dw_canvas_tent |
| 3 | dw_wash_trough | dw_scrub_station | dw_mask_rack | dw_salt_barrel | dw_burn_bin | dw_sample_coffer |
| 4 | dw_great_pyre | dw_body_cart | dw_stretchers | dw_body_sacks | dw_ossuary | dw_exam_table |
| 5 | dw_vial_rack | dw_copper_still | dw_map_table | dw_names_board | dw_quarantine_fence | dw_fence_gate |
| 6 | dw_mess_table | dw_lean_to | dw_supply_stack | dw_water_tank | dw_signpost | dw_candle_shrine |

---

## SHEET 5: 36 creatures (MAGENTA KEY)

```
Generate ONE sprite sheet image, 2048x2048, a 6 columns x 6 rows grid = 36 separate creature sprites, each cell about 341x341. Flat pure #FF00FF magenta background everywhere. Each sprite is ONE single creature (or one small swarm where the prompt says so), full body, centred in its own cell with a wide margin, not touching or overlapping its neighbours or the image edge, nothing cropped. No ground, no shadow, no glow halo bleeding onto the background, no text, no labels, no numbers, no grid lines, no frames, no borders. Never use magenta or pink anywhere on the creatures themselves (flesh is grey-pink, ashen and bruised, never magenta). Nothing modern or from the real world: no clothing, gear or objects from Earth.

Match the attached reference creatures EXACTLY in style, camera angle, outline and level of detail: they are from the same set. Painterly semi-realistic WoW Classic style: strong readable silhouette, soft dark outline, chunky simple shapes legible at small size, consistent soft lighting from the top-left.

Camera: every creature faces three-quarters toward the lower-right, standing in its natural pose, the same angle across the whole sheet.

Setting: DEADWIND PASS, where time broke and a sickly glowing fallout mutated every living thing. These creatures are GROTESQUE and DISGUSTING, not gory: tumours, extra limbs, extra heads, swollen bodies, sores and glowing green-yellow pustules, patchy fur and feathers, bone pushing through skin, bodies fused together, and the worst of them fused with copies of themselves from other moments in time. No blood sprays, no open gore. Palette: dead grey, black, ashen grey-pink flesh, bruise purple, rust, sickly glowing green-yellow; broken-time creatures in cold grey and violet-white.

Creatures keep their RELATIVE scale: ogres, the fused abomination and the broodmother widow are the largest; crows, hatchlings and a leech are small. Do not blow each one up to fill its own cell.

Creatures are numbered row by row, left to right, top to bottom:

Row 1 - THE MUTATED WILD: 1 a Deadwind wolf with tumours down its flank and a second smaller head growing out of its neck; 2 a three-headed wolf whose heads are the same wolf young, grown and old; 3 a crow with too many eyes and patchy feathers; 4 a boar swollen with glowing pustules, its tusks grown through its own cheeks; 5 two bats fused into one body with four wings; 6 a gaunt deer whose antlers have grown into a cage of bone over its eyes, its ribs showing.

Row 2 - THE DEADWIND OGRES: 7 a mutated ogre brute with one arm swollen to twice the size of the other; 8 an ogre with a second face growing out of its shoulder; 9 an ogre shaman covered in glowing sores, holding a skull staff; 10 an ogre with a smaller, younger copy of its own head growing out of its chest; 11 an ogre mauler wrapped in rusted chains, its eyes grown over; 12 a bloated ogre leaking glowing ooze from its sores.

Row 3 - THE STUCK (caught in broken time, cold grey and violet-white): 13 a translucent grey human figure replaying its last moment, shown as three overlapping poses; 14 a thing aged to bone in an instant, a skeleton still walking with scraps of grey skin; 15 a wraith whose body is shattered into glassy shards with dark gaps between them; 16 a man-shaped mass of overlapping limbs, the same person at many moments at once; 17 a hound flickering between living and skeleton, half of each; 18 a soldier half turned to grey glassy stopped time, still moving slowly.

Row 4 - KARAZHAN'S SPILL (things that wandered out of the sealed tower, violet and ghostly): 19 a spectral servant in tattered old livery carrying a tray; 20 a spectral stablehand with a pitchfork; 21 an animated suit of rusted armour glowing violet inside; 22 a flock of animated books flapping like bats (one swarm); 23 an arcane anomaly, a floating violet-white swirl crackling with arcs of light; 24 a ghostly noblewoman frozen mid-dance, beautiful and decayed.

Row 5 - THE FALLOUT HORRORS: 25 a crawling mass of glowing slag and flesh with several mouths; 26 a bloated walker, a swollen man-sized figure about to burst, glowing veins under stretched skin; 27 an abomination of fused animals, wolf, boar and crow in one body; 28 a glowing green-yellow ooze with bones floating inside it; 29 a hunched thing of grey flesh with far too many arms; 30 a seep-wyrm, a long pale worm glowing from inside.

Row 6 - THE WIDOWS AND THE CAVES: 31 a huge black Deadwind widow spider, its abdomen swollen with glowing eggs; 32 a swarm of widow hatchlings (one swarm); 33 a broodmother widow, bloated and tumorous, bigger than the rest; 34 a pale eyeless burrowing cave beast; 35 a huge glowing cave leech; 36 a cave horror of mud, roots and drowned animals with an open mouth.
```

Re-roll anything with blood or open wounds (it should disgust, not splatter), and any "stuck" creature that comes back
solid and coloured instead of grey and glassy.

### Slice order (`tools/slice_building_sheet.py deadwind_creatures <sheet.png>`, to `assets/creatures/_src/deadwind/`)

| row | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 1 | dw_tumour_wolf | dw_three_age_wolf | dw_many_eyed_crow | dw_pustule_boar | dw_fused_bat | dw_cage_deer |
| 2 | dw_ogre_brute | dw_two_faced_ogre | dw_sore_shaman | dw_twice_ogre | dw_chained_mauler | dw_leaking_ogre |
| 3 | dw_echo | dw_aged_walker | dw_shard_wraith | dw_many_moments | dw_flicker_hound | dw_stopped_soldier |
| 4 | dw_spectral_servant | dw_spectral_stablehand | dw_violet_armour | dw_book_flock | dw_arcane_anomaly | dw_dancing_ghost |
| 5 | dw_slag_crawler | dw_bloated_walker | dw_fused_abomination | dw_bone_ooze | dw_many_arms | dw_seep_wyrm |
| 6 | dw_widow | dw_widow_hatchlings | dw_broodmother | dw_cave_burrower | dw_cave_leech | dw_mud_horror |

---

## SHEET 6: 48 dungeon floor and wall tiles, the Fallout Zone (NO magenta)

```
Generate ONE texture sheet image, 2048x1536, laid out as a strict 8 columns x 6 rows grid = 48 separate seamless floor and wall textures, each cell exactly 256x256. Each cell is COMPLETELY FILLED by its texture, edge to edge, touching its neighbours with no gap. No border, no background colour, no magenta, no frames, no gutters, no grid lines, no text, no labels, no numbers. Every texture must TILE SEAMLESSLY with itself on all four sides: no single large feature that would obviously repeat, no emblem or pattern repeated in every tile, no lighting gradient across the cell, flat even illumination, no vignette, no baked shadows, no objects standing on the floor. Straight top-down view, no perspective. Nothing modern or from the real world: no concrete, no metal sheeting, no pipes.

Match the attached reference tiles EXACTLY in style, scale of detail and level of saturation: they are from the same set. Painterly semi-realistic WoW Classic dungeon texture style, dark, readable at small size, not too busy.

Setting: THE FALLOUT ZONE, a dungeon down inside the wound under Deadwind Pass, where the ground tore when the worlds merged. It gets worse the deeper you go: first dark Deadwind rock, then the glowing fallout, then flesh growing over the stone, then broken time, and at the bottom the wound itself, flesh, black glass and light fused together. Grotesque and disgusting, not gory. Palette: black and dark grey rock, grey ash, rust, sickly glowing green-yellow, wet grey-pink flesh, bone white, bruise purple, deep red-violet, cold violet-white light.

Tiles are numbered row by row, left to right, top to bottom:

Row 1 - THE MOUTH (the way down): 1 rough gouged dark rock floor; 2 dark gravel and grit; 3 cracked dark rock with glowing green-yellow seep in the cracks; 4 packed dark earth under grey ash; 5 rock floor scorched black; 6 a floor of broken fallen rock; 7 a dark rock wall seen straight on (a wall); 8 a dark rock wall streaked with glowing seep, seen straight on (a wall).

Row 2 - THE FALLOUT: 9 a floor of glassy glowing yellow-green slag; 10 crusted rings of dried seep in yellow, green and rust; 11 glowing ooze over black stone; 12 a floor of deep grey ash; 13 corroded rock, pitted and rusted orange; 14 a floor bristling with small jagged yellow-green crystals; 15 a glassy glowing slag wall, seen straight on (a wall); 16 the surface of a pool of glowing green-yellow ooze.

Row 3 - THE FLESH: 17 a floor of grey-pink flesh growth with dark veins; 18 wet veined flesh grown over stone; 19 a mat of fused bones; 20 black roots matted with grey flesh; 21 flesh covered in glowing blisters; 22 a floor of red-grey sinew strands; 23 a living wall of grey-pink tissue with veins, seen straight on (a wall); 24 a wall of bones fused into rock, seen straight on (a wall).

Row 4 - BROKEN TIME: 25 rock cracked like shattered glass, each shard a slightly different shade; 26 black glass with violet light deep inside; 27 stone covered in faint pale overlapping ghostly outlines; 28 a water surface stopped mid-ripple, grey and glassy, not ice; 29 mottled ancient grey dust and fresh dark stone in patches; 30 dark stone threaded with cracks of cold violet-white light; 31 a black glass wall with violet light inside, seen straight on (a wall); 32 a wall of shattered glassy rock with dust frozen in the air in front of it, seen straight on (a wall).

Row 5 - THE WOUND (the deepest): 33 rock, flesh and black glass fused together; 34 dark red-violet tissue threaded with thin white light; 35 grey flesh studded with small closed eyes, subtle; 36 black stone with glowing green-yellow veins; 37 a tar-black floor with glowing bubbles; 38 a floor of crystallised bone; 39 a wall of red-violet flesh and black glass, seen straight on (a wall); 40 a wall of rock with unrecognisable animal shapes half sunk into it, seen straight on (a wall).

Row 6 - WATER AND RESTING TILES: 41 deep glowing green-yellow toxic water; 42 shallow glowing toxic water over stone; 43 black oily water; 44 rust-red water; 45 plain dark wet stone floor, the quiet tile; 46 plain dark stone floor with a little ash; 47 a dark iron grate over a black pit; 48 old dark flagstones, cracked, the foundations of an ancient tower reaching down this far.
```

Re-roll any cell that comes back gory (blood, open wounds) instead of grotesque, and any wall tile that isn't viewed
straight on.

### Slice order (`tools/slice_tile_sheet.py deadwind_dungeon`, to `assets/tiles/fallout_zone/`)

| row | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| 1 | fz_gouged_rock | fz_gravel | fz_seep_rock | fz_ash_earth | fz_scorched_rock | fz_rubble | fz_rock_wall | fz_seep_wall |
| 2 | fz_slag | fz_stain_rings | fz_ooze_stone | fz_deep_ash | fz_corroded | fz_crystal_floor | fz_slag_wall | fz_ooze_pool |
| 3 | fz_flesh | fz_flesh_stone | fz_bone_mat | fz_root_flesh | fz_blisters | fz_sinew | fz_flesh_wall | fz_bone_wall |
| 4 | fz_shattered | fz_black_glass | fz_echo_stone | fz_stopped_water | fz_aged_dust | fz_light_cracks | fz_glass_wall | fz_stopped_wall |
| 5 | fz_fused | fz_wound_tissue | fz_eye_flesh | fz_glow_veins | fz_tar | fz_bone_crystal | fz_wound_wall | fz_sunk_wall |
| 6 | fz_toxic_deep | fz_toxic_shallow | fz_black_water | fz_rust_water | fz_quiet_stone | fz_ash_stone | fz_iron_grate | fz_tower_flags |

---

## SHEET 7: 24 dungeon set pieces, 6 dungeon bosses, 2 cave bosses and 4 rares (MAGENTA KEY)

```
Generate ONE sprite sheet image, 2048x2048, a 6 columns x 6 rows grid = 36 separate sprites, each cell about 341x341. Flat pure #FF00FF magenta background everywhere. Each sprite is ONE single object or figure, centred in its own cell with a wide margin, not touching or overlapping its neighbours or the image edge, nothing cropped. No ground, no floor patch, no liquid under it unless the prompt puts the liquid inside the object's own rim, no cast shadow, no glow halo bleeding onto the background, no text, no labels, no numbers, no grid lines, no frames, no borders. Never use magenta or pink anywhere on the sprites themselves (flesh is grey-pink, ashen and bruised, never magenta). Nothing modern or from the real world: no machines, no concrete, no gas masks (masks are beaked plague-doctor masks of leather).

Match the attached references EXACTLY in style, camera angle, outline and level of detail: they are from the same set. Painterly semi-realistic WoW Classic style: strong readable silhouette, soft dark outline, chunky simple shapes legible at small size, consistent soft lighting from the top-left.

Camera: rows 1 to 4 are dungeon set pieces in isometric three-quarter view elevated about 45 degrees, EVERY one turned the same way, front face toward the lower-right. Rows 5 and 6 are bosses and rares, full body, facing three-quarters toward the lower-right, nothing cropped. Consistency of angle across the sheet is critical.

Setting: THE FALLOUT ZONE, the dungeon inside the wound under Deadwind Pass, where time broke and a sickly glowing fallout mutated everything. It gets worse the deeper you go: dark rock, then glowing fallout, then flesh growing over stone, then broken time, then the wound itself. Grotesque and disgusting, not gory: tumours, extra limbs, fused bodies, sores, glowing pustules, bone through skin. No blood sprays, no open gore. Palette: black rock, grey ash, rust, sickly glowing green-yellow, wet grey-pink flesh, bone white, bruise purple, deep red-violet, cold violet-white light.

Sprites keep their RELATIVE scale: bosses are drawn LARGER than ordinary creatures, and the last boss (cell 30) is the largest figure on the sheet; the heart (cell 23) and the wound (cell 24) are the largest set pieces; a fallen satchel or a crystal cluster is visibly far smaller. Do not blow each one up to fill its own cell.

Sprites are numbered row by row, left to right, top to bottom:

Row 1 - THE MOUTH: 1 a rough stone stair going down into the dark, glowing green from below; 2 a barricade of timber and sacks with a green lantern, the volunteers' last forward post; 3 a dead volunteer's kit on the ground, a cracked beaked leather mask, a satchel and a lantern; 4 a rock pillar wrapped in glowing seep crystals; 5 a collapsed timber tunnel support; 6 a cracked ancient foundation stone carved with runes.

Row 2 - THE FALLOUT: 7 a pool of glowing slag in a crusted rock rim, the glow inside the rim; 8 a vent breathing glowing green-yellow fumes; 9 a tall cluster of jagged slag crystals; 10 glowing ooze spilling from a rock lip into a basin, all inside the basin's rim; 11 a heap of mutated carcasses half dissolved into slime; 12 a corroded iron cage hanging from a chain with something fused inside it.

Row 3 - THE FLESH: 13 a pillar of veined grey-pink flesh holding up a ceiling; 14 a pulsing flesh sac on the floor with a shape moving inside; 15 a cluster of eyes set in a lump of flesh; 16 a giant ribcage arch big enough to walk under; 17 a flesh pod split open, empty and wet; 18 an altar of fused bone.

Row 4 - BROKEN TIME AND THE WOUND: 19 an explosion stopped mid-burst, rock shards hanging in the air around a grey flash; 20 a man-tall shard of black glass with violet light inside; 21 a ring of stones floating and turning slowly; 22 a tear in the air, a tall slit of violet-white light with black edges; 23 a heart-like mass of tissue and black glass the size of a cart, veins running off it; 24 the wound itself, a pit of red-violet light ringed by fused rock and flesh, the light inside the rim.

Row 5 - THE FALLOUT ZONE'S BOSSES: 25 Gristlemaw, a heap of fused Deadwind ogres moving as one body, many arms, three faces; 26 the Stopped Man, a volunteer in an oilcloth coat and a cracked beaked leather mask, frozen mid-scream in grey glassy stopped time, shards orbiting him; 27 Broodmother Vexis, a colossal mutated widow spider, tumorous, its egg sacs glowing; 28 the Glow-Eater, a bloated thing swollen on fallout, its skin stretched thin and glowing from inside; 29 Archivist Nine, an old tower mage shown as nine overlapping copies of himself at different ages, books orbiting him; 30 the Wound's Heart, a towering mass of flesh, black glass and violet-white light with arms made of fused bodies, the last boss and the largest figure on the sheet.

Row 6 - CAVE BOSSES AND RARES: 31 the Silk Mother, a widow queen fused with her own cocoon; 32 the Drowned Thing, a bloated mass of mud, roots and drowned animals; 33 Old Three-Heads, a great wolf whose three heads are the same wolf young, grown and old; 34 the Wagon Driver, a grey echo of a carter with his horses fused to the wagon; 35 Mog'grak the Twice-Born, an ogre chief fused with his own younger self; 36 the Crow King, a giant crow made of many crows fused together, eyes everywhere.
```

The boss and rare names are working names for the art. Kyle settles the dungeon's name and roster when it's built.

### Slice order (`tools/slice_building_sheet.py deadwind_dungeon <sheet.png>`, to `assets/creatures/_src/deadwind/`; the 24 set pieces then move to `assets/tiles/dungeon_props/`)

| row | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 1 | fz_down_stair | fz_barricade | fz_dead_kit | fz_crystal_pillar | fz_collapsed_support | fz_rune_stone |
| 2 | fz_slag_pool | fz_fume_vent | fz_slag_cluster | fz_ooze_fall | fz_carcass_heap | fz_hanging_cage |
| 3 | fz_flesh_pillar | fz_flesh_sac | fz_eye_cluster | fz_rib_arch | fz_open_pod | fz_bone_altar |
| 4 | fz_stopped_blast | fz_glass_shard | fz_floating_ring | fz_air_tear | fz_heart_mass | fz_wound_pit |
| 5 | fz_boss_gristlemaw | fz_boss_stopped_man | fz_boss_vexis | fz_boss_glow_eater | fz_boss_archivist | fz_boss_wound_heart |
| 6 | dw_boss_silk_mother | dw_boss_drowned_thing | dw_rare_three_heads | dw_rare_wagon_driver | dw_rare_moggrak | dw_rare_crow_king |

---

## SHEET 8: 9 giant landmarks (MAGENTA KEY)

```
Generate ONE sprite sheet image, 2048x2048, a 3 columns x 3 rows grid = 9 separate large landmark sprites, each cell about 682x682. Flat pure #FF00FF magenta background everywhere. Each sprite is ONE single landmark, centred in its own cell with a wide margin, not touching or overlapping its neighbours or the image edge, nothing cropped. No surrounding ground beyond the landmark's own base, no cast shadow, no glow halo bleeding onto the background (glow stays inside the landmark), no people, no text, no labels, no numbers, no grid lines, no frames, no borders. Never use magenta or pink anywhere on the landmarks themselves. Nothing modern or from the real world EXCEPT cell 1: the Ferris wheel is the only modern object on this sheet, and nothing else may borrow its style.

Match the attached references EXACTLY in style, camera angle, outline and level of detail: they are from the same set. Painterly semi-realistic WoW Classic style: strong readable silhouette, soft dark outline, chunky simple shapes legible at small size, consistent soft lighting from the top-left.

Camera: isometric three-quarter view elevated about 45 degrees. EVERY landmark is turned the same way, front face toward the lower-right. Consistency of angle across all 9 is critical.

Setting: DEADWIND PASS, a dead mountain pass where time broke and a sickly glowing fallout leaked out of the ground and mutated everything. Dark, grim and disgusting. Palette: dead grey-brown, black rock, grey ash, rust, bruise purple, sickly glowing green-yellow, cold violet-white for broken time, and the faded yellow paint of the wheel's gondolas, the brightest colour in the whole pass.

Landmarks keep their RELATIVE scale: the Ferris wheel and the dark tower are the tallest, filling most of their cells; the others are still huge, but lower and wider. Do not shrink the wheel or the tower to match the rest.

Landmarks are numbered row by row, left to right, top to bottom:

Row 1: 1 THE WHEEL: a tall abandoned Ferris wheel, its lattice frame of rusted red-brown steel, round yellow gondolas with scalloped rims hanging from it, the yellow paint faded and flaking, two gondolas hanging askew, dead grey birch saplings growing up through its base, the whole thing standing over a cracked crater whose bottom glows sickly green-yellow (the glow kept inside the crater's rim); 2 THE DARK TOWER: a tall black stone wizard's tower on a jagged crag, ancient, sealed, its windows dark, thin cracks of cold violet-white light running across its stone as if time had broken around it; 3 THE STOPPED AVALANCHE: a whole slope of boulders and dust stopped in mid-fall over a gorge, hanging still in the air.

Row 2: 4 THE BROKEN BRIDGE: a stone bridge over a gorge stopped in the middle of collapsing, its broken pieces hanging in the air; 5 THE OGRE GATE: the great gate of an ogre compound, logs, hides and skulls, overgrown with grey-pink flesh-like growth and glowing pustules; 6 THE GREAT CRYPT: a large stone mausoleum in a graveyard, cracked open down its front, sickly green light inside.

Row 3: 7 THE ELDER TREE: a colossal dead tree aged ten thousand years in an instant, grey, crumbling to dust at its edges, a small living-but-colourless sapling of itself standing at its foot; 8 THE CONTAINMENT SPIRE: a tall tower of dark stone and black iron raised by the volunteers at the edge of the rupture, its sides carved with glowing blue runes, iron chains anchoring it to the rock, bone wards hung from it; 9 THE TUNNEL MOUTH: a fresh split in a mountainside of dark jungle rock, a tunnel going in, a faint sick green glow deep inside it.
```

Re-roll the wheel if it comes back new, clean or lit up; it should look abandoned for decades. Re-roll the tower if it
looks like a castle.

### Slice order (`tools/slice_building_sheet.py deadwind_landmarks <sheet.png>`, to `assets/buildings/`)

| row | 1 | 2 | 3 |
|---|---|---|---|
| 1 | dw_ferris_wheel | dw_dark_tower | dw_stopped_avalanche |
| 2 | dw_broken_bridge | dw_ogre_gate | dw_great_crypt |
| 3 | dw_elder_tree | dw_containment_spire | dw_tunnel_mouth |
