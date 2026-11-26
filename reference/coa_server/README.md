# CoA server reconstruction: class mechanics reference

Pulled 26 Nov 2026 from https://github.com/Conquest-of-AzerothCore/azerothcore-wotlk-coa
(commit 3b7091ec58930bef01c988f9578adf86b3dde4e1). Kyle: "any way to mine CoA data from here".

That project rebuilds the lost Conquest of Azeroth server on AzerothCore from the client's own data (Spell.dbc,
the other client tables, the tooltips) plus recovered changelogs and combat logs. It's GPL-2. These files are kept
as **reference only**, beside `reference/coa_sidekick/`. Nothing in the game reads them.

## What's here
- `<class>-completion.md` (15 classes): their reconstructed mechanics, rule by rule.
  - Covers: Barbarian, Chronomancer, Cultist, Felsworn, Guardian, Knight of Xoroth, Necromancer, Pyromancer, Starcaller, Sun Cleric, Templar, Tinker, Venomancer, Witch Doctor and Witch Hunter.
  - Includes resource caps, what spends what, per-stack scaling, refunds, proc ownership and coefficient notes.
  - Example: "Demonfire remains a six-stack aura... Skulltaker and Warbringer gain 20% and 18% damage per Demonfire".
- `class-conformance-rulings.md`: their general rulings on reading tooltips literally.
- `level-scaling.md` and `item-power.md`: how CoA scales spells and items by level.
- `CoARotationData.h`: rotation priorities for every class and spec. It's a list of (spec, ability, condition, value) rules, such as "use X when the target is missing debuff Y" or "when resource Z is at least N". Useful for recruit combat AI.

## What's not here, and why
- **Base numbers** (damage per rank, mana costs, durations) live in the CoA client's Spell.dbc, which isn't in that repo.
  Their scenarios read it from a private client copy. For numbers, Frontier keeps its own balance tables.
- **Stormbringer, Primalist, Reaper, Runemaster, Ranger and Bloodmage** have no completion doc there yet, only tests and scattered scenarios.
- **The 5,000 or so gameplay scenarios and the C++ handlers** are left in the source repo. They can be pulled class by class if a question needs them.
