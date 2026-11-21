#!/usr/bin/env python3
"""Add the sheet-6 companions: records in data/npcs/recruits.json, character traits (kits) in
data/npcs/personal_kits.json. Idempotent.

    PYTHONPATH=. python3 tools/build_sheet6_recruits.py            # dry run: placements, waiting, problems
    PYTHONPATH=. python3 tools/build_sheet6_recruits.py --write

Kyle, 20 Nov 2026: "Let's make a batch of 16 recruits... 75% men and 25% women", for the sky and the tree, with "a
Healer recruit in the start of the zone". The roster and the reasons are in claude/recruit_art_prompts_sheet6.md: the
gap at 45 to 52 (no tank, one melee, two healers) is where twelve of them go.

WHO THEY ARE is tools/writing/sheet6_recruits.py (BATCH for the record text, TRAITS for the one-line read). WHERE:
tools/build_sheet4_recruits.py's walk for the tree's five, and pinned posts for the sky's seven (the Annex's guests,
Lenswatch's workshop, the Expanse's islands, Aurelion's embassy and Academies). WHAT THEY CAN DO: the KITS below, one
named passive and three abilities each, every one quoting the line of their story it comes from and built only from
mechanics other kits already use. Cooldowns are 10 to 15 turns (Kyle's rule for skills).

WAITING. The Aetherian start zone (Ines, Lukas, Rafael and Samir) is parked, so their four aren't in ROSTER yet; their
art is sliced and waiting in assets/npcs/recruits.
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
from writing.sheet6_recruits import BATCH  # noqa: E402

CROWN, LENS, EXPANSE, AURELION = "The Sunward Crown", "Lenswatch", "The Celestial Expanse", "Aurelion"
#: the sky's seven stand where their story puts them, not where the walk would drop them
PINNED = {"mauricio_reaper": (226, 136), "etienne_mage": (248, 147),      # the Annex, with the survey's guests
          "tariq_bloodmage": (206, 190), "isabela_mage": (170, 126),       # the Ground Embassy; the Academies
          "facundo_chronomancer": (112, 166),                                # the Golem Fields
          "raul_barbarian": (92, 78),                                     # the Great Settlement's market
          # the tree's three with a camp in their story: Mossroof, Heartwatch, Highrest's windward edge
          "clara_primalist": (96, 33), "federico_templar": (38, 55), "connor_shaman": (98, 99)}

#: id -> (name, spec, class, level, zone, gender, colour, row)
ROSTER = {
    "alvaro_venomancer":  ("Álvaro Ruiz", "venomancer_fortitude", "Venomancer", 43, "Rootwater Isle", "male", "#4E7A2E", "front"),
    "clara_primalist":    ("Clara Weiss", "primalist_grovekeeper", "Primalist", 45, "The Lower Boughs", "female", "#7FA65A", "back"),
    "raul_barbarian":    ("Raúl Castillo", "barbarian_headhunting", "Barbarian", 46, "The Great Settlement", "male", "#A8763E", "front"),
    "federico_templar":   ("Federico Lagos", "templar_oathkeeper", "Templar", 47, "The Middle Boughs", "male", "#C9B27A", "front"),
    "connor_shaman":      ("Connor Walsh", "shaman_enhancement", "Shaman", 48, "The Upper Boughs", "male", "#3E7FC1", "front"),
    "mauricio_reaper":    ("Mauricio Peña", "reaper_domination", "Reaper", 49, CROWN, "male", "#E08A1E", "front"),
    "etienne_mage":       ("Étienne Gagnon", "mage_frost", "Mage", 49, CROWN, "male", "#8FC8E8", "back"),
    "oliver_suncleric":   ("Oliver Hayes", "sun_cleric_blessings", "Sun Cleric", 48, LENS, "male", "#E8C25A", "back"),
    "facundo_chronomancer": ("Facundo Herrera", "chronomancer_time", "Chronomancer", 50, EXPANSE, "male", "#C8A050", "back"),
    "renata_rogue":      ("Renata Rojas", "rogue_combat", "Rogue", 51, EXPANSE, "female", "#B8202E", "front"),
    "tariq_bloodmage":    ("Tariq Al-Jubouri", "bloodmage_eternal", "Bloodmage", 52, AURELION, "male", "#8E1B24", "front"),
    "isabela_mage":       ("Isabela Moura", "mage_arcane", "Mage", 52, AURELION, "female", "#9A6AD8", "back"),
}

KITS = {
    "alvaro_venomancer": (P("Stung Ten Thousand Times", "'He's been stung more times than he can count'",
                            max_health_pct=5, nature_resistance=15), [
        A("alvaro_venomancer", "Tell the Bees the News", "'He talked to the bees every morning'",
          "live: threat_generation_pct + damage taken reductions", "buff", "self", 12, 4, 100,
          "For 4 turns, Álvaro draws far more attention and takes 20% less damage.",
          stat_mods={"threat_generation_pct": 200, "physical_damage_taken_pct": -20, "magic_damage_taken_pct": -20}),
        A("alvaro_venomancer", "Stand Still", "'Stand still if something lands on you, that's the whole trick.'",
          "live: damage_to_heal", "buff", "party", 12, 4, 100,
          "For 4 turns, 30% of the nature damage the party takes heals them instead.",
          damage_to_heal={"pct": 30, "school": "nature"}),
        A("alvaro_venomancer", "The Poison Likes Him", "'The venomancers say the poison likes him.'",
          "existing (spell_dot on an enemy row)", "spell_dot", "enemy_aoe", 12, 4, 45,
          "Venom eats into one enemy row over 4 turns.", damage_school="nature"),
    ]),
    "clara_primalist": (P("Four Hundred Years in a Pencil", "'every dry summer, every fire and every bad winter'",
                          healing_done=10, mp5=5), [
        A("clara_primalist", "The Bark Warmed", "'the bark warmed under it, and a scratch on her wrist closed'",
          "live: on_low_health", "buff", "ally", 12, 4, 100,
          "For 4 turns, the first time the ally drops below 35% health they're healed for 30% of their maximum.",
          on_low_health={"pct": 35, "heal_pct": 30}),
        A("clara_primalist", "Every Bad Winter", "'every bad winter the tree lived through'",
          "live: wounded_allies_bonus_pct", "heal", "party", 12, 0, 55,
          "Heals the party, 20% more for each wounded ally.", wounded_allies_bonus_pct=20),
        A("clara_primalist", "With Evidence", "'she wants to know it properly, with evidence'",
          "live: low_health_bonus 30% under half health", "heal", "ally", 10, 0, 60,
          "A careful heal on one ally, 30% stronger on an ally below half health.",
          low_health_bonus={"below": 50, "bonus": 30}),
    ]),
    "raul_barbarian": (P("A Buckle for Every Win", "'a silver buckle for every one he won'",
                          crit_chance_physical=5, max_health_pct=5), [
        A("raul_barbarian", "Eight Seconds", "'Eight seconds is a long time on a bull'",
          "existing (self buff stat_mods)", "buff", "self", 12, 4, 100,
          "For 4 turns, Raúl deals 20% more damage and shakes off stuns twice as fast.",
          stat_mods={"damage_dealt_pct": 20, "stun_duration_reduction_pct": 50}),
        A("raul_barbarian", "Stayed On for Nine", "'stayed on for nine seconds'",
          "live: consecutive_target_bonus", "damage", "enemy", 12, 0, 70,
          "Each hit on the same target in a row deals 25% more, up to 100% more.",
          consecutive_target_bonus={"pct": 25, "cap": 100}),
        A("raul_barbarian", "Among Their Trophies", "'hung his old rodeo number among their trophies'",
          "live: mark", "debuff", "enemy", 15, 5, 25,
          "Marks one enemy as his trophy for 5 turns, and the party deals 25% more damage to it.", mark={"pct": 25}),
    ]),
    "federico_templar": (P("Read Aloud Before Signing", "'He read every contract aloud before anyone signed'",
                           armor_pct=10, max_health_pct=5), [
        A("federico_templar", "Ten Thousand Promises", "'I've witnessed ten thousand promises'",
          "live: threat_generation_pct + damage taken reductions", "buff", "self", 12, 4, 100,
          "For 4 turns, Federico draws far more attention and takes 20% less damage.",
          stat_mods={"threat_generation_pct": 200, "physical_damage_taken_pct": -20, "magic_damage_taken_pct": -20}),
        A("federico_templar", "He Kept That Promise", "'The first time he promised to keep a stranger alive'",
          "live: death_prevent", "buff", "ally", 15, 4, 100,
          "For 4 turns, a blow that would kill the ally leaves them at 15% health instead.",
          death_prevent={"pct": 15}),
        A("federico_templar", "The Notary's Seal", "'He still stamps the oaths the climbers swear'",
          "existing (debuff on an enemy row)", "debuff", "enemy_aoe", 12, 3, 100,
          "For 3 turns, the enemies in one row deal 30% less damage.", stat_mods={"damage_dealt_pct": -30}),
    ]),
    "connor_shaman": (P("Out for the Pots", "'through every storm the Atlantic sent'", nature_damage_pct=10,
                        crit_chance_physical=5), [
        A("connor_shaman", "Read the Sky", "'His father taught him to read the sky before he could read a book'",
          "live: reveals_intent and sure_target", "debuff", "enemy", 12, 3, 0,
          "For 3 turns, shows what the target will do next, and the party's attacks on it can't miss.",
          reveals_intent="all", sure_target=True),
        A("connor_shaman", "Laughing in the Storm", "'laughing, with sparks running down his arms'",
          "existing (spell_dot on an enemy row)", "spell_dot", "enemy_aoe", 12, 3, 45,
          "Lightning crawls through one enemy row over 3 turns.", damage_school="nature"),
        A("connor_shaman", "Never Caught Out", "'weather has never caught him out'",
          "existing (self buff stat_mods)", "buff", "self", 12, 4, 100,
          "For 4 turns, Connor dodges far more often and deals 15% more damage.",
          stat_mods={"dodge": 15, "damage_dealt_pct": 15}),
    ]),
    "mauricio_reaper": (P("Marigolds From the Door to the Street", "'marigolds from the door to the street'",
                          shadow_resistance=15, max_health_pct=5), [
        A("mauricio_reaper", "Took It Very Well", "'decided he'd died, and took it very well'",
          "live: death_prevent", "buff", "self", 15, 4, 100,
          "For 4 turns, a blow that would kill Mauricio leaves him at 20% health instead.",
          death_prevent={"pct": 20, "lethal_only": False}),
        A("mauricio_reaper", "Asked It to Stay", "'He asked it politely to stay a while, and it did.'",
          "live: summon_pet", "summon_pet", "self", 15, 0, 40,
          "Asks something that died nearby to stay a while and fight beside him.", summon_pet_template="ghoul"),
        A("mauricio_reaper", "The Biggest Altar in the Barrio", "'he built the biggest altar in the barrio'",
          "live: damage_to_heal", "buff", "party", 12, 4, 100,
          "For 4 turns, 30% of the shadow damage the party takes heals them instead.",
          damage_to_heal={"pct": 30, "school": "shadow"}),
    ]),
    "etienne_mage": (P("Ice Like Glass", "'the players said his ice was like glass'", frost_damage_pct=10,
                       crit_chance_spell=5), [
        A("etienne_mage", "Flooded at Six", "'He flooded the ice at six every morning, slow and even'",
          "live: per_use_bonus any", "spell_damage", "enemy", 12, 0, 65,
          "Frost damage. Each use in a fight deals 12% more, up to 60% more.", damage_school="frost",
          per_use_bonus={"pct": 12, "cap": 60, "any": True}),
        A("etienne_mage", "The Quiet Before Anyone Came In", "'he loved the quiet before anyone came in'",
          "live: idle_charge", "buff", "self", 12, 4, 30,
          "For 4 turns, each turn Étienne doesn't attack adds 30% to his next spell, up to 120%.",
          idle_charge={"pct": 30, "cap": 120}),
        A("etienne_mage", "Freeze It Flat", "'until he could freeze it flat and clear enough to see the fish'",
          "existing (spell_dot on an enemy row)", "spell_dot", "enemy_aoe", 12, 4, 45,
          "Frost settles over one enemy row and bites for 4 turns.", damage_school="frost"),
    ]),
    "oliver_suncleric": (P("Follow My Finger", "'Follow my finger, please. Sorry, it's a habit.'", healing_done=10,
                           crit_chance_spell=5), [
        A("oliver_suncleric", "Through the Glass", "'it went straight through the glass into the wound'",
          "live: low_health_bonus 30% under half health", "heal", "ally", 10, 0, 60,
          "Sunlight through a lens on one ally, 30% stronger on an ally below half health.",
          low_health_bonus={"below": 50, "bonus": 30}),
        A("oliver_suncleric", "A Routine Test", "'during a routine test'",
          "live: dispel and heals_dispelled_damage", "dispel", "party", 12, 0, 0,
          "Takes one harmful effect off every ally and heals them for the damage it would have done.",
          dispel_count=1, dispel_type=["magic", "curse", "poison", "disease"], heals_dispelled_damage=True),
        A("oliver_suncleric", "Nine Hours of Questions", "'asked him about eyes for nine hours straight'",
          "live: heals_party_pct_max and party_resource_pct", "heal", "party", 15, 0, 25,
          "Heals the party for 15% of their maximum health and gives back 15% of their resource.",
          heals_party_pct_max=15, party_resource_pct=15),
    ]),
    "facundo_chronomancer": (P("Never Force a Watch", "'you never force a watch'", healing_done=10, haste=5), [
        A("facundo_chronomancer", "Wound It Back", "'He wound it back a few seconds, and the cut wasn't there.'",
          "live: grants_turn - the healed ally's turn meter is filled", "heal", "ally", 12, 0, 55,
          "Winds an ally back a few seconds. Heals them, and they take a turn straight away.", grants_turn=True),
        A("facundo_chronomancer", "A Few Seconds Apart", "'a wall of clocks that all struck noon a few seconds apart'",
          "live: heals_party_pct_max", "heal", "party", 15, 0, 25,
          "Heals the party for 20% of their maximum health.", heals_party_pct_max=20),
        A("facundo_chronomancer", "Listen Until It Tells You", "'You listen to it until it tells you what's wrong.'",
          "live: death_prevent", "buff", "ally", 15, 4, 100,
          "For 4 turns, a blow that would kill the ally leaves them at 15% health instead.",
          death_prevent={"pct": 15}),
    ]),
    "renata_rogue": (P("Do It Twice", "'she'll do any fall twice if the first take wasn't clean'",
                        crit_chance_physical=5, dodge=8), [
        A("renata_rogue", "The High Fall", "'She did the high fall in a telenovela finale'",
          "live: high_health_bonus", "damage", "enemy", 12, 0, 110,
          "Drops onto a target from above. Deals 100% more damage to a target above 60% health.",
          high_health_bonus={"above": 60, "bonus": 100}),
        A("renata_rogue", "I Always Land", "'I've jumped off taller things for less money, and I always land.'",
          "existing (self buff stat_mods)", "buff", "self", 12, 3, 100,
          "For 3 turns, Renata dodges far more often.", stat_mods={"dodge": 25}),
        A("renata_rogue", "Faster Than the Skiffs", "'She runs messages between the islands faster than the skiffs'",
          "live: consecutive_target_bonus", "damage", "enemy", 10, 0, 65,
          "Each hit on the same target in a row deals 25% more, up to 100% more.",
          consecutive_target_bonus={"pct": 25, "cap": 100}),
    ]),
    "tariq_bloodmage": (P("Every Eight Weeks", "'gave blood every eight weeks from the day he turned eighteen'",
                          max_health_pct=10, armor_pct=5), [
        A("tariq_bloodmage", "It Gives a Little Back", "'Now it seems the blood remembers, and it gives a little back.'",
          "live: heals_lowest_ally_pct", "spell_damage", "enemy", 12, 0, 70,
          "Shadow damage. Heals the most wounded ally for 60% of the damage dealt.", damage_school="shadow",
          heals_lowest_ally_pct=60),
        A("tariq_bloodmage", "It Pulled Him Back Up", "'the blood didn't run. It stopped, and it pulled him back up'",
          "live: threat_generation_pct + damage taken reductions", "buff", "self", 12, 4, 100,
          "For 4 turns, Tariq draws far more attention and takes 20% less damage.",
          stat_mods={"threat_generation_pct": 200, "physical_damage_taken_pct": -20, "magic_damage_taken_pct": -20}),
        A("tariq_bloodmage", "Lifted the Cart", "'lifted a fallen cart off an Aetherian child'",
          "live: damage_share", "buff", "party", 12, 2, 100,
          "For 2 turns, Tariq takes the next hit meant for any ally, at 50% less damage.",
          damage_share={"pct": 100, "reduction_pct": 50, "uses": 1}),
    ]),
    "isabela_mage": (P("The Colour Tells the Heat", "'She could tell the heat of the glass by its colour'",
                       arcane_damage_pct=10, crit_chance_spell=5), [
        A("isabela_mage", "It Sang", "'when she touched it, it sang'",
          "live: cannot_miss", "spell_damage", "enemy", 12, 0, 75,
          "Arcane damage. A singing note of crystal that cannot miss.", damage_school="arcane", cannot_miss=True),
        A("isabela_mage", "A Furnace That Never Went Out", "'a furnace that never went out'",
          "existing (spell_dot on an enemy row)", "spell_dot", "enemy_aoe", 12, 4, 45,
          "Arcane heat pours over one enemy row for 4 turns.", damage_school="arcane"),
        A("isabela_mage", "A Whole Summer", "'a chandelier for a church that took her a whole summer'",
          "live: mana_restore_pct", "restore_resource", "party", 15, 0, 15,
          "Gives every ally back 15% of their mana.", mana_restore_pct=15),
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
        if rid in PINNED:
            x, y = PINNED[rid]
            if (x, y) not in dist or not all(math.dist((x, y), o) >= 3 for o in occupied if o[0] is not None):
                problems.append(f"{rid}: pinned post ({x},{y}) isn't walkable or is on top of someone")
                continue
            d = dist[(x, y)]
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
