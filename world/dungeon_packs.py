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


#: Kyle, 14 Nov 2026: "in dungeons enemies are in packs of 4 to 5...not individual! This is important
#: for tempest isle and royal hive!" The hand-built dungeons wrote their trash as pack(...) groups of
#: two or three, but only the flat list reached the spawn engine, so every one of them was a lone
#: fight. They hand their groups to pad_packs() now, and it fills each to four or five.
PACK_SIZES = (4, 5)


def pad_packs(zone, packs, avoid=(), sizes=PACK_SIZES):
    """Fill each authored pack to four or five (alternating), adding more of the pack's own kinds
    on open floor beside it. packs: [[(x, y, name, level), ...], ...]. avoid: tiles (portals,
    bosses) nobody may stand within five of. Deterministic. Returns the padded packs."""
    taken = {(x, y) for p in packs for (x, y, _n, _l) in p}
    out = []
    for i, pack in enumerate(packs):
        pack = list(pack)
        want = max(len(pack), sizes[i % len(sizes)])
        cx = round(sum(m[0] for m in pack) / len(pack))
        cy = round(sum(m[1] for m in pack) / len(pack))
        spots = sorted(((dx * dx + dy * dy, cx + dx, cy + dy) for dy in range(-6, 7) for dx in range(-6, 7)),
                       key=lambda t: (t[0], t[2], t[1]))
        k = 0
        for (_d, x, y) in spots:
            if len(pack) >= want:
                break
            if not (0 <= x < zone.width and 0 <= y < zone.height) or not zone.is_walkable(x, y):
                continue
            if (x, y) in taken or any(abs(x - t[0]) + abs(y - t[1]) < 2 for t in taken):
                continue
            if any(abs(x - a[0]) + abs(y - a[1]) < 5 for a in avoid):
                continue
            src = pack[k % len(pack)]
            pack.append((x, y, src[2], src[3]))
            taken.add((x, y))
            k += 1
        out.append(pack)
    return out


def attach_packs(zone, packs, avoid=()):
    """Pad the packs and hand them to the spawn engine (zone.trash_packs) with the flat list
    beside them (zone.trash_spawns) for the quest locator and previews."""
    built = pad_packs(zone, packs, avoid)
    zone.trash_packs = built
    zone.trash_spawns = [m for p in built for m in p]
    return built
