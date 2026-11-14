#!/usr/bin/env python3
"""Tempest Isle's two open zones have something living in them.

    PYTHONPATH=. python3 tools/qa_tempest_openworld.py

Both zones shipped with dungeons and no open-world table at all (tools/build_tempest_openworld.py).
SIX CLAIMS:
  1. Both zones have an open-zone table and a table for every subzone on their map.
  2. Levels fit: Tempest Shallows 52-55, The Ashen Reach 55-58.
  3. One rare per unsafe subzone, at weight 0, in subzone tables only, never in the open table.
  4. The landing, the works and the town gate are safe.
  5. Every creature has a kit, a sprite of its own kind, and every rare has loot at level + 3
     and a sturdy body (Kyle: "Dont make the boss with 1300 HP").
  6. The dungeon tables under each zone are still there, untouched.
"""
import contextlib
import io
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

BANDS = {"Tempest Shallows": (52, 55), "The Ashen Reach": (55, 58)}
SAFE = {"Tempest Shallows": {"Ashclaim Landing"},
        "The Ashen Reach": {"The Ashclaim Works", "Cinderwharf Gate"}}
DUNGEON = {"Tempest Shallows": "Khaz Varun, the Black Hollow", "The Ashen Reach": "The Emberdeep"}


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        import creature_sprites as CS
        import tools.handbuilt_tempest_shallows as TS
        import tools.handbuilt_ashen_reach as AR
        from world.creature_manager import CreatureManager
        CM = CreatureManager()
    enc = json.loads((ROOT / "data/creatures/encounters.json").read_text(encoding="utf-8"))["zones"]
    creatures = json.loads((ROOT / "data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"]
    kits = json.loads((ROOT / "data/creatures/ability_kits.json").read_text(encoding="utf-8"))["kits"]
    loot = json.loads((ROOT / "data/loot/tempest_isle_rare_loot.json").read_text(encoding="utf-8"))
    bad, n_mobs, n_rares, weakest = [], set(), set(), None

    for zone, mod in (("Tempest Shallows", TS), ("The Ashen Reach", AR)):
        z = enc.get(zone, {})
        lo, hi = BANDS[zone]
        if not (z.get("open_zone") or {}).get("creatures"):
            bad.append(f"{zone}: no open-zone table")
            continue
        subs = z.get("subzones") or {}
        if set(subs) != {s[0] for s in mod.SUBZONES}:
            bad.append(f"{zone}: subzone tables do not match the map")
        if DUNGEON[zone] not in (z.get("caves") or {}) or len(z["caves"][DUNGEON[zone]]["creatures"]) < 20:
            bad.append(f"{zone}: the dungeon table for {DUNGEON[zone]} is missing or cut down")
        for n in z["open_zone"]["creatures"]:
            if creatures.get(n, {}).get("is_boss"):
                bad.append(f"{zone}: rare {n} is in the open-zone table")
        for sub, t in subs.items():
            if sub in SAFE[zone]:
                if not t.get("safe") or t.get("creatures"):
                    bad.append(f"{zone} / {sub} should be safe and empty")
                continue
            rares = [n for n in t["creatures"] if creatures.get(n, {}).get("is_boss")]
            if len(rares) != 1 or t["creatures"][rares[0]] != 0:
                bad.append(f"{zone} / {sub}: rares {rares}, wanted exactly one at weight 0")
            n_rares.update(rares)
        names = set(z["open_zone"]["creatures"]) | {n for t in subs.values() for n in t["creatures"]}
        n_mobs |= names
        for n in names:
            c = creatures.get(n)
            if c is None:
                bad.append(f"{n} is in a table and is not a creature")
                continue
            if not (lo <= c["level_range"][0] and c["level_range"][1] <= hi):
                bad.append(f"{n} is level {c['level_range']}; {zone} is {lo}-{hi}")
            if c.get("ability_kit") not in kits or len(kits[c["ability_kit"]]) < 3:
                bad.append(f"{n} has no kit of three abilities")
            sprite = CS.sprite_for(n, c["template"])
            if not sprite or sprite in ("bandit_human", "bear") :
                bad.append(f"{n} draws as {sprite!r}")
            if c.get("is_boss"):
                pool = loot.get(n) or []
                if len(pool) < 4 or any(i["item_level"] != c["level_range"][1] + 3 for i in pool):
                    bad.append(f"{n}: loot is {[i['item_level'] for i in pool]}, wanted four or more at "
                               f"item level {c['level_range'][1] + 3}")
                with contextlib.redirect_stdout(io.StringIO()):
                    m = CM.spawn_creature(n, c["level_range"][1], zone)
                hp = getattr(m, "max_health", None)
                if not hp:
                    bad.append(f"{n} could not be spawned")
                else:
                    weakest = hp if weakest is None else min(weakest, hp)
                    if hp < 2500:
                        bad.append(f"{n} has {hp} health; a rare at this level should not be flimsy")

    print(f"{len(n_mobs - n_rares)} creatures and {len(n_rares)} rares across both zones"
          + (f"; the flimsiest rare has {weakest} health" if weakest else ""))
    for b in bad[:30]:
        print("  FAIL", b)
    print("\nTempest open world OK - both zones are lived in." if not bad else f"\n{len(bad)} problems")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
