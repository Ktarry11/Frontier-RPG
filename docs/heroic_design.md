# Heroic dungeons (18 Nov 2026)

Kyle, 18 Nov 2026, in order:
- "drop rep gain from Dungeons that are not heroic beyond revered. This will force players to do heroics to get to
  exalted!"
- "for heroic we will use same gear. Just improve stats. But some gear we can add."
- "Every dungeon yes."
- "Ensure vendor trash Is also appropriately improved in heroics as are chests drops."
- "Only TWO of the top tier crafting materials each bro. We want to keep a backup for higher tiers" and "heroics can
  get the same 2 crafting materials that We would put in the first few pure 60 zones. Do note which ones they are."

His answers on the shape: pick Normal or Heroic at the door; once per market day; level-60 elites with one
heroic-only trick per boss and "sometimes a heroic only boss for spice"; extra loot is a heroic-only item per
dungeon and badges for a vendor.

## The level-60 gear ladder (item levels)

| Source | Item level |
|---|---|
| Normal level-60 dungeons | 60-63 |
| Honored rep | 62 |
| Revered rep | 66 |
| **Heroic dungeons** (bosses, boss chests) | **66** |
| Heroic trash and side chests | 63 |
| **Heroics of the skull zones** | **68** (not built yet) |
| **Heroics of the frontier zones** | **69** (not built yet) |
| Exalted rep (a few slots per armour type; 250-350g) | 68 |
| T1, the Fallen Bluff | 68 (full sets) |
| Cairne Unmade | 71 |

Kyle: "Heroics are 66 (skull zones and frontier zones can be 68 and 69 heroics...so different)". The numbers live in
`world/heroic.py` (`ITEM_LEVEL`, `TRASH_ITEM_LEVEL`, `SPECIAL_ITEM_LEVEL`). The skull and frontier heroics aren't
built yet. Until they are, the hidden places stay as they are and are never heroic.

## Stage 1: the core (built 18 Nov 2026)

- **The door.** Walking into any dungeon from outside at level 60 asks Normal or Heroic (N / H, Esc to stay out).
  Every dungeon in `world/zone_classification.DUNGEONS` has a heroic. Floors and wings reached from inside are the
  same run. Walking back out of the dungeons ends the run.
- **Lockout.** Each heroic can be run once per market day (the market's clock, 24 market hours). It locks when you
  walk in, and a save keeps the run and the day's locks (`TravelManager.heroic_run`, `heroic_locks`).
- **Monsters.** Everything in a heroic run is level 60, and elite on top of its own difficulty row: health x1.3,
  damage x1.15 (`data/balance/monster_difficulty.json` "heroic"). That's a first guess, to tune once played.
- **Boss loot.** A boss drops the same item as on normal, rebuilt at item level 66, worn at 60. It keeps its name
  and stat mix, its stats are put on the item curve, and its weapon damage and armour grow as the loot generator's
  would. Pythas's Thunderstaff goes from 9 Intellect / 23 spell power at 24 to 32 / 82 at 66. A boss with no fixed
  table rolls a 66 blue.
- **Trash, coin and chests.** Heroic trash gear rolls at 63. Coin and vendor trash pay 1.5x a normal level-60 kill.
  Boss chests roll at 66 and side chests at 63, all worn at 60.
- **Materials.** A heroic monster rolls the level-59 pool plus only the two lowest top-tier rungs of each kind that
  monsters drop (`entities/material_tiers.HEROIC_TOP`). These are the same two the first pure-60 zones will use,
  and the 16 rungs above each pair are kept for higher tiers:
  - cloth: **Dreamsilk** (skill 310) and **Chronoweave** (320)
  - leather: **Manticore** (310) and **Chimera** (320)

  Ore, herbs, wood and gems are gathered, and a dungeon has no nodes, so they aren't affected. A heroic doesn't
  count as "pure 60", so its recipes stay pre-60.
- **Rep.** A heroic pays past Revered, and a faction's tabard takes its kill rep (`docs/tabards_design.md`).
  Combat passes its zone as a key (`wailing_caverns`), and the Revered cap now reads that key too. Before this fix,
  the cap never fired in a real fight.

QA: `tools/qa_heroic.py`, `tools/qa_tabards_and_dungeon_cap.py`.

## Stage 2: badges and heroic-only items (next)

- A badge from every heroic boss, and a badge vendor selling 66 gear.
- One heroic-only rare 66 per dungeon, from its last boss.

## Stage 3: tricks and spice

- One heroic-only ability per boss, from the boss mechanics already in the game.
- Now and then a heroic-only boss.

## Later

- The skull zone (68) and frontier zone (69) heroics.
- Tuning the elite multipliers once heroics have been played.
