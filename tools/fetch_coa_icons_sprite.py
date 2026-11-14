#!/usr/bin/env python3
"""
Slice the CoA builder icon sprite into per-ability PNGs.

    PYTHONPATH=. python3 tools/fetch_coa_icons_sprite.py [--all] [--out DIR]

Kyle, 2026-11-01: "lets replace CoA art with authentic art. this will never see anyone other
than me or my friends." His call, his private project, and the whole game is already a WoW fan
build - Durotar, Orgrimmar, Thrall. Noted here so the provenance is not a mystery later: these
are Blizzard icons by way of Ascension's CoA builder, not art we made.

HOW THE SPRITE WORKS. allthingscoa.com serves every icon as one 3520x3520 webp with a 55x55
grid of 64px cells, and coa-icons.css addresses it by background-position percentages at
background-size 5500%. For a 55-column sheet the percentage for column c is c/54*100 - so
1.85185% is column 1, 3.7037% is column 2, and the column is round(pct * 54 / 100). Same for
rows. That is the whole decoding.

THE ONE TRAP: 163 of the 3,019 rules write a bare `0` for an axis instead of `0%`. A regex that
requires the percent sign on both axes parses 2,856 of them and silently drops the rest - and
the dropped ones are not junk, they include ability_shaman_echooftheelements and
nhi_deathbolt_border. The percent is optional below.

By default this extracts only the icons the CoA data actually references, named by ABILITY, so
the output is a usable library rather than 3,000 files called inv_misc_something. --all dumps
the whole sheet under its raw icon names as well.
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

BASE = "https://allthingscoa.com/css/"
WORK = Path("/tmp/claude-0/coa_icons")
COA = ROOT / "data/reference/coa"
OUT_DEFAULT = ROOT / "assets/icons/coa"
GRID = 55          # 55x55 cells
CELL = 64


def fetch(name):
    WORK.mkdir(parents=True, exist_ok=True)
    dest = WORK / name
    if dest.exists() and dest.stat().st_size > 1000:
        return dest
    req = urllib.request.Request(BASE + name, headers={"User-Agent": "Mozilla/5.0"})
    dest.write_bytes(urllib.request.urlopen(req, timeout=120).read())
    return dest


def cells():
    """{css class name: (col, row)} for every icon in the sheet."""
    css = fetch("coa-icons.css").read_text(errors="replace")
    # The `%` is OPTIONAL - see the module docstring. Requiring it loses 163 icons.
    rx = re.compile(r"\.coa-builder-icon\.([a-z0-9_\-]+)\{background-position:"
                    r"([-\d.]+)%?\s+([-\d.]+)%?")
    out = {}
    for m in rx.finditer(css):
        x, y = float(m.group(2)), float(m.group(3))
        out[m.group(1)] = (round(x * (GRID - 1) / 100), round(y * (GRID - 1) / 100))
    return out


def icon_class(icon_path):
    """Mirror of the site's own coaIconClass(): "Interface\\Icons\\Foo_Bar" -> "foo_bar".

    Hyphens are kept literally - the sheet has ~28 class names with them (yogg-saronicon), and
    folding them to underscore orphans those icons silently.
    """
    if not icon_path:
        return ""
    name = icon_path.split("\\")[-1].lower().lstrip("_")
    name = re.sub(r"[^a-z0-9_\-]", "_", name)
    return ("_" + name) if name[:1].isdigit() else name


def wanted():
    """{css class: set of ability names} for everything the CoA data references."""
    out = {}
    for p in sorted(COA.glob("*.json")):
        for n in json.loads(p.read_text(encoding="utf-8")):
            cls = icon_class(n.get("iconPath"))
            if cls:
                out.setdefault(cls, set()).add(n.get("name") or "?")
    return out


def main(argv):
    from PIL import Image
    out_dir = Path(argv[argv.index("--out") + 1]) if "--out" in argv else OUT_DEFAULT
    grid = cells()
    sheet = Image.open(fetch("coa-builder-icon.webp")).convert("RGBA")
    if sheet.size != (GRID * CELL, GRID * CELL):
        print(f"  WARN sheet is {sheet.size}, expected {(GRID * CELL,) * 2}")

    need = wanted()
    missing = sorted(set(need) - set(grid))
    out_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    for cls, names in sorted(need.items()):
        if cls not in grid:
            continue
        c, r = grid[cls]
        tile = sheet.crop((c * CELL, r * CELL, (c + 1) * CELL, (r + 1) * CELL))
        if tile.getbbox() is None:          # an empty cell means the mapping is off
            continue
        for nm in names:
            slug = re.sub(r"[^a-z0-9]+", "_", nm.lower()).strip("_") or cls
            tile.save(out_dir / f"{slug}.png")
            written += 1

    print(f"{len(grid)} icons in sheet, {len(need)} referenced by CoA data, "
          f"{written} written -> {out_dir.relative_to(ROOT)}")
    if missing:
        print(f"  {len(missing)} referenced icons not in the sheet: {missing[:6]}")

    if "--all" in argv:
        raw = out_dir / "_raw"
        raw.mkdir(exist_ok=True)
        n = 0
        for cls, (c, r) in sorted(grid.items()):
            tile = sheet.crop((c * CELL, r * CELL, (c + 1) * CELL, (r + 1) * CELL))
            if tile.getbbox() is None:
                continue
            tile.save(raw / f"{cls}.png")
            n += 1
        print(f"  --all: {n} raw icons -> {raw.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
