# Plaguelands secret places: art backlog (sheets 9 to 11)

Kyle, 16 Nov 2026: "do you need ice tiles? I can add these to the backlog for the next art pass". The Plaguelands'
two skull zones and their frontier are built from tiles already on disk (Aspen's snow and pond ice, the Underdark's
ice walls, the Plaguelands' own fen and grass, Ashenvale's elven ruins) and placeholder creatures, so none of this
blocks anything. These sheets replace the stand-ins. They say what to paint, not where it is.

The header rules are sheet 1's (`docs/plaguelands_art_prompts.md`): ONE image, 2048x2048, flat pure #FF00FF magenta
background for creatures and props, each sprite alone in its cell with a wide margin, no ground patch, no shadow, no
text or grid lines, never magenta on the subject, painterly semi-realistic WoW Classic style, soft dark outline,
light from the top-left. Ground tiles are square, seamless and straight top-down, with no objects.

---

## SHEET 9: 36 ground tiles (seamless squares)

**Done, 17 Nov 2026.** Sliced by `tools/slice_tile_sheet.py cold_lands` into `assets/tiles/cold_lands/ground` (cl_
names, kept general so Winterspring can use the same snow and ice). The tiles sat apart on magenta, so the slicer
finds each one's edges, and they are made seamless by overlap (the tile's own continuation is cross-faded along a
ragged line), because an edge cross-fade left straight seams in the reeds and the meadow. The three hidden maps now
paint with them in place of their stand-ins. Four are one-off pieces rather than repeating ground: the ice hole edge,
the causeway, the reflecting pool and the gold-to-grey transition.

> ONE image, 2048x2048, 6 x 6 grid = 36 SQUARE SEAMLESS textures, straight top-down, no objects.
>
> Row 1 - TUNDRA: wind-packed snow with faint ridges; thin snow over dry steppe grass; old blue-white glacier ice
> seen from above; frozen river ice with white cracks and trapped bubbles; frost-rimed grey stone; trampled snow
> with hoofprints and dung (not gross).
> Row 2 - TUNDRA AND ICE WALL: dark open water under ice at the edge of a hole; scree under snow; a glacier wall face
> in deep blue and white, seamless left-right; grey moraine gravel; snow-dusted lichen rock; red ochre earth
> trodden into snow.
> Row 3 - FEN: grey sphagnum moss; green floating moss over black water; black peat with standing water; reed beds
> seen from above; pale sunken causeway stones half under the peat; cold shallow fen water, brown-black.
> Row 4 - FEN AND BARROWS: deep black mere water with a faint blue sheen; old bronze-green Amani paving, broken; barrow
> turf, short and dark; drowned grass under shallow water; a mist-pale mud bank; wet grey sand.
> Row 5 - ELVEN WAYSTATION: white and gold elven paving in a leaf pattern; a golden meadow in late afternoon light;
> silver-leaved grass; red-gold fallen leaves on grass; a mossy elven road with gold inlay; a still reflecting pool.
> Row 6 - THE BREACH: golden grass dying to grey at one edge; Scourge-cracked earth with violet light in the cracks;
> elven paving split and blackened; plague-grey grass; bone-white soil; burned gold leaves.

## SHEET 10: 36 creatures

**Done, 17 Nov 2026.** Sliced into `assets/creatures/ps_*.png` (`creature_sprites.SHEETS["plaguelands_secrets"]`).
The 25 creatures of the three hidden maps wear it (set in `tools/build_hidden_content.py`, so a rebuild keeps it),
and three of their people have their own figures: the Finnish scientist, the elven ranger and the elven
quartermaster. Eight are parked for when more people stand there: the stone age woman, the palaeontologist, the
frozen hunter, the fisherwoman, the bog eel, the reed heron, the wardstone and the dead ranger. The palaeontologist
was drawn as a man, and the one in the game is a woman, so she keeps her figure. The magenta rim was cleaned with
`purge_magenta.py`'s new `rim_fix`, except on the four that really are violet light.

> Creatures, 6 x 6, magenta key, the shared rules. Bosses are large and distinct from each other.
>
> Row 1 - ICE AGE BEASTS: a woolly mammoth with long curved tusks and red-brown shaggy hair; a woolly rhinoceros with
> two horns, low and heavy; a dire wolf, bigger and heavier-jawed than a grey wolf, pale winter coat; a giant elk
> with enormous palmate antlers; a cave bear, huge and humped, dark brown; a steppe bison with a tall shaggy hump.
> Row 2 - ICE AGE BOSSES AND PEOPLE: an ancient woolly mammoth matriarch, enormous, scarred, frost in her hair (boss);
> a cave lion, maneless and pale with a faint striped coat and a scar across its face (boss); a walking glacier, a
> towering mass of blue ice with boulders and old bones frozen inside it (boss); a stone age woman in furs with a
> flint knife and red ochre handprints on her furs, calm and watchful; a palaeontologist in a modern parka with a
> notebook (a person from our world); a frozen hunter in furs, half in ice.
> Row 3 - FEN: a will-o'-the-wisp, a cold blue light with a faint face; a drowned man in old peasant clothes, dripping
> weed; a great grey fen owl; a bog crocodile-like lurker, peat-brown, low; an Amani troll barrow-shade, ghostly
> green with bronze jewellery; a bog hulk of peat, reeds and roots.
> Row 4 - FEN BOSSES AND PEOPLE: a dead lamplighter in a long coat holding a lantern with a cold blue flame (boss); an
> ancient bog hag made of moss and reeds, the size of a hill bank (boss); a Finnish scientist in waders and a
> beanie (a person from our world); an old Forsaken fisherwoman with a reed basket; a bog eel; a reed heron.
> Row 5 - THE WAYSTATION: an Eversong lynx, golden with tufted ears; a mana wyrm, a small blue arcane serpent; an
> arcane remnant, a figure of violet light; a ghostly high elf sentinel in gold armour; a living high elf ranger
> woman with a longbow; an elven quartermaster, prim and tidy.
> Row 6 - THE WAYSTATION BOSSES AND THE BREACH: an elven magister ghost in red and gold robes, light pouring from his
> eyes (boss); a hulking abomination with a hook and chain, gnawing (boss); a gaunt ghoul; a Scourge necromancer in
> black; a cracked wardstone, golden, on its own; a dead elven ranger, preserved and peaceful.

## SHEET 11: 36 props

**Done, 17 Nov 2026.** 37 came back (a crystal wardstone beside the golden one), sliced into
`assets/tiles/plaguelands_secrets/props/ps_*.png` with `slice_prop_sheet.py --dilate 6`, which keeps the flint flakes
together as one prop. 44 props in the three hidden maps swapped to these at the same spots, so where you can walk
is unchanged. Not placed yet: the ivory figurine and the hole in the ice.

> Props, 6 x 6, magenta key, the isometric three-quarter view with the front toward the lower-right.
>
> Row 1 - ICE AGE CAMP: a dome hut built of mammoth bones and hides; a drying rack with hides; a stone hearth with
> embers; a mammoth skull half in snow; a pile of flint flakes and tools; a carved ivory figurine on a rock.
> Row 2 - THE PAINTED CAVE AND THE ICE: a cave mouth in a rock face with red and black animal paintings on the walls
> inside; a standing slab with a painted lion; a large ice boulder with a shape frozen inside; glacier seracs (tall
> jagged ice blocks); a frozen waterfall; a dark open hole in lake ice.
> Row 3 - THE FEN: a lantern post leaning in the bog with a cold blue flame; a sunken Amani stone head; a bog oak
> stump, black and twisted; a reed bed clump; a barrow mound with a stone door; a fallen lantern in shallow water.
> Row 4 - THE WAYSTATION: an elven wardstone, a tall golden obelisk with runes; a broken wardstone; an elven arch
> with gold leaf; a white stone bench under a golden tree; a golden-leaved elven tree; an elven lamp post.
> Row 5 - THE WAYSTATION AND THE BREACH: a reflecting pool rim; an elven ranger lodge with a balcony; a quartermaster's
> stall of elven goods; a Scourge bone barricade chewing into elven paving; a Scourge obelisk; a breach in a
> golden shimmering wall, black at the edges.
> Row 6 - EXTRA: three snowy krummholz pines; a boulder with snow; a frozen dead tree; a moss-covered troll idol; a
> golden sapling; a heap of bones half under snow.
