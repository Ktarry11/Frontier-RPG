#!/usr/bin/env python3
"""Recruit abilities grow at 15 / 30 / 45 / 60.

    python3 tools/rank_kit_abilities.py [--apply]

Kyle, 13 Nov 2026: "we upgrade their abilities at 15/30/45/60 so they should (WHEN POSSIBLE)
have 5 ranks ... This is for attacks or spells or heals that have potency ... these are trump
cards to make characters that have similar classes and specs stand out from one another."

Every one of the 201 had ONE rank, sized for level 1. A class's bread-and-butter attack grows
from about 44 at level 1 to about 140 at 60, so by the middle of the game a recruit's own
trump card hit softer than the Heroic Strike beside it.

What gets five ranks (Kyle: "Only ones that do damage, or heal"): an attack, a spell, a heal,
a damage- or heal-over-time, a flat shield, a trap's damage, a heal armed on taking damage. What does not:
buffs and debuffs, a percentage (30% more damage is 30% at any level), a heal for a
share of maximum health, a dispel, a summon (pets scale themselves), anything that rearranges.

The last rank is sized against the CLASS kits at 60, not against its own level-1 number - see
TRUMP below. Mana costs rise with rank (x1, 1.4, 1.8, 2.2, 2.6), as class spells do; rage,
energy, focus and the other small pools stay flat, as class attacks do.

Rebuilt from rank 1 every run, so it is safe to run twice.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KITS = ROOT / "data" / "npcs" / "personal_kits.json"

LEVELS = (1, 15, 30, 45, 60)
MANA = (1.0, 1.4, 1.8, 2.2, 2.6)
POTENCY_TYPES = ("damage", "spell_damage", "ranged_damage", "heal", "hot", "dot", "spell_dot",
                 "damage_and_heal")
WIDE = ("party", "enemy_aoe", "all_enemies", "all_allies")

#: HOW MUCH BIGGER THAN A CLASS ABILITY. Kyle, 13 Nov: "We need to ensure the END rank is
#: stronger than lvl 60 abilities. So that includes for dots, hots etc ... i can not stress
#: enough how these should be massive 'oh shit' buttons, like trump cards. hence why they have
#: 10-15 turn CDs."
#:
#: The first version tripled the level-1 number and stopped. Measured against the class kits at
#: 60 that left a recruit's heal at 120-420 beside class heals of 480, and a damage-over-time
#: at 135 beside class ones of 285: a 12-turn cooldown for less than a spammable spell.
#:
#: So the last rank is set from the CLASS abilities instead: the strong end (90th percentile) of
#: what any class has at 60 for the same kind and width, times TRUMP. An ability authored
#: bigger than its neighbours stays bigger (its share of its group's median, held between
#: LOW and HIGH), and the ranks between run in a straight line from the authored level-1 number.
TRUMP = 2.0
LOW, HIGH = 1.6, 3.0
#: Below this many turns of cooldown an ability is not a trump card, it is a rotation button.
TRUMP_COOLDOWN = 6
SPAMMABLE = 1.15


def kind_of(a):
    """(kind, 'wide' | 'single') - which class abilities this one is measured against."""
    t = a["effect_type"]
    wide = "wide" if a.get("target_type") in WIDE else "single"
    if a.get("absorb"):
        return "shield", wide
    if (a.get("on_damage_hot") or {}).get("potency"):
        return "hot", "wide"
    if a.get("trap") or a.get("damage_per_dispel"):
        return "damage", "single"
    return {"ranged_damage": "damage", "damage_and_heal": "damage", "spell_dot": "dot"}.get(t, t), wide


_class_refs = None


def class_refs():
    """{(kind, width): the 90th-percentile top-rank effect_value among class abilities usable
    by level 60}. Read from data/abilities, so it moves when the classes do."""
    global _class_refs
    if _class_refs is not None:
        return _class_refs
    rows = {}
    for path in sorted((ROOT / "data" / "abilities").glob("*.json")):
        d = json.loads(path.read_text())
        items = d if isinstance(d, list) else d.get("abilities", d)
        items = items.values() if isinstance(items, dict) else items
        for a in items:
            if not isinstance(a, dict) or not a.get("ranks") or a.get("effect_type") not in POTENCY_TYPES:
                continue
            top = [r for r in a["ranks"] if r.get("level_req", 1) <= 60]
            ev = (top[-1].get("effect_value") or 0) if top else 0
            if ev > 0:
                rows.setdefault(kind_of({"effect_type": a["effect_type"], "target_type": a.get("target_type")}), []).append(ev)
    refs = {}
    import statistics
    for key, evs in rows.items():
        # Not the freaks: Lay on Hands, Revive Pet and the revives are filed as heals and are
        # five to ten times an ordinary one. Anything over three times its group's median is
        # left out before the percentile is taken.
        mid = statistics.median(evs)
        evs = sorted(e for e in evs if e <= mid * 3)
        refs[key] = evs[max(0, int(len(evs) * 0.9) - 1)]
    # A shield is measured against a single-target heal (0.8 of it): the classes have too few
    # flat shields to take a percentile from. A party shield against a party heal.
    for width in ("single", "wide"):
        refs[("shield", width)] = int(refs.get(("heal", width), 300) * 0.8)
    _class_refs = refs
    return refs


def grows(a):
    """What about this ability is a number that should grow: a set of
    'effect_value' / 'absorb' / 'on_damage_hot_potency', possibly empty."""
    out = set()
    base = a["ranks"][0]
    if a["effect_type"] in POTENCY_TYPES and (base.get("effect_value") or 0) > 0:
        out.add("effect_value")
    if a.get("trap") or a.get("damage_per_dispel"):
        if (base.get("effect_value") or 0) > 0:
            out.add("effect_value")
    # Kyle, 13 Nov, as this was being built: "not each ability will get multiple ranks! Only
    # ones that do damage, or heal." Then: "shield or absorb too, yes."
    if a.get("absorb"):
        out.add("absorb")
    if (a.get("on_damage_hot") or {}).get("potency"):
        out.add("on_damage_hot_potency")
    return out


def base_size(a):
    """The authored level-1 number for whatever grows."""
    what = grows(a)
    if "absorb" in what:
        return a["absorb"]
    if "on_damage_hot_potency" in what:
        return a["on_damage_hot"]["potency"] * a["on_damage_hot"].get("duration", 3)
    return a["ranks"][0].get("effect_value") or 0


_medians = None


def group_medians(doc):
    global _medians
    if _medians is None:
        import statistics
        groups = {}
        for kid, kit in doc.items():
            if kid.startswith("_"):
                continue
            for a in kit["abilities"]:
                if grows(a):
                    groups.setdefault(kind_of(a), []).append(base_size(a))
        _medians = {k: statistics.median(v) for k, v in groups.items()}
    return _medians


def final_size(a, doc):
    """What the last rank is worth: TRUMP times the strong end of the class kits, scaled by how
    this ability was authored against its own group, and never smaller than three times its
    level-1 number."""
    key = kind_of(a)
    ref = class_refs().get(key) or class_refs().get((key[0], "single")) or 200
    if (a.get("cooldown") or 0) < TRUMP_COOLDOWN:
        # Usable every turn or nearly: it should beat a class ability, not double one.
        return int(round(max(base_size(a) * 3, ref * SPAMMABLE)))
    share = base_size(a) / max(1, group_medians(doc).get(key, base_size(a)))
    return int(round(max(base_size(a) * 3, ref * min(HIGH, max(LOW, TRUMP * share)))))


def ranks_for(a, doc):
    what = grows(a)
    base = dict(a["ranks"][0])
    for k in ("absorb", "on_damage_hot_potency"):
        base.pop(k, None)
    base["rank"], base["level_req"] = 1, 1
    if not what:
        return [base]
    mana = a.get("resource_type") == "mana"
    start, end = base_size(a), final_size(a, doc)
    out = []
    for i, lvl in enumerate(LEVELS):
        size = start + (end - start) * i / 4.0
        r = dict(base)
        r["rank"], r["level_req"] = i + 1, lvl
        if "effect_value" in what:
            r["effect_value"] = int(round(size))
        if "absorb" in what:
            r["absorb"] = int(round(size))
        if "on_damage_hot_potency" in what:
            r["on_damage_hot_potency"] = int(round(size / a["on_damage_hot"].get("duration", 3)))
        if mana and base.get("cost"):
            r["cost"] = int(round(base["cost"] * MANA[i]))
        out.append(r)
    return out


def main():
    doc = json.loads(KITS.read_text())
    grown = same = 0
    for kid, kit in doc.items():
        if kid.startswith("_"):
            continue
        for a in kit["abilities"]:
            new = ranks_for(a, doc)
            grown += len(new) == 5
            same += len(new) == 1
            a["ranks"] = new
    print(f"{grown} abilities with five ranks, {same} that do not grow (percentages, dispels, summons)")
    if "--apply" in sys.argv:
        KITS.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
        print("written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
