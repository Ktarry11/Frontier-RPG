#!/usr/bin/env python3
"""The Zukk'ash Hive (Feralas's silithid cave, 47-49): creatures, kits, encounter table and boss loot. Idempotent.

    PYTHONPATH=. python3 tools/build_zukkash_hive_content.py

The map is tools/handbuilt_zukkash_hive.py (its docstring has the shape: a dig, not a string of rooms). A cave, not a
dungeon: the two bosses pinned by the map, trash rolled from the cave's own table under the High Wilderness's "caves".

  THE DEEP MOTHER          the hive's queen, in her chamber where the gallery levels out (the last boss)
  TUNNELMASTER ZIX'TAL     at the dig's head, driving the workers on toward the Dry Deep (optional: you can walk past
                           the chamber to him, or leave him and go home)

THE NUMBERS are the Plaguelands and Azshara caves': a boss's basic hit 10L - 200, trash 4L - 10, boss health 2.5 for the
one at the end and 2.3 for the optional one. Both carry something dangerous (Kyle: "make sure bosses are not just
debuffing"; tools/qa_dungeon_boss_turns.py holds them to it).

THE SPRITES: built before Kyle's Feralas sheets, so the trash draws as the silithid workers already in the game and the
Deep Mother as the Royal Hive's queen art until sheet 7 (fe_boss_deep_mother) is sliced. tools/build_feralas_openworld
writes every Feralas sprite rule; this script adds the cave's own the same way.

LOOT. Four items a boss, item level = the boss's level + 2 (the caves' lift), spread over the armour types and the six
stat templates. No trinkets (a trinket from 50 has to do something).
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.build_return_voyage_content import (  # noqa: E402
    CREATURES, KITS, ENCOUNTERS, kit_slug, merge_json, _detect_format, dmg, dot, loot_audit)
from tools.build_scarlet_monastery_content import opener, stun_hit, heal, hit_with  # noqa: E402
from tools import handbuilt_zukkash_hive as ZH  # noqa: E402

LOOT = ROOT / "data/loot/zukkash_hive_boss_loot.json"
CAVE = ZH.NAME


def BH(level):
    return 10 * level - 200


def T(level):
    return 4 * level - 10


#: name -> (template, lo, hi, boss multiplier or None, sprite, placeholder)
ROSTER = {
    "Zukk'ash Hive Worker":    ("vermin_swarm",     47, 48, None, "fe_silithid_tunneler", "silithid_worker_2"),
    "Zukk'ash Hive Warrior":   ("humanoid_warrior", 47, 48, None, "fe_silithid_warrior", "silithid_worker_4"),
    "Zukk'ash Wasp":           ("vermin_swarm",     47, 48, None, "fe_silithid_swarmer", "silithid_worker_3"),
    "Zukk'ash Ravager":        ("humanoid_warrior", 48, 49, None, "fe_silithid_ravager", "silithid_worker_1"),
    "Zukk'ash Resin-Spitter":  ("humanoid_caster",  48, 49, None, "fe_resin_spitter", "silithid_worker_2"),
    "The Deep Mother":         ("beast_large",      49, 49, 2.5, "fe_boss_deep_mother", "silithid_worker_4"),
    "Tunnelmaster Zix'tal":    ("humanoid_warrior", 49, 49, 2.3, "fe_silithid_ravager", "silithid_worker_1"),
}
BOSSES = {n for n, r in ROSTER.items() if r[3]}


def sprite(name):
    own, ph = ROSTER[name][4], ROSTER[name][5]
    return own if (ROOT / "assets/creatures" / f"{own}.png").exists() else ph


def trash(level, basic, second, third, school="physical"):
    t = T(level)
    return [dmg(basic, t, school=school), second(t), third(t)]


def boss(level, school, basic, second, heavy, spread, signature, *, aoe=True, extra=()):
    b = BH(level)
    kit = [opener(basic, b, school), dmg(second, int(b * 0.88), cooldown=4, school=school),
           dmg(heavy, int(b * 1.3), cooldown=4, school=school)]
    kit.append(dmg(spread, int(b * 0.7), cooldown=5, school=school, is_aoe=True) if aoe
               else dot(spread, int(b * 0.4), 5, 4, school=school))
    kit.extend(extra)
    kit.extend(signature)
    kit.append(dict(name="Last Stand", kind="buff", amount=0, cooldown=99, mana_cost=0, school=school,
                    duration=30, self_only=True, hp_below=0.3, stat_mods={"attack_power": int(b * 0.4)}))
    return kit


def kits():
    k = {}
    k["Zukk'ash Hive Worker"] = trash(48, "Digging Claw", lambda t: dmg("Burrow Strike", int(t * 1.25), cooldown=4),
                                      lambda t: hit_with("Chitin Plates", int(t * 0.7), {"armor": 140}, 3, on="buff"))
    k["Zukk'ash Hive Warrior"] = trash(48, "Mandible", lambda t: stun_hit("Pin to the Wall", int(t * 1.1), 5),
                                       lambda t: dmg("Scything Claws", int(t * 0.7), cooldown=4, is_aoe=True))
    k["Zukk'ash Wasp"] = trash(48, "Sting", lambda t: dot("Venom", int(t * 0.3), 4, 3, school="nature",
                                                         dispel_type="poison"),
                               lambda t: dmg("Swarm", int(t * 0.7), cooldown=4, is_aoe=True))
    k["Zukk'ash Ravager"] = trash(49, "Blade-Arm", lambda t: dmg("Ravage", int(t * 1.35), cooldown=4),
                                  lambda t: hit_with("Rending Bite", int(t * 0.8), {"armor": -150}, 3))
    k["Zukk'ash Resin-Spitter"] = trash(49, "Resin Spit", lambda t: hit_with("Gummed Up", int(t * 0.8), {"haste": -14},
                                                                             3, school="nature"),
                                        lambda t: dmg("Burning Resin", int(t * 0.7), cooldown=4, school="nature",
                                                      is_aoe=True), school="nature")
    k["The Deep Mother"] = boss(49, "nature", "Queen's Mandibles", "Brood Venom", "The Hive's Weight", "Call the Swarm",
                                [dmg("The Whole Hive Answers", int(BH(49) * 1.8), cooldown=4, school="nature"),
                                 dot("Larval Burrow", int(BH(49) * 0.5), 5, 4, school="nature", dispel_type="poison")],
                                extra=[heal("Feed on the Brood", int(BH(49) * 1.1), 6, school="nature")])
    k["Tunnelmaster Zix'tal"] = boss(49, "physical", "Digging Blades", "Undermine", "Cave-In", "Spoil Heap",
                                     [dmg("The Tunnel Comes Down", int(BH(49) * 1.8), cooldown=4),
                                      stun_hit("Buried", int(BH(49) * 1.1), 6)])
    return k


#: boss -> [(item, slot, suffix, (a|w, type) or None, stat template)]
POOLS = {
    "The Deep Mother": [
        ("Brood-Queen's Carapace", "chest", "of the Bear", ("a", "plate"), "str_physical"),
        ("Hive-Silk Robe", "chest", "of the Sorcerer", ("a", "cloth"), "int_caster"),
        ("Resin-Sealed Leggings", "legs", "of the Wolf", ("a", "leather"), "agi_int_hybrid"),
        ("Mother's Ovipositor Spike", "main_hand", "of the Physician", ("w", "dagger"), "spi_healer")],
    "Tunnelmaster Zix'tal": [
        ("Zix'tal's Digging Claw", "main_hand", "of the Monkey", ("w", "fist_weapon"), "agi_physical"),
        ("Undermined Mail Girdle", "waist", "of the Gorilla", ("a", "mail"), "str_int_hybrid"),
        ("Tunnel-Dust Cowl", "head", "of the Prophet", ("a", "cloth"), "spi_healer"),
        ("Chitin-Plated Sabatons", "feet", "of the Tiger", ("a", "mail"), "agi_physical")],
}


def build_loot():
    from tools.build_durotar_content import make
    from entities.item_budget import budget_ratio, fit_to_curve
    out, rows = {}, []
    for b, items in POOLS.items():
        ilvl = ROSTER[b][2] + 2
        built = []
        for (name, slot, suffix, typ, template) in items:
            kw = {}
            if typ and typ[0] == "a":
                kw["armor_type"] = typ[1]
            elif typ:
                kw["weapon_type"] = typ[1]
            d = make(name, slot, suffix, ilvl, "", **kw)
            d.pop("flavor_text", None)
            d["stat_template"] = template
            d["item_id"] = "zkh_" + kit_slug(name)
            r = budget_ratio(d)
            if r is not None and not 0.65 <= r <= 1.45:
                fit_to_curve(d)
            built.append(d)
            rows.append((name, slot, "weapon" if typ and typ[0] == "w" else "armor", typ[1] if typ else None,
                         template))
        out[b] = built
    return out, rows


RULES_START = "    # THE ZUKK'ASH HIVE (generated by tools/build_zukkash_hive_content.py; do not edit by hand)\n"
RULES_END = "    # END THE ZUKK'ASH HIVE\n"


def write_sprite_rules():
    path = ROOT / "creature_sprites.py"
    s = path.read_text(encoding="utf-8")
    block = RULES_START + "".join(f'    (r"^{re.escape(n.lower())}$", "{sprite(n)}"),\n' for n in ROSTER) + RULES_END
    if RULES_START in s:
        s = s[:s.index(RULES_START)] + block + s[s.index(RULES_END) + len(RULES_END):]
    else:
        anchor = "    # AZSHARA'S OPEN WORLD (tools/build_azshara_openworld.py)"
        s = s.replace(anchor, block + anchor, 1)
    path.write_text(s, encoding="utf-8")


def check(k, loot):
    bad = []
    if set(k) != set(ROSTER):
        bad.append(f"kits and roster differ: {sorted(set(k) ^ set(ROSTER))}")
    if set(POOLS) != BOSSES:
        bad.append(f"loot pools and bosses differ: {sorted(set(POOLS) ^ BOSSES)}")
    if set(ZH.BOSSES) != BOSSES:
        bad.append(f"bosses on the map {sorted(ZH.BOSSES)} differ from the roster {sorted(BOSSES)}")
    existing = json.loads(CREATURES.read_text(encoding="utf-8"))["creatures"]
    for name, r in ROSTER.items():
        prior = existing.get(name)
        if prior and prior.get("ability_kit") != kit_slug(name):
            bad.append(f"{name} already exists elsewhere; names never repeat")
        if not (ROOT / "assets/creatures" / f"{sprite(name)}.png").exists():
            bad.append(f"{name}'s sprite {sprite(name)} is not on disk")
    names = [i["name"] for v in loot.values() for i in v]
    dup = [n for n, c in Counter(names).items() if c > 1]
    if dup:
        bad.append(f"duplicate item names: {dup}")
    import creature_sprites as CS
    for name, r in ROSTER.items():
        if CS.sprite_for(name, r[0]) != sprite(name):
            bad.append(f"creature_sprites.py draws {name} as {CS.sprite_for(name, r[0])}, not {sprite(name)}")
    return bad


def main():
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    ZH.build_zukkash_hive_baked()
    write_sprite_rules()
    k = kits()
    loot, rows = build_loot()
    bad = check(k, loot)
    if bad:
        print("FAILED - fix the data, not the check:")
        for b in bad:
            print("  -", b)
        return 1
    creatures = {}
    for name, (template, lo, hi, mult, _s, _p) in ROSTER.items():
        e = {"template": template, "level_range": [lo, hi], "is_boss": bool(mult), "ability_kit": kit_slug(name)}
        if mult:
            e["boss_multiplier"] = mult
        creatures[name] = e
    merge_json(CREATURES, "creatures", creatures, "creatures.json")
    merge_json(KITS, "kits", {kit_slug(n): v for n, v in k.items()}, "ability_kits.json")
    raw = ENCOUNTERS.read_text(encoding="utf-8")
    enc = json.loads(raw)
    indent, newline = _detect_format(enc, raw)
    caves = enc["zones"].setdefault(ZH.PARENT, {}).setdefault("caves", {})
    caves[CAVE] = {"name": CAVE, "creatures": {n: (0 if r[3] else 4) for n, r in ROSTER.items()}}
    ENCOUNTERS.write_text(json.dumps(enc, indent=indent, ensure_ascii=False) + ("\n" if newline else ""),
                          encoding="utf-8")
    out = {"_notes": ("Boss loot for the Zukk'ash Hive (Feralas, 47-49). ONE item per kill from the boss's four; "
                      "item_level = boss level + 2. Hand-authored in tools/build_zukkash_hive_content.py.")}
    out.update(loot)
    LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "tools/whole_number_gear.py")], check=True, stdout=subprocess.DEVNULL)
    print(f"{len(ROSTER)} creatures ({len(BOSSES)} bosses); {sum(len(v) for v in loot.values())} boss items")
    return 0


if __name__ == "__main__":
    sys.exit(main())
