#!/usr/bin/env python3
"""Fill the missing talent icons from CoA's own builder data.

    PYTHONPATH=. python3 tools/fill_talent_icons_from_coa.py \
        --web-dir /path/to/scratch/coa_web [--apply]

WHY THIS BEATS THE OCR PIPELINE. `claude/coa_reference_screenshots.md`
describes reading 7,378 JPEG screenshots with tesseract, at ~1.7s each, to
recover ability text that comes back as "Movementspced" and "1S yd range".
That was the best source available on 1 Nov.

Kyle found a better one on 6 Nov. allthingscoa.com is a CoA builder that
serves the real data as JSON, one file per class:

    https://allthingscoa.com/data/classes/<slug>.json

7,224 nodes across the 21 CoA classes, each carrying name, iconPath, tier,
position, connections, maxPoints, requiredLevel and the actual tooltip HTML.
No OCR, no ambiguity, no "%" reading as "°". The icons themselves are one
CSS sprite - coa-builder-icon.webp, a 55x55 grid of 64x64 tiles - addressed
by WoW icon name through coa-icons.css.

WHAT THIS DOES. Our 2,441 talent nodes resolve icons by filename: the
renderer looks for <talent_id>.png in assets/icons/talents/ then
assets/icons/abilities/. 542 had no file and drew the blue procedural
fallback. Matching our talent NAME against CoA's talent name resolves 522
of those 542 - 96% - because our trees were ported from theirs and kept the
names even where the mechanics were rewritten for turn-based.

So: our talent name -> CoA talent name -> iconPath -> css class -> sprite
cell -> a 64x64 PNG written as <our talent_id>.png.

THE NAME MATCH IS DELIBERATELY STRICT. Normalisation is case, punctuation
and whitespace only; no fuzzy matching. A fuzzy pass over this set offered
"Rotclaw" -> "Iron Claws" and "Axe Training" -> "Shield Training", which are
different talents that would have been given confidently wrong art. 20
unmatched talents stay unmatched and keep the fallback; they are ours, not
CoA's, and need real art or a deliberate reuse.

AMBIGUITY IS RESOLVED BY CLASS, THEN REFUSED. A handful of names appear on
more than one CoA class with different icons ("Vitality", "Enduring").
Those are matched within the class first; if the class has no such talent
and the global name is ambiguous, the talent is skipped and listed rather
than given a coin-flip icon.
"""

import argparse
import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TALENT_DIR = ROOT / "data/talents"
ICON_OUT = ROOT / "assets/icons/talents"
ABILITY_ICONS = ROOT / "assets/icons/abilities"

#: The sprite is a square grid of this many columns and rows. The CSS says
#: so itself - "background-size:5500%" means each tile is 1/55 of the
#: sheet - and it is asserted against the image rather than trusted.
SPRITE_GRID = 55

#: Our talent trees that came from a CoA class, mapped to that class's slug
#: on allthingscoa.com. Our nine vanilla-derived classes (druid, hunter,
#: mage, paladin, priest, rogue, shaman, warlock, warrior) have no CoA
#: counterpart and are matched globally only.
CLASS_SLUGS = {
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


def norm(s):
    """Case, punctuation and whitespace only. Nothing fuzzy - see docstring."""
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", (s or "").lower())).strip()


def coa_icon_class(icon_path):
    """Port of allthingscoa's js/icons.js coaIconClass().

    Its own comment records the bug worth keeping: hyphens are preserved,
    not folded to "_", because ~28 sprite classes keep them literally
    ("yogg-saronicon"). Folding them orphaned those icons silently.
    """
    if not icon_path:
        return ""
    name = icon_path.replace("/", "\\").split("\\")[-1].lower()
    name = name.lstrip("_")
    name = re.sub(r"[^a-z0-9_\-]", "_", name)
    if name[:1].isdigit():
        name = "_" + name
    return name


def parse_sprite_css(css_path):
    """css class -> (col, row) in the sprite grid."""
    text = css_path.read_text()
    step = 100.0 / (SPRITE_GRID - 1)
    cells = {}
    pattern = re.compile(
        r"\.coa-builder-icon\.([a-z0-9_\-]+)\{background-position:"
        r"(-?[\d.]+)%?\s+(-?[\d.]+)%?")
    for cls, xs, ys in pattern.findall(text):
        cells[cls] = (round(float(xs) / step), round(float(ys) / step))
    return cells


def load_coa(web_dir):
    """(name, class) and name -> set of iconPath, from the class JSON."""
    by_name = collections.defaultdict(set)
    by_class = collections.defaultdict(set)
    total = 0
    for path in sorted((web_dir / "data/classes").glob("*.json")):
        slug = path.stem
        for node in json.loads(path.read_text()):
            if not isinstance(node, dict):
                continue
            total += 1
            name, icon = node.get("name"), node.get("iconPath")
            if name and icon:
                by_name[norm(name)].add(icon)
                by_class[(slug, norm(name))].add(icon)
    return by_name, by_class, total


def our_missing():
    """Talent nodes with no icon file, as (tree, talent_id, name)."""
    have = {p.stem for p in ICON_OUT.glob("*.png")}
    have |= {p.stem for p in ABILITY_ICONS.glob("*.png")}
    out, total = [], 0
    for path in sorted(TALENT_DIR.glob("*.json")):
        tree = path.stem
        for node in json.loads(path.read_text()).get("nodes", []):
            if not isinstance(node, dict):
                continue
            total += 1
            tid = node.get("talent_id") or node.get("id")
            if tid not in have:
                out.append((tree, tid, node.get("name")))
    return out, total


def slug_for(tree):
    """Our tree name is "<class>_<spec>"; find the longest class prefix."""
    for key in sorted(CLASS_SLUGS, key=len, reverse=True):
        if tree.startswith(key + "_") or tree == key:
            return CLASS_SLUGS[key]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--web-dir", required=True, type=Path,
                    help="directory holding the fetched allthingscoa files "
                         "(data/classes/*.json, css/coa-icons.css, "
                         "css/coa-builder-icon.webp)")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    web = args.web_dir
    cells = parse_sprite_css(web / "css/coa-icons.css")
    by_name, by_class, coa_total = load_coa(web)
    missing, our_total = our_missing()

    print(f"CoA: {coa_total} nodes, {len(by_name)} distinct talent names, "
          f"{len(cells)} sprite cells")
    print(f"ours: {our_total} talent nodes, {len(missing)} with no icon\n")

    resolved, ambiguous, unmatched, no_cell = {}, [], [], []
    for tree, tid, name in missing:
        key = norm(name)
        slug = slug_for(tree)
        paths = by_class.get((slug, key)) if slug else None
        if not paths:
            paths = by_name.get(key)
        if not paths:
            unmatched.append((tree, name))
            continue
        if len(paths) > 1:
            ambiguous.append((tree, name, sorted(paths)))
            continue
        icon_path = next(iter(paths))
        cell = cells.get(coa_icon_class(icon_path))
        if cell is None:
            no_cell.append((tree, name, icon_path))
            continue
        resolved[tid] = (cell, icon_path, name)

    print(f"resolved        {len(resolved):>4}")
    print(f"ambiguous       {len(ambiguous):>4}  (same name, different icon "
          f"on another class - skipped)")
    print(f"no sprite cell  {len(no_cell):>4}  (named an icon the sheet "
          f"does not carry)")
    print(f"unmatched       {len(unmatched):>4}  (ours, not CoA's)")

    if unmatched:
        print("\nunmatched - these need real art or a deliberate reuse:")
        for tree, name in sorted(unmatched):
            print(f"  {tree:32}{name}")
    if ambiguous:
        print("\nambiguous:")
        for tree, name, paths in sorted(ambiguous)[:20]:
            print(f"  {tree:32}{name:28}{len(paths)} candidates")

    if not args.apply:
        print("\n(report only; pass --apply to write the PNGs)")
        return 0

    from PIL import Image
    sheet = Image.open(web / "css/coa-builder-icon.webp").convert("RGBA")
    w, h = sheet.size
    tile_w, tile_h = w // SPRITE_GRID, h // SPRITE_GRID
    assert w % SPRITE_GRID == 0 and h % SPRITE_GRID == 0, (
        f"sprite {w}x{h} is not a clean {SPRITE_GRID}x{SPRITE_GRID} grid")

    ICON_OUT.mkdir(parents=True, exist_ok=True)
    written = 0
    for tid, ((col, row), icon_path, name) in sorted(resolved.items()):
        box = (col * tile_w, row * tile_h, (col + 1) * tile_w,
               (row + 1) * tile_h)
        sheet.crop(box).save(ICON_OUT / f"{tid}.png")
        written += 1
    print(f"\nwrote {written} PNGs ({tile_w}x{tile_h}) to {ICON_OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
