#!/usr/bin/env python3
"""Rebuild data/spellbook_tabs_coa.json from CoA's own tabId, not a handoff list.

    PYTHONPATH=. python3 tools/rebuild_spellbook_tabs.py --web-dir DIR [--apply]

WHAT WAS WRONG. The spellbook groups a character's kit into Core plus one
tab per talent tree. Which tab an ability lands in comes from
data/spellbook_tabs_coa.json, generated 30 Oct "from the CoA handoff's
per-spec ability lists". Anything the handoff did not list fell to core,
and at least one entry was simply wrong:

    templar_attack        -> templar_zealot      (the basic attack!)
    guardian_heavy_blow   -> core                (CoA says Vanguard)
    ranger_attack         -> ranger_archery
    bloodmage_attack      -> bloodmage_accursed

Kyle, 6 Nov, looking at a Templar spellbook showing Core(3) and Zealot(1):
"Is Chastise core? attack is zealot....bro."

The damage is uneven rather than uniform, which is why it went unnoticed:
Cultist put 3% of its kit in Core and Felsworn 72%. A class whose early
abilities all fell through reads as "nothing is sorted"; a class where
they all matched reads fine.

THE REAL SOURCE. allthingscoa.com serves CoA's builder data as JSON, one
file per class, every node carrying a `tabId`. data/classes-meta.js maps
those ids to spec names and states `classTab: 87` - the shared Class tree
every CoA class has, which is exactly what our Core tab is. So CoA states
the answer for all 7,224 nodes instead of us inferring it from a list.

    node.tabId == <class>.classTab   -> "core"
    node.tabId == <spec>.tab         -> that spec's tree

WHAT STAYS CORE, CORRECTLY. CoA has no "Attack", "Shoot" or "Wand" - auto
attack is not a talent in WoW and never appears in a builder. Those are
ours (universal_shoot, universal_wand, <class>_attack) and Core is their
right home. An ability CoA does not know is left in core rather than
guessed, and reported.

NAME MATCHING IS STRICT, same as tools/fill_talent_icons_from_coa.py:
case, punctuation and whitespace only. A tab is a quieter thing to get
wrong than an icon - nobody notices a misfiled spell as fast as a wrong
picture - so a fuzzy match here would rot for longer.
"""

import argparse
import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data/spellbook_tabs_coa.json"

#: Our class-file prefix -> allthingscoa slug. Our nine vanilla-derived
#: classes have no CoA counterpart and keep CLASS_SCHOOL_TREE_MAP.
SLUGS = {
    "barbarian": "barbarian", "bloodmage": "bloodmage",
    "chronomancer": "chronomancer", "cultist": "cultist",
    "felsworn": "felsworn", "guardian": "guardian",
    "knight_of_xoroth": "knight-of-xoroth", "necromancer": "necromancer",
    "primalist": "primalist", "pyromancer": "pyromancer",
    "ranger": "ranger", "reaper": "reaper", "runemaster": "runemaster",
    "starcaller": "starcaller", "stormbringer": "stormbringer",
    "sun_cleric": "sun-cleric", "templar": "templar", "tinker": "tinker",
    "venomancer": "venomancer", "witch_doctor": "witch-doctor",
    "witch_hunter": "witch-hunter",
}

#: CoA spec name -> our tree suffix, where the two drifted apart. Both
#: were inferred from the data rather than guessed: every talent in one of
#: our trees was looked up by name in CoA's and voted on its tabId.
#:
#:     runemaster_engravement   Runic 16, Arcane 2
#:     runemaster_glyphic       Arcane 25
#:     runemaster_riftblade     Riftblade 19, Runic 2
#:
#: Without these, 25 abilities whose spec CoA states plainly fell back to
#: core because "runemaster_arcane" is not a tree we have.
SPEC_ALIASES = {
    "runemaster": {"runic": "engravement", "arcane": "glyphic"},
    "witch_doctor": {"shadow_hunting": "shadowhunting"},
}

#: The tab key for a class's shared, non-spec abilities. CoA has exactly
#: this: classTab 87, a Class tree sitting alongside the three spec trees.
#: We used to fold it into Core, which is why Core filled with real combat
#: spells. Kyle, 6 Nov: "core should ONLY be stuff like auto attack, wand,
#: shoot, eventually things like racial skills etc."
CLASS_TAB = "class"

#: Display class name in the output file -> our class-file prefix.
DISPLAY = {
    "Barbarian": "barbarian", "Bloodmage": "bloodmage",
    "Chronomancer": "chronomancer", "Cultist": "cultist",
    "Felsworn": "felsworn", "Guardian": "guardian",
    "Knight of Xoroth": "knight_of_xoroth", "Necromancer": "necromancer",
    "Primalist": "primalist", "Pyromancer": "pyromancer",
    "Ranger": "ranger", "Reaper": "reaper", "Runemaster": "runemaster",
    "Starcaller": "starcaller", "Stormbringer": "stormbringer",
    "Sun Cleric": "sun_cleric", "Templar": "templar", "Tinker": "tinker",
    "Venomancer": "venomancer", "Witch Doctor": "witch_doctor",
    "Witch Hunter": "witch_hunter",
}


def norm(s):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", (s or "").lower())).strip()


def parse_meta(path):
    """slug -> {tabId: tree_suffix or "core"}, from classes-meta.js."""
    text = path.read_text(encoding="utf-8")
    out = {}
    blocks = re.findall(
        r'\{\s*name:\s*"([^"]+)",\s*slug:\s*"([^"]+)",\s*classTab:\s*(\d+)'
        r'.*?specs:\s*\[(.*?)\]\s*\}', text, re.S)
    for _name, slug, class_tab, specs in blocks:
        tabs = {int(class_tab): "core"}
        for spec_name, _role, tab in re.findall(
                r'\{\s*name:\s*"([^"]+)",\s*role:\s*"([^"]+)",\s*tab:\s*(\d+)',
                specs):
            tabs[int(tab)] = re.sub(r"[^a-z0-9]+", "_", spec_name.lower()).strip("_")
        out[slug] = tabs
    return out


def our_abilities(prefix):
    """ability_id -> name, for one of our class ability files."""
    path = ROOT / f"data/abilities/{prefix}.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    entries = doc.get("abilities", doc)
    if isinstance(entries, dict):
        entries = list(entries.values())
    return {a["ability_id"]: a.get("name") for a in entries
            if isinstance(a, dict) and a.get("ability_id")}


def our_trees(prefix):
    return {p.stem for p in (ROOT / "data/talents").glob(f"{prefix}_*.json")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--web-dir", required=True, type=Path)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    web = args.web_dir
    meta = parse_meta(web / "data/classes-meta.js")
    old = json.loads(OUT.read_text(encoding="utf-8"))

    result, stats, unknown, retabbed = {}, [], [], []
    for display, prefix in sorted(DISPLAY.items()):
        slug = SLUGS[prefix]
        tabs = meta.get(slug, {})
        trees = our_trees(prefix)

        # CoA talent/ability name -> tree_id (or "core")
        coa = {}
        for node in json.loads((web / f"data/classes/{slug}.json").read_text(encoding="utf-8")):
            if not isinstance(node, dict) or not node.get("name"):
                continue
            suffix = tabs.get(node.get("tabId"))
            if suffix is None:
                continue
            if suffix == "core":
                # CoA's shared Class tree. NOT our Core - see CLASS_TAB.
                coa.setdefault(norm(node["name"]), CLASS_TAB)
                continue
            suffix = SPEC_ALIASES.get(prefix, {}).get(suffix, suffix)
            tree_id = f"{prefix}_{suffix}"
            # Only trust a tree we actually have. CoA spec names and ours
            # agree almost everywhere, but a rename on either side must
            # fall back to core rather than invent a tab the spellbook
            # would then render empty.
            coa[norm(node["name"])] = tree_id if tree_id in trees else CLASS_TAB

        mapping, n_core, n_unknown = {}, 0, 0
        for aid, name in sorted(our_abilities(prefix).items()):
            tab = coa.get(norm(name))
            if tab is None:
                # CoA has never heard of this ability. That is NOT evidence
                # it belongs in Core - it is one of ours, and the 30 Oct
                # handoff map is the only evidence that exists for it. Keep
                # what we had. Forcing these to core would move ~200
                # correctly-filed abilities into Core and recreate the exact
                # "they are all core" complaint this tool exists to fix.
                n_unknown += 1
                unknown.append((display, aid, name))
                was = old.get(display, {}).get(aid)
                # An ability of ours that the old map had in core is a
                # class ability with no spec owner, not a universal one.
                # Core is now reserved for universals only, so it belongs
                # in the class tab alongside CoA's own shared abilities.
                tab = CLASS_TAB if was in (None, "core") else was
            # ...with one exception. The universal basic attack is ours, so
            # CoA cannot vouch for it, and it is the entry that was most
            # visibly wrong (templar_attack -> templar_zealot). Auto attack
            # is never spec content.
            # The only things that stay in Core: the universal basic
            # attack and the universal ranged attacks. Racials join them
            # when they exist.
            if aid.endswith(("_attack", "_shoot", "_wand")):
                tab = "core"
            if tab == "core":
                n_core += 1
            mapping[aid] = tab
            was = old.get(display, {}).get(aid)
            if was is not None and was != tab:
                retabbed.append((display, aid, name, was, tab))
        result[display] = mapping
        stats.append((display, n_core, n_unknown, len(mapping)))

    total = sum(s[3] for s in stats)
    print(f"{total} abilities across {len(result)} CoA classes\n")
    print(f"{'class':20}{'core':>6}{'unknown':>9}{'total':>7}")
    for display, n_core, n_unknown, n in sorted(stats):
        print(f"  {display:18}{n_core:>6}{n_unknown:>9}{n:>7}")

    print(f"\nchanged tab: {len(retabbed)}")
    for display, aid, name, was, now in sorted(retabbed)[:40]:
        print(f"  {display:18}{name[:24]:26}{was:26}-> {now}")
    if len(retabbed) > 40:
        print(f"  ... and {len(retabbed) - 40} more")

    print(f"\nnot in CoA at all ({len(unknown)}) - left in core:")
    shown = collections.Counter(n for _c, _a, n in unknown)
    for name, count in shown.most_common(14):
        print(f"  {name[:34]:36}x{count}")

    if not args.apply:
        print("\n(report only; pass --apply to write)")
        return 0
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
