# The item curve: Felwood, Tempest Isle and the Plaguelands (16 Nov 2026)

Kyle, 09:56: "So if the item score is too weak we can improve it bro. We can look at the Felwood, Tempest Isle and
the plaguelands all at once."

## What was wrong
- The open-world rares in these zones were built by LootGenerator, which spends a budget as a plain sum split by the
  suffix it rolled. The curve (`entities/item_budget.py`) reads stats through the 1.5 / 2-3 norm, so the same budget
  landed anywhere from a tenth of the line to on it.
- Medians against the curve before the fix: Felwood's rares 0.71, the Plaguelands' 0.62 and 0.69, Tempest Isle's
  0.93 (a handful far off). The game's loot as a whole sits at 0.95.
- **The curve did not price single-school spell power at all**, so every staff or wand carrying nature, shadow,
  fire, frost, arcane or holy power read as nearly worthless (Mycelial Staff: 1% of its budget).
- 72 generated rares had rolled none of the stat their template exists for: Stamina-only caster gloves, a
  resistance-and-healing wand.

## What changed
- **School spell power is priced**, from Kyle's own rule rather than fitted: one Intellect buys 1.5 spell power
  or about 1.8 of a single school (`entities/power_scale.py`), so a school point costs spell power x 0.55 / (2/3),
  0.592 on this curve.
- **`entities/item_budget.fit_to_curve(item)`** scales an item's budget stats so it sits on the line, keeping its
  stat mix (the curve is linear in a uniform multiply). Weapon damage, speed and armour don't move.
- **`tools/fit_rares_to_curve.py`**:
  - the generated rare tables (Felwood, Tempest Isle, both Plaguelands files) go to exactly 1.0, and a rare
    missing its template's lead stat gets it first, at the size of its biggest stat;
  - the hand-authored tables (Tempest Isle's boss loot, the Felwood and Tempest Shallows quest rewards) keep their
    author's spread, and only items outside the audit's band (0.65 to 1.45) move.
- 202 items moved. Every table in the pass now has a median of 0.97 to 1.0 and nothing out of band.
- **The four open-world builders** (`build_felwood_openworld`, `build_tempest_openworld`, `build_wpl_openworld`,
  `build_epl_openworld`) put every rare on the curve as they write it, so a rebuild can't slide back.

## Before and after (examples)
| Item | Before | After |
|---|---|---|
| Infernal-Ash Boots | 2 Stamina, 1 Arcane Resistance | 22 Agility, 9 Stamina, 4 Arcane Resistance |
| Mycelial Staff | 1 Stamina, 56 nature and 56 shadow power | 48 Intellect, 1 Stamina, 48 nature and 48 shadow power |
| Abbey Bell-Ringer's Gloves | 2 Stamina | 24 Intellect, 10 Stamina |
| Captain's Last Stand | 16 Stamina, 16 block rating, 16 block value, 5 AP | 10, 10, 10, 3 (it was over the line) |

## Not in this pass
- `audit_item_curve` still fails game-wide: about 1,000 items elsewhere sit under their budget (crafted recipes
  and older quest rewards lead the list). Those are older content and Kyle's call.
