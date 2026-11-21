# Fourteen figures: art prompt (sheet FG1)

**Status (21 Nov 2026): delivered and in the game.** See `docs/art_status.md` for every sheet.

Kyle, 21 Nov 2026: "Let's also make a prompt for Corvo and Lysse and the sky npcs. All in one prompt. Add sprites up to
14 max in one sheet with anything you need as well." Fourteen figures that wear borrowed art today:

- **The sky (4):** the Exarch's two guards in the Ascendant Spire, Corvo and Lysse (stock commander and warden art), and
  the Crown's two allies, Ilaren Vey and Leandro Arrieta (stock Aetherian and human looks).
- **Dawnhaven (10):** its six cave bosses and four rares, all on other zones' creatures today.

The Mural Shard's Collection icon and the keepsake icons are icons, not figures, so they wait for an icon sheet.

**Attach as references:** `assets/creatures/_src/bastions/` (any two of the AB2 bosses, for the finish and the scale),
and `assets/npcs/aetherian/aetherian_m3/down.png` (an Aetherian).

Sliced by `tools/slice_building_sheet.py fg1 tools/building_sheets/figures_fg1.png` (blob-finding, row by row) to
`assets/creatures/` under the ids below. The creatures' sprites point at them (`tools/build_dawnhaven_content.py`,
`tools/build_citadel_dungeons_content.py`, `creature_sprites.py`). Ilaren and Leandro are people, so their figures went
to `assets/npcs/leaders/<npc id>/down.png` for each place they stand (the Crown, the Expanse and Aurelion).

---------------------------------------------------------------------
## SHEET FG1: FOURTEEN FIGURES (paste this whole block)

```
Generate ONE sprite sheet image, 2048x1024, a grid of 7 columns x 2 rows = 14 separate full-body character sprites. Flat pure #FF00FF magenta background everywhere. Each figure stands fully inside its own cell with a wide margin and does NOT touch or overlap neighbours or the image edge. Every figure faces the viewer (front view, "facing down" on a top-down game map), in an idle pose (menacing for the enemies, calm for the two allies), slight 3/4 top-down camera angle. Big beasts and spirits may fill more of their cell than the people do. No ground shadow, no text, no labels, no grid lines. Painterly semi-realistic, WoW Classic art style matching the attached references, lighting from the top-left, crisp clean edges, no pink or magenta anywhere in the figures. Glows are painted as opaque soft colour, never transparent.

Row 1:
1 ASCENDANT GUARD CORVO: a towering Aetherian man, one of an emperor's two personal guards, pale blue-grey skin, glowing white eyes, sharp crystal growths at his brow and shoulders, in ornate white-enamel and gold plate with a tall crested helm and a deep blue cloak, a long crystal-bladed halberd held upright. Grim, immovable.
2 ASCENDANT GUARD LYSSE: his partner, a tall Aetherian woman with warm bronze skin and glowing gold eyes, crystal growths along her cheekbones, in the same white-enamel and gold plate but lighter, a crested half-helm, twin curved crystal blades and a small round gold shield on her arm. Poised, watchful.
3 ILAREN VEY: a young Aetherian scholar and envoy, slender, pale blue-grey skin, softly glowing pale-blue eyes, small clear crystals at his temples, long silver hair tied back, in a long ivory and sky-blue scholar's coat with fine gold trim and a satchel of scrolls, a small lens of blue crystal on a chain. Earnest, gentle, a little dishevelled after a crash.
4 LEANDRO ARRIETA: a human man from our world who has lived three years among the sky-people, Argentine, about 40, weathered and lean, short dark hair with grey, a short beard, tanned skin, in a mix of a torn old paragliding harness and borrowed Aetherian ivory-and-blue clothes, a coil of rope and a folded scrap of bright paraglider fabric at his belt. Wry, tired, kind.
5 TIDECALLER SSZELITH: a naga priestess, a serpent's coiled teal-and-gold tail below a woman's body, four arms, fins on her head like a crest, coral and shell jewellery, holding a staff of twisted coral with a glowing sea-green pearl. Cold and proud.
6 SEA-WITCH ILTHESSA: a larger, older naga sorceress, deep blue-black scales, a mane of trailing seaweed-like hair, glowing pale eyes, wrapped in nets and old drowned sailcloth, a trident with frost-blue light crackling on its points. Menacing, the leader of a war camp.
7 WARDEN ISILIEN: the ghost of a high elf warden who sealed herself in a crypt a thousand years ago, translucent-looking pale blue spirit (painted opaque), a tall elven woman in faded white and gold elven armour with a tattered crimson cloak, long hair floating, holding a ring of old keys and a spectral blade. Sorrowful, still guarding.

Row 2:
8 ARCHIVIST LORETHAS: an undead high elf scholar, gaunt and grey-skinned with glowing violet eyes, in rotting crimson and gold archivist's robes covered in arcane writing, an open book floating beside him, his fingers trailing violet magic. Quiet, terrible, starving.
9 THE STARVED LIGHT: a hungry spirit of arcane light that lived under a dark well, a tall shifting shape of violet and gold light with a hollow dark centre like an open mouth, ragged streamers of light trailing off it like torn cloth. Beautiful and wrong.
10 OLD SALTSPINE: a huge armoured sea-crab boss, rust-red shell crusted with white salt crystals and spines, one enormous claw raised, barnacles and old naga spear-hafts stuck in its back.
11 OLD BARNACLE: a grumpy giant shore crab, grey-green shell so thick with barnacles and limpets it looks like a rock, one big claw and one small, a strand of kelp hanging off it. Different from the one before it: rounder, smaller and comic.
12 GOLDMANE: a great golden lynx, much bigger than any wild cat, a thick gold mane-like ruff around its neck, tufted black ears, pale green eyes, crouched to pounce. Beautiful and dangerous.
13 RUDDY, THE HOLLOW KING: a huge old red-brown bear standing up on its hind legs, shaggy autumn-red fur, a crown of fallen red leaves caught in its fur, scars across its muzzle, enormous claws. The king of a red autumn forest.
14 THE GRIEVING LADY: the ghost of a high elf noblewoman, pale blue spirit painted opaque, in a long faded crimson and gold gown, a veil over her face, hands clasped over a locket, mist pooling at the hem of her gown. Mournful, drifting.

Keep every figure fully separated on flat magenta. Before you finish, check that there are exactly 14 figures in two rows of seven.
```

Slice order: `ae_guard_corvo`, `ae_guard_lysse`, `npc_ilaren_vey`, `npc_leandro_arrieta`, `dh_tidecaller_sszelith`,
`dh_seawitch_ilthessa`, `dh_warden_isilien`; `dh_archivist_lorethas`, `dh_starved_light`, `dh_old_saltspine`,
`dh_old_barnacle`, `dh_goldmane`, `dh_hollow_king`, `dh_grieving_lady`.
