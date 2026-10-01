# Generated Tauren & Troll sprite sheets — raw, not yet cropped

Imported 2026-09-09. Same AI-generation pipeline as the Forsaken sheet
from earlier this session (easy-peasy.ai), following prompts built off
real Wowpedia/Warcraft Wiki research for both races. Both came back as
full 20-character sets (10 male / 10 female each) in a single generation,
with visual consistency holding up across the whole sheet - no
noticeable quality drop-off in later rows, which was a real risk at this
character count.

## What's here

- `tauren_sheet/tauren_contact_sheet_raw.png` — 20 Tauren (10 male, 10
  female). Strong fur-color variety (black, brown, white, grey, tan,
  reddish, mottled), males visibly bulkier with larger horns per the
  prompt's explicit rule, natural leather/bone/totem gear throughout.
- `troll_sheet/troll_contact_sheet_raw.png` — 20 Trolls (10 male, 10
  female). Blue/teal/green skin tones, tusks, tribal tattoos/paint,
  dreadlocks/mohawks/braids, iconic bow/spear/axe weapons.

## Known issues before these are usable

1. **No real transparency.** Both files are RGB, not RGBA - the
   checkerboard "transparent" pattern is baked into the pixels, not an
   actual alpha channel. Same issue as the Forsaken sheet. Needs real
   background removal (not just a crop) before any character is usable
   as a game sprite.
2. **Irregular grid - do not naively grid-crop.** Neither sheet is a
   clean uniform grid: row counts vary (Tauren: 4/4/2 male rows, 4/6
   female rows; Troll: 4/4/2 male rows, 5/5 female rows), and a
   "MALE TAUREN" / "FEMALE TAUREN" text label sidebar eats horizontal
   space on the left of every row. A fixed-size grid slice will cut
   several characters wrong. Row boundaries ARE detectable via a
   per-row pixel-variance scan (checkerboard/empty rows read as low
   variance vs. character rows) - confirmed working as a starting point,
   just needs real iteration per-sheet to get all 20 boundaries exactly
   right, not a single generic script.
3. **Single front-facing pose only**, same as Forsaken - fine for
   portraits/static NPCs (which is the confirmed intended use - Kyle:
   "for NPCs, we don't need them to walk right"), not for a walking
   overworld character needing down/left/right frames.

## Next steps when picked back up

Kyle's call (2026-09-09): finish the current game-systems queue first,
crop/integrate these later. When that happens: crop each of the 40
characters into its own file, run background removal to get real alpha,
then decide integration path (new race folders under assets/npcs/,
or feed into the boss_icons.py-style portrait system like the Forsaken
set is more likely headed for).
