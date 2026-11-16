# Stonetalon art prompts (4 sheets)

For `docs/stonetalon_brief.md`. Reused from the library: Aspen's burned materials and props for the blowdown, the tau_ building set for Sun Rock Retreat, lava tiles, bears, fire and earth elementals, harpies, goblins and panthers. These four sheets cover what nothing in the library does.

| Sheet | What | Key |
|---|---|---|
| 1 | 48 ground, wall and dungeon-interior tiles | **NO magenta** (tiles run flush to their edges) |
| 2 | 16 giant trees: redwoods, sequoias, the fallen, the dungeon's tree | magenta |
| 3 | 36 props and set pieces | magenta |
| 4 | 36 creatures and the dungeon's bosses | magenta |

**Priority if you only do some today:**
1. **Sheet 2 (the trees).** The West can't be built without them.
2. **Sheet 1 (the tiles).**
3. **Sheets 3 and 4.**

The East can start on existing art meanwhile.

---

## SHEET 1 — 48 tiles (NO magenta)

> Generate ONE texture sheet image, 2048x1536, laid out as a strict 8 columns x 6 rows grid = 48 separate seamless ground and wall textures. Each cell is COMPLETELY FILLED by its texture, edge to edge, touching its neighbours with no gap, no border, no background colour, no magenta, no frames, no gutters, no text, no labels, no numbers. Every texture must TILE SEAMLESSLY with itself - no single large feature that would obviously repeat, no lighting gradient across the cell, flat even illumination, no vignette, no baked shadows. Straight top-down view.
>
> Painterly semi-realistic WoW Classic style, muted and slightly desaturated, readable at small size. Setting: STONETALON, a mountain range where Earth's Pacific Northwest landed: coastal redwood fog forest, giant sequoia slopes, and a grey volcanic blast zone below a dormant volcano. Palette: redwood red-brown and cinnamon, deep fern green, wet moss, fog-pale grey-green; ash grey, pumice cream, basalt black and sulphur yellow for the volcano; warm red sandstone for the tauren.
>
> Tiles are numbered row by row, left to right:
>
> Row 1 - THE REDWOOD FOG VALLEY: 1 dark red-brown redwood needle duff (the main forest floor); 2 redwood sorrel carpet, low clover-like green leaves over duff; 3 sword fern understory seen from above; 4 wet moss over dark soil; 5 pale damp duff under thin fog haze; 6 tangle of mossy surface roots over earth; 7 red bark-chip and needle litter; 8 clear creek water over brown gravel.
>
> Row 2 - THE SEQUOIA SLOPES: 9 cinnamon-red sequoia bark flakes and needle litter; 10 dry mountain pine-needle floor with small cones; 11 sunlit meadow grass between the giants; 12 grey granite outcrop with yellow-green lichen; 13 dry brown duff with scattered big pinecones; 14 packed dirt forest trail; 15 trail edge with needles and grass creeping in; 16 grey granite cliff face with cracks and moss (a wall).
>
> Row 3 - THE BLOWDOWN (volcanic blast zone): 17 flat grey ash plain; 18 grey ash with pink fireweed sprouting through; 19 ash with broken grey wood splinters; 20 cream pumice gravel; 21 dried grey volcanic mudflow, cracked; 22 wind-rippled ash dunes; 23 rain-cut ash gully, darker grey; 24 trodden ash path with boot and cart marks.
>
> Row 4 - THE VOLCANO: 25 black basalt rock; 26 red-brown cinder scoria gravel; 27 yellow sulphur crust over grey rock; 28 dark steaming wet volcanic ground; 29 glossy black obsidian floor; 30 black basalt cliff wall with columnar cracks (a wall); 31 deep cold blue crater-lake water; 32 shallow turquoise crater-lake water over pale stones.
>
> Row 5 - SUN ROCK, THE GRIMTOTEM, THE MULGORE RIM: 33 warm red sandstone plateau rock; 34 tauren stone plaza with faded painted patterns; 35 packed red-earth camp ground; 36 red sandstone cliff wall (a wall); 37 Grimtotem trampled dark earth with bones and blood-dark stains; 38 dead black grass at the edge of a cursed land; 39 cracked earth with inky black seeping from the cracks; 40 inky black void ground, almost lightless, a faint dark red undertone.
>
> Row 6 - INSIDE THE GIANT SEQUOIA (a dungeon): 41 smooth red-gold heartwood floor with faint growth rings; 42 heartwood wall of tight concentric growth rings (a wall); 43 rough dark inner bark wall (a wall); 44 golden amber sap pool, glossy; 45 bark-beetle galleries, wood bored with winding tunnels; 46 top of a huge branch seen from above, a bark walkway; 47 dense green needle canopy seen from above (a floor of foliage); 48 open sky seen from high above, white clouds over far blue (what's below the branches).

Re-roll any cell that comes back with a visible tile seam or a lighting gradient. The failure mode for row 3 is "grey concrete"; it should read as ash and pumice.

### Slice order (`tools/slice_tile_sheet.py`, a new `stonetalon` set, to `assets/tiles/stonetalon/materials/`)

| row | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| 1 | st_redwood_duff | st_redwood_sorrel | st_sword_ferns | st_wet_moss | st_fog_duff | st_mossy_roots | st_bark_litter | st_creek_gravel |
| 2 | st_sequoia_litter | st_needle_cones | st_meadow_grass | st_granite_lichen | st_dry_duff | st_trail | st_trail_edge | st_granite_cliff |
| 3 | st_ash_plain | st_ash_fireweed | st_ash_splinters | st_pumice_gravel | st_mudflow | st_ash_dunes | st_ash_gully | st_ash_path |
| 4 | st_basalt | st_scoria | st_sulphur | st_steaming_ground | st_obsidian | st_basalt_cliff | st_crater_deep | st_crater_shallow |
| 5 | st_sandstone | st_tauren_plaza | st_camp_earth | st_sandstone_cliff | st_grimtotem_earth | st_dead_grass | st_dark_seep | st_void_ground |
| 6 | st_heartwood_floor | st_ring_wall | st_inner_bark_wall | st_sap_pool | st_beetle_galleries | st_branch_walk | st_canopy_floor | st_sky_below |

---

## SHEET 2 — 16 giant trees (MAGENTA KEY)

> Generate ONE sprite sheet image, 2048x2048, a 4 columns x 4 rows grid = 16 separate tree sprites. Flat pure #FF00FF magenta background everywhere. Each tree is ONE single object, centred in its own cell with a wide margin, not touching or overlapping its neighbours or the image edge. No ground, no grass patch, no dirt patch, no cast shadow, no text, no labels, no numbers, no grid lines, no frames. Never use magenta or pink anywhere on the trees themselves.
>
> Painterly semi-realistic WoW Classic style: strong readable silhouette, soft dark outline, chunky simple shapes legible at small size, consistent soft lighting from the top-left. Camera: the same three-quarter top-down view as a WoW Classic prop, elevated about 45 degrees. The trunk base sits at the bottom of the cell and the crown at the top, so a character can walk past the trunk with the crown overhead. Consistency of angle across all 16 is critical.
>
> Setting: STONETALON, where Earth's coastal redwoods and giant sequoias landed among the mountain's own great trees. These are GIANT trees: massive straight red-brown trunks, deeply furrowed fibrous bark, the lowest branches very high, dark green needle crowns. Redwoods are taller and slimmer with darker, wetter bark; sequoias are wider, with cinnamon-orange bark and rounded crowns.
>
> Trees keep their RELATIVE scale: the great sequoia is the largest sprite on the sheet, and a young redwood is visibly far smaller. Do not blow each one up to fill its own cell.
>
> Row 1 - COASTAL REDWOODS: 1 a towering old-growth redwood, very tall and straight, with a narrow dark crown; 2 two redwoods grown from one base, forking near the ground; 3 a young redwood, slim and dense green; 4 a "fairy ring", five young redwoods in a circle around an old cut stump.
>
> Row 2 - GIANT SEQUOIAS: 5 THE GREAT SEQUOIA, the largest tree on the sheet, an enormous cinnamon trunk wider than a house, with a tall split in its base like a doorway glowing faint gold inside; 6 a mature giant sequoia with a rounded crown; 7 a giant sequoia with a black fire scar hollowing one side of its base; 8 a young sequoia, conical and bright green.
>
> Row 3 - THE FALLEN (the blast and the loggers): 9 a giant redwood log lying on its side, grey and weathered by ash; 10 a toppled sequoia with its huge root plate torn up and standing on end; 11 a giant snag, a grey dead trunk snapped off halfway up; 12 a giant logged stump, flat-topped, with axe cuts and square springboard notches in its side.
>
> Row 4 - THE FOREST'S OWN: 13 a hollow redwood whose burned-out base you could walk into; 14 a nurse log, a fallen trunk with ferns and three small saplings growing out of its top; 15 a redwood with a huge knobbed burl swelling from its trunk; 16 a giant tree crown seen from above, a dark green canopy disc of needles with no trunk visible (an overlay that hangs over paths).

Re-roll any tree that comes back as an ordinary pine or oak; the failure mode is "normal forest tree", and these must read as giants.

### Slice order (a new `stonetalon_trees` set, to `assets/tiles/stonetalon/props/`)

| row | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| 1 | st_redwood_giant | st_redwood_twin | st_redwood_young | st_redwood_ring |
| 2 | st_sequoia_great | st_sequoia_mature | st_sequoia_scarred | st_sequoia_young |
| 3 | st_log_redwood | st_sequoia_rootplate | st_giant_snag | st_logged_stump |
| 4 | st_redwood_hollow | st_nurse_log | st_redwood_burl | st_canopy_overlay |

---

## SHEET 3 — 36 props and set pieces (MAGENTA KEY)

> Generate ONE sprite sheet image, 2048x2048, a 6 columns x 6 rows grid = 36 separate sprites. Flat pure #FF00FF magenta background everywhere. Each sprite is ONE single object, centred in its own cell with a wide margin, not touching or overlapping its neighbours or the image edge. No ground, no dirt patch, no grass, no cast shadow, no text, no labels, no numbers, no grid lines, no frames. Never use magenta or pink anywhere on the objects themselves.
>
> Painterly semi-realistic WoW Classic style: strong readable silhouette, soft dark outline, chunky simple shapes legible at small size, consistent soft lighting from the top-left. Camera: isometric three-quarter view elevated about 45 degrees. EVERY object is turned the same way, front face toward the lower-right. Consistency of angle across all 36 is critical.
>
> Setting: STONETALON. Rows 1 and 2 are the goblin Venture Co.'s logging and salvage works: rusty iron, riveted plates, green-painted machinery, crude timber and rope, sawdust. Row 3 is the volcano. Row 4 is the Grimtotem tauren: dark hides, blood-red paint, bone and black feathers. Row 5 is the harpies' crags and the mine. Row 6 is the edge of Mulgore, a cursed land of permanent night, plus small forest pieces.
>
> Objects keep their RELATIVE scale: a lantern is visibly far smaller than a sawmill. Do not blow each one up to fill its own cell.
>
> Row 1 - VENTURE CO. LOGGING: a log deck of five huge cut logs stacked and chained; a steam-powered saw rig with a big round blade and a smokestack; a goblin steam winch on a sled with a cable drum (a donkey engine); a logging bunkhouse of corrugated iron and planks; a wrecked shredder (a two-legged goblin logging walker) toppled on its side; a smoking sawdust burner shaped like a cone.
>
> Row 2 - THE SALVAGE AND THE CUTLINE: a flatbed log sled with one giant log chained on it; a pile of fresh sawdust and bark slabs; a Venture Co. signpost with a crude painted tree and a cross through it; a stack of blasting powder kegs; a goblin lookout tower of scrap timber; a rope-and-pulley climbing rig hanging from above (for climbing giant trunks).
>
> Row 3 - THE VOLCANO: a fumarole vent crusted with yellow sulphur, with a plume of white steam; a cluster of three small steam vents; a large glossy black obsidian boulder; the mouth of a lava tube, a dark round cave opening in black basalt with a faint orange glow inside; a cream pumice boulder pile; a small black cinder cone, smoking.
>
> Row 4 - THE GRIMTOTEM: a tall Grimtotem war totem of carved dark wood, painted blood red, with a horned skull; a large Grimtotem tent of dark hides and black feathers; a Grimtotem war drum on a frame; a palisade section of sharpened dark logs with red handprints; a ritual stone circle of standing stones with red paint; a rack of drying hides and a horned skull.
>
> Row 5 - THE CRAGS AND THE MINE: a harpy nest of sticks, bones and torn cloth on a rock; a tall wind-carved rock spire with harpy perches; a weathered rock arch scoured smooth by wind; a Venture Co. mine entrance framed in timber, cut into a cliff, with a lantern and mine cart rails; a mine cart full of ore; a small tauren scouts' camp (a hide lean-to with a fire pit) for a quest camp.
>
> Row 6 - THE MULGORE RIM AND THE FOREST: a fence of black thorned stakes hung with torn tauren totems; a tauren burial platform on tall poles, burned and broken; a border cairn of dark stones with a single dim red lantern; a big clump of sword ferns; a patch of redwood sorrel with tiny white flowers; a moss-covered boulder with a small fern growing on top.

### Slice order (a new `stonetalon` set; row 1's bunkhouse and row 2's tower to `assets/buildings/`, the rest to `assets/tiles/stonetalon/props/`)

| row | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 1 | st_log_deck | st_saw_rig | st_steam_winch | st_venture_bunkhouse | st_shredder_wreck | st_sawdust_burner |
| 2 | st_log_sled | st_sawdust_pile | st_venture_sign | st_powder_kegs | st_venture_tower | st_climbing_rig |
| 3 | st_fumarole | st_steam_vents | st_obsidian_boulder | st_lava_tube_mouth | st_pumice_pile | st_cinder_cone |
| 4 | st_grim_war_totem | st_grim_tent | st_grim_drum | st_grim_palisade | st_grim_stone_circle | st_grim_hide_rack |
| 5 | st_harpy_nest | st_wind_spire | st_wind_arch | st_mine_entrance | st_ore_cart | st_scout_camp |
| 6 | st_rim_thorn_fence | st_burial_platform | st_rim_cairn | st_ferns_big | st_sorrel_patch | st_moss_boulder |

---

## SHEET 4 — 36 creatures and the sequoia's bosses (MAGENTA KEY)

> Generate ONE sprite sheet image, 2048x2048, a 6 columns x 6 rows grid = 36 separate creature sprites. Flat pure #FF00FF magenta background everywhere. Each creature is ONE single figure, centred in its own cell with a wide margin, not touching or overlapping its neighbours or the image edge. No ground, no dirt patch, no cast shadow, no text, no labels, no numbers, no grid lines, no frames. Never use magenta or pink anywhere on the creatures themselves.
>
> Painterly semi-realistic WoW Classic style: strong readable silhouette, soft dark outline, chunky simple shapes legible at small size, consistent soft lighting from the top-left. Every creature faces three-quarters toward the lower-right, full body, feet or base included. Consistency of angle across all 36 is critical.
>
> Setting: STONETALON, a mountain range of giant redwoods and sequoias below a volcano, where goblin loggers, hardline tauren and harpies fight over the forest. Palette: redwood red-brown, deep green, ash grey, basalt black, sulphur yellow, Grimtotem blood red.
>
> Creatures keep their RELATIVE scale: a boss is visibly far larger than a cougar, and a goblin is small. Do not blow each one up to fill its own cell.
>
> Row 1 - THE GRIMTOTEM, hardline tauren: huge bull-headed humanoids with dark brown and black fur, blood-red war paint, bone and black-feather gear. A warrior with a two-handed totem axe; a shaman with a staff crackling with red-orange flame; a hunter with a heavy spear and a bow on his back; a brute in spiked hide armour with a stone maul; a mystic with a bowl of smoking herbs and a skull rattle; a Grimtotem elder chieftain, old and scarred, in a feathered headdress.
>
> Row 2 - THE VENTURE CO., goblin loggers: small green-skinned goblins in hard hats, overalls and leather aprons. A logger with a long-handled axe; a sawyer carrying a huge two-man crosscut saw on his shoulder; a demolitionist with a lit stick of blasting powder; a foreman with a clipboard, a cigar and a pistol; a rigger hanging off a climbing rope with spiked boots; a SHREDDER, a two-legged iron logging walker with saw-blade arms, a goblin in its cockpit.
>
> Row 3 - THE WINDSHEAR AND THE WILD: a Windshear harpy, blue-grey feathered, mid-shriek; a Windshear storm witch, a harpy wreathed in wind; a mountain cougar, tawny and lean; a bull elk with a huge rack of antlers; a bald eagle with spread wings; a black bear, glossy and heavy.
>
> Row 4 - THE VOLCANO'S ELEMENTALS AND THE FOREST: an ash elemental, a swirling man-shape of grey ash with ember eyes; a pumice golem, cream and pitted stone; a steam elemental, white vapour around a glowing yellow sulphur core; a magma-veined basalt elemental; a giant bark beetle, glossy black and the size of a pony; a redwood ancient, a treant made of red bark with a mossy beard and fern hair.
>
> Row 5 - IN THE GREAT TREE AND AT THE RIM: a bark beetle swarm-mother, a bigger winged beetle; a living sap ooze of golden amber with things trapped inside; a giant canopy owl with tufted ears; a sky-serpent coiled on a branch, green and feathered; a RISEN TAUREN from Mulgore, a dead tauren hunter standing again, grey-black hide, empty white eyes, still holding its spear; a risen tauren stalker, gaunter and hunched, its horns broken, dragging a chain.
>
> Row 6 - THE GREAT SEQUOIA'S BOSSES, large and distinct: Rigboss Gazzle, a goblin foreman on a rope-and-pulley climbing platform with a winch and a shotgun; the Heartrot Queen, a huge bark beetle queen with a swollen egg sac; Ambermaw, a giant golden sap elemental with a whole goblin trapped inside it; Old Talonwing, a colossal storm-roc, an eagle-like sky beast with lightning in its feathers, nesting in the crown; Topper Kezzik, the Venture Co.'s climbing shredder, a huge spider-legged iron walker clinging to bark with a giant chainsaw arm; the Eldest, the great tree's own spirit, a towering ancient of cinnamon bark and needles, the largest figure on the sheet.

Re-roll any risen tauren that comes back cartoonish or bloodless; they're the first look at Mulgore and should be unsettling. Re-roll any goblin that comes back human-sized.

### Slice order (a new `stonetalon_creatures` set, to `assets/creatures/_src/stonetalon/`)

| row | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 1 | st_grim_warrior | st_grim_shaman | st_grim_hunter | st_grim_brute | st_grim_mystic | st_grim_elder |
| 2 | st_venture_logger | st_venture_sawyer | st_venture_demolitionist | st_venture_foreman | st_venture_rigger | st_venture_shredder |
| 3 | st_windshear_harpy | st_windshear_witch | st_cougar | st_bull_elk | st_bald_eagle | st_black_bear |
| 4 | st_ash_elemental | st_pumice_golem | st_steam_elemental | st_basalt_elemental | st_bark_beetle | st_redwood_ancient |
| 5 | st_beetle_mother | st_sap_ooze | st_canopy_owl | st_sky_serpent | st_risen_tauren | st_risen_stalker |
| 6 | st_boss_rigboss_gazzle | st_boss_heartrot_queen | st_boss_ambermaw | st_boss_old_talonwing | st_boss_topper_kezzik | st_boss_the_eldest |

The boss names are drafts for you to change.
