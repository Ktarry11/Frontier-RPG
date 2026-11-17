"""
Meat from beasts - the raw stock for Cooking.

Kyle, 2026-10-28: "i think we need to build the cooking system".

THIS IS THE SKINNING MODEL, DELIBERATELY. entities/skinning_drops.py already answers "which beast, at
which level, gives which tier of material", it already routes through entities/vendor_trash.classify
so a harpy counts as a person and a kodo does not, and that classification has been audited across all
871 creatures. Writing a second, subtly different answer to the same question is how a tauren ends up
being skinnable but not edible.

So meat uses the same classify() gate and the same level-banded tables, with two differences that are
real rather than cosmetic:

  * NO PROFESSION GATE. Skinning requires the profession; meat does not. Anyone can take the meat off a
    boar - you need Cooking to do anything WITH it, which is where the skill belongs. A cooking
    profession nobody can start because they never learned to pick up ingredients is a dead profession.
  * IT DOES NOT ALWAYS DROP. Leather is a guaranteed 1 per beast. Meat is a chance, because otherwise
    every single beast kill in the game adds an inventory line and the bags fill with pork.

EIGHT TIERS now, matching the cooked-meal tiers in data/consumables (and the five vendor meals they
improve on). More tiers than there are recipes to use them is exactly the dead-material problem this
pass exists to fix.
"""
import random
import re

from entities.vendor_trash import classify

#: Only things that are made of meat. Same family vocabulary classify() returns.
EDIBLE = {"beast"}

#: (min_level, max_level, {material_id: weight}). Overlapping bands on purpose, same as leather:
#: a tier fades in while the one below fades out, so no level is a hard wall.
BANDS = [
    (1,  12, {"meat_stringy": 4}),
    (8,  20, {"meat_stringy": 2, "meat_lean": 3}),
    (16, 30, {"meat_lean": 3, "meat_thick": 2}),
    (24, 38, {"meat_lean": 1, "meat_thick": 3, "meat_rich": 1}),
    (32, 46, {"meat_thick": 2, "meat_rich": 3, "meat_prime": 1}),
    (40, 99, {"meat_rich": 2, "meat_prime": 3}),
    (38, 48, {"meat_prime": 3, "meat_marbled": 2}),
    (44, 52, {"meat_prime": 1, "meat_marbled": 3, "meat_aged": 2}),
    (48, 99, {"meat_marbled": 1, "meat_aged": 3, "meat_select": 2}),
]

#: Chance a normal beast yields meat at all. Low enough that bags do not fill, high enough that a
#: player who decides to go cooking can get what they need in an evening.
DROP_CHANCE = 0.35

#: A boss is a lot of animal.
BOSS_QTY = (3, 5)


#: EGGS (Kyle, 16 Nov 2026: "Having more meat or items drop from animal mobs from 1 to 60....eggs from birds").
#: Anything that lays them - birds, raptors, crocolisks, basilisks, serpents, plainstriders - can leave one, on
#: top of its meat. Matched on the creature's name, the same way classify() reads a family off it.
LAYS_EGGS = re.compile(r"vulture|hawk|\bowls?\b|buzzard|condor|\bcrows?\b|raven|eagle|falcon|carrion bird|"
                       r"strider|chicken|turkey|rooster|\bhens?\b|gull|parrot|\brocs?\b|shrike|raptor|"
                       r"crocolisk|basilisk|serpent|turtle|tortoise|thunder lizard|wind rider|cockatrice", re.I)
EGG_BANDS = [
    (1, 26, {"egg_small": 1}),
    (18, 46, {"egg_speckled": 1}),
    (38, 99, {"egg_giant": 1}),
]
EGG_CHANCE = 0.25


def lays_eggs(name):
    return bool(LAYS_EGGS.search(name or ""))


def _pick(level, rng, bands=None):
    pool = {}
    for lo, hi, weights in (bands or BANDS):
        if lo <= level <= hi:
            for mat, w in weights.items():
                pool[mat] = pool.get(mat, 0.0) + w
    if not pool:
        return "meat_prime" if level >= 40 else "meat_stringy"
    return rng.choices(list(pool), weights=list(pool.values()), k=1)[0]


def roll_meat(enemy, player=None, rng=random):
    """[(material_id, quantity)] from a defeated beast. No profession needed to pick it up.

    `player` is accepted and ignored, so this can be called from the same place as roll_leather
    without the caller having to remember which of the two gates on a profession.
    """
    name = getattr(enemy, "name", "")
    family, _coin = classify(name, getattr(enemy, "template", None))
    if family not in EDIBLE:
        return []

    level = max(1, int(getattr(enemy, "level", 1)))
    got = []
    if getattr(enemy, "is_boss", False):
        got.append((_pick(level, rng), rng.randint(*BOSS_QTY)))
    elif rng.random() <= DROP_CHANCE:
        got.append((_pick(level, rng), 1))
    if lays_eggs(name) and (getattr(enemy, "is_boss", False) or rng.random() <= EGG_CHANCE):
        got.append((_pick(level, rng, EGG_BANDS), 2 if getattr(enemy, "is_boss", False) else 1))
    return got
