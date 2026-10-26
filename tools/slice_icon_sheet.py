#!/usr/bin/env python3
"""Slice an 8x6 magenta-background icon sheet into 48 transparent square PNGs.

    python3 tools/slice_icon_sheet.py trash  tools/icon_sheets/vendor_trash_sheet.png
    python3 tools/slice_icon_sheet.py quest  tools/icon_sheets/quest_items_sheet.png

Each cell is keyed against #FF00FF (soft alpha ramp + magenta despill so dark outlines don't get a pink halo),
cropped to the icon's bounding box, padded to a square and resized to 96x96.  Output names come from the NAMES
tables below (same order as the prompts in claude/vendor_trash_icon_prompts.md and claude/quest_item_icon_prompts.md).
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
COLS, ROWS = 8, 6
OUT_SIZE = 96

#: Sheets whose icons must keep their RELATIVE size instead of each being
#: normalised to fill its own cell.
#:
#: The default (normalise everything) is right for the trash and quest sheets:
#: those are unrelated objects - a feather and a strongbox - where drawing the
#: feather smaller would just read as a lower-resolution icon.
#:
#: It is wrong for the potion sheet, where size IS the information. The art
#: deliberately ascends 119 -> 164px across the four healing potions and
#: 117 -> 174px across the mana line, and every elixir's greater bottle is
#: 8-20% taller than its lesser. Normalising each icon to its own bounding box
#: threw all of that away: at 32px in the bag the four healing potions became
#: indistinguishable, and most lesser/greater pairs read identically.
#:
#: In this mode every icon is scaled against the LARGEST icon on the sheet, so
#: the biggest bottles still fill their cell and the smaller ones stay visibly
#: smaller. MIN_RELATIVE_SCALE floors it so even the smallest icon stays chunky
#: rather than shrinking to a dot.
PRESERVE_SCALE = {"potions"}
MIN_RELATIVE_SCALE = 0.62

NAMES = {
    "trash": ("vendor_trash", [
        "vt_pelt", "vt_claw", "vt_fang", "vt_tusk", "vt_feathers", "vt_horn_chunk", "vt_fur_tuft", "vt_wing_membrane",
        "vt_raw_hide", "vt_chitin_plate", "vt_stinger", "vt_mandibles", "vt_venom_gland", "vt_silk_ball", "vt_egg_sac", "vt_dried_scales",
        "vt_fish_scales", "vt_fin", "vt_shell", "vt_pearl", "vt_bone", "vt_jawbone", "vt_shroud", "vt_grave_dust",
        "vt_ghost_vial", "vt_grave_ring", "vt_core", "vt_shard", "vt_slag", "vt_mote", "vt_geode", "vt_ash",
        "vt_demon_horn", "vt_brimstone", "vt_sigil", "vt_charred_claw", "vt_bark", "vt_seed_pod", "vt_thorn_vine", "vt_spore_cap",
        "vt_broken_dagger", "vt_tin_cup", "vt_locket", "vt_map_scrap", "vt_dice", "vt_idol", "vt_arrowheads", "vt_rags",
    ]),
    "quest": ("quest_items", [
        "qi_letter", "qi_scroll", "qi_ledger", "qi_page", "qi_papers", "qi_journal", "qi_chart", "qi_ticket",
        "qi_key_iron", "qi_key_brass", "qi_shackle", "qi_signet", "qi_ward_seal", "qi_dog_tag", "qi_prayer_beads", "qi_coin_pouch",
        "qi_crate", "qi_strongbox", "qi_powder_keg", "qi_seed_sack", "qi_flask", "qi_vial", "qi_clay_jar", "qi_egg",
        "qi_ore", "qi_crystal", "qi_amber", "qi_coral", "qi_gem", "qi_tablet", "qi_headstone", "qi_heart_stone",
        "qi_herbs", "qi_petals", "qi_moss", "qi_pumpkin", "qi_seed_packet", "qi_wreath", "qi_dewleaf", "qi_root",
        "qi_horn", "qi_lantern", "qi_harpoon", "qi_pennant", "qi_totem", "qi_trophy_cord", "qi_chalice", "qi_gold_thread",
    ]),
    # Potions and elixirs (claude/alchemy_art_prompts.md). Row 1 is the two
    # potion lines as four ascending sizes each; rows 2-6 are 20 elixir
    # effect-families as lesser/greater PAIRS, left cell lesser, right cell
    # greater. The middle power tier of a family reuses its lesser art -
    # see consumable_icons.py's CONSUMABLE_ICONS for which of the 68
    # consumables maps onto each of these 48 files.
    "potions": ("consumables", [
        # Row 1 - health x4 ascending, mana x4 ascending
        "healing_potion_minor", "healing_potion_standard", "healing_potion_superior", "healing_potion_mega",
        "mana_potion_minor", "mana_potion_standard", "mana_potion_superior", "mana_potion_mega",
        # Row 2 - strength, agility, intellect, spell power
        "elixir_strength_lesser", "elixir_strength_greater",
        "elixir_agility_lesser", "elixir_agility_greater",
        "elixir_intellect_lesser", "elixir_intellect_greater",
        "elixir_spellpower_lesser", "elixir_spellpower_greater",
        # Row 3 - attack power, physical crit, spell crit, haste
        "elixir_attackpower_lesser", "elixir_attackpower_greater",
        "elixir_crit_physical_lesser", "elixir_crit_physical_greater",
        "elixir_crit_spell_lesser", "elixir_crit_spell_greater",
        "elixir_haste_lesser", "elixir_haste_greater",
        # Row 4 - str+int, agi+int, stamina, spirit
        "elixir_str_int_lesser", "elixir_str_int_greater",
        "elixir_agi_int_lesser", "elixir_agi_int_greater",
        "elixir_stamina_lesser", "elixir_stamina_greater",
        "elixir_spirit_lesser", "elixir_spirit_greater",
        # Row 5 - stam+spirit fortitude, armor, mana regen, dodge
        "elixir_fortitude_lesser", "elixir_fortitude_greater",
        "elixir_armor_lesser", "elixir_armor_greater",
        "elixir_mana_regen_lesser", "elixir_mana_regen_greater",
        "elixir_dodge_lesser", "elixir_dodge_greater",
        # Row 6 - the four resistance wards
        "elixir_ward_fire_lesser", "elixir_ward_fire_greater",
        "elixir_ward_frost_lesser", "elixir_ward_frost_greater",
        "elixir_ward_nature_lesser", "elixir_ward_nature_greater",
        "elixir_ward_shadow_lesser", "elixir_ward_shadow_greater",
    ]),
}


def key_magenta(rgb):
    """-> RGBA float array. Soft alpha from distance to #FF00FF, un-mix the magenta from edge pixels, then strip the
    remaining magenta spill from pixels touching the background (fur / feather tips pick up a purple fringe)."""
    from scipy import ndimage
    mag = np.array([255.0, 0.0, 255.0])
    dist = np.sqrt(((rgb - mag) ** 2).sum(axis=2))
    alpha = np.clip((dist - 80.0) / 100.0, 0.0, 1.0)
    a = alpha[..., None]
    safe = np.maximum(a, 1e-3)
    clean = np.clip((rgb - (1.0 - a) * mag) / safe, 0, 255)
    clean = np.where(a > 0.02, clean, 0.0)
    near_bg = ndimage.binary_dilation(alpha < 0.05, iterations=3)
    spill = np.maximum(0.0, np.minimum(clean[..., 0], clean[..., 2]) - clean[..., 1] * 1.05 - 8.0)
    spill = np.where(near_bg & (alpha > 0.0), spill, 0.0)
    clean[..., 0] -= spill
    clean[..., 2] -= spill
    return np.dstack([np.clip(clean, 0, 255), alpha * 255.0])


def slice_sheet(kind, sheet_path, out_dir=None):
    from scipy import ndimage
    folder, names = NAMES[kind]
    out_dir = Path(out_dir) if out_dir else ROOT / "assets" / "icons" / folder
    out_dir.mkdir(parents=True, exist_ok=True)
    im = Image.open(sheet_path).convert("RGB")
    W, H = im.size
    rgba = key_magenta(np.asarray(im).astype(np.float64))
    cw, ch = W / COLS, H / ROWS
    # The generated sheets are not on a perfect pixel grid (rows drift by ~10px), so icons are found as connected
    # blobs (dilated so multi-part icons like dice or arrowheads stay together) and assigned to the grid cell that
    # holds their centre.
    solid = rgba[..., 3] > 24
    solid[:4, :] = solid[-4:, :] = False
    solid[:, :4] = solid[:, -4:] = False
    labels, n = ndimage.label(ndimage.binary_dilation(solid, iterations=3))
    cells = {}
    for lab in range(1, n + 1):
        ys, xs = np.where((labels == lab) & solid)
        if len(ys) < 60:
            continue
        cell = (int(ys.mean() // ch), int(xs.mean() // cw))
        cells.setdefault(cell, []).append((labels == lab) & solid)
    problems = []

    # Pass 1 - cut every icon out of the sheet. Collected rather than written
    # immediately because PRESERVE_SCALE mode needs the largest icon on the
    # whole sheet before it can size any individual one.
    crops = {}
    for idx, name in enumerate(names):
        r, c = divmod(idx, COLS)
        blobs = cells.get((r, c))
        if not blobs:
            problems.append(f"{name}: no icon found in cell {r},{c}")
            continue
        if len(blobs) > 1:
            problems.append(f"{name}: {len(blobs)} separate blobs merged")
        mask = np.logical_or.reduce(blobs)
        ys, xs = np.where(mask)
        bx0, bx1, by0, by1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        crop = rgba[by0:by1, bx0:bx1].copy()
        crop[..., 3] = np.where(mask[by0:by1, bx0:bx1], crop[..., 3], 0)
        crops[name] = crop

    preserve = kind in PRESERVE_SCALE
    sheet_max = max((max(c.shape[0], c.shape[1]) for c in crops.values()), default=1)

    # Pass 2 - pad to a square and resize.
    written = 0
    for name, crop in crops.items():
        if preserve:
            # Scale against the biggest icon on the sheet, so relative size
            # survives into the game. The square canvas is sized so this icon
            # occupies `scale` of it; the resize to OUT_SIZE then preserves
            # that fraction exactly.
            scale = max(MIN_RELATIVE_SCALE, max(crop.shape[0], crop.shape[1]) / sheet_max)
            side = int(max(crop.shape[0], crop.shape[1]) / scale) + 2
        else:
            side = int(max(crop.shape[0], crop.shape[1]) * 1.10) + 2
        canvas = np.zeros((side, side, 4))
        oy, ox = (side - crop.shape[0]) // 2, (side - crop.shape[1]) // 2
        canvas[oy:oy + crop.shape[0], ox:ox + crop.shape[1]] = crop
        img = Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8), "RGBA").resize((OUT_SIZE, OUT_SIZE), Image.LANCZOS)
        img.save(out_dir / f"{name}.png")
        written += 1
    extra = [k for k in cells if k[0] >= ROWS or k[1] >= COLS]
    print(f"{kind}: wrote {written} icons to {out_dir}")
    for p in problems + [f"stray blob in cell {k}" for k in extra]:
        print("  WARN", p)
    return problems


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in NAMES:
        sys.exit(__doc__)
    slice_sheet(sys.argv[1], sys.argv[2])
