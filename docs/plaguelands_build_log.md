# The Plaguelands: build log

Design: `docs/plaguelands_design.md`. Art prompts: `docs/plaguelands_art_prompts.md`.

## 16 Nov 2026: the four maps, wired and playable (placeholder art)

Kyle, 07:54: "Start building everything you can with the layouts. I will get art to you in about 30min."

### Maps (all four built, walkable, joined up)

| Map | Size | Band | Builder | What's on it |
|---|---|---|---|---|
| Western Plaguelands South | 180x160 | 51-54 | `tools/handbuilt_wpl_south.py` | the Bulwark, Felstone Field, Dalson's Tears, the Writhing Haunt, Andorhal, Sorrow Hill and Uther's Tomb, Darrowmere Lake and Caer Darrow |
| Western Plaguelands North | 180x140 | 53-56 | `tools/handbuilt_wpl_north.py` | the Pale Watch, Northridge Lumber Camp, Gahrron's Withering, Hearthglen Fields, the Thondroril |
| Eastern Plaguelands West | 170x150 | 55-58 | `tools/handbuilt_epl_west.py` | Terrordale, the Marris Stead, Plaguewood, Stratholme's gates, the Fungal Vale, Corin's Crossing |
| Eastern Plaguelands East | 170x150 | 56-60 | `tools/handbuilt_epl_east.py` | Crown Guard Camp, Darrowshire, Blackwood Lake, Light's Hope Chapel, Tyr's Hand, Quel'Lithien Lodge, Zul'Mashar, the Pestilent Scar |

- **Geography follows WoW's, read north-up** ("familiar-ish"): the Bulwark on the Tirisfal border, the four cauldron
  farms, Andorhal in the south-west, Sorrow Hill and Darrowmere in the south, Hearthglen at the top, the Thondroril
  between the two Plaguelands, Stratholme in EPL's north-west, Light's Hope in the east and Tyr's Hand on the coast.
- **Andorhal sits in the south map** (WoW has it south-west), so the design doc's map split was adjusted: Felstone,
  Dalson's, the Writhing Haunt and Andorhal are south; Gahrron's is north.
- **The road:** Eastern Tirisfal's Bulwark road now runs to its east edge (re-baked) and into South WPL's west gate;
  South's north gate to North; North's Thondroril crossing to EPL West; EPL West's east gate to EPL East. All in
  `world/portal_manager.py`, both sides of every door.
- **Doors cut and waiting** (`LATER_PORTALS`, ground already open so nothing needs re-baking): the Alterac foothills
  road and the Undercity sewer door (South), Scholomance on Caer Darrow (South), Hearthglen (North), Stratholme (West).

### Hubs (inn and flight master each)
- **The Bulwark** (Forsaken): High Executor Marla Venn, Apothecary Dorian Vesk (the cauldron quests), an inn, bats,
  the quartermaster, and Deathstalker Ilsa Rook (the Undercity door chain).
- **Sorrow Hill** (the Order of the Pale Flame): Flamekeeper Rory Callahan, the quartermaster, an inn, the hawk roost,
  the drillmaster, and the chaplain at Uther's Tomb.
- **Crown Guard Camp:** Captain Joss Varden, an inn, bats.
- **Light's Hope Chapel** (the Argent Dawn): Commander Eligor Dawnbringer, the Scourgestone archmage, the quartermaster,
  an inn, bats.
- **The Pale Watch** (North WPL, not a hub): three of the Order watching Hearthglen's road.
- Six new flight points: the Bulwark, Sorrow Hill, Crown Guard, Light's Hope (four nodes) on the Eastern Kingdoms map.

### Creatures
- 95 new creatures across the four maps (open-world wildlife and Scourge, the Cult at the cauldrons, the Scarlet
  Crusade at Northridge, Hearthglen Fields and Tyr's Hand, the Mossflayer trolls at Zul'Mashar), each with a kit.
- **One rare per subzone, 22 in all**, with hand-named loot pools at level + 3 (`data/loot/plaguelands_rare_loot.json`,
  `data/loot/plaguelands_east_rare_loot.json`). The Bone Colossus (60) is the East's field boss.
- Placeholder sprites from the existing undead, cultist, Scarlet, troll and beast art (`creature_sprites.py`) until
  Kyle's creature sheets land.
- **Names never repeat.** Two collisions were caught and fixed: "Carrion Vulture" (the Valley of Trials' level 2-5
  vulture, briefly overwritten) and the "scarlet_inquisitor" kit (Tirisfal's Scarlet Preacher uses it). Both builders
  now refuse a name or kit slug that already belongs to someone else.

### Factions
- **The Order of the Pale Flame** and **the Argent Dawn** are in `data/factions/factions.json`
  (`tools/build_plaguelands_factions.py`), with leaders, lore and quest rep for the Plaguelands.
- **Capped kill rep is new** (`world/faction_manager.py`): a kill can be `[amount, cap tier]` and stops paying at that
  tier, and a dungeon can carry a cap in `dungeon_rep.caps`. Open-world Scarlets pay the Pale Flame 5 a kill up to
  Honored (Kyle: "Little until honored"); the Monastery's cap goes in when its wings exist.
- The Argent Dawn's kill rep waits on the Commission trinket.
- Reward shelves come when the items are authored.

### Gathering and the pure 60 rule
- Node pools and fishing for all four maps, inside the pre-60 line (Thorium, Truesilver, Dreamfoil, Golden Sansam,
  Icecap, Black Lotus in the East, Starleaf and Stormoak). `qa_no_postgame_below_pure_60` covers them.

### Ground paint
- `tools/bake_ashenvale.py` paints the four maps from Kyle's ground sheet (`_plague_sheet`, below). The first pass
  used the undead farmland and haunted forest textures as stand-ins.

## 16 Nov 2026 (later): Kyle's first three sheets

Kyle sent the ground, buildings and props sheets at 09:21. All three are filed, sliced and in the maps.

### Slicing
- `tools/tile_sheets/plaguelands_ground.png` → 48 tiles in `assets/tiles/plaguelands/ground/` (slice set `plaguelands`
  in `tools/slice_tile_sheet.py`).
- `tools/building_sheets/plaguelands_buildings.png` → 36 buildings in `assets/buildings/` (`plaguelands_buildings`):
  the Bulwark, the Pale Flame's keep, Light's Hope, Crown Guard, the Scarlet town set, Tyr's Hand, and the dungeon
  fronts (the Monastery, Stratholme, Scholomance, Hearthglen's keep gate) plus the Scourge ziggurat and spire.
- `tools/building_sheets/plaguelands_props.png` → 36 props in `assets/tiles/plaguelands/props/` (`plaguelands_props`):
  cauldrons, farm ruin, Andorhal's clock stump, the Darrowshire doll, Uther's statue, Scourge and Scarlet camp pieces,
  the Order's banner, tent and rack, and three trees. `pl_fence_broken` came out as two fence lengths in one sprite,
  which is right.

### Ground
- Two sheets now: `WPL_SHEET` (golden sick farmland: `pl_wpl_grass_trod` as the base, `pl_wpl_grass`, dead clover,
  violet blight, wheat stubble in the farm patches, green puddles at the cauldrons, ash soil where things burned)
  and `EPL_SHEET` (greyer and wetter: `pl_epl_grass`, grey moss, seep cracks, bone dirt, Terrordale dust, plague
  slime, the Plaguewood floor under the woods).
- The "root" material wins about two fifths of the open ground in these layouts (it rings every wood), so it carries
  the main grass. The first bake had cracked farm earth there and the whole map read as brown dirt.
- Cliffs stay the Valley of Trials' rock, tinted grey and lifted (the sheet has no cliff face).
- GRADE is back near neutral, (1.0, 1.05) in the West and (0.95, 1.05) in the East, because Kyle's tiles are lit
  already. The stand-ins needed (0.85, 1.65).

### Buildings and props (what replaced the stand-ins)
- **The Bulwark:** `pl_bulwark_gate`, palisade, bat roost, barracks tent, apothecary, wagon shed, a live cauldron.
- **The farms** (Felstone, Dalson's, the Writhing Haunt, Gahrron's): plagued barns, burned farmhouses, cauldron
  platforms and runoff pools, the broken windmill at Dalson's, wheat stooks, rotten pumpkins, broken fences.
- **Andorhal:** burned houses, ruin walls, the clock stump, a ruin arch, a burned stall, a meat wagon, a Scourge banner.
- **Sorrow Hill:** `pf_keep`, `pf_chapel`, `pf_training_yard`, `pf_hall` (the inn), `pf_stable`, the Order's banners
  and rack, and `pl_knight_statue` as Uther's Tomb.
- **Caer Darrow:** `scholo_entrance`, placed so its door sits on the Scholomance door tile.
- **North WPL:** the Pale Watch in the Order's tents and banner; Northridge with `sc_barracks`, war tents and supply
  carts; Hearthglen Fields with war tents and two pyres and `mardenholde_tower` on the shoulder; `hearthglen_gatehouse`
  on the dungeon door.
- **EPL West:** `strat_gates` on the Stratholme door; a `scourge_spire` in the Plaguewood; a `scourge_ziggurat` over
  Corin's Crossing; mushrooms in the Fungal Vale; Terrordale and the Marris Stead in farm ruin.
- **EPL East:** `crown_guard_tower` and `cg_palisade_tent`; `lh_chapel`, `lh_command_tent`, `lh_field_hospital`,
  `lh_flight_perch`; Tyr's Hand as a full Scarlet town (`sc_courtyard_gate`, `tyr_town_hall`, `tyr_abbey`,
  `tyr_harbour_tower`, `tyr_dock_warehouse`, `sc_bell_tower`, `sc_town_house`, `sc_stable`); Darrowshire with the doll;
  lantern posts at Quel'Lithien; `zm_ruin_block` at Zul'Mashar; an obelisk and a dead cauldron in the Pestilent Scar.
- **Trees:** Kyle's dead oak leads in the West, his purple blight pine shows up only inside woods; the Plaguewood tree
  fills EPL West's woods.
- Every door tile (live and later) was checked walkable after dressing. The first placement of the Caer Darrow front
  covered the Scholomance door, and it was moved.
- Not used yet: `sm_facade` (Tirisfal's Monastery door), `hearthglen_keep_gate` (inside Hearthglen), `sc_chapel`,
  `pf_gate`, and a few props kept for quest set pieces.

### What the full QA run caught (all fixed)
- **Mailboxes:** the four new inns had none (`qa_auction_house`). `tools/place_market_npcs.py` placed them; the
  Plaguelands' human hubs use the Forsaken box's grey iron (`INN_CULTURE`) until there's a human mailbox.
- **Factions:** the Eastern Plaguelands were claimed by both new factions, and Tirisfal's Scarlets already paid the
  Forsaken (`qa_factions`: a zone's quests and a creature's kills pay one faction). The West's quests now pay the
  Pale Flame and the East's the Argent Dawn; the Order's chains that run east go in its `also` list. Tirisfal's
  Scarlets stay the Forsaken's, so the Order's open-world kill rep starts at the Plaguelands' border.
- **Node levels:** Mithril was too low for both West maps and Stormoak too high for South WPL (`qa_node_levels`:
  a node of skill S fits a zone lo-hi when (lo-15)x5 <= S <= hix5). Thorium and Starleaf took their weight.
- **NPCs under buildings:** the Bulwark gate and the Pale Flame hall were drawn over two NPCs; both moved.
- **Eastern Tirisfal:** the Bulwark road's extension was rerouted a little north at its east end and the zone
  re-baked.
- **Loot curve:** the rares are on the item curve (see `docs/item_curve_fix_2026_11_16.md`).

### Still to do
- Kyle's creature sheets (Scarlets and the Pale Flame, then the Scourge), then swap the placeholder sprites.
- Quests (about 40 a map), the cauldron chains, the Pale Flame and Argent Dawn chains, the Undercity door chain.
- Faction reward shelves, the Commission, Scourgestones.
- The dungeons: Hearthglen (with Kyle's hidden chain), Scholomance, both halves of Stratholme, the Monastery's wings.
- The Alterac foothills road map.
