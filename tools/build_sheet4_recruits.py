#!/usr/bin/env python3
"""Add the 16 sheet-4 companions: records in data/npcs/recruits.json, character traits in data/npcs/personal_kits.json.

    PYTHONPATH=. python3 tools/build_sheet4_recruits.py            # dry run: placements and problems
    PYTHONPATH=. python3 tools/build_sheet4_recruits.py --write

Kyle, 16 Nov 2026: "we add another 16 to the game to fill in what's missing". The art landed 17 Nov 2026 (sliced by
tools/asset_pipeline/slice_recruit_sheet4.py), and "They can be spread out as per our previous discussions": the
places in claude/recruit_art_prompts_sheet4.md, with the Plaguelands moves since then:
  - Sorrow Hill is gone and the Order of the Pale Flame lives in the Bulwark, so Bruno and Joaquín stand there.
  - Crown Guard is inside Light's Hope Chapel, so Isla is there.
  - Graham goes to the Pale Watch and Dale to the Eastern Plaguelands, so no town holds three.

WHO THEY ARE is tools/writing/sheet4_recruits.py. WHERE: tools/build_sheet3_recruits.py's walk (from the tile you
arrive on, never past a dungeon's first boss, off the doormat, off every other person). WHAT THEY CAN DO: the KITS
below, one or two named passives and three abilities each, every one quoting the line of their story it comes from
and built only from mechanics other kits already use and the engine already runs (the "engine" note names it). The
abilities that deal damage, heal or shield get five ranks from tools/rank_kit_abilities.py's own rule (1, 15, 30, 45,
60, the last one sized past the class kits at 60), applied to these sixteen only.
"""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from writing.sheet4_recruits import BATCH  # noqa: E402

#: id -> (name, spec, class, level, zone, gender, colour, row)
ROSTER = {
    "rhys_ranger":         ("Rhys Morgan", "ranger_farstrider", "Ranger", 31, "Stonetalon West", "male", "#4E7D3A", "back"),
    "gunnar_barbarian":    ("Gunnar Sigurðsson", "barbarian_ancestry", "Barbarian", 35, "Hammerfall", "male", "#A9746E", "front"),
    "reka_necromancer":    ("Réka Farkas", "necromancer_animation", "Necromancer", 51, "The Black Strand", "female", "#D8D2C4", "back"),
    "ramiro_primalist":    ("Ramiro Quispe", "primalist_geomancy", "Primalist", 51, "Onyxhollow", "male", "#B8860B", "back"),
    "graham_warlock":      ("Graham Ashworth", "warlock_affliction", "Warlock", 52, "The Pale Watch", "male", "#6B8E23", "back"),
    "elie_bloodmage":      ("Elie Khoury", "bloodmage_fleshweaver", "Bloodmage", 53, "Khaz Varun, the Black Hollow", "male", "#A0202A", "back"),
    "bruno_templar":       ("Bruno Teixeira", "templar_zealot", "Templar", 53, "The Bulwark", "male", "#F0E6C8", "front"),
    "joaquin_suncleric":   ("Joaquín Duarte", "sun_cleric_valkyrie", "Sun Cleric", 54, "The Bulwark", "male", "#E3B448", "front"),
    "astrid_starcaller":   ("Astrid Lindqvist", "starcaller_sentinel", "Starcaller", 54, "North Felwood", "female", "#9DB8E0", "back"),
    "luka_stormbringer":   ("Luka Perić", "stormbringer_maelstrom", "Stormbringer", 54, "Tempest Shallows", "male", "#2E8B8B", "back"),
    "zofia_cultist":       ("Zofia Nowak", "cultist_corruption", "Cultist", 55, "Western Plaguelands North", "female", "#5B3A8C", "back"),
    "omar_venomancer":     ("Omar Saleh", "venomancer_venom", "Venomancer", 55, "The Royal Hive", "male", "#5E8C31", "back"),
    "santiago_runemaster": ("Santiago Ríos", "runemaster_engravement", "Runemaster", 56, "The Ashen Reach", "male", "#3D7DD8", "front"),
    "emiliano_pyromancer": ("Emiliano Vargas", "pyromancer_draconic", "Pyromancer", 56, "Cinderwharf", "male", "#D9471E", "back"),
    "isla_witchhunter":    ("Isla Fraser", "witch_hunter_boltslinger", "Witch Hunter", 57, "Light's Hope Chapel", "female", "#B5492C", "back"),
    "dale_reaper":         ("Dale Brekke", "reaper_harvest", "Reaper", 58, "Eastern Plaguelands East", "male", "#7A5C3A", "front"),
}


def A(rid, name, frm, engine, et, tt, cd, dur, value, desc, cost=None, stat_mods=None, instant=True, **extra):
    """One kit ability, rank 1. The ranks past it are added by rank_kit_abilities' rule in main()."""
    first = rid.split("_")[0]
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    a = {"ability_id": f"personal_{first}_{slug}", "name": name, "from": frm, "engine": engine,
         "effect_type": et, "target_type": tt, "resource_type": None, "cooldown": cd, "duration": dur,
         "stat_mods": stat_mods or {}, "description": desc,
         "ranks": [{"rank": 1, "level_req": 1, "cost": cost, "effect_value": value}], "is_instant": instant}
    a.update(extra)
    return a


def P(name, frm, **stats):
    return {"_name": name, "_from": frm, **stats}


KITS = {
    "rhys_ranger": (P("She Came Through With Him", "'his hawk came through with him'", pet_damage=15, pet_health=15), [
        A("rhys_ranger", "Flown at Weddings", "'Rhys flew hawks at weddings in the Brecon Beacons'",
          "live: summon_pet", "summon_pet", "self", 12, 0, 40, "Calls Tegan, his hawk, to fight beside him.",
          summon_pet_template="war_falcon"),
        A("rhys_ranger", "Weather Off the Beacons", "'He still checks the sky for weather the way he did at home'",
          "live: high_health_bonus", "ranged_damage", "enemy", 10, 0, 80,
          "A heavy shot. Deals 40% more damage to a target above full health's worth of its own pool (above 100%).",
          high_health_bonus={"above": 100, "bonus": 40}),
        A("rhys_ranger", "The Hawk's Opinion", "'he trusts the hawk's opinion of a stranger more than his own'",
          "live: reveals_intent and sure_target", "debuff", "enemy", 12, 3, 0,
          "For 3 turns, shows what the target will do next, and the party's attacks on it cannot miss.",
          reveals_intent="all", sure_target=True),
    ]),
    "gunnar_barbarian": (P("Akureyri Winters", "'He landed in snow, which helped.'", max_health_pct=10,
                           frost_resistance=10), [
        A("gunnar_barbarian", "Second Row", "'He played second row for a rugby club'",
          "live: high_health_bonus", "damage", "enemy", 12, 0, 110,
          "A huge opening hit. Deals 100% more damage to a target above 60% health.",
          high_health_bonus={"above": 60, "bonus": 100}),
        A("gunnar_barbarian", "Something You Should Try", "'Sit down, I've got something you should try.'",
          "live: heals_party_pct_max and party_resource_pct", "heal", "party", 15, 0, 40,
          "Passes the keg round. Heals the party for 30% of their maximum health and gives back 20% of their "
          "resource.", heals_party_pct_max=30, party_resource_pct=20),
        A("gunnar_barbarian", "Before a Fight", "'anyone who toasts their ancestors before a fight has the right idea'",
          "live: per_use_bonus any", "damage", "enemy", 10, 0, 65,
          "Each time Gunnar uses it in a fight it deals 12% more, up to 60% more.",
          per_use_bonus={"pct": 12, "cap": 60, "any": True}),
    ]),
    "reka_necromancer": (P("Twelve Years of Small Adjustments", "'with patience and a lot of small adjustments'",
                           crit_chance_spell=5, shadow_resistance=10), [
        A("reka_necromancer", "One Frame at a Time", "'moving puppets one frame at a time until they looked alive'",
          "live: per_use_bonus any", "spell_damage", "enemy", 10, 0, 70,
          "Shadow damage. Each use in a fight deals 15% more, up to 75% more.", damage_school="shadow",
          per_use_bonus={"pct": 15, "cap": 75, "any": True}),
        A("reka_necromancer", "Where She'd Gone Wrong With the Elbow", "'she said she knew exactly where she'd gone "
          "wrong with the elbow'", "live: immediate repeat_last", "buff", "self", 12, 0, 100,
          "Casts her last ability again at once.", immediate={"action": "repeat_last"}),
        A("reka_necromancer", "Everything Holds Still", "'until they looked alive'",
          "existing (debuff on an enemy row)", "debuff", "enemy_aoe", 12, 3, 100,
          "For 3 turns, the enemies in one row deal 30% less damage.", stat_mods={"damage_dealt_pct": -30}),
    ]),
    "ramiro_primalist": (P("The Mountain Talks Before It Moves", "'the mountain talks before it moves'",
                           armor_pct=10, nature_resistance=10), [
        A("ramiro_primalist", "The Rock Settling", "'You can hear the rock settling.'",
          "live: delayed", "damage", "enemy_aoe", 12, 2, 100,
          "Brings the rock down on one enemy row two turns from now.", delayed={"turns": 2, "mult": 1.0}),
        A("ramiro_primalist", "Timbered the Old Way", "'to timber a drift the way his father did'",
          "live: absorb and absorb_refreshes", "buff", "party", 15, 5, 100,
          "For 5 turns, shields every ally for 70 damage, and the shield refills each turn.",
          absorb=70, absorb_refreshes=True),
        A("ramiro_primalist", "Where the Vein Runs", "'he hears the rock the way they do'",
          "live: armor_ignore_pct", "damage", "enemy", 10, 0, 95,
          "A blow along the grain. Ignores 60% of the target's armour.", armor_ignore_pct=60),
    ]),
    "graham_warlock": (P("Nineteen Years of Night Shifts", "'a hospice nurse in Lancashire for nineteen years'",
                         mp5=6, shadow_resistance=10), [
        A("graham_warlock", "A Slow Ending", "'a slow ending can be a kind one if somebody pays attention'",
          "existing (spell_dot on an enemy row)", "spell_dot", "enemy_aoe", 10, 4, 45,
          "Shadow damage over 4 turns to every enemy in one row.", damage_school="shadow"),
        A("graham_warlock", "Sit Down a Minute", "'Sit down a minute if you need to.'",
          "live: wounded_allies_bonus_pct", "heal", "party", 12, 0, 60,
          "Heals the party, 25% more for each wounded ally.", wounded_allies_bonus_pct=25),
        A("graham_warlock", "He Knows the Signs", "'learned that a slow ending can be a kind one if somebody pays attention'",
          "live: reveals_intent", "debuff", "enemy", 10, 5, 100,
          "For 5 turns, shows what the target will do next and lowers every resistance it has by 20.",
          stat_mods={"fire_resistance": -20, "frost_resistance": -20, "nature_resistance": -20,
                     "shadow_resistance": -20, "arcane_resistance": -20, "holy_resistance": -20},
          reveals_intent="all"),
    ]),
    "elie_bloodmage": (P("The One the Nervous Patients Asked For", "'he was the one the nervous patients asked for'",
                         healing_done=10, max_health_pct=5), [
        A("elie_bloodmage", "Find the Vein", "'blood listens to him now'",
          "live: heals_pct_max and requires_target_below_pct", "heal", "ally", 12, 0, 50,
          "Heals an ally below 25% health for 50% of their maximum health.",
          heals_pct_max=50, requires_target_below_pct=25),
        A("elie_bloodmage", "A Clean Draw", "'He heals with it'",
          "live: dispel and returns_dispelled_damage", "dispel", "ally", 12, 0, 0,
          "Draws one harmful effect out of an ally and turns the damage it would have done back on its caster.",
          dispel_count=1, dispel_type=["magic", "curse", "poison", "disease"], returns_dispelled_damage=True),
        A("elie_bloodmage", "Tourniquet", "'He came through with a tourniquet in his pocket'",
          "live: on_low_health", "buff", "ally", 12, 4, 100,
          "For 4 turns, the first time the ally drops below 35% health they are healed for 30% of their maximum.",
          on_low_health={"pct": 35, "heal_pct": 30}),
    ]),
    "bruno_templar": (P("Twenty-Three Fights", "'twenty-three fights with eighteen wins'", max_health_pct=10,
                        crit_damage_physical=20), [
        A("bruno_templar", "Ground and Pound", "'he fights like the bell's about to go'",
          "live: consecutive_target_bonus", "damage", "enemy", 10, 0, 70,
          "Each hit on the same target in a row deals 25% more, up to 100% more.",
          consecutive_target_bonus={"pct": 25, "cap": 100}),
        A("bruno_templar", "Walked Out Beside Him", "'he walked out of it beside Rory Callahan'",
          "live: damage_share", "buff", "party", 12, 2, 100,
          "For 2 turns, Bruno takes the next hit meant for any ally, at 50% less damage.",
          damage_share={"pct": 100, "reduction_pct": 50, "uses": 1}),
        A("bruno_templar", "Very Hard to Knock Down", "'very hard to knock down'",
          "live: death_prevent", "buff", "self", 15, 4, 100,
          "For 4 turns, a blow that would kill Bruno leaves him at 20% health instead.",
          death_prevent={"pct": 20, "lethal_only": False}),
    ]),
    "joaquin_suncleric": (P("He Listened", "'he was patient and he listened'", healing_done=10,
                            shadow_resistance=10), [
        A("joaquin_suncleric", "The Same Hands", "'Now he heals with the same hands, and he fights with them too'",
          "live: heals_lowest_ally_pct", "damage", "enemy", 10, 0, 75,
          "A sunlit blow. Heals the most wounded ally for 80% of the damage dealt.", heals_lowest_ally_pct=80),
        A("joaquin_suncleric", "A Prisoner He'd Been Told to Break", "'sitting with a prisoner he'd been told to break'",
          "existing (harmless_to_source)", "debuff", "enemy", 12, 3, 0,
          "For 3 turns, the target cannot harm Joaquín.", stat_mods={"harmless_to_source": 1}),
        A("joaquin_suncleric", "What He Carries", "'he carries what he did there without asking anyone to carry it'",
          "live: fallen_allies_bonus_pct", "heal", "party", 15, 0, 55,
          "Heals the party, 40% more for each fallen ally.", fallen_allies_bonus_pct=40),
    ]),
    "astrid_starcaller": (P("Lying in Snow Waiting", "'lying in snow waiting for the sky to do something'",
                            crit_chance_spell=5, arcane_damage_pct=10), [
        A("astrid_starcaller", "Long Exposure", "'very good at waiting for the right moment'",
          "live: idle_charge", "buff", "self", 12, 4, 30,
          "For 4 turns, each turn Astrid does not attack adds 30% to her next shot, up to 120%.",
          idle_charge={"pct": 30, "cap": 120}),
        A("astrid_starcaller", "A Clear Night", "'She came through on a clear night'",
          "live: always_crits and cannot_miss", "damage", "enemy", 15, 0, 130,
          "A starlit arrow that cannot miss and always lands a critical hit.", always_crits=True,
          cannot_miss=True),
        A("astrid_starcaller", "The Stars Are Wrong", "'The stars are wrong, but they're very bright.'",
          "existing (miss_chance_pct on every enemy)", "debuff", "all_enemies", 12, 2, 0,
          "For 2 turns, every enemy misses 25% more often.", stat_mods={"miss_chance_pct": 25}),
    ]),
    "luka_stormbringer": (P("Fifteen Years on the Crossing", "'captained a car ferry between Split and the islands "
                            "for fifteen years'", frost_damage_pct=10, nature_damage_pct=10), [
        A("luka_stormbringer", "The Squall Comes In", "'Ever seen a squall come in over open water?'",
          "live: self_stun_turns", "spell_damage", "enemy_aoe", 15, 0, 160,
          "Brings a squall down on one enemy row for huge nature damage. Luka loses his next turn.",
          damage_school="nature", self_stun_turns=1),
        A("luka_stormbringer", "Stand Behind Me", "'Stand behind me and you'll be fine.'",
          "existing (party damage_taken_pct)", "buff", "party", 10, 2, 100,
          "For 2 turns, the party takes 25% less damage.", stat_mods={"damage_taken_pct": -0.25}),
        A("luka_stormbringer", "The Last Ferry", "'he blows it once every evening at the time the last ferry used to "
          "leave'", "live: mana_restore_pct", "restore_resource", "party", 12, 0, 20,
          "Gives every ally back 20% of their mana.", mana_restore_pct=20),
    ]),
    "zofia_cultist": (P("Nobody Talks Down to Her Twice", "'nobody talks down to her twice'", crit_chance_spell=5,
                        shadow_resistance=10), [
        A("zofia_cultist", "Eight Hours of Shouting", "'eight hours a day of people shouting at her'",
          "live: target_health_bonus_pct", "spell_damage", "enemy", 12, 0, 100,
          "Shadow damage, up to 50% more against a target with more health.", damage_school="shadow",
          target_health_bonus_pct=50),
        A("zofia_cultist", "She Walked Out", "'she walked out of Andorhal with what they'd taught her'",
          "live: damage_to_shield", "buff", "self", 12, 3, 100,
          "For 3 turns, 40% of the magic damage Zofia takes becomes a shield on her.",
          damage_to_shield={"pct": 40, "school": "magic"}),
        A("zofia_cultist", "Three of Their Books", "'she took three of the Cult's books with her'",
          "existing (debuff on an enemy row)", "debuff", "enemy_aoe", 12, 3, 100,
          "For 3 turns, the enemies in one row deal 30% less damage.", stat_mods={"damage_dealt_pct": -30}),
    ]),
    "omar_venomancer": (P("Very Calm Around Things That Sting", "'very calm around things that sting'",
                          nature_damage_pct=10, nature_resistance=10), [
        A("omar_venomancer", "Fogging the Block", "'fumigating apartment blocks and restaurants'",
          "existing (spell_dot on an enemy row)", "spell_dot", "enemy_aoe", 10, 4, 45,
          "Nature damage over 4 turns to every enemy in one row.", damage_school="nature"),
        A("omar_venomancer", "Half an Antidote", "'a poison you understand is half an antidote'",
          "live: dispel and heals_dispelled_damage", "dispel", "party", 10, 0, 0,
          "Takes one poison or disease off every ally and heals them for the damage it would have done.",
          dispel_count=1, dispel_type=["poison", "disease"], heals_dispelled_damage=True),
        A("omar_venomancer", "The Second Treatment", "'the same job'",
          "live: max_stacks and stack_on repeat", "debuff", "enemy", 12, 5, 100,
          "For 5 turns the target takes 15% more damage. Using it again stacks it, up to three times.",
          stat_mods={"physical_damage_taken_pct": 15, "magic_damage_taken_pct": 15}, max_stacks=3,
          stack_on="repeat"),
    ]),
    "santiago_runemaster": (P("A Waiting List That Ran for Months", "'a perfectionist about line work'",
                              crit_chance_physical=5, arcane_damage_pct=10), [
        A("santiago_runemaster", "A Line You Can't Take Back", "'Every rune's a line you can't take back.'",
          "live: cannot_miss", "damage", "enemy", 10, 0, 75, "A runed cut that cannot miss.", cannot_miss=True),
        A("santiago_runemaster", "Session by Session", "'runes started showing up in his work'",
          "live: max_stacks and stack_on attack", "buff", "self", 10, 5, 100,
          "For 5 turns, each attack Santiago lands raises his damage by 8%, up to five times.",
          stat_mods={"damage_dealt_pct": 8}, max_stacks=5, stack_on="attack"),
        A("santiago_runemaster", "The Stencil", "'he engraves them into his blades now'",
          "live: mark", "debuff", "enemy_aoe", 12, 5, 30,
          "Marks one enemy row for 5 turns. The party deals 30% more damage to marked enemies.", mark={"pct": 30}),
    ]),
    "emiliano_pyromancer": (P("Never Once Burned Himself", "'He never once burned himself'", fire_damage_pct=10,
                              fire_resistance=10), [
        A("emiliano_pyromancer", "Two Minutes a Red Light", "'two minutes a red light, for coins from the windows'",
          "live: on_kill_repeat_pct", "spell_damage", "enemy_aoe", 12, 0, 120,
          "Fire on one enemy row. If it kills anything, it goes off again at 50%.", damage_school="fire",
          on_kill_repeat_pct=50),
        A("emiliano_pyromancer", "The Whole Breath", "'Now it comes out of him the colour of a dragon's breath'",
          "live: self_stun_turns", "spell_damage", "enemy", 15, 0, 210,
          "Breathes out everything he has for huge fire damage. Emiliano loses his next turn.",
          damage_school="fire", self_stun_turns=1),
        A("emiliano_pyromancer", "Lit It From Across the Yard", "'he lit their forge from across the yard'",
          "live: damage_to_heal", "buff", "party", 12, 4, 100,
          "For 4 turns, 30% of the fire damage the party takes heals them instead.",
          damage_to_heal={"pct": 30, "school": "fire"}),
    ]),
    "isla_witchhunter": (P("The Stillest Person You'll Ever Meet", "'the stillest person you'll ever meet with a "
                           "weapon in her hands'", crit_chance_physical=5, dodge=5), [
        A("isla_witchhunter", "Between Two Heartbeats", "'shot biathlon for Scotland'",
          "live: turn_meter_boost", "buff", "self", 10, 1, 100, "Isla takes another turn straight away.",
          turn_meter_boost=1.0),
        A("isla_witchhunter", "She Doesn't Miss", "'I don't miss, and I'd rather not have to prove it today.'",
          "live: missing_health_bonus_pct", "damage", "enemy", 10, 0, 80,
          "A bolt that deals up to 80% more the more health the target is missing.", missing_health_bonus_pct=80,
          reach="ranged"),
        A("isla_witchhunter", "Stalking the Glen", "'stalked deer in the Highlands for the estates'",
          "live: reveals_intent and sure_target", "debuff", "enemy", 12, 3, 0,
          "For 3 turns, shows what the target will do next, and the party's attacks on it cannot miss.",
          reveals_intent="all", sure_target=True),
    ]),
    "dale_reaper": (P("Four Generations on the Same Ground", "'land his family had worked for four generations'",
                      max_health_pct=10, armor_pct=10), [
        A("dale_reaper", "Bring It In Before the Weather", "'he knows how to bring a harvest in before the weather "
          "turns'", "existing (damage on an enemy row)", "damage", "enemy_aoe", 10, 0, 65,
          "A long sweep of the scythe through one enemy row."),
        A("dale_reaper", "The Last Pass", "'it felt like the last pass of a long harvest'",
          "live: delayed", "damage", "enemy_aoe", 12, 2, 100,
          "A great swing that lands on one enemy row two turns from now.", delayed={"turns": 2, "mult": 1.0}),
        A("dale_reaper", "After Church on Sunday", "'they called every Sunday after church'",
          "live: heals_party_pct_max and party_resource_pct", "heal", "party", 15, 0, 40,
          "Heals the party for 30% of their maximum health and gives back 20% of their resource.",
          heals_party_pct_max=30, party_resource_pct=20),
    ]),
}

#: never this close to a map's edge, where the exits are
EDGE = 8

# Rank-1 sizes are held so the kit medians tools/rank_kit_abilities.py sizes everyone against do not move: adding
# these sixteen leaves every older kit's ranks exactly as they were (checked 17 Nov 2026).
COST = {"mana": 30, "rage": 20, "energy": 25, "combo": 28, "focus": 25, "felfury": 28, "life_force": 40,
        "archery_points": 25}


def main():
    write = "--write" in sys.argv
    import math
    import contextlib
    import io
    from build_sheet3_recruits import arrival_points, bfs, MIN_STEPS_IN, BOSS_CLEAR
    from combat.abilities import get_class_resource
    import rank_kit_abilities as RK
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
    problems, rows = [], []
    placed_here = {}
    for variant, (rid, (name, spec, cls, level, zname, gender, colour, row)) in enumerate(ROSTER.items(), start=1):
        if rid not in BATCH:
            problems.append(f"{rid}: no prose")
            continue
        if not (ROOT / f"assets/npcs/recruits/{rid}/down.png").exists():
            problems.append(f"{rid}: no sprite")
        z = zones.get(zname)
        if z is None:
            problems.append(f"{rid}: no zone {zname}")
            continue
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
        occupied |= {(r.get("x"), r.get("y")) for r in existing if r.get("zone") == zname}
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
        # within a few steps of the target walk, the one nearest the middle of the map (never an exit edge)
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
        passive, abilities = KITS[rid]
        for a in abilities:
            a["resource_type"] = res
            if a["ranks"][0]["cost"] is None:
                a["ranks"][0]["cost"] = COST.get(res, 30)
        kit = {"name": name, "passives": passive, "abilities": abilities}
        rows.append((rid, zname, level, x, y, d, first_boss))
        if rid in have:
            existing[:] = [r if r["recruit_id"] != rid else rec for r in existing]
        else:
            existing.append(rec)
        kdoc[rid] = kit
    # five ranks on the sixteen's damage, heal and shield abilities, by rank_kit_abilities' own rule
    ranked = 0
    for rid in ROSTER:
        for a in kdoc.get(rid, {}).get("abilities", []):
            if RK.grows(a):
                a["ranks"] = RK.ranks_for(a, kdoc)
                ranked += 1
    for rid, zname, level, x, y, d, fb in rows:
        print(f"  {rid:22s} {level:3d} ({x},{y}) {d:4d} steps in, first boss {fb or '-'}  {zname}")
    print(f"  {len(rows)} placed, {ranked} abilities ranked to 60, {len(problems)} problem(s)")
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
