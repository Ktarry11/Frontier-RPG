#!/usr/bin/env python3
"""Carry tailoring, leatherworking and woodworking to skill 300.

    PYTHONPATH=. python3 tools/build_professions_300.py [--apply] [profession ...]

Idempotent. Prints the plan by default; --apply writes it.

=============================================================================
WHY
=============================================================================

Kyle, 7 Nov 2026: "Go to skill 300", and "I want crafting to be FULLY viable
as a path alternative to raids and Dungeons."

After the ladder work, each gatherable runs 1-300 with ~22 materials. The
professions did not follow:

    tailoring      gear stopped at 208, and ELEVEN of twenty-two cloths had
                   no bolt recipe at all, so the cloth was unspinnable
    leatherworking gear stopped at 295 but four leathers went unused
    woodworking    gear stopped at 205, so the top two tiers of stick, fiber
                   and pages that tools/build_woodworking_300.py created had
                   nothing to feed

This is the same shape blacksmithing was in before tools/build_blacksmithing_300.py:
the recipe skill climbed while the materials stood still.

=============================================================================
ROLE PAIRS
=============================================================================

Kyle chose pairs over one-role-per-material or a free-for-all: each material
covers two related roles. The pairs differ per profession because the armour
does:

    tailoring       cloth is caster kit, so int_caster + spi_healer, with an
                    agi_int_hybrid line for Tinker, Felsworn, Venomancer and
                    Witch Doctor
    leatherworking  agi_physical + agi_int_hybrid for rogues and rangers, AND
                    spi_healer - Kyle: "Resto druid is spi leather". Its mail
                    line carries int_caster for elemental shaman.
    woodworking     staves, bows and wands, so int_caster + spi_healer and
                    agi_physical + agi_int_hybrid

=============================================================================
EPICS AND RAID PARITY
=============================================================================

Same rule blacksmithing uses, from the game's own formula
(world/crafting_manager.py): item_level = skill * 60 / 300 + 1. Skill 300 is
item level 61; boss drops cap at rare, item level 57. Epic begins at skill 265
(item level 54) rather than at the first high material, because an epic that
loses to a dungeon drop is worse for the crafting path than no epic at all.
"""
import argparse
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MATS = ROOT / "data" / "gathering" / "materials.json"

EPIC_FROM, RARE_FROM, CEILING = 265, 150, 300

PAIRS = {
    "CASTER": ("int_caster", "spi_healer"),
    "AGI":    ("agi_physical", "agi_int_hybrid"),
    "HYBRID": ("agi_int_hybrid", "int_caster"),
}

CLOTH_SLOTS = ["head", "shoulder", "chest", "wrist", "hands", "waist", "legs", "feet", "back"]
LEATHER_SLOTS = CLOTH_SLOTS

#: profession -> config
PROFS = {
    "tailoring": dict(
        file="data/crafting/recipes.json", key="tailoring",
        family="bolt", armor_types=["cloth"], slots=CLOTH_SLOTS,
        pairs=["CASTER", "CASTER", "HYBRID"], weapons=[], per_mat=4,
        piece={"head": "Hood", "shoulder": "Mantle", "chest": "Robe",
               "wrist": "Cuffs", "hands": "Gloves", "waist": "Sash",
               "legs": "Leggings", "feet": "Slippers", "back": "Cloak"}),
    "leatherworking": dict(
        file="data/leatherworking/recipes.json", key=None,
        family="leather", armor_types=["leather", "mail"], slots=LEATHER_SLOTS,
        pairs=["AGI", "CASTER", "AGI"], weapons=[], per_mat=4,
        piece={"head": "Helm", "shoulder": "Spaulders", "chest": "Vest",
               "wrist": "Bracers", "hands": "Gloves", "waist": "Belt",
               "legs": "Pants", "feet": "Boots", "back": "Cloak"}),
    "woodworking": dict(
        file="data/crafting/recipes.json", key="woodworking",
        family="plank", armor_types=[], slots=[],
        pairs=["CASTER", "AGI"], per_mat=0,
        weapons=[("main_hand", "wand"), ("two_hand", "staff"),
                 ("ranged", "bow"), ("two_hand", "polearm"),
                 ("ranged", "crossbow"), ("off_hand", "tome")],
        per_weapon=3,
        wname={"wand": "Wand", "staff": "Staff", "bow": "Longbow",
               "polearm": "Spear", "crossbow": "Crossbow", "tome": "Codex"}),
}

#: Which weapon types suit which role - no caster longbows.
WEAPON_ROLE = {
    "wand": "CASTER", "staff": "CASTER", "tome": "CASTER",
    "bow": "AGI", "crossbow": "AGI", "polearm": "AGI",
}

COST = {"chest": 8, "legs": 7, "head": 6, "shoulder": 5, "hands": 4,
        "feet": 4, "waist": 4, "wrist": 3, "back": 4,
        "main_hand": 5, "two_hand": 8, "ranged": 7, "off_hand": 5}


def item_level(skill):
    return max(1, int(skill * 60 / 300) + 1)


def rarity(skill):
    return "epic" if skill >= EPIC_FROM else ("rare" if skill >= RARE_FROM else "uncommon")


def spread(lo):
    return [lo + 5, lo + 15, lo + 25, lo + 35]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("professions", nargs="*")
    args = ap.parse_args()

    mats_doc = json.loads(MATS.read_text())
    mats = mats_doc["materials"]
    want = set(args.professions) or set(PROFS)
    docs, summary = {}, []

    for prof in sorted(want & set(PROFS)):
        cfg = PROFS[prof]
        rel, key = cfg["file"], cfg["key"]
        if rel not in docs:
            docs[rel] = json.loads((ROOT / rel).read_text())
        recipes = docs[rel]["professions"][key]["recipes"] if key else docs[rel]["recipes"]

        # ---- tailoring first needs a bolt for every cloth
        made_bolts = 0
        if prof == "tailoring":
            spun = {i for r in recipes.values() if isinstance(r, dict)
                    for i in (r.get("inputs") or {}) if i.startswith("cloth_")}
            for mid, m in sorted(mats.items(),
                                 key=lambda kv: (kv[1].get("skill_range") or [0])[0]):
                if m["material_type"] != "cloth" or mid in spun:
                    continue
                sk = (m.get("skill_range") or [0])[0]
                if sk > CEILING:
                    continue
                bolt = "bolt_" + mid[len("cloth_"):]
                if bolt not in mats:
                    continue
                rid = f"p300_bolt_{mid[len('cloth_'):]}"
                if rid in recipes:
                    continue
                made_bolts += 1
                if args.apply:
                    recipes[rid] = dict(
                        name=f"Bolt of {m['name'].replace(' Cloth', '')}",
                        skill_required=sk, skill_range=spread(sk), source="trainer",
                        inputs={mid: 3},
                        output=dict(kind="material", material_id=bolt))

        # ---- gear on every material of the family that nothing uses yet
        used = {i for r in recipes.values() if isinstance(r, dict)
                for i in (r.get("inputs") or {})}
        fam = cfg["family"]
        pool = sorted(((m.get("skill_range") or [9999])[0], mid)
                      for mid, m in mats.items()
                      if m["material_type"] == fam
                      and (m.get("skill_range") or [9999])[0] <= CEILING)
        # only the upper half matters: that is where the professions stop
        top = [(s, mid) for s, mid in pool if s >= 150]

        made, si, wi, pi = {}, 0, 0, 0
        for skill, mid in top:
            base = skill
            short = mid.split("_", 1)[1]
            label = mats[mid]["name"]
            for suffix in (" Cloth", " Leather", " Plank", "Bolt of "):
                label = label.replace(suffix, "")
            label = label.strip()
            pair = PAIRS[cfg["pairs"][pi % len(cfg["pairs"])]]; pi += 1
            step = 0

            for k in range(cfg["per_mat"]):
                slot = cfg["slots"][si % len(cfg["slots"])]; si += 1
                sk = min(CEILING, base + step); step += 5
                at = cfg["armor_types"][k % len(cfg["armor_types"])]
                rid = f"p300_{prof[:2]}_{short}_{slot}"
                if rid in recipes:
                    continue
                made[rid] = dict(
                    name=f"{label} {cfg['piece'][slot]}",
                    skill_required=sk, skill_range=spread(sk), source="trainer",
                    inputs={mid: COST[slot]},
                    output=dict(kind="armor", slot=slot, armor_type=at,
                                stat_template=pair[k % 2], item_level=item_level(sk),
                                rarity=rarity(sk), material_tier=short))

            for k in range(cfg.get("per_weapon", 0)):
                slot, wt = cfg["weapons"][wi % len(cfg["weapons"])]; wi += 1
                sk = min(CEILING, base + step); step += 5
                role = PAIRS[WEAPON_ROLE[wt]]
                rid = f"p300_{prof[:2]}_{short}_{wt}"
                if rid in recipes:
                    continue
                made[rid] = dict(
                    name=f"{label} {cfg['wname'][wt]}",
                    skill_required=sk, skill_range=spread(sk), source="trainer",
                    inputs={mid: COST[slot]},
                    output=dict(kind="weapon", slot=slot, weapon_type=wt,
                                stat_template=role[k % 2], item_level=item_level(sk),
                                rarity=rarity(sk), material_tier=short))

        before = max((r.get("skill_required", 0) for r in recipes.values()
                      if isinstance(r, dict) and (r.get("output") or {}).get("kind")
                      in ("armor", "weapon")), default=0)
        after = max([before] + [r["skill_required"] for r in made.values()])
        summary.append((prof, before, after, len(recipes), len(made), made_bolts, made))
        if args.apply:
            recipes.update(made)

    print(f"  epic from skill {EPIC_FROM}, item_level = skill*60/300+1 "
          f"(boss drops cap at rare, 57)\n")
    print(f"  {'profession':16}{'gear reach':>12}{'recipes':>12}{'new':>6}{'bolts':>7}")
    for prof, b, a, n, k, bolts, _ in summary:
        print(f"  {prof:16}{f'{b} -> {a}':>12}{f'{n} -> {n + k + bolts}':>12}{k:>6}{bolts:>7}")

    for prof, b, a, n, k, bolts, made in summary:
        if not made:
            continue
        r = collections.Counter(x["output"]["rarity"] for x in made.values())
        t = collections.Counter(x["output"]["stat_template"] for x in made.values())
        lv = [x["output"]["item_level"] for x in made.values()]
        print(f"\n  {prof}: {dict(r)}  item level {min(lv)}-{max(lv)}")
        print(f"    roles {dict(t)}")

    if args.apply:
        for rel, doc in docs.items():
            (ROOT / rel).write_text(json.dumps(doc, indent=2) + "\n")
        print(f"\n  wrote {', '.join(sorted(docs))}")
    else:
        print("\n  dry run - pass --apply to write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
