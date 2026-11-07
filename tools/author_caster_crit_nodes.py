#!/usr/bin/env python3
"""Author the 20 missing caster spell-crit-damage talents.

    PYTHONPATH=. python3 tools/author_caster_crit_nodes.py [--apply]

Kyle, 6 Nov: "Lets ensure that each caster can get a talent that does
that.. It would be a 5 point talent."

tools/add_caster_crit_damage_capstone.py standardised the 17 caster trees
that already had a crit-damage node. These are the 20 that had nothing, so
there is no node to upgrade and one has to be placed.

GEOMETRY IS DERIVED, NOT GUESSED. Every tree lays its tiers out on a fixed
row: hex_y == -6 + 2 * tier, verified across all 97 files. The new node
goes on tier 4's row at the first free hex_x beside the existing tier-4
nodes, and takes `connected_to` pointing at the nearest tier-3 node by
hex_x so the tree draws an edge rather than leaving it floating.

Tier 4 because that is where priest_shadow's Shadow Power sits - the
WoW-accurate model this whole standardisation is copying - and because a
+100% crit-damage talent is a mid-late investment, not an opener.

CONNECTIONS ARE COSMETIC HERE. ui/screens/talent_tree_screen.py is the
only reader of connected_to and it draws lines with it; spending is gated
by tier_requirements alone (entities/talent_manager.py). So a wrong edge
is an ugly line, not a broken tree - but it is still worth getting right.

ADDING POINTS CANNOT BREAK REACHABILITY. qa_talent_tiers_reachable fails a
tree when the points available BELOW a tier are fewer than that tier's
gate. Every tree here gains 5 points at tier 4, which can only help tiers
5 and 6 and cannot hurt tiers 0-4. Checked after applying regardless.

NAMES ARE HAND-PICKED, one per tree, in that tree's own voice. A generated
name - "Spell Crit Damage" on twenty trees - is exactly the lame shit Kyle
asked not to get. priest_holy's is Holy Power, mirroring priest_shadow's
Shadow Power, because that pairing already exists in WoW and the tree was
missing its half of it.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TALENTS = ROOT / "data/talents"

KEY = "crit_damage_spell"
RANKS = 5
PER_RANK = 0.2
TIER = 4

#: tree -> the talent's name in that tree's voice.
NAMES = {
    "bloodmage_fleshweaver": "Hemorrhagic Shock",
    "chronomancer_time": "Compounded Moment",
    "cultist_heretic": "Blasphemy",
    "druid_restoration": "Wild Abundance",
    "necromancer_animation": "Grave Harvest",
    # Sanctified Light and Tidal Force already exist in these two trees
    # granting crit CHANCE, which is a different talent. The collision
    # check caught it; these are the replacements.
    "paladin_holy": "Light's Fury",
    "priest_discipline": "Exalted Grace",
    "priest_holy": "Holy Power",
    "primalist_grovekeeper": "Verdant Fury",
    "pyromancer_draconic": "Draconic Fury",
    "pyromancer_flameweaving": "Conflagration",
    "runemaster_riftblade": "Rift Resonance",
    "shaman_restoration": "Surging Tides",
    "starcaller_moon_priest": "Lunar Fury",
    "stormbringer_wind": "Gale Force",
    "sun_cleric_blessings": "Radiant Zeal",
    "venomancer_vizier": "Virulent Insight",
    "warlock_affliction": "Withering Agony",
    "warlock_demonology": "Demonic Fury",
    "witch_doctor_brewing": "Potent Brew",
}


def row_for(tier):
    return -6 + 2 * tier


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    placed, skipped = [], []
    for tree, name in sorted(NAMES.items()):
        path = TALENTS / f"{tree}.json"
        doc = json.loads(path.read_text())
        nodes = doc.get("nodes", [])

        if any(isinstance(n, dict) and n.get("name") == name for n in nodes):
            skipped.append((tree, name, "name already used in this tree"))
            continue
        if any(isinstance(n, dict)
               and any("crit_damage" in k for k in (n.get("effects") or {}))
               for n in nodes):
            skipped.append((tree, name, "tree already has a crit-damage node"))
            continue

        row = row_for(TIER)
        same_row = [n for n in nodes if isinstance(n, dict) and n.get("tier") == TIER]
        used_x = {n.get("hex_x") for n in same_row}
        # First free slot outward from the existing block, so the node lands
        # beside its tier rather than adrift across the canvas.
        hex_x = (max(used_x) + 1) if used_x else 0
        while hex_x in used_x:
            hex_x += 1

        above = [n for n in nodes if isinstance(n, dict) and n.get("tier") == TIER - 1]
        parent = min(above, key=lambda n: abs((n.get("hex_x") or 0) - hex_x),
                     default=None)

        node = {
            "talent_id": f"{tree}_{name.lower().replace(' ', '_').replace(chr(39), '')}",
            "name": name,
            "description": (f"Increases the critical strike damage of your "
                            f"spells by {PER_RANK * 100:g}% per rank."),
            "node_type": "passive",
            "tier": TIER,
            "max_points": RANKS,
            "cost_per_point": 1,
            "hex_x": hex_x,
            "hex_y": row,
            "effects": {KEY: PER_RANK},
            "connected_to": [parent["talent_id"]] if parent else [],
            "_source": (
                "Authored 6 Nov. Kyle: 'all caster classes should have a 5 "
                "point talent that increases their spell crit damage by "
                "100%.' Mirrors priest_shadow's Shadow Power and "
                "shaman_elemental's Elemental Fury, both of which are "
                "WoW-accurate at 5 x 20%. Placed on tier 4 beside the "
                "existing tier-4 block; connected_to is cosmetic (it draws "
                "the edge), spending is gated by tier_requirements."),
        }
        nodes.append(node)
        placed.append((tree, name, hex_x,
                       parent["name"] if parent else "(no tier-3 node)"))
        if args.apply:
            path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")

    print(f"placed {len(placed)} nodes at tier {TIER} "
          f"(hex_y {row_for(TIER)}), {RANKS} x {PER_RANK * 100:g}% = "
          f"{RANKS * PER_RANK * 100:g}%\n")
    print(f"{'tree':28}{'talent':22}{'hex_x':>6}  connects to")
    for tree, name, hex_x, parent in placed:
        print(f"  {tree:26}{name:22}{hex_x:>6}  {parent}")
    if skipped:
        print(f"\nskipped {len(skipped)}:")
        for tree, name, why in skipped:
            print(f"  {tree:26}{name:22}{why}")
    if not args.apply:
        print("\n(report only; pass --apply to write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
