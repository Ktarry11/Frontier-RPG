"""Add the missing baseline rogue abilities to data/abilities/rogue.json (idempotent).

Rogue shipped with 19 entries and long level gaps (nothing new between 22 and 30).  These follow the same
conventions as the existing kit: Energy costs against a 100 pool, effect_value ranks rising ~+25 per rank band,
stuns via is_stun (the engine's only real CC), no stealth/combo-point systems (opener/finisher flavour is in the
description only).  Run:  python3 tools/expand_rogue_kit.py
"""
import json, os
P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data/abilities/rogue.json")


def ab(aid, name, etype, cost, cd, levels, values, desc, dur=0, mods=None, **extra):
    d = {"ability_id": aid, "name": name, "resource_type": "energy", "cooldown": cd, "effect_type": etype,
         "duration": dur, "stat_mods": mods or {}, "description": desc,
         "ranks": [{"rank": i + 1, "level_req": lv, "cost": cost, "effect_value": v}
                   for i, (lv, v) in enumerate(zip(levels, values))],
         "icon_id": None}
    d.update(extra)
    return d


NEW = [
    ab("rogue_garrote", "Garrote", "dot", 40, 3, [14, 26, 38, 50, 62], [40, 68, 96, 124, 152],
       "Garrotes the target, causing bleed damage over 4 turns.", dur=4, damage_school="physical"),
    ab("rogue_cheap_shot", "Cheap Shot", "debuff", 60, 8, [18], [100],
       "A dirty opener that stuns the target for 1 turn.", dur=1, is_stun=True, is_instant=True),
    ab("rogue_deadly_poison", "Deadly Poison", "spell_dot", 30, 2, [20, 32, 44, 56], [40, 66, 92, 118],
       "Coats your blade in a lethal toxin, dealing Nature damage over 4 turns.", dur=4, damage_school="nature"),
    ab("rogue_ambush", "Ambush", "damage", 60, 4, [18, 30, 42, 54], [95, 135, 175, 215],
       "A heavy surprise strike from the shadows. (No stealth system exists - the opener flavour is cosmetic.)"),
    ab("rogue_crippling_poison", "Crippling Poison", "debuff", 20, 3, [24], [100],
       "Coats your blade in a numbing toxin, slowing the target for 3 turns.", dur=3,
       mods={"haste": -30}, is_instant=True),
    ab("rogue_shiv", "Shiv", "damage", 30, 3, [24, 38, 52], [48, 78, 108],
       "A quick, cheap stab that deals bonus damage and is cheap to chain.", is_instant=True),
    ab("rogue_blade_flurry", "Blade Flurry", "buff", 25, 8, [28], [100],
       "Your blades become a blur, greatly increasing your attack speed for 3 turns.", dur=3,
       mods={"haste": 30}, target_type="self", is_instant=True, buff_scope="combat"),
    ab("rogue_kidney_shot", "Kidney Shot", "debuff", 50, 10, [30], [100],
       "A finishing blow to the kidney that stuns the target for 2 turns.", dur=2, is_stun=True, is_instant=True),
    ab("rogue_blind", "Blind", "debuff", 40, 12, [34], [100],
       "Throws blinding powder, incapacitating the target for 2 turns.", dur=2, is_stun=True, is_instant=True),
    ab("rogue_envenom", "Envenom", "damage", 35, 3, [36, 48, 60], [100, 135, 170],
       "A venom-laced finisher that deals Nature damage.", damage_school="nature"),
    ab("rogue_fan_of_knives", "Fan of Knives", "damage", 50, 4, [40, 52, 62], [60, 85, 110],
       "Hurls a whirl of knives at every enemy.", target_type="enemy_aoe"),
    ab("rogue_preparation", "Preparation", "reset_cooldowns", 0, 20, [42], [0],
       "Resets all of your ability cooldowns.", target_type="self", is_instant=True),
    ab("rogue_killing_spree", "Killing Spree", "damage", 60, 10, [50], [220],
       "Vanishes between a flurry of devastating strikes on the target.", is_instant=True),
]

d = json.load(open(P, encoding="utf-8"))
have = {a["ability_id"] for a in d["abilities"]}
added = [a for a in NEW if a["ability_id"] not in have]
d["abilities"].extend(added)
json.dump(d, open(P, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(P, "a", encoding="utf-8").write("\n")
print(f"rogue abilities: {len(d['abilities'])} (+{len(added)})")
