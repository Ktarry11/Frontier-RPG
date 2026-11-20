# Feralas: what was built (19-20 Nov 2026)

The vision and Kyle's answers are `docs/feralas_brief.md`, the quest plan `docs/feralas_quest_plan.md`, the art
`docs/feralas_art_prompts.md`. Kyle, 19 Nov 2026: "Let's build feralas first", then "Build without art for now".

## Built on art already in the game

Nothing here waits on the Feralas sheets. When they come, slicing them swaps everything over:
- **Ground:** `FERALAS_SHEET` and `FERALAS_COAST_SHEET` in `tools/bake_ashenvale.py` (Ashenvale's deep green floor,
  grass and ferns, Stonetalon's moss, canopy floor and granite; the Fog Groves are Stonetalon's redwood duff and
  sorrel). Point the stems at `assets/tiles/feralas/ground/` and re-bake.
- **Trees and props:** Ashenvale's canopy trees and Stonetalon's sequoias and redwoods; Grimtotem camp pieces stand in
  for the gnolls; the cave entrance library for every door.
- **Buildings:** Mojache is Camp Taurajo's, Moonglade's tauren and the Aspen camp's pieces; Feathermoon is Felwood's
  Sentinel hall and towers with Moonglade's night elf houses, inn and moonwell.
- **Creatures:** `PLACEHOLDER` in `tools/build_feralas_openworld.py` and the placeholder column in
  `tools/build_zukkash_hive_content.py`. Each creature names its own fe_* sprite from sheet 7; until that file is on
  disk it draws as the nearest existing one. Re-run both scripts after slicing.

## The maps

| Map | Levels | Builder | Size |
|---|---|---|---|
| The High Wilderness (the east arm) | 44-46 | `tools/handbuilt_feralas_high_wilderness.py` | 220x160 |
| The Forgotten Coast | 46-48 | `tools/handbuilt_feralas_forgotten_coast.py` | 200x200 |
| The Twin Colossals | 47-49 | `tools/handbuilt_feralas_twin_colossals.py` | 180x220 |
| Camp Mojache (town) | 44-46 | `tools/handbuilt_camp_mojache.py` | 124x96 |
| Feathermoon Stronghold (town, island) | 46-48 | `tools/handbuilt_feathermoon_stronghold.py` | 124x104 |
| The Zukk'ash Hive (cave) | 47-49 | `tools/handbuilt_zukkash_hive.py` | 104x124 |

**The links:** the Aspen Wilderness's south-west bench (4,154) to the foot of the High Wilderness's descent; the
High Wilderness west to the Forgotten Coast; the Forgotten Coast north to the Twin Colossals; Camp Mojache behind its
totem gate; Feathermoon by boat from the landing's pier; the Zukk'ash Hive's mouth in the Hive Fields, and the tunnel at
its back out into the Dry Deep's Brine Seep (3,37). Dire Maul's gate stands with its door shut (the dungeon is 55-60,
later).

**The cave's name:** "The Writhing Deep" is already the Plaguelands' spider cave, so Feralas's hive is the Zukk'ash
Hive (the classic hive's name) until Kyle picks another.

## The people (`tools/build_feralas_towns.py`)

**Camp Mojache:** Chieftain Ahanu Swiftstrider, Hadoken Swiftstrider, Elder Nayeli Cloudhoof, Brann Tallgrass, Krueg
Skullsplitter (Orgrimmar's), Orwin Gizzmick (goblin), Brave Takoda Mistrunner, Innkeeper Greul, Wind Rider Master Shyn
(the east arm's flight path), Trainer Ishana Brightmane, a hide pair, an herb pair, a smith, a provisioner, a mailbox.

**Feathermoon Stronghold:** Shandris Feathermoon (the faction's leader), Latronicus Moonspear, Sentinel Selarin,
Kindal Moonweaver, Huntress Jalara Nightwind, Sentinel Aelyra Tidewatch on the pier, Innkeeper Shyria, Fyldren
Moonfeather (the coast's flight path), Trainer Nalia Moonbrow, an herb pair, a fishing and cooking pair, an armourer,
a provisioner, Quartermaster Lyriel Dawnbough (gives no quests, so she can move), a mailbox.

**Out on the maps:** Scout Wapi Longstride at the foot of the descent; the settlers of Cedar Hollow (June Nakamura,
Walt Hollis, Rosa Ibarra, Sam Okonkwo) and Sentinel Mirael Duskbrook at the landing; Sentinel Aerwyn Starbrook,
Tahu Swiftrunner and Dreamwatcher Sylanna at the Sentinels' Watch.

## The creatures

- **Open world** (`tools/build_feralas_openworld.py`): 58 creatures, 12 rares (one per subzone that has one), 48
  rare drops spread over every armour class and the six stat templates, the 40s forest gathering.
- **The Zukk'ash Hive** (`tools/build_zukkash_hive_content.py`): five kinds of Zukk'ash, the Deep Mother (the queen) and
  Tunnelmaster Zix'tal (at the dig's head), four drops each.
- All 14 named got their damage factor measured (`tools/calibrate_boss_damage.py --only`, every other boss's factor
  left exactly as it was).

## The quests (`tools/feralas_quests.py`, `tools/build_feralas_quests.py`)

83 quests: 57 given in Camp Mojache or Feathermoon (69%), nobody giving more than four, every kill target spawning
where it's sent, every explore point walkable. The theme is that everybody's digging: the Zukk'ash toward the Dry
Deep, the Hatecrest naga and the Gordunni after the way into Eldre'Thalas (Dire Maul), set up without opening it.
Chains out to Camp Taurajo (Brann's list for Elder Longtread), Onyxhollow (through the tunnel), Moonglade (the Dream
Bough), and Orgrimmar (Krueg's report). Earth comes up in 29% of them, mostly from the settlers, inside the band
`tools/qa_quest_lore.py` holds a 44-49 zone to. 249 hand-authored rewards, every spec of every class gets at least 25.

## The Feathermoon Sentinels (`tools/build_feathermoon_sentinels.py`)

The new faction, led by Shandris Feathermoon. TBC-style shelf on Moonglade's shelf code: friendly the Sentinel's
Draught and the tabard, honored the Feathermoon Crescent and a leatherworking pattern, revered six ilvl 67 blues and a
blacksmithing pattern, exalted the Moonbolt Crossbow, the Crescent Moonblade, the Staff of the Watchful Moon and two
recipes on their real level-60 ingredients. Rep: Feathermoon's people and the Sentinels' Watch pay the Sentinels
(225 a quest), Mojache's people pay Orgrimmar, the settlers pay nobody.

## Order to re-run after the art lands
1. Slice the sheets (`docs/feralas_art_prompts.md` has the slice tables).
2. Point `FERALAS_SHEET` / `FERALAS_COAST_SHEET` at the new ground and re-bake the three maps and two towns
   (`tools/bake_ashenvale.py feralas_*`, `tools/bake_ashenvale_towns.py camp_mojache feathermoon_stronghold`), the cave
   (`tools/bake_zukkash_hive.py`).
3. Swap the props and buildings in the five map modules' `dress()`.
4. `tools/build_feralas_openworld.py` and `tools/build_zukkash_hive_content.py` (the sprites switch themselves).

## Checked (20 Nov 2026)
- Every link walked both ways from the built zones: each lands on open ground, never on a portal.
- The levelling run (`tools/sim_campaign.py`) with Feralas in: all three specs reach 60, nothing in Feralas killed any
  of them, and the 46-50 band now does 113-116 quests (it was 105-109). The rare census for Feralas alone (`--zones`):
  the warrior and the priest win 60-100% against every rare, the mage 20-40% (the class pass's, as everywhere).
