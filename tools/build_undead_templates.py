#!/usr/bin/env python3
"""Add the missing undead chassis, and put the undead on them.

    PYTHONPATH=. python3 tools/build_undead_templates.py [--apply]

WHAT WAS WRONG. Kyle: "we can fix up the ghouls, yes." The Rotting Ghoul sat
on humanoid_warrior and so carried no shadow resistance at all - but the
ghoul was a symptom. There is exactly ONE undead template in the game,
undead_basic, and it is a melee rage chassis with no mana and no spell
power. So every undead CASTER and every undead BEAST has had to sit on a
living template to function at all, and a creature only ever gets the undead
resistance baseline (shadow 20, frost 10) from its template.

Most of them were covered by accident. CreatureManager._apply_cast_affinity
gives a spawn 40 resistance in whatever school its own kit casts, so a
shadow-casting wraith comes out shadow-40 regardless of its chassis. What
that cannot cover is an undead that does NOT cast the school it should
resist, and measuring the spawns found exactly three:

    Rotting Ghoul        shadow 0   (its kit is physical + nature)
    Zombie Bear          shadow 0   (physical + nature)
    Deathguard Captain   EVERY SCHOOL 0  - a Forsaken boss with no
                         resistance to anything, because its kit is
                         entirely physical

BEING UNDEAD CHANGES WHAT YOU RESIST, NOT HOW BIG YOU ARE. The first
version of this derived the whole undead_basic-against-humanoid_warrior
delta - less health, softer hit, slower, no parry - and applied it to the
other chassis. The resistances came out right and the bodies came out 14-18%
smaller: Vile Plague Abomination 2111 -> 1809 health, Tome Wraith -17%,
Zombie Bear -18%. Nothing broke (qa_difficulty_bands still passed) but that
is an unrequested nerf to eleven creatures including two bosses, whose
encounters were tuned at the numbers they already had.

So the new chassis take ONLY the resistance baseline - shadow 20, frost 10,
read off undead_basic - and keep their living body exactly. The one
exception is the Rotting Ghoul, which moves to undead_basic outright,
because it IS a ghoul and was sitting on a soldier's body: 476 health and 8
parry, against the 426 and no parry the game's other hundred-odd undead
carry. That one is a correction rather than a retune, and it is the one Kyle
asked for.

Name, default_kit and resource_type are untouched: an undead caster still
runs on mana, and every creature names its own ability_kit anyway.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "data/creatures/templates.json"
CREATURES = ROOT / "data/creatures/creatures.json"

#: The pair that states what being undead means, in the data's own terms.
BASE, UNDEAD = "humanoid_warrior", "undead_basic"

#: living chassis -> the undead one derived from it
DERIVE = {"humanoid_warrior": "undead_warrior",
          "humanoid_caster": "undead_caster",
          "beast_basic": "undead_beast"}

NAMES = {"undead_warrior": "Undead Warrior",
         "undead_caster": "Undead Caster",
         "undead_beast": "Undead Beast"}

RESISTS = ("base_fire_resist", "base_frost_resist", "base_nature_resist",
           "base_shadow_resist", "base_arcane_resist", "base_holy_resist")

#: Creatures that ARE undead and were on a living chassis. Split by the body
#: they need. The casters are all already shadow-40 through cast affinity;
#: they are moved anyway so the baseline is theirs by nature rather than by
#: what they happen to cast - an Ambermill Ghost-Mage casts frost and came
#: out with shadow 0.
MOVE = {
    # THE ONE BODY THAT MOVES. A ghoul on a soldier's chassis, at 476 health
    # and 8 parry where the game's other undead carry 426 and none.
    "undead_basic": [
        "Rotting Ghoul",
    ],
    # Resistances fixed, bodies left exactly as their content pass tuned
    # them. The Deathguard Captain is the only creature in the game measured
    # at zero resistance in EVERY school - a Forsaken boss whose kit is
    # entirely physical, so cast affinity had nothing to give it.
    "undead_warrior": [
        "Plague Zombie",
        "Plague Abomination",
        "Vile Plague Abomination",
        "Deathguard Captain",
    ],
    "undead_caster": [
        "Howling Wraith",
        "Talon Wraith",
        "Tome Wraith",
        "Ambermill Ghost-Mage",
    ],
    "undead_beast": [
        "Zombie Bear",
    ],
}

#: Read as undead by name, left alone on purpose - the call is Kyle's, not a
#: tool's. Printed every run so they do not quietly become permanent.
FLAGGED = {
    "Weeping Shade": "already the best-resisted creature of the set - shadow "
                     "40 from cast affinity plus a flat 10 in every school "
                     "from elemental_caster, so it needs nothing, and moving "
                     "it off that chassis would only cost it the spread",
    "Scourge Necromancer": "in a Scourge cave and casts Shadow Bolt, but a "
                           "Scourge necromancer is a LIVING cultist in real "
                           "Classic - undead chassis or not is a lore call",
    "Feral Rotting Kobold": "a kobold with rot, which is a diseased living "
                            "thing rather than an animated corpse",
    "Gorge the Corpsegrinder": "named for what it eats, not what it is",
    "Crypt Crawler": "lives in a crypt; vermin, not risen",
    "Bone-Strewn Cur": "scavenger named for the bones around it",
    "Bonefield Hyena": "as above",
    "Boneyard Vulture": "as above",
    "Old Bonepicker": "as above",
    "Roost Bonepicker": "as above",
}


def undead_delta(tmpl):
    """The undead resistance baseline, read off UNDEAD.

    Read rather than typed so that retuning undead_basic - the one place
    the game states what undead resist - carries to the other three
    chassis on a re-run instead of leaving them behind. BASE is still
    named in the report, because undead_basic against humanoid_warrior is
    the comparison that shows the baseline is an undead trait and not just
    a low-level-ghoul one.
    """
    b = tmpl[UNDEAD]
    return {"resists": {f: b.get(f, 0) for f in RESISTS}}


def derive(src, key, d):
    """The living chassis with the undead resistance baseline on top.

    max(), not replace: a ghost-mage's arcane 10 is a CASTER trait and an
    elemental's spread is an elemental one, so the undead floor is added
    under whatever the body already resists rather than overwriting it.
    """
    out = dict(src)
    out["name"] = NAMES[key]
    for f in RESISTS:
        out[f] = max(src.get(f, 0), d["resists"].get(f, 0))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    tdoc = json.loads(TEMPLATES.read_text(encoding="utf-8"))
    tmpl = tdoc.get("templates", tdoc)
    cdoc = json.loads(CREATURES.read_text(encoding="utf-8"))
    cre = cdoc["creatures"]

    d = undead_delta(tmpl)
    print(f"the undead resistance baseline, read off {UNDEAD}:")
    print("  " + ", ".join(
        f"{k.replace('base_','').replace('_resist','')} {v}"
        for k, v in d["resists"].items() if v))

    print("\nnew templates:")
    for src_key, new_key in DERIVE.items():
        tmpl[new_key] = derive(tmpl[src_key], new_key, d)
        s, n = tmpl[src_key], tmpl[new_key]
        body = ("body unchanged" if all(s[k] == n[k] for k in
                ("base_hp", "base_attack", "base_armor", "base_parry",
                 "base_dodge", "speed", "crit_chance")) else "BODY CHANGED")
        print(f"  {new_key:16} from {src_key:17} {body}, "
              f"shadow {s['base_shadow_resist']}->{n['base_shadow_resist']}, "
              f"frost {s['base_frost_resist']}->{n['base_frost_resist']}")

    print("\nre-templated:")
    missing = []
    for new_key, names in MOVE.items():
        for n in names:
            if n not in cre:
                missing.append(n)
                continue
            old = cre[n].get("template")
            cre[n]["template"] = new_key
            print(f"  {n:26} {old:17} -> {new_key}")
    if missing:
        print(f"\n  NOT FOUND, nothing written: {missing}")
        return 1

    print("\nread as undead and deliberately left alone - Kyle's call:")
    for n, why in FLAGGED.items():
        print(f"  {n:26} {why}")

    if not args.apply:
        print("\n(report only; pass --apply to write)")
        return 0
    TEMPLATES.write_text(json.dumps(tdoc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    CREATURES.write_text(json.dumps(cdoc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nwrote {TEMPLATES}\nwrote {CREATURES}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
