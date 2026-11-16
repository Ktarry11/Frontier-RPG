# Epic drops: the plan (16 Nov 2026)

Kyle, 09:59: "Dont forget we likely need to ensure a healthy and varied amount of epic world drops from 30-60 and
also that dungeons above level 40 can drop very very rare epics. So we should ensure this is the case. Usually epics
in dungeons are found on the final boss with a low thing like 4% or 5% chance."

## Where it stands (before this pass)
- `entities/epic_drops.py` rolls named epics from `data/loot/epic_drops.json`.
- The world pool has 32 epics. Only 3 are at level 55 or above, and cloth and mail have 3 each.
- The dungeon pool has 27 epics, shared by every boss at level 30 or above, at 6% a kill (world bosses and caves
  included).
- The world roll is already one roll (0.25%) and then one pick, but the pick reads the PLAYER's level (anything up
  to it plus two), not the zone's.

## Kyle's answers
- **Dungeons above 40:** each dungeon's final boss gets one or two named epics of its own, at about 5%. The other
  bosses get none.
- **Dungeons 30 to 39:** keep an epic, at a lower chance (about 2%), on the final boss only.
- **World epics:** "have about 70 but DONT have each one roll a 1/400 - have the roll first then a second roll to
  determine the epic based on lvl....this will prevent a massive swamp of epics dropping if each one is rolled
  individually. Have about 100+ world epics from 30-60 and make sure they are varied between classes and
  slots....keep them somewhat generalist but you can have a few that are more specific for classes (maybe about 10
  more class specific ones and 115 generalist) this is how wow does it."
- **World rate:** keep about 1 in 400 kills.

## The build
1. **One roll, then one pick by ZONE level.** A kill at 30+ rolls 1 in 400 once. On a hit, the epic is picked from
   those whose level fits the zone's level band (`data/zones/zone_levels.json`), not the player's level. Kyle,
   10:05: "not picked by player level! picked by zone level". So a level 60 farming a level 35 zone gets that
   zone's epics, and a zone's epics are what the zone is known for. Never one roll per epic.
2. **World pool to about 125:** 115 generalist and about 10 class-specific, spread evenly over 30 to 60 by level band,
   across every slot and armour type and the weapon families, checked against the 97 specs of 30 classes.
3. **Dungeon epics by dungeon:** every dungeon whose final boss is 40 or above gets one or two of its own, themed on
   that boss, at about 5%. Final bosses from 30 to 39 roll the shared dungeon pool at about 2%. Nothing else rolls.
4. **QA:** `qa_epic_drops` checks the rates, the one-roll rule, the level window, the coverage by slot and spec, and
   that every 40+ dungeon's final boss has its own epic.

## Icons
Kyle, 10:03: "We can also draw world drops from some current wow icons as we have more epic looking ones. We need to
just ensure that they only take 1 icon...this is similar to boss drops.....every unique item in the game can only
have ONE icon."
- Every new epic gets an icon no other item uses. The build picks from the unused epic-looking icons and the QA
  fails if two unique items share one.

## What was built (16 Nov 2026)
- **Tables:** `tools/epic_table.py` (identity, flavour, icon, boss), built by `tools/build_epic_drops.py` into
  `data/loot/epic_drops.json`. New epics come from LootGenerator at epic budget and go onto the item curve at 1.0;
  older epics keep their stats unless they were off the curve.
- **The world pool:** 131 epics from level 30 to 60, about twenty in every five-level band, across every slot and
  armour type. Ten are class-leaning (Kyle: "not class locked, more just class leaning"), with authored stat lines
  in `MIX`: a Restoration Druid idol and vest, a Shaman totem, a Paladin libram, a frost wand, a Rogue kris, a fire
  mantle, shadow robes, Primalist legguards, a Hunter bow and a Felsworn cowl.
- **The dungeon epics:** 28. The 40+ final bosses (the Bloodsail Raider, the Lashings, the Mother Vein, the
  Captain's Cabin, the Cistern, Khaz Varun, Jaedenar, the Royal Hive and the Emberdeep) each have two of their own
  at 5%. The 30-39 final bosses roll at 2%: the Deep Bloom its own five, the others a shared five. The Plaguelands
  dungeons join when they're built.
- **The roll:** `entities/epic_drops.roll_epic(enemy, player_level, zone=...)`. One roll a kill; on a hit, one pick
  from `world_pool(zone band)`, the epics whose required level sits from three under the band's floor to one over
  its top. Combat passes its zone. Every zone from 30 up has at least eight to pick from.
- **Icons:** every epic has an icon no other item uses. 59 came from Kyle's pack ("WoW Icon Pack", the TBC and
  Wrath half that was never installed), as `gear_wow_*` so the procedural roller's `gear_inv_*` prefixes can never
  hand one to a random drop (`tools/install_epic_icons.py`). The 40 older epics that shared `gear_epic_*` art
  with crafted gear moved onto their own.
- **Flavour:** rewritten plain for every epic, old and new (Kyle: "please dont make weird ass AI tics for flavor
  line").
- **Trinkets:** the two new level 50+ trinkets do something (Heart of the Last Winter, Glassmaw's Gullet).
- **QA:** `tools/qa_epic_drops.py` checks the gate, the 1-in-400 rate, that the pick follows the zone and not the
  player, the 5% and 2% final-boss rates, that no other boss rolls a dungeon epic, the per-zone pool sizes, that
  every epic is reachable, the icons and the spread.
- **Also fixed:** `entities/boss_loot` read `epic_drops.json` as boss tables, so it believed in bosses called
  "world" and "dungeon". It skips that file now.
- **Worth knowing:** the procedural roller also makes random epics at about 0.3% a kill at level 38, alongside the
  named 0.25%. That was Kyle's earlier call ("BOTH kinds are wanted") and is unchanged.
