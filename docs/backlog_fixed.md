# Backlog: what's fixed (look here before fixing anything)

Kyle, 18 Nov 2026: "Update fixed things so they don't get fixed 50 times." Open work is `docs/backlog_nov17_onwards.md`.
When something on it is fixed, or turns out to be fixed already, it comes off that list and goes here in the same
commit: what it was, what fixed it, and the check that keeps it fixed. If an item is listed here, it's done; if it
seems broken again, the guard named beside it is the first place to look.

Secrets stay counts and names only here too.

## 19 Nov 2026

| Was | Fixed by | Guarded by |
|---|---|---|
| Recruit bonds were parked beyond the pilot three | Waves 2 and 3: every recruit has a bond record, banter and relationships | `qa_recruit_bonds`, `qa_relationships` |
| Sworn skills weren't built | Wave 4: 98 Sworn skills, one per recruit bar Asher | `qa_sworn_skills` |
| No way to call back a recruit who'd gone home | The mailbox's Friends tab: write to anyone you've been out with, they answer by bond and personality and meet you at a town you pick (`world/recruit_mail.py`) | `qa_recruit_mail` |

## 18 Nov 2026

**Standing QA failures** (commit 17b165b)

| Was | Fixed by | Guarded by |
|---|---|---|
| qa_teleport_menu flagged the U key | U is the Collection's key now; the check asks that U opens neither Unstuck nor Teleport | `qa_teleport_menu` |
| qa_world_view_clipped found 929 pixels in the badge strip | It was the experience rate switch, which belongs there; the empty region stops short of it | `qa_world_view_clipped` |
| Timbermaw's Bloodvenom Sample and Fel-Tainted Seed Pouch dropped at 60% for quests wanting 6 | 0.75, in `tools/build_timbermaw_hold.py` and the data | `qa_hunting_and_quest_drops` |
| Ashenvale's Vigil Lights read as promising gear ("take one") | "take a light" | `audit_quest_rewards` |
| Two world epics weaker than blues | Thunderhoof (a mace with only block rating) and Breastplate of the Unbowed (no stamina) got real stat lines; the QA now prices stats on the item curve, which found 8 more hand-authored epics under a blue, put on the curve with their mix kept | `qa_epic_superiority` |

**Small backlog items**

| Was | Fixed by | Guarded by |
|---|---|---|
| No guard against ratings that read as percents | 121 ratings were fractional or under 5 (curve fits had scaled them); rounded, floor 5. `fit_to_curve` keeps ratings whole and at 5 or more from now on | `qa_rating_stats` (`--fix` rounds) |
| An Agility rogue reached the 50% dodge plus parry cap | Agility per 1% dodge at 60 is 14 (was 10); Enveloping Shadows 1% a rank (was 2%). A rogue with every dodge talent: 38% at 40, 41% at 60, still the dodgiest class | `audit_avoidance_and_crit` (a report) |
| Combat log never said when a rune changed a hit's school | " (as Frost)" on the hit line (`Monster.landed_as`, `_landed_note` in `combat/abilities.py`) | |
| Old saves: quest-reward gear kept a 0 sell price | A saved 0 on a quest reward (its `unique_` id) loads as "price me" (`entities/item._saved_price`); recruit kits keep 0 | |
| Crafted intermediates (kits, scopes, pages, sticks, fibre) sold for less than their inputs | `tools/price_intermediates.py`: inputs' worth per one made x 1.10, only ever raised, never a money loop. 101 repriced | `qa_material_prices` check 6 |
| Ragefire Chasm's NPC tile at (100,100) in rock | Already gone by 14 Nov (the cave rebuild); found still listed 18 Nov | `qa_npc_tiles` |
| verify_portals: 19 one-way links out of hidden maps | Hidden maps are entered by secret doors, so their only portal is the way out, by design; `secret_entered()` accepts them without listing any. The other 11 (dungeon fast exits and the boat's loop) are on `ONE_WAY_OK` | `verify_portals` |
| Tarren Mill's flight master had no spot on the town map | Wind-Rider Ghulrak stands under the bat roost | `qa_hillsbrad_quests` |
| Quest directions: 8 WRONG and 32 SILENT (the backlog said 22) | WRONG: three were the audit reading "West Azshara" and "North Felwood" as directions (it skips place names now); five got a direction from the giver (Moonglade, Deadwind, Azshara). SILENT: 29 got one, two fragments rewritten on the way. The 3 left are inside hidden maps and stay on the backlog | `audit_quest_directions --all` (0 WRONG) |
| Battle-screen icons (Kyle, 15 Nov) | The combat hotbar and extra slots draw each ability's and potion's icon, with the hotkey in the corner: cooldown dark with the turns left, "Form"/"Stance" when it needs another, blue when you can't pay. Hover shows name, reach (new: "Ranged, a row of your choice", "Melee, one enemy in the front row", "One ally"...), cost, cast speed, cooldown and damage range; potions got a hover card. Area spells' tooltips said "all enemies" and now say one row, as they hit. Party buffs and debuffs were already icons with hover text. A tooltip from the last fight no longer stays up over the new one | `qa_hotbar_icons` |
| verify_portals: 21 portal tiles "not walkable" | All 21 were secret doors, and every one works in the game. The check built its maps without laying the secrets, which the game always does when it starts; it lays them now. 447 portals, 0 failures | `verify_portals` (PASS) |
| Crafting had nothing at the heroic or raid level, and trades capped at 300 while level 60's materials need 310-320 | Kyle, 18 Nov: "I'll ALWAYS want crafting to be competitive to raiding/Dungeons". A Master tier (cap 325, level 60, 150g, the Artisan trainers) and 94 Master recipes (every spec of every class can use at least 3): two bolts, blues at 66 (trainer, first rung) and epics at 68 (heroic boss patterns, second rung + a gem) in all six gear trades, on the item curve like heroic drops. The Exalted rep patterns got their real ingredients (second rung); Revered first rung; Honored stays pre-60. Also fixed: one Jewelcrafting rep pattern didn't need the jeweler's kit | `tools/build_master_crafting.py`, `tools/qa_master_crafting.py`, `docs/master_crafting.md` |
| Woodworking's level 50-56 tier needed three level-60 woods (Emberwood, Frostheart, Ebonthorn) that grew on no map, so 25 recipes, 9 intermediates and 3 kits could never be made; Sunheart planks sat above their wood | Kyle, 18 Nov: "Nothing sub 60 should use lvl 60 materials." The three woods joined the pre-60 ladder (245, 268, 275) and now grow beside Moonpetal, Starleaf and Stormoak (27 zone tables, each only where its level fits); Sunheart planks at 300. Names, icons, recipes, vendors and quest rewards unchanged. Level 60's woods are now Voidwood and Dreamwillow | `tools/fix_pre60_woods.py`, `tools/qa_no_level60_materials_below_60.py` (every trade) |
| Heroic mode didn't exist (normal dungeons capped at Revered with no way past it) | Stage 1: Normal or Heroic at every dungeon's door at 60, once per market day, level-60 elites, boss drops rebuilt at 66 (worn at 60), trash and side chests at 63, boss chests at 66, coin and vendor trash x1.5, only Dreamsilk, Chronoweave, Manticore and Chimera from the top tiers, rep past Revered and tabards live. Also fixed: the Revered cap read the display name, and combat passes a key, so it never fired in a real fight | `world/heroic.py`, `tools/qa_heroic.py`, `docs/heroic_design.md` |
| Rep gear sat above the raid it should lead into (Revered 67, Exalted 73) | Kyle's level-60 ladder, 18 Nov: Honored 62, Revered 66, Exalted 68. 147 quartermaster items and the 38 rep patterns' made items refitted at the new level with their stat mix and strength kept (none moved more than 5% off its old ratio); prices kept | `tools/relevel_rep_gear.py` (reports "already on the ladder"), `qa_faction_rewards` |
| Dungeon rep went on to Exalted; no way to pick which faction a dungeon pays | Kyle, 18 Nov: normal dungeons stop at Revered (heroics go on), and 16 faction tabards (Friendly, 1g, own slot) move a heroic's kill rep to the faction you wear. Heroic mode itself is the next item. Their art (sheet T1) landed the same day | `world/faction_manager.award_for_kill`, `tools/build_tabards.py`, `world/tabards.py`, `tools/qa_tabards_and_dungeon_cap.py`, `docs/tabards_design.md` |
| The 18 Nov art drop waited on sheets | 17 sheets landed and sliced the same day: H1 (harvest find, junk, salvage and fishing reins icons), H2 (six fishing mounts, rideable now), H3 (Deadwind's own backgrounds for the pass, Ariden's Watch, the Widows' Nest, the Seep and the Exclusion Zone's three floors), H4 to H7 (fifteen AH mounts), H8 (their reins, the AH forms' charms and nine family charms, which took the forms on the wolf charm from 418 to 204), F1 and F2 (every class form in four facings, drawn on the map), F3 to F5 (18 looks in the Collection), the twelve AH forms, the Woodworking epic scroll, and Mohammed Saleh's sprite and portrait (he was on a stand-in) | `tools/asset_pipeline/slice_mount_sheet.py` (now `--grid` and `--out=`), `slice_collection_icons.py --ids=`, `tools/build_collection.py`, `world/collection.class_form_path`, `tools/qa_shapeshift_art.py` |
| Thunder Clap hit one enemy | Kyle, 18 Nov: "Thunderclap should hit one row that the tank is on." It's a melee area ability now, so it hits the front row, the row facing you | `qa_ability_text` |
| 20 player abilities had no icon, two pairs shared one, Greater Heal and Chain Heal on stand-ins | `tools/fetch_missing_ability_icons.py`: the classic ones got their real WoW icon (Kyle: "you CAN find them online"); the CoA ones a Blizzard icon tinted to their class's colour, read off the class icon (Kyle: "colour tint some other stuff to the theme of the class"). Rejuvenation was wearing Swiftmend's idol. Every class's bar: 0 missing, no shared picture but Bear and Dire Bear Form | `qa_hotbar_icons` |
| Junk and salvage fishing pools had sprites and no catches | Built as harvest finds (`docs/harvest_finds_design.md`), with Kyle's quest starters from gathering: 16 starters and 32 quests, junk and salvage pools, Earth junk, salvage with greens and eight fishing-only gear pieces, six fishing mounts and four titles | `qa_harvest_finds` |
| qa_kit_abilities_batch10: seven recruit heals "not growing" | The abilities were fine. The test's recruits were built bare with about 800 health, less than the heals, so every growing heal hit the cap. They get the Stamina for room now | `qa_kit_abilities_batch10` (38 OK) |
| 3 SILENT quests inside hidden maps | Left silent on purpose: a direction there would say where the map is. Not a bug | `audit_quest_directions --all` (they're the 3 it lists) |
| NPCs into towns, part two: trainers, vendors and innkeepers had no check | Measured: all 174 stand in a town (a map with an innkeeper or a class trainer, or a hub). No moves needed; the guard is new | `qa_service_npcs_in_towns` |
| Ariden's Watch and Nighthaven had no mailbox by the inn (missed when they were built, 18 Nov) | `tools/place_market_npcs.py --apply` put one beside each innkeeper | `qa_auction_house` |
| West, Central and East Azshara, Deadwind West and East had fishing but no pool art picked | Each given its water's pools in `world/fishing_pools.py` (rivers, reeds, the drowned coast, the Black Tarn's plague and swamp, the gorge and the seep's glow) | `qa_fishing_pools` |

## 17 Nov 2026 (moved off the backlog 18 Nov)

| Was | Fixed by |
|---|---|
| Timbermaw Warhide's own icon | RC3's last row |
| Art sheets | The two crafting icon-fix sheets (45 icons), the consumables sheet (28), the three crafted-epic sheets (82), enchanting EN1-EN4 (144), recipe sheets RC2-RC3 |
