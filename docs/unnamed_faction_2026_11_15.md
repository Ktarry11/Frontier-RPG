# "????": the secret faction and its hidden seller (15 Nov 2026)

## What Kyle asked for

- "I want another secret vendor. Honored will be blue ilvl 69. Revered will be epic ilvl 78, Exalted will be ilvl 85."
- "Faction is '????' - It will be INCREDIBLY WELL HIDDEN and rep will only be through Frontier Bosses and not advertised where rep comes from. Frontier bosses give 50 rep a kill but we don't have an indication of how much rep we have it's only advertised as 'Current Status: Neutral / Friendly .... / Exalted'."
- He wants the seller "at the end of a frontier dungeon zone THROUGH another hidden zone", on a path that isn't linear, and "not even I can know where it is". He sells 24 items, 8 per tier (later raised to 15 per tier, 45 in all).
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

### The stock: 45 items, worn at 60 (15 a tier)

Kyle, 15 Nov 2026: "lets do 15/15/15 ---- why not. Don't forget ALL the CoA classes, all the equipment slots....everything. Don't be limited! Like trinkets". Then, on my first draft: "wheres my tinkerer healer? My caster shield? My strength leather? Etc....don't neglect people - stop defaulting to classic 9 classes".

- **Theme:** the edge of the map. These are the people who went past where the roads stop, and what they brought back.
- **Stats** come from the crafted-gear identities, on the bent budget past 60. Two identities are new (in `tools/build_crafted_gear.py`), for the slots everybody shares:
  - `physical`: attack power, hit and stamina, with no strength or agility, so one cloak or trinket serves a Barbarian, a Rogue and a Reaper alike.
  - `tank_any`: stamina, defense and dodge, with no strength or agility, so one ring serves a Warrior, a Bloodmage and a Reaper alike.
- **Every epic has its own line**, and so does every blue.
- **Three trinkets do things** (procs below).

**Checked against all 97 specs of the 30 classes** (`data/items/spec_gear.json`), not the classic 9. `qa_unnamed_faction` fails unless:
- every spec finds at least one piece at **every tier** that it can equip (`entities/proficiency.can_equip`) and wants (its role and stat template). Today the fewest any spec gets across the shop is 4;
- every armour type is made for every role that wears it: cloth casters and healers; leather fighters (agility AND strength), tanks, healers and casters; mail fighters, tanks, healers and casters; plate fighters, tanks, healers and casters;
- every weapon any spec carries is sold: all 1H and 2H types, fist weapons, polearms, staff, dagger, shield, tome, bow, gun, crossbow, wand, thrown, totem, idol and libram;
- every equipment slot appears: head, neck, shoulder, back, chest, wrist, hands, waist, legs, feet, ring, trinket, main hand, off hand and ranged;
- there's a tank's shield, a caster's shield and a healer's shield;
- every trinket has a proc.

Kyle's three examples are in: the **Tinker healer** (Flare of the Lost Party, a healing gun, plus Wayfinder's Bracers in mail), the **caster's shield** (Ward of the Last Map, and Last Light Aegis for healers), and **strength leather** (Cragstrider's Jerkin, for the Barbarian).

| Standing | Item | Type and slot | For | Stats | Price | Flavour |
|---|---|---|---|---|---|---|
| Honored (blue 69) | Edgewalker's Treads | leather feet | agility melee | +17 agility, +9 stamina, +43 attack power | 150g | Worn thin at the toe by roads that stopped being roads. |
| Honored (blue 69) | Mapless Spaulders | plate shoulder | caster **plate caster (Starcaller, Cultist)** | +23 intellect, +52 spell power | 165g | Engraved with a map, and every line on it trails off. |
| Honored (blue 69) | Farwatch Gauntlets | plate hands | plate tank | +24 stamina, +9 strength, +19 defense rating | 150g | Made for holding a line that nobody else can see. |
| Honored (blue 69) | Lantern-Bearer's Cord | cloth waist | healer | +12 spirit, +9 intellect, +52 healing power | 145g | A hook on the left hip for a lantern, and scorch marks where it hung. |
| Honored (blue 69) | Trailblazer's Legguards | mail legs | agility + intellect (hunter, Tinker, Venomancer) | +21 agility, +17 intellect, +62 attack power | 180g | Scratched by brush that doesn't grow anywhere you've been. |
| Honored (blue 69) | Band of the Unmarked Road |  ring | ANY tank (stamina, defense, dodge) | +21 stamina, +14 defense rating, +10 dodge rating | 155g | There's no stone in it, only a groove where the road should be. |
| Honored (blue 69) | Pendant of No North |  neck | caster (crit) | +8 intellect, +32 spell power, +13 crit chance spell | 155g | A compass rose with the north point filed off. |
| Honored (blue 69) | Wayfinder's Bracers | mail wrist | healer (mp5) **mail healer (Tinker, Shaman, Vizier)** | +14 intellect, +67 healing power | 140g | Etched with stars. Not the ones you know. |
| Honored (blue 69) | Flare of the Lost Party | gun ranged | healer (mp5) **Tinker healer** | +13 intellect, +58 healing power | 170g | Built to call for help. Turns out it can be the help. |
| Honored (blue 69) | Cragstrider's Jerkin | leather chest | strength melee **strength leather (Barbarian)** | +24 strength, +14 stamina, +62 attack power | 175g | Cut loose and heavy across the shoulders, for someone who climbs with their arms. |
| Honored (blue 69) | Hollowridge Headguard | mail head | agility tank (bear, beetle, Bloodmage, Felsworn, Reaper...) **mail tank** | +27 stamina, +17 agility, +13 dodge rating | 165g | The dents all face forward. |
| Honored (blue 69) | Lamplighter's Wand | wand ranged | caster | +17 intellect, +38 spell power | 150g | It was a lamp-lighting taper once. It still finds the dark. |
| Honored (blue 69) | Compass of Bad Directions |  trinket | ANY fighter (attack power, hit) | +11 stamina, +40 attack power, +11 hit rating *Proc:* Your critical hits have a chance to grant 60 attack power for 3 turns. | 160g | It points at trouble. It has never once been wrong. |
| Honored (blue 69) | Surveyor's Gloves | leather hands | caster (crit) **leather caster** | +9 intellect, +36 spell power, +14 crit chance spell | 150g | Ink-stained at the fingertips from maps nobody finished. |
| Honored (blue 69) | The Last Handhold | axe_1h main_hand | agility + intellect (Felsworn, Witch Doctor) | +20 agility, +17 intellect, +42 attack power | 170g | A climber's axe, the last grip before the drop. Somebody pried it loose and kept it. |
| Revered (epic 78) | Edge of the Known | fist_weapon main_hand | agility melee (crit) | +28 agility, +75 attack power, +28 crit chance physical | 560g | Everything on this side of it has a name. |
| Revered (epic 78) | The Blank Atlas | tome off_hand | healer | +25 spirit, +20 intellect, +111 healing power | 520g | Every page is empty. Every page is somewhere you haven't been yet. |
| Revered (epic 78) | Farwatch Bulwark | shield off_hand | shield tank | +50 stamina, +18 strength, +45 block value | 540g | Somebody has to stand where the map runs out. |
| Revered (epic 78) | Pathless Greatbow | bow ranged | agility ranged (crit) | +24 agility, +64 attack power, +24 crit chance physical | 600g | There's no road where you're aiming. There never was. |
| Revered (epic 78) | Ridgebreaker Legplates | plate legs | strength melee | +46 strength, +26 stamina, +118 attack power | 580g | The ridge was in the way. Now it isn't. |
| Revered (epic 78) | Hood of the Farthest Light | cloth head | caster | +44 intellect, +100 spell power | 560g | The last lamp before the dark. Whoever wore it kept walking. |
| Revered (epic 78) | Hide of the Long Dark | leather chest | agility tank (bear, beetle, Bloodmage, Felsworn, Reaper...) | +59 stamina, +39 agility, +30 dodge rating | 600g | Whatever lives out past the edge didn't get through this. It tried. |
| Revered (epic 78) | Hauberk of the Last Signal | mail chest | caster (haste) | +33 intellect, +98 spell power, +27 haste | 600g | The last word anyone heard from out there came from someone wearing this. |
| Revered (epic 78) | Ten-Foot Pole | polearm main_hand | agility melee | +39 agility, +22 stamina, +99 attack power | 580g | For prodding the things you'd rather not get any closer to. |
| Revered (epic 78) | Where the Road Ends | sword_2h main_hand | strength melee (crit) | +33 strength, +89 attack power, +33 crit chance physical | 600g | It isn't a figure of speech. You'll know the place when you see it. |
| Revered (epic 78) | Holdfast | mace_2h main_hand | agility tank (Reaper, Venomancer, Druid) | +53 agility, +31 stamina, +18 dodge rating, 166 armour | 580g | Plant it, and nothing gets past. Not even you. |
| Revered (epic 78) | Cairn Totem | totem ranged | caster | +16 intellect, +44 spell power, +8 crit chance spell | 520g | Stones stacked where the trail ends. Whoever passes adds one more. |
| Revered (epic 78) | Last Light Aegis | shield off_hand | healer **healer's shield** | +23 spirit, +18 intellect, +99 healing power | 560g | Polished bright enough to signal with. Whoever held it wanted to be found. |
| Revered (epic 78) | The Last Lantern |  trinket | healer | +20 intellect, +16 spirit, +88 healing power *Proc:* Your healing spells have a chance to restore 60 mana and grant 90 healing power for 3 turns. | 560g | It's never been lit. It's never gone out. |
| Revered (epic 78) | Lightkeeper's Pauldrons | plate shoulder | healer (mp5) **plate healer** | +33 intellect, +120 healing power, +7 mp5 | 560g | Somebody kept the light at the edge burning for years, and kept everyone near it alive. |
| Exalted (epic 85) | Here Be Monsters | axe_2h main_hand | strength melee (crit) | +42 strength, +113 attack power, +42 crit chance physical | 1200g | The old maps warned you. This is what the warning was for. |
| Exalted (epic 85) | Lodestar | staff main_hand | caster (crit) | +51 intellect, +189 spell power, +76 crit chance spell | 1150g | It always points the same way. Nobody knows what's there. |
| Exalted (epic 85) | Warden of the Edge | sword_1h main_hand | tank (1H, armour) | +70 stamina, +28 hit rating, +34 defense rating, 422 armour | 1050g | Nothing comes back over the edge while this is drawn. |
| Exalted (epic 85) | Farsight | crossbow ranged | agility ranged (hit) | +31 agility, +80 attack power, +31 hit rating | 1000g | You can see a long way from the edge. Further than is comfortable. |
| Exalted (epic 85) | The Long Way Home | mace_1h main_hand | healer | +35 intellect, +28 spirit, +155 healing power | 1050g | Everyone who made it back came the long way. |
| Exalted (epic 85) | Unmapped | dagger main_hand | agility melee (crit) | +36 agility, +96 attack power, +36 crit chance physical | 1000g | If it isn't on the map, it can't be found. Neither can you. |
| Exalted (epic 85) | Signet of the Final Mile |  ring | caster (spell hit) | +20 intellect, +77 spell power, +31 spell hit rating | 950g | Most turn back with a mile to go. This was made for the ones who didn't. |
| Exalted (epic 85) | Trophy of the Farthest Hunt |  trinket | agility tank (bear, beetle, Bloodmage, Felsworn, Reaper...) | +46 stamina, +31 agility, +23 dodge rating *Proc:* When you're struck, you have a chance to shrug it off: a shield that absorbs 8% of your health. | 1000g | Out past the last trail, something bigger than a bear is still hunting. So are you. |
| Exalted (epic 85) | Ward of the Last Map | shield off_hand | caster **caster's shield** | +35 intellect, +95 spell power, +17 crit chance spell | 1000g | The only map of the far side is painted on the inside of this shield. Don't lose it. |
| Exalted (epic 85) | Idol of the Last Grove | idol ranged | healer | +17 spirit, +14 intellect, +75 healing power | 950g | Carved from the last tree before the edge. It still has roots. |
| Exalted (epic 85) | Libram of the Final Entry | libram ranged | strength + intellect (Paladin, Sun Cleric, Cultist, Primalist, Templar) | +20 strength, +20 intellect, +56 attack power | 950g | The last page was written by someone who was still walking. |
| Exalted (epic 85) | Stone from the Edge | thrown ranged | agility melee (crit) | +31 agility, +80 attack power, +31 crit chance physical | 950g | Thrown from the very last step. It came back. |
| Exalted (epic 85) | Signal-Fire Breastplate | plate chest | strength + intellect (Paladin, Sun Cleric, Cultist, Primalist, Templar) | +50 strength, +50 intellect, +133 attack power | 1150g | Lit at the edge, so the next ones would know how far the last ones got. |
| Exalted (epic 85) | Lifeline Harness | leather chest | healer **leather healer** | +42 intellect, +33 spirit, +183 healing power | 1100g | Tied to the one behind you, so nobody goes over the edge alone. |
| Exalted (epic 85) | Cloak of the Last Horizon |  back | ANY fighter (attack power, hit) | +26 stamina, +101 attack power, +26 hit rating | 1000g | Dyed the colour of the sky right where it meets the edge. |

**Prices** are my first pass (Kyle didn't set them): blues 140-180g, revered epics 520-600g, exalted epics 950-1200g.

**Changed from the 24-item draft:**
- Mapless Mantle became the plate Mapless Spaulders (plate casters).
- Band of the Unmarked Road went from strength to any-tank.
- Edge of the Known went from a sword to a fist weapon. Fist weapons are wider: Shaman and Witch Doctor can't use swords.
- Farsight went from a gun to a crossbow, since the healing gun covers guns.
- Mask of the Farthest Hunt became the trinket Trophy of the Farthest Hunt.

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
