#!/usr/bin/env python3
"""Add the 16 sheet-5 companions: records in data/npcs/recruits.json, character traits (kits) in
data/npcs/personal_kits.json. Idempotent.

    PYTHONPATH=. python3 tools/build_sheet5_recruits.py            # dry run: placements, waiting, problems
    PYTHONPATH=. python3 tools/build_sheet5_recruits.py --write

Kyle, 18 Nov 2026: "Let's build another 16 recruits... Keep in mind next zone will be deadwind pass. And we can have
some filler. Also will eventually have moonglade and winterspring." Then "Make 5 characters attractive latino
females", "We can put recruits in older zones too! Don't think they ALL have to be end game", and "ensure they have
backstories, and character traits". The roster and the reasons are in claude/recruit_art_prompts_sheet5.md.

WHO THEY ARE is tools/writing/sheet5_recruits.py (BATCH for the record text, TRAITS for the one-line read). WHERE:
tools/build_sheet4_recruits.py's walk, from the tile you arrive on, never past a dungeon's first boss, off the doormat
and off every other person. WHAT THEY CAN DO: the KITS below, one named passive and three abilities each, every one
quoting the line of their story it comes from and built only from mechanics other kits already use (the "engine" note
names it). The abilities that deal damage, heal or shield get five ranks from tools/rank_kit_abilities.py's own rule.

WAITING. Deadwind Pass, Moonglade and Winterspring aren't built yet, so their eight are left out of the files until
those maps exist, and the dry run lists them. The other eight are written now. Until the art is sliced
(tools/asset_pipeline/slice_recruit_sheet5.py) the map draws them as the generic human (ui/tilemap_renderer.py's
fallback), the same as Mohammed was.
"""
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from build_sheet4_recruits import A, P, COST, EDGE  # noqa: E402
from writing.sheet5_recruits import BATCH  # noqa: E402

DEADWIND, MOONGLADE, WINTERSPRING = "Deadwind Pass", "Moonglade", "Winterspring"

#: id -> (name, spec, class, level, zone, gender, colour, row)
ROSTER = {
    "taras_witchhunter":    ("Taras Kovalenko", "witch_hunter_houndmaster", "Witch Hunter", 57, DEADWIND, "male", "#6E6A5E", "front"),
    "lucia_suncleric":      ("Lúcia Ferreira", "sun_cleric_piety", "Sun Cleric", 15, "Crossroads", "female", "#E8C25A", "back"),
    "wes_warrior":          ("Wes Dahlberg", "warrior_protection", "Warrior", 58, DEADWIND, "male", "#8A8F94", "front"),
    "mariana_priest":       ("Mariana Treviño", "priest_holy", "Priest", 57, DEADWIND, "female", "#F2EBD9", "back"),
    "neil_felsworn":        ("Neil Hartley", "felsworn_infernal", "Felsworn", 59, DEADWIND, "male", "#4FA83A", "back"),
    "cristobal_knight":     ("Cristóbal Muñoz", "knight_of_xoroth_hellfire", "Knight of Xoroth", 19, "Camp Taurajo", "male", "#C2401C", "front"),
    "valentina_starcaller": ("Valentina Soto", "starcaller_warden", "Starcaller", 59, MOONGLADE, "female", "#7F9BD6", "front"),
    "faris_shaman":         ("Faris Al-Tamimi", "shaman_restoration", "Shaman", 58, MOONGLADE, "male", "#3C8DAD", "back"),
    "iker_guardian":        ("Iker Etxeberria", "guardian_inspiration", "Guardian", 30, "Arathi West", "male", "#C8102E", "front"),
    "wade_barbarian":       ("Wade Lindgren", "barbarian_headhunting", "Barbarian", 59, WINTERSPRING, "male", "#9C7B55", "front"),
    "ximena_primalist":     ("Ximena Huamán", "primalist_mountain_king", "Primalist", 60, WINTERSPRING, "female", "#7D8A96", "front"),
    "hector_witchdoctor":   ("Héctor Salinas", "witch_doctor_shadowhunting", "Witch Doctor", 36, "Gurbashi Arena", "male", "#5A3D7A", "back"),
    "tobias_paladin":       ("Tobias Keller", "paladin_protection", "Paladin", 56, "Light's Hope Chapel", "male", "#D9C27A", "front"),
    "camila_venomancer":    ("Camila Ortega", "venomancer_stalking", "Venomancer", 43, "Northern Tanaris", "female", "#3F7A3A", "front"),
    "sebastian_bloodmage":  ("Sebastián Cruz", "bloodmage_sanguine", "Bloodmage", 8, "Western Tirisfal", "male", "#9E1B2C", "back"),
    "enzo_cultist":         ("Enzo Marchetti", "cultist_godblade", "Cultist", 34, "Scarlet Monastery Grounds", "male", "#4B2F6B", "front"),
}

KITS = {
    # Kyle, 18 Nov 2026: "Taras better get character traits related to his dog lol. Remember that traits are trump
    # cards with long CDs or some passives." So all four are Kashtan's. The passive was +20/+20; Kyle: "This is
    # too high. Do 5% and 7.5%".
    "taras_witchhunter": (P("Sausage in His Pockets", "'every dog at every checkpoint ... knew his pockets had sausage "
                            "in them'", pet_damage=5, pet_health=7.5), [
        A("taras_witchhunter", "Kashtan", "'a Zone stray he'd been feeding at the checkpoint for years'",
          "live: summon_pet", "summon_pet", "self", 15, 0, 40, "Whistles Kashtan in to fight beside him.",
          summon_pet_template="wolf"),
        A("taras_witchhunter", "Kashtan Won't Go There", "'Kashtan won't set a paw where the ground's gone bad'",
          "live: reveals_intent and sure_target", "debuff", "enemy", 15, 3, 0,
          "Kashtan growls at it. For 3 turns, shows what the target will do next, and the party's attacks on it "
          "can't miss.", reveals_intent="all", sure_target=True),
        A("taras_witchhunter", "Every Dog at Every Checkpoint", "'He knew every dog at every checkpoint by name'",
          "live: mark", "debuff", "enemy_aoe", 15, 5, 30,
          "Taras whistles, and Kashtan and every stray in earshot pile onto one enemy row. Marks it for 5 turns, "
          "and the party deals 30% more damage to marked enemies.", mark={"pct": 30}),
    ]),
    "lucia_suncleric": (P("Out Loud and With Her Whole Heart", "'out loud and with her whole heart'",
                          crit_chance_spell=5, shadow_resistance=10), [
        A("lucia_suncleric", "A Copper and a Blessing", "'She charges a copper and a blessing.'",
          "live: heals_lowest_ally_pct", "spell_damage", "enemy", 12, 0, 75,
          "Holy damage. Heals the most wounded ally for 80% of the damage dealt.", damage_school="holy",
          heals_lowest_ally_pct=80),
        A("lucia_suncleric", "Every Name on the List", "'lit a candle every Sunday for everybody on their street, "
          "by name'", "live: per_use_bonus any", "spell_damage", "enemy", 12, 0, 65,
          "Holy damage. Each use in a fight deals 12% more, up to 60% more.", damage_school="holy",
          per_use_bonus={"pct": 12, "cap": 60, "any": True}),
        A("lucia_suncleric", "The Saint's Medal", "'a silver saint's medal on a chain'",
          "live: death_prevent", "buff", "ally", 15, 4, 100,
          "For 4 turns, a blow that would kill the ally leaves them at 15% health instead.",
          death_prevent={"pct": 15}),
    ]),
    "wes_warrior": (P("Twenty Years in a Suit", "'He did it in a suit, by the procedure, with a partner, every single "
                      "day.'", max_health_pct=10, armor_pct=10, nature_resistance=10), [
        A("wes_warrior", "Suit Check", "'Suit check before you go past the fence.'",
          "live: threat_generation_pct + damage taken reductions", "buff", "self", 12, 4, 100,
          "For 4 turns, Wes draws far more attention and takes 20% less damage.",
          stat_mods={"threat_generation_pct": 200, "physical_damage_taken_pct": -20, "magic_damage_taken_pct": -20}),
        A("wes_warrior", "With a Partner", "'with a partner, every single day'",
          "live: damage_share", "buff", "party", 12, 2, 100,
          "For 2 turns, Wes takes the next hit meant for any ally, at 50% less damage.",
          damage_share={"pct": 100, "reduction_pct": 50, "uses": 1}),
        A("wes_warrior", "Outlives Everybody", "'waste that'll outlive everybody who ever made it'",
          "live: death_prevent", "buff", "self", 15, 4, 100,
          "For 4 turns, a blow that would kill Wes leaves him at 20% health instead.",
          death_prevent={"pct": 20, "lethal_only": False}),
    ]),
    "mariana_priest": (P("To the Millimetre", "'lining up beams to the millimetre'", healing_done=10, mp5=6), [
        A("mariana_priest", "Hit the Tumour and Nothing Else", "'so the radiation hit the tumour and nothing else'",
          "live: low_health_bonus 30% under half health", "heal", "ally", 12, 0, 60,
          "A careful heal on one ally, 30% stronger on an ally below half health.",
          low_health_bonus={"below": 50, "bonus": 30}),
        A("mariana_priest", "Not Afraid of the Word", "'someone who wasn't afraid of the word radiation'",
          "live: dispel and heals_dispelled_damage", "dispel", "party", 12, 0, 0,
          "Takes one harmful effect off every ally and heals them for the damage it would have done.",
          dispel_count=1, dispel_type=["magic", "curse", "poison", "disease"], heals_dispelled_damage=True),
        A("mariana_priest", "The Last Day of Treatment", "'rang a little bell for them on their last day of "
          "treatment'", "live: wounded_allies_bonus_pct", "heal", "party", 12, 0, 60,
          "Heals the party, 25% more for each wounded ally.", wounded_allies_bonus_pct=25),
    ]),
    "neil_felsworn": (P("A Written Plan", "'with a lot of respect and a written plan'", fire_damage_pct=10,
                        shadow_resistance=10), [
        A("neil_felsworn", "The Old Ponds", "'taking apart things that were never meant to be taken apart'",
          "live: summon_pet", "summon_pet", "self", 15, 0, 40, "Brings an infernal down to fight for him.",
          summon_pet_template="infernal"),
        A("neil_felsworn", "Half-Life", "'he makes truly awful jokes about half-lives'",
          "existing (spell_dot on an enemy row)", "spell_dot", "enemy_aoe", 12, 4, 45,
          "Fel fire burns one enemy row over 4 turns.", damage_school="fire"),
        A("neil_felsworn", "He Wants the Dose", "'he wanted to know the dose of everything'",
          "live: reveals_intent", "debuff", "enemy", 12, 5, 100,
          "For 5 turns, shows what the target will do next and lowers every resistance it has by 20.",
          stat_mods={"fire_resistance": -20, "frost_resistance": -20, "nature_resistance": -20,
                     "shadow_resistance": -20, "arcane_resistance": -20, "holy_resistance": -20},
          reveals_intent="all"),
    ]),
    "cristobal_knight": (P("Four Days on the Hills", "'he spent four days on the hills above his mother's house'",
                           fire_resistance=15, max_health_pct=5), [
        A("cristobal_knight", "Cut a Firebreak", "'drilling a dozen young tauren on how to cut a firebreak'",
          "existing (debuff on an enemy row)", "debuff", "enemy_aoe", 12, 3, 100,
          "For 3 turns, the enemies in one row deal 30% less damage.", stat_mods={"damage_dealt_pct": -30}),
        A("cristobal_knight", "Walked Out of It", "'he was the only one who walked out of it'",
          "live: damage_to_heal", "buff", "party", 12, 4, 100,
          "For 4 turns, 30% of the fire damage the party takes heals them instead.",
          damage_to_heal={"pct": 30, "school": "fire"}),
        A("cristobal_knight", "Reckless With Himself", "'reckless with himself but never with anybody else'",
          "live: high_health_bonus", "damage", "enemy", 12, 0, 110,
          "A huge opening blow. Deals 100% more damage to a target above 60% health.",
          high_health_bonus={"above": 60, "bonus": 100}),
    ]),
    "valentina_starcaller": (P("Three Languages a Night", "'in Spanish, English and Portuguese'",
                               crit_chance_physical=5, arcane_damage_pct=10), [
        A("valentina_starcaller", "The Southern Cross First", "'She always found the Southern Cross first'",
          "live: cannot_miss", "damage", "enemy", 12, 0, 75, "A starlit cut that cannot miss.", cannot_miss=True),
        A("valentina_starcaller", "Night Eyes", "'so she doesn't ruin her night eyes'",
          "live: idle_charge", "buff", "self", 12, 4, 30,
          "For 4 turns, each turn Valentina doesn't attack adds 30% to her next blow, up to 120%.",
          idle_charge={"pct": 30, "cap": 120}),
        A("valentina_starcaller", "New Charts", "'she started drawing new charts'",
          "live: reveals_intent and sure_target", "debuff", "enemy", 12, 3, 0,
          "For 3 turns, shows what the target will do next, and the party's attacks on it can't miss.",
          reveals_intent="all", sure_target=True),
    ]),
    "faris_shaman": (P("Look After the Water First", "'you look after the water first and the palms look after "
                       "themselves'", healing_done=10, nature_resistance=10), [
        A("faris_shaman", "Where the Rivers Meet", "'where the Tigris and the Euphrates meet'",
          "live: heals_party_pct_max and party_resource_pct", "heal", "party", 15, 0, 40,
          "Heals the party for 30% of their maximum health and gives back 20% of their resource.",
          heals_party_pct_max=30, party_resource_pct=20),
        A("faris_shaman", "In the Shade of the Palms", "'Ninety palms, a house with a courtyard and a fig tree'",
          "live: on_low_health", "buff", "ally", 12, 4, 100,
          "For 4 turns, the first time the ally drops below 35% health they're healed for 30% of their maximum.",
          on_low_health={"pct": 35, "heal_pct": 30}),
        A("faris_shaman", "Good Water", "'Sit by the water for a while, it's good water.'",
          "live: mana_restore_pct", "restore_resource", "party", 12, 0, 15,
          "Gives every ally back 15% of their mana.", mana_restore_pct=15),
    ]),
    "iker_guardian": (P("Never Been Tired in His Life", "'he's never been tired in his life'", max_health_pct=5,
                        crit_chance_physical=5), [
        A("iker_guardian", "One More Lap", "'he's never met anyone he couldn't shout into running one more lap'",
          "live: grants_turn - the healed ally's turn meter is filled", "heal", "ally", 12, 0, 55,
          "Shouts an ally on. Heals them, and they take a turn straight away.", grants_turn=True),
        A("iker_guardian", "Off the Fronton Wall", "'a fronton wall that was older than the church'",
          "live: consecutive_target_bonus", "damage", "enemy", 12, 0, 70,
          "Each hit on the same target in a row deals 25% more, up to 100% more.",
          consecutive_target_bonus={"pct": 25, "cap": 100}),
        A("iker_guardian", "The Whistle", "'a whistle round his neck and a line of tired farmhands behind him'",
          "live: heals_party_pct_max and party_resource_pct", "heal", "party", 15, 0, 25,
          "Blows the whistle. Heals the party for 15% of their maximum health and gives back 20% of their resource.",
          heals_party_pct_max=15, party_resource_pct=20),
    ]),
    "wade_barbarian": (P("Thirty Winters", "'for thirty winters'", frost_resistance=15, max_health_pct=5), [
        A("wade_barbarian", "Taken Cleanly", "'He wants to take the biggest thing in Winterspring, cleanly'",
          "live: execute_threshold_pct 30 (refused above it) and cast_bonus_pct 200 (triple)", "damage", "enemy",
          12, 0, 90, "A finishing blow on a target below 30% health, for triple damage.",
          execute_threshold_pct=30, cast_bonus_pct=200),
        A("wade_barbarian", "Wind's From the North", "'Wind's from the north tonight.'",
          "existing (miss_chance_pct on every enemy)", "debuff", "all_enemies", 12, 2, 0,
          "For 2 turns, every enemy misses 25% more often.", stat_mods={"miss_chance_pct": 25}),
        A("wade_barbarian", "A Trophy From Every Hunt", "'He keeps a trophy from each hunt'",
          "live: per_use_bonus any", "damage", "enemy", 12, 0, 80,
          "Each time Wade uses it in a fight it deals 12% more, up to 60% more.",
          per_use_bonus={"pct": 12, "cap": 60, "any": True}),
    ]),
    "ximena_primalist": (P("Eleven Summits", "'she summited Huascarán eleven times'", armor_pct=10,
                           max_health_pct=10, frost_resistance=10), [
        A("ximena_primalist", "Roped In", "'you go up with me, roped in, and you do what I tell you'",
          "live: party damage reduction + taunts_all", "buff", "party", 12, 4, 100,
          "For 4 turns, every enemy turns on Ximena, and the party takes 20% less damage.",
          stat_mods={"physical_damage_taken_pct": -20, "magic_damage_taken_pct": -20}, taunts_all=True),
        A("ximena_primalist", "Snow Hole", "'She dug a snow hole, waited out the storm'",
          "live: absorb and absorb_refreshes", "buff", "party", 15, 5, 100,
          "For 5 turns, shields every ally for 70 damage, and the shield refills each turn.",
          absorb=70, absorb_refreshes=True),
        A("ximena_primalist", "The Way a Mountain Does", "'she stands in front of people the way a mountain does'",
          "live: death_prevent", "buff", "self", 15, 4, 100,
          "For 4 turns, a blow that would kill Ximena leaves her at 20% health instead.",
          death_prevent={"pct": 20, "lethal_only": False}),
    ]),
    "hector_witchdoctor": (P("Fifteen Years Under the Mask", "'nobody outside his family ever saw his face'",
                             crit_chance_spell=5, dodge=5), [
        A("hector_witchdoctor", "Off the Top Rope", "'he learned shadow and spirit the way he'd learned to fall'",
          "live: target_health_bonus_pct", "spell_damage", "enemy", 12, 0, 120,
          "Shadow damage, up to 50% more against a target with more health.", damage_school="shadow",
          target_health_bonus_pct=50),
        A("hector_witchdoctor", "The Crowd Loves Him", "'the crowds at the arena love him'",
          "live: mark", "debuff", "enemy_aoe", 12, 5, 30,
          "Marks one enemy row for 5 turns. The party deals 30% more damage to marked enemies.", mark={"pct": 30}),
        A("hector_witchdoctor", "Never Unmasked", "'a luchador who loses his mask loses his name'",
          "live: damage_to_shield", "buff", "self", 12, 3, 100,
          "For 3 turns, 40% of the magic damage Héctor takes becomes a shield on him.",
          damage_to_shield={"pct": 40, "school": "magic"}),
    ]),
    "tobias_paladin": (P("Seven Hundred Years of Repairs", "'the team that's been repairing the cathedral for seven "
                         "hundred years'", armor_pct=12, max_health_pct=8), [
        A("tobias_paladin", "Repointing", "'on the scaffold by the chapel wall, repointing mortar'",
          "live: absorb and absorb_refreshes", "buff", "party", 15, 5, 100,
          "For 5 turns, shields every ally for 70 damage, and the shield refills each turn.",
          absorb=70, absorb_refreshes=True),
        A("tobias_paladin", "Mind the Scaffold", "'Mind the scaffold.'",
          "live: threat_generation_pct + damage taken reductions", "buff", "self", 12, 4, 100,
          "For 4 turns, Tobias draws far more attention and takes 20% less damage.",
          stat_mods={"threat_generation_pct": 200, "physical_damage_taken_pct": -20, "magic_damage_taken_pct": -20}),
        A("tobias_paladin", "All of It's True", "'he says very little, but all of it's true'",
          "live: dispel and returns_dispelled_damage", "dispel", "ally", 12, 0, 0,
          "Draws one harmful effect out of an ally and turns the damage it would have done back on its caster.",
          dispel_count=1, dispel_type=["magic", "curse", "poison", "disease"], returns_dispelled_damage=True),
    ]),
    "camila_venomancer": (P("Ten Thousand Times", "'She's done it ten thousand times, with tweezers and a steady "
                            "hand.'", dodge=5, nature_damage_pct=10), [
        A("camila_venomancer", "Waiting for It to Move", "'She's very good at waiting for something to move'",
          "live: idle_charge", "buff", "self", 12, 4, 30,
          "For 4 turns, each turn Camila doesn't attack adds 30% to her next strike, up to 120%.",
          idle_charge={"pct": 30, "cap": 120}),
        A("camila_venomancer", "Milking the Sting", "'milking them for the venom that makes antivenom'",
          "live: max_stacks and stack_on repeat", "debuff", "enemy", 12, 5, 100,
          "For 5 turns the target takes 15% more damage. Using it again stacks it, up to three times.",
          stat_mods={"physical_damage_taken_pct": 15, "magic_damage_taken_pct": 15}, max_stacks=3,
          stack_on="repeat"),
        A("camila_venomancer", "The Dose, the Timing and the Antidote", "'she asked for the dose, the timing and the "
          "antidote, in that order'", "live: dispel and heals_dispelled_damage", "dispel", "party", 12, 0, 0,
          "Takes one poison or disease off every ally and heals them for the damage it would have done.",
          dispel_count=1, dispel_type=["poison", "disease"], heals_dispelled_damage=True),
    ]),
    "sebastian_bloodmage": (P("Twelve Years at the Grill", "'Sebastián ran the grill at a steakhouse in Palermo'",
                              crit_chance_spell=5, max_health_pct=5), [
        A("sebastian_bloodmage", "Low and Slow", "'He knows meat, blood and fire better than anyone'",
          "existing (spell_dot on an enemy row)", "spell_dot", "enemy_aoe", 12, 4, 45,
          "Blood magic that wears one enemy row down over 4 turns.", damage_school="shadow"),
        A("sebastian_bloodmage", "He Knows When It's Ready", "'He knows when it's ready.'",
          "live: missing_health_bonus_pct", "spell_damage", "enemy", 12, 0, 100,
          "Shadow damage that deals up to 80% more the more health the target is missing.",
          damage_school="shadow", missing_health_bonus_pct=80),
        A("sebastian_bloodmage", "Asado for Twenty", "'he cooked asado for his whole family, twenty people'",
          "live: heals_party_pct_max and party_resource_pct", "heal", "party", 15, 0, 70,
          "Feeds everyone. Heals the party for 30% of their maximum health and gives back 20% of their resource.",
          heals_party_pct_max=30, party_resource_pct=20),
    ]),
    "enzo_cultist": (P("Fourth, Twice", "'came fourth at the Olympic trials, twice'", crit_chance_physical=5,
                       dodge=5), [
        A("enzo_cultist", "Riposte", "'You're watching my feet. Good, that's where everybody should look.'",
          "live: counter_on_miss - a dodged, parried or missed attack is answered with a free basic attack",
          "buff", "self", 12, 4, 0, "For 4 turns, every attack that misses Enzo is answered with a free attack.",
          counter_on_miss=True),
        A("enzo_cultist", "Flèche", "'he fenced sabre for Naples from the age of eight'",
          "live: turn_meter_boost", "buff", "self", 12, 1, 100, "Enzo takes another turn straight away.",
          turn_meter_boost=1.0),
        A("enzo_cultist", "What He Traded", "'he's honest with himself about what he traded'",
          "live: always_crits and cannot_miss", "damage", "enemy", 15, 0, 80,
          "A blade full of shadow that can't miss and always lands a critical hit.", always_crits=True,
          cannot_miss=True),
    ]),
}


def main():
    write = "--write" in sys.argv
    import contextlib
    import io
    from build_sheet3_recruits import arrival_points, bfs, MIN_STEPS_IN, BOSS_CLEAR
    from combat.abilities import get_class_resource
    import rank_kit_abilities as RK
    from tools.build_tempest_quests import voice_problems
    with contextlib.redirect_stdout(io.StringIO()):
        from world.zone_generator import create_all_zones
        zones = create_all_zones()
    from world.ambient_npc_manager import get_ambient_npc_manager
    from world.vendor_manager import get_vendor_manager
    amb, vm = get_ambient_npc_manager(), get_vendor_manager()
    arrive = arrival_points()
    GEAR = json.loads((ROOT / "data/items/spec_gear.json").read_text(encoding="utf-8"))

    rdoc = json.loads((ROOT / "data/npcs/recruits.json").read_text(encoding="utf-8"))
    existing = rdoc["recruits"]
    have = {r["recruit_id"] for r in existing}
    kdoc = json.loads((ROOT / "data/npcs/personal_kits.json").read_text(encoding="utf-8"))
    problems, rows, waiting, no_art = [], [], [], []
    placed_here = {}
    for variant, (rid, (name, spec, cls, level, zname, gender, colour, row)) in enumerate(ROSTER.items(), start=1):
        if rid not in BATCH:
            problems.append(f"{rid}: no prose")
            continue
        if rid not in KITS:
            problems.append(f"{rid}: no kit")
            continue
        if spec not in GEAR:
            problems.append(f"{rid}: no spec {spec}")
        for k_, v in BATCH[rid].items():
            if k_ != "look":
                problems += [f"{rid} {k_}: {p}" for p in voice_problems(v)]
        z = zones.get(zname)
        if z is None:
            waiting.append(f"{rid} ({zname})")
            continue
        if not (ROOT / f"assets/npcs/recruits/{rid}/down.png").exists():
            no_art.append(rid)
        starts = arrive.get(zname) or []
        if not starts:
            problems.append(f"{rid}: no arrival point for {zname}")
            continue
        dist = bfs(z, starts[0])
        bosses = [b for b in (getattr(z, "boss_positions", None) or []) if b]
        if not bosses and getattr(z, "boss_position", None):
            bosses = [z.boss_position]
        boss_d = sorted(d for d in (dist.get((b[0], b[1])) for b in bosses) if d is not None)
        first_boss = boss_d[0] if boss_d else None
        occupied = {(n.x, n.y) for n in list(amb.get_npcs_in_zone(zname)) + list(vm.get_vendors_in_zone(zname))}
        occupied |= {(r.get("x"), r.get("y")) for r in existing if r.get("zone") == zname and r["recruit_id"] != rid}
        occupied |= set(placed_here.get(zname, []))
        road = getattr(z, "road_tiles", None) or set()
        mine = placed_here.get(zname, [])

        def clear(x, y):
            return (all(math.dist((x, y), o) >= 3 for o in occupied if o[0] is not None)
                    and all(math.dist((x, y), o) >= 12 for o in mine))
        cands = [(d, x, y) for (x, y), d in dist.items()
                 if d >= MIN_STEPS_IN and clear(x, y) and (x, y) not in road
                 and (first_boss is None or d < first_boss)
                 and not any(math.dist((x, y), (b[0], b[1])) < BOSS_CLEAR for b in bosses)
                 and EDGE <= x < z.width - EDGE and EDGE <= y < z.height - EDGE
                 and sum((x + dx, y + dy) in dist for dx in (-1, 0, 1) for dy in (-1, 0, 1)) == 9]
        if not cands:
            problems.append(f"{rid}: nowhere clear in {zname}")
            continue
        target = first_boss * 0.55 if first_boss else max(d for d, _x, _y in cands) * 0.35
        mid = (z.width / 2, z.height / 2)
        d, x, y = min(cands, key=lambda c: (abs(c[0] - target) // 6, math.dist((c[1], c[2]), mid)))
        placed_here.setdefault(zname, []).append((x, y))
        p = BATCH[rid]
        rec = {"recruit_id": rid, "name": name, "char_class": cls, "spec": spec, "level": level, "zone": zname,
               "x": x, "y": y, "row": row, "npc_color": colour, "backstory": p["backstory"], "greeting": p["greeting"],
               "gear_theme": GEAR.get(spec, {}).get("role", "melee_dps"),
               "home_town": None, "home_x": None, "home_y": None, "home_note": None,
               "gender": gender, "appearance_variant": variant,
               "background_sections": {k: p[k] for k in ("before", "adjustment", "forward", "now")},
               "look": p["look"]}
        res = getattr(get_class_resource(cls), "value", str(get_class_resource(cls)))
        passive, abilities = json.loads(json.dumps(KITS[rid]))
        for a in abilities:
            a["resource_type"] = res
            if a["ranks"][0]["cost"] is None:
                a["ranks"][0]["cost"] = COST.get(res, 30)
        rows.append((rid, zname, level, x, y, d, first_boss))
        if rid in have:
            existing[:] = [r if r["recruit_id"] != rid else rec for r in existing]
        else:
            existing.append(rec)
        kdoc[rid] = {"name": name, "passives": passive, "abilities": abilities}
    ranked = 0
    for rid, *_ in rows:
        for a in kdoc[rid]["abilities"]:
            if RK.grows(a):
                a["ranks"] = RK.ranks_for(a, kdoc)
                ranked += 1
    for rid, zname, level, x, y, d, fb in rows:
        print(f"  {rid:22s} {level:3d} ({x},{y}) {d:4d} steps in, first boss {fb or '-'}  {zname}")
    print(f"  {len(rows)} placed, {ranked} abilities ranked to 60, {len(problems)} problem(s)")
    if waiting:
        print(f"  waiting for their zone ({len(waiting)}): {', '.join(waiting)}")
    if no_art:
        print(f"  art still to come ({len(no_art)}), drawn as the generic human until then")
    for p_ in problems:
        print("  PROBLEM " + p_)
    if write and not problems:
        (ROOT / "data/npcs/recruits.json").write_text(json.dumps(rdoc, indent=2, ensure_ascii=False) + "\n",
                                                      encoding="utf-8")
        (ROOT / "data/npcs/personal_kits.json").write_text(json.dumps(kdoc, indent=2, ensure_ascii=False) + "\n",
                                                           encoding="utf-8")
        print(f"  written: {len(existing)} recruits, {len([k for k in kdoc if not k.startswith('_')])} kits")
    elif write:
        print("  REFUSING TO WRITE while there are problems")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
