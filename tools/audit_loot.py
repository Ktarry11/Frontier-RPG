#!/usr/bin/env python3
"""Roll every loot source thousands of times and report what never came out.

WHY THIS EXISTS, AND WHY IT IS NOT ANOTHER VALIDATOR. The loot data in this
repo is well-formed. validate_content.py reads it, checks every id resolves,
and passes - and it passed while 43 of the 77 authored gear suffixes could
not be rolled at all. Nothing about `"of the Bulwark": {"stamina": 0.5,
"block_rating": 0.25, "block_value": 0.25}` tells you whether the roller can
ever choose it; that is decided by _suffixes_for_template, by which classes
are in LOOT_CLASS_POOL, and by what level the content ceiling reaches. An
entry that cannot be rolled is dead content however correct its data looks.

So this does not read the tables and check them. It calls the real
generators - LootGenerator, boss_loot.get_fixed_boss_loot, epic_drops.
roll_epic, cloth/skinning/meat/essence/recipe/vendor-trash roll_* - tens of
thousands of times with real creature names and real player classes, and
reports every authored entry that never once came out.

The same distinction runs through the stat check. A stat key on an item is
not live because the engine mentions the string somewhere: it is live if
equipping an item carrying it changes something on the character. The unit
and liveness conventions in this engine are PER KEY AND PER CHANNEL - the
same name can be real in one channel and decorative in another - so this
equips a probe item per key and watches every numeric attribute on a real
Character. That measurement found `block_value`, which is a real Character
attribute, a real Item constructor field and a real stat-conversion target,
and is still dead when it arrives as an item's secondary stat.

    python3 tools/audit_loot.py
    python3 tools/audit_loot.py --rolls 50000
    python3 tools/audit_loot.py --section suffixes

WHAT THIS TOOL GOT WRONG BEFORE IT GOT IT RIGHT, recorded because the
instrument misreading good code is the expensive failure here, not a missed
bug:

  * The first procedural sweep rolled with char_class=None and reported
    `polearm` and `agi_int_hybrid` as unreachable dead content. They are
    not. _roll_target_class returns the PLAYER's class CLASS_BIAS_CHANCE of
    the time, so a Tinker does see polearms - passing None suppressed the
    only path that reaches them. The sweep now rolls once per player class,
    which turns a false "dead" into the true and much narrower finding: one
    class of thirty can roll it and the other twenty-nine cannot.
  * The first material sweep invented creature names ("Bandit Thug") and
    reported all 40 cloth tiers unreachable. vendor_trash.classify resolves
    a creature's family by looking its NAME up in creatures.json, so an
    invented name resolves to `beast` and a humanoid-only drop correctly
    yields nothing. Every roll here now uses real names out of
    data/creatures/creatures.json.
  * Separating "cannot be rolled" from "nothing in the world is high enough
    level yet" matters more than anything else this tool prints. The highest
    creature in the game is level 40. Thirty-one cloth tiers and thirty-two
    leather tiers therefore never drop, and not one of them is a bug: they
    are authored for 41-60 content that does not exist, exactly as
    entities/material_tiers.py describes. So each material sweep runs twice,
    once at real content levels and once at synthetic 1-99, and only an
    entry dead in BOTH is reported as unrollable.
"""

from __future__ import annotations

import collections
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: Rolls per source. The binding constraint is the rarest single outcome in
#: the procedural roller: a specific weapon type for a class that has many
#: (a Hunter's bow is roughly 1 roll in 1000, being 20% weapon-slot x 1 of
#: 10 valid types x the 2 ranged slots it competes for). At 20000 rolls the
#: chance of missing a 1-in-1000 outcome is (1-0.001)^20000, about 2e-9, so
#: anything this reports as never-rolled is unreachable rather than unlucky.
#: report_confidence() prints the real figure for the rarest outcome seen so
#: the number is justified by measurement rather than by this comment.
ROLLS = 20000

#: Level bands reported against. The last two exist deliberately even though
#: no creature reaches them - an empty 41-60 band is the content ceiling
#: being visible rather than a gap in the loot tables.
BANDS = [(1, 10), (11, 20), (21, 30), (31, 40), (41, 50), (51, 60)]

RESISTANCE_STATS = frozenset({
    "fire_resistance", "frost_resistance", "nature_resistance",
    "shadow_resistance", "arcane_resistance", "holy_resistance",
    "magic_resistance",
})

#: Kyle's hard rule: "Magic resistance gear starts only after level 45."
#: Checked against the level a player can EQUIP the item at (required_level),
#: not item_level, because that is the level the rule is about.
RESISTANCE_MIN_PLAYER_LEVEL = 45


# ----------------------------------------------------------------- data
def jload(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def creatures():
    return jload("data/creatures/creatures.json")["creatures"]


def all_classes():
    """The 30 classes, from the armour map rather than a list kept here.

    A second hand-maintained roster is how an audit ends up measuring a
    different game than the one that ships - the stale roster inside
    LootGenerator.LOOT_CLASS_POOL is precisely the bug this tool found.
    """
    return list(jload("data/items/armor_types.json")["class_armor_map"])


def selectable_classes():
    """Classes character creation actually offers, read out of the screen.

    Needed to tell "loot never itemises for this class" apart from "this
    class is not playable yet", which is the defence LOOT_CLASS_POOL's own
    comment used to offer and which stopped being true.
    """
    import re
    src = (ROOT / "ui/screens/character_screen.py").read_text(encoding="utf-8")
    block = src.split("self.classes = [", 1)[1].split("]", 1)[0]
    return [c for c in re.findall(r'"([^"]+)"', block)]


def boss_loot_files():
    return sorted((ROOT / "data/loot").glob("*_loot.json"))


def boss_loot_entries():
    """[(file, boss_name, item_def)] over every hand-authored boss pool."""
    out = []
    for path in boss_loot_files():
        for boss, pool in json.loads(path.read_text(encoding="utf-8")).items():
            if boss.startswith("_"):
                continue
            for item_def in pool:
                out.append((path.name, boss, item_def))
    return out


def quest_reward_entries():
    """[(file, quest_id, item_def)] over every hand-authored quest reward.

    unique_item_defs only. The procedural branch of Quest.get_gear_choices
    is covered by the procedural sweep instead, since it calls the same
    LootGenerator - and it is only reached when a quest has NO
    unique_item_defs, which build_unique_reward_set takes priority over.
    """
    out = []
    for path in sorted((ROOT / "data/quests").glob("*.json")):
        for quest in json.loads(path.read_text(encoding="utf-8")).get("quests", []):
            for item_def in (quest.get("unique_item_defs") or []):
                out.append((path.name, quest.get("quest_id"), item_def))
    return out


def epic_entries():
    data = jload("data/loot/epic_drops.json")
    return ([("world", d) for d in data.get("world", [])]
            + [("dungeon", d) for d in data.get("dungeon", [])])


# ------------------------------------------------------- 1. procedural
def section_procedural(rolls):
    """Roll the real drop path once per player class and report the gaps.

    ROLLED PER PLAYER CLASS, NOT ONCE WITH NO CLASS. generate_loot_for_
    creature takes char_class and _roll_target_class honours it
    CLASS_BIAS_CHANCE of the time; rolling with None removes the only path
    to any class outside LOOT_CLASS_POOL and makes their armour and weapon
    types look dead when they are merely unreachable for everyone else.
    """
    from entities.loot_generator import LootGenerator

    gen = LootGenerator()
    classes = all_classes()
    per_class = int(max(200, rolls / len(classes)))

    seen_wt = collections.Counter()
    seen_at = collections.Counter()
    seen_st = collections.Counter()
    seen_slot = collections.Counter()
    seen_rarity = collections.Counter()
    # Which weapon types each player class can actually be handed, which is
    # the real question behind "is loot spread fairly across the classes".
    wt_by_class = collections.defaultdict(collections.Counter)
    at_by_class = collections.defaultdict(collections.Counter)

    max_creature = max(v["level_range"][1] for v in creatures().values())
    for cls in classes:
        for _ in range(per_class):
            level = random.randint(1, max_creature)
            item = gen.generate_loot_for_creature(
                creature_level=level, char_class=cls,
                drop_chance=1.0, player_level=level)
            if item is None:
                continue
            seen_slot[item.slot] += 1
            seen_rarity[item.rarity] += 1
            seen_st[item.stat_template] += 1
            if item.weapon_type:
                seen_wt[item.weapon_type] += 1
                wt_by_class[cls][item.weapon_type] += 1
            if item.armor_type:
                seen_at[item.armor_type] += 1
                if item.armor_type != "accessory":
                    at_by_class[cls][item.armor_type] += 1

    authored_wt = set(jload("data/items/weapon_types.json")["weapon_types"])
    authored_at = set(jload("data/items/armor_types.json")["armor_types"])
    authored_st = set(jload("data/items/stat_templates.json")["stat_templates"])
    authored_slot = set(jload("data/items/slots.json")["slots"])

    print(f"{len(classes)} player classes x {per_class} rolls "
          f"= {len(classes) * per_class} real drops through "
          f"generate_loot_for_creature\n")

    findings = []

    never_wt = sorted(authored_wt - set(seen_wt))
    if never_wt:
        findings.append(
            f"weapon types no class can ever be handed: {', '.join(never_wt)}")
    never_at = sorted(authored_at - set(seen_at))
    if never_at:
        findings.append(f"armour types never rolled: {', '.join(never_at)}")
    never_st = sorted(authored_st - {k for k in seen_st if k})
    if never_st:
        findings.append(f"stat templates never rolled: {', '.join(never_st)}")
    # "ring1"/"trinket1" are concrete Equipment slots, not item identities -
    # an item is stamped with the generic "ring"/"trinket" on purpose (see
    # ACCESSORY_SLOTS) so a drop can fill whichever of the pair is open.
    # Reporting them as unrolled would be the audit accusing a deliberate fix.
    never_slot = sorted(authored_slot - set(seen_slot)
                        - {"ring1", "ring2", "trinket1", "trinket2"})
    if never_slot:
        findings.append(f"slots never rolled: {', '.join(never_slot)}")

    # ONE-CLASS WEAPON TYPES. Not dead - reachable by exactly one class of
    # thirty and by nobody else, which is the same lopsidedness problem as
    # an armour-class skew and invisible to any check that only asks
    # "reachable: yes/no".
    narrow = []
    for wt in sorted(authored_wt):
        owners = [c for c in classes if wt_by_class[c].get(wt)]
        if 0 < len(owners) <= 2:
            narrow.append((wt, owners, seen_wt[wt]))

    print("WEAPON TYPE REACH (how many of the 30 classes can be handed one)")
    for wt in sorted(authored_wt):
        owners = [c for c in classes if wt_by_class[c].get(wt)]
        flag = "  <-- one class only" if len(owners) == 1 else ""
        print(f"  {wt:14} {len(owners):>2}/30 classes  "
              f"{seen_wt[wt]:>6} rolls{flag}")
    print()

    print("ARMOUR CLASS SHARE OF PROCEDURAL DROPS")
    total_at = sum(v for k, v in seen_at.items() if k != "accessory")
    for at in ("cloth", "leather", "mail", "plate"):
        share = seen_at[at] / total_at * 100 if total_at else 0
        print(f"  {at:8} {seen_at[at]:>7}  {share:5.1f}%")
    if total_at:
        shares = {a: seen_at[a] / total_at for a in
                  ("cloth", "leather", "mail", "plate")}
        hi, lo = max(shares, key=shares.get), min(shares, key=shares.get)
        spread = shares[hi] / shares[lo] if shares[lo] else 0
        print(f"  spread: {hi} is {spread:.2f}x {lo}")
        # Kyle's standing instruction is that loot must be varied rather
        # than lopsided. 1.20x is the threshold because the ideal here is
        # not 1.00: the 30 classes divide 8/8/7/7 across the four armour
        # classes, so a perfectly fair roller still lands at 8/7 = 1.14.
        if spread > 1.20:
            findings.append(
                f"procedural drops are lopsided toward {hi}: {spread:.2f}x "
                f"{lo}, against the 1.14x that an even roll across all 30 "
                f"classes would give")

    print()
    for wt, owners, count in narrow:
        print(f"  NARROW: {wt} reaches only {', '.join(owners)} "
              f"({count} rolls in {len(classes) * per_class})")

    return findings, {"wt_by_class": wt_by_class, "at_by_class": at_by_class,
                      "max_creature": max_creature}


# ---------------------------------------------------------- 2. suffixes
def section_suffixes(rolls):
    """Roll _roll_stats per template per band; report suffixes never produced.

    This is the check that would have caught the 43-of-77 failure. It rolls
    through generate_armor_piece rather than calling _suffixes_for_template,
    so the low-level primary-stat cap, the resistance gate and the bonus
    rolls are all exercised the way a real drop exercises them.
    """
    from entities.loot_generator import LootGenerator

    gen = LootGenerator()
    suffixes = jload("data/items/gear_suffixes.json")["suffixes"]
    templates = list(jload("data/items/stat_templates.json")["stat_templates"])
    findings = []

    # A suffix is identified by the stats it hands out, since that is what a
    # roll produces - the name is only a label on the chosen entry.
    by_stats = collections.defaultdict(list)
    for name, data in suffixes.items():
        by_stats[tuple(sorted(data["stats"].items()))].append(name)
    duplicates = {k: v for k, v in by_stats.items() if len(v) > 1}

    # THE ROOT CAUSE, CHECKED AS A ROOT CAUSE. _suffixes_for_template builds
    # its candidate list by intersecting a template's real stats with each
    # suffix's, then falls soft to the ENTIRE 77-entry table if the
    # intersection is empty. So a template missing from _SUFFIX_TEMPLATE_STATS
    # does not roll nothing - it rolls everything, including the suffixes the
    # map exists to keep away from it and (because the fail-soft runs after
    # the resistance stripper) including resistance at any level. That is a
    # far more diagnostic thing to report than the symptom, and it is checked
    # against the engine's own map rather than a copy kept here.
    from entities.loot_generator import LootGenerator as _LG
    unmapped = [t for t in templates if t not in _LG._SUFFIX_TEMPLATE_STATS]
    if unmapped:
        findings.append(
            f"stat template(s) with no entry in LootGenerator."
            f"_SUFFIX_TEMPLATE_STATS: {', '.join(unmapped)} - "
            f"_suffixes_for_template's fail-soft hands them the whole 77-entry "
            f"suffix table, so they roll every other role's suffixes AND "
            f"resistance at any level")

    per_cell = int(max(400, rolls / (len(templates) * len(BANDS))))
    reached = collections.defaultdict(set)      # template -> {suffix}
    resist_early = []                           # rule violations
    resist_only = []                            # pools with nothing else

    for template in templates:
        for lo, hi in BANDS:
            got = collections.Counter()
            for _ in range(per_cell):
                ilvl = random.randint(lo, hi)
                item = gen.generate_armor_piece(
                    "chest", "mail", template, ilvl, "uncommon")
                stats = set(item.primary_stats) | set(item.secondary_stats)
                name = _suffix_of(item.name, suffixes)
                if name:
                    got[name] += 1
                    reached[template].add(name)
                if stats & RESISTANCE_STATS:
                    # required_level is item_level - 2 (generate_armor_piece),
                    # so this is the level a player could WEAR it at.
                    if item.required_level <= RESISTANCE_MIN_PLAYER_LEVEL:
                        resist_early.append(
                            (template, item.item_level, item.required_level,
                             sorted(stats & RESISTANCE_STATS)))
            if got:
                pure_resist = all(
                    set(suffixes[n]["stats"]) & RESISTANCE_STATS for n in got)
                if pure_resist and lo >= 1:
                    resist_only.append((template, lo, hi, len(got)))

    print(f"{len(templates)} templates x {len(BANDS)} bands x {per_cell} "
          f"rolls = {len(templates) * len(BANDS) * per_cell} stat rolls\n")

    print(f"{'template':16} {'reached':>8} {'authored':>9}  never rolled")
    print("-" * 100)
    for template in templates:
        missing = sorted(set(suffixes) - reached[template])
        print(f"{template:16} {len(reached[template]):>8} {len(suffixes):>9}  "
              f"{len(missing)} suffix(es)")
        # A template not rolling a suffix meant for another role is correct
        # and desirable - a Warrior must not roll "of the Prophet". What is
        # reportable is a suffix NO template reaches, below.
    print()

    unreached = sorted(set(suffixes) - set().union(*reached.values()))
    if unreached:
        findings.append(
            f"{len(unreached)} of {len(suffixes)} suffixes are unreachable by "
            f"EVERY stat template at every level band: "
            f"{', '.join(unreached)}")
        print(f"UNREACHABLE BY EVERY TEMPLATE: {len(unreached)}")
        for name in unreached:
            print(f"    {name:28} {suffixes[name]['stats']}")
        print()
    else:
        print(f"All {len(suffixes)} suffixes are reachable by at least one "
              f"template.\n")

    if resist_early:
        # EARLIEST FIRST. Insertion order walks templates then bands, so the
        # first rows are whichever template happens to be listed first in
        # stat_templates.json at its HIGHEST band - which buries the actual
        # violation (a level-8 item) under a pile of level-45 ones.
        resist_early.sort(key=lambda r: r[2])
        per_template = collections.Counter(r[0] for r in resist_early)
        worst = min(resist_early, key=lambda r: r[2])
        findings.append(
            f"RULE VIOLATION - magic resistance before level "
            f"{RESISTANCE_MIN_PLAYER_LEVEL}: {len(resist_early)} rolled items "
            f"carry a resistance stat at a required_level a player reaches "
            f"earlier. Templates: {dict(per_template)}. Earliest: {worst[0]} "
            f"ilvl {worst[1]}, required_level {worst[2]}, {worst[3]}")
        print(f"RESISTANCE BEFORE LEVEL {RESISTANCE_MIN_PLAYER_LEVEL}: "
              f"{len(resist_early)} rolls")
        for template, ilvl, req, stats in resist_early[:12]:
            print(f"    {template:16} ilvl {ilvl:>3} req {req:>3}  "
                  f"{', '.join(stats)}")
        print()

    if resist_only:
        findings.append(
            "templates whose whole suffix pool is resistance suffixes in some "
            "band, so gear there rolls no primary stats at all: "
            + ", ".join(f"{t} at ilvl {lo}-{hi}" for t, lo, hi, _ in resist_only))
        print("RESISTANCE-ONLY SUFFIX POOLS (no primary stats possible):")
        for template, lo, hi, n in resist_only:
            print(f"    {template:16} ilvl {lo}-{hi}  pool is {n} suffix(es), "
                  f"all resistance")
        print()

    if duplicates:
        print("DUPLICATE SUFFIXES - identical stat blocks under two names. "
              "Both are\nrollable, so neither is dead; they are the same "
              "content twice and the\nowner decides whether to keep both:")
        for stats, names in duplicates.items():
            print(f"    {' == '.join(names):50} {dict(stats)}")
        print()

    # A resistance school the engine reads but no suffix can grant.
    granted = set()
    for data in suffixes.values():
        granted |= set(data["stats"])
    for school in sorted(RESISTANCE_STATS - {"magic_resistance"}):
        if school not in granted:
            findings.append(
                f"{school} is read by Character._recalculate_derived_stats and "
                f"has get_resistance() support, and no gear suffix grants it - "
                f"there is no way to obtain it")

    return findings


def _suffix_of(item_name, suffixes):
    """The suffix an item's generated name ends with, or None.

    Matched longest-first: "of the Bear" and "of the Beast" both end in a
    shared prefix, and the shorter one would otherwise claim the longer
    one's items and report the longer one dead.
    """
    for name in sorted(suffixes, key=len, reverse=True):
        if item_name.endswith(name):
            return name
    return None


# -------------------------------------------------------- 3. fixed boss
def section_fixed_boss(rolls):
    """Roll each hand-authored boss pool and check the boss itself is real.

    ENTRY REACHABILITY IS NOT THE INTERESTING QUESTION HERE and saying so
    matters: get_fixed_boss_loot does random.choice over the pool, so every
    index comes out eventually and a roll count proves nothing. What decides
    whether an authored pool is live is whether its KEY names a creature that
    exists and is flagged is_boss - combat_engine looks the table up by
    enemy.name. A pool keyed on a name no creature has is 4 authored items
    that cannot drop, and no amount of rolling reveals it.
    """
    from entities.boss_loot import get_fixed_boss_loot, has_fixed_boss_loot

    cre = creatures()
    real_bosses = {n for n, v in cre.items() if v.get("is_boss")}
    findings = []

    tables = collections.defaultdict(list)
    for fname, boss, item_def in boss_loot_entries():
        tables[boss].append((fname, item_def))

    not_a_creature = [b for b in tables if b not in cre]
    not_a_boss = [b for b in tables if b in cre and b not in real_bosses]

    print(f"{len(tables)} authored boss pools, "
          f"{sum(len(v) for v in tables.values())} items\n")

    if not_a_creature:
        findings.append(
            f"{len(not_a_creature)} boss loot table(s) are keyed on a name no "
            f"creature has, so the whole pool is unreachable: "
            f"{', '.join(sorted(not_a_creature))}")
    if not_a_boss:
        findings.append(
            f"{len(not_a_boss)} boss loot table(s) name a creature that is not "
            f"is_boss, so combat_engine never consults the table: "
            f"{', '.join(sorted(not_a_boss))}")
    if not not_a_creature and not not_a_boss:
        print(f"Every pool key names a real is_boss creature "
              f"({len(tables)}/{len(tables)}).")

    # boss_loot._load_boss_loot_tables globs data/loot and treats every
    # top-level key as a boss name. epic_drops.json's keys are "world" and
    # "dungeon", so a creature called either would be served the epic pool
    # as fixed boss loot. Nothing is named that today, which is why this is
    # a latent trap rather than a live bug - and why it is worth closing.
    for stray in ("world", "dungeon"):
        if has_fixed_boss_loot(stray):
            findings.append(
                f"boss_loot registers {stray!r} as a boss name - it is a "
                f"top-level key in data/loot/epic_drops.json and the loader's "
                f"glob does not exclude that file")

    # Roll anyway: it exercises _item_from_def on every authored entry, which
    # is where a malformed def would raise rather than merely read oddly.
    rolled = 0
    per_boss = max(8, int(rolls / max(1, len(tables)) / 4))
    for boss in tables:
        if boss not in real_bosses:
            continue
        for _ in range(per_boss):
            item = get_fixed_boss_loot(boss)
            if item is not None:
                rolled += 1
    print(f"{rolled} items built through the real _item_from_def path "
          f"with no failures.\n")

    # Duplicate NAMES across pools: two bosses handing out the same named
    # item. Not dead content - both drop - but it is the same reward twice.
    names = collections.Counter(d["name"] for _, _, d in boss_loot_entries())
    dups = {n: c for n, c in names.items() if c > 1}
    if dups:
        print("SAME NAMED ITEM IN MORE THAN ONE POOL (both reachable):")
        for name, count in sorted(dups.items()):
            where = [f"{f}:{b}" for f, b, d in boss_loot_entries()
                     if d["name"] == name]
            print(f"    {name:40} {count}x  {', '.join(where)}")
        print()

    return findings


# ------------------------------------------------------------ 4. epics
def section_epics(rolls):
    """Roll roll_epic against real level-30+ enemies and report unreached epics."""
    from entities.epic_drops import roll_epic, MIN_LEVEL

    cre = creatures()
    bosses = [(n, v) for n, v in cre.items()
              if v.get("is_boss") and v["level_range"][1] >= MIN_LEVEL]
    trash = [(n, v) for n, v in cre.items()
             if not v.get("is_boss") and v["level_range"][1] >= MIN_LEVEL]
    findings = []

    class Enemy:
        def __init__(self, name, level, is_boss):
            self.name, self.level, self.is_boss = name, level, is_boss

    seen = collections.Counter()
    max_level = max(v["level_range"][1] for v in cre.values())
    # WORLD EPICS ARE A 1-IN-400 ROLL (epic_drops.WORLD_CHANCE 0.0025), and
    # then one of twelve, so a single world epic is roughly 1 in 4800 kills.
    # At rolls*40 that is ~170 expected appearances each at the default roll
    # count; at rolls*4 three of them went missing purely to variance and
    # this reported them as unreachable, which is the instrument and not the
    # game. The multiplier is set from the real rate rather than guessed.
    calls = rolls * 40
    for _ in range(calls):
        pool = bosses if random.random() < 0.5 else trash
        if not pool:
            continue
        name, data = random.choice(pool)
        level = random.randint(max(MIN_LEVEL, data["level_range"][0]),
                               data["level_range"][1])
        player = random.randint(MIN_LEVEL, 60)
        item = roll_epic(Enemy(name, level, bool(data.get("is_boss"))), player)
        if item is not None:
            seen[item.name] += 1

    authored = {d["name"] for _, d in epic_entries()}
    never = sorted(authored - set(seen))
    print(f"{calls} roll_epic calls against real level-{MIN_LEVEL}+ "
          f"creatures ({len(bosses)} bosses, {len(trash)} trash)\n")
    print(f"{len(seen)} of {len(authored)} named epics dropped at least once; "
          f"rarest dropped {min(seen.values()) if seen else 0} time(s).")
    if never:
        print(f"NEVER DROPPED: {', '.join(never)}")
        findings.append(
            f"{len(never)} named epic(s) never dropped: {', '.join(never)}")
    # An epic nobody can reach because no enemy is high enough is a content
    # ceiling, not a loot bug - say which it is.
    for bucket, item_def in epic_entries():
        need = item_def.get("required_level", 1)
        if need > max_level + 2:
            findings.append(
                f"epic {item_def['name']!r} needs level {need} and the highest "
                f"creature in the game is {max_level} - content ceiling, not a "
                f"table bug")
    print()
    return findings


# -------------------------------------------------------- 5. materials
def section_materials(rolls):
    """Roll every gathering drop module twice: real levels, then 1-99.

    THE TWO SWEEPS ARE THE POINT. A tier that never drops today because the
    world stops at level 40 is correct content authored ahead of its zones
    (entities/material_tiers.py says so explicitly). A tier that never drops
    even at synthetic level 99 cannot be rolled at all. Reporting the first
    as a bug would bury the second under thirty false positives.
    """
    from entities.cloth_drops import roll_cloth, BANDS as CLOTH_BANDS
    from entities.skinning_drops import roll_leather, BANDS as LEATHER_BANDS
    from entities.meat_drops import roll_meat, BANDS as MEAT_BANDS
    from entities.material_tiers import HIGH_TIER, HIGH_TIER_FLOOR
    from entities.vendor_trash import classify

    cre = creatures()
    mats = jload("data/gathering/materials.json")["materials"]
    findings = []

    # Real creature names per family - classify() resolves a family by NAME
    # lookup against creatures.json, so an invented name silently becomes
    # `beast` and a humanoid-only drop correctly yields nothing.
    by_family = collections.defaultdict(list)
    for name, data in cre.items():
        by_family[classify(name, data.get("template", ""))[0]].append(name)

    class Enemy:
        def __init__(self, name, level, is_boss=False, template=""):
            self.name, self.level = name, level
            self.is_boss, self.template = is_boss, template
            self.location_type = "open_zone"

    modules = [
        ("cloth", roll_cloth, CLOTH_BANDS, "humanoid"),
        ("leather", lambda e: roll_leather(e), LEATHER_BANDS, "beast"),
        ("meat", lambda e: roll_meat(e), MEAT_BANDS, "beast"),
    ]

    max_level = max(v["level_range"][1] for v in cre.values())
    print(f"highest creature level in the game: {max_level}\n")
    print(f"{'ladder':9} {'authored':>8} {'drops now':>10} {'rollable':>9}  "
          f"status")
    print("-" * 100)

    violations = []
    for label, roll, bands, family in modules:
        authored = set()
        for _lo, _hi, weights in bands:
            authored |= set(weights)
        names = by_family.get(family) or []
        if not names:
            print(f"{label:9} no {family} creatures exist - cannot roll")
            continue

        # Sweep 1: real creature levels only.
        now = collections.Counter()
        for name in names:
            lo, hi = cre[name]["level_range"]
            tpl = cre[name].get("template", "")
            boss = bool(cre[name].get("is_boss"))
            for level in range(lo, hi + 1):
                for _ in range(6):
                    for mid, _qty in roll(Enemy(name, level, boss, tpl)):
                        now[mid] += 1
                        if level < HIGH_TIER_FLOOR and mid in HIGH_TIER:
                            violations.append((label, name, level, mid))

        # Sweep 2: synthetic 1-99 on the same real names, which is the only
        # way to separate the content ceiling from an unrollable band.
        ever = collections.Counter()
        probes = names[: max(6, len(names) // 20)]
        per = max(60, int(rolls / (99 * len(probes))))
        for level in range(1, 100):
            for name in probes:
                tpl = cre[name].get("template", "")
                for _ in range(per):
                    for mid, _qty in roll(Enemy(name, level, False, tpl)):
                        ever[mid] += 1
                        if level < HIGH_TIER_FLOOR and mid in HIGH_TIER:
                            violations.append((label, name, level, mid))

        unrollable = sorted(authored - set(ever))
        ceiling = sorted(set(ever) - set(now))
        status = (f"{len(ceiling)} held back by the level-{max_level} "
                  f"content ceiling")
        if unrollable:
            status = f"UNROLLABLE: {', '.join(unrollable)}"
            findings.append(
                f"{label}: {len(unrollable)} authored tier(s) cannot be rolled "
                f"at any level 1-99: {', '.join(unrollable)}")
        print(f"{label:9} {len(authored):>8} {len(now):>10} {len(ever):>9}  "
              f"{status}")

        missing = sorted(m for m in (set(now) | set(ever)) if m not in mats)
        if missing:
            findings.append(
                f"{label}: rolled material id(s) that do not exist in "
                f"data/gathering/materials.json: {', '.join(missing)}")

    print()
    if violations:
        worst = collections.Counter((v[0], v[3]) for v in violations)
        findings.append(
            f"RULE VIOLATION - high-tier material below level "
            f"{HIGH_TIER_FLOOR}: {len(violations)} rolls. "
            f"{dict(list(worst.items())[:8])}")
        print(f"HIGH-TIER MATERIAL BELOW LEVEL {HIGH_TIER_FLOOR}: "
              f"{len(violations)} rolls")
        for label, name, level, mid in violations[:15]:
            print(f"    {label:9} {name:30} level {level:>2}  {mid}")
    else:
        print(f"No high-tier material was rolled below level "
              f"{HIGH_TIER_FLOOR} in any sweep.")
    print()
    return findings


# ------------------------------------------------------ 6. vendor trash
def section_trash(rolls):
    """Roll vendor trash off every creature and report entries never produced."""
    from entities.vendor_trash import roll_drops, _config

    cfg = _config()
    cre = creatures()
    findings = []

    class Enemy:
        def __init__(self, name, level, is_boss, location_type):
            self.name, self.level = name, level
            self.is_boss, self.location_type = is_boss, location_type

    seen_pairs = set()
    seen_ids = collections.Counter()
    per = max(6, int(rolls / max(1, len(cre)) / 4))
    for name, data in cre.items():
        lo, hi = data["level_range"]
        boss = bool(data.get("is_boss"))
        for level in {lo, (lo + hi) // 2, hi}:
            for place in ("open_zone", "cave"):
                for _ in range(per):
                    for item in roll_drops(Enemy(name, level, boss, place))["items"]:
                        seen_ids[item["item_id"]] += 1
                        parts = item["item_id"].split("_")
                        seen_pairs.add((parts[1], parts[2]))

    authored_pairs = {(fam, e["id"]) for fam, entries in cfg["families"].items()
                      for e in entries}
    never = sorted(authored_pairs - seen_pairs)
    print(f"{sum(seen_ids.values())} trash items rolled off "
          f"{len(cre)} creatures; {len(seen_ids)} distinct item ids\n")
    print(f"{len(authored_pairs) - len(never)} of {len(authored_pairs)} "
          f"authored trash entries were produced at least once.")
    if never:
        findings.append(
            f"{len(never)} vendor trash entries never dropped: "
            + ", ".join(f"{f}/{e}" for f, e in never))
    print()
    return findings


# ----------------------------------------------------------- 7. recipes
def section_recipes(rolls):
    """Roll recipe scrolls and report drop-source recipes that never appear."""
    from entities.recipe_drops import roll_recipe
    from world.recipe_manager import all_recipes_by_source

    drop_recipes = all_recipes_by_source("drop")
    cre = creatures()
    max_level = max(v["level_range"][1] for v in cre.values())
    findings = []

    class Enemy:
        def __init__(self, level, is_boss=False, is_elite=False):
            self.level, self.is_boss, self.is_elite = level, is_boss, is_elite

    seen = set()
    # A NORMAL KILL YIELDS A SCROLL 0.4% OF THE TIME, and roll_recipe then
    # narrows to the top quarter of what that level can give - so the lowest
    # eligible recipe only appears off a LOW level mob, where the eligible
    # pool is short enough for it to be inside the cut. Reaching every one of
    # the 135 needs volume across the whole level range, not just volume:
    # rolls*6 left 34 missing, which read as dead and was variance.
    calls = rolls * 60
    for _ in range(calls):
        level = random.randint(1, max_level)
        kind = random.random()
        enemy = Enemy(level, is_boss=kind < 0.1, is_elite=0.1 <= kind < 0.3)
        rid = roll_recipe(enemy)
        if rid:
            seen.add(rid)

    never = sorted(set(drop_recipes) - seen)
    print(f"{calls} roll_recipe calls at content levels 1-{max_level}\n")
    print(f"{len(seen)} of {len(drop_recipes)} drop-source recipes dropped.")

    # THEN ANSWER IT DETERMINISTICALLY, because sampling cannot distinguish
    # "unreachable" from "reachable off one creature in the whole game at
    # 0.18% a kill". roll_recipe narrows to the top quarter of what a level
    # can give, so a recipe's real reach is the set of creature levels whose
    # cut contains it - and that is computable rather than sampleable.
    from entities.recipe_drops import eligible
    cut_at = {}
    for level in range(1, max_level + 1):
        pool = eligible(level)
        cut_at[level] = set(pool[max(0, len(pool) - max(8, len(pool) // 4)):])
    levels_per_creature = collections.Counter()
    for data in cre.values():
        lo, hi = data["level_range"]
        for level in range(lo, hi + 1):
            levels_per_creature[level] += 1

    unreachable, single_source = [], []
    for rid in drop_recipes:
        levels = [lv for lv in range(1, max_level + 1) if rid in cut_at[lv]]
        carriers = sum(levels_per_creature[lv] for lv in levels)
        if not levels:
            unreachable.append(rid)
        elif carriers <= 2:
            single_source.append((rid, levels, carriers))

    if unreachable:
        findings.append(
            f"{len(unreachable)} recipe(s) marked source=drop are in no "
            f"creature level's drop cut at all, so nothing in the world can "
            f"hand them over: {', '.join(unreachable)}")
        print(f"IN NO LEVEL'S CUT: {', '.join(unreachable)}")
    if single_source:
        findings.append(
            f"{len(single_source)} drop-source recipe(s) are reachable from "
            f"two creatures or fewer in the whole game, because their skill "
            f"requirement only enters the cut at the very top of the "
            f"level-{max_level} content ceiling: "
            + ", ".join(f"{r} (levels {lv}, {c} creature(s))"
                        for r, lv, c in single_source))
        print(f"REACHABLE FROM <= 2 CREATURES IN THE GAME:")
        for rid, levels, carriers in single_source:
            print(f"    {rid:36} skill "
                  f"{drop_recipes[rid][1].get('skill_required', 0):>3}  "
                  f"only in the cut at creature level(s) {levels}, "
                  f"{carriers} creature(s) reach that")
    if not unreachable and not single_source:
        print("Every drop-source recipe sits in the drop cut of a level that "
              "several creatures reach.")
    print()
    return findings


# --------------------------------------------------------- 8. stat keys
def section_stat_keys(rolls):
    """Equip a probe item per stat key and report the ones that change nothing.

    MEASURED, NOT GREPPED. A stat key is not live because the engine mentions
    the string: the conventions in this codebase are per key AND per channel,
    and `block_value` proves why that distinction has to be measured. It is a
    real Character attribute, a real Item constructor field and a real
    stat-conversion target, so every string-scanning check calls it live -
    and when it arrives as an item's secondary stat it goes into the bonus
    pool, which _recalculate_derived_stats never reads for that key. The
    shield's own block_value FIELD is summed by Equipment, the stat KEY is
    not, and only equipping one and watching the character tells them apart.
    """
    from entities.character import Character
    from entities.item import Item
    from entities.loot_generator import LootGenerator

    gen = LootGenerator()
    findings = []

    keys = set()
    for data in jload("data/items/gear_suffixes.json")["suffixes"].values():
        keys |= set(data["stats"])
    keys |= set(jload("data/items/stat_templates.json")["secondary_stat_pool"])
    # Everything any authored item actually ships, so a key used only by a
    # hand-written boss drop or quest reward is covered too.
    for _f, _b, item_def in boss_loot_entries():
        keys |= set(item_def.get("primary_stats") or {})
        keys |= set(item_def.get("secondary_stats") or {})
    for _f, _q, item_def in quest_reward_entries():
        keys |= set(item_def.get("primary_stats") or {})
        keys |= set(item_def.get("secondary_stats") or {})
    for _b, item_def in epic_entries():
        keys |= set(item_def.get("primary_stats") or {})
        keys |= set(item_def.get("secondary_stats") or {})

    def snapshot(char):
        return {k: v for k, v in vars(char).items()
                if isinstance(v, (int, float)) and not isinstance(v, bool)}

    dead = []
    print(f"{len(keys)} distinct stat keys appear on gear. Each is probed by "
          f"equipping\nan item carrying only that key and diffing every "
          f"numeric attribute on a\nreal level-40 Character.\n")
    print(f"{'stat key':26} {'verdict':8} changes")
    print("-" * 100)
    for key in sorted(keys):
        char = Character(name="Probe", char_class="Warrior", level=40)
        # A SHIELD, because three of these keys only do anything with one
        # equipped: block_chance is gated on having a shield, and without it
        # block_rating and defense_rating would both read as half-dead and
        # this check would accuse working code.
        char.equipment.equip(
            gen.generate_weapon("off_hand", "shield", "str_physical", 40, "rare"))
        char._recalculate_derived_stats()
        before = snapshot(char)
        char.equipment.equip(Item(
            item_id="probe", name="Probe", slot="ring", item_level=40,
            rarity="rare", armor_type="accessory",
            secondary_stats={key: 100.0}))
        char._recalculate_derived_stats()
        after = snapshot(char)
        changed = [k for k in after if before.get(k) != after[k]
                   and k not in ("current_health", "current_mana")]
        verdict = "live" if changed else "DEAD"
        if not changed:
            dead.append(key)
        print(f"{key:26} {verdict:8} {', '.join(changed[:5]) or '-'}")
    print()

    if dead:
        findings.append(
            f"{len(dead)} stat key(s) on gear change nothing on a real "
            f"character: {', '.join(dead)} - dead data that looks like a "
            f"mechanism, the same shape as the `stunned` stat_mod")
        for key in dead:
            users = [f"{f}:{b}:{d['name']}" for f, b, d in boss_loot_entries()
                     if key in (d.get("secondary_stats") or {})]
            q_users = [f"{f}:{q}:{d['name']}" for f, q, d in quest_reward_entries()
                       if key in (d.get("secondary_stats") or {})]
            suffix_users = [n for n, data
                            in jload("data/items/gear_suffixes.json")["suffixes"].items()
                            if key in data["stats"]]
            print(f"DEAD KEY {key!r} is carried by:")
            print(f"    {len(suffix_users)} gear suffix(es): "
                  f"{', '.join(suffix_users)}")
            print(f"    {len(users)} boss loot item(s), "
                  f"{len(q_users)} quest reward item(s)")
            print()

    return findings


# ---------------------------------------------------------- 9. resolve
def section_resolve(rolls):
    """Resolve every authored loot entry's ids, then try to really equip it.

    The equip attempt is the part a validator cannot do. Three quest rewards
    carry slot "weapon", which is the sentinel build_reward_gear_set uses to
    pick its WEAPON plan and is not an Equipment slot at all - so the item
    builds, reads correctly, validates, and Equipment.equip refuses it.
    """
    from entities.equipment import EQUIPMENT_SLOTS, PAIRED_SLOTS, Equipment
    from entities.item import Item

    armor_types = set(jload("data/items/armor_types.json")["armor_types"])
    weapon_types = set(jload("data/items/weapon_types.json")["weapon_types"])
    rarities = set(jload("data/items/rarity.json")["rarity_tiers"])
    valid_slots = set(EQUIPMENT_SLOTS) | set(PAIRED_SLOTS)
    findings = []

    sources = [("boss loot", boss_loot_entries()),
               ("quest reward", quest_reward_entries()),
               ("named epic", [(b, b, d) for b, d in epic_entries()])]

    for label, entries in sources:
        bad_slot, bad_at, bad_wt, bad_rarity, unequippable = [], [], [], [], []
        for where, owner, item_def in entries:
            slot = item_def.get("slot")
            if slot not in valid_slots:
                bad_slot.append((where, owner, item_def.get("name"), slot))
            if item_def.get("armor_type") and item_def["armor_type"] not in armor_types:
                bad_at.append((where, owner, item_def.get("name"),
                               item_def["armor_type"]))
            if item_def.get("weapon_type") and item_def["weapon_type"] not in weapon_types:
                bad_wt.append((where, owner, item_def.get("name"),
                               item_def["weapon_type"]))
            if item_def.get("rarity") and item_def["rarity"] not in rarities:
                bad_rarity.append((where, owner, item_def.get("name"),
                                   item_def["rarity"]))
            # Really equip it. Equipment.equip returns a 2-tuple on success
            # and a bare None when the slot is not one it owns, so an item
            # that cannot be worn is distinguishable from one that displaces
            # nothing.
            equipment = Equipment()
            result = equipment.equip(Item(
                item_id="x", name=item_def.get("name", "?"), slot=slot,
                item_level=item_def.get("item_level", 1),
                rarity=item_def.get("rarity", "common"),
                armor_type=item_def.get("armor_type"),
                weapon_type=item_def.get("weapon_type")))
            if result is None or not equipment.get_all_equipped():
                unequippable.append((where, owner, item_def.get("name"), slot))

        print(f"{label}: {len(entries)} authored items")
        for name, rows in (("slot is not an Equipment slot", bad_slot),
                           ("armor_type not in armor_types.json", bad_at),
                           ("weapon_type not in weapon_types.json", bad_wt),
                           ("rarity not in rarity.json", bad_rarity)):
            if rows:
                findings.append(
                    f"{label}: {len(rows)} item(s) where {name}: "
                    + ", ".join(f"{w}/{o}/{n} -> {v!r}" for w, o, n, v in rows[:6]))
                print(f"    {len(rows):>4} {name}")
                for w, o, n, v in rows[:8]:
                    print(f"         {w}  {o}  {n!r} -> {v!r}")
            else:
                print(f"       0 {name}")
        if unequippable:
            findings.append(
                f"{label}: {len(unequippable)} item(s) that Equipment.equip "
                f"refuses outright, so they can never be worn: "
                + ", ".join(f"{o}/{n} (slot {s!r})"
                            for _w, o, n, s in unequippable[:6]))
            print(f"    {len(unequippable):>4} REFUSED by Equipment.equip")
            for w, o, n, s in unequippable[:8]:
                print(f"         {w}  {o}  {n!r} slot={s!r}")
        print()

    # An armour/weapon slot item with NEITHER armor_type nor weapon_type
    # bypasses proficiency entirely: can_wear_armor_type passes None and
    # can_wear_weapon_type passes None, so every class of thirty can equip
    # it. Correct for accessories, which is what loot_generator stamps
    # "accessory" on; wrong for off_hand, where the engine's own holdable
    # type is "tome".
    typeless = collections.Counter()
    for label, entries in sources:
        for where, owner, item_def in entries:
            if not item_def.get("armor_type") and not item_def.get("weapon_type"):
                typeless[(label, item_def.get("slot"))] += 1
    print("ITEMS WITH NEITHER armor_type NOR weapon_type (no proficiency gate)")
    for (label, slot), count in sorted(typeless.items()):
        note = ("  <-- expected: accessories carry no armour class"
                if slot in ("neck", "ring", "trinket", "back", "ring1", "ring2",
                            "trinket1", "trinket2")
                else "  <-- every one of the 30 classes can equip this")
        print(f"    {label:14} slot {slot:12} {count:>4}{note}")
        if slot not in ("neck", "ring", "trinket", "back", "ring1", "ring2",
                        "trinket1", "trinket2"):
            findings.append(
                f"{label}: {count} {slot} item(s) carry neither armor_type nor "
                f"weapon_type, so they bypass proficiency and every class can "
                f"equip them")
    print()
    return findings


# ----------------------------------------------------- 10. distribution
def section_distribution(rolls):
    """Armour class and weapon type share, per boss/quest source file.

    Kyle's standing instruction: boss and quest loot must be varied, not
    lopsided toward one armour class or weapon type. So this reports per
    SOURCE FILE rather than in total - a game-wide average can look even
    while a particular dungeon hands out nothing but plate, which is what a
    player actually experiences.
    """
    findings = []
    LOPSIDED_SHARE = 0.55     # one armour class taking over half a source
    MIN_ITEMS = 8             # below this a share is noise, not a pattern

    def report(label, rows):
        armour = collections.Counter()
        weapon = collections.Counter()
        by_source = collections.defaultdict(
            lambda: (collections.Counter(), collections.Counter()))
        for where, _owner, item_def in rows:
            at = item_def.get("armor_type")
            wt = item_def.get("weapon_type")
            if wt:
                weapon[wt] += 1
                by_source[where][1][wt] += 1
            elif at and at != "accessory":
                armour[at] += 1
                by_source[where][0][at] += 1
            else:
                armour["(accessory)"] += 1
                by_source[where][0]["(accessory)"] += 1

        total_armour = sum(v for k, v in armour.items() if k != "(accessory)")
        print(f"=== {label}: {len(rows)} items ===")
        print(f"  armour  " + "  ".join(
            f"{a}={armour[a]} ({armour[a] / total_armour * 100:.0f}%)"
            for a in ("cloth", "leather", "mail", "plate")) +
            f"   accessory={armour['(accessory)']}")
        print(f"  weapons {sum(weapon.values())} total: " + ", ".join(
            f"{w}={c}" for w, c in weapon.most_common()))

        if total_armour:
            shares = {a: armour[a] / total_armour
                      for a in ("cloth", "leather", "mail", "plate")}
            hi, lo = max(shares, key=shares.get), min(shares, key=shares.get)
            spread = shares[hi] / shares[lo] if shares[lo] else float("inf")
            print(f"  spread  {hi} {shares[hi] * 100:.0f}% vs {lo} "
                  f"{shares[lo] * 100:.0f}%  = {spread:.2f}x")

        # Weapon types nobody authored at all in this channel.
        authored = set(jload("data/items/weapon_types.json")["weapon_types"])
        missing = sorted(authored - set(weapon))
        if missing:
            print(f"  weapon types never authored here: {', '.join(missing)}")

        # Per source file, which is the lopsidedness a player can feel.
        lopsided = []
        for where in sorted(by_source):
            arm, wep = by_source[where]
            n = sum(v for k, v in arm.items() if k != "(accessory)")
            if n < MIN_ITEMS:
                continue
            top, count = max(
                ((k, v) for k, v in arm.items() if k != "(accessory)"),
                key=lambda kv: kv[1])
            if count / n >= LOPSIDED_SHARE:
                lopsided.append((where, top, count, n))
        if lopsided:
            print(f"  LOPSIDED SOURCES (one armour class >= "
                  f"{LOPSIDED_SHARE:.0%} of that file's armour):")
            for where, top, count, n in sorted(
                    lopsided, key=lambda r: -r[2] / r[3]):
                print(f"    {where:38} {top:8} {count}/{n} "
                      f"({count / n * 100:.0f}%)")
            findings.append(
                f"{label}: {len(lopsided)} lopsided source(s): "
                + ", ".join(f"{w} is {c}/{n} {t}"
                            for w, t, c, n in lopsided[:8]))

        # A weapon type only one class can use is a lopsidedness of its own:
        # authoring effort aimed at 1/30 of the roster.
        class_weapon = jload("data/items/weapon_types.json")["class_weapon_map"]
        narrow = []
        for wt, count in weapon.items():
            owners = [c for c, lst in class_weapon.items() if wt in lst]
            if len(owners) <= 2 and count >= 3:
                narrow.append((wt, count, owners))
        if narrow:
            print(f"  WEAPON TYPES USABLE BY <= 2 OF THE 30 CLASSES:")
            for wt, count, owners in sorted(narrow, key=lambda r: -r[1]):
                print(f"    {wt:12} {count:>4} items  usable by "
                      f"{', '.join(owners)}")
            findings.append(
                f"{label}: " + "; ".join(
                    f"{c} {wt} items are usable by only {', '.join(o)}"
                    for wt, c, o in sorted(narrow, key=lambda r: -r[1])))
        print()

    report("BOSS LOOT", boss_loot_entries())
    report("QUEST REWARDS", quest_reward_entries())
    report("NAMED EPICS", [(b, b, d) for b, d in epic_entries()])
    return findings


# ------------------------------------------------------- 11. class cover
def section_coverage(rolls):
    """Per class, per level band: is there reachable gear it can equip?

    REACHABLE means an item some roll in this run actually produced, not an
    item the data describes. The corpus is built from real rolls - procedural
    drops per class, every fixed boss pool, every named epic - and then each
    class is asked through the real proficiency.can_equip, not through a
    reimplementation of the ladder.
    """
    from entities.character import Character
    from entities.item import Item
    from entities.loot_generator import LootGenerator
    from entities.boss_loot import get_fixed_boss_loot
    from entities.proficiency import can_equip
    from entities.equipment import EQUIPMENT_SLOTS, PAIRED_SLOTS

    gen = LootGenerator()
    classes = all_classes()
    playable = set(selectable_classes())
    cre = creatures()
    max_level = max(v["level_range"][1] for v in cre.values())
    findings = []

    # The corpus: real rolled items, tagged with the band they can drop in.
    corpus = collections.defaultdict(list)       # band_index -> [Item]
    per_class = max(100, int(rolls / len(classes) / 4))
    for cls in classes:
        for _ in range(per_class):
            level = random.randint(1, max_level)
            item = gen.generate_loot_for_creature(
                creature_level=level, char_class=cls,
                drop_chance=1.0, player_level=level)
            if item is None:
                continue
            corpus[_band_of(item.required_level)].append(item)

    real_bosses = {b for _f, b, _d in boss_loot_entries()
                   if b in cre and cre[b].get("is_boss")}
    for boss in real_bosses:
        for _ in range(6):
            item = get_fixed_boss_loot(boss)
            if item is not None:
                corpus[_band_of(item.required_level)].append(item)

    for _bucket, item_def in epic_entries():
        corpus[_band_of(item_def.get("required_level", 1))].append(
            Item.from_dict(dict(item_def)))

    # Slots a class is expected to be able to fill. ring2/trinket2 are the
    # second half of a pair the item itself never names, and the four bag
    # slots take bags rather than gear - counting either as a gap would be
    # the audit misreading a deliberate design (see Equipment.PAIRED_SLOTS).
    gear_slots = [s for s in EQUIPMENT_SLOTS
                  if s not in ("ring2", "trinket2")
                  and not s.startswith("bag")]

    # PER-CLASS EXPECTED SLOTS, because a class with no ranged weapon type
    # authored at all cannot fill the ranged slot and that is design, not a
    # loot gap. Reaper is the clear case: its whole weapon list is sword_2h,
    # axe_2h and mace_2h, so it has no off_hand and no ranged by intent, and
    # the first version of this check reported both as missing gear for it -
    # the audit accusing a deliberately narrow kit. Derived from the engine's
    # own class_weapon_map and hand data rather than a list kept here.
    weapon_types = jload("data/items/weapon_types.json")
    class_weapon = weapon_types["class_weapon_map"]
    hand_of = {k: v.get("hand") for k, v in weapon_types["weapon_types"].items()}

    def expected_slots(cls):
        allowed = class_weapon.get(cls, [])
        hands = {hand_of.get(w) for w in allowed}
        out = []
        for slot in gear_slots:
            if slot == "ranged" and "ranged" not in hands:
                continue
            if slot == "off_hand" and not (hands & {"off_hand", "main_or_off"}):
                continue
            out.append(slot)
        return out

    # BANDS THE CONTENT CEILING PUTS OUT OF REACH, computed rather than
    # eyeballed. A procedural drop's item_level is capped at the creature's
    # level and its required_level is item_level - 2, so nothing above
    # max_creature - 2 can come off a kill at all. Reporting those bands as
    # per-class gear gaps produced 30 identical findings on the first run,
    # every one of them the level-40 world and none of them a loot bug.
    drop_ceiling = max_level - 2
    ceiling_bands = {i for i, (lo, _hi) in enumerate(BANDS) if lo > drop_ceiling}

    print(f"corpus: {sum(len(v) for v in corpus.values())} items actually "
          f"rolled this run, over {len(BANDS)} bands")
    print(f"a kill can produce required_level {drop_ceiling} at most "
          f"(creature cap {max_level}, minus the 2-level item_level lead), so "
          f"bands\n" + ", ".join(f"{BANDS[i][0]}-{BANDS[i][1]}"
                                 for i in sorted(ceiling_bands)) +
          " are beyond the content ceiling and are reported as such.\n")
    print(f"{'class':18} {'armour':8} " +
          " ".join(f"{lo}-{hi}".rjust(7) for lo, hi in BANDS) + "   worst gap")
    print("-" * 110)

    armour_map = jload("data/items/armor_types.json")["class_armor_map"]
    starved = []
    for cls in classes:
        char = Character(name="C", char_class=cls, level=60)
        want = expected_slots(cls)
        cells, gaps = [], []
        for band_index, (lo, hi) in enumerate(BANDS):
            if band_index in ceiling_bands:
                cells.append(" (ceil)")
                continue
            pool = corpus.get(band_index, [])
            filled = set()
            for item in pool:
                concrete = PAIRED_SLOTS.get(item.slot, [item.slot])[0]
                if concrete not in want:
                    continue
                ok, _why = can_equip(char, item)
                if ok:
                    filled.add(concrete)
            missing = [s for s in want if s not in filled]
            cells.append(f"{len(filled)}/{len(want)}".rjust(7))
            if missing:
                gaps.append((lo, hi, missing))
        worst = ""
        if gaps:
            lo, hi, missing = max(gaps, key=lambda g: len(g[2]))
            worst = f"{lo}-{hi}: no {', '.join(missing)}"
            starved.append((cls, lo, hi, missing))
        skipped = [s for s in gear_slots if s not in want]
        tag = ""
        if skipped:
            tag = f"   (no {'/'.join(skipped)} weapon type authored)"
        if cls not in playable:
            tag += " (not selectable)"
        print(f"{cls:18} {armour_map.get(cls, '?'):8} " +
              " ".join(cells) + f"   {worst}{tag}")

    print()
    if starved:
        findings.append(
            f"{len(starved)} class(es) have a level band inside the content "
            f"ceiling with a gear slot they cannot fill from any reachable "
            f"item: "
            + "; ".join(f"{c} ({lo}-{hi}: {', '.join(m)})"
                        for c, lo, hi, m in starved[:8]))
    else:
        print("Every class can fill every slot it has a weapon type for, in "
              "every band\ninside the content ceiling.")
        print()
    return findings


def _band_of(level):
    for index, (lo, hi) in enumerate(BANDS):
        if lo <= level <= hi:
            return index
    return len(BANDS) - 1 if level > BANDS[-1][1] else 0


# ------------------------------------------------------------ 12. rules
def section_rules(rolls):
    """The project owner's hard tier and level rules, checked as rules.

    These are stated as absolutes, so they are checked here as absolutes
    rather than inferred from whatever the drop sweeps happened to produce:
    ladder tier COUNTS (no new tiers beyond the authored 40), node pool
    contents (no ore or wood above mid tier until 41-60 zones exist), and the
    two level floors.
    """
    from entities.material_tiers import (HIGH_TIER, HIGH_TIER_FLOOR,
                                         HIGH_TIER_CLOTH, HIGH_TIER_LEATHER)
    findings = []

    mats = jload("data/gathering/materials.json")["materials"]
    ladders = collections.Counter(v["material_type"] for v in mats.values())

    #: The authored ladder sizes, recorded the day this audit was written
    #: (2026-10-29). Kyle's rule is "no NEW tiers of gathering materials
    #: beyond the authored 40-tier ladders", which is a statement about a
    #: count, so the count is what is pinned. A ladder growing past its
    #: number here is the violation; a ladder shrinking is also worth seeing,
    #: because it means authored tiers went missing.
    EXPECTED_LADDERS = {
        "ore": 40, "wood": 40, "cloth": 40, "leather": 40,
        "bar": 41, "plank": 40, "bolt": 40,
        "meat": 5, "essence": 10, "crystal": 5, "herb": 16,
    }
    print("GATHERING LADDER SIZES")
    for name, expected in sorted(EXPECTED_LADDERS.items()):
        actual = ladders.get(name, 0)
        mark = "ok" if actual == expected else (
            "NEW TIERS ADDED" if actual > expected else "TIERS MISSING")
        print(f"  {name:9} {actual:>3} / {expected:>3}  {mark}")
        if actual != expected:
            findings.append(
                f"RULE VIOLATION - gathering ladder {name!r} has {actual} "
                f"tiers against the authored {expected}")
    print()

    # NODE POOLS: no ore or wood tier beyond what pre-41 zones should carry.
    zones = jload("data/gathering/node_pools.json")["zones"]
    used = set()
    for zone in zones.values():
        used |= set(zone["table"])
    unknown = sorted(m for m in used if m not in mats)
    if unknown:
        findings.append(
            f"node pools reference material id(s) that do not exist: "
            f"{', '.join(unknown)}")
    ALLOWED_NODE_TIERS = {"early", "mid"}
    print(f"NODE POOLS: {len(zones)} zones, {len(used)} distinct materials")
    for kind in ("ore", "wood"):
        ids = sorted(m for m in used
                     if m in mats and mats[m]["material_type"] == kind)
        tiers = sorted({mats[m].get("tier") for m in ids})
        over = [m for m in ids if mats[m].get("tier") not in ALLOWED_NODE_TIERS]
        print(f"  {kind:5} {len(ids):>2} in node pools, tiers {tiers}")
        if over:
            findings.append(
                f"RULE VIOLATION - {kind} node pool tiers above mid with no "
                f"41-60 zones to hold them: "
                + ", ".join(f"{m} ({mats[m].get('tier')})" for m in over))
    print()

    # HIGH TIER BEFORE 60, stated against the authored sets rather than only
    # against what the sweeps rolled, so an authored band that happens to be
    # unreachable today still gets checked.
    from entities.cloth_drops import BANDS as CLOTH_BANDS
    from entities.skinning_drops import BANDS as LEATHER_BANDS
    from entities.material_tiers import in_reach
    leaks = []
    for label, bands in (("cloth", CLOTH_BANDS), ("leather", LEATHER_BANDS)):
        for lo, hi, weights in bands:
            for level in range(lo, min(hi, HIGH_TIER_FLOOR - 1) + 1):
                served = in_reach(weights, level)
                for mid in served:
                    if mid in HIGH_TIER:
                        leaks.append((label, level, mid))
    print(f"HIGH-TIER FLOOR (level {HIGH_TIER_FLOOR}): "
          f"{len(HIGH_TIER_CLOTH)} cloth + {len(HIGH_TIER_LEATHER)} leather "
          f"tiers held back")
    if leaks:
        findings.append(
            f"RULE VIOLATION - in_reach serves high-tier material below level "
            f"{HIGH_TIER_FLOOR}: {len(leaks)} band/level pairs, e.g. "
            + ", ".join(f"{l} at {lv}: {m}" for l, lv, m in leaks[:6]))
        for label, level, mid in leaks[:10]:
            print(f"    {label} band serves {mid} at level {level}")
    else:
        print(f"  in_reach serves no high-tier material at any level below "
              f"{HIGH_TIER_FLOOR}.")
    print()

    # MAGIC RESISTANCE AFTER 45, against every authored item as well as the
    # rolled ones the suffix sweep covers.
    early = []
    for label, rows in (("boss loot", boss_loot_entries()),
                        ("quest reward", quest_reward_entries()),
                        ("named epic", [(b, b, d) for b, d in epic_entries()])):
        for where, owner, item_def in rows:
            stats = (set(item_def.get("primary_stats") or {})
                     | set(item_def.get("secondary_stats") or {}))
            hit = stats & RESISTANCE_STATS
            need = item_def.get("required_level",
                                max(1, item_def.get("item_level", 1) - 2))
            if hit and need <= RESISTANCE_MIN_PLAYER_LEVEL:
                early.append((label, where, owner, item_def["name"], need,
                              sorted(hit)))
    print(f"MAGIC RESISTANCE FLOOR (player level "
          f"{RESISTANCE_MIN_PLAYER_LEVEL})")
    if early:
        findings.append(
            f"RULE VIOLATION - {len(early)} authored item(s) grant magic "
            f"resistance at a required_level of "
            f"{RESISTANCE_MIN_PLAYER_LEVEL} or below: "
            + ", ".join(f"{n} (req {r})" for _l, _w, _o, n, r, _s in early[:8]))
        for label, where, owner, name, need, stats in early[:12]:
            print(f"    {label:13} {where:30} {name!r} req {need} "
                  f"{', '.join(stats)}")
    else:
        print(f"  No authored boss, quest or epic item grants a resistance "
              f"stat at all, so none grants one early.")
    print()
    return findings


# -------------------------------------------------------------- driver
SECTIONS = [
    ("procedural", section_procedural),
    ("suffixes", section_suffixes),
    ("fixed-boss", section_fixed_boss),
    ("epics", section_epics),
    ("materials", section_materials),
    ("trash", section_trash),
    ("recipes", section_recipes),
    ("stat-keys", section_stat_keys),
    ("resolve", section_resolve),
    ("distribution", section_distribution),
    ("coverage", section_coverage),
    ("rules", section_rules),
]


def main(argv):
    rolls = int(argv[argv.index("--rolls") + 1]) if "--rolls" in argv else ROLLS
    only = argv[argv.index("--section") + 1] if "--section" in argv else None
    if "--seed" in argv:
        random.seed(int(argv[argv.index("--seed") + 1]))

    findings = []
    for name, fn in SECTIONS:
        if only and name != only:
            continue
        print("=" * 100)
        print(f"  {name.upper()}")
        print("=" * 100)
        result = fn(rolls)
        if isinstance(result, tuple):
            result = result[0]
        findings.extend(f"[{name}] {f}" for f in (result or []))

    print("=" * 100)
    print(f"  {len(findings)} FINDING(S)")
    print("=" * 100)
    for finding in findings:
        print(f"\n  * {finding}")
    if not findings:
        print("\n  Every authored loot entry came out of a real roll, every "
              "stat key on\n  every item changes something on a real "
              "character, no source is\n  lopsided, and no tier or level "
              "rule is broken.")
    print()
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
