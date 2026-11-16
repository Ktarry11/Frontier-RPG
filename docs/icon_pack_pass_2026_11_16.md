# Kyle's icon pack: epics, crafted gear and consumables (16 Nov 2026)

Kyle, 10:03: "every unique item in the game can only have ONE icon". 10:18, sending the pack: "Take what you need
and include it for current crafting and cooking or other professions as needed! A lot of it was never utilized."
10:26: "We can use some of other overlapping images for crafted epics. Since we have too many things. We can make
sets that look similar bro."

## The pack
- Two halves. "WoW Vanilla:Classic Icon Pack" is what was already in the game as `gear_inv_*`. "WoW Icon Pack" (TBC
  and Wrath art: about 1,100 armour and weapon icons, plus potions, food, relics, books and trinkets) was never
  installed.
- The larger half's file names lost their slot words (`Armour/101_2.png`), so its icons were labelled:
  - chest, legs and boots by armour type, from the `Cloth_NN`, `Leather_NN`, `Mail_NN` and `Plate_NN` families
    (each family is a chest, a pair of legs and boots; a small image classifier against the labelled Vanilla
    icons decided which was which, and the result was checked by eye);
  - helmets are the numbered files, gloves, bracers, belts and shoulders were picked out by eye, the Naxxramas
    "Desecrated" set is labelled by its names;
  - weapons by name (bows, crossbows, rifles, halberds, fist weapons, short blades), staves, wands, books, idols,
    totems, librams and trinkets by name. The numbered weapon icons are close-ups that can't be told apart
    reliably, so they're left out.
- The labels are in `tools/pack_icon_labels.json` (879 icons). Only icons that something uses are copied in.

## Named epics (committed earlier today)
- Every world and dungeon epic has an icon no other item uses (`tools/install_epic_icons.py`, 59 icons).

## Crafted gear (`tools/assign_crafted_icons.py`)
- Every crafted piece takes the icon nearest its collection's colour from the game's own icons plus the pack, so
  a collection reads as one set (Kyle's "sets that look similar").
- **Crafted epics** draw from the pack only and never share: all 107 have an icon nothing else in the game uses.
- **Greens and blues:** no collection repeats an icon now (before: 50 collections did). Across the game an icon
  nothing else uses is preferred, then one another crafted piece uses, then one a quest or boss item uses. Some
  slots don't have enough art for all of them (rings, necks, shields, wands, staves), so 125 icons are still on
  more than one green or blue. No crafted piece takes a named epic's icon.
- 415 pack icons came in as `gear_wow_<kind>_<source>`. The procedural roller's `gear_inv_*` prefixes never reach
  them, so a random drop can't take a crafted piece's icon.
- The picks are written to `data/items/crafted_icons.json`, and `tools/build_crafted_gear.icon_for` reads it first,
  so a rebuild keeps them.
- `qa_crafted_icons` passes now (it failed before on repeats inside collections): every piece has its file, no
  collection repeats, colour match 81%, a rebuild keeps every icon, every crafted epic has its own.

## Consumables (`tools/assign_consumable_icons.py`)
- 27 consumables had no art at all: the higher potion ranks, the herb potions and flasks, the newer meals and
  drinks. Each took a pack icon chosen by eye (healing red, mana blue, the herb's own colour, roasts for the
  roasts).
- 20 middle-rank elixirs shared their family's bottle. Each now takes the pack potion nearest that bottle's colour,
  so the family still reads as one.
- 271 consumables, none without art, none sharing. A file named after the consumable now wins over the family map
  (`entities/consumable_icons.icon_for`).

## Found along the way (not fixed, for Kyle)
- **Re-running `tools/build_crafted_gear.py` damages the recipe data.** A run renamed ordinary pieces to their
  secret variants' names ("Starweave Robe" became "Scribe's Starweave Robe"), and changed their rarity and stats.
  The run was reverted. Don't re-run that tool until it's fixed.
- Outside crafting, many quest and boss items still share icons with each other (about 400 icons are on more than
  one item). Fixing that would need art for slots the packs are short on (rings, necks, shields, wands).
