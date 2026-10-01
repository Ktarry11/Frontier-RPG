# Generated Goblin sprite sheet (redo) — raw, not yet cropped

Imported 2026-09-10. Same AI-generation pipeline as every other sheet
this session. 24 characters in one generation (12 male, 12 female).

This is a REDO of an existing live race - assets/npcs/goblin/ already
has older-style goblin art in the game. Kyle's stated goal: "I think
i'll replace all NPCs with these sprites" (the nicer AI-generated style
used across this whole session's sheets) - goblin was picked as the
first redo candidate specifically (over a from-scratch human sheet,
which is already well-covered at ~16 male/16 female live) since goblin's
existing art is older/rougher and goblins are common enough in this
game to be worth the upgrade.

## What's here

- `goblin_contact_sheet_raw.png` — 12 male + 12 female goblins, with
  individually numbered labels (1-12 per section, same easy-to-crop
  convention as the earlier Orc/Elf sheet). Real skin tone variety per
  Kyle's explicit ask ("not pure green as obviously BB goblins are
  different than winterspring and gadgetzan") - olive, yellow-green,
  sickly yellow, and pale green-grey all represented across the set,
  not a uniform palette. Clear split between "flashy trader" designs
  (gold chains, cigars, jeweled rings, bright cartel-color coats) and
  "industrial worker" designs (welding goggles, wrenches, soot-stained
  overalls, mining gear), matching the real cartel-to-cartel visual
  range described in Bilgewater/Steamwheedle/Venture Company lore.

## Known issues before this is usable (same as every prior sheet)

1. **No real transparency** - RGB, checkerboard baked into pixels.
2. **Not a uniform grid** - 2 rows of 6 per gender, but DOES have
   individual numbered labels under every character (matches the
   Orc/Elf sheet's easier-crop convention, not the label-free Tauren/
   Troll/Forsaken/Dwarf+Gnome sheets).
3. **Single front-facing pose only** - fine for the confirmed NPC/
   portrait use case, not a walking replacement for the existing
   assets/npcs/goblin/ folder's down/left/right frames as-is - a full
   "replace all NPCs" goal will eventually need directional frames per
   character for any race meant to walk around the overworld, not just
   stand as a portrait/vendor NPC. Worth deciding per-race whether that
   matters before a full replacement pass.

## Next steps when picked back up

Same as every other npcs_staging folder - crop, add real alpha, decide
integration path. This one specifically will also need a decision on
whether it fully REPLACES assets/npcs/goblin/'s existing folder
structure or lives alongside it - Kyle's "replace all NPCs" framing
suggests replace, but that's a real decision to make explicitly during
integration, not assume silently.
