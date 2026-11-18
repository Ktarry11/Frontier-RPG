#!/usr/bin/env python3
"""The Timbermaw Tunnel's people, the Timbermaw Hold reputation, its quartermaster's shelf, its quests. Idempotent.

    PYTHONPATH=. python3 tools/build_timbermaw_hold.py

Kyle, 17 Nov 2026: "How about we ... add timbermaw hold? We have the art for it and we can add the reputation. And
since it won't have mobs it'll be an easy build!", then "So timbermaw is a tunnel bro!", "It'll eventually go to
winterspring and moonglade" and "Timbermaw hold will be in Azshara!" So the map is the TUNNEL,
tools/handbuilt_timbermaw_tunnel.py, at the top of North Felwood's spine road, with the Timbermaw who came down from
the Hold to deal with the Deadwood camped along it. The Hold itself comes with Azshara; its reputation starts here.
This script does everything that lives in data.

THE TIMBERMAW HOLD REPUTATION, the way Classic did it:
  * Deadwood kills. The Deadwood are the Timbermaw's own cousins, gone mad on the fel, and every one you put down in
    Felpaw Village pays the Hold: 10 a kill and Chieftain Grimpelt 50, up to Honored. A creature pays one faction
    (qa_factions), so the Deadwood move off the Emerald Reclamation's list; the Reclamation keeps the Legion, the
    satyrs, the Shadow Council and the fel-rotted wildlife.
  * Deadwood Headdress Feathers. Every Deadwood carries one now and then; Featherkeeper Imna takes them ten at a time,
    as often as you bring them, for 100. That's the road past Honored.
  * The tunnel's quests (zone timbermaw_tunnel), 325 a quest, and Barrowpaw's Felpaw chain at Talonbranch (Timbermaw
    business, so it's in `also`), with Chieftain Grimpelt worth 500. The chain already covers Felpaw's warriors, its
    totems and Grimpelt, so the tunnel's own quests don't repeat them: the shamans, the Bloodvenom in Selva's spring,
    the bears at the mouth, and the Deadwood's seeds.
THE SHELF, TBC-style like every other faction (tools/build_faction_rewards.py's model and rules, authored here with
the same author_unique() and the crafted gear's author(); that script and build_crafted_gear.py must not be re-run):
friendly supplies; honored and revered patterns moved off town shelves (leatherworking and woodworking, the
Timbermaw's trades); revered six ilvl 67 blues; exalted three ilvl 73 epics at 250-350g, and two recipes that craft
ilvl 73 epics. A direction, not a cage: every role and armour type is somewhere on it.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import build_faction_rewards as BFR  # noqa: E402

FID = "timbermaw_hold"
ZONE = "timbermaw_tunnel"
#: the Hold itself, in Azshara (tools/handbuilt_timbermaw_hold.py, 17 Nov 2026)
HOLD = "timbermaw_hold"
#: Kyle, 17 Nov 2026: "timbermaw rep vendor and the leader will be in timbermaw hold and not in the tunnel"
MOVED_UP = ("tm_elder", "tm_quartermaster")
NF = "north_felwood"
QM_ID = "tm_quartermaster"

# ---------------------------------------------------------------------------------------------- the people
#: vendor_id -> (name, race, gender, variant, facing, gear_level, sells_gear, everyday stock, greeting)
VENDORS = {
    "tm_quartermaster": ("Quartermaster Bruna Honeyhide", "furbolg", "female", 2, "down", 55, True,
                         ["healing_potion_masterwork", "mana_potion_masterwork", "kit_field_repair", "whetstone"],
                         "The Hold trades with those who've stood with it. Show me you have, and I'll show you "
                         "what the carvers made for friends of the Timbermaw."),
    "tm_provisioner": ("Provisioner Orbo", "furbolg", "male", 1, "right", 55, False,
                       ["meal_saltback_roast", "drink_deepwell_cordial", "hunters_brace_platter", "cook_flour",
                        "cook_spice", "cook_water", "cook_mushroom", "beast_lure"],
                       "Honey, smoked fish and bread, carried all the way down from the Hold. Eat before you go "
                       "down to Felwood, because Felwood doesn't feed anybody."),
}
#: npc_id -> (name, race, gender, variant, facing, greeting)
AMBIENT = {
    "tm_elder": ("Elder Haldor Mossmane", "furbolg", "male", 3, "down",
                 "Welcome to the Hold. I sat in the tunnel for three years seeing to Felwood myself, and now the "
                 "tunnel's open, I can see to it from home. We let the Deadwood leave us, and we mean to bring back "
                 "whoever of them can still be brought."),
    "tm_windtalker": ("Windtalker Selva Brightpelt", "furbolg", "female", 6, "right",
                      "The passage past my spring goes on to Moonglade again. The druids up there dug it out from "
                      "their side, them and the strange humans they call the Wakened, and now the wind brings the "
                      "glade down to me as well as Felwood's drums."),
    "tm_pathfinder": ("Pathfinder Grosk", "furbolg", "male", 5, "left",
                      "I walk the tunnel down to Felwood every morning and count what's changed in Felpaw. Every "
                      "morning, something has."),
    "tm_featherkeeper": ("Featherkeeper Imna", "furbolg", "female", 4, "right",
                         "Every Deadwood wears the headdress, and every headdress was a Timbermaw's once. Bring me "
                         "their feathers and I'll see they're burned properly."),
    "tm_honeykeeper": ("Honeykeeper Tova", "furbolg", "female", 2, "down",
                       "The honey comes down from the Hold's hives in these crates. Every bear in Felwood can smell "
                       "it from the tunnel mouth, and every one of them has tried."),
    "tm_south_warden": ("Warden Bramblecoat", "furbolg", "male", 1, "down",
                        "Come in, then. The Elders opened the tunnel to anyone who comes in peace, and you've come "
                        "in peace or you'd be lying at the bottom of the hill."),
    "tm_north_warden": ("Warden Durn Rockpelt", "furbolg", "male", 4, "up",
                        "This passage went on to Winterspring, once. The day the world changed, the roof came down, "
                        "and nobody's dug far enough to say what's on the other side."),
}
#: THE HOLD'S OWN PEOPLE (tools/handbuilt_timbermaw_hold.py). The brief: an inn and no flight point, Earth volunteers
#: among the Timbermaw, and wardens on the sealed deep gate. Vendors as VENDORS above, everyone else as AMBIENT.
HOLD_VENDORS = {
    "th_provisioner": ("Provisioner Hunnla Thistlefur", "furbolg", "female", 5, "down", 56, False,
                       ["meal_saltback_roast", "drink_deepwell_cordial", "hunters_brace_platter", "cook_flour",
                        "cook_spice", "cook_water", "cook_mushroom", "beast_lure"],
                       "Smoked fish from the spring, bread from the ovens and honey on all of it. The tunnel gets "
                       "what's left after the Hold's eaten, so you've come to the right end."),
    "th_smith": ("Smith Grumm Ironpaw", "furbolg", "male", 2, "down", 56, True,
                 ["kit_field_repair", "whetstone", "flux_strong", "healing_potion_masterwork"],
                 "We don't make much iron up here, but what we make lasts. Bring me whatever you've broken and "
                 "I'll have it right before the bellows cool."),
    "th_honeymother": ("Honeymother Ama Goldmane", "furbolg", "female", 3, "right", 56, False,
                       ["drink_deepwell_cordial", "hunters_brace_platter", "cook_spice", "cook_flour", "beast_lure"],
                       "Every hive on these terraces is older than me, and every jar in the store has a name on it. "
                       "Buy what's on the shelf and don't touch what isn't."),
}
HOLD_AMBIENT = {
    "th_innkeeper": ("Innkeeper Bortha Mossbelly", "furbolg", "female", 4, "down",
                     "There's a bed by the fire and honey bread in the morning. Outsiders sleep at the inn, and "
                     "nobody minds what you are so long as you keep your boots off the furs."),
    "th_totemkeeper": ("Totemkeeper Ungar Ashbrow", "furbolg", "male", 6, "down",
                       "Every bear on the great totem was an Elder of the Hold. The carvers add one when an Elder "
                       "dies, and they haven't had to add one for the Deadwood yet. I'd like to keep it that way."),
    "th_spring_keeper": ("Springwarden Lessa Brightwater", "furbolg", "female", 2, "right",
                         "The spring comes up from under the mountain, clean, the way it always has. Since the deep "
                         "gate started to stain, I taste it every morning before anyone drinks."),
    "th_deep_warden": ("Deepwarden Grothar", "furbolg", "male", 5, "down",
                       "The deep gate stays shut. Whatever turned the Deadwood came up from under the Hold, and the "
                       "Elders sealed it the night they found out. Don't stand on the crack."),
    "th_deep_warden_b": ("Deepwarden Ulma", "furbolg", "female", 1, "left",
                         "We take turns listening at the gate. Some nights it's quiet, and some nights something on "
                         "the other side is digging."),
    "th_carver": ("Carver Bennik Ashpaw", "furbolg", "male", 3, "down",
                  "That totem in the yard has been waiting for its last face for a year. The Elders haven't decided "
                  "whose it should be, and I'm not carving a face for somebody who isn't dead."),
    "th_volunteer": ("Ingrid Solberg", "human", "female", 4, "down",
                     "I was a park ranger in Jotunheimen before the Integration. The Timbermaw took me in when the "
                     "Horde camps wouldn't, and now I keep the long hall's stores. Bears that talk back took some "
                     "getting used to."),
    "th_gate_warden": ("Gatewarden Hrolm", "furbolg", "male", 1, "down",
                       "The pass down to Azshara's forest is steep, and the satyrs watch the bottom of it. Come and "
                       "go in daylight if you can."),
    "th_gate_warden_b": ("Gatewarden Tibba", "furbolg", "female", 6, "down",
                         "Welcome to Timbermaw Hold. Mind the Elders, mind the hives, and don't go near the gate in "
                         "the floor."),
    "th_tunnel_warden": ("Tunnelwarden Burrfoot", "furbolg", "male", 4, "right",
                         "The tunnel's through there, all the way to Felwood. It's a long walk in the dark, so take "
                         "a torch and follow the totems."),
    # ---- a capital's services (Kyle, 17 Nov 2026: "an actual capital city... similar to how org is")
    "th_banker": ("MerchantTusk", "troll", "male", 3, "down",
                  "Dere is only one bank, mon, and dere is only one me. Do not ask how dat works. Hand me ya things "
                  "and go be a hero."),
    "th_auctioneer": ("Auctioneer Fizzbit Coppercrank", "goblin", "female", 2, "down",
                      "The Timbermaw don't haggle, they trade, and they write down every deal. Put it on the block "
                      "and the whole Horde can bid. The house takes its cut, same as anywhere."),
    "th_orc_envoy": ("Envoy Grashak Stonetusk", "orc", "male", 6, "down",
                     "Orgrimmar sent me to keep the road to the Hold open. The Elders let me sit on their terrace "
                     "and wait, and I've learned that waiting is most of what an envoy does here."),
    "ct_timbermaw_hold": ("Trainer Ursa Greymantle", "furbolg", "female", 3, "down",
                          "I've trained warriors, healers and the odd mage the Elders took in. Tell me what you are "
                          "and I'll show you what's next."),
    "pt_th_forge": ("Forgekeeper Dunn Ironpelt", "furbolg", "male", 4, "down",
                    "Mining, the forge and gems. The ore's deep in this mountain, and the Hold's been digging it "
                    "since before your grandparents' grandparents."),
    "pt_th_hide": ("Hidewright Tess Softpaw", "furbolg", "female", 5, "down",
                   "Skinning, leather, cloth and cooking, all from the same kill. Pay once and I'll teach you the "
                   "lot."),
    "pt_th_herbs": ("Herbwarden Fenna Mossbrow", "furbolg", "female", 1, "down",
                    "Herbs and alchemy. The racks dry what the terraces grow, and I don't let any of it go to waste."),
    "pt_th_wood": ("Woodwright Brann Oakpaw", "furbolg", "male", 2, "left",
                   "Woodcutting and woodworking. The carvers take the best wood for the totems, so you'll learn on "
                   "what's left, same as I did."),
}
#: flags carried on top of the plain record (the bank role, the trainers)
HOLD_FLAGS = {
    "th_banker": {"is_banker": True, "sprite_scale": 2.0},
    "ct_timbermaw_hold": {"trains_class": "*"},
}
HOLD_TRAINERS = {
    "pt_th_forge": ["mining", "blacksmithing", "jewelcrafting"],
    "pt_th_hide": ["skinning", "leatherworking", "tailoring", "cooking", "fishing"],
    "pt_th_herbs": ["herbalism", "alchemy"],
    "pt_th_wood": ["woodcutting", "woodworking"],
}
HOLD_SERVICES = {"th_innkeeper": ["inn"], "th_auctioneer": ["auction"]}
#: the mail, between the bank's and the auction house's doors (Kyle, 17 Nov 2026: "an auction house, a bank, and a
#: mailbox close together"). Its id is the one tools/place_market_npcs.py gives an inn's box, so that tool leaves it be.
HOLD_MAILBOX = ("mailbox_th_innkeeper", (162, 161), "assets/tiles/market/props/mailbox_tauren.png")

#: the gatewarden in North Felwood stops saying the tunnel is shut
THORNCLAW = ("fn_timbermaw_guard", "The tunnel behind me is the Timbermaw's road through the mountain. The Elders have "
                                   "opened it to anyone who comes in peace, so mind your manners up there.")

# ---------------------------------------------------------------------------------------------- the faction
DEADWOOD = ["Deadwood Warrior", "Deadwood Den Watcher", "Deadwood Pathfinder", "Deadwood Shaman",
            "Deadwood Gardener"]
GRIMPELT = "Chieftain Grimpelt"

#: the Rotroot Deeps' trash (tools/build_rotroot_deeps_content.py ROSTER), written out here so a rebuild of the Hold
#: keeps paying for it without importing the dungeon's builder
ROTROOT_TRASH = ["Rotroot Furbolg", "Rotroot Mystic", "Rotroot Mauler", "Drifting Sporecloud", "Satyr Rot-Tender",
                 "Gloomhollow Satyr", "Rootbound Horror", "Rotroot Bodyguard"]

FACTION = {
    "name": "Timbermaw Hold",
    "description": ("The Timbermaw furbolgs of the hold above Felwood: the last of their people the fel didn't "
                    "take, and they mean to take their cousins back."),
    "home_zone": HOLD,
    "home_name": "Timbermaw Hold, in Azshara (its people also keep the Timbermaw Tunnel above Felwood)",
    "leader": {
        "title": "Elder",
        "name": "Haldor Mossmane",
        "npc_id": "tm_elder",
        "location": "The Elders' Great Lodge, in Timbermaw Hold",
        "line": ("Every Deadwood in Felpaw was born in the Hold, or their mother was. We don't hate them. We "
                 "can't afford to stop fighting them, either."),
    },
    "_lore_note": "Kyle, 17 Nov 2026: 'add timbermaw hold ... and we can add the reputation'.",
    "lore": [
        "The Timbermaw's home is the Hold in Azshara, and their tunnels run through the mountains from there to "
        "Felwood, Winterspring and Moonglade. They were the only furbolgs the fel never took, because they kept to "
        "the mountain and kept their own counsel.",
        "Their cousins weren't so lucky. The Deadwood tribes of Felwood drank the corruption with the water, and "
        "they've been raiding the forest ever since. Felpaw Village is the worst of them.",
        "The day the world changed, the roof came down on the tunnel's Winterspring and Moonglade passages. The "
        "Elders took it as a sign to look south instead, and for the first time in a long time they opened the "
        "tunnel's Felwood mouth to outsiders who'd help. The Moonglade passage has since been dug out from the "
        "glade's side; Winterspring's is still shut.",
        "They trade with the Emerald Reclamation and they like its druids, but the Hold keeps its own counsel and "
        "its own ledger. The Timbermaw remember every favour, and every insult, for a very long time.",
    ],
    "quest_rep": {
        "_comment": "Per quest, by shape. Matches the other factions' rates.",
        "_comment_rate": ("325 a quest, not the 225 most factions pay: the Timbermaw own eight quests and the feathers, "
                          "and questing has to show on the bar (qa_factions)."),
        "default": 325,
        "boss": 350,
        "capstones": {},
        "zones": [ZONE, HOLD],
    },
    "kill_rep": {
        "_comment": ["The Deadwood (Classic's Timbermaw rep): 10 a kill and Grimpelt 50, up to Honored. Past Honored "
                     "it's Deadwood Headdress Feathers at the Hold and the Hold's quests."],
        "creatures": {**{n: [10, "honored"] for n in DEADWOOD}, GRIMPELT: [50, "honored"],
                      # the Rotroot Deeps under the Hold (tools/build_rotroot_deeps_content.py): its trash pays on
                      # past Honored, since the dungeon is how the Hold's people get to Revered
                      **{n: [10, "revered"] for n in ROTROOT_TRASH}},
    },
    "dungeon_rep": {
        "_comment": "A boss kill in the Rotroot Deeps pays 75 (tools/build_rotroot_deeps_content.py).",
        "per_boss": 75,
        "dungeons": ["The Rotroot Deeps"],
    },
}

# ---------------------------------------------------------------------------------------------- the shelf
#: (id, name, slot, kind, type, identity, price in gold, flavour)
REVERED = [
    ("tm_honeywood_bulwark_helm", "Honeywood Bulwark Helm", "head", "armor", "plate", "tank", 70,
     "Plate beaten over a cap of carved honeywood. The Hold's smiths line everything with wood."),
    ("tm_windtalkers_shoulderwraps", "Windtalker's Shoulderwraps", "shoulder", "armor", "cloth", "healer", 60,
     "Woven by the spring, from wool the Timbermaw trade for with the night elves."),
    ("tm_pathfinders_jerkin", "Pathfinder's Jerkin", "chest", "armor", "leather", "agility", 68,
     "Worn soft by a lot of mornings walking the tunnel down to Felwood."),
    ("tm_featherkeepers_cord", "Featherkeeper's Cord", "waist", "armor", "cloth", "caster", 48,
     "A belt of braided hide with one clean feather tied at the knot, for every one that's burned."),
    # leather and Strength: until this piece no rep shelf had one, which left Barbarian's two strength specs with only
    # weapons and rings (tools/audit_rep_coverage.py, 17 Nov 2026)
    ("tm_totemcarved_bracers", "Totem-Carved Bracers", "wrist", "armor", "leather", "strength", 46,
     "Thick hide bracers with a bear's head carved into the wooden backing of each one."),
    ("tm_mossmane_signet", "Mossmane Signet", "ring", "armor", None, "strength_crit", 55,
     "Elder Haldor's own family mark, a bear's paw pressed into dark amber."),
]
EXALTED = [
    ("tm_maul_of_the_elders", "Maul of the Elders", "main_hand", "weapon", "mace_2h", "strength", 330,
     "A totem pole's top, cut off and hafted. The Elders say the bear on it was a real one."),
    ("tm_staff_of_the_hold", "Staff of the Hold", "main_hand", "weapon", "staff", "bear_weapon", 300,
     "Honeywood, iron-shod at the foot. It's for whoever stands in the tunnel when the Deadwood come."),
    ("tm_brightpelts_spirit_totem", "Brightpelt's Spirit Totem", "off_hand", "weapon", "tome", "high_healer", 275,
     "A little carved totem Selva keeps by the spring. She made a second one and won't say who for."),
]
#: patterns moved onto the shelf from the town shelves that sold them (TBC rep patterns were sold only for standing)
MOVED = {"honored": ["lw_fiendish_boots", "wwx_frostheart_tide_totem"],
         "revered": ["p300_le_savage_head", "wwx_starleaf_bow"]}
#: (id, trade, name, slot, kind, type, identity, flavour)
EXALTED_RECIPES = [
    ("rep_tm_timbermaw_warhide", "leatherworking", "Timbermaw Warhide", "chest", "armor", "leather", "feral",
     "Thick fur over hardened hide, the way the Hold's own defenders wear it."),
    ("rep_tm_honeywood_longbow", "woodworking", "Honeywood Longbow", "ranged", "weapon", "bow", "hunter_crit",
     "Honeywood from the mountain's top, strung with gut and waxed with the Hold's own honey."),
]
SUPPLIES = {"friendly": ["healing_potion_supreme"], "honored": ["mana_potion_supreme"]}

# ---------------------------------------------------------------------------------------------- feathers and drops
FEATHER = ("tm_deadwood_headdress_feather", "Deadwood Headdress Feather",
           "A feather from a Deadwood headdress, stained green at the quill. Featherkeeper Imna in Timbermaw Hold "
           "takes these ten at a time.", "qi_feather")
SAMPLE = ("tm_q_bloodvenom_sample", "Bloodvenom Sample",
          "A jar of what's inside a Seepage Ooze. It's warm, and it moves when you're not looking at it.")
SEEDS = ("tm_q_fel_seed_pouch", "Fel-Tainted Seed Pouch",
         "A Deadwood gardener's seed pouch. Whatever these grow into, the Timbermaw don't want it planted.")
#: Felwood's own Timbermaw quests, given by Barrowpaw at Talonbranch: Timbermaw business, so they pay the Timbermaw
ALSO = ["fw_to_timbermaw_hold", "fw_felpaw_village", "fw_the_totems_of_felpaw"]
CAPSTONES = {"fw_chieftain_grimpelt": 500, "tm_deadwood_feathers": 100}

# ---------------------------------------------------------------------------------------------- the quests
XP = {54: 3960, 55: 4040}
GOLD = {54: 15600, 55: 15900}
DOWN = "down the tunnel to North Felwood"


def kill(target, n):
    return {"type": "kill", "target": target, "count": n, "zone": NF}


def quests():
    from tools.felwood_quest_kit import Q
    tm = "timbermaw"
    qs = [
        dict(quest_id="tm_the_tunnel_opens", title="The Tunnel Opens", giver_npc_id="tm_south_warden", zone=ZONE,
             level_min=54, level_max=54,
             description=("Warden Bramblecoat keeps the Timbermaw Tunnel's south mouth. Thornclaw promised you'd be "
                          "the first outsider up the hill once the Elders opened it, and the Elders want to meet you."),
             objectives=[{"type": "deliver", "target": "tm_q_bramblecoat_token", "count": 1,
                          "label": "Bring Bramblecoat's token to Elder Haldor Mossmane at the Great Lodge in "
                                   "Timbermaw Hold"}],
             accept_text=("Thornclaw said you'd be the first one up the hill, and he was right. Three years that "
                          "mouth has been shut, and you're the first outsider through it.\n\nTake this token so "
                          "the others know I let you in. Climb past the waystation and through the Honey Galleries, "
                          "then keep on along the passage past them all the way to its end. That's the door to "
                          "Timbermaw Hold, our home. Elder Haldor's at the Great Lodge at the top of the Hold, and he "
                          "wants to see who Thornclaw's been talking about."),
             turn_in_text=("So you're Thornclaw's outsider. Welcome to Timbermaw Hold.\n\nNot many outsiders have "
                           "come this far, and the ones who did usually came to steal honey. Look round as long as "
                           "you like. When you want work, Pathfinder Grosk in the tunnel's Lower Galleries has been "
                           "watching Felpaw for me, and he'll tell you what needs doing."),
             next_quest_id="tm_the_shamans_who_turned", turn_in_npc_id="tm_elder",
             requires_quests=["fw_to_timbermaw_hold"],
             grant_items={"on_accept": [{"item_id": "tm_q_bramblecoat_token", "name": "Bramblecoat's Token",
                                         "description": "A carved wooden bear's head on a cord. The Timbermaw "
                                                        "know whose it is.", "count": 1}]},
             reward_exp=XP[54] // 2, reward_gold=GOLD[54] // 2,
             gear_reward_gear_level=55, gear_reward_rarity="uncommon"),
        Q("tm_the_shamans_who_turned", "The Shamans Who Turned", "tm_pathfinder", 54, 54, tm,
          "Kill the Deadwood Shamans of Felpaw Village for Pathfinder Grosk.",
          [kill("Deadwood Shaman", 6)],
          ("The Elder sent you to me, so you've seen the Hold. The Deadwood were Timbermaw once, and some of them "
           "were born up there. The fel got into them through the water, but it's their shamans who keep it in "
           "them. Every night they feed the fel to the rest, and every night the rest forget a little more of who "
           "they were.\n\nGo " + DOWN + " and south-east to Felpaw Village, and put the shamans down. I'm not "
           "asking you to enjoy it, because I don't."),
          ("The drums stopped last night. Selva heard it from the spring before the wardens did.\n\nWithout their "
           "shamans, some of the Deadwood might remember us. Not many, but I'll take some."),
          zone=ZONE),
        Q("tm_what_the_water_carries", "What the Water Carries", "tm_windtalker", 54, 54, tm,
          "Bring Windtalker Selva Brightpelt Bloodvenom Samples from the Seepage Oozes at Bloodvenom Falls.",
          [{"type": "fetch", "target": SAMPLE[0], "count": 6}],
          ("My spring's water comes down through the mountain from the north, and for three years the Moonglade "
           "side was shut and the water tasted of Felwood. It still does. Something from the Bloodvenom is "
           "getting into it.\n\nThe oozes at Bloodvenom Falls are made of that water. Bring me what's inside them, "
           "sealed, and I'll find out what it is. The falls are " + DOWN + " and a long way south, past "
           "Talonbranch Glade."),
          ("Warm, and it moves. That isn't water any more.\n\nI'll set a jar of it beside the spring and watch "
           "which way it pulls. If it's pulling toward the mountain, we'll need to dam the seep before it reaches "
           "the Hold's own wells."),
          zone=ZONE),
        Q("tm_bears_at_the_mouth", "Bears at the Mouth", "tm_honeykeeper", 54, 54, tm,
          "Kill the Fel-Rotted Bears of North Felwood that come to the tunnel mouth for Honeykeeper Tova.",
          [kill("Fel-Rotted Bear", 8)],
          ("The honey comes down from the Hold's hives in these crates, and every bear in Felwood can smell it from "
           "the tunnel mouth. The healthy ones give up. The fel-rotted ones don't, and two of them came up the "
           "hill last week and took a crate and half of Bramblecoat's coat.\n\nGo " + DOWN + " and thin out "
           "the rotted bears. They wander all over the valley, so you won't have to look hard."),
          ("Bramblecoat says the hill's quiet. He's growing his coat back, and he's not happy about the bald "
           "patch.\n\nTake something sweet for the road. You've earned the first pick of the crates."),
          zone=ZONE),
        Q("tm_seeds_of_the_fel", "Seeds of the Fel", "tm_pathfinder", 54, 54, tm,
          ("Take Fel-Tainted Seed Pouches from the Deadwood Gardeners and kill the Deadwood Pathfinders of Felpaw "
           "Village for Pathfinder Grosk."),
          [{"type": "fetch", "target": SEEDS[0], "count": 6}, kill("Deadwood Pathfinder", 6)],
          ("The Deadwood have started planting. They never planted anything before the newcomers came through, and "
           "now I watch their gardeners from the ridge above Felpaw, going out with full pouches and coming back "
           "with empty ones. Whatever they're planting, it isn't food.\n\nBring me their seed pouches before any "
           "more go in the ground, and put down their pathfinders while you're at it, because they're the ones "
           "who show the gardeners where to dig. Felpaw Village is " + DOWN + " and south-east."),
          ("Look at these. Green right through, every seed. Selva will want to burn them at the spring.\n\nI'll go "
           "back to the ridge tomorrow and see whether they've got any left. I hope they haven't."),
          zone=ZONE),
    ]
    feathers = dict(
        quest_id="tm_deadwood_feathers", title="Deadwood Headdress Feathers", giver_npc_id="tm_featherkeeper",
        zone=ZONE, level_min=54, level_max=54,
        description="Bring Featherkeeper Imna a handful of Deadwood Headdress Feathers from the Deadwood of Felpaw "
                    "Village.",
        objectives=[{"type": "fetch", "target": FEATHER[0], "count": 10, "label": FEATHER[1]}],
        accept_text=("Every Deadwood wears a headdress, and every headdress has Timbermaw feathers in it, from "
                     "when they still knew who they were. I burn them in the waystation's fire, so whatever's left "
                     "of who they were comes home.\n\nBring me a handful whenever you have them, as often as you "
                     "like. The Deadwood are in Felpaw Village, " + DOWN + " and south-east."),
        turn_in_text=("That's a handful come home. I'll burn them tonight, and the Elders will hear about who "
                      "brought them.\n\nBring me more when you've got them."),
        next_quest_id=None, repeatable=True, reward_exp=0, reward_gold=0)
    return qs + [feathers]


def drops():
    """creature -> [drop rows]: feathers from every Deadwood, the quests' items from their own kind."""
    def row(item, chance, amount=1, category="material"):
        iid, name, desc = item[:3]
        r = {"item_id": iid, "name": name, "category": category, "description": desc, "chance": chance}
        if category == "material":
            r.update(amount=amount, icon_id=item[3], sell_price=25)
        return r
    out = {n: [row(FEATHER, 0.35)] for n in DEADWOOD}
    out[GRIMPELT] = [row(FEATHER, 1.0, 3)]
    out["Deadwood Gardener"].append(row(SEEDS, 0.75, category="quest"))
    out["Seepage Ooze"] = [row(SAMPLE, 0.75, category="quest")]
    return out


# ---------------------------------------------------------------------------------------------- write it
def load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))


def save(p, d):
    (ROOT / p).write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    import build_crafted_gear as C
    from crafted_icon_palette import Picker
    from tools.build_tempest_quests import voice_problems
    from tools import handbuilt_timbermaw_tunnel as M
    C.PICKER = Picker()
    bad = []

    # ---- the people
    from tools import handbuilt_timbermaw_hold as HM
    # the tunnel's people from the tunnel's layout; the two who moved up, and the Hold's own, from the Hold's
    pos = {k: (v, ZONE) for k, v in M.NPC_POSITIONS.items()}
    pos.update({k: (v, HOLD) for k, v in HM.NPC_POSITIONS.items()})
    roster = set(VENDORS) | set(AMBIENT) | set(HOLD_VENDORS) | set(HOLD_AMBIENT)
    missing = [k for k in roster if k not in pos]
    spare = [k for k in pos if k not in roster]
    wrong = [k for k in MOVED_UP if pos.get(k, (None, None))[1] != HOLD]
    if missing or spare or wrong:
        raise SystemExit(f"roster and layout disagree: missing {missing}, spare {spare}, not in the Hold {wrong}")
    VENDORS.update(HOLD_VENDORS)
    AMBIENT.update(HOLD_AMBIENT)
    for k, v in list(VENDORS.items()) + list(AMBIENT.items()):
        bad += [f"{k} greeting: {p}" for p in voice_problems(v[-1])]
    vd, ad = load("data/npcs/vendors.json"), load("data/npcs/ambient_npcs.json")
    vby = {v["vendor_id"]: v for v in vd["vendors"]}
    aby = {a["npc_id"]: a for a in ad["npcs"]}
    for vid, (name, race, gender, var, facing, gl, gear, sells, greet) in VENDORS.items():
        (x, y), zone = pos[vid]
        rec = vby.get(vid)
        if rec is None:
            rec = {"vendor_id": vid}
            vd["vendors"].append(rec)
        rec.update(name=name, zone=zone, x=x, y=y, tile_sprite="npc", buys_from_player=True, faction="neutral",
                   gear_level=gl, sells_gear=gear, race=race, gender=gender, appearance_variant=var, facing=facing,
                   greeting=greet)
        rec.setdefault("sells", list(sells))
    for nid, (name, race, gender, var, facing, greet) in AMBIENT.items():
        (x, y), zone = pos[nid]
        rec = aby.get(nid)
        if rec is None:
            rec = {"npc_id": nid}
            ad["npcs"].append(rec)
        rec.update(name=name, zone=zone, x=x, y=y, greeting=greet, gender=gender, race=race,
                   appearance_variant=var, facing=facing)
        rec.update(HOLD_FLAGS.get(nid, {}))
        if nid in HOLD_TRAINERS:
            rec["trains_profession"] = list(HOLD_TRAINERS[nid])
    mid, (mx, my), prop = HOLD_MAILBOX
    box = next((r for r in ad["npcs"] if r["npc_id"] == mid), None)
    if box is None:
        box = {"npc_id": mid}
        ad["npcs"].append(box)
    box.update(name="Mailbox", zone=HOLD, x=mx, y=my, facing="down", race="tauren", appearance_variant=0,
               is_mailbox=True, prop=prop,
               greeting="The Hold's mailbox, between the bank and the auction house. Innkeeper Bortha sorts the "
                        "letters, parcels and whatever the auction house owes you.")
    aby = {a["npc_id"]: a for a in ad["npcs"]}
    aby[THORNCLAW[0]]["greeting"] = THORNCLAW[1]

    # ---- the gear
    fr = load("data/items/faction_rewards.json")
    items = fr["items"]
    from tools.reward_icons import unclash
    for (iid, name, slot, kind, typ, ident, price, flav) in REVERED:
        items[iid], b = BFR.author_unique(iid, name, slot, kind, typ, ident, BFR.BLUE_ILVL, "rare", flav, price)
        items[iid]["faction"] = FID
        unclash(items[iid])
        bad += b
    for (iid, name, slot, kind, typ, ident, price, flav) in EXALTED:
        items[iid], b = BFR.author_unique(iid, name, slot, kind, typ, ident, BFR.EPIC_ILVL, "epic", flav, price)
        items[iid]["faction"] = FID
        bad += b

    # ---- the exalted recipes
    docs = {}
    for rid, trade, name, slot, kind, typ, ident, flav in EXALTED_RECIPES:
        path = ROOT / "data" / BFR.TRADE_FILE[trade] / "recipes.json"
        d = docs.setdefault(path, json.loads(path.read_text(encoding="utf-8")))
        book = d["professions"][trade]["recipes"] if "professions" in d else d["recipes"]
        inputs, tier = BFR.PLACEHOLDER[trade]
        out = {"kind": kind, "slot": slot, "stat_template": C.IDENTITIES[ident][1], "item_level": BFR.EPIC_ILVL,
               "rarity": "epic", "material_tier": tier, "identity": ident, "flavor": flav,
               "fixed_item_level": True, "required_level": BFR.WORN_AT}
        if kind == "weapon":
            out["weapon_type"] = typ
            ident = C.weapon_identity(typ, ident)
        else:
            out["armor_type"] = typ
        item = C.author(rid, {"name": name, "output": dict(out)}, ident, flav)
        bad += C.audit_item("reputation recipe", rid, item)
        item["required_level"] = BFR.WORN_AT
        out["item"] = item
        book[rid] = {"name": name, "inputs": dict(inputs), "skill_required": 300, "output": out,
                     "skill_range": [300, 305, 310, 315], "source": "vendor", "faction": FID,
                     "_rare_ingredients_todo": True}

    # ---- the quests
    qs = quests()
    for q in qs:
        for key in ("description", "accept_text", "turn_in_text"):
            bad += [f"{q['quest_id']} {key}: {p}" for p in voice_problems(q[key])]
    if bad:
        print("FAILED - fix the data, not the check:")
        for b in bad:
            print("  -", b)
        return 1

    # ---- write
    td = load("data/travel/travel_data.json")
    for k, v in HOLD_SERVICES.items():
        td["services"][k] = sorted(set(td["services"].get(k, [])) | set(v))
    save("data/travel/travel_data.json", td)
    tr = load("data/training/trainers.json")
    tr["class_trainers"].setdefault("ct_timbermaw_hold", "*")
    for k, v in HOLD_TRAINERS.items():
        tr["profession_trainers"].setdefault(k, list(v))
    (ROOT / "data/training/trainers.json").write_text(json.dumps(tr, indent=2) + "\n", encoding="utf-8")
    save("data/npcs/vendors.json", vd)
    save("data/npcs/ambient_npcs.json", ad)
    save("data/items/faction_rewards.json", fr)
    for path, d in docs.items():
        path.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    save("data/quests/timbermaw_tunnel.json",
         {"_doc": "The Timbermaw Tunnel's quests and the Deadwood feather turn-in. Written by tools/build_timbermaw_hold.py.",
          "quests": qs})

    dd = load("data/creatures/quest_drops.json")
    ours = {FEATHER[0], SAMPLE[0], SEEDS[0], "tm_q_corrupted_totem_shard"}
    for cre, rows in dd["drops"].items():
        dd["drops"][cre] = [r for r in rows if r["item_id"] not in ours]
    for cre, rows in drops().items():
        dd["drops"].setdefault(cre, []).extend(rows)
    dd["drops"] = {k: v for k, v in dd["drops"].items() if v}
    save("data/creatures/quest_drops.json", dd)

    fd = load("data/factions/factions.json")
    facs = fd["factions"]
    rec = facs.get(FID, {})
    keep_rewards = rec.get("rewards")
    rec.update(json.loads(json.dumps(FACTION)))
    if keep_rewards:
        rec["rewards"] = keep_rewards
    facs[FID] = rec
    # a creature pays one faction: the Deadwood leave the Reclamation's list
    er = facs["emerald_reclamation"]["kill_rep"]["creatures"]
    for n in DEADWOOD + [GRIMPELT]:
        er.pop(n, None)
    rec["quest_rep"]["capstones"] = dict(CAPSTONES)
    rec["quest_rep"]["also"] = list(ALSO)
    rw = rec.setdefault("rewards", {})
    rw["vendor_stock"] = {QM_ID: {
        "friendly": list(SUPPLIES["friendly"]),
        "honored": list(SUPPLIES["honored"]) + MOVED["honored"],
        "revered": MOVED["revered"] + [f"unique:{r[0]}" for r in REVERED],
        "exalted": [f"unique:{r[0]}" for r in EXALTED] + [r[0] for r in EXALTED_RECIPES],
    }}
    rw["_comment"] = ["Gates, not a displayed ladder (the faction panel stays information only).",
                      "TBC-style shelves (tools/build_timbermaw_hold.py, 17 Nov 2026): friendly supplies, honored "
                      "patterns, revered six ilvl 67 blues, exalted three ilvl 73 epics (250-350g) and two epic "
                      "recipes."]
    rw.setdefault("quests", {})
    save("data/factions/factions.json", fd)

    # the moved patterns leave the town shelves
    vd = load("data/npcs/vendors.json")
    moved = set(MOVED["honored"] + MOVED["revered"])
    for v in vd["vendors"]:
        if v.get("sells") and v["vendor_id"] != QM_ID:
            v["sells"] = [s for s in v["sells"] if s not in moved]
    save("data/npcs/vendors.json", vd)

    print(f"Timbermaw Hold: {len(VENDORS) + len(AMBIENT)} people, {len(REVERED) + len(EXALTED)} rep items, "
          f"{len(EXALTED_RECIPES)} exalted recipes, {len(moved)} patterns moved, {len(qs)} quests "
          f"(1 repeatable), {len(drops())} creatures carrying feathers")
    return 0


if __name__ == "__main__":
    sys.exit(main())
