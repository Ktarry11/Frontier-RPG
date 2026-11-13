#!/usr/bin/env python3
"""Every talent number is a clean one - at every rank, and in its text.   (idempotent)

    python3 tools/clean_talent_numbers.py [--dry-run]

Kyle, [29]: "Talent percentages must be clean numbers. ASKED BEFORE."

WHAT WAS WRONG. A talent's design is a TOTAL ("Smash damage +16.2%", "hit chance +5%") and the
data stores it per point, as total / ranks. So a three-rank talent worth 35% is 11.67% a rank,
one worth 5 hit is 1.6667 a rank, and the totals themselves came out of an earlier rescale as
16.2%, 10.8%, 13.5%, 18.9%. 1,800 of the 2,461 talents carried a number like that.

THE RULE. Each rank is worth a WHOLE number - a whole percent for a percentage, a whole point
for a rating - never less than one, and the total is that times the ranks. 16.2% over three
ranks becomes 5% a rank, 15%; 35% becomes 12% a rank, 36%; 5 hit becomes 2 a rank, 6. Nothing
moves by more than half a rank's worth, and the description is rewritten to the new total.

A number is read the way the game reads it: a value below 1 is a fraction (0.054 is 5.4%),
anything else is points. Values that are already whole are left exactly as they are.

Run after any talent generator; tools/qa_talent_clean_numbers.py fails until it has been.
"""
import glob
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def half_up(x):
    return int(x + 0.5) if x >= 0 else -int(-x + 0.5)


def in_points(key):
    """True for a stat that is ALWAYS points, even below 1. An ability's own crit bonus is
    added straight to crit chance (Ability._roll_crit), so 0.6 there is six tenths of a
    point - not 60% - and is the one family where "below 1 means a fraction" is wrong."""
    return bool(key) and (key.endswith("_crit") or key in ("crit_chance_physical", "crit_chance_spell",
                                                           "crit_chance", "crit"))


def clean(value, key=None):
    """The clean per-rank value for `value`, in the same unit it was written in."""
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value == 0:
        return value
    sign = -1 if value < 0 else 1
    mag = abs(value)
    if mag < 1 and not in_points(key):            # a fraction: whole percent, at least 1%
        pct = max(1, half_up(mag * 100))
        return sign * pct / 100
    return sign * max(1, half_up(mag))            # points: whole, at least 1


def is_clean(value, key=None):
    return clean(value, key) == value or (isinstance(value, float) and abs(clean(value, key) - value) < 1e-9)


def unit(value, key=None):
    return 100 if (abs(value) < 1 and not in_points(key)) else 1


def shown(value, ranks, key=None):
    """How a total reads in a description: '16.2' for 0.054 x 3, '5' for 1.6667 x 3."""
    return f"{round(abs(value) * ranks * unit(value, key), 1):g}"


#: What tools/rescale_coa_talents.py multiplied each family of CoA talent by (6 Nov). It only
#: rewrote a description when the line quoted ONE number, so several hundred still quote the
#: number from before: "Increases the damage of Chastise by 25%" on a talent that gives 13.5%.
RESCALE_FACTORS = (0.40, 0.50, 0.533, 0.54, 0.60, 0.75, 0.80)


def totals(value, ranks, key=None):
    """(total, per rank) as the numbers a description would quote."""
    u = unit(value, key)
    return round(abs(value) * ranks * u, 2), round(abs(value) * u, 2)


def retell_stale(node):
    """Rewrite percentages in the description that quote the PRE-RESCALE number.

    For each effect whose real total appears nowhere in the text, look for a quoted percentage
    that is that total divided by one of the rescale factors - the number the line was written
    with - and put the real one there. A percentage that several effects disagree about is
    left alone: a stale number is better than a confidently wrong rewrite. Returns how many
    numbers were rewritten.
    """
    text = node.get("description", "")
    ranks = int(node.get("max_points") or 1)
    effects = {k: v for k, v in (node.get("effects") or {}).items()
               if isinstance(v, (int, float)) and not isinstance(v, bool) and v}
    if not effects or "%" not in text:
        return 0
    quoted = {float(m) for m in re.findall(r"(?<![\d.])(\d+(?:\.\d+)?)%", text)}
    real = set()
    for k, v in effects.items():
        real.update(totals(v, ranks, k))
    proposals = {}
    per_rank_text = "per rank" in text.lower() or "per point" in text.lower()
    for k, v in effects.items():
        total, each = totals(v, ranks, k)
        if total in quoted or (each in quoted and per_rank_text):
            continue                                  # this effect is already told truthfully
        want = each if per_rank_text else total
        for q in quoted - real:
            if any(abs(want / q - f) <= 0.035 * f for f in RESCALE_FACTORS):
                proposals.setdefault(q, set()).add(want)
    done = 0
    for q, wants in proposals.items():
        if len(wants) != 1:
            continue
        new = next(iter(wants))
        text = re.sub(r"(?<![\d.])" + re.escape(f"{q:g}") + r"%", f"{new:g}%", text)
        done += 1
    node["description"] = text
    return done


#: Lines the rules above cannot repair: they quote several numbers, or describe something the
#: talent's effects do not hold. Each is rewritten BY HAND to what the effects really do.
#: (tree, talent) -> description.
TEXT_FIXES = {
    ("barbarian_headhunting", "Frothing Savage"): "Increases the critical strike chance of your spears and Berserker Axe by 9%.",
    ("bloodmage_accursed", "Monstrous Appetite"): "Your strikes drink deep, healing you for 12% of the damage dealt, and your blood spells hit 14% harder.",
    ("cultist_corruption", "Terror"): "Increases Horrorbolt and Wrath of the Black Empire damage by 2% per rank.",
    ("cultist_heretic", "Shadow Training"): "Increases Eldritch Mending healing by 2% per rank. Your heals cannot be parried or dodged.",
    ("cultist_heretic", "Grace of the Deep"): "Increases healing done to targets below 50% health by 2% per rank.",
    ("primalist_mountain_king", "Stone Soldier"): "Increases your attack power by 2% and your chance to hit by 1% per rank.",
    ("primalist_mountain_king", "Everything's A Nail"): "Mountain Hammer's effect lasts 1 turn longer per rank.",
    ("primalist_mountain_king", "Earth Destroyer"): "Judgement of the Three Hammers lasts 1 turn longer per rank.",
    ("pyromancer_flameweaving", "Spirit of Fire"): "Inferno Barrier and Volcanic Shell last 1 turn longer.",
    ("pyromancer_flameweaving", "From The Ashes"): "Increases your healing power by 12%.",
    ("pyromancer_flameweaving", "Phoenix Dive"): "Phoenix Dive's shield lasts 1 turn longer.",
    ("reaper_soul", "Spectre's Call"): "Increases the damage of Murder and Soul Strike by 15% and the healing of Deathwind by 12%.",
    ("runemaster_glyphic", "Unleashed Power"): "Increases the damage of Glyphic Ruin and Thaumaturgy by 2% per rank.",
    ("runemaster_riftblade", "Tempo"): "Increases Runeblade damage by 2% per rank.",
    ("shaman_enhancement", "Improved Windfury Totem"): "Your Windfury Totem lasts 1 turn longer per rank.",
    ("shaman_restoration", "Improved Earth Shield"): "Reduces the cooldown of your Earth Shield by 1 turn per rank.",
    ("starcaller_moon_guard", "Starbound"): "Increases your healing done by 2% per rank. Your heals have a 15% chance per rank to bind a star to you, healing you for 50.",
    ("stormbringer_maelstrom", "Conductor In Charge"): "Increases all damage you deal by 3%.",
    ("tinker_invention", "Surge Protector"): "While above 65% mana, your healing is 3% stronger.",
    ("tinker_mechanics", "Cogmaster"): "Increases your critical strike chance by 3%. Your critical strikes have a 50% chance to scavenge 3 Scrap and restore mana.",
    ("tinker_mechanics", "Bombs? BOMBS!"): "Reduces the cooldown of Sticky Bomb by 12% per rank.",
    ("venomancer_fortitude", "Drown In Poison"): "Increases the damage of Venomtip Poison by 15% and of Expulsion by 12%.",
    ("venomancer_vizier", "The Antidote"): "Increases the duration of Rejuvenating Venom by 1 turn.",
}


def fix_file(path, write):
    doc = json.loads(Path(path).read_text())
    nodes = doc["nodes"]
    changed = retold = touched = 0
    for node in (nodes if isinstance(nodes, list) else nodes.values()):
        ranks = int(node.get("max_points") or 1)
        effects = node.get("effects") or {}
        swaps = {}
        for key, value in list(effects.items()):
            if isinstance(value, bool) or not isinstance(value, (int, float)) or is_clean(value, key):
                continue
            new = clean(value, key)
            old_text, new_text = shown(value, ranks, key), shown(new, ranks, key)
            effects[key] = int(new) if float(new).is_integer() and abs(new) >= 1 else new
            changed += 1
            if old_text != new_text:
                swaps[old_text] = new_text
        before_text = node.get("description", "")
        text = before_text
        for old_text, new_text in swaps.items():
            # the number as a whole token: "16.2%" or "by 5 " - never the 5 inside 15
            pattern = r"(?<![\d.])" + re.escape(old_text) + r"(?![\d.])"
            if re.search(pattern, text):
                text = re.sub(pattern, new_text, text)
                retold += 1
        node["description"] = text
        # ...then whatever the line still quotes from before the rescale
        retold += retell_stale(node)
        fixed = TEXT_FIXES.get((os.path.basename(path)[:-5], node.get("name")))
        if fixed:
            node["description"] = fixed
        if node["description"] != before_text:
            touched += 1
    if (changed or touched) and write:
        raw = Path(path).read_text()
        indent = 2 if raw.startswith('{\n  "') else (1 if raw.startswith('{\n "') else 4)
        Path(path).write_text(json.dumps(doc, indent=indent, ensure_ascii="\\u" in raw)
                              + ("\n" if raw.endswith("\n") else ""))
    return changed, retold, touched


def main():
    write = "--dry-run" not in sys.argv
    totals = [0, 0, 0]
    for path in sorted(glob.glob(str(ROOT / "data/talents/*.json"))):
        got = fix_file(path, write)
        totals = [a + b for a, b in zip(totals, got)]
        if got[0] or got[2]:
            print(f"  {os.path.basename(path)[:-5]:38} {got[0]:4} values, {got[1]:3} numbers rewritten "
                  f"in {got[2]:3} descriptions")
    print(f"{totals[0]} values made clean; {totals[1]} description numbers rewritten in "
          f"{totals[2]} descriptions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
