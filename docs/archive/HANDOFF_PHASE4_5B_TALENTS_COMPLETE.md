# FRONTIER RPG — PHASE 4.5b HANDOFF: TALENTS WIRED + ALL 9 CLASSES BUILT

**Status:** Complete, compiled, tested end-to-end.
**Save Version:** bumped to **v4** (talent spend is now serialized).
**Date:** August 24, 2026

---

## TL;DR

- **3 real engine bugs fixed** (see Part 1) — all three would have silently corrupted talent behaviour
- **Talents now actually affect combat** — damage, resource cost, cooldowns, and derived stats
- **All 27 trees for the 9 original WoW classes built** — 621 talents, every effect key validated against real code
- **CoA's 21 classes deliberately not started** — see "Why 9, not 30" at the bottom

---

## PART 1: BUGS FIXED (all three were live)

### 1. Multi-rank talents were divided by their own max rank
`TalentNode.get_effective_effects()` scaled effects by `points_spent / max_points`
instead of `× points_spent`.

Result: a 5-rank "+5% crit per rank" talent granted **5% at 5/5**, not 25%.
Every multi-rank talent in the game was worth exactly one rank no matter how
much you invested in it. A 1-rank talent was unaffected, which is why this
never looked obviously broken.

**Fixed** in `entities/talent_node.py`. JSON effect values are unchanged and
now mean what their descriptions always said — per rank.

### 2. Talent points did not survive save/load
`Character.to_dict()` never wrote `talent_trees`, and `from_dict()` rebuilt
fresh empty trees and recomputed `talent_points_available` from level. Every
point you spent was refunded on reload.

**Fixed** in `entities/character.py`. Talent spend is now stored sparsely
(only nodes with points), so saves stay small and adding new talents to a
tree later won't invalidate old saves. `SAVE_VERSION` bumped 3 → 4.

### 3. Click detection forced a cramped layout
`TalentTreeScreen.handle_click()` rounded the mouse position to integer hex
coordinates and required an exact `==` match against `node.hex_x/hex_y`. Any
node not on a tight integer lattice was literally unclickable.

This is the actual root cause of the "talents are spatially squished"
complaint in the Phase 4.5 handoff — it was a hit-testing constraint, not a
rendering choice.

**Fixed** — `_node_at_pixel()` now measures real pixel distance to each
node's rendered centre. Coordinates can be anything; trees are laid out with
~90px column spacing and ~78px tier spacing against a 30px hex radius.

### Bonus: two stats ignored their bonus pool
`parry` and `block` were computed purely from base stats, ignoring gear and
talent bonuses entirely. Any item or talent rolling Parry did nothing.
Both now read `bonuses` like Dodge always did.

---

## PART 2: TALENT → COMBAT WIRING (the actual Phase 4.5b work)

### Character side (`entities/character.py`)
Three new methods:
- `get_talent_effects()` — sums every effect key across all owned trees
- `get_talent_effect(key, default)` — single lookup
- `get_talent_unlocked_abilities()` — reserved for `unlock_ability` (see Known Gaps)

Talent stat effects are folded into the **same bonus dict as equipment** at
the top of `_recalculate_derived_stats()`. This means a talent granting +3
Strength flows through the identical maths as a +3 Strength item — no
parallel code path to keep in sync.

### Ability side (`combat/abilities.py`)
`Ability` gained `talented_cost()`, `talented_cooldown()`, and
`_damage_multiplier()`. `use()` now routes cost and cooldown through them,
and `_apply_effect()` multiplies damage/healing by the talent multiplier.

`_has_resource()` / `_consume_resource()` take an optional explicit cost and
default to the untalented rank cost, so any older call site still behaves
exactly as before.

Monsters have no `get_talent_effect`, so every lookup degrades to neutral for
them automatically — no branching at call sites.

### Effect key reference

**Stat keys** (folded into the gear bonus pool):
`strength`, `stamina`, `intellect`, `spirit`, `agility`, `attack_power`,
`spell_power`, `healing_power`, `crit_chance_physical`, `crit_chance_spell`,
`dodge`, `parry`, `block`, `haste`, `armor`, `magic_resistance`,
`hit_rating`, `max_health_pct`, `max_mana_pct`

**Global multipliers** (0.02 = +2%):
`all_damage`, `physical_damage`, `spell_damage`, `healing_done`

**Per-ability** (`<id>` must be a real `Ability.ability_id`):
`ability_<id>_damage` (multiplier), `ability_<id>_cost` (flat reduction),
`ability_<id>_cooldown` (flat turn reduction)

All numeric values are **per rank**.

### Verified working
```
Warrior 40, warrior_arms: Cruelty 5/5 + Imp. Heroic Strike 3/3
                          + Mortal Strike 1/1 + Arms Mastery 1/1

  crit           12.8%  ->  17.8%   (+5.0, exactly 5 ranks x 1%)
  HS Rage cost      20  ->     17   (-3, exactly 3 ranks x 1)
  HS damage        235  ->    318   (x1.356 = 1.20 per-ability x 1.13 global)
```

---

## PART 3: THE 27 TREES

621 talents across 9 classes × 3 specs, ~23 per tree.

| Class | Trees |
|---|---|
| Warrior | Arms, Fury, Protection |
| Rogue | Assassination, Combat, Subtlety |
| Hunter | Beast Mastery, Marksmanship, Survival |
| Mage | Arcane, Fire, Frost |
| Warlock | Affliction, Demonology, Destruction |
| Priest | Discipline, Holy, Shadow |
| Druid | Balance, Feral, Restoration |
| Shaman | Elemental, Enhancement, Restoration |
| Paladin | Holy, Protection, Retribution |

**Structure:** 7 tiers (0–6), 4 columns per tier, gated at
0/5/10/15/20/25/30 points. Each tier-6 capstone is a single big payoff
(usually +10% all damage or +12% healing).

**Point economy:** you get 56 points at level 60 (1/level from level 5).
Fully spending a single tree costs 58–74. So you can never max one tree —
that is deliberate and matches vanilla (51 points into 61-point trees). Every
build is a real choice.

### How they were authored
Hand-writing 621 JSON nodes means hand-placing 621 hex coordinates and 621
connection lists — that's where data-entry errors live. Instead trees are
authored as compact tuples in `tools/talents_*.py`:

```python
("cruelty", "Cruelty", 0, 3, 5, {"crit_chance_physical": 1.0},
 "Increases your melee critical strike chance by 1% per rank.")
#  suffix   name      tier col maxpts  effects              description
```

`tools/talent_builder.py` derives hex position from (tier, column) and
auto-connects each node to the nearest node one tier up.

**To regenerate after editing:** `python3 tools/generate_talents.py`

The generated JSON is plain, hand-editable, and in the exact schema
`TalentManager` already reads. The runtime never imports `tools/` — it's an
authoring aid only, safe to delete if you'd rather hand-maintain the JSON
from here.

### Validation
`generate_talents.py` fails loudly on:
- an effect key targeting an `ability_id` that doesn't exist
- an unrecognised effect key no code consumes
- two talents colliding on the same (tier, column) slot
- tier/column out of range

Current run: **621 talents, 0 problems.** Every single effect key in every
tree is consumed by real code. There are no decorative talents that silently
do nothing.

---

## PART 4: KNOWN GAPS & HONEST CAVEATS

1. **Your classes only have 3 abilities each** (plus auto-attack). That's the
   real ceiling on talent design right now. Roughly 70% of these talents are
   stat/global effects precisely because there aren't enough abilities to
   modify. **Expanding class ability kits is the highest-value next task** —
   it'll make the existing trees deeper without touching them.

2. **`unlock_ability` is not wired.** `get_talent_unlocked_abilities()`
   exists and reads the key, but nothing consumes the result yet. No talent
   currently uses it — I'd rather ship zero fake capstones than 27 that
   pretend to grant abilities. Capstones are stat/damage payoffs for now.

3. **Talents are not spec-locked.** A Warrior can spend across Arms, Fury,
   and Protection freely, gated only by per-tree tier requirements. That's
   vanilla-correct. Nothing enforces a "primary spec" yet.

4. **No talent reset / respec cost.** Right-click refunds a point for free,
   any time. WoW charged gold and escalated. You have a currency system now,
   so this is easy to add whenever you want the friction.

5. **Rogue crit reaches ~64% at level 60** in this test build. That's not a
   talent problem — `crit_chance_physical = agility * 0.5` was already very
   generous before talents existed, and talents just made it visible. Worth
   a balance look, but it's a pre-existing baseline issue.

6. **Prestige still assumes level 100 in places** — carried over from the
   previous handoff, still not audited. Talent points are computed as
   `level - 4`, which now caps at 56 given the level-60 cap.

7. **Balance is unplaytested.** The numbers are internally consistent and
   sane on paper. They are not tuned. Expect to move them.

---

## FILE MANIFEST

**New:**
- `tools/talent_builder.py` — layout + JSON emitter
- `tools/talents_physical.py` — Warrior, Rogue, Hunter data
- `tools/talents_casters.py` — Mage, Warlock, Priest data
- `tools/talents_hybrids.py` — Druid, Shaman, Paladin data
- `tools/generate_talents.py` — regenerate + validate
- `data/talents/*.json` — 27 generated trees

**Modified:**
- `entities/talent_node.py` — rank scaling fix
- `entities/character.py` — talent effect aggregation, derived-stat folding,
  parry/block bonus fix, talent serialization
- `combat/abilities.py` — talent-aware cost/cooldown/damage
- `ui/screens/talent_tree_screen.py` — pixel-accurate hit testing
- `config.py` — `SAVE_VERSION` 3 → 4

**Removed:**
- `data/talents/warrior_arms_TEMPLATE.json` (superseded)

---

## WHY 9, NOT 30

CoA's 21 classes are **not** started here, on purpose.

Both CoA data sources are unreachable programmatically — `coabuildhub.com`
hard-blocks automated requests, and `db.ascension.gg` disallows them via
robots.txt and renders client-side anyway. The fan wikis that *are* reachable
are near-identical SEO-farm copy across four domains; fine for spec names and
resource mechanics, not trustworthy for ability names, costs, or ranks.

That makes CoA ability/talent data the single worst thing to put on the
critical path to a shippable base game. The 9 vanilla classes need no
scraping at all.

**If you want the CoA trees:** open coabuildhub in a browser and paste raw
page text or a spec's ability list into chat. That converts the bottleneck
from impossible to merely tedious, and the tuple format above makes turning
it into JSON fast.

---

## RECOMMENDED NEXT STEPS

1. **Playtest a Warrior or Mage to ~20** and spend points. Confirm the
   numbers feel right, not just that they're correct.
2. **Expand ability kits** from 3 to 6–8 per class. This is the single
   biggest multiplier on everything built here.
3. **Add respec cost** now that currency exists.
4. **Balance pass on crit baselines** (see caveat 5).
5. Only then consider CoA, and only with pasted source data.

---
---

# ADDENDUM: SKILLS PASS — ALL 9 ABILITY KITS + STATUS EFFECT SYSTEM

**Status:** Complete, compiled, all 79 abilities regression-tested.

## What changed

Ability kits went from **3 abilities per class to 8–9**, and abilities moved
out of hardcoded Python into JSON like every other system in the project.

| Class | Abilities | Class | Abilities |
|---|---|---|---|
| Warrior | 9 | Priest | 9 |
| Rogue | 8 | Druid | 9 |
| Hunter | 8 | Shaman | 9 |
| Mage | 9 | Paladin | 9 |
| Warlock | 9 | **Total** | **79** |

## New: status effect system (`combat/status_effects.py`)

Before this, `effect_type` supported only damage / spell_damage / heal, plus
a "buff" stub that did nothing. Every nominally-DoT ability — Rend,
Corruption, Immolate, Shadow Word: Pain, Moonfire, Rejuvenation — resolved as
a single instant hit. Roughly half the roster is built around damage over
time and had no actual identity in combat.

Now supported: `dot`, `spell_dot`, `hot`, `buff`, `debuff`.

- `StatusEffectMixin` is mixed into both Character and Monster, so the engine
  never branches on which class it holds.
- Effects tick in `CombatEngine._end_turn()`, the same place cooldowns
  decrement, so "1 turn" means the same thing everywhere.
- Damage applies **before** duration decrements, so an N-turn DoT ticks
  exactly N times.
- Re-applying the same `effect_id` **refreshes** rather than stacking
  (WoW-correct, prevents "spam Corruption 8 times").
- Buff/debuff `stat_mods` fold into the **same bonus pool as gear and
  talents** — a +30 Attack Power buff and a +30 Attack Power item are
  indistinguishable to every downstream formula.
- Effects are cleared on combat end so nothing leaks between fights.

Verified: Demon Armor takes Armor 56 → 196 → back to 56 on expiry. Warlock
Corruption at 56 dmg/turn becomes 81 with Improved Corruption 5/5 +
Unstable Affliction 1/1 — exactly the +45% those talents promise.

## New bugs found and fixed

### 4. Every ability was castable from level 1
`refresh_rank_for_level()` clamped `current_rank_index` to 0 regardless of
whether the character met rank 1's own level requirement. With 3 abilities
all learned at level 1 this was invisible. With 9-ability kits it meant a
**level 1 Warrior could open with Mortal Strike** (learned at 30) at full
rank-1 power.

Fixed — `Ability.is_learned` is now set by the same refresh, `use()` refuses
unlearned abilities outright, and `Character.get_learned_abilities()` is the
filter for UI. Progression now reads correctly: Warrior knows 3 at level 1,
7 at level 20, 9 at level 40.

### 5. Hotbar started empty
Tolerable with 3 abilities, tedious with 9. `_autofill_hotbar()` now places
newly-learned abilities into the first free slots on creation and level-up.
It only ever fills **empty** slots and never reorders or removes anything, so
manual arrangements are preserved.

## Abilities are now data-driven

`data/abilities/<class>.json`, regenerated by:

```
python3 tools/generate_abilities.py
```

`get_class_abilities()` keeps its exact signature, so every existing caller
works untouched. A class with no authored kit (the 21 CoA classes) returns an
empty book rather than crashing.

Validation fails loudly on unknown effect types, DoT/HoT/buff entries missing
a duration, buff/debuff entries with no stat_mods, ranks past the level cap,
duplicate ids, and — importantly — **any talent referencing an ability id
that no longer exists**. Ability and talent data can no longer silently
drift apart.

## Caveats

1. **The combat UI does not display active effects yet.** DoTs tick and log
   correctly, but there's no buff/debuff icon row on the combat screen. The
   data is there (`get_effects_summary()` returns `(name, turns, type)`
   tuples ready to render) — it just needs UI work. This is the most
   visible remaining gap.

2. **Monsters can't apply DoTs.** The mixin is on Monster so they can
   *receive* effects, but `MonsterAbility` has no DoT authoring. Enemy
   casters still only deal instant damage.

3. **"Stun" is modeled as a heavy slow**, not a real skipped turn — Hammer of
   Justice and Frost Nova apply large Haste debuffs. A true turn-skip needs
   turn_meter work.

4. **AoE is still single-target.** Thunder Clap, Multi-Shot, Arcane
   Explosion and Chain Lightning are authored and flavored as AoE but hit one
   target, since combat is 1v1 until the party system lands (Phase 9).

5. **Not balance-tested.** 79 abilities × 5 ranks is a lot of numbers that
   are internally consistent and untuned. Expect to move them.

## Files

**New:** `combat/status_effects.py`, `tools/ability_data.py`,
`tools/generate_abilities.py`, `data/abilities/*.json` (9 files)

**Modified:** `combat/abilities.py` (JSON loader replaces 9 factory
functions, new effect types, learned-gating), `combat/combat_engine.py`
(effect ticking + cleanup), `entities/character.py` (mixin, buff recalc
hooks, autofill, `get_learned_abilities`), `entities/monster.py` (mixin)

---
---

# ADDENDUM 2: UI BUGFIX PASS (Kyle's playtest report)

All five reported issues fixed, plus two more found while fixing them.

### 1. Talent tree cut off
`center_y` was hardcoded to 150 with fixed spacing. Trees span hex_y −6 to
+6, so tier 0 rendered at y = 150 − 234 = **−84**, entirely above the window.

`_fit_layout()` now measures each tree's actual coordinate extents and
derives spacing to fill the available area, then centres it. Horizontal and
vertical spacing are fitted **independently** — a single uniform spacing got
clamped by the tighter (vertical) axis and squeezed the tree into a narrow
column, using 295px of 940px available. Now uses 743px with a node radius of
35 instead of 18. Also survives trees growing deeper or wider later.

### 2. No way to exit the talent screen
`GameStateManager` constructed `TalentTreeScreen(1200, 700, None)` with no
state_manager reference, and the ESC handler did
`getattr(self, 'state_manager', None)` — which was always None. **ESC could
never have worked.**

State manager is now passed in, ESC works, and there's a visible **Back**
button top-right. Screen also now uses the real `SCREEN_WIDTH/HEIGHT` from
config rather than hardcoded 1200×700 on a 1280×720 window.

### 3. Forced into one spec
The screen opened on `list(talent_trees.keys())[0]` and had no way to switch,
so a Shaman was locked to whichever tree the dict happened to yield first.

Added **spec tabs** across the top — one per tree, showing points spent in
each, click to switch. Confirmed working for all 9 classes.

### 4. All skills available at level 1
The gating logic was correct (`is_learned` was landing right), but both the
Skills screen and the character sheet listed
`ability_book.get_all_abilities()` — every ability in the class kit
regardless of level. So a level 1 character *saw* all 9 and could slot them.

Both now use `Character.get_learned_abilities()`, the same filter the hotbar
autofill uses, so they cannot disagree. Verified: Shaman goes 3 → 4 → 6 → 7
→ 8 → 9 abilities across levels 1/4/8/10/16/24.

### 5. Skills running off the page
Character sheet drew the ability book as one unbounded horizontal strip;
fine at 3 abilities, off-screen at 9. Now wraps into rows at the window edge.

The dedicated Skills tab already existed but had **never worked** (see below).

### 6. (found) The Skills tab crashed on open
`SkillsScreen.__init__` took `game_state_manager` and passed it to
`BaseScreen`, which stores it as `self.state_manager` — but the class
referenced `self.game_state_manager` in six places. It also called
`set_state()` (method doesn't exist; it's `transition_to()`) and made twelve
`draw_text()` calls with `font_size=` and `center=True` kwargs that the
shared `Renderer` has never accepted.

This screen raised on the first line of its own render. It was dead code.
Fixed and the render method rewritten cleanly.

### 7. (found) Scroll offset was never modified
`scroll_offset` existed and was applied to the list slice, but nothing ever
changed it — no wheel handler. Harmless at 3 abilities, a real trap at 9+.
Mouse wheel now scrolls, clamped to both ends, with a `[3-12]` position
indicator in the panel header.

Also while in there: hotbar labels wrap instead of truncating at 10 chars
("Demoralizi"), and the ability list shows current rank (`Rank 3/5`).

## Files touched
`ui/screens/talent_tree_screen.py`, `ui/screens/skills_screen.py`,
`ui/screens/character_sheet_screen.py`, `core/game_state.py`

## Still outstanding
Combat UI still doesn't display active DoTs/buffs — `get_effects_summary()`
returns render-ready tuples, it just needs the icon row. That remains the
biggest visible gap.

---
---

# ADDENDUM 3: COMBAT STATUS EFFECT DISPLAY

The last known gap is closed — active DoTs, HoTs, buffs and debuffs now show
on the combat screen instead of only in the log.

### What it looks like
A row of colour-coded chips under each combatant's health bar, showing the
effect name and turns remaining (`Corruption 3`). Colours:

| Type | Colour |
|---|---|
| DoT | red |
| HoT | green |
| Buff | blue |
| Debuff | amber |

Chips wrap to a second row rather than overflowing the panel, long names
abbreviate (the turn counter is what matters at a glance), and the row
collapses to zero height when nothing is active so it never pushes the
layout around unnecessarily.

`_draw_status_effects()` returns the height it consumed so the caller
advances its own layout cursor — the player panel, enemy panel and combat log
all stay correctly spaced regardless of how many effects are running.

It reads `get_effects_summary()`, which both Character and Monster expose via
`StatusEffectMixin`, so the same code renders both sides with no branching.

### Verified
Warlock 30 opening Corruption + Immolate + Demon Armor:

```
turn 1: enemy 4886 | enemy: Corruption(3) Immolate(2) | player: Demon Armor(4)
turn 2: enemy 4772 | enemy: Corruption(2) Immolate(1) | player: Demon Armor(3)
turn 3: enemy 4658 | enemy: Corruption(1)             | player: Demon Armor(2)
turn 4: enemy 4612 | enemy: -                         | player: Demon Armor(1)
turn 5: enemy 4612 | enemy: -                         | player: -
```

Counters tick down, chips disappear on expiry, DoT damage stops exactly when
they do. All six test classes render all five screens cleanly.

### Also fixed: a third get_all_abilities() caller
`CombatScreen.start_combat()` auto-slots abilities when the hotbar is empty,
and was still using `get_all_abilities()` — so an old save could get level 30
abilities slotted onto a level 1 bar, where they would then refuse to fire.
Now uses `get_learned_abilities()` like everywhere else, and slots up to 10
instead of 5. Audited: no unfiltered callers remain in the UI layer.

## Files touched
`ui/screens/combat_screen.py`

---
---

# ADDENDUM 4: TWO NEW ZONES — SOUTHERN DUROTAR & THE BARRENS

World goes from 4 zones to **6**, level ceiling from ~16 to **25**.

| Zone | Size | Levels | Subzones | Caves |
|---|---|---|---|---|
| Southern Durotar | 140x110 | 8–13 | 2 | 2 |
| The Barrens | 200x160 | 10–25 | 6 | 2 |

The Barrens is now the largest map in the game.

## Southern Durotar
Durotar was one 150x100 map covering the whole 4–13 band, but the bestiary
doc splits it North/Central (4–10) and South (8–13). **The southern creatures
already existed in `creatures.json` and were already grouped into subzones —
they just had nowhere on the map to live.** This gives them a home.

Terrain: Southfury river down the west edge, ocean along the south (Scuttle
Coast), a cliff-ringed bowl for Kolkar Crag in the east, broken cliffs
northeast for Drygulch Ravine.

Content: The Southern Reach (open), Kolkar Crag + Scuttle Coast (subzones),
Drygulch Ravine + Dustwind Cave (caves). All reuse existing creatures.

## The Barrens
Golden savanna with roads crossing at a central hub.

- **Open zone** — The Golden Plains: Plainstriders, Zhevra, Savannah cats,
  Giraffes, Sunscale Screechers (10–16)
- **Lushwater Oasis** — silithid (12–16)
- **The Forgotten Pools** — murlocs, water elementals, Gaharrz the Drowned (17–22)
- **Razorfen Approach** — Bristleback quilboar (14–20)
- **Kolkar Plains** — centaur, Verog the Dervish (15–21)
- **Field of Giants** — kodo, Sunscale Lashtails (20–24)
- **Witchwing Terrace** — cliff-ringed harpy roost, Hezrul Bloodmark (20–25)
- **Boulder Lode Mine** (cave) — Venture Co., Foreman Grills (16–22)
- **Wailing Caverns** (cave) — deviates, Druids of the Fang, Skum (18–24)

**The Crossroads** sits at the centre: four buildings, cleared ground, two
vendors, with north-south and east-west roads carved through the whole map so
it reads as a real hub rather than a clearing.

**42 new creatures**, all template+delta (never full stat blocks) per the
bestiary rule, so balance passes stay single-edit.

## Connectivity
Three new portal links:
- Durotar (75,95) ↔ Southern Durotar (70,3)
- Southern Durotar (136,55) ↔ The Barrens (4,76)
- Durotar (110,95) ↔ The Barrens (100,4) — direct north road, so the 10–16
  Barrens content isn't gated behind an 8–13 zone the player may have
  outlevelled

Added `ZoneGenerator._carve_landing()`: every portal placement now guarantees
a walkable patch around itself. Portals placed after random terrain scatter
could otherwise end up buried under trees/rock/water — visible but
unsteppable. Applied to the two new Durotar exits as well.

## Verified
- All 6 zones reachable from the start point
- Every linked portal tile walkable; every spawn point walkable and in-bounds
- Flood fill: Southern Durotar **100%** connected, The Barrens **99.8%**
  (~64 tiles isolated inside oasis water). No stranded portals or NPCs.
- Encounters spawn at correct level bands in every open zone, subzone and cave
- Cave-entrance portals are intentionally unlinked (traversal is a later
  phase); `try_use_portal()` already fails safe on those
- Combat: 8/8 wins at ~3 turns per kill for Hunter/Warrior/Warlock/Mage/Priest
  across levels 11–24

## Also fixed: vendors never worked, in any zone
`vendors.json` keys zones as `"valley_of_trials"`, but `ZoneManager` passes
the Tilemap display name `"Valley of Trials"`. Nothing normalized between
them, so `get_vendor_at_location()` **never matched anything** — the entire
vendor system was unreachable everywhere, not just in the new zones.

Added `VendorManager._zone_key()` normalizing on both load and lookup, so it
accepts either form. All 4 original vendors now resolve. Verified: Old Marta
is reachable at (60,50) in Valley of Trials.

Three new vendors added (2 at the Crossroads, 1 in Southern Durotar), all
selling validated consumable ids.

## Files
**New:** `tools/add_zones.py` (idempotent data generator)
**Modified:** `world/zone_generator.py`, `world/portal_manager.py`,
`world/vendor_manager.py`, `data/creatures/creatures.json`,
`data/creatures/encounters.json`, `data/npcs/vendors.json`

---
---

# ADDENDUM 5: SUBZONES, CAVES, MAP SCREEN, DUROTAR REBUILD

**World is now 15 maps: 5 overworld zones + 10 real caves.**

## 1. Subzones and caves were never places

You were right — they existed **only as encounter-table keys** in
`encounters.json`. There was no way to be standing in one. `trigger_encounter()`
hardcoded `location_type="open_zone"`, which means the **subzone (1.2x) and
cave (1.5x) XP multipliers have been dead code since they were written** —
built, tested, correct, and never once fired in play.

Now:
- `Tilemap.subzones` — named rectangular regions, `add_subzone()` /
  `get_subzone_at()`
- `ZoneManager.get_location_context()` returns `(location_type, table_key)`
  from the player's actual tile
- Caves are **real tilemaps**, entered through a portal

Verified on an identical Plainstrider at level 18:

| Location | XP |
|---|---|
| open_zone | 427 |
| subzone | 512 (**1.2x**) |
| cave | 640 (**1.5x**) |
| boss | 747 (1.75x) |

**10 caves generated:** The Den, Burning Blade Coven (Valley); Drygulch
Ravine, Skull Rock, Tiragarde Hold, Dustwind Cave (Durotar); Sunken Temple
Grotto, Zalazane's Hollow (Echo Isles); Boulder Lode Mine, Wailing Caverns
(Barrens).

Cave layout is a chamber chain — entrance at the bottom, corridor, boss
chamber at the top with the treasure — so the deepest point is always
furthest from the exit, matching the bestiary's design rule. All 10 verified
enterable and exitable through real portal use.

**Subzone regions registered:** Valley (Scorpid Nest); Durotar (Thunder Ridge,
Rocktusk Farm, Kolkar Crag, Scuttle Coast); Echo Isles (Troll Camps); Barrens
(all 6). Every key validated against `encounters.json` — a region whose table
is missing falls back to the open-zone table rather than returning nothing.

## 2. Durotar rebuilt to real WoW geography

Was 150x100 (wide). Real Durotar is a **tall north-south coastal strip**, so
it's now **110x240**, with landmarks where they actually belong:

| Landmark | Position |
|---|---|
| Orgrimmar gate | far north-west |
| Drygulch Ravine | north-east |
| Thunder Ridge | north-east, below Drygulch |
| Valley of Trials | west, upper-middle |
| Razor Hill | centre-east |
| Skull Rock | east coast, centre |
| Rocktusk Farm | south-centre-west |
| Tiragarde Keep | south-east coast |
| **Kolkar Crag (centaur)** | **south-west** |
| Sen'jin Village | south |
| Scuttle Coast | south-east shore |
| **Echo Isles portal** | **south-east, offshore** |
| Southfury River | western border |

A north-south road runs Orgrimmar → Razor Hill → Sen'jin. The **separate
"Southern Durotar" zone is folded back in** — real Durotar is one contiguous
zone, and its creatures now live in properly-placed subzone regions instead
of a bolted-on second map. Its encounter tables merged into Durotar's.

All portals repositioned to match.

## 3. Map screen (M)

`ui/screens/map_screen.py`. Zones run up to 200x160 against a ~40x22 tile
viewport, so there was previously no way to see a zone's shape or find its
exits.

Shows the full map scaled to fit (aspect-ratio preserved — Durotar is tall,
the Barrens is wide, a fixed rect would distort both), with player position,
portals, NPCs, treasure, and outlined+labelled subzone regions. Terrain is
cached per zone rather than re-rendered each frame. M or ESC closes.

## 4. Fixed: features sealed off by terrain scatter

Random terrain (dense forest on Echo Isles, canyon rock in Durotar) runs
across the whole map and routinely sealed clearings and portal landings into
isolated pockets — **visible on the map, impossible to walk to**. Echo Isles
was the worst case: only **0.7%** of it was reachable from its own portals,
with all three stranded.

Added `ZoneGenerator._carve_path()`, and every hand-placed feature that must
be reachable now carves a corridor back to the zone interior. Cave interiors
get the same treatment — the wobbling corridor could pinch shut and seal the
boss chamber behind solid rock.

After: **all 15 maps have zero stranded portals or chests.** Echo Isles went
0.7% → 95.4%.

Also moved Kolkar Plains off the Crossroads so the hub town isn't inside a
hostile subzone.

## Verified
- 15/15 maps reachable from the start point
- Every portal linked, walkable, with a valid walkable spawn
- All 10 caves entered and exited via real portal use
- Subzone/cave detection correct at 12 tested positions
- XP multipliers confirmed at exactly 1.2x / 1.5x
- All 6 screens render; M toggles the map
- Cave combat resolves and awards bonus XP

## Files
**New:** `ui/screens/map_screen.py`
**Modified:** `world/tilemap.py`, `world/zone_generator.py`,
`world/zone_manager.py`, `world/portal_manager.py`,
`ui/screens/overworld_screen.py`, `core/game_state.py`,
`core/game_states.py`, `data/creatures/encounters.json`

## Still open
- Cave bosses spawn from the normal weighted table rather than as a fixed
  spawn at the deepest point — the bestiary calls for fixed spawns and no
  respawns until you leave. Needs a spawn-point system.
- `tools/add_zones.py` still emits a "Southern Durotar" block that is now
  folded into Durotar on load. Harmless, but worth cleaning if you re-run it.

---
---

# ADDENDUM 6: TOWNS, CAVE BOSSES, ORGRIMMAR, ZEPPELIN, TIRISFAL GLADES

**World: 22 maps — 10 zones + 12 caves. Two continents.**

## THE BIG ONE: collision was inverted game-wide

`Tilemap.is_walkable()` returned `not is_walkable(collision_tile)`. Every
collision tile in tiles.py is flagged `walkable=False`, so `not False` made
**walls, trees, rocks and cliffs all passable** — while `bushes`
(`walkable=True`) became a solid wall.

Every collision tile in the game did the exact opposite of its job. All my
earlier connectivity numbers were meaningless: nothing was blocking anything.
Fixed, and every map re-validated against real collision.

Related: **`wood` is not a walkable tile type**, so using it as a floor made
Ratchet's docks, the zeppelin platform and building interiors impassable.
Walkable surfaces now use `stone`. `_carve_path`/`_carve_landing` also now
replace *any* non-walkable base tile, not just water.

## 1. Cave bosses + fixed spawns

Caves used the same weighted random roll as open zones, so the boss was just
another table entry — you could fight Gazz'uz three times in the entrance
chamber, or clear the cave and never meet him.

`world/cave_spawns.py` implements the bestiary rules properly:
- **Fixed spawn points** — you see the mob, you fight the mob
- **Exactly one boss, at the boss chamber**, placed rather than rolled
- **No respawns** until you exit and re-enter (verified: clear 11/11, walk
  over them again → 0 re-triggers; leave → 0 spawns; return → 11 again, boss
  alive)
- Trash count scales with cave size (5–16), spaced apart, kept clear of the
  exit and the boss chamber

Bosses are a real wall — at-level tests: 3 wins, 2 losses. Trash always
clears. That's the intended shape: bosses should need gear or talents.

## 2. Caves got spicy — four layout archetypes

| Layout | Feel |
|---|---|
| `chain` | entrance → corridor → boss chamber (classic) |
| `warren` | branching tunnels between many small chambers |
| `cavern` | one huge open space with rock pillars (arena) |
| `spiral` | a single tunnel curling inward to the centre |

Each records `boss_position` so the spawn manager knows where the back is.
All 12 caves assigned a layout; entrance→boss connectivity guaranteed.

## 3. Ratchet & Camp Taurajo

- **Ratchet** (70x60) — goblin port, three docks over open water, a boat,
  two vendors. East coast of the Barrens.
- **Camp Taurajo** (64x56) — tauren camp of round hide tents (not square
  buildings), palisades north and south, vendor. Southern Barrens.

Both are **safe hubs**: explicit empty encounter tables, so they return no
encounter rather than falling through to the Barrens table and spawning
quilboar inside a tavern.

## 4. Orgrimmar (placeholder)

90x80 walled capital: outer wall with a south gate, seven district blocks, a
road grid, two vendors. **Structural only** — no unique content, quests or
interiors. It exists so northern Durotar leads somewhere and the zeppelin
has a home.

## 5. The zeppelin — Durotar → Tirisfal Glades

**Two hops on purpose.** Walk to the tower outside Orgrimmar's gates, climb
the spiral timber ramp, board at the docking platform up top. Crossing
continents reads as a journey rather than one more identical portal tile.

Verified: Durotar (40,8) → Zeppelin Tower → Tirisfal Glades (138,114).

## 6. Tirisfal Glades (150x130, levels 1–12)

Full undead starting zone. Blighted woodland, northern sea, roads linking
everything.

- **Deathknell** (SW) — starting village, buildings, Undertaker Mordo
- **Brill** (centre) — zone hub, Innkeeper Renee
- **Solliden Farmstead** (W) — 4–8
- **Agamand Mills** (N centre) — 6–10, Thurman Agamand
- **Balnir Farmstead** (E) — 7–10
- **Whispering Shore** (N coast) — 5–9, Vile Fin murlocs
- **The Scarlet Watch** (NE) — 9–12, Interrogator Vishas
- **Night Web's Hollow** (cave) — 6–11, Broodmother Nesh'ka
- **Scarlet Crypt** (cave) — 10–15, High Inquisitor Fairbanks

**34 new creatures**, all template+delta. All 5 subzones + 2 caves verified
detecting and spawning at correct level bands.

## 7. Also fixed: towns were being treated as caves

`is_in_cave()` inferred cave-ness from whether `.region` named another map —
but town hubs legitimately name their parent zone, so Ratchet, Orgrimmar,
Camp Taurajo and the zeppelin tower were all getting fixed spawns, cave XP
bonuses and cave encounter lookups. Replaced with an explicit
`Tilemap.is_cave` flag.

## 8. Also fixed: all 4 original vendors were on tiles with no NPC marker

Even after last session's zone-key fix, Old Marta, Kelm, Shu and Gruk were
standing on empty ground — nothing to interact with. Re-homed onto real NPC
tiles. Echo Isles had **no `npc` tile anywhere on the map**, so one was
added. Now 15 vendors, 0 misplaced.

## Verified
- 22/22 maps reachable; every portal linked, walkable, valid spawn
- Zero stranded portals, NPCs or chests **under correct collision**
- All 12 caves: one boss each at the boss chamber, no respawns
- Safe towns spawn nothing
- Tirisfal: all 5 subzones + 2 caves detect and spawn correctly
- Zeppelin round trip works
- All screens render in every new map

## Files
**New:** `world/cave_spawns.py`, `tools/add_tirisfal.py`
**Modified:** `world/tilemap.py` (**collision fix**, `is_cave`),
`world/zone_generator.py`, `world/zone_manager.py`, `world/portal_manager.py`,
`ui/screens/overworld_screen.py`, `data/creatures/*.json`,
`data/npcs/vendors.json`

## Still open
- Cave spawns aren't drawn on the overworld yet — you walk into them blind.
  `cave_spawns.active_positions()` returns `(x, y, is_boss)` ready to render.
- Orgrimmar is structure only; Tirisfal has no quests (no quest system yet).
- Boss fights are single-phase; multi-phase is Phase 8.
