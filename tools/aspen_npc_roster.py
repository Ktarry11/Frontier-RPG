"""
The people of the Aspen Wilderness (13).

Data only - tools/sync_aspen_npcs.py writes these into data/npcs/*.json and takes every coordinate from
the zone module's NPC_POSITIONS, so the layout stays the only place a position is decided.

NOBODY HERE IS FROM HERE, AND THAT IS THE ROSTER'S JOB.

The mountain arrived four years ago. The tauren in it arrived after Thunder Bluff went down, walked south
past Taurajo because Taurajo was already full, and stopped at the first country that had timber in it.
They are a people who lived on open plain and now live under trees, and the roster should sound like that:
they are good at this already and they hate how good they are getting, because competence here is proof
they are not going home.

The orc at the gate is Orgrimmar's, sent to find out what the Warchief now shares a border with. The
goblin on the rim is selling rope to people who have to get down a cliff, which is the purest business
opportunity on the continent and he knows it.

VOICE. Tauren are patient and talk in ground and weather, but these ones are DISPLACED tauren, so the
patience has an edge on it. They measure things in winters. They do not say "home" about this place and
they do not say it about Mulgore either, because one of those is gone and the other is worse. The orc is
blunt and slightly out of his depth. The goblin is delighted.

Nobody here mentions Earth. The player's origin comes up in one greeting out of thirteen - see
claude/quest_writing_guide.md: roughly 10% of content, never the default tone.

(record shapes: VENDORS -> name, race, gender, variant, stock, sells_gear, greeting
                AMBIENT -> name, race, gender, variant, greeting)
"""

# =====================================================================================================
# THE HIGH BASIN - the gate, the Seam, and the top of the Lift. Where everybody arrives.
# =====================================================================================================
ASPEN_AMBIENT = {
    "asp_gate_scout": (
        "Scout Garuk Emberhide", "orc", "male", 3,
        "Warchief wants to know what we border now. I have been here a season and my answer is still "
        "'a mountain', which he will not like."),
    "asp_lift_keeper": (
        "Keeper Nalu Stillgrass", "tauren", "female", 2,
        "I kept the winch on this side for eleven years. The cable still runs out thirty feet and into "
        "granite, and I still come up here and look at it."),
    "asp_seam_watcher": (
        "Watcher Tomak Redhoof", "tauren", "male", 5,
        "Stand with your left foot in red dust and your right in leaf mould. The line is that sharp. "
        "Nothing grew across it. Nothing is going to."),

    # ---- THE RIM. Two people whose whole trade is the drop.
    "asp_rope_master": (
        "Fizzik Quickline", "goblin", "male", 1,
        "Four ways down off this rim and three of them kill you. I sell rope. You see the opportunity "
        "here, I can tell by your face."),
    "asp_rim_runner": (
        "Runner Ash Winterfall", "tauren", "male", 8,
        "I take the chutes. Everyone tells me not to. They are the only ground up here that stays swept, "
        "and a swept path is a fast path if you are not slow."),
    "asp_cave_watch": (
        "Hesta Coldshoulder", "tauren", "female", 7,
        "Something is melting up here and I would like to know how fast. The creek at the bottom runs "
        "higher every spring and nobody downstream has worked out why."),

    # ---- LONGSTAND CAMP, in the Gold Stands. The logging camp.
    "asp_camp_elder": (
        "Elder Mura Longstand", "tauren", "female", 4,
        "We were plains people a very short time ago. Now I can tell you which of these trees will split "
        "clean and which will fight you, and I would rather not have learned it."),
    "asp_logger": (
        "Hateg Barkhand", "tauren", "male", 6,
        "Aspen is not oak and it is not kodo-grass. Green it is heavy and wet, seasoned it is light as "
        "nothing. Everything we knew about wood was about a different wood."),
    "asp_camp_hunter": (
        "Hunter Sani Quietstep", "tauren", "female", 9,
        "Elk up here are bigger than anything on the plain and they do not run the same. You lose them in "
        "timber. I never once lost anything on open ground."),

    # ---- DOWNSLOPE - the meadow and the valley floor
    "asp_meadow_scout": (
        "Scout Owen Tallgrass", "tauren", "male", 11,
        "Elkhorn is the only place in this zone you can see anything. Everywhere else is trees and the "
        "trees are all the same trees. I come up here to remember what distance looks like."),
    "asp_bench_warden": (
        "Warden Gelt Rivermane", "tauren", "male", 10,
        "The beavers had this valley before we did and they have done more with it. Every pond on these "
        "benches is theirs. We just walk between them.\n\nYou came off that blue world, didn't you. Do "
        "they have beavers there? Nobody can ever tell me."),
}

# =====================================================================================================
# VENDORS. A logging camp, so the stock is practical and there is not much of it.
# =====================================================================================================
ASPEN_VENDORS = {
    "asp_camp_cook": (
        "Cook Behr Ashmantle", "tauren", "male", 12,
        ["healing_potion_standard", "bread_and_cheese", "roasted_meat", "mana_potion_standard"], False,
        "Everything here gets smoked because everything here gets wet. You will stop minding the taste."),
    "asp_camp_smith": (
        "Smith Durga Ironhoof", "tauren", "female", 13,
        ["whetstone", "flux_medium", "thread_coarse", "vial_empty"], True,
        "No ore in this mountain worth the walk. I mend what comes up the trail and I charge for the "
        "mending, not the metal."),
}
