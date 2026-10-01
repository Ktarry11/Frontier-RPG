# Staged sprite packs — not yet wired into the game

Imported 2026-09-09 (Kyle: "here are some more sprites to include in the
game files"). These are NOT yet usable in-game — nothing in
world/race_registry.py, world/creature_manager.py, or any spawn table
references them. This folder exists so the raw art is in the repo and
findable, without pretending it's already integrated.

## What's here

- `soldier_pack/` — Tiny RPG Character Asset Pack v2.0, Soldier character.
  Idle/Walk/Attack01-03/Hurt/Death spritesheets (600x100, 6 frames of
  100x100 each) + an arrow projectile sprite (two sizes).
- `orc_soldier_pack/` — same pack, Orc character. Idle/Walk/Attack01-02/
  Hurt/Death spritesheets, same frame layout.

Kyle uploaded 4 versions of this same asset pack (a "Demo" and three
numbered releases, 1.02 through 2.0). Only v2.0 was imported — it's a
strict superset of the other three (same art, plus the projectile sprites
and source .aseprite files) - so importing all four would have meant
three redundant copies of the same character for no benefit.

## What's NOT done (Kyle: "not sure yet, I'll decide later" on intended use)

1. **Frame-splitting.** Every file above is a horizontal spritesheet
   (multiple 100x100 frames in one PNG), not individual frame files.
   assets/npcs/<race>/<variant>/{down,left,right,up}.png (the format
   world/race_registry.py's sprite_base_path() and ui/sprite_loader.py's
   get_npc_sprite() expect) needs single directional frames, not a sheet.
   This pack's animations are Idle/Walk/Attack/Hurt/Death, not the
   4-directional walk-cycle shape the existing race packs use - reconciling
   those two conventions is real design work, not a mechanical export step.

2. **No race_registry.py entry.** Decide whether Soldier becomes a new
   human appearance variant, a new race entirely, or something else -
   see race_registry.py's existing per-race variant lists for the pattern
   to follow once that's decided.

3. **No spawn-table entry.** Neither character appears in any zone's
   encounter table (data/creatures/encounters.json) or ambient-NPC
   population - they won't appear anywhere in-game until added there.

4. **Orc naming collision to resolve.** The game already has a full
   `assets/npcs/orc/` race folder in active use (player-facing Orc NPCs,
   Horde flavor). This pack's Orc is a distinct enemy-style sprite
   (soldier-armor orc, Attack01/02 combat animations, not the ambient-NPC
   walk cycle the existing orc folder has) - recommend a distinct name
   like `orc_raider` or `orc_marauder` for whatever this becomes, so it's
   never confused with the existing playable-race orc art at integration
   time.
