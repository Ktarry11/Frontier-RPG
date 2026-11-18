# Tabards and the Revered dungeon cap (18 Nov 2026)

Kyle, 18 Nov 2026:
- "drop rep gain from Dungeons that are not heroic beyond revered. This will force players to do heroics to get to
  exalted!"
- "I want to have the tabbard style rep where wearing a factions tabbard will shift all rep gained to that faction.
  Since no factions will gain rep in dungeons past revered unless the dungeon is heroic - this will help to get all
  factions to exalted and lets the player pick." ("this is what cataclysm did i think": it is, championing.)

His answers on the details:
- **What moves:** dungeon kills only. Quest and zone rep never move, so a tabard never costs a zone its rep.
- **Where it works:** heroic dungeons only.
- **Order:** build the cap and the tabards now, then design heroic mode with him next.

## How it works

**The cap.** Any kill inside a dungeon (`world/zone_classification.is_dungeon`, which includes the hidden layers)
pays nothing to a faction already at Revered, unless the dungeon is heroic. The open world isn't touched.
The older per-dungeon caps still apply on top. For example, the Scarlet Monastery wings stop paying the Pale Flame
at Honored. (`world/faction_manager.DUNGEON_CAP`, `FactionManager.award_for_kill`)

**The tabards.** There's one per faction, 16 in all. The secret faction has none, because it's never advertised.
- Each faction's quartermaster sells its tabard at Friendly for 1 gold. Like every quartermaster item, it never goes
  on the auction house.
- A tabard has no stats and goes in its own slot, under Ranged on the paper doll.
- (`tools/build_tabards.py`, `data/items/tabards.json`, `world/tabards.py`)

**Championing.** The party leader's tabard counts. In a heroic dungeon, a kill pays the most any faction would have
had for it, all of it to the tabard's faction, and nothing to the others. That pay goes all the way to Exalted. In a
normal dungeon, or out in the world, the tabard does nothing. A secret faction's rep never moves.

**Cenarion Circle and the Wakened** have no dungeons of their own. Once heroics exist, a heroic in their tabard is
their dungeon road.

## Not built yet

- **Heroic mode.** There's nothing heroic anywhere in the game yet. The combat engine reads `self.heroic`, which
  nothing sets, so until heroics exist dungeons stop at Revered and tabards wait. Quests still go to Exalted. This is
  the next design job with Kyle.
- **Tabard art.** The icons are the guild tabard tinted to each faction's colours, with a prompt to come.

QA: `tools/qa_tabards_and_dungeon_cap.py`.
