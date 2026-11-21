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
| Frontier Quartermasters: the Pathfinder line | 66 |
| Frontier Quartermasters: the Horizon line | 68 (blue) |
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
  Every dungeon in `world/zone_classification.DUNGEONS` has a heroic. The Return Voyage's two Bloodsail ships and the
  Eldest Sequoia joined the list on 21 Nov 2026 (Kyle: "ensure all Dungeons are counting as Dungeons"). Floors and wings reached from inside are the
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
- **Materials: the first top tiers.** Kyle: "So only take 2 from the ore/cloth/leather/wood and these will be in
  heroics and lvl 60 zones to craft gear", then gems too. Level 60 gets only the two lowest rungs of each endgame
  ladder, and everything above stays for higher content (`entities/material_tiers.LEVEL60_TOP`):

  | Kind | The two | From |
  |---|---|---|
  | cloth | **Dreamsilk** (310), **Chronoweave** (320) | humanoids in heroics |
  | leather | **Manticore** (310), **Chimera** (320) | skinning beasts in heroics |
  | ore | **Frostforged Silver** (310), **Sylvanite** (310) | heroic bosses (2-4), heroic side chests |
  | wood | **Voidwood** (310), **Dreamwillow** (320) | heroic bosses (2-4), heroic side chests |
  | gem | **Glacier Sapphire** (310), **Sylvan Emerald** (310) | heroic bosses (1), heroic side chests |

  These are the same ten the level-60 zones will use when they're built ("Heroic bosses, chests and eventually the
  lvl 60 zones"). A heroic monster's cloth and leather come from the level-59 pool plus these two. Every heroic boss
  also drops one find of ore, wood or a gem. A side chest holds one instead of gear 40% of the time. A heroic
  doesn't count as "pure 60", so its recipes stay pre-60.
- **Rep.** A heroic pays past Revered, and a faction's tabard takes its kill rep (`docs/tabards_design.md`).
  Combat passes its zone as a key (`wailing_caverns`), and the Revered cap now reads that key too. Before this fix,
  the cap never fired in a real fight.

QA: `tools/qa_heroic.py`, `tools/qa_tabards_and_dungeon_cap.py`.

## Stage 2: the Frontier Mark, the Frontier Quartermasters and heroic-only items (built 21 Nov 2026)

Kyle, 21 Nov 2026: "Yeah build stage 2", "the badge vendor can have multiple tabs. We can organize it by armor slot and
type and weapon slot. We will have heroic sales and maybe some more expensive buy only blues", "Ensure the vendor is
well organized and sleek and sexy. Make the more expensive blues higher ilvl", "Don't call them badge of honor. We are
Frontier RPG", "quartermaster to sell will be in capital cities only. Org, UC, and Auerlion", "we should have an icon for
them on the map, maybe use the frontier mark to indicate where they are". Built by `tools/build_heroic_rewards.py`;
art is sheet HB1 (`docs/heroic_art_prompts.md`, `tools/slice_heroic_icons.py`).

- **The Frontier Mark.** Every boss killed on a heroic run drops one (both bosses of a pair fight each drop one). It's a
  material that stacks to 500, and it's what the quartermasters trade for.
- **The Frontier Quartermasters**, one in each capital: Gruka Ashmane in Orgrimmar, Lorran Wicke in the Undercity and
  Ysane Corvell in Aurelion, each beside the city's banker. The map marks them with the mark itself.
- **The shelf**, tabbed by armour type and weapon slot (Cloth, Leather, Mail, Plate, Jewelry, Main Hand, Off Hand,
  Ranged, and All), each tab sorted head to toe. Every row shows the piece's icon, its slot, its item level and its
  line, and the price in marks beside the mark's picture; the marks you're carrying show under the shelf.
  - **The Pathfinder line, item level 66** (a heroic boss's level), 46 pieces: every armour slot in all four types,
    cloaks, necks, rings, and a weapon for every hand. 15 to 45 marks.
  - **The Horizon line, item level 68**, 25 pieces, sold nowhere else and dearer: head, shoulders, chest and legs in
    all four types (each in the stat mix the Pathfinder piece in that slot doesn't have), jewellery and five weapons.
    30 to 75 marks. It sits beside the Exalted rep epics and T1 on item level, under them on budget.
- **Heroic-only items.** Every dungeon's last boss (the highest-level boss on the last floor of each dungeon chain, 39 dungeons) has a one-in-five
  chance on a heroic run at an item nothing else drops, item level 66, worn at 60. The 26 highest dungeons' items have
  their own icons from HB1; the rest wear stock icons.
- **Bound.** Neither the quartermasters' gear nor a heroic-only item can go on the auction house or in the mail.

QA: `tools/qa_heroic_rewards.py`.

## Stage 3: tricks and spice

- One heroic-only ability per boss, from the boss mechanics already in the game.
- Now and then a heroic-only boss.

## Crafting stays competitive (Kyle, 18 Nov 2026: "I'll ALWAYS want crafting to be competitive to raiding/Dungeons")

Measured on 18 Nov: almost nothing crafts from the first top tiers yet. The only crafted gear at the heroic or raid
level is the 32 Exalted rep patterns (68). Woodworking's level 50-56 tier turned out to be built on three level-60
woods that grew nowhere. Those woods were moved below the line the same day (Kyle: "Nothing sub 60 should use lvl 60
materials"; `tools/fix_pre60_woods.py`, guarded by `tools/qa_no_level60_materials_below_60.py`). The ten
materials above then got a crafting tier of their own, the Master tier (`tools/build_master_crafting.py`,
`docs/master_crafting.md`): blues at 66 from the first rung, and epics at 68 from the second rung, whose patterns drop
from heroic bosses.

## Later

- The skull zone (68) and frontier zone (69) heroics.
- Tuning the elite multipliers once heroics have been played.
