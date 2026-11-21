#!/usr/bin/env python3
"""Add the sheet-7 companions (the bears) as each is placed: records in data/npcs/recruits.json, kits in
data/npcs/personal_kits.json. Idempotent. Runs on tools/build_sheet6_recruits.py's builder with this sheet's roster.

    PYTHONPATH=. python3 tools/build_sheet7_recruits.py            # dry run
    PYTHONPATH=. python3 tools/build_sheet7_recruits.py --write

WHO is tools/writing/sheet7_recruits.py. WHERE: pinned posts. Dawnhaven's three (Kyle, 21 Nov 2026: "Can you move one
bear recruit to lower level so the island has 3 recruits", then "Island bears"): Rhodri Evans (tank) by the scaffold on
Amberwatch's gatehouse, Yiannis Papadakis (healer) on the Waking Shore, Leif Halvorsen (melee) in the Red Hollow. The
other thirteen wait for their zones. Their bonds, banter, relationships, Sworn skills and keepsakes are in the usual
places (tools/wave2/, tools/wave3/, tools/wave4/, data/npcs/keepsakes.json), from their profiles in docs/recruits/. Kits: one named passive and
three abilities, every one quoting his story and built only from mechanics other kits use, 10 to 15 turn cooldowns.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
os.chdir(ROOT)

import build_sheet6_recruits as S6  # noqa: E402
from build_sheet4_recruits import A, P  # noqa: E402
from writing.sheet7_recruits import BATCH  # noqa: E402

#: id -> (name, spec, class, level, zone, gender, colour, row)
ROSTER = {
    "rhodri_knight": ("Rhodri Evans", "knight_of_xoroth_defiance", "Knight of Xoroth", 4, "Amberleaf Glade", "male",
                      "#B3261E", "front"),
    "yiannis_paladin": ("Yiannis Papadakis", "paladin_holy", "Paladin", 3, "Amberleaf Glade", "male", "#E8D9A0",
                        "back"),
    "leif_primalist": ("Leif Halvorsen", "primalist_wildwalker", "Primalist", 7, "Duskfall Woods", "male", "#6E8B3D",
                       "front"),
}
PINNED = {"rhodri_knight": (60, 101),      # by the scaffold on Amberwatch's gatehouse
          "yiannis_paladin": (82, 106),    # on the Waking Shore, by the guard post
          "leif_primalist": (40, 96)}      # in the Red Hollow, hauling deadwood

KITS = {
    "rhodri_knight": (P("Fifteen Years in the Front Row", "'propped for Pontypridd on Saturdays for fifteen years'",
                        armor_pct=10, max_health_pct=5), [
        A("rhodri_knight", "Nobody Got Past Him", "'Nobody got past him on the pitch'",
          "live: threat_generation_pct + damage taken reductions", "buff", "self", 12, 4, 100,
          "For 4 turns, Rhodri draws far more attention and takes 20% less damage.",
          stat_mods={"threat_generation_pct": 200, "physical_damage_taken_pct": -20, "magic_damage_taken_pct": -20}),
        A("rhodri_knight", "Clipped On", "'He clipped every one of those lads on before they climbed'",
          "live: death_prevent", "buff", "ally", 15, 4, 100,
          "For 4 turns, a blow that would kill the ally leaves them at 15% health instead.",
          death_prevent={"pct": 15}),
        A("rhodri_knight", "Pack Down", "'anyone daft enough to pack down against him'",
          "existing (debuff on an enemy row)", "debuff", "enemy_aoe", 12, 3, 100,
          "For 3 turns, the enemies in one row deal 30% less damage.", stat_mods={"damage_dealt_pct": -30}),
    ]),
    "yiannis_paladin": (P("Since He Was Nine", "'Yiannis dived for octopus off Chania from the age of nine'",
                          healing_done=10, mp5=5), [
        A("yiannis_paladin", "She Breathed", "'Light came into his hands while he worked on her, and she breathed.'",
          "live: low_health_bonus 30% under half health", "heal", "ally", 10, 0, 60,
          "Light from his hands on one ally, 30% stronger on an ally below half health.",
          low_health_bonus={"below": 50, "bonus": 30}),
        A("yiannis_paladin", "Wrapped in a Blanket", "'wraps them in a blanket and sings them a couplet'",
          "live: on_low_health", "buff", "ally", 12, 4, 100,
          "For 4 turns, the first time the ally drops below 35% health they're healed for 30% of their maximum.",
          on_low_health={"pct": 35, "heal_pct": 30}),
        A("yiannis_paladin", "Sings to the Sea", "'He sings to the sea when it's rough'",
          "live: wounded_allies_bonus_pct", "heal", "party", 12, 0, 55,
          "Heals the party, 20% more for each wounded ally.", wounded_allies_bonus_pct=20),
    ]),
    "leif_primalist": (P("Twenty-Five Years in the Woods", "'twenty-five years in the Oregon woods'",
                         nature_damage_pct=10, crit_chance_physical=5), [
        A("leif_primalist", "Where It Leans", "'Watch where you stand.'",
          "live: reveals_intent and sure_target", "debuff", "enemy", 12, 3, 0,
          "For 3 turns, shows what the target will do next, and the party's attacks on it can't miss.",
          reveals_intent="all", sure_target=True),
        A("leif_primalist", "Never Once Fell", "'Leif went up the trees instead, and he never once fell.'",
          "existing (self buff stat_mods)", "buff", "self", 12, 4, 100,
          "For 4 turns, Leif dodges far more often and deals 15% more damage.",
          stat_mods={"dodge": 15, "damage_dealt_pct": 15}),
        A("leif_primalist", "The Biggest One Standing", "'he loves trees more than anybody you'll meet'",
          "live: high_health_bonus", "damage", "enemy", 12, 0, 110,
          "He takes the biggest one first. Deals 100% more damage to a target above 60% health.",
          high_health_bonus={"above": 60, "bonus": 100}),
    ]),
}

if __name__ == "__main__":
    S6.ROSTER, S6.KITS, S6.PINNED, S6.BATCH = ROSTER, KITS, PINNED, BATCH
    sys.exit(S6.main())
