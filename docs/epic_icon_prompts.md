# Epic gear icon prompts — 2 sheets of 48

Kyle, 7 Nov: *"for unique purples I can start to use prompts to get about
48 x 2 icons for epic items. They should be unique looking compared to
current gear."*

## Why these are a separate family

An epic currently draws from the same pool as a quest green. The only thing
marking it out is the rarity tint on the border, so a purple sword and a white
sword are the same picture. `gear_icons.py` now keeps a parallel family —
`gear_epic_<key>_N.png` — and `pick_weapon_icon` / `pick_armor_icon` take a
`rarity`, preferring that family for epic and legendary and falling back to
the ordinary pool for any family with no epic art yet.

So this can land one sheet, or one row, at a time. Nothing breaks while it is
half full.

## Where the files go

Straight into `assets/icons/gear/`, which the resolver already searches. They
are invisible to ordinary drops because every ordinary prefix begins
`gear_inv_`, so a rare can never roll an epic icon by accident.

Naming is positional, left to right, top to bottom:

    gear_epic_sword_1h_1.png   gear_epic_sword_1h_2.png   gear_epic_sword_1h_3.png
    gear_epic_axe_1h_1.png     ...

`tools/slice_icon_sheets.py` does the cutting; it takes the same kind of
manifest as the background slicer and names each cell from it.

## House style for BOTH sheets

Put this at the top of every generation, then append the per-item line:

> Game inventory icon, single object centred on a plain dark neutral
> background, no border, no frame, no text, no character, no hands. Painted
> fantasy style, strong rim light from the upper left, deep shadow on the
> lower right. Item fills about 85% of the square. Square 1:1.

And the thing that makes them read as epic rather than just "nicer":

> Epic tier: ornate and clearly magical. Violet or amethyst accents somewhere
> on the object — a gem, an inlay, an energy glow along an edge. Gold or
> blackened-silver metal rather than plain steel. Visible enchantment: faint
> runes, a wisp of arcane light, or a glow from within. Never plain, never
> rusted, never mundane.

**DO NOT say "keep the violet consistent".** That line was in the first
version of this file and sheet 1 came back as forty-eight purple objects.
Kyle, 7 Nov: *"we need to fix everything looking violet"*. What ties the
family together is CRAFTSMANSHIP — elaborate shaping, filigree, gem settings,
engraved runes, an enchanted sheen — not one hue. The rarity border already
tells the player it is epic; the icon does not have to shout it in a single
colour. So instead:

> Vary the accent colour across the grid — amethyst, sapphire, emerald, ruby,
> amber, teal, pale gold — and vary the cloth and leather dyes too: deep red,
> forest green, midnight blue, bone white, oxblood, charcoal. No two adjacent
> cells should share an accent colour. Do not make the sheet monochrome;
> purple should appear on no more than about a quarter of the items.

Also ask for **generous dark gutters, nothing overhanging into a neighbouring
cell**, and ~80% fill rather than 85%. On sheet 1 a polearm tassel reached
into the shield beside it and the slicer had to widen its trim to 1/14th of a
cell to cut it back out.

---

## Sheet 1 — weapons (48 = 16 families x 3)

Three variants each. Make them differ in SILHOUETTE, not just in colour, or
the three read as one icon recoloured.

| key | 3 variants |
|---|---|
| `sword_1h` | a straight knightly blade with a winged crossguard and amethyst pommel; a curved sabre with a glowing violet edge; a broad leaf-shaped blade with runes down the fuller |
| `sword_2h` | a greatsword with a cathedral-window crossguard; a flamberge with a wavy blade and purple fire along it; a slab-like executioner blade, gold-chased |
| `axe_1h` | a crescent hand axe with a gem set in the eye; a bearded axe with a spiked haft; a double-bit axe with violet energy arcing between the heads |
| `axe_2h` | a great double-bit axe with a skull boss; a halberd-axe with a hooked back spike; a single-bit greataxe with a runed blade and trailing light |
| `mace_1h` | a flanged mace with a glowing amethyst core; a gold sceptre topped with a faceted gem; a spiked war-club wound with runed bands |
| `mace_2h` | a two-handed maul with a cube head and inset gems; a great flanged hammer, gold on blackened steel; a pillar-headed maul crackling with violet light |
| `dagger` | a wavy kris with a purple-glowing edge; a slim stiletto with a gem pommel and gold filigree; a curved ritual knife with a hooked tip and rune etching |
| `staff` | a staff crowned with a floating amethyst orb; a gnarled branch staff with a lantern of violet fire; a straight gold rod with a ring of orbiting runes |
| `polearm` | a glaive with a long curved blade and tassel; a spear with a leaf head and gem collar; a halberd with an axe blade, hook and glowing spike |
| `shield` | a kite shield with a raised gold boss and violet gem; a round shield with a runic rim and arcane sheen; a tower shield with a cathedral face and inset crystals |
| `bow` | a recurve bow of pale wood with gold tips and a glowing string; a compound horn bow wrapped in runed cord; an ornate longbow with a floating amethyst at the grip |
| `gun` | an ornate blunderbuss with a flared gold muzzle; a long rifle with a runed barrel and amethyst stock inlay; a pistol with scrollwork and a glowing chamber |
| `wand` | a slim gold wand with a floating violet crystal tip; a bone wand bound with runed wire; a twisted rod with an eye-shaped gem |
| `fist_weapon` | a clawed gauntlet-blade with three violet talons; a spiked knuckleduster with gem studs; a crescent punch dagger with gold filigree |
| `tome` | a thick grimoire clasped in gold with a violet gem lock; an open book with glowing runes rising off the page; a chained black tome with an eye on the cover |
| `libram` | a gold-cased libram on a stand, radiant; a slim prayer book with ribbon and amethyst inlay; a stone tablet-libram with carved glowing script |

## Sheet 2 — armour (48 = 12 slots x 4 materials)

Four per slot: **plate, mail, leather, cloth**, in that order left to right.
The material must be readable at a glance — plate is solid shaped steel, mail
is visible rings, leather is stitched hide with buckles, cloth is draped fabric
with trim.

| key prefix | the object |
|---|---|
| `head` | a full helm / a coifed helm / a hooded mask / a circlet or crown |
| `shoulder` | spiked pauldrons / ringed spaulders / studded shoulder guards / a mantle with gem clasps |
| `chest` | a breastplate / a hauberk / a stitched cuirass / a robe front with embroidery |
| `hands` | gauntlets / mail mitts / bracered gloves / long gem-cuffed gloves |
| `waist` | a plate girdle with a gem buckle / a ringed belt / a buckled leather belt / a sash with hanging charms |
| `legs` | legplates / chain greaves / leather leggings / draped trousers with trim |
| `feet` | sabatons / mail boots / cuffed boots / soft slippers with gold thread |
| `wrist` | vambraces / mail bracers / strapped bracers / embroidered cuffs |
| `back` | a heavy mantled cloak / a chain-trimmed cape / a hide cloak with fur / a long flowing cloak with runed hem |
| `neck` | a gorget with a central gem / a chain collar / a corded pendant / a jewelled necklace |
| `ring` | a thick signet with a violet stone / a braided band / a carved bone ring / a delicate gold band with a floating gem |
| `trinket` | a sealed reliquary / a compass-like device / a pouch of charms / a floating arcane sigil |

For `neck`, `ring`, `trinket` and `back` the ordinary table does not split by
armour type, so the four variants are just four different designs rather than
four materials — name them `gear_epic_neck_1..4` and so on.

---

## After the sheet lands

    PYTHONPATH=. python3 tools/slice_icon_sheets.py SHEET.jpg --apply

Then nothing else. The pickers find the new family by prefix, and every epic
in that family switches over on the next drop. Items already in a save keep
the icon they were stamped with.
