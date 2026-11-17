#!/usr/bin/env python3
"""No two crafted pieces with different names and the very same stats; woodworking's top end isn't all healing.

    PYTHONPATH=. python3 tools/diversify_crafted_gear.py [--apply]

Kyle, 16 Nov 2026, with screenshots of three skill-300 mantles all "+69 Spell Power, +28 Spell Crit, +19 Int": "Some of
these are identical! we need a bit of diversity here. A lot of the end game wood working are mostly just healing
items? Let's mix this up bro."

HOW IT HAPPENS. A crafted piece's stats come from its identity (tools/build_crafted_gear.IDENTITIES: "caster_crit" is
spell power, spell crit and intellect) and its item level. Two pieces of one trade, one armour type, one identity and
one item level come out the same, slot for slot. 58 sets of differently named pieces did (126 pieces).

WHAT THIS DOES
  * In every such set the first piece keeps its identity and each other piece takes a sister identity: the same
    stat template (a caster stays a caster, a healer a healer), one that suits its armour (no bear tank in plate,
    no plate healer in cloth) and one nobody else in the set has. "Navigator's Silk Mantle" stays caster crit;
    "Mantle of the Walkout" turns haste caster; "Velaren's Mantle" another.
  * Woodworking's healing-heavy sets (Moonpetal at 240, Sunheart at 300) trade some healing for casters and a tank
    shield: WOODWORKING below.
  * The choices go in data/items/crafted_identity_overrides.json, which build_crafted_gear.author reads, so a rebuild
    of any trade makes the same pieces. Only the stats change: name, icon, recipe and source stay.
  * The hidden vendors' copies of a recipe (secret_*) are the same piece, and follow it.

Without --apply it lists what would change.
"""
import argparse
import collections
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

OVERRIDES = ROOT / "data/items/crafted_identity_overrides.json"
FILES = {"blacksmithing": "data/blacksmithing/recipes.json", "leatherworking": "data/leatherworking/recipes.json",
         "jewelcrafting": "data/jewelcrafting/recipes.json"}
SHARED = "data/crafting/recipes.json"          # tailoring, woodworking, engineering, ...

#: Woodworking (Kyle: "A lot of the end game wood working are mostly just healing items"). Moonpetal (240-250) was six
#: healing pieces of seven and Sunheart (300) four of six; these move to casters and a tank's shield.
WOODWORKING = {
    "p300_wo_moonpetal_wand": "precise_caster",
    "wwx_moonpetal_codex": "nature",
    "wwx_moonpetal_blossom": "spirit_caster",
    "wwx_blessed_sunheart_codex": "holy",
    "wwx_sunheart_tideguard": "shield_tank",
}

#: identities that suit an armour type (None: weapons, shields, off-hands, jewellery, cloaks: anything goes)
SUITS = {
    "cloth": {"starter_caster", "sturdy_caster", "traveller", "caster", "arcane", "arcane_crit", "caster_crit",
              "haste_caster", "precise_caster", "shadow_sturdy", "shadow", "frost", "fire", "spirit_caster",
              "dark_haste", "nature", "blood", "fel", "death", "storm", "hex", "battlemage", "void", "holy",
              "spirit_healer", "healer", "high_healer"},
    "leather": {"agi_starter", "agility", "feral", "rogue_crit", "assassin", "bear", "physical", "wildheart",
                "spirit_healer", "healer", "high_healer", "tide_healer", "nature", "storm", "spirit_caster",
                "melee_starter", "bruiser", "strength", "strength_crit", "strength_hit", "hunter_precise",
                "hunter_crit", "hunter"},
    "mail": {"hunter", "hunter_crit", "hunter_precise", "agility", "physical", "earthen", "crusader", "mail_caster",
             "tide_healer", "healer", "storm", "nature", "melee_starter", "strength", "strength_crit",
             "strength_hit", "bruiser", "tank_any", "rogue_crit", "assassin", "agi_starter", "wildheart",
             "haste_caster", "caster", "caster_crit"},
    "plate": {"melee_starter", "strength", "strength_crit", "strength_hit", "bruiser", "tank", "tank_any",
              "crusader", "earthen", "plate_healer", "healer", "high_healer"},
}
#: never handed out to a piece that didn't already have one (they're shaped for one kind of item)
SPECIAL = {"tank_weapon", "bear_weapon", "shield_tank", "starter_caster", "agi_starter", "melee_starter",
           "traveller"}


def load_all():
    """-> {path: doc} and [(path, prof, rid, recipe)] for every crafted piece."""
    docs, rows = {}, []
    for prof, path in FILES.items():
        docs[path] = json.loads((ROOT / path).read_text(encoding="utf-8"))
        for rid, r in docs[path]["recipes"].items():
            rows.append((path, prof, rid, r))
    docs[SHARED] = json.loads((ROOT / SHARED).read_text(encoding="utf-8"))
    for prof, p in docs[SHARED]["professions"].items():
        for rid, r in (p.get("recipes") or {}).items():
            rows.append((SHARED, prof, rid, r))
    rows = [x for x in rows if ((x[3].get("output") or {}).get("item"))]
    return docs, rows


def stats_of(item):
    return tuple(sorted({**(item.get("primary_stats") or {}), **(item.get("secondary_stats") or {})}.items()))


def base_rid(rid, known):
    """secret_<seller>_<rid> -> rid (a hidden vendor's copy of a recipe)."""
    if not rid.startswith("secret_"):
        return rid
    for i in range(len(rid)):
        if rid[i] == "_" and rid[i + 1:] in known:
            return rid[i + 1:]
    return rid


def sisters(ident, armour, taken, salt):
    import build_crafted_gear as C
    template = C.IDENTITIES[ident][1]
    out = []
    # the same template first; a hybrid with only two identities borrows from its nearest plain template
    for t in (template, NEAREST.get(template)):
        # identities with the same weights under another name (crusader and earthen, assassin and hunter_precise)
        # make the same piece, so a weight-twin of one already in the set doesn't count as different
        same = [C.IDENTITIES[x][0] for x in taken if x in C.IDENTITIES]
        pool = [k for k, (w, tt) in C.IDENTITIES.items()
                if tt == t and k not in taken and k not in SPECIAL and w not in same
                and (armour not in SUITS or k in SUITS[armour])]
        out += sorted(pool, key=lambda k: hashlib.sha1(f"{salt}:{k}".encode()).hexdigest())
    return out


NEAREST = {"str_int_hybrid": "str_physical", "agi_int_hybrid": "agi_physical", "spi_healer": "int_caster"}


def plan():
    """-> {rid: new identity}, with the sets it came from."""
    import build_crafted_gear as C
    docs, rows = load_all()
    known = {rid for _p, _prof, rid, _r in rows if not rid.startswith("secret_")}
    current = {}
    groups = collections.defaultdict(list)
    for path, prof, rid, r in rows:
        if rid.startswith("secret_"):
            continue
        it = r["output"]["item"]
        current[rid] = it.get("identity")
        kind = it.get("armor_type") if r["output"].get("kind") == "armor" else it.get("weapon_type")
        groups[(prof, kind, stats_of(it))].append((r.get("skill_required") or 0, rid, it))
    out = dict(WOODWORKING)
    try:
        # earlier runs' picks stand unless they still collide (run until nothing changes)
        out.update(json.loads(OVERRIDES.read_text(encoding="utf-8"))["identities"])
    except (OSError, ValueError, KeyError):
        pass
    sets = []
    for (prof, kind, _st), members in groups.items():
        if len({m[2]["name"] for m in members}) < 2:
            continue
        members.sort(key=lambda m: (m[0], m[1]))
        taken = {members[0][2].get("identity")}
        for _s, rid, it in members[1:]:
            if rid in WOODWORKING:
                taken.add(out[rid])
                continue
            ident = it.get("identity")
            if ident not in C.IDENTITIES:
                continue
            armour = it.get("armor_type") if it.get("slot") not in ("back", "neck", "ring", "trinket") else None
            pick = sisters(ident, armour, taken, rid)
            if pick:
                out[rid] = pick[0]
                taken.add(pick[0])
        sets.append([m[2]["name"] for m in members])
    return docs, rows, known, out, sets


def reauthor(rid, r, ident):
    """The recipe's piece with `ident`'s stats; everything that isn't a stat stays as it was."""
    import build_crafted_gear as C
    old = r["output"]["item"]
    out = dict(r["output"])
    out["stat_template"] = C.IDENTITIES[ident][1]
    out = {k: v for k, v in out.items() if k != "item"}
    new = C.author(rid, {"name": old["name"], "output": out}, ident, old.get("flavor_text") or "")
    item = dict(old)
    for k in ("primary_stats", "secondary_stats", "armor_value", "stat_template", "identity",
              "weapon_damage_min", "weapon_damage_max", "attack_speed", "block_value"):
        if k in new:
            item[k] = new[k]
    return out["stat_template"], item


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    import build_crafted_gear as C
    from crafted_icon_palette import Picker
    C.PICKER = Picker()
    docs, rows, known, picks, sets = plan()
    C._OVERRIDES = picks            # author() applies the overrides itself; it must see these, not the file's
    changed, bad = [], []
    # every copy of a piece moves together, or none does: a hidden vendor's copy that fails the audit keeps the
    # original's stats too
    staged, failing = [], set()
    for path, prof, rid, r in rows:
        base = base_rid(rid, known)
        if base not in picks:
            continue
        template, item = reauthor(base, r, picks[base])
        audit = C.audit_item(prof, base, item)
        if audit:
            bad.append(f"{rid}: {audit}")
            failing.add(base)
        staged.append((prof, rid, base, r, template, item))
    for base in failing:
        picks.pop(base, None)
    for prof, rid, base, r, template, item in staged:
        if base in failing:
            continue
        before = stats_of(r["output"]["item"])
        r["output"]["stat_template"] = template
        r["output"]["item"] = item
        if not rid.startswith("secret_"):
            changed.append((prof, r.get("skill_required"), item["name"], picks[base], dict(before), stats_of(item)))
    print(f"{len(sets)} sets of identical pieces; {len(picks)} pieces given a new identity "
          f"({len(changed)} recipes, plus their hidden-vendor copies)")
    for prof, sk, name, ident, before, after in sorted(changed, key=lambda c: -(c[1] or 0))[:14]:
        print(f"  {prof:14s} {sk:>3} {name:34s} -> {ident:15s} {dict(after)}")
    if bad:
        print(f"{len(bad)} would fail the crafted-gear audit and were left alone:")
        for b in bad[:10]:
            print("   ", b)
    if a.apply:
        for path, doc in docs.items():
            (ROOT / path).write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        OVERRIDES.write_text(json.dumps({
            "_notes": "Identities that replace a crafted piece's own, so no two differently named pieces share every "
                      "stat (Kyle, 16 Nov 2026). Written by tools/diversify_crafted_gear.py; read by "
                      "tools/build_crafted_gear.author, so a rebuild makes the same pieces.",
            "identities": dict(sorted(picks.items()))}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
