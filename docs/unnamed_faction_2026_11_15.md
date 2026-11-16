# "????": the secret faction and its hidden seller (15 Nov 2026)

## What Kyle asked for

- "I want another secret vendor. Honored will be blue ilvl 69. Revered will be epic ilvl 78, Exalted will be ilvl 85."
- "Faction is '????' - It will be INCREDIBLY WELL HIDDEN and rep will only be through Frontier Bosses and not advertised where rep comes from. Frontier bosses give 50 rep a kill but we don't have an indication of how much rep we have it's only advertised as 'Current Status: Neutral / Friendly .... / Exalted'."
- He wants the seller "at the end of a frontier dungeon zone THROUGH another hidden zone", on a path that isn't linear, and "not even I can know where it is". He sells 24 items, 8 per tier.
- Then: "design everything with the items and everything and have the vendor but dont place him since he MUST be at the bottom of a high-end dungeon and be a bitch to get to ... not implement him yet."

## Built (`tools/build_unnamed_faction.py`, guarded by `tools/qa_unnamed_faction.py`)

### The faction, "????"

- **Nothing to read.** It's flagged `secret` in `data/factions/factions.json` and has no description, lore, leader or home.
- **The journal shows one line, in the list and on its own page:** "Current Status: <tier>". There's no bar and no number.
- **Its only source:** any **boss** killed inside a **frontier zone** pays 50, through `world/faction_manager.award_for_kill` (`frontier_boss_rep`).
  - Frontier trash pays nothing.
  - Bosses anywhere else pay nothing.
  - Quests pay nothing.
- **Combat stays silent about it.** It prints no "+50 reputation" line and no "You are now Friendly" line, and the victory screen doesn't count it.

### The seller, Wayless (parked)

- His record is in `data/npcs/unplaced_vendors.json`. Nothing loads that file.
- His shelf is the faction's `vendor_stock_unplaced`. Nothing reads that either.
- He's in no zone and on no shop, so nobody can find him until he's placed.
- His greeting: "You found me. Most people turn back long before here, so I don't get much company. Let's see what you've brought back from out there."

### The stock: 24 items, worn at 60

- **Theme:** the edge of the map. These are the people who went past where the roads stop, and what they brought back.
- **Stats** come from the crafted-gear identities, on the bent budget past 60.
- **Every tier serves tanks, healers, casters and fighters.**
- **Every epic has its own line.**

| Standing | Item | Slot | For | Price | Flavour |
|---|---|---|---|---|---|
| Honored (blue 69) | Edgewalker's Treads | leather feet | agility melee | 150g | Worn thin at the toe by roads that stopped being roads. |
| Honored (blue 69) | Mapless Mantle | cloth shoulder | caster | 160g | Embroidered with a map, and every line on it trails off. |
| Honored (blue 69) | Farwatch Gauntlets | plate hands | tank | 150g | Made for holding a line that nobody else can see. |
| Honored (blue 69) | Lantern-Bearer's Cord | cloth waist | healer | 145g | A hook on the left hip for a lantern, and scorch marks where it hung. |
| Honored (blue 69) | Trailblazer's Legguards | mail legs | hunter | 180g | Scratched by brush that doesn't grow anywhere you've been. |
| Honored (blue 69) | Band of the Unmarked Road |  ring | strength melee (crit) | 155g | There's no stone in it, only a groove where the road should be. |
| Honored (blue 69) | Pendant of No North |  neck | caster (crit) | 155g | A compass rose with the north point filed off. |
| Honored (blue 69) | Wayfinder's Bracers | mail wrist | healer (mp5) | 140g | Etched with stars. Not the ones you know. |
| Revered (epic 78) | Edge of the Known | sword_1h main_hand | agility melee (crit) | 560g | Everything on this side of it has a name. |
| Revered (epic 78) | The Blank Atlas | tome off_hand | healer | 520g | Every page is empty. Every page is somewhere you haven't been yet. |
| Revered (epic 78) | Farwatch Bulwark | shield off_hand | shield tank | 540g | Somebody has to stand where the map runs out. |
| Revered (epic 78) | Pathless Greatbow | bow ranged | hunter (crit) | 600g | There's no road where you're aiming. There never was. |
| Revered (epic 78) | Ridgebreaker Legplates | plate legs | strength melee | 580g | The ridge was in the way. Now it isn't. |
| Revered (epic 78) | Hood of the Farthest Light | cloth head | caster | 560g | The last lamp before the dark. Whoever wore it kept walking. |
| Revered (epic 78) | Hide of the Long Dark | leather chest | bear / beetle tank | 600g | Whatever lives out past the edge didn't get through this. It tried. |
| Revered (epic 78) | Hauberk of the Last Signal | mail chest | caster (haste) | 600g | The last word anyone heard from out there came from someone wearing this. |
| Exalted (epic 85) | Here Be Monsters | axe_2h main_hand | strength melee (crit) | 1200g | The old maps warned you. This is what the warning was for. |
| Exalted (epic 85) | Lodestar | staff main_hand | caster (crit) | 1150g | It always points the same way. Nobody knows what's there. |
| Exalted (epic 85) | Warden of the Edge | sword_1h main_hand | tank (1H, armour) | 1050g | Nothing comes back over the edge while this is drawn. |
| Exalted (epic 85) | Farsight | gun ranged | hunter (hit) | 1000g | You can see a long way from the edge. Further than is comfortable. |
| Exalted (epic 85) | The Long Way Home | mace_1h main_hand | healer | 1050g | Everyone who made it back came the long way. |
| Exalted (epic 85) | Unmapped | dagger main_hand | agility melee (crit) | 1000g | If it isn't on the map, it can't be found. Neither can you. |
| Exalted (epic 85) | Signet of the Final Mile |  ring | caster (spell hit) | 950g | Most turn back with a mile to go. This was made for the ones who didn't. |
| Exalted (epic 85) | Mask of the Farthest Hunt | leather head | bear / beetle tank | 980g | Out past the last trail, something bigger than a bear is still hunting. So are you. |

**Prices** are my first pass (Kyle didn't set them): blues 140-180g, revered epics 520-600g, exalted epics 950-1200g.

## A number to look at: how long the grind is

At 50 a frontier boss, on the shared ladder:

| Standing | Total rep | Boss kills |
|---|---|---|
| Honored | 9,000 | 180 |
| Revered | 21,000 | 420 |
| Exalted | 42,000 | 840 |

- **Bosses available today:** 2 frontier zones with 3 bosses each, so 6.
- **What that means:** exalted is 140 full clears of both frontiers. Revered alone is 70 clears.
- **This will ease** as more frontier zones (and bosses) are added, since every one of them pays. It's Kyle's call whether to keep 50 or raise it.

## Placing him (not done: the design only)

The rules he'll be placed by:
- **The depth:** at the bottom of a high-end dungeon.
- **The way in:** reached **through** a hidden zone. The way is never visible from any main path.
- **The route is not straight.** For example, from one corner it might go south, then east, then north, then east, then north again, with secrets along the way.
- **The room** feels earned: somewhere you'd only end up by going all the way.

When he's placed, his record moves into `data/npcs/vendors.json` (placed through the zone's builder) and the faction's `vendor_stock_unplaced` becomes `vendor_stock`. Then `qa_unnamed_faction` flips its parked checks to placed ones.

**Where he ends up is never written in a doc, a commit message or a reply** (the SECRETS rule: "not even I can know where it is").
