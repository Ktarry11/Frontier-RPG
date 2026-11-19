# Master crafting: level-60 gear (18 Nov 2026)

Kyle, 18 Nov 2026:
- "I'll ALWAYS want crafting to be competitive to raiding/Dungeons."
- "Then we can add crafting for new gear for each profession."
- "Keep going."

His answers: a new **Master** tier, cap 325, taught by the same trainers as Artisan at level 60. The materials are
level 60's two per kind, the two lowest top-tier rungs of each ladder (`docs/heroic_design.md`).

## The tier

| Tier | Cap | Level | Cost |
|---|---|---|---|
| Artisan | 300 | 40 | 60g |
| **Master** | **325** | **60** | **150g** (the rep discount applies) |

`data/professions/professions.json`, `Character.PROFESSION_TIER_CAPS`. The cap covers exactly the first two
level-60 tiers (skill 310-320). Later tiers raise it again with raid content. Gathering a level-60 node can now skill
up to the trade's own cap (Master).

## The materials, by trade

| Trade | Blues: the first rung | Epics: the second rung (+ a gem) |
|---|---|---|
| Tailoring | Bolt of Dreamsilk (new, 3 Dreamsilk) | Bolt of Chronoweave (new, 3 Chronoweave), Glacier Sapphire |
| Leatherworking | Manticore leather | Chimera leather, Sylvan Emerald |
| Blacksmithing | Frostforged Silver bars | Sylvanite bars, Sylvan Emerald |
| Woodworking | Voidwood planks | Dreamwillow planks, Glacier Sapphire |
| Jewelcrafting | Frostforged Silver, Glacier Sapphire | Sylvanite, Sylvan Emerald, Glacier Sapphire |
| Engineering | Frostforged Silver, gear assemblies | Sylvanite, Glacier Sapphire |

The raw ten come from heroics for now, and from the level-60 zones once those are built. Smelting, planking and gem
cutting already existed; the two bolts are new.

## The gear (94 recipes, `tools/build_master_crafting.py`, ids `m60_`)

- **Blues: item level 66, worn at 60, level with a heroic's drops.** Taught by the trainer from skill 300 to 318.
  - Tailoring: a nine-piece Dreamsilk caster and healer set.
  - Leatherworking: an eight-piece Manticore leather set and a six-piece Manticore-Scale mail set.
  - Blacksmithing: an eight-piece Frostforged plate set, plus a greatsword, longsword, shield and healer's hammer.
  - Woodworking: a Voidwood staff, longbow, codex, wand and totem.
  - Jewelcrafting: two rings and two necks.
  - Engineering: a rifle and two pairs of goggles.
- **Epics: item level 68, worn at 60, level with T1 and Exalted.** Skill 320-325. Their patterns only drop from heroic
  bosses (15% a boss, `world/heroic.roll_pattern`, source "heroic"), and no trainer or world drop has them.
  - Tailoring: Chronoweave Cowl, Vestments, Trousers and Cloak of Hours.
  - Leatherworking: Chimera Hide Jerkin and Leggings, Chimera-Scale Hauberk and Legguards.
  - Blacksmithing: Sylvanite Warhelm, Breastplate, Greataxe and Aegis.
  - Woodworking: Dreamwillow Greatstaff and Warbow.
  - Jewelcrafting: Sylvanite Signet of Frost and Sylvan Emerald Torc.
  - Engineering: Sylvanite Hand Cannon and Gyro-Goggles.

**A little for every class** (Kyle: "We can have a little bit for most classes"). A second pass added 27 pieces for
the specs that got little or nothing:
- the strength-and-intellect plate wearers (Paladin, Cultist, Primalist, Sun Cleric and Knight of Xoroth tank specs):
  a Frostforged Crusader helm, breastplate and legplates and a warmace, plus Sylvanite Bastion Legplates and a
  Crusader's Hammer at epic;
- the plate healers: a Lightbringer mantle and chestguard, and a Sylvanite Mace of Mending;
- the mail agility fighters (Hunter, Reaper, Witch Hunter, Venomancer, enhancement Shaman): a Manticore-Scale
  brigandine, spaulders and bracers, and a Chimera-Scale Helm;
- the leather and mail healers: Mending vest and leggings, a Tidemail chest, and a Chimera Mending Robe;
- the agility-and-intellect leather wearers (Felsworn, Witch Doctor): a Wildstalker jerkin and leggings, and a
  Chimera Wildstalker Tunic;
- Barbarians: a Brute's harness and leggings;
- a saber, a crossbow, a libram and an idol.

Every one of the 97 specs can now use at least 3 Master pieces, and 91 of them 5 or more (`qa_master_crafting`
check 7).

Every piece is authored like every other crafted item (identity, its own icon, the crafted-gear audit), then put on
the item curve (1.0). That's the same strength as a heroic drop of its level: competitive, never above or below.

## The rep patterns' real ingredients

The Exalted rep patterns (68) were on stand-in ingredients "until the rare ingredients exist". They now use their
trade's second rung at skill 320. The Revered patterns (66) use the first rung at 305. The Honored ones (62) stay
pre-60.

## Not yet

- Showpieces at item level 71 wait for the raid's own materials.
- Tailoring and Leatherworking cloaks, belts and bracers at epic, and more trades (Alchemy, Enchanting) at Master, as
  Kyle wants.

QA: `tools/qa_master_crafting.py`, `tools/qa_no_level60_materials_below_60.py`.
