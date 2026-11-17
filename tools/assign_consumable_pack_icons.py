#!/usr/bin/env python3
"""Give the 16 Nov 2026 cooking, alchemy and engineering consumables (and the eggs) their own art from Kyle's icon pack.

    PYTHONPATH=. python3 tools/assign_consumable_pack_icons.py --pack "/path/to/unzipped/wowiconpack" [--apply]

Kyle, 16 Nov 2026: "You should have a lot of additional food icons and reagent icons in the icon list". The new
consumables started on copies of the nearest existing icon (tools/build_crafting_expansion_nov16.py); this swaps each
for a pack icon nothing else in the game draws:

  * the pool is the pack's icons of the right kind, by file name (food for meals, beer, milk, tea and wine for
    drinks, potions and flasks for alchemy, bombs, gizmos and shot for engineering, eggs for eggs);
  * an icon already in the game, under any name, is skipped (matched by a small fingerprint of the picture);
  * an alchemy potion takes the bottle nearest its colour (Might red, Grace green, Clarity blue, ...);
  * the pick is seeded on the item's id, so the same pack gives the same icons.

Without --apply it prints what it would do. The files land at assets/icons/consumables/<id>.png (96 px) and
assets/gathering_nodes/meat/<egg>.png (64 px), where the game already looks.
"""
import argparse
import colorsys
import functools
import hashlib
import json
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
TAG = "16 Nov 2026 crafting"

#: words a file name has to contain (matched whole, after splitting the name into words)
POOLS = {
    "meal": "food steak steaks sausage bread cheese pie soup stew mushroom fruit pumpkin apple ribs kabob skewer "
            "cake cookie pear melon corn carrot chicken ham bacon drumstick omelet biscuit muffin dumpling roast "
            "flatbread caribou talbuksteak goulash chowder",
    "drink": "beer milk tea honeytea wine drink mead cider juice rum whiskey ale mug firedrink goatsmilk "
             "coffee brew",
    "potion": "potion elixir flask vial endlessflask",
    "explosive": "bomb explosive grenade dynamite charge",
    "gadget": "gizmo gear gears gadget engineering spanner wrench scope device gyro",
    "ammo": "bullet bullets gunpowder",
    "egg": "egg",
}
PREFER = {"skewers": "kabob skewer steak", "stew": "stew soup goulash", "pie": "pie bread flatbread",
          "ribs": "ribs steak ham drumstick roast", "omelette": "omelet cheese bread",
          "chowder": "soup chowder stew", "tea": "tea honeytea milk", "cider": "cider juice drink",
          "mead": "mead beer ale mug brew", "wine": "wine", "infusion": "tea drink milk",
          "flask": "flask endlessflask"}


def words(stem):
    """'INV_Misc_Food_14' -> {'inv', 'misc', 'food'}; 'NewGoggles' -> {'new', 'goggles', 'newgoggles'}."""
    parts = re.split(r"[_\-\s]+|\d+", stem)
    out = set()
    for part in parts:
        if not part:
            continue
        out.add(part.lower())
        out |= {w.lower() for w in re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])", part)}
    return out


def has(stem, vocab):
    return bool(words(stem) & set(vocab.split()))


#: an alchemy family's colour (r, g, b)
COLOUR = {"might": (200, 40, 40), "grace": (60, 180, 60), "clarity": (60, 110, 220), "fury": (230, 120, 30),
          "sorcery": (150, 60, 200), "vigor": (220, 190, 50), "calm": (60, 200, 210), "mending": (240, 150, 190),
          "healing": (210, 30, 40), "mana": (40, 80, 230), "fire": (230, 90, 20), "frost": (140, 200, 250),
          "nature": (90, 200, 60), "shadow": (110, 50, 150), "arcane": (210, 100, 230)}
EXCLUDE = re.compile(r"place|spell|abilit|armou?r|weapon|character|creature", re.I)


@functools.lru_cache(maxsize=None)
def fingerprint(path):
    try:
        im = Image.open(path).convert("RGB").resize((12, 12))
    except OSError:
        return None
    return bytes(c // 32 for px in im.getdata() for c in px)


@functools.lru_cache(maxsize=None)
def hue_of(path):
    im = Image.open(path).convert("RGB").resize((24, 24))
    r = g = b = n = 0
    for (pr, pg, pb) in im.getdata():
        h, s, v = colorsys.rgb_to_hsv(pr / 255, pg / 255, pb / 255)
        if s > 0.45 and v > 0.35:
            r, g, b, n = r + pr, g + pg, b + pb, n + 1
    return (r / n, g / n, b / n) if n else (128, 128, 128)


def dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def wants(c):
    """-> (pool, preferred words or None, colour or None) for a new consumable."""
    cid, kind = c["consumable_id"], c["consumable_type"]
    if kind == "meal":
        key = cid.split("_x16_")[1].rsplit("_", 1)[0]
        return "meal", PREFER.get(key), None
    if kind == "drink":
        key = cid.split("_x16_")[1].rsplit("_", 1)[0]
        return "drink", PREFER.get(key), None
    if kind in ("elixir", "health_potion", "mana_potion"):
        if cid.startswith("flask_"):
            return "potion", PREFER["flask"], None
        if kind == "health_potion":
            return "potion", "potion", COLOUR["healing"]
        if kind == "mana_potion":
            return "potion", "potion", COLOUR["mana"]
        fam = cid.split("_x16_")[1].split("_")[0]
        return "potion", None, COLOUR.get(fam)
    return {"explosive": "explosive", "gadget": "gadget", "ammo": "ammo"}[kind], None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", required=True)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    pack = [p for p in Path(a.pack).rglob("*.png") if not EXCLUDE.search(str(p.parent.name))]
    cons = json.loads((ROOT / "data/consumables/consumable_types.json").read_text(encoding="utf-8"))
    new = [c for lst in cons.values() if isinstance(lst, list) for c in lst
           if str(c.get("_source", "")).startswith(TAG)]
    own = {f"{c['consumable_id']}.png" for c in new}
    # every picture already in the game, except the stand-ins this replaces
    in_game = set()
    for p in list((ROOT / "assets/icons").rglob("*.png")) + list((ROOT / "assets/gathering_nodes").rglob("*.png")):
        if p.name in own or p.name.startswith("egg_"):
            continue
        fp = fingerprint(p)
        if fp:
            in_game.add(fp)
    taken = set()
    plan = []

    def choose(cid, pool, prefer, colour):
        cands = [p for p in pack if has(p.stem, POOLS[pool]) and p not in taken]
        cands = [p for p in cands if fingerprint(p) not in in_game]
        if prefer:
            better = [p for p in cands if has(p.stem, prefer)]
            cands = better or cands
        if not cands:
            return None

        def key(p):
            h = hashlib.sha1(f"{cid}:{p.name}".encode()).hexdigest()
            return (dist(hue_of(p), colour) if colour else 0, h)
        best = min(cands, key=key)
        taken.add(best)
        in_game.add(fingerprint(best))
        return best

    for c in sorted(new, key=lambda c: c["consumable_id"]):
        pool, prefer, colour = wants(c)
        got = choose(c["consumable_id"], pool, prefer, colour)
        if got:
            plan.append((got, ROOT / "assets/icons/consumables" / f"{c['consumable_id']}.png", 96))
    # the eggs by hand: a plain one, a speckled one and a big green-spotted one (the pack's other "eggs" are a
    # portal and a shadow orb)
    for egg, stem in (("egg_small", "INV_Egg_01"), ("egg_speckled", "INV_Egg_03"), ("egg_giant", "INV_Egg_02")):
        got = next((p for p in pack if p.stem == stem), None)
        if got:
            taken.add(got)
            plan.append((got, ROOT / "assets/gathering_nodes/meat" / f"{egg}.png", 64))
    short = len(new) + 3 - len(plan)
    print(f"{len(plan)} icons from the pack ({short} kept their stand-in: the pack ran short)")
    for src, dst, _ in plan[:8]:
        print(f"  {dst.name:44s} <- {src.name}")
    if a.apply:
        for src, dst, size in plan:
            Image.open(src).convert("RGBA").resize((size, size), Image.LANCZOS).save(dst)
        print("written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
