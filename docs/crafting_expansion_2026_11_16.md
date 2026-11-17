# Crafting expansion (16 Nov 2026, evening)

Kyle's asks from the same evening, and what each one became.

## Cooking (+99): "Keep in mind cooking we can have a food buff and a drink buff!"
- Six meal lines at nine levels each (5 to 59): Hunter's Skewers (agility, stamina), Brawler's Stew (strength,
  stamina), Fisher's Pie (intellect, spirit), Ale-Smoked Ribs (attack power), Omelette (stamina, health per turn) and
  Scholar's Chowder (spell power). Every dish is made of what its name says.
- Five drink lines: herb teas (spirit, mana per turn), Cider (stamina, health per turn), Mead (attack power), Spiced
  Wine (spell power) and herb infusions (Healing Power). A drink restores mana and leaves you Refreshed. That buff sits in its
  own slot (`Character.drink_buff`), so a meal and a drink stack. Saved with the character.
- Eggs (Kyle: "eggs from birds"): Small, Speckled and Giant Eggs drop from birds, raptors, crocolisks, basilisks and
  serpents, 1 to 60 (`entities/meat_drops.LAYS_EGGS`, rolled with the meat). "You found a nest near ...".

## Alchemy (+100): "it is very bare"
- Eight families at nine levels (10 to 60): Tonics of Might, Grace, Clarity, Fury and Sorcery (battle elixirs) and
  Draughts of Vigor, Calm and Mending (guardian elixirs; Mending says "Healing Power").
- Healing and mana potions between the old ones (5, 14, 22, 29, 37), eight flasks (55 to 60) and protection potions
  for fire, frost, nature, shadow and arcane (40 and 55).
- "Maybe lets not heal this much HP and mana": a potion now restores a share of a fixed curve for its own level, not
  the drinker's. Minor Healing about 85, the top potion about 640; mana from about 150 to 1,350.

## Engineering (+89): "another 75 or so", then goggles and guns
- Goggles of leather and gems at seven levels from 6 to 58 for every armour type, each with its own tinted goggle art
  (`tools/make_goggle_icons.py`), and each type's roles taking turns (caster, healer, fighter, tank).
- Guns for every role: fighters, tanks (stamina, hit and defense rating, with armour), healers (Healing Power: the
  Tinker's Invention spec and the Vizier carry a gun) and hybrids (agility and intellect).
- Bombs in five schools at three levels, gadgets (hit, armour, haste, crit, stamina), and shot between the old tiers.

## Enchanting: "large gaps ... 30 to 60, 70 to 110, 120 to 170, 180 to 210"
- Each tier's formulas are spread across their own stretch: Minor 0 to 30, Lesser 35 to 105, plain 110 to 160,
  Greater 165 to 215, Superior 220 to 270, Major 275 to 300. The slots take turns, so it isn't always another bracer.
  A formula takes its tier's rod. `tools/build_enchanting.SPREAD`, written into the data by
  `tools/patch_enchanting_spread.py`.

## Identical gear: "Some of these are identical! we need a bit of diversity here"
- 58 sets of differently named pieces had every stat the same (same trade, armour, identity and item level). 73 pieces
  now take a sister identity: the same kind of item (a caster stays a caster), one that suits the armour, and none
  that matches another in the set. The three skill-300 mantles and the two warplates all differ now.
- Woodworking's healing-heavy sets mix it up: Moonpetal's wand, codex and blossom and Sunheart's codex go to casters,
  and the Sunheart Tideguard becomes a tank's shield.
- `data/items/crafted_identity_overrides.json`, read by `build_crafted_gear.author`, so a rebuild keeps them.
  `tools/diversify_crafted_gear.py`. 20 sets of very low-level pieces (one or two stats, below skill 65) still come
  out the same; at that budget there's nothing left to tell them apart.

## Craftsman Codex
- MerchantTusk sells it on his screen: one more primary profession slot each, 100, 200, 300, 400 gold, then 500 every
  time after. He stops once every trade has a slot. `world/craftsman_codex.py`, `tools/qa_craftsman_codex.py`.

## Icons: "You should have a lot of additional food icons and reagent icons in the icon list"
- 237 new consumables and the three eggs take art from Kyle's icon pack that nothing else in the game uses (alchemy
  by colour: Might red, Grace green, Clarity blue). Two kept a copy of the nearest existing icon where the pack ran
  out. `tools/assign_consumable_pack_icons.py --pack <dir>`.

## Also
- A recipe on a vendor's shelf (and in your bags) says "Requires Jewelcrafting (200)", what it teaches you to make and
  what that does (a piece's stats, a dish's or potion's effect, an enchantment's bonus), and the materials.
  `ui/recipe_tooltip.py`, `tools/qa_recipe_tooltips.py`.
- Booty Bay: the signpost in the bend below the Stranglethorn gate and the one north of the flight master stand
  aside now, the crates that pinched the ramp foot are gone, and the supply store moved off the end of the north pier.
- Item text says "Healing Power", as the character sheet does.
- The professions overview is dark plates with an old-gold edge and a slim gold bar, two columns, no scrolling.
