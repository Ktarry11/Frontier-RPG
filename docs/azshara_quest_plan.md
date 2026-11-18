# Azshara: the quest plan (about 90 quests)

Kyle, 18 Nov 2026: "Braided, both ends". The Landing's quests run the orc and blood elf salvage feud and end in the
Drowned Palace; the Hold's run the rot and end in the Rotroot Deeps; the two arcs meet at the Ruins of Eldarath. About
70% of the quests are given in Talrendis Landing and Timbermaw Hold (docs/azshara_brief.md). No giver gives more than
five. Reputation goes by who gives the quest: the Conclave's magisters pay the Sunreach Conclave, the orcs pay
Orgrimmar, the Hold pays Timbermaw Hold.

Rules carried over from Stonetalon and Felwood: every kill target spawns where the quest says, every fetch item drops,
every explore point is walkable, dungeon and cave quests are given in a hub, a chain is a chain, and between them the
rewards give every spec something it wants. Earth comes up about a quarter of the time, from the transplants.

## The people

**Talrendis Landing** (the six who are there now, plus five new):
- Overseer Durgash Stonejaw (orc, Orgrimmar's man on the dig), Spellbreaker Ilanthe (blood elf, the gate),
  Grunt Mazkar (orc, the gate), Innkeeper Mohammed Saleh (transplant, Aqaba), Forgemaster Gharza Ironbrow (orc),
  Provisioner Dana Whitfield (transplant, a North Sea rig cook).
- New: **Magister Caelin Brightspire** (blood elf, the Conclave's archivist), **Magistrix Ysolde Emberwind** (blood
  elf, the Conclave's dig magister), **Salvage Boss Rukka Ironhide** (orc, runs the orc crews), **Dr. Amara Okafor**
  (transplant, a field archaeologist from Lagos who signed on with both sides), **Farseer Thrag Windcaller** (orc, the
  dig's shaman, who doesn't like what the leylines are doing).
- Grand Magister Velanthe Sunreach and Quartermaster Sylvaen Dawnward give and take nothing (Kyle: they move to the
  elves' island later).

**Timbermaw Hold** (all already there): Elder Haldor Mossmane, Totemkeeper Ungar Ashbrow, Springwarden Lessa
Brightwater, Deepwarden Grothar and Deepwarden Ulma (the deep gate), Carver Bennik Ashpaw, Ingrid Solberg (the
transplant volunteer, from Tromso), Gatewarden Hrolm, Tunnelwarden Burrfoot, Envoy Grashak Stonetusk (orc),
Herbwarden Fenna Mossbrow.

**The field** (new): **Captain Zarga Bloodfang** at Stormwatch (East), the Horde's lookout over the drowned coast, and
**Ranger Thessaly Dawnsong** (blood elf) with her, the Conclave's eyes on the Court. **Grunt Okkar** at Valormok.

## The arcs

**THE SALVAGE FEUD (the Landing, about 38).** Both sides want what's under Eldarath, and neither trusts the other with
it. Early quests are honest work: clearing satyrs off the dig road, shades off the trenches, crabs off the beach
camp. Then it turns: an orc crew finds a relic and it goes missing; the Conclave says the orcs sold it, the orcs say
the elves hid it. Dr. Okafor works both sides and finds that the naga took it, and that the naga are digging too,
from the sea side. The relics are keys to Azshara's palace. It ends with the Landing sending a joint team into the
Drowned Palace (the dungeon quests), and the Grand Magister and the Overseer agreeing on one thing: neither side gets
what's in the vault.

**THE ROT (the Hold, about 34).** Whatever turned the Deadwood came up from under the Hold. Early quests are the
Hold's life: honey, the spring, the totems, the wolves on the Ursolan pass, Haldarr's satyrs. Then the spring starts
going green, the deep wardens hear things under the gate, and Ingrid Solberg (a soil scientist at home) traces the rot
in the roots to the satyrs of Legash and Haldarr, who are feeding it. The Elder opens the deep gate (the Rotroot Deeps
quests). Kills of the rotted pay toward Revered.

**THEY MEET AT ELDARATH (about 8).** The Hold's furbolgs remember the Highborne: the satyrs were Highborne once, and
the rot is Highborne magic gone bad. The orcs' dig at Eldarath is right on top of the root of it. A chain that both
hubs give, ending with the Elder and the Overseer at the dig, and the Conclave admitting what its ancestors did.

**OUT (about 10).** Chains to Orgrimmar (the Overseer reports to the Valley of Honor), Ashenvale (the Sentinels'
Shadowsong dead), Felwood (the Timbermaw Tunnel's people, and Felpaw's Deadwood), Silvermoon by letter (the Conclave
writes home), and the Eastern Kingdoms (a relic to the Undercity's apothecaries, who want it for the wrong reasons).

## The dungeons and caves (given in a hub, never inside)

- **Haldarr Den:** Haldarr the Hornlord (Totemkeeper Ungar), the Bound Magister (Magister Brightspire: the Conclave
  wants him freed, not killed, and freeing him is killing him).
- **Hetaera's Grotto:** Tide-Priestess Sel'thira (Dr. Okafor: the naga's dig), Hetaera (Salvage Boss Rukka).
- **The Rotroot Deeps:** five, from the deep wardens and the Elder, the last one Xavras (the Elder).
- **The Drowned Palace:** six, from the Overseer, the Grand Magister's archivist and Dr. Okafor; the Echo of the Queen
  last, from both hubs together.

## The Sunreach Conclave (faction)

New faction: the blood elf magisters reclaiming what their ancestors lost. Quests from Brightspire, Emberwind and the
Stormwatch ranger pay it; the Drowned Palace's bosses pay it (75 a boss), and so do its naga and ghosts in the open
world, to Honored. Its quartermaster's shelf is TBC-style: friendly supplies, honored patterns, revered blues (item
level 67), exalted epics and two epic recipes, the way Timbermaw Hold's is.

## Build order

1. The Conclave faction and its shelf; the new people placed in the Landing, Stormwatch and Valormok.
2. The Landing's quests (`tools/azshara_quests.py`, written by `tools/build_azshara_quests.py`, which holds them to
   the rules above).
3. The Hold's quests.
4. Eldarath, the dungeons and caves, and the chains out.
5. The transplant recruit, and the hidden content.
