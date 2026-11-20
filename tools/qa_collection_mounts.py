#!/usr/bin/env python3
"""The wild and Exalted mounts (sheets H9 to H13, 20 Nov 2026) are reachable, and the AH forms turn four ways.

    PYTHONPATH=. python3 tools/qa_collection_mounts.py

Checks:
  1. every wild mount drops from a real rare (is_boss) standing in an open-world subzone, none in a hidden place, at a
     chance between 1% and 10%, and the combat roll (world/collection.rare_drop) hands it out
  2. every Exalted mount's faction has a quartermaster; the mount is on that shelf at Exalted and not at Revered;
     the shelf entry makes a priced item (world/vendor_stock) that needs Exalted (world/rep_items)
  3. every mount has its four facings on disk
  4. every form with facings has all four, and form_facing_path finds them
"""
import contextlib
import io
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

FACINGS = ("down", "left", "right", "up")


class _Always:
    def random(self):
        return 0.0


def main():
    from world import collection as C
    from world.hidden_zones import creature_kinds, is_hidden
    bad = []
    creatures = json.loads((ROOT / "data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"]
    zones = json.loads((ROOT / "data/creatures/encounters.json").read_text(encoding="utf-8"))["zones"]
    in_subzone = {}
    for z, t in zones.items():
        for st in (t.get("subzones") or {}).values():
            for n in (st.get("creatures") or {}):
                in_subzone.setdefault(n, set()).add(z)
    hidden = set(creature_kinds())
    wild = exalted = 0
    for e in C.entries():
        eff = e.get("effect") or {}
        src = eff.get("drops_from")
        if src:
            wild += 1
            if not creatures.get(src, {}).get("is_boss"):
                bad.append(f"{e['id']} drops from {src}, which isn't a rare")
            if src in hidden or not any(not is_hidden(z) for z in in_subzone.get(src, ())):
                bad.append(f"{e['id']}'s rare stands in no open-world subzone")
            if not 0.01 <= float(eff.get("drop_chance", 0)) <= 0.10:
                bad.append(f"{e['id']}'s drop chance {eff.get('drop_chance')} is outside 1-10%")
            if C.rare_drop(src, _Always()) != e["id"]:
                bad.append(f"{e['id']}: the combat roll never hands it out")
        if e.get("kind") == "mount" and (src or eff.get("exalted_mount_of")):
            stem = e["id"]
            for f in FACINGS:
                if not (ROOT / f"assets/mounts/{stem}_{f}.png").exists():
                    bad.append(f"{stem} has no {f} facing")
                    break
    from world.faction_manager import FactionManager
    from world.vendor_stock import resolve_vendor_item
    from world import rep_items as RI
    with contextlib.redirect_stdout(io.StringIO()):
        fm = FactionManager()
    fac = json.loads((ROOT / "data/factions/factions.json").read_text(encoding="utf-8"))["factions"]
    need = RI._table()[0]
    for fid, fd in fac.items():
        cid = C.exalted_mount_of(fid)
        if not cid:
            continue
        exalted += 1
        stock = (fd.get("rewards") or {}).get("vendor_stock") or {}
        if not stock:
            bad.append(f"{fid} has an Exalted mount but no quartermaster")
            continue
        qm = next(iter(stock))
        f = fm.factions[fid]
        tiers = {t["id"]: t["at"] for t in f.tiers}
        f.standing = tiers["revered"]
        if f"collection:{cid}" in fm.vendor_unlocks(qm):
            bad.append(f"{fid}'s mount is on sale at Revered")
        f.standing = tiers["exalted"]
        if f"collection:{cid}" not in fm.vendor_unlocks(qm):
            bad.append(f"{fid}'s mount isn't on {qm}'s shelf at Exalted")
        f.standing = 0
        it = resolve_vendor_item(f"collection:{cid}")
        if it is None or not getattr(it, "vendor_price", 0):
            bad.append(f"{cid} makes no priced item")
        elif need.get(it.item_id) != (fid, "exalted"):
            bad.append(f"{cid} doesn't need Exalted with {fid} (rep_items: {need.get(it.item_id)})")
    turned = 0
    for e in C.entries():
        base = (e.get("effect") or {}).get("facings")
        if not base:
            continue
        turned += 1
        for f in FACINGS:
            if C.form_facing_path(e["id"], f) != f"{base}_{f}.png":
                bad.append(f"{e['id']} has no {f} facing")
                break
    for b in bad:
        print("FAIL", b)
    print(f"{wild} wild mounts, {exalted} Exalted mounts, {turned} forms turned four ways")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
