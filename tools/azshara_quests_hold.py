"""
Azshara's quests, the second half: Timbermaw Hold's (the rot), the two arcs meeting at Eldarath, and the last of the
Drowned Palace. Read through tools/azshara_quests.build(); the people, helpers and maps are that file's.

THE ROT (Kyle, 18 Nov 2026: "Braided, both ends"). Whatever turned the Deadwood came up from under the Hold. The early
quests are the Hold's life: the pass, the spring, the totems, the carvers. Then Ingrid Solberg, a soil scientist at
home in Tromso, traces the rot in the roots to the satyrs of Haldarr and Legash, who are feeding it, and the Elder
opens the deep gate (the Rotroot Deeps).

ELDARATH. The Hold remembers what the Highborne were, and the satyrs were Highborne once: the rot is Highborne magic
gone bad, and the orcs' dig sits on top of its root. The Elder and the Conclave's archivist have to say so to each
other, and then the palace's last door opens for both hubs at once.
"""
from tools.azshara_quests import (  # noqa: F401
    Q, k, boss, explore, deliver, carry, fetch, FETCH_DROPS,
    WA, CA, EA, TL, TH, HD, RD, DP, DV, TT,
    ELDER, UNGAR, LESSA, GROTHAR, ULMA, BENNIK, INGRID, HROLM, BURRFOOT, GRASHAK, FENNA, GROSK,
    CAELIN, THRAG, DURGASH, OKKAR, SALEH)

FETCH_DROPS.update({
    "Autumn Treant": [("az_q_treant_heartwood", "Autumn Heartwood", "A knot of red-gold heartwood from inside a treant. "
                                                                   "It's warm, and the grain runs in spirals.")],
    "Legash Felhound": [("az_q_fel_tainted_soil", "Fel-Tainted Soil", "A pouch of soil from under a felhound's paws. "
                                                                      "It's green at the bottom and it smells wrong.")],
})


def gather(mat, n, label):
    return dict(type="gather", target=mat, count=n, label=label)


def build_hold():
    out = []
    A = out.append

    # ================================================================================= TIMBERMAW HOLD
    # ---- Gatewarden Hrolm
    A(Q("az_hippogryphs_on_the_pass", "Hippogryphs on the Pass", HROLM, 53, 53, "Passwarden",
        "The cliff hippogryphs on the Ursolan heights have started diving at anyone who climbs the pass to the Hold, "
        "and Gatewarden Hrolm has a gate full of furbolgs too scared to go down for supplies. The Hold's had more visitors since the Integration than in a hundred years, and the hippogryphs don't like any of them.",
        [k("Cliff Hippogryph", 8, WA)],
        "The Cliff Hippogryphs nest along the Ursolan pass, below the gate. Bring a few down, and the rest will learn "
        "to keep their distance. They're clever birds.",
        "The supply walkers went down the pass this morning and came back with all their fingers. The Hold thanks "
        "you, and I thank you.", zone=TH))
    A(Q("az_the_shadowsong_dead", "The Shadowsong Dead", HROLM, 54, 54, "Shadowsong",
        "The Timbermaw and the night elves of Shadowsong Shrine kept the peace for a long time. The Sentinels never "
        "left their shrine when they died, and now they don't know friend from foe.\n\nHrolm wants them laid to "
        "rest, kindly.",
        [k("Shadowsong Sentinel", 8, WA)],
        "Shadowsong Shrine's in the north-east of West Azshara, in the trees. Every Shadowsong Sentinel there was a "
        "friend of the Hold once. Let them go, and say a word for them if you can.",
        "They're resting now, all of them. I'll carve their names on the gate. The Timbermaw remember their friends.", zone=TH))

    # ---- Springwarden Lessa Brightwater
    A(Q("az_heartwood_for_the_spring", "Heartwood for the Spring", LESSA, 53, 53, "Springwood",
        "Springwarden Lessa keeps the Hold's spring clean with heartwood charms, and the old charms have started to "
        "go dark. The autumn treants in the forest grow the best heartwood there is.",
        [fetch("az_q_treant_heartwood", 8)],
        "The Autumn Treants walk the woods all over West Azshara. They'll give up their heartwood if you insist. "
        "Bring it back and I'll carve new charms.",
        "Good wood, warm and strong. The spring will like these. Ingrid says back home they'd test the water before "
        "they carved charms for it, but she'll allow it.", zone=TH,
        nxt="az_the_spring_goes_green"))
    A(Q("az_the_spring_goes_green", "The Spring Goes Green", LESSA, 54, 54, "Greenwater",
        "The new charms went dark in a day. Something is coming up into the spring from below, and Lessa has seen "
        "the same green in the water at the Sundering Mere. She wants to know if it's spreading.",
        [explore(154, 181, "Look into the water of the Sundering Mere", WA, radius=9)],
        "The Sundering Mere's in the south-east of West Azshara. Look at the water near the reeds. If it's green "
        "at the bottom, it's the same thing.",
        "Green at the bottom. It's the same rot, and it isn't only under the Hold.\n\nIngrid will want to hear "
        "this. She's been taking samples.", zone=TH))
    A(Q("az_sporecloud_samples", "Sporecloud Samples", LESSA, 56, 56, "Sporeward",
        "Down past the deep gate the air itself is rotten, and Lessa wants to know what's in it. The Drifting "
        "Sporeclouds in the Rotroot Deeps are made of it.",
        [k("Drifting Sporecloud", 10, RD)],
        "The Drifting Sporeclouds float through the Sporegarden under the Hold. Burst them, and you'll want to "
        "breathe through a cloth while you do it.",
        "The spores are dying in the air already. The spring smells better tonight than it has in a month.",
        zone=TH, requires_quests=["az_open_the_deep_gate"]))

    # ---- Herbwarden Fenna Mossbrow
    A(Q("az_dreamfoil_for_the_healers", "Dreamfoil for the Healers", FENNA, 54, 54, "Dreamleaf",
        "The Hold's healers are running out of dreamfoil, and the herbs on the Ursolan slopes are going brown. "
        "Herbwarden Fenna wants fresh leaves from lower down. The newcomers who climb the pass bring sicknesses the Hold's healers have never seen.",
        [gather("herb_dreamfoil", 8, "Gather dreamfoil in Azshara")],
        "Dreamfoil grows all over West and Central Azshara where the ground's soft. Pick it fresh. If it's brown "
        "at the edges, leave it.",
        "Good leaves, clean and cool. The healers will stop glaring at me.", zone=TH))
    A(Q("az_golden_sansam", "Golden Sansam", FENNA, 55, 55, "Sansam",
        "Golden sansam is what the Hold's healers use for rot fever, and since the spring went green there's a lot "
        "more rot fever. Fenna wants every root you can find.",
        [gather("herb_golden_sansam", 8, "Gather golden sansam in Azshara")],
        "Golden sansam grows in the forest across Azshara, mostly near water. Dig the whole root, it's no good "
        "without it.",
        "That's a winter's worth. We'll need it.", zone=TH))

    # ---- Carver Bennik Ashpaw
    A(Q("az_a_totem_for_valormok", "A Totem for Valormok", BENNIK, 54, 54, "Carver's",
        "Carver Bennik heard the satyrs burned Valormok's watch out, and he's carved a small totem for the orc who "
        "stayed. The Timbermaw give a totem to anyone who holds a gate alone.",
        [deliver("az_q_bennik_totem", "Bring Bennik's totem to Grunt Okkar at Valormok")],
        "Valormok's down the road to Orgrimmar, south of the crossroads. Give it to the grunt there. Tell him the "
        "Hold knows what he did.",
        "A furbolg totem, and it's for me.\n\nI'll put it on the new gate when I build it. Tell the carver I said thanks, "
        "and I don't say that much.", zone=TH, turn_in_npc_id=OKKAR,
        grant_items=carry("az_q_bennik_totem", "Bennik's Totem", "A small totem with a bear on top and an orc's face "
                                                                 "carved below it, both of them stubborn.")))
    A(Q("az_the_stolen_totem", "The Stolen Totem", BENNIK, 56, 56, "Legash",
        "The satyrs at Legash Encampment stole a Timbermaw totem when they came through the Ursolan pass, and they "
        "stood it over their warlord's throne. Bennik carved it, and he wants it home.",
        [k("Legash Satyr", 10, CA)],
        "Legash Encampment's under the northern mountains in Central Azshara. Break every Legash Satyr standing "
        "between you and the throne. The totem's the one with the bear on it.",
        "You brought it back. It's scratched and burned, and it's home.\n\nI'll carve it a new face. It's earned "
        "one.", zone=TH, requires_quests=["az_warlord_sethrak"]))

    # ---- Ingrid Solberg (the transplant volunteer)
    A(Q("az_samples_from_haldarr", "Samples from Haldarr", INGRID, 54, 54, "Fieldkit",
        "Ingrid Solberg was a soil scientist back home in Tromso, and she's been taking samples from round the Hold "
        "since the spring went green. She thinks the rot is coming from somewhere, and she wants soil from the "
        "satyrs' encampment.",
        [explore(160, 150, "Take a soil sample at the Haldarr Encampment", WA, radius=9)],
        "The Haldarr Encampment's in the south-east of West Azshara, over the den. Take a sample from under the "
        "tents. The satyrs won't like it, so be quick.",
        "Green all the way down. Worse than the Mere.\n\nThe satyrs aren't just living on the rot. They're "
        "feeding it.", zone=TH, nxt="az_samples_from_legash"))
    A(Q("az_samples_from_legash", "Samples from Legash", INGRID, 55, 55, "Fieldkit",
        "If the Haldarr satyrs are feeding the rot, Ingrid thinks the Legash camp is too. The Legash Felhounds dig "
        "under the tents, and what's under their paws is what she needs.",
        [fetch("az_q_fel_tainted_soil", 6)],
        "Legash Encampment's in the north of Central Azshara. The Legash Felhounds dig all round it. Bring me what "
        "they're digging in.",
        "It's the same green, the same smell, and it's running downhill. Toward the Hold.", zone=TH,
        nxt="az_tell_the_elder"))
    A(Q("az_tell_the_elder", "Tell the Elder", INGRID, 55, 55, "Fieldkit",
        "Ingrid has samples from the Mere, from Haldarr and from Legash, and they all say the same thing: the rot "
        "runs downhill from the satyrs' camps, and it all ends under the deep gate.\n\nShe wants the Elder to hear "
        "it from someone the Hold trusts.",
        [deliver("az_q_ingrid_findings", "Bring Ingrid's findings to Elder Haldor Mossmane at the Great Lodge")],
        "Take these to the Elder. I've written it plainly. He'll ask you if it's true, and you've seen it, so "
        "you'll know what to tell him.",
        "Under the deep gate. We sealed it because of what we heard down there, and we told ourselves it was "
        "only the wind.\n\nIt wasn't the wind.", zone=TH, turn_in_npc_id=ELDER, nxt="az_open_the_deep_gate",
        grant_items=carry("az_q_ingrid_findings", "Ingrid's Findings", "Ingrid's notebook, every sample labelled, "
                                                                       "and a map of the rot running downhill.")))
    A(Q("az_who_feeds_it", "Who Feeds It", INGRID, 56, 56, "Rotbreaker",
        "Ingrid says the rot spreads fastest where the satyrs work it, and the Haldarr Rogues carry it on their "
        "blades into the woods. Fewer satyrs means a slower rot.",
        [k("Haldarr Felsworn", 8, WA)],
        "The Haldarr Felsworn tend the fel fires in the encampment over the den. Put the fires out, and the ones "
        "who tend them, and don't breathe the smoke.",
        "The samples from the woods came back cleaner this week. Not clean, cleaner.", zone=TH,
        requires_quests=["az_samples_from_haldarr"]))

    # ---- Totemkeeper Ungar Ashbrow
    A(Q("az_the_ursolan_totems", "The Ursolan Totems", UNGAR, 53, 53, "Ursolan",
        "The totems along the Ursolan pass mark the Timbermaw's road, and Totemkeeper Ungar says one of them has "
        "gone quiet. He wants someone to walk the pass and see which one.",
        [explore(62, 24, "Walk the totems on the Ursolan pass", WA, radius=9)],
        "The pass runs down from the Hold's gate into West Azshara. Walk it to the bottom. The quiet one will feel "
        "cold when you pass it.",
        "The lowest one, by the road. Rot in the wood, all the way up.\n\nThe rot's reached the pass. I'll carve a "
        "new one, and I'll carve it from heartwood.", zone=TH))
    A(Q("az_satyrs_at_haldarr", "Satyrs at Haldarr", UNGAR, 54, 54, "Totemguard",
        "Haldarr's satyrs knock down every Timbermaw totem they find, and Ungar has carved enough replacements. He'd "
        "rather the satyrs stopped.",
        [k("Haldarr Trickster", 8, WA)],
        "The Haldarr Tricksters run the encampment's curses, and they love knocking totems over. Show them how it "
        "feels to be knocked over.",
        "The totems on the south road are still standing. That's the first time in a month.", zone=TH,
        nxt="az_haldarr_the_hornlord"))
    A(Q("az_haldarr_the_hornlord", "Haldarr the Hornlord", UNGAR, 56, 56, "Hornlord's",
        "The satyrs' lord, Haldarr, lives in the hollow at the top of the den under his encampment, and every satyr "
        "in West Azshara answers to him. Ungar says it ends with him.",
        [boss("Haldarr the Hornlord", HD)],
        "Haldarr Den's under the encampment in the south-east of West Azshara. Climb the taproot to his hollow. "
        "He'll pin you to the tree if you let him.",
        "The Hornlord's dead. The Haldarr will scatter without him, and the rot will slow.\n\nI'll carve a totem "
        "for the day. A small one, with a broken horn.", zone=TH))

    # ---- Envoy Grashak Stonetusk (Orgrimmar's man in the Hold)
    A(Q("az_orgrimmars_hand", "Orgrimmar's Hand", GRASHAK, 54, 54, "Envoy's",
        "Envoy Grashak says the Hold and the Landing ought to be talking, and they aren't, because the elves don't "
        "come up the mountain and the furbolgs don't go down it. He has a letter for Overseer Durgash. Grashak's been the Warchief's man in the Hold for three years, since the tunnel opened.",
        [deliver("az_q_grashak_letter", "Bring Grashak's letter to Overseer Durgash in Talrendis Landing")],
        "Take it down to the Landing. Durgash is on the high ground, watching the dig. Tell him the furbolgs are "
        "worth knowing, and they're better neighbours than the elves.",
        "Grashak thinks the furbolgs know something about the dig. He's never wrong about who knows what.\n\nI'll "
        "write back, slowly, the way furbolgs like it.", zone=TH, turn_in_npc_id=DURGASH,
        grant_items=carry("az_q_grashak_letter", "Grashak's Letter", "A letter from the Hold's envoy, smelling of "
                                                                     "honey and woodsmoke.")))
    A(Q("az_boars_for_the_hold", "Boars for the Hold", GRASHAK, 53, 53, "Huntsman",
        "The furbolgs eat honey, roots and fish, and Grashak hasn't had a proper piece of meat in a month. The "
        "russet boars in the forest are calling to him.",
        [fetch("az_q_boar_haunch", 6)],
        "The Russet Boars root all over West Azshara's woods. Bring me the haunches and I'll roast them where the "
        "furbolgs can't see.",
        "Now that's food. Don't tell the Elder.", zone=TH))

    # ---- Tunnelwarden Burrfoot
    A(Q("az_word_down_the_tunnel", "Word Down the Tunnel", BURRFOOT, 55, 55, "Tunnelward",
        "The Timbermaw in the tunnel above Felwood need to know about the rot under the Hold, because the Deadwood "
        "drank the same thing. Tunnelwarden Burrfoot wants word taken to Pathfinder Grosk. The tunnel's far mouths came down the day the world changed, and the Felwood one's the only one still open.",
        [deliver("az_q_burrfoot_warning", "Bring Burrfoot's warning to Pathfinder Grosk in the Timbermaw Tunnel")],
        "Out the Hold's west door and along the East Passage into the tunnel. Grosk's in the Lower Galleries, "
        "watching Felpaw. Tell him it's the same rot.",
        "The same rot. Under the Hold.\n\nThen the Deadwood weren't unlucky. Something fed it to them. I'll warn "
        "the tunnel.", zone=TH, turn_in_npc_id=GROSK,
        grant_items=carry("az_q_burrfoot_warning", "Burrfoot's Warning", "A strip of bark with a warning carved in "
                                                                         "Timbermaw marks, the kind you carve fast.")))

    # ---- Elder Haldor Mossmane
    A(Q("az_open_the_deep_gate", "Open the Deep Gate", ELDER, 55, 56, "Elder's",
        "The Elder has decided. The deep gate in the Hold's floor was sealed to keep the rot out, and now the rot's "
        "coming anyway. He'll open it, and he wants someone to go down first.\n\nThe first thing waiting below is Old "
        "Mossjaw, the Hold's own chieftain, the first the rot took.",
        [boss("Old Mossjaw", RD)],
        "The deep gate's in the basin floor. The wardens will open it for you. Mossjaw lies on his bier at the end "
        "of the burial halls. Put him to rest. He was a good chieftain.",
        "Mossjaw's at rest. He'd have wanted it done by someone who didn't flinch.\n\nYou'll have to go deeper. "
        "Grothar knows what's down there.", zone=TH, requires_quests=["az_tell_the_elder"]))
    A(Q("az_xavras_the_gloomtender", "Xavras the Gloomtender", ELDER, 58, 58, "Gloomtender's",
        "At the bottom of the deeps, on an island in the fel lake, is the satyr who planted the rot: Xavras the "
        "Gloomtender. Everything the Hold has lost started with her.",
        [boss("Xavras the Gloomtender", RD)],
        "She's at the bottom, on her throne island in the Gloomhollow. One causeway out to her. She'll call her "
        "satyrs, and at the end she'll bring the rot up out of the lake. Don't be standing in it.",
        "Xavras is dead, and the lake's going quiet.\n\nThe Hold will be talking about this for a hundred years. "
        "We'll be talking about you.", zone=TH, requires_quests=["az_thornblight"]))
    A(Q("az_what_the_satyrs_were", "What the Satyrs Were", ELDER, 57, 57, "Elder's",
        "The Elder says the furbolgs remember what the elves forget: the satyrs were Highborne once, Azshara's own "
        "court, before they gave themselves to the Legion. The rot is their magic gone bad. He wants the Conclave "
        "to hear it, from him.",
        [deliver("az_q_elder_word", "Bring the Elder's word to Magister Caelin Brightspire in Talrendis Landing")],
        "Take this to the Conclave's archivist at the Landing. He'll want to argue. Let him read it first.",
        "The satyrs were Highborne. We knew that, of course. We didn't want to know it.\n\nAnd if the rot is "
        "Highborne magic, then it's ours, and it's under our dig.", zone=TH, turn_in_npc_id=CAELIN,
        nxt="az_what_our_ancestors_did", requires_quests=["az_open_the_deep_gate"],
        grant_items=carry("az_q_elder_word", "The Elder's Word", "A carved bark tablet in Timbermaw marks, with a "
                                                                 "Common translation in Ingrid's hand.")))
    A(Q("az_echo_of_the_queen", "Echo of the Queen", ELDER, 60, 60, "Queen's",
        "At the bottom of the Drowned Palace, in front of an empty throne, something made of moonlight and water "
        "is waiting in the queen's shape. The Elder and the Overseer agree on one thing: whatever's in the vault, "
        "nobody gets it. Not Orgrimmar, not the Conclave.\n\nThe Echo of the Queen has to go.",
        [boss("Echo of the Queen", DV)],
        "Through the palace and down into the Queen's Vault, past the well, to the throne room. She'll call her "
        "court, and then the sea. Go with everyone you trust.",
        "It's done, and the vault's sealed, by the Hold and the Landing both.\n\nThe Conclave will grumble, Orgrimmar "
        "will grumble, and the coast will sleep. That's a good bargain.", zone=TH,
        requires_quests=["az_the_tidelord", "az_xavras_the_gloomtender"]))

    # ---- Deepwarden Grothar
    A(Q("az_down_the_deep_gate", "Down the Deep Gate", GROTHAR, 55, 56, "Deepwarden's",
        "Deepwarden Grothar has stood on the deep gate for three years listening to the Hold's dead walk around "
        "under it. Now it's open, and he wants them quiet.",
        [k("Rotroot Furbolg", 10, RD)],
        "Down the gate stair into the burial halls. The Rotroot Furbolgs were our people. Put them down, and don't "
        "hate them for what they've become.",
        "The halls are quiet. I'll sleep on the gate tonight, and I think I'll actually sleep.", zone=TH,
        requires_quests=["az_open_the_deep_gate"]))
    A(Q("az_mother_sporeheart", "Mother Sporeheart", GROTHAR, 56, 56, "Sporebane",
        "Past the burial halls the floor has gone to fungus, and the thing that grows it sits on an island in the "
        "middle: Mother Sporeheart. Grothar says the spores in the spring come from her.",
        [boss("Mother Sporeheart", RD)],
        "She's on the big island in the Sporegarden, past the first slope. She'll seed the air and feed on her "
        "garden. Kill the clouds she makes, then kill her.",
        "The spores in the spring stopped this morning. Lessa cried, and she'll tell you she didn't.", zone=TH,
        requires_quests=["az_open_the_deep_gate"]))
    A(Q("az_rotwarden_kazthul", "Rotwarden Kaz'thul", GROTHAR, 57, 57, "Wardenbreaker",
        "The satyrs keep cages down there, a long hall of them, and the one with the keys is Rotwarden Kaz'thul. "
        "Grothar has heard the cages from the gate, and some of what's in them used to be furbolg.",
        [boss("Rotwarden Kaz'thul", RD)],
        "The Warden's Gauntlet is the long hall of cages past the Sporegarden. Kaz'thul's at the far end. He'll "
        "cage you, and then he'll open the other cages.",
        "The cages are open and nothing's coming out of them anymore. That's a mercy.", zone=TH,
        requires_quests=["az_open_the_deep_gate"]))
    A(Q("az_thornblight", "Thornblight", GROTHAR, 57, 58, "Rootbreaker",
        "Under the cages is the cathedral the roots made, and Grothar says the roots are the Hold's own. They grew "
        "down into the rot and came back as Thornblight, and Thornblight is holding the whole hall up.",
        [boss("Thornblight", RD)],
        "Down past the gauntlet into the Root Cathedral. The floor's a fel lake, and the roots are the only bridges. "
        "Thornblight's on the middle knot. When it's dying, it'll try to bring the roof down.",
        "The roots are dead, and the Hold's still standing. I didn't know which way that would go.", zone=TH,
        requires_quests=["az_rotwarden_kazthul"]))

    # ---- Deepwarden Ulma
    A(Q("az_the_rotroot_mystics", "The Rotroot Mystics", ULMA, 56, 56, "Mystic's",
        "Deepwarden Ulma says the Hold's own shamans went down after the rot years ago and never came up. The "
        "Rotroot Mystics in the deeps heal the rot like they used to heal the Hold.",
        [k("Rotroot Mystic", 8, RD)],
        "The Rotroot Mystics walk the burial halls and the Sporegarden. They'll heal the others, so kill them "
        "first.",
        "My teacher was one of them. I hope it was you who found her.", zone=TH,
        requires_quests=["az_open_the_deep_gate"]))
    A(Q("az_the_rot_tenders", "The Rot-Tenders", ULMA, 57, 57, "Tenderbane",
        "The satyrs who tend the rot keep it fed, and Ulma wants every Satyr Rot-Tender in the deeps dead before "
        "the Hold goes down to the lake.",
        [k("Satyr Rot-Tender", 8, RD)],
        "The Satyr Rot-Tenders work the gauntlet and the cathedral. They heal each other, so don't let them stand "
        "together.",
        "Nobody's feeding it now, so it'll starve.", zone=TH, requires_quests=["az_open_the_deep_gate"]))

    # ======================================================================== ELDARATH, and the palace's knight
    A(Q("az_what_our_ancestors_did", "What Our Ancestors Did", CAELIN, 58, 58, "Confession",
        "Magister Brightspire has read the Chamberlain's ledger and the Elder's word, and they say the same thing: "
        "the rot is Highborne magic, and the satyrs are what the court became. The Conclave has to say so to the "
        "Hold.\n\nHe wants it said by someone who isn't an elf.",
        [deliver("az_q_conclave_answer", "Bring the Conclave's answer to Elder Haldor Mossmane in Timbermaw Hold")],
        "Take it up to the Hold. The Grand Magister wrote it herself. It isn't an apology. We'd need a longer "
        "page for that.",
        "The Conclave admits it. Their ancestors made the satyrs, and the satyrs made the rot.\n\nThat's more "
        "honest than I expected. The Hold will remember that, too.", zone=TL, turn_in_npc_id=ELDER,
        grant_items=carry("az_q_conclave_answer", "The Conclave's Answer", "A letter in the Grand Magister's own hand, "
                                                                           "sealed with a sun over a line of sea.")))
    A(Q("az_the_moonguard_revenant", "The Moonguard Revenant", SALEH, 60, 60, "Moonguard",
        "Layla Saleh's brother Mohammed dreams of a knight under the sea whose spirit won't rest, and Farseer Thrag says the "
        "dream's true. The knight swore an oath to a queen who isn't coming back. The Moonguard Revenant holds the processional in the Queen's Vault.",
        [boss("The Moonguard Revenant", DV)],
        "Down the flooded stair into the Queen's Vault. The Revenant's at the end of the processional. It'll put "
        "up its shield and then it'll charge. Let it go.",
        "It's resting at last. The spirits on this coast are fewer tonight, and quieter.", zone=TL,
        requires_quests=["az_the_tidelord"]))
    return out
