# Azshara art prompts (sheets 1 to 6)

For `docs/azshara_brief.md`. Kyle, 17 Nov 2026: "we can get up to 6 art sheets!", split as he approved: ground tiles,
props and Highborne ruins, Talrendis Landing, Timbermaw Hold, creatures, the two dungeons.

**What already exists and is reused, so it isn't asked for again:**
- **Buildings:** the full blood elf building set (`be_*`: inn, spires, sanctum, library, market stalls, gatehouse
  and so on) and the orc town sets (`orc_*`). The Landing's sheet is only the salvage camp's own pieces.
- **Timbermaw:** the Timbermaw lodge and totem (`fw_timbermaw_*`), the Ashenvale furbolg lodge, bonfire, totem and
  den mouth, and six furbolg NPC looks. The Hold's sheet is the caldera city's bigger pieces.
- **Creatures:**
  - Felwood's satyrs (rogue, trickster, shadowstalker, felsworn, hellcaller, lord), felguard and infernal. The
    creature sheet adds Azshara's own cursed satyrs, not more Jadefire.
  - Three naga (two myrmidons and a warrior), a mana wyrm, an arcane elemental, dragon whelps, and two Plaguelands
    ghosts.
- **Ground:** Ashenvale's forest materials (the autumn floor is new; the green Ashenvale floor isn't reused here).

**Priority, for the first playable slice (West Azshara, Talrendis Landing, Timbermaw Hold):** sheets 1, 3 and 4 first,
then 2. Creatures and dungeons can come while the slice is built.

Every sheet uses the shared header rules:
- ONE image, 2048x2048, flat pure #FF00FF magenta background.
- Each sprite alone in its cell with a wide margin: no ground patch, no shadow, no text or grid lines.
- Never magenta on the subject.
- Painterly semi-realistic WoW Classic style, soft dark outline, light from the top-left.
- Buildings and props: isometric three-quarter view, with the front toward the lower-right.
- Creatures: three-quarters toward the lower-right, full body.
- Relative scale is kept: a wyrm is small, a boss is big.

The ground sheet is the exception: square seamless textures, straight top-down.

---

## SHEET 1: 48 Azshara ground tiles (seamless squares)

> Generate ONE image, 2048x2048, an 8 columns x 6 rows grid = 48 separate SQUARE ground textures, each tile filling
> its own cell edge to edge, each one SEAMLESS (tileable on all four sides). Straight top-down view, no perspective,
> no objects, no props, no shadows from objects, no text, no labels, no grid lines. Painterly semi-realistic WoW
> Classic ground texture style, soft even light.
>
> Setting: AZSHARA, the ancient night elf coast, forever in autumn. Palette for rows 1-3: warm red, rust, burnt orange
> and gold leaves over dark loam, mossy greens kept low. Rows 4-6 turn to the drowned city: wet white marble, silver,
> pale teal, verdigris and coral pink, with dark sea-teal water. Keep every row readable and not too busy.
>
> Row 1 - AUTUMN FOREST: forest floor thick with red and orange fallen leaves; the same floor with gold leaves and
> dark loam showing; autumn grass, gold-tinted; autumn grass trampled with dirt; dark wet loam with a few red leaves;
> a carpet of crimson undergrowth; pine needle floor with orange leaves; a mossy autumn floor with small white
> mushrooms.
> Row 2 - HIGHLANDS AND THE MOUNTAINS: rocky autumn hillside, grey stone and orange grass; grey mountain scree;
> lichen-covered stone, orange and green lichen; dry gold mountain grass; packed earth trail; a furbolg-trodden path
> of dark earth and wood chips; a honey-gold clay ground; a snow-dusted rock (the high mountain tops only).
> Row 3 - THE CURSE AND THE DIG: satyr-cursed ground, dark violet-black soil with faint green fel veins; scorched
> earth with ash; fel-rot soil, black with sickly green moss; the salvage dig's churned brown earth with stone chips;
> wooden plank walkway over mud (tileable along its length); excavated pale sand with marble fragments; leyline
> ground, autumn grass with faint glowing blue arcane lines running through it; blue crystal-glass ground, the land
> itself turning to pale blue crystal.
> Row 4 - HIGHBORNE STONE: Highborne paving of pale cream marble with fine gold inlay; the same paving cracked and
> overgrown with red leaves; Highborne mosaic floor with a faint crescent-moon pattern (subtle, not a repeating
> emblem in every square); moss-covered ancient flagstone; a white marble road, worn; a broken marble terrace with
> grass in the cracks; Highborne violet-and-silver tile, faded; a ruined plaza of large pale slabs.
> Row 5 - THE DROWNED CITY: wet white marble with a thin sheen of water; marble with barnacles and green verdigris;
> drowned mosaic, teal and silver, cracked; coral-encrusted stone, pink and white coral; seaweed-strewn marble;
> silt and shell sand, grey-white; tide-pool rock, dark and wet with tiny pools; kelp-tangled flooded floor.
> Row 6 - WATER AND SHORES: deep sea water, dark teal; shallow coastal water over white sand; teal shallows over
> drowned marble (pale stone visible under the water); Lake Mennar's calm blue water; wet dark sand beach; pale shell
> beach; the storm-churned surf of the Bay of Storms, grey-teal with foam; glowing arcane water, pale blue (the
> leyline pools only).

### Slice order (a new `azshara_ground` set, to `assets/tiles/azshara/ground/`)

| row | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| 1 | az_leaf_floor | az_leaf_gold | az_grass_gold | az_grass_trod | az_loam | az_crimson_brush | az_needle_leaf | az_moss_shroom |
| 2 | az_rock_hill | az_scree | az_lichen_stone | az_mountain_grass | az_trail | az_furbolg_path | az_honey_clay | az_snow_rock |
| 3 | az_cursed_soil | az_scorched | az_felrot_soil | az_dig_earth | az_plank_walk | az_dig_sand | az_leyline_grass | az_crystal_glass |
| 4 | az_highborne_paving | az_paving_leaves | az_moon_mosaic | az_mossy_flag | az_marble_road | az_marble_terrace | az_violet_tile | az_plaza_slab |
| 5 | az_wet_marble | az_barnacle_marble | az_drowned_mosaic | az_coral_stone | az_seaweed_marble | az_shell_silt | az_tidepool_rock | az_kelp_floor |
| 6 | az_sea_deep | az_sea_shallow | az_drowned_shallows | az_lake_water | az_wet_sand | az_shell_beach | az_storm_surf | az_arcane_water |

The ground follows "less is more": a map uses only a handful of these, a dozen at most.

---

## SHEET 2: 36 Azshara props and Highborne ruins (open world)

> Isometric three-quarter view, every object turned the same way, front toward the lower-right. 6 x 6 grid, 36
> sprites, magenta key, the shared rules.
>
> Row 1 - THE AUTUMN FOREST: a tall Azshara tree with a broad crown of red and orange leaves; a smaller gold-leaved
> tree; a cluster of three slim autumn birches; a fallen autumn log with red moss; a crimson-leaved bush; a mossy
> boulder with orange lichen.
> Row 2 - HIGHBORNE RUINS: a broken Highborne spire, tall and slender, pale marble with gold trim and a violet roof
> half gone; a toppled column of white marble; a ruined archway with crescent-moon carvings, overgrown with red
> leaves; a statue of a Highborne noblewoman, cracked, one arm missing; a crumbling stone wall section with a gold
> moon emblem; a Highborne fountain, dry and broken.
> Row 3 - THE RISING: a drowned spire rising out of water, wet and hung with seaweed; a barnacle-covered marble statue
> of a Highborne sorceress; a coral-grown archway; a toppled drowned obelisk with glowing blue runes; a cluster of
> pink and white coral; a giant clam shell, open.
> Row 4 - THE SALVAGE: a wooden excavation scaffold with ropes and a pulley; a crate of salvaged Highborne relics
> (gold, marble fragments, a glowing orb); an arcane containment pylon of blood elf gold and red, crackling blue;
> an orc dig cart full of rubble; a stack of marked survey stakes and a tripod; a canvas-covered find under guard
> ropes.
> Row 5 - THE LEYLINES AND THE BLUES: a tall blue arcane crystal formation; a leyline node, a ring of standing stones
> glowing blue; a crystal-glassed tree, half turned to pale blue crystal; a blue dragon's scale-shed pile; a broken
> mana tower of the Highborne, pale and glowing; a small cluster of glowing blue mushrooms.
> Row 6 - THE CURSE AND THE COAST: a satyr totem of horns and skulls with violet cloth; a satyr bonfire of green fel
> flame; a cursed tree, twisted black with violet leaves; a shipwreck's prow on the sand; a naga banner of
> scaled teal cloth on a coral pole; a naga tide-altar of coral and pearl.

### Slice order (a new `azshara_props` set, to `assets/tiles/azshara/props/`)

| row | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 1 | az_autumn_tree | az_gold_tree | az_birch_trio | az_autumn_log | az_crimson_bush | az_lichen_boulder |
| 2 | az_broken_spire | az_toppled_column | az_moon_arch | az_noble_statue | az_ruin_wall | az_dry_fountain |
| 3 | az_drowned_spire | az_barnacle_statue | az_coral_arch | az_drowned_obelisk | az_coral_cluster | az_giant_clam |
| 4 | az_dig_scaffold | az_relic_crate | az_containment_pylon | az_dig_cart | az_survey_stakes | az_covered_find |
| 5 | az_arcane_crystal | az_leyline_node | az_crystal_tree | az_scale_pile | az_mana_tower | az_glow_shrooms |
| 6 | az_satyr_totem | az_fel_bonfire | az_cursed_tree | az_wreck_prow | az_naga_banner | az_tide_altar |

---

## SHEET 3: 36 Talrendis Landing pieces (the orc and blood elf salvage camp)

> Isometric three-quarter view, front toward the lower-right, 6 x 6, magenta key, the shared rules.
>
> Setting: a Horde salvage camp on an old night elf point in Azshara. The ORCS build in rough dark timber, hide and
> iron with red-brown Horde cloth. The BLOOD ELVES build in red, gold and white with arcane fittings that glow
> pale gold or blue. Here they build TOGETHER, badly: orc timber frames with blood elf gold trim bolted on, elf
> pavilions held down with orc rope and stakes. Keep both styles readable in every mixed piece.
>
> Row 1 - THE LANDING'S HEART: a mixed command hall, orc longhouse frame with a blood elf gold-and-red roof spire;
> the inn, an orc lodge with a blood elf awning and hanging gold lanterns; a gatehouse of orc timber with blood elf
> banners and a gold arch above the gate; a wind rider roost of orc timber with a blood elf crystal beacon on top; a
> quartermaster's store with crates; a dock and jetty of heavy orc timber.
> Row 2 - THE ORC SIDE: an orc salvage barracks of dark timber and hide; an orc forge under a timber roof; a war tent
> with Horde banners; a lumber stack and sawpit; a crane of orc timber for lifting stone; a watchtower of lashed logs.
> Row 3 - THE BLOOD ELF SIDE: a magister's pavilion of red and gold silk; an arcane research tent with floating glowing
> orbs; a blood elf ward-pylon, gold, crackling; a portable spire, small and slender, gold-capped; a scribes'
> canopy with a table of scrolls; a mana-cell rack of glowing gold crystals.
> Row 4 - THE SALVAGE YARD: a sorting shed with marble pieces stacked inside; a containment cage of gold bars holding
> a glowing Highborne relic; a cart rail with a stone-loaded cart; a heavy stone sledge; a pile of salvaged marble
> columns; a guarded vault-crate, iron-bound, with blood elf seals.
> Row 5 - WHERE THEY ARGUE: a half-built shared wall, orc timber on one side and elf stone on the other, meeting badly;
> a notice board with orc and Thalassian notices pinned over each other; a cook fire with an orc pot and an elf
> kettle side by side; a sparring ring with a rope; a long shared mess table under an awning; a signpost with
> Horde and blood elf arrows.
> Row 6 - THE SHORE AND THE DIG: an orc longboat pulled up on the sand; a blood elf skiff with a gold prow; a dig
> trench entrance framed in timber going down into the earth; a survey tower with a spyglass platform; a stack of
> sandbags and a breakwater; a shrine the transplants built, a cairn of stones with ribbons and small carved
> keepsakes tied to it.

### Slice order (a new `talrendis` set, to `assets/buildings/`)

| row | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 1 | tl_command_hall | tl_inn | tl_gatehouse | tl_wind_rider_roost | tl_quartermaster | tl_dock |
| 2 | tl_orc_barracks | tl_orc_forge | tl_war_tent | tl_lumber_stack | tl_stone_crane | tl_log_watchtower |
| 3 | tl_magister_pavilion | tl_research_tent | tl_ward_pylon | tl_field_spire | tl_scribes_canopy | tl_mana_cell_rack |
| 4 | tl_sorting_shed | tl_relic_cage | tl_rail_cart | tl_stone_sledge | tl_column_pile | tl_vault_crate |
| 5 | tl_split_wall | tl_notice_board | tl_shared_fire | tl_sparring_ring | tl_mess_table | tl_signpost |
| 6 | tl_orc_longboat | tl_elf_skiff | tl_dig_entrance | tl_survey_tower | tl_breakwater | tl_cairn |

---

## SHEET 4: 36 Timbermaw Hold pieces (the caldera city)

> Isometric three-quarter view, front toward the lower-right, 6 x 6, magenta key, the shared rules.
>
> Setting: TIMBERMAW HOLD, the furbolgs' home, a city built in the huge hollow of a mountain, open to the sky, with
> lodges and terraces climbing the inside walls. Timbermaw work is sturdy honey-brown timber, thatch, hide and
> carved bear totems, with green and gold beadwork, painted bear-paw marks and honey everywhere. It's older and
> grander than the Timbermaw lodge already in the game, the way a capital is grander than a camp.
>
> Row 1 - THE GREAT LODGES: the Elders' Great Lodge, a huge longhouse of honey timber with a carved bear-head gable
> and totem posts at the door; a Timbermaw inn, a warm lodge with a hanging honeycomb sign; a long communal hall
> with smoke holes; a two-storey lodge built against rock; a round den house of timber and thatch; a carvers' hall
> with half-finished totems leaning outside.
> Row 2 - THE TERRACES AND THE WALLS: a timber terrace platform with a railing, built out from the cliff; a wooden
> stair-ramp climbing the rock; a rope-and-timber bridge section; a lodge built into a cave mouth in the cliff; a
> lookout platform on stilts; a carved timber gate with two bear totems.
> Row 3 - HONEY AND HIVES: a great hive-tree, a hollow trunk with wild bee combs; tall straw skep hives in a row; a
> honey store, a hut stacked with clay honey jars; a honey press with a barrel; wax candles on a carved stand; a
> beekeepers' smoke pot.
> Row 4 - TOTEMS AND THE SACRED: a giant Timbermaw totem pole of stacked carved bears, painted; an ancestor shrine
> with offerings and antlers; a sacred spring pool rimmed with mossy stones, clean blue water; a great bonfire pit
> ringed with logs for seats; a carved standing stone with bear-paw prints; a drum circle of hide drums.
> Row 5 - THE HOLD AT WORK: a furbolg smithy with a stone forge and bear-shaped bellows; a tannery with stretched
> hides; a market stall of carved wood selling honey and herbs; a woodpile and splitting block; a herb-drying rack;
> a supply cache of baskets and bundles.
> Row 6 - THE DEEP GATE AND THE ROT: the sealed lower gate, a massive timber-and-iron door set into the caldera floor
> with heavy chains and wards; a guard post beside it with spears; a warning totem, its paint scratched and green
> stains creeping up it; a rockfall of boulders; a cracked floor stone seeping faint green fel light; a furbolg
> war-banner of green and gold.

### Slice order (a new `timbermaw_hold` set, to `assets/buildings/` for rows 1-2 and the gate, the rest to
`assets/tiles/timbermaw/props/`)

| row | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 1 | tm_elders_great_lodge | tm_inn | tm_long_hall | tm_cliff_lodge | tm_round_den | tm_carvers_hall |
| 2 | tm_cliff_terrace | tm_stair_ramp | tm_rope_bridge | tm_cave_lodge | tm_lookout | tm_totem_gate |
| 3 | tm_hive_tree | tm_skep_row | tm_honey_store | tm_honey_press | tm_candle_stand | tm_smoke_pot |
| 4 | tm_great_totem | tm_ancestor_shrine | tm_sacred_spring | tm_bonfire_pit | tm_paw_stone | tm_drum_circle |
| 5 | tm_smithy | tm_tannery | tm_market_stall | tm_woodpile | tm_herb_rack | tm_supply_cache |
| 6 | tm_deep_gate | tm_gate_guard_post | tm_warning_totem | tm_rockfall | tm_fel_crack | tm_war_banner |

---

## SHEET 5: 36 Azshara creatures

> Full body, three-quarters toward the lower-right, 6 x 6, magenta key, the shared rules. Relative scale kept: a mana
> wyrm is small, a naga myrmidon is tall, a dragon is huge.
>
> Row 1 - THE NAGA OF ZIN-AZSHARI: a naga siren, slender, four arms, teal scales and a coral crown; a naga tidehunter
> with a trident and net; a naga sea witch with a staff of pearl and glowing water; a naga royal guard in barnacled
> gold armour; a naga coilskar brute, heavy, with a stone club; a snap-jawed sea serpent hatchling.
> Row 2 - THE HIGHBORNE GHOSTS: a Highborne noble's ghost, pale blue, elegant robes, haughty; a Highborne arcanist
> ghost with floating books; a Highborne palace guard's ghost with a glaive; a Highborne handmaiden's ghost, sad,
> fading at the edges; a ghostly hound of the court; a tormented Highborne ghost twisted by madness.
> Row 3 - AZSHARA'S SATYRS AND THE LEGION: a cursed Azshara satyr, violet fur and gold Highborne jewellery still on it;
> a satyr Highborne-turned sorcerer, half elf, half satyr; a satyr hound-master; a felhound with violet crystals;
> a demon of the old Legion, an eredar-style warlock in Highborne violet; a doomguard sentinel, tall and ancient.
> Row 4 - THE BLUE DRAGONFLIGHT: a blue drake, sleek and sapphire, mid-size; a blue dragonspawn guard with a polearm;
> a blue whelp; a mana wyrm swarm-leader, larger than the existing one, glowing; an arcane construct of floating blue
> crystals; a ley-beast, a crystal-backed deer-like beast that grazes on mana.
> Row 5 - THE FEL ROT (Timbermaw's enemy below): a fel-rot furbolg, a Timbermaw gone green and twisted, moss and fel
> crystals in its fur; a fel-rot furbolg shaman with a glowing green totem; a rot-beast, a bear fused with fel fungus;
> a fel spore cloud creature, drifting; a fel-rot root horror, roots and green light; a satyr rot-tender who tends the
> corruption.
> Row 6 - THE WILD: an Azshara timber wolf with autumn-red fur; a thunder lizard of the coast; a giant shore crab,
> barnacled; a cliff hippogryph, gold and red feathers; an autumn treant with red and orange leaves; a wild Azshara
> boar with dark russet bristles.

### Slice order (`tools/slice_building_sheet.py`, a new `azshara_creatures` set, to `assets/creatures/_src/azshara/`)

| row | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 1 | az_naga_siren | az_naga_tidehunter | az_naga_sea_witch | az_naga_royal_guard | az_naga_brute | az_serpent_hatchling |
| 2 | az_ghost_noble | az_ghost_arcanist | az_ghost_guard | az_ghost_handmaiden | az_ghost_hound | az_ghost_tormented |
| 3 | az_satyr_cursed | az_satyr_sorcerer | az_satyr_houndmaster | az_felhound | az_eredar_warlock | az_doomguard_sentinel |
| 4 | az_blue_drake | az_blue_dragonspawn | az_blue_whelp | az_mana_wyrm_leader | az_arcane_construct | az_ley_beast |
| 5 | az_rot_furbolg | az_rot_shaman | az_rot_beast | az_spore_cloud | az_root_horror | az_rot_tender |
| 6 | az_timber_wolf | az_thunder_lizard | az_shore_crab | az_cliff_hippogryph | az_autumn_treant | az_russet_boar |

---

## SHEET 6: the two dungeons, interiors and bosses (36)

> Rows 1-4 are props and set pieces, isometric three-quarter view, front toward the lower-right. Rows 5-6 are bosses,
> full body, three-quarters toward the lower-right, drawn larger than ordinary creatures. 6 x 6, magenta key, the
> shared rules.
>
> Row 1 - THE FEL ROT, the halls under Timbermaw Hold: a furbolg burial niche overgrown with green fel fungus; a
> giant fel mushroom cluster glowing green; a collapsed timber support beam with rot; a fel-crystal vein bursting
> from rock; a corrupted Timbermaw totem, bent and dripping green; a pool of fel ooze in a rock basin.
> Row 2 - THE FEL ROT, deeper: a satyr ritual circle of violet runes; a root-wall of black roots threaded with green
> light; a demonic gateway half grown over with fungus; a cage of roots holding a captured furbolg; a fel-spore
> vent puffing green mist; a throne of roots and skulls.
> Row 3 - THE VAULT OF ZIN-AZSHARI, the flooded halls: a drowned Highborne colonnade, columns in water; a flooded
> grand staircase; a coral-encrusted throne of a lesser noble; a fallen chandelier of gold and crystal in the water;
> a naga war-shrine built into Highborne marble; a drowned library shelf with ruined books.
> Row 4 - THE VAULT, Azshara's own: a vault door of gold and violet with a great moon seal; a pedestal holding a
> glowing artifact under a dome of arcane light; a mirror of dark water in a gold frame; a Highborne treasure pile of
> gold, gems and relics; an arcane well, the ancient kind, cracked and leaking light; Queen Azshara's empty throne,
> huge, gold and violet, untouched by the water.
> Row 5 - THE FEL ROT'S FIVE BOSSES: Old Mossjaw, a giant fel-rot furbolg chieftain with a fungus crown; Mother
> Sporeheart, a bloated fungal horror with spore sacs; Rotwarden Kaz'thul, a satyr warden with chains and a green lamp;
> Thornblight, a root horror the size of a tree; Xavras the Gloomtender, a Highborne-turned satyr lord, regal and
> rotting, the last boss. (Row 5's sixth cell: a fel-rot furbolg elite, the bosses' bodyguard.)
> Row 6 - THE VAULT'S SIX BOSSES: Lady Ssiriss, a naga siren queen; Tidelord Vashj'ren, a huge naga warlord in coral
> armour; the Drowned Chamberlain, a Highborne ghost steward with keys and a ledger; Magistrix Elaria the Undying,
> a Highborne sorceress ghost wreathed in blue fire; the Moonguard Revenant, a drowned Highborne knight in silver
> armour; the Echo of the Queen, a towering spectral Highborne queen made of moonlight and water, the last boss.

The boss names are working names for the art. Kyle settles the dungeons' names and rosters later.

### Slice order (`tools/slice_building_sheet.py`: rows 1-4 to `assets/tiles/dungeon_props/`, rows 5-6 a new
`azshara_bosses` set to `assets/creatures/_src/azshara/`)

| row | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 1 | fr_burial_niche | fr_fel_mushrooms | fr_rotten_beam | fr_crystal_vein | fr_corrupt_totem | fr_ooze_pool |
| 2 | fr_ritual_circle | fr_root_wall | fr_fungus_gate | fr_root_cage | fr_spore_vent | fr_root_throne |
| 3 | vz_drowned_colonnade | vz_flooded_stair | vz_coral_throne | vz_fallen_chandelier | vz_naga_shrine | vz_drowned_shelf |
| 4 | vz_vault_door | vz_artifact_pedestal | vz_water_mirror | vz_treasure_pile | vz_ancient_well | vz_queens_throne |
| 5 | fr_boss_mossjaw | fr_boss_sporeheart | fr_boss_kazthul | fr_boss_thornblight | fr_boss_xavras | fr_elite_guard |
| 6 | vz_boss_ssiriss | vz_boss_vashjren | vz_boss_chamberlain | vz_boss_elaria | vz_boss_revenant | vz_boss_echo_queen |
