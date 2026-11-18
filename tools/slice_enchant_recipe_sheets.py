#!/usr/bin/env python3
"""Slice Kyle's enchanting sheets (EN1-EN4) and recipe-scroll sheets (RC2, RC3) and point the game at them. Idempotent.

    PYTHONPATH=. python3 tools/slice_enchant_recipe_sheets.py

The cell lists are tools/enchant_recipe_art.py's (docs/enchanting_recipe_art_prompts.md). Kyle delivered EN1-EN4,
RC2 and RC3 on 17 Nov 2026; RC1 (Blacksmithing, Leatherworking, Tailoring and Woodworking's first three) is in the
backlog, and those scrolls keep their profession's one picture until it lands.

WHERE THEY GO
  enchant scrolls   assets/gathering_nodes/enchanting/<stem>.png (96px), and each enchant's material icon_id in
                    data/gathering/materials.json (tools/build_enchanting.py reads the same map, so a rebuild keeps it)
  enchanted wands   assets/icons/gear/gear_<stem>.png, as the wand recipes' output icon_id (world/crafted_items.build)
  enchanting oils   assets/icons/consumables/<oil>.png, which entities/consumable_icons.icon_for picks up by name
  recipe scrolls    assets/icons/recipes/<stem>.png (96px); world/recipe_manager picks the scroll by profession,
                    skill grade and found/bought, falling back to the profession's old picture

THE KEY. Kyle: "the background is pink-magenta rather than guaranteed pure #FF00FF. Check the chroma key before
slicing." So each sheet's key is measured off its own corners: the clear point sits just under the background's
own magenta strength rather than at a fixed 210, which left a pink film on these sheets.

RC2 CAME OUT OF ORDER. The model drew six Woodworking cells where the list has eight (no epic), and one extra each for
Engineering and Jewelcrafting, so RC2 is mapped by what's actually in each cell (RC2_DRAWN) rather than by number.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.slice_crafting_fix_icons import objects  # noqa: E402
from tools import enchant_recipe_art as ART  # noqa: E402

SHEETS = ROOT / "tools/icon_sheets"
ENCH_DIR = ROOT / "assets/gathering_nodes/enchanting"
GEAR = ROOT / "assets/icons/gear"
CONS = ROOT / "assets/icons/consumables"
RECIPES = ROOT / "assets/icons/recipes"
SIZE = 96

#: RC2 by what's drawn, cell by cell (1-based): the stems each cell stands for. Cell 7 (a parchment gear sketch that
#: matches nothing on the list) is left out.
RC2_DRAWN = {
    1: ["recipe_woodworking_4_found"], 2: ["recipe_woodworking_5_found"],
    3: ["recipe_woodworking_1_bought", "recipe_woodworking_2_bought"], 4: ["recipe_woodworking_3_bought"],
    5: ["recipe_woodworking_4_bought"], 6: ["recipe_woodworking_5_bought"],
    8: ["recipe_engineering_epic"],
    **{9 + i: [f"recipe_engineering_{i + 1}_found"] for i in range(5)},
    **{14 + i: [f"recipe_engineering_{i + 1}_bought"] for i in range(5)},
    19: ["recipe_jewelcrafting_1_found"], 21: ["recipe_jewelcrafting_2_found"],
    22: ["recipe_jewelcrafting_3_found"], 23: ["recipe_jewelcrafting_4_found"], 24: ["recipe_jewelcrafting_5_found"],
    **{25 + i: [f"recipe_jewelcrafting_{i + 1}_bought"] for i in range(5)},
    30: ["recipe_jewelcrafting_epic"],
    **{31 + i: [f"recipe_alchemy_{i + 1}_found"] for i in range(5)},
    36: ["recipe_alchemy_1_bought"],
}


def key(cell, clear):
    """Magenta out, measured: solid below 120, clear at `clear` (the sheet's own background strength less a margin)."""
    a = np.asarray(cell.convert("RGB"), np.float32)
    mag = np.minimum(a[..., 0], a[..., 2]) - a[..., 1]
    alpha = np.clip((clear - mag) / (clear - 120.0), 0.0, 1.0)
    solid = alpha > 0.5
    lab, n = ndi.label(ndi.binary_dilation(solid, iterations=6))
    if n > 1:
        sizes = ndi.sum(solid, lab, range(1, n + 1))
        alpha = alpha * (lab == (1 + int(np.argmax(sizes))))
    edge = ndi.binary_dilation(alpha < 0.95, iterations=3) & (alpha > 0)
    spill = np.clip(mag, 0, None) * edge
    a[..., 0] -= spill
    a[..., 2] -= spill
    return Image.fromarray(np.dstack([np.clip(a, 0, 255), alpha * 255]).astype(np.uint8), "RGBA")


def sheet_clear(sheet):
    a = np.asarray(sheet, np.float32)
    h, w = a.shape[:2]
    border = np.concatenate([a[:12].reshape(-1, 3), a[-12:].reshape(-1, 3), a[:, :12].reshape(-1, 3),
                             a[:, -12:].reshape(-1, 3)])
    mag = np.minimum(border[:, 0], border[:, 2]) - border[:, 1]
    return float(np.clip(np.percentile(mag, 2) - 12, 170, 215))


def cut(sheet, box, clear):
    W, H = sheet.size
    x0, y0, x1, y1 = box
    pad = 6
    im = key(sheet.crop((max(0, x0 - pad), max(0, y0 - pad), min(W, x1 + pad), min(H, y1 + pad))), clear)
    im = im.crop(im.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox())
    side = int(max(im.size) * 1.06) + 2
    sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    sq.paste(im, ((side - im.size[0]) // 2, (side - im.size[1]) // 2))
    return sq.resize((SIZE, SIZE), Image.LANCZOS)


def enchant_dest(stem):
    if stem.startswith("ench_") and stem.endswith("_wand"):
        return GEAR / f"gear_{stem}.png"
    if stem.startswith("enchant_scroll_"):
        return ENCH_DIR / f"{stem}.png"
    return CONS / f"{stem}.png"


def slice_enchanting():
    done = {}
    for i, cells in enumerate(ART.enchant_cells(), 1):
        sheet = Image.open(SHEETS / f"enchanting_en{i}.png").convert("RGB")
        clear = sheet_clear(sheet)
        boxes = objects(sheet, 6, 6)
        for k, (stem, _d, ids) in enumerate(cells):
            slot = (k % 6, k // 6)
            if slot not in boxes:
                raise SystemExit(f"EN{i} cell {k + 1} ({stem}): nothing found")
            cut(sheet, boxes[slot], clear).save(enchant_dest(stem))
            done[stem] = ids
    return done


def slice_recipes():
    done = []
    sheet = Image.open(SHEETS / "recipes_rc2.png").convert("RGB")
    clear, boxes = sheet_clear(sheet), objects(sheet, 6, 6)
    for cell, stems in RC2_DRAWN.items():
        im = cut(sheet, boxes[((cell - 1) % 6, (cell - 1) // 6)], clear)
        for s in stems:
            im.save(RECIPES / f"{s}.png")
            done.append(s)
    sheet = Image.open(SHEETS / "recipes_rc3.png").convert("RGB")
    clear, boxes = sheet_clear(sheet), objects(sheet, 6, 6)
    for k, (stem, _d) in enumerate(ART.recipe_cells()[2]):
        im = cut(sheet, boxes[(k % 6, k // 6)], clear)
        dest = GEAR / f"{stem}.png" if stem.startswith("gear_") else RECIPES / f"{stem}.png"
        im.save(dest)
        done.append(stem)
    return done


def point_data(enchants):
    """Enchant materials and wand recipes at their new art."""
    p = ROOT / "data/gathering/materials.json"
    raw = p.read_text(encoding="utf-8")
    d = json.loads(raw)
    mats = d["materials"] if "materials" in d else d
    by_id = ART.enchant_icon_map()
    n = 0
    for mid, m in mats.items():
        if isinstance(m, dict) and m.get("material_type") == "enchant_scroll" and mid in by_id:
            if m.get("icon_id") != by_id[mid]:
                m["icon_id"] = by_id[mid]
                n += 1
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + ("\n" if raw.endswith("\n") else ""), encoding="utf-8")
    p = ROOT / "data/enchanting/recipes.json"
    raw = p.read_text(encoding="utf-8")
    d = json.loads(raw)
    w = 0
    for rid, r in d["recipes"].items():
        out = r.get("output", {})
        if out.get("weapon_type") == "wand":
            icon = ART.wand_icon(rid)
            if icon and out.get("icon_id") != icon:
                out["icon_id"] = icon
                w += 1
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + ("\n" if raw.endswith("\n") else ""), encoding="utf-8")
    return n, w


def point_warhide():
    """Timbermaw Warhide's own art (RC3's second-last cell): its recipe and its crafted_icons.json pick."""
    stem = "gear_epic_crafted_timbermaw_warhide"
    if not (GEAR / f"{stem}.png").exists():
        return 0
    n = 0
    for f in ("data/leatherworking/recipes.json", "data/items/crafted_icons.json"):
        p = ROOT / f
        raw = p.read_text(encoding="utf-8")
        d = json.loads(raw)
        if "icons" in d:
            n += d["icons"].get("Timbermaw Warhide") != stem
            d["icons"]["Timbermaw Warhide"] = stem
        else:
            for r in d.get("recipes", {}).values():
                it = (r.get("output") or {}).get("item") or {}
                if it.get("name") == "Timbermaw Warhide" and it.get("icon_id") != stem:
                    it["icon_id"] = stem
                    n += 1
        p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + ("\n" if raw.endswith("\n") else ""),
                     encoding="utf-8")
    return n


def main():
    ench = slice_enchanting()
    rec = slice_recipes()
    n, w = point_data(ench)
    point_warhide()
    print(f"{len(ench)} enchanting icons, {len(rec)} recipe icons; {n} enchant materials and {w} wand recipes moved")


if __name__ == "__main__":
    main()
