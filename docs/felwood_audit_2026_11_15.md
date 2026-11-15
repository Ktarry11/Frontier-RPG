# Felwood audit (15 Nov 2026)

Companion to claude/felwood_brief.md.

Commit 050461e. Guarded by `tools/qa_felwood.py`.

**Already sound:**
- Every map is linked both ways (Ashenvale East, South, Sanctuary, North, Jaedenar).
- Encounter tables cover every subzone, and every creature resolves to its own sprite.
- Each open map has 3 secrets, fishing and gathering pools.
- The inn and the flight master are at the Sanctuary.
- All 52 quests have real givers and turn-ins.
- The zone, NPC, portal, quest-giver and node QA tests pass.

**Fixed:**

| Problem | Fix |
|---|---|
| Emerald Reclamation rewards were an empty placeholder. | Quartermaster: Supreme Healing Potion at friendly, Supreme Mana Potion at honored. Timbermaw trader: ribs and wine at friendly, High Table Feast at honored, Blessed Sunheart Codex and Sunheart Tideguard patterns at revered, Sunheart Staff, Blessed Sunheart Staff and Sunheart Longbow patterns at exalted. |
| The vendor screen ignored faction standing entirely. No reputation reward in the game (Codex, Ashclaim, Reclamation) ever appeared on a shelf. | It now reads `available_consumables()` and rebuilds each time the shop opens. |
| North Felwood (the demon wastes) fought in the glowing-woodland backdrop. | North Felwood and the Fel Line now use the blighted backdrop. |
| Jaedenar wasn't classed as a dungeon. Neither were Khaz Varun, the Emberdeep or the Royal Hive. | Added to the dungeon list, along with Stromgarde Keep. Drywhisker Deeps stays a mine with its ore. |
| Morlos'Aren is a safe settlement whose quest promises two Sentinels, but nobody stood there. | Sentinels Ilthara Swiftleaf and Aeris Moonvale now hold it. They give no quests, because givers stay in the hubs. |

**Open:**
- A class trainer at the Sanctuary? Cinderwharf has one; the Sanctuary has only the herbalism and alchemy
  trainer Kyle asked for.
- The Timbermaw tunnel stays closed until Winterspring exists.
