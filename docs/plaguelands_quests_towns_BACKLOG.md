# Plaguelands quests and towns: backlog (16 Nov 2026)

Kyle, after playing the Plaguelands: "Right now they dont even talk to you...no lore no talking....the people are read
as total disconnected third character... All the plaguelands quests are like this." And: "we need to 100% fix up the
quests in Plaguelands." Stonetalon Peak has the same problem.

## Quest writing
**Done** in 29fd4a4 for the Plaguelands. Stonetalon's pass is still open.
- Every Plaguelands quest is written about the giver ("Clerk Wendel Ashby kept Hearthglen's books... He wants a
  copy"), not by them. Rewrite every one in the giver's own voice, the way Emerald Sanctuary and Onyxhollow are
  written: who they are and why it matters to them, in their words; what they need; where to go and what you'll
  meet; and what they'll give you or do with it.
- Model: Emerald Sanctuary (Dr. Nkechi Adeyemi, "Bandages and Bitterroot") and Onyxhollow (Geomancer Vigdis
  Stonesong, the Last Water).
- Same pass for Stonetalon Peak afterwards (Spiritwalker Tohana's "Rot in the Heartwood" reads the same way).
- Audit every Plaguelands quest, including the cave and dungeon quests added on 16 Nov, plus their turn-in text.

## Towns
**Done** in 29fd4a4.
- The Bulwark and The Pale Watch become their own town maps, stand-alone, like every other town in the game.
- Remove Sorrow Hill; its people move into the Bulwark. One flight path in the zone, not two.
- Crown Guard moves into Light's Hope Chapel, which becomes its own town map.

## Vendors at the wrong level
Kyle: "ensure that vendors sell at the appropriate level! Looking at a vendor sell lvl 1 food in a lvl 55 zone is fun
and all, but this keeps happening."
- tools/qa_vendor_stock.py already checks this and passes, so it has a hole. Find out why it missed this vendor (a
  zone missing from data/zones/zone_levels.json, food or drink not covered, or stock added at runtime), fix the
  stock across every zone, and make the check fail on exactly this case so it can't come back.

**Done, 17 Nov 2026 morning.** Why it kept happening:
- `qa_vendor_stock.py` printed 256 under-levelled listings on 92 vendors every run, and then returned 0.
- Its zone match skipped 21 vendors in "the_" zones.

The fix:
- `tools/fix_vendor_levels.py` puts food, drink, meals, potions, arrows, bolts and shot on tier chains. 183 listings
  on 56 vendors were brought up to the best tiers in reach of their zone, for example Light's Hope's quartermaster:
  Bread and Cheese -> High Table Feast, Waterskin -> Starfall Wine.
- The QA now fails on any chain item more than 8 levels under the zone, and on any vendor whose zone has no band. A
  bread roll put back in a level-56 shop fails it.
- Sun Rock Retreat had no band; it's 26-29, the value `build_zone_levels.py` derives.
- Don't re-run `build_zone_levels.py` blind: today it would give the Bulwark 7-54 and Northern Barrens 12-33. Hand
  edits in zone_levels.json are holding those, so the builder has a bug to look at.

## Vendor recipe tooltips
Kyle: "when buying recipes it should say what it does. Also what it requires! Like not a level but a 'Jewelcrafting -
200'". A recipe, design or formula on a vendor shows "Requires level 1". It should show what it makes (the item's
card or the consumable's effect) and "Requires Jewelcrafting (200)".
**Done** in b5e7da3 (`ui/recipe_tooltip.py`, shared by the bags and the vendor).

## Booty Bay (small)
**Done** in b5e7da3.
- The top-left way in and out to Stranglethorn is blocked.
- Only a tiny path north of the flight master.
- The top (north) of the three docks is blocked by a building where it meets the outer wharf.

## Hammerfall and Arathi
Kyle: "why does hammerfall have like 3 quests only? ... Theyre also written in weird AI tics. Did hammerfall get nuked
and all the NPCs died?" The data has 11 quests given in Hammerfall, 16 in West Arathi, 6 central and 5 east, so
either most aren't reaching the player (chain gates, levels, missing NPCs) or Kyle is seeing a different set. Find
out which, give Arathi a proper quest count from its town, and rewrite the text in people's own voices (the
Emerald Sanctuary model).

**Done, 17 Nov 2026** (`tools/build_arathi_voice.py`, text in `tools/arathi_quest_voice.py`). Why Kyle saw about
three:
- Hammerfall had 5 givers and 10 quests. Two of those were deep in the Drywhisker chain and the rest were at 34-36.
- 13 of the hold's 18 people gave nothing.

Now:
- Hammerfall gives 20. Ten are new, from 8 people who had none: the Overlord, Sergeant Mok, Stablemaster Rukka,
  Innkeeper Grettha, Quartermaster Urga, Weaponsmith Krol, Wind Rider Master Dreka, Trader Molg and Reagent-Keeper
  Shelna. Most are at 33.
- 13 quests are open the moment you walk in.
- Central Arathi is 22 of 26 from a town.
- All 56 Arathi quests are rewritten in their givers' voices: first person, contractions, no "it is not X, it is Y",
  no fragments. Every kill is named and every place has a direction.
- Six objectives that didn't match their own text are fixed:
  - Four Circles stands you in the circles.
  - The Answer counts the west circle and leads on to Boulderfist Hall.
  - Ask Them First sends you to the hall's mouth; it used to complete on accept.
  - Gallowmast goes to Gallowmast.
  - The Harbinger's charms are in Witherbark Hollow.
  - One wreck was on a rock tile.
- `build_arathi_quests.py` must not be re-run (it would drop all of this); its docstring says so.

## NPCs into towns
Kyle: "move everyone from outside tarren mill inside....oh fuck, did we not do that great movement of NPCs out of
town INTO towns". It's backlog [69]+[74] (claude/playtest_backlog_2026_11_10.md): done for the Barrens and
Hillsbrad's quest givers on 13 Nov (61 quests moved to town givers, `qa_quest_hubs`), not for every zone and not for
non-quest NPCs. Tarren Mill first: everyone standing outside the town moves inside it. Then the same sweep across
every zone, with the check extended to every NPC whose role belongs in a town.
- Kyle: "around 30% of quest givers are outside of towns and 70% are inside (rough numbers)". The rule for every
  zone, checked per zone by `qa_quest_hubs` (today it only covers the Barrens and Hillsbrad).

**Tarren Mill done, 17 Nov 2026** (0d88dce): the 11 people on the grounds outside the gate now stand inside the
town. The sweep across every other zone is next.

## Hidden sellers: cheaper, and their stock rotates (Kyle, 17 Nov 2026)
"make like 25% cheaper for weapon and armor from these vendors... we have rotating stock in these secret
vendors....like they have 6 or 7 blue items but only 3 to 4 are at once. They can follow 12 hour rotations with the
time passing like how the AH passes."

**Done, 17 Nov 2026.**
- Every one-of-a-kind piece costs 75% of what it did. The old price is kept as `price_full`.
- 49 hidden sellers now carry a pool of seven pieces each: 193 new pieces, named from the seller's own pieces and
  name.
  - They're made by LootGenerator and put on the item curve.
  - They're spread over all four armour classes, every stat template, and the weapon types the sellers never had.
- The shelf shows four pieces at a time and turns over every twelve market hours (the auction house's clock).
  - The shop says when new stock comes.
  - The same window always shows the same four.
  - Within a week every piece comes round.
  - Recipes and supplies never rotate, and reputation quartermasters never rotate.
- Code: `world/vendor_rotation.py`, `tools/build_secret_rotation.py`, `tools/qa_secret_rotation.py`.
- The Dry Deep recut had opened two hidden caches to the cave. They're in fresh rock again (`qa_secrets` green).
  Locations not described.

## Southshore
Kyle: "lets just make southshore an actual town at this point." Its own town map, built like the others, with the
humans backlog [72] asked for.

**Done, 17 Nov 2026** (`tools/handbuilt_southshore.py`, 96x80, baked by `tools/bake_hillsbrad.py southshore`):
- One street from the north gate down through the square to the strand and out along the quay to the ship. The
  chapel, townhouses, granary, barn and Holloway's plots are to the west. The inn, militia hall, stable, smithy and
  trading post are to the east. The boathouse, fishery and watchtower are on the beach.
- Its nine people moved in (`tools/sync_hillsbrad_npcs.py` now covers four maps). The town's stance is unchanged:
  no bed, no bind, no flight and no trainer for the Horde. Beatrix Rowe is now a vendor who sells food through the
  inn's window.
- On Western Hillsbrad, the trunk road ends at Southshore's gatehouse (94,128). A hedge is a wall round the old
  town ground, and the rooftops, quay and ship show behind it. The coast road and the orchard lane now leave the
  trunk road outside the gate. The marines and Bosun Harlow stay on the approaches.
- "Scouting the dock" sends you through the gate to the quay; Henk's Harlow line says where Harlow works now.
- `ek_gatehouse` counts as entrance art (world/portal_art.py).
- QA: portals, NPC tiles and props, building and prop overlap, vendors and stock, quest hubs, creature and zone
  reachability, encounters, secrets, exits framed and flight paths all pass. Two failures were already there
  before this change: verify_portals' 34 one-way dungeon links, and qa_hillsbrad_quests (arw_through_the_wall's
  giver, tarren_mill_flight_master, has no spot in Tarren Mill's layout).

## Timbermaw: the tunnel now, the Hold with Azshara (Kyle, 17 Nov 2026)
Kyle: "add timbermaw hold? We have the art for it and we can add the reputation", then "So timbermaw is a tunnel bro!",
"It'll eventually go to winterspring and moonglade", "Timbermaw hold will be in Azshara!" and "Make the tunnel massive
bro!". He picked "Tunnel now, Hold later".

**Done:**
- **The Timbermaw Tunnel** (`tools/handbuilt_timbermaw_tunnel.py`, 180x200, painted by
  `tools/bake_ashenvale_dungeons.py timbermaw_tunnel`): a long climb from North Felwood's Timbermaw Gate (94,4).
  It has ten halls: the South Mouth, the Lower Galleries, the Storeroom, the Waystation, Selva's Spring (a lake),
  the Honey Galleries (a loop back up), the Root Hall and the Elders' Rest. The Moonglade passage and the
  Winterspring passage are shut by rockfalls. Their door spots are recorded in LATER_DOORS. No mobs.
- **Nine Timbermaw** live along it (`tools/build_timbermaw_hold.py`, idempotent): Elder Haldor Mossmane, Quartermaster
  Bruna Honeyhide, Provisioner Orbo, Featherkeeper Imna, Pathfinder Grosk, Windtalker Selva Brightpelt,
  Honeykeeper Tova, and Wardens Bramblecoat and Durn Rockpelt. Gatewarden Thornclaw's line says the tunnel's open.
- **The Timbermaw Hold reputation:**
  - Deadwood kills in Felpaw Village pay 10 each, and Grimpelt 50, up to Honored. They moved off the Emerald
    Reclamation's list, because a creature pays one faction.
  - Deadwood Headdress Feathers drop from every Deadwood, and Imna takes them ten at a time for 100, repeatable.
  - The tunnel's quests pay 325 each. Barrowpaw's Felpaw chain at Talonbranch now pays the Timbermaw too (To
    Timbermaw Hold, Felpaw Village, The Totems of Felpaw), and Chieftain Grimpelt pays 500. Questing alone reaches
    Friendly; past that it's feathers and Deadwood kills.
- **Five quests and the feather turn-in**, none repeating Barrowpaw's chain:
  - The Tunnel Opens: Bramblecoat lets you in after "To Timbermaw Hold", so Thornclaw's promise is kept.
  - The Shamans Who Turned.
  - What the Water Carries: Bloodvenom samples for Selva's spring.
  - Bears at the Mouth.
  - Seeds of the Fel.
- The tunnel is a town map like Onyxhollow, not a cave, so nothing spawns in it and you can ride the climb.
- **The shelf, TBC-style:**
  - Friendly: supplies.
  - Honored and revered: leatherworking and woodworking patterns, moved off Tarren Mill's bowyer and the
    Steamwheedle chandler.
  - Revered: six ilvl 67 blues across every role.
  - Exalted: three ilvl 73 epics (Maul of the Elders, Staff of the Hold, Brightpelt's Spirit Totem) and two epic
    recipes (Timbermaw Warhide, Honeywood Longbow).

**Next, Kyle's call: Azshara, 52-59, "with a frontier twist"**, home to Timbermaw Hold, the town.

## Map icon for reputation quartermasters (Kyle, 17 Nov 2026)
"Let's have a map icon for Rep Vendors? So they're easy to find." **Done:** a lime banner on the world map, in
place of the shop's coin, on every quartermaster that sells for standing. There are 13 of them, including the
Timbermaw trader and the new Timbermaw quartermaster. A secret faction's seller is never marked. It's in the map
legend. Built with `world/faction_manager.quartermaster_ids()` and checked by `tools/qa_map_rep_icons.py`.

## Mounts
Kyle: "for mounts we need a way to select the mount - as when we buy them it just replaces the old mount with the
new ones". Keep every mount you've bought (saved with the character), and a picker to choose which one you ride.

**Done, 17 Nov 2026.** Every mount bought was already kept (TravelManager.owned_mounts, saved); what was missing was a
way to choose. Clicking the Mount button opens a picker when you own more than one: every mount, the riding skill it
needs, its blurb, the one R summons marked, and Dismount while riding. Picking rides it and makes it R's. In a cave
the pick is kept and you stay on foot. Speed comes from your riding skill, not the animal, so the choice is how you
look. `tools/qa_mount_picker.py`.

## Plaguelands art (sheets 4 to 8, landed 16 Nov)
Sliced: the dungeon props, the dungeon floors, the creatures, the Scarlet and Pale Flame roster and the dungeon
bosses. They replace the borrowed art on the zone's creatures and on its people (Rory and the Pale Flame, the
Bulwark's Forsaken, the Argent Dawn), and they are what Scholomance, Stratholme and Hearthglen were waiting on to be
wired (rosters, kits, loot, floors, doors, one-way exits). Crown Guard Camp folds into Light's Hope.

## Sheet 4 recruits: sixteen more companions (art landed 17 Nov 2026)
- **Done, 17 Nov 2026.** Kyle: "They can be spread out as per our previous discussions." The roster in
  docs/recruit_art_prompts_sheet4.md, with the Plaguelands moves since it was written: Sorrow Hill is gone, so Bruno
  and Joaquín stand in the Bulwark; Crown Guard folded into Light's Hope, so Isla is there; Graham went to the Pale
  Watch and Dale to the Eastern Plaguelands so no town holds three.
- Art: tools/asset_pipeline/slice_recruit_sheet4.py cut both 4x4 sheets into a sprite and a portrait each.
- Who they are: tools/writing/sheet4_recruits.py. Records, kits and placement: tools/build_sheet4_recruits.py.
- Each one has one named passive and three abilities quoting their own story, built only from mechanics the engine
  already runs. Twenty-five of them rank to 60 by tools/rank_kit_abilities.py's rule. Five rank-1 sizes were held so
  the kit medians did not move, which leaves every older recruit's ranks exactly where they were.
- QA changes: qa_recruit_placement's ceiling is now 58, and qa_recruit_talents catches a recruit up only as far as
  level 60 (it was asking a level-58 reaper to hold 74 levels of points).
- Open: audit_recruit_combat still exits 1 on Ryan's Health Funnel healing his Felhunter. That was there before
  this work, and none of the sixteen fail it.

## Crafting: recipes are bought at the trainer (playtest and Kyle, 17 Nov 2026)
- **Done.** Playtest: Leatherworking at skill 1 with 107 Scrap Leather said "Missing materials" on the first three
  recipes. The trainer only handed recipes over when a trade was learned or a tier trained, and that save had
  learned the trade when the first recipes needed a skill it didn't have yet, so it knew none.
- Kyle: "You need to go to the trainer and it costs money to learn!" and "Crafting is an investment and costs
  money to learn". Now no recipe is ever free. Not on learning a trade, not on training a tier, not on a skill-up.
  A trainer lists every recipe your skill has reached, each with a price, plus "Learn all you can afford".
- Price: 10c + skill squared / 5, so 10c at 0, 5s at 50, 45s at 150, 1g80 at 300. A recipe can set its own
  "train_cost". A whole trade's recipes come to about 40-100g on top of the 77g of tier fees.
- Every trade now refuses a recipe you don't know (only Blacksmithing and Leatherworking did). The message says
  where to get it, and the list marks it "Visit trainer" or "Not learned".
- Two Jewelcrafting jade designs had no seller. They are now sold beside the rest of the jade family.
- Test: tools/qa_trainer_recipes_follow_skill.py, covering all ten trades.

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

**Done, 17 Nov 2026** (`tools/build_secrets_pass3.py`, additive and idempotent; `tools/build_secrets.py` is not
re-run). Counts only, never places:
- 28 of the 38 behind-a-building sellers now stand in real hidden ground: a hollow inside the rock, cliff or trees
  round their map, reached through a way in that still looks solid. 10 stay behind their buildings, Razor Hill's
  among them.
- The three maps with none now have two each, six caches in all.
- Six long runs, each at least 50 tiles long, with a cache partway along.
- 402 secrets in all. `qa_secrets` is green: every seller and cache can be walked to, every way in keeps its rock,
  the map keeps lying, and nothing is drawn until you're in there.

## The Gilded Vale and the Emberwild (Kyle, 17 Nov 2026; names only, never where)
Kyle, on the Azshara autumn trees: "these trees are gorgeous. We will need to make an autumn-style skull-zone and
frontier zone elsewhere in the world with them. Dunno where but I'd like two zones.... The Gilded Vale (skull) → The
Emberwild (Frontier)".
- **The Gilded Vale**, a skull zone: a new hidden open map, entered by a secret door from an ordinary zone, the
  parent's level band, 2.5x HP and damage, loot +4-5, one resident with 3-4 quests (one elite), no hub.
- **The Emberwild**, its frontier: entered from inside the Gilded Vale, open 3.5x / 3.5x, loot +8, every boss with
  an epic, a resident with a chain and a secret seller. The most care of anything (playbook section 8).
- Both painted with the Azshara autumn set (ground sheet 1, the trees and props on sheet 2). Not Azshara itself:
  "elsewhere in the world". The choice of parent zone is made blind and never written here or told to Kyle.
- Next after the Azshara slice is pushed.

## Grovekeeper healing (backlogged by Kyle, 17 Nov 2026)
Grovekeeper is Primalist's melee healer, held to 75% of a full healer's output. To reach that in the heal sim, its
hidden spec aura would need to be about 1.5x, but the aura is capped lower, so it falls short of its own target. The
fix is in its kit (more or bigger heals, or Hammer of Life's splash), not the cap. Kyle: "backlog the groovekeeper".

## Class buffs (overview measured 16 Nov 2026)
**Mostly done, 16 Nov 2026 night** (docs/support_pass.md):
- Every flat stat on a class buff or debuff is now sized by level, and 65 buffs and debuffs have a rank every ten
  levels.
- Tooltips drop descriptions that list stale numbers, and long buffs no longer say "for N turns".
- Flash Heal, Greater Heal, Lesser Healing Wave, Chain Heal, the revives and the new cleanses are in their healing
  tabs.
- Resistance buffs are on the 0-60 scale: Grounding Totem gives 40, not 710; the resist totems 22, not 166; Mage
  Armor 18, not 74.
- **Done, 17 Nov 2026 morning** (Kyle: "Each gets one", "Real mp5, sized by level"):
  - The eight classes got a long party buff.
  - mp5 is sized by level.
  - Wisdom, Mana Spring and Water Shield give mp5.
  - Every healer class can give its party mana.
  - See "Long party buffs and mp5" in docs/support_pass.md.
- **Done, 17 Nov 2026 afternoon** (Kyle: "Make the classes get a 30min buff"): Bloodmage, Guardian, Knight of
  Xoroth, Necromancer and Ranger got one too. Every class now has a thirty-minute party buff.

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
tools/qa_bench_cap.py. The Party Buffs list now scrolls inside its box, above the action buttons
(tools/qa_party_buffs_scroll.py). Done.

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
**Done, 16 Nov 2026 night.** It's a map of its own, `tools/handbuilt_fourth_peg.py` (96x72), with its gate on
the Abyssal Sands where the camp stood, at (140, 22).
- **Inside:** all eight survey people moved in. Marda's inn has a mailbox. There's the forge, the depot, the
  brewer, Vizzi's winch yard, the survey office and Hask's shed. The peg is on the paved square.
- **New:** a wyvern roost with Wyvern-Keeper Rixa Dunlow (the flight node `fourth_peg`) and Gate-Warden Pik Tallow.
- **On the Sands:** the old camp's ground is "Fourth Peg Flat", still safe, with the gate, a sign and the crew's
  old marker.
- **Wiring:** baked by `tools/bake_tanaris_places.py fourth_peg`, with NPCs from `tools/sync_abyssal_npcs.py`.

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

**Done, 17 Nov 2026 morning.** `tools/handbuilt_dry_deep.py` went from 10 rooms and 12 tunnels to 17 rooms, 23
tunnels and 3 dead-end side passages:
- Seven new places on the outside ring: the Salt Galleries, the Brine Seep, the Whispering Fault, the Fossil Shelf,
  the Brood Shelf, the Black Pool and the Glass Seam.
- Four new loops round the edge that never touch the Drained Sea. `verify()` now checks that every room except the
  three dead ends has two ways out, and that the outer ring still joins up with the Sea taken out.
- Three optional bosses, all off the chain's route: the Salt Widow (46, a caster with a curse and a wail), the
  Coil of the Old Sea (47, a stun and a bleed) and the Mother of Crawlers (46, she calls Limestone Crawlers).
  Each has its own four-piece loot pool (`build_dry_deep_content.py`, loot_audit passes over all five pools) and
  its own quest from someone in Fourth Peg (Sepp, Gorra and Tobbit, the three with the fewest).
- Damage is calibrated for all three (field_boss).
- Four more chests, seven in all.
- Both builders now only ADD. The first two bosses' kits and the first four quests' rewards had been through later
  passes, so a re-run leaves them alone (`--rewrite` to force).
- QA: reachability, encounters, portals, boss turns, summons, quest hubs, givers, lore and voice are all green.
  audit_loot's ore/wood tier warning was already failing on main.

## Kyle, 16 Nov 2026 21:34: next up once the Plaguelands are done
"do the backlog of support skills. Full audit to put them closer to where they should be and 100% we need to fix the
healing end game.....we need an actual formula and do it right.... a spot heal from a non-spec'd character shouldn't
heal 80% tank HP and like 200% boss damage...."

This makes the heal pass first in line, and it has to be an actual formula, not more trimming.
- Write the formula down first: base heal by level, what spell power adds, what spec and talents add, and what gear
  adds.
- Target a naked, unspecced spot heal at about 20-25% of a same-level tank's HP, and well under one boss hit.
- Then audit every support skill (heals, shields, HoTs, buffs, cleanses) against that formula.
