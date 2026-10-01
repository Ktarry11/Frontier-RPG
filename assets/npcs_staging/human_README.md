# Generated Human sprite sheet — raw, not yet cropped

Imported 2026-09-10. 28 characters in one generation (14 male, 14
female) - the largest clean single-sheet success this session, zero
quality drop-off across either gender.

## Why this sheet exists (important context for integration)

This is NOT "more human variety" - assets/npcs/human/ already has ~16
male + ~16 female variants live in-game. This sheet exists because Kyle
judged the EXISTING human art as weak ("the human models we have suck.
they are weird") and wants to replace the human base entirely as part
of a broader "replace all NPCs with this nicer style" goal - goblin was
already redone for the same reason (see goblin_README.md). Human was
deliberately scoped as PROFESSION variety rather than a random 28
generic adventurers - the whole point of this sheet is that each
character reads as a distinct kind of person (blacksmith, farmer,
priest, sailor, innkeeper, bard, knight, rogue, etc.), not a palette-
swapped hero.

## What's here

- `human_contact_sheet_raw.png` — 14 male + 14 female humans, each a
  different profession/archetype: warriors, guards, and knights
  alongside blacksmiths, farmers, merchants, sailors, priests, healers,
  innkeepers, miners, and bards. Real age/build/skin-tone variety within
  the realistic-human design brief (no exaggerated fantasy proportions,
  unlike the other races this session).

## Known issues before this is usable (same as every sheet this session)

1. **No real transparency** - RGB, checkerboard baked into pixels.
2. **Not a uniform grid**, no individual numbered labels (only row-level
   MALE HUMAN / FEMALE HUMAN headers).
3. **Single front-facing pose only** - a genuine "replace the existing
   folder" goal for this specific race WILL eventually need directional
   walk frames (down/left/right, matching assets/npcs/human/'s current
   real structure), not just a portrait pose, since humans are the
   primary player-adjacent NPC race and walk around the overworld far
   more than a boss/vendor-only race would. Bigger integration lift than
   most other sheets in this batch - flagging explicitly rather than
   letting it get treated the same as a portrait-only race.

## Next steps when picked back up

Same as every other npcs_staging folder - crop, add real alpha. Given
the note above, human integration should be planned as its own
dedicated pass (deciding replace-vs-supplement for assets/npcs/human/,
and whether directional frames are needed) rather than batched
identically with the portrait-only races.
