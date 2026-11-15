#!/usr/bin/env python3
"""Talents whose effects are read by nothing - a talent point that does nothing.

    PYTHONPATH=. python3 tools/audit_dead_talent_keys.py [--verbose]

Found in the class pass, 15 Nov 2026: Enhancement's Mental Quickness promises "spell power equal to 10% of your
attack power per rank" through spell_power_from_ap_pct, and Mental Dexterity attack power from Intellect through
attack_power_from_intellect_pct - neither key is read anywhere, so Enhancement's spells ran on almost no spell
power. Static Shock and Maelstrom Weapon have no effects at all. tools/audit_talents.py checks wording and numbers,
not whether an effect is ever READ, so dead talents slipped through.

A key counts as read when the engine source (combat/, entities/, world/, ui/, core/) names it as a string, or it
belongs to a family the engine builds dynamically:
  ability_<ability_id>_<suffix>        Ability._talent(f"ability_{id}_...") for the suffixes it reads
  <school>_<suffix>                    per-school damage, crit damage, spell power, resistance, DoT damage
  anything StatusEffect/stat code folds generically (stat names the character sheet carries)
Reports: talents with NO effects (description only), and talents whose effect keys are all or partly dead.
"""
import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

SCHOOLS = ("fire", "frost", "arcane", "shadow", "nature", "holy", "physical", "shadowfrost", "magic", "spell",
           "chaos", "fel", "void", "blood", "storm", "lightning", "plague", "poison", "bleed")
DIRS = ("combat", "entities", "world", "ui", "core")
#: keys the engine reads through a computed name - the stems after "<something>_"
ABILITY_SUFFIXES = ("potency", "healing", "duration", "damage", "crit_damage", "crit", "cost_pct", "cost",
                    "cooldown_pct", "cooldown", "range", "targets", "heal", "absorb", "stacks", "chance")
SCHOOL_SUFFIXES = ("damage", "spell_damage", "dot_damage", "damage_pct", "crit_damage_pct", "spell_power",
                   "resistance", "damage_taken_pct", "crit", "crit_damage")


def source_text():
    parts = []
    for d in DIRS:
        for f in glob.glob(f"{d}/**/*.py", recursive=True):
            parts.append(Path(f).read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(parts)


def sheet_stats():
    """Stat names that fold straight into Character bonuses (anything the sheet sums generically)."""
    try:
        sys.path.insert(0, str(ROOT))
        from entities.character import Character
        return set(getattr(Character, "WHOLE_NUMBER_STATS", ()) or ())
    except Exception:                                           # noqa: BLE001
        return set()


CONVERSION = re.compile(r"^([a-z_]+?)_from_([a-z_]+)_pct$")


def is_read(key, src, ability_ids):
    if f'"{key}"' in src or f"'{key}'" in src:
        return True
    # "<target>_from_<source>_pct": Character._apply_stat_conversions (15 Nov 2026) for its known targets
    # combined-school damage keys ("arcane_fire_frost_nature_damage_pct", "holy_fire_spell_damage"): read by
    # Ability._school_damage_bonus, which splits the name into schools
    for suffix in ("_spell_damage", "_damage_pct"):
        if key.endswith(suffix) and len(key[:-len(suffix)].split("_")) > 1 and \
                all(p in SCHOOLS for p in key[:-len(suffix)].split("_")):
            return True
    m = CONVERSION.match(key)
    if m:
        try:
            from entities.character import Character
            return m.group(1) in Character.CONVERSION_TARGETS and m.group(2) in (
                "strength", "agility", "intellect", "spirit", "stamina", "str_int", "weapon", "ap", "attack_power")
        except Exception:                                       # noqa: BLE001
            return False
    if key.startswith("ability_"):
        rest = key[len("ability_"):]
        for aid in ability_ids:
            if rest.startswith(aid + "_") and rest[len(aid) + 1:] in ABILITY_SUFFIXES:
                return True
        return False
    for sch in SCHOOLS:
        if key.startswith(sch + "_") and key[len(sch) + 1:] in SCHOOL_SUFFIXES:
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    src = source_text()
    ability_ids = set()
    for f in glob.glob("data/abilities/*.json"):
        d = json.load(open(f, encoding="utf-8"))
        L = d if isinstance(d, list) else d.get("abilities", d)
        for e in (L.values() if isinstance(L, dict) else L):
            if isinstance(e, dict) and e.get("ability_id"):
                ability_ids.add(e["ability_id"])
    ability_ids = sorted(ability_ids, key=len, reverse=True)
    empty, dead, partly, total = [], [], [], 0
    dead_keys = {}
    for f in sorted(glob.glob("data/talents/*.json")):
        d = json.load(open(f, encoding="utf-8"))
        nodes = d.get("nodes") or d.get("talents") or d
        for n in (nodes if isinstance(nodes, list) else nodes.values()):
            if not isinstance(n, dict) or "talent_id" not in n:
                continue
            total += 1
            eff = n.get("effects") or {}
            tid = n["talent_id"]
            if not eff and not n.get("proc") and not n.get("procs") and not n.get("unlock_ability"):
                empty.append((tid, n.get("name"), (n.get("description") or "")[:90]))
                continue
            bad = [k for k in eff if not is_read(k, src, ability_ids)]
            for k in bad:
                dead_keys.setdefault(k, []).append(tid)
            if bad and len(bad) == len(eff):
                dead.append((tid, n.get("name"), bad))
            elif bad:
                partly.append((tid, n.get("name"), bad))
    print(f"audited {total} talents")
    print(f"\n{len(empty)} talents with NO effects (the description promises something; nothing happens):")
    for t in empty[: (None if args.verbose else 40)]:
        print(f"   {t[0]} ({t[1]}): {t[2]}")
    print(f"\n{len(dead)} talents whose every effect key is read by nothing:")
    for t in dead[: (None if args.verbose else 40)]:
        print(f"   {t[0]} ({t[1]}): {t[2]}")
    print(f"\n{len(partly)} talents with some dead keys:")
    for t in partly[: (None if args.verbose else 25)]:
        print(f"   {t[0]} ({t[1]}): {t[2]}")
    print(f"\n{len(dead_keys)} distinct dead keys, most used first:")
    for k, v in sorted(dead_keys.items(), key=lambda kv: -len(kv[1]))[:40]:
        print(f"   {k:44} {len(v)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
