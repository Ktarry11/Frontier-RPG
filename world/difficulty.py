"""Global monster difficulty: one table, three kinds of place (data/balance/monster_difficulty.json).

Kyle, 14 Nov 2026: "I want Dungeons to NEED a group of 5 and open world should still have danger to
it.....not tank and spanking Everything mindlessly."

WHY ONE TABLE AND NOT 1,200 KITS. Measured with tools/sim_difficulty.py the same evening: a geared
player lost about a fifth of their health to a same-level creature in every band from 10 to 54,
and a party of three beat most dungeon bosses with nobody dying. That is not one creature tuned
wrong, it is the whole curve sitting low, so it is corrected where the curve is applied rather
than in every kit, and it can be turned back by editing three pairs of numbers.

  open   anything met in the open world
  cave   trash in a cave or dungeon (cave_spawns tags it)
  boss   a boss of a real five-player dungeon (world/zone_classification.DUNGEONS)
  field_boss  every other boss: the named one at the back of a small cave. Kyle, 14 Nov, after a friend at level 17 met Tidelord Gharesh in the Echo Isles grotto
         with 5,700 health: "it shouldn't be that high." Then: "keep Dungeons around 3x health and
         3x damage... He did it with 2 people. So why the fuck not." Both kinds are 3x/3x today;
         they are separate keys so they can be split again.
  tuned_boss  a boss whose kit was already tuned by hand against the sim (the Tempest Isle
         dungeons and the Royal Hive), named in the table's "tuned_bosses" list
  hidden_layer / skull_zone  every monster, trash and boss alike, in a hidden level under a dungeon
         or a hidden open-world map (world/hidden_zones.py). These rows also carry
         loot_ilvl_bonus: what they drop sits that many item levels above them.

  rare        a named creature in the open world, not in a cave (Kyle, 19 Nov 2026: "split the rares from boss and
         tune the difficulty", "rares should be around 75-90% win rate"). Its own row, with by_level steps, tuned with
         tools/sim_campaign.py's rare census. It replaced the early_rare damper, which softened field bosses outside
         caves under 45 but left them on the dungeon-boss 3x row.

  low_level  not a kind: a multiplier on top of whichever row applies, for every creature under
         level 10 (Kyle, 16 Nov 2026: 20% less damage, 15% less health).

Damage is a multiplier on what the monster deals (Monster.damage_output_multiplier); health is
applied once, when the creature is made.
"""
import json
from functools import lru_cache
from pathlib import Path

_PATH = Path(__file__).resolve().parent.parent / "data" / "balance" / "monster_difficulty.json"


@lru_cache(maxsize=1)
def table():
    try:
        return json.loads(_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


@lru_cache(maxsize=1)
def _tuned():
    return frozenset(table().get("tuned_bosses") or ())


@lru_cache(maxsize=1)
def dungeon_bosses():
    """The bosses that appear in a real dungeon's encounter table (data/creatures/encounters.json)."""
    from world.zone_classification import DUNGEONS
    root = Path(__file__).resolve().parent.parent / "data" / "creatures"
    try:
        enc = json.loads((root / "encounters.json").read_text(encoding="utf-8"))
        cre = json.loads((root / "creatures.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return frozenset()
    cre = cre.get("creatures", cre)
    found = {}

    def walk(node, key):
        if isinstance(node, dict):
            if isinstance(node.get("creatures"), dict):
                found.setdefault(node.get("name") or key, set()).update(node["creatures"])
            for k, v in node.items():
                walk(v, k)
    walk(enc, None)
    wanted = set(DUNGEONS)
    return frozenset(c for zone, names in found.items() if zone in wanted
                     for c in names if (cre.get(c) or {}).get("is_boss"))


def kind_of(monster):
    from world.hidden_zones import creature_kinds
    hidden = creature_kinds().get(getattr(monster, "name", None))
    if hidden:
        return hidden
    if getattr(monster, "is_boss", False):
        name = getattr(monster, "name", None)
        if name in _tuned():
            return "tuned_boss"
        if name in dungeon_bosses():
            return "boss"
        # AN OPEN-WORLD RARE is its own kind (Kyle, 19 Nov 2026: "split the rares from boss and tune the difficulty",
        # "rares should be around 75-90% win rate... Some rares would fucking clap you so hard.... but most were
        # soloable"). The same creature standing in a cave is still a field boss.
        return "field_boss" if getattr(monster, "location_type", None) == "cave" else "rare"
    return "cave" if getattr(monster, "location_type", None) == "cave" else "open"


_BOSS_DAMAGE = None
BOSS_DAMAGE_KINDS = ("boss", "tuned_boss", "field_boss", "rare")


def boss_damage(name):
    """A boss's own damage factor, putting its average action on the healing formula's reference
    (data/balance/boss_damage.json, tools/calibrate_boss_damage.py; Kyle 16 Nov 2026: "Yes that's fine to drop
    bosses a bit to account for it"). 1.0 for a boss it hasn't measured, or with FRONTIER_BOSS_DAMAGE=off."""
    global _BOSS_DAMAGE
    if _BOSS_DAMAGE is None:
        import os
        if os.environ.get("FRONTIER_BOSS_DAMAGE", "").lower() == "off":
            _BOSS_DAMAGE = {}
        else:
            try:
                _BOSS_DAMAGE = json.loads((_PATH.parent / "boss_damage.json").read_text(encoding="utf-8")).get(
                    "bosses") or {}
            except (OSError, ValueError):
                _BOSS_DAMAGE = {}
    return float(_BOSS_DAMAGE.get(name, 1.0))


_RARE_TUNE = None


def rare_tune(name):
    """An open-world rare's own damage factor, on top of the rare row and its boss_damage factor
    (data/balance/rare_tune.json, tools/tune_rares.py). Kyle, 19 Nov 2026: "rares should be around 75-90% win rate...
    Some rares would fucking clap you so hard.... but most were soloable"; 20 Nov: "Fix that next", the census's rares
    that one class couldn't beat. Fitted per rare against a Protection Warrior, a Holy Priest and a Fire Mage at the
    rare's level, so no class is hard-countered and none walks through it. 1.0 for an unfitted rare, or with
    FRONTIER_RARE_TUNE=off (what the tool measures under)."""
    global _RARE_TUNE
    if _RARE_TUNE is None:
        import os
        if os.environ.get("FRONTIER_RARE_TUNE", "").lower() == "off":
            _RARE_TUNE = {}
        else:
            try:
                _RARE_TUNE = json.loads((_PATH.parent / "rare_tune.json").read_text(encoding="utf-8")).get(
                    "rares") or {}
            except (OSError, ValueError):
                _RARE_TUNE = {}
    return float(_RARE_TUNE.get(name, 1.0))


def factor(monster, what):
    f = float((table().get(kind_of(monster)) or {}).get(what, 1.0))
    if what == "damage" and kind_of(monster) == "rare":
        f *= rare_tune(getattr(monster, "name", None))
    # Hidden places keep their own rows (qa_hidden_zones holds them to it): they are brutal on purpose, so only the
    # dungeon and field bosses come onto the healing formula's reference.
    if what == "damage" and getattr(monster, "is_boss", False) and kind_of(monster) in BOSS_DAMAGE_KINDS:
        f *= boss_damage(getattr(monster, "name", None))
    # THE FIRST TEN LEVELS (Kyle, 16 Nov 2026: "tone down the difficulty before lvl 10 by about 20% overall.
    # Any enemies below lvl 10 should deal 20% less damage and have 15% less HP"): on top of the row above,
    # whatever kind of creature it is.
    # A HEROIC (world/heroic.py, Kyle 18 Nov 2026: "Level 60 elites"): every monster in a heroic run is level 60, and
    # elite on top of whatever row it already has.
    if getattr(monster, "_heroic", False):
        f *= float((table().get("heroic") or {}).get(what, 1.0))
    low = table().get("low_level") or {}
    if (getattr(monster, "level", 99) or 99) < int(low.get("below_level", 0)):
        f *= float(low.get(what, 1.0))
    # A WHOLE ZONE TUNED (Kyle, 23 Nov 2026: "Deathknell is overtuned, drop whole zone damage by 15% and HP by 10%"):
    # the table's "zones" rows, on top of everything above, for every creature that spawns in the zone or in one of
    # the caves its row "includes".
    f *= zone_factor(getattr(monster, "spawn_zone", None), what)
    # A ROW THAT CHANGES WITH LEVEL: "by_level" is [[level, health, damage], ...], read straight between its points
    # and flat past either end, on top of the row's own numbers (the rare row, tuned with tools/sim_campaign.py's
    # rare census so every level band lands in Kyle's 75-90%).
    steps = (table().get(kind_of(monster)) or {}).get("by_level")
    if steps:
        f *= _by_level(steps, getattr(monster, "level", 1) or 1, 1 if what == "health" else 2)
    # LATE DUNGEON BOSSES HIT HARDER (Kyle, 16 Nov 2026: "i can 2 man dungeons without any issues"; "Both, a little
    # each"). On top of the boss row, a dungeon boss's damage climbs from its from_level to full_level, so the big
    # dungeons near 60 need the group they're built for and the early ones stay as they were.
    late = table().get("endgame_boss") or {}
    if what in late and kind_of(monster) in (late.get("kinds") or ()) \
            and getattr(monster, "name", None) not in (late.get("except") or ()):
        lv = getattr(monster, "level", 1) or 1
        lo, hi = int(late.get("from_level", 30)), int(late.get("full_level", 50))
        k = min(1.0, max(0.0, (lv - lo) / max(1, hi - lo)))
        f *= 1.0 + (float(late[what]) - 1.0) * k
    return f


@lru_cache(maxsize=1)
def _zone_rows():
    out = {}
    for name, row in (table().get("zones") or {}).items():
        if name.startswith("_") or not isinstance(row, dict):
            continue
        for z in [name] + list(row.get("includes") or ()):
            out[z] = row
    return out


def zone_factor(zone, what):
    """The "zones" row's multiplier for a creature that spawned in this zone (or one of its caves), 1.0 elsewhere."""
    if not zone:
        return 1.0
    return float((_zone_rows().get(zone) or {}).get(what, 1.0))


def _by_level(steps, level, col):
    pts = sorted(steps)
    if level <= pts[0][0]:
        return float(pts[0][col])
    for a, b in zip(pts, pts[1:]):
        if level <= b[0]:
            k = (level - a[0]) / max(1, b[0] - a[0])
            return float(a[col]) + (float(b[col]) - float(a[col])) * k
    return float(pts[-1][col])


def apply_health(monster):
    """Scale a freshly made monster's health for where it stands. Idempotent per monster."""
    old = getattr(monster, "_difficulty_health", 1.0)
    new = factor(monster, "health")
    # Idempotent on the factor itself, not just the kind: a cave's own zone row (spawn_zone, set after the
    # creature is made) changes the factor without changing the kind.
    if getattr(monster, "_difficulty_kind", None) == kind_of(monster) and abs(new - old) < 1e-9:
        return
    monster.max_health = max(1, int(monster.max_health / old * new))
    monster.current_health = monster.max_health
    monster._difficulty_health = new
    monster._difficulty_kind = kind_of(monster)
    row = table().get(monster._difficulty_kind) or {}
    monster.loot_ilvl_bonus = int(row.get("loot_ilvl_bonus", 0))
    monster.loot_epic_chance = float(row.get("trash_epic_chance", 0.0))
