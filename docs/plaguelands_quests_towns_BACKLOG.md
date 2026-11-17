# Plaguelands quests and towns: backlog (16 Nov 2026)

Kyle, after playing the Plaguelands: "Right now they dont even talk to you...no lore no talking....the people are read
as total disconnected third character... All the plaguelands quests are like this." And: "we need to 100% fix up the
quests in Plaguelands." Stonetalon Peak has the same problem.

## Quest writing
- Every Plaguelands quest is written about the giver ("Clerk Wendel Ashby kept Hearthglen's books... He wants a
  copy"), not by them. Rewrite every one in the giver's own voice, the way Emerald Sanctuary and Onyxhollow are
  written: who they are and why it matters to them, in their words; what they need; where to go and what you'll
  meet; and what they'll give you or do with it.
- Model: Emerald Sanctuary (Dr. Nkechi Adeyemi, "Bandages and Bitterroot") and Onyxhollow (Geomancer Vigdis
  Stonesong, the Last Water).
- Same pass for Stonetalon Peak afterwards (Spiritwalker Tohana's "Rot in the Heartwood" reads the same way).
- Audit every Plaguelands quest, including the cave and dungeon quests added on 16 Nov, plus their turn-in text.

## Towns
- The Bulwark and The Pale Watch become their own town maps, stand-alone, like every other town in the game.
- Remove Sorrow Hill; its people move into the Bulwark. One flight path in the zone, not two.
- Crown Guard moves into Light's Hope Chapel, which becomes its own town map.

## Vendors at the wrong level
Kyle: "ensure that vendors sell at the appropriate level! Looking at a vendor sell lvl 1 food in a lvl 55 zone is fun
and all, but this keeps happening."
- tools/qa_vendor_stock.py already checks this and passes, so it has a hole. Find out why it missed this vendor (a
  zone missing from data/zones/zone_levels.json, food or drink not covered, or stock added at runtime), fix the
  stock across every zone, and make the check fail on exactly this case so it can't come back.

## Vendor recipe tooltips
Kyle: "when buying recipes it should say what it does. Also what it requires! Like not a level but a 'Jewelcrafting -
200'". A recipe, design or formula on a vendor shows "Requires level 1". It should show what it makes (the item's
card or the consumable's effect) and "Requires Jewelcrafting (200)".

## Booty Bay (small)
- The top-left way in and out to Stranglethorn is blocked.
- Only a tiny path north of the flight master.
- The top (north) of the three docks is blocked by a building where it meets the outer wharf.

## Hammerfall and Arathi
Kyle: "why does hammerfall have like 3 quests only? ... Theyre also written in weird AI tics. Did hammerfall get nuked
and all the NPCs died?" The data has 11 quests given in Hammerfall, 16 in West Arathi, 6 central and 5 east, so
either most aren't reaching the player (chain gates, levels, missing NPCs) or Kyle is seeing a different set. Find
out which, give Arathi a proper quest count from its town, and rewrite the text in people's own voices (the
Emerald Sanctuary model).

## NPCs into towns
Kyle: "move everyone from outside tarren mill inside....oh fuck, did we not do that great movement of NPCs out of
town INTO towns". It's backlog [69]+[74] (claude/playtest_backlog_2026_11_10.md): done for the Barrens and
Hillsbrad's quest givers on 13 Nov (61 quests moved to town givers, `qa_quest_hubs`), not for every zone and not for
non-quest NPCs. Tarren Mill first: everyone standing outside the town moves inside it. Then the same sweep across
every zone, with the check extended to every NPC whose role belongs in a town.
- Kyle: "around 30% of quest givers are outside of towns and 70% are inside (rough numbers)". The rule for every
  zone, checked per zone by `qa_quest_hubs` (today it only covers the Barrens and Hillsbrad).

## Southshore
Kyle: "lets just make southshore an actual town at this point." Its own town map, built like the others, with the
humans backlog [72] asked for.

## Mounts
Kyle: "for mounts we need a way to select the mount - as when we buy them it just replaces the old mount with the
new ones". Keep every mount you've bought (saved with the character), and a picker to choose which one you ride.

## Plaguelands art (sheets 4 to 8, landed 16 Nov)
Sliced: the dungeon props, the dungeon floors, the creatures, the Scarlet and Pale Flame roster and the dungeon
bosses. They replace the borrowed art on the zone's creatures and on its people (Rory and the Pale Flame, the
Bulwark's Forsaken, the Argent Dawn), and they are what Scholomance, Stratholme and Hearthglen were waiting on to be
wired (rosters, kits, loot, floors, doors, one-way exits). Crown Guard Camp folds into Light's Hope.

## Secrets (counts only; never where)
Kyle asked how many secrets are "just vendors behind buildings". 390 secrets on 147 maps; 55 are "behind a
building", and 38 of the 52 hidden sellers are exactly that and nothing else. Every open-world zone from the Valley of
Trials to 60 has secrets; the 22 maps without are dungeons, caves and ships, plus the Scarlet Monastery Grounds, The
Lashings and Jaedenar.
- Move most of the 38 behind-a-building sellers into real hidden ground (a cut path, a gap in a cliff, a cellar
  door), keeping a few behind buildings.
- Give the Scarlet Monastery Grounds, The Lashings and Jaedenar their own; maybe one cache per dungeon.
- Kyle: "dont be afraid to have LONGER secrets....like walking into a hidden thing in the bottom left of a map and
  ending up in top right". Some secrets should be long hidden runs across a whole map, not a pocket beside the road.

## Class buffs (overview measured 16 Nov 2026)
**Mostly done, 16 Nov 2026 night** (docs/support_pass.md):
- Every flat stat on a class buff or debuff is now sized by level, and 65 buffs and debuffs have a rank every ten
  levels.
- Tooltips drop descriptions that list stale numbers, and long buffs no longer say "for N turns".
- Flash Heal, Greater Heal, Lesser Healing Wave, Chain Heal, the revives and the new cleanses are in their healing
  tabs.
- Resistance buffs are on the 0-60 scale: Grounding Totem gives 40, not 710; the resist totems 22, not 166; Mage
  Armor 18, not 74.
- Still open, for Kyle:
  - The eight classes with no long party buff.
  - Mana regeneration buffs (mp5) now that mp5 is real.

Kyle: "a lot of buffs look like this? It says 12 but it gives 29 spell power. Also we need to revamp ALL classes now
that we fixed up spells and have actual mp5 elements in the game... ensure that some things are put properly like
shaman healing spells in wrong tab... the damage and healing is fine, now we need to look at buffs."
- 312 buffs across 30 classes. 118 are long buffs (30 minutes, kept between fights); 95 of those tooltips still say
  "lasts N turns".
- 16 tooltips show the written number, not what the rank gives (Flametongue Rank 8 says +12, gives 29).
- Only 21 buffs touch mana regeneration (mp5 or Spirit). Water Shield is "+4% maximum mana".
- Eight classes have no long buff at all: Felsworn, Hunter, Rogue, Templar, Warlock, Warrior, Witch Doctor, Witch
  Hunter. Only 43 long buffs reach the party.
- Heals with no spec tab: Priest Flash Heal and Greater Heal, Shaman Lesser Healing Wave and Chain Heal (and the
  revives) sit in "Class" instead of their healing spec.
- Magnitudes are off both ways: Strength of Earth Totem Rank 9 gives +3 Strength and Agility at 60 ("lvl 60 and it
  gives 9 agi and 9 str?"), while Grounding Totem Rank 3 gives +500 Magic Resistance ("lmao over 700 magic
  resistance"). The revamp sizes every buff against the level it's learned at, as the damage and healing pass did.

## Endgame heals: ranks slow past 35, power carries the rest (Kyle, 16 Nov 2026)
**Done, 16 Nov 2026 night**, as the healing formula (docs/heal_formula.md) and the support pass
(docs/support_pass.md).

"Lets drop heals down more, i think we should have things past 35 to slow down A LOT in terms of ranks but start to
need spell power and healing power....and talents." Parked for after the Plaguelands ("keep these as backlog and finish
the plaguelands").
- In now: heal_trim (heal ranks learned 30->40 lose up to 15%, mana cost with them), bosses from 30 hit up to 25%
  harder by 50 (endgame_boss row), stuns diminish (tools/qa_stun_diminishing.py).
- To do: flatten heal rank growth past 35 (a level-60 rank well under today's), and raise the healing-power share of
  those ranks so a geared, specced healer heals what today's naked one does. Decide whether damage ranks past 35 do the
  same with spell/attack power. Measure heal / geared tank HP at 35-60 naked and geared (healsim), then
  tools/sim_difficulty.py with 5, 3 and 2.
- Healing talents should be worth taking: check the Restoration/Holy trees give real throughput at 60.

## The bench has no limit, and the party screen overflows (Kyle, 16 Nov 2026)
**Bench capped at two** (Kyle: "I want a hard cap of TWO benched characters"). That's on main (321bb66), with
tools/qa_bench_cap.py. The party-buffs list overflowing is still open.

"no limit to how many people i can bench??? Lol" (screenshot: Bench (9), the list running off the bottom, the Party
Buffs list drawn under the action buttons, the footer hint over the last bench row).
- Decide: cap the bench (and what happens to the recruit you'd push past it), or keep it open and make it scroll.
- Either way: the bench list scrolls inside its box, the Party Buffs tab scrolls (or pages) above the buttons, and
  the footer hint never sits on a row. A QA that fills the bench past what fits and checks nothing overlaps.

## Eat and Drink: see the buff, pick the food (Kyle, 16 Nov 2026)
**Done, 16 Nov 2026 night**:
- Clicking Eat or Drink opens a picker, and a pick is remembered for F and Q.
- Running food, drink and elixir buffs show as chips with time left. Hover one for details.
- tools/qa_food_picker.py checks it.

"we need to have a way to see our food buff. Also a way to select food. these should open menu to select food
options...." (screenshot: the overworld's "Eat (F): 0" and "Drink (Q): 0" buttons).
- Clicking Eat or Drink opens a small picker of what's in the bags (icon, name, what it gives, how many), and the one
  picked is remembered as the default for F / Q.
- The food and drink buffs that are running show on the overworld (icon, what it gives, time left), the way the
  party screen's buff tab does; hover for the full line.
- A QA: with three foods in the bags, the picker lists all three and F eats the chosen one; the buff shows after.

## Fourth Peg as a real town (Kyle, 16 Nov 2026)
"Lets make Fourth Peg an ACTUAL town. i feel that'd solve a lot of whats ugly in Abyssal Sands."
- Its own map off Abyssal Sands, the way the Plaguelands' towns went (docs/plaguelands_towns_plan.md): its people
  moved in, one inn and one flight point, the camp's ground on Abyssal Sands given back to the zone.
- Then look again at what was ugly round it once the camp's gone.

## The Dry Deep: more tunnels, more places, optional bosses round the edge (Kyle, 16 Nov 2026)
"Dry deep is a cool concept, but i think we need more tunnels and zones and maybe some optional bosses around the
outside." (map screenshot: the Drained Sea in the middle, ten "Under the ..." rooms round it, one way through.)
- More tunnels: loops between the outer rooms, so it isn't a hub with spokes; a few dead-end side passages.
- More named places on the outside ring, and two or three optional bosses out there (off the main route), each with
  its own loot and a reason to go.
- Re-check reachability, packs and chests after the recut.

## Kyle, 16 Nov 2026 21:34: next up once the Plaguelands are done
"do the backlog of support skills. Full audit to put them closer to where they should be and 100% we need to fix the
healing end game.....we need an actual formula and do it right.... a spot heal from a non-spec'd character shouldn't
heal 80% tank HP and like 200% boss damage...."

This makes the heal pass first in line, and it has to be an actual formula, not more trimming.
- Write the formula down first: base heal by level, what spell power adds, what spec and talents add, and what gear
  adds.
- Target a naked, unspecced spot heal at about 20-25% of a same-level tank's HP, and well under one boss hit.
- Then audit every support skill (heals, shields, HoTs, buffs, cleanses) against that formula.
