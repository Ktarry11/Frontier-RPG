# FRONTIER RPG — SESSION HANDOFF
## Party System, Stormbringer (first CoA class), and Playtest Bug Pass

**Status:** Playable end-to-end. All changes compiled and verified headless.
**Save version:** 5
**Scale:** 65 Python files, ~14,300 lines
**Build:** `frontier_rpg_party.zip`

This supplements `HANDOFF_MASTER.md`, which is still accurate for everything
it describes. This document covers what changed in this session.

---

## 1. WHAT CHANGED — QUICK NUMBERS

| | Before | After |
|---|---|---|
| Playable classes | 9 | **10** (Stormbringer added) |
| Abilities | 79 | **89** |
| Talent trees | 27 | **30** |
| Talents | 621 | **678** |
| Combat | 1v1 only | **up to 5v N** |
| Recruitable companions | none | **4, in Valley of Trials** |
| Save version | 4 | **5** (party + recruit state) |

---

## 2. THE PARTY SYSTEM (new — the big one)

### Design, as confirmed by Kyle

- **5 in the active party, player included.** Unlimited bench.
- Companions are **full `Character` objects** — same gear, abilities,
  resources, ranks and levelling as the player. There is deliberately no
  parallel lightweight companion class to maintain.
- **The player controls every member, FF-style. There is NO companion AI.**
  This was a large scope saving — every ally takes its own turn on the shared
  turn meter and the human picks the action.
- Companions are **spec-locked**. Class and spec are fixed at recruitment and
  are their identity ("loved healing on Earth, now a Resto Druid"). They still
  earn talent points but should only spend them in their one tree.
  **⚠️ The data is set (`Character.locked_spec`) but the talent screen does not
  yet enforce it** — see Section 6.
- **Benched members earn 50% XP** (`Party.BENCH_XP_RATIO`) so they fall behind
  without rotting into unusable dead weight.
- Recruits are scattered across the world as **exploration content**.

### Rows — soft, per Kyle's choice

Every ability stays usable from either row; position only applies incoming
damage modifiers. `entities/party.py` → `ROW_DAMAGE_MODIFIERS`:

| Row | Physical | Magic |
|---|---|---|
| Front | 1.15x | 0.95x |
| Back | 0.70x | 1.05x |

Enemy AI **preferentially targets the front line** (`default_target_for`),
falling back to any living ally when the front row is gone. This is what makes
rows matter — verified in simulation, enemies only ever struck the two
front-row members while the healer and hunter stayed clean.

Applied in `Character.take_damage()` AFTER armor mitigation, so it modifies
real incoming damage rather than being swallowed by the mitigation curve.

### The engine rewrite

`CombatEngine` no longer has a `player`/`enemy` pair. It now owns
`self.allies` (the party's members) and `self.enemies` (a list).

- Old 1v1 signature `CombatEngine(player, enemy)` **still works** — it builds a
  one-member party against a one-member enemy group.
- Turn meter runs across all combatants at once.
- XP sums across every enemy, then `Party.award_experience()` distributes it.
- Loot rolls **once per enemy**; everything goes to the player's bags.
- Victory = all enemies down. Defeat = **party wipe**, not player death.
- A combatant who dies to a DoT between turns correctly forfeits their turn.

### Group encounters — and the dungeon difficulty lever

`ZoneManager.trigger_encounter_group(player_level, party_size)`:

```
count = max(1, (party_size + 1) // 2)     # 5 party members -> 3 enemies
if cave:     count += 1
if subzone:  count += 1 when party_size >= 4
```

**This is the difficulty knob for dungeons.** Raising the cave modifier makes
caves genuinely harder without touching a single creature stat block. Fixed
cave spawns stay single-mob deliberately — "you see the mob, you fight the
mob" is the existing design.

### UI

- **Party roster strip** (left side of combat): per-member HP + resource bars,
  `[F]`/`[B]` row tags, acting member highlighted, downed members greyed.
- **Every enemy gets a bar** on the right, dead ones greyed but still listed.
- The left panel and hotbar **swap to whoever is acting**, using their ability
  book — not always the player's.
- Heals/HoTs auto-target the **most wounded living ally**.
- The turn gate is now "is an ally acting", not "is the player acting".

### New/changed files

| File | What |
|---|---|
| `entities/party.py` | **NEW** — Party, rows, bench, XP distribution |
| `world/recruit_manager.py` | **NEW** — recruit NPCs, themed starter gear |
| `data/npcs/recruits.json` | **NEW** — the 4 companions |
| `combat/combat_engine.py` | Rewritten to allies[]/enemies[] |
| `ui/screens/combat_screen.py` | Acting-member control, roster, multi-enemy panel |
| `ui/screens/overworld_screen.py` | Recruitment on Space, group encounters |
| `world/zone_manager.py` | `get_recruit_at_location`, `trigger_encounter_group` |
| `world/zone_generator.py` | 4 new NPC tiles in Valley, carved + validated |
| `core/game_state.py` | `get_party()` |
| `core/save_system.py` | Party + recruit persistence, `load_full_save()` |
| `entities/character.py` | Row damage modifier in `take_damage()` |

---

## 3. THE FOUR RECRUITS

All in **Valley of Trials**. Press **Space** on their tile.

| Name | Class / Spec | Tile | Row |
|---|---|---|---|
| Dan Okafor | Warrior — Protection | 28, 34 | Front |
| Ama Boateng | Priest — Holy | 86, 46 | Back |
| Silas Vance | Rogue — Combat | 52, 88 | Front |
| Rosa Delgado | Hunter — Marksmanship | 100, 78 | Back |

Classic 5-man composition: tank, healer, melee DPS, ranged DPS, plus the
player. Each has an Earth backstory tied to the role they always played.

They arrive in a **themed Common-quality starter set** (`GEAR_THEMES` in
`recruit_manager.py`) — Dan in 7 pieces of plate with a shield, Ama in cloth
with a staff. Deliberately basic; the real gearing is the player's job.

**Every recruit tile calls `_carve_landing()` before placement and was
verified walkable.** Vendors previously shipped standing on tiles that terrain
scatter had sealed off, and the entire vendor system silently did nothing as a
result. Do not place a world feature without validating reachability.

---

## 4. STORMBRINGER — first CoA class, and the dual-resource system

### The mechanic

Stormbringer is a **builder/spender**. Mana-cost abilities BANK Static;
Static-cost abilities spend it for the payoffs. Static caps at 100 and decays
2/step out of combat like Rage, so you cannot walk into a fight pre-loaded.

Verified rotation:
```
Aeroblast          FAIL  static=0   "Not enough static (need 50)"
Forked Lightning   ok    mana 705->664   static 15
Electrocute        ok    mana 664->618   static 35
Gale               ok    mana 618->590   static 55
Aeroblast          ok    mana 590        static 55->5
```

### What was built underneath (generic, benefits all 21 CoA classes)

- **`Character.secondary_resources`** dict + `get_resource()` /
  `spend_resource()` / `gain_resource()` / `set_resource()`. Keyed by
  `ResourceType.value`. **This did not exist** — the docs claimed Character
  tracked a pool per secondary resource; it tracked nothing.
- **`generates` on Ability** — `{"resource": "static", "amount": 20}`. This is
  the builder/spender primitive every CoA class needs.
- `_has_resource` / `_consume_resource` are now fully generic instead of a
  four-branch if-chain.
- `SECONDARY_DECAY_PER_STEP` for resources that bleed off out of combat.
- Secondary resource bar in combat UI, colour-coded per resource type.

### Data

- 10 abilities / 32 ranks in `data/abilities/stormbringer.json`
- 3 talent trees × 19 talents: **Wind / Maelstrom / Lightning**
- `tools/talents_coa.py` — **NEW**, the authoring source

**⚠️ Correction to `COA_21_CLASS_RESOURCE_REFERENCE.md`:** that document guesses
the specs are "Lightning / Thunder / Winds" from fan wikis. The real specs, per
in-client screenshots, are **Wind / Maelstrom / Lightning**. Maelstrom replaces
Thunder. Also, `CLASS_RESOURCE_MAP` now maps Stormbringer to
`(MANA, STATIC)` — Mana is primary because it gates the rotation.

### Honest caveats

- Talent **effects** are calibrated for this engine, not copied from CoA.
  Real Aeroblast is `109+0+NatP*0.635`; there is no Nature Power stat and no
  `COND(GT(FroP, NatP))` support. Names and structure are authentic; numbers
  are tuned.
- Mechanics the engine can't express yet were made stat/damage talents rather
  than fake capstones: Air Elemental (needs pets), Storm Ascendance
  (transformations), charge-based abilities, AoE.

### The CoA data pipeline (proven, reusable)

**Kyle's format works — docx export + in-client screenshots per class.**

- The **docx** gives costs, cast times, cooldowns, damage formulas, and
  **~116 embedded ability icons** (this solves item #14 for free).
- The **screenshots** give spec tags, level requirements, and the
  Talent/Ability/Class/Passive taxonomy — none of which the docx exposes.
- They are complementary, not redundant. Roughly 15 abilities appear in the
  screenshots but not the docx. **Always send both.**
- Skip entries flagged `Deprecated`, `DEPRECATED`, `NEEDS REDONE`, `Unused`.

---

## 5. BUGS FIXED THIS SESSION

The pattern that matters: **most of these were systems that were fully
written, documented as complete, and had never once executed.** That is now
seven or more occurrences in this project.

1. **Vendors were completely broken** (`vendor_screen.py`) — four stacked
   bugs, three of which had never run:
   - 13 `draw_text()` calls using `font_size=`, `center=`, and separate `x, y`
     args the Renderer never accepted. Crashed on the first draw call.
   - Every reference used `self.game_state_manager`; `BaseScreen` stores
     `state_manager`.
   - Every reference used `.character`; the manager holds `.player`.
   - The screen was cached forever, so the second vendor would show the
     first's stock.
   **Fix:** `Renderer.draw_text()` upgraded to accept tuple *or* `x, y`, plus
   `font_size` (cached) and `center`. Backward compatible.

2. **No stat growth on level-up (#23).** `_apply_level_scaling()` existed and
   was correct but was **only ever called at character creation**. A level 60
   character had the exact core stats of a level 1 one. It used `+=` on
   current values so it couldn't just be re-run. **Fix:** snapshot level-1
   stats into `Character.class_base_stats`, recompute from that every time —
   now idempotent. Verified Warrior L1 `15/14/10, 212 HP` → L60 `74/67/33,
   636 HP`, and running it twice changes nothing.

3. **Talent points could never be spent (#54).** `talent_points_available` was
   set once at creation. Create at level 1 → 0 points → level to 30 → still 0.
   The spend logic was fine; it never had points. **Fix:**
   `_grant_talent_points()` *derives* `(level - 4) - points_spent` rather than
   incrementing, so it can't drift and self-corrects on load.

4. **DoT/HoT ticking (#9).** `_end_turn()` ticked status effects **and
   cooldowns** for *both* combatants on *every* turn, so every duration in the
   game was effectively halved — unevenly, since the turn meter lets a fast
   combatant act twice. **Fix:** only the actor whose turn just ended
   advances. Verified `4 → 3 (player turn) → 3 (enemy turn) → 2 (player turn)`.

5. **Static silently billed Mana.** `_RESOURCE_BY_NAME` only listed
   rage/energy/mana/health, so `"static"` fell back to MANA. Aeroblast was
   castable at 0 Static. **Fix:** derived from the enum
   (`{rt.value: rt for rt in ResourceType}`), plus generator validation of
   resource names and `generates` targets.

6. **Prestige was anchored to level 100 (#20)** in the UI while
   `config.PRESTIGE_LEVEL` has been 60 throughout. Also `prestige()` reset to
   level 1 but never re-derived stats — you'd keep level-60 stats through a
   prestige. Both fixed.

7. **No equip restrictions existed at all (#13).** A Priest could wear plate.
   **Fix:** `entities/proficiency.py` — WoW-style ladder, your class's armor
   type plus everything lighter. Paladin → all four, Priest → cloth only.

8. **Loot was 100% tailored to the player's class (#12).** Now rolls across
   the full 9-class pool with a **35% soft bias** toward your own class, so
   progression doesn't stall but gear for other classes exists in the world —
   which the party system needs.

### Also completed

- **#15/#38** Combat log reports XP and per-level stat gains
- **#16** Overworld HP + class resource bars
- **#17** Armor tooltips show real damage reduction — computed as the
  *difference the piece makes at your current armor*, since armor has
  diminishing returns and a flat "12 armor = X%" would be a lie
- **#18** Core stat hover shows what each stat feeds
- **#19** Grey/Poor items enabled (drop_weight 18)
- **#53** Talent tooltips follow the mouse (previously required clicking —
  you had to spend the point to learn what it did)
- **#5** Vendors (see above)

`Character.mitigation_from()` is now the single source of truth for the armor
curve, shared by `take_damage()` and both tooltips.

---

## 6. WHAT STILL NEEDS FIXING

### Blocking — do these first

1. **Save/load has no load path (#22).** `load_character()` is **never called
   by anything in the game**. The v5 format writes party + recruit state
   correctly, but nothing reads it back. Recruit a party, close the game, it's
   gone. Also blocks Kyle's friend testing.
2. **No party management screen.** You can recruit five people but cannot swap
   rows, bench anyone, or equip a companion. Their gear is frozen at whatever
   they arrived in.
3. **Companion spec-lock is not enforced.** `Character.locked_spec` is set
   correctly on recruits, but `talent_tree_screen.py` ignores it — Ama can
   currently spend points in Shadow. Small fix; flagged because it is
   otherwise a fake-finished system.

### Combat & mechanics
- **#4/#52** Enemy mana pools — casters spam Dark Mending with no cost
- **#1** Out-of-combat casting (heals/buffs)
- **#2** 30-minute real-time buffs instead of turn-based
- **#3** Spirit-based HP regen per step
- **#8/#50** Ability naming — Kul Tiras Sharpshooters use "Gore", Scarlet
  Crusade casts Shadow Bolt (they're holy)
- **#21** Pet + transformation system (warlock pets, druid forms, Air Elemental)
- **#39** Treasure chests do nothing

### Zone routing — one cluster, one root cause
**#6, #25, #27, #31, #36, #44, #45.** The portal graph is wrong. Echo Isles →
Razor Hill should be Sen'jin Village (new town); Zeppelin Tower always dumps
you in Orgrimmar regardless of origin; the Barrens' west portal loops to
Durotar; Camp Taurajo spits you out the wrong side; attacks happening in
Crossroads. Do these together.

### Terrain & tilesets
**#7, #28, #29, #30, #32, #47, #49** — Tiragarde tiles, biome lushness
(Barrens/Valley less green, Tirisfal more rotted), oasis creatures
(centaur/turtle/raptor/kodo, no silithid), Wailing Caverns entrance at
Lushwater Oasis, house tiles, Durotar rock density + cacti.

### Dungeons — **now unblocked by the party system**
**#10, #40, #41, #42, #43, #48.** Cave mobs drawn on the map with boss icons,
real dungeon tilesets, expanded group-oriented layouts, elite mobs, guaranteed
blue boss drops (Skum's dagger). Group-encounter scaling is already the
difficulty lever.

### UI
**#24, #33, #34, #37, #46, #51** — centering, redundant legend, vertical
layout for a bigger viewport, oversized SHIFT display, dots rendering
off-screen, names overflowing. **#48** (can't see walls) is closer to a real
bug than polish.

**#14 Spell icons** — largely solved by accident; the CoA docx exports carry
~116 embedded icons each.

### Content
**#23** Races (stat growth done, races not) · **#26** Item naming (plate called
"tunic") · **#11** 2×2 portals · **20 remaining CoA classes**

---

## 7. RECOMMENDED NEXT STEPS

1. **Save/load** — protects the party that was just built, unblocks external testing
2. **Party management screen** — completes the party system
3. **Dungeons** — the fun part, and finally unblocked

---

## 8. WORKING PRINCIPLES (unchanged, and repeatedly validated)

- **Read the real code before claiming anything works.** Seven-plus systems in
  this project shipped, were documented as complete, and had never executed.
  Anything documented as done but never *observed in play* is unverified.
- **Single source of truth.** `CLASS_RESOURCE_MAP`,
  `get_exp_needed_for_level()`, `mitigation_from()`, `_grant_talent_points()`.
  Duplicate a formula and it *will* drift.
- **Derive, don't increment.** Talent points and level scaling both broke
  because they accumulated state. Both now recompute from a fixed baseline.
- **Validate geometry, don't assume it.** Every hand-placed feature that must
  be reachable calls `_carve_path()` / `_carve_landing()` and is verified.
- **WoW authenticity is the benchmark.** Mana costs scale per rank;
  Rage/Energy/Static stay flat.
- **Playable at every phase.** The principle that keeps this from becoming the
  stalled JRPG.

---

## 9. RUNNING IT

```bash
cd frontier_rpg/
pip install -r requirements.txt
python3 main.py
```

**Controls:** WASD move · Space interact (vendor / recruit / portal) ·
1–0 and Shift+1–0 hotbar · M map · ESC back
