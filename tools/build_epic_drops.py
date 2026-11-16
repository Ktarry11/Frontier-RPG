#!/usr/bin/env python3
"""The named epics: world drops and the occasional dungeon purple. Idempotent.

    PYTHONPATH=. python3 tools/build_epic_drops.py

Kyle, 2026-10-28: "We can get the occasional drops as epic after lvl 30 in Dungeons and also for
world drop after lvl 30. Think of how wow does it with world drops."

Kyle, 2026-10-29: "Each epic should be unique bro and spread across the classes... i'd like to see
more and more 'open world' epics pop up... These will be hand crafted. But also we can get the open
world epics that are just procedurally generated with affixes like the greens/blues... Also some of
the dungeons can drop them at a small chance."

WHAT THE AUDIT FOUND. All 892 hand-authored dungeon items are rarity rare - there is not one epic
drop anywhere in the game - while two upgrade kits take any crafted piece to epic plus five item
levels. So there was no gear reason to run a dungeon. The procedural roller already gates epic at
level 30 exactly as Kyle describes, but hand-authored boss pools bypass it: get_fixed_boss_loot
returns a fixed item before the procedural roll ever happens, and all 44 bosses above level 30 have
one.

WOW'S WORLD-DROP MODEL IS WHY THESE ARE NAMED AND FEW. A world epic in WoW is memorable because it
is a specific item - people know the name, they know roughly what drops it, and almost nobody has
one. A purple generated on the fly from a stat budget cannot do that however rare you make it, so
these are hand-authored: thirty-six items, each with its own name and its own reason to exist.

STATS COME FROM THE ENGINE, NOT FROM ME. Only the identity is authored here - name, slot, type,
item level, who it suits. LootGenerator fills in the actual numbers at epic budget, which is the
same code path every other item in the game goes through. Hand-writing stat blocks for 36 epics
would mean hand-deriving the armour and damage curves, and the first one I got slightly wrong would
sit there being slightly wrong forever.

THREE GUARDS, each of which exists because the thing it guards against already happened:

  * strict=True on generate_weapon. "The Quiet Argument" was authored as a spi_healer mace and
    "The Deep Bloom's Root" as a spi_healer staff; spi_healer was valid on no weapon type, so
    generate_weapon substituted valid_templates[0] and both became int_caster items. Silently.
    The table still said healer. Both weapon types now accept spi_healer, and a future mismatch
    raises instead of lying.

  * coherent(). A stat template only gates which gear SUFFIXES are eligible, so "agi_physical"
    means "may roll any physical-ish suffix" rather than "carries agility". An agility 2H mace
    came back carrying agility in 1 roll of 8, and 17 of 36 epics had no primary stats at all.
    Each item is rerolled until it carries the stat it is named for, meaningfully. The engine is
    untouched - that randomness is correct for procedural drops and wrong for a named item.

  * ranged slots. 24 ranged weapons were authored into main_hand, so equipping a bow took the
    melee weapon off. That was fixed in the data and in Equipment._resolve_slot, and then I
    reintroduced it here by regenerating from a source that still said main_hand. The check is
    upstream of the build now, on the table itself.

SPREAD IS CHECKED, NOT ASSUMED, because Kyle's standing rule is that loot must not be lopsided
toward one armour class or weapon type. The audit() at the bottom fails the build if it is.
"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: The tables live in tools/epic_table.py (16 Nov 2026): the world pool, the dungeon epics by final boss, the
#: class-leaning stat mixes and each epic's own icon.
from tools.epic_table import DUNGEON, FINAL_BOSSES, MIX, NEW_PROCS, SHARED_30S, WORLD  # noqa: E402

#: Trinkets that DO something. Kyle, 10 Nov: "trinkets over 50+ WILL AND MUST start to
#: actually do stuff." The payload is a StatusEffect proc dict - the same engine talents use
#: (combat/status_effects.py, fire_proc_trigger) - carried by the item and hung on the wearer
#: by Character._sync_equipment_procs while it is equipped.
#:
#: The Unbanked Fire is Wrath of Cenarius: damaging spells sometimes flood the caster with
#: spell power for a few turns. Sized against a level 55 caster's gear, a spike of roughly a
#: third of their spell power, which is where Wrath of Cenarius sat in its own tier.
PROCS = {
    "The Unbanked Fire": {
        "trigger": "on_damage_cast",
        "chance": 8,
        "icd": 5,
        "apply_effect": {
            "effect_id": "unbanked_fire_blaze",
            "name": "Uninsured Blaze",
            "effect_type": "buff",
            "duration": 3,
            "stat_mods": {"spell_power": 40},
            "on_target": False,
        },
        "describe": "Your damaging spells have a chance to grant 40 spell power for 3 turns.",
    },
    # The healer's version of the same idea.
    "The Borrowed Hour": {
        "trigger": "on_heal_cast", "chance": 10, "icd": 5,
        "apply_effect": {"effect_id": "borrowed_hour_minute", "name": "A Spare Minute",
                         "effect_type": "buff", "duration": 3,
                         "stat_mods": {"healing_power": 60}, "on_target": False},
        "describe": "Your healing spells have a chance to grant 60 healing power for 3 turns.",
    },
    # Crits feed it, for anyone who hits with a weapon.
    "Witness": {
        "trigger": "on_crit", "chance": 20, "icd": 4,
        "apply_effect": {"effect_id": "witness_clear_sight", "name": "Clear Sight",
                         "effect_type": "buff", "duration": 3,
                         "stat_mods": {"attack_power": 70}, "on_target": False},
        "describe": "Your critical strikes have a chance to grant 70 attack power for 3 turns.",
    },
    # A tank trinket: being hit sometimes heals you. heal_flat lands on the wearer.
    "The Long Watch": {
        "trigger": "on_damage_taken", "chance": 12, "icd": 5,
        "apply_effect": {"effect_id": "long_watch_stand", "name": "Stand Your Ground",
                         "effect_type": "buff", "duration": 3,
                         "stat_mods": {"armor": 500, "block_rating": 30}, "on_target": False},
        "describe": "When you are hit, you have a chance to gain 500 armour and 30 block rating for 3 turns.",
    },
    "The Queen's Regard": {
        "trigger": "on_heal_cast", "chance": 10, "icd": 5,
        "apply_effect": {"effect_id": "queens_regard_favour", "name": "The Queen's Favour",
                         "effect_type": "buff", "duration": 3,
                         "stat_mods": {"healing_power": 66, "haste": 4}, "on_target": False},
        "describe": "Your healing spells have a chance to grant 66 healing power and 4 haste for 3 turns.",
    },
    "Serpent's Second Skin": {
        "trigger": "on_damage_taken", "chance": 12, "icd": 4, "heal_flat": 220,
        "describe": "When you are hit, you have a chance to heal for 220.",
    },
}

PROCS.update(NEW_PROCS)

#: An item named for a stat has to carry it. See coherent().
LEAD_SHARE = 0.25
MAX_REROLLS = 200


def lead_stats(gen, stat_template):
    """The primary stat(s) this template exists to deliver."""
    return gen._TEMPLATE_LEAD.get(stat_template, frozenset())


def templateless(gen, kind, atype):
    """True for an item type the engine generates without consulting a stat
    template at all - a shield, whose budget goes to stamina, armour and
    block value by construction. Asking such an item to carry strength is
    asking for something generate_weapon never promised, and the first run
    of the coherence guard spent 200 rerolls discovering that about "What
    the Tide Kept" before failing the build. The table still names a
    template for a shield, because the name and the icon come from it."""
    if kind != "weapon":
        return False
    wt = gen.weapon_types["weapon_types"].get(atype, {})
    return not wt.get("valid_stat_templates")


def coherent(item, gen, stat_template, kind=None, atype=None):
    """True if the item carries the stat it is named for, meaningfully.

    Items the engine builds without a template (shields) are coherent by
    construction and exempt. Everything else must put at least LEAD_SHARE of
    its primary stat points into one of its template's lead stats -
    present-but-trivial is the failure mode this catches, where an "agility"
    weapon rolls 1 agility and 40 stamina.
    """
    if kind is not None and templateless(gen, kind, atype):
        return True
    leads = lead_stats(gen, stat_template)
    if not leads:
        return True
    primaries = item.primary_stats or {}
    total = sum(primaries.values())
    if not total:
        return False
    best = max((primaries.get(s, 0) for s in leads), default=0)
    return best >= LEAD_SHARE * total


def build_one(gen, name, slot, kind, atype, ilvl, template):
    """Generate until the item is coherent, or report which one would not be."""
    for _ in range(MAX_REROLLS):
        if kind == "armor":
            item = gen.generate_armor_piece(slot, atype, template, ilvl, "epic")
        else:
            item = gen.generate_weapon(slot, atype, template, ilvl, "epic", strict=True)
        if item is None:
            return None, f"the generator would not build {name} ({atype} {slot})"
        if coherent(item, gen, template, kind, atype):
            return item, None
    return None, (f"{name} ({atype}, {template}) never rolled {int(LEAD_SHARE * 100)}% of its "
                  f"primary stats into {'/'.join(sorted(lead_stats(gen, template)))} "
                  f"in {MAX_REROLLS} tries - the suffix pool for this template may have no "
                  f"suffix that leads with it")


def check_ranged_slots(rows):
    """A ranged weapon type authored into a melee slot - the regression I
    reintroduced after fixing it once, so the check sits on the table."""
    wt = json.loads((ROOT / "data/items/weapon_types.json").read_text(encoding="utf-8"))["weapon_types"]
    ranged = {k for k, v in wt.items() if v.get("hand") == "ranged"}
    return [f"{name} is a {atype} (ranged) but authored into slot '{slot}'"
            for name, slot, kind, atype, *_rest in rows
            if kind == "weapon" and atype in ranged and slot != "ranged"]


def audit(rows):
    """Kyle's standing rule: boss and quest loot must not lean on one armour class or weapon type."""
    armour = Counter(r[3] for r in rows if r[2] == "armor" and r[3] != "accessory")
    weapons = Counter(r[3] for r in rows if r[2] == "weapon")
    templates = Counter(r[5] for r in rows)
    problems = []
    for cls in ("cloth", "leather", "mail", "plate"):
        if armour[cls] < 2:
            problems.append(f"only {armour[cls]} {cls} pieces - the spread is lopsided")
    cap = max(3, sum(weapons.values()) // 3)
    if max(weapons.values(), default=0) > cap:
        hog = max(weapons, key=weapons.get)
        problems.append(f"{weapons[hog]} of the weapons are {hog} (cap {cap})")
    if len(templates) < 6:
        missing = {"str_physical", "agi_physical", "int_caster", "spi_healer",
                   "str_int_hybrid", "agi_int_hybrid"} - set(templates)
        problems.append(f"only {len(templates)} stat templates of 6 - missing "
                        f"{', '.join(sorted(missing))}")
    share = max(templates.values(), default=0) / max(len(rows), 1)
    if share > 0.40:
        hog = max(templates, key=templates.get)
        problems.append(f"{templates[hog]} of {len(rows)} epics are {hog} "
                        f"({share:.0%}) - Kyle: \"spread across the classes\"")
    names = [n for n, *_r in rows]
    dupes = [n for n, c in Counter(names).items() if c > 1]
    if dupes:
        problems.append(f"duplicate names: {', '.join(dupes)} - Kyle: \"Each epic should be unique\"")
    print(f"  armour: {dict(armour)}")
    print(f"  weapons: {dict(weapons)}")
    print(f"  stat templates: {dict(templates)}")
    return problems


def apply_mix(d, mix):
    """A class-leaning epic's stat line: the authored mix, split into primary and secondary."""
    prim = {k: v for k, v in mix.items() if k in ("strength", "agility", "stamina", "intellect", "spirit")}
    sec = {k: v for k, v in mix.items() if k not in prim}
    d["primary_stats"], d["secondary_stats"] = prim, sec


def icon_users():
    """icon_id -> names of every OTHER item in data/ that draws it (the one-icon rule)."""
    from collections import defaultdict
    users = defaultdict(set)

    def walk(o):
        if isinstance(o, dict):
            if isinstance(o.get("icon_id"), str) and o.get("name") and (o.get("item_level") or o.get("slot")):
                users[o["icon_id"]].add(o["name"])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    for f in sorted((ROOT / "data").rglob("*.json")):
        if f.name == "epic_drops.json":
            continue
        try:
            walk(json.loads(f.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            continue
    return users


def main():
    from entities.item_budget import budget_ratio, fit_to_curve
    from entities.loot_generator import LootGenerator
    gen = LootGenerator()

    rows = [r[:7] for r in WORLD] + [r[:7] for r in DUNGEON]
    print(f"spread check over {len(rows)} epics:")
    problems = audit(rows) + check_ranged_slots(rows)
    bosses = {r[8] for r in DUNGEON} - {SHARED_30S}
    problems += [f"{b} has epics but is not on FINAL_BOSSES" for b in sorted(bosses - set(FINAL_BOSSES))]
    problems += [f"{b} is a 40+ final boss with no epic of its own" for b, (_d, ch) in FINAL_BOSSES.items()
                 if ch >= 0.05 and b not in bosses]
    # One icon per item (Kyle, 16 Nov: "every unique item in the game can only have ONE icon"). An icon an epic
    # takes must belong to no other item anywhere in data/, and to no other epic.
    users = icon_users()
    seen = {}
    for r in list(WORLD) + list(DUNGEON):
        icon = r[7]
        if not icon:
            continue
        if users.get(icon):
            problems.append(f"{r[0]}'s icon {icon} is already {sorted(users[icon])[0]}'s")
        if icon in seen:
            problems.append(f"{r[0]} and {seen[icon]} share the icon {icon}")
        seen[icon] = r[0]
        if not (ROOT / "assets/icons/gear" / f"{icon}.png").exists():
            problems.append(f"{r[0]}'s icon {icon} is not on disk")
    if problems:
        print("\nFAILED - fix the table, not the check:")
        for p in problems:
            print(f"  - {p}")
        return 1

    p = ROOT / "data/loot/epic_drops.json"
    try:
        existing = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        existing = {}
    have = {d.get("item_id"): d for key in ("world", "dungeon", "pending") for d in existing.get(key, [])}

    out = {"_notes": ("Named epic drops (docs/epic_drops_plan.md). WORLD: one 1-in-400 roll on any level 30+ kill, "
                      "then one pick from the epics that fit the zone's level band. DUNGEON: a final boss's own "
                      "epics (or the shared 30-39 pool) at the chance in final_bosses. PENDING: built, waiting on "
                      "an icon of their own, and never dropped. Identity in tools/epic_table.py; stats from "
                      "LootGenerator at epic budget, then put on the item curve. Rolled by entities/epic_drops.py."),
           "final_bosses": {b: {"dungeon": d, "chance": ch} for b, (d, ch) in FINAL_BOSSES.items()},
           "world": [], "dungeon": [], "pending": []}
    kept = rolled = 0
    for key, table in (("world", WORLD), ("dungeon", DUNGEON)):
        for row in table:
            name, slot, kind, atype, ilvl, template, flavour, icon = row[:8]
            item_id = "epic_" + name.lower().replace("'", "").replace(" ", "_").replace(",", "")
            if item_id in have:
                d = dict(have[item_id])
                r = budget_ratio(d)
                if r and not 0.65 <= r <= 1.45:      # off the curve: back onto it, mix kept
                    fit_to_curve(d)
                kept += 1
            else:
                item, err = build_one(gen, name, slot, kind, atype, ilvl, template)
                if err:
                    print(f"FAILED: {err}")
                    return 1
                d = item.to_dict()
                if name in MIX:
                    apply_mix(d, MIX[name])
                fit_to_curve(d)
                rolled += 1
            d["name"] = name
            d["flavor_text"] = flavour
            d["item_id"] = item_id
            d["icon_id"] = icon
            d["power_scale"] = 3
            if name in MIX:
                d["class_leaning"] = True
            else:
                d.pop("class_leaning", None)
            if key == "dungeon":
                d["boss"] = row[8]
            else:
                d.pop("boss", None)
            if name in PROCS:
                d["proc"] = PROCS[name]
            else:
                d.pop("proc", None)
            out[key if icon else "pending"].append(d)

    if not out["pending"]:
        del out["pending"]
    p.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    off = [d["name"] for k in ("world", "dungeon") for d in out[k]
           if (budget_ratio(d) or 1) < 0.65 or (budget_ratio(d) or 1) > 1.45]
    print(f"\n  world {len(out['world'])}, dungeon {len(out['dungeon'])}, pending an icon {len(out.get('pending', []))}")
    print(f"  kept {kept} unchanged, rolled {rolled} new")
    if off:
        print(f"  off the item curve: {', '.join(off)}")
    print(f"wrote {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
