#!/usr/bin/env python3
"""The per-rare damage factors (data/balance/rare_tune.json, tools/tune_rares.py) are sane and reach the game.

    PYTHONPATH=. python3 tools/qa_rare_tune.py

Checks:
  1. every tuned name is a real rare (is_boss) standing in an open-world subzone table, and none is in a hidden place
  2. every factor is inside the tool's own steps (0.5 to 1.8)
  3. a spawned rare's damage factor (world/difficulty.factor) carries its tune, and a dungeon boss's doesn't
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


def main():
    from world import difficulty as D
    from world.creature_manager import CreatureManager
    from world.hidden_zones import creature_kinds, is_hidden
    bad = []
    data = json.loads((ROOT / "data/balance/rare_tune.json").read_text(encoding="utf-8"))
    tune = data.get("rares") or {}
    creatures = json.loads((ROOT / "data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"]
    zones = json.loads((ROOT / "data/creatures/encounters.json").read_text(encoding="utf-8"))["zones"]
    in_subzone = {}
    for z, t in zones.items():
        for st in (t.get("subzones") or {}).values():
            for n in (st.get("creatures") or {}):
                in_subzone.setdefault(n, set()).add(z)
    hidden = set(creature_kinds())
    for name, t in tune.items():
        if not creatures.get(name, {}).get("is_boss"):
            bad.append(f"{name} is tuned but isn't a rare")
        if name in hidden or not any(not is_hidden(z) for z in in_subzone.get(name, ())):
            bad.append(f"{name} is tuned but stands in no open-world subzone")
        if not 0.5 <= float(t) <= 1.8:
            bad.append(f"{name}'s factor {t} is outside 0.5 to 1.8")
    with contextlib.redirect_stdout(io.StringIO()):
        cm = CreatureManager()
    checked = 0
    for name, t in list(tune.items())[:5]:
        zone = next(z for z in in_subzone[name] if not is_hidden(z))
        with contextlib.redirect_stdout(io.StringIO()):
            m = cm.spawn_creature(name, zone_name=zone)
        m.location_type = "subzone"
        got = D.factor(m, "damage")
        saved, D._RARE_TUNE = D._RARE_TUNE, {}
        bare = D.factor(m, "damage")
        D._RARE_TUNE = saved
        if D.kind_of(m) != "rare" or abs(got - bare * float(t)) > 1e-6:
            bad.append(f"{name}: the game doesn't read its factor {t} (kind {D.kind_of(m)}, factor {got:.3f})")
        checked += 1
    boss = next((n for n in D.dungeon_bosses() if n in creatures), None)
    if boss and D.rare_tune(boss) != 1.0:
        bad.append(f"the dungeon boss {boss} picked up a rare's tune")
    for b in bad:
        print("FAIL", b)
    down = sum(1 for v in tune.values() if v < 1)
    print(f"{len(tune)} rares tuned ({down} softened, {len(tune) - down} sharpened), {checked} spawned and read back")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
