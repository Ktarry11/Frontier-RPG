#!/usr/bin/env python3
"""Shaman weapon imbues + Windfury Totem: one imbue at a time, each with its own job, all with real rank progression.

Before (Kyle, 2026-10-24): Rockbiter / Flametongue / Windfury Weapon were one rank each and could ALL be up at once, so
they were just three stacked flat bonuses with no choice in them.

After:
  * exclusive_group "shaman_imbue": applying one replaces the active one (a weapon carries one imbue, like Classic).
  * Rockbiter Weapon   (L1)  steady physical bonus on every swing + a little Attack Power / Armor  -> the tank / safe pick
  * Flametongue Weapon (L10) bigger Fire bonus on every swing + Spell Power                         -> casters / hybrids
  * Frostbrand Weapon  (L20, NEW) chunky Frost hit on 35% of swings that also slows the target      -> control pick
  * Windfury Weapon    (L30) 20-28% chance of a free extra attack                                   -> pure melee burst
  * Windfury Totem     (L30) party-wide extra-attack chance, 20-26% (separate totem slot, can stack with an imbue)
Idempotent: rewrites those entries every run.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from combat.rank_generator import generate_rank_levels  # noqa: E402
from expand_single_ranks import curve, ranks_wanted     # noqa: E402

PATH = ROOT / "data" / "abilities" / "shaman.json"


def lin(a, b, n):
    return [round(a + (b - a) * i / max(1, n - 1), 3) for i in range(n)]


def build_ranks(learned, proc_fn=None, scale_ev=False):
    levels = generate_rank_levels(learned, ranks_wanted(learned))
    n = len(levels)
    ranks = []
    for i, lvl in enumerate(levels):
        ev = int(round(100 * curve(lvl) / curve(learned))) if scale_ev else 100
        rk = {"rank": i + 1, "level_req": lvl, "cost": 0, "effect_value": ev}
        if proc_fn:
            override = proc_fn(i, n)
            if override:
                rk["proc"] = override
        ranks.append(rk)
    return ranks


def main():
    data = json.loads(PATH.read_text(encoding="utf-8"))
    by_id = {a["ability_id"]: a for a in data["abilities"]}

    rock = by_id["shaman_rockbiter_weapon"]
    rock.update({
        "stat_mods": {"attack_power": 8, "armor": 25},
        "exclusive_group": "shaman_imbue",
        "description": ("Imbue your weapon with the strength of stone: every melee hit deals bonus physical damage and "
                       "you gain a little Attack Power and Armor. The steady, safe imbue. Only one imbue can be active "
                       "at a time."),
        "proc": {"trigger": "on_weapon_swing", "chance": 100, "icd": 0, "bonus_pct": 0.10},
    })
    rock["ranks"] = build_ranks(1, lambda i, n: {"bonus_pct": lin(0.10, 0.24, n)[i]}, scale_ev=True)

    flame = by_id["shaman_flametongue_weapon"]
    flame.update({
        "stat_mods": {"spell_power": 12},
        "damage_school": "fire",
        "exclusive_group": "shaman_imbue",
        "description": ("Imbue your weapon with living flame: every melee hit adds bonus Fire damage and your spells "
                       "gain Spell Power. Hits harder than Rockbiter but gives no armor. Only one imbue can be active "
                       "at a time."),
        "proc": {"trigger": "on_weapon_swing", "chance": 100, "icd": 0, "bonus_pct": 0.15},
    })
    flame["ranks"] = build_ranks(10, lambda i, n: {"bonus_pct": lin(0.15, 0.34, n)[i]}, scale_ev=True)

    frost = {
        "ability_id": "shaman_frostbrand_weapon",
        "name": "Frostbrand Weapon",
        "resource_type": "mana",
        "cooldown": 0,
        "effect_type": "buff",
        "duration": 5,
        "stat_mods": {"attack_power": 6},
        "damage_school": "frost",
        "exclusive_group": "shaman_imbue",
        "description": ("Imbue your weapon with biting cold: 35% of your melee hits add a heavy Frost strike and slow "
                       "the target. The control imbue. Only one imbue can be active at a time."),
        "ranks": [],
        "target_type": "self",
        "is_instant": True,
        "icon_id": None,
        "proc": {"trigger": "on_weapon_swing", "chance": 35, "icd": 0, "bonus_pct": 0.40,
                 "apply_effect": {"effect_id": "frostbrand_slow", "name": "Frostbrand", "effect_type": "debuff",
                                  "duration": 2, "stat_mods": {"haste": -25}, "dispel_type": "magic",
                                  "on_target": True}},
    }
    frost["ranks"] = build_ranks(20, lambda i, n: {"bonus_pct": lin(0.40, 0.80, n)[i]}, scale_ev=True)
    if "shaman_frostbrand_weapon" in by_id:
        by_id["shaman_frostbrand_weapon"].update(frost)
    else:
        idx = data["abilities"].index(flame) + 1
        data["abilities"].insert(idx, frost)

    wf = by_id["shaman_windfury_weapon"]
    wf.update({
        "exclusive_group": "shaman_imbue",
        "description": ("Imbue your weapon with the howling wind: your melee hits have a chance to trigger a free extra "
                       "attack. Higher ranks proc more often. Only one imbue can be active at a time."),
        "proc": {"trigger": "on_weapon_swing", "chance": 20, "icd": 3, "extra_attack": True},
    })
    chances = [20, 24, 28]
    wf["ranks"] = build_ranks(30, lambda i, n: {"chance": chances[min(i, len(chances) - 1)]})

    tot = by_id["shaman_windfury_totem"]
    tot["description"] = ("Air totem. Every living party member's melee attacks have a chance to trigger an extra attack "
                          "(each member rolls independently). Higher ranks proc more often.")
    chances = [20, 23, 26]
    tot["ranks"] = build_ranks(30, lambda i, n: {"chance": chances[min(i, len(chances) - 1)]})

    PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    for aid in ("shaman_rockbiter_weapon", "shaman_flametongue_weapon", "shaman_frostbrand_weapon",
                "shaman_windfury_weapon", "shaman_windfury_totem"):
        a = next(x for x in data["abilities"] if x["ability_id"] == aid)
        print(aid, [r["level_req"] for r in a["ranks"]], [r.get("proc") for r in a["ranks"]][:3])


if __name__ == "__main__":
    main()
