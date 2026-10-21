# Dungeon layout inspiration pool (Kyle, 2026-10-21)

Three blueprint sheets of layout ideas live in the repo at `docs/dungeon_layout_inspiration/` (`lexicon_expanded_types.jpg`, `lexicon_silhouettes.jpg`, `lexicon_floor_plans.jpg`). **Inspiration only**: do NOT copy names, do NOT map them 1:1 onto a dungeon, do NOT use them all. Mix, remix, combine, and scale to the job: a cave, a full dungeon, or a 2-boss raid. Multi-floor (layered) dungeons come later; until then a "floor" = one standalone map.

Use together with the LAYOUT VARIETY RULE in `claude/zone_perfection_playbook.md` section 4: before authoring a cave, pick a topology from here that no sibling cave in that cluster already uses.

## Shape families on the sheets
- **Blob clusters (organic):** hive / hivemind chamber, fungal-grotto hive, central core with budding chambers and a spiral ramp. Many round lobes joined by short necks. Good for spiders, murlocs, insects, fungal caves.
- **Spaghetti tunnels:** one long switchbacking passage with a barrier and a pit; combat is a corridor crawl, not rooms.
- **Open cavern with rock islands:** one big cave you walk around pillars/pools in (crystal grotto, glowing lichen, underground rill).
- **Chasm / fissure:** a branching crack with a single bridge crossing and vents/magma pools in the arms.
- **Sinuous creature-shaped:** a spine track with a head cauldron and tail observatory; the map IS a serpent/skeleton. Also the skull crypt (eye pool, jaw ramp) = silhouette dungeon.
- **Linear chain of octagons:** tower floors, one room after another with a spiral stair; horned top room as a boss arena. Single path, big set-piece rooms.
- **Hub and radial:** octagon hub with 4-8 wings (star-shaped), forge hub of arcs around a central reservoir, sunken-city hub with long diagonal avenues to wings.
- **Ring of chambers:** crescent loop, octagon hub inside a ring corridor with side rooms. Naturally gives a loop route and optional spurs.
- **Cruciform temple / crypt:** symmetric chapel, altar, reliquary; formal, rooms off a nave.
- **Labyrinth catacombs:** maze with a pilgrim's path and crypt chambers on the edge, one hidden sanctum.
- **Prison blocks:** cell rows around a central yard, guard towers, admin wing, infirmary; strictly rectilinear.
- **Stepped cliff / monastery:** diagonal cliff walk, overlook, dormitories; a staircase-shaped footprint.
- **Irregular orthogonal complex:** rooms of different sizes bolted together at awkward angles, deepening alcoves.

## Implementation notes for our toolkit
- Already available in `tools/handbuilt_echo_caves.py`: `cavern`, `tube` (Catmull-Rom), `disc`, `wall_annulus`, plus `Builder.rect/lobes/corridor`. That covers blob clusters, tunnels, rotunda/ring, C-warrens and gorges.
- Worth adding when a dungeon needs them: a regular-polygon helper (octagon rooms with cut corners), a spiral-stair/ramp helper (a walkable curved strip), a mirrored-wings helper for radial hubs, and a silhouette mask (draw a skull/serpent as a signed-distance field, then carve rooms inside it). Chasm bridges = a 2-wide walkable strip across a non-walkable gap.
- Props must still be guarded and logical (playbook section 5). Rooms read through their dressing: the shape gives the silhouette, the 6-15 hand-placed props give the identity.
- Keep the flood-fill QA (`L.finish`) on every shape; chambers with one entrance are fine, unreachable floor is not.
