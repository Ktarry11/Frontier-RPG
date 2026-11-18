# Moonglade: the vision (sketched with Kyle, 18 Nov 2026)

Kyle, 18 Nov 2026: "We have the stuff for moonglade as it will likely be more of a massive town. It won't have enemies
yet unless we go into the barrows but they will be for a later date. We do need the giant water in the middle that can
have something later too. So how about we design it and keep it open for later with a potential of 3 possible
dungeons. One will be a corrupted druid one, the second will be emerald dream style, third will be under lake
Elune'ara." And: "Get that mystical druid look for moonglade, we should have the lush tiles, trees, and brillian
beautiful water!" Then: "moonglade can be quite a decent size but is still a town and hub. there will be an inn and
a flight path. no monsters"

His picks, the same day:
- **New art first.** Moonglade gets its own sheets (`docs/moonglade_art_prompts.md`) and is built once they're in.
- **Two factions in good standing:** the **Cenarion Circle**, true to lore, and **the Wakened**, transplant-led.
- **"Moonglade looks similar but something else is waking up."**
- **The way under the lake is an island in the middle**, there from the start and out of reach until its dungeon exists.
- **The Cenarion Circle is a reputation faction** with its own quartermaster. The Wakened are the second.

**Status:** built, 18 Nov 2026, from Kyle's four sheets. What's in the game is `docs/moonglade_build_log.md`. Two
changes from the design: the Wakened's recipes are tailoring and blacksmithing (cooking makes no gear), and the
Circle's are leatherworking and woodworking.

---

## What Moonglade is

The end of the 55-60 road in Kalimdor, and the one place up there that's beautiful. A deep valley ringed by mountains,
with Lake Elune'ara filling the middle, moonlit all the time, and Nighthaven round its shore. It's a **town-sized map**
(the town rule: a town is always its own map, and this town is the whole valley): no enemies, no gathering nodes, an inn
and one flight path. It should feel like somewhere you go to breathe after Felwood, Azshara's rot and Deadwind.

**It looks the way Moonglade always did, nearly.** The Integration came and went, and the glade is still green, still
quiet, the lake still silver. The difference is small and everybody who lives there can feel it. The druids who sleep
in the Barrow Dens talk in their sleep now. The stones of an arch in the north woods are warm at night. On a still night
the island in the lake hums. **Something else is waking up**, and nobody agrees on what.

That's the line that runs under the whole zone, and it's left open on purpose: each of the three dungeons, when it's
built, answers part of it.

## The two factions

**The Cenarion Circle** (true to lore). Night elf and tauren druids, together the way they always were in Nighthaven.
More tauren than before: when Thunder Bluff fell, the tauren druids who survived came here, so the tauren half of
Nighthaven is grieving and a little crowded. **Leader: Rabine Saturna**, who keeps Nighthaven. **Keeper Remulos** stands
at his shrine on the north-west shore. The Circle cares about one thing: the land getting sick. Felwood, Azshara's rot,
the Plaguelands, and now the wound in Deadwind all worry them, which is why their quests send you back out.

**The Wakened** (transplant-led). When the Integration struck, the Dream bled into the glade for a moment, and the
transplants who came through anywhere near it arrived asleep. The druids found them lying in the grass round the lake,
dreaming, and woke them one at a time. Most stayed. They built a settlement on the west shore, they work with the
Circle, and they're the closest thing in Azeroth to people who understand the Dream from the outside, because they've
been in it. **Leader: Dr. Ingrid Sandvik**, a sleep researcher from Trondheim who spent twenty years studying what
people's brains do at night and then woke up in one. Not everyone woke: the ones who didn't sleep on in the Barrow Dens
beside the druids, and the Wakened visit them.

They're in good standing with each other. The tension is gentle and human: the Circle sees the Dream as sacred, the
Wakened see it as something that happened to them and want to understand it.

Both are reputation factions, TBC-style (Kyle's canon): friendly and honored give supplies and recipes, revered six
blues (ilvl 67), exalted three epics (ilvl 73) and recipes. Direction without pigeonholing:
- **The Cenarion Circle:** nature and restoration, but for everyone: druid-leaning leather and mail, healers' and
  ferals' pieces, a nature-resistance set later for the dungeons. Recipes: leatherworking and alchemy.
- **The Wakened:** practical transplant craft: things made by people who had to learn everything here. Mixed armour,
  a couple of weapons, the dreamers' pieces (spirit and stamina). Recipes: tailoring and cooking.

Rep sources: Moonglade's quests (split between the two), plus the Circle's quests out in the sick lands; later, the
three dungeons (each leans to one faction: the Barrow Dens and the lake the Circle, the Dream the Wakened).

## The map (one map, about 200 x 170)

Orientation follows the overworld: Moonglade sits north of Felwood with Winterspring to the east.

```
                 N
     the north woods: THE DREAMING ARCH (seed 2)
   SHRINE OF REMULOS                       the Winterspring pass (shut: snow and rockfall)
   (the great tree, NW shore)                                         \
                    \                                                  \
   THE WAKENED'S         ~~~~~~~~ LAKE ELUNE'ARA ~~~~~~~~        NIGHTHAVEN
   SETTLEMENT           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~       (east shore: the town)
   (west shore)        ~~~~~~~~~~~~ (the island) ~~~~~~~~~~~      inn, roost, Circle hall,
                        ~~~~~~~~~~~~~~ seed 3 ~~~~~~~~~~~~       tauren lodges, pier
                          ~~~~~~~~~~~~~~~~~~~~~~~~~~~
   STORMRAGE BARROW DENS                                  the way in from the Timbermaw
   (south-west hills, seed 1)                             Tunnel (south-east pass)
                 S
```

- **Lake Elune'ara** fills the middle, about half the map's width. The water is the show: clear shallows over pale stone
  and lilies at the edges, deepening to a luminous silver-blue, moonlight on it everywhere. A wooden pier off
  Nighthaven, reed beds and lily pads round the west shore, stepping stones in the shallows by the Shrine.
- **The island** sits in the middle of the lake: a ring of moonstones round a still pool that doesn't reflect the sky,
  and a broken stair going down into it. Visible from every shore, out of reach for now (no bridge, no boat). This is
  where the third dungeon starts.
- **Nighthaven** (east shore), the town proper and the biggest piece: night elf houses of curved living wood beside
  tauren lodges of hide and carved timber; the inn; the Cenarion Circle's hall; the moonwell; the flight roost
  (hippogryphs and wind riders on one roost, the zone's one flight path); the trainers; the tauren lodges
  (Thunder Bluff's survivors); the pier.
- **The Shrine of Remulos** (north-west shore): a great tree on a point of land, Remulos beneath it, the druids'
  sanctum. Moonwells and old standing stones.
- **The Dreaming Arch** (north woods, behind the shrine): an arch of pale stone carved with sleeping faces, in a ring of
  flowers that bloom only at night. Its stones are warm. This is the door to the Emerald Dream dungeon; for now the arch
  frames nothing.
- **The Wakened's settlement** (west shore): built by people who'd never built anything before, and you can tell. Timber
  longhouses, gardens, a wash house, the infirmary where they keep the ones who wake badly, a meeting house, a long
  wall where everyone has carved the last thing they remember from Earth.
- **The Stormrage Barrow Dens** (south-west hills): the hillside doors where the druids sleep in the Dream, as in lore,
  and where the Wakened who never woke sleep beside them. The doors are shut behind a living thorn ward with Circle
  wardens on it. This is the corrupted-druid dungeon's way in; for now nobody goes in.
- **The way in** is the south-east pass, from the Timbermaw Tunnel's Moonglade passage (its rockfall, `LATER_DOORS` in
  `tools/handbuilt_timbermaw_tunnel.py`, becomes the door). **The Winterspring pass** in the north-east stays shut
  (snow and rockfall) until Winterspring exists.

## The three dungeons (seeds only)

Nothing is built for these but their doors. Each is a different answer to "what's waking up". All are probably level 60
content (pure 60 materials rules apply when they're built).

1. **The Barrow Dens: the corrupted druids.** The sleepers aren't only dreaming any more. Something in the Dream has
   found them, the druids and the Wakened who never woke alike, and is dreaming through them. A descent through the
   barrow halls, the sleepers' cells turning from moss and moonlight to thorn and rot the deeper you go.
2. **The Dreaming Arch: the Emerald Dream.** The arch opens onto the Dream itself: Moonglade as it would be with no one
   in it, green and gold and soft-edged, the lake hanging in the sky, the paths moving. Dream logic, not a cave.
3. **Under Lake Elune'ara: the drowned moon.** Down the island's stair, under the lake. The night elves built something
   down there before the Sundering and flooded it on purpose. It's been quiet for ten thousand years.

**What's waking** is decided when the first of them is built. It can be one thing seen from three sides or three things
waking at once.

## The people (a first pass)

**The Cenarion Circle (Nighthaven):** Rabine Saturna (leader), Keeper Remulos (at his shrine), a tauren archdruid who
led the survivors out of Mulgore, Bunthen Plainswind (the wind riders' keeper: he used to fly to Thunder Bluff, and he
still flies there in his sleep), the Circle's quartermaster, the innkeeper, the class trainer, trade pairs (herbalism
with alchemy, leatherworking with skinning), a cook and a fishing master on the pier, wardens on the Barrow Dens' ward.

**The Wakened (west shore):** Dr. Ingrid Sandvik (leader), their quartermaster, the infirmary's keeper, the carver who
started the wall of last memories, the gardener, someone who never stopped trying to go back to sleep.

**Recruits:** Valentina Soto (Atacama, Starcaller Warden) and Faris Al-Tamimi (Basra, Restoration Shaman), from sheet 5,
both level 58. Valentina grew up under the clearest night sky on Earth and works the lakeshore at night; Faris grew up
beside the marshes of southern Iraq and keeps the reed beds. Each knows the Wakened and the Circle, not the other.

## Quests (outline, about 30)

No enemies in the valley, so the quests are the town's stories and the Circle sending you back out:
1. **Arrival:** through the tunnel and into the glade; the Circle and the Wakened, and how the transplants woke.
2. **The Wakened's stories:** the wall of last memories, the ones who woke strange, the ones who didn't.
3. **The Circle's watch:** quests sent out to the sick lands (Felwood, Azshara's rot, the Plaguelands, Deadwind's wound
   and the Exclusion Zone), ending back here. Moonglade as the hub that ties the 55-60 zones together.
4. **The tauren after Thunder Bluff:** the survivors, what they carried out, and what they won't talk about yet.
5. **Something waking:** the sleepers talking, the warm arch, the island humming. Explore and listen quests at the three
   doors that build the mystery and resolve nothing. No world changes (Kyle, 18 Nov: "i dont want change with quests").

Earth references run heavy, the Wakened are all transplants. Voice rules as always: givers talk to you in their own
voice, contractions, no fragments, no dashes, the useful thing first.

## Open questions for later

- What's waking (decided with the first dungeon).
- Fishing pools in the lake (the town rule bans gathering nodes in towns; fishing pools aren't nodes, so probably yes).
- Whether Winterspring's pass opens before or after the dungeons.
