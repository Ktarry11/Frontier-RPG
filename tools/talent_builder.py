"""
talent_builder.py - authoring helper for talent tree JSON.

WHY THIS EXISTS
---------------
Hand-writing ~570 talent nodes as raw JSON means hand-placing ~570 hex
coordinates and ~570 connection lists. That is where data-entry errors live,
and it is why the original warrior_arms.json ended up visually cramped.

Instead, trees are authored here as compact tuples:

    (suffix, name, tier, column, max_points, effects, description)

...and this module derives hex_x / hex_y / connected_to mechanically:

  * hex_x comes from `column`, an index in COLUMN_X (4 columns per tier).
    Columns are spaced 2 hex units apart (~90px at the default hex_spacing
    of 45), versus the 1 unit (~45px, with a 30px hex radius) the original
    tree used - that is the actual fix for the "talents are squished"
    complaint from the Phase 4.5 handoff.
  * hex_y comes from `tier`, spaced 2 hex units apart (~78px) and centred
    so tier 0 sits above the middle of the screen and the deepest tier sits
    below it.
  * connected_to auto-links each node to the nearest node in the tier above
    it, producing the staggered branching structure without hand-authoring
    hundreds of edge lists.

This is only an authoring tool. It emits plain JSON in the exact schema
TalentManager._parse_tree_data() already reads - the runtime does not import
this file, and the generated JSON is fully hand-editable afterwards.

EFFECT KEY REFERENCE (consumed by entities/character.py + combat/abilities.py)
-----------------------------------------------------------------------------
Stat keys (folded into the same bonus pool as gear):
    strength, stamina, intellect, spirit, agility
    attack_power, spell_power, healing_power
    crit_chance_physical, crit_chance_spell
    dodge, parry, block, haste, armor, magic_resistance, hit_rating
    max_health_pct, max_mana_pct          (percentages, 0.05 = +5%)

Global combat multipliers (0.02 = +2%):
    all_damage, physical_damage, spell_damage, healing_done

Per-ability keys (<id> must be a real Ability.ability_id):
    ability_<id>_damage      multiplier
    ability_<id>_cost        flat resource cost reduction
    ability_<id>_cooldown    flat cooldown turn reduction

All numeric values are PER RANK - a max_points=5 talent with 0.02 totals
0.10 at 5/5. (This is what TalentNode.get_effective_effects() now does; it
previously divided by max_points, making maxed talents worth one rank.)
"""
import json
from pathlib import Path

# Four columns per tier. Values are hex units; at the default hex_spacing of
# 45px this puts columns ~90px apart, comfortably clear of the 30px radius.
COLUMN_X = [-3, -1, 1, 3]

# Vertical spacing between tiers, in hex units.
TIER_STEP = 2

# Tiers 0-6 centred vertically around the screen midpoint.
TIER_Y_OFFSET = -6

# Standard gating for every tree: 5 points per tier unlocked.
TIER_REQUIREMENTS = {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30}


def _hex_pos(tier, column):
    """Map (tier, column) to hex grid coordinates."""
    return COLUMN_X[column], tier * TIER_STEP + TIER_Y_OFFSET


def build_tree(tree_id, spec_name, description, talents):
    """Turn compact talent tuples into a full talent-tree dict.

    talents: iterable of
        (suffix, name, tier, column, max_points, effects, description)
    suffix is appended to tree_id to form talent_id, keeping ids unique
    across trees (warrior_arms_cruelty vs warrior_fury_cruelty).
    """
    nodes = []
    by_tier = {}

    for suffix, name, tier, column, max_points, effects, desc in talents:
        hex_x, hex_y = _hex_pos(tier, column)
        node = {
            "talent_id": f"{tree_id}_{suffix}",
            "name": name,
            "description": desc,
            "node_type": "passive",
            "tier": tier,
            "max_points": max_points,
            "cost_per_point": 1,
            "hex_x": hex_x,
            "hex_y": hex_y,
            "effects": effects,
            "connected_to": [],
        }
        nodes.append(node)
        by_tier.setdefault(tier, []).append((column, node))

    # Auto-connect: each node links to the closest-column node one tier up.
    for tier in sorted(by_tier):
        if tier == 0:
            continue
        parents = by_tier.get(tier - 1)
        if not parents:
            continue
        for column, node in by_tier[tier]:
            nearest = min(parents, key=lambda p: abs(p[0] - column))
            parent_node = nearest[1]
            node["connected_to"].append(parent_node["talent_id"])
            parent_node["connected_to"].append(node["talent_id"])

    return {
        "spec_name": spec_name,
        "tree_id": tree_id,
        "description": description,
        "tier_requirements": dict(TIER_REQUIREMENTS),
        "nodes": nodes,
    }


def write_tree(out_dir, tree_id, spec_name, description, talents):
    """Build a tree and write it to <out_dir>/<tree_id>.json."""
    tree = build_tree(tree_id, spec_name, description, talents)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{tree_id}.json"
    with open(path, "w") as f:
        json.dump(tree, f, indent=2)
    return path, len(tree["nodes"])
