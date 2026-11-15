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

## Content sweeps (16:30–16:50 UTC, `--mode content --fights 3`)

**Geared with talents** (`/tmp/claude-0/content_geared.{log,json}`)
- Every spec in its slot of the standard party clears every content kind in every bracket. The median win rate is 100% everywhere.
- The only friction is skull-dungeon (hidden layer) trash at 16–30: DPS and tank slot medians are 67%, with a range of 0–100%.

**Green gear, no talents** (`/tmp/claude-0/content_under.{log,json}`)
- Regular dungeons: the median is still 100% in every bracket (some DPS swaps dip to 33% on 46–60 bosses, but at 3 fights that's noise).
- Hidden-layer and frontier-deep trash pulls of 3 win only 0–50%, while their **bosses win 67–100%**. That's an inverted difficulty: hidden bosses get the hidden multiplier on base boss stats, and each trash mob gets the same multiplier, three at a time. **This is a content-tuning question for Kyle** (raise hidden bosses, or make the packs smaller).
- No frontier-open creatures exist yet (both frontier zones are deep).

**Reading:** group results prove nothing is broken for any spec, but the other four members carry a weak one. Spec quality is judged by the parity sims, solo runs and tank survival, plus the new trio mode (tank, healer and one DPS).

## Kyle's decisions, 09:55–09:58 local (16:55 UTC)

- **The healer test must respect archetypes:** single-target, HoT, AoE and party healers, cleave/smart heals, shields (Discipline's "bubble priest"), and on-hit heals like Earth Shield. Don't call Discipline weaker because shields aren't heals. The plan: a party of 5 under several damage patterns (tank-heavy, raid AoE, mixed), each healer playing its own kit on real mana, scored on the most damage it can keep the party through for 20 turns, per pattern.
- **Long-cast, cheap, big heals against fast, expensive, small ones** (Healing Wave vs Lesser Healing Wave) must each have their place. Kyle picked:
  - **"Speed sets next turn"**, for ALL casters, not just heals. Each spell has a speed: quick means the next turn comes after about 0.6 of a turn, normal after 1, slow after about 1.5. Slow spells are big and cheap per point; quick ones are smaller, pricier per point, and land sooner.
  - **"Add the classic set"**: Classic's fast/slow pairs where a class lacks them (Lesser Healing Wave, Flash Heal, Greater Heal, Regrowth/Healing Touch, Flash of Light/Holy Light), with ranks on today's curve. Icons go to the art backlog.

## Cast speed and the healer kits (built 17:05–17:20 UTC)

**The engine**
- `combat/abilities.py` `CAST_SPEEDS` = {quick 0.6, normal 1.0, slow 1.5}. `cast_speed_value()` reads the ability's `cast_speed` field (a name or a number, clamped to 0.3–2.5); untagged abilities are normal.
- `combat_engine.execute_ability` sets `actor._cast_speed` before `_end_turn`, and `_end_turn` passes it to `TurnMeter.consume_turn(char, speed)`. The meter loses THRESHOLD × speed and may go down to −THRESHOLD, so a slow cast waits longer. Speed 1 behaves exactly as before.
- Tooltips show "Quick cast" or "Slow cast". "Instant" still means a free action.

**The heal pairs** (`line(L) = 54 × (1 + 0.03636(L−1))`, the authored healer line)

| Spell | Speed | Value | Cost | Notes |
|---|---|---|---|---|
| Priest Heal | normal | the line | baseline | unchanged |
| **Flash Heal** (new) | quick | 0.65× | 0.85× | ranks 20–56, cd 0 |
| **Greater Heal** (new) | slow | 1.5× | 1.15× | ranks 40–58, cd 1 |
| Shaman Healing Wave | slow | ×1.5 | ×1.15 | retagged |
| **Lesser Healing Wave** (new) | quick | 0.65× | 0.85× | ranks 20–58 |
| **Chain Heal** (new) | normal | 0.6× each | 1.1× | `target_type` party, `max_recipients` 3, ranks 40–58 |
| Paladin Holy Light | slow | ×1.5 | ×1.15 | retagged |
| Paladin Flash of Light | quick | 0.65× line | 0.85× | retagged |
| Druid Healing Touch | slow | 1.5× line | — | cooldown 2 → 1 |

- Quick heals give about the same healing per unit of time with about 24% worse healing per mana, and they land sooner. Slow heals give about 30% better healing per mana, but late.
- **Icons:** Flash Heal, Lesser Healing Wave and Aspect of the Viper are the real WoW icons (the WotLK glyph set already in the scratchpad, 36→56 px). Greater Heal (a brighter Heal) and Chain Heal (Chain Lightning turned green) are stand-ins on the art backlog.
- **Kyle's icon sources:** github.com/orourkek/Wow-Icons (only 111 class and spec emblems), github.com/kodewdle/IconPacks and github.com/AcidWeb/Clean-Icons-Mechagnome-Edition. The last two ship their icons as release downloads, which this workspace can't fetch. They can be used for anything: spells, crafting, loot, vendor trash.
- CoA healers and all damage spells stay normal for now. Kyle: "if we add these fast, normal, slow casts then we need to ensure they're worth it and they're balanced.....so we go through it all again".

**The sims now count TIME, not actions:** `sim_dps_parity` and `sim_heal_parity` run to a time budget, and a cast's speed is the time it takes.

**The healer test** (`tools/sim_heal_scenarios.py`, Kyle's "st, hots, aoe heals, cleave heals... bubble priest... earth shield"):
- The healer plus a Protection Warrior, Fire Mage, Combat Rogue and Marksmanship Hunter, against four patterns: tank 20% a round, AoE 7% each, mixed (tank 12% + everyone 3.5%), and a 45% tank spike every third round.
- Real mana and cast-speed timing. Policy: emergency heal, then party or chain heal, then shields/HoTs/Earth Shield kept up on the tank, then an efficient heal, otherwise wait.
- The score is the highest intensity survived for 20 rounds (binary search, 2 seeds).
- **First results** (old healing auras):
  - Discipline 1.13 and 1.08, above Holy at 0.98 and 0.81, so shields count properly now.
  - Resto Druid 0.84 → **0.57** (tank pattern 0.42).
  - **Sun Cleric Blessings 0.68 → 0.49**: its heals cost about 2x per point, and its old bonus was 0.5–0.7.
  - Grovekeeper 0.65–0.77 (its target is 0.75).
- **Change:** `calibrate_spec_auras.py --kind healing --method scenarios` sets healing auras from this test (the geometric mean of the four patterns). The fighting hybrid (Cryotherapist) keeps its throughput aura. A run started at 17:15 UTC, with the log at `/tmp/claude-0/aura_heal_scen.log`.

**Trio results** (`/tmp/claude-0/trio.log`, old auras)
- DPS groups win 92–100% in every bracket. Tanks are fine except Dreadnought at 31–45 (75%).
- Tinker Invention healer: 25–33% at 1–30. Its kit has Repair Shot from level 2, uses healing power (Kyle confirmed), and carries a musket in the sim, so it's probably noise plus its old aura. Recheck after the recalibration.

**UI note for later** (backlog item 10): hotbar icons with hover tooltips (amount, cast speed, cost), and party buff icons.

## Talents and kits, 17:25–17:40 UTC

- **Dead talents: 99 → 0** (`tools/audit_dead_talent_keys.py`). Stat conversions are implemented (`Character._apply_stat_conversions`, `CONVERSION_TARGETS`). Writhing Mass and Void Resilience now read `shadow_damage_taken_pct`. The audit now knows the engine's dynamic families: per-school and combined-school keys, `ability_<id>_*`, and `scale_talent_key` read from data.
- **Agility melee:** `Character.AGI_MELEE_AP` 0.5 → 1.0 (Classic). Stat tooltips show per-point values at your level.
- `ENERGY_PER_TURN` (25) named but unchanged: measured from 25 to 40, it would push Combat and Subtlety past the pack without fixing Feral or Assassination.
- **Cast speeds on classic damage spells** (`tools/apply_cast_speeds.py`): slow Pyroblast, Starfire, Aimed Shot; quick Fire Blast, Ice Lance, Searing Pain, Conflagrate, Mind Blast, the shocks, Moonfire, Arcane Shot, Holy Shock, Hammer of Wrath.
- `sim_class_balance.plan` ranks attacks and heals per turn of time.
- **Cross-tree talent references** (validate_class): fixed 9 classic talents (Improved Healing → Heal and Greater Heal, Searing Light, Natural Shapeshifter, Incanter's Absorption, Improved Stings, Surprise Attacks, Opportunity). `validate_class`: 0 errors on all 9 classic classes and 20 of 21 CoA classes.
- **For Kyle:** Primalist's 4 shared core abilities (Seismic Wave, Seismic Tremor, Terrasurge, Primal Rush) are each unlocked by one tree but referenced by all four, giving 18 dead references. The recommendation is to make them baseline and turn each unlock node into "Improved X". **Not done; it needs his call.**
- Starcaller Sentinel's Keen Sight converts 10% of Intellect to ranged AP, against 99% on the same key elsewhere. Flagged and left alone.
- Meditation, Arcane Meditation and Intensity are 17% a rank (51%); seven mana refunds were rounded to whole percents. QA fixes: `qa_trinket_procs` (world curve), `qa_spellbook_refine` (Zap's text), `qa_talent_clean_numbers`.

## Pass 4, 17:45–18:30 UTC

- **Damage auras, pass 4:** 10 spec-levels at the clamp (from 14). Still pinned: Feral at 10, 50 and 60; Assassination and Subtlety at 30; Survival at 30 and 60; Stalking and Enhancement at 20; Balance at 10.
- **Cat Form** (`combat/forms.py`): +25% attack power. It gave a flat 20 Agility that never grew, while Classic's cat form *was* the Feral's attack power. A level-50 Cat: 594 → 727 AP.
- **Healing auras from the party scenarios.** A first pass from auras-off overshot (Sun Cleric went from the bottom to the top), because party survival isn't linear in the aura. `calibrate_spec_auras --iterate` measures WITH the current auras and nudges each toward the median (damp 0.7). A run started at 18:05 UTC, logging to `/tmp/claude-0/aura_heal_iter.log`.
- **Rank depth** (Kyle: "appropriate ranks for spells, abilities, buffs ... in line with Classic"). `tools/audit_rank_depth.py` sets per-category Classic norms (direct damage: 5 ranks, one every 9.5 levels, last at 56; heals: 7 ranks every 7.1; DoTs and HoTs similar).
  - **Damage, DoTs, heals and HoTs: 0 thin** in every class, thanks to this morning's rank fixes.
  - Buffs: flat attack/spell/healing power, mp5 and primary stats grow through the world curve (the job Classic's buff ranks did). Percent buffs and flags don't rank, as in Classic, and shields that absorb a share of max health grow with the bar.
  - Armour doesn't scale, so the 5 single-rank armour buffs and debuffs now rank every 12 levels, with only the armour growing.
  - **Engine:** `Ability.stat_mods` is the current rank's own `stat_mods` when the rank carries them.
  - Hunter's Mark (3 ranks) is left alone.

## Sim fidelity fixes, 18:30–18:50 UTC (they change what the auras are set from)

- **DoTs:** the planner valued a DoT at total ÷ duration (a quarter of its worth) and the parity/viability loops refreshed ticking DoTs. Now a DoT is worth 75% of its total per cast and is never recast while it ticks. At 40 with auras off: Affliction 1,117 ≈ Fire 1,120, Shadow 969, Destruction 971, Assassination 922.
- **Mana tools:** `sim_class_balance.mana_tools` / `mana_move`. Under 25% mana a spec uses its restores (Life Tap, Dark Pact, Innervate, Sanity Tap, Satiate, Draconic Invocation, Paradox Cannon, Time Out, Sunstrider Array...). Hunters swap to Viper when low and back to Hawk at 90%. At 50 with auras off: Survival 1,251, MM 1,369, BM 1,236 (Fire 2,043).
- **Rogue poisons** are cast DoTs here (Deadly Poison, 4 turns, cooldown 2), not weapon coatings.
- Starcaller Keen Sight (2%/rank) matches its own CoA tooltip text, so it's left alone.
- A damage aura recalibration (pass 4b) is running, logging to `/tmp/claude-0/aura_dmg_p4b.log`. The healing iteration is at `/tmp/claude-0/aura_heal_iter.log`.

## Pass 5 (Kyle 10:30 local: "Yes to primalist. After this ... relook at the classes, talents, specs ... run everything again with similar and different simulations ... each time we change stuff. So we do it again and again")

- **Healing iteration** landed: all healers 0.7–1.67, only Vizier at 10 clamped. Verified at 30/50: most within ±10%; Sun Cleric 1.31 at 50, Holy 0.84 and Tinker 0.86 at 50. The pass-5 iteration continues this.
- **Damage pass 4b:** 6 at the clamp (Enhancement 20, the three Hunter specs at 30, Survival 50, Feral 60).
- **Primalist (approved):** Seismic Wave, Seismic Tremor, Terrasurge and Primal Rush are core spells learned by level. Their unlock nodes became Improved Seismic Tremor / Seismic Wave / Terrasurge / Primal Rush (+20%; Terrasurge also −1 cooldown). `validate_class primalist`: 0 errors.
- **`tools/audit_ability_lines.py`:** every damage and healing ability against the line, adjusted for cooldown, AoE share, cast speed, over-time totals (1.5x a nuke) and builder/spender role. Physical strikes aren't judged "below" (weapon damage is added on top).
  - **33 weak DoTs/HoTs** (0.1–0.4x, CoA per-tick numbers entered as totals) were lifted to 0.7x by `tools/fix_weak_over_time.py`: Rupture 169 → 414, Vampiric Touch 48 → 129, Witchbane 84 → 383.
  - **22 strong outliers** (2.2–4.8x; mostly CoA AoEs hitting each target harder than a nuke, plus the Seismic Crash builder and a few party heals) were brought to 1.6x by `tools/fix_strong_outliers.py`: Starcall 491 → 163, Obliteration Beam 326 → 110, Forked Lightning 292 → 116, Facemelter 337 → 137.
  - Recruit kits were re-sized (`rank_kit_abilities --apply`): trump cards are 1.6–3.1x.
- **New sim:** `sim_dps_parity --targets N`, damage against a pack. At 50 against 1/3/5 targets: Fire 1,934/1,936/2,988, Fury 1,482/2,115/4,690.
- Mana costs were recalibrated. **The pass-5 recalibration is running** (damage → `/tmp/claude-0/aura_dmg_p5.log`, healing iterate → `/tmp/claude-0/aura_heal_p5.log`).
- **Next, the verification battery:**
  - Same as before: parity on seed 3, the heal scenarios, trio, solo (geared, under-geared, no talents), content (geared), the tank matrix, mana endurance, `sim_difficulty` open world and dungeons, hidden zones.
  - New: multi-target parity at 3 and 5 targets, short-fight (4-turn) burst parity, no-buffs, and consumables.

## Pass 5→6 (17:35–17:55 UTC): Kyle's rank-shape check and four spells

Kyle (10:37 local): "We are ensuring that even coa classes have the proper ranks leveling up and follows the front loaded increases ... and lower % increases at end level with roughly a 9x increase compared to monster 10x?" Then: "I want to see max rank lightning bolt, max rank shock (stormbringer). Max rank holy light (paladin) and max rank invigorating shot (tinkerer)". Then: "Dig deep."

- **The damage pass-5 recalibration finished** (clamped: Starcaller Warden 30 at 1.83, Feral 60 at 1.97). **The heal pass was stopped** before the fixes below and restarted as pass 6.
- **Answer on 9x vs 10x:** that was the old flat world. Now a level-1 mob has 120 health and a level-60 mob 6,600 (×55). Max-rank Lightning Bolt base is ×25 over rank 1 (×43 in measured hits, ×45–60 geared). Fight length holds: ~2.5 rank-1 bolts at 1, ~3 geared bolts at 60 (2.4 with crits).
- **FOUND: 264 abilities off the rank line** (nearly all CoA; 129 outgrew the world by >1.4x, e.g. Runeblade rank 1 at half a spell, top rank 4x). The curve multiplies by growth / authored line, so authored steepness was stacked on top. **Fixed** by `tools/fix_rank_lines.py --apply`: every rank = anchor × (1 + 3.636%·(L−1)), anchor = geometric mean of the old ratios (size kept). After (scratchpad rank_shape.py), median rank step CoA/Classic:
  - L2–15: +92% / +89%
  - L16–30: +62% / +66%
  - L31–45: +32% / +36%
  - L46–60: +31% / +32%
  - 0 abilities grow faster or slower than the world over their span.
- **The four spells at level 60 max rank** (engine casts ×400, non-crit range, non-resistant target; scratchpad show4.py):
  - Lightning Bolt (R9): naked 1,449–1,654; geared 1,776–2,047; tooltip base 1,010–1,209; L1 41–47.
  - Shock (R8): naked 1,107–1,272; geared 1,582–1,798; base 1,362–1,631; L1 55–63. Costs 806 mana = 6.5% of a 12,450 bar (15 casts); the spenders cost Static. Within the 20-turn target, so not a bug (I wrongly flagged it to Kyle at first).
  - Holy Light (R8, slow, cd 1): geared ~1,800–2,100; base 1,631–1,954.
  - Repair Shot (Tinker's heal shot; there is no "Invigorating Shot"; Stormbringer has Invigorating Surge): geared 1,700–2,042; base 946–1,133.
- **FOUND: slow casts took the same share of power as normal ones.** Only the base was sized by cast speed. **Fixed:** coefficients × cast_speed_value (slow 1.5, quick 0.65), like Classic's cast time / 3.5 (`combat/ability_scaling.apply`).
- **FOUND: the "over" gear tier was naked in every sim.** Gear at +5 ilvl needs level ilvl−2, so it was never equipped. **Fixed** in `sim_matrix.make_dress` (required_level held at the character's level). Every earlier "over" result is void.
- **FOUND: Healing Wave ≈ 2x Holy Light per cast** with the same data and coefficient. The cause is talents:
  - Resto stacks Improved Healing Wave 5×3% + Healing Way 3×8% = +39% on Healing Wave, plus Purification +10% and Nature's Guardian +30% below 35% health.
  - Holy has Healing Light +12%.
  - Spec auras level the TOTALS (Holy 0.91, Resto 0.94 at 60). Left as kit flavour; Classic Resto leaned on Healing Wave too.
- **`tools/audit_talent_stacking.py` (report only).** 15 abilities take more than +60% from per-ability talents across all trees; 8 within one tree (Jungle Shrooms +136%, Mechsuit Combustion +87%, Veinburst +71%, Scrap Shot / Spider Bomb / Laser Beam +69%, Widowmaker +66%, Voodoo Cauldron +63%).
  - An automatic cap was tried and REVERTED: shared-number nodes (Rockadier, Turbo Upgrade!, Master Mixologist) garbled their descriptions, and most are CoA capstones that transform the ability. Any trim is a hand edit; this is a design call for Kyle.
- **Fixed:** Starcaller Keen Sight 0.02 → 0.1 a rank (10% of Intellect as ranged AP per rank, 50% at 5; the key is a raw multiplier; Careful Aim is 33% a rank). `validate_class`: 0 errors on all 30 classes.
- **Fixed:** three Tinker descriptions with stale numbers (Repair Shot "for 38", Rocket Launcher "174", Emergency Heal "116").
- Recruit kits were re-ranked against the corrected class kits; `qa_kit_ranks` passes.
- **Commits:** ffbd305 (rank lines), 6af22c0 (cast-speed coefficients, over-gear, Keen Sight, audit).
- **Running:** pass-6 recalibration (task bayx98bct): damage → `/tmp/claude-0/aura_dmg_p6.log`, heal iterate → `/tmp/claude-0/aura_heal_p6.log`.
- **Then the full battery**, with "over" now real: parity on seed 3, multi-target 3/5, short-fight 4 turns, heal scenarios, trio, solo (geared, under, no talents, OVER), content, tanks, endurance, difficulty, hidden, no-buffs, consumables, the QA suite.

### 17:55–18:15 UTC: Kyle's calls on Healing Wave and the talent stacks

Kyle (10:50 local): "That is fine. As holy pally gets illumination. So they usually last longer anyways. This allows shamans to not cast as much to save mana. Healing wave should be more expensive than holy light as well. Let's edit some of them hand by hand but DONT lose the cool CoA identity by butchering them too badly"

- **Healing Wave 2x Holy Light: kept** (Kyle: fine). Healing Wave is now priced dearer: `calibrate_mana_costs.HEAL_TARGET = {"shaman": 16}`, so the main heal lasts 16 casts from a full bar instead of 20, 25% dearer as a share of the bar. The shaman's other heals move with it. Before this, at 60 Healing Wave cost 4.0% of the bar and Holy Light 3.3%; at 20 it was 4.3% vs 4.7%.
- **FOUND: 68 damage and heal abilities learned by 44 top out at 50–53** (Holy Light 50, Heal 50, Healing Wave 51, Eviscerate 51, Immolate 51, Earth Shock 53, Rejuvenation 53, Bloodthirst 52, …). They stood still for 7–10 levels while the world grows ~30%; Classic ranks its main buttons at 56–60.
  - **Fixed** by `tools/add_top_ranks.py --apply`: one rank at 58 (or 60 when the last was 53), on the line, with mana cost grown the same way; rage, energy and built resources stay flat.
  - This also explains Lesser Healing Wave costing as much as Healing Wave at 60: HW's top rank was at 51, so it had the cheaper cost multiplier of the lower level.
  - `qa_trainer_offers`, `qa_kit_ranks` and `validate_class` (all 30): pass.
- **Talent stacks trimmed by hand, capstones kept:**
  - Jungle Booms 53% → 30%, Fresh Ingredients 5 → 4% a rank, Doctor of the Jungle 4 → 3% a rank. Jungle Shrooms goes +136% → +107%.
  - Turbo Upgrade! 54% → 40%, and Turbo Guns 4 → 3% a rank. Combustion goes +87% → +70%, Laser Beam +69% → +55%.
  - Rockadier 54% → 45%. Scrap Shot goes +69% → +60%, Rocket Launcher +45%.
  - Veinburst 9 → 7% a rank. Veinburst goes +71% → +65%.
  - Left alone: Duobombers (it's a second bomb), Widowmaker (a finisher, +66%), Voodoo Cauldron (+63%).
  - Descriptions now match the data: Turbo Upgrade's "54% duration" is +1 turn; Mechanical Synergy is 5% a rank (it said 15%); Virulent Resonance's finishers bonus is 6% (it said 10%).
- **Commit** 42fd93e.
- **Running:** full mana recalibration (task b83buw2lk → `/tmp/claude-0/mana_p6.log`). Then the aura recalibration (damage + healing iterate), then the battery.

### 18:15–19:20 UTC: pass 6 battery aborted twice; the deep dive starts early and finds real bugs

Kyle (10:55 local): "So once these are all done. You'll do one last absolute deep dive. Aim for scenarios you didn't probe!"

**Deep-dive list (new scenarios only):**
1. School resistances by zone
2. Every level 1–60
3. Tail risk (death rate over many fights)
4. Healers solo-leveling
5. Odd groups (no tank, no healer, two healers, all ranged, a member 3 levels under)
6. 40+ turn bosses (who goes out of mana)
7. Chain pulls without drinking
8. Pet classes with the pet dead
9. Half-built talents and wrong-stat gear
10. Bosses +3 (hit)
11. Threat
12. Downranking
13. Recruits in party
14. First 5 levels

**Earlier steps in this stretch:**
- Mana recalibrated (49e5ce9). Healing Wave vs Holy Light as a share of the bar: L20 5.3% vs 4.6%, L40 8.0% vs 6.0%, L60 5.8% vs 4.2%.
- Auras pass 6 (dc… → 04b546a).

**FOUND: the damage-parity target was not neutral.**
- It was the alphabetically first creature of each band: Armored Scorpid (Nature 60) at 10, Corrupted Treant at 20 (Nature 60, Fire −40, every other school 10, armour 512).
- So every damage aura at 10–20 favoured Fire and punished Nature (Enhancement clamped at 20).
- **Fixed:** `sim_dps_parity.neutralize` (no resists; armour = the band's median), also used for the Cryotherapist heal-parity target. 8e4e263.
- Re-run: the clamps went from 4 to 1 (only Survival L30 is left).

**Deep dive #1: `tools/sim_school_exposure.py`** (8ba0664).
- Each spec's real school mix, against every encounter table in its band, using resistances as SPAWNED (templates carry none).
- Below 60: the worst table keeps about 62% (the 30 cap gives 37.5% off), and the median keeps 92–100%.
- AT 60 (the 75% wall, Kyle's 6 Nov design: resist max 60, spell pen 2:1, 30 pen cancels it):
  - Mono-school specs keep 42–52% against the worst endgame tables: Incineration 42%, Elemental 44%, Balance 48%, Fire Mage 52%, Venom 52%.
  - 3–5 of 15 tables are below 70%. Median kept: Incineration 82%, Enhancement 82%, Fire Mage 85%.
  - The tool counts no spell penetration. The cliff is exactly at 60 (cap 30 at 59 → 60 at 60). **For Kyle:** ramp it from 50 to 60?

**FOUND: the Arcane Mage had no Arcane single-target spell** (its damage was 62% Fire; the builder's notes said "Arcane's own spells are mostly absent").
- **ADDED** `mage_arcane_missiles`: trained at 8, ranked every 8 levels to 56, slow cast, 1.5x a Fireball rank for 1.15x its cost. Icon: Spell_Nature_StarFall (WotLK glyph set).
- Missile Barrage re-aimed at Arcane Missiles. Arcane Stability now also gives +3% a rank to Missiles. 2b69c23.

**FOUND: the planner ranked on base size and ignored talents.**
- Missiles tied Fireball and lost on file order, and Frost cast Fireball over Frostbolt.
- **Fixed:** `plan.per_turn` × (1 + the ability's damage talents + the school's talents via the engine's `_school_damage_bonus`).
- Arcane leads with Missiles at 40/60; Frost leads with Frostbolt.

**FOUND: 19 damage spells had no `damage_school`** and landed as generic "magic", untouched by any school talent.
- The Shadow Priest's whole kit: Shadow Word: Pain, Mind Flay, Vampiric Touch, Mind Sear. **Shadow measured 0% Shadow.**
- Also Corruption, Unstable Affliction, Moonfire, Insect Swarm, Starfall, Consecration, Flame Shock, Searing and Magma Totem, Ravenous Strike, Final Verdict, Argent Blade, Titanstrike, Spirit in a Bottle and Noctis Blade.
- **Fixed**, with a new guard `tools/qa_spell_schools.py`.

**FOUND: Shadow still cast Smite over Mind Flay.** Mind Flay totalled 765 at 58 against a 1,060 Smite (0.41x of expected).
- `fix_weak_over_time` second round, floor 0.6 → 0.8: **34 DoTs/HoTs lifted.** These include Mind Flay, Curse of Agony, Unstable Affliction, Insect Swarm, Renew, Deadly Poison, Hemorrhage, Garrote, Mind Sear, plus 25 CoA.
- Shadow now opens Shadow Word: Pain, Mind Flay, Mind Blast.

**Three spenders at 0.33x lifted to 0.8x:** Venomtip Poison, Torchlight, Divine Force. Commit 8d0fcec.

**Running:** pass-7 recalibration (task bg9gqejyi → `/tmp/claude-0/aura_dmg_p7.log`, `aura_heal_p7.log`). Then the battery and the rest of the deep-dive list.

### 19:20–20:05 UTC: Kyle's calls on resistances and hit, plus both-weapon strikes

Kyle (11:16–11:20 local):
- "For resistances. Add a ramp from 50 to 60, yes. I want hit rating, yes. We need to have spell hit, physical hit. Different hit rating for spells vs skills vs 2H vs 1H."
- "We need UI to display spell pen and also hit rating ... Main hand hit chance, off hand hit chance, ability hit chance, spell hit chance, spell pen values. Writing what cap is. So people can over cap too and it shows."
- "Also are you accounting for proper abilities like stormstrike that hit for both weapons. Or a character with 2 weapons using attack and hitting twice ... Wildclaw with primalist is another example"

- **Pass-7 auras** (4fa45e7).
  - Damage clamps: Enhancement 20, Survival 30, Assassination 30, Fury 30 (×2.48). The Fury at 30 breakdown: Cleave 85% of its damage.
  - Heal clamps: Vizier 10 and 20, Grovekeeper 30, Brewing 60.
- **Resistance ramp** (2b… → commit "Resistance ceiling ramps"): the ceiling is 30 up to 50, then +3 a level, reaching 60 at 60 (`RESIST_RAMP_FROM`). `qa_resistance_scale` updated.
- **HIT** (f2a45ca):
  - Classic table:
    - Same level: physical 5%, spell 4%.
    - Target +1/+2: +1/+2.
    - Target +3: physical 8%, spell 17%.
    - Beyond +3: +2 physical / +11 spell a level.
  - Dual-wield WHITE swings (both hands) +19%; abilities never.
  - Two stats: `hit_rating` and `spell_hit_rating`. Caps: 8 (abilities/2H), 27 (dual-wield), spell 16 (1% floor).
  - `Character.miss_chance_vs` / `hit_chance_vs`; `abilities._hit_vs` at every miss roll (the actual target's level).
  - Talents: 17 → spell hit, 9 + 6 count for both, 22 stay physical.
  - Items: `tools/split_spell_hit.py` moved 128 caster stat blocks; 427 kept.
- **Both weapons:** specials are main-hand only unless `strikes_both_weapons`. 16 abilities carry it: Stormstrike, Wildclaw, Mutilate, Killing Spree, Glorious Execution, Justice, Dirge, Dusk Blade, Purifier's Edge, and Felsworn's Twin Slice, Annihilan Strike, Glaiving, Fury Unleashed, Fury of the Illidari, Felrend and Carve.
  - A dual-wield Attack swings both hands, each rolling its own hit; the off hand lands even when the main hand misses. The combat log shows "(off hand +N)" / "(off hand misses)".
- **Sheet:** Hit / Spell Hit against their caps, with overcap shown. Main Hand / Off Hand / Abilities / Spells / Ranged are each shown at your level and against a +3 boss. Spell Penetration against its cap, with overcap. Checked by screenshot; `qa_screen_layout` passes.
- **Running:** the full QA suite (`/tmp/claude-0/qa7`). Then: damage auras (the hit changes move every spec's damage), the battery, and the rest of the deep dive. Kit hand-fixes are still owed: Fury, Assassination, Survival, Enhancement, Vizier, Grovekeeper and Brewing.

### 20:05–21:10 UTC: dual wield, the Rogue dip, Vizier, Warrior signatures

Kyle (11:27, 11:32 local): "Yup. Keep going bro." and "After this last round of fixes we will look at gear again. We will remove and fix up a lot of drip stats by changing stats from % to rating where 10 rating is 1%. Obviously some weigh more. Like crit rating is cheaper than parry rating etc." (This is backlog item 8; it comes NEXT, after this round.)

- **Pass 8 (hit changes):** 8 clamped, mostly dual-wield melee at 30. Cause: specials went main-hand only, so a dual-wielder was a two-hander with a smaller weapon (white swings cost a turn here).
- **FIXED, the off hand's own swing** (commit "Dual wield: the off hand takes its own white swing"):
  - Beside every main-hand special, the off hand swings white, with its own dual-wield miss roll against the target's level and its own crit.
  - Damage is 0.5 × (weapon × world curve + attack power × AP_BASE) × the off-hand talents.
  - Both-weapon strikes carry the off hand inside the strike.
  - Fury at 30: 566 → 692.
- **FIXED:** Dual Wield Specialization is now Classic's off-hand damage (`offhand_damage_pct`): Fury +5% a rank, Rogue +10% a rank. Before, it was +1–2% to all damage.
- **Pass 8b:** 9 clamped, the level-30 physical cluster.
- **FOUND (a sim problem, not a kit problem): energy.** Assassination did less at 30 (742) than at 24 (777): the planner spread energy over DoTs and poison, and Sinister Strike fell from 23 casts to 7. **Fixed:** energy abilities are ranked per turn of energy (cost / 25). Assassination at 30: 884.
- **FIXED:** HoTs can carry an up-front `heal_value`, which lands on cast and takes healing power by its share of the spell. Shadra's Prayer got CoA's direct heal (0.8× the HoT total). Before this, the Vizier had no spammable heal until 20.
- **Pass 9:** 8 clamped, 1.8–1.99:
  - Enhancement 20, Survival 30, Assassination 30, Subtlety 30, Fury 30, Warden 40, Feral 60, Valkyrie 60.
- **Hit-size check at 30/50, no auras.** Physical strikes are BIGGER per hit than nukes (Sinister Strike 709 vs Shadow Bolt 541 at 30). The gap is resource-gated: Barbarian's 20-energy, 845 strike is 2.4× the Rogue's damage per energy.
- **Residual causes:**
  - Enhancement at 20 plays as a caster (its melee kit comes later).
  - Fury at 30 lives on Cleave.
  - Valkyrie spams one spell.
  - Feral's Rake is weak.
- **FIXED:** Bloodthirst ×2.58 and Mortal Strike ×1.83, to 1.35× a same-level Heroic Strike. Bloodthirst was authored at a quarter of one (1,110 vs 1,571 at 50).
- **Running:** pass 10, damage then healing (task b71on7mlu). The QA suite is still in its tail (no failures in the first 52 of 197).

### 21:10–22:30 UTC: QA, gear ratings, crafting, engineering

Kyle (11:36–12:09 local): "This will fix a lot of the partial numbers we see on gear and rounding stuff. Same as we did with stormy gemstones." / "If you wanted to devote a little bit of effort while the QA runs you can start to adjust some of the drip stats, fix up boss loot and quest loot to slap in some ratings for easier transition from 1 to max level so not every rating is just dropped post 50. They need to be spread out and logically done. None of this weird stuff we saw with crafting." / "Go through crafting please. We have spare credits." / "I think you should just full on fix and audit engineering when you're done too."

- **Pass 10 auras** (committed): 6 damage clamps (Enhancement 20, Marksmanship 30, Survival 30, Assassination 30, Warden 50, Feral 60) and 5 heal (Vizier 10/20, Grovekeeper 30, Brewing 50/60, the last at 2.15).
- **Full QA, 197 tests.** Only the pre-existing gathering_legality and underdark_content fail; the four kit tests were fixed later in the run.
  - Fixes: a certain hit (+100 or more) is certain past the caps.
  - Three kit tests were updated for the split hit table: Sondre's spell hit, Dan's boar at his level, and the blind removes spell hit too.
- **BOSS AND QUEST LOOT RATINGS** (`tools/rating_pass.py`; 8b98e67, redone in e1a3d19 with the floor at 5).
  - The data already held ratings; the drip was a flat "+10 (1%)" at every item level.
  - Sizing: 20% → 35% of the budget by item level (tank gear 1.4×), floor 5, one rating when two won't fit. Primaries pay, so items stay on the curve (78% inside tolerance before and after).
  - 210 off-role ratings swapped; 246 items gained one.
  - Presence: 10–19 6% → 11%, 20s 18% → 30%, 30s 37%, 40s 43%, 50s+ 50%. Medians 5/6/8/9/12/14.
  - Parry 1.25 and dodge 1.1 a point (crit 1.0).
- **Spec gear:** healers name no school (healing reads healing power only); Balance → arcane.
- **CRAFTING:**
  - `build_crafted_gear`: precise_caster → spell hit; a near-floor rating rounds UP to 5 and the lead stat pays; 845 items rebuilt (counts unchanged).
  - Crafted ratings by band: 10–19 1%, 20s 7%, 30s 28%, 40s 41%, 50s 48%. Low crafted greens stay primaries only (Kyle's 14 Nov rule).
  - Jewelcrafting: Veiled and Lambent → spell hit; six Regal gems re-cut at the new dodge price; Black Diamond Crab defense 1 → 10 (a pre-ratings 1% the conversion missed).
  - **build_jewelcrafting is NOT safe to rerun alone.** It rewrites blacksmithing and drops 11 recipes other tools add (10 secret rings and Regal Jet). The data was edited in place.
  - The "Great" spell-hit gem cut was NOT added: it reshuffles cut assignments and vendor sources. Needs the full builder chain.
- **ENGINEERING** (c4e04a2, new guard `tools/qa_engineering.py`):
  - 24 of 27 consumables did nothing. Consumable.use had no explosive or gadget branch, and the shots granted nothing. Fixed:
    - Bombs hit all enemies, by their own school (some stun), from the hotbar, and spend the turn.
    - Gadgets act through a new gadget buff slot (saved, ticked, shown in the bag), turn-based effects, a heal, a revive, or the hearthstone reset.
    - Shots give +4..+26 AP for 30 minutes.
  - **Bombs and shot stopped at 29:** added 4 bombs (38/46/50/57) and 3 shots (38/52/57).
  - **Tideglass Seal** had no source: now trainer-taught.
  - **Proc tooltips** now show the world-curved number (`combat/proc_text.py`): the Dragonling Core says 470 at 60, not 160.
  - The three shop-sold gadgets (spare lens, recall beacon, grapple) work too.
- **Notes for Kyle:**
  - Arrows and bolts (woodworking) still stop at level 30 (heavy, +15 AP).
  - The "Great" spell-hit gem needs a full jewelcrafting rebuild.

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

## Crafting, later on 15 Nov (pointer)

- 68f1486: arrows and bolts reach level 57 (AP 18/22/26), matching gun shot. Ammo is a 30-minute +AP buff,
  one quiver at a time, and isn't spent per shot.
- 5e0da72: the woodworking expansion. 86 pieces, 18 kits, 4 bow parts and 3 scopes. Fighter staves are priced
  as two-handers, crafted weapons and trinkets no longer carry stray armour, and bombs can't be dodged.
- 4cdae4f: the spell-hit gems (Great, Vivid, Serene, Piercing).
- Full record: docs/woodworking_expansion_2026_11_15.md (project copy: claude/woodworking_expansion_2026_11_15.md).
- Open questions for Kyle: should kits on crafted epics be capped at epic? And sheet E4 (7 epic icons).
