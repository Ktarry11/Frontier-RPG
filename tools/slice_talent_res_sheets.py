#!/usr/bin/env python3
"""Slice the two missing-talent icon sheets and the res spell sheet (Kyle, 12 Nov 2026).

    python3 tools/slice_talent_res_sheets.py [--preview OUT.png]

Prompts and cell order: claude/talent_icon_prompts_missing_65.md and
claude/res_spell_icon_prompts.md. NAMES below is those tables, and they must stay in step.

These are SQUARE icons with their own painted border, so unlike the gem and material sheets
nothing is keyed out: the magenta is only used to FIND each square. Keying would punch holes
in every icon with violet or pink in it (the void rift, the soul shard, the crowned spider).
Each square is cropped from the untouched image, trimmed a few pixels to lose the pink
fringe on its outer edge, and saved opaque at 56x56 like every other talent icon.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
SHEETS = ROOT / "tools" / "icon_sheets"
SIZE = 56
TRIM = 0.03          # share of the square's side shaved off each edge

TALENTS_1 = """
    bloodmage_fleshweaver_hemorrhagic_shock chronomancer_infinite_end_of_time chronomancer_time_compounded_moment
    cultist_heretic_blasphemy druid_restoration_wild_abundance knight_of_xoroth_war_pestilence_of_death
    necromancer_animation_grave_harvest paladin_holy_lights_fury priest_discipline_exalted_grace
    priest_holy_holy_power primalist_grovekeeper_verdant_fury primalist_wildwalker_pulverize
    primalist_wildwalker_primal_instincts pyromancer_draconic_draconic_fury pyromancer_flameweaving_conflagration
    ranger_farstrider_command_of_the_farstrider runemaster_riftblade_rift_resonance shaman_restoration_surging_tides
    starcaller_moon_priest_lunar_fury stormbringer_lightning_thunderous stormbringer_wind_gale_force
    sun_cleric_blessings_radiant_zeal templar_crusader_templar_zeal tinker_invention_field_medic
    venomancer_vizier_virulent_insight warlock_affliction_withering_agony warlock_demonology_demonic_fury
    witch_doctor_brewing_potent_brew knight_of_xoroth_war_burning_blade templar_crusader_crusading_strike
    primalist_wildwalker_pulverizing_strikes necromancer_animation_depravity bloodmage_accursed_blood_pact_talent
    bloodmage_accursed_cursed_blood bloodmage_accursed_crimson_terror_acc bloodmage_eternal_shadow_pact_eternal""".split()
TALENTS_2 = """
    bloodmage_fleshweaver_blood_rituals chronomancer_infinite_temporal_decay chronomancer_infinite_erosion
    chronomancer_time_patient_mending guardian_gladiator_mace_training guardian_inspiration_war_drums
    knight_of_xoroth_defiance_hellish_rebuke knight_of_xoroth_defiance_hellfire_imp_mastery knight_of_xoroth_hellfire_pestilence_of_apocalypse
    knight_of_xoroth_war_fiend knight_of_xoroth_war_warbringer knight_of_xoroth_war_skulltaker_mastery
    primalist_grovekeeper_aftershock primalist_mountain_king_everythings_a_nail pyromancer_flameweaving_lifebinders_fire
    pyromancer_incineration_residual_power ranger_archery_serrations ranger_brigand_assassin
    reaper_soul_the_jailers_call stormbringer_lightning_voltaic_bursts templar_crusader_titanstrike_mastery
    templar_oathkeeper_paragon_of_light tinker_invention_battery_reclaimer tinker_mechanics_master_builder
    tinker_mechanics_junkyard_loiter venomancer_stalking_potency venomancer_stalking_contagion_spread
    venomancer_venom_shadras_gift witch_hunter_boltslinger_witchbane_mastery""".split()
RES = """
    priest_resurrection paladin_redemption shaman_ancestral_spirit
    druid_rebirth chronomancer_undo_the_hour cultist_called_back
    primalist_breath_of_the_wild pyromancer_rekindle starcaller_moonrise
    sun_cleric_second_dawn templar_rite_of_rising venomancer_shadras_thread
    witch_doctor_loas_bargain stormbringer_restart_the_heart status_fallen
    warlock_soulstone""".split()

#: (sheet file, columns, rows, names, where each goes)
JOBS = [
    ("talents_missing_sheet1.png", 6, 6, TALENTS_1, lambda n: ROOT / "assets/icons/talents"),
    ("talents_missing_sheet2.png", 6, 5, TALENTS_2, lambda n: ROOT / "assets/icons/talents"),
    # two spares on the res sheet are not abilities: the fallen marker and a Soulstone
    ("res_spells_sheet.png", 4, 4, RES,
     lambda n: ROOT / ("assets/icons/spares" if n in ("status_fallen", "warlock_soulstone")
                       else "assets/icons/abilities")),
]


def squares(im, cols, rows):
    """{(row, col): (x0, y0, x1, y1)} - the icon square found in each grid cell."""
    a = np.asarray(im.convert("RGB")).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    magenta = (r > 180) & (b > 180) & (g < 110)
    labels, n = ndimage.label(~magenta)
    h, w = magenta.shape
    out = {}
    for lab, sl in enumerate(ndimage.find_objects(labels), 1):
        ys, xs = sl
        if (ys.stop - ys.start) < h / rows * 0.45 or (xs.stop - xs.start) < w / cols * 0.45:
            continue                                   # a speck, not an icon
        cy, cx = (ys.start + ys.stop) / 2, (xs.start + xs.stop) / 2
        out[(int(cy // (h / rows)), int(cx // (w / cols)))] = (xs.start, ys.start, xs.stop, ys.stop)
    return out


def main():
    preview = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    tiles, problems = [], []
    for sheet, cols, rows, names, where in JOBS:
        im = Image.open(SHEETS / sheet).convert("RGB")
        found = squares(im, cols, rows)
        for i, name in enumerate(names):
            box = found.get(divmod(i, cols))
            if box is None:
                problems.append(f"{sheet}: no icon in cell {i + 1} for {name}")
                continue
            x0, y0, x1, y1 = box
            t = int(round(min(x1 - x0, y1 - y0) * TRIM))
            icon = im.crop((x0 + t, y0 + t, x1 - t, y1 - t)).resize((SIZE, SIZE), Image.LANCZOS)
            out = where(name)
            out.mkdir(parents=True, exist_ok=True)
            icon.convert("RGBA").save(out / f"{name}.png")
            tiles.append(icon)
        extra = len(found) - len(names)
        if extra > 0:
            problems.append(f"{sheet}: {extra} more icon(s) on the sheet than names")
        print(f"{sheet}: {min(len(found), len(names))}/{len(names)} sliced")
    for p in problems:
        print("  !!", p)
    if preview:
        per = 12
        sheet = Image.new("RGB", (per * (SIZE + 4), ((len(tiles) + per - 1) // per) * (SIZE + 4)), (40, 40, 48))
        for i, t in enumerate(tiles):
            sheet.paste(t, ((i % per) * (SIZE + 4) + 2, (i // per) * (SIZE + 4) + 2))
        sheet = sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST)
        sheet.save(preview)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
