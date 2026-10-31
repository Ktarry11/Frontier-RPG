#!/usr/bin/env python3
"""Every town with a shop must show a vendor icon on its map.

Kyle, 2026-10-31: "Can we get a map icon indicating vendors? Since I can't find
vendors in towns without clicking on every single person."

Trainers, innkeepers, flight masters, forges and sawmills all had their own map
glyph. The NPC who simply SELLS you things had nothing but the same grey dot
every other person in town gets, so the shop was the one thing on the map you
could not find.

This reproduces the map screen's own marker logic (same services_for_npc call,
same "no service of its own" rule) and reports the count per zone. The NEGATIVE
CONTROL is the point: a zone with no vendors must show NO icon, or the marker is
firing on every NPC and is worth nothing.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    from world.zone_manager import ZoneManager
    from world.ambient_npc_manager import get_ambient_npc_manager
    from world.travel_manager import services_for_npc
    from world.zone_generator import create_all_zones

    zm = ZoneManager()
    zones = create_all_zones()
    vm = getattr(zm, "vendor_manager", None)
    if vm is None:
        print("  no vendor_manager - cannot check"); return 1

    rows = []
    for name in sorted(zones):
        npcs = list(get_ambient_npc_manager().get_npcs_in_zone(name))
        npcs += list(vm.get_vendors_in_zone(name))
        shops, serviced, plain = set(), 0, 0
        for npc in npcs:
            if services_for_npc(npc):
                serviced += 1
                continue
            sells = (list(getattr(npc, "sells", None) or [])
                     or bool(getattr(npc, "sells_gear", False)))
            if sells:
                shops.add((npc.x, npc.y))
            else:
                plain += 1
        rows.append((len(shops), name, len(npcs), serviced, plain))

    withshops = [r for r in rows if r[0]]
    print(f"  {len(rows)} zones; {len(withshops)} now show at least one vendor icon\n")
    for n, name, total, serviced, plain in sorted(withshops, reverse=True)[:25]:
        print(f"    {n:3d} vendor icon(s)   {name:38s} ({total} NPCs, {serviced} service, {plain} plain)")

    ok = True
    if not withshops:
        ok = False
        print("\n  FAIL - no zone shows a vendor icon. The marker never fires.")

    # NEGATIVE CONTROL: zones with NPCs but no sellers must stay clean.
    noshop = [r for r in rows if r[0] == 0 and r[2] > 0]
    print(f"\n  control: {len(noshop)} zone(s) have NPCs but no seller, and show no icon")
    if not noshop:
        ok = False
        print("  FAIL (control) - every populated zone got an icon, so the marker")
        print("  is firing on NPCs generally rather than on vendors.")
    else:
        for n, name, total, serviced, plain in noshop[:5]:
            print(f"    {name:38s} {total} NPCs, none selling")

    # A TOWN with no vendor at all is a content gap, not a map bug - but this is
    # the one place in the codebase that now knows where every shop is, so it is
    # the cheapest place to notice. Reported, never failed: whether a given town
    # should have a shop is Kyle's call, not this tool's.
    towns = [n for n in sorted(zones) if getattr(zones[n], "is_town", False)]
    byname = {r[1]: r[0] for r in rows}
    bare = [t for t in towns if not byname.get(t)]
    if bare:
        print(f"\n  NOTE - {len(bare)} town(s) have no vendor at all:")
        for t in bare:
            print(f"    {t}")

    print("\nPASS" if ok else "\nFAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
