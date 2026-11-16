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

## 16 Nov 2026 (later): where the rep comes from, and what it buys

Kyle: "we need the rep vendors and where the rep comes from. Pale Flame from killing Scarlet Crusade and Argent Dawn
from killing Scourge".

### Where the rep comes from
- **The Order of the Pale Flame:** Scarlet kills in the open Plaguelands (5 a kill, up to Honored) and in the Scarlet
  Monastery (10 a kill and 75 a boss, up to Honored); **Crusader's Insignia**, which every Plaguelands Scarlet carries
  (rares carry three), handed to Chaplain Odile Marchand at Sorrow Hill by the stack of ten for 75, as often as you
  like; the Order's quests (the Monastery chain from Flamewarden Novak in Brill so far); Hearthglen when it's built,
  uncapped.
- **The Argent Dawn:** Scourge kills in the Plaguelands, meaning every undead and every Cult of the Damned member
  (5 a kill, rares 25, up to Honored; 39 kinds and 15 rares, read from the rosters so new ones count the day they're
  added); **Scourgestones** to Archmage Lysander Hale at Light's Hope: Minion's from the western Scourge (a stack of
  ten for 75), Invader's from the eastern (ten for 150), Corruptor's from the Scourge's rares (one for 100); the
  Dawn's quests; Scholomance and Stratholme's undead half when they're built.
- The stones and insignia are **materials**, so they drop whether or not a turn-in is open, and they stack.
- **Repeatable quests are new** (`world/quest_manager.py`): a repeatable goes back on offer when it's turned in.
  `tools/qa_repeatable_quests.py` takes each one, hands in a stack, checks the standing and takes it again; it also
  holds that no repeatable is a chain's predecessor. `audit_quests` and `qa_hunting_and_quest_drops` know about them.

### The quartermasters (`tools/build_plaguelands_rewards.py`)
Quartermaster Hollis Burke at Sorrow Hill and Quartermaster Hasana Reed at Light's Hope, the TBC way:
- **Friendly / Honored:** supplies, and patterns moved onto the shelf (only ones a vendor sold, so no trainer lost
  anything): the Order has the major-healing bracer and glove enchants and two zircon cuts; the Dawn has the
  Lifewarden's Board and the Greater Runes of Warding and of Dawn.
- **Revered:** six ilvl 67 blues each, worn at 60. Pale Flame: Sorrow Hill Bulwark Helm (plate tank), Flamewarden's
  Mantle (cloth caster), Defector's Brigandine (leather agility), Uther's Vigil Gauntlets (mail healer), Ironworker's
  Girdle (plate strength), Pale Flame Signet (ranged ring). Argent Dawn: Argent Vanguard Breastplate (plate tank),
  Lightwarden's Cord (cloth healer), Dawnstrider Leggings (leather feral tank), Chapel Ward Hauberk (mail hunter),
  Scourgebane Wristwraps (cloth caster), Argent Crusader's Sabatons (plate str/int).
- **Exalted:** three ilvl 73 epics each at 270-340g, with flavour. Pale Flame: Callahan's Rivet Maul (2H strength),
  Shield of the Walkout (tank), Staff of the Pale Flame (healer). Argent Dawn: Light's Hope Greatbow, Argent
  Avenger's Blade (agility 1H), Tome of the Last Vigil (caster). Plus two recipes each that craft ilvl 73 epics: Pale
  Flame Warplate and Mantle of the Walkout; Argent Lightguard Greaves and Dawnwatch Jerkin. Their epics have icons
  nothing else has (Kyle's pack), recorded in `data/items/crafted_icons.json`.
- **Why a separate builder:** `tools/build_faction_rewards.py` rewrites every faction's exalted recipes bare, and only
  `tools/build_crafted_gear.py` fills them back in, and that one must not be re-run. This one authors its two
  factions' recipes itself with the same `author()`.
- **One icon per epic:** quest and reputation rewards authored through the colour picker could draw an epic's icon
  (the Monastery's first quest rewards took three). `tools/reward_icons.unclash` gives them another.
- Not yet: the Revered shoulder enchants and the tabards from the design doc (no shoulder-enchant or tabard item
  type exists yet).

## 16 Nov 2026 (later): the Plaguelands quests

Kyle: "we NEED to write the quests for EPL and WPL", "Ensure quests are well written, ensure there is lore", and the
Order is "RUN by earth transplants". Built by `tools/build_plaguelands_quests.py` from one content module a map
(`tools/plaguelands_quests_south.py`, `_north.py`, `_epl_west.py`, `_epl_east.py`), one quest file a map
(`data/quests/plaguelands_<part>.json`).

| Map | Levels | Quests | Given at | Pays |
|---|---|---|---|---|
| South WPL | 51-54 | 37 | the Bulwark, Sorrow Hill | the Forsaken (Bulwark), the Order |
| North WPL | 53-56 | 30 | the Pale Watch | the Order |
| West EPL | 55-58 | 27 | Crown Guard, Light's Hope (no camp on that map) | the Argent Dawn |
| East EPL | 56-60 | 34 | Crown Guard, Light's Hope, one little ghost in Darrowshire | the Argent Dawn |

**The people.** Fifteen new quest givers, placed and synced: Deathguard Captain Ludo Vance, Surgeon Halbert Grey,
Scout Agata Wrobel and Ser Aldren Holt in the south; Sister Amalie Crane, Woodwright Jonah Lind, Oona Byrne and
Clerk Wendel Ashby at the Pale Watch; Corporal Ines Duarte, Outrider Bram Tolliver, Edda Marris, Dr. Sun Li and
Gravewarden Osric Vey at Crown Guard; Lightwarden Ysolde Carrow, Sergeant Marisol Reyes, Ranger Faelis Dawnreach, Ser
Roland Ashcombe and Huntress Kaia Lindgren at Light's Hope; and Pamela Redpath in Darrowshire.

**Who knows what.** Transplants talk about home by city (Boston, Hamburg, Kumasi, Lyon, Leicester, Bergen, the
Tatras, Lisbon, Monterrey, Kunming, Tromso, Duluth, Galway, Rosario, Winnipeg). Natives say newcomers and never
Earth; the builder fails a quest where a native giver says Earth. `tools/qa_quest_lore.py` now counts "back home" and
"from/on Earth" as the premise, which it is.

**Links.** Out to Kalimdor: Vesk's cauldron samples to Merrow Vane and Priya's letters to Dr. Lindqvist at Sun Rock,
Osric's account of Terrordale to Spiritwalker Tohana at Sun Rock (the dead rising in Mulgore), Noah's serum to Dr.
Nkechi Adeyemi and Sun Li's spores to Yuki Hashimoto at the Emerald Sanctuary, Ines's filter drawings to Tomasz Wolny
there, Marisol's notes to Marcus Oyelaran at Talonbranch. Across the Eastern Kingdoms: Rook's report to the
Undercity, Lena's letter to Novak in Brill, and the Order's letters running between Sorrow Hill, the Pale Watch and
Light's Hope (Dawnbringer writes to Rory; the Argent Dawn and the Order start talking).

**Rules held by the builder** (the Stonetalon and Monastery passes' rules): every target spawns where the quest says,
every fetch item drops, every giver and turn-in person exists, no one gives more than five quests counting every
quest file in the game, at least 80% from hubs, the voice rules, no counts beside the words the objectives use, every
explore point is a walkable tile, reward names are new to the game, and each map's rewards give all 97 specs at least
two pieces they can wear and want. Reward names are built in a fixed order from all four maps at once so they come
out the same every run.

**The Forsaken's share.** `qa_factions` wants a faction's last tiers to take at least the last 40% of its quests. The
Forsaken own more quests than anyone, so every Forsaken quest at 51+ lands after Exalted and pushes them under the
line. The Bulwark gives seventeen, sixteen of which pay the Forsaken (Venn's dispatch is handed to Rory, and the Order
pays it); everything else in the Plaguelands pays the Order or the Dawn. Any new Forsaken quest above level 40 needs
the same thought.

**Other fixes on the way.** `qa_runecrafting` now counts a reputation quartermaster's shelf as a shelf (the two rune
patterns moved to Light's Hope). Quest trinkets at 50+ became cloaks and rings, because `qa_trinket_procs` wants
every trinket from 50 up to do something. The Scarlet Monastery's quests got the same change.

### Boss phases (for Dathrohan, and raids later)
Kyle: "if you need to build the proper transformation mechanism thats fine. A lot of raids have them... having the
mechanism in place for phases is good." A creature's entry in `data/creatures/creatures.json` can carry `"phases"`:
`{"at_pct": 40, "into": "<creature>", "text": "<combat log line>"}` turns the boss into another creature (its name,
sprite, kit and full health), and `{"at_pct": 50, "kit": "<kit id>"}` keeps the creature and swaps its abilities.
The blow that crosses the line stops on it, however big it was, so nobody one-shots a phase. Loot, quest credit
and rep come off whatever it is when it dies; the old names are kept on `former_names`. Code:
`entities/monster.Monster._phase_cap` and `_enter_phase`, fed by `world/creature_manager.spawn_creature`. QA:
`tools/qa_boss_phases.py`. Nothing in the bestiary uses it yet; Dathrohan will.

## 16 Nov 2026 (later): the Plaguelands' secrets

Kyle: "make TWO skull zones somewhere in the open world for plaguelands", then "add a frontier open world on one of
these skull zones... Skull zones should be fun, frontier zones should represent the essence of our game", "Don't
make all the shapes the same. You default to blobs", and "just make sure it's from the plaguelands". Where any of
it is stays out of this log (the standing rule): counts only.

- **Two skull zones and one frontier**, each its own painted map with its own shape (no two share a topology), its
  own creatures, bosses (seven in all, every one holding something dangerous: `audit_boss_turns --only` passes),
  loot pools and one person living there with four quests, the third of them elite.
- **The frontier is entered from inside one of the skull zones**, and both skull zones are entered from the
  Plaguelands' open maps. Doors were placed by the usual secrets pass; nothing already in the game moved.
- **Two hidden sellers** (one-of-a-kind rares and two secret recipes each, never epics) and **12 new caches** across
  the four open Plaguelands maps and the hidden maps.
- **New tooling:** `scatter` in `tools/handbuilt_skull_zones.py` dresses a map's shores, rock lips and open ground
  by rule (seeded, so it comes out the same every run); a great tree can now lead to an open hidden map as well as
  a hidden level (`tools/build_secrets._placed_door_secrets`); `tools/build_hidden_content.py` keeps keys other
  builders add to a zone's registry entry (the fast exits) and has kit numbers for 55 and 60.
- **Art:** built from tiles and props on disk; the backlog sheets are `docs/plaguelands_secrets_art_prompts.md`.
