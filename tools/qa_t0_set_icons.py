#!/usr/bin/env python3
"""T0 set pieces show their own art, and every version of a piece has its own picture.

    PYTHONPATH=. python3 tools/qa_t0_set_icons.py

Kyle sent seven of the eight set sheets on 13 Nov 2026 (tools/slice_t0_set_icons.py). FOUR CLAIMS:
  1. Every set whose sheet is in tools/icon_sheets has all eight icons, 64x64 with alpha.
  2. Every OTHER version of such a set has its own recoloured icon for all eight slots, and it is
     not the same picture as the first version's.
  3. gear_sets.make_piece() hands out the right icon, exchange() swaps it, and a piece loaded from
     an old save (no icon_id) picks its icon up.
  4. A set with no sheet yet makes a piece with no icon, which draws the plain slot box - it does
     not point at a file that is not there.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))


def main():
    from PIL import Image
    import slice_t0_set_icons as T
    from world import gear_sets as G
    from entities.item import Item

    sets = json.loads((ROOT / "data/items/gear_sets.json").read_text())["sets"]
    bad, drawn, waiting, files = [], [], [], 0
    for n, classes in T.SHEETS.items():
        have = (T.SHEET_DIR / f"t0_sets_sheet{n}.png").exists()
        for c in classes:
            (drawn if have else waiting).append(T.set_id(c))
    if set(drawn) | set(waiting) != set(sets):
        bad.append(f"sheets do not cover the sets: {sorted(set(sets) ^ (set(drawn) | set(waiting)))}")

    for sid in drawn:
        versions = list(sets[sid]["variants"])
        for slot in T.SLOTS:
            base = T.OUT / f"{sid}_{slot}.png"
            if not base.exists():
                bad.append(f"{base.name} missing")
                continue
            im = Image.open(base)
            files += 1
            if im.size != (T.SIZE, T.SIZE) or im.mode != "RGBA":
                bad.append(f"{base.name}: {im.size} {im.mode}")
            for v in versions[1:]:
                alt = T.OUT / f"{sid}_{slot}__{v}.png"
                if not alt.exists():
                    bad.append(f"{alt.name} missing")
                elif Image.open(alt).tobytes() == im.tobytes():
                    bad.append(f"{alt.name} is the same picture as the first version")
                else:
                    files += 1
            piece = G.make_piece(sid, slot)
            if piece.icon_id != f"{sid}_{slot}":
                bad.append(f"{sid} {slot}: make_piece gave icon {piece.icon_id!r}")
            if len(versions) > 1:
                G.exchange(piece, versions[1])
                want = f"{sid}_{slot}__{versions[1]}"
                if piece.icon_id != want:
                    bad.append(f"{sid} {slot}: after exchange the icon is {piece.icon_id!r}, wanted {want!r}")
                old = Item.from_dict({**piece.to_dict(), "icon_id": None})
                if old.icon_id != want:
                    bad.append(f"{sid} {slot}: an old save loads with icon {old.icon_id!r}")
    for sid in waiting:
        piece = G.make_piece(sid, "chest")
        if piece.icon_id is not None:
            bad.append(f"{sid}: no sheet yet but the chest has icon {piece.icon_id!r}")

    print(f"{len(drawn)} sets drawn ({files} icon files), {len(waiting)} waiting on art: {', '.join(waiting) or 'none'}")
    for b in bad[:30]:
        print("  FAIL", b)
    print("\nT0 set icons OK - every drawn piece and version has its picture." if not bad else f"\n{len(bad)} problems")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
