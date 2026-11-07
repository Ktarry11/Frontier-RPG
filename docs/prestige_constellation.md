# The Prestige Constellation

**Status: DESIGN ONLY — NOT BEING BUILT.** Kyle, 7 Nov 2026: *"So im gunna
drump some stuff for you to convert to a full markdown and keep. We WONT do
this yet."* This document is the consolidated record of that dump. Nothing
here is implemented, and nothing here should be implemented until Kyle says
so. It is a concept library, not a specification.

Reference point: **Path of Exile's passive skill tree.** Kyle: *"I will want
it like Path of Exile!"*

---

## 1. The vision

A massive, interconnected passive progression system giving characters
effectively limitless long-term build customization.

Every character begins with their chosen class, and prestige lets them
gradually transcend the boundaries of that class. A Warrior can develop
Shaman-inspired elemental weapon mechanics. A Mage can adopt Chronomancer
temporal manipulation. A Rogue can incorporate Ranger precision mechanics.

These are **not borrowed abilities**. They are modifications, interactions and
mechanical enhancements that change how a character's *existing* abilities
work.

The philosophy:

- A character's original class should always matter.
- Prestige should introduce new ways to build and play, not bigger numbers.
- Choices should have meaningful trade-offs.
- Players should never be able to acquire everything.
- Two characters of the same class should be capable of feeling radically
  different.
- Long-term investment should unlock increasingly interesting possibilities.

> A Warrior should not simply be a Warrior with 500 extra Strength. One
> Warrior might be an unstoppable defensive fortress, another a
> critical-strike executioner, another an elemental weapon specialist who has
> incorporated Shaman and Stormbringer mechanics. All three are Warriors. All
> three are fundamentally different.
>
> **The class determines where your journey begins. Prestige determines what
> you ultimately become.**

---

## 2. The point system

**Every Prestige level awards 5 Prestige Points.** Points are permanently
retained through subsequent progression and prestige levels.

| Prestige level | Total points |
|---|---|
| 1 | 5 |
| 5 | 25 |
| 10 | 50 |
| 15 | 75 |
| 20 | 100 |
| 30 | 150 |
| 40 | 200 |
| 50 | 250 |
| 75 | 375 |
| 100 | 500 |

### Node costs

Two cost tables were given. They agree in shape and differ slightly in the
upper bands; both are recorded rather than silently merged.

| Node tier | Cost (table A) | Cost (table B) | Intended role |
|---|---|---|---|
| Minor attribute / minor combat | 1 | 1 | Small permanent bonuses |
| Standard / advanced passive | 2 | 2 | Useful combat improvements |
| Notable | 3 | 3–5 | Meaningful mechanical modifiers |
| Major specialization | 5 | 5–8 | Powerful class or spec interactions |
| Keystone | 8 | 8–12 | Build-defining mechanical changes |
| Legendary | 12 | 12–20 | Rare, highly specialized effects |

These are starting design targets, not final balance values. Players should be
allowed to **save** points rather than feeling compelled to spend immediately.

---

## 3. The five node categories

### A. Attributes
Cheap, plentiful, reliable. +2 Strength / Agility / Stamina / Intellect /
Spirit; +1% Max Health; +1% Max Mana; +1% Crit Chance; +1% Crit Damage;
+1% Physical Damage; +1% Spell Damage; +1% Healing Effectiveness.

### B. Combat mastery
Improves turn-based combat without changing underlying mechanics.

- **Offensive** — physical damage, elemental damage, crit damage, damage
  against weakened enemies, damage against enemies suffering status effects,
  damage against enemies at full health.
- **Defensive** — armor, magical resistance, reduced crit damage received,
  shield effectiveness, reduced damage below 30% health, increased healing
  received.
- **Tactical** — initiative, resource regeneration, reduced cooldowns, longer
  beneficial effects, crowd-control resistance, status-effect effectiveness.

### C. Mechanical modifiers
**One of the most important categories.** These change how existing abilities,
attributes, effects and interactions behave:

- Critical strikes generate additional resources.
- Damage-over-time effects strengthen each round.
- Overheal generates temporary shields.
- Defensive abilities grant counterattack opportunities.
- Killing an enemy reduces a random ability's cooldown.
- Applying a debuff increases subsequent damage against that target.
- Resource generation increases when fighting multiple enemies.

### D. Class influence
Incorporate mechanics *inspired by* another class. Players inherit
**mechanical enhancements, not the original class's abilities.** This is where
the 30-class ecosystem becomes interesting.

### E. Keystones
Large, build-defining, and frequently carrying drawbacks:

- Crits no longer deal bonus damage but trigger an additional attack.
- Heals can no longer crit but generate shields.
- Damage increases significantly as health decreases.
- Every third ability costs no resources.
- Status effects last longer but apply weaker.
- Deal increased damage, receive increased damage.
- Defensive abilities become offensive counterattacks.

---

## 4. The choice node system — the signature feature

Major nodes should frequently present **two or three mutually exclusive
options**. The options represent different *philosophies*, not different
numbers.

A good choice makes the player think: *"I really want both of these, but which
one suits my build?"*

| Offensive choice | Competing alternative |
|---|---|
| Increased critical damage | Increased critical chance |
| Additional attack opportunities | Increased damage per attack |
| Stronger damage over time | Increased direct damage |
| Resource generation on kills | Resource generation on crits |
| Increased damage at full health | Increased damage at low health |
| More powerful debuffs | Longer debuff duration |
| Increased healing output | Excess healing generates shields |

Not every node needs to be exclusive — but major ones usually should be.

---

## 5. The constellation's geography

**One enormous interconnected structure with 30 starting regions, one per
playable class.** Each class starts with access to its own region and travels
outward through connected pathways.

- **Outer regions** — class identity, basic attributes, class-specific
  mechanical enhancements.
- **Intermediate regions** — cross-class influences, specialized combat
  modifiers, mutually exclusive choices.
- **Inner regions** — powerful keystones, advanced mechanical combinations,
  rare legendary modifiers.
- **Universal regions** — general attributes, initiative, resource management,
  party-wide effects, defensive and offensive mastery.

**Not every region connects directly to every other.** Pathways have
meaningful investment costs, which makes route planning part of progression.

---

## 6. Exclusive node pairs — Batch 1

28 pairs. Each pair is mutually exclusive: choosing one locks the other until
respec.

### Warrior
- **Major · 5** — *Unstoppable Juggernaut* (taking damage empowers the next
  offensive ability, stacking to a limit) **vs** *The Perfect Counter*
  (blocking or avoiding empowers the next attack to a guaranteed crit).
  *Relentless aggression vs reactive precision.*
- **Keystone · 8** — *Blood and Thunder* (bleeds spread to another enemy on
  death) **vs** *Single-Minded Fury* (Rage-consuming abilities deal
  substantially more damage but generate less Rage).

### Paladin
- **Major · 5** — *Divine Retribution* (a portion of absorbed damage returns
  as Holy damage) **vs** *Aegis of the Faithful* (healing an ally below a
  threshold grants them a damage-reduction shield).
- **Keystone · 8** — *Judgement of the Crusader* (Judgements empower the next
  Holy ability against that target) **vs** *Beacon of Sacrifice* (healing the
  Paladin receives partly redirects to the most injured ally; own healing
  effectiveness reduced).

### Hunter
- **Major · 5** — *Apex Predator* (attacking below a health threshold grants
  crit chance and crit damage) **vs** *Patient Marksman* (consecutive attacks
  on the same enemy build Precision, empowering the next shot).
- **Keystone · 8** — *Pack Alpha* (pet gains enhanced attacks when the Hunter
  uses an ability) **vs** *Lone Wolf* (without a pet, ranged abilities gain
  damage and crit).

### Rogue
- **Major · 5** — *Death in the Shadows* (bonus damage and crit against an
  enemy that has not acted this round) **vs** *Exposed Weakness* (crits apply
  a vulnerability increasing the Rogue's subsequent damage).
- **Keystone · 8** — *A Thousand Cuts* (finishers may refund resource cost)
  **vs** *One Perfect Strike* (finishers consume all combo points and gain a
  multiplier based on points consumed).

### Priest
- **Major · 5** — *Searing Revelation* (Holy damage is stronger against
  enemies affected by the Priest's healing or shields) **vs** *Guardian of
  Souls* (shielding an ally also grants resistance to the next harmful status
  effect).
- **Keystone · 8** — *Shadow Communion* (Shadow damage restores primary
  resource; direct healing costs more) **vs** *Light's Mercy* (overhealing
  becomes a barrier; direct damage reduced).

### Shaman
- **Major · 5** — *Thrall's Wrath* (Windfury can trigger up to three
  additional attacks per proc) **vs** *Blessing of Theradras* (while Rockbiter
  is active, magic damage received reduced 10%).
- **Keystone · 8** — *Elemental Convergence* (using different elemental types
  in succession empowers the next elemental ability) **vs** *Storm Unbound*
  (lightning crits may refund another ability's cooldown).

### Mage
- **Major · 5** — *Living Inferno* (Fire damage to a burning target may extend
  its burn) **vs** *Absolute Zero* (Frost is stronger against slowed/frozen
  enemies; Fire deals less).
- **Keystone · 8** — *Arcane Overflow* (spending extra mana increases damage)
  **vs** *Spellblade* (Arcane abilities empower the next weapon attack, adding
  a portion of Spell Power).

### Warlock
- **Major · 5** — *Pact of Endless Torment* (DoTs deal increasing damage each
  turn they persist) **vs** *Soulfire Exchange* (consume an active DoT to
  detonate it based on remaining duration).
- **Keystone · 8** — *Master of the Legion* (demon attacks empower the next
  Warlock spell; own direct damage reduced) **vs** *The Fel Vessel* (a portion
  of damage dealt restores health; max health reduced).

### Druid
- **Major · 5** — *Nature's Predator* (attacking enemies affected by the
  Druid's DoTs increases crit chance) **vs** *Keeper of the Grove* (HoTs
  strengthen each turn they remain).
- **Keystone · 8** — *Primal Instinct* (shapeshifting grants a form-based
  bonus; leaving removes it and incurs a temporary penalty) **vs** *The
  Emerald Guardian* (in a defensive form, a portion of damage taken converts
  to healing over subsequent turns).

### Death Knight
- **Major · 5** — *Feast of Souls* (killing restores runic resources and
  empowers the next disease) **vs** *Frozen Dominion* (enemies with the DK's
  diseases deal reduced damage to the DK).
- **Keystone · 8** — *Army of the Damned* (summoned undead gain a portion of
  the DK's offensive stats and strengthen per active disease) **vs** *One With
  the Grave* (once per battle, lethal damage leaves the DK at 1 HP and
  consumes active diseases to restore health).

### Chronomancer
- **Major · 5** — *Time Fracture* (crits may reduce a random ability's
  cooldown) **vs** *Borrowed Moments* (the first ability each battle grants
  initiative next turn).
- **Keystone · 8** — *Temporal Paradox* (first cooldown each round may be
  partially refunded; subsequent cooldowns increased) **vs** *The Unbroken
  Timeline* (the first action each battle repeats at reduced effectiveness
  next round).

### Necromancer
- **Major · 5** — *Gravebound* (enemy deaths grant a stacking temporary
  defensive bonus) **vs** *Soul Consumption* (enemy deaths restore primary
  resource).
- **Keystone · 8** — *Eternal Servitude* (summons persist longer and gain
  durability; summoning costs more) **vs** *Master of the Final Breath*
  (sacrifice undead to empower an ability, scaling with the summon).

### Tinker
- **Major · 5** — *Overclocked* (every third offensive ability deals bonus
  damage) **vs** *Emergency Protocol* (once per battle, falling below 25%
  health activates an automatic defence).
- **Keystone · 8** — *Unstable Engineering* (mechanical abilities gain greatly
  increased effects but may malfunction) **vs** *Precision Instruments*
  (mechanical abilities cannot malfunction and gain accuracy, but lose their
  bonus effects).

### Venomancer
- **Major · 5** — *Toxic Accumulation* (each poison application increases
  subsequent tick damage) **vs** *Venomous Execution* (poison damage increased
  below a health threshold; duration reduced).
- **Keystone · 8** — *Plague Carrier* (poison spreads when a poisoned enemy
  dies) **vs** *Paralyzing Venom* (poison may reduce initiative or delay the
  enemy's next action).

---

## 7. Experimental standalone concepts

| Class | Node | Cost | Effect |
|---|---|---|---|
| Warrior | Last Stand of the Warlord | 12 | The lower the Warrior's health, the more damage their abilities deal |
| Paladin | Martyr's Oath | 12 | Heals can sacrifice the Paladin's own health to increase effectiveness |
| Hunter | Predator's Patience | 8 | Skipping an offensive action builds a powerful bonus for the next attack |
| Rogue | Death's Dividend | 12 | Killing refunds a portion of the resources spent on the killing ability |
| Priest | Suffering Transference | 8 | A portion of damage dealt to allies transfers to enemies under the Priest's Shadow effects |
| Shaman | Elemental Overload | 12 | Elemental abilities can trigger a second, weaker effect of the same type |
| Mage | Calculated Cataclysm | 12 | Spells strengthen for each turn spent without casting from that school |
| Warlock | Infernal Bargain | 8 | Sacrifice health to empower the next ability |
| Druid | Cycle of Life | 12 | Alternating offensive and healing abilities progressively empowers both |
| Death Knight | Cold Embrace | 12 | Enemies attacking the DK while diseased suffer additional damage |
| Chronomancer | Future Sight | 12 | Once per battle, preview an enemy's next action and gain a bonus if countered |
| Necromancer | Death's Harvest | 12 | Damage increases with the number of enemies that have died this encounter |
| Tinker | Salvage Protocol | 8 | Destroying one of the Tinker's summons refunds resources and empowers the next construct |
| Venomancer | Living Toxin | 12 | Poisons adapt, becoming more effective against enemies resistant to previous applications |

---

## 8. Legendary capstones

**Legendary · 12 points each.** For the deepest parts of the tree. Each
redefines a build and carries a real limitation.

- **The World Breaker** (Warrior) — Rage generation dramatically increased, but
  Rage decays each round and abilities become progressively more expensive as
  Rage accumulates. *Explosive burst windows.*
- **The Last Light** (Paladin) — Healing dramatically stronger when an ally is
  near death; significantly weaker above 75% health. *Emergency healer.*
- **The Grand Deception** (Rogue) — The first attack against an enemy each
  encounter is a guaranteed crit; subsequent attacks against that enemy cannot
  crit until a condition is met. *Calculated assassination.*
- **Entropy's Crown** (Chronomancer) — Cooldowns reduce whenever an enemy takes
  an additional turn, but enemies gain increased initiative. *Manipulating the
  tempo of battle.*

---

## 9. Build-altering keystones (general pool)

Glass Cannon · Last Stand · Blood Price · Critical Momentum · Unstoppable ·
Perfect Timing · Death's Dividend · Overwhelming Force · Arcane Instability ·
Iron Will · Echoing Magic · Relentless · Defiance · Soul Battery

- **Glass Cannon** — substantially increased damage dealt and received.
- **Last Stand** — lower health, greater defensive effectiveness.
- **Blood Price** — certain abilities consume health instead of another resource.
- **Critical Momentum** — crits increase the damage of your next attack.
- **Unstoppable** — immune to the first crowd-control effect each encounter.
- **Perfect Timing** — every fourth ability gains an additional effect.
- **Death's Dividend** — defeating an enemy restores a percentage of primary resource.
- **Overwhelming Force** — attacks ignore a portion of enemy armor but cost more.
- **Arcane Instability** — spell damage fluctuates between greatly increased and reduced.
- **Iron Will** — cannot be critically hit while above 80% health.
- **Echoing Magic** — certain spells repeat at reduced effectiveness next round.
- **Relentless** — consecutive offensive actions become progressively more powerful.
- **Defiance** — taking damage increases the effectiveness of your next defensive ability.
- **Soul Battery** — excess resource generation is stored and spent later.

---

## 10. Cross-class combinations

> *"The real magic happens when players combine multiple class influences."*

These should **emerge organically through the constellation** rather than being
predetermined subclasses.

- **Warrior + Shaman** — elemental weapon specialist. Weapon attacks generate
  elemental charges; crits trigger additional elemental effects; defensive
  imbues improve magical resistance.
- **Mage + Chronomancer** — temporal spellcaster. Spell crits reduce cooldowns;
  consecutive spells generate temporal charges; delayed spell effects gain damage.
- **Rogue + Venomancer** — poison executioner. Poison stacks increase crit
  damage; crits extend poison duration; killing poisoned enemies generates combo
  resources.
- **Paladin + Bloodmage** — blood-forged holy defender. Healing consumes caster
  health for increased effectiveness; Holy attacks generate blood shields;
  low-health allies receive stronger defensive benefits.
- **Warlock + Necromancer** — master of corruption and death. DoTs strengthen
  against enemies with multiple debuffs; killing afflicted enemies generates
  resources; corruption becomes harder to remove.
- **Hunter + Tinker** — engineering marksman. Ammunition generates mechanical
  charges; critical ranged attacks trigger secondary effects; certain defensive
  abilities deploy countermeasures.

---

## 11. Respec and experimentation

- Prestige points are **permanently earned**.
- Players can refund allocated nodes.
- Respecs cost an **increasing in-game currency** amount.
- Major choice nodes can be changed through respec.
- **No node should permanently lock a character out of the constellation.**

The goal is to make experimentation possible without making every decision
meaningless.

---

## 12. Long-term progression stages

- **Early** — attribute improvements, basic combat bonuses, first class
  influence pathways.
- **Intermediate** — notable modifiers, first major exclusive choices, access
  to neighbouring class regions, initial cross-class combinations.
- **Advanced** — powerful keystones, multiple class influence pathways,
  specialized mechanical combinations.
- **Endgame** — legendary keystones, deep cross-class synergies, hybrid builds,
  extremely expensive and highly specific pathways.

The player should always have something interesting to work toward.

---

## 13. Balance rules

1. Prestige expands possibilities rather than increasing damage indefinitely.
2. Class identity must remain recognizable.
3. Cross-class influences enhance mechanics, they do not erase the original class.
4. Mutually exclusive nodes create meaningful build decisions.
5. Defensive, offensive and utility builds must all have viable pathways.
6. No single route becomes mandatory for every character.
7. Major modifiers must be tested against the turn-based combat system.
8. **Avoid effects that trigger recursively or generate infinite action/resource loops.**
9. Party-wide modifiers need particular care — their power scales with party size.
10. The system must reward experimentation and creative combinations.

---

## 14. System-wide rules to define before any implementation

1. **Proc limits** — triggered effects must not recursively trigger themselves.
2. **Trigger ownership** — does an effect trigger from the character's own
   actions, allies, summons, reflected damage, DoT ticks, or secondary attacks?
3. **Turn timing** — immediate, end of action, end of turn, or start of round?
4. **Stacking** — max stacks, refresh rules, whether copies coexist.
5. **Cooldown interaction** — can reductions affect abilities already used this
   round? Can cooldowns reach zero?
6. **Death and encounter resets** — which counters reset between battles?
7. **Exclusive choices** — the lock must be visible *before* the player commits.
8. **Class identity** — cross-class influence adds a dimension, it does not make
   the original class irrelevant.
9. **Balance** — compare by expected value over a full encounter, not peak burst.
10. **Specialization compatibility** — a modifier must not be a dead node for
    most of its intended audience.

---

## 15. Future systems

- **Prestige Mastery Challenges** — encounters testing investment in a
  particular class influence.
- **Legendary Constellation Nodes** — rare nodes requiring prerequisites from
  several different class regions.
- **Hidden Pathways** — secret connections found through exploration, quests or
  hard encounters.
- **Class Influence Collections** — cosmetic rewards for deep investment in
  other class regions.
- **Prestige Milestones** — titles, visual effects and achievements at major
  thresholds.
- **Legendary Build Recognition** — achievements for unusual combinations, such
  as investing deeply in three or more class regions.

---

## 16. Open questions for the next pass

This batch contains **28 exclusive pairs, 14 experimental concepts and 4
legendary capstones.** It is a concept library, not a final node count, and it
does not claim to cover every class.

The next pass should use the game's **real** class and spec roster (30 classes,
97 talent trees). For each candidate node, record: eligible classes and specs;
the exact abilities, passives, resources and status effects affected; point cost
and prerequisites; whether it is exclusive with another node; trigger conditions
and internal cooldown / proc limit; expected impact over a typical encounter;
and potential interactions, exploits and edge cases.

**Known gaps to resolve against the live game:**

- The brainstorm names classes that may not match the real 30-class roster
  (e.g. "Death Knight", "Warlock" appear here; the game ships Felsworn,
  Knight of Xoroth, Runemaster, Starcaller, Primalist, Templar and others).
  Every node needs remapping onto classes that actually exist.
- Several concepts assume mechanics the engine does not yet have — initiative
  manipulation, delayed/repeating casts, summon sacrifice, malfunction rolls.
  Each needs an engine check before costing.
- Prestige already exists in the game as a level 60 → 1 reset. How the
  constellation attaches to that loop is undecided.

**Design philosophy:** Prestige should not simply make a character bigger. It
should let the player decide what kind of character they become.

---

## 17. Kyle's notes on the concept art (7 Nov)

Kyle produced a visual of the constellation — 30 class sigils around the rim
of a single interconnected web, with a legend for Starting Position / Class
Path / Shared Path / Keystone / Legendary Node, titled *"30 CLASSES · 70
SPECIALIZATIONS · INFINITE POSSIBILITIES"* and *"CHOOSE · ADAPT · EVOLVE"*.

His two notes on it:

> *"obviously the classes need to be way more seperated, and there needs to be
> WAY more nodes."*

Both are direction for the real layout, not criticisms of the concept:

- **Class separation.** The art has the 30 class regions crowded onto one rim
  with short paths between neighbours. The real tree needs far more distance
  between starting positions, so reaching another class's region is a genuine
  investment rather than two nodes sideways. This is what makes Class
  Influence (§3D) cost something and what keeps class identity recognizable
  (§13). Path of Exile's tree is the reference: a character sees most of the
  tree as unreachable.
- **Node count.** The art shows on the order of a few hundred nodes. PoE ships
  roughly 1,500. The density matters because the cheap attribute nodes (§3A)
  are what pad the distance between notables — without enough of them, every
  path is short and every build reaches everything.

Also recorded from the art: the game ships **30 classes and 70
specializations**, which is the roster any real node list has to be built
against — see the class-mismatch gap in §16.
