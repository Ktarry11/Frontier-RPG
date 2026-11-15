# Woodworking expansion (15 Nov 2026)

Kyle: "Massively expand out wood working." And: "we don't want it flooded with garbage things that make no
sense. The crafted items need to be logical and not full of drip stats. Most staves should have spell power or
healing power but ALSO don't forget.....Beetle tanks and bear tanks (venomancer and druids) can use
staves....so agi staves and tank staves are real".

Builder: `tools/build_woodworking_expansion.py` (idempotent; owns recipe ids `wwx_*`, `engx_scope_*`, the
18 new kits and 7 new parts). Then `tools/build_crafted_gear.py` authors the stats, and
`tools/build_recipe_vendors.py` stocks the vendor patterns.

## What the audit found

| Gap | Before |
|---|---|
| Skill 150 to 300 | 14 woods, 2 or 3 pieces each (43 items). Stormoak's caster had no off-hand; Moonpetal's healer had none. |
| Dead planks | Emberwood, Frostheart, Ebonthorn and Sunheart were sawn and made into nothing. |
| Staves | Every one was a caster's. No staff for a bear druid or a Venomancer beetle. |
| Strength polearms | One, at skill 178. Reapers can only use polearms. |
| Shields | Stopped at skill 125. |
| Relics | Nobody made a totem, idol or libram. |
| Upgrade kits | Two (Ashwood, Ironbark) for 16 woods. A Felbark or Moonpetal piece could never be upgraded. |
| Bow parts and scopes | Stopped at skill 140 (+11 damage). |
| Arrows and bolts | Stopped at level 30 (fixed earlier the same day). |

## What it adds: 86 pieces, 18 kits, 4 bow parts, 3 scopes

Woodworking went from 229 to 337 recipes. Every role comes from the wood or a named line, and every number
from the gear builder's identities.

- **Casting weapons (27).** Each wood gets the staff, wand and codex its school calls for.
  - Silverbark, Redbark and Marshwillow get a wand and a codex. Goldenleaf, Bloodwood and Moonpetal get a
    codex (the Moonpetal healer finally has an off-hand). Felbark gets a wand and a staff.
  - Emberwood (fire), Frostheart (frost) and Ebonthorn (shadow, "void": spell power, Intellect, Stamina) each
    get a full staff, wand and codex.
  - Starleaf gets a staff and a wand; Stormoak gets its codex.
  - Sunheart, the skill-300 wood, makes the holy Sunheart Staff (epic) for Sun Cleric, Templar or a smiting
    Priest, plus the Blessed Sunheart Staff (epic) and Blessed Sunheart Codex for healers.
- **Fighter staves (10).**
  - Prowler's and Stalker's staves (cat druid, hunter) lead with attack power and Agility.
  - Barkguard staves (bear druid, Venomancer beetle) carry Stamina, Agility and dodge.
  - Five tiers each, at levels about 18, 29, 38, 49 and 57.
  - See "Fighter staves are two-handers" below.
- **Bows, crossbows and a spear (8).** These fill the gaps in the hunter ladder. The Sunheart Longbow and
  Stormoak Crossbow are epics.
- **Polearms (6).** Four strength Warpikes (levels 23, 34, 45, 56) for warriors, barbarians, Reapers and
  Knights of Xoroth. Two Warden's Glaives (Strength, Intellect, attack power) for paladins and templars.
- **Shields (7).** Tideguards (healing) and Thundershields (nature, haste) for the shaman-shaped classes,
  levels 32 to 59.
- **Relics (20).** Two of each role, at about level 33 to 39 and 47 to 56:
  - Totems: Tide (resto), Storm (elemental), Earthshaker (enhancement).
  - Idols: Grove (healer), Moon (balance), Claw (cat), Barkguard (bear).
  - Librams: Mercy (holy), Zeal (ret), Bulwark (prot).
- **Trinkets (5), each with a proc:**
  - Carved Hawk Fetish: on crit, +35 AP for 3 turns.
  - Barkguard Ward: when hit, a shield of 5% of your health.
  - Moonpetal Blossom: on heal, 70 mana.
  - Emberwood Brand: on damaging spell, 110 fire damage, scaled by the world curve.
  - Stormoak Heart: on damaging spell, +45 spell power for 3 turns.
- **Heads (3).** Bloodroot Mask (feral), Felbark Helm (mail, earthen), Starleaf Crown (wildheart).
- **Upgrade kits (18).** One for every wood with gear. Half are taught by the trainer and half sold as
  patterns, so the trade's trainer share stays inside qa_recipe_sources' 50 to 55%. Icons are the Ironbark kit
  tinted to each plank's colour.
- **Bow and crossbow parts (4):** Bloodroot Limbs +14 (skill 185), Moonpetal Sight Pin +17 (230), Starleaf
  Nock +20 (265), Stormoak Limbs +24 (290). Each is about a fifth of a crafted bow's average hit at its level,
  as Heartwood Limbs is.
- **Engineering scopes (3), kept level:** Mithril +14 (185, trainer), Thorium +18 (245, vendor), Arcanite +24
  (290, drop).

Reagents follow the existing ladders, so nothing asks for a reagent the woodworker can't make yet:
- a stick in every shaft (tier_crafting_reagents);
- glue below skill 150 and resin above;
- fibre: tough, then braided at 195, corded at 260, warded at 290;
- pages: fine, then vellum at 205, leafed at 270, gilded at 300.

The new arrows and bolts were re-tiered the same way.

## Engine and builder changes

- **Fighter staves are two-handers** (`build_crafted_gear.FIGHTING_STAFF`, `as_built`).
  - A staff's damage tier is "staff": a 0.55 dps multiplier, with a 1.8 stat budget to make up for it.
  - That suits a caster but is a trap for anyone who swings it: a Stalker's staff at level 57 hit for
    56-76, where the same staff priced as a two-hander hits for 139-188. Its extra stats were worth far less
    than the damage it gave up.
  - Staves with a feral, bear, crusader, strength or agility identity are now priced as two-handers (damage,
    speed 3.6 and budget) and stay staves.
  - This also moves the three existing crusader staves: Oakheart Staff, Warden's Staff and Crusader's Staff.
- **No stray armour on weapons or trinkets.**
  - The reference item's random "+armor" roll was folding into the armour value, giving a Starleaf Wand 138
    armour and a caster trinket 185.
  - Weapons other than shields, and trinkets, now carry none.
  - This touched 41 existing woodworking weapons, 13 engineering weapons and 13 blacksmithing weapons
    (armour only; none of their stats moved). Jewelcrafting and leatherworking were unaffected.
- **New woods and lines** (`build_crafted_gear`):
  - WOODS: emberwood (fire), frostheart (frost), ebonthorn (void), sunheart (holy, a new identity).
  - WOOD_RANGED: hunter roles for the new woods.
  - WOOD_LINES: Prowler's/Stalker's (feral) and Barkguard (bear).
  - WOOD_RELIC_LINES and RELICS.
  - Warpike (strength polearm) and Thunder/Storm (storm shield).
  - New WOOD_TRINKET_LINES, WOOD_HEAD_LINES and WOOD_PROCS.
  - `weapon_identity` lets a bear staff stay a bear's ("no one tanks with a greataxe", but a druid does with
    a staff).
- `world/upgrade_manager.py`: 18 kits in MATERIAL_KITS.
- `world/attachment_manager.py`: 7 new ATTACHMENTS.
- **Bombs can't be dodged.**
  - qa_engineering caught a Shrapnel Charge landing for 0 on a boar that "parried" it, because physical damage
    rolls the monster's avoidance.
  - `entities/consumable.py` now sets `_unavoidable_hit` on each target for the blast's call, and
    `Monster.take_damage` skips avoidance when it's set.

## Checks

- **build_crafted_gear audit:** 0 failures (no dribbles, power leads, every trinket has a proc).
- **Crafting QA (all pass):** qa_recipe_sources (woodworking 54%, engineering 54%), qa_engineering,
  qa_crafted_icons, qa_profession_subtabs, qa_profession_tabs, qa_trainer_offers, qa_recipe_scroll_safe and
  qa_profession_trainers.
- **validate_content:** no woodworking failures (the remaining gear-no-kit failures are leatherworking and
  tailoring tiers, already there before).
- **In game:** every new piece equips on its classes, among them:
  - Druid: Barkguard Staff, Stalker's Staff, Barkguard Idol, Starleaf Crown.
  - Venomancer: Barkguard Staff.
  - Totems on Shaman, Stormbringer and Primalist; librams on Paladin and Templar.
  - Warpike on Warrior and Reaper; Sunheart Staff on Priest and Sun Cleric.

  Stormoak Limbs take a Frostheart Longbow from 80-109 to 104-133. The Moonpetal, Stormoak and Sunheart kits
  upgrade their pieces.

## For Kyle

- **Kits on crafted epics: DONE.** Kyle: "No. A kit can't upgrade past epic! Hard no."
  - `world/upgrade_manager.KIT_RARITY_CAP = "epic"`: a kit's first application on an epic leaves it epic and
    still gives the +10% stats; the second gives the +20%.
  - The kit panel says "stays Epic".
  - A save holding a kit-made legendary loads back as epic (`Item.from_dict`).
  - Guarded by `tools/qa_upgrade_kit_cap.py`, which kits 39 crafted epics, 379 rares and 376 uncommons twice
    each. 39 crafted epics already had a kit, so this could have happened before today.
- **New epics (7) need art.** They use the epic stand-ins until then; sheet E4 is below.

## Sheet E4: woodworking epics (7 icons)

```
Generate ONE sprite sheet image, 1536x256, a 7 columns x 1 row grid = 7 separate game icons (each cell about 219x256). Flat pure #FF00FF magenta background everywhere. Each icon is ONE single object, centred in its own cell with a WIDE empty margin on every side: nothing touches a neighbour or the image edge. Painterly semi-realistic WoW Classic inventory-icon style for EPIC (purple-quality) crafted gear: rich materials, ornate trim, a faint glow of the item's element, strong readable silhouette, soft dark outline, lighting from the top-left, slight 3/4 view. No hands, no bodies, no text, no labels, no grid lines, no frames, no borders. No magenta or pink inside any icon. Left to right:

SUNHEART (warm honey-gold wood that glows from within like late sunlight, gold leaf inlay, a small sun motif) and STORMOAK (dark storm-grey oak scarred by lightning, copper bindings, blue-white sparks):
1. SUNHEART STAFF: a tall staff of glowing honey-gold wood, its head a carved open sunburst with a bright golden light at the centre
2. BLESSED SUNHEART STAFF: a tall honey-gold staff whose head curls around a soft white-gold flame, small carved leaves and a hanging gold charm
3. SUNHEART LONGBOW: a long recurve bow of glowing honey-gold wood with gold-leaf inlay along the limbs and a gold string
4. SUNHEART TIDEGUARD: a round wooden shield of honey-gold planks, a gold sun boss ringed with carved wave runes, glowing warmly
5. STORMOAK CROSSBOW: a heavy crossbow of dark lightning-scarred oak with copper bindings, blue-white sparks along the prod
6. STORMOAK BARKGUARD STAFF: a thick heavy fighting staff of dark storm-grey oak plated with rough bark guards, copper bands at both ends, faint sparks
7. STORMOAK HEART: a fist-sized knot of dark lightning-struck oak heartwood, cracked, with blue-white light crackling inside the cracks
```

Slice to `assets/icons/gear/gear_epic_crafted_<name>.png`:
- sunheart_staff
- blessed_sunheart_staff
- sunheart_longbow
- sunheart_tideguard
- stormoak_crossbow
- stormoak_barkguard_staff
- stormoak_heart

---

# Spell-hit gems (same day)

Kyle: "add a spell hit gem and also some variations of gems that include spell hit + other."

**Before:** two cuts carried spell hit. Veiled (orange: spell power and spell hit) and Lambent (green: spell
hit and mp5). There was no pure spell-hit gem; Rigid is physical hit.

**Added: four cuts, 38 gems.** 16 are craftable now. The rest sit on the stones above skill 300 and wait with
their ores, as every other cut does.

| Cut | Colour | Stats | Recipe source |
|---|---|---|---|
| Great | yellow | spell hit (+5 to +11 on today's stones) | trainer |
| Vivid | green | spell hit and Stamina | vendor |
| Serene | green | spell hit and Spirit | drop |
| Piercing | green | spell hit and spell penetration | vendor |

- Intellect is a yellow stat like spell hit, and no colour has a yellow two-stat cut, so there's no
  Intellect + spell hit gem.
- Lambent's and Veiled's descriptions still said "Hit Rating" from before the split. All 12 now say "Spell Hit
  Rating".

**How it was built.**
- `tools/build_jewelcrafting.py` doesn't reproduce today's data when re-run. A scratch run of the full chain
  rewrote 8 data files, losing the hand edits made since.
- So the cuts are in its CUTS table, with a SOURCE_FOR override that teaches Great, so a rebuild keeps them.
- `tools/add_spell_hit_gems.py` writes them in place using the builder's exact loop: same budget, rating floor,
  source rule and skill offsets.
- `tools/build_cut_gem_icons.py` has a look for each new cut. Re-running it changed no existing icon.

**Checks:**
- qa_jewelcrafting OK (trainer share 50%); qa_recipe_sources (jewelcrafting 52%); qa_crafted_icons and
  qa_recipe_scroll_safe pass.
- In game: a Great Moonsilver Zircon (+11) and a Piercing Huge Emerald (+4 / +4) socketed in a staff raise the
  wearer's spell hit from 0% to 1.5%.
