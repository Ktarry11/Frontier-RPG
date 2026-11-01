#!/usr/bin/env python3
"""Content invariants that the data files must satisfy.

    python3 tools/validate_content.py

WHY THIS EXISTS
---------------
Over one session (2026-10-26) the same shape of bug turned up five separate
times, each found by hand, each only after something looked wrong on screen:

  * 17 blacksmithing recipes used weapon_type "sword"/"axe"/"mace" when the
    real types are sword_1h/sword_2h/... - generate_weapon indexes the type
    table with no guard, so every one raised KeyError. Blacksmithing, the
    weapon profession, could not craft a single melee weapon.
  * 27 recipes used slot "shoulders" (plural). The slot is "shoulder". Same
    uncaught KeyError; those had never been craftable.
  * 33 recipes used slot "two_hand", which is a weapon HAND category and not
    a slot at all. They crafted fine, then equip() silently put them nowhere.
  * 5 weapon types had no entry in WEAPON_NAME_NOUNS, so every bow, crossbow,
    gun, polearm and thrown weapon in the game was named "Weapon of Agility".
  * 2 crafted recipes were named with a procedural rarity PREFIX - one of them
    "Tattered Spirit Gloves", where Tattered is the grey-tier prefix on an
    uncommon item.

Every one of them was invisible to the checks being run at the time, which
verified that recipe INPUTS resolved to real materials but never that an
OUTPUT was something the engine could actually build and equip. These are
those missing checks, written down so they run instead of being remembered.

Exit code is non-zero when anything fails, so this can gate a commit.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

GEAR_KINDS = ("armor", "weapon")

#: Every recipe file, and the key it nests recipes under (None = top level).
RECIPE_SOURCES = {
    "blacksmithing": ("data/blacksmithing/recipes.json", None),
    "leatherworking": ("data/leatherworking/recipes.json", None),
    "alchemy": ("data/crafting/recipes.json", "alchemy"),
    "tailoring": ("data/crafting/recipes.json", "tailoring"),
    "woodworking": ("data/crafting/recipes.json", "woodworking"),
    "woodcutting": ("data/crafting/recipes.json", "woodcutting"),
    "engineering": ("data/crafting/recipes.json", "engineering"),
}


def load(rel):
    with open(REPO / rel) as f:
        return json.load(f)


def all_recipes():
    out = {}
    for prof, (path, nest) in RECIPE_SOURCES.items():
        doc = load(path)
        out[prof] = doc["recipes"] if nest is None else doc["professions"][nest]["recipes"]
    return out


def main():
    import pygame
    pygame.init()
    pygame.display.set_mode((64, 64))

    from entities.equipment import Equipment, PAIRED_SLOTS
    from entities.loot_generator import (LootGenerator, ARMOR_NAME_PREFIXES,
                                         WEAPON_NAME_NOUNS, ARMOR_NAME_NOUNS)
    from world.upgrade_manager import MATERIAL_KITS
    from world.attachment_manager import ATTACHMENTS

    gen = LootGenerator()
    recipes = all_recipes()
    materials = load("data/gathering/materials.json")["materials"]
    weapon_types = set(load("data/items/weapon_types.json")["weapon_types"])

    equip_slots = set(Equipment().to_dict()) | set(PAIRED_SLOTS)
    gen_slots = set(gen.slots["slots"]) | set(PAIRED_SLOTS)
    rarity_prefixes = {p for v in ARMOR_NAME_PREFIXES.values() for p in v}
    #: The concrete halves of every paired slot - ring1/ring2, trinket1/2,
    #: bag1-4. Real slots, but never what an ITEM should carry.
    concrete_paired = {s for pair in PAIRED_SLOTS.values() for s in pair}

    failures = []

    def fail(check, detail):
        failures.append((check, detail))

    # ── 1. every output slot must be generatable AND equippable ──────────
    for prof, recs in recipes.items():
        for rid, r in recs.items():
            out = r.get("output", {})
            if out.get("kind") not in GEAR_KINDS:
                continue
            slot = out.get("slot")
            if slot not in gen_slots:
                fail("slot-not-generatable", f"{prof}/{rid}: slot {slot!r}")
            elif slot not in equip_slots:
                fail("slot-not-equippable", f"{prof}/{rid}: slot {slot!r}")
            elif slot in concrete_paired:
                # The sneakiest version of this bug, and the one the two
                # checks above CANNOT catch: "trinket1" is a real equipment
                # slot and is generatable, so it looks fine - but an item must
                # carry the GENERIC slot ("trinket") so Equipment._resolve_slot
                # can place it in whichever of the pair is open. Hardcoded to
                # trinket1, it can never fill an empty trinket2, which is the
                # original "can only equip one ring" bug returning by the back
                # door. It shipped once already in the engineering trinkets.
                fail("slot-hardcoded-pair",
                     f"{prof}/{rid}: slot {slot!r} should be {slot[:-1]!r} (generic)")

    # ── 2. every weapon_type must be real and have a display noun ────────
    for prof, recs in recipes.items():
        for rid, r in recs.items():
            out = r.get("output", {})
            if out.get("kind") != "weapon":
                continue
            wt = out.get("weapon_type")
            if wt not in weapon_types:
                fail("weapon-type-unknown", f"{prof}/{rid}: weapon_type {wt!r}")
            elif wt not in WEAPON_NAME_NOUNS:
                fail("weapon-type-unnamed", f"{prof}/{rid}: {wt!r} renders as 'Weapon'")
    for wt in sorted(weapon_types - set(WEAPON_NAME_NOUNS)):
        fail("weapon-type-unnamed", f"(no recipe) {wt!r} has no entry in WEAPON_NAME_NOUNS")

    # ── 3. every recipe input must resolve to a real or craftable material ─
    produced = set()
    for recs in recipes.values():
        for r in recs.values():
            o = r.get("output", {})
            if o.get("kind") == "material" and o.get("material_id"):
                produced.add(o["material_id"])
    smelt = load("data/gathering/smelting_recipes.json")
    for k, r in smelt.get("recipes", smelt).items():
        if isinstance(r, dict):
            o = r.get("output")
            produced.add(o if isinstance(o, str) else (o or {}).get("material_id", ""))
    known = set(materials) | produced
    for prof, recs in recipes.items():
        for rid, r in recs.items():
            for inp in r.get("inputs", {}):
                if inp not in known:
                    fail("input-unresolved", f"{prof}/{rid}: input {inp!r}")

    # ── 4. crafted/boss names must not borrow a procedural rarity prefix ──
    # A hand-authored item is supposed to read as hand-made. Borrowing a
    # prefix makes it look like a random drop, and borrowing the WRONG tier's
    # prefix actively lies about the item's quality.
    for prof, recs in recipes.items():
        for rid, r in recs.items():
            if r.get("output", {}).get("kind") not in GEAR_KINDS:
                continue
            first = (r.get("name") or " ").split()[0]
            if first in rarity_prefixes:
                fail("name-uses-loot-prefix", f"{prof}/{rid}: {r['name']!r} starts with {first!r}")
    from entities.boss_loot import _load_boss_loot_tables
    for boss, defs in _load_boss_loot_tables().items():
        for d in defs:
            first = (d.get("name") or " ").split()[0]
            if first in rarity_prefixes:
                fail("name-uses-loot-prefix", f"boss {boss}: {d['name']!r}")

    # ── 5. crafted gear must have an upgrade kit that matches its tier ────
    covered = set(MATERIAL_KITS.values())
    for prof, recs in recipes.items():
        for rid, r in recs.items():
            out = r.get("output", {})
            if out.get("kind") not in GEAR_KINDS or r.get("skill_required", 0) > 225:
                continue
            mt = out.get("material_tier")
            if not mt:
                fail("gear-untagged", f"{prof}/{rid}: no material_tier, can never be upgraded")
            elif mt not in covered:
                fail("gear-no-kit", f"{prof}/{rid}: material_tier {mt!r} has no kit")

    # ── 6. every upgrade kit and attachment must be obtainable ────────────
    for kit in sorted(MATERIAL_KITS):
        if kit not in materials:
            fail("kit-undefined", f"{kit}: in MATERIAL_KITS but not a material")
        elif kit not in produced:
            fail("kit-uncraftable", f"{kit}: no recipe produces it")
    for aid in sorted(ATTACHMENTS):
        if aid not in materials:
            fail("attachment-undefined", f"{aid}: not a material")
        elif aid not in produced:
            fail("attachment-uncraftable", f"{aid}: no recipe produces it")

    # ── 7. no crafted part should be a dead end ───────────────────────────
    used = set()
    for recs in recipes.values():
        for r in recs.values():
            used |= set(r.get("inputs", {}))
    for mid in sorted(produced - used):
        if mid.startswith("upgrade_kit") or mid in ATTACHMENTS:
            continue  # consumed by upgrade_manager / attachment_manager, not a recipe
        if materials.get(mid, {}).get("material_type") == "part":
            fail("part-dead-end", f"{mid}: crafted but nothing consumes it")

    # ── 8. every recipe input must be OBTAINABLE, not merely defined ──────
    # Check 3 only proves an input names a material that exists. A material
    # can exist and still be unreachable - bolt_mageweave was a real material
    # with no recipe, no node and no drop, which made the Mageweave Upgrade
    # Kit uncraftable through an input that looked perfectly valid. This asks
    # the harder question: can a player ever actually hold one?
    obtainable = set(produced)                      # crafted or smelted
    for zone in load("data/gathering/node_pools.json")["zones"].values():
        obtainable |= set(zone.get("table", {}))    # gathered from a node
    for v in load("data/npcs/vendors.json")["vendors"]:
        obtainable |= set(v.get("sells", []))       # bought
    # Prised out of an ore vein. Kyle, 31 Oct 2026: "remove the gemstones as a gathering
    # node bro. we have 40 sprites for wood, ore, and herbs. dont use random shit." The five
    # crystals stopped being their own node type that day, so nothing in node_pools produces
    # them any more and this check correctly started reporting them as unobtainable. They are
    # not: a vein rolls one as a bonus. Read that table rather than hardcoding the ids, so
    # this stays true if the pools change.
    try:
        from world.gathering_manager import GatheringNodeManager
        for pool in GatheringNodeManager.CRYSTAL_FROM_VEIN.values():
            obtainable |= set(pool)
    except Exception as exc:
        fail("vein-crystal-table-unreadable", str(exc))

    # Dropped off creatures - read the real drop tables rather than guessing.
    for mod_name, attr in (("entities.cloth_drops", "BANDS"),
                           ("entities.skinning_drops", "BANDS")):
        try:
            mod = __import__(mod_name, fromlist=[attr])
            for band in getattr(mod, attr, []):
                obtainable |= set(band[2])
        except Exception as exc:
            fail("drop-table-unreadable", f"{mod_name}: {exc}")

    for prof, recs in recipes.items():
        for rid, r in recs.items():
            # A recipe flagged staged_post_60 is authored content waiting on zones that do not
            # exist yet - its material has art and a tier, and is deliberately not gatherable.
            # Reporting it as broken buries the recipes that are ACTUALLY broken: woodcutting
            # alone put 25 of these in the failure list, which is where a real one would hide.
            if r.get("staged_post_60"):
                continue
            for inp in r.get("inputs", {}):
                if inp in known and inp not in obtainable:
                    fail("input-unobtainable",
                         f"{prof}/{rid}: {inp!r} is defined but nothing drops, grows, sells or crafts it")

    # ── report ────────────────────────────────────────────────────────────
    pygame.quit()
    by_check = defaultdict(list)
    for check, detail in failures:
        by_check[check].append(detail)

    total_gear = sum(1 for recs in recipes.values() for r in recs.values()
                     if r.get("output", {}).get("kind") in GEAR_KINDS)
    print(f"checked {sum(len(r) for r in recipes.values())} recipes "
          f"({total_gear} gear) across {len(recipes)} professions")
    if not failures:
        print("\nAll content invariants hold.")
        return 0
    print(f"\n{len(failures)} FAILURES\n" + "=" * 60)
    for check in sorted(by_check):
        items = by_check[check]
        print(f"\n{check}  ({len(items)})")
        for d in items[:12]:
            print(f"    {d}")
        if len(items) > 12:
            print(f"    ... and {len(items)-12} more")
    return 1


if __name__ == "__main__":
    sys.exit(main())
