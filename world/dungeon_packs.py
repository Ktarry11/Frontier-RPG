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


#: Boss maps that are dungeons in all but name (the Return Voyage's ships, the Eldest Sequoia): their trash is held to
#: the same pack sizes. tools/qa_dungeon_packs.py and tools/qa_dungeon_fast_exits.py read this list.
ALSO_DUNGEONS = {"The Bloodsail Raider", "The Raider's Hold", "The Galleon's Weather Deck", "The Galleon's Hold",
                 "The Captain's Cabin", "The Eldest Sequoia", "The Eldest's Crown"}
#: PACK SIZE BY LEVEL (Kyle, 14 Nov 2026: "in dungeons enemies are in packs of 4 to 5...not individual!"; 17 Nov: "we
#: keep them 3-4 below 30"). A dungeon whose band starts at 30 or above fights in packs of 4-5, below that 3-4.
BIG_PACKS_FROM = 30


def band_sizes(name, levels=None):
    """(smallest, largest) pack for a dungeon, from its band in data/zones/zone_levels.json."""
    if levels is None:
        try:
            with open(os.path.join(os.path.dirname(PACKS_PATH), "..", "zones", "zone_levels.json"),
                      encoding="utf-8") as f:
                levels = json.load(f)
        except (OSError, ValueError):
            levels = {}
        levels = levels.get("zones") or levels
    band = levels.get(name)
    return (4, 5) if band and band[0] >= BIG_PACKS_FROM else (3, 4)


def pad_to_bands(zones):
    """Fill every dungeon's packs up to its band's size (17 Nov 2026). Several dungeons were built with packs of two
    and three before the sizes were settled, Stonetalon's, the Return Voyage's ships and the Arena among them, and
    some hidden ones; this brings every one to the rule in one place rather than in each builder. A pack already big
    enough is left alone, and a pack with no floor beside it stays as it is (tools/qa_dungeon_packs.py reports it).
    Runs after apply_packs, inside create_all_zones."""
    from world.zone_classification import is_dungeon
    try:
        with open(os.path.join(os.path.dirname(PACKS_PATH), "..", "zones", "zone_levels.json"),
                  encoding="utf-8") as f:
            levels = json.load(f)
    except (OSError, ValueError):
        levels = {}
    levels = levels.get("zones") or levels
    padded = 0
    for name, zone in zones.items():
        packs = getattr(zone, "trash_packs", None)
        if not packs or not (is_dungeon(name) or name in ALSO_DUNGEONS):
            continue
        lo, hi = band_sizes(name, levels)
        if all(len(p) >= lo for p in packs):
            continue
        avoid = [(b[0], b[1]) for b in (getattr(zone, "boss_positions", None) or [])]
        layer = getattr(zone, "interaction_layer", None) or []
        avoid += [(x, y) for y, row in enumerate(layer) for x, v in enumerate(row) if v == "portal"]
        sizes = (lo, hi)
        built = pad_packs(zone, [list(p) for p in packs], avoid, sizes=sizes)
        padded += sum(len(b) - len(p) for b, p in zip(built, packs))
        zone.trash_packs = built
        zone.trash_spawns = [m for p in built for m in p]
    return padded
