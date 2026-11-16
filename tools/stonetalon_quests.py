"""
Stonetalon: Stonetalon East, Sun Rock Retreat, Stonetalon West, Mistwalker Camp, Windshear Mine, the Ashvent and
the Eldest Sequoia. Levels 26-33. Read by tools/build_stonetalon_quests.py, which holds them to the Felwood and
Tempest Isle rules before anything is written.

WHAT STONETALON IS ABOUT (docs/stonetalon_brief.md). A piece of the Pacific Northwest came through in the
Integration and set itself down on the mountain: a volcano that blew the eastern forest flat, and redwoods and
sequoias in the west that nothing in Azeroth ever grew. Sun Rock took in Thunder Bluff's survivors when the
bluffs fell, and from its towers you can watch Mulgore, where the daylight stops. The Venture Co. is logging
the giants, the Grimtotem think Sun Rock is ripe, the Windshear harpies own the crag, and something on the
Mulgore side is getting the dead back on their feet.

  IN (2)          Sergra at the Crossroads and Overseer Gorada at Splintertree send people west.
  SUN ROCK (32)   The hold's own (the elder, the spiritwalker, the watch, the refugees), the three envoys
                  (Orgrimmar, the Cartel, the Forsaken), a transplant geologist, and the trainers.
  MISTWALKER (14) The camp in the redwoods: a Mistwalker, a transplant tree climber, a goblin who quit the
                  Venture Co., and a Forsaken alchemist who stands downwind.
  CAVES (4)       Windshear Mine and the Ashvent, given in Sun Rock and at the camp.
  DUNGEON (4)     The Eldest Sequoia, given in Sun Rock, never inside.
  OUT (3)         To Camp Taurajo in the Barrens, Splintertree in Ashenvale and the Aspen Wilderness, and an
                  answer back from each. All three answers open the Rim's last quest (Kyle: Linken's Sword).
  EAST (6)        Across the sea to the Eastern Kingdoms and back: the Rim samples to Hammerfall in Arathi,
                  the stolen blasting caps to the Cartel's factor in Booty Bay, and the volcano's ash to Brill.
                  The Booty Bay answer is what opens Yard Boss Krizzle.

Reputation goes by who gives the quest (Kyle, 15 Nov 2026: "Depending on quest giver. Thunder bluff,
steamwheedle, and orgrimmar. Maybe one or two forsaken."): Thunder Bluff by default, the envoys' and the camp's
goblin and Forsaken by name (tools/build_stonetalon_quests.FACTION_BY_GIVER).

VOICE (Kyle): whole sentences the way a person says them, contractions, the useful thing first, no dashes, no
counts beside an objective word, every kill target named. Earth comes up about a quarter of the time, from the
people who came from there.
"""
from tools.build_durotar_quests import kill, fetch  # noqa: F401

SE, SW, SR = "stonetalon_east", "stonetalon_west", "sun_rock_retreat"
# the key the game passes on a kill: the map name lowercased, spaces to underscores, apostrophes gone, "The" kept
WM, AV, ES, EC = "windshear_mine", "the_ashvent", "the_eldest_sequoia", "the_eldests_crown"
XR, ST, CT, AW = "crossroads", "splintertree_post", "camp_taurajo", "the_aspen_wilderness"
# the Eastern Kingdoms (Kyle, 15 Nov 2026: "Get some chains from eastern kingdom too bro. dont limit it")
HF, BB, BR = "hammerfall", "booty_bay", "brill"

# ---- the people
ELDER, TOHANA, AHROK, KUNA = "sr_elder", "sr_spirit_walker", "sr_watch_captain", "sr_rim_watcher"
HALONA, TAVO, GARNAK, PIXIE = "sr_refugee_mother", "sr_refugee_hunter", "sr_orgrimmar_envoy", "sr_steamwheedle_agent"
MERROW, HANNAH, KAUWA = "sr_forsaken_apothecary", "sr_transplant_geologist", "sr_innkeeper"
BRAK, OHANZEE, NAWA, KESH = "pt_sun_rock_forge", "pt_sun_rock_hide", "pt_sun_rock_herbs", "pt_sun_rock_wood"
IYANA, TAMSIN, NOZZLE, RENNICK = "mw_camp_leader", "mw_arborist", "mw_ex_venture", "mw_forsaken_chem"
SERGRA, GORADA, LONGTREAD, NALU = "crossroads_sergra", "splintertree_commander", "taurajo_elder", "asp_lift_keeper"
VOSS, WEEZEL, GRAEL = "hammerfall_apothecary", "bootybay_cartel_factor", "brill_apothecary_asst"

HUB_GIVERS = {ELDER, TOHANA, AHROK, KUNA, HALONA, TAVO, GARNAK, PIXIE, MERROW, HANNAH, KAUWA, BRAK, OHANZEE,
              NAWA, KESH, IYANA, TAMSIN, NOZZLE, RENNICK}


def k(target, n, zone):
    return kill(target, n, zone=zone)


def boss(target, zone):
    return {"type": "kill_boss", "target": target, "count": 1, "zone": zone}


def explore(x, y, label, zone, radius=7):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius, label=label)


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def gather(mat, n, label):
    return dict(type="gather", target=mat, count=n, label=label)


def craft(recipe, n, label):
    return dict(type="craft", target=recipe, count=n, label=label)


def carry(item_id, name, desc):
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=1)]}


#: creature -> [(item_id, name, description[, chance])], three in four unless a chance is given
FETCH_DROPS = {
    "Grey Elk": [("st_q_elk_hide", "Grey Elk Hide", "A heavy grey hide with ash worked deep into the fur.")],
    "Bull Elk": [("st_q_elk_hide", "Grey Elk Hide", "A heavy grey hide with ash worked deep into the fur."),
                 ("st_q_grove_venison", "Grove Venison", "A good cut of elk, dark and lean, wrapped in fern.")],
    "Ash Drifter": [("st_q_ash_core", "Ash Core", "A fist of ash packed so hard it rings like stone. It's still warm "
                                                  "in the middle.")],
    "Windshear Wind Witch": [("st_q_wind_fetish", "Wind Fetish", "Feathers and bone bound with hair. When you hold "
                                                                 "it up, it pulls toward the crag.")],
    "Venture Co. Blaster": [("st_q_blasting_cap", "Venture Blasting Cap", "A brass cap packed with something that "
                                                                          "smells like a struck match. Hold it gently.")],
    "Risen Tauren": [("st_q_rim_tissue", "Sealed Sample Jar", "A jar with a waxed lid. Whatever's inside it is "
                                                              "still moving a little.")],
    "Risen Stalker": [("st_q_rim_tissue", "Sealed Sample Jar", "A jar with a waxed lid. Whatever's inside it is "
                                                               "still moving a little.")],
    "Ridge Cougar": [("st_q_cougar_flank", "Cougar Flank", "Tough, stringy meat that needs a long time in a pot.")],
    "Black Bear": [("st_q_bear_hide", "Thick Bear Hide", "A black bear's hide, heavy as a blanket and twice as warm.")],
    "Greatwood Bear": [("st_q_bear_hide", "Thick Bear Hide", "A black bear's hide, heavy as a blanket and twice as "
                                                             "warm.")],
    "Venture Co. Shredder": [("st_q_shredder_gear", "Shredder Drive Gear", "A toothed gear as wide as a dinner "
                                                                           "plate, with sawdust packed in the teeth.")],
    "Crater Ash Wraith": [("st_q_wraith_ash", "Wraith Ash", "Grey ash that drifts back toward the crater when you "
                                                            "open the pouch.")],
    "Living Sap": [("st_q_eldest_amber", "Eldest's Amber", "A lump of fresh amber from inside the Eldest Sequoia. "
                                                           "There's light in it that isn't from outside.")],
}

#: monster-drop quest starters: creature -> [(item_id, name, description, chance)]
STARTER_DROPS = {
    "Grimtotem Firecaller": [("st_q_charred_orders", "Charred Grimtotem Orders", "A strip of hide with orders "
                              "burned into it in Grimtotem script. Somebody important wanted this read and then "
                              "burned.", 0.08)],
    "Venture Co. Cut Foreman": [("st_q_work_order", "Venture Co. Work Order", "A folded work order on Venture "
                                 "Co. paper, stamped urgent three times. The tree it names is the biggest one on "
                                 "the mountain.", 0.25)],
}
STARTER_DROPS["Risen Stalker"] = [("st_q_bloodhoof_charm", "Bloodhoof Hunting Charm", "A hunter's charm of "
                                  "braided hide and a carved bead, the kind Bloodhoof hunters wore. It's warm, "
                                  "which it shouldn't be.", 0.10)]
STARTER_IDS = {"st_q_charred_orders": "st_orders_in_ash", "st_q_work_order": "st_the_work_order",
               "st_q_bloodhoof_charm": "st_a_name_on_the_post"}

#: per quest: [(slot, kind, type, identity)]: the rewards, authored in tools/build_stonetalon_quests.py
#: from the crafted-gear identities and checked against all 97 specs.
#: kinds: "armor" (type = cloth/leather/mail/plate, or None for a ring, neck, back or trinket), "weapon".


def Q(qid, title, giver, lo, hi, prefix, desc, objs, accept, done, rewards, nxt=None, zone=SR, **engine):
    q = dict(quest_id=qid, title=title, giver_npc_id=giver, zone=zone, level_min=lo, level_max=hi,
             description=desc, objectives=objs, accept_text=accept, turn_in_text=done, next_quest_id=nxt,
             _prefix=prefix, _rewards=rewards)
    q.update({kk: vv for kk, vv in engine.items() if vv})
    return q


def build():
    out = []
    A = out.append

    # ======================================================================================== IN
    A(Q("st_road_west", "The Road West", SERGRA, 26, 26, "Crossroads",
        "Sergra Darkthorn has a dispatch for Orgrimmar's envoy at Sun Rock Retreat, in Stonetalon. The road runs "
        "west out of the Barrens' Dry Hills and up into the mountains.\n\nShe doesn't trust the Grimtotem with "
        "it, she doesn't trust the harpies with it, and she says she doesn't trust you much either, but you're "
        "the one standing in front of her.",
        [deliver("st_q_sergra_dispatch", "Bring the dispatch to Envoy Garnak at Sun Rock Retreat")],
        "Take the road west out of the Dry Hills and keep climbing. Sun Rock's the hold on the mesa. Don't stop "
        "to admire the view, the harpies like people who do.",
        "That's Sergra's seal, so she's still alive, then.\n\nShe wants to know if Sun Rock will hold. Stay a while "
        "and you'll be able to tell her yourself.",
        [("chest", "armor", "mail", "hunter"), ("waist", "armor", "cloth", "caster"),
         ("feet", "armor", "plate", "tank")],
        zone=XR, turn_in_npc_id=GARNAK,
        grant_items=carry("st_q_sergra_dispatch", "Sealed Dispatch", "A dispatch with Sergra Darkthorn's seal. "
                                                                     "It's heavier than a letter should be.")))
    A(Q("st_talondeep", "Down the Talondeep", GORADA, 26, 26, "Splintertree",
        "Overseer Gorada wants a pair of eyes in Stonetalon. The Talondeep Path runs south out of Ashenvale, "
        "through the hill and down onto a mountainside that used to be forest.\n\nOrgrimmar's envoy at Sun "
        "Rock Retreat writes to her every week, and every week the letters are shorter. Go and find out why.",
        [deliver("st_q_gorada_letter", "Bring Gorada's letter to Envoy Garnak at Sun Rock Retreat")],
        "South down the Talondeep road, through the tunnel. When the trees stop, you're in Stonetalon. Sun Rock's "
        "the big mesa in the middle of the burn.",
        "Gorada thinks I've gone quiet, but I've just run out of good news to put in letters.\n\nYou're "
        "here now, though, and that's something.",
        [("hands", "armor", "leather", "agility"), ("shoulder", "armor", "mail", "tide_healer"),
         ("neck", "armor", None, "caster")],
        zone=ST, turn_in_npc_id=GARNAK,
        grant_items=carry("st_q_gorada_letter", "Gorada's Letter", "A short letter in Overseer Gorada's hand. "
                                                                   "Most of it is questions.")))

    # ================================================================================ SUN ROCK
    # ---- Elder Muhana Windhoof
    A(Q("st_hides_for_the_lodge", "Hides for the Lodge", ELDER, 26, 27, "Sun Rock",
        "Elder Muhana Windhoof has more people on Sun Rock than she has roofs. The refugees who got out when "
        "Thunder Bluff fell in the Integration sleep under the sky, and the wind off the Blowdown has started to bite at night.\n\nThe grey elk graze "
        "the burn, and the bull elk keep to the Standing Grove. Their hides make good tents.",
        [fetch("st_q_elk_hide", 8)],
        "The grey elk are all over the Blowdown below us, and the bull elk keep to the trees in the Standing Grove "
        "to the south-west. Bring the hides back to me and I'll see them stitched.",
        "These will keep a family dry. Thank you.\n\nIt's a small thing, a tent. It's still a long way better "
        "than nothing.",
        [("back", "armor", None, "physical"), ("wrist", "armor", "cloth", "healer"),
         ("legs", "armor", "plate", "strength")],
        nxt="st_word_to_taurajo"))
    A(Q("st_word_to_taurajo", "Word to Camp Taurajo", ELDER, 27, 27, "Sun Rock",
        "Elder Longtread at Camp Taurajo speaks for the tauren now, while nobody knows where Cairne is. Elder "
        "Muhana has written to him about the Rim, about the refugees, and about the dead that won't lie down "
        "on the Mulgore side.\n\nShe wants it put in his hand, and she wants to know what he says.",
        [deliver("st_q_muhana_letter", "Bring Muhana's letter to Elder Longtread at Camp Taurajo")],
        "Camp Taurajo's in the southern Barrens. The wind riders will take you most of the way. Don't let anyone "
        "else read it, and don't read it yourself.",
        "Muhana always did write the truth plainly. I'll answer her properly.",
        [("head", "armor", "leather", "bear"), ("ring", "armor", None, "healer"),
         ("hands", "armor", "mail", "earthen")],
        nxt="st_taurajo_answer", turn_in_npc_id=LONGTREAD,
        grant_items=carry("st_q_muhana_letter", "Muhana's Letter", "A thick letter tied with a strip of "
                                                                  "white hide, the way the elders mark serious news.")))
    A(Q("st_taurajo_answer", "Longtread's Answer", LONGTREAD, 27, 27, "Taurajo",
        "Elder Longtread has read Muhana's letter twice. He's written back, and he's asked you to carry it, "
        "because he'd rather it went with somebody who has seen Sun Rock.\n\nHe's also told you what he hasn't "
        "written down: that Taurajo can't send warriors, and that he's sorry.",
        [deliver("st_q_longtread_answer", "Bring Longtread's answer to Elder Muhana at Sun Rock Retreat")],
        "Take it to Muhana. Tell her I'd come myself if the camp could spare me, and tell her it can't.",
        "He can't send anyone. I didn't think he could.\n\nHe's sent his blessing, and he's told us to hold the "
        "Rim. We'll hold it. Kuna will want to hear this too.",
        [("chest", "armor", "cloth", "high_healer"), ("main_hand", "weapon", "axe_1h", "strength"),
         ("feet", "armor", "leather", "agility")],
        zone=CT, turn_in_npc_id=ELDER,
        grant_items=carry("st_q_longtread_answer", "Longtread's Answer", "A reply in Elder Longtread's careful "
                                                                         "hand, sealed with clay.")))

    # ---- Spiritwalker Tohana
    A(Q("st_ash_that_walks", "Ash That Walks", TOHANA, 26, 27, "Spirit-Bound",
        "The forest on the Blowdown came through with the mountain three years ago, and it didn't burn. It was knocked flat in one breath and buried in ash, and the "
        "spirits of it never had time to leave. Now the Ash Drifters walk the burn, and Spiritwalker Tohana says "
        "they're what's left of the trees trying to remember what they were.\n\nHe wants them put to rest.",
        [k("Ash Drifter", 10, SE)],
        "The ash drifters walk the open burn north and west of here. You'll see them as a grey shape that moves "
        "against the wind. Be gentle if you can, and quick if you can't.",
        "The burn's quieter. I can hear the wind on it again, and nothing else.\n\nThank you. They didn't ask "
        "for what happened to them.",
        [("staff", "weapon", "staff", "spirit_healer"), ("chest", "armor", "leather", "feral"),
         ("waist", "armor", "mail", "mail_caster")],
        nxt="st_old_greyhide"))
    A(Q("st_old_greyhide", "Old Greyhide", TOHANA, 27, 28, "Spirit-Bound",
        "There's an elk on the Blowdown that should have died when the mountain blew. Old Greyhide was standing "
        "in the blast and walked out of it, and he hasn't been right since. He leads the grey elk in circles "
        "round the place the forest used to be.\n\nTohana says the herd won't scatter while he's alive, and "
        "the herd needs to scatter.",
        [boss("Old Greyhide", SE)],
        "He's huge and he's grey all over, ash in his coat right down to the skin. Look for him in the middle of "
        "the Blowdown with the herd round him.",
        "The herd's scattering already. They'll find new grazing now, away from the worst of the ash.\n\nHe was "
        "an old soul. I hope he's somewhere green.",
        [("main_hand", "weapon", "polearm", "physical"), ("shoulder", "armor", "plate", "plate_healer"),
         ("head", "armor", "cloth", "arcane"), ("off_hand", "weapon", "shield", "shield_tank")]))
    A(Q("st_rot_in_the_heartwood", "Rot in the Heartwood", TOHANA, 30, 32, "Heartwood",
        "The Eldest Sequoia is the greatest tree on Stonetalon, and Spiritwalker Tohana says it's dying from "
        "the inside. The Venture Co. bored into it to tap its sap, and the heartrot beetles followed them in. "
        "Their queen is eating the tree's heart.\n\nThe Eldest stands on the slopes of Stonetalon West, and you "
        "go in at its foot and climb.",
        [boss("The Heartrot Queen", ES)],
        "Go into the Eldest Sequoia, from the door at its foot in Stonetalon West. The Heartrot Queen nests in "
        "the galleries the beetles chewed, and she won't come out to you. Take friends with you. A lot of them.",
        "I felt it go. The tree took a breath, I swear it did.\n\nThe heart can heal now. It'll take longer than "
        "either of us will be alive, but it can heal.",
        [("chest", "armor", "mail", "hunter"), ("legs", "armor", "cloth", "caster_crit"),
         ("main_hand", "weapon", "mace_1h", "high_healer"), ("hands", "armor", "plate", "tank")],
        nxt="st_rest_for_the_eldest"))
    A(Q("st_rest_for_the_eldest", "Rest for the Eldest", TOHANA, 32, 33, "Heartwood",
        "The heart's clean, but the Eldest's spirit isn't at peace. Tohana has been listening at the foot of "
        "the tree for three nights, and what he hears from the crown is rage. The spirit has been bored and "
        "tapped and climbed on for so long that it's lashing out at anything that moves.\n\nHe wants you to "
        "climb to the crown and give it rest. The tree will go on standing. The spirit just needs to sleep.",
        [boss("The Eldest", EC)],
        "Climb the trunk and out onto the crown. The Eldest waits at the very top. Bring your best people, and "
        "don't look down for long.",
        "It's asleep, and for the first time in years the whole mountain is quiet at once.\n\nI'll go up there "
        "myself in the spring and tell it what you did. I think it would want to know.",
        [("staff", "weapon", "staff", "caster_crit"), ("chest", "armor", "leather", "bear"),
         ("head", "armor", "plate", "strength_crit"), ("shoulder", "armor", "mail", "tide_healer")],
        elite=True))

    # ---- Watch Captain Ahrok Stonemane
    A(Q("st_harpies_on_the_crag", "Harpies on the Crag", AHROK, 27, 28, "Watch-Hall",
        "The Windshear harpies have nested on the crag north of the Blowdown for as long as anyone can remember. "
        "Since the mountain blew they've been coming down to Sun Rock's supply lines and taking whatever they "
        "can carry.\n\nWatch Captain Ahrok Stonemane wants every Windshear Harpy and Windshear Talon pushed back "
        "up the crag where they belong.",
        [k("Windshear Harpy", 8, SE), k("Windshear Talon", 5, SE)],
        "Windshear Crag's the high ground north-east of here, past the Blowdown. The talons are the bigger ones "
        "with the hooked claws, so kill those first if you can.",
        "The supply runs got through untouched yesterday. First time this month.\n\nThey'll be back. They always "
        "are. For now, though, it's quieter.",
        [("ranged", "weapon", "bow", "hunter_crit"), ("feet", "armor", "cloth", "haste_caster"),
         ("chest", "armor", "plate", "tank_any")],
        nxt="st_wind_witch_fetishes"))
    A(Q("st_wind_witch_fetishes", "What the Wind Witches Carry", AHROK, 28, 28, "Watch-Hall",
        "The wind witches are what keep the harpies coming. Ahrok has watched them through his glass: before "
        "every raid they hold up little bundles of feather and bone, and the wind turns their way.\n\nHe wants "
        "those fetishes, so Spiritwalker Tohana can find out what they do and how to stop it.",
        [fetch("st_q_wind_fetish", 6)],
        "The Windshear wind witches stay up near the top of the crag. Bring me what they carry. Don't hold the "
        "fetishes up into the wind yourself, whatever you do.",
        "Tohana says they call the wind down off the peak. Without them, the harpies have to fly against it "
        "like everyone else.\n\nAnd there's one witch who makes them for the rest.",
        [("neck", "armor", None, "caster_crit"), ("legs", "armor", "leather", "rogue_crit"),
         ("wrist", "armor", "mail", "earthen")],
        nxt="st_matron_shrieka"))
    A(Q("st_matron_shrieka", "Matron Shrieka", AHROK, 28, 29, "Watch-Hall",
        "Matron Shrieka is the oldest of the Windshear wind witches. She makes every fetish on the crag, and she "
        "sends every raid down onto the road.\n\nAhrok wants her gone for good, not just driven off.",
        [boss("Matron Shrieka", SE)],
        "She keeps the highest nest on Windshear Crag. You'll hear her before you see her. Take friends and "
        "plug your ears if you can.",
        "That's the end of the raids for a season, maybe longer.\n\nYou've done Sun Rock a real service. "
        "Pick something from the armoury.",
        [("main_hand", "weapon", "dagger", "assassin"), ("chest", "armor", "cloth", "precise_caster"),
         ("hands", "armor", "plate", "crusader"), ("off_hand", "weapon", "shield", "haste_caster")]))
    A(Q("st_the_grimtotem_line", "The Grimtotem Line", AHROK, 28, 29, "Watch-Hall",
        "The Grimtotem have built a compound south of the Blowdown, closer to Sun Rock every month. Ahrok says "
        "they're testing the hold, sending Grimtotem Raider bands and Grimtotem Spearhunter packs out to see how far they can get before the "
        "watch notices.\n\nHe wants them to learn that the watch always notices.",
        [k("Grimtotem Raider", 8, SE), k("Grimtotem Spearhunter", 6, SE)],
        "The compound's to the south, past the Standing Grove. The raiders and spearhunters patrol the ground "
        "round it. Hit them there, before they reach the road.",
        "They pulled their patrols back last night, so they're thinking about it now.\n\nGood, let them think.",
        [("main_hand", "weapon", "mace_2h", "strength"), ("shoulder", "armor", "leather", "strength"),
         ("hands", "armor", "cloth", "spirit_caster")]))

    # ---- Kuna Ashhorn, the Rim
    A(Q("st_carrion_from_the_rim", "Carrion from the Rim", KUNA, 28, 28, "Rim-Watch",
        "Kuna Ashhorn watches the Mulgore Rim from the south-east tower. She says the carrion birds that roost "
        "on the Rim fly into Mulgore at night and come back in the morning, and what they carry back in their "
        "beaks shouldn't be carried anywhere.\n\nShe wants every Rim Carrion Bird dead before it drops what it carries on Sun Rock.",
        [k("Rim Carrion Bird", 8, SE)],
        "The Mulgore Rim is in the south-east corner of Stonetalon, where the light goes strange. The carrion "
        "birds roost on the dead trees along the edge. Don't stand under them.",
        "The sky's clear over the Rim this morning, and that's rare.\n\nI've seen what they bring back. I'm glad you "
        "didn't have to.",
        [("back", "armor", None, "caster"), ("legs", "armor", "mail", "hunter_precise"),
         ("feet", "armor", "plate", "tank")],
        nxt="st_what_walks_the_rim"))
    A(Q("st_what_walks_the_rim", "What Walks the Rim", KUNA, 28, 29, "Rim-Watch",
        "Every night more of them stand on the Rim and look toward Sun Rock. They were tauren once. Some of them "
        "were people Kuna knew. Something in Mulgore killed them, and then got them back up again, and now "
        "they hunt along the edge of the dark.\n\nKuna wants the Risen Tauren and the Risen Stalker hunters cut down "
        "and the Rim looked at properly, from the overlook at the end.",
        [k("Risen Tauren", 8, SE), k("Risen Stalker", 5, SE),
         explore(176, 164, "Look into Mulgore from the Rim overlook", SE)],
        "The risen walk the Mulgore Rim. The overlook is at the far end, where the ground drops away into the "
        "dark. Look, then come back and tell me what you saw. Don't stay too long.",
        "You looked, so now you know.\n\nI used to think Mulgore would come back one day. I don't think that now. "
        "We just have to make sure the dark stays on its side of the Rim.",
        [("main_hand", "weapon", "sword_2h", "strength_hit"), ("chest", "armor", "cloth", "holy"),
         ("waist", "armor", "leather", "agility"), ("hands", "armor", "mail", "tide_healer")],
        nxt="st_the_risen_hunter"))
    A(Q("st_the_risen_hunter", "The Risen Hunter", KUNA, 29, 29, "Rim-Watch",
        "There's one of the risen that leads the rest. Kuna knows him. He was a Bloodhoof hunter, the best "
        "tracker in Mulgore, and now he tracks for whatever is down there.\n\nShe wouldn't send you until she "
        "knew Sun Rock wasn't alone. Now Camp Taurajo, Splintertree and the Aspen have all answered, and she "
        "says it's time.",
        [boss("The Risen Hunter", SE)],
        "He hunts the Mulgore Rim with the risen behind him. He knows you're coming, he always does. Go "
        "together, and don't follow him into the dark past the Rim.",
        "Is he down, properly down?\n\nThen he can rest. I'll carve his name back on the hunters' post. He "
        "earned it a long time before this.",
        [("ranged", "weapon", "gun", "hunter"), ("chest", "armor", "plate", "plate_healer"),
         ("head", "armor", "leather", "feral"), ("main_hand", "weapon", "staff", "bear_weapon"),
         ("trinket", "armor", None, "caster")],
        elite=True, requires_quests=["st_taurajo_answer", "st_splintertree_answer", "st_aspen_answer"]))

    # ---- Halona Stillwater, the refugees
    A(Q("st_kingsblood_for_the_sick", "Kingsblood for the Sick", HALONA, 26, 27, "Refugee's",
        "Half the children on Sun Rock have a cough from the ash. Halona Stillwater knows an old Mulgore remedy "
        "that uses kingsblood, and kingsblood grows on Stonetalon if you know where to look.\n\nShe can't leave "
        "the camp. Somebody has to bring it to her.",
        [gather("herb_kingsblood", 6, "Kingsblood from Stonetalon's slopes")],
        "Kingsblood grows on the slopes all over Stonetalon. You'll need to know a bit of herbalism to pick it. "
        "If you don't, Nawa by the herb garden will teach you.",
        "That's enough for every child in the camp, and some for the grown-ups too.\n\nThank you. You've no "
        "idea how good it feels to hear them sleep through the night.",
        [("wrist", "armor", "leather", "physical"), ("neck", "armor", None, "spirit_healer"),
         ("shoulder", "armor", "plate", "tank_any")],
        nxt="st_letter_to_the_aspen"))
    A(Q("st_letter_to_the_aspen", "A Letter South", HALONA, 27, 27, "Refugee's",
        "Halona's brother left Thunder Bluff a different way when it fell, south toward the mountains. She heard "
        "he reached the Aspen Wilderness, where the Keeper of the old lift still waits for a cable that doesn't "
        "come back.\n\nShe's written him a letter. She doesn't know if he's alive. She wants it sent anyway.",
        [deliver("st_q_halona_letter", "Bring Halona's letter to Keeper Nalu Stillgrass in the Aspen Wilderness")],
        "The Aspen Wilderness is south, past the Barrens, where the mountains came through. Keeper Nalu "
        "Stillgrass keeps the old lift there. Ask her about a tauren named Hoka, and don't believe he's gone until you've asked.",
        "You're asking about Hoka? I know Hoka well. He's here, he's well, and he talks about his sister every "
        "day.\n\nPull up a seat. He'll want to write back, and he writes slowly.",
        [("head", "armor", "mail", "mail_caster"), ("feet", "armor", "leather", "bear"),
         ("ring", "armor", None, "strength")],
        nxt="st_aspen_answer", turn_in_npc_id=NALU,
        grant_items=carry("st_q_halona_letter", "Halona's Letter", "A letter folded small, with a lock of white "
                                                                  "hair tied round it.")))
    A(Q("st_aspen_answer", "Hoka's Answer", NALU, 28, 28, "Aspen-Born",
        "Hoka wrote three pages to his sister and then asked Keeper Nalu to add a fourth, saying the Aspen has "
        "room for anyone from Sun Rock who wants to come south, and that the Aspen's hunters will stand with Sun "
        "Rock if the Rim ever breaks.\n\nNalu wants it carried back by the same hand that brought the first one.",
        [deliver("st_q_hoka_answer", "Bring Hoka's answer to Halona Stillwater at Sun Rock Retreat")],
        "Take it back to Halona at Sun Rock, and tell her the Aspen meant what it wrote. Every word of it's true.",
        "He's alive, and he says he's fat and happy.\n\nI'll stay here, I think. Sun Rock's home "
        "now. But it's good to know there's somewhere else if it needs to be.",
        [("back", "armor", None, "agility"), ("legs", "armor", "cloth", "healer"),
         ("main_hand", "weapon", "mace_1h", "crusader")],
        zone=AW, turn_in_npc_id=HALONA,
        grant_items=carry("st_q_hoka_answer", "Hoka's Answer", "Four pages, the last in a different hand.")))

    # ---- Tavo Longrun, the hunter
    A(Q("st_meat_for_the_rock", "Meat for the Rock", TAVO, 26, 27, "Longrun",
        "Tavo Longrun hunted Mulgore his whole life. Now he hunts for a mesa full of people who lost everything, "
        "and there aren't enough hunters.\n\nThe bull elk in the Standing Grove are fat and the grove's thick "
        "enough to sneak up on them. He wants venison, and lots of it.",
        [fetch("st_q_grove_venison", 8)],
        "The Standing Grove's in the south-west, the trees the blast missed. The bull elk graze between them. "
        "Come in from downwind.",
        "That'll feed the camp for days. Kauwa will be pleased, and she's not easy to please.\n\nYou hunt like "
        "a tauren. That's the best thing I can say about anyone.",
        [("ranged", "weapon", "crossbow", "hunter_precise"), ("chest", "armor", "mail", "earthen"),
         ("head", "armor", "cloth", "frost")],
        nxt="st_cougars_in_the_grove"))
    A(Q("st_cougars_in_the_grove", "Cougars in the Grove", TAVO, 27, 28, "Longrun",
        "The ridge cougars have learned that Sun Rock's hunters bring meat home through the grove. Two of Tavo's "
        "people were jumped last week, and one of them won't walk right again.\n\nHe wants the cougars taught "
        "that the hunters bite back.",
        [k("Ridge Cougar", 8, SE)],
        "Every Ridge Cougar in the area hunts the Standing Grove and the rocks round it. They hunt from above, so "
        "look up before you look ahead. They'll be waiting.",
        "The trails are safe again, for now.\n\nThere's a big one I haven't seen yet, though. The others give "
        "way to him.",
        [("main_hand", "weapon", "sword_1h", "rogue_crit"), ("hands", "armor", "leather", "hunter"),
         ("chest", "armor", "plate", "strength")],
        nxt="st_broadpaw"))
    A(Q("st_broadpaw", "Broadpaw", TAVO, 28, 28, "Longrun",
        "Broadpaw is the black bear the Standing Grove belongs to. He's never bothered the hunters before, but "
        "the cougars have pushed him out of his den, and now he's taking out his temper on anybody in the "
        "trees.\n\nTavo says he's sorry for the bear. He also says the bear has to go.",
        [boss("Broadpaw", SE)],
        "He's deep in the Standing Grove, bigger than any bear you've seen, and he'll charge. Don't be where "
        "you were standing when he does.",
        "He was a fine animal, and I'll use every bit of him, the way we always did.\n\nTake this one. I made it before "
        "the bluffs fell, and I've been waiting for the right person.",
        [("main_hand", "weapon", "staff", "bear_weapon"), ("shoulder", "armor", "cloth", "caster"),
         ("legs", "armor", "mail", "hunter_crit"), ("wrist", "armor", "plate", "tank")]))

    # ---- Envoy Garnak, Orgrimmar
    A(Q("st_grimtotem_intent", "The Grimtotem's Intent", GARNAK, 28, 28, "Warsong",
        "Orgrimmar wants to know whether the Grimtotem mean to take Sun Rock or only to frighten it. Envoy "
        "Garnak wants the compound scouted from close enough to see what they're building, and he wants the "
        "Grimtotem Brute guards to know they've been seen.",
        [explore(80, 146, "Scout the Grimtotem Compound", SE), k("Grimtotem Brute", 5, SE)],
        "The compound's south of the Blowdown. Get close enough to see inside, and if the brutes come at you, "
        "make an example of them.",
        "They're building siege ladders.\n\nThen it's not a threat any more, it's a plan. I'll "
        "write to Orgrimmar tonight.",
        [("main_hand", "weapon", "axe_2h", "strength_crit"), ("chest", "armor", "leather", "agility"),
         ("feet", "armor", "mail", "mail_caster")],
        nxt="st_word_to_splintertree"))
    A(Q("st_orders_in_ash", "Orders in Ash", "item:st_q_charred_orders", 28, 29, "Warsong",
        "You took a strip of burned hide off a Grimtotem firecaller. There are orders on it in Grimtotem script, "
        "half burned away. Envoy Garnak at Sun Rock reads Grimtotem. He'll want to see this.\n\nWhat's still "
        "legible names the Grimtotem Firecaller and Grimtotem Mystic circles, and a date.",
        [k("Grimtotem Firecaller", 6, SE), k("Grimtotem Mystic", 6, SE)],
        "This is a call to fire the Blowdown again, round Sun Rock, when the wind's right. The firecallers and "
        "the mystics are meant to start it. Stop them before the wind turns.",
        "Burn the burn again, with Sun Rock in the middle of it. Clever, and very nearly worked.\n\nYou found "
        "this by luck and acted on it fast. Orgrimmar will hear about you.",
        [("staff", "weapon", "staff", "fire"), ("legs", "armor", "plate", "tank"),
         ("hands", "armor", "leather", "rogue_crit")],
        turn_in_npc_id=GARNAK, nxt="st_hargol_bloodhorn"))
    A(Q("st_hargol_bloodhorn", "Hargol Bloodhorn", GARNAK, 29, 29, "Warsong",
        "Hargol Bloodhorn leads the Grimtotem in Stonetalon. The fire was his idea, and so are the ladders. "
        "Garnak doesn't think there'll be a siege without him, and Orgrimmar has said it would rather there "
        "wasn't one.\n\nHe's asked you to make sure there isn't.",
        [boss("Hargol Bloodhorn", SE)],
        "He's in the middle of the Grimtotem Compound with his best people round him, so take yours.",
        "Without Hargol they'll argue about who's next for a month, and they won't climb any ladders while "
        "they're arguing.\n\nThat was well done, really well done.",
        [("main_hand", "weapon", "polearm", "strength_hit"), ("head", "armor", "mail", "hunter"),
         ("chest", "armor", "cloth", "shadow"), ("off_hand", "weapon", "shield", "shield_tank")]))
    A(Q("st_word_to_splintertree", "Word to Splintertree", GARNAK, 28, 28, "Warsong",
        "Garnak has written to Overseer Gorada at Splintertree Post about the ladders, the fire and Hargol. He "
        "doesn't trust a wind rider with it, because the harpies have been knocking them out of the sky.\n\n"
        "He wants it carried on foot, up the Talondeep Path to Ashenvale.",
        [deliver("st_q_garnak_report", "Bring Garnak's report to Overseer Gorada at Splintertree Post")],
        "North up the Talondeep Path and through the tunnel. Splintertree's the Horde post in Ashenvale. "
        "Gorada will be on the wall, she always is.",
        "Siege ladders, fire, and a Grimtotem chief who thought he could have Sun Rock. And Garnak sends it on "
        "foot.\n\nHe was right to. I'll answer him now.",
        [("ring", "armor", None, "physical"), ("waist", "armor", "plate", "plate_healer"),
         ("head", "armor", "leather", "wildheart")],
        nxt="st_splintertree_answer", turn_in_npc_id=GORADA,
        grant_items=carry("st_q_garnak_report", "Garnak's Report", "Three pages in Garnak's square hand, "
                                                                  "sealed with Orgrimmar's mark.")))
    A(Q("st_splintertree_answer", "Splintertree's Answer", GORADA, 28, 28, "Splintertree",
        "Overseer Gorada has written back to Garnak. Splintertree can't spare warriors, not with the demons in "
        "Ashenvale, but it can spare arrows and a promise, and she's sent both.\n\nShe wants the answer carried "
        "back down the Talondeep the way the report came.",
        [deliver("st_q_gorada_answer", "Bring Gorada's answer to Envoy Garnak at Sun Rock Retreat")],
        "Back down the Talondeep to Sun Rock. Tell Garnak the arrows follow on the next cart, and that I meant "
        "the promise. He'll know what I mean.",
        "Arrows and a promise. From Gorada, that's a lot.\n\nKuna will want to know that Ashenvale's answered. "
        "Go and tell her.",
        [("ranged", "weapon", "bow", "hunter_crit"), ("wrist", "armor", "cloth", "arcane_crit"),
         ("chest", "armor", "mail", "tide_healer")],
        zone=ST, turn_in_npc_id=GARNAK,
        grant_items=carry("st_q_gorada_answer", "Gorada's Answer", "A short letter, and a long list of what's "
                                                                  "coming on the next cart.")))

    # ---- Pixie Brightcog, the Cartel
    A(Q("st_the_salvage_yard", "The Salvage Yard", PIXIE, 27, 28, "Cartel",
        "Pixie Brightcog would like everybody to know the Steamwheedle Cartel has nothing to do with the Venture "
        "Co. The Venture Co. has set up a salvage yard in the middle of the Blowdown, stripping the dead forest "
        "for timber and selling it cheap. It's ruining prices and it's ruining the good name of goblins.\n\nShe "
        "also blames the newcomers, a bit. Before the Integration, nobody had heard of a whole forest just "
        "falling over.",
        [k("Venture Co. Salvager", 8, SE), k("Venture Co. Bucker", 6, SE)],
        "The salvage yard's in the middle of the Blowdown. You can't miss it, it's the only thing out there "
        "making noise. The Venture Co. Salvager crews and the Venture Co. Bucker crews do the cutting. Stop them cutting.",
        "Production's down at the yard. Prices on Redbark are up already.\n\nI'm not saying I'm happy about it. "
        "I'm just saying the numbers are better.",
        [("main_hand", "weapon", "sword_1h", "assassin"), ("legs", "armor", "plate", "strength"),
         ("head", "armor", "cloth", "caster")],
        nxt="st_blasting_caps"))
    A(Q("st_blasting_caps", "Blasting Caps", PIXIE, 28, 28, "Cartel",
        "The Venture Co. blasters are clearing the Blowdown with powder, and they're not careful about it. One "
        "of their charges shook the mesa last week and took a corner off the inn.\n\nPixie wants their blasting "
        "caps and their yard foremen. Without both, nothing goes bang.",
        [fetch("st_q_blasting_cap", 6), k("Venture Co. Yard Foreman", 3, SE)],
        "The blasters and the Venture Co. Yard Foreman bosses work the salvage yard. Bring me the caps, and carry "
        "them very, very carefully. I'm being serious.",
        "These are Cartel caps. Stolen Cartel caps! From our own warehouse in Ratchet!\n\nI'm taking these "
        "home. And then I'm finding out who signed them out.",
        [("off_hand", "weapon", "tome", "caster_crit"), ("chest", "armor", "leather", "physical"),
         ("feet", "armor", "mail", "hunter")],
        nxt="st_cartel_paperwork"))
    A(Q("st_yard_boss_krizzle", "Yard Boss Krizzle", PIXIE, 28, 28, "Cartel",
        "Yard Boss Krizzle runs the salvage yard, and Pixie has found out he used to be Cartel. He walked out "
        "with a warehouse key and a crate of caps when the Venture Co. offered him more money.\n\nShe'd like to "
        "have a word. You're the word.",
        [boss("Yard Boss Krizzle", SE)],
        "He's in the salvage yard, in the middle of it all, shouting at people. Tell him Pixie says hello.",
        "Did he say anything? He didn't say anything about me, did he?\n\nNo, never mind. The Cartel looks after "
        "its own, and you've looked after the Cartel. Take something nice.",
        [("main_hand", "weapon", "dagger", "rogue_crit"), ("chest", "armor", "mail", "mail_caster"),
         ("hands", "armor", "plate", "tank"), ("ring", "armor", None, "healer")]))
    A(Q("st_windshear_mine", "Trouble in Windshear Mine", PIXIE, 28, 30, "Cartel",
        "The Venture Co. has dug a mine under Windshear Crag, and Pixie's people say the ore that comes out of it "
        "gets sold in Ratchet under a forged Cartel stamp. The man running the dig is Driller Mozzik, and "
        "his Venture Co. Shaft Miner crews are the ones swinging the picks.\n\nShe wants the mine shut, and she means shut.",
        [k("Venture Co. Shaft Miner", 8, WM), boss("Driller Mozzik", WM)],
        "Windshear Mine is under the crag in the north-east. The miners are all through the galleries, and "
        "Mozzik is at the back where the drilling's loudest, so take friends.",
        "No more fake stamps in Ratchet. My cousin's going to buy me a drink for this.\n\nYou can have the "
        "drink, actually, and this as well.",
        [("main_hand", "weapon", "mace_2h", "strength_crit"), ("legs", "armor", "leather", "feral"),
         ("shoulder", "armor", "cloth", "fire"), ("head", "armor", "plate", "plate_healer")]))
    # ---- Apothecary Merrow Vane, the Forsaken
    A(Q("st_samples_from_the_rim", "Samples from the Rim", MERROW, 28, 29, "Deathwatch",
        "Apothecary Merrow Vane knows the tauren don't want him on Sun Rock. He also knows that whatever is "
        "getting the dead up in Mulgore isn't the Scourge, and isn't anything the Forsaken have seen. He wants "
        "to find out what's doing it before it reaches anywhere else.\n\nHe needs samples from the risen tauren and the "
        "risen stalkers on the Rim.",
        [fetch("st_q_rim_tissue", 6)],
        "The risen walk the Mulgore Rim in the south-east. Take the samples from the ones you put down. The jars "
        "seal themselves, mostly, but don't count on it.",
        "Fascinating, and horrible. There's no plague in this tissue at all. Nothing I know of is holding it "
        "together.\n\nWhatever's doing this isn't from Azeroth. I'd stake what's left of my life on it.",
        [("wrist", "armor", "cloth", "shadow"), ("head", "armor", "mail", "earthen"),
         ("legs", "armor", "leather", "bear")],
        nxt="st_what_raised_them"))
    A(Q("st_what_raised_them", "What Raised Them", MERROW, 29, 29, "Deathwatch",
        "Merrow wants to see what the risen see. There's a cairn at the edge of the Rim where the dark starts, "
        "and he believes the thing that raises them reaches up out of Mulgore there. He wants you to stand at "
        "the cairn and tell him what you feel, and to thin out the Risen Tauren that guard it.",
        [explore(160, 152, "Stand at the cairn on the edge of the dark", SE), k("Risen Tauren", 6, SE)],
        "The cairn's on the Mulgore Rim, right where the daylight gives up. Stand there as long as you can bear "
        "it. Then come back and tell me everything.",
        "Cold, and a pull downward, as if the ground wanted you. That's exactly what I felt, through the jars.\n\n"
        "I'll write this up for the Royal Apothecary Society. They won't believe me either.",
        [("main_hand", "weapon", "dagger", "caster"), ("chest", "armor", "plate", "crusader"),
         ("back", "armor", None, "physical")]))

    # ---- Dr. Hannah Lindqvist, the geologist
    A(Q("st_ground_zero", "Ground Zero", HANNAH, 26, 27, "Field Survey",
        "Dr. Hannah Lindqvist studied volcanoes in Washington State before the Integration. She says the "
        "mountain above Sun Rock is Mount St. Helens, or something very like it, and the Blowdown is what it did "
        "in 1980 all over again, right down to the way the trees lie.\n\nShe needs to see the middle of the "
        "blast and the edge of the salvage yard with her own eyes, but she's not much good with a weapon.",
        [explore(76, 64, "Stand where the blast was strongest", SE),
         explore(64, 50, "Look over the edge of the salvage yard", SE)],
        "Go and stand where the blast was strongest, out in the middle of the Blowdown, and then look over the "
        "edge of the salvage yard. Tell me which way the trees are lying. I'll do the rest.",
        "Lying away from the peak in a fan, and stripped of their bark on one side. It's St. Helens. It's "
        "exactly St. Helens.\n\nWhich means that mountain isn't finished, and somebody should probably tell the "
        "tauren.",
        [("head", "armor", "cloth", "traveller"), ("hands", "armor", "leather", "agility"),
         ("wrist", "armor", "plate", "tank")],
        nxt="st_cores_of_ash"))
    A(Q("st_cores_of_ash", "Cores of Ash", HANNAH, 27, 27, "Field Survey",
        "The ash drifters on the Blowdown are made of the same ash the mountain threw, and Hannah says they pack "
        "it down tight in the middle like a core sample. If she can read their layers, she can tell how long "
        "the mountain rested between eruptions.\n\nShe wants their ash cores.",
        [fetch("st_q_ash_core", 6)],
        "The ash drifters walk all over the Blowdown. Break them open and bring me what's in the middle. It'll be "
        "warm. That's good, that means it's fresh.",
        "There are four layers, so four eruptions, and the gaps between them are getting shorter.\n\nI need to see the top. "
        "I need to see it before it goes again.",
        [("chest", "armor", "mail", "hunter_precise"), ("feet", "armor", "cloth", "healer"),
         ("main_hand", "weapon", "mace_1h", "tank_weapon")],
        nxt="st_vents_on_the_peak"))
    A(Q("st_vents_on_the_peak", "Vents on the Peak", HANNAH, 30, 31, "Field Survey",
        "The peak of Stonetalon is in the West, past the redwoods, and Hannah's convinced the vents up there "
        "are opening. Every Vent Steamling on the peak is a vent walking around, she says, a crack in the mountain "
        "letting off pressure.\n\nShe wants them put out and the crater rim looked over.",
        [k("Vent Steamling", 8, SW), explore(104, 30, "Look into the crater from the rim", SW)],
        "Take the road through Stonetalon West and up to the peak. The vent steamlings are all over the top. Look "
        "into the crater from the rim and tell me if the lake's steaming.",
        "Steaming, and the colour's changed. That's gas coming up through the water.\n\nIt's not going to blow "
        "tomorrow. But there's a lava tube on the flank that's feeding it, and something down there keeps "
        "it hot.",
        [("off_hand", "weapon", "tome", "fire"), ("head", "armor", "leather", "rogue_crit"),
         ("legs", "armor", "plate", "tank_any")],
        nxt="st_into_the_ashvent"))
    A(Q("st_into_the_ashvent", "Into the Ashvent", HANNAH, 30, 32, "Field Survey",
        "The Ashvent is a lava tube on the flank of the peak, and Hannah says the heat at the bottom of it "
        "shouldn't be there. Something called Magmacore sits on the last of the molten rock and keeps it from "
        "cooling, and as long as it does the whole mountain stays warm.\n\nShe can't go down there, but you can.",
        [boss("Magmacore", AV)],
        "The Ashvent opens on the north flank of Stonetalon Peak. Follow the tube all the way down to the crust "
        "at the bottom, where Magmacore sits. Bring people who don't mind the heat.",
        "It's cooling already. My instruments say the whole tube dropped forty degrees overnight.\n\nYou might just have "
        "put off an eruption by a hundred years. Nobody will ever know, except me and you.",
        [("main_hand", "weapon", "staff", "frost"), ("chest", "armor", "leather", "bear"),
         ("hands", "armor", "mail", "hunter_crit"), ("head", "armor", "plate", "strength_hit")]))

    # ---- the trainers and the inn
    A(Q("st_iron_under_the_burn", "Iron Under the Burn", BRAK, 27, 28, "Ironhoof",
        "Forgemaster Brak Ironhoof says there's good iron on Stonetalon now that the trees aren't sitting on it. "
        "Sun Rock needs spearheads and hinges and nails, and he needs ore to make them.",
        [gather("ore_iron", 8, "Iron Ore from Stonetalon's seams")],
        "Iron shows up all over the Blowdown and the slopes in the West. You'll need to know mining to get it "
        "out. If you don't, I'll teach you.",
        "That's good ore. Clean, and plenty of it.\n\nSun Rock will have nails by the morning. Take this with you. It's "
        "the last thing I made from Thunder Bluff iron.",
        [("main_hand", "weapon", "mace_1h", "crusader"), ("feet", "armor", "leather", "physical"),
         ("shoulder", "armor", "mail", "earthen")]))
    A(Q("st_fallen_not_felled", "Fallen, Not Felled", KESH, 27, 28, "Highfeather",
        "Woodwright Kesh Highfeather won't touch a living giant. The Blowdown is full of trees that came "
        "through already down, though, and redbark from a fallen tree is as good as redbark from a standing one.\n\nHe wants "
        "logs for the new lodge.",
        [gather("wood_redbark_tree", 8, "Redbark Logs from fallen trees")],
        "There's redbark down all over Stonetalon. Cut it where it lies. You'll need woodcutting, and if you "
        "haven't got it, I'll teach you.",
        "Good, straight logs. These will hold a roof up for a hundred years.\n\nNow they need milling.",
        [("ring", "armor", None, "agility"), ("legs", "armor", "cloth", "spirit_caster"),
         ("chest", "armor", "plate", "tank")],
        nxt="st_planks_for_the_lodge"))
    A(Q("st_planks_for_the_lodge", "Planks for the Lodge", KESH, 28, 28, "Highfeather",
        "Kesh has the logs. Now he needs planks, and he wants you to mill them yourself at his bench, because "
        "he says you'll never look at a lodge the same way again once you've cut the boards for one.",
        [craft("plank_redbark", 6, "Mill Redbark Planks")],
        "Mill them at my bench, or any woodworker's bench, it doesn't matter. Straight, even planks. Mind your thumbs.",
        "That's a fine set of boards. You've a feel for wood.\n\nThe lodge will go up next week, and I'll tell "
        "everybody who cut the first planks.",
        [("main_hand", "weapon", "staff", "spirit_healer"), ("head", "armor", "mail", "hunter"),
         ("hands", "armor", "leather", "bear")]))
    A(Q("st_fireweed_and_amber", "Amber from the Eldest", NAWA, 30, 32, "Greenmane",
        "Herbalist Nawa Greenmane has heard the Eldest Sequoia's sap runs as living amber inside the trunk, and "
        "that it heals burns better than anything that grows on the outside. The Venture Co. has been tapping "
        "it, and the living sap that pools in the galleries carries it.\n\nShe wants some before the Venture Co. "
        "sells all of it.",
        [fetch("st_q_eldest_amber", 5)],
        "Go into the Eldest Sequoia from the door at its foot. The living sap moves through the lower galleries. "
        "Bring me the amber they carry. Take friends, it's a dungeon in there.",
        "Look at the light in it. That's not reflection, that's the tree.\n\nI'll make a salve that'll keep the "
        "children's burns from scarring.",
        [("legs", "armor", "leather", "wildheart"), ("chest", "armor", "cloth", "high_healer"),
         ("main_hand", "weapon", "sword_2h", "strength"), ("ring", "armor", None, "tank_any")]))
    A(Q("st_cougar_stew", "Cougar Stew", KAUWA, 27, 27, "Hearthside",
        "Innkeeper Kauwa feeds everybody on Sun Rock, and the elk are running thin. She says cougar makes a good "
        "stew if you cook it long enough, and the ridge cougars have been eating well on the Blowdown.",
        [fetch("st_q_cougar_flank", 6)],
        "The ridge cougars hunt all over the Blowdown and in the Standing Grove. Bring me the flanks. I'll do the "
        "cooking, you just do the hunting.",
        "That'll stew down nicely. Pull up a chair later and have a bowl.\n\nAnd take this. A guest gave it to me "
        "for a room and never came back for it.",
        [("trinket", "armor", None, "physical"), ("feet", "armor", "plate", "plate_healer"),
         ("waist", "armor", "cloth", "caster_crit")]))
    A(Q("st_hides_for_the_cold", "Hides for the Cold", OHANZEE, 27, 30, "Ohanzee's",
        "Tanner Ohanzee wants bear hides, black bear from the Standing Grove or greatwood bear from the redwoods "
        "in the West, it doesn't matter which. Winter on a mesa is cold, and a bear hide is the warmest thing a "
        "tauren can sleep under.",
        [fetch("st_q_bear_hide", 6)],
        "Black bears in the Standing Grove, greatwood bears in the West. Bring me the hides and I'll tan them for "
        "the refugees' beds.",
        "These are good, thick hides. They'll keep a family warm all winter.\n\nI made this from the first bear "
        "I ever skinned. I think it's time it went to someone who'll use it.",
        [("chest", "armor", "leather", "bear"), ("hands", "armor", "cloth", "healer"),
         ("legs", "armor", "mail", "hunter_precise")]))

    # ================================================================================ MISTWALKER CAMP
    # ---- Mistwalker Iyana Rainsong
    A(Q("st_beetles_in_the_bark", "Beetles in the Bark", IYANA, 29, 30, "Mistwalker",
        "Mistwalker Iyana Rainsong walks the fog under the redwoods that came through with the mountain, and she "
        "says the Bark Beetles have never "
        "been this bad. They bore into the giants and lay their eggs, and a tree that size dies so slowly that "
        "nobody notices until it's too late.\n\nShe wants the beetles cut back before they get into the oldest "
        "trees.",
        [k("Bark Beetle", 10, SW)],
        "The bark beetles are thickest in Greatwood Vale, below the camp. You'll hear them chewing if you stand "
        "still and listen.",
        "The vale sounds like a forest again, not a mill.\n\nThe trees will heal. They've healed from worse. "
        "They just needed a little help this time.",
        [("legs", "armor", "leather", "physical"), ("chest", "armor", "cloth", "spirit_healer"),
         ("main_hand", "weapon", "axe_2h", "strength")],
        zone=SW, nxt="st_the_ancients_wake"))
    A(Q("st_the_ancients_wake", "The Ancients Wake", IYANA, 30, 31, "Mistwalker",
        "Some of the giants were awake when they came through the Integration. Iyana calls them the Redwood "
        "Ancients, and since the Venture Co. started cutting they've been waking in a rage and walking the vale, "
        "flattening anything they find.\n\nShe can't calm them. She wants them put back to sleep the only way "
        "that works now.",
        [k("Redwood Ancient", 6, SW)],
        "The redwood ancients walk in Greatwood Vale and on the Sequoia Slopes. They're slow, and they hit like "
        "a falling tree. Don't stand still in front of one.",
        "They're quiet now, rooted where they stopped.\n\nI'll sit with them tonight, because somebody should."
        "",
        [("main_hand", "weapon", "staff", "bear_weapon"), ("head", "armor", "mail", "tide_healer"),
         ("shoulder", "armor", "plate", "strength")],
        zone=SW, nxt="st_gnawheart"))
    A(Q("st_gnawheart", "Gnawheart", IYANA, 31, 31, "Mistwalker",
        "The bark beetles have a mother. Iyana has found where she's been laying, inside a giant in Greatwood Vale "
        "that's hollow now from the root to the crown, and she calls the beetle Gnawheart because that's what "
        "she does.\n\nThe beetles won't stop coming while Gnawheart lives.",
        [boss("Gnawheart", SW)],
        "Gnawheart lives in a hollow giant deep in Greatwood Vale. She's bigger than a kodo. Bring friends and "
        "don't let her get behind you.",
        "No more eggs. No more beetles, not like before.\n\nThe Mistwalkers will remember this. Take what you "
        "like.",
        [("ranged", "weapon", "bow", "hunter_precise"), ("legs", "armor", "plate", "tank"),
         ("head", "armor", "cloth", "nature"), ("hands", "armor", "leather", "wildheart")],
        zone=SW, nxt="st_grandfather_burl"))
    A(Q("st_grandfather_burl", "Grandfather Burl", IYANA, 32, 32, "Mistwalker",
        "Grandfather Burl is the oldest of the redwood ancients. He woke when the Venture Co. cut his neighbour, "
        "and he's been walking the Sequoia Slopes ever since, tearing out anything that moves, Mistwalkers "
        "included.\n\nIyana loved him. She knew him for three years, which is nothing to a tree, and she still "
        "says she loved him. She wants him given rest.",
        [boss("Grandfather Burl", SW)],
        "He walks the Sequoia Slopes, round the foot of the great sequoia. He's slow and he's very, very strong, "
        "so go together.",
        "He's rooted again. I watched him do it. He picked a spot in the sun and put his roots down and stopped."
        "\n\nThank you. That's the end I wanted for him.",
        [("staff", "weapon", "staff", "nature"), ("chest", "armor", "plate", "tank_any"),
         ("legs", "armor", "mail", "hunter"), ("trinket", "armor", None, "healer")],
        zone=SW, elite=True))

    # ---- Tamsin Reyes, the arborist
    A(Q("st_a_climbers_look", "A Climber's Look", TAMSIN, 29, 30, "Climber's",
        "Tamsin Reyes climbed redwoods for a living back in Humboldt County. She says the tallest tree on Earth "
        "was a redwood called Hyperion, and the great sequoia on the slopes here would make Hyperion look like a "
        "sapling.\n\nShe wants to know how it's standing, and she wants you to look at the foot of it and the "
        "fall line on the slopes, because she's not climbing anything until she knows.",
        [explore(98, 76, "Look at the foot of the great sequoia", SW),
         explore(132, 70, "Look down the fall line from the slopes", SW)],
        "The great sequoia's on the Sequoia Slopes, north of the vale. Look at the base for cracks, then go "
        "across the slopes and look at which way it'd fall. I'll be here, nervously.",
        "No cracks at the base, and it's leaning uphill, which is the good way. It's going to stand for another "
        "thousand years.\n\nUnless somebody cuts it. Somebody's trying to cut it.",
        [("feet", "armor", "leather", "agility"), ("wrist", "armor", "mail", "mail_caster"),
         ("head", "armor", "plate", "plate_healer")],
        zone=SW, nxt="st_sap_on_the_slopes"))
    A(Q("st_sap_on_the_slopes", "Sap on the Slopes", TAMSIN, 30, 31, "Climber's",
        "The Sap Oozes are what happens when a sequoia bleeds, Tamsin says. The Venture Co. tap the giants and "
        "the sap runs out and gets up and walks away. It sticks to everything, and it sticks to her climbing "
        "rope worst of all.\n\nShe wants the sap oozes cleared off the slopes so she can climb.",
        [k("Sap Ooze", 8, SW)],
        "The sap oozes crawl all over the Sequoia Slopes. Watch your feet, they're stickier than they look, and "
        "they look very sticky.",
        "Clean rope, clean bark. I can climb.\n\nI'll take a look at the crown from up there and see what the "
        "eagles think of all this.",
        [("main_hand", "weapon", "polearm", "physical"), ("chest", "armor", "mail", "earthen"),
         ("shoulder", "armor", "cloth", "caster")],
        zone=SW, nxt="st_skyreach"))
    A(Q("st_skyreach", "Skyreach", TAMSIN, 31, 32, "Climber's",
        "Tamsin got halfway up a sequoia before a sky serpent the size of a canoe came round the trunk at her. "
        "The ridge eagles nest up on the peak, and she says the biggest of the serpents up there, Skyreach, has "
        "been driving them off and taking the nests.\n\nShe'd like to climb without being eaten. She'd also like "
        "the eagles to have their peak back.",
        [k("Ridge Eagle", 4, SW), boss("Skyreach", SW)],
        "Skyreach hunts round Stonetalon Peak. Every Ridge Eagle that's gone feral up there will attack anyone, "
        "so clear a few on the way. Skyreach will come to you.",
        "The eagles are back on the peak. I saw a pair going up this morning with sticks in their beaks.\n\n"
        "That's the best thing I've seen since I came through, and I mean that.",
        [("ranged", "weapon", "gun", "hunter_crit"), ("hands", "armor", "plate", "strength_crit"),
         ("chest", "armor", "cloth", "precise_caster"), ("feet", "armor", "mail", "tide_healer")],
        zone=SW))

    # ---- Nozzle Quickspan, ex-Venture Co.
    A(Q("st_the_cutline", "The Cutline", NOZZLE, 30, 31, "Quickspan",
        "Nozzle Quickspan ran a Venture Co. saw crew for years. He quit the day they started cutting the "
        "living giants, and now he works for the Cartel undoing what he used to do. The Venture Cutline is "
        "eating into the redwoods from the east, and he knows every crew on it by name.\n\nHe wants the fellers "
        "and the riggers stopped.",
        [k("Venture Co. Feller", 8, SW), k("Venture Co. Rigger", 6, SW)],
        "The Venture Cutline's east of the camp, where the trees stop and the stumps start. The Venture Co. "
        "Feller crews cut and the Venture Co. Rigger crews haul, and I want both stopped.",
        "The saws are quiet on the east side. First time in a month.\n\nI used to love that sound. I don't any "
        "more.",
        [("main_hand", "weapon", "axe_1h", "strength_hit"), ("chest", "armor", "leather", "rogue_crit"),
         ("head", "armor", "cloth", "haste_caster")],
        zone=SW, nxt="st_shredder_gears"))
    A(Q("st_shredder_gears", "Shredder Gears", NOZZLE, 31, 32, "Quickspan",
        "The Venture Co. Shredder walkers do the work of ten crews. Nozzle helped build the first ones, and he knows "
        "they can't run without their drive gears. Pull the gears and the shredders are scrap.\n\nHe also says "
        "the newcomers are half the problem. Before the Integration there were no trees this big to cut, and "
        "nobody would have built a machine this stupid to cut them.",
        [k("Venture Co. Shredder", 5, SW), fetch("st_q_shredder_gear", 5)],
        "The shredders work the Venture Cutline. Bring me their drive gears. Don't climb into one while it's "
        "running, I've seen what happens.",
        "These are mine. I designed these gears. That's not a good feeling.\n\nWithout them the Cutline is "
        "down to hand saws. Brakka's going to be furious.",
        [("main_hand", "weapon", "mace_2h", "strength_crit"), ("legs", "armor", "cloth", "arcane"),
         ("chest", "armor", "mail", "hunter_crit")],
        zone=SW, nxt="st_saw_boss_brakka"))
    A(Q("st_saw_boss_brakka", "Saw-Boss Brakka", NOZZLE, 32, 32, "Quickspan",
        "Saw-Boss Brakka runs the Venture Cutline. She was Nozzle's foreman, and she's the one who decided the "
        "living giants were fair game. Nozzle says she won't stop while she's breathing, and that she's very "
        "good at breathing.\n\nHe wants her stopped, and every Venture Co. Cut Foreman with her.",
        [boss("Saw-Boss Brakka", SW), k("Venture Co. Cut Foreman", 3, SW)],
        "Brakka's at the head of the Venture Cutline with her foremen. She carries a saw on a pole that'll take "
        "your arm off, so go together.",
        "Is she really down?\n\nThen the Cutline's finished. The Cartel will buy what's left and turn it "
        "into something useful. A sawmill for fallen wood, maybe. I'd like that.",
        [("main_hand", "weapon", "polearm", "strength"), ("off_hand", "weapon", "shield", "shield_tank"),
         ("chest", "armor", "leather", "feral"), ("head", "armor", "mail", "mail_caster")],
        zone=SW, elite=True))
    A(Q("st_the_work_order", "The Work Order", "item:st_q_work_order", 31, 32, "Quickspan",
        "You took a work order off one of the Venture Co. foremen on the Cutline. It's stamped urgent three times and it names the "
        "Eldest Sequoia, the greatest tree on the mountain. The crews inside the trunk have orders to cut it "
        "from within.\n\nNozzle Quickspan at Mistwalker Camp used to read these for a living.",
        [deliver("st_q_work_order", "Bring the work order to Nozzle Quickspan at Mistwalker Camp")],
        "Take it to Nozzle at Mistwalker Camp. He'll know what it means, and he won't like it.",
        "They're cutting the Eldest. They're actually cutting it from the inside.\n\nI know these crews and I "
        "know how they climb. Give me a moment and I'll tell you how to stop them.",
        [("ring", "armor", None, "caster_crit"), ("feet", "armor", "plate", "tank_any"),
         ("wrist", "armor", "leather", "agility")],
        zone=SW, turn_in_npc_id=NOZZLE, nxt="st_topping_the_eldest"))

    A(Q("st_topping_the_eldest", "Topping the Eldest", NOZZLE, 31, 33, "Quickspan",
        "The work order was real. The Venture Co. means to cut the Eldest Sequoia from the inside and the top at "
        "once. Rigboss Gazzle runs the crews climbing the trunk, and Topper Kezzik has a walking shredder up in "
        "the crown, cutting the top off so the rest comes down in pieces.\n\nNozzle trained half those crews "
        "himself. He says that makes it his job to stop them, and since he's no good in a fight, it's yours.",
        [boss("Rigboss Gazzle", ES), boss("Topper Kezzik", EC)],
        "Go into the Eldest Sequoia from the door at its foot, on the slopes north-east of here. Gazzle runs the rigs "
        "inside the trunk, and Kezzik's walker is up on the crown. Bring a full crew, I mean it.",
        "The crews have pulled out, every last one. The Venture Co. says it's a temporary setback.\n\nIt isn't "
        "temporary. The Cartel pays well for good work, and this was the best work I've seen.",
        [("main_hand", "weapon", "axe_1h", "physical"), ("chest", "armor", "plate", "tank_any"),
         ("legs", "armor", "mail", "tide_healer"), ("hands", "armor", "cloth", "precise_caster")],
        zone=SW))

    # ---- Alchemist Rennick Toll, the Forsaken
    A(Q("st_sulphur_and_ash", "Sulphur and Ash", RENNICK, 31, 31, "Undercity",
        "Alchemist Rennick Toll came to Stonetalon for the volcano's ash. Undercity's alchemists want it for "
        "something he won't explain, and the best ash on the mountain is the ash that walks around on its own: "
        "the crater ash wraiths on the peak.\n\nHe'd also like the basalt hulks kept off him while he works.",
        [fetch("st_q_wraith_ash", 6), k("Basalt Hulk", 4, SW)],
        "Stonetalon Peak, at the top of the West. The crater ash wraiths drift round the rim and the Basalt "
        "Hulk brutes stamp round the crater. Bring me the ash, and don't forget to seal the pouch.",
        "Good, fine ash, and it's still trying to go back to the crater. Undercity will be delighted.\n\nI won't "
        "say what for. You wouldn't sleep.",
        [("off_hand", "weapon", "tome", "shadow"), ("legs", "armor", "leather", "bear"),
         ("chest", "armor", "plate", "strength_hit")],
        zone=SW, nxt="st_the_ash_mother"))
    A(Q("st_the_ash_mother", "The Ash Mother", RENNICK, 31, 32, "Undercity",
        "The ash wraiths come from somewhere, Rennick says, and he's found where. There's a hollow off the "
        "skylight in the Ashvent where the ash falls in through the roof and something gathers it into the "
        "shape of a woman. The ash mother makes the wraiths, and she's making more of them every week.\n\nHe "
        "wants her ash. All of it, preferably.",
        [boss("The Ash Mother", AV)],
        "The Ashvent opens on the peak's north flank. Go down the tube to the skylight and find the hollow off "
        "it. She's in there. Take friends who can stand the heat.",
        "The ash of the thing that makes the ash. Undercity will want to talk to you.\n\nThey won't, of course. "
        "But I'll tell them you were extraordinary.",
        [("main_hand", "weapon", "dagger", "assassin"), ("chest", "armor", "cloth", "death"),
         ("shoulder", "armor", "mail", "hunter"), ("hands", "armor", "plate", "plate_healer")],
        zone=SW))
    A(Q("st_hulks_on_the_peak", "Hulks on the Peak", RENNICK, 31, 32, "Undercity",
        "The basalt hulks and the peak sky serpents have started coming down off the peak to Rennick's sampling "
        "sites, and he's run out of patience and nearly out of sites.\n\nHe says he'd do it himself, but he's an "
        "alchemist, and the hulks don't drink.",
        [k("Basalt Hulk", 6, SW), k("Peak Sky Serpent", 5, SW)],
        "Every Basalt Hulk and Peak Sky Serpent you'll need to deal with is up on Stonetalon Peak. Clear them off "
        "the high ground round the crater.",
        "My sites are clear. I can take readings for a week now.\n\nThis is for your trouble. It's been in a "
        "drawer in Undercity for twenty years. It deserves some air.",
        [("staff", "weapon", "staff", "shadow"), ("waist", "armor", "plate", "tank"),
         ("chest", "armor", "leather", "wildheart")],
        zone=SW))

    # ---- the far side's road west
    A(Q("st_the_road_to_desolace", "The Closed Road", IYANA, 30, 30, "Mistwalker",
        "There's a road off the west side of Stonetalon that goes down toward Desolace. Iyana says nobody's come "
        "up it since the Integration, and nobody who's gone down has come back. She wants to know if it's still "
        "shut, and what's been coming up to the edge of it.\n\nShe also wants the Fog Cougar packs cleared off "
        "the road on the way.",
        [k("Fog Cougar", 6, SW), explore(10, 150, "Look down the closed road toward Desolace", SW)],
        "The road's in the far south-west of Stonetalon West, past the vale. The fog cougars hunt along it. Look "
        "down it and come back and tell me what you saw.",
        "It's shut, and there's nothing on the road but rockfall. That's good enough.\n\nNot good forever. Just good for now. I'll take it.",
        [("hands", "armor", "mail", "earthen"), ("feet", "armor", "cloth", "caster_crit"),
         ("ring", "armor", None, "tank_any")],
        zone=SW))

    # ================================================================================ EAST, ACROSS THE SEA
    # ---- Merrow's samples to Hammerfall
    A(Q("st_for_the_society", "For the Society", MERROW, 29, 30, "Deathwatch",
        "Merrow wants a second opinion, and the only Forsaken apothecary he trusts on this side of the world is "
        "Dellwyn Voss at Hammerfall, in the Arathi Highlands. Voss has written four reports about something "
        "living in the mere water there that won't die properly, and Merrow thinks it might be the same thing "
        "as the Rim.\n\nHe's packed the samples in ice. He wants them carried across the sea.",
        [deliver("st_q_packed_samples", "Bring the packed samples to Apothecary Dellwyn Voss at Hammerfall")],
        "Hammerfall's in the Arathi Highlands, in the Eastern Kingdoms. Take a ship from the coast or the "
        "zeppelin, whichever gets you there faster. Don't open the box. I mean it.",
        "Merrow Vane sent you? I haven't heard that name in years.\n\nAnd these are something I've seen before. "
        "Give me a day with them, and then come back.",
        [("neck", "armor", None, "spirit_healer"), ("legs", "armor", "plate", "strength_crit"),
         ("head", "armor", "leather", "hunter")],
        nxt="st_voss_replies", turn_in_npc_id=VOSS,
        requires_quests=["st_what_raised_them"],
        grant_items=carry("st_q_packed_samples", "Packed Samples", "A small chest packed with ice. Something "
                                                                   "inside it knocks, very softly, now and then.")))
    A(Q("st_voss_replies", "Voss Replies", VOSS, 30, 30, "Hammerfall",
        "Dellwyn Voss has had the samples for a day and a night. What lives in the Arathi mere isn't the same "
        "thing as what's on the Rim, she says, but it was made the same way, by something that doesn't need "
        "plague to hold the dead together.\n\nShe's written it all down for Merrow, in a hand so small you'd "
        "need his eyes to read it.",
        [deliver("st_q_voss_reply", "Bring Voss's reply to Apothecary Merrow Vane at Sun Rock Retreat")],
        "Take this back to Merrow at Sun Rock. Tell him he was right, and tell him I hate that he's right.",
        "Two places, a world apart, and the same hand behind both.\n\nI'll write to the Society, and they'll "
        "laugh. Then the third place will happen, and they'll stop laughing.",
        [("main_hand", "weapon", "wand", "death"), ("chest", "armor", "mail", "tide_healer"),
         ("hands", "armor", "leather", "feral")],
        zone=HF, turn_in_npc_id=MERROW,
        grant_items=carry("st_q_voss_reply", "Voss's Reply", "Six pages of very small writing, and a pressed "
                                                             "leaf from the mere's edge.")))
    # ---- Pixie's caps to Booty Bay
    A(Q("st_cartel_paperwork", "Cartel Paperwork", PIXIE, 28, 28, "Cartel",
        "Somebody signed those blasting caps out of a Cartel warehouse, and Pixie wants to know who. The Cartel's "
        "warehouse ledgers for this side of the world are kept by Factor Weezel in Booty Bay, because Booty Bay "
        "never throws anything away.\n\nShe's written down every stamp number off the caps.",
        [deliver("st_q_stamp_list", "Bring the stamp list to Factor Weezel in Booty Bay")],
        "Booty Bay is at the bottom of Stranglethorn, in the Eastern Kingdoms. Weezel keeps the ledgers. He'll "
        "tell you he's busy, because he's always busy. Wait for him anyway.",
        "These stamp numbers are from the Kalimdor stock. Somebody's been very careless.\n\nHave a seat. This "
        "won't take long, or not very long.",
        [("main_hand", "weapon", "sword_1h", "tank_weapon"), ("waist", "armor", "cloth", "caster"),
         ("feet", "armor", "leather", "physical")],
        nxt="st_weezels_findings", turn_in_npc_id=WEEZEL, requires_quests=["st_blasting_caps"],
        grant_items=carry("st_q_stamp_list", "Stamp List", "A list of numbers copied off the bottoms of stolen "
                                                           "blasting caps, in Pixie's round hand.")))
    A(Q("st_weezels_findings", "Weezel's Findings", WEEZEL, 28, 28, "Cartel",
        "Factor Weezel found the signature. The caps were signed out by a Krizzle, a Cartel man in Ratchet, on "
        "the same day he resigned. Weezel says Krizzle took a key, a crate and the Cartel's good name with him, "
        "and the Cartel would like at least one of the three back.\n\nHe's written it up for Pixie, with the "
        "seal that means she can do what she likes about it.",
        [deliver("st_q_weezel_findings", "Bring Weezel's findings to Pixie Brightcog at Sun Rock Retreat")],
        "Take these to Pixie Brightcog. The seal means she has the Cartel's leave. She'll know what that means.",
        "It was Krizzle all along. I knew it, I just knew it!\n\nAnd the seal too. Weezel's given me leave. Now we can talk about the "
        "salvage yard properly.",
        [("ring", "armor", None, "tank_any"), ("legs", "armor", "mail", "hunter_crit"),
         ("shoulder", "armor", "cloth", "arcane")],
        zone=BB, turn_in_npc_id=PIXIE, nxt="st_yard_boss_krizzle",
        grant_items=carry("st_q_weezel_findings", "Weezel's Findings", "Two pages, a copied ledger line and a "
                                                                       "heavy Cartel seal.")))
    # ---- Rennick's ash to Brill
    A(Q("st_ash_for_brill", "Ash for Brill", RENNICK, 32, 32, "Undercity",
        "Rennick has ash from the wraiths and ash from the thing that made them, and he wants both in the hands "
        "of the apothecaries at Brill, in Tirisfal. He says they'll know what to do with it. He also says it's "
        "better if you don't know.\n\nHe's sealed it in lead.",
        [deliver("st_q_lead_box", "Bring the lead box to Assistant Grael in Brill")],
        "Brill's in Tirisfal Glades, by Undercity, in the Eastern Kingdoms. Assistant Grael will take it. Don't "
        "drop it, and don't shake it.",
        "This is from Rennick, from a volcano? He always did have the best ideas and the worst timing.\n\nGive me a "
        "moment to write him back.",
        [("off_hand", "weapon", "tome", "void"), ("chest", "armor", "leather", "agility"),
         ("head", "armor", "plate", "tank")],
        zone=SW, nxt="st_grael_writes_back", turn_in_npc_id=GRAEL, requires_quests=["st_the_ash_mother"],
        grant_items=carry("st_q_lead_box", "Lead Box", "A small lead box, sealed shut, warm on one side.")))
    A(Q("st_grael_writes_back", "Grael Writes Back", GRAEL, 32, 32, "Brill",
        "Assistant Grael has written to Rennick. The ash is exactly what Brill wanted, and there's a request for "
        "more, and a warning that the Royal Apothecary Society has heard about Rennick's work and would like a "
        "word.\n\nShe doesn't say which word.",
        [deliver("st_q_grael_letter", "Bring Grael's letter to Alchemist Rennick Toll at Mistwalker Camp")],
        "Take this back to Rennick. He'll be pleased. Then he'll read the second page and he won't be.",
        "More ash, and a word from the Society. How absolutely wonderful.\n\nWell, you've been very good to an "
        "old corpse. Take this, and don't tell the tauren where it came from.",
        [("main_hand", "weapon", "dagger", "rogue_crit"), ("chest", "armor", "cloth", "void"),
         ("hands", "armor", "mail", "earthen")],
        zone=BR, turn_in_npc_id=RENNICK,
        grant_items=carry("st_q_grael_letter", "Grael's Letter", "Two pages. The second is written much more "
                                                                 "carefully than the first.")))

    # ---- a hunter's charm off the Rim
    A(Q("st_a_name_on_the_post", "A Name on the Post", "item:st_q_bloodhoof_charm", 28, 29, "Rim-Watch",
        "You found a Bloodhoof hunting charm on one of the risen stalkers. It's braided hide and a carved bead, "
        "and there's a name worked into the bead. Somebody on Sun Rock will know whose it was.\n\nKuna Ashhorn "
        "keeps the hunters' post on the south-east tower.",
        [deliver("st_q_bloodhoof_charm", "Bring the charm to Kuna Ashhorn at Sun Rock Retreat")],
        "Take it to Kuna Ashhorn on the south-east tower at Sun Rock. She knew every hunter in Mulgore, and she'll know this one.",
        "This was Tahu's charm. He taught me to set a snare when I was a calf.\n\nHe's on the post already, "
        "carved there the week the bluffs fell. I'll hang this under his name. Thank you for bringing it home.",
        [("back", "armor", None, "hunter"), ("feet", "armor", "mail", "earthen"),
         ("wrist", "armor", "cloth", "holy")],
        zone=SE, turn_in_npc_id=KUNA))

    return out
