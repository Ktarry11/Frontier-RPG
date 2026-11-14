"""Group pulls for fixed-spawn dungeons.

tools/build_dungeon_pulls.py regroups each dungeon's trash into PACKS of 3-4 mobs (about 3-4 pulls before each boss) and
writes data/dungeons/trash_packs.json. create_all_zones() calls apply_packs() to attach them: zone.trash_packs (what the
spawn engine uses - a pack pulls together) and zone.trash_spawns (the flat list, for the quest locator / previews). The
dungeon's original hand-authored flat list is kept on zone.authored_trash_spawns, which is what the tool regroups from.
"""
import json
import os

PACKS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "data", "dungeons", "trash_packs.json")


def load_packs():
    try:
        with open(PACKS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def apply_packs(zones):
    data = load_packs()
    for name, packs in data.items():
        zone = zones.get(name)
        if zone is None:
            continue
        if getattr(zone, "authored_trash_spawns", None) is None:
            zone.authored_trash_spawns = list(getattr(zone, "trash_spawns", None) or [])
        built = []
        for pack in packs:
            members = []
            for (x, y, mob, lvl) in pack:
                if not zone.is_walkable(x, y):
                    raise ValueError(f"{name}: pack member {mob} at ({x},{y}) is not walkable - the layout changed; "
                                     f"re-run tools/build_dungeon_pulls.py")
                members.append((x, y, mob, lvl))
            built.append(members)
        zone.trash_packs = built
        zone.trash_spawns = [m for p in built for m in p]
