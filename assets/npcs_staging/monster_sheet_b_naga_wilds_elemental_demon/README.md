# Generated Monster Sheet B — Naga, Aquatic, Wilds, Elemental & Demon
# raw, not yet cropped, PARTIAL GENERATION (39 of 44 requested)

Imported 2026-09-10. Companion sheet to Monster Sheet A (Beasts/Vermin -
see note below on that sheet's own staging status). Cave-dwelling
monster art, non-humanoid, meant to fill out the real gaps found in
data/creatures/creatures.json when cross-referencing what's actually
spawnable in caves (see this session's design discussion: humanoid-
shaped enemies like cultists/naga-warriors/quilboar already reuse human/
orc race sprites via the humanoid_* templates - this sheet and Sheet A
cover the genuinely non-humanoid creature templates: beast_*, vermin_*,
undead_basic, elemental_*, demon_*, aquatic_basic).

## IMPORTANT: partial generation

Requested 44 creatures (11 each: Naga/Aquatic, Wilds, Elemental, Demon).
The generation stopped at 39 - Demon section only got 6 of its intended
11 (variants 1-6: fel imp, felhound, voidwalker, greater fel demon,
fel stalker, shadow imp; missing: fel caster demon, void horror,
young felhound, fel-touched hound, imp swarm-leader). Kyle's call:
keep the 39 as-is rather than regenerate for the missing 5 - "well, it
didn't give them all lol. but theyre still nice! these work." If more
demon variety is wanted later, that's a small targeted follow-up
generation, not a full redo of this sheet.

## What's here

- `monster_b_contact_sheet_raw.png` — 39 creatures across 4 sections,
  individually numbered (1-39):
  - **Naga & Aquatic (1-11):** 5 real naga archetypes per Kyle's
    correction that naga don't need wide variety ("mostly in either sea
    witch form, archer, heavy ass naga myrmidon form...and that's more
    or less it") - sea witch, myrmidon, harpooner, elder guardian,
    snake-guard - plus 6 murlocs with real size/age variety.
  - **Wilds (12-22):** 5 centaur archetypes (raider, archer, shaman,
    warlord, outrunner) + 6 harpies (screecher, windcaller, matriarch,
    coastal, witchwing, young).
  - **Elemental (23-33):** 11 elemental types across rock/magma/water/
    crystal/ice, including "elite" larger variants.
  - **Demon (34-39):** 6 of the intended 11 demon types - fel imp,
    felhound, voidwalker, greater fel demon (elite), fel stalker,
    shadow imp. See "partial generation" note above.

## Known issues before this is usable (same as every prior sheet)

1. **No real transparency** - RGB, checkerboard baked into pixels.
2. **Not a uniform grid**, but individually numbered (1-39), matching
   the Orc/Elf/Goblin/Sheet-A convention that makes cropping/mapping
   back to a design intent much easier than the label-free sheets.
3. **Side/three-quarter dynamic monster poses**, not the front-facing
   portrait stance the NPC race sheets use - correct and intentional
   for creatures (matches Monster Sheet A's same convention), but means
   this pipeline is visually distinct from the NPC sheets and should be
   treated as its own category during integration, not mixed into
   assets/npcs/.

## Related: Monster Sheet A (Beasts & Vermin)

Sheet A (32 creatures: 20 Beasts, 12 Vermin - boars, raptors, crocolisks,
wolves, spiders, scorpids, worms, centipedes) - now properly staged
alongside this sheet, see monster_sheet_a_beasts_vermin/README.md.

## Next steps when picked back up

Sheet A and the Human sheet are now both properly staged (see
monster_sheet_a_beasts_vermin/ and human_sheet/). Next real step: crop,
add real alpha, decide integration path for all of it. Total staged
sheets as of this one: 10 (Forsaken, Tauren, Troll, Orc, Elf, Dwarf+
Gnome, Goblin, Human, Monster A, Monster B) - a real crop/integration
session is increasingly overdue.
