"""Shared pieces for the Tempest Isle quest pass (tools/build_tempest_quests.py).

Zone keys, the people, reward themes and the one quest constructor, so the two quest lists
(tempest_quests_shallows.py and tempest_quests_reach.py) cannot disagree about any of them.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools import tirisfal_gear                          # noqa: E402
from tools.build_durotar_quests import kill, fetch       # noqa: E402,F401
from tools.tirisfal_gear import reward_pack              # noqa: E402

TS = "tempest_shallows"
AR = "the_ashen_reach"
CW = "cinderwharf"
KV = "khaz_varun,_the_black_hollow"
ED = "the_emberdeep"

XP = {52: 3800, 53: 3880, 54: 3960, 55: 4040, 56: 4120, 57: 4200, 58: 4280}
GOLD = {52: 15000, 53: 15300, 54: 15600, 55: 15900, 56: 16200, 57: 16500, 58: 16800}

# ---- the people (tools/tempest_npc_roster.py)
GREKKA, DURN, PIM = "ts_landing_bosun", "ts_landing_quartermaster", "ts_landing_surveyor"
HALLA, IMANI, ROZZ = "ts_landing_cook", "ts_landing_medic", "ts_landing_shipwright"
BRON, HESTA, TEODORA, JEX = ("ts_gate_watch", "ts_belt_prospector", "ts_belt_botanist",
                             "ts_shallows_wader")
BRAKKA, TOBBLE, KETTIL = "ar_works_foreman", "ar_works_enginewright", "ar_door_warden"
MIZZI, VARGA, GRIB = "ar_coast_surveyor", "ar_flats_scout", "ar_gate_factor"
RUDDI, ORRIN, KENJI = "ar_works_assayer", "ar_works_powderman", "ar_works_volcanologist"
THANE, VELA, HOGAR, BRENNA = ("cw_thane_ashhold", "cw_quartermaster", "cw_blacksmith",
                              "cw_armoursmith")
MORN, DOLLA, NIX, GEX = "cw_shrine_keeper", "cw_innkeeper", "cw_underwriter", "cw_general_goods"
PELL, TAZZ = "cw_alchemist", "cw_salvage_broker"
SKEZZ, THORA, PRIYA = "cw_harbourmaster", "cw_archivist", "cw_claims_clerk"
MORGRIM = "oh_thane"            # Thane Morgrim, in Onyxhollow under the Black Strand

#: Where a giver's quests count as "from a hub". The landing and the Works are camps with a bed
#: or a yard; Cinderwharf is the town.
HUB_GIVERS = {GREKKA, DURN, PIM, HALLA, IMANI, ROZZ,
              BRAKKA, TOBBLE, RUDDI, ORRIN, KENJI,
              THANE, VELA, HOGAR, BRENNA, MORN, DOLLA, NIX, GEX, PELL, TAZZ, SKEZZ, THORA, PRIYA}

tirisfal_gear.THEMES.update({
    "ashclaim": (["Ashclaim", "Cinderwharf", "Tapped-Vein", "Underwriter's", "Berth-Fee"],
                 ["Ashclaim issue. Dwarf made and goblin priced.",
                  "There's a weigh stamp inside from the Cinderwharf gate.",
                  "Signed out of the Ashclaim stores, with the signature still wet.",
                  "It came over on the supply boat and it's been repaired twice since."]),
    "landing": (["Jetty-Hand's", "Landing", "Saw-Pit", "Tidewalker's", "Long-Tent"],
                ["It smells of tar and crab, like everything at the landing.",
                 "Carried up from the jetty by hand, like everything else there.",
                 "Stitched by lamplight in the long tent.",
                 "Salt has got into the buckles and it isn't coming out."]),
    "greenbelt": (["Greenbelt", "Canopy", "Warm-Ash", "Ashfur", "Botanist's"],
                  ["Dyed green by the jungle, and it won't wash out.",
                   "Lined with gorilla fur that still smells of woodsmoke.",
                   "The vine lashing has put out a leaf since it was tied.",
                   "Teodora labelled it before she let anyone wear it."]),
    "khazvarun": (["Black-Hollow", "Khaz Varun", "Gatewarden's", "Ashhold", "Counting-Hall"],
                  ["Old Dark Iron work, four generations in the dark and still sound.",
                   "There's an Ashhold oath-mark stamped under the strap.",
                   "It came up through the gate of Khaz Varun in somebody's pack.",
                   "The Thane says it should go back down one day."]),
    "cinderflat": (["Cinder-Flat", "Ventwalker's", "Scoria", "Works-Yard", "Steamcrust"],
                   ["Scorched along one edge by a vent that wasn't there the day before.",
                    "Works issue, patched with basilisk hide.",
                    "The brass has gone green from the air off the vents.",
                    "It's warm to the touch and nobody can say why."]),
    "emberdeep": (["Emberdeep", "Caldera", "Lake-Born", "Doorwarden's", "Basalt-Shelf"],
                  ["It was cooled in the Emberdeep's lake and it rings when you tap it.",
                   "There's a seam of red in the metal that moves in a slow light.",
                   "Brought up past the Doorwarden, who wrote it in his book.",
                   "Black glass from the caldera, set by the Cinderwharf smith."]),
    "wreck": (["Wreck-Salvage", "Scourcoast", "Barge-Timber", "Tide-Chart", "Brinebound"],
              ["Salvage from a ship older than the Ashclaim.",
               "The barnacles came off and the marks they left didn't.",
               "It has a berth number burned into it from Cinderwharf.",
               "It was under water for a long time and came up in good order."]),
})


def k(target, n, zone):
    return kill(target, n, zone=zone)


def boss(target, zone):
    return {"type": "kill_boss", "target": target, "count": 1, "zone": zone}


def explore(x, y, label, zone, radius=7):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius, label=label)


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def talk(*topics):
    return dict(type="dialogue", topics=list(topics))


def carry(item_id, name, desc, count=1):
    """What the giver hands you. Pass as grant_items=carry(...)."""
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=count)]}


def Q(qid, title, giver, lo, hi, theme, desc, objs, accept, done, nxt=None, zone=TS, **engine):
    is_boss = any(o["type"] == "kill_boss" for o in objs)
    ilvl = hi + 2 if is_boss else hi + 1
    rarity = "rare" if is_boss else "uncommon"
    mult = 1.3 if is_boss else 1.0
    q = dict(quest_id=qid, title=title, giver_npc_id=giver, zone=zone, level_min=lo, level_max=hi,
             description=desc, objectives=objs,
             reward_exp=int(XP[hi] * mult), reward_gold=int(GOLD[hi] * mult),
             accept_text=accept, turn_in_text=done, next_quest_id=nxt,
             unique_item_defs=reward_pack(qid, theme, ilvl, lo, rarity, 4 if is_boss else 3),
             gear_reward_gear_level=ilvl, gear_reward_rarity=rarity)
    q.update({kk: vv for kk, vv in engine.items() if vv})
    return q
