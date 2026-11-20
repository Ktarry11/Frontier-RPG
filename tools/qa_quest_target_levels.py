#!/usr/bin/env python3
"""Every open-world quest sends you after creatures you can fight at the quest's level.

    PYTHONPATH=. python3 tools/qa_quest_target_levels.py

For each kill objective (its target and alt_targets) and each fetch objective (every creature that drops the item,
data/creatures/quest_drops.json), the lowest level any of those creatures can be is compared with the quest's
level_max. Three or more levels above it fails.

Found 20 Nov 2026 by the levelling run (tools/sim_campaign.py): Razor Hill's "What the Kolkar Left Behind" (then 6-9)
took its crates from the Kolkar Raider, a 14-17 centaur in the Northern Barrens, and killed the warrior and the mage
37 times between them at level 11. The crates drop in Kolkar Crag now and the quest is 8-11.

It also checks every open-world encounter table (each zone's open ground and each subzone, with the zone's
level_overrides applied): a creature whose lowest level is four or more above the table's median fails. Found the same
day: the Drowned Deckhand is shared with Silverpine (16-18), Durotar's global level patch for it had been overwritten,
and the Scuttle Coast (7-10) rolled a 16-18 undead one time in eight. Durotar carries it in level_overrides now.

Bosses and anything in a hidden place are skipped (a named quest boss is meant to be a step up; hidden places have
their own rules), and so is a quest in a hidden zone.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

GAP = 3


def main():
    from world.hidden_zones import creature_kinds, is_hidden
    hidden = set(creature_kinds())
    creatures = json.loads((ROOT / "data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"]
    drops = json.loads((ROOT / "data/creatures/quest_drops.json").read_text(encoding="utf-8"))["drops"]
    droppers = {}
    for name, items in drops.items():
        for it in items:
            droppers.setdefault(it.get("item_id"), []).append(name)
    bad, checked = [], 0
    for f in sorted((ROOT / "data/quests").glob("*.json")):
        try:
            quests = json.loads(f.read_text(encoding="utf-8")).get("quests", [])
        except ValueError:
            continue
        for q in quests:
            if is_hidden(q.get("zone") or ""):
                continue
            hi = q.get("level_max") if q.get("level_max") is not None else q.get("level_min", 1)
            for o in q.get("objectives") or []:
                kind = o.get("type")
                if kind == "kill":
                    names = [o.get("target")] + list(o.get("alt_targets") or [])
                elif kind == "fetch":
                    names = droppers.get(o.get("target"), [])
                else:
                    continue
                names = [n for n in names if n in creatures and n not in hidden
                         and not creatures[n].get("is_boss") and creatures[n].get("level_range")]
                if not names:
                    continue
                checked += 1
                low = min(creatures[n]["level_range"][0] for n in names)
                if low - hi >= GAP:
                    bad.append(f"{f.name}: {q.get('quest_id')} ({q.get('title')}, to {hi}) {kind}s from "
                               + ", ".join(f"{n} {creatures[n]['level_range']}" for n in names))
    print(f"{checked} kill and fetch objectives checked, {len(bad)} send you {GAP}+ levels above the quest")
    bad += tables(creatures, hidden)
    for b in bad:
        print("FAIL", b)
    return 1 if bad else 0


def tables(creatures, hidden):
    import statistics
    from world.gathering_manager import CAVE_TO_PARENT_ZONE
    from world.hidden_zones import is_hidden
    from world.zone_classification import DUNGEONS
    closed = set(DUNGEONS) | set(CAVE_TO_PARENT_ZONE)
    zones = json.loads((ROOT / "data/creatures/encounters.json").read_text(encoding="utf-8"))["zones"]
    bad, n = [], 0
    for zone, t in zones.items():
        if is_hidden(zone):
            continue
        over = t.get("level_overrides") or {}
        tabs = [("open ground", (t.get("open_zone") or {}).get("creatures") or {})]
        tabs += [(sz, st.get("creatures") or {}) for sz, st in (t.get("subzones") or {}).items() if sz not in closed]
        for where, table in tabs:
            rows = [(c, over.get(c) or creatures[c]["level_range"]) for c, w in table.items()
                    if w and c in creatures and c not in hidden and not creatures[c].get("is_boss")
                    and creatures[c].get("level_range")]
            if len(rows) < 3:
                continue
            n += 1
            mid = statistics.median(lv[0] for _c, lv in rows)
            bad += [f"{zone}, {where}: {c} {lv} among creatures around {mid:g}" for c, lv in rows if lv[0] - mid >= 4]
    print(f"{n} open-world encounter tables checked, {len(bad)} with a creature 4+ levels above the rest")
    return bad


if __name__ == "__main__":
    sys.exit(main())
