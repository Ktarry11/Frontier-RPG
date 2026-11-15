#!/usr/bin/env python3
"""Caster gear carries SPELL HIT, not weapon hit.

    PYTHONPATH=. python3 tools/split_spell_hit.py            # show
    PYTHONPATH=. python3 tools/split_spell_hit.py --apply

Kyle, 15 Nov 2026: "I want hit rating, yes. We need to have spell hit, physical hit." Until then one hit_rating
served swords and spells. Every stat block in the item, set, gem, recipe, loot and quest-reward data that carries
hit_rating with CASTER stats (Intellect, spell power, healing, spell crit, Spirit, mp5, spell penetration) and no
PHYSICAL ones (Strength, Agility, attack power, physical crit, armour penetration, avoidance) gets spell_hit_rating
instead. Mixed blocks and plain ones (hit + Stamina) keep weapon hit. Creature kits are not items and are skipped.
"""
import glob
import json
import os
import sys

CASTER = {"intellect", "spell_power", "healing_power", "crit_chance_spell", "spirit", "mp5", "mana_per_5",
          "spell_penetration", "fire_spell_power", "frost_spell_power", "nature_spell_power", "shadow_spell_power",
          "arcane_spell_power", "holy_spell_power", "mana"}
PHYS = {"strength", "agility", "attack_power", "ranged_attack_power", "crit_chance_physical", "armor_penetration_pct",
        "expertise", "dodge", "dodge_rating", "parry", "parry_rating", "block_rating", "defense_rating", "block_value"}
SKIP = {"data/creatures/ability_kits.json"}


def walk(node, counts):
    if isinstance(node, dict):
        if "hit_rating" in node and isinstance(node["hit_rating"], (int, float)):
            keys = set(node)
            if keys & CASTER and not keys & PHYS:
                node["spell_hit_rating"] = node.pop("hit_rating")
                counts["spell"] += 1
            else:
                counts["kept"] += 1
        for v in node.values():
            walk(v, counts)
    elif isinstance(node, list):
        for v in node:
            walk(v, counts)


def main():
    apply = "--apply" in sys.argv
    os.chdir(os.path.join(os.path.dirname(__file__), ".."))
    tot = {"spell": 0, "kept": 0}
    for f in sorted(glob.glob("data/**/*.json", recursive=True)):
        if f in SKIP or f.startswith("data/talents/") or f.startswith("data/abilities/"):
            continue
        txt = open(f, encoding="utf-8").read()
        if "hit_rating" not in txt:
            continue
        d = json.loads(txt)
        c = {"spell": 0, "kept": 0}
        walk(d, c)
        if c["spell"] or c["kept"]:
            print(f"  {f:<50} spell hit {c['spell']:>3}   weapon hit kept {c['kept']:>3}")
        tot["spell"] += c["spell"]
        tot["kept"] += c["kept"]
        if apply and c["spell"]:
            open(f, "w", encoding="utf-8").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    print(f"{tot['spell']} stat blocks {'moved' if apply else 'would move'} to spell hit; {tot['kept']} keep weapon hit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
