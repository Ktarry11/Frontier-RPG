# Crafting: drift, not dominate. Bags capped at 20. Tank weapons carry armour (15 Nov 2026)

## Drift, not dominate

**Kyle:**
- "classes miss out in entire tiers of gear. This will be crippling at frontier level crafting. The vision is that specific materials can DRIFT slightly towards styles, but not dominate. Take mooncloth, it makes Healer gear (mooncloth set in wow) BUT used for lots of other things."
- "rarely is a single spell type a good idea bro unless it's an exception, not a rule."

**Before:**
- Every piece of a material took that material's one role. 44 material-and-armour groups made one kind of gear only: all of Thorium's plate was a tank's, all of Moonsilk a healer's, all of Duskfang a rogue's.
- Whole skill bands served one role.
- The school materials put one spell school on every piece: Emberweave fire, Frostweave frost, Starweave arcane, and every wood's staff, wand and codex.

**Now** (`tools/build_crafted_gear.py`: `plan_drift`, `POOLS`, `SCHOOL_GENERIC`):

1. **Grouping.** Pieces are grouped by trade, material and family: cloth, leather, mail and plate armour; casting weapons (staff, wand, tome); and shooting weapons (bow, crossbow, gun).
2. **The lean.** In skill order, the material's lean takes every third piece, starting with the first.
3. **The rest.** The other pieces walk that family's pool of roles from a starting point set by the material, so neighbouring materials don't repeat each other. The pools:

| Family | Roles |
|---|---|
| Cloth | caster, healer, crit caster, spell-hit caster, high healer, haste caster, spirit caster, battlemage, spirit healer, sturdy caster |
| Leather | agility, healer, rogue crit, feral, assassin, bear, wildheart, caster |
| Mail | hunter, tide healer, hunter crit, mail caster, hunter hit, earthen, haste caster, tank |
| Plate | strength, tank, plate healer, strength crit, crusader, strength hit |
| Casting weapons | caster, healer, crit caster, high healer, spell-hit caster, haste caster, spirit caster, spell pen |
| Shooting weapons | hunter, hunter crit, hunter hit |

4. **Spell power is general.** School identities become general ones:
   - arcane, fire, frost, shadow, nature, holy and hex become caster;
   - arcane crit becomes crit caster;
   - storm and dark haste become haste caster;
   - void, fel and sturdy shadow become sturdy caster.

   The exception is each school material's **signature piece**: its chest or staff, else its first piece. That one piece keeps the school and says what the material is. Felcloth Robe is still shadow, and Stormoak Staff is still nature and haste. There are 23 such pieces across all trades.
5. **What keeps its role.**
   - Named lines are deliberate sets and keep their role: Moonrobe, Earthbound, Prowler's, Barkguard, the woodworking heads and relics.
   - So do jewellery, shields and metal melee weapons.
   - Reputation recipes pin their own identities.
6. **Fallback.** If a drifted role is too much for a low-level piece (a level 20 belt can't carry a spell crit rating under its spell power), that piece keeps its material's lean.

**Result:**
- Single-role groups fell from 44 to 5. The 5 left are deliberate: a named mail set, wooden shields, Ironbark wands and Bronze maces.
- `tools/audit_class_gear_coverage.py`: every one of the 97 specs has at least 3 armour pieces and 3 weapons in every level band.

Examples:
- **Moonsilk:** cuffs and leggings for healers, gloves for a high healer, a haste caster sash.
- **Thorium plate:** tank gauntlets and sabatons, a strength crit girdle, crusader legplates.
- **Duskfang:** rogue boots and belt, feral bracers, agility gloves, healer pants.
- **Felcloth:** a sturdy caster mantle and gloves, a crit caster's cuffs, and the Felcloth Robe as its shadow signature.

## Bags: capped at 20, eight tailoring bags (`tools/cap_bags.py`)

**Kyle:** "They're way too strong and easy to make.....like 28 spot bags? No thanks. Have tailor bags capped out at 20 slots for now..not ever cloth needs a bag."

- **Every bag is capped at 20 slots, shop bags included.** Booty Bay sold 24-slot bags, which would beat the tailor's best the day you bought one.
- **The ladder is re-spaced** (4, 6, 8, 10, 12, 14, 16, 18, 20), with prices following the slots.
- **Tailoring keeps eight bags:**

| Cloth | Skill | Slots |
|---|---|---|
| Linen | 20 | 6 |
| Wool | 70 | 8 |
| Silk | 110 | 10 |
| Mageweave | 140 | 12 |
| Runecloth | 255 | 14 |
| Shadowsilk | 270 | 16 |
| Bloodsilk | 295 | 18 |
| Bloodsilk | 300 | 20 |

- **Nine bag recipes are gone:** cotton, hempen, spidersilk, gossamer, shadowsilk (the Tideworn chest), and starweave and bloodsilk duplicates. Their bags are still in shops and loot.
- **Old saves:** a bag already in a save keeps the size it was made with.

## Tank weapons carry armour, and only tank weapons

**Kyle:**
- "Armor can be on tank weapons. We see this in wow. Change attack power to 10 more agility and rest of the attack power goes into armor."
- "We can have 1H swords that are obviously tank with armor too!" He sent WoW's King's Defender: Stamina, 182 armour, defense and hit.
- "DONT GO THROWING ARMOR ON EVERY SINGLE WEAPON PLEASE."

There are two identities, and they're the only weapons that carry armour:

| Identity | Shape | Used by |
|---|---|---|
| `bear_weapon` | Stamina and Agility in equal parts, dodge, bonus armour | Every bear or beetle staff: the five Barkguard staves, the Spire-Warden's Staff |
| `tank_weapon` | Stamina, armour, defense, hit (King's Defender) | One-handed swords, maces and axes with the tank role: the Mithril Warhammer, the new Bastion Warden's Blade |

Six crafted weapons carry armour, apart from shields.

Bonus armour is folded into the item's armour value, never shown as a stat line (`qa_whole_number_gear`).

**Spire-Warden's Staff** (Thunder Bluff exalted):
- 218-296 damage, speed 3.6.
- +26 Stamina, +25 Agility, +12 dodge rating, 43 armour.
- Flavour: "If you can hold them, I can heal you - R".

My first suggestion (30/20/40 AP/14) was over the item's budget. This keeps the same shape inside the budget every other item uses.

**Bastion Warden's Blade** (Crimson Codex exalted):
- It replaces the Codex's tank cloak, so the Codex still has a tank piece at exalted.
- 162-219 damage, speed 2.4.
- +25 Stamina, 127 armour, +13 hit rating, +12 defense rating.

## Two card fixes found while rendering the tank weapon

- **Flavour text never showed on gear cards.** `ui/screens/inventory_screen.py` drew every line but the flavour. Rares and epics now show it in gold quotes, the way WoW does.
- **Fighter staves showed a maul's icon.** They're priced as two-handers, and the icon was picked from that stand-in type. It now uses the item's own type, staff.


## Weapon armour is cheap; the Spire-Warden as Kyle wants it

**Kyle:** "Why is armor so expensive on weapons? Reduce armor cost on weapons! Also change the agility from 25 to 35 and change Stam to 20."

**Cheaper armour on weapons:**
- A tank weapon's armour is bought at `WEAPON_ARMOR_COST` = 0.04 a point, a fifth of the 0.2 it costs elsewhere.
- It's priced outside the stat split, so the stats keep their share of the budget.

**The new shapes:**
- `bear_weapon`: Agility 0.48, Stamina 0.28, dodge 0.18, armour 0.06.
- `tank_weapon`: Stamina 0.5, hit 0.2, defense 0.18, armour 0.12.

**The two exalted tank weapons now:**

| Item | Stats |
|---|---|
| Spire-Warden's Staff | +35 Agility, +20 Stamina, +12 dodge rating, 109 armour |
| Bastion Warden's Blade | +37 Stamina, +14 hit, +17 defense, 217 armour |

**Crafted tank weapons follow the same shapes:**
- The Barkguard staves run from 18 armour at level 19 to 89 at level 58.
- The Mithril Warhammer has 110.

## Past level 60, the stat budget bends upward

**Kyle:**
- "Things over lvl 60 and higher ilvl will need a better way to measure stats."
- "I want past 60, especially with rares, epics and stuff to work towards that the linear line changes."

**The problem:**
- A piece's stat budget was a straight line in its item level.
- Past 60 the world keeps compounding: `combat/world_curve` adds 3.5% a level, so the world is 56% bigger at 73 than at 60.
- On the straight line, an item level 73 epic was only 22% better than a 60 one.

**The fix:** `entities/item_budget.budget_level(item_level, rarity)`.

- Up to item level 60, nothing changes.
- Past 60, a rare or better spends its budget as if its level were 60 × 1.035^(levels past 60 × steepness).
- **Steepness by rarity:**
  - Epic: 1.0 (follows the world exactly).
  - Rare: 0.75.
  - Legendary: 1.15.
- Commons and greens stay on the straight line.

| Item level | 61 | 66 | 73 | 80 | 92 |
|---|---|---|---|---|---|
| Epic budget level | 62.1 | 73.8 | 93.8 | 119.4 | 180.4 |
| Rare budget level | 61.6 | 70.0 | 83.9 | 100.5 | 137.0 |

**Where it applies.** Every budget asks this one function:
- `LootGenerator`, for drops and shops;
- `tools/build_crafted_gear.py`, for crafted and reputation gear;
- `expected_budget`, for the audits.

**Existing item level 61 drops** (14 Tempest Isle and secret pieces) would gain under 2%, so they're left as authored.

**Where the reputation gear lands now:**
- **Item level 73 epics:** about 28% more stats than before.
  - The Spire-Warden's Staff keeps the shape Kyle set: Agility leads at 35:20 against Stamina, plus dodge and armour. It now comes out at +45 Agility, +26 Stamina, +15 dodge, 140 armour.
- **Item level 67 blues:** about 7% more.
