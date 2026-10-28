#!/usr/bin/env python3
"""Pull the missing icons out of Kyle's WoW icon pack and file them where the game looks.

    PYTHONPATH=. python3 tools/install_icon_pack.py --pack "/path/to/WoW Icon Pack" [--apply]

Kyle, 2026-10-28, on the recipe scrolls: "we can do wow style and reuse heavily" - then supplied the
pack.

WHY THIS EXISTS. 103 materials, 57 consumables and all 192 recipe scrolls had no icon. gear_icons.py's
own header explains why: the pack has 2023 icons across Armour, Weapons, Items, Trade, Abilities and
Spells, and only Armour and Weapons were ever copied in, the rest skipped as "966 unused files". Trade
and Miscellaneous are exactly where the vials, stones, essences, dusts, casings, scopes, scrolls,
parchment, meat and food live. Nothing needed drawing; it needed copying.

ONLY MAPPED FILES ARE COPIED, because Kyle wants the repo smaller rather than larger. Bringing the
whole pack in would add about 1900 files to carry 160. Every entry below is a deliberate pairing.

SIZES ARE CONVERTED, NOT ASSUMED. The pack is 60x60 RGB. Gathered materials in this project are 32x32
RGBA and render through get_tile_sprite at 32; consumables are 96x96 RGBA; gear is 60x60. Dropping a
60x60 RGB file into the materials folder would render at the wrong scale with no alpha, so each
destination declares its own size and everything is converted to RGBA on the way in.

REUSE IS THE POINT FOR SCROLLS. WoW uses a handful of scroll and book icons for hundreds of recipes -
one per profession, give or take - so that is what this does: six icons covering all 192, named by
the word that profession's scrolls already use (Pattern, Plans, Schematic, Recipe, Formula).
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: destination folder -> (pixel size, {stem: pack-relative source})
#: Stems are the icon_id the data already carries, so nothing in data/ has to change.
JOBS = {
    "assets/gathering_nodes/crystals": (32, {
        "azure": "Trade/EmpyreanSapphire_01.png",
        "emberglass": "Trade/Pyrestone_01.png",
        "quartz": "Trade/Gem_01.png",
        "tideglass": "Trade/SeasprayEmerald_01.png",
        "voidglass": "Trade/Nightseye_01.png",
    }),
    # Motes are the small drop, Hearts the large one - the pack's own Dust/Essence split says the
    # same thing, so motes take dusts and hearts take large essences.
    "assets/gathering_nodes/essences": (32, {
        "cinder": "Trade/DustStrange.png",
        "draft": "Trade/DustVision.png",
        "grit": "Trade/DustIllusion.png",
        "runoff": "Trade/DustDream.png",
        "static": "Trade/DustArcane.png",
        "brine": "Trade/EssenceAstralLarge.png",
        "ember": "Trade/EssenceEternalLarge.png",
        "gale": "Trade/EssenceNetherLarge.png",
        "granite": "Trade/EssenceMysticalLarge.png",
        "umbral": "Trade/EssenceMagicLarge.png",
    }),
    "assets/gathering_nodes/fibers": (32, {
        "fiber_coarse": "Trade/MoonRag_01.png",
        "fiber_supple": "Trade/MoonRag_02.png",
        "fiber_tough": "Trade/FelRag.png",
    }),
    "assets/gathering_nodes/pages": (32, {
        "pages_rough": "Trade/Papyrus.png",
        "pages_pressed": "Trade/Parchment.png",
        "pages_fine": "Trade/ParchmentVar01.png",
    }),
    "assets/gathering_nodes/herbs": (32, {
        "blindweed": "Miscellaneous/Herb_ConstrictorGrass.png",
        "khadgar": "Miscellaneous/Herb_Dreamingglory.png",
    }),
    "assets/gathering_nodes/meat": (32, {
        "meat_stringy": "Miscellaneous/Food_132_Meat.png",
        "meat_lean": "Miscellaneous/Food_133_Meat.png",
        "meat_thick": "Miscellaneous/Food_135_Meat.png",
        "meat_rich": "Miscellaneous/Food_137_Meat.png",
        "meat_prime": "Miscellaneous/FOOD_83_TALBUKSTEAK.png",
    }),
    "assets/gathering_nodes/kits": (32, {
        "upgrade_kit_iron": "Trade/GrindingStone_03.png",
        "upgrade_kit_resonant": "Trade/PrismaticSphere.png",
    }),
    # WoW's own armour kits ARE scrolls and its weapon upgrades ARE stones, so the split follows
    # the material: leather and cloth kits get the armour scrolls, metal kits get the stones.
    "assets/gathering_nodes/upgrade_kits": (32, {
        "upgrade_kit_linen": "Trade/ArmorScroll01.png",
        "upgrade_kit_cotton": "Trade/ArmorScroll01.png",
        "upgrade_kit_wool": "Trade/ArmorScroll02.png",
        "upgrade_kit_hempen": "Trade/ArmorScroll02.png",
        "upgrade_kit_silk": "Trade/ArmorScroll03.png",
        "upgrade_kit_mageweave": "Trade/ArmorScroll03.png",
        "upgrade_kit_runecloth": "Trade/WeaponScroll03.png",
        "upgrade_kit_scrap": "Trade/WeaponScroll01.png",
        "upgrade_kit_light": "Trade/WeaponScroll01.png",
        "upgrade_kit_medium": "Trade/WeaponScroll02.png",
        "upgrade_kit_heavy": "Trade/WeaponScroll02.png",
        "upgrade_kit_thick": "Trade/WeaponScroll03.png",
        "upgrade_kit_rugged": "Trade/WeaponScroll03.png",
        "upgrade_kit_fiendish": "Trade/FormulaSuperior_01.png",
        "upgrade_kit_light_armor": "Trade/ArmorScroll01.png",
        "upgrade_kit_medium_armor": "Trade/ArmorScroll02.png",
        "upgrade_kit_thick_armor": "Trade/ArmorScroll03.png",
        "upgrade_kit_copper": "Trade/GrindingStone_01.png",
        "upgrade_kit_bronze": "Trade/GrindingStone_02.png",
        "upgrade_kit_rough_iron": "Trade/WeightStone_01.png",
        "upgrade_kit_steel": "Trade/WeightStone_03.png",
        "upgrade_kit_ashwood": "Trade/SharpeningStone_01.png",
        "upgrade_kit_ironbark": "Trade/SharpeningStone_04.png",
    }),
    "assets/gathering_nodes/parts": (32, {
        "azure_coil": "Trade/DelicateCopperWire.png",
        "bronze_framework": "Trade/BronzeFramework_01.png",
        "bronze_tube": "Trade/Pipe_01.png",
        "copper_tube": "Trade/Pipe_02.png",
        "steel_barrel": "Trade/HardenedAdamantiteTube.png",
        "coiled_spring": "Trade/MithrilFiligree.png",
        "copper_bolts": "Trade/FelIronBolts.png",
        "copper_modulator": "Trade/FuelCell.png",
        "flint_striker": "Trade/ElementalBlastingPowder.png",
        "gear_assembly": "Miscellaneous/Gear_01.png",
        "unstable_trigger": "Miscellaneous/Gear_02.png",
        "void_regulator": "Miscellaneous/EngGizmos_03.png",
        "resonant_core": "Trade/KhoriumPowerCore.png",
        "iron_casing": "Trade/FelIronCasing.png",
        "part_tide_seal": "Trade/BronzeSetting.png",
        "glass_lens": "Trade/Scope01.png",
        "sight_glass": "Trade/Scope02.png",
        "precision_sight": "Miscellaneous/Spyglass_02.png",
        "scope_crude": "Miscellaneous/Spyglass_01.png",
        "scope_standard": "Miscellaneous/Spyglass_02.png",
        "scope_precision": "Miscellaneous/Spyglass_03.png",
        "scope_resonant": "Miscellaneous/EngGizmos_04.png",
        "pin_truesight": "Trade/ThoriumSetting.png",
        "wooden_stock": "Miscellaneous/Idol_02.png",
        "limbs_heartwood": "Miscellaneous/Horn_02.png",
        "limbs_laminated": "Miscellaneous/Horn_03.png",
        "nock_horn": "Miscellaneous/Horn_01.png",
    }),
    "assets/gathering_nodes/reagents": (32, {
        "vial_empty": "Trade/Potion_Empty.png",
        "vial_crystal": "Trade/CrystalVial.png",
        "vial_leaded": "Trade/LeadedVial.png",
        "whetstone": "Trade/GrindingStone_04.png",
        "parchment": "Trade/ParchmentVar02.png",
        "thread_coarse": "Trade/Linen_01.png",
        "thread_fine": "Trade/Silk_01.png",
        "thread_silken": "Trade/Mageweave_01.png",
        "bowstring": "Trade/Wool_02.png",
        "sinew": "Trade/Wool_03.png",
        "fletching": "Weapons/Arrow_02.png",
        "flux_weak": "Trade/Pigment_Grey.png",
        "flux_medium": "Trade/Pigment_Silvery.png",
        "flux_strong": "Trade/Pigment_White.png",
        "coal": "Trade/Pigment_Ebon.png",
        "bleach": "Trade/InkWhite01.png",
        "dye_mild": "Trade/InkBlueWhite02.png",
        "dye_bright": "Trade/InkRed02.png",
        "salt": "Trade/Pigment_Icy.png",
        "curing_salt": "Trade/Pigment_Burnt.png",
        "tanning_reagent": "Trade/Pigment_Golden.png",
        "resin": "Trade/Pigment_Verdant.png",
        "glue": "Trade/Pigment_Emerald.png",
    }),
    # Consumables are 96x96 RGBA in this project, matching the elixir art already there.
    "assets/icons/consumables": (96, {
        "meal_tough_jerky": "Miscellaneous/Food_132_Meat.png",
        "meal_trailbread": "Miscellaneous/Food_04.png",
        "meal_river_fish": "Miscellaneous/Food_142_Fish.png",
        "meal_spiced_haunch": "Miscellaneous/FOOD_83_TALBUKSTEAK.png",
        "meal_kodo_ribs": "Miscellaneous/Food_137_Meat.png",
        "drink_waterskin": "Miscellaneous/Food_75.png",
        "drink_barley_beer": "Miscellaneous/BrewfestBuff_01.png",
        "drink_spring_flask": "Miscellaneous/Food_76.png",
        "drink_honeyed_mead": "Miscellaneous/Food_109_HoneyLichen.png",
        "drink_birch_wine": "Miscellaneous/FireDrink.png",
        "meal_cooked_campfire_strips": "Miscellaneous/Food_133_Meat.png",
        "meal_cooked_seared_cut": "Miscellaneous/Food_135_Meat.png",
        "meal_cooked_herb_roast": "Miscellaneous/Food_96_ZangarCaps.png",
        "meal_cooked_slow_stew": "Miscellaneous/Bowl_01.png",
        "meal_cooked_feast_roast": "Miscellaneous/Food_120_SharkMeat.png",
        "bread_and_cheese": "Miscellaneous/Food_17.png",
        "roasted_meat": "Miscellaneous/Food_121_ButterMeat.png",
        "spiced_stew": "Miscellaneous/ToW_SpiceBowl.png",
        "spiced_wine": "Miscellaneous/FireDrink_1.png",
        "honeyed_fruit": "Miscellaneous/Food_18.png",
        "mushroom_broth": "Miscellaneous/Food_22.png",
        "rough_arrows": "Weapons/Arrow_01.png",
        "sturdy_arrows": "Weapons/Arrow_03.png",
        "heavy_arrows": "Weapons/Arrow_05.png",
        "rough_bolts": "Weapons/Arrow_02.png",
        "sturdy_bolts": "Weapons/Arrow_04.png",
        "heavy_bolts": "Weapons/Arrow_06.png",
        "shot_rough": "Weapons/Bullet_01.png",
        "shot_iron": "Weapons/Bullet_02.png",
        "shot_charged": "Weapons/Bullet_03.png",
        "shot_emberglass": "Weapons/Bullet_04.png",
        "shot_void": "Trade/FelIronShell.png",
        "shot_brine": "Trade/AdamantiteShells.png",
        "bomb_rough": "Miscellaneous/Bomb_01.png",
        "bomb_iron": "Miscellaneous/Bomb_02.png",
        "bomb_emberglass": "Miscellaneous/Bomb_03.png",
        "bomb_shrapnel": "Miscellaneous/Bomb_04.png",
        "bomb_concussion": "Miscellaneous/Bomb_05.png",
        "bomb_static": "Miscellaneous/Bomb_06.png",
        "bomb_brine": "Trade/FelIronBomb.png",
        "bomb_voidsplit": "Trade/SuperSapperCharge.png",
        "bomb_dynamite": "Miscellaneous/Ammo_Gunpowder_01.png",
        "bomb_sapper": "Miscellaneous/Ammo_Gunpowder_02.png",
        "bomb_ember_cluster": "Trade/ElementalBlastingPowder.png",
        "kit_field_repair": "Miscellaneous/EngGizmos_01.png",
        "kit_reinforce": "Miscellaneous/EngGizmos_02.png",
        "goggle_lens_spare": "Trade/NewGoggles.png",
        "device_recall": "Trade/PrismaticSphere.png",
        "device_lantern": "Miscellaneous/Idol_01.png",
        "device_compass": "Miscellaneous/Spyglass_01.png",
        "device_decoy": "Trade/GoblinBoomBox_01.png",
        "device_grapple": "Trade/RocketBoot_01.png",
        "device_goggleset": "Trade/Scope02.png",
        "device_repair_hv": "Miscellaneous/EngGizmos_03.png",
        "device_target_dummy": "Trade/GnomishFlameTurret.png",
        "device_jumper_cables": "Trade/DelicateCopperWire.png",
        "device_repair_bot": "Trade/GoblingTonkController.png",
    }),
    # One icon per profession, reused across all 192 scrolls, exactly as WoW does. Stems match
    # world/recipe_manager's own profession prefixes so the name on the item and the picture agree.
    "assets/icons/recipes": (60, {
        "recipe_tailoring": "Trade/ArmorScroll02.png",
        "recipe_leatherworking": "Trade/WeaponScroll01.png",
        "recipe_blacksmithing": "Trade/Scroll.png",
        "recipe_engineering": "Trade/FormulaGood_01.png",
        "recipe_alchemy": "Trade/FormulaSuperior_01.png",
        "recipe_woodworking": "Trade/WeaponScroll02.png",
        "recipe_cooking": "Miscellaneous/Book_09.png",
        "recipe_default": "Trade/Scroll.png",
    }),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", required=True, help='the extracted "WoW Icon Pack" directory')
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    pack = Path(args.pack)
    if not pack.is_dir():
        print(f"no such directory: {pack}")
        return 1

    from PIL import Image

    total = sum(len(files) for _size, files in JOBS.values())
    missing, written = [], 0
    for dest, (size, files) in JOBS.items():
        out = ROOT / dest
        for stem, rel in files.items():
            src = pack / rel
            if not src.exists():
                missing.append(f"{rel} (wanted for {dest}/{stem}.png)")
                continue
            if args.apply:
                out.mkdir(parents=True, exist_ok=True)
                img = Image.open(src).convert("RGBA")
                if img.size != (size, size):
                    img = img.resize((size, size), Image.LANCZOS)
                img.save(out / f"{stem}.png")
            written += 1
        print(f"  {dest:<42}{len(files):>3} at {size}px")

    print(f"\n{written} of {total} mapped icons resolved")
    if missing:
        print(f"\n{len(missing)} source files not found in the pack:")
        for m in missing:
            print(f"  - {m}")
        return 1
    if not args.apply:
        print("\n(dry run - pass --apply to copy)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
