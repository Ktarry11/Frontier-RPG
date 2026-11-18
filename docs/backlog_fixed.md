# Backlog: what's fixed (look here before fixing anything)

Kyle, 18 Nov 2026: "Update fixed things so they don't get fixed 50 times." Open work is `docs/backlog_nov17_onwards.md`.
When something on it is fixed, or turns out to be fixed already, it comes off that list and goes here in the same
commit: what it was, what fixed it, and the check that keeps it fixed. If an item is listed here, it's done; if it
seems broken again, the guard named beside it is the first place to look.

Secrets stay counts and names only here too.

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
| Thunder Clap hit one enemy | Kyle, 18 Nov: "Thunderclap should hit one row that the tank is on." It's a melee area ability now, so it hits the front row, the row facing you | `qa_ability_text` |
| 20 player abilities had no icon, two pairs shared one, Greater Heal and Chain Heal on stand-ins | `tools/fetch_missing_ability_icons.py`: the classic ones got their real WoW icon (Kyle: "you CAN find them online"); the CoA ones a Blizzard icon tinted to their class's colour, read off the class icon (Kyle: "colour tint some other stuff to the theme of the class"). Rejuvenation was wearing Swiftmend's idol. Every class's bar: 0 missing, no shared picture but Bear and Dire Bear Form | `qa_hotbar_icons` |
