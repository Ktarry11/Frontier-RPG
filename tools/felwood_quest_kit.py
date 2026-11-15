"""Shared pieces for the Felwood quest pass (tools/build_felwood_quests.py).

Zone keys, the people, reward themes and the quest constructor. The objective helpers are the
Tempest Isle pass's own (tools/tempest_quest_kit.py), so both passes write quests the same way.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools import tirisfal_gear                                       # noqa: E402
from tools.tempest_quest_kit import k, boss, explore, deliver, carry, fetch  # noqa: E402,F401
from tools.tirisfal_gear import reward_pack                           # noqa: E402

SF = "south_felwood"
NF = "north_felwood"
ES = "emerald_sanctuary"
JD = "jaedenar"
# elsewhere: where Felwood's quests send you, or where they come from
AE = "ashenvale_east"
TS = "tempest_shallows"
RH = "the_royal_hive"
KV = "khaz_varun,_the_black_hollow"

XP = {50: 3640, 51: 3720, 52: 3800, 53: 3880, 54: 3960, 55: 4040, 56: 4120}
GOLD = {50: 14400, 51: 14700, 52: 15000, 53: 15300, 54: 15600, 55: 15900, 56: 16200}

# ---- the people. Emerald Sanctuary (tools/sync_emerald_sanctuary_npcs.py)
AELYRA, SARANIS, GRUMHALL, THORNBARK = ("es_arch_druid", "es_sentinel_captain", "es_timbermaw_elder",
                                         "es_treant_elder")
NELANTHE, ELM = "es_innkeeper", "es_treant_warden"
NKECHI, TOMASZ, YUKI, ANA = ("es_volunteer_medic", "es_volunteer_carpenter", "es_volunteer_botanist",
                             "es_volunteer_runner")
# ---- the Talonbranch camp in North Felwood (tools/sync_felwood_north_npcs.py)
ELANYA, ARATHEL, BARROWPAW, MARCUS, THORNCLAW = ("fn_talonbranch_captain", "fn_talonbranch_druid",
                                                 "fn_talonbranch_scout", "fn_talonbranch_medic",
                                                 "fn_timbermaw_guard")
# ---- elsewhere
FOREMAN = "warsong_foreman"     # Ashenvale East, the Warsong camp at the foot of the Felwood road
IMANI = "ts_landing_medic"      # Dr. Imani at Ashclaim Landing, Tempest Isle

#: Kyle, 14 Nov: "Keep most quest givers in hubs." The Sanctuary is the town and Talonbranch the camp.
HUB_GIVERS = {AELYRA, SARANIS, GRUMHALL, THORNBARK, NELANTHE, ELM, NKECHI, TOMASZ, YUKI, ANA,
              ELANYA, ARATHEL, BARROWPAW, MARCUS, THORNCLAW}

tirisfal_gear.THEMES.update({
    "reclamation": (["Reclaimer's", "Moonbough", "Glade-Grown", "Cleansed", "Sanctuary"],
                    ["Grown, not made, by the Sanctuary's druids.",
                     "It smells faintly of moonflowers.",
                     "There's a sprig of something green worked into the stitching.",
                     "A volunteer from the camp kitchen patched it, and the patch is the best part."]),
    "sentinel": (["Sentinel", "Fel-Line", "Barricade", "Duskwhisper-Bane", "Watch-Hall"],
                 ["Sentinel issue, made for the north.",
                  "There's a moon stamped inside it, worn half away.",
                  "It came off the rack in the watch-hall with a tag that just says Line.",
                  "Somebody carved a tally of nights on it and stopped at forty."]),
    "timbermaw": (["Timbermaw", "Honey-Wood", "Lodge", "Oakpelt", "Totem-Carved"],
                  ["Timbermaw work, heavy and honest.",
                   "It's been rubbed with beeswax until it shines.",
                   "There's a bear's paw burned into it near the edge.",
                   "The furbolgs say it's lucky. They say that about most things."]),
    "wastes": (["Talonbranch", "Bloodvenom", "Irontree", "Felbrand", "Wasteland"],
               ["It came through the wastes and it shows.",
                "The leather's stained green in one corner and it won't scrub out.",
                "Carried up to Talonbranch in somebody's pack.",
                "There's a burn on it from something that wasn't fire."]),
    "jaedenar": (["Jaedenar", "Black-Gate", "Shadow-Hold", "Pit-Born", "Council-Taken"],
                 ["Taken back out of Jaedenar.",
                  "There's a Council sigil under the strap that somebody tried to scratch off.",
                  "It still smells of the incense they burn in the Hold.",
                  "Highborne work under it, and the Council's work over it."]),
})


def Q(qid, title, giver, lo, hi, theme, desc, objs, accept, done, nxt=None, zone=ES, **engine):
    """A quest. Item level = top level + 1, or + 2 with a boss in it (the Tempest pass's rule)."""
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
