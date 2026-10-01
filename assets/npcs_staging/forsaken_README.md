# Generated Forsaken sprite sheet — raw, not yet cropped

Imported 2026-09-09/10. The FIRST sheet generated this session (using
easy-peasy.ai), which set the visual bar and prompt-writing pattern for
every sheet that followed. 16 characters in one generation (8 male, 8
female). Real WoW Undead/Forsaken lore was researched before writing the
prompt specifically to avoid the two failure modes these generators
default to - full skeleton or generic zombie - neither of which matches
actual Forsaken design (a former human in visible decay, mostly intact
body with only small patches of exposed bone, glowing YELLOW eyes per
Wowpedia, dignified rather than shambling posture).

## What's here

- `forsaken_contact_sheet_raw.png` — 8 male + 8 female Forsaken, each
  with a distinct face, hairstyle, and clothing/decay pattern. Kyle's
  reaction: "these actually look good... genuinely reads as WoW
  Forsaken, not skeleton, not zombie."

## Known issues before this is usable (same as every sheet this session)

1. **No real transparency** - RGB, checkerboard baked into pixels.
2. **Not a uniform grid**, no individual numbered labels (only row-level
   MALE FORSAKEN / FEMALE FORSAKEN headers) - same cropping difficulty
   as the Tauren/Troll/Dwarf+Gnome sheets, harder than the later
   numbered sheets (Orc/Elf/Goblin/Monster A/Monster B).
3. **Single front-facing pose only** - fine for the confirmed NPC/
   portrait use case.

## Next steps when picked back up

Same as every other npcs_staging folder - crop, add real alpha, decide
integration path (new race folder under assets/npcs/, since no
"forsaken"/"undead" folder currently exists there - only skeleton/
zombie, which are a different, cruder design).
