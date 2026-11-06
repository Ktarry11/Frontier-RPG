#!/usr/bin/env python3
"""Shared machinery for rebuilding a Classic tree from the real 3.3.5a data.

Imported by the tools/build_<class>_<spec>.py scripts. It exists so each
builder is its per-node DESIGN and SOURCE NOTES rather than 200 lines of
repeated plumbing and assertions - and so every tree is checked by the same
assertions instead of whichever ones its author remembered.

WHAT A BUILDER STILL OWNS: the module docstring recording source, role and
what is not buildable; one node() call per talent carrying its WotLK
wording and every departure from it. That is the part worth writing by
hand, and the part a future reader needs.

WHAT THIS OWNS: the tree skeleton, hex layout, and the checks below.

THE CHECKS, each one a mistake this project has actually shipped:

  - a duplicate talent_id
  - a connected_to naming a node that is not in the tree (eight unlock
    nodes were silently dropped this way once, stranding abilities)
  - an unlock_ability naming an ability that does not exist
  - an ability-scoped key whose ability_id half is typo'd: the suffix is
    real, the key is well formed, audit_talents passes, and the talent
    never fires. Nothing else in the project can see it.
  - an ability_filter naming an ability that does not exist, which makes a
    proc that can never match
  - low_health_threshold_pct authored at all: it is UNSCALED and SUMS
    across talents, and is SHARED between the target-side conditional
    (low_health_damage_pct, default 0.35) and the actor-side one
    (low_health_damage_reduction_pct, default 0.5). Authoring it for one
    corrupts the other, and both defaults are already correct.
  - a node that does nothing: no proc, no effects, no unlock
  - fewer than 56 points, which is what a level-60 pure spec must be able
    to spend in ONE tree

Unit conventions are NOT checked here - they are not inferable from a key
name, and tools/audit_talents.py is the only reliable check. Run it.
"""

import glob
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from probe_talent_key import split_ability_key  # noqa: E402

#: Frontier trees are tier 0-6 - SEVEN tiers - with cumulative point gates.
TIER_REQUIREMENTS = {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25,
                     "6": 30}

#: A level-60 character has 56 talent points and a pure spec spends them
#: all in one tree, so a tree below this is unfinishable.
MIN_POINTS = 56

#: Conditional keys - a node carrying one is not a flat scalar, it is a
#: situational mechanic, and the classification report counts it as such.
CONDITIONAL_KEYS = {
    "low_health_damage_pct", "low_health_damage_reduction_pct",
    "low_health_healing_pct", "execute_threshold_pct",
    "high_health_damage_pct",
}

#: Authoring this is always wrong. See the module docstring.
FORBIDDEN_KEYS = {"low_health_threshold_pct"}

_ABILITY_IDS = None


def ability_ids():
    global _ABILITY_IDS
    if _ABILITY_IDS is None:
        _ABILITY_IDS = set()
        for path in glob.glob(str(ROOT / "data/abilities/*.json")):
            for a in json.loads(Path(path).read_text()).get("abilities", []):
                _ABILITY_IDS.add(a["ability_id"])
    return _ABILITY_IDS


class Tree:
    """One talent tree under construction."""

    def __init__(self, tree_id, spec_name, description):
        self.tree_id = tree_id
        self.prefix = tree_id + "_"
        self.data = {
            "spec_name": spec_name,
            "tree_id": tree_id,
            "description": description,
            "tier_requirements": dict(TIER_REQUIREMENTS),
            "nodes": [],
        }

    def node(self, talent_id, name, description, tier, hex_x, max_points,
             effects=None, proc=None, connected_to=None,
             node_type="passive", source="", require_form=None,
             raw_id=False, raw_links=(), icon_id=None):
        """Add one node.

        raw_id=True uses `talent_id` VERBATIM instead of prefixing it with
        the tree id. That exists for PRESERVED nodes whose ids are already
        in the data under a different prefix - Shaman Enhancement's homebrew
        tank branch is `shaman_tank_*`, not `shaman_enhancement_*`, and
        renaming those ids would silently break any save, recruit build or
        tooling that refers to them. raw_links is the same escape hatch for
        connected_to.
        """
        n = {
            "talent_id": talent_id if raw_id else self.prefix + talent_id,
            "name": name,
            "description": description,
            "node_type": node_type,
            "tier": tier,
            "max_points": max_points,
            "cost_per_point": 1,
            "hex_x": hex_x,
            # The project's layout convention: tier 0 sits at -6 and each
            # tier is two rows below the last.
            "hex_y": tier * 2 - 6,
            "effects": effects or {},
            "_source": source,
            "connected_to": ([self.prefix + c for c in (connected_to or [])]
                             + list(raw_links)),
        }
        if proc:
            n["proc"] = proc
        if require_form:
            n["require_form"] = require_form
        # Preserved homebrew branches ship their own art; dropping the
        # icon_id would leave those nodes blank in the talent screen.
        if icon_id:
            n["icon_id"] = icon_id
        self.data["nodes"].append(n)
        return n

    # ------------------------------------------------------------- checks
    def classify(self, n):
        if n.get("proc"):
            return "proc"
        eff = n.get("effects") or {}
        if "unlock_ability" in eff:
            return "unlock"
        if not eff:
            return "EMPTY - does nothing"
        if any(k in CONDITIONAL_KEYS for k in eff):
            return "conditional"
        scoped = [bool(split_ability_key(k)) for k in eff]
        if scoped and all(scoped):
            return "ability-scoped"
        if any(scoped):
            return "mixed"
        return "flat stat"

    def check(self):
        nodes = self.data["nodes"]
        ids = [n["talent_id"] for n in nodes]
        dupes = [k for k, v in Counter(ids).items() if v > 1]
        assert not dupes, f"duplicate talent_id: {dupes}"

        known = set(ids)
        real = ability_ids()
        problems = []

        for n in nodes:
            tid = n["talent_id"]
            for c in n["connected_to"]:
                if c not in known:
                    problems.append(f"{tid}: connects to unknown node {c}")

            eff = n.get("effects") or {}
            for key, val in eff.items():
                if key in FORBIDDEN_KEYS:
                    problems.append(
                        f"{tid}: authors {key}, which SUMS across talents "
                        f"and is shared between the target-side and "
                        f"actor-side conditionals - use the defaults")
                if key == "unlock_ability":
                    if val not in real:
                        problems.append(
                            f"{tid}: unlocks '{val}', which is not an "
                            f"ability")
                    continue
                split = split_ability_key(key)
                if split and split[0] not in real:
                    problems.append(
                        f"{tid}: key {key} names ability '{split[0]}', "
                        f"which does not exist - silent dead data")

            proc = n.get("proc") or {}
            for aid in proc.get("ability_filter") or []:
                if aid not in real:
                    problems.append(
                        f"{tid}: ability_filter names '{aid}', which does "
                        f"not exist - this proc can never match")
            spec = proc.get("apply_effect")
            for s in (spec if isinstance(spec, list) else [spec] if spec
                      else []):
                if not s.get("effect_type"):
                    problems.append(
                        f"{tid}: apply_effect has no effect_type - "
                        f"StatusEffect REQUIRES it, TypeError at proc time")

            if self.classify(n) == "EMPTY - does nothing":
                problems.append(f"{tid}: no proc, no effects, no unlock")

        points = sum(n["max_points"] for n in nodes)
        if points < MIN_POINTS:
            problems.append(
                f"only {points} points - a level-60 pure spec must be able "
                f"to spend {MIN_POINTS} in ONE tree")

        if problems:
            print(f"\n  {len(problems)} PROBLEM(S) IN {self.tree_id}\n")
            for p in problems:
                print(f"    {p}")
            raise SystemExit(1)
        return points

    def write(self, was=None):
        points = self.check()
        out = ROOT / f"data/talents/{self.tree_id}.json"
        out.write_text(json.dumps(self.data, indent=2) + "\n")
        nodes = self.data["nodes"]
        print(f"  wrote {out.relative_to(ROOT)}")
        print(f"  {len(nodes)} nodes, {points} points\n")
        counts = Counter(self.classify(n) for n in nodes)
        for kind, n in sorted(counts.items(), key=lambda kv: -kv[1]):
            print(f"      {kind:22s} {n}")
        if was:
            print(f"\n  was: {was}")
        return 0
