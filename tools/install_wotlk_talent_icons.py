#!/usr/bin/env python3
"""Install the real 3.3.5a talent icons for the nine original classes.

    PYTHONPATH=. python3 tools/install_wotlk_talent_icons.py --repo <path> --dry-run
    PYTHONPATH=. python3 tools/install_wotlk_talent_icons.py --repo <path> --apply

SOURCE, and it is the same one the talent rebuild used:
github.com/atosfr/WotLK-3.3.5-Talent-Calculator, which Kyle supplied ("i
sent you the github too", 5 Nov 2026). Its Image/Talents/<Class>/<tree>.jpg
files are the game's own talent icons.

NOTHING IS SCRAPED FROM A WEBSITE HERE. The art comes out of a repository
Kyle pointed at, already cloned locally for the talent data. The other two
icon sources in this project are the same kind of thing: Kyle's own WoW
icon pack (tools/install_icon_pack.py) and the zamimg CDN by explicit icon
name (tools/fetch_classic_ability_icons.py).

HOW THE SHEETS WORK, measured rather than assumed:
  - Each sheet is ONE TREE. Cells are 36x36, laid out in a single column
    sequence left to right, and the sheet is 72 tall = TWO ROWS.
  - ROW 0 IS COLOUR, ROW 1 IS GREYSCALE - the learned and unlearned states.
    We want row 0. A contact sheet of Druid Balance confirmed it by eye.
  - width / 36 equals the tree's talent count for ALL 27 classic trees,
    checked against data/reference/wotlk/*.json. That check is re-run here
    and the tree is SKIPPED if it ever stops holding, because a sheet that
    has drifted from the data would silently install wrong art for every
    talent in the tree.
  - The index is NOT inferred from file order. Each talent in the repo's
    Talents.json carries an explicit "icon" field, and that is what is
    used, so a reordered list cannot shift every icon by one.

MATCHING TO OUR TALENTS. Our rebuilt nodes mostly keep the real talent's
display name, so the match is by name (normalised). Where a node was
deliberately renamed because the real talent could not be built as written,
an explicit alias is needed - those are listed in ALIASES below, each with
the reason. Any talent that matches nothing is REPORTED, never guessed:
installing a plausible-looking icon under the wrong id is worse than a
blank, because a blank is visible and a wrong icon is not.

OUTPUT FORMAT follows the existing talent art exactly: 56x56 RGBA PNG at
assets/icons/talents/<talent_id>.png, upscaled from the 36x36 source with
LANCZOS. The upscale is real quality loss and is the honest cost of this
source; the alternative is a flat coloured square, which is what 702
abilities and talents currently render.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT_DIR = ROOT / "assets/icons/talents"
CELL = 36
TARGET = 56

#: Our tree id -> (repo class folder, repo tree name)
TREES = {
    "druid_balance": ("Druid", "Balance"),
    "druid_feral": ("Druid", "Feral Combat"),
    "druid_restoration": ("Druid", "Restoration"),
    "hunter_beast_mastery": ("Hunter", "Beast Mastery"),
    "hunter_marksmanship": ("Hunter", "Marksmanship"),
    "hunter_survival": ("Hunter", "Survival"),
    "mage_arcane": ("Mage", "Arcane"),
    "mage_fire": ("Mage", "Fire"),
    "mage_frost": ("Mage", "Frost"),
    "paladin_holy": ("Paladin", "Holy"),
    "paladin_protection": ("Paladin", "Protection"),
    "paladin_retribution": ("Paladin", "Retribution"),
    "priest_discipline": ("Priest", "Discipline"),
    "priest_holy": ("Priest", "Holy"),
    "priest_shadow": ("Priest", "Shadow"),
    "rogue_assassination": ("Rogue", "Assassination"),
    "rogue_combat": ("Rogue", "Combat"),
    "rogue_subtlety": ("Rogue", "Subtlety"),
    "shaman_elemental": ("Shaman", "Elemental"),
    "shaman_enhancement": ("Shaman", "Enhancement"),
    "shaman_restoration": ("Shaman", "Restoration"),
    "warlock_affliction": ("Warlock", "Affliction"),
    "warlock_demonology": ("Warlock", "Demonology"),
    "warlock_destruction": ("Warlock", "Destruction"),
    "warrior_arms": ("Warrior", "Arms"),
    "warrior_fury": ("Warrior", "Fury"),
    "warrior_protection": ("Warrior", "Protection"),
}

#: our node name -> the REAL talent whose icon it should wear, for nodes
#: renamed during the rebuild because the real talent was unbuildable.
#: Keyed by tree so a name reused across classes cannot collide.
#: THREE OF THESE ARE LITERAL TYPOS IN THE GAME'S OWN DBC DATA, not in our
#: names - "Survival Instincs" is missing its t, "Improved Scubbus" its c,
#: and "Everşasting Affliction" has a Turkish s-cedilla where an l belongs.
#: They are matched here rather than "corrected" in the reference, because
#: the reference is meant to be a faithful dump of what the game shipped.
ALIASES = {
    "druid_feral": {
        "Survival Instincts": "Survival Instincs",
    },
    "warlock_demonology": {
        "Improved Succubus": "Improved Scubbus",
        # Renamed in the rebuild: Healthstones need an item system that does
        # not exist, so the node was retargeted onto Demon Armor. It still
        # occupies Improved Healthstone's slot and wears its icon.
        "Improved Demon Armor": "Improved Healthstone",
    },
    "warlock_affliction": {
        "Everlasting Affliction": "Everşasting Affliction",
        # Drain Soul does not exist; only the mana-on-kill half was kept.
        "Soul Harvest": "Improved Drain Soul",
    },
    "priest_holy": {
        "Desperate Prayer": "Desperate Power",
    },
    "hunter_beast_mastery": {
        # The tree's 1-point capstone, renamed during the rebuild.
        "Marked for Death": "Beast Mastery",
    },
    "mage_frost": {
        "Elemental Precision": "Precision",
        # Ours is the ability unlock; the real tree's node improves it.
        "Blizzard": "Improved Blizzard",
    },
}

#: Nodes that correctly match NOTHING and must never be aliased. Listed so
#: the unmatched report can be read as "expected" vs "needs a look".
#:   mage_frost     - the 9 homebrew Cryotherapist healing talents
#:   shaman_enhancement - the 7 homebrew tank talents
#:   druid_feral Dire Bear Form - not a WotLK talent; the project gates the
#:                form behind one, so there is no real icon to inherit
#:   priest_shadow Mind Sear, shaman_restoration Call of the Ancestors -
#:                project-specific ability unlocks with no real counterpart
#: Each of these would rather render a blank than wear another talent's art.
EXPECTED_UNMATCHED = 19

NORM = re.compile(r"[^a-z0-9]+")


def norm(s):
    return NORM.sub("", (s or "").lower())


def load_repo(repo):
    data = json.loads((Path(repo) / "Talents.json").read_text())
    classes = data if isinstance(data, list) else list(data.values())[0]
    out = {}
    for cls in classes:
        for tree in cls.get("trees", []):
            out[(cls["name"], tree["name"])] = tree
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    from PIL import Image

    repo = Path(args.repo)
    trees = load_repo(repo)

    installed = skipped = 0
    unmatched = []
    tree_skips = []

    for tree_id, (cls, tree_name) in sorted(TREES.items()):
        tpath = ROOT / "data/talents" / f"{tree_id}.json"
        if not tpath.exists():
            tree_skips.append((tree_id, "no such tree file"))
            continue
        spec = trees.get((cls, tree_name))
        if spec is None:
            tree_skips.append((tree_id, f"repo has no {cls}/{tree_name}"))
            continue

        sheet_path = repo / "Image/Talents" / cls.replace(" ", "") / spec["spriteSheet"]
        if not sheet_path.exists():
            tree_skips.append((tree_id, f"missing sheet {sheet_path.name}"))
            continue
        sheet = Image.open(sheet_path).convert("RGBA")

        # The integrity check described in the docstring. A sheet whose
        # width no longer matches the tree's talent count has drifted, and
        # installing from it would misfile every icon in the tree.
        n_cells = sheet.width // CELL
        if n_cells != len(spec["talents"]):
            tree_skips.append((tree_id,
                               f"sheet has {n_cells} cells but the tree has "
                               f"{len(spec['talents'])} talents - NOT sliced"))
            continue

        by_name = {norm(t["name"]): t for t in spec["talents"]}
        aliases = {norm(k): norm(v) for k, v in ALIASES.get(tree_id, {}).items()}

        nodes = json.loads(tpath.read_text())["nodes"]
        for node in nodes:
            tid = node["talent_id"]
            key = norm(node.get("name"))
            real = by_name.get(key) or by_name.get(aliases.get(key, ""))
            if real is None:
                unmatched.append((tree_id, node.get("name"), tid))
                continue

            idx = real.get("icon")
            if idx is None or not (0 <= idx < n_cells):
                unmatched.append((tree_id, node.get("name"), f"{tid} (bad icon index {idx})"))
                continue

            cell = sheet.crop((idx * CELL, 0, (idx + 1) * CELL, CELL))
            cell = cell.resize((TARGET, TARGET), Image.LANCZOS)
            dest = OUT_DIR / f"{tid}.png"
            if args.apply:
                OUT_DIR.mkdir(parents=True, exist_ok=True)
                cell.save(dest)
            installed += 1

    print()
    print(f"  {installed} talent icons {'INSTALLED' if args.apply else 'would be installed'}")
    if tree_skips:
        print(f"\n  {len(tree_skips)} TREE(S) SKIPPED ENTIRELY:")
        for t, why in tree_skips:
            print(f"      {t}: {why}")
    if unmatched:
        print(f"\n  {len(unmatched)} node(s) matched no real talent - LEFT ALONE, not guessed:")
        for tree_id, name, tid in unmatched:
            print(f"      {tree_id:<24} {name}")
    print()
    if not args.apply:
        print("  dry run - nothing written. Re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
