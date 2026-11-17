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
