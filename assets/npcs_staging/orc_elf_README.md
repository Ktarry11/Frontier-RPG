# Generated Orc & Elf sprite sheets — raw, not yet cropped

Imported 2026-09-09/10. Same AI-generation pipeline as the Forsaken/
Tauren/Troll sheets from earlier this session. Both came back as full
22-character sets in a single generation each, with consistency holding
up well across the whole sheet.

## What's here

- `orc_sheet/orc_contact_sheet_raw.png` — 22 Orcs (11 male, 11 female).
  Green skin range (chartreuse to dark forest, plus a couple grey-brown/
  tan), tusks, tribal gear, real weapon variety (axes, maces, bows,
  spears, daggers, shields). Females read as properly strong/orcish, not
  softened into a generic fantasy-woman design.
- `elf_sheet/elf_contact_sheet_raw.png` — 22 Elves, split into two
  clearly distinct subraces per the prompt's explicit design rules:
  11 Blood Elf (pale/tan/ruddy skin, gold-blond-white-brown hair, ears
  point UPWARD, red/gold refined-arcane aesthetic) and 11 Night Elf
  (purple/blue skin, ears point BACKWARD, silver/white/green hair,
  tribal tattoos, nature/druidic aesthetic). The two subraces are
  genuinely unmistakable at a glance in the result - no ambiguous
  in-between designs, which was the real risk on a mixed sheet.

## Advantage over the earlier sheets

Unlike Forsaken/Tauren/Troll (which only had a row-level race/gender
label), **both of these sheets have individual numbered labels under
every single character** (1-11 per row/section). This makes precise
cropping much easier - the numbers are a direct reference for matching
a cropped file back to its intended variant description, no guessing
which blob in a grid is "male orc variant 7".

## Known issues before these are usable (same as every prior sheet)

1. **No real transparency** - both files are RGB, checkerboard is baked
   into the pixels, not real alpha. Needs real background removal.
2. **Not a uniform grid** - orc sheet is 2 rows of 6 + 1 row of 5 per
   gender (11 each); elf sheet is 2 rows of 6 + 1 row of 5 per subrace
   (11 each). Same "don't naively grid-slice" caution as the other
   sheets, though the numbered labels make manual/semi-automated
   cropping meaningfully faster here.
3. **Single front-facing pose only** - fine for the confirmed NPC/
   portrait use case, not a walking overworld sprite.

## Next steps when picked back up

Same as tauren_troll_README.md: crop all 44 characters into individual
files, run background removal for real alpha, then decide integration
path. Kyle's call: finish the current game-systems queue first.
