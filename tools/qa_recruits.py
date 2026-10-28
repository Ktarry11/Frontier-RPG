#!/usr/bin/env python3
"""Every recruit is somewhere real, reachable, and at the level of the ground they stand on.

    PYTHONPATH=. python3 tools/qa_recruits.py

A MISPLACED RECRUIT NEVER RAISES ANYTHING. get_recruit_at_location is a pure coordinate match with no
walkability dependency, so a companion standing inside rock is not an error - you just walk at him
forever and nothing happens. That is exactly how ivan_warrior sat unreachable in Ragefire Chasm, and how
kesten_the_catalogued - the Crimson Codex's REVERED reward - pointed at zone "kaels_bastion" when every
zone key in this codebase is a display name, and so resolved to no zone at all.

So this checks the four ways a recruit goes quietly missing:
  * a zone name that does not resolve against the real generated world
  * a tile that is not walkable
  * standing on top of another NPC, vendor or recruit
  * a level that does not belong to the zone they are found in (Kyle, 2026-10-28: "we need to put them
    roughly at the level of the zone they're found in")

The level band comes from the zone's own creatures where it has any, and from its bosses where it is a
cave with hand-placed packs instead of an encounter table.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

#: How far outside its zone's band a recruit's level may sit. Generous on purpose - "roughly" is the
#: word Kyle used, and a companion a little under the local mobs is a reasonable thing to find.
LOW, HIGH = -6, 4


def key(s):
    return str(s).lower().replace(" ", "_").replace("'", "")


def main():
    from world.zone_generator import create_all_zones
    Z = create_all_zones()
    creatures = json.loads((ROOT / "data/creatures/creatures.json").read_text())["creatures"]
    enc = json.loads((ROOT / "data/creatures/encounters.json").read_text())["zones"]

    def is_town(zone_name):
        """A zone with no OPEN-ZONE creatures is a town, and a town has no level.

        This check nearly moved three correct recruits. The Undercity's open zone is empty - it is a
        capital, nothing hostile walks its streets - so its whole "band" of 30-34 comes from the
        Plague Depths dungeon underneath it, and Marco, Sophia and Ryan at levels 10-12 were flagged
        for standing in the Forsaken capital at a sensible level for it. Same shape as the vendor
        audit pricing Orgrimmar for its own rats: a settlement's level is about who passes THROUGH,
        and a town is where everybody does.
        """
        zd = enc.get(zone_name, {})
        if zd.get("open_zone", {}).get("creatures"):
            return False
        # A CAVE IS NOT A TOWN, though both have an empty open_zone table. Caves keep hand-placed
        # packs and pinned bosses instead of an encounter table, so bosses are the tell - without
        # this, blanking towns also blanked Azurelode Mine and the level check stopped doing its job
        # in exactly the places a recruit is most likely to be mis-levelled.
        z = Z.get(zone_name)
        if z is not None and (getattr(z, "boss_positions", None) or getattr(z, "boss_position", None)):
            return False
        return True

    def band(zone_name):
        zd = enc.get(zone_name, {})
        lv = []
        for t in [zd.get("open_zone", {})] + list(zd.get("subzones", {}).values()) \
                + list(zd.get("caves", {}).values()):
            for n in t.get("creatures", {}):
                r = creatures.get(n, {}).get("level_range")
                if r:
                    lv += list(r)
        if lv:
            return min(lv), max(lv)
        # A dungeon or mine cave keeps hand-placed packs rather than an encounter table, so its own
        # bosses are the only level signal there is.
        z = Z.get(zone_name)
        bp = list(getattr(z, "boss_positions", None) or []) if z else []
        bl = [creatures[b[2]]["level_range"] for b in bp
              if len(b) > 2 and b[2] in creatures and creatures[b[2]].get("level_range")]
        if bl:
            flat = [x for r in bl for x in r]
            # Bosses sit above their trash, so read the floor down a little.
            return min(flat) - 6, max(flat)
        return None

    recruits = json.loads((ROOT / "data/npcs/recruits.json").read_text())["recruits"]
    amb = json.loads((ROOT / "data/npcs/ambient_npcs.json").read_text())["npcs"]
    ven = json.loads((ROOT / "data/npcs/vendors.json").read_text())["vendors"]
    occupied = {}
    for n in amb:
        occupied.setdefault(key(n["zone"]), set()).add((n["x"], n["y"]))
    for v in ven:
        occupied.setdefault(key(v["zone"]), set()).add((v["x"], v["y"]))

    placed = [r for r in recruits if r.get("zone")]
    unplaced = [r for r in recruits if not r.get("zone")]
    fails = []
    seen = {}

    print(f"== {len(recruits)} recruits: {len(placed)} placed, {len(unplaced)} not\n")
    print(f"{'recruit':<24}{'class':<13}{'lvl':>4}  {'zone':<28}{'pos':<11}band        verdict")
    for r in sorted(placed, key=lambda r: (r.get("level", 0), r["recruit_id"])):
        zn, x, y, lv = r["zone"], r.get("x"), r.get("y"), r.get("level", 0)
        z = Z.get(zn)
        notes = []
        if z is None:
            fails.append(f"{r['recruit_id']}: zone {zn!r} does not resolve - zone keys are display "
                         f"names everywhere in this codebase")
            notes.append("NO SUCH ZONE")
        else:
            if not z.is_walkable(x, y):
                fails.append(f"{r['recruit_id']}: ({x},{y}) in {zn} is not walkable - unreachable, "
                             f"and nothing will ever warn about it")
                notes.append("UNWALKABLE")
            if (x, y) in occupied.get(key(zn), set()):
                fails.append(f"{r['recruit_id']}: ({x},{y}) in {zn} is already occupied by an NPC")
                notes.append("ON AN NPC")
            dup = seen.get((key(zn), x, y))
            if dup:
                fails.append(f"{r['recruit_id']} and {dup} are on the same tile in {zn}")
                notes.append("STACKED")
            seen[(key(zn), x, y)] = r["recruit_id"]
        b = band(zn) if z is not None else None
        if b and is_town(zn):
            b = None          # see is_town - a town's band is its dungeon's, not its own
        if b:
            if lv < b[0] + LOW or lv > b[1] + HIGH:
                fails.append(f"{r['recruit_id']}: level {lv} against a {b[0]}-{b[1]} zone ({zn})")
                notes.append(f"LEVEL OFF ({b[0]}-{b[1]})")
        print(f"{r['name']:<24}{r['char_class']:<13}{lv:>4}  {zn:<28}{str((x, y)):<11}"
              f"{str(b):<12}{', '.join(notes) or 'ok'}")

    if unplaced:
        print(f"\n  {len(unplaced)} with no zone (authored but not in the world):")
        for r in unplaced:
            print(f"    {r['recruit_id']:<24}{r['char_class']:<13}lvl {r.get('level')}")

    print("\n== spread")
    from collections import Counter
    byzone = Counter(r["zone"] for r in placed)
    lv = sorted(r.get("level", 0) for r in placed)
    print(f"  {len(byzone)} zones hold recruits; levels {lv[0]}-{lv[-1]}")
    crowded = [z for z, n in byzone.items() if n > 3]
    for z in crowded:
        print(f"  note: {z} holds {byzone[z]} recruits")

    print()
    if fails:
        print(f"FAIL ({len(fails)})")
        for f in fails:
            print("  -", f)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
