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

THE EARTH-TRANSPLANT UNDERCURRENT (Kyle, 2026-10-30: about 30% of the zone, "a note, never the
theme").  The first pass ran it at eleven of eighteen, which is 61% and is the theme.  So the second
pass trimmed two of the lightest - Pell no longer explains what a tally is to somebody he assumes has
never seen a book, and Mokra no longer pointedly does not ask where you are from - and added four.
NINE OF THIRTY.  No two carry it the same way and none of them is an aside:
    Zul'jana      says somebody will ask you where you were the day the sky changed, and that she
                  will not, because she has had that answer out of eleven of you (stn_one_road_four_names)
    Zekka         came off the airship listed in the cargo column himself (stn_including_me)
    Vrak          asks whether you are staying.  She is not making conversation, she is counting
                  (stn_keep_to_it)
    Rukha         THE EXCEPTION, and the reason the rest reads as deliberate: she says out loud that
                  she does not care where you came from (stn_twelve_bunks_and_a_fire)
    Pazzik        your lot gave him the word "timetable" and he kept it, free
                  (stn_the_baron_charges_me_to_land)
  -- second pass --
    Ukko          had a sergeant who said your sort could not be taught the canopy.  He was wrong and
                  he was not stupid, and half the camp still says it worse.  Ukko has stopped
                  correcting them because he got tired (stn_nothing_they_have_fought_climbs)
    Ghulrak       half his garrison says the Hillsbrad fences came down the year the sky changed.
                  They came down the year the Syndicate noticed nobody was watching.  "But a man
                  would rather blame a sky he saw change than a neighbour he has to live beside."
                  (stn_two_roosts_one_ledger)
    Vrak          asks you to carry the thing precisely because you are not on the camp's name post.
                  "That is not an insult. That is the reason." (stn_in_the_count)
    Ashi          a survey clerk who came through the same season you did has been correcting her
                  sheets for a year and a half and has never been south of the Barrens - and he
                  learned the jungle off the sheets he is correcting (stn_a_mark_for_a_thing_still_being_made)

SHAPES, not objective types (Kyle: "vary the SHAPE").  A clerk being wrong in his own handwriting.
A giver who is lying, where the turn-in is how you find out (Zekka).  Somebody covering a mistake
and asking you to leave it out of the hall (Sulaa).  A favour asked as a favour by somebody with no
standing to ask (Teza).  A man who ran the flags on his own judgement four times and intends to put
that in writing before anybody writes a kinder version (Grut).  A quest whose real reward is a word
in a language that is not the camp's (Zul'jana).  A quest where the sensible thing and the asked-for
thing differ (Sulaa; Vrak, who asks you not to look at the ground by the west wall).

OBJECTIVE TYPES.  The first pass used four of seven (kill 16, fetch 8, explore 9, kill_boss 2); the
second added the three it had skipped and the zone now runs all seven: kill 22, explore 10, fetch 8,
gather 5, deliver 5, dialogue 3, kill_boss 2.  What changed:
  dialogue   world/quest_dialogue.py now merges a per-zone module by name, so the topic content for
             this zone is world/quest_dialogue_stranglethorn_north.py and nobody else writes it.
             Three quests, three topics each, and all three are quests where the content IS the
             conversation - there is nothing to fetch that would say it.
  deliver    five, now that there is a far end.  Four of them are the flight thread north; the fifth
             crosses the camp, because Zekka will not be the one holding that paper when Mokra reads
             it.  Each one's item comes from the quest's own grant_items on_accept.
  gather     five.  GATHER does not consume at turn-in, so it is for the things the giver wants put
             to use rather than filed: vine into a climbing frame, haunches into a feed trough.
  craft      still none.  There is no profession bench in Grom'gol; the camp's trade IS the airship.
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
    # -- second pass (the three new themes). Deliberately NOT more prefixes on "gromgol": the name
    # picks are seeded off the theme's prefix LIST, so lengthening an existing list silently renames
    # the first pass's reward items. New quests get new themes instead and the 18 stay byte-stable.
    "roost": (["Long-Haul", "Windrider's", "Relay", "Tower-Lit", "Open-Water", "Ledgered"],
              ["Carried on a wyvern that was over open water when it got wet, and it shows.",
               "Flight-store issue, and the flight store is a crate under a tarpaulin.",
               "Smells of feed block, wet leather and goblin arithmetic.",
               "It has crossed more of this world in a week than its owner did in a life."]),
    "drill": (["Drill-Ground", "Hand-Over-Hand", "Third-Direction", "Palisade", "Frame-Cut"],
              ["Worn through at the shoulder, where a climbing frame takes the weight.",
               "Drillmaster's issue. It has been thrown at somebody at least once.",
               "Spliced twice, because nothing in this camp gets spliced only once.",
               "Green vine still in the stitching, cut long and cut fresh."]),
    "pens": (["Feeding-Hour", "Handler's", "Rail-Worn", "Haunch-Cut", "Pen-Side"],
             ["It smells of raptor, and that is not something that washes out of a thing.",
              "Cut off the pen rail, where the paint has gone from two seasons of leaning.",
              "Boar leather, tanned by somebody who had other work on that day.",
              "Nothing in the pens has a name, including this."]),
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


def gather(target, n):
    """GATHER, not FETCH: ObjectiveType.GATHER counts the item in the bag and does NOT consume it at
    turn-in (world/quest.py's own comment on the enum). Used where the giver wants to see the stuff
    rather than keep it - Ukko's vine coil goes into his frame, Ashi's chips go into a chart note."""
    return dict(type="gather", target=target, count=n)


def deliver(item_id, label):
    """DELIVER: one carried item, counted out of the bag like FETCH and consumed by turn_in_npc_id.
    The item has to be handed over by somebody's grant_items or the objective can never start - see
    tools/audit_quests.py's DELIVER branch - so every deliver here is paired with a grant() below."""
    return dict(type="deliver", target=item_id, count=1, label=label)


def dialogue(*topics):
    """DIALOGUE: completed by asking the GIVER about every topic id (not the turn-in NPC - see
    QuestManager.get_in_progress_dialogue_quests, which indexes quests_by_giver). Every topic id
    below is authored in world/quest_dialogue_stranglethorn_north.py; a topic with no authored text
    renders no button at all and makes the quest uncompletable, which is why they are asserted."""
    return dict(type="dialogue", topics=list(topics))


def grant(item_id, name, desc):
    return {"on_accept": [{"item_id": item_id, "name": name, "description": desc, "count": 1}]}


def Q(qid, giver, zone, lo, hi, theme, objs, nxt=None, exp=None, gold=None, seed=None, **engine):
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
             # NOT "rewards".  QuestManager._build_quest reads unique_item_defs and never looks at a
             # key called "rewards" - every quest in southern_needles.json, aspen.json and three
             # others authored its gear under "rewards" and awards NOTHING, which
             # tools/audit_quests.py reports as "the quest awards no gear".  Those files are not
             # this pass's to fix; this one is written the way the engine reads.
             # gear_reward_gear_level must also be set, or get_gear_choices is never called at all.
             # `seed` only reseeds tirisfal_gear.specs's RNG; it is not the quest id and nothing at
             # runtime sees it. It exists because specs() picks a quest's armour classes off that
             # seed alone and takes no view of the zone's aggregate, so thirty quest ids can land on
             # a spread the audit below (rightly) fails - leather 20 to cloth 12 on the first attempt
             # at this pass. Salting three seeds is the honest fix; renaming a quest to move its loot
             # around would change an authored id, and widening the audit's threshold would just stop
             # it noticing. Only the three salted quests carry it and the first eighteen do not.
             unique_item_defs=reward_pack(seed or qid, theme, ilvl, lo, rarity, 4 if is_boss else 3),
             gear_reward_gear_level=ilvl, gear_reward_rarity=rarity)
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
# Second pass: the camp's two remaining written-but-questless NPCs.  Same principle as the first
# fourteen - both of them already had a line and the quests are built out of what they were saying.
UKKO = "gromgol_drillmaster"         # Drillmaster Ukko - "Half of them have never fought anything that climbs"
KOZZA = "gromgol_beast_handler"      # Beast-Handler Kozza - "They are not tame. They are fed."

# THE FAR END OF THE CROSS-ZONE THREAD.  Real, already-placed flight masters, a continent away, both
# of whom already had the exact line this thread needs.  Nothing is invented at the far end and no
# other pass's roster is touched: these two give and collect, and that is all.
GHULRAK = "tarren_mill_flight_master"    # Wind-Rider Ghulrak, Tarren Mill - "all fences... until you are over it"
ODO = "sepulcher_flight_master"          # Bat Handler Odo, the Sepulcher - "Fly the Rearguard's route"
TM, SEP = "tarren_mill", "sepulcher"     # their quests' own zone keys, as data/quests/hillsbrad.json spells them

# Walkable clearings in tools/handbuilt_stranglethorn_north.py: CLEARINGS/TRAMPLED, which is where the
# explore gates sit.  (34,68) is the Marosh ford; (100,177) is the south seam into Central.
FORK, FORD, SEAM = (116, 90), (34, 68), (100, 177)
LAGOON, COURT, MOUTH = (42, 136), (134, 60), (148, 42)
FEN_LANDING, COAST_NORTH = (172, 122), (32, 34)
#: The ninth clearing, unused by the first pass: "a cutline camp" above the fork.  Checked walkable
#: against tools/handbuilt_stranglethorn_north.build_layout()'s own L.z.is_walkable, not tile_kind.
CUTLINE_CAMP = (86, 90)


# ===================================================================================================
# THE SUPPLY LINE - the spine.  Six crates a week, and by the fourth quest it was never a theft.
# ===================================================================================================
def supply_line():
    return [
        Q("stn_the_weekly_shortfall", PELL, GG, 30, 31, "gromgol",
          [k("Vinecrest Raptor", 8), fetch("gromgol_crate_stave", 6)],
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
# SECOND PASS (2026-10-30): twelve more, 18 -> 30.
#
# WHAT THIS PASS IS FIXING ABOUT THE FIRST ONE.  The first eighteen used four objective types out of
# seven - kill 16, fetch 8, explore 9, kill_boss 2 - and skipped dialogue because topic content lived
# in one shared file that three parallel passes would have fought over. It does not any more
# (world/quest_dialogue.py merges a per-zone module by name), so this pass owns
# world/quest_dialogue_stranglethorn_north.py and uses DIALOGUE, DELIVER and GATHER.
#
# AND IT IS LEAVING THE ZONE.  The first pass used explore gates on the Vine Road's two ends as a
# cross-zone gesture because every NPC south of the seam belonged to a pass being written at the same
# time. North is nobody's in-flight work: Tarren Mill and the Sepulcher have been built for months and
# both of their flight masters already say, in their own written greetings, the thing this thread
# needs them to say. So the thread goes north, on a wyvern, and the far end is real.
# ===================================================================================================


# ---------------------------------------------------------------------------------------------------
# THE SECOND ROOST - four quests, three zones.  Pazzik pays Baron Revilgaz to land in Booty Bay and has
# paid it every week since the camp came down.  stn_the_baron_charges_me_to_land established there is
# no roost on the north coast, so he stops looking for a near one and prices the longest route anybody
# has proposed: Grom'gol to Tarren Mill in one hop, with a dead man's bat tower holding the middle.
#
# Gated behind the quest that produced the problem, so a player who has not had "canopy to the
# waterline" out of Pazzik never sees the answer to it.
# ---------------------------------------------------------------------------------------------------
def second_roost():
    return [
        Q("stn_the_long_haul", PAZZIK, GG, 33, 34, "roost",
          [gather("longhaul_feed_block", 6), k("Thornback Ape", 6)],
          nxt="stn_a_name_at_the_other_end",
          requires_quests=["stn_the_baron_charges_me_to_land"]),
        # First deliver in the zone, and it goes a continent north. turn_in_npc_id is Ghulrak, so the
        # turn-in text is in HIS voice, not Pazzik's - the handoff is the quest.
        Q("stn_a_name_at_the_other_end", PAZZIK, GG, 33, 34, "roost",
          [deliver("pazzik_route_proposal",
                   "Put Pazzik's route in Wind-Rider Ghulrak's hand at Tarren Mill")],
          nxt="stn_two_roosts_one_ledger", turn_in_npc_id=GHULRAK,
          grant_items=grant("pazzik_route_proposal", "Pazzik's Proposed Route",
                            "A schedule and a price, written small and fast on both sides of one "
                            "card. The price is the part anybody will argue with.")),
        # Given at Tarren Mill, asked at Tarren Mill, collected at the Sepulcher. The dialogue has to
        # sit on the GIVER (get_in_progress_dialogue_quests indexes quests_by_giver), which is exactly
        # right here: Ghulrak is the man who has flown the middle of this route.
        Q("stn_two_roosts_one_ledger", GHULRAK, TM, 33, 34, "roost",
          [dialogue("fences_from_the_air", "why_not_bats", "what_the_jungle_sends_north"),
           deliver("ghulrak_relay_endorsement",
                   "Carry Ghulrak's endorsement to Bat Handler Odo at the Sepulcher")],
          nxt="stn_the_relay_signed", turn_in_npc_id=ODO,
          grant_items=grant("ghulrak_relay_endorsement", "Ghulrak's Endorsement",
                            "An orc's hand under a goblin's arithmetic, and the honest part is the "
                            "line naming what he cannot solve.")),
        # And back to Grom'gol, which closes the thread where it opened.
        Q("stn_the_relay_signed", ODO, SEP, 34, 34, "roost",
          [deliver("odo_countersigned_route",
                   "Take the countersigned route back to Windrider-Keeper Pazzik at Grom'gol")],
          turn_in_npc_id=PAZZIK,
          grant_items=grant("odo_countersigned_route", "The Countersigned Route",
                            "Three hands on one page now. The last one wrote his condition under "
                            "the signature instead of over it, which was not an accident.")),
    ]


# ---------------------------------------------------------------------------------------------------
# DRILLMASTER UKKO - the camp's first dialogue quest, and the only job in Grom'gol that had to change
# because of who the airship started bringing.  He is fair about it; the camp is not, and he says so.
# ---------------------------------------------------------------------------------------------------
def drill_ground():
    return [
        Q("stn_nothing_they_have_fought_climbs", UKKO, GG, 30, 31, "drill",
          [dialogue("what_climbs", "what_the_drill_is_for", "who_you_get"),
           k("Thornback Ape", 8)],
          nxt="stn_the_third_direction"),
        Q("stn_the_third_direction", UKKO, GG, 31, 32, "drill",
          [gather("strangler_vine_coil", 7), k("Coilvine Python", 8)]),
    ]


# ---------------------------------------------------------------------------------------------------
# BEAST-HANDLER KOZZA - a pair that runs feed first and conversation second, because the conversation
# only means anything once you have stood in the pens.  The middle topic quietly corroborates the
# supply-line chain (regular, slow, uphill, same hour every week) without resolving any of it.
# ---------------------------------------------------------------------------------------------------
def pens():
    return [
        Q("stn_not_tame_fed", KOZZA, GG, 30, 31, "pens",
          [gather("rootgrubber_haunch", 8), k("Greenpelt Panther", 6)],
          nxt="stn_what_the_pens_know"),
        Q("stn_what_the_pens_know", KOZZA, GG, 32, 33, "pens",
          [dialogue("the_difference", "the_raptors_on_the_road", "what_she_will_not_do")],
          seed="stn_what_the_pens_know#14"),
    ]


# ---------------------------------------------------------------------------------------------------
# FOUR THAT HANG OFF THE FIRST PASS.  Each one is a consequence somebody in the first eighteen walked
# away from, and three of them are gated on the quest that created the consequence.  None of the
# original eighteen is edited to make these work - requires_quests points backwards only.
# ---------------------------------------------------------------------------------------------------
def consequences():
    return [
        # Zekka's grant is the other end of stranglethorn_south's bb_fipples_decision, which delivers
        # a berth grant TO him. He will not carry it to Mokra. Deliver inside the camp, forty paces.
        Q("stn_signed_for_twice", ZEKKA, GG, 31, 32, "gromgol",
          [deliver("gromgol_berth_grant", "Put the berth grant in Overseer Mokra's hand")],
          turn_in_npc_id=MOKRA,
          grant_items=grant("gromgol_berth_grant", "Grom'gol's Berth, In Perpetuity",
                            "The Baron's stamp, a rate, and a date in a much smaller hand "
                            "underneath. The date is the interesting one.")),
        Q("stn_four_reports_and_a_boot", SULAA, GG, 32, 33, "rotvine",
          [gather("sourwater_fen_tuber", 7), k("Bloatspawn Toad", 6)],
          seed="stn_four_reports_and_a_boot#9", requires_quests=["stn_standing_water"]),
        # Vrak asked you once not to look at the ground outside the west wall. This is her asking for
        # the thing instead, and the turn-in is Rukha, who keeps the only honest list of the camp.
        Q("stn_in_the_count", VRAK, GG, 31, 32, "gromgol",
          [deliver("vrak_burial_request", "Take Vrak's request to Innkeeper Rukha"),
           k("Greenpelt Panther", 8)],
          turn_in_npc_id=RUKHA, seed="stn_in_the_count#4", requires_quests=["stn_keep_to_it"],
          grant_items=grant("vrak_burial_request", "Vrak's Request",
                            "Four lines, unsealed, from somebody who has never written to anybody "
                            "in this camp before.")),
        Q("stn_a_mark_for_a_thing_still_being_made", ASHI, GG, 32, 33, "marosh",
          [gather("fourface_relief_chip", 6), explore(NS, *CUTLINE_CAMP)],
          requires_quests=["stn_less_wrong_than_it_was"]),
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


# SECOND-PASS DROPS GO TO A STAGING FILE, NOT data/creatures/quest_drops.json.  The Central and
# Southern Stranglethorn passes are writing that same file right now and three read-modify-writes to
# one JSON blob is how content disappears without an error. Same row shape as the real file's "drops"
# table; Kyle merges the three staging files himself.
STAGING_DROPS = {
    "Rootgrubber Boar": [("longhaul_feed_block", "Pressed Feed Block",
                          "Boar fat and jungle grain beaten together until it goes hard. A wyvern "
                          "eats before a long crossing, not during one.", 0.40),
                         ("rootgrubber_haunch", "Rootgrubber Haunch",
                          "Off the leg, not the gut. A raptor that gets slop remembers it.", 0.48)],
    "Thornback Ape": [("longhaul_feed_block", "Pressed Feed Block",
                       "Taken back off an ape that took it off the feed store first.", 0.34)],
    "Coilvine Python": [("strangler_vine_coil", "Coil of Strangler Vine",
                         "Cut long and cut fresh, before it goes woody. Exactly the colour of the "
                         "thing that was lying along it.", 0.46)],
    "Rotvine Strangler": [("strangler_vine_coil", "Coil of Strangler Vine",
                           "Green and wet and still trying. The cave grows it faster than the road "
                           "does.", 0.38)],
    "Fenrot Creeper": [("sourwater_fen_tuber", "Sourwater Tuber",
                        "Pale, about a thumb long, and it pulls the water out of whatever you pack "
                        "it against.", 0.44)],
    "Sourwater Ooze": [("sourwater_fen_tuber", "Sourwater Tuber",
                        "Come up out of the rot with the ooze on it. It still works.", 0.30)],
    "Zul'Marosh Stairwarden": [("fourface_relief_chip", "Four-Faced Relief Chip",
                                "Off the NEW work, which is dressed on four faces by somebody who "
                                "has never seen the stair finished.", 0.44)],
    "Zul'Marosh Stonehand": [("fourface_relief_chip", "Four-Faced Relief Chip",
                              "Carried down off the scaffold and dropped on the cutline.", 0.30)],
}


def check_dialogue(quests):
    """FAIL THE BUILD on a dialogue topic with no authored text.

    A DIALOGUE objective completes when every id in `topics` has been asked, and QuestDialogScreen
    only renders a button for a topic world.quest_dialogue.get_topic can answer. So an unauthored
    topic is not a missing line of flavour, it is a quest that loads clean, accepts clean and can
    never be handed in - the same failure shape as Ashenvale's four null-target explores.
    """
    from world.quest_dialogue import get_topic
    missing = [f"{q['quest_id']}:{t}" for q in quests for o in q["objectives"]
               if o["type"] == "dialogue" for t in o["topics"]
               if not get_topic(q["quest_id"], t)]
    if missing:
        raise SystemExit("BUILD FAILED: unauthored dialogue topics (no button renders, quest is "
                         "uncompletable):\n  " + "\n  ".join(missing))


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
    rew = [r for q in quests for r in q["unique_item_defs"]]
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

    quests = (supply_line() + lagoon() + steps() + fen() + hollow() + standalone()
              + second_roost() + drill_ground() + pens() + consequences())
    extra = set(TEXT) - {q["quest_id"] for q in quests}
    if extra:
        raise SystemExit(f"{TEXT_SRC.name} has text for quests this builder does not build: "
                         f"{sorted(extra)}")
    check_dialogue(quests)
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
    #
    # AND SECOND PASS: THAT WRITE IS NOW OPT-IN.  The first pass's fourteen rows are already in the
    # live file (checked), so re-running this builder would have rewritten the whole of a file that
    # two other content passes are editing right now, for no change at all - a read-modify-write
    # whose only possible effect is to lose somebody else's concurrent key.  So the merge needs
    # --merge-drops, and the second pass's own rows go to tools/staging_drops_stranglethorn_north.json
    # below instead of here.
    dp = ROOT / "data/creatures/quest_drops.json"
    missing = {r[0] for rows in FETCH_DROPS.values() for r in rows} - {
        d["item_id"] for rows in json.loads(dp.read_text()).get("drops", {}).values() for d in rows}
    if "--merge-drops" in sys.argv:
        drops = json.loads(dp.read_text())
        table = drops.setdefault("drops", drops)
        for cre, rows in FETCH_DROPS.items():
            cur = [d for d in table.get(cre, []) if d["item_id"] not in {r[0] for r in rows}]
            for (iid, nm, desc, ch) in rows:
                cur.append({"item_id": iid, "name": nm, "category": "quest", "description": desc,
                            "chance": ch})
            table[cre] = cur
        dp.write_text(json.dumps(drops, indent=2, ensure_ascii=False) + "\n")
        print(f"  merged {sum(len(v) for v in FETCH_DROPS.values())} first-pass rows into "
              f"{dp.name}")
    elif missing:
        print(f"  NOTE: {len(missing)} first-pass drop item(s) are NOT in {dp.name} "
              f"({sorted(missing)}) - re-run with --merge-drops when no other pass is writing it.")

    sp = ROOT / "tools/staging_drops_stranglethorn_north.json"
    staged = {"_notes": "SECOND-PASS quest drops for Northern Stranglethorn, staged for merge into "
                        "data/creatures/quest_drops.json's \"drops\" table. Written here and not "
                        "there because the Central and Southern Stranglethorn passes are editing "
                        "that file concurrently. Generated by "
                        "tools/build_stranglethorn_north_quests.py.",
              "drops": {cre: [{"item_id": iid, "name": nm, "category": "quest",
                               "description": desc, "chance": ch}
                              for (iid, nm, desc, ch) in rows]
                        for cre, rows in STAGING_DROPS.items()}}
    sp.write_text(json.dumps(staged, indent=2, ensure_ascii=False) + "\n")

    chains = sum(1 for q in quests if q.get("next_quest_id"))
    print(f"Northern Stranglethorn quests: {len(quests)} total, {chains} chained links, "
          f"{len(FETCH_DROPS)} fetch sources, "
          f"{sum(len(v) for v in FETCH_DROPS.values())} drop rows, text from {TEXT_SRC.name}")


TEXT = {}

if __name__ == "__main__":
    main()
