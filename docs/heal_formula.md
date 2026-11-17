# The healing formula (16 Nov 2026)

Kyle: "we need to fix the healing end game.....we need an actual formula and do it right.... a spot heal from a
non-spec'd character shouldn't heal 80% tank HP and like 200% boss damage...."

Kyle signed it off the same night: "20 unspecced is fine. 2 is fine with 40 and 25%. Yes that's fine to drop bosses a
bit to account for it. I think having more varied aoe damage bosses will help make it more spicy post lvl 40 too".
The section "What went in" at the bottom covers the build.

## What happens now (tools/sim_heal_formula.py, every healer spec, strongest single-target heal)

- **bare**: no talents and no gear.
- **built**: talents spent for healing, rare gear at level.
- **tank**: a geared Protection Warrior of the same level.
- **boss**: the median of every dungeon boss's average action within two levels.

| Level | Tank HP | A normal monster's action | A boss's action | Bare heal | Built heal | Built / bare |
|---|---|---|---|---|---|---|
| 20 | 907 | 3% of tank | 43% of tank | 28-71% of tank | 34-203% | x0.8 to x2.8 |
| 40 | 2155 | 11% | 69% | 29-61% | 49-154% | x0.8 to x3.3 |
| 60 | 3255 | 10% | 103% | 37-77% | 71-185% | x1.0 to x4.7 |

Where a level-60 built heal comes from, as a share of the tank's health:

| | Range across specs | What it should be |
|---|---|---|
| The rank's base | 35-72% | the main thing to fix: 20% |
| Healing power from gear | 7-20% | too little: gear barely matters |
| Spec aura | x0.63 to x1.75 | a balancing fudge, hiding kit gaps |
| Talents and crit | x1.04 to x4.64 | uncapped: Tinker's Zap x4.6, Shaman x2.6 |

So it's four problems, not one:
- The ranks are too big on their own.
- Gear adds almost nothing.
- Talents and the spec aura stack with no ceiling.
- Bosses are oversized too: an average boss action at 60 is a whole tank's health.

## The formula

Everything is measured against **T(L)**: the max health of a geared tank of level L. It's a reference table from
the world curve, so the same shares hold at every level.

```
heal = ( 0.20 x T(Lrank) x S x A          the rank: what training the spell gives you
       + HP  x C x S x A )                healing power: what gear gives you
       x Spec                             talents and spec, all of them together, capped
       x crit                             as now (x1.5 on a crit)
```

- **Lrank** is the level the rank is learned at. A rank 6 levels later is about +100% early and +23% late, the same
  feel as the world curve, and an outlevelled rank falls behind as T grows. Downranking keeps its penalty.
- **S, cast speed** (unchanged): quick x0.65, normal x1.0, slow x1.5.
- **A, area share**: one target 1.0, two or three targets 0.7 each, the whole party 0.45 each.
- **HP x C, healing power**: C is set so that rare gear at your level adds +40% of the base.
- **Spec**: all healing multipliers multiplied together: the spec aura, healing_done talents, per-ability talents
  and low-health bonuses. The total is capped at x1.25 for a full healing tree. The spec aura is recalibrated into
  0.9-1.1, so it's a small nudge and not a crutch.

### What that gives, as a share of a same-level geared tank

| Heal | Bare (no talents, no gear) | Geared | Geared and specced |
|---|---|---|---|
| Quick (Flash Heal) | 13% | 18% | 23% |
| **Normal (Heal, Healing Wave)** | **20%** | **28%** | **35%** |
| Slow (Greater Heal, Healing Touch) | 30% | 42% | 52% |
| Party heal, each target | 9% | 13% | 16% |

Kyle's example: a 4,800 HP tank hit for 1,000.
- **Today:** a naked, unspecced heal lands 2,600.
- **Under the formula:**
  - unspecced normal heal: 960
  - geared normal heal: 1,350
  - geared and specced normal heal: 1,680
  - geared and specced slow heal: 2,500

### The rest of support, on the same reference
- **HoT**: 1.2x a normal heal in total, spread over its duration. It pays for being slow.
- **Shield**: 0.9x a normal heal, because it can't overheal.
- **Chain heal**: 0.7 / 0.5 / 0.35 of a normal heal across three hops.
- **Emergency heals** (Lay on Hands and the like) stay as they are.
- **Mana**: a heal's cost moves with its size, so the main heal still lasts about 20 casts from a full bar.

### Bosses, on the same reference
Heals at these sizes only work if bosses hit on the same scale.
- A boss's normal hit is 20-25% of the tank.
- A big hit is 40-45%.
- A spread is 10-12% on each target.
- Trash is 8-10% (already true: 10% at 40 and 60).

At 60 that means bringing an average boss action down from about 100% of the tank to about 25-30%. Today it's
inflated by three stacked multipliers:
- the boss multiplier, x1.6 to x2.6
- the endgame ramp, up to +25% from 30
- the kit's heavy hits

## Order of work once it's signed off
1. Generate the T(L) table (tools/, from the tank build, averaged over gear seeds) and write it into
   data/balance/heal_reference.json.
2. Heals take their base from the formula instead of the rank curve and heal_trim, and keep each spell's identity
   from its own authored ratio. C goes in, and the Spec cap.
3. Bosses come onto the reference.
4. Recalibrate:
   - spec auras into 0.9-1.1
   - healer parity (sim_heal_parity), within about 10%
   - party scenarios (sim_heal_scenarios)
   - the dungeon sims, so parties of 5 win most fights and the last bosses stay hard
5. Audit every other support skill against the same reference: shields, HoTs, buffs and cleanses.
6. Run tools/sim_heal_formula.py again and put the before and after in this doc.

## What went in (16 Nov 2026, night)

**Code and data:**
- `combat/heal_formula.py` holds the formula: a share of T(L), shape, the gear coefficient, the +25% cap, 1.5x crits
  and the echo room.
- `data/balance/heal_reference.json` (`tools/calibrate_heal_reference.py`) holds T(L), healing power and the authored
  lines.
- `combat/ability_scaling.curved_ranks` takes heal and HoT sizes from the formula, and mana cost moves with size.
  `heal_trim` is retired. `FRONTIER_HEAL_FORMULA=off` turns the whole thing off for before/after sims.

**Spec cap.** Every healing talent and low-health bonus is capped together at x1.25, in `Ability._damage_multiplier`.
Extra heals that a heal sets off come out of the same +25%. These are talent echoes: Emergency Enhancer, Eureka!,
Ancestral Awakening and the bonus procs. Before this, a Tinker's Zap plus its echoes landed 3.9x the Zap. Heal crits
are a flat 1.5x, with no crit-damage talents.

**Bosses.**
- `data/balance/boss_damage.json` (`tools/calibrate_boss_damage.py`) gives every boss a factor. It brings its average
  action to a share of T:
  - dungeon boss 35%
  - a run's last boss 45%
  - field boss 25%
- A boss keeps a little of its own weight, (own / peers)^0.4.
- Hidden layers and skull zones keep their own rows: they're brutal on purpose, and qa_hidden_zones holds them
  there.
- Bosses only come down. Of the 526 dungeon and field bosses, the ones already at or under their target keep
  what they hit for.

**AoE past 40.** `data/balance/boss_aoe.json` (`tools/build_boss_aoe.py`) gives dungeon bosses from level 40 the
party-wide shapes they were missing:
- a blast
- a blight that can be cleansed
- on every third boss, a wounding blast that cuts healing taken by 20% for 3 turns

Each boss's additions are tested in a 40-turn fight against its own kit. It keeps the first set that doesn't stop any
of its own attacks from being used. The first build without this test left 47 of the bosses' own attacks never
thrown. The result is 111 abilities on 83 bosses, and one boss had no room for any.

**Spec auras, interim.** Healing auras sit outside the cap, because they balance one healer's kit against another's.
Healers' sustained output at 60 ran from 16.5% to 45.6% of a tank a turn, so the range is wide, 0.6-1.6, until each
healer's kit is fixed by hand. That's the next pass. The goal is 0.9-1.1.

### After (tools/sim_heal_formula.py, strongest single-target heal, share of T)

Slow heals (Greater Heal, Healing Touch, Healing Wave) are 1.5x a normal one, so they sit at the top of each range.

| Level | Bare heal | Built heal |
|---|---|---|
| 20 | 15-33% (was 28-71%) | 19-58% (was 34-203%) |
| 40 | 17-33% (was 29-61%) | 21-56% (was 49-154%) |
| 60 | 17-33% (was 37-77%) | 30-59% (was 71-185%) |

### Dungeons (tools/sim_difficulty.py --dungeon, 4 fights a boss, after the last calibration)
Parties of five beat every boss in every dungeon. The last bosses are the hard ones:
- Grand Crusader Dathrohan: won 3/4, with 2.5 standing on average.
- Victor Hale: won 4/4, 2.8 standing.
- Ras Frostwhisper: 3.5 standing.
- Alexei Barov: 3.8 standing.
- Hrun and the Baron: 4.0-4.2 standing.

Parties of three and two lose the late bosses. qa_dungeon_boss_turns passes: every boss acts, uses what it carries,
and has something dangerous.
