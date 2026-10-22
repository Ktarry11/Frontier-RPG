"""Quest helper: where do I find the creature this quest wants killed?

Answers "which subzone / cave / dungeon" for a creature name by reading the same sources the game spawns from:
  * data/creatures/encounters.json - open land, subzones and caves of every zone (random-encounter tables), and
    the dungeon sections at the top level of that file;
  * the live zones' fixed spawn lists (trash_spawns / boss_positions) for hand-built dungeons.
Pure lookup, no game state; the quest journal formats the result.
"""
import json
from pathlib import Path

_ENC = None
_INDEX = None


def _encounters():
    global _ENC
    if _ENC is None:
        path = Path(__file__).resolve().parent.parent / "data" / "creatures" / "encounters.json"
        try:
            _ENC = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            _ENC = {}
    return _ENC


def _add(index, creature, kind, place, region, rare):
    entry = (kind, place, region, rare)
    lst = index.setdefault(creature, [])
    if entry not in lst:
        lst.append(entry)


def _walk(node, path, index):
    if not isinstance(node, dict):
        return
    creatures = node.get("creatures")
    if isinstance(creatures, dict):
        label = node.get("name") or (path[-1] if path else "")
        if len(path) >= 3 and path[0] == "zones":
            zone, section = path[1], path[2]
            if section == "open_zone":
                kind, place, region = "open", label, zone
            elif section == "subzones":
                kind, place, region = "subzone", label, zone
            elif section == "caves":
                kind, place, region = "cave", label, zone
            else:
                kind, place, region = "area", label, zone
        elif len(path) >= 2 and path[0] == "zones":     # zones/<Zone>/open_zone handled above; defensive
            kind, place, region = "open", label, path[1]
        else:
            region = path[0] if path else ""
            kind = "dungeon" if len(path) == 1 else "area"
            place = label if len(path) > 1 else path[0]
        for name, weight in creatures.items():
            _add(index, name, kind, place, region, weight == 0)
    # single-boss dungeon sections: {"boss": {...}} etc. - recurse into every dict child
    for k, v in node.items():
        if k == "creatures":
            continue
        _walk(v, path + [k], index)


def build_index(zones=None):
    """{creature name: [(kind, place, region, is_rare_or_boss), ...]}.  zones: optional {name: Tilemap}."""
    index = {}
    enc = _encounters()
    for top, val in enc.items():
        if top == "zones":
            for zname, zdata in val.items():
                _walk(zdata, ["zones", zname], index)
        else:
            _walk(val, [top], index)
    for zone in (zones or {}).values():
        spawns = getattr(zone, "trash_spawns", None) or []
        bosses = list(getattr(zone, "boss_positions", None) or [])
        bp = getattr(zone, "boss_position", None)
        if bp and len(bp) >= 3:
            bosses.append(bp)
        region = getattr(zone, "region", "") or ""
        for sp in spawns:
            if len(sp) >= 3:
                _add(index, sp[2], "dungeon", zone.name, region, False)
        for b in bosses:
            if len(b) >= 3:
                _add(index, b[2], "dungeon", zone.name, region, True)
    return index


_ZONE_INDEX = (None, None)     # (id(zones), index)


def locate(creature, zones=None):
    """Human-readable 'where to find' strings for a creature (best first, deduped)."""
    global _INDEX, _ZONE_INDEX
    if zones is not None:
        if _ZONE_INDEX[0] != id(zones):
            _ZONE_INDEX = (id(zones), build_index(zones))
        index = _ZONE_INDEX[1]
    else:
        if _INDEX is None:
            _INDEX = build_index()
        index = _INDEX
    order = {"subzone": 0, "cave": 1, "dungeon": 1, "open": 2, "area": 3}
    out, seen = [], set()
    entries = index.get(creature, [])
    cave_places = {e[1] for e in entries if e[0] == "cave"}
    for kind, place, region, rare in sorted(entries, key=lambda e: (order.get(e[0], 9), e[1])):
        if kind == "dungeon" and place in cave_places:
            continue                                  # the same place is already listed as a cave
        if kind == "subzone":
            s = f"{place} ({region})" if region and region != place else place
        elif kind == "cave":
            s = f"{place} - cave in {region}" if region and region != place else f"{place} - cave"
        elif kind == "dungeon":
            s = f"{place} (dungeon)"
        elif kind == "open":
            s = f"{place} - open land in {region}" if region and region != place else place
        else:
            s = f"{place} ({region})" if region and region != place else place
        if rare:
            s += " [rare/boss]"
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


_DROPS = None


def item_sources(item_id):
    """Creature names that can drop a quest item, from data/creatures/quest_drops.json (most likely first)."""
    global _DROPS
    if _DROPS is None:
        path = Path(__file__).resolve().parent.parent / "data" / "creatures" / "quest_drops.json"
        try:
            _DROPS = json.loads(path.read_text(encoding="utf-8")).get("drops", {})
        except (OSError, ValueError):
            _DROPS = {}
    found = []
    for creature, drops in _DROPS.items():
        for d in drops:
            if d.get("item_id") == item_id:
                found.append((-float(d.get("chance", 1.0)), creature))
    return [c for _, c in sorted(found)]


def locate_item(item_id, zones=None):
    """'Creature - where' strings for a quest item that drops from creatures (best first, deduped)."""
    out = []
    for creature in item_sources(item_id):
        places = locate(creature, zones)
        out.append(f"{creature} - {places[0]}" if places else creature)
    return out
