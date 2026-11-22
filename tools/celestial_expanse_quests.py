"""
The Celestial Expanse's quests (49-51): the council's skiff came down on the way to fetch you, and the road to Aurelion
runs upriver across the islands. Read by tools/build_celestial_expanse_quests.py, which holds them to every rule before
anything is written. The brief is docs/worldtree_brief.md; the map is tools/handbuilt_worldtree_celestial_expanse.py.

THE THREADS (Kyle, 20 Nov 2026: "The old sky ruins wake (Kharad-age machinery, sky-golems); Ascendancy patrols; sky
beasts"):
  The crash: the old Kharad wards woke when the seal cracked and fired on the first bright ship they saw, the council's
    skiff. Ilaren Vey and Leandro Arrieta were on it with you. The pilot wants the skiff's heart back, the herald wants
    the council's courtesy found and its word carried upriver, and Ilaren wants to know whose wards they were.
  The Kharad: Scholar Idris Marrowell of the House of Long Memory has been laughed at for saying the Kharad were here
    first. The core under the sword is the zone's piece of the sky's one mystery (docs/worldtree_brief.md): Kharad
    stone, Aetherian crystal and a Veyr-sung storm in one golem, three peoples' work in one thing. Their war-golems are standing up on the Golem Fields, and the forge that made them is warming. Ilaren takes
    up the forge once Idris has proved the rest.
  The Earthborn of Tethertown: thirty-one Earth people who woke on the islands and tied two rocks to a bigger one.
    Kaisa Lehtonen is still finding the last few; Gustavo Pires keeps the ropes; Annelies de Vries grows Earth seeds in
    sky soil. They pay nobody (transplants are factionless).
  Halcyon Rest: the Aetherian waystation, fuller of refugees than travellers. The keeper takes the herald's word, the
    skiffmaster keeps his skiffs flying dark, Teodric Ashlane lost his street when the Eighth Ring fell and hears the
    ring's bells in his sleep, and Dace Morrow put his lance down rather than fire on a parley.
  The whales: Dr. Ana Kealoha counted humpbacks off Maui and now counts the whales in the cloud.
  The Spillway: Aurelion's own water, falling through its broken aqueduct. The aqueduct-warden wants to know what's
    living in it.
  The vault: under the Golem Fields the Kharad kept the golems they never sent out, and the crews who built them lay
    down in the stone beside them. Leandro wants to see what's down there; the pilot wants the storm that powers the
    wards, the one that brought his skiff down, put out at the bottom of it.
  The bridge: the herald's seal and the bridgewarden's word. Aurelion's door opens for you, and the city is the next
    build: nothing here goes inside it.

THE RULES IT KEEPS: no map changes with quests; transplants are factionless; the Aetherians only ever say they don't know
what the change was. VOICE (Kyle): whole sentences the way a person says them, contractions, no dashes, no sentence of
one or two words, the useful thing first, every kill target named, no count beside an objective word.
"""
from tools.build_durotar_quests import kill, fetch  # noqa: F401
from tools.moonglade_quests import CYCLE

CE = "celestial_expanse"
GV = "golem_vault"         # the cave under the Golem Fields (tools/handbuilt_golem_vault.py)
SW = "storm_well"          # its second floor, down the Deep Stair (tools/handbuilt_storm_well.py)

# ---- Crashfall
ILAREN, LEANDRO, PILOT, HERALD, HASK = "ce_ilaren", "ce_leandro", "ce_pilot", "ce_herald", "ce_landing_hand"
# ---- Tethertown
KAISA, GUSTAVO, ANNELIES = "ce_tether_lead", "ce_tether_rigger", "ce_tether_farmer"
# ---- Halcyon Rest
ITHREN, DAVIN, TEODRIC, DACE = "ce_keeper", "ce_skiffmaster", "ce_refugee", "ce_deserter"
# ---- out on the islands
IDRIS, ANA, LORNE, CALDUS = "ce_golem_scholar", "ce_whale_watcher", "ce_spill_tender", "ce_bridgewarden"

#: the people who stand in Halcyon Rest, the Expanse's town (its own map since 22 Nov 2026, Kyle's town rule): the pair
#: and the herald came up the river from the wreck, Idris lodges there, and Tethertown is tied on below it
HUB_GIVERS = {ILAREN, LEANDRO, HERALD, IDRIS, KAISA, GUSTAVO, ANNELIES, ITHREN, DAVIN, TEODRIC, DACE}
#: the Aetherians pay the Aetherians; the Earthborn (Leandro, Kaisa, Gustavo, Annelies, Ana) pay nobody
SKY_GIVERS = {ILAREN, PILOT, HERALD, HASK, ITHREN, DAVIN, TEODRIC, DACE, IDRIS, LORNE, CALDUS}


def k(target, n, zone=CE):
    return kill(target, n, zone=zone)


def boss(target, zone=CE):
    return {"type": "kill_boss", "target": target, "count": 1, "zone": zone}


def explore(x, y, label, zone=CE, radius=4):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius, label=label)


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def gather(material, n, label):
    return dict(type="gather", target=material, count=n, label=label)


def carry(item_id, name, desc):
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=1)]}


#: creature -> [(item_id, name, description[, chance])], three in four unless a chance is given
FETCH_DROPS = {
    "Crashfall Scuttler": [("ce_q_skiff_crystal", "Piece of Skiff Crystal", "A splinter of the council skiff's "
                            "crystal, dark now, dragged off the wreck by a Crashfall Scuttler that liked the shine.")],
    "Cloudfleece Ram": [("ce_q_ram_shank", "Cloudfleece Shank", "A lean shank off a Cloudfleece Ram. The meat's pale and "
                         "smells faintly of rain.")],
    "Kharad Sentinel": [("ce_q_ward_core", "Sentinel Ward-Core", "A fist of grey stone from a Kharad Sentinel's chest, "
                         "cut with the same runes as the wards that brought the skiff down. It's warm.")],
    "Molten Crystal Elemental": [("ce_q_forge_glass", "Cooled Forge-Glass", "A lump of crystal that was molten inside a "
                                  "Molten Crystal Elemental and set hard when it fell. It's cloudy and doesn't shine.")],
    "Skymane Lion": [("ce_q_lion_sinew", "Skymane Sinew", "A long cord of sinew from a Skymane Lion. It's stronger than "
                      "any rope Tethertown has.")],
    "Ascendancy Scout Construct": [("ce_q_patrol_log", "Scout Patrol Log", "A crystal plate from an Ascendancy Scout "
                                    "Construct, etched with the routes it flew and the times it flew them.")],
}
STARTER_DROPS = {}
STARTER_IDS = {}

_cyc = [41]


def R():
    """The next reward triple off the shared cycle (tools/moonglade_quests.CYCLE)."""
    r = CYCLE[_cyc[0] % len(CYCLE)]
    _cyc[0] += 1
    return list(r)


def Q(qid, title, giver, lo, hi, prefix, desc, objs, accept, done, rewards=None, nxt=None, zone=CE, **engine):
    q = dict(quest_id=qid, title=title, giver_npc_id=giver, zone=zone, level_min=lo, level_max=hi,
             description=desc, objectives=objs, accept_text=accept, turn_in_text=done, next_quest_id=nxt,
             _prefix=prefix, _rewards=rewards or R())
    q.update({kk: vv for kk, vv in engine.items() if vv})
    return q


# ------------------------------------------------------------------------------ places (walkable, checked)
WRECK = (60, 198)             # the council's skiff where it came down on Crashfall
GIANT_SWORD = (112, 158)      # the sword the size of a tree on the Golem Fields
OBSERVATORY = (142, 126)      # the old observatory ruin on the Broad Isle's rise
LAST_EDGE = (22, 242)         # the Last Falls, where the river goes over into nothing
SECOND_ROCK = (52, 91)        # Tethertown's second rock, below Halcyon Rest (tools/handbuilt_worldtree_halcyon_rest.py)
HR = "halcyon_rest"         # the Expanse's town, its own map
CITADEL = (72, 68)            # in front of the broken citadel in the middle of the ring
SPIRE = (270, 112)            # under the Ascendancy's watch-spire on the Lancer's Perch
WHALE_ROCK = (234, 200)       # the rock the whales rub on, out in the Shallows
DEEP_CLOUD = (252, 184)       # the far side of the Shallows, where the pod turns
BRIDGE_FOOT = (226, 8)        # the foot of the sky-bridge


def build():
    out = []
    A = out.append

    # =================================================================================== 1. CRASHFALL
    A(Q("ceq_what_brought_us_down", "What Brought Us Down", ILAREN, 49, 49, "Crashfall",
        "Ilaren Vey watched the light that hit the skiff come up off the islands. The Ward-Spark that still crackles "
        "round the wreck is what's left of it, and it hasn't stopped firing.",
        [k("Ward-Spark", 7)],
        "Every Ward-Spark round this wreck is a piece of whatever shot us down, and they're still trying to finish the "
        "job. Put them out before they set the rest of the skiff alight. I want to look at what they leave behind.",
        "They go out like candles, and they leave a little ash shaped like a letter.\n\nI've seen that letter before, "
        "on the seal at the Crown. These wards aren't Aetherian, and they're not new.",
        nxt="ceq_the_wards_were_kharad"))
    A(Q("ceq_the_wards_were_kharad", "The Wards Were Kharad", ILAREN, 49, 49, "Wardreader's",
        "Ilaren has copied the letter the Ward-Sparks leave behind. There's a scholar from the House of Long Memory on "
        "the Golem Fields who has spent her whole life on the Kharad, and Ilaren wants her to see it.",
        [deliver("ce_q_ward_sketch", "Take Ilaren's sketch to Scholar Idris Marrowell at Halcyon Rest")],
        "My house used to laugh at the House of Long Memory. They said the Kharad built the old stones before we came, "
        "and we said they were telling children's stories. Idris Marrowell is up on the Golem Fields, upriver from "
        "here. Take her this, and tell her I'm sorry we laughed.",
        "Ilaren Vey sent this, and Ilaren Vey said sorry? I'll have that written down.\n\nIt's Kharad, and it's a ward "
        "letter, the one that means strike, and it's cut on every golem lying out on these fields. They're the same "
        "makers, and they woke up on the same day.",
        turn_in_npc_id=IDRIS, nxt="ceq_they_were_lying_still",
        grant_items=carry("ce_q_ward_sketch", "Ilaren's Ward Sketch", "A page from Ilaren Vey's notebook with one "
                          "Kharad letter drawn on it over and over, each copy neater than the last.")))
    A(Q("ceq_the_skiffs_heart", "The Skiff's Heart", PILOT, 49, 49, "Pilot's",
        "Skiff-Pilot Varo Senn can't stand yet, but he can count. Half the skiff's crystal is gone, and the Crashfall "
        "Scuttler swarming the wreck has been dragging the pieces off.",
        [fetch("ce_q_skiff_crystal", 6)],
        "The skiff's crystal broke when we hit, and every Crashfall Scuttler on this rock has carried a piece of it "
        "off to its hole. They like anything that shines, even when it's dark. Bring me back what they took, and I'll "
        "see if there's enough of her heart left to send a signal.",
        "It's enough for a signal, but it isn't enough to fly.\n\nShe was a good skiff. I'll send word to Halcyon Rest "
        "that we're alive, and then I'll sit here and feel sorry for her."))
    A(Q("ceq_stone_in_the_road", "Stone in the Road", PILOT, 49, 50, "Roadclearer's",
        "The road upriver to the Golem Fields is the way to Halcyon Rest and Aurelion. Varo has seen the Golem-Field "
        "Rubble rolling over it, and he's sure it wasn't moving last month.",
        [k("Golem-Field Rubble", 7)],
        "When my leg holds, I'll be walking that road like the rest of you, and I don't want to walk it round rocks "
        "that get up and follow me. The Golem-Field Rubble upriver is moving. Break it up so the road stays a road.",
        "It's rubble that stays where you drop it now, which is how I like my rubble.\n\nThe golems it came off are "
        "still out there, though. I saw one sit up this morning."))
    A(Q("ceq_the_councils_courtesy", "The Council's Courtesy", HERALD, 49, 49, "Herald's",
        "Herald Cassian Orel came down with a case of gifts and the council's own seal, to welcome you to Aurelion "
        "properly. The case was thrown clear somewhere in the wreck.",
        [explore(*WRECK, "Search the council's wrecked skiff for the herald's seal-case")],
        "The High Houses don't send a guest an invitation without a seal on it, and mine is somewhere in that wreck. "
        "The gifts don't matter, but the seal does. If you'll climb in and look, I'll stand here and try not to look "
        "like a man who lost the council's seal.",
        "The gifts are glass now, but the seal's whole. That's the first thing that's gone right today.\n\nI can't "
        "walk into Aurelion with you yet. The keeper at Halcyon Rest has to hear first that the council's guests are "
        "alive."))
    A(Q("ceq_word_upriver", "Word Upriver", PILOT, 49, 49, "Messenger's",
        "Halcyon Rest is the waystation halfway up the river, and its keeper speaks to the council every evening. "
        "Herald Cassian wants him to hear about the crash from someone who walked away from it.",
        [deliver("ce_q_heralds_letter", "Take the pilot's letter to Keeper Ithren Lorrow at Halcyon Rest")],
        "Keeper Ithren Lorrow at Halcyon Rest will tell the council anything I write, and he'll believe it more if it "
        "comes in your hand. It's upriver, past the Golem Fields and across the Broad Isle. Don't stop for the "
        "scenery, it's lovely and most of it bites.",
        "The council's skiff came down, and the council's guests walked here anyway.\n\nI'll send this tonight. I've "
        "had a lot of bad news to send lately, and it's good to send some that's only half bad.",
        turn_in_npc_id=ITHREN,
        grant_items=carry("ce_q_heralds_letter", "Pilot's Letter", "A letter in Skiff-Pilot Varo Senn's square hand, "
                          "written lying down and folded round a flight log with the last entry still wet.")))
    A(Q("ceq_something_to_eat", "Something to Eat", LEANDRO, 49, 49, "Campcook's",
        "The skiff's stores went over the edge when it came down. Leandro Arrieta has a fire going and nothing to put "
        "on it, and the Cloudfleece Ram is grazing all over Crashfall.",
        [fetch("ce_q_ram_shank", 6)],
        "Everything we had to eat is somewhere below us, falling. There's a Cloudfleece Ram on every patch of grass "
        "round here, though, and I know how to cook one. Bring me back some shanks, and I'll feed everyone who "
        "walked out of that wreck.",
        "Three years up here, and I've learned to cook a sky sheep. My mother would be proud and a little confused.\n\n"
        "Eat something while it's hot, because there's a long walk upriver, and nobody's carrying you."))
    A(Q("ceq_other_earthborn", "Other Earthborn", LEANDRO, 49, 49, "Earthborn",
        "Leandro has heard there are Earth people living on tethered rocks off the Broad Isle. He's never met any "
        "Earthborn outside the survey's Annex, and he wants someone to find out if it's true.",
        [deliver("ce_q_leandros_note", "Take Leandro's note to Kaisa Lehtonen in Tethertown")],
        "The survey kept us at the Annex like guests, and I never met another one of us who wasn't on a scholar's "
        "list. The Aetherians say there's a place called Tethertown off the Broad Isle where Earth people live on "
        "their own. Take them this note, and tell them there's a guy from Buenos Aires who'd like to say hello.",
        "Leandro Arrieta, from Buenos Aires, three years in the sky. I like him already.\n\nThere are thirty-one of us "
        "here. Nobody kept us anywhere, so we tied our own rocks together and stayed.",
        turn_in_npc_id=KAISA,
        grant_items=carry("ce_q_leandros_note", "Leandro's Note", "A folded note in Spanish and English, with a little "
                          "drawing of a football at the bottom.")))
    A(Q("ceq_mind_the_gangway", "Mind the Gangway", HASK, 49, 49, "Landing Hand's",
        "Landing Hand Hask Merrow keeps the survey's skiff landing on Crashfall. Every Young Crystalback on the rock "
        "has decided the gangway's timbers are the best thing to sharpen its back on.",
        [k("Young Crystalback", 7)],
        "Every Young Crystalback on Crashfall comes down to the landing at night and rubs its crystals on my gangway, "
        "and every morning there's a little less gangway. The skiff from Lenswatch is the only way off this rock. "
        "Chase them off for good.",
        "The gangway's still standing, and so am I, which is more than I'd have bet on yesterday.\n\nThe skiff "
        "comes down tomorrow. You'll be upriver by then, if you've got any sense."))

    # =================================================================================== 2. THE GOLEM FIELDS
    A(Q("ceq_they_were_lying_still", "They Were Lying Still", IDRIS, 49, 50, "Golemwarden's",
        "The war-golems lay on these fields for as long as the Aetherians have kept records. Since the seal cracked, "
        "every Waking War-Golem has been getting up, and they're all walking the same way.",
        [k("Waking War-Golem", 8)],
        "The House of Long Memory has drawings of these golems lying exactly where they fell, three hundred years of "
        "drawings. Now every Waking War-Golem on the field is standing up and walking downriver toward the wards. Put "
        "them back down. I'll write down where each one falls.",
        "They were walking toward Crashfall, every one of them.\n\nI think they're going back to their posts, to the "
        "wards that shot your skiff down. They were made to guard something, and they've remembered.",
        requires_quests=["ceq_the_wards_were_kharad"], nxt="ceq_the_unbound_core"))
    A(Q("ceq_the_sentinels_still_keep_watch", "The Sentinels Still Keep Watch", IDRIS, 49, 50, "Sentinel's",
        "The Kharad Sentinel didn't lie down with the golems. Idris says each one carries a ward-core cut with the "
        "same letter as the wards at Crashfall, and she wants to read them.",
        [fetch("ce_q_ward_core", 5)],
        "A Kharad Sentinel never fell with the golems, it just stood still with its eyes shut. Now they've opened them. "
        "Every one has a ward-core in its chest cut with the strike letter, and I want them on my table. If I can read "
        "the wards, maybe I can tell them to stop.",
        "They're warm, all of them, and they're warm the same way.\n\nThey're answering something. It isn't anything "
        "on the fields, it's something in the middle of them, under the sword. I've heard it humming for a week."))
    A(Q("ceq_the_unbound_core", "The Unbound Core", IDRIS, 50, 50, "Corebreaker's",
        "Under the great sword in the middle of the Golem Fields, something is humming. Idris thinks The Unbound Core is "
        "what's waking the golems, and that it won't stop until every one of them is standing.",
        [boss("The Unbound Core")],
        "The Unbound Core is what's under the sword, and it's what's waking them. Every time it pulses, another golem "
        "stands up. I've spent my life proving the Kharad were real, and I'd love to study it. I'd love even more to "
        "still be alive tomorrow, so break it.",
        "The fields are quiet, and the golems that were standing have fallen over where they stood.\n\nI opened "
        "what's left of the core. It's Kharad stone round a heart of crystal cut the way only my people cut it, and "
        "the storm inside it was sung in, the way the Veyr sing to weather. Three peoples made that golem, and my house "
        "doesn't have a single story where they ever stood in the same room. The forge "
        "that made them is on the island west of here. Ilaren Vey ought to see it. If the golems woke, the forge "
        "might have too.",
        requires_quests=["ceq_they_were_lying_still", "ceq_the_sentinels_still_keep_watch"]))

    # =================================================================================== 2b. THE GOLEM VAULT (cave)
    A(Q("ceq_the_sleepers_wake", "The Sleepers Wake", LEANDRO, 50, 51, "Vaultdelver's",
        "The war-golems on the fields came from somewhere, and Idris has found the door. Down in the Golem Vault, the "
        "Kharad crews who built them lie in the stone, and Leandro has heard that the Vault Sleeper is waking with the "
        "golems.",
        [k("Vault Sleeper", 6, zone=GV), k("Thunder-Binder Sleeper", 4, zone=GV)],
        "Idris found a door on the west side of the Golem Fields, and she says it goes down to where the Kharad kept "
        "their golems. She also says the crews are down there, asleep in the stone, and they're waking up. Every Vault "
        "Sleeper and Thunder-Binder Sleeper that gets up is one more giant between us and Aurelion. I'm curious, and "
        "I'm not stupid, so you go first.",
        "Giants, real ones, with beards like a mountain and shields like doors.\n\nThree years up here, and I "
        "thought I'd seen the strangest thing the sky had. Idris is going to be unbearable about this, and I think "
        "she's earned it.",
        requires_quests=["ceq_they_were_lying_still"]))
    A(Q("ceq_vault_thane_brask", "Vault-Thane Brask", LEANDRO, 51, 51, "Thanebreaker's",
        "Leandro has heard Idris read the name cut over the wrights' hall in the Golem Vault. Vault-Thane Brask kept "
        "the vault, and he's guarding it again.",
        [boss("Vault-Thane Brask", zone=GV)],
        "Idris read the name over the hall where the golems were made, and it's Vault-Thane Brask. He was the vault's "
        "keeper, and he's awake and keeping it, with his shield up in the wrights' hall. You don't have to go and fight "
        "him, but I'd like to know what a giant thane guards so hard.",
        "Plates, hundreds of them, each one cut with a golem's name.\n\nHe wasn't guarding treasure. He was "
        "guarding the list of every golem they made, so they'd know which ones came home.",
        requires_quests=["ceq_the_sleepers_wake"]))
    A(Q("ceq_stormwright_yrvald", "Stormwright Yrvald", DAVIN, 51, 51, "Stormbreaker's",
        "Every golem's core and every ward that fired on the skiff runs on the same storm. Idris has traced it to the "
        "Storm-Well, the Golem Vault's lowest floor, and Skiff-Pilot Varo wants it put out by whoever keeps it.",
        [boss("Stormwright Yrvald", zone=SW)],
        "Idris says the light that killed my skiff's crystal came from a storm the Kharad bound in a well under the "
        "Golem Fields, and that one of them still keeps it. Stormwright Yrvald, she calls him. Go down the Deep Stair "
        "to the Storm-Well and put him out. I'd go, but I'd have to crawl.",
        "The wards on Crashfall went dark an hour ago. I watched them go.\n\nThat's the first time since we came "
        "down that I've felt like a pilot again. Nothing down here will shoot at a skiff now, and I'll fly again.",
        requires_quests=["ceq_the_sleepers_wake"]))

    # =================================================================================== 3. THE SILENT FORGE
    A(Q("ceq_the_forge_is_warm", "The Forge Is Warm", ILAREN, 50, 51, "Forgewatch",
        "Idris told Ilaren what she found, and Ilaren has been looking west ever since. The Silent Forge has been cold "
        "for ages, and now there's smoke over it, with a Forge Guardian at the door and an Ancestral Smith at the anvil.",
        [k("Forge Guardian", 7), k("Ancestral Smith", 5)],
        "Idris says the golems were made at the Silent Forge, on the island west of the fields, and there's smoke "
        "over it for the first time in anyone's memory. A Forge Guardian stands at every door and an Ancestral Smith "
        "is working at every anvil, and I don't want to find out what they're making. Put out the forge's keepers.",
        "They weren't making golems. They were mending them, the ones that fell on the fields, piece by piece.\n\nI "
        "think something in there still gives the orders. The smiths were all turned toward the biggest anvil.",
        requires_quests=["ceq_the_unbound_core"], nxt="ceq_forge_elder_ommun"))
    A(Q("ceq_glass_that_burns", "Glass That Burns", DAVIN, 50, 51, "Skiffmaster's",
        "Skiffmaster Davin Sorell keeps his skiffs flying with their crystals hooded so the old wards don't see them. "
        "The best hood is crystal that doesn't shine, and the Molten Crystal Elemental at the forge sets into exactly "
        "that.",
        [fetch("ce_q_forge_glass", 5)],
        "My hoods are cloth, and cloth slips. The Molten Crystal Elemental at the Silent Forge turns cloudy and dull "
        "when it cools, and dull is what I need. Bring me back the cooled glass, and I'll make hoods that the wards "
        "won't see through.",
        "It's ugly, and it's perfect.\n\nMy skiffs will fly safer with this on them than they've flown since the "
        "seal cracked. I'll owe you a seat on any one of them, for as long as I'm flying."))
    A(Q("ceq_forge_elder_ommun", "Forge-Elder Ommun", ILAREN, 51, 51, "Forge-Elder's Bane",
        "The smiths at the Silent Forge all face the biggest anvil. Ilaren has read the name cut over it, and he's sure "
        "Forge-Elder Ommun is the one still giving the forge its orders.",
        [boss("Forge-Elder Ommun")],
        "The name over the biggest anvil is Ommun, and the letter after it means elder. Forge-Elder Ommun's still "
        "working in there, mending golems for a war that ended before my people learned to build. Go in and put the "
        "old smith to rest.",
        "Ommun's hammer stopped, and the forge went cold the moment it did.\n\nI'll write all of this down for the "
        "council. The Kharad were here first, they made weapons, and their weapons are waking up. That should make "
        "the High Houses very quiet for once.",
        requires_quests=["ceq_the_forge_is_warm"]))

    # =================================================================================== 4. TETHERTOWN
    A(Q("ceq_the_last_few", "The Last Few", KAISA, 49, 50, "Searcher's",
        "Thirty-one Earthborn woke on these islands, and Kaisa Lehtonen has found twenty-eight of them. She has two "
        "places left to look, the old observatory on the Broad Isle and the edge of the Last Falls.",
        [explore(*OBSERVATORY, "Search the old observatory on the Broad Isle"),
         explore(*LAST_EDGE, "Search the edge of the Last Falls")],
        "I've found twenty-eight of us, and there are three I haven't. Somebody saw a light in the old observatory "
        "on the Broad Isle, and somebody else saw footprints going down to the Last Falls. I can't leave the camp "
        "for long. Go and look, and bring back anything you find, even if it's bad.",
        "A coat with a Toronto transit pass in the pocket at the observatory, and a fire that's been lit this week.\n\n"
        "Nothing at the falls but the falls. I'll take the coat, and I'll take the fire. Someone's alive out there.",
        nxt="ceq_old_goldmane"))
    A(Q("ceq_old_goldmane", "Old Goldmane", KAISA, 50, 50, "Goldmane's Bane",
        "Kaisa's search parties keep turning back on the Broad Isle. An old lion with a gold mane follows them through "
        "the long grass, and Old Goldmane is the reason nobody's searched the island properly.",
        [boss("Old Goldmane")],
        "Every time we go out on the Broad Isle, Old Goldmane follows us. He's the biggest lion I've ever seen, and "
        "he doesn't attack, he just walks behind us in the grass until we lose our nerve. Whoever lit that fire at "
        "the observatory is living with him. Make the Broad Isle safe to search.",
        "We went out again this morning, with nothing behind us.\n\nWe found her, a woman from Toronto who'd been "
        "living in the observatory for a year. She'd been hiding from the lion too, and now there are two still out there.",
        requires_quests=["ceq_the_last_few"]))
    A(Q("ceq_hawks_on_the_lines", "Hawks on the Lines", GUSTAVO, 49, 50, "Rigger's",
        "Gustavo Pires tied Tethertown's rocks together with every rope the Earthborn could find. The Gale Hawk nests "
        "on the lines, and the hawks pick at them until they fray.",
        [k("Gale Hawk", 8)],
        "Every Gale Hawk on the Broad Isle thinks my ropes are the best perch in the sky, and they pick at them while "
        "they sit there. If a line frays, a rock with a house on it drifts off. Thin them out, please, before I'm "
        "tying knots in the dark again.",
        "Nothing's sitting on my lines, and nothing's picking them.\n\nI'll be honest, I like the hawks. I just like "
        "my neighbours more, and my neighbours live on the end of those ropes."))
    A(Q("ceq_sinew_for_rope", "Sinew for Rope", GUSTAVO, 49, 50, "Ropemaker's",
        "Tethertown's ropes are old and Earth-made, and Gustavo can't make more. The Skymane Lion on the Broad Isle "
        "has sinew stronger than any of them.",
        [fetch("ce_q_lion_sinew", 5)],
        "My ropes are climbing rope and ship rope and one very long extension cord, and they won't last forever. "
        "Every Skymane Lion on the Broad Isle has sinew that'd hold a house. Bring me some, and I'll braid lines that "
        "outlast all of us.",
        "That's lovely sinew. I've never said that before, and I hope I'll never have to again.\n\nI'll braid it "
        "tonight. The second rock's line is the oldest, so it gets the first new one."))
    A(Q("ceq_check_the_knots", "Check the Knots", GUSTAVO, 50, 50, "Knotkeeper's",
        "The new line's on the second rock, and Gustavo can't cross to check it without leaving the main lines "
        "untended. He wants someone to go over the planks and look at the knots.",
        [explore(*SECOND_ROCK, "Cross the planks and check the knots on Tethertown's second rock", zone=HR)],
        "Go across the planks to the second rock and look at every knot I tied. If one's slipping, you'll see the rope "
        "pale where it's pulled. I'd go myself, but if I step away from the main lines, something always goes wrong "
        "while I'm gone.",
        "Every knot holding, and the new line taking the weight. That's a good day's work for a guy from Rio.\n\nIt's "
        "a strange thing to be proud of, tying rocks to the sky. I'm proud of it anyway.",
        requires_quests=["ceq_sinew_for_rope"]))
    A(Q("ceq_boars_in_the_rows", "Boars in the Rows", ANNELIES, 49, 50, "Gardener's",
        "Annelies de Vries has planted every Earth seed she carried in sky soil. The Crystalback Boar digs her rows up "
        "every night, and the young ones follow.",
        [k("Crystalback Boar", 7), k("Young Crystalback", 5)],
        "Every Crystalback Boar on the Broad Isle comes down to my rows at night and roots up whatever I planted, and "
        "the Young Crystalback follows along to learn how. I grew forty hectares of tomatoes under glass back home in Westland, and I'd never "
        "had a pest with crystals on its back. Keep them out of my garden.",
        "The rows are whole, and the blue tomatoes are still coming up.\n\nI tasted one this morning. It tasted like a "
        "tomato that had been somewhere strange, and I think that's what we all taste like now."))
    A(Q("ceq_seeds_in_sky_soil", "Seeds in Sky Soil", ANNELIES, 49, 50, "Seedkeeper's",
        "Annelies wants to know what grows wild up here before she plants anything else. Sungrass grows all over the "
        "islands, and she wants enough to plant beside her own seeds.",
        [gather("herb_sungrass", 6, "Gather Sungrass on the islands")],
        "I want to see what the sky soil likes before I spend another seed. Sungrass grows wild all over these "
        "islands, so gather me some, and I'll plant it next to the tomatoes. If they grow well together, we'll eat "
        "better this winter.",
        "They'll grow together. Look at the roots on this, they're already reaching for each other.\n\nYou've done "
        "more for this garden than anyone except me. Take something for the road."))

    # =================================================================================== 5. HALCYON REST AND THE RING
    A(Q("ceq_the_road_from_the_spillway", "The Road From the Spillway", ITHREN, 50, 51, "Waywarden's",
        "Refugees from the fallen Eighth Ring walk down from the Spillway to Halcyon Rest. Keeper Ithren Lorrow has "
        "lost two of them on the way to the Skymane Lion hunting the river road.",
        [k("Skymane Lion", 7)],
        "The people from the Eighth Ring walk down the river to us because the city has nowhere to put them. Every "
        "Skymane Lion on the Broad Isle has learned that the river road is full of tired people. Hunt them, so the "
        "next ones who walk down here don't get eaten on the way.",
        "The road's quiet, and the last group walked in without a scratch.\n\nThey asked who'd cleared it, and I told "
        "them a guest of the council. They didn't believe the council had guests, and since the change, nobody in Aurelion believes much of what they're told. I'm not sure I did either.",
        requires_quests=["ceq_word_upriver"]))
    A(Q("ceq_the_broken_citadel", "The Broken Citadel", ITHREN, 50, 51, "Citadel",
        "In the middle of the Orbiting Ruins stands a broken citadel that the Aetherians never built. Keeper Ithren "
        "has heard Idris's news about the Kharad, and he wants to know if the citadel is theirs.",
        [explore(*CITADEL, "Stand in front of the broken citadel in the middle of the Orbiting Ruins")],
        "Halcyon Rest has looked out at the Orbiting Ruins for three hundred years, and none of us ever asked who built "
        "them. If the scholar's right about the Kharad, that citadel is theirs. Walk out across the ring and look at "
        "it, and tell me if it's cut with the same letters.",
        "The strike letter on the gate, and the guard letter all round it.\n\nIt's Kharad, then. We've been drinking "
        "tea and watching a Kharad fortress turn for three hundred years, and we thought it was pretty."))
    A(Q("ceq_the_bells_of_the_ring", "The Bells of the Ring", TEODRIC, 50, 51, "Bellsilencer's",
        "Teodric Ashlane was at the market when the Eighth Ring fell, and the bells on the Orbiting Ruins rang that "
        "morning. The Bellringer Sprite still rings them, and he can hear them from Halcyon Rest.",
        [k("Bellringer Sprite", 7)],
        "The bells out on the ring rang the morning the Eighth Ring fell. Every Bellringer Sprite out there rings them "
        "every morning since, and every morning I wake up thinking it's that morning again. Make them stop, please. "
        "I'd like to wake up in this one.",
        "It's quiet out there, and I slept until the sun was up.\n\nThe Eighth Ring stood for nine hundred years and fell two years after the change, and nobody in Aurelion can tell you why. I don't know if the bells knew. I don't know if "
        "they rang because the ring was falling, or if the ring fell and they rang. I'd still rather not hear them."))
    A(Q("ceq_wyrms_on_the_ring", "Wyrms on the Ring", TEODRIC, 50, 51, "Wyrmwatch",
        "Teodric wants to go out to the Orbiting Ruins and see the bells for himself. The Ringwind Wyrm coils round "
        "every span of the ring, and he isn't a fighter.",
        [k("Ringwind Wyrm", 8)],
        "I want to stand by those bells and look at them, just once, without hearing them. I can't fight, and every "
        "Ringwind Wyrm on the ring coils round the spans like they're its own. Clear them off, and I'll walk out there "
        "myself.",
        "I went out this morning and stood under the biggest bell.\n\nIt's just bronze, cut with letters I can't "
        "read. I thought it'd be bigger, or worse. Something in the citadel was watching me the whole time, though.",
        nxt="ceq_ringwarden_kozh"))
    A(Q("ceq_ringwarden_kozh", "Ringwarden Kozh", TEODRIC, 51, 51, "Ringwarden's Bane",
        "Something in the broken citadel watched Teodric the whole time he stood under the bells. The stone keeper of "
        "the ring is Ringwarden Kozh, and it's started walking the spans.",
        [boss("Ringwarden Kozh")],
        "It was Ringwarden Kozh, a stone thing as tall as a house, and it watched me from the citadel gate. Today it "
        "walked out onto the ring and pushed a pilgrim off the spans. Nobody's going to walk out there again while "
        "it's standing.",
        "It's down, and the ring's still turning without it.\n\nI'll go out again tomorrow and stand under the bells. "
        "I think I'll do it every morning, for my street.",
        requires_quests=["ceq_wyrms_on_the_ring", "ceq_the_bells_of_the_ring"]))
    A(Q("ceq_eyes_over_the_river", "Eyes Over the River", DAVIN, 50, 51, "Skyreader's",
        "The Ascendancy flies scouts over the river from the Lancer's Perch. Skiffmaster Davin wants their patrol "
        "routes, and the Ascendancy Scout Construct carries them etched on a crystal plate.",
        [fetch("ce_q_patrol_log", 5)],
        "Every Ascendancy Scout Construct that flies over the river from the Lancer's Perch carries a log of where it "
        "flew and when. Bring me those logs, and I'll know where they'll be tomorrow. My skiffs will be somewhere "
        "else.",
        "They fly the same routes every day, like clockwork, which is a thing the Earthborn say.\n\nThat's "
        "enough to keep my skiffs out of their way for a season. The Ascendancy isn't very imaginative."))

    # =================================================================================== 6. THE LANCER'S PERCH
    A(Q("ceq_the_lancers_perch", "The Lancer's Perch", DACE, 50, 51, "Deserter's",
        "Dace Morrow served at the Lancer's Perch until he put his lance down. He knows what used to stand under the "
        "watch-spire, and he wants to know what stands there now.",
        [explore(*SPIRE, "Get under the Ascendancy's watch-spire on the Lancer's Perch and count what's there")],
        "I walked off the Perch with nothing but my boots, and they'll have added to it since. Cross the chains from "
        "here and get under the watch-spire. Count the guns, count the tents, and count the lancers on the rest. "
        "Don't let them see you, they'll know who sent you.",
        "Two guns where there was one, and twice the tents.\n\nThey're not watching the river any more. They're getting "
        "ready to close it, and anyone who wants to walk to Aurelion will have to walk under their guns.",
        nxt="ceq_lances_down"))
    A(Q("ceq_lances_down", "Lances Down", DACE, 50, 51, "Lancebreaker's",
        "Dace knows every Perch Lancer on the rest, and he knows they'll fire on anyone they're ordered to. He wants "
        "them to know what that costs.",
        [k("Perch Lancer", 7)],
        "I trained half of them myself. Every Perch Lancer on that rest will fire on refugees if the captain says so, "
        "because I would have, once. Go up and break them. I don't want them dead because I hate them. I want them "
        "dead because they won't put their lances down.",
        "You did what I couldn't do, and I'm grateful, and I feel sick about it.\n\nThat's two feelings, and they're "
        "both true. The captain's still up there.",
        requires_quests=["ceq_the_lancers_perch"]))
    A(Q("ceq_binders_and_inquisitors", "Binders and Inquisitors", DACE, 50, 51, "Perchbreaker's",
        "Every Ascendancy Gravity-Binder on the Perch holds the spire up, and every Ascendancy Inquisitor makes sure "
        "nobody on it thinks too hard about their orders.",
        [k("Ascendancy Gravity-Binder", 5), k("Ascendancy Inquisitor", 5)],
        "The Ascendancy Gravity-Binder holds that spire up in the air, and the Ascendancy Inquisitor holds the "
        "soldiers in line. The inquisitors are why I didn't put my lance down sooner. Break both, and the Perch "
        "starts to come apart.",
        "The spire's listing, and the soldiers are arguing with each other on the rest. I can hear it from here.\n\n"
        "That's how it starts. That's how it started for me."))
    A(Q("ceq_spire_captain_alun_vesk", "Spire-Captain Alun Vesk", DACE, 51, 51, "Spire-Captain's Bane",
        "Spire-Captain Alun Vesk is the officer who ordered his lancers to fire on a parley. Dace walked away from him "
        "then, and he wants you to walk up to him now.",
        [boss("Spire-Captain Alun Vesk")],
        "Spire-Captain Alun Vesk gave the order I wouldn't follow. He said a parley with refugees was a trick, and he "
        "told us to fire. Some of us did, and I put my lance down on the stones. Go up the spire and finish what I should have "
        "started that day.",
        "Vesk's gone, and the Perch is falling back to its tents.\n\nThe river road's open to Aurelion. I'll never wear "
        "the Ascendancy's colours again, but I might wear the council's, if they'll have a deserter.",
        requires_quests=["ceq_lances_down", "ceq_binders_and_inquisitors"]))

    # =================================================================================== 7. THE WHALE SHALLOWS
    A(Q("ceq_counting_whales", "Counting Whales", ANA, 50, 51, "Whalecounter's",
        "Dr. Ana Kealoha counts the whales in the Whale Shallows every day. She's sure the pod has got smaller, and she "
        "wants someone who can walk the far side of the cloud to count with her.",
        [explore(*WHALE_ROCK, "Go out to the rock the whales rub on in the Shallows"),
         explore(*DEEP_CLOUD, "Go to the far side of the Shallows where the pod turns")],
        "I count the pod from here every morning, and every week the number's smaller. Walk out to the rock they rub "
        "on, then go round to the far side where they turn. Count them the way I'd count humpbacks off Maui, from the flukes, "
        "and I'll count from this side.",
        "Eleven from your side and eleven from mine, and three weeks ago it was fourteen.\n\nSomething's taking the "
        "calves. I've seen serpents in the cloud under the pod, and I didn't want it to be them.",
        nxt="ceq_serpents_under_the_pod"))
    A(Q("ceq_serpents_under_the_pod", "Serpents Under the Pod", ANA, 50, 51, "Podguard's",
        "The Cloud Serpent hunts under the whale pod, and the Skimming Ray follows to take what it leaves. Ana has "
        "watched them take the calves.",
        [k("Cloud Serpent", 7), k("Skimming Ray", 5)],
        "Every Cloud Serpent in the Shallows swims under the pod and waits for a calf to drift low. Then the Skimming "
        "Ray comes in after it. I spent fifteen years telling people not to interfere with nature, and I've decided "
        "this isn't my nature. Keep them off the calves.",
        "The pod's swimming higher, and the calves are in the middle where they belong.\n\nI've never been so happy to "
        "be a hypocrite. There's one serpent left that I've seen, and it's bigger than all the others.",
        requires_quests=["ceq_counting_whales"], nxt="ceq_the_pale_serpent"))
    A(Q("ceq_the_pale_serpent", "The Pale Serpent", ANA, 51, 51, "Pale Serpent's Bane",
        "The biggest serpent in the Shallows is pale as the cloud it swims in. Ana has seen The Pale Serpent take a "
        "calf in one bite, and the pod won't come down low while it's there.",
        [boss("The Pale Serpent")],
        "The Pale Serpent is white like the cloud, and you only see it when it moves. I watched it take a calf in one "
        "bite last week, and the mother called for it all night. Find it in the white, and don't let it see you first.",
        "The pod came down low this morning, all eleven, and the mother's calling has stopped.\n\nI'll keep counting. "
        "That's what I do, and up here I get to count something nobody's ever counted before.",
        requires_quests=["ceq_serpents_under_the_pod"]))

    # =================================================================================== 8. THE SPILLWAY
    A(Q("ceq_whats_in_the_water", "What's in the Water", LORNE, 51, 51, "Aqueduct-Warden's",
        "Aurelion's water should turn back into the city through the Fourth Aqueduct. Since the change, it spills down into "
        "the Spillway, and the Spillway Eel and Crystal Crab have come up to live in it.",
        [k("Spillway Eel", 7), k("Crystal Crab", 6)],
        "This is Aurelion's water, and it's meant to be clean enough to drink in the High Houses. Now every Spillway "
        "Eel and Crystal Crab in the Expanse has found it and moved in. Clear them out of the pool, and I'll be able "
        "to see what's wrong with the aqueduct.",
        "The pool's clear enough to see the bottom, and I wish it weren't.\n\nThere are cracks in the stone under the "
        "pool, and something's coming up out of them. That isn't water damage."))
    A(Q("ceq_out_of_the_cracks", "Out of the Cracks", LORNE, 51, 51, "Crackwarden's",
        "The stone under the Spillway's pool is cracked, and the Rift Crawler is climbing up out of the cracks. "
        "Aqueduct-Warden Lorne Ishay wants them back where they came from.",
        [k("Rift Crawler", 7)],
        "Every Rift Crawler round the pool came up out of those cracks, and more come up every night. I don't know "
        "what's under there, and I don't want to find out by being pulled in. Drive them back down.",
        "Fewer coming up, and the ones that do come up are smaller.\n\nThe cracks are still there, though. The biggest "
        "one's in the middle of the pool, and something lives in it.",
        nxt="ceq_old_mouth_of_the_spill"))
    A(Q("ceq_old_mouth_of_the_spill", "Old Mouth of the Spill", LORNE, 51, 51, "Spillwarden's",
        "The biggest crack in the Spillway's pool has something living in it. Lorne calls it the Old Mouth of the "
        "Spill, and it pulls in anything that comes near the water.",
        [boss("Old Mouth of the Spill")],
        "The Old Mouth of the Spill lives in the crack in the middle of the pool. It drags in eels and crabs, and last "
        "night it dragged in a refugee's cart. If the council wants guests walking up to the bridge, the Mouth has to "
        "go first.",
        "The pool's still, and the crack's just a crack.\n\nI'll seal it when the masons come down from the city. "
        "Aurelion's water should go back to Aurelion, but at least now it won't eat anyone on the way.",
        requires_quests=["ceq_out_of_the_cracks", "ceq_whats_in_the_water"]))

    # =================================================================================== 9. THE BRIDGE
    A(Q("ceq_the_heralds_seal", "The Herald's Seal", HERALD, 51, 51, "Sealbearer's",
        "The river road is open, the Perch has fallen back and the forge is cold. Herald Cassian Orel wants the "
        "council's seal taken to the bridgewarden at the sky-bridge, so Aurelion's door will open for you.",
        [deliver("ce_q_council_seal", "Take the council's seal to Bridgewarden Caldus Rhee at the sky-bridge")],
        "The road's open, the Perch is quiet and the forge is cold, and that's more than the council asked of its "
        "guests. Take the seal up the river to Bridgewarden Caldus Rhee at the foot of the sky-bridge. It's your "
        "invitation, and I'd like you to deliver it yourself.",
        "The council's own seal, carried up the river by the council's own guest.\n\nI've been told to wait for word, "
        "and this is the word. I'm sorry I made you wait for it.",
        turn_in_npc_id=CALDUS,
        requires_quests=["ceq_word_upriver", "ceq_spire_captain_alun_vesk", "ceq_forge_elder_ommun"],
        nxt="ceq_the_sky_bridge",
        grant_items=carry("ce_q_council_seal", "The Council's Seal", "A disc of white crystal set in gold, warm to "
                          "the touch, carrying the marks of all the High Houses of Aurelion.")))
    A(Q("ceq_the_sky_bridge", "The Sky-Bridge", CALDUS, 51, 51, "Bridgewarden's",
        "Bridgewarden Caldus Rhee has the council's seal, and Aurelion's door is open to you. He wants you to walk up to "
        "the foot of the sky-bridge and see it for yourself.",
        [explore(*BRIDGE_FOOT, "Walk up to the foot of the sky-bridge")],
        "Go on up to the foot of the bridge and look. I've stood guard on it for twelve years, and I've never let "
        "anyone from the ground walk on it. I want to see what your face does.",
        "That's what everyone's face does, the first time.\n\nAurelion's rings round the Spire Palace, and the High "
        "Houses' towers on top like a crown. You could walk across right now and nobody would stop you. But the "
        "council's word came with a second letter, and it isn't good news.",
        nxt="ceq_word_to_the_wardens"))
    A(Q("ceq_word_to_the_wardens", "Word to the Wardens", CALDUS, 51, 51, "Wardensworn",
        "The council's second letter says the Third Anchor is slipping, and Aurelion's outer rings are moored to the "
        "shelf it holds. Bridgewarden Caldus Rhee wants you to take it east along the old aqueduct arm to the "
        "Anchor-Wardens at Keelstone.",
        [deliver("ce_q_second_letter", "Take the council's second letter to Warden-Prime Aldric Sorne at Keelstone")],
        "The anchors hold up the shelf the outer rings are moored to, and they have for a thousand years. One of them's "
        "slipping, and the council would rather its first guest from the ground saw to that before a ring drops. Go east along the aqueduct arm from the "
        "Spillway to the Anchorfields, and take this to the Warden-Prime at Keelstone. The bridge will still be here.",
        "The council's sent me a guest from the ground, with a letter saying the guest is the help.\n\nWell, I've "
        "asked for help for forty years and got letters. Help is new. Welcome to the Anchorfields.",
        turn_in_npc_id="af_warden_prime", requires_quests=["ceq_the_sky_bridge"],
        grant_items=carry("ce_q_second_letter", "The Council's Second Letter", "A short letter sealed in grey wax, the "
                          "council's mark for bad news, addressed to the Anchor-Wardens of Keelstone.")))
    return out
