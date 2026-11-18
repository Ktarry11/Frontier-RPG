# Moonglade: what was built (18 Nov 2026)

The vision is `docs/moonglade_brief.md` and the art `docs/moonglade_art_prompts.md`. This is what's in the game.

Kyle, 18 Nov 2026: "moonglade can be quite a decent size but is still a town and hub. there will be an inn and a flight
path. no monsters", "Get that mystical druid look for moonglade, we should have the lush tiles, trees, and brillian
beautiful water!", and the two factions: "the cenarion circle is still there and the Wakened. They are in good
standing with each other. The wakened is transplant led while cenarion circle is true to lore. Moonglade looks
similar but 'something else is waking up'".

## The map

| | |
|---|---|
| Builder | `tools/handbuilt_moonglade.py` (200x170, the Ashenvale town kit), baked by `tools/bake_ashenvale_towns.py moonglade` |
| Levels | 55-60, a town: no monsters, no gathering nodes |
| Way in | The Timbermaw Tunnel's Moonglade passage (12,34), dug out on Moonglade's side, to the valley's south-east pass (156,169) |
| Services | The inn (Innkeeper Talowyn Nightbreeze), the roost (Bunthen Plainswind, the valley's one flight path), a class trainer for every class (Loganaar), herbalism with alchemy, skinning with leatherworking, cooking with fishing on the pier, a provisioner, both quartermasters |

**Lake Elune'ara** fills the middle: clear pebbled shallows going down to luminous blue, lilies and reeds round the
edges, the Falls of Elune'ara coming down onto the north shore. **The island** sits in the middle, a ring of
moonstones round a still pool that reflects nothing, with a broken stair going down into it: in view from every shore,
out of reach (no bridge, no boat). **Nighthaven** is the east shore: the great moonwell in its square, the roost and the
tauren quarter north of it, the Cenarion Circle's hall and the night elf houses south, the inn by the way in, the pier.
**The Shrine of Remulos** is the north-west point, with **the Dreaming Arch** behind it in the north woods. **The
Wakened** have the west shore: the longhouse, the cabins, the infirmary and its dream cots, the gardens and the wall of
last memories. **The Stormrage Barrow Dens'** door is in the south-west hills behind a living thorn ward. The pass to
Winterspring in the north-east is shut by rockfall.

**The art** is Kyle's four Moonglade sheets: the ground and water (sliced to `assets/tiles/moonglade/ground`, rows
measured on the seams), the nature props (`assets/tiles/moonglade/props`), the town buildings and the nine landmarks
(`assets/buildings/mg_*`). The ground paints from `MOONGLADE_SHEET` in `tools/bake_ashenvale.py`; the pier is the sheet's
silver boardwalk.

**The three dungeon doors** are on the map from the start and lead nowhere yet (`DOORS` in the map module): the Barrow
Dens (the corrupted druids), the Dreaming Arch (the Emerald Dream) and the island (under the lake).

## The people (`tools/build_moonglade.py`)

**The Cenarion Circle, Nighthaven:** Rabine Saturna (leader), Archdruid Hamuul Runetotem and Elder Mahala Dawnhorn
with the tauren who came up from Thunder Bluff, Bunthen Plainswind, Moonwell Keeper Aedris Silverbrook, Quartermaster
Ellandris Dawnleaf, Innkeeper Talowyn Nightbreeze, Trainer Loganaar, Herbwarden Mylla Starbloom, Hidewright Tannar
Proudhoof, Ilyssa Moonwater on the pier, Provisioner Kesha Windmane. **Keeper Remulos** at his shrine, **Dreamwatcher
Lethiel** at the arch, Wardens Taerenas and Torin Grayhoof on the Barrow Dens.

**The Wakened, west shore:** Dr. Ingrid Sandvik (leader, a sleep researcher from Trondheim), Quartermaster Tomas
Ribeiro (Porto), Nurse Adaeze Okafor (Lagos), Hamish MacLeod (the Isle of Lewis), Mei-Lin Zhou (Chengdu), Danny
Kowalczyk (Buffalo).

**Recruits:** Valentina Soto on the north shore and Faris Al-Tamimi in the reed beds below the Wakened
(`tools/build_sheet5_recruits.py`). Winterspring's two still wait for their map.

## The factions

Both TBC-style, like every faction: friendly a supply of their own (the Circle's Moonwell Draught, the Wakened's Waking
Tea), honored a neck piece and a pattern, revered six ilvl 67 blues and a pattern, exalted three ilvl 73 epics and two
recipes. A direction, not a cage: the Circle leans nature, healers and ferals (leatherworking and woodworking
recipes), the Wakened practical gear (tailoring and blacksmithing), and both serve tanks, healers, casters and
fighters. Reputation comes from Moonglade's quests by giver; there's nothing to kill in the valley, so **past Friendly
is the dungeons' job** when they're built.

## The quests (`tools/moonglade_quests.py`, `tools/build_moonglade_quests.py`)

30 quests, 19 for the Circle and 11 for the Wakened, nobody giving more than four. The first is given in the Timbermaw
Tunnel by Windtalker Selva Brightpelt and brings you up the passage. Then:
- **The Wakened:** how they woke, the wall of last memories, Danny who wants to fall asleep and wake up in Buffalo,
  the ones who don't wake, the night watch, what the sleepers say in eleven languages.
- **The Circle's watch** out over the sick lands: Felwood's satyrs and Zar'gothrax behind Jaedenar's Black Gate, the
  rot under Timbermaw Hold (Xavras), the Bloodvenom, Deadwind's stags that don't dream, the satyr count in Azshara.
- **The tauren** who carried their totems out of Thunder Bluff, raising one, and the list of survivors for Elder
  Longtread at Camp Taurajo.
- **Something waking:** warm stones at the arch, the moonwell running over when the island's pool lights, a voice in
  the Barrow Dens answering the sleepers, the fish turning toward the island, nineteen strangers dreaming the same
  door, and Remulos walking into the Dream to look. It resolves nothing; the three dungeons will.

Also: the Timbermaw Tunnel's Moonglade passage is open now (its rockfall pushed aside), and Windtalker Selva's lines and
the Timbermaw's lore say so.
