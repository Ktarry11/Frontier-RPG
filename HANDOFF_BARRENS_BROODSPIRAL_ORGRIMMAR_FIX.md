# Session Handoff — Barrens Expansion, Broodspiral Dungeon, Orgrimmar NPC Fix

**Date**: September 11-12, 2026
**Status**: ✅ All work verified end-to-end through real game code (spawn tests, flood-fill reachability, sprite resolution, quest cross-references) — not just "looks right on paper"

---

## Summary

This session covered three major pieces of work:

1. **NPC art replacement** (early session) — Orc/Troll/Elf/Goblin/Human redone with new AI-generated art, Forsaken/Tauren/Dwarf/Gnome added as new races, Skeleton/Zombie retired
2. **Full Barrens expansion** — Northern, Central, and Southern Barrens built out from mostly-skeleton zones into fully realized content: 22 subzones total, ~35 new creatures, a home-brew 4-boss dungeon, 50 quests
3. **Orgrimmar NPC bug fix** (end of session) — found and fixed why NPCs "weren't showing up" in Orgrimmar

---

## 1. NPC Art Replacement

- Cropped 10 AI-generated contact sheets (247 individual character sprites) into clean, transparent PNGs — see the crop pipeline work if extending this further; every sheet needed manual digit-ghost/neighbor-bleed cleanup after automated cropping
- Replaced Orc, Troll, Elf (Blood+Night), Goblin, Human folders entirely in `assets/npcs/`
- Added Forsaken (replaces Skeleton+Zombie as the one real Undead race), Tauren, Dwarf, Gnome
- `world/race_registry.py` fully rewritten — new `RACE_OPTIONS`, updated `ZONE_POPULATION_MIX`
- **Gotcha discovered**: 15 NPCs/vendors had hardcoded `"race": "skeleton"`/`"race": "zombie"` in JSON data that would've silently rendered as blank squares after the race deletion — all remapped to `forsaken`
- Elixir/food consumable system also got a real overhaul this session: `stat_bonuses` dict replaces the old single `effect_value`, real WoW-scaled numbers (not the old +25/+50/+100 nonsense), casters no longer locked out of Battle/Guardian elixirs. See `entities/consumable.py` and `data/consumables/consumable_types.json`.
- Added real vendor greetings + a Shop/Leave dialogue choice (`ui/screens/quest_dialog_screen.py`) — vendors used to skip straight to the shop screen with no NPC personality at all

## 2. Barrens Expansion (Northern → Central → Southern, in that order)

### Northern Barrens (`tools/zone_expansion_generators.py::generate_northern_barrens`)
- 5 → **10 subzones**: added Dry Hills, Far Watch Post, Mor'shan Base Camp, Merchant Coast, Gold Road (all real WoW locations, researched before placement)
- New creatures: Serena Bloodfeather (named boss) + Witchwing Slayer, Southsea Brigand/Cannoneer/Captain Saltspray (named boss), Kolkar Raider, Road Bandit
- 2 hub NPCs added directly in the zone (Far Watch Post, Mor'shan Base Camp) — first "quest givers live in the wilderness, not just towns" NPCs
- 20 quests in `data/quests/northern_barrens.json`

### Central Barrens (`generate_central_barrens`)
- 4 → **10 subzones**: added Dreadmist Peak, Dreadmist Den, Grol'dom Farm, Shrine of the Fallen Warrior, Agama'gor, Bramblescar
- **Level band correction mid-session**: Kyle confirmed Central Barrens should stay 12-18, not follow Northern's 12-24 spread — this meant NOT reusing the existing 18-24 Bristleback Quilboar (already correctly placed in Southern Barrens' Razorfen Approach) and instead writing a new capped-down "Bristleback Raider" (15-18) tier
- New creatures: Bristleback Raider/Shaman, Razormane Veteran/Warcaller, Dreadmist Cultist/Warlock, Rathorian (named boss) + Xelnaz (named boss, guards the real "Demon Seed")
- 1 hub NPC (Kranal Fiss, Grol'dom Farm — a real WoW quest-hub NPC name)
- 14 quests in `data/quests/central_barrens.json`

### Southern Barrens (`generate_southern_barrens`)
- 3 → **6 subzones**: added Bael'dun Keep, Blackthorn Ridge, Raptor Grounds
- Real level band: **18-24** (confirmed against existing creatures already in this zone)
- **Note**: Razorfen Downs and Fray Island were researched but deliberately excluded — real dungeon instance (35-42) and real level-30 arena content respectively, don't belong as open-world subzones at this tier
- New creatures: Razormane Stalker/Seer, Hagg Taurenbane (named rare), Brontus (named rare kodo), General Twinbraid (named boss) — plus reused the already-correct Dwarf trio and Sunscale Lashtail/Screecher
- 16 quests in `data/quests/southern_barrens.json`

### The Broodspiral (home-brew dungeon, `generate_the_broodspiral`)
Kyle's explicit request: a 3→4-boss silithid mini-dungeon, **real Archimedean spiral layout** (not a real WoW instance — original content). Visually verified via rendered collision-map image, not just described.

- **Layout**: entrance at outer edge, corridor spirals ~2.2 turns inward, 4 boss rooms break off at meaningful radius checkpoints (not evenly-spaced), Queen's chamber sits at the true geometric center
- **4 bosses**, ability count follows Kyle's rule ("20+ level = more dangerous = more abilities"):
  - Carapace Warden (lvl 19, outer ring) — 3 abilities
  - The Broodkeeper (lvl 21, mid ring) — 4 abilities
  - Larval Broodguard (lvl 22, screening the approach) — 4 abilities
  - Broodspiral Queen (lvl 24, center, final) — 4 abilities, hits hardest
- **13 hand-authored loot items** in `data/loot/broodspiral_boss_loot.json` — every number computed from the real `entities/loot_generator.py` formulas (STAT_BUDGET_BASE_MULT, weight_tiers, armor_types.json multipliers, gear_suffixes.json's real per-stat costs) at item_level = boss_level+3 (Kyle's "slightly above standard rare" ask). Includes a real int/healing_power **gun** and a str/crit **1H mace** — the gun deliberately ignores the procedural generator's `valid_stat_templates` constraint (gun→agi_physical only) because Kyle flagged that as actively limiting the CoA custom classes' weapon variety
- **⚠️ Mid-session recovery incident**: an early `str_replace` insertion accidentally deleted the entire pre-existing `generate_wailing_caverns_expanded()` function. Caught by running the full `create_all_zones()` integration test (not just testing the new function in isolation) — recovered the function body from the session's own backup zip and reinserted it. **Lesson reinforced**: always run the full-system test after touching a shared file, not just the piece you were focused on.

## 3. Quest Reward Discipline (established + retrofitted this session)

Kyle's explicit pushback: *"why is everything int/spirit and agi/stam... give me some creativity."*

- **The `unique_item_defs` system already existed** in `world/quest.py` (`build_unique_reward_set`) but wasn't being used — earlier quests in this session used the generic procedural `gear_reward_slot`/`gear_reward_rarity` path instead, which rolls a random class-appropriate item rather than a hand-picked one. **Retrofitted 6 quests** (5 in Northern Barrens, 1 in Central Barrens) to use real named unique items instead.
- **Real stat-combo discipline going forward** (keep this in mind for future quest/loot work):
  - Real per-stat budget costs from `data/items/gear_suffixes.json`'s `stat_budget_costs` — primary stats and school spell powers cost 1.0, spell_power/healing_power cost 1.25, attack_power is cheap (0.5), crit/hit cost 10.0, haste costs 12.0 (priciest secondary stat)
  - **OG 9-class spec-level thinking**, not just 5 broad archetypes — tank specs (Prot Warrior/Pally, Feral Bear Druid) want defense/dodge/block, not just str/stam; caster specs split by role (Elemental wants spell power, Resto wants healing power + mp5, Shadow Priest wants crit_spell)
  - **School-specific spell power (fire/frost/nature/shadow/holy/arcane) is explicitly saved for higher-level content** — Kyle's call: keep secondary stats generic (`spell_power`, not `fire_spell_power`) at the current Barrens tier (12-24)
  - No trinkets in the Broodspiral loot table (Kyle: save that slot's rarity for later/special drops)
  - Every hand-authored item across this session's ~50 quests + 13 dungeon drops avoids repeating a stat combo

## 4. Orgrimmar NPC Bug Fix (end of session)

**Symptom reported**: "yellow NPC markers across Orgrimmar but no NPCs are there," "should be more than 12 NPCs."

**Root cause**: The real in-game Orgrimmar (`tools/orgrimmar_undercity_expansion.py::generate_orgrimmar_expanded` → `OrgrimmarMassive.generate_orgrimmar_massive`) is a 200×200, 9-district capital city with **35 real, pre-carved, walkable NPC marker slots** already baked into the terrain (one per district role — shaman trainer, blacksmith, mage trainer, etc. — plus a 12-stall central marketplace). The actual NPC *data* in `ambient_npcs.json`/`vendors.json` only ever populated 12 of these 35 slots, at coordinates that don't match this real generator at all (leftover from an old, explicitly-commented "PLACEHOLDER" 90×80 zone that isn't even the one wired into `create_all_zones()`). Every other district's marker tiles rendered with nothing behind them — exactly the "empty yellow marker" symptom.

**Fix**: Removed the 12 mis-placed NPCs, repopulated all 35 real slots (41 total NPCs — some slots got 2), preserved all 8 `npc_id`s that this session's Barrens quests reference as quest givers (just moved to correct positions), verified every position walkable + every sprite resolves + zero coordinate collisions.

**If NPCs still seem missing after this fix**: check whether the player's save file has a stale cached zone (old `Orgrimmar` tilemap baked into a save) rather than regenerating from `create_all_zones()` fresh — that's the next thing to check if the symptom persists.

---

## Verification Standard Used This Session

Every claim in this handoff is backed by one of:
- Real headless spawn tests (`SDL_VIDEODRIVER=dummy`) through actual `CreatureManager`/`QuestManager`/`VendorManager` code, not just data-file inspection
- Flood-fill reachability tests from real entrance portals to every boss room / new subzone
- Rendered PNG visualizations of terrain layouts (spiral shape, Orgrimmar district population) — actually looked at, not assumed
- Cross-reference checks: every `giver_npc_id`, kill target, gather/fetch item, dialogue topic, and `next_quest_id` chain link resolves to something real, checked programmatically against the live data files

## Known Follow-ups / Not Done This Session

- Walk-cycle animations still pending for the newly-replaced NPC races (single front-facing pose only, per earlier explicit scope call)
- Undercity's own NPC population wasn't audited — if it was built alongside Orgrimmar in the original expansion, it may have the same empty-slot problem and is worth checking
- Razorfen Downs (real dungeon, 35-42) and Fray Island (real level-30 arena) were identified as real content during Southern Barrens research but intentionally deferred, not built
- Dreadmist Den/Rathorian/Xelnaz "Demon Seed" storyline is left narratively open-ended (`org_seed_and_seal`'s turn-in text explicitly says "that's not the end of this") — real hook for a future quest chain if wanted
