#!/usr/bin/env python3
"""The hidden zones work, and stay hidden.

    PYTHONPATH=. python3 tools/qa_hidden_zones.py

Kyle, 14 Nov 2026: hidden levels under dungeons at "4x HP and 4.5x Damage... they drop at 4 to 5
ilvl and can have unique epics above level 30... 1 to 2 bosses max and like 5 trash pulls"; hidden
open maps with "a skull next to them" at "2.5x hp and 2.5x damage", with "max of like 3 or 4"
quests, elite ones allowed; and "I don't want to see as I want these to be secrets."

Prints counts only, never places.

CLAIMS
  1. Every zone in data/world/hidden_zones.json is built, and its parent exists.
  2. Its way in is a secret door in the parent (world/secrets.py), linked both ways; both ends
     stand on walkable ground, and so does where you arrive at each end.
  3. The door gets no map dot, no exit frame, and no glow for anyone outside its secret.
  4. A layer has one or two bosses and five pulls, all on walkable floor, and its spawns populate.
  5. Every creature is in creatures.json with a kit, and is made at the right strength: health and
     damage multipliers 4 / 4.5 in a layer, 2.5 / 2.5 in a skull zone, and a loot lift of 4-5.
  6. Every boss has a pool of its own at its level + 5, drops two, and from level 30 has a
     one-of-a-kind epic; below 30 it has none.
  7. A skull zone has three or four quests, at least one elite, all from someone standing in it;
     every kill target lives there, every fetch item drops from something that lives there, and
     every reward builds and can be worn at the quest's level.
  8. The testing screen's zone list doesn't name them.
"""
import contextlib
import io
import json
import os
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        import pygame
        pygame.init()
        pygame.display.set_mode((64, 64))
        from world.zone_manager import ZoneManager
        zm = ZoneManager()
    from world.hidden_zones import registry, creature_kinds
    from world.secrets import get_secrets
    from world import difficulty
    bad = []
    reg = registry()
    S = get_secrets()
    zones = {n: e["tilemap"] for n, e in zm.zones.items()}
    cre = json.loads((ROOT / "data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"]
    kits = json.loads((ROOT / "data/creatures/ability_kits.json").read_text(encoding="utf-8"))["kits"]
    loot = json.loads((ROOT / "data/loot/hidden_boss_loot.json").read_text(encoding="utf-8"))
    if not reg:
        bad.append("no hidden zones")

    def reach(tm, start):
        seen, q = {start}, deque([start])
        while q:
            x, y = q.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (x + dx, y + dy)
                if n not in seen and 0 <= n[0] < tm.width and 0 <= n[1] < tm.height and tm.is_walkable(*n):
                    seen.add(n)
                    q.append(n)
        return seen

    doors = {d[3]: d for d in S.doors()}
    kinds = {"layer": 0, "skull": 0}
    for zname, info in reg.items():
        kinds[info["kind"]] = kinds.get(info["kind"], 0) + 1
        tm = zones.get(zname)
        if tm is None:
            bad.append(f"a hidden zone is not built ({info['kind']})")
            continue
        if info["parent"] not in zones:
            bad.append("a hidden zone's parent does not exist")
            continue
        # 2. the door
        d = doors.get(zname)
        if d is None:
            bad.append("a hidden zone has no secret door")
            continue
        parent, x, y, _to, tx, ty = d
        ptm = zones[parent]
        if zm.portal_manager.get_destination(parent, x, y) is None or \
                zm.portal_manager.get_destination(zname, tx, ty) is None:
            bad.append("a secret door is not linked both ways")
        if not ptm.is_walkable(x, y) or not ptm.is_walkable(x, y - 2):
            bad.append("a secret door, or where you come back out of it, is not walkable")
        if not tm.is_walkable(tx, ty) or not tm.is_walkable(tx, ty - 2):
            bad.append("a hidden zone's way in, or where you arrive, is not walkable")
        if ptm.get_tile(x, y, "interaction") != "portal":
            bad.append("a secret door has no portal tile")
        # 3. hidden
        if (x, y) not in S.hidden_points(parent):
            bad.append("a secret door would get a map dot")
        if S.shows(parent, x, y, (x + 12, y)):
            bad.append("a secret door glows for someone outside its secret")
        for lm in getattr(ptm, "landmarks", []):
            if lm.get("exit_frame") and lm["anchor_x"] <= x < lm["anchor_x"] + lm["width_tiles"] \
                    and lm["anchor_y"] <= y < lm["anchor_y"] + lm["height_tiles"]:
                bad.append("a secret door has an exit frame drawn round it")
        # the whole hidden zone can be walked from where you arrive
        seen = reach(tm, (tx, ty - 2))
        total = sum(tm.is_walkable(xx, yy) for yy in range(tm.height) for xx in range(tm.width))
        if total - len(seen) > 0:
            bad.append(f"{total - len(seen)} tiles of a hidden zone can't be walked to")
        # 4. a layer's shape
        if info["kind"] == "layer":
            bosses = getattr(tm, "boss_positions", None) or []
            packs = getattr(tm, "trash_packs", None) or []
            if not 1 <= len(bosses) <= 2:
                bad.append(f"a hidden layer has {len(bosses)} bosses")
            if len(packs) != 5:
                bad.append(f"a hidden layer has {len(packs)} pulls")
            for (bx, by, _n) in bosses:
                if (bx, by) not in seen:
                    bad.append("a hidden layer's boss can't be reached")
            for p in packs:
                for (px, py, _m, _l) in p:
                    if (px, py) not in seen:
                        bad.append("a hidden layer's pull stands where nobody can reach")
            with contextlib.redirect_stdout(io.StringIO()):
                try:
                    zm.transition_to_zone(zname, tx, ty - 2, via_portal=False)
                    if not zm.cave_spawns.spawns:
                        bad.append("a hidden layer populated no spawns")
                except Exception as e:  # noqa: BLE001
                    bad.append(f"a hidden layer failed to populate: {type(e).__name__}: {e}")
    # 5. creatures
    from world.creature_manager import CreatureManager
    cm = zm.creature_manager if hasattr(zm, "creature_manager") else CreatureManager()
    want = {"hidden_layer": (4.0, 4.5), "skull_zone": (2.5, 2.5)}
    ck = creature_kinds()
    if not ck:
        bad.append("no creature is in a hidden zone's table")
    for name, kind in ck.items():
        d = cre.get(name)
        if d is None or d.get("ability_kit") not in kits:
            bad.append(f"a hidden creature has no entry or no kit")
            continue
        m = cm.spawn_creature(name)
        if m is None:
            bad.append("a hidden creature could not be made")
            continue
        if difficulty.kind_of(m) != kind:
            bad.append(f"a hidden creature is the wrong kind ({difficulty.kind_of(m)})")
        h, dmg = want[kind]
        if abs(getattr(m, "_difficulty_health", 0) - h) > 1e-6 or abs(difficulty.factor(m, "damage") - dmg) > 1e-6:
            bad.append(f"a hidden creature is not at {h}x health / {dmg}x damage")
        if not 4 <= getattr(m, "loot_ilvl_bonus", 0) <= 5:
            bad.append("a hidden creature's loot is not lifted 4-5 item levels")
    # 6. boss loot
    from entities.boss_loot import get_fixed_boss_loot_all
    for zname, info in reg.items():
        for boss in info.get("bosses") or []:
            pool = loot.get(boss)
            lvl = cre.get(boss, {}).get("level_range", [0, 0])[1]
            if not pool:
                bad.append("a hidden boss has no loot of its own")
                continue
            if any(it["item_level"] != lvl + 5 for it in pool):
                bad.append("a hidden boss's loot is not at its level + 5")
            epics = [it for it in pool if it["rarity"] == "epic"]
            if lvl >= 30 and info["kind"] == "layer" and not epics:
                bad.append("a hidden boss from level 30 has no one-of-a-kind epic")
            if lvl < 30 and epics:
                bad.append("a hidden boss below level 30 has an epic")
            if len(get_fixed_boss_loot_all(boss)) != 2:
                bad.append("a hidden boss doesn't drop two pieces")
    # 7. skull zone quests
    from world.quest_manager import QuestManager
    with contextlib.redirect_stdout(io.StringIO()):
        qm = QuestManager()
    npcs = json.loads((ROOT / "data/npcs/ambient_npcs.json").read_text(encoding="utf-8"))["npcs"]
    npc_at = {n["npc_id"]: n for n in npcs}
    drops = json.loads((ROOT / "data/creatures/quest_drops.json").read_text(encoding="utf-8"))["drops"]
    n_quests = 0
    for zname, info in reg.items():
        if info["kind"] != "skull":
            continue
        key = zname.lower().replace(" ", "_").replace("'", "")
        qs = [q for q in qm.quests.values() if getattr(q, "zone", None) == key]
        n_quests += len(qs)
        if not 3 <= len(qs) <= 4:
            bad.append(f"a skull zone has {len(qs)} quests")
        if not any(getattr(q, "elite", False) or "(Elite)" in q.title for q in qs):
            bad.append("a skull zone has no elite quest")
        here = {n for n, k in ck.items() if k == "skull_zone"}
        tm = zones.get(zname)
        for q in qs:
            g = npc_at.get(q.giver_npc_id)
            if g is None or g.get("zone") != key or (tm and not tm.is_walkable(g["x"], g["y"])):
                bad.append("a skull zone quest's giver isn't standing in the zone")
            for o in q.objectives:
                t = o.get("target") if isinstance(o, dict) else getattr(o, "target", None)
                typ = o.get("type") if isinstance(o, dict) else getattr(o, "type", None)
                if typ == "kill" and t not in here:
                    bad.append("a skull zone quest sends you after something that doesn't live there")
                if typ == "fetch" and not any(any(d.get("item_id") == t for d in drops.get(c, [])) for c in here):
                    bad.append("a skull zone quest wants an item nothing there drops")
            for r in (q.unique_item_defs or []):
                if r.get("required_level", 0) > q.level_min:
                    bad.append("a skull zone quest reward can't be worn at the quest's level")
    # 8. not listed
    from world.testing import zones as test_zones
    if any(d["zone"] in reg for d in test_zones(zm)):
        bad.append("the testing screen lists a hidden zone")

    print(f"{kinds.get('layer', 0)} hidden layers, {kinds.get('skull', 0)} skull zones, {len(ck)} creatures, "
          f"{sum(len(v) for k, v in loot.items() if not k.startswith('_'))} boss items, {n_quests} quests")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for b in bad[:30]:
            print("  -", b)
        return 1
    print("\nHidden zones OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
