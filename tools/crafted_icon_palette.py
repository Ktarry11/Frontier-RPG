"""Crafted greens and blues borrow icons from the gear pack, picked to match their collection's colour.

Kyle, 15 Nov 2026: "You can shift some icons to use for crafting. Blues I don't much care about. For epics
we will use proper art."

Before this, a crafted piece took a seeded pick from its slot's pool, so a Felcloth robe could be any
colour at all and the five pieces of one collection looked like five different sets. Now:

  * Each piece gets a target colour from the words in its name (fel is fel-green, ember is red-orange,
    frost is icy blue, mithril is pale silver, iron is grey...), falling back to its armour (undyed cloth,
    brown leather, grey metal) when its name says nothing about colour.
  * Every pack icon is measured once: its main hue, how saturated and how bright it is.
  * The piece takes the icon nearest its colour. Within one collection an icon is never used twice,
    and across the game an icon already used costs a little more, so the pack spreads out.

EPICS are not handled here: they get their own art (gear_epic_crafted_<slug>.png). Until a piece's art
is sliced in, it keeps the epic pool's stand-in (see build_crafted_gear.icon_for).

Deterministic: same recipes in, same icons out.
"""
import colorsys
import math
import re
from functools import lru_cache

from PIL import Image

import gear_icons as GI

#: (keywords, (hue degrees, saturation, value)). First match in the NAME wins, so the order matters:
#: "Bloodiron" is blood before iron, "Frostpine" is frost before wood, "Deepearth" is earth before sea.
PALETTE = [
    (("fel",), (95, 0.70, 0.60)),
    (("plague", "venom", "putrid", "putresc", "rot", "brood", "virulent", "chitin", "carapace"), (75, 0.60, 0.45)),
    (("ember", "fire", "blaze", "flame", "scorch", "infernal", "charred", "soulscorch", "redbark"), (15, 0.75, 0.70)),
    (("frost", "rime", "ice", "winter", "skyglass"), (200, 0.45, 0.80)),
    (("blood", "scarlet", "heart", "crimson", "garnet", "carnelian"), (355, 0.70, 0.50)),
    (("void", "nether", "soul", "demon", "fiend", "shadow", "dusk", "night", "dark", "hex", "curse", "shroud",
      "black", "voodoo", "mojo", "fetish", "shade", "accursed"), (275, 0.50, 0.35)),
    (("gold", "gilded", "honey", "amber", "topaz", "citrine", "sun", "tigerseye", "radiant", "blessed"),
     (45, 0.70, 0.75)),
    (("moon", "silver", "star", "mithril", "truesilver", "arcane", "sky", "mystic", "spirit", "prism"),
     (220, 0.20, 0.80)),
    # before the sea words, so Deepearth is stone rather than sea
    (("iron", "tin", "steel", "thorium", "smelted", "rune", "stone", "earth", "crag", "forge", "scrap",
      "weakstone", "dredged", "bone"), (210, 0.12, 0.55)),
    (("tide", "sea", "deep", "brine", "storm", "aqua", "azur", "blue", "naga", "mist", "tidal", "serpent",
      "hydra", "undertow", "drift", "marsh", "gale", "wind", "salt", "coldwater"), (185, 0.55, 0.55)),
    (("jade", "verdant", "living", "moss", "grove", "leaf", "vine", "bramble", "thorn", "briar", "wild",
      "lifebark", "plains", "seed", "sap", "earthwalker", "druid"), (115, 0.50, 0.50)),
    (("copper",), (22, 0.60, 0.55)),
    (("bronze", "brass"), (35, 0.50, 0.50)),
    (("ash",), (30, 0.10, 0.45)),
    (("linen", "wool", "cotton", "hempen", "silk", "woven", "pilgrim", "traveler", "scribe", "healer"),
     (40, 0.20, 0.75)),
    (("wood", "bark", "pine", "oak", "willow", "tiki", "carved", "staff"), (30, 0.40, 0.45)),
]

#: when the name says nothing about colour
BY_ARMOUR = {"cloth": (40, 0.20, 0.75), "leather": (28, 0.45, 0.40), "mail": (210, 0.12, 0.55),
             "plate": (210, 0.12, 0.55)}
LEATHER_BROWN = (28, 0.45, 0.40)


#: collection words the keyword scan would read wrongly
OVERRIDE = {"ironbark": (30, 0.40, 0.45), "ironwood": (30, 0.40, 0.45), "deepearth": (210, 0.12, 0.55),
            "ironweald": (115, 0.50, 0.50)}


def target(name, armor_type=None):
    """The colour a piece should be: its collection word first ("Verdant Iron Belt" is verdant, not iron),
    then the rest of its name, else its armour."""
    first = name.split()[0].lower() if name else ""
    if first in OVERRIDE:
        return OVERRIDE[first]
    for text in (first, name.lower()):
        for words, colour in PALETTE:
            if any(w in text for w in words):
                return colour
    return BY_ARMOUR.get(armor_type, LEATHER_BROWN)


@lru_cache(maxsize=None)
def measure(icon_id):
    """(hue degrees, saturation, value) of an icon's visible pixels; hue is the saturation-weighted mean."""
    img = Image.open(GI.GEAR_ICON_DIR / f"{icon_id}.png").convert("RGBA").resize((32, 32))
    xs = ys = 0.0
    ss = vs = n = w = 0.0
    for r, g, b, a in img.getdata():
        if a < 128:
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


def distance(want, got):
    (ht, st, vt), (hi, si, vi) = want, got
    dh = abs(ht - hi) % 360
    dh = min(dh, 360 - dh) / 180
    # hue only matters as much as both are actually coloured
    return dh * 3.5 * min(st, si) + abs(st - si) + abs(vt - vi) * 0.7


def pool(slot, armor_type=None, weapon_type=None):
    """The ordinary pack icons for this kind of piece, exactly as gear_icons would choose from."""
    if weapon_type:
        prefixes = GI.WEAPON_ICON_PREFIXES.get(weapon_type)
    else:
        base = re.sub(r"\d+$", "", slot or "")
        prefixes = GI.ARMOR_ICON_PREFIXES.get((base, armor_type)) or GI.ARMOR_ICON_PREFIXES.get((base, None))
    return sorted(GI._icons_for_prefixes(prefixes)) if prefixes else []


class Picker:
    """Hands out icons across one build: no repeats inside a collection, and a light cost for reuse."""

    REUSE_COST = 0.06

    def __init__(self):
        self.used = {}          # icon -> times used across the game
        self.by_set = {}        # collection -> icons it already has

    def pick(self, name, slot, armor_type=None, weapon_type=None):
        cands = pool(slot, armor_type, weapon_type)
        if not cands:
            return None
        collection = name.split()[0].lower()
        taken = self.by_set.setdefault(collection, set())
        want = target(name, armor_type)
        free = [c for c in cands if c not in taken] or cands
        best = min(free, key=lambda c: (distance(want, measure(c)) + self.REUSE_COST * self.used.get(c, 0), c))
        taken.add(best)
        self.used[best] = self.used.get(best, 0) + 1
        return best
