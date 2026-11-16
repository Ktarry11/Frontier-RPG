# Plaguelands art prompts (sheets 1 to 8)

For `docs/plaguelands_design.md`. Kyle, 16 Nov 2026, chose all four kinds: ground and props per map, buildings,
dungeon interiors, creatures and bosses.

**What already exists and is reused, so it isn't asked for again:** zombies, skeletons, ghouls, abominations,
banshees, plague rats, spiders and broodmothers, necromancers and cultists, three Scarlet sprites (crusader, archer,
priest), the undead farmland ground (blighted grass, dead crop fields, grave dirt, crypt floor, stagnant pond) and its
props (farmhouse ruin, scarecrow, rotted hay, gravestones), the Tirisfal Scarlet tent, banner and crates, the plague
cauldron and plague cart.

**Priority, for the first playable slice (South WPL, the Bulwark, Sorrow Hill):** sheets 1, 2, 3 and 6 first. The rest
can come while the slice is built.

Every sheet uses the same header rules as Felwood's: ONE image, 2048x2048, flat pure #FF00FF magenta background, each
sprite alone in its cell with a wide margin, no ground patch, no shadow, no text or grid lines, never magenta on the
subject, painterly semi-realistic WoW Classic style, soft dark outline, light from the top-left. Buildings and props
use the isometric three-quarter view with the front toward the lower-right; creatures face three-quarters toward the
lower-right, full body. Relative scale is kept: a rat is small, a boss is big.

---

## SHEET 1: 48 Plaguelands ground tiles (seamless squares)

> Generate ONE image, 2048x2048, an 8 columns x 6 rows grid = 48 separate SQUARE ground textures, each tile filling
> its own cell edge to edge, each one SEAMLESS (tileable on all four sides). Straight top-down view, no perspective,
> no objects, no props, no shadows from objects, no text, no labels, no grid lines. Painterly semi-realistic WoW
> Classic ground texture style, soft even light.
>
> Setting: THE PLAGUELANDS of Lordaeron, the plagued north. Palette: sick olive and mustard grass, grey-brown dead
> earth, ash grey, bruise violet and plague green as accents only. Keep every row muted; the green glow belongs only
> where a row says so.
>
> Row 1 - WESTERN PLAGUELANDS FIELDS: dry plagued grass, olive and straw; the same grass trampled with dirt showing;
> dead wheat stubble rows; cracked grey-brown farm earth; plagued grass with small violet weeds; muddy cart ruts; a
> patch of thin dead clover; grass sprinkled with ash.
> Row 2 - EASTERN PLAGUELANDS, darker and further gone: grey-green dead grass; black ash soil; grey earth with
> green-tinged puddles; withered purple-grey moss; cracked earth with faint green seepage in the cracks; bone-strewn
> dirt (tiny bone fragments only); Plaguewood forest floor of grey needles and dead leaves; Terrordale's pale dust.
> Row 3 - SCOURGE GROUND: dark violet-grey Scourge stone slabs with faint runes; Scourge stone cracked; ziggurat step
> stone in black and violet; necropolis-style dark metal grating; plague slime ground, sickly green and wet (the one
> bright tile in the row); blight-soaked black mud; corpse-pit earth, dark and churned; a Scourge rune circle
> fragment that tiles as a pattern.
> Row 4 - ROADS AND TOWNS: worn Lordaeron cobblestone road; cobblestone with weeds pushing through; packed dirt road;
> Andorhal's broken town paving with ash; a mossy old flagstone; Light's Hope chapel courtyard stone, pale and
> clean; the Bulwark's packed earth with wooden board walkways; Sorrow Hill's grey gravel path.
> Row 5 - SCARLET AND HOLY STONE: Scarlet Crusade courtyard flagstone in pale cream stone with red-brown grout;
> red-carpeted cathedral floor runner (tileable along its length); Scarlet monastery stone floor with a faint
> inlaid flame motif; Hearthglen's town cobble, cleaner and swept; Mardenholde Keep's grey castle floor; pale
> marble with gold vein (Uther's Tomb); Pale Flame keep stone, grey with soft white chalk marks; a scorched
> stone floor (burned courtyards).
> Row 6 - WATER AND SHORES: Darrowmere Lake water, cold grey-blue; the lake's shallow edge over pebbles; plagued
> water, murky green-grey; stagnant black pond water; a sandy grey lakeshore; pebble beach; the EPL coast's cold
> sea water near Tyr's Hand; marshy reeds-and-mud ground.

### Slice order (a new `plaguelands_ground` set, to `assets/tiles/plaguelands/ground/`)

| row | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| 1 | pl_wpl_grass | pl_wpl_grass_trod | pl_wheat_stubble | pl_farm_earth | pl_grass_violet | pl_cart_ruts | pl_dead_clover | pl_grass_ash |
| 2 | pl_epl_grass | pl_ash_soil | pl_green_puddles | pl_grey_moss | pl_seep_cracks | pl_bone_dirt | pl_plaguewood_floor | pl_terrordale_dust |
| 3 | pl_scourge_slab | pl_scourge_cracked | pl_ziggurat_step | pl_necro_grate | pl_plague_slime | pl_blight_mud | pl_corpse_pit | pl_rune_circle |
| 4 | pl_cobble_road | pl_cobble_weeds | pl_dirt_road | pl_andorhal_paving | pl_mossy_flag | pl_lightshope_stone | pl_bulwark_earth | pl_sorrow_gravel |
| 5 | pl_scarlet_flag | pl_cathedral_runner | pl_monastery_floor | pl_hearthglen_cobble | pl_keep_floor | pl_uther_marble | pl_paleflame_stone | pl_scorched_stone |
| 6 | pl_lake_water | pl_lake_shallow | pl_plague_water | pl_black_pond | pl_grey_shore | pl_pebble_beach | pl_cold_sea | pl_reed_marsh |

The ground follows "less is more": a map uses only a handful of these. Twelve or so per map at most.

---

## SHEET 2: 36 Plaguelands buildings (part 1: the hubs and the Scarlet towns)

> Isometric three-quarter view, every object turned the same way, front toward the lower-right. 6 x 6 grid, 36
> sprites, magenta key, the shared rules above.
>
> Row 1 - THE BULWARK (Forsaken): a fortified Forsaken gatehouse of dark timber and iron with purple banners; an
> apothecary field lab with green-glowing glass vats under a canvas roof; a wooden palisade wall segment with
> spikes; a Forsaken barracks tent of dark canvas; a bat roost tower of black timber; a plague wagon depot shed.
> Row 2 - SORROW HILL, THE ORDER OF THE PALE FLAME'S KEEP: a small grey stone keep with a squat tower and white
> banners bearing a PALE white-gold flame (a Scarlet flame with the red scraped off, plain and clean); a chapel of
> grey stone with a white flame window; a training yard pavilion with weapon racks; a stone hall with a white flame
> over the door; a gate with a white-flame banner; a stable of grey stone and dark timber.
> Row 3 - LIGHT'S HOPE AND CROWN GUARD: Light's Hope Chapel, a pale stone chapel with a tall steeple and Argent Dawn
> silver-and-blue banners; an Argent Dawn command tent of white canvas; a gryphon-free flight perch (a tall wooden
> roost with a hanging lantern); Crown Guard Tower, a broken Lordaeron watchtower partly repaired with timber; an
> outpost palisade tent; a field hospital tent with a red-cross-free white banner.
> Row 4 - HEARTHGLEN AND THE SCARLET CRUSADE: a Scarlet town house of cream stone and red tile roof; a Scarlet chapel
> with a red flame window; a Scarlet barracks with crimson banners; a gatehouse of Hearthglen with red and gold
> doors; Mardenholde Keep's main tower, tall and grim, crimson banners; a Scarlet bell tower.
> Row 5 - TYR'S HAND AND THE COAST: a Scarlet fortified town hall; a cathedral-style abbey of cream stone with a rose
> window; a Scarlet dock warehouse; a stone harbour watchtower with a beacon; a walled courtyard gate; a Scarlet
> stable.
> Row 6 - THE GREAT DOORS (dungeon fronts): the Scarlet Monastery's front, a huge cathedral facade with doors; the
> gates of Stratholme, a great stone city gate with a broken portcullis; Scholomance on Caer Darrow, a dark keep
> entrance with a stone stair; Hearthglen's keep gate, crimson and gold with a great iron door; a Scourge
> ziggurat, a stepped black-and-violet pyramid with a glowing top; a necropolis-style Scourge spire.

### Slice order (a new `plaguelands_buildings` set, to `assets/buildings/`)

| row | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 1 | pl_bulwark_gate | pl_bulwark_apothecary | pl_bulwark_palisade | pl_bulwark_barracks | pl_bulwark_bat_roost | pl_bulwark_wagon_shed |
| 2 | pf_keep | pf_chapel | pf_training_yard | pf_hall | pf_gate | pf_stable |
| 3 | lh_chapel | lh_command_tent | lh_flight_perch | crown_guard_tower | cg_palisade_tent | lh_field_hospital |
| 4 | sc_town_house | sc_chapel | sc_barracks | hearthglen_gatehouse | mardenholde_tower | sc_bell_tower |
| 5 | tyr_town_hall | tyr_abbey | tyr_dock_warehouse | tyr_harbour_tower | sc_courtyard_gate | sc_stable |
| 6 | sm_facade | strat_gates | scholo_entrance | hearthglen_keep_gate | scourge_ziggurat | scourge_spire |

---

## SHEET 3: 36 Plaguelands props (open world)

> Isometric three-quarter view, 6 x 6, magenta key, the shared rules.
>
> Row 1 - THE CAULDRONS: a giant Scourge plague cauldron of black iron bubbling bright green; the same cauldron
> smashed and dead; a Scourge cauldron with a cultist work platform and a ladder; a pile of corpse sacks; a Scourge
> meat wagon (a spiked cart with a hook); a plague cauldron runoff pool rim, green.
> Row 2 - FARMS GONE TO PLAGUE: a burned Lordaeron farmhouse half collapsed; a plagued barn with sagging roof; a
> rotten pumpkin patch; a broken windmill of Lordaeron style; a split-rail fence segment, broken; a plagued wheat
> sheaf stook.
> Row 3 - ANDORHAL AND DARROWSHIRE RUINS: a ruined town house wall with a window; a broken clock tower stump; a
> collapsed stone arch; a burned market stall; a ghostly little doll lying on a stone (Darrowshire's doll, small);
> a toppled Lordaeron statue of a knight.
> Row 4 - SCOURGE THINGS: a Scourge banner of black and violet with a skull; a bone spike barricade; a necrotic
> obelisk humming violet; a ghoul pit with bones; an abomination's butcher block; a skull pile.
> Row 5 - SCARLET AND PALE FLAME FIELD KIT: a Scarlet war camp tent of crimson canvas with gold trim; a Scarlet
> pyre (a stake on a pile of wood, unlit, unoccupied); a Scarlet supply cart; a Pale Flame banner, white with a pale
> flame on grey; a Pale Flame field tent of grey canvas; a weapon rack with plain steel swords and a round shield.
> Row 6 - TREES AND LAND: a dead Plaguewood tree hung with old webbing; a twisted grey dead oak; a blighted pine with
> violet needles; a Quel'Lithien-style elven lodge lantern post; a Zul'Mashar troll ruin block with a carved face;
> a cluster of grey-violet plague mushrooms.

### Slice order (a new `plaguelands_props` set, to `assets/tiles/plaguelands/props/`)

| row | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 1 | pl_cauldron_live | pl_cauldron_dead | pl_cauldron_platform | pl_corpse_sacks | pl_meat_wagon | pl_runoff_pool |
| 2 | pl_farmhouse_burned | pl_barn_plagued | pl_pumpkin_rot | pl_windmill_broken | pl_fence_broken | pl_wheat_stook |
| 3 | pl_ruin_wall | pl_clock_stump | pl_ruin_arch | pl_stall_burned | pl_darrowshire_doll | pl_knight_statue |
| 4 | pl_scourge_banner | pl_bone_barricade | pl_necro_obelisk | pl_ghoul_pit | pl_butcher_block | pl_skull_pile |
| 5 | sc_war_tent | sc_pyre | sc_supply_cart | pf_banner | pf_field_tent | pf_weapon_rack |
| 6 | pl_plaguewood_tree | pl_dead_oak | pl_blight_pine | ql_lantern_post | zm_ruin_block | pl_plague_mushrooms |

---

## SHEET 4: 36 dungeon interior props (Monastery, Scholomance, Stratholme, Hearthglen)

> Isometric three-quarter view, 6 x 6, magenta key, the shared rules.
>
> Row 1 - THE SCARLET MONASTERY: a cathedral pew of dark wood; a tall candelabra; a library bookshelf with red
> spines; a reading lectern with an open book; an armory weapon rack of polished Scarlet steel; a Scarlet altar
> with a red-flame brazier.
> Row 2 - MORE MONASTERY: a crypt sarcophagus with a carved knight; an iron maiden-free interrogation chair of wood
> and leather straps (no blood); a training dummy in red tabard; a stained-glass window fragment set in a stone
> frame; a marble statue of a robed saint; a stack of Scarlet supply crates.
> Row 3 - SCHOLOMANCE: an alchemy table with skulls and green bottles; a classroom desk with old books; a bone
> golem assembly table; a ritual circle stone with violet runes; a wall of jars holding pale specimens (vague, not
> gory); a dark iron cage.
> Row 4 - STRATHOLME: a burned Stratholme market stall; a broken fountain; a ziggurat brazier of violet fire; a
> pile of rubble and roof tiles; a cart of plague grain; a crumbling city wall segment.
> Row 5 - HEARTHGLEN AND MARDENHOLDE: a Scarlet throne of red velvet and gold; a war table with a map; a hanging
> crimson banner; a chapel organ of dark wood and brass pipes; a choir stall; a kennel of iron bars.
> Row 6 - LOOT AND LIGHT: a Scarlet treasure chest; a Scourge bone chest; a gilded reliquary; a wall torch; a hanging
> iron chandelier with candles; a broken holy symbol of the Silver Hand.

### Slice order (a new `plaguelands_dungeon_props` set, to `assets/tiles/plaguelands/dungeon_props/`)

| row | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 1 | sm_pew | sm_candelabra | sm_bookshelf | sm_lectern | sm_weapon_rack | sm_altar |
| 2 | sm_sarcophagus | sm_interrogation_chair | sm_training_dummy | sm_glass_window | sm_saint_statue | sm_supply_crates |
| 3 | scholo_alchemy_table | scholo_desk | scholo_golem_table | scholo_ritual_stone | scholo_specimen_jars | scholo_iron_cage |
| 4 | strat_stall_burned | strat_fountain | strat_ziggurat_brazier | strat_rubble | strat_grain_cart | strat_wall |
| 5 | hg_throne | hg_war_table | hg_banner | hg_organ | hg_choir_stall | hg_kennel |
| 6 | sc_treasure_chest | scourge_bone_chest | hg_reliquary | dg_wall_torch | dg_chandelier | silver_hand_symbol |

---

## SHEET 5: 36 dungeon floors and walls (seamless squares)

> ONE image, 2048x2048, 6 x 6 grid = 36 SQUARE SEAMLESS textures, straight top-down, no objects, the tile rules from
> sheet 1.
>
> Row 1 - SCARLET MONASTERY: graveyard crypt stone; library parquet of dark wood; armory stone with iron studs;
> cathedral nave marble in cream and red; a red carpet field; the monastery's outer wall stone.
> Row 2 - SCHOLOMANCE: dark violet-grey classroom flagstone; bone-white ritual floor with runes; damp crypt stone with
> green moss; black marble of the Barov halls; the keep's outer wall stone; violet-lit ossuary floor.
> Row 3 - STRATHOLME LIVING SIDE: burned cobble streets; Scarlet Bastion courtyard; market square stone; charred
> wood floor; grey city wall stone; ash-covered pavement.
> Row 4 - STRATHOLME UNDEAD SIDE: Scourge-paved street of black and violet; ziggurat interior stone; slaughterhouse
> floor (dark, grim, not gory); a necropolis grate; frost-rimed black stone; the Baron's hall floor.
> Row 5 - HEARTHGLEN TOWN: clean cream cobble; tiled town square; a garden path of pale gravel; chapel floor;
> barracks timber floor; red-gold mosaic.
> Row 6 - MARDENHOLDE KEEP: grey keep flagstone; throne room carpet field; keep wall stone; kennel straw floor;
> library wood floor; a burned keep floor for the last fight.

### Slice order (a new `plaguelands_dungeon_ground` set, to `assets/tiles/plaguelands/dungeon_ground/`)

| row | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 1 | sm_crypt | sm_parquet | sm_armory | sm_nave | sm_carpet | sm_wall |
| 2 | scholo_flag | scholo_ritual | scholo_crypt | scholo_marble | scholo_wall | scholo_ossuary |
| 3 | strat_burned_cobble | strat_bastion | strat_market | strat_charred_wood | strat_wall | strat_ash |
| 4 | strat_scourge_street | strat_ziggurat | strat_slaughter | strat_grate | strat_frost | strat_baron_hall |
| 5 | hg_cobble | hg_square | hg_gravel | hg_chapel | hg_barracks | hg_mosaic |
| 6 | mh_flag | mh_throne_carpet | mh_wall | mh_kennel | mh_library | mh_burned |

---

## SHEET 6: 36 creatures (the Scourge and the living of the Plaguelands)

> Creatures, 6 x 6, magenta key, the shared rules. Setting: THE PLAGUELANDS. Palette: grey-green rot, bone, black
> and violet Scourge gear, plague green as the glow.
>
> Row 1 - THE SCOURGE'S BIG THINGS: a plague eruptor (bloated walking corpse with green boils); a flesh golem
> stitched from many bodies; a stone gargoyle with bat wings; a crypt fiend (a huge undead spider-man); a death
> knight on foot in black plate with a runeblade; a skeletal warhorse.
> Row 2 - THE SCOURGE'S SMALL THINGS: a plaguebat (big, leathery, sickly); a plaguehound with exposed ribs; a
> carrion grub; a frenzied ghoul crawling low; a skeletal mage with a cracked staff; a wailing spirit (pale,
> drifting, translucent blue-white).
> Row 3 - THE CULT OF THE DAMNED: a cult neophyte in grey robes; a cult plaguebringer carrying a green flask; a
> necrolyte with a bone wand; a cult cauldron tender with a long stirring paddle; a dark caster with a floating
> book; a cult lieutenant in black-violet robes and a bone crown.
> Row 4 - THE PLAGUED WILD: a diseased black bear; a plagued wolf; a carrion vulture; a blighted stag with dead
> antlers; a mutated plague slime; a Plaguewood giant spider (huge, grey, webbed).
> Row 5 - THE LIVING: a Forsaken apothecary in a leather apron and goggles; a Forsaken deathguard in heavy armour;
> an Argent Dawn crusader in silver and blue; an Argent Dawn priestess in white; a Darrowshire ghost villager
> (pale, sad); a Zul'Mashar troll warrior with a bone necklace.
> Row 6 - FIELD BOSSES AND RARES, large and distinct: a giant abomination farmer with a scythe (South WPL's field
> boss); a lich magistrate in tattered robes over Andorhal (North WPL); a Plaguewood brood queen spider (West EPL); a
> bone colossus (East EPL); a plagued horse rider rare; a cult arch-necromancer rare.

### Slice order (a new `plaguelands_creatures` set, to `assets/creatures/_src/plaguelands/`)

| row | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 1 | pl_plague_eruptor | pl_flesh_golem | pl_gargoyle | pl_crypt_fiend | pl_death_knight | pl_skeletal_warhorse |
| 2 | pl_plaguebat | pl_plaguehound | pl_carrion_grub | pl_frenzied_ghoul | pl_skeletal_mage | pl_wailing_spirit |
| 3 | pl_cult_neophyte | pl_cult_plaguebringer | pl_necrolyte | pl_cauldron_tender | pl_dark_caster | pl_cult_lieutenant |
| 4 | pl_diseased_bear | pl_plagued_wolf | pl_carrion_vulture | pl_blighted_stag | pl_plague_slime | pl_plaguewood_spider |
| 5 | pl_forsaken_apothecary | pl_deathguard | ad_crusader | ad_priestess | pl_darrowshire_ghost | zm_troll_warrior |
| 6 | pl_boss_abomination_farmer | pl_boss_lich_magistrate | pl_boss_brood_queen | pl_boss_bone_colossus | pl_rare_plague_rider | pl_rare_arch_necromancer |

---

## SHEET 7: 36 creatures (the Scarlet Crusade and the Order of the Pale Flame)

> Creatures, 6 x 6, magenta key, the shared rules. The Scarlet Crusade: cream, crimson and gold, polished steel, red
> flame tabards. The Order of the Pale Flame: grey steel, white and pale gold, a plain pale flame where the Scarlets
> wear a red one. Several Pale Flame members and some Scarlets are EARTH TRANSPLANTS: give those faces modern human
> variety (different ethnicities, short modern haircuts, a beard trim, a scar), wearing the same fantasy armour.
> No Earth objects or clothing.
>
> Row 1 - SCARLET MONASTERY RANKS: a Scarlet monk (hand wraps, no weapon); a Scarlet zealot with a mace; a Scarlet
> adept (robed caster); a Scarlet chaplain with a holy book; a Scarlet myrmidon with a two-handed sword; a Scarlet
> centurion with sword and tower shield.
> Row 2 - HEARTHGLEN RANKS: a Scarlet knight in full plate; a Scarlet inquisitor in red robes and a tall hat; a
> Scarlet judicator with a warhammer; a Scarlet arcanist with a red staff; a Scarlet war hound (big mastiff in red
> barding); a mounted Scarlet cavalier on a white warhorse.
> Row 3 - TRANSPLANT SCARLETS (Earth-born zealots): a transplant crusader, broad, shaved head, wild-eyed; a transplant
> sniper with a crossbow; a transplant drill sergeant shouting; a transplant inquisitor, cold and neat; a transplant
> champion, a huge boxer-built man in crimson plate; a transplant cleric, young, fervent.
> Row 4 - THE ORDER OF THE PALE FLAME: Flamekeeper Rory Callahan (a grey-bearded man in his fifties, scarred, tired
> eyes, grey plate with a pale flame tabard, a big two-handed sword); Sione Tuilagi (a big Samoan man, shield and
> one-handed hammer, grey plate); Mateus Correia (a lean Portuguese man in grey robes over mail, a healer's staff,
> haunted look); Hana Kobayashi (a Japanese woman with a tall longbow, grey leather); a Pale Flame sentry with
> a spear; a Pale Flame quartermaster with a ledger.
> Row 5 - HEARTHGLEN BOSSES (part 1): a gatewarden with two leashed war hounds (one sprite); a quartermaster boss
> beside a barrel of black powder; twin pyre-sister inquisitors back to back (one native, one transplant, ONE
> sprite); a transplant drillmaster with a whistle and a halberd; a high inquisitor holding a burning book;
> a kennelmaster with a whip.
> Row 6 - HEARTHGLEN BOSSES (part 2) and the last fight: an arcanist in a crimson tower robe with a floating orb; Lady
> Elsbeth Marden, a noblewoman in crimson and gold with a rapier; the Crimson Choir (three robed singers, ONE
> sprite); Champion Dmitri Volkov, a transplant boxer in heavy crimson plate with gauntlets; Grand Crusader Victor
> Hale, a tall transplant commander in ornate crimson-gold plate with a flaming greatsword (largest on the sheet);
> his Scarlet charger, a barded white warhorse.

### Slice order (a new `plaguelands_scarlet` set, to `assets/creatures/_src/plaguelands/`)

| row | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 1 | sc_monk | sc_zealot | sc_adept | sc_chaplain | sc_myrmidon | sc_centurion |
| 2 | sc_knight | sc_inquisitor | sc_judicator | sc_arcanist | sc_war_hound | sc_cavalier |
| 3 | sc_tp_crusader | sc_tp_sniper | sc_tp_drill_sergeant | sc_tp_inquisitor | sc_tp_champion | sc_tp_cleric |
| 4 | pf_rory_callahan | pf_sione_tuilagi | pf_mateus_correia | pf_hana_kobayashi | pf_sentry | pf_quartermaster |
| 5 | hg_boss_gatewarden | hg_boss_quartermaster | hg_boss_pyre_sisters | hg_boss_drillmaster | hg_boss_high_inquisitor | hg_boss_kennelmaster |
| 6 | hg_boss_arcanist | hg_boss_lady_marden | hg_boss_crimson_choir | hg_boss_volkov | hg_boss_victor_hale | hg_scarlet_charger |

The three recruitable Pale Flame fighters also need portraits, done the way the other recruits' were.

---

## SHEET 8: 36 creatures (the classic dungeon bosses)

> Creatures, 6 x 6, magenta key, the shared rules. Bosses are large and distinct from each other.
>
> Row 1 - SCARLET MONASTERY: an interrogator with a branding iron; a bloodmage in red with a floating blood orb; a
> houndmaster with a crossbow; an arcanist in red with a glowing staff; a huge Scarlet champion with an axe and red
> plate; a Scarlet commander in gold-trimmed plate with a hammer.
> Row 2 - MORE MONASTERY AND SCHOLOMANCE: a white-haired Scarlet high inquisitor woman in white and red with a staff;
> a giant bat-winged gargoyle boss (the bat-thing of Scholomance's gate); a frail noblewoman ghost with a fan; a
> huge bone construct with a hook and chains; an undead frost lich with ice armour; a plague-doctor-like
> alchemist.
> Row 3 - SCHOLOMANCE: a zombie librarian with books; a cold female instructor with a whip; a noble lady in
> a black gown; a noble lord in black and silver; the headmaster necromancer in dark violet robes with a bone
> staff (big); a ghostly Barov family servant.
> Row 4 - STRATHOLME LIVING SIDE: a ghoul-like boss in rags (small and fast); a cannon master next to a cannon; an
> archivist with a torch and a burning book; a Scarlet grand crusader who is secretly a dreadlord (show him in
> red and gold with dark horns faintly showing); a dreadlord with bat wings; a crusade magistrate.
> Row 5 - STRATHOLME UNDEAD SIDE: a nerubian crypt lord boss; a banshee baroness; a lich in black with a skull
> staff; a huge flesh-golem Ramstein-type with a meat hook; a death knight baron in black plate with a runeblade; a
> skeletal deathcharger horse (the rare mount, dark and fiery).
> Row 6 - EXTRA ROOM: a cult necromancer boss; a ghostly Silver Hand paladin; a plague gate guardian; a scourge
> eye-construct; a cultist chorus leader; an abomination butcher.

### Slice order (a new `plaguelands_dungeon_bosses` set, to `assets/creatures/_src/plaguelands/`)

| row | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 1 | sm_boss_interrogator | sm_boss_bloodmage | sm_boss_houndmaster | sm_boss_arcanist | sm_boss_champion | sm_boss_commander |
| 2 | sm_boss_high_inquisitor | scholo_boss_gargoyle | scholo_boss_ghost_lady | scholo_boss_bone_construct | scholo_boss_frost_lich | scholo_boss_alchemist |
| 3 | scholo_boss_librarian | scholo_boss_instructor | scholo_boss_noble_lady | scholo_boss_noble_lord | scholo_boss_headmaster | scholo_ghost_servant |
| 4 | strat_boss_ghoul_runt | strat_boss_cannon_master | strat_boss_archivist | strat_boss_grand_crusader | strat_boss_dreadlord | strat_boss_magistrate |
| 5 | strat_boss_crypt_lord | strat_boss_baroness | strat_boss_lich | strat_boss_flesh_golem | strat_boss_baron | strat_deathcharger |
| 6 | pl_boss_cult_necromancer | pl_silver_hand_ghost | pl_boss_gate_guardian | pl_boss_eye_construct | pl_boss_chorus_leader | pl_boss_abom_butcher |

---

## Icons (later)

The Pale Flame and Argent Dawn quartermaster gear, the Scourgestones, the Scarlet insignia, the Commission trinket,
the two chargers and the set pieces will need icons. Those prompts come once the item lists are final, so they
match what's actually in the game.
