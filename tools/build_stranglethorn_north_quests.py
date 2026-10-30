"""
Grom'gol + Northern Stranglethorn + Rotvine Hollow quest pass (levels 30-34).  Idempotent.

    PYTHONPATH=. python3 tools/build_stranglethorn_north_quests.py
    PYTHONPATH=. python3 tools/build_quest_text.py stranglethorn_north

Writes data/quests/stranglethorn_north.json and adds the fetch drops to data/creatures/quest_drops.json.

WHERE THE PROSE LIVES.  Not here.  tools/quest_text_src/stranglethorn_north.txt is the authored text
and this builder PARSES IT (through tools/build_quest_text.parse, the same parser the overlay
compiler uses) and writes those exact strings into the zone file.  Every other zone keeps two copies -
one in the builder, one in the overlay - and the overlay silently wins, so a rewrite in the builder
does nothing and a rewrite in the overlay drifts from the JSON.  One file, one copy, and re-running
this build never reverts a rewrite because the rewrite is its input.  A missing or short quest entry
in that file is a hard failure here, not a fallback.

NO ESCORTS (Kyle's standing rule, and the only hard "never" in quest design).
NO QUESTS BUILT AROUND RARES - Mistvale Longjaw and Ka'tesh the Last Stairkeeper are the zone's two
named rares and neither is named by any objective in this file.  Rootmaw and Hap'ka the Drowned are
CAVE BOSSES in the Rotvine Hollow table, which is a different thing: a cave boss is the back of a
cave and the chain that walks you to it is the point of the cave.

THE ZONE'S ONE IDEA, AND EVERY QUEST SERVES IT:
                    NOBODY IN GROM'GOL CHOSE STRANGLETHORN.  THEY WERE POSTED TO IT.

Grom'gol is the only settlement in the game that was flown in (tools/handbuilt_gromgol.py: "a supply
line with a fence round it").  Everything in it came off an airship, the jungle takes some of it back
every week, and the camp's whole emotional weather is that of a garrison on the end of a thread.  So
the spine is the SUPPLY LINE, and it is not a background flavour, it is the plot:

    a weekly shortfall of six crates (Pell)            -> the staves are CUT, not chewed
    the thieves at the cutline fork (Mokra)            -> they STACKED it, which is worse
    the boards are being dressed into battens (Dorgun) -> they are SCAFFOLD battens
    and the road itself has three older names (Zul'jana)

By the fourth quest the player understands the first one differently: there was never a theft. There
is a building programme on the Zul'Marosh crag, being paid for out of Grom'gol's lumber.

THREE GENERATIONS OF TROLL STONEWORK - THIS ONE IS THE OLDEST AND THE MOST THOROUGHLY ABANDONED.
Zul'Marosh is a stair-temple up a crag face.  Nobody left alive built it; Zul'jana's own tribe has no
story about building it OR about leaving it.  The Rotvine squat in it and call themselves its keepers.
The quests RAISE and do not answer:
    * the stair ends on a flat court with an empty socket cut in it (Hanzo)
    * the old stone is dressed on five faces, the new work on four - they are copying the outside of
      a thing they never saw finished (Hanzo)
    * the vinespeakers' knot-cord is a record, and every cord is less than three years old: they did
      not keep records until something started them (Zul'jana)
    * the drowned keepers' tokens count stair courses, and the count is BIGGER THAN THE STAIR (the
      cave) - the stair was taller, somebody took the top off it, and the Rotvine are building back
      toward a number they found written on a dead man
Zul'jana's guess "belongs further south, with trolls who never stopped keeping theirs" (the Gurbashi
in Central), and Mokra's finale hands the player a knot-cord that Zul'jana will not translate:
"Ask her again when you are further south than this."  Central answers part, Southern finishes it.

THE EARTH-TRANSPLANT UNDERCURRENT (Kyle: present often enough that a player notices a pattern, never
loud enough to become the subject).  Ten of the eighteen carry it and no two carry it the same way:
    Pell          explains what a tally is, slowly, to someone he assumes has never seen a book
    Mokra         does not ask where you are from, and does not offer a reason for not asking
    Zul'jana      has a name for this road.  Four of them.  You are using the newest and shortest
    Mossa         gives you the plant's real name twice and writes it down the real way regardless
    Zekka         came off the airship listed as cargo himself - the other kind of transplant
    Zul'jana      says somebody will ask you where you were the day the sky changed, and that she
                  will not, because she has had that answer out of eleven of you
    Vrak          asks whether you are staying.  She is not making conversation, she is counting
    Pazzik        a flat Earth reference: your lot gave him the word "timetable" and he kept it
    Mokra         is told, politely, in her own hall, that a thing she paid for is not hers to read
    Rukha         THE EXCEPTION, and the reason the rest reads as deliberate: she says out loud that
                  she does not care where you came from, and nobody else in the camp will

SHAPES, not objective types (Kyle: "vary the SHAPE").  A clerk being wrong in his own handwriting.
A giver who is lying, where the turn-in is how you find out (Zekka).  Somebody covering a mistake
and asking you to leave it out of the hall (Sulaa).  A favour asked as a favour by somebody with no
standing to ask (Teza).  A man who ran the flags on his own judgement four times and intends to put
that in writing before anybody writes a kinder version (Grut).  A quest whose real reward is a word
in a language that is not the camp's (Zul'jana).  A quest where the sensible thing and the asked-for
thing differ (Sulaa; Vrak, who asks you not to look at the ground by the west wall).

WHAT IS NOT HERE, and why:
  dialogue   world/quest_dialogue.py owns the topic content and this pass owns no file in world/.
  craft      no profession bench in Grom'gol; the camp's trade IS the airship.
  deliver    a deliver objective needs a turn_in_npc_id, and the only NPCs south of the seam belong
             to the Central and Southern passes being written in parallel.  Cross-zone pull is done
             with explore gates on the two ends of the Vine Road instead, which costs nothing if the
             other agents rename an NPC.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools import tirisfal_gear                                  # noqa: E402
from tools.build_durotar_quests import kill, fetch               # noqa: E402
from tools.build_quest_text import parse                         # noqa: E402
from tools.tirisfal_gear import reward_pack                      # noqa: E402

OUT = ROOT / "data/quests/stranglethorn_north.json"
TEXT_SRC = ROOT / "tools/quest_text_src/stranglethorn_north.txt"

#: Zone keys are the SLUG OF THE MAP'S DISPLAY NAME, not the handbuilt module's KEY.  record_kill /
#: record_zone_entered compare against what the overworld passes, which is slug(zone.name) - so
#: "northern_stranglethorn", never "stranglethorn_north" (the module key, which nothing at runtime
#: ever sees).  Getting this wrong produces quests that load clean and can never advance.
GG = "gromgol"                      # Grom'gol - every giver in this pass stands in the camp
NS = "northern_stranglethorn"       # the open jungle
RH = "rotvine_hollow"               # the cave in the crag face above the Steps

XP = {30: 2040, 31: 2120, 32: 2200, 33: 2280, 34: 2360}
GOLD = {30: 8400, 31: 8700, 32: 9000, 33: 9300, 34: 9600}

# The zone's gear flavour.  Nothing here is Earth-made: the only things in this jungle that came from
# anywhere else are the airship's lumber, the airship's bad boots, and the people.
tirisfal_gear.THEMES.update({
    "gromgol": (["Berth-Issue", "Grom'gol", "Airborne", "Signed-For", "Camp-Cut"],
                ["Came off the airship in a lot of forty and this is what is left of the forty.",
                 "Stamped on the inside with a requisition number nobody can look up.",
                 "Three years of damp in the stitching and it is still the best thing in the stores.",
                 "Quartermaster's issue. Signed for, issued, and he wants it back."]),
    "mistvale": (["Mistvale", "Stiltstalker", "Brackwater", "Mangrove-Cut", "Longjaw"],
                 ["Salt and fresh water both got into it and neither one left.",
                  "Cut off the water-side root, which is the only part worth taking.",
                  "It has been wet so long that dry is what would ruin it now.",
                  "Something with a very long jaw had hold of this first."]),
    "marosh": (["Zul'Marosh", "Stairkeeper's", "Five-Faced", "Course-Cut", "Stairwarden"],
               ["Dressed on five faces. You only leave the fifth rough if you know what goes on top.",
                "Older than any story anybody in this jungle still tells.",
                "Taken off a relief that was holding a flight of stairs in good order.",
                "The crag has been shedding this for longer than the camp has existed."]),
    "rotvine": (["Rotvine", "Fenrot", "Sourwater", "Causeway", "Gaslit"],
                ["It smells of the fen and it is going to go on smelling of the fen.",
                 "Standing dead and standing water, in about that order.",
                 "Whatever was in it has gone out of it and left the shape.",
                 "Found on the causeway, which is a road the way the fen is a field."]),
    "hollow": (["Drowned", "Sump-Found", "Rootmaw", "Cistern", "Still-Counting"],
               ["It was under water that has not moved in a very long time.",
                "A root grew through this and then grew out the other side.",
                "The hill runs warm and this came out of the warm part.",
                "Taken off somebody who drowned at his post and carried on standing at it."]),
})


# ---------------------------------------------------------------------------------------------------
# objective helpers
# ---------------------------------------------------------------------------------------------------
def k(target, n, zone=NS):
    return kill(target, n, zone=zone)


def kc(target, n):
    """A kill inside the cave. Zone-restricted, because Zul'Marosh Drowned also want to read as the
    Steps' dead and a future pass may pin them on the open crag."""
    return kill(target, n, zone=RH)


def boss(target, zone=RH):
    return dict(type="kill_boss", target=target, count=1, zone=zone)


def explore(zone, x=None, y=None, radius=7):
    o = dict(type="explore", target=zone)
    if x is not None:
        o.update(target_x=x, target_y=y, radius=radius)
    return o


def Q(qid, giver, zone, lo, hi, theme, objs, nxt=None, exp=None, gold=None, **engine):
    """One quest. The four text fields come out of tools/quest_text_src/stranglethorn_north.txt."""
    t = TEXT.get(qid)
    if not t:
        raise SystemExit(f"NO TEXT for {qid} in {TEXT_SRC.name} - the prose is the input, not an "
                         f"afterthought. Add an '@ {qid}' block with Title/D/A/T.")
    missing = [f for f in ("title", "description", "accept_text", "turn_in_text") if not t.get(f)]
    if missing:
        raise SystemExit(f"{qid}: {TEXT_SRC.name} is missing {missing}")
    is_boss = any(o["type"] == "kill_boss" for o in objs)
    ilvl = max(3, hi if is_boss else hi - 1)
    rarity = "rare" if is_boss else "uncommon"
    mult = 1.3 if is_boss else 1.0
    q = dict(quest_id=qid, title=t["title"], giver_npc_id=giver, zone=zone,
             level_min=lo, level_max=hi, description=t["description"], objectives=objs,
             reward_exp=exp if exp is not None else int(XP[hi] * mult),
             reward_gold=gold if gold is not None else int(GOLD[hi] * mult),
             accept_text=t["accept_text"], turn_in_text=t["turn_in_text"], next_quest_id=nxt,
             rewards=reward_pack(qid, theme, ilvl, lo, rarity, 4 if is_boss else 3))
    q.update({kk: vv for kk, vv in engine.items() if vv})
    return q


# Grom'gol givers - data/npcs/ambient_npcs.json + data/npcs/vendors.json, zone=gromgol.
# Every one of them already had a name and a written greeting before this pass; the quests are built
# out of what they were already saying.
MOKRA = "gromgol_commander"          # Overseer Mokra - "The camp holds. That is the whole of my report"
ZEKKA = "gromgol_berth_master"       # Berth-Master Zekka - "Everything you see here came off that airship"
GRUT = "gromgol_signalman"           # Signalman Grut - "Two flags means they are coming in"
HANZO = "gromgol_scout"              # Scout Hanzo - "I do not recommend the walk"
VRAK = "gromgol_south_sentry"        # Sentry Vrak - "Road's that way"
TEZA = "gromgol_wounded_runner"      # Runner Teza - "Took the long way round the fen"
SULAA = "gromgol_field_medic"        # Field-Medic Sulaa - "Bring them to me either way"
ASHI = "gromgol_cartographer"        # Mapmaker Ashi - "The map is wrong. It is less wrong than it was"
ZULJANA = "gromgol_troll_attache"    # Attache Zul'jana - "It has a name. Several."
PELL = "gromgol_storesman"           # Storesman Pell - "Count it in, count it out"
DORGUN = "gromgol_smith"             # Smith Dorgun - "Damp eats steel faster than any enemy"
RUKHA = "gromgol_innkeeper"          # Innkeeper Rukha - "Twelve bunks and a fire"
PAZZIK = "gromgol_flight_master"     # Windrider-Keeper Pazzik - "the Baron charges me to land"
MOSSA = "gromgol_herbalist"          # Herbalist Mossa (vendor) - "I sell the other half"

# Walkable clearings in tools/handbuilt_stranglethorn_north.py: CLEARINGS/TRAMPLED, which is where the
# explore gates sit.  (34,68) is the Marosh ford; (100,177) is the south seam into Central.
FORK, FORD, SEAM = (116, 90), (34, 68), (100, 177)
LAGOON, COURT, MOUTH = (42, 136), (134, 60), (148, 42)
FEN_LANDING, COAST_NORTH = (172, 122), (32, 34)


# ===================================================================================================
# THE SUPPLY LINE - the spine.  Six crates a week, and by the fourth quest it was never a theft.
# ===================================================================================================
def supply_line():
    return [
        Q("stn_the_weekly_shortfall", PELL, GG, 30, 31, "gromgol",
          [k("Vinecrest Raptor", 8), fetch("gromgol_crate_stave", 5)],
          nxt="stn_cut_not_chewed"),
        Q("stn_cut_not_chewed", MOKRA, GG, 30, 31, "gromgol",
          [k("Zul'Marosh Stonehand", 10), explore(NS, *FORK)],
          nxt="stn_what_the_wood_is_for"),
        Q("stn_what_the_wood_is_for", DORGUN, GG, 31, 32, "marosh",
          [fetch("dressed_stair_batten", 6), k("Thornback Ape", 6)],
          nxt="stn_one_road_four_names"),
        # The payoff is a WORD, not a reward: the road's third name. Both ends of the Vine Road, and
        # the south gate of it is the seam into Central Stranglethorn.
        Q("stn_one_road_four_names", ZULJANA, GG, 32, 33, "marosh",
          [k("Coilvine Python", 8), explore(NS, *FORD), explore(NS, *SEAM)]),
    ]


# ===================================================================================================
# MISTVALE LAGOON - brackish mangrove country south-west of the camp.  Three quests, three lies:
# a wrong cut, a wrong diagnosis, and a crate that is not stores.
# ===================================================================================================
def lagoon():
    return [
        Q("stn_the_other_half", MOSSA, GG, 30, 31, "mistvale",
          [fetch("mistvale_bark_strip", 7), k("Mangrove Stiltstalker", 6)]),
        Q("stn_standing_water", SULAA, GG, 31, 32, "mistvale",
          [k("Mistvale Crocolisk", 8), explore(NS, *LAGOON)]),
        # Zekka is lying on accept and the turn-in is the only way the player finds out.  He is also
        # the zone's other kind of transplant: he came off that airship himself, in the cargo column.
        Q("stn_including_me", ZEKKA, GG, 31, 32, "mistvale",
          [fetch("berth_manifest_crate", 4), k("Bloatspawn Toad", 6)]),
    ]


# ===================================================================================================
# ZUL'MAROSH STEPS - the oldest troll work in the jungle, and the one nobody can account for.
# A chain that gets quieter and worse: a ruin that is growing, a stair that ends in an empty socket,
# and a record that is three years old.
# ===================================================================================================
def steps():
    return [
        Q("stn_less_wrong_than_it_was", ASHI, GG, 31, 32, "marosh",
          [explore(NS, *COURT), explore(NS, *MOUTH)],
          nxt="stn_the_stair_ends_in_a_socket"),
        Q("stn_the_stair_ends_in_a_socket", HANZO, GG, 32, 33, "marosh",
          [k("Zul'Marosh Stairwarden", 10), fetch("marosh_course_stone", 5)],
          nxt="stn_nobody_left_who_built_it"),
        Q("stn_nobody_left_who_built_it", ZULJANA, GG, 32, 33, "marosh",
          [k("Zul'Marosh Vinespeaker", 9), fetch("vinespeaker_knot_cord", 5)]),
    ]


# ===================================================================================================
# ROTVINE FEN - the rotting east, downhill of the Hollow's outflow.  Both of these are about somebody
# having been wrong on their own initiative and deciding to write it down.
# ===================================================================================================
def fen():
    return [
        Q("stn_the_long_way_round", TEZA, GG, 32, 33, "rotvine",
          [explore(NS, *FEN_LANDING), k("Fenrot Creeper", 8)],
          nxt="stn_three_flags"),
        Q("stn_three_flags", GRUT, GG, 33, 34, "rotvine",
          [k("Sourwater Ooze", 8), fetch("rotgas_bladder", 5)]),
    ]


# ===================================================================================================
# ROTVINE HOLLOW - the cave.  Three quests, and the middle one is where the Steps thread turns over:
# the drowned keepers' tokens count more courses than the stair has.
# Gated on Zul'jana's Steps quest, so the player arrives already knowing who the Rotvine are not.
# ===================================================================================================
def hollow():
    return [
        Q("stn_the_hill_runs_warm", HANZO, GG, 33, 34, "hollow",
          [explore(RH), kc("Rotvine Strangler", 8)],
          nxt="stn_what_was_holding_it_back"),
        Q("stn_what_was_holding_it_back", ZULJANA, GG, 33, 34, "hollow",
          [boss("Rootmaw"), kc("Zul'Marosh Drowned", 5)],
          nxt="stn_hapka_still_counting",
          requires_quests=["stn_nobody_left_who_built_it"]),
        # Mokra closes the cave for the reason the camp would actually close it: the berth will not
        # moor in a stink.  The knot-cord she hands the attache is the handoff to Central/Southern.
        Q("stn_hapka_still_counting", MOKRA, GG, 34, 34, "hollow",
          [boss("Hap'ka the Drowned")]),
    ]


# ===================================================================================================
# OUTSIDE ANY CHAIN - the gate, the hearth and the roost.  Rukha is the warm one on purpose.
# ===================================================================================================
def standalone():
    return [
        Q("stn_keep_to_it", VRAK, GG, 30, 31, "gromgol",
          [k("Greenpelt Panther", 8)]),
        Q("stn_twelve_bunks_and_a_fire", RUKHA, GG, 30, 31, "gromgol",
          [fetch("buttress_resin", 6), k("Rootgrubber Boar", 6)]),
        Q("stn_the_baron_charges_me_to_land", PAZZIK, GG, 33, 34, "gromgol",
          [explore(NS, *COAST_NORTH), k("Vinecrest Raptor", 10)]),
    ]


# ===================================================================================================
# DROPS.  Every fetch item has at least one source and most have two, so no objective is hostage to a
# single creature's spawn weight.
# ===================================================================================================
FETCH_DROPS = {
    "Vinecrest Raptor": [("gromgol_crate_stave", "Grom'gol Crate Stave",
                          "A board off a camp crate. The end of it is flat, which is not what a "
                          "raptor leaves you.", 0.46)],
    "Zul'Marosh Stonehand": [("gromgol_crate_stave", "Grom'gol Crate Stave",
                              "Camp lumber, carried off the road and not yet dressed.", 0.38),
                             ("dressed_stair_batten", "Dressed Stair Batten",
                              "Thin, cut to one length, with a lashing notch at the end. Somebody is "
                              "standing on these to reach something.", 0.46),
                             ("marosh_course_stone", "Loose Course Stone",
                              "Old grey stair stone, dressed on five faces.", 0.28)],
    "Thornback Ape": [("dressed_stair_batten", "Dressed Stair Batten",
                       "Taken off the cutline, where the apes come down for anything that smells of "
                       "the camp.", 0.36),
                      ("buttress_resin", "Buttress Resin",
                       "Prised out of the bark of a buttress tree. It burns wet, which is the whole "
                       "miracle of it.", 0.30)],
    "Mangrove Stiltstalker": [("mistvale_bark_strip", "Mangrove Bark Strip",
                               "Off the water-side root. Dead'wa, if you are going to say it properly.",
                               0.48)],
    "Bloatspawn Toad": [("mistvale_bark_strip", "Mangrove Bark Strip",
                         "Trodden into the root mud and still good for a wash.", 0.32),
                        ("rotgas_bladder", "Rotgas Bladder",
                         "It comes up out of the rot full and goes back down empty, and in between the "
                         "fen smokes.", 0.30)],
    "Mistvale Crocolisk": [("berth_manifest_crate", "Berth Manifest Bundle",
                            "Oilcloth, lashed, with a requisition number on the outside and a name in "
                            "the cargo column.", 0.44)],
    "Zul'Marosh Stairwarden": [("marosh_course_stone", "Loose Course Stone",
                                "Fallen rather than laid. The fifth face is still rough.", 0.46)],
    "Zul'Marosh Vinespeaker": [("vinespeaker_knot_cord", "Vinespeaker's Knot-Cord",
                                "A record, in knots, and not one knot in it is three years old.",
                                0.48)],
    "Sourwater Ooze": [("rotgas_bladder", "Rotgas Bladder",
                        "They go through these like a boot through ice, and the camp calls the result "
                        "a fire.", 0.46)],
    "Rootgrubber Boar": [("buttress_resin", "Buttress Resin",
                          "Rooted out of the bark and trodden into the mulch, which is where you will "
                          "be getting it from.", 0.44)],
}


def audit(quests):
    """FAIL THE BUILD on a reward spread that favours one armour class or one weapon type.

    tirisfal_gear.specs() samples all four armour kinds per pack, so a single quest is never lopsided
    - but eighteen packs drawn off eighteen different quest-id seeds can still land badly in
    aggregate, and nobody notices a zone that quietly hands plate wearers twice what it hands cloth.
    This is the Southern Needles loot audit moved up a level: same thresholds, counted over the whole
    zone's rewards instead of one content file's drop table.

    Also enforces the standing content rules that are cheap to check and expensive to ship wrong:
    no escort-shaped objective, no named rare as an objective, no stat numbers in the prose.
    """
    rew = [r for q in quests for r in q["rewards"]]
    arm, wep = {}, {}
    for r in rew:
        if r.get("armor_type"):
            arm[r["armor_type"]] = arm.get(r["armor_type"], 0) + 1
        if r.get("weapon_type"):
            wep[r["weapon_type"]] = wep.get(r["weapon_type"], 0) + 1
    errs = []

    # ---- armour spread: four classes, and no class more than 1.6x the thinnest -------------------
    if set(arm) != {"cloth", "leather", "mail", "plate"}:
        errs.append(f"armour does not cover all four classes: {arm}")
    elif max(arm.values()) > 1.6 * min(arm.values()):
        errs.append(f"armour spread lopsided (max > 1.6x min): {arm}")

    # ---- weapons: at least four distinct types, none of them more than a third of the weapons ----
    if len(wep) < 4:
        errs.append(f"fewer than four distinct weapon types offered: {wep}")
    elif max(wep.values()) > max(2, 0.34 * sum(wep.values())):
        errs.append(f"one weapon type dominates: {wep}")

    # ---- casting vs melee share, the Southern Needles band ---------------------------------------
    casting = sum(1 for r in rew if {"intellect", "spirit"} & set(r.get("primary_stats") or {}))
    if not 0.30 <= casting / len(rew) <= 0.60:
        errs.append(f"casting share {casting}/{len(rew)} outside 30-60%")

    # ---- standing rules -------------------------------------------------------------------------
    RARES = {"Mistvale Longjaw", "Ka'tesh the Last Stairkeeper"}
    for q in quests:
        for o in q["objectives"]:
            if o["type"] not in {"kill", "kill_boss", "fetch", "gather", "explore", "deliver",
                                 "craft", "dialogue", "story"}:
                errs.append(f"{q['quest_id']}: unknown objective type {o['type']!r}")
            if o.get("target") in RARES:
                errs.append(f"{q['quest_id']}: objective names the named rare {o['target']!r}")
        blob = " ".join((q["description"], q["accept_text"], q["turn_in_text"])).lower()
        for word in ("escort", "follow me", "protect me as", "see me safely", "accompany me"):
            if word in blob:
                errs.append(f"{q['quest_id']}: escort-shaped prose ({word!r})")
        for tell in ("brave adventurer", "these lands", "ancient evil", "darkness stirs",
                     "hangs in the balance", "take your pick", "thank you, friend"):
            if tell in blob:
                errs.append(f"{q['quest_id']}: banned phrase {tell!r}")
        import re
        if re.search(r"\b\d+\s*(armou?r|stamina|strength|agility|intellect|spirit|damage|dps)\b",
                     blob):
            errs.append(f"{q['quest_id']}: stat numbers in the prose")

    # ---- chains: every next_quest_id and requires_quests resolves, and nothing loops -------------
    ids = {q["quest_id"] for q in quests}
    for q in quests:
        for req in q.get("requires_quests", []):
            if req not in ids:
                errs.append(f"{q['quest_id']}: requires unknown quest {req!r}")
    nxt = {q["quest_id"]: q.get("next_quest_id") for q in quests}
    for start in ids:
        seen, cur = [], start
        while cur:
            if cur in seen:
                errs.append(f"chain loop: {' -> '.join(seen + [cur])}")
                break
            seen.append(cur)
            if cur not in ids:
                errs.append(f"{seen[-2]}: next_quest_id {cur!r} is not a quest in this file")
                break
            cur = nxt.get(cur)

    if errs:
        raise SystemExit("BUILD FAILED:\n  " + "\n  ".join(errs))
    print(f"  audit ok: {len(rew)} rewards, armour {arm}, weapons {wep}, "
          f"casting {casting}/{len(rew)}")


def main():
    global TEXT
    if not TEXT_SRC.exists():
        raise SystemExit(f"{TEXT_SRC} is missing - it is the prose, and it is this build's input.")
    TEXT = parse(str(TEXT_SRC))

    quests = supply_line() + lagoon() + steps() + fen() + hollow() + standalone()
    extra = set(TEXT) - {q["quest_id"] for q in quests}
    if extra:
        raise SystemExit(f"{TEXT_SRC.name} has text for quests this builder does not build: "
                         f"{sorted(extra)}")
    audit(quests)

    OUT.write_text(json.dumps(
        {"_notes": "Grom'gol / Northern Stranglethorn / Rotvine Hollow quest pass (2026-10-30). "
                   "Generated by tools/build_stranglethorn_north_quests.py, which READS its prose "
                   "from tools/quest_text_src/stranglethorn_north.txt - edit the text there and "
                   "re-run, do not hand-edit this file.",
         "quests": quests}, indent=2, ensure_ascii=False) + "\n")

    # THE LOADERS READ data["drops"], NOT THE TOP LEVEL (both combat_engine._get_loot_item_drops and
    # quest_locator.item_sources do json.load(f).get("drops", {})) - a creature key written beside
    # "drops" instead of inside it is read by nothing and the item never drops.  Cost the Aspen pass
    # 23 un-droppable quest items.  Append-only per creature, and re-read immediately before writing
    # because the Central and Southern passes are adding their own keys to this same file.
    dp = ROOT / "data/creatures/quest_drops.json"
    drops = json.loads(dp.read_text())
    table = drops.setdefault("drops", drops)
    for cre, rows in FETCH_DROPS.items():
        cur = [d for d in table.get(cre, []) if d["item_id"] not in {r[0] for r in rows}]
        for (iid, nm, desc, ch) in rows:
            cur.append({"item_id": iid, "name": nm, "category": "quest", "description": desc,
                        "chance": ch})
        table[cre] = cur
    dp.write_text(json.dumps(drops, indent=2, ensure_ascii=False) + "\n")

    chains = sum(1 for q in quests if q.get("next_quest_id"))
    print(f"Northern Stranglethorn quests: {len(quests)} total, {chains} chained links, "
          f"{len(FETCH_DROPS)} fetch sources, "
          f"{sum(len(v) for v in FETCH_DROPS.values())} drop rows, text from {TEXT_SRC.name}")


TEXT = {}

if __name__ == "__main__":
    main()
