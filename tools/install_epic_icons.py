#!/usr/bin/env python3
"""Give every named epic an icon of its own, from Kyle's WoW icon pack.

    PYTHONPATH=. python3 tools/install_epic_icons.py --pack "/path/to/WoW Icon Pack" [--apply]

Kyle, 16 Nov 2026: "every unique item in the game can only have ONE icon", then he sent the pack: "Take what you
need". The pack's larger half ("WoW Icon Pack": TBC and Wrath art) was never installed; only the Vanilla half was,
as gear_inv_*. These go in as gear_wow_<name> so gear_icons.py's procedural prefixes (gear_inv_*) can never hand one
of them to a random drop, which is what keeps them unique.

ONLY MAPPED FILES ARE COPIED (Kyle wants the repo small). Each entry is one epic's icon, chosen by eye.
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "assets/icons/gear"

#: icon_id -> pack-relative source (under "WoW Icon Pack/")
ICONS = {
    # heads, chests, shoulders, belts, bracers: the Naxxramas set art, by armour type
    "gear_wow_desecrated_leather_helm": "Miscellaneous/Desecrated_LeatherHelm.png",
    "gear_wow_desecrated_mail_helm": "Miscellaneous/Desecrated_MailHelm.png",
    "gear_wow_desecrated_cloth_chest": "Miscellaneous/Desecrated_ClothChest.png",
    "gear_wow_desecrated_mail_chest": "Miscellaneous/Desecrated_MailChest.png",
    "gear_wow_desecrated_plate_chest": "Miscellaneous/Desecrated_PlateChest.png",
    "gear_wow_desecrated_mail_shoulder": "Miscellaneous/Desecrated_MailShoulder.png",
    "gear_wow_desecrated_plate_shoulder": "Miscellaneous/Desecrated_PlateShoulder.png",
    "gear_wow_desecrated_leather_shoulder": "Miscellaneous/Desecrated_LeatherShoulder.png",
    "gear_wow_desecrated_leather_belt": "Miscellaneous/Desecrated_LeatherBelt.png",
    "gear_wow_desecrated_plate_belt": "Miscellaneous/Desecrated_PlateBelt.png",
    "gear_wow_desecrated_cloth_belt": "Miscellaneous/Desecrated_ClothBelt.png",
    "gear_wow_desecrated_cloth_bracer": "Miscellaneous/Desecrated_ClothBracer.png",
    "gear_wow_circlet_gold": "Armour/96_1.png",
    # bracers and gloves
    "gear_wow_bracer_cloth_beads": "Armour/100_1.png",
    "gear_wow_bracer_mail_blue": "Armour/94_2.png",
    "gear_wow_bracer_plate_gold": "Armour/94_1.png",
    "gear_wow_bracer_leather_coil": "Armour/88_2.png",
    "gear_wow_bracer_plate_iron": "Armour/86_2.png",
    "gear_wow_gauntlet_plate_blue": "Armour/87_2.png",
    "gear_wow_gauntlet_mail": "Armour/89_2.png",
    "gear_wow_glove_cloth_violet": "Armour/84_1.png",
    "gear_wow_gauntlet_plate_brown": "Armour/113_1.png",
    "gear_wow_glove_leather_dark": "Armour/104_1.png",
    "gear_wow_glove_leather_grey": "Armour/93_1.png",
    "gear_wow_glove_leather_red": "Armour/101_2.png",
    # boots and legs
    "gear_wow_boots_cloth_grey": "Armour/Cloth_14.png",
    "gear_wow_boots_mail_bronze": "Armour/Chain_09_1.png",
    "gear_wow_boots_leather_fur": "Armour/Leather01.png",
    "gear_wow_boots_cloth_tan": "Armour/Cloth_13.png",
    "gear_wow_boots_plate_star": "Armour/Plate_14_1.png",
    "gear_wow_boots_mail_fur": "Armour/Mail_08_2.png",
    "gear_wow_boots_plate_greaves": "Armour/Plate_05.png",
    "gear_wow_boots_plate_silver": "Armour/Plate_02.png",
    "gear_wow_boots_leather_strap": "Armour/Leather_03B.png",
    "gear_wow_legs_plate_march": "Armour/Plate_09_1.png",
    "gear_wow_legs_cloth_violet": "Armour/Cloth_37_1.png",
    "gear_wow_legs_mail_pack": "Armour/Mail_15_1.png",
    "gear_wow_legs_mail_bronze": "Armour/Mail_20.png",
    "gear_wow_legs_leather_red": "Armour/Leather_19.png",
    "gear_wow_legs_plate_silver": "Armour/Plate_13.png",
    "gear_wow_legs_mail_wind": "Armour/Mail_19.png",
    "gear_wow_legs_leather_tally": "Armour/Leather_20.png",
    # weapons, relics, books, cloaks, trinkets
    "gear_wow_fist_hooked": "Weapons/Hand_05.png",
    "gear_wow_bow_drakewood": "Weapons/Bow_10.png",
    "gear_wow_bow_nightstalker": "Weapons/Bow_33.png",
    "gear_wow_bow_yew": "Weapons/Bow_12.png",
    "gear_wow_crossbow_heavy": "Weapons/Crossbow_26.png",
    "gear_wow_staff_living_root": "Weapons/Staff_109.png",
    "gear_wow_idol_rejuvenation": "Miscellaneous/IdolofRejuvenation.png",
    "gear_wow_totem_rage": "Miscellaneous/TotemofRage.png",
    "gear_wow_book_green": "Miscellaneous/Book_05.png",
    "gear_wow_book_prayers": "Miscellaneous/Book_07.png",
    "gear_wow_cape_sea": "Miscellaneous/Cape_05.png",
    "gear_wow_trinket_aq_1": "Miscellaneous/AhnQirajTrinket_01.png",
    "gear_wow_trinket_aq_2": "Miscellaneous/AhnQirajTrinket_02.png",
    "gear_wow_trinket_aq_3": "Miscellaneous/AhnQirajTrinket_03.png",
    "gear_wow_trinket_aq_4": "Miscellaneous/AhnQirajTrinket_04.png",
    "gear_wow_trinket_aq_5": "Miscellaneous/AhnQirajTrinket_05.png",
    "gear_wow_trinket_aq_6": "Miscellaneous/AhnQirajTrinket_06.png",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", required=True)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    from PIL import Image
    pack = Path(a.pack)
    missing = [src for src in ICONS.values() if not (pack / src).exists()]
    if missing:
        print("not in the pack:", ", ".join(missing))
        return 1
    if len(set(ICONS.values())) != len(ICONS):
        print("one pack file mapped twice")
        return 1
    for icon_id, src in ICONS.items():
        out = DEST / f"{icon_id}.png"
        if a.apply:
            Image.open(pack / src).convert("RGBA").resize((60, 60), Image.LANCZOS).save(out)
    print(f"{len(ICONS)} icons {'installed' if a.apply else 'checked'} -> {DEST.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
