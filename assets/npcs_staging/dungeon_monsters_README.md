# Dungeon monster sprite packs — not yet wired into the game

Imported 2026-09-09 (Kyle: "they will be DUNGEON monster sprites! Since we
can see the spawn locations inside the dungeons"). Like the other folders
under npcs_staging/, nothing here is referenced by any live game system yet
- this is raw art, staged and organized, waiting on an integration pass.

## Intended use (per Kyle)

These are meant to become real per-creature spawn/boss icons, the same
system built for boss_marker tiles on 2026-09-06/09 (see boss_icons.py,
ui/tilemap_renderer.py's cave_spawns rendering block, and
ui/screens/map_screen.py). That system currently maps a creature's
`template` field (from data/creatures/creatures.json) to one of a small
set of hand-picked portrait icons via TEMPLATE_ICON. These 27 new
characters are strong candidates to either extend that template-level
mapping with more variety, or - a bigger but more accurate change - move
toward per-creature-NAME icons instead of per-template, now that there's
enough real art to support it. That's a design decision for the
implementation pass, not made here.

## What's here

### dungeon_monsters_pack1/ (15 characters)
Goblins (archer, fanatic, fighter, occultist, wolf rider), lizardfolk
(archer, gladiator, scout, spearman), halflings (assassin, bard, ranger,
rogue, slinger), bestial lizardfolk. Each folder has the character's
.aseprite source, a .gif preview, and the actual sprite sheet PNG (mostly
64x16 - 4 frames of 16x16). `_contact_sheet.png` shows all 12 monster
variants at a glance (bestial lizardfolk/halfling bard/halfling ranger
weren't in the original contact sheet grid - check individual folders).

### dungeon_monsters_pack2/ (10 characters, NOT all dungeon-appropriate)
Elves (bladedancer, enchanter, lord, sharpshooter, wayfarer), merfolk
(aquamancer, impaler, javelineer, mystic, scout). Same per-folder
.aseprite/.gif/.png structure. `_contact_sheet.png` shows all 15 (see
note below on the 5 not listed above).

**Flagged for review before use as dungeon spawns:** this pack's source
zip also included "Adventurous Adolescent", "Boisterous Youth", "Joyful
Kid", "Overworked Villager", and "Playful Child" - unarmed, civilian-
styled sprites (visible in the contact sheet's bottom two rows) that read
as town/ambient-NPC flavor, not dungeon monsters. They were staged here
along with everything else from the zip rather than silently dropped, but
almost certainly belong in assets/npcs/ as ambient-NPC art (see
world/ambient_npc_manager.py) instead of a dungeon monster/boss pool if
Kyle wants them used at all.

## What's NOT done

1. No template or per-creature mapping in boss_icons.py yet.
2. No frame extraction - each PNG above is a small multi-frame sheet
   (mostly 4 frames), not a single ready-to-use portrait. The existing
   boss_icons.py pipeline (see /tmp work from 2026-09-06's boss-icon
   session, or just redo it) crops one clean frame, pads to a square
   canvas, and resizes to 64x64 - the same process would apply here.
3. No entry in data/creatures/creatures.json linking any of these to a
   real creature name/template.
