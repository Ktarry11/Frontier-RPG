#!/usr/bin/env python3
"""The Scarlet Monastery is whole: five maps joined, every boss and pack reachable, and every creature, kit, loot pool,
level band, rep source and epic it needs in place. Every boss acts in a real fight and throws something dangerous
(tools/audit_boss_turns.py).

    PYTHONPATH=. python3 tools/qa_scarlet_monastery.py

docs/scarlet_monastery_build_log.md. Kyle, 16 Nov 2026: "So can you also make SM with the 4 different dungeons? The
layout etc."
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main():
    from tools.build_fast_exits import flood, load_world
    from tools import handbuilt_scarlet_monastery as SM
    from tools import build_scarlet_monastery_content as SMC
    from world.portal_manager import PortalManager
    from world.zone_classification import is_dungeon
    from entities.boss_loot import MULTI_DROP, SHARED_HOARD

    bad = []
    tiles = load_world()
    links = PortalManager()._links
    creatures = json.loads((ROOT / "data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"]
    kits = json.loads((ROOT / "data/creatures/ability_kits.json").read_text(encoding="utf-8"))["kits"]
    loot = json.loads((ROOT / "data/loot/scarlet_monastery_boss_loot.json").read_text(encoding="utf-8"))
    levels = json.loads((ROOT / "data/zones/zone_levels.json").read_text(encoding="utf-8"))["zones"]
    enc = json.loads((ROOT / "data/creatures/encounters.json").read_text(encoding="utf-8"))["zones"]

    maps = (SM.GROUNDS,) + SM.WINGS
    for m in maps:
        if m not in tiles:
            bad.append(f"{m} is not in the world")
        if m not in levels:
            bad.append(f"{m} has no level band")
    if bad:
        return report(bad)

    # ---- the doors: Eastern Tirisfal <-> grounds <-> each wing, and every door stands on walkable ground
    def leads(a, b):
        return [(p, d) for p, d in links.get(a, {}).items() if d[0] == b]

    if not leads("Eastern Tirisfal", SM.GROUNDS) or not leads(SM.GROUNDS, "Eastern Tirisfal"):
        bad.append("the gate between Eastern Tirisfal and the grounds is not two-way")
    g = tiles[SM.GROUNDS]
    gate = SM.GROUNDS_GATE
    g_reach = flood(g, (gate[0], gate[1] - 2))
    for wing in SM.WINGS:
        out, back = leads(SM.GROUNDS, wing), leads(wing, SM.GROUNDS)
        if not out or not back:
            bad.append(f"{wing}: its door is not two-way")
            continue
        for (p, _d) in out:
            if not any((p[0] + a, p[1] + b) in g_reach for a in (-1, 0, 1) for b in (-1, 0, 1)):
                bad.append(f"{wing}: its door in the grounds can't be walked to from the gate")
        for (_p, (_z, x, y)) in back:
            if not g.is_walkable(x, y):
                bad.append(f"leaving {wing} lands on a blocked tile in the grounds")
        for (_p, (_z, x, y)) in out:
            if not tiles[wing].is_walkable(x, y - 2):
                bad.append(f"entering {wing} lands on a blocked tile")
        if not is_dungeon(wing):
            bad.append(f"{wing} is not classified as a dungeon")

    # ---- every wing: bosses and packs reachable from the door, each with a record, a kit and loot
    for wing in SM.WINGS:
        t = tiles[wing]
        dx, dy = SM.WING[wing]["door"]
        reach = flood(t, (dx, dy - 2))
        bosses = [tuple(b[:3]) for b in t.boss_positions]
        for (x, y, n) in bosses:
            if (x, y) not in reach:
                bad.append(f"{wing}: {n} can't be reached")
        packs = getattr(t, "trash_packs", None) or []
        if len(packs) < 6:
            bad.append(f"{wing}: only {len(packs)} pulls")
        for p in packs:
            if not 4 <= len(p) <= 5:
                bad.append(f"{wing}: a pull of {len(p)}")
            for (x, y, n, lvl) in p:
                if (x, y) not in reach:
                    bad.append(f"{wing}: a {n} stands where nobody can reach it")
                c = creatures.get(n)
                if not c:
                    bad.append(f"{wing}: {n} has no creature record")
                    continue
                if not c["level_range"][0] <= lvl <= c["level_range"][1]:
                    bad.append(f"{wing}: {n} spawns at {lvl}, outside {c['level_range']}")
        lo, hi = levels[wing]
        names = {n for (_x, _y, n) in bosses} | {m for ms in (getattr(t, "boss_pack", {}) or {}).values()
                                                 for (*_p, m) in ms}
        for n in names | {m for p in packs for (*_q, m, _l) in p}:
            c = creatures.get(n) or {}
            if c.get("ability_kit") not in kits:
                bad.append(f"{n} has no fighting kit")
        for n in names:
            c = creatures.get(n) or {}
            if not c.get("is_boss"):
                bad.append(f"{n} is placed as a boss but isn't one")
            if not lo <= c.get("level_range", [0, 0])[1] <= hi:
                bad.append(f"{n} is outside {wing}'s {lo}-{hi}")
            owner = SHARED_HOARD.get(n, n)
            pool = loot.get(owner) or []
            want = 3 * MULTI_DROP[owner] if owner in MULTI_DROP else 3
            if len(pool) != want:
                bad.append(f"{n}: {len(pool)} loot items, wanted {want}")
            for i in pool:
                if i["item_level"] != creatures[owner]["level_range"][1] + 3:
                    bad.append(f"{i['name']}: item level {i['item_level']}")
        cave = enc.get(SMC.REGION, {}).get("caves", {}).get(wing, {}).get("creatures", {})
        if not names <= set(cave):
            bad.append(f"{wing}: bosses missing from its encounter table: {sorted(names - set(cave))}")
        final = SMC.FINALS[wing]
        if tuple(t.boss_position)[:2] != next((x, y) for (x, y, n) in bosses if n == final):
            bad.append(f"{wing}: the map's named boss isn't {final}")

    # ---- the two-for-one at the end of the Cathedral
    if MULTI_DROP.get("High Inquisitor Whitemane") != 3 or \
            SHARED_HOARD.get("Scarlet Commander Mograine") != "High Inquisitor Whitemane":
        bad.append("Whitemane and Mograine don't share one hoard of three")
    pack = getattr(tiles[SM.CATHEDRAL], "boss_pack", {}) or {}
    if "Scarlet Commander Mograine" not in {m for ms in pack.values() for (*_p, m) in ms}:
        bad.append("Mograine isn't folded into Whitemane's fight")

    # ---- rep: the Order of the Pale Flame, every wing and its Scarlets, capped at Honored
    pf = json.loads((ROOT / "data/factions/factions.json").read_text(encoding="utf-8"))["factions"]["pale_flame"]
    dr = pf.get("dungeon_rep", {})
    for wing in SM.WINGS:
        if wing not in dr.get("dungeons", []) or dr.get("caps", {}).get(wing) != "honored":
            bad.append(f"{wing}: its bosses don't pay the Pale Flame up to Honored")
    kr = pf.get("kill_rep", {}).get("creatures", {})
    for n in SMC.SCARLETS:
        if (kr.get(n) or [0, None])[1] != "honored":
            bad.append(f"{n} doesn't pay the Pale Flame up to Honored")

    # ---- epics on the last bosses; Whitemane's two are her own, each with an icon nothing else uses
    ep = json.loads((ROOT / "data/loot/epic_drops.json").read_text(encoding="utf-8"))
    fb = ep.get("final_bosses", {})
    for wing, boss in SMC.FINALS.items():
        if boss not in fb:
            bad.append(f"{boss} rolls no epic")
    own = [i for i in ep.get("dungeon", []) if i.get("boss") == "High Inquisitor Whitemane"]
    if len(own) != 2:
        bad.append(f"Whitemane has {len(own)} epics of her own, wanted 2")
    every_icon = []
    for path in (ROOT / "data").rglob("*.json"):
        try:
            every_icon.append(path.read_text(encoding="utf-8"))
        except OSError:
            pass
    blob = "\n".join(every_icon)
    for i in own:
        icon = i.get("icon_id")
        if not icon or not (ROOT / "assets/icons/gear" / f"{icon}.png").exists():
            bad.append(f"{i['name']} has no icon on disk")
        elif blob.count(f'"{icon}"') != 1:
            bad.append(f"{i['name']}'s icon {icon} is used {blob.count(chr(34) + icon + chr(34))} times")

    # ---- every boss acts and throws something dangerous (Kyle: "make sure bosses are not just debuffing. they
    # should have something dangerous"), measured in a fight by tools/audit_boss_turns.py
    import subprocess
    names = ",".join(n for n, r in SMC.ROSTER.items() if r[3])
    run = subprocess.run([sys.executable, str(ROOT / "tools/audit_boss_turns.py"), "--only", names],
                         capture_output=True, text=True, cwd=str(ROOT))
    if run.returncode != 0:
        tail = [ln for ln in run.stdout.splitlines() if ln.strip() and "Loaded talent" not in ln][-8:]
        bad.append("a boss is passive or toothless in a real fight: " + " | ".join(tail))

    if bad:
        return report(bad)
    n_packs = sum(len(getattr(tiles[w], "trash_packs", []) or []) for w in SM.WINGS)
    n_boss = sum(len(tiles[w].boss_positions) for w in SM.WINGS)
    print(f"PASS - the grounds and four wings: {n_boss} bosses, {n_packs} pulls, "
          f"{sum(len(v) for k, v in loot.items() if not k.startswith('_'))} boss items")
    return 0


def report(bad):
    print(f"FAIL ({len(bad)})")
    for b in bad:
        print("  -", b)
    return 1


if __name__ == "__main__":
    sys.exit(main())
