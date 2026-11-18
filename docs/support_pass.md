# The support pass (16 Nov 2026, night)

Kyle asked for three things:
- "get into the support skills and them not actually benefiting from ranking up and being obsolete"
- "Make sure support skills and buffs are actually properly done with proper skill levels too.. don't forget to
  look at EVERY Healer"

This pass follows the healing formula (docs/heal_formula.md) and is built on the same idea: size things against
what a character of that level actually has.

## Every healer
Measured with `tools/calibrate_spec_auras.py --kind healing`, every healer spec at 10-60.

**Before:** after the formula went in, healers' sustained output at 60 ran from 16.5% to 45.6% of a tank's health a
turn. The hidden spec aura had to be widened to 0.6-1.6 to cover it.

**Causes, and what changed:**
- **HoTs stacked.** At 1.2x a heal, a kit that keeps several HoTs rolling out-healed the rest by a quarter to a
  third. Vizier rolls three, the Sun Cleric two, and the Chronomancer has Accelerated Recovery. A HoT now totals one
  heal (`HOT_FACTOR` 1.0), which is a heal delivered later.
- **A spell's character ran ±20-25%.** It's now held to 0.9-1.15 (`IDENTITY_RANGE`).
- **Kits set by hand.** Each outlier gets an explicit `formula_identity` on its abilities, and the reason is written
  in each ability's `_tuning`:

  | Spec | Abilities | Identity |
  |---|---|---|
  | Pyromancer | Ember Touch, Kindle, Cinderheart | 1.35 |
  | Grovekeeper | Hand of the Earthmother | 1.35 |
  | Grovekeeper | its three HoTs | 1.3 |
  | Discipline | Penance | 1.3 |
  | Restoration Druid | Rejuvenation, Regrowth | 1.2 |
  | Restoration Druid | Healing Touch | 1.15 |
  | Moon Priest | Hand of Elune, Moonwell Splash | 0.9 |
  | Time | Epoch, Accelerated Recovery | 0.85 |
  | Vizier | Alkahest | 0.85 |
  | Vizier | its three HoTs | 0.8 |

- **The Cryotherapist** (Frost Mage's healing) heals 12% of the damage its converted nukes deal, down from 30%. It
  was at 1.5x the 75% of a healer it's held to.
- **The parity sim was wrong in two places**, both fixed in `tools/sim_heal_parity.py`:
  - It cast a damage-and-heal spell at the healer itself (Pyromancer's Cleansing Flames), so Flameweaving read as half
    a healer at 50-60.
  - It counted a shield a healer puts on itself (Volcanic Shell, Ice Barrier) as healing.

**After:** healing auras are back to 0.9-1.1, and from 30 to 60 almost every spec needs no more than that.

**Left over:**
- Grovekeeper, a damage-healer held to 75% of a healer, still wants about 1.5 at the explicit cap.
  - **17 Nov 2026**, Kyle: "We can buff all its heals about 10% across the board." Every heal a Grovekeeper casts is
    now x1.10 on top of its aura (`combat/ability_scaling.HEAL_SPEC_BONUS`), HoT ticks and Seismic Wave included.
    The parity sim puts it at 0.85 / 0.72 / 0.81 of its 75% target at 20 / 40 / 60 (it was about 0.65-0.77), so
    it's closer but still short. The rest would be a kit change (more or bigger heals), Kyle's call.
- Restoration Druid wants about 1.3 at 30-40, where its kit is thin.

## Shields on someone else
`combat/heal_formula.shield_size`: a shield cast on an ally or the party soaks 0.9x the heal of its shape, healing
power included, with the spec cap.

Before, it was a flat share of the recipient's health:
- Power Word: Shield 30%
- Void Shield 18%
- Inferno Barrier 16%

That was the same at 6 as at 60, naked or geared, and healing power didn't touch it. A shield on yourself (Ice
Barrier, Volcanic Shell, a Dreadnought Shield) is a defensive cooldown and keeps its share of your own health.

## Buffs and debuffs: sized by level, and ranked
**Before:**
- Power Word: Fortitude's top rank gave +3 Stamina at 60, about 70 health on a 4,400-health tank.
- 165 of the 228 class buffs and debuffs with flat stats had one rank, so they never grew.

**The size rule** (`combat/support_formula.py`, `data/balance/stat_reference.json` written by
`tools/calibrate_stat_reference.py`). Every flat stat is a share of what a geared character of the rank's level has
(the 75th percentile across specs). For a debuff on an enemy, it's a share of the median monster's stat. The shares:

| Kind of buff | Share |
|---|---|
| Long party buff | 15% |
| Long party buff giving four or more core stats (Kings, Mark of the Wild) | 8% a stat |
| Short party buff in a fight | 15% |
| Short buff on yourself or one ally | 20% |
| Debuff on an enemy | 15% |

- **Armour** takes half the share, because plate sets the reference.
- **Not sized:** percentages and resistances. (mp5 is sized as of 17 Nov 2026; see the end of this doc.)
- **Floor:** a stat is never smaller than authored. The rule lifts what went obsolete; it doesn't cut what a
  designer made big on purpose.

**Ranks** (`tools/regrade_buff_ranks.py`):
- 65 buffs and debuffs now have a rank every 10 levels up to 58.
- The first rank stays as authored.
- A buff that was already densely ranked keeps its ranks (Sunder Armor's eight).

**Examples, levels 10 → 20 → 30 → 40 → 50 → 60:**

| Buff | 10 | 20 | 30 | 40 | 50 | 60 |
|---|---|---|---|---|---|---|
| Power Word: Fortitude (Stamina) | 2 | 7 | 12 | 15 | 15 | 20 |
| Blessing of Might (attack power) | 13 | 24 | 51 | 69 | 85 | 117 |
| Battle Shout (attack power) | 9 | 18 | 38 | 60 | 81 | 137 |
| Sunder Armor (armour) | -60 | -84 | -109 | -126 | -142 | -159 |
| Demon Armor (armour, from 20) | | 87 | 148 | 212 | 304 | 404 |

## Cleanses
Bosses from 40 now carry party damage-over-time in curse, magic, poison and disease (`tools/build_boss_aoe.py`).
`tools/add_missing_cleanses.py` adds:

| Class | Before | Added |
|---|---|---|
| Druid | nothing | Remove Curse (18), Abolish Poison (26) |
| Shaman | only a level-50 curse talent | Cure Toxins (poison and disease, 16) |
| Mage | nothing | Remove Curse (18) |

Every other healer already had two or three schools.

## Checked
- **QA:** the support-related QA, 83 scripts. Every failure left also fails on main and is unrelated: revives
  "not dead" in a living party, talent text, item templates and recruit kit timing.
- **Heals at 60** (`tools/sim_heal_formula.py`, strongest single-target heal, as a share of a tank's health):
  - Bare: 18-37%.
  - Geared and specced: 33-54%. The top of that range is the slow heals, which are 1.5x by design.
- **Dungeons** (`tools/sim_difficulty.py --dungeon`, 4 fights a boss):
  - Parties of five beat every boss.
  - The hard ones are Victor Hale (won 3/4, 3.2 standing) and Dathrohan (3.2 standing).
  - The Baron, Gandling, Ras and Hrun leave 3.8-4.0 standing.

## Long party buffs and mp5 (17 Nov 2026)
Kyle's two answers: every class without a long party buff gets one ("Each gets one"), and mana buffs give "Real mp5,
sized by level", with every healer class able to give its party mana. Written by `tools/build_long_party_buffs.py`;
checked by `tools/qa_long_party_buffs.py`.

**mp5 in the formula.**
- Gear barely carries mp5, so its reference is 1.2 x the Spirit reference.
- A long buff's mp5 (on yourself or the party, 15%) gives back about what a geared caster's Spirit does on a turn they
  cast.
- An in-fight one is 20%.

| Long mp5 buff | 20 | 30 | 40 | 50 | 60 |
|---|---|---|---|---|---|
| mp5 | 8 | 11 | 11 | 13 | 16 |
| mana per turn (x world curve) | 13 | 22 | 23 | 32 | 46 |

**Mana buffs.**
- "Maximum mana %" buffs are gone. Blessing of Wisdom, Mana Spring Totem and Water Shield give mp5.
- New ways to give the party mana: Priest Divine Spirit (Spirit, from 30), Chronomancer Borrowed Moments (mp5),
  Starcaller Moonwell's Blessing (mp5).
- Whispers of C'thun and Inner Flame also give mp5 now.
- The 14 single-rank mp5 buffs got a rank every ten levels.
- Two had a flat 18 and 15 from level 6 (Aspect of the Moonwell, Vow of Grace). The formula now sizes them by rank.

**The eight new long party buffs** (all from 20, ranked to 58):

| Class | Buff | Gives |
|---|---|---|
| Warrior | Commanding Shout | Stamina (Battle Shout stays the in-fight one) |
| Hunter | Trueshot Aura | attack power |
| Rogue | Cutthroat's Edge | Agility |
| Warlock | Demonic Pact | spell power |
| Felsworn | Felbrand | Strength (Fel Infusion stays the in-fight aura its talent shortens) |
| Templar | Templar's Oath | Stamina and armour |
| Witch Doctor | Spirit Fetish | Spirit and mp5 |
| Witch Hunter | Hunter's Ward | Shadow resistance, 12 -> 22 like the resistance totems |

**The five more** (Kyle, 17 Nov 2026 afternoon: "Make the classes get a 30min buff. Most classes should have one."),
all from 20, ranked to 58, with the in-fight buffs left as they were:

| Class | Buff | Gives (20 -> 58) |
|---|---|---|
| Bloodmage | Bloodbond | Stamina 12 -> 20 |
| Guardian | Marching Song | Strength 7 -> 11 and Agility 9 -> 17 |
| Knight of Xoroth | Hellfire Ward | Fire resistance 12 -> 22 |
| Necromancer | Grave Wisdom | Intellect 12 -> 20 |
| Ranger | Farstrider's Mark | Agility 9 -> 17 |

Every class now brings a thirty-minute party buff. `qa_long_party_buffs` holds all thirteen that got one.
