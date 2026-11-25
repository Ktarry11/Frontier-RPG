"""The player's own difficulty: monster health and damage, 0.5x to 2x, for four kinds of place.

Kyle, 25 Nov 2026: "A way for my friend, or myself, to test some things out... a small box where the EXP bar is,
that opens a new menu. We can call it 'Difficulty' It will let the player, still have the EXP options but also
difficulty options. We can sort it by 'Open World' 'Dungeons' 'Skull Zones' 'Frontier Zones' -- They can adjust
either HP or Damage. Maybe have it like 0.5x, 0.75x, 1x, 1.25x, 1.5x, 1.75x, and 2x. HP and damage done seperately
and all 4 zones done seperately. This will allow him to play around and be like 'Hmmm, lvl 30 to 40 is too easy'."

It belongs to the save (Party.difficulty, written with the party, beside Party.xp_rate), so each character keeps
its own. It's applied last in world/difficulty.factor, on top of every row the game itself uses, so 1x everywhere
is exactly the game as tuned. Nothing outside a bound party ever sees it: the sims and balance tools never bind
one, or bind a fresh party that sits at 1x, so they always measure the real game.

WHICH PLACE a monster counts as (category()):
  skull     the one-skull hidden places (world/hidden_zones.py kinds "hidden_layer" and "skull_zone")
  frontier  the two-skull ones ("frontier_deep", "frontier_open")
  dungeon   a five-player dungeon's bosses and trash, and every heroic run
  open      everything else: the open world, its rares, and the small caves
"""
STEPS = (0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0)
DEFAULT = 1.0
CATEGORIES = (("open", "Open World"), ("dungeon", "Dungeons"), ("skull", "Skull Zones"),
              ("frontier", "Frontier Zones"))
WHATS = (("health", "Monster health"), ("damage", "Monster damage"))

_PARTY = None


def bind(party):
    """The party whose settings count (entities/party.py binds itself when it's made)."""
    global _PARTY
    _PARTY = party


def fresh():
    return {c: {w: DEFAULT for w, _ in WHATS} for c, _ in CATEGORIES}


def clean(data):
    """A saved table, with anything missing or not one of the steps put back to 1x."""
    out = fresh()
    for c, _ in CATEGORIES:
        row = (data or {}).get(c) if isinstance(data, dict) else None
        for w, _ in WHATS:
            v = (row or {}).get(w, DEFAULT) if isinstance(row, dict) else DEFAULT
            out[c][w] = v if v in STEPS else DEFAULT
    return out


def get(cat, what):
    table = getattr(_PARTY, "difficulty", None) if _PARTY is not None else None
    if not table:
        return DEFAULT
    v = (table.get(cat) or {}).get(what, DEFAULT)
    return v if v in STEPS else DEFAULT


def set_step(party, cat, what, value):
    if value not in STEPS or cat not in dict(CATEGORIES) or what not in dict(WHATS):
        return False
    if not getattr(party, "difficulty", None):
        party.difficulty = fresh()
    party.difficulty.setdefault(cat, {})[what] = value
    return True


def reset(party):
    party.difficulty = fresh()


def is_default():
    return all(get(c, w) == DEFAULT for c, _ in CATEGORIES for w, _ in WHATS)


def category(monster):
    """Which of the four places this monster counts as (see the module docstring)."""
    from world.difficulty import kind_of
    k = kind_of(monster)
    if k in ("hidden_layer", "skull_zone"):
        return "skull"
    if k and k.startswith("frontier"):
        return "frontier"
    if getattr(monster, "_heroic", False) or k in ("boss", "tuned_boss"):
        return "dungeon"
    zone = getattr(monster, "spawn_zone", None)
    if zone:
        from world.zone_classification import DUNGEONS
        if zone in DUNGEONS:
            return "dungeon"
    return "open"


def multiplier(monster, what):
    if _PARTY is None:
        return DEFAULT
    return get(category(monster), what)


def label(v):
    return f"{v:g}x"
