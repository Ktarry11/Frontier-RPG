# The Plaguelands: design (16 Nov 2026)

Kyle, 16 Nov 2026: "WPL and EPL? School, strath, and maybe a new Scarlet Crusade dungeon? Keep the similar cauldron
quests", then the faction: "I want a new faction. One that is unique because the leader and top fighters are FROM
EARTH. They're Order of the Pale Flame and they recruited defects from The Scarlet Crusade and they're more selective
in who they kill, they don't go after all undead, only mindless ones. They're mix between Argent dawn and Scarlet
Crusade and you get rep by killing Scarlet fanatics. So it'll be rep from Scarlet monetary and the new dungeon in WPL
where hearthglen is". And: "The Geography can be somewhat similar with minor adjustments as the integration didn't
change this too too much geographically. It should feel familar-ish for players."

Every decision below was Kyle's answer to a question unless it's marked **(assumed)**. Assumptions stand until he
vetoes them.

## The one hard rule

Kyle: "this is CRITICAL that no post-game materials drop and no post-game gathering nodes in zones that are NOT pure
60. So even though these zones go to 60, they are not at pure 60."

- **Pure 60 means a zone whose band is exactly 60 to 60.** Nothing in this push is pure 60: every Plaguelands map,
  Scholomance, both halves of Stratholme, Hearthglen and the Scarlet Monastery are all held below the line.
- The line is `entities/material_tiers.py` (above Runecloth, Rugged Leather and Thorium, and the endgame wood tier).
- **The line, in code (`material_tiers.is_postgame`):** anything whose skill starts above 300, plus the high cloth
  and leather tiers. Frontier fillers between the WoW anchors and 300 (Ashen Steel, Starleaf) stay pre-60 under the
  "go to skill 300" crafting canon. Kyle confirmed it 16 Nov ("No we keep it as it is"): about 16 to 18 tiers of
  each ladder stay end-game only, as the crafting raid tiers. `qa_gathering_legality` now uses the same line and
  checks each ladder keeps that backlog.
- **What had to change in code (done 16 Nov):** the floor today is applied by the *creature's* level (drop bands stop at 59). A
  level 60 elite in a 55 to 60 zone would get past it. The gate moves to the *zone's* band: a drop or a node is
  high tier only if the zone it rolls in is pure 60. Same for chests, skinning, mob reagents, fishing, ore-vein
  crystals and dungeon boss tables.
- **QA that fails the build:** `qa_no_postgame_below_pure_60` sweeps every zone whose band isn't 60 to 60 and fails
  on any high-tier material in a node pool, a drop band, a chest table, a skinning or fishing table, a mob reagent
  or a boss pool. It runs on the Plaguelands from the first commit and on every zone after.

## Levels (Plan A)

| Place | Band |
|---|---|
| Alterac foothills road (Hillsbrad to WPL) | 50 to 52 |
| South Western Plaguelands | 51 to 54 |
| North Western Plaguelands | 53 to 56 |
| West Eastern Plaguelands | 55 to 58 |
| East Eastern Plaguelands | 56 to 60 |
| Scholomance | 56 to 60 |
| Stratholme, both halves | 57 to 60 |
| Hearthglen | 58 to 60 |
| Scarlet Monastery: Graveyard / Library / Armory / Cathedral | 28 to 32 / 32 to 36 / 35 to 39 / 38 to 42 |

The four-map split inside each of WPL and EPL is my reading of "WPL 51 to 56, EPL 55 to 60" across two maps each.

## Maps

**Western Plaguelands, two maps.**
- *South WPL:* the Bulwark at the Tirisfal border, Felstone Field and Dalson's Tears with their cauldrons, Sorrow
  Hill and Uther's Tomb, the Pale Flame's keep, the Caer Darrow shore with Scholomance across the water.
- *North WPL:* Andorhal's ruins and the Scourge against Forsaken line through them, Gahrron's Withering and the
  Writhing Haunt with their cauldrons, Northridge Lumber Camp, and Hearthglen's gates at the top.

**Eastern Plaguelands, two maps.**
- *West EPL:* Plaguewood and Terrordale, Stratholme's gates, Corin's Crossing, the Marris Stead.
- *East EPL:* Light's Hope Chapel, Tyr's Hand on the coast, Darrowshire, Crown Guard Tower's camp, Zul'Mashar and
  Quel'Lithien Lodge in the far north east.

The ground should read as the Plaguelands players remember, with the Integration's small adjustments rather than a
new map.

**Ways in.**
- *Tirisfal via the Bulwark:* Eastern Tirisfal's east edge, the classic road.
- *The Alterac foothills road:* a short pass map up from Eastern Hillsbrad (the Tarren Mill side) with a Pale Flame
  checkpoint on it.
- *The Undercity side door:* a quest chain from the Bulwark's apothecaries opens a sewer route from the Undercity
  into South WPL. It's on the map once it's open.
- *Flight points:* the Bulwark, Light's Hope, Sorrow Hill and Crown Guard once found.

**Hubs.**
- **The Bulwark** (Forsaken): apothecaries, the cauldron quests, the Undercity door chain.
- **Sorrow Hill** (the Pale Flame's keep by Uther's Tomb, right under Hearthglen's nose): the faction's home,
  quartermaster, leader, recruits.
- **Light's Hope Chapel** (the Argent Dawn): Scourgestone turn-ins, Argent quartermaster.
- **Crown Guard camp:** a small outpost in EPL between Stratholme and Light's Hope.
- Every hub gets an inn and a flight master. Profession trainers stay in themed pairs and only where a hub needs them.

**Set pieces kept:** Andorhal, Uther's Tomb, Darrowshire and Pamela's chain, Tyr's Hand, Plaguewood and Terrordale,
the Marris Stead and Corin's Crossing, Zul'Mashar and Quel'Lithien. (Tirion's hut wasn't picked, so it isn't planned.)

**A hidden zone:** yes. Kyle: "Surprise me....but yes! Yes yes". Its place and contents are kept out of this doc.

## The Order of the Pale Flame

**Who they are.** A holy order whose leader and best fighters are Earth transplants. The leader joined the Scarlet
Crusade during the Integration, when the Crusade looked like the only people fighting what was killing everyone. He
saw what it was, and he walked out with the best of the people around him. They scraped the red off the Crusade's
flame, which is where the name comes from. They kill the mindless dead and leave the thinking ones alone.

**Leader (pitch, Kyle to veto):** *Flamekeeper Rory Callahan*. A man in his fifties, a gruff veteran with dry humour
and old scars, born in Cork and an ironworker in Boston until the Integration. He served beside the man who now leads
Hearthglen, and he left the night the Crusade burned a transplant camp for "consorting with the dead".

**Recruitable fighters (three, from recruit sheet 4, `docs/recruit_art_prompts_sheet4.md`):**
- *Bruno*, a heavyweight fighter from Curitiba (Templar Zealot) who walked out of the Crusade beside Rory.
- *Joaquín*, from Rosario, once a Scarlet interrogator (Sun Cleric Valkyrie); he carries what he did there.
- *Isla*, a deer stalker from the Highlands (Witch Hunter Boltslinger) who joined after the Crusade years, never before.
Each joins after a Pale Flame chain, with full character traits and bond writing like the recruit overhaul. They all
serve the Order, but the recruits-don't-know-each-other rule holds: each one's text talks about Rory and the Order,
never about another recruit.

**Earth talk:** loud inside the Order (they talk about home freely among themselves), the usual high-zone band
everywhere else.

**Relations.**
- *The Forsaken:* an uneasy truce. They won't hunt the Forsaken, they trade carefully, and some members hate the
  truce. Forsaken player characters are welcome but watched.
- *The Argent Dawn:* rivals who need each other. The Argent Dawn sees them as Scarlets with better manners; the Pale
  Flame thinks the Argent Dawn is too slow. They share Scholomance and Stratholme intelligence.
- *The Scarlet Crusade:* the enemy. The Crusade has its own transplants now, and the worst of them leads Hearthglen.

**Reputation.**
- Scarlet kills in the Scarlet Monastery pay rep, **capped at Honored**. Hearthglen and quests carry you to Exalted.
- Scarlet kills in Hearthglen and in Stratholme's Scarlet half pay rep with no cap **(assumed for Strat)**.
- Open-world Scarlets (Tirisfal's Scarlet Watch, Tyr's Hand, Northridge) pay a little, **up to Honored**.
- Pale Flame quests across WPL and EPL.
- Stackable Scarlet insignia turn-ins at Sorrow Hill **(assumed)**.
- Rates follow the existing economy: about 150 to 250 a quest, 75 a boss in a linked dungeon.

**Rewards, standard rep style** (the TBC model already in the faction canon): Friendly and Honored sell supplies and
recipes; Revered sells level 60 item level 67 blues; Exalted sells level 60 item level 73 epics at about 250 to 350
gold; about six blues and three epics, themed to the Order but not pigeonholed; recipes including Exalted epic
recipes; a Revered shoulder enchant per role; a tabard.

## The Argent Dawn (its own faction)

- Scourgestone turn-ins (Minion's, Invader's, Corruptor's) at Light's Hope.
- The Argent Dawn Commission, a trinket that lets Scourge kills pay Argent rep.
- Scourge kills in Scholomance and Stratholme's undead half.
- Shoulder enchants of a different flavour from the Pale Flame's, and gear by standing for every spec.

## Dungeons

**Hearthglen (new).** Town and citadel: fight up through the occupied streets of Hearthglen, then Mardenholde Keep.
**Ten or more bosses.** The last is an **Earth-born Grand Crusader**, a transplant zealot Rory once served beside
(pitch: *Grand Crusader Victor Hale*, a former private security contractor who decided the Integration was a
judgment). Rare drop: a Scarlet charger from the last boss.

**Hearthglen's hidden depths (Kyle, 16 Nov 2026, "breaking the rules"; more details to come from him).**
Inside Hearthglen, very well hidden, a chain of three hidden places, each inside the last:
1. a hidden skull layer with three bosses;
2. past it, a hidden Frontier dungeon with three bosses;
3. past that, an **Integration Zone**, a new kind of hidden place at **7.5x health and 8.5x damage**: a crypt
   flooded with bodies, and a single boss. The ???? seller waits past that boss.
How each is found is never written down where Kyle reads it. Hearthglen's layout leaves room for all three from
the first build, and the Integration Zone's multipliers become a new hidden-zone tier in `world/hidden_zones.py`.

**Stratholme, two halves.** The living side (the Scarlet Bastion, Pale Flame rep) and the undead side (the Baron,
Argent rep). Rare drop: the Baron's deathcharger.

**Scholomance, classic and full.** Caer Darrow, the Barovs, Kirtonos, Rattlegore, Ras Frostwhisper, Gandling.

**The Scarlet Monastery, four wings** off the gate in Eastern Tirisfal: Graveyard, Library, Armory, Cathedral.

**Shared rules.**
- No keys. Every dungeon is open.
- Packs of four to five, never lone trash.
- Set pieces (our T0 style, with the 2, 4, 6 and 8 piece bonuses) spread across Scholomance, both Stratholme halves
  and Hearthglen, with tokens so every spec is covered.
- Rare recipes and plans from Scholomance and Stratholme, classic style.
- All loot checked against the 97 specs of the 30 classes.
- Dungeon quests are given in town, not by someone parked at the door.

## Quests and the open world

- **About forty quests a map**, so about 160 across the four, with chains across maps and into the dungeons, and
  pointers out to other continents.
- **The cauldrons** (Felstone, Dalson's Tears, Gahrron's Withering, the Writhing Haunt) are the Bulwark
  apothecaries' quests: the Forsaken want samples to make their own plague.
- **One field boss per map** plus named rares in subzone tables only.
- Kill quests use real places and directions, written to the current voice rules (whole sentences, contractions, no
  dashes, no counts as the whole order).

## Art (prompt sheets, the way Felwood and Stonetalon were done)

- Ground and props per map: plagued grass, ash, cauldrons, ziggurats, Scarlet banners, ruins.
- Buildings: the Bulwark, Light's Hope, Sorrow Hill keep, Crown Guard, Hearthglen, Andorhal's ruins.
- Dungeon interiors: the four Monastery wings, Scholomance, both halves of Stratholme, Hearthglen.
- Creatures and bosses: Scourge, Scarlets, the Pale Flame, the Cult of the Damned, plague beasts.

## Build order (region first)

1. **South WPL, the Bulwark and Sorrow Hill** as a playable slice: map, paint, creatures, gathering under the hard
   rule, the Pale Flame faction and its first chain, the cauldron quests, the Tirisfal road.
2. **North WPL and Hearthglen.**
3. **Scholomance.**
4. **West and East EPL, Light's Hope and Crown Guard**, the Argent Dawn faction.
5. **Stratholme**, both halves.
6. **The Scarlet Monastery**, four wings.
7. The Alterac foothills road and the Undercity door chain slot in with the maps they open into.

Art prompt sheets go to Kyle up front so the art can arrive while the maps are built.

## Assumptions to confirm

- Stratholme's Scarlet half pays Pale Flame rep with no cap.
- Insignia turn-ins exist and are repeatable.
- The four-map level split above.
- The leader, the recruits and the Grand Crusader are pitches.
