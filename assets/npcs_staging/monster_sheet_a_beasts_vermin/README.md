# Generated Monster Sheet A — Beasts & Vermin — raw, not yet cropped

Imported 2026-09-10. Companion sheet to Monster Sheet B (Naga/Wilds/
Elemental/Demon - see monster_sheet_b_naga_wilds_elemental_demon/
README.md for the full design reasoning behind splitting monsters into
two themed sheets). 32 characters in one generation (20 Beasts, 12
Vermin), full clean generation with zero drop-off - Kyle's reaction:
"Bro this shit actually doesn't care" (i.e. genuinely good, no
complaints).

## Why this sheet exists

Cross-referencing data/creatures/creatures.json against what's actually
spawnable in caves (data/creatures/encounters.json) showed the
humanoid_* templates (cultists, naga warriors, quilboar, etc. - ~42
creatures) already correctly reuse human/orc-style race sprites. The
genuine gap was real NON-humanoid monster art: beast_fast/large/basic
(21 existing creatures) and vermin_sneaky/swarm (13 existing creatures)
were the two largest under-covered categories, so this sheet was sized
and themed specifically to fill them.

## What's here

- `monster_a_contact_sheet_raw.png` — 20 Beasts (boars, raptors,
  crocolisks, wolves, panthers, bats, bears, lions, hyenas, owls, giant
  rats, "elite" glowing/spiked variants) + 12 Vermin (spiders, scorpids,
  centipedes, cave worms), individually numbered 1-20 and 1-12. Real
  side-profile/three-quarter dynamic monster poses (not the front-facing
  NPC portrait stance the race sheets use) - correct and intentional for
  creature art, matches Monster Sheet B's same convention.

## Known issues before this is usable (same as every sheet this session)

1. **No real transparency** - RGB, checkerboard baked into pixels.
2. **Not a uniform grid**, but individually numbered (1-20, 1-12),
   matching the easier-to-crop convention (same as Orc/Elf/Goblin/
   Monster B).
3. **Side/dynamic monster poses**, not front-facing portraits - treat as
   its own integration category, not mixed into assets/npcs/.

## Next steps when picked back up

Same as every other npcs_staging folder - crop, add real alpha, then
map each creature to a real data/creatures/creatures.json entry (this
sheet was explicitly designed to fill named template gaps - beast_fast/
beast_large/beast_basic/vermin_sneaky/vermin_swarm - so the mapping
should be reasonably direct once cropped, not a guessing exercise).
