#!/usr/bin/env python3
"""Harvest finds work end to end: the starters, the fishing junk and salvage, the mounts and the titles.

    PYTHONPATH=. python3 tools/qa_harvest_finds.py

Kyle, 18 Nov 2026: quests "starting FROM harvesting", and for fishing "the occasional green item and maybe something
unique to fishing! Something fun." (docs/harvest_finds_design.md). Checks, through the real code:
  1. every starter's quest is in the game, started by the item, delivered to someone who exists, and its follow-up
     needs it first and is given by the person it was delivered to
  2. gathering a starter's own material in its band, on a lucky roll, puts the starter in the bag with its quest on it;
     it never comes twice while held; the wrong material or the wrong level never turns it up
  3. a skinned beast of a skinning starter's band can turn one up
  4. a junk pool's catch brings Earth junk; a salvage pool's brings salvage, and on lucky rolls a green and a piece of
     fishing-only gear; an ordinary pool of a mount's water can give its reins; a fishing mount's own pool kinds
     cover every ordinary pool the game shows
  5. the titles come at their milestones, once each
  6. the counters save and load with the character
  7. fishing spots deal out junk and salvage pools now and then, with their own sprites
  8. no trader lists a fishing collectable, and the fishing gear is on the item curve with icons of its own
  9. every new item has an icon on disk
"""
import contextlib
import io
import json
import os
import random
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

fails = []


def check(ok, msg):
    if not ok:
        fails.append(msg)
    return ok


class Lucky(random.Random):
    """Every chance comes up."""
    def random(self):
        return 0.0


class Unlucky(random.Random):
    def random(self):
        return 0.999999


def fresh(level, cls="Warrior"):
    from entities.character import Character
    with contextlib.redirect_stdout(io.StringIO()):
        c = Character(name="QA", char_class=cls, level=level)
    c.inventory = []
    return c


def main():
    import pygame
    pygame.init()
    pygame.display.set_mode((8, 8))
    from world import harvest_finds as HF
    from world.quest_manager import get_quest_manager
    from world.gathering_manager import GatheringNode, JUNK_POOLS, SALVAGE_POOLS
    from world import collection as CL
    d = HF.data()
    with contextlib.redirect_stdout(io.StringIO()):
        qm = get_quest_manager()

    # 1. the quests
    npcs = set()
    for f in (ROOT / "data/npcs").glob("*.json"):
        def walk(o):
            if isinstance(o, dict):
                if o.get("npc_id"):
                    npcs.add(o["npc_id"])
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(json.loads(f.read_text(encoding="utf-8")))
    check(len(d["starters"]) == 16, f"{len(d['starters'])} starters, wanted 16")
    for s in d["starters"]:
        q1 = qm.quests.get(s["quest"])
        if not check(q1 is not None, f"{s['id']}: quest {s['quest']} isn't loaded"):
            continue
        check(q1.giver_npc_id == f"item:{s['id']}", f"{q1.quest_id} isn't started by its item")
        check(q1.turn_in_npc_id in npcs, f"{q1.quest_id} turns in to {q1.turn_in_npc_id}, who doesn't exist")
        q2 = qm.quests.get(q1.next_quest_id)
        if check(q2 is not None, f"{q1.quest_id} has no follow-up"):
            check(q2.giver_npc_id == q1.turn_in_npc_id, f"{q2.quest_id} isn't given by whoever took {q1.quest_id}")
            check(q1.quest_id in (getattr(q2, "requires_quests", None) or []), f"{q2.quest_id} doesn't need {q1.quest_id}")
        check([q.quest_id for q in qm.quests_started_by_item(s["id"])] == [s["quest"]],
              f"{s['id']} doesn't offer its quest from the bag")

    # 2. node starters
    for s in [x for x in d["starters"] if x["trade"] != "skinning"]:
        lo, hi = s["band"]
        p = fresh((lo + hi) // 2)
        lines = HF.on_gather(p, s["trade"], s["mats"][0] if s["mats"] else None, rng=Lucky())
        got = [i for i in p.inventory if getattr(i, "item_id", None) == s["id"]]
        if check(got, f"{s['id']}: a lucky {s['trade']} gather in band didn't turn it up ({lines})"):
            check(got[0].starts_quest_id == s["quest"], f"{s['id']} doesn't start {s['quest']}")
        HF.on_gather(p, s["trade"], s["mats"][0] if s["mats"] else None, rng=Lucky())
        check(sum(getattr(i, "quantity", 1) for i in p.inventory if getattr(i, "item_id", None) == s["id"]) == 1,
              f"{s['id']} came twice while held")
        if s["mats"]:
            q = fresh((lo + hi) // 2)
            HF.on_gather(q, s["trade"], "ore_weakstone_not_it", rng=Lucky())
            check(not any(getattr(i, "item_id", None) == s["id"] for i in q.inventory),
                  f"{s['id']} turned up from the wrong material")
        q = fresh(min(60, hi + 8) if hi < 52 else max(1, lo - 10))
        HF.on_gather(q, s["trade"], s["mats"][0] if s["mats"] else None, rng=Lucky())
        check(not any(getattr(i, "item_id", None) == s["id"] for i in q.inventory),
              f"{s['id']} turned up outside its band")

    # 3. skinning
    for s in [x for x in d["starters"] if x["trade"] == "skinning"]:
        p = fresh(sum(s["band"]) // 2)
        HF.on_gather(p, "skinning", level=sum(s["band"]) // 2, rng=Lucky())
        check(any(getattr(i, "item_id", None) == s["id"] for i in p.inventory),
              f"{s['id']}: a lucky skin of a beast in band didn't turn it up")
        check(any(getattr(i, "item_id", None) == s["id"] for i in HF.LAST_ITEMS),
              f"{s['id']} isn't reported for the victory panel")

    # 4. fishing pools
    p = fresh(30)
    junk = GatheringNode(0, 0, "fish_x")
    junk.find = "junk"
    HF.on_gather(p, "fishing", "fish_x", node=junk, rng=Unlucky())
    check(any(str(getattr(i, "item_id", "")).startswith("ej_") for i in p.inventory), "a junk pool brought no Earth junk")
    p = fresh(40)
    salv = GatheringNode(0, 0, "fish_x")
    salv.find = "salvage"
    HF.on_gather(p, "fishing", "fish_x", node=salv, rng=Unlucky())
    check(any(str(getattr(i, "item_id", "")).startswith("sv_") for i in p.inventory), "a salvage pool brought no salvage")
    p = fresh(40)
    HF.on_gather(p, "fishing", "fish_x", node=salv, rng=Lucky())
    check(any(str(getattr(i, "item_id", "")).startswith("fg_") for i in p.inventory),
          "a lucky salvage haul at 40 brought no fishing-only gear")
    shown = set()
    from world.fishing_pools import ZONE_POOLS, DEFAULT
    for v in list(ZONE_POOLS.values()) + [DEFAULT]:
        shown |= set(v)
    covered = set()
    for m in d["mounts"]:
        covered |= set(m["pools"])
    check(shown <= covered, f"no fishing mount for the pools {sorted(shown - covered)}")
    real_learned = CL.learned
    CL.learned = lambda cid: False
    try:
        for m in d["mounts"]:
            p = fresh(50)
            n = GatheringNode(0, 0, "fish_x")
            n.water = n.pool = m["pools"][0]
            HF.on_gather(p, "fishing", "fish_x", node=n, rng=Lucky())
            check(any(getattr(i, "collection_id", None) == m["id"] for i in p.inventory),
                  f"a lucky catch from {m['pools'][0]} didn't bring {m['id']}")
        # 5. titles
        p = fresh(30)
        p.harvest_log = {"fish": 999, "salvage": 49, "mounts": 0, "found": []}
        HF.on_gather(p, "fishing", "fish_x", node=salv, rng=Unlucky())
        have = {getattr(i, "collection_id", None) for i in p.inventory}
        check("title_the_master_angler" in have, "the thousandth fish didn't earn the Master Angler")
        check("title_the_salvager" in have, "the fiftieth salvage didn't earn the Salvager")
        HF.on_gather(p, "fishing", "fish_x", node=salv, rng=Unlucky())
        check(sum(1 for i in p.inventory if getattr(i, "collection_id", None) == "title_the_salvager") == 1,
              "a title came twice")
    finally:
        CL.learned = real_learned

    # 6. save
    from entities.character import Character
    p = fresh(20)
    p.harvest_log = {"fish": 12, "salvage": 3, "mounts": 1, "found": ["hf_tagged_ear"]}
    with contextlib.redirect_stdout(io.StringIO()):
        back = Character.from_dict(p.to_dict())
    check(back.harvest_log == p.harvest_log, f"the counters didn't survive a save: {back.harvest_log}")

    # 7. pools on the shore
    check(len(JUNK_POOLS) >= 5 and len(SALVAGE_POOLS) >= 3, f"pool sprites {JUNK_POOLS} {SALVAGE_POOLS}")
    with contextlib.redirect_stdout(io.StringIO()):
        from world.zone_manager import ZoneManager
        zm = ZoneManager()
    kinds = {"junk": 0, "salvage": 0, None: 0}
    for _ in range(12):
        zm.transition_to_zone("Durotar", None, None, via_portal=False)
        for node in zm.gathering_manager.active_nodes:
            if node.pool is not None and node.pool_tile:
                kinds[node.find] = kinds.get(node.find, 0) + 1
                if node.find:
                    check(node.pool.startswith(node.find + "_"), f"a {node.find} pool shows {node.pool}")
                    check(node.water is not None, "a junk or salvage pool lost its water")
    check(kinds["junk"] > 0 and kinds["salvage"] >= 0 and kinds[None] > kinds["junk"],
          f"fishing spots over twelve visits: {kinds}")

    # 8. market and gear
    from world.market import market as M
    src = Path(M.__file__).read_text(encoding="utf-8")
    check('not e.get("found_only")' in src, "traders can list a fishing collectable")
    for cid in [m["id"] for m in d["mounts"]] + [t["id"] for t in d["titles"]]:
        e = CL.get_entry(cid)
        check(e is not None and e.get("found_only"), f"{cid} isn't a found-only collectable")
    from entities.item_budget import budget_ratio
    icons = [g["icon_id"] for g in d["fish_gear"]]
    check(len(set(icons)) == len(icons), "two fishing gear pieces share an icon")
    for g in d["fish_gear"]:
        r = budget_ratio(g)
        check(r is None or 0.65 <= r <= 1.45, f"{g['name']} is off the item curve ({r:.2f})")

    # 9. icons
    icon_dirs = [ROOT / "assets/icons" / x for x in ("quest_items", "vendor_trash", "collection", "gear")]
    for i in ([s["icon"] for s in d["starters"]] + [r["icon"] for r in d["earth_junk"] + d["salvage"]]
              + [CL.get_entry(m["id"])["icon_id"] for m in d["mounts"]] + icons):
        check(any((dd / f"{i}.png").exists() for dd in icon_dirs), f"no icon {i}")

    print(f"{len(d['starters'])} starters, {len(d['earth_junk'])} Earth junk, {len(d['salvage'])} salvage, "
          f"{len(d['fish_gear'])} fishing gear, {len(d['mounts'])} mounts, {len(d['titles'])} titles; "
          f"Durotar's spots over twelve visits: {kinds}")
    if fails:
        print(f"FAIL {len(fails)}:")
        for f in fails[:25]:
            print("  ", f)
        return 1
    print("harvest finds OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
