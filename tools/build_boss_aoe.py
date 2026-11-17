#!/usr/bin/env python3
"""Write data/balance/boss_aoe.json: party-wide damage for every dungeon boss from level 40, in more than one shape.

    PYTHONPATH=. python3 tools/build_boss_aoe.py [--check]

Kyle, 16 Nov 2026, signing off the healing formula: "I think having more varied aoe damage bosses will help make it
more spicy post lvl 40 too". With heals sized against the tank (combat/heal_formula.py), a boss that only ever hits
the tank leaves a healer one job; party damage is what makes a healer choose.

Measured first: of the 90 dungeon bosses (and hand-tuned ones) that reach 40, 6 had no party-wide ability at all and
43 had exactly one, almost always the same shape (a party-wide hit). Two shapes, so every one of them has both:

  BLAST  a hit on the whole party (combat takes 0.6 each), every 4 turns. Sized from the boss's own most common hit,
         so it lands about 10-12% of a tank's health on each person once the boss's damage is on the reference
         (tools/calibrate_boss_damage.py).
  BLIGHT a damage-over-time on the whole party, every 5 turns for 4, in a dispellable school where the boss's school
         has one (curse, magic, poison, disease; a physical boss bleeds, which nothing cleanses).
  SPICE  every third boss also gets a lighter WOUNDING blast (every 6 turns) that leaves healing taken cut by 20% for
         3 turns on whoever it hit: a reason to heal ahead of it, and a reason the tank isn't the only bar to watch

A boss that already has a shape keeps its own and only gets the one it's missing. The abilities live in this file,
keyed by creature name, and Monster reads them after its kit (entities/monster.py), so a kit builder that rewrites
data/creatures/ability_kits.json can't drop them. Rerun tools/calibrate_boss_damage.py after this: the averages move.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
OUT = ROOT / "data/balance/boss_aoe.json"
FROM_LEVEL = 40

#: school -> (blast name, blight name, dispel type of the blight)
FLAVOUR = {
    "shadow": ("Shadow Nova", "Creeping Dread", "curse"),
    "frost": ("Frost Nova", "Bitter Chill", "magic"),
    "fire": ("Flamestrike", "Lingering Embers", "magic"),
    "arcane": ("Arcane Explosion", "Mana Burn Field", "magic"),
    "nature": ("Thunderclap", "Poison Cloud", "poison"),
    "holy": ("Consecration", "Searing Brand", "magic"),
    "physical": ("Whirlwind", "Rending Wounds", None),
}
#: school -> the wounding blast's name
WOUND = {"shadow": "Withering Shriek", "frost": "Shattering Cold", "fire": "Scorching Wave", "arcane": "Unravel",
         "nature": "Venom Spray", "holy": "Judgement", "physical": "Mortal Sweep"}
DISEASE_HINTS = ("plague", "rot", "blight", "gorger", "abomination", "flesh", "carrion", "maggot", "ghoul")


def is_blast(a):
    return a.get("kind", "damage") == "damage" and a.get("is_aoe")


def is_blight(a):
    return a.get("kind") == "dot" and a.get("is_aoe")


def main_hit(kit):
    """The boss's most common hit: its lowest-cooldown single-target damage ability (ties: the smaller)."""
    hits = [a for a in kit if a.get("kind", "damage") == "damage" and not a.get("is_aoe") and a.get("amount")]
    if not hits:
        return None
    return min(hits, key=lambda a: (a.get("cooldown", 0) or 0, a.get("amount", 0)))


def school_of(kit):
    from collections import Counter
    c = Counter(a.get("school", "physical") for a in kit if a.get("kind", "damage") in ("damage", "dot"))
    return c.most_common(1)[0][0] if c else "physical"


def build():
    from world import difficulty as D
    cre = json.loads((ROOT / "data/creatures/creatures.json").read_text(encoding="utf-8"))
    cre = cre.get("creatures", cre)
    kits = json.loads((ROOT / "data/creatures/ability_kits.json").read_text(encoding="utf-8"))
    kits = kits.get("kits", kits)
    dungeon = D.dungeon_bosses() | set(D.table().get("tuned_bosses") or ())
    out, n_added, spice, seen = {}, 0, 0, 0
    for name in sorted(dungeon):
        d = cre.get(name) or {}
        if not d.get("is_boss") or (d.get("level_range") or [0, 0])[1] < FROM_LEVEL:
            continue
        kit = kits.get(d.get("ability_kit")) or []
        base = main_hit(kit)
        if base is None:
            continue
        school = school_of(kit)
        blast_name, blight_name, dispel = FLAVOUR.get(school, FLAVOUR["physical"])
        if any(h in name.lower() for h in DISEASE_HINTS) and school in ("shadow", "nature", "physical"):
            blight_name, dispel = "Festering Plague", "disease"
        add = []
        amt = int(base["amount"])
        if not any(is_blast(a) for a in kit):
            e = {"name": blast_name, "kind": "damage", "amount": max(1, int(amt * 0.85)), "cooldown": 4,
                 "mana_cost": 0, "school": school, "is_aoe": True}
            add.append(e)
        if not any(is_blight(a) for a in kit):
            e = {"name": blight_name, "kind": "dot", "amount": max(1, int(amt * 0.22)), "duration": 4,
                 "cooldown": 5, "mana_cost": 0, "school": school, "is_aoe": True}
            if dispel:
                e["dispel_type"] = dispel
            add.append(e)
        # SPICE: every third boss also carries a wounding blast, lighter, that leaves healing taken cut by 20% for 3
        # turns on everyone it hit
        if seen % 3 == 0:
            add.append({"name": WOUND.get(school, WOUND["physical"]), "kind": "damage",
                        "amount": max(1, int(amt * 0.5)), "cooldown": 6, "mana_cost": 0, "school": school,
                        "is_aoe": True,
                        "rider": {"effect": "debuff", "duration": 3, "stat_mods": {"healing_taken_pct": -20}}})
            spice += 1
        seen += 1
        if add:
            out[name] = add
            n_added += len(add)
    return out, n_added, spice


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    out, n, spice = build()
    data = {"_about": "Party-wide damage added to dungeon bosses from level 40, by name; read by entities/monster.py "
                      "after the kit. Written by tools/build_boss_aoe.py.", "from_level": FROM_LEVEL, "bosses": out}
    if args.check:
        cur = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
        same = cur.get("bosses") == out
        print("up to date" if same else "OUT OF DATE")
        return 0 if same else 1
    OUT.write_text(json.dumps(data, indent=1), encoding="utf-8")
    print(f"{len(out)} bosses get {n} abilities ({spice} blasts also cut healing taken). Wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    sys.exit(main())
