#!/usr/bin/env python3
"""Do a quest's directions point at where the thing actually is?

    PYTHONPATH=. python3 tools/audit_quest_directions.py [zone-file-stem ...] [--all]

Playtest, 12 Nov 2026 - "quest text on Scouting the Prowler Den is messed up" - and Kyle's
verdict on it: "Either trash writing or trash directions." The text of a quest and the place
it sends you were authored separately, and nothing ever compared them.

For every quest whose giver stands on a map, this works out WHERE each objective is on that
same map - an explore point, the subzone a creature spawns in, the door of the cave it lives
in, the creature that carries a fetch item - takes the compass bearing from the giver to it,
and reads the compass words out of what the giver says. It reports:

    WRONG     the text names a direction and the target is nowhere near that bearing
    SILENT    the target is a specific place a good walk away and the text gives neither a
              direction nor the place's name
    UNPLACED  the objective has nowhere to be: a creature in no spawn table of its zone, a
              fetch item nothing carries

It reads the live maps (the same ones the game builds), so it cannot drift from them.
"""
import glob
import json
import math
import os
import re
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

#: Closer than this (tiles) a direction is not needed and is not judged.
NEAR = 14
#: Further than this, with no direction and no place name, the quest is SILENT.
FAR = 30

BEARINGS = ["east", "south-east", "south", "south-west", "west", "north-west", "north", "north-east"]
WORDS = {
    "north-east": r"north[\s-]?east(?:ern)?|\bNE\b", "north-west": r"north[\s-]?west(?:ern)?|\bNW\b",
    "south-east": r"south[\s-]?east(?:ern)?|\bSE\b", "south-west": r"south[\s-]?west(?:ern)?|\bSW\b",
    "north": r"\bnorth(?:ern|ward|wards)?\b", "south": r"\bsouth(?:ern|ward|wards)?\b",
    "east": r"\beast(?:ern|ward|wards)?\b", "west": r"\bwest(?:ern|ward|wards)?\b",
}


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", str(s or "").lower()).strip("_")


def bearing(dx, dy):
    ang = math.degrees(math.atan2(dy, dx)) % 360          # screen y runs down: +y is south
    return BEARINGS[int((ang + 22.5) // 45) % 8]


def said(text):
    """Compass words in the text. A compound ('south-west') hides its two halves."""
    found, rest = set(), text
    for name in ("north-east", "north-west", "south-east", "south-west"):
        if re.search(WORDS[name], rest, re.I):
            found.add(name)
            rest = re.sub(WORDS[name], " ", rest, flags=re.I)
    for name in ("north", "south", "east", "west"):
        if re.search(WORDS[name], rest, re.I):
            found.add(name)
    return found


def agrees(word, actual):
    """Within one compass step: 'north' is fine for north-east, wrong for east."""
    i, j = BEARINGS.index(word), BEARINGS.index(actual)
    return min((i - j) % 8, (j - i) % 8) <= 1


class World:
    def __init__(self):
        import pygame
        pygame.init()
        pygame.display.set_mode((64, 64))
        from world.zone_manager import ZoneManager
        from world.ambient_npc_manager import get_ambient_npc_manager
        self.zm = ZoneManager()
        self.maps = {slug(name): (name, z["tilemap"]) for name, z in self.zm.zones.items()}
        self.npcs = {}
        for nid, n in get_ambient_npc_manager().npcs.items():
            self.npcs[nid] = (slug(n.zone), n.x, n.y, n.name)
        try:
            from world.vendor_manager import get_vendor_manager
            vm = get_vendor_manager()
            for vid, v in getattr(vm, "vendors", {}).items():
                if vid not in self.npcs and getattr(v, "x", None) is not None:
                    self.npcs[vid] = (slug(v.zone), v.x, v.y, v.name)
        except Exception:
            pass
        self.enc = json.load(open("data/creatures/encounters.json"))["zones"]
        drops = json.load(open("data/creatures/quest_drops.json"))["drops"]
        self.carriers = {}
        for creature, ds in drops.items():
            for d in ds:
                self.carriers.setdefault(d.get("item_id"), set()).add(creature)

    def anywhere(self, creature):
        from world.quest_locator import locate
        try:
            return bool(locate(creature, self.zm.zones))
        except Exception:
            return True

    def places(self, map_key, creature):
        """[(label, x, y)] on this map where the creature is met; [] if it roams the open zone;
        None if this zone's tables do not have it at all."""
        name, tm = self.maps[map_key]
        table = self.enc.get(name)
        if table is None:
            return None
        out, anywhere, known = [], False, False
        if creature in (table.get("open_zone", {}).get("creatures") or {}):
            anywhere = known = True
        for key, sz in (table.get("subzones") or {}).items():
            if creature in (sz.get("creatures") or {}):
                known = True
                rect = next((s for s in tm.subzones if s.get("table_key") == key or s.get("name") == key), None)
                if rect is not None:
                    out.append((sz.get("name") or key, rect["x"] + rect["w"] / 2, rect["y"] + rect["h"] / 2))
        for key, cave in (table.get("caves") or {}).items():
            if creature in (cave.get("creatures") or {}):
                known = True
                for (px, py) in self.zm.portal_manager.get_portal_positions(name) or []:
                    dest = self.zm.portal_manager.get_destination(name, px, py)
                    if dest and dest[0] == key:
                        out.append((cave.get("name") or key, px, py))
        # hand-placed spawns on this map (pinned bosses, dungeon trash)
        for attr in ("fixed_spawns", "trash_spawns"):
            spawns = getattr(tm, attr, None)
            for sp in (spawns if isinstance(spawns, (list, tuple)) else []):
                if not isinstance(sp, dict):
                    continue
                names = sp.get("creatures") or [sp.get("creature") or sp.get("name")]
                if creature in [n for n in names if n]:
                    known = True
                    out.append((creature, sp.get("x", 0), sp.get("y", 0)))
        if not known:
            return None
        return [] if (anywhere and not out) else out


def audit(world, stems):
    findings = {"WRONG": [], "SILENT": [], "UNPLACED": []}
    seen = judged = 0
    # Rewritten zones keep their text in an overlay (data/quests/text/<zone>.json) that
    # QuestManager lays over the quest files; judge that, not the text underneath it.
    overlay = {}
    for path in glob.glob("data/quests/text/*.json"):
        data = json.load(open(path))
        for qid, fields in (data.get("quests", data) if isinstance(data, dict) else {}).items():
            if isinstance(fields, dict):
                overlay.setdefault(qid, {}).update(fields)
    for path in sorted(glob.glob("data/quests/*.json")):
        stem = os.path.basename(path)[:-5]
        if stems and stem not in stems:
            continue
        data = json.load(open(path))
        quests = data.get("quests", data) if isinstance(data, dict) else data
        quests = quests if isinstance(quests, list) else list(quests.values())
        for q in quests:
            if not isinstance(q, dict) or "objectives" not in q:
                continue
            q = dict(q, **overlay.get(q.get("quest_id"), {}))      # the text the game actually shows
            seen += 1
            giver = world.npcs.get(q.get("giver_npc_id"))
            if giver is None or giver[0] not in world.maps:
                continue
            gmap, gx, gy, _gname = giver
            text = " ".join(str(q.get(k, "")) for k in ("accept_text", "description"))
            words = said(text)
            targets, unplaced = [], []
            for o in q["objectives"]:
                kind, tgt = o.get("type"), o.get("target")
                if kind == "explore" and o.get("target_x") is not None and slug(tgt) == gmap:
                    targets.append((o.get("label") or "the place", o["target_x"], o["target_y"]))
                    continue
                creatures = []
                if kind in ("kill", "kill_boss") and tgt:
                    creatures = [tgt] + list(o.get("alt_targets") or [])
                elif kind in ("fetch", "gather") and tgt:
                    creatures = sorted(world.carriers.get(tgt, ()))
                    if not creatures and kind == "fetch":
                        unplaced.append(f"nothing drops {tgt}")
                for c in creatures:
                    where = world.places(gmap, c)
                    if where is None:
                        # not on the giver's map: fine if it lives somewhere. Nowhere at all is the bug.
                        if not world.anywhere(c):
                            unplaced.append(f"{c} is in no spawn table or dungeon anywhere")
                        continue
                    targets.extend(where)
            for u in unplaced:
                findings["UNPLACED"].append((stem, q["title"], u))
            far = [(label, x, y, math.hypot(x - gx, y - gy)) for label, x, y in targets]
            far = [t for t in far if t[3] >= NEAR]
            if not far:
                continue
            judged += 1
            actual = sorted({bearing(x - gx, y - gy) for _l, x, y, _d in far})
            if words:
                if not any(agrees(w, a) for w in words for a in actual):
                    findings["WRONG"].append((stem, q["title"],
                                              f"says {'/'.join(sorted(words))}; {far[0][0]} is {actual[0]}"
                                              + (f" (also {', '.join(actual[1:])})" if len(actual) > 1 else "")))
            else:
                named = any(slug(l) and re.search(re.escape(l), text, re.I) for l, *_ in far)
                longest = max(far, key=lambda t: t[3])
                if not named and longest[3] >= FAR:
                    findings["SILENT"].append((stem, q["title"],
                                               f"{longest[0]} is {int(longest[3])} tiles {bearing(longest[1] - gx, longest[2] - gy)} and the text gives no direction or name"))
    return findings, seen, judged


def main():
    stems = [a for a in sys.argv[1:] if not a.startswith("--")]
    findings, seen, judged = audit(World(), stems)
    by_zone = {}
    for kind, rows in findings.items():
        for stem, title, why in rows:
            by_zone.setdefault(stem, []).append((kind, title, why))
    for stem in sorted(by_zone):
        rows = by_zone[stem]
        print(f"\n{stem}  ({len(rows)})")
        if stems or "--all" in sys.argv:
            for kind, title, why in sorted(rows):
                print(f"   {kind:8s} {title}: {why}")
        else:
            counts = {k: sum(1 for r in rows if r[0] == k) for k in findings}
            print("   " + ", ".join(f"{n} {k}" for k, n in counts.items() if n))
    print(f"\n{seen} quests read, {judged} with a place to point at: "
          + ", ".join(f"{len(v)} {k}" for k, v in findings.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
