"""
Water textures tile without a line.

Kyle, 12 Nov: "Do notice a lot of the water tiles have that black line in them. Theyre not
cropped properly."

22 of 56 were cut from their sheets with a sliver of dock or bank along one edge, which
repeats as a dark line every 256px. tools/fix_water_seams.py trimmed, flattened and wrapped
them. This holds the result:

  - every water texture's opposite edges agree (the seam ratio: how far the first and last
    row or column differ, against a normal one-pixel step - about 1 for a tile that wraps,
    3 to 6 for the cut ones)
  - every texture on the fixer's list is on its record as processed, with the file unchanged
    since, so a re-export from the original sheet cannot quietly bring the line back
"""
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIMIT = 2.5


def main():
    spec = importlib.util.spec_from_file_location("fix", ROOT / "tools/fix_water_seams.py")
    fix = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fix)
    from PIL import Image

    water = re.compile(r"(water|sea|ocean|lake|river|pool|pond|lagoon|tide)")
    files = [p for p in (ROOT / "assets/tiles").rglob("*.png")
             if water.search(p.stem.lower())
             and any(part in ("materials", "_materials", "vot_cluster", "seamless") for part in p.parts)
             and "_previews" not in p.parts]
    files = [p for p in files if Image.open(p).size == (256, 256)]
    if len(files) < 50:
        print(f"FAIL only {len(files)} water textures found - the rig is not seeing them")
        return 1

    bad = []
    for p in sorted(files):
        if not water.search(p.stem.lower()) or "floor" in p.stem or "seam_" in p.stem:
            continue
        rows, cols = fix.seam_ratio(p)
        if rows > LIMIT or cols > LIMIT:
            bad.append(f"{p.relative_to(ROOT)}: edges disagree x{rows:.1f} top/bottom, "
                       f"x{cols:.1f} left/right - it will draw a line when tiled")

    record = json.loads(fix.RECORD.read_text(encoding="utf-8")) if fix.RECORD.exists() else {}
    for name in fix.NAMES:
        for p in fix.copies(name):
            key = str(p.relative_to(ROOT))
            if key not in record:
                bad.append(f"{key}: on the fixer's list but never processed")
            elif record[key] != hashlib.md5(p.read_bytes()).hexdigest():
                bad.append(f"{key}: changed since it was fixed - re-run tools/fix_water_seams.py "
                           f"after removing it from the record")

    print(f"{len(files)} water textures checked, {len(record)} on the fixer's record")
    if bad:
        print(f"FAIL {len(bad)}:")
        for b in bad[:25]:
            print("  ", b)
        return 1
    print("water textures OK - every one wraps.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
