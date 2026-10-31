#!/usr/bin/env python3
"""Can a player actually gather, skin and loot cloth in every zone?

    PYTHONPATH=. python3 tools/audit_zone_harvestables.py [--zone <name>]

Kyle, 29 Oct 2026: "we also need to ensure harvestables are in the zone, cloth from humanoids,
skin from beasts etc. herbs, ore, trees."

Those are two different systems and they fail in two different ways.

NODES (herbs, ore, trees, crystals) are declared per zone in data/gathering/node_pools.json. A zone
with no entry has no nodes at all, and a zone whose table happens to hold only herbs is a zone where
a miner finds nothing. Both are silent - you walk the whole zone and conclude the game is like that.

CLOTH AND LEATHER are not declared anywhere. They are inferred from the creature's NAME at kill
time: entities/cloth_drops.roll_cloth pays out only for family "humanoid", and
entities/skinning_drops.roll_leather only for family "beast", and the family comes from
vendor_trash.classify(name) matching keywords. So a creature can be mis-typed by its own name and
yield nothing, with no error and nothing to see but an empty corpse.

That is not hypothetical. Sporelit Bat, a level-31 beast in Rotvine Hollow, classified as `plant`
because "spore" appears in its name, and plants cannot be skinned. It had presumably never dropped
leather. Found by running this check, not by reading the data.

WHAT IT CHECKS, per zone:
  1. The zone has a node pool at all (towns, caves and arenas are exempt - an ore vein in an inn is
     a mistake, not a feature).
  2. The pool covers every gathering profession the zone's tier should support, so no profession is
     locked out of a whole zone.
  3. Node material tiers are plausible for the creature levels there - a level-40 zone handing out
     tier-early copper is a zone nobody gathers in twice.
  4. The zone has at least one skinnable beast and one cloth-dropping humanoid, so neither
     profession is dead there.
  5. THE IMPORTANT ONE: a creature whose NAME ENDS IN AN ANIMAL NOUN, whose STAT TEMPLATE is a
     beast or vermin block, and which nonetheless classifies as `plant` or `elemental`. That is the
     Sporelit Bat failure and it is invisible by every other route.

     All three conditions are needed, and the first version of this check had only the template one.
     It reported 36 creatures, every one of them correct: harpies and worgen are humanoid and drop
     cloth instead of leather, crabs and lurkers are aquatic, treants are plants, and a Zombie Bear
     is undead - those families legitimately yield neither cloth nor leather, by design. Narrowing
     to an animal head noun still flagged twelve, and those are deliberate too: a felhound is a
     demon, a quilboar is a humanoid, a crab is aquatic. Only plant and elemental are indefensible
     for something whose name says it is an animal and whose stat block agrees. A check that cries
     wolf 36 times to find one real fault is a check nobody runs twice.

Exits non-zero on a finding.
"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from entities.vendor_trash import _ANIMAL_HEAD, classify, _template_of  # noqa: E402

#: Region CONTAINERS, not zones. encounters.json is keyed by zone except for these, which hold the
#: creatures a builder filed against a whole region - "Eastern Kingdoms - Stranglethorn" carries the
#: five Gurbashi Arena bosses, put there by build_gurbashi_content.py. Nobody walks them, so every
#: check below is meaningless for them.
REGION_CONTAINERS = {"eastern_kingdoms_-_stranglethorn"}

#: Underground. No trees below ground, so woodcutting is correctly absent rather than missing - the
#: Crystalline Underdark is a cavern and has herbalism and mining as it should.
NO_WOODCUTTING_EXPECTED = {"crystalline_underdark", "frostward_descent", "deep_bloom", "weeping_ice"}

#: Zones that should have no gathering nodes. A town is paved, a boss arena is sand, and a dungeon
#: is somewhere you fight through rather than prospect.
NO_NODES_EXPECTED = {
    "orgrimmar", "razor_hill", "crossroads", "camp_taurajo", "ratchet", "splintertree_post",
    "astranaar", "zoram_strand", "freewind_post", "undercity", "brill", "sepulcher",
    "tarren_mill", "kaels_bastion", "gromgol", "booty_bay", "deathknell", "valley_of_trials",
    "gurbashi_arena", "zeppelin_tower", "undercity_zeppelin_tower", "gromgol_zeppelin_tower",
    # dungeons
    "frostward_descent", "drowning_floor", "deep_bloom",
}

#: Stat templates that mean somebody built this thing as an animal. NOT a family declaration - see
#: the _ANIMAL_HEAD note in vendor_trash - but a strong signal that it was meant to be skinnable.
BEASTY_TEMPLATES = ("beast_basic", "beast_fast", "beast_large", "vermin_sneaky", "vermin_swarm")

GATHERING_PROFESSIONS = {"herbalism", "mining", "woodcutting"}


def zkey(name):
    from world.zone_keys import zone_key
    return zone_key(name)


def material_professions():
    data = json.loads((ROOT / "data/gathering/materials.json").read_text())
    rows = data.get("materials", data)
    out = {}
    if isinstance(rows, list):
        for r in rows:
            out[r.get("material_id")] = (r.get("profession"), r.get("tier"))
    else:
        for k, v in rows.items():
            out[k] = (v.get("profession"), v.get("tier"))
    return out


def encounter_creatures():
    """zone display name -> {creature name: weight}, flattened over open_zone/subzones/caves."""
    data = json.loads((ROOT / "data/creatures/encounters.json").read_text())
    zones = data.get("zones", data)
    out = {}
    for zname, body in zones.items():
        names = {}

        def grab(node):
            if isinstance(node, dict):
                if isinstance(node.get("creatures"), dict):
                    names.update(node["creatures"])
                for v in node.values():
                    grab(v)

        grab(body)
        out[zname] = names
    return out


def main():
    only = None
    if "--zone" in sys.argv:
        only = zkey(sys.argv[sys.argv.index("--zone") + 1])

    pools_doc = json.loads((ROOT / "data/gathering/node_pools.json").read_text())
    pools = {zkey(k): v for k, v in pools_doc.get("zones", pools_doc).items()}
    prof = material_professions()
    enc = encounter_creatures()

    findings = []

    # ---- 5. mis-typed animals, game-wide. Run first: it is the one that hides. ----------------
    creature_doc = json.loads((ROOT / "data/creatures/creatures.json").read_text())
    crows = creature_doc.get("creatures", creature_doc)
    cnames = list(crows) if isinstance(crows, dict) else [r.get("name") for r in crows]
    for cname in cnames:
        if not cname:
            continue
        template = _template_of(cname)
        if template not in BEASTY_TEMPLATES:
            continue
        if not _ANIMAL_HEAD.search(cname):
            continue
        family, _coin = classify(cname)
        if family in ("plant", "elemental"):
            findings.append(
                f"creature {cname!r} is named as an animal and built on {template}, but classifies "
                f"as {family!r}, so it can never be skinned - a keyword in its name is beating its "
                f"head noun in vendor_trash._FAMILY_RULES"
            )

    # ---- per-zone ------------------------------------------------------------------------------
    for zname, creatures in sorted(enc.items()):
        key = zkey(zname)
        if only and key != only:
            continue
        if not creatures:
            continue
        if key in REGION_CONTAINERS:
            continue

        fams = Counter(classify(c)[0] for c in creatures)
        has_beast = fams.get("beast", 0) + fams.get("insect", 0) > 0
        has_humanoid = fams.get("humanoid", 0) > 0

        pool = pools.get(key)
        exempt = key in NO_NODES_EXPECTED

        bits = [f"beasts {fams.get('beast', 0)}", f"humanoids {fams.get('humanoid', 0)}"]
        if pool:
            table = pool.get("table", [])
            rows = table if isinstance(table, list) else list(table)
            profs = Counter()
            for r in rows:
                mid = r.get("material_id") if isinstance(r, dict) else r
                profs[prof.get(mid, (None, None))[0]] += 1
            bits.append("nodes " + "/".join(f"{p}:{n}" for p, n in sorted(profs.items()) if p))
            required = set(GATHERING_PROFESSIONS)
            if key in NO_WOODCUTTING_EXPECTED:
                required.discard("woodcutting")
            missing = required - set(profs)
            if missing:
                findings.append(
                    f"{zname}: node pool has no {', '.join(sorted(missing))} - that profession "
                    f"finds nothing in the whole zone"
                )
        elif not exempt:
            findings.append(f"{zname}: no gathering node pool, so no herbs, ore or trees anywhere")
            bits.append("nodes NONE")
        else:
            bits.append("nodes n/a")

        if not has_beast and not exempt:
            findings.append(f"{zname}: no skinnable creature, so Skinning is dead here")
        if not has_humanoid and not exempt:
            findings.append(f"{zname}: no cloth-dropping humanoid, so Tailoring has no source here")

        print(f"  {zname:38} {'  '.join(bits)}")

    print()
    if findings:
        print(f"{len(findings)} finding(s):")
        for f in findings:
            print(f"  {f}")
        return 1
    print("every zone has nodes, a skinnable beast and a cloth source; no mis-typed animals")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
