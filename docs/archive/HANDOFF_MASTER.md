# FRONTIER RPG — MASTER HANDOFF

**Status:** Playable end-to-end. All systems compiled and tested.
**Save version:** 4
**Scale:** 61 Python files, ~12,600 lines
**Last updated:** August 2026

This replaces the chain of per-session handoff docs. It is the single source
of truth for what exists, what's half-built, and what's next.

---

## 1. QUICK NUMBERS

| | |
|---|---|
| Playable classes | 9 (all vanilla WoW) |
| Abilities | 79 across 9 classes, JSON-driven, ranked |
| Talent trees | 27 (9 classes × 3 specs) |
| Talents | 621 |
| Maps | 22 — 10 zones + 12 caves |
| Creatures | 143 |
| Vendors | 15 |
| Level cap | 60 (content supports ~1–25) |
| Continents | 2 (Kalimdor + Eastern Kingdoms via zeppelin) |

---

## 2. WHAT'S BUILT

### Core engine
- Pathlib-relative folder structure (portable across machines)
- Game state machine, 60 FPS main loop
- Versioned JSON save/load — **v4** (adds talent spend)
- Four-layer tilemaps (base / visual / collision / interaction)

### Character system
- 5 core stats (STR/STA/INT/SPI/AGI), 10 derived
- **Base stats never mutate** — gear, talents and buffs all fold into one
  shared "effective stats" bonus pool, so every source flows through
  identical maths
- Levelling to 60, prestige system
- Custom XP curve in `config.py` (~6–7 fights L1→2, ~40–50/level in the 40s,
  ~150–175 for 59→60). `get_exp_needed_for_level()` is the **single source of
  truth** — never hardcode the formula a second time.

### Abilities (`data/abilities/*.json`)
- 8–9 per class, old-school WoW ranks (Fireball Rank 1/2/3)
- Mana costs rise per rank; Rage/Energy stay flat (WoW-correct)
- Level-gated: a level 1 Warrior knows 3 abilities, 7 at 20, 9 at 40
- Effect types: `damage`, `spell_damage`, `heal`, `dot`, `spell_dot`, `hot`,
  `buff`, `debuff`
- Regenerate with `python3 tools/generate_abilities.py`

### Status effects (`combat/status_effects.py`)
- DoTs, HoTs, buffs, debuffs, ticking in `CombatEngine._end_turn()`
- `StatusEffectMixin` on both Character and Monster — no branching
- Same `effect_id` **refreshes** rather than stacks (WoW-correct)
- Buff `stat_mods` fold into the gear/talent bonus pool
- Cleared on combat end so nothing leaks between fights
- Displayed as colour-coded chips under each health bar in combat

### Talents (`data/talents/*.json`)
- 27 trees, ~23 talents each, 7 tiers gated at 0/5/10/15/20/25/30 points
- 56 points at level 60 vs 58–74 to fill one tree — **you can never max a
  tree**, matching vanilla. Every build is a real choice.
- Effects actually fire in combat: per-ability damage/cost/cooldown, global
  damage/healing multipliers, and raw stat grants
- Regenerate with `python3 tools/generate_talents.py`, which **fails loudly**
  if any talent references an ability that doesn't exist

### Combat
- Turn-meter based (AGI-driven), 20-slot hotbar (1–0 and Shift+1–0)
- Hit Rating (8% base physical miss, 6% spell)
- Weapon damage main-hand + off-hand (50% dual-wield penalty)
- Loot drops on victory, XP bonuses for boss (1.75x) / cave (1.5x) /
  subzone (1.2x) — **all live**

### Equipment
- 16 slots, 4 armor types, 13 weapon types, procedural generation
- `armor_type` (defense + equip restriction) and `stat_template` (which stats
  roll) are **independent axes** — scales to the full 30-class roster
- Rarity Common→Epic, level-gated. Legendary reserved, unused.

### Consumables & economy
- WoW-style copper/silver/gold (100:1), potions/elixirs/food
- Consumables live in the existing hotbar (no separate quickbar)
- 15 vendors across 8 locations, all on verified NPC tiles

### World — 10 zones
| Zone | Size | Levels | Subzones |
|---|---|---|---|
| Valley of Trials | 120x120 | 1–6 | 1 |
| Durotar | 110x240 | 1–13 | 4 |
| Razor Hill | 60x60 | town | — |
| Echo Isles | 100x100 | 10–15 | 1 |
| The Barrens | 200x160 | 10–25 | 6 |
| Ratchet | 70x60 | town | — |
| Camp Taurajo | 64x56 | town | — |
| Orgrimmar | 90x80 | placeholder | — |
| Zeppelin Tower | 34x46 | transit | — |
| Tirisfal Glades | 150x130 | 1–12 | 5 |

Durotar is laid out to match real WoW: tall north-south, Orgrimmar gate far
NW, Kolkar Crag SW, Echo Isles portal SE, Southfury River W border.

### World — 12 caves
The Den, Burning Blade Coven (Valley) · Drygulch Ravine, Skull Rock,
Tiragarde Hold, Dustwind Cave (Durotar) · Sunken Temple Grotto, Zalazane's
Hollow (Echo Isles) · Boulder Lode Mine, Wailing Caverns (Barrens) ·
Night Web's Hollow, Scarlet Crypt (Tirisfal)

- Four layout archetypes: `chain`, `warren`, `cavern`, `spiral`
- **Fixed spawn points** — you see the mob, you fight the mob
- **Exactly one boss** placed at the boss chamber, never rolled
- **No respawns** until you exit and re-enter
- Bosses are a genuine wall: at-level testing gave 3 wins / 2 losses

### The zeppelin
Durotar → Zeppelin Tower (climb the spiral ramp) → Tirisfal Glades.
Deliberately two hops so crossing continents feels like a journey.

### UI screens
Menu · Character creation · Character sheet · Skills · Talents · Inventory ·
Vendor · Overworld · Combat · **Map (M key)**

Map shows the full zone scaled with aspect preserved, player position,
portals, NPCs, treasure, and labelled subzone regions.

---

## 3. BUGS FOUND AND FIXED (worth knowing — several were severe)

These were all live in shipped builds. Listed because the pattern matters:
most were systems that *looked* finished and had never actually run.

1. **Collision was inverted game-wide.** `is_walkable()` returned
   `not is_walkable(collision_tile)`, making every wall, tree, rock and cliff
   **passable**, while bushes blocked you. Nothing in the game collided.
2. **The Skills screen had never worked.** Wrong attribute name in 6 places,
   a call to a nonexistent method, and 12 `draw_text()` calls using kwargs
   the Renderer never accepted. It raised on its own first render line.
3. **Vendors never worked in any zone.** `vendors.json` keys zones as
   `valley_of_trials`; ZoneManager passed `"Valley of Trials"`. Nothing
   normalized. Then, after fixing that, all 4 original vendors turned out to
   be standing on tiles with no NPC marker — Echo Isles had no `npc` tile
   anywhere on the map.
4. **Multi-rank talents were divided by their own max rank.** A 5/5
   "+5% per rank" talent granted 5%, not 25%.
5. **Talent points didn't survive save/load.** `to_dict()` never wrote them.
6. **Talent screen ESC could never have worked** — constructed with no state
   manager reference. There was no way out of the screen.
7. **Cave/subzone XP bonuses were dead code** since written — subzones
   existed only as encounter-table keys, so `location_type` was always
   `"open_zone"`.
8. **Every ability was castable at level 1** — rank gating clamped to rank 0
   without checking rank 1's own level requirement.
9. **No DoT system existed.** Rend, Corruption, Immolate, Shadow Word: Pain,
   Moonfire and Rejuvenation all resolved as single instant hits.
10. **Talent tree rendered off-screen** — fixed `center_y` put tier 0 at
    y = −84.
11. Towns were treated as caves (cave-ness inferred from `.region`).
12. `wood` is not a walkable tile — using it as flooring made docks and
    platforms impassable.
13. Terrain scatter sealed features into unreachable pockets. Echo Isles was
    **0.7% reachable** from its own portals at worst.

---

## 4. WORK IN PROGRESS / NEXT UP

Roughly highest value first.

### Immediate
1. **Draw cave spawns on the overworld.** You currently walk into fixed
   spawns blind, which undercuts the whole "you see the mob, you fight the
   mob" design. `cave_spawns.active_positions()` already returns
   `(x, y, is_boss)` ready to render. **Small job, big payoff.**
2. **Playtest and balance.** 79 abilities × 5 ranks and 621 talents are
   internally consistent and completely untuned. Level a character to ~20 and
   report what feels wrong. This is worth more than another system.
3. **Expand ability kits beyond 8–9.** Roughly 70% of talents are stat/global
   effects because there aren't enough abilities to modify. More abilities
   deepen all 27 existing trees without touching them.

### Known gaps in shipped systems
- `unlock_ability` talent effect is read but nothing consumes it — no talent
  uses it (deliberately: no fake capstones)
- Talents aren't spec-locked (vanilla-correct) and respec is free — you have
  currency now, so adding a cost is easy
- "Stun" is modelled as a heavy Haste debuff, not a real skipped turn
- AoE abilities hit one target (combat is 1v1 until parties exist)
- Monsters can't apply DoTs — `MonsterAbility` has no DoT authoring
- Boss fights are single-phase
- Item sets, sockets, enchants: schema-ready, zero logic
- Inventory is unlimited (no bag caps)
- `combat_ui_panel.py` is confirmed dead code
- `tools/add_zones.py` still emits a "Southern Durotar" block that is now
  folded into Durotar on load — harmless, worth cleaning

### Roadmap phases not started
- **Phase 7 — Quests.** Nothing exists. The XP curve was cut 10% assuming
  quests would fill the gap.
- **Phase 8 — Dungeons & multi-phase bosses.**
- **Phase 9 — Party/recruitment.** Unlocks AoE meaningfully.
- **Phase 10 — Content expansion.** Orgrimmar is structure only; Tirisfal
  has no quests.
- **Phase 11 — Sprite/art pass.** Still placeholder shapes.
- **Prestige audit** — may still assume level 100 in places; cap is 60.

### The 21 CoA classes
Data-modeled (resources, armor, stats) but **not selectable**, and ability/
talent data isn't written. Both sources are unreachable programmatically:
`coabuildhub.com` hard-blocks bots, `db.ascension.gg` disallows via
robots.txt and renders client-side. Reachable fan wikis are near-identical
SEO-farm copy — fine for resource mechanics, not trustworthy for ability
names or numbers.

**To unblock: open the site in a browser and paste raw page text into chat.**
The tuple format in `tools/ability_data.py` and `tools/talents_*.py` makes
conversion fast once real data exists.

Recommendation stands: **ship the base game on 9 classes.** CoA is the
expansion.

---

## 5. AUTHORING TOOLS

`tools/` is authoring-only — the runtime never imports it. Safe to delete if
you'd rather hand-maintain the JSON.

| Script | Purpose |
|---|---|
| `generate_talents.py` | Rebuild all 27 trees + validate |
| `generate_abilities.py` | Rebuild all 9 ability kits + validate |
| `add_zones.py` | Barrens creature/encounter data |
| `add_tirisfal.py` | Tirisfal creature/encounter data |
| `talent_builder.py` | Hex layout + JSON emitter |
| `ability_data.py`, `talents_*.py` | The actual authored data |

Both generators hard-fail on unknown effect keys, missing ability references,
durations missing on DoT/buff types, ranks past the level cap, and layout
collisions. **Ability and talent data cannot silently drift apart.**

---

## 6. WORKING PRINCIPLES

- **WoW authenticity is the benchmark.** Check how vanilla actually works
  rather than inventing adjacent mechanics.
- **Single source of truth.** `CLASS_RESOURCE_MAP`, `get_exp_needed_for_level()`,
  `get_learned_abilities()` — duplicate a formula and it *will* drift.
- **Template + delta, never full stat blocks.** Creatures are
  `{"template": "beast_basic", "hp_mult": 1.15}` so balance passes stay
  single-edit.
- **Playable at every phase.** The principle that keeps this from becoming
  the stalled JRPG.
- **Validate geometry, don't assume it.** Random terrain scatter has sealed
  off portals, NPCs and chests repeatedly. Every hand-placed feature that
  must be reachable calls `_carve_path()` / `_carve_landing()`.
- **Read the real code before claiming anything works.** Three separate
  systems in this project were shipped, documented as complete, and had
  never executed once.

---

## 7. RUNNING IT

```bash
cd frontier_rpg/
pip install -r requirements.txt
python3 main.py
```

**Controls:** WASD move · Space interact (vendor/portal) · 1–0 and Shift+1–0
hotbar · **M map** · ESC back
