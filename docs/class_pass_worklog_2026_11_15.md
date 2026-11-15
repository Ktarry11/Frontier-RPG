# Class pass work log, 15 Nov 2026 (Rafa)

Kyle (09:38 local): "Keep detailed logs of what you're doing in case of compacted chat! THIS IS CRITICAL BRO! WE WILL NEED DETAILED RECORDS!!"

This is the running record of the class pass: every change, why it was made, what it measured, and how to resume. Times are UTC, and Kyle's local time is UTC-7. The design summary lives in `claude/class_balance_2026_11_15.md` (project doc); this file is the blow-by-blow.

**Standing rules for this work**
- Push whatever is fixed as it lands, with the commit trailer.
- Check text encoding before every commit: `PYTHONPATH=. python3 tools/fix_text_encoding.py --check`.
- Never `git stash`.
- **Never say where hidden places are.** Hidden zones are reported by *kind* only.
- QA environment: `PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy`. The machine has 2 cores.

---

## Kyle's mandate today (in order)

1. 07:44: "spending almost all day fixing classes. All 9 classic classes and coa classes. All specs, ability ranks.....everything."
2. Multiple passes: naked, under, geared, over gear; under and over level; tanks, healers and DPS; mana levels. "Casters should oom longer fights."
3. Classes "unique but not wildly different": Wrath ≈ Lightning Bolt ≈ Shock. TBC-era mana (not WotLK infinite, not Cata 3 casts).
4. His picks:
   - 3–4 casts to kill a normal mob.
   - Per-ability coefficients.
   - About 20 turns to run out of mana.
   - The TBC five-second rule.
   - Costs normalised per class.
   - Damage specs within about 10% of each other.
   - Meditation-type talents at 17/34/50%.
   - Rime's Ice Mastery at 15%.
   - Grovekeeper and Cryotherapist at 75% of a healer.
5. "Bro I don't think ranks are scaling!", "a Healer should not fucking heal the same 14 levels later". Reference: Classic Lightning Bolt is about 20 at rank 1 and 430–470 at 56.
6. "Higher rank spells scale more from spell power, attack power, and healing power than low rank ones do. Wow also does this."
7. "Each spell rank or ability rank should FEEL like an actual step." He picked **"Steeper world from ~20 up"** and showed Healing Touch going 40–55 to 2,267–2,677, with mana 25 to 800.
8. "Spells and heals have ranges!" Spells and heals already rolled ±9%, and the hybrid tooltips now show it.
9. Spell power is NOT shown in the tooltip, and he does NOT want a "+X from spell power" line.
10. "do it a 3rd time. Then a 4th... Push the system to check for any breaks! Check class viability. Check end game Dungeons. Check frontier zones."
11. "Try everything. Specs, classes, different talents. Buffs, professions... Can every Healer be viable? Every tank? Dps? Is support useful or a waste of space?"
12. "Are classes viable at each step? 1-15, 16-30, 31-45, and 46-60... What's the point of 30 classes if 90% of them suck."
13. "test in open world, Dungeons, skull zones (open and dungeon) and frontier zone (open and dungeon)... exhaustive... We won't be adding more cool places until it's fully done."
14. "a lot of coa classes are builder and spenders... think like combo points and rage."
    - Checked: every spender has a FIXED cost (Eviscerate 40 combo, Torrential Wrath 40 static), and nothing scales with banked points. So the sim's "cast the spender as soon as you can pay" is optimal play.
    - Builders below the line and spenders above it is by design. The line audit must not flag spenders.

---

## Commits today (class pass), oldest first

| Commit | What | Why / numbers |
|---|---|---|
| f5e71e8 | Free actions: only cooldown buffs skip the end of the turn | 235 abilities (Searing Pain, CC, heals, summons) were free actions |
| df7e78d / 77a3fa2 | `combat/ability_scaling.py`: ranks, per-ability coefficients, calibration | First curve: x1 to 20, rising to x1.6 at 60 (later replaced) |
| 40d98ef / d365d3c / ac917c7 | Rank gaps filled, early-stopping abilities extended to 58, ranks above 60 pulled down | `tools/fix_ability_rank_levels.py`; migration file in `data/migrations/` |
| 657849e / 8895ba1 | Status `max_health_pct` etc. are FRACTIONS | Witch Hunter 6x and Guardian 9x max-health procs |
| 7e22131 / 4053115 | Mana economy | Five-second rule (`CASTING_SPIRIT_REGEN` 0.30); per-class costs to ~20 turns; refunds as % of the bar; clearcasting fixed; spirit 0.6 a point; Meditation-type talents 17/34/50% |
| 13c54cf | Knight of Xoroth builds rage from combat | — |
| 12e18f5 | Feral rebuilt on combo points; parity sims; two-handers no longer stripped in the sims | — |
| 35d782e | A refunded cast is refused | Judgement with no Seal ended the turn |
| 431ece4 | Healing auras; Vizier heal at 6; Felsworn Tyrant defensives trimmed; Rime damage talents halved | — |
| 1d95093 | Ranks track monster health from level 1; Classic low-level and downrank penalties; battle rezzes are revives | — |
| **168bfd0** | **THE STEEPER WORLD**, see "The world curve" below | Fireball 44→1,110 at 56; Heal 54→1,225 at 50 |
| 1698fa9 | Pets take the rank curve; sims summon screen pets; Aspect of the Viper; mana costs from the real rotation | — |
| b1d3155 | White damage at full power; recruit kits re-sized; viability harness | — |
| c3eeb9b | Viability harness: content, hidden and consumables modes | — |
| 60abb3d | Necromancer Lichfrost and Crypt Swarm x0.75 | Free builders hit at a full nuke's value |
| 6052b2a | Sun Cleric Illumination on the healer line; heal parity counts shields | — |
| 74846c5 | Tank sims without screen pets | A pet soaked the hits, so "turns alive" was garbage |

---

## The world curve (`combat/world_curve.py`), the core of the "steeper world"

**Growth:** `growth(L)` compounds per level. The rate starts at 13% at level 1 (`R_START`), eases to 3.5% by level 30 (`R_LATE`, at `KNEE`), and holds there. That's ×2.2 at 8, ×6 at 20, ×10 at 30, ×15 at 40, ×20 at 50 and ×29 at 60. The old line was 1 + 0.15(L−1), which is ×10 at 60.

**Scale:** `world_scale(L) = growth / old line`, which is ×1.0 at level 1, ×1.6 at 20, ×2.1 at 40 and ×2.9 at 60.

**Where it applies:**
- **Monsters** (`entities/monster.py`): health, attack and spell power, and mana use `growth(L)`. Kit damage, heal and DoT amounts are ×`world_scale(L)`. Buffs and debuffs aren't scaled (they're percentages). Armour stays on the old line (it's mitigation).
- **Free pets** (`entities/pet.py`): the same as monsters. Pet abilities' `power_scale` is also × `rank_multiplier(pet level)`. Pets built off their owner follow the owner.
- **Characters** (`entities/character.py`):
  - In `_recalculate_derived_stats`: health, mana, attack power and ranged attack power ×`_ws` (sheet values).
  - At combat read: spell and healing power (`get_effective_spell_power`, `combat_spell_power`, `combat_healing_power`).
  - The weapon roll (`get_weapon_damage_roll`).
  - In-combat regen (`mana_per_turn`) and hp5.
- **Out-of-combat regen:** `combat/status_effects.py` `tick_out_of_combat_regen`.
- **Flat procs** (`status_effects.py`): `heal_flat`, `damage_flat` and flat `smart_heal`, at the carrier's world scale.
- **Consumables:** `Consumable.restore_amount(level)`. Potions use the drinker's level; meals and drinks use their own `required_level`. The bag tooltip, the professions screen and `use()` all call it, and 119 potion and food descriptions lost their hard-coded "Restores N".
- **Ranks:** `ability_scaling.rank_multiplier(lr) = growth(lr) / (1 + 0.03636(lr−1))`, applied in `curved_ranks` to `effect_value`, `heal_value` and `absorb`.
- **Switch:** `FRONTIER_WORLD_CURVE=off` puts everything on the old line.

**Rank steps:**
- Fireball: 44 → 83 → 154 → 255 → 376 → 514 → 662 → 856 → 1,110, which is +89%, +86%, +66%, +47%, +37%, then about +30% a rank.
- Heal: 54 → 123 → 241 → 405 → 581 → 748 → 957 → 1,225.
- Normal mob health: 120 at 1, about 4,400 at 56.
- Fights hold at 2.2–3.0 turns to kill at 20–60, the same as before the change.

**Coefficients** (`ability_scaling.coefficient`): a base by kind (SP 1.5, HEAL 1.2, AP 0.5, DOT_SP 1.0, DOT_AP 0.3, HOT 0.8) × a cooldown weight × an AoE share.
- **Low-level penalty:** −3.75% per level under 20, but ONLY while a higher rank exists. The top or only rank (Attack, Shoot, Wand) always gets 100%. Fixed in b1d3155; before that, white damage was at 29%.
- **Downrank penalty:** (next rank's level − 1 + 6) / caster level, capped at 1.
- **Pets:** pet casters (`char_class == "Pet"`) are exempt from both penalties.

---

## Calibration data (rerun after any kit or talent change)

```
PYTHONPATH=. python3 tools/calibrate_mana_costs.py --write                 # ~1 min; damage rows from the real rotation (6 samples)
PYTHONPATH=. python3 tools/calibrate_spec_auras.py --kind damage --passes 5 --write   # ~25-40 min
PYTHONPATH=. python3 tools/calibrate_spec_auras.py --kind healing --passes 5 --write  # ~10 min
```

- `data/balance/mana_costs.json`: multipliers per class, kind and level, so a rotation lasts about 20 turns from full.
- `data/balance/spec_auras.json`: hidden per-spec damage and healing multipliers, clamped to 0.35–1.75.
  - At 1.75 the kit is too weak, so fix it by hand.
  - Below 0.5 the spec stacks too much, so look at its tree.
- **Last damage aura run** (before the white-damage and Necromancer fixes, so it's stale): 20 spec-levels at the clamp.
  - Feral at 10 and 40–60; Enhancement at 10, 20, 50 and 60; Hunters (all three) at 30–60; Assassination at 20 and 30; Subtlety at 30; Godblade, Stalking and Balance at 10–20.
  - Low (overtuned): Necromancer, all three at 0.41–0.79; Stormbringer around 0.65; Knight of Xoroth 0.54–0.86; Cultist Corruption and Godblade around 0.65; Starcaller Sentinel around 0.58; Venomancer Venom around 0.62.
- **Last healing aura run:**
  - Cryotherapist about 0.8.
  - Clamped: Tinker Invention at 60 (0.27), Vizier at 10 (2.7), Cryotherapist at 10.
  - Since then Zap and My Greatest Invention were fixed, Illumination was fixed, and shields are counted, so it **needs a rerun**.

## Measuring tools

| Tool | What |
|---|---|
| `tools/sim_dps_parity.py` | Damage per turn of every damage spec on one target. `--seed`, `--passes`, `--json`. `damage_per_turn(..., mana_stats={})` measures rotation mana spend. |
| `tools/sim_heal_parity.py` | Healing per turn. Counts every `heal()` in full (overheal included) plus shields. Hybrids use `HYBRID_HEALERS` (75%). Cryotherapist fights. |
| `tools/sim_matrix.py` | Spec × gear tier × level offset × role. Tanks get turns alive and damage taken. `--endurance-only` gives mana endurance. `build()` summons the pet-screen pet for non-tanks. |
| `tools/sim_class_balance.py` | Turns to kill, win rate and health left, every class with talents. |
| `tools/sim_difficulty.py` | Open world (1, 2 and 3 mobs) and dungeon bosses with parties of 5 and 3. |
| **`tools/sim_viability.py`** | Modes: `solo`, `group`, `hidden` (by kind), and **`content`**: every spec in its party slot against dungeon, skull_open, skull_dungeon, frontier_open and frontier_deep, trash and bosses, every bracket. Flags: `--no-talents`, `--no-buffs`, `--tier`, `--consumables`. |
| `tools/audit_ability_ranks.py` | Rank stalls, gaps, wobble, cost. |
| `/tmp/claude-0/breakdown.py LEVEL spec...` | Scratch: damage per turn by ability (spec aura off). Recreate if lost. |
| `/tmp/claude-0/heal_breakdown.py LEVEL spec...` | Scratch: healing per turn by ability. |
| `/tmp/claude-0/audit_lines.py` | Scratch: authored value per rank against the main-spell line, adjusted for cooldown and AoE. Over 2x: 65 abilities. **Builders and spenders are NOT bugs.** |

---

## Findings so far, pass 3

**Solo viability** (`--mode solo`, levels 12, 25, 38, 52 and 58)
- Geared with talents, every spec wins a single same-level mob, except three small-sample cases (Frost Mage at 52, Vizier at 58, Witch Doctor Brewing at 38). Rerun those.
- Danger: geared with talents loses only 1–10% of health to one mob. Green gear with no talents loses 15–30% (88–95% wins), and two mobs win 36–60% of the time. That matches Kyle's target ("one mob ≈ a third"), so open-world numbers are left alone.

**Hidden content by kind** (talented, geared, at the creature's level)

| Kind | Party of 3, 2 trash | Party of 3, boss | Party of 5, boss |
|---|---|---|---|
| Skull zone | 100% | 75% | 100% |
| Hidden layer | 100% | 50% | 100% |
| Frontier (deep) | 75% | 25% | 100% |

- Kyle's friend's Shoals struggle: his group was under-level (15–19), with untrained ranks, on the old build. Players buy ranks from trainers; recruits auto-train.

**Tanks** (`sim_matrix --roles tank`, without pets): 9–39 turns alive. Felsworn Tyrant and Seraphim lead (37–39 at 58); Mountain King and Black Knight trail (17–19 at 58). Venomancer Fortitude is 11 at 25. That's about a 2x spread, so look at the tails.

**Healers:** Resto Shaman's edge is its talents (Healing Wave is on the line), and the aura absorbs it. Discipline now measures 0.95–0.97 of the median, with Holy at 1.03–1.05.

**Hunters:** they had no mana tool, so Viper was added (placeholder icon `assets/icons/abilities/hunter_aspect_of_the_viper.png`, copied from `coa/viper_ward.png`; **needs art**). Their accuracy is fine. With the pet now full size (about 183 a turn at 60), BM is about 1,180 a turn against Demonology's 2,180 with auras off. The aura covers the rest.

**Pre-existing content gap:** `qa_gathering_legality` fails because no ore above Thorium is placed and no endgame wood is placed (it fails at 1d95093 too).

**QA fixed today for the world curve:** `qa_effects_end_with_combat`, `qa_gear_sets` and `qa_food_drink` (amounts on the curve), `qa_kit_ranks` (curved), `qa_kit_abilities_batch8` (Duel ÷ aura), `qa_asher_locked` (one dash became ", and" in the [47] pass; hash updated, punctuation only), and `qa_spell_range_on_tooltip` (slack grows with the range).

---

## Parked (Kyle said note it only; class balance comes first)

- **16:41 UTC.** Hand-authored boss drops convert from percentage hit, crit, dodge, parry and so on to RATINGS (10 rating = 1%, like gems and crafted gear), cleaning out the "trash drip" stats. This is item 8 in `claude/playtest_backlog_2026_11_14.md`.

## Running right now (16:38 UTC)

- `--mode content --fights 3` geared with talents writes `/tmp/claude-0/content_geared.{log,json}`.
- `--mode content --fights 3 --tier under --no-talents --seed 2` writes `/tmp/claude-0/content_under.{log,json}`. Started 16:30; expect about 40–60 min.
- The full QA suite is in its tail (`/tmp/claude-0/qa_*.log`, failures in the task output).

## Next (pass 3, then pass 4)

1. Read the content sweeps: specs well behind their role (`report_content` "BEHIND"), any content kind that fails outright, and support specs against a plain DPS.
2. Recalibrate damage and healing auras (stale after the white-damage, Necromancer, Illumination, Zap, Invention and shield-counting changes), then verify parity on `--seed 2`.
3. Fix kits at the clamp by hand (Feral, Enhancement, Hunters, Assassination and Subtlety at 20–30), checking builder/spender economy first.
4. Tank tails (Mountain King, Black Knight, Venomancer Fortitude) and the healer tails.
5. Pass 4: the full matrix again (naked, under, over gear × under and over level), `--no-buffs`, `--consumables`, and a fresh seed. Then a support analysis (party kill turns with a support spec against a plain DPS).
6. Keep this log and `claude/class_balance_2026_11_15.md` current after every step.
