#!/usr/bin/env python3
"""Give every crafted piece its own icon, from the game's icons and Kyle's WoW icon pack.

    PYTHONPATH=. python3 tools/assign_crafted_icons.py --pack "/path/to/WoW Icon Pack" [--apply]

Kyle, 16 Nov 2026: "every unique item in the game can only have ONE icon", then, sending the pack: "Take what you
need and include it for current crafting and cooking or other professions as needed! A lot of it was never
utilized." And on crafted epics: "We can use some of other overlapping images for crafted epics. Since we have too
many things. We can make sets that look similar bro."

HOW A PIECE IS GIVEN ITS ICON
  * The pool for a piece is every icon of its kind: the game's own (gear_inv_*, the Vanilla pack) and the pack's
    larger half that was never installed (TBC and Wrath art), labelled by slot and armour type in
    tools/pack_icon_labels.json.
  * The piece takes the icon nearest its collection's colour (tools/crafted_icon_palette.py: fel is fel-green,
    ember red-orange, frost icy blue), so a collection reads as one set.
  * An icon is never used twice inside a collection. Across the game an icon that nothing else uses is
    preferred, then one another crafted piece uses, and last one a quest or boss item uses: the pool for some
    slots (rings, necks, shields, wands) is smaller than the number of crafted pieces, so a few still share.
  * EPICS draw from the pack only and never share: each crafted epic has an icon no other item has. No crafted
    piece ever takes a named world or dungeon epic's icon (data/loot/epic_drops.json).
  * Same recipes in, same icons out. The picks are written to data/items/crafted_icons.json, which
    build_crafted_gear.icon_for reads, so a rebuild keeps them.

Only the pack icons a piece actually takes are copied in (gear_wow_<kind>_<source>), so the repo grows by what's
used. The procedural roller's prefixes (gear_inv_*) never reach them.
"""
import argparse
import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import crafted_icon_palette as CP  # noqa: E402

FILES = ["data/crafting/recipes.json", "data/blacksmithing/recipes.json", "data/leatherworking/recipes.json",
         "data/jewelcrafting/recipes.json"]
LABELS = ROOT / "tools/pack_icon_labels.json"
OUT = ROOT / "data/items/crafted_icons.json"
GEAR = ROOT / "assets/icons/gear"

#: a weapon type -> the pack label that draws it
WEAPON_LABEL = {"bow": "bow", "crossbow": "crossbow", "gun": "gun", "polearm": "polearm", "fist_weapon": "fist",
                "dagger": "dagger", "sword_1h": "dagger", "staff": "staff", "wand": "wand", "tome": "tome",
                "idol": "idol", "totem": "totem", "libram": "libram"}


def walk(x):
    if isinstance(x, dict):
        o = x.get("output")
        if isinstance(o, dict) and isinstance(o.get("item"), dict) and o["item"].get("slot"):
            yield o["item"]
        for v in x.values():
            yield from walk(v)
    elif isinstance(x, list):
        for v in x:
            yield from walk(v)


def icons_used_elsewhere():
    """icon -> names of items OUTSIDE the crafting files that draw it."""
    used = collections.defaultdict(set)
    skip = {str(ROOT / f) for f in FILES} | {str(OUT)}

    def rec(o):
        if isinstance(o, dict):
            if isinstance(o.get("icon_id"), str) and o.get("name") and (o.get("item_level") or o.get("slot")):
                used[o["icon_id"]].add(o["name"])
            for v in o.values():
                rec(v)
        elif isinstance(o, list):
            for v in o:
                rec(v)
    for f in sorted((ROOT / "data").rglob("*.json")):
        if str(f) in skip:
            continue
        try:
            rec(json.loads(f.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            continue
    return used


def pack_id(source, kind):
    stem = re.sub(r"[^a-z0-9]+", "_", Path(source).stem.lower()).strip("_")
    return f"gear_wow_{kind}_{stem}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", required=True)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    from PIL import Image
    pack = Path(a.pack)
    labels = json.loads(LABELS.read_text(encoding="utf-8"))
    from tools.install_epic_icons import ICONS as EPIC_ICONS
    taken_sources = set(EPIC_ICONS.values())

    # ---- the pack candidates, measured from the pack itself (only the ones used are copied in)
    cand = {}                       # icon id -> (kind, material, source)
    for source, (kind, material) in labels.items():
        if source in taken_sources or not (pack / source).exists():
            continue
        cand[pack_id(source, kind)] = (kind, material, source)
    measured = {}

    def measure(icon):
        if icon in cand:
            if icon not in measured:
                measured[icon] = _measure_path(pack / cand[icon][2])
            return measured[icon]
        return CP.measure(icon)

    def pack_pool(slot, armor, weapon):
        kind = WEAPON_LABEL.get(weapon) if weapon else re.sub(r"\d+$", "", slot)
        if kind is None:
            return []
        out = []
        for icon, (k, m, _s) in cand.items():
            if k != kind:
                continue
            if m and armor and m != armor:
                continue
            out.append(icon)
        return sorted(out)

    # ---- every crafted piece, once per name
    docs = {f: json.loads((ROOT / f).read_text(encoding="utf-8")) for f in FILES}
    pieces = {}
    for f, d in docs.items():
        for it in walk(d):
            pieces.setdefault(it["name"], it)
    elsewhere = icons_used_elsewhere()
    # the named epics' icons are theirs alone (tools/build_epic_drops.py): no crafted piece may take one
    ep = json.loads((ROOT / "data/loot/epic_drops.json").read_text(encoding="utf-8"))
    epic_owned = {d.get("icon_id") for k in ("world", "dungeon") for d in ep.get(k, [])}
    used = collections.Counter()            # crafted uses so far
    by_set = collections.defaultdict(set)
    assign = {}
    epic_icons = set()
    epics = [n for n, it in pieces.items() if it.get("rarity") in ("epic", "legendary")]
    plain = [n for n in pieces if n not in set(epics)]

    def cost(icon, want, epic):
        c = CP.distance(want, measure(icon))
        if epic:
            return c
        c += 0.5 * used[icon]                 # another crafted piece has it
        if elsewhere.get(icon):
            c += 1.0                          # a quest or boss item has it
        return c

    for group, names in (("epic", sorted(epics)), ("plain", sorted(plain))):
        for name in names:
            it = pieces[name]
            slot, armor, weapon = it["slot"], it.get("armor_type"), it.get("weapon_type")
            collection = name.split()[0].lower()
            want = CP.target(name, armor)
            if group == "epic":
                pool = [i for i in pack_pool(slot, armor, weapon) if not used[i] and not elsewhere.get(i)]
                if not pool:   # the pack has nothing of this kind left: an unused icon of the game's own
                    pool = [i for i in CP.pool(slot, armor, weapon) if not used[i] and not elsewhere.get(i)]
            else:
                pool = [i for i in CP.pool(slot, armor, weapon) + pack_pool(slot, armor, weapon)
                        if i not in epic_icons]
            pool = [i for i in pool if i not in epic_owned]
            pool = [i for i in pool if i not in by_set[collection]] or pool
            if not pool:
                print(f"  no icon at all for {name} ({slot} {armor or weapon})")
                continue
            best = min(pool, key=lambda i: (cost(i, want, group == "epic"), i))
            assign[name] = best
            used[best] += 1
            if group == "epic":
                epic_icons.add(best)
            by_set[collection].add(best)

    # ---- report
    shared = sum(1 for i, n in used.items() if n > 1)
    clash = sum(1 for n, i in assign.items() if elsewhere.get(i))
    fresh = sorted({i for i in assign.values() if i in cand})
    epic_ok = sum(1 for n in epics if used[assign.get(n)] == 1 and not elsewhere.get(assign.get(n)))
    print(f"{len(assign)} crafted pieces: {len(fresh)} pack icons taken, {shared} icons still on more than one "
          f"crafted piece, {clash} sharing with a quest or boss item; epics with an icon of their own "
          f"{epic_ok}/{len(epics)}")
    if not a.apply:
        return 0

    for icon in fresh:
        Image.open(pack / cand[icon][2]).convert("RGBA").resize((60, 60), Image.LANCZOS).save(GEAR / f"{icon}.png")
    for f, d in docs.items():
        for it in walk(d):
            if it["name"] in assign:
                it["icon_id"] = assign[it["name"]]
        (ROOT / f).write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT.write_text(json.dumps({"_notes": "Crafted piece -> its icon. Written by tools/assign_crafted_icons.py; "
                                         "read by tools/build_crafted_gear.icon_for so a rebuild keeps them.",
                               "icons": dict(sorted(assign.items()))}, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} and the recipe files; copied {len(fresh)} icons")
    return 0


def _measure_path(path):
    """crafted_icon_palette.measure, for a file that isn't in the gear folder by id."""
    import colorsys
    import math
    from PIL import Image
    img = Image.open(path).convert("RGBA").resize((32, 32))
    xs = ys = 0.0
    ss = vs = n = w = 0.0
    for r, g, b, al in (img.get_flattened_data() if hasattr(img, 'get_flattened_data') else img.getdata()):
        if al < 128:
            continue
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        n += 1
        ss += s
        vs += v
        if s > 0.2 and v > 0.15:
            k = s * v
            xs += math.cos(h * 2 * math.pi) * k
            ys += math.sin(h * 2 * math.pi) * k
            w += k
    if not n:
        return (0.0, 0.0, 0.0)
    hue = (math.degrees(math.atan2(ys, xs)) % 360) if w else 0.0
    return (hue, ss / n, vs / n)


if __name__ == "__main__":
    sys.exit(main())
