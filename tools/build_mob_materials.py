#!/usr/bin/env python3
"""
Crafting materials that monsters drop, WoW-style (Kyle, 15 Nov 2026). Idempotent.

    PYTHONPATH=. python3 tools/build_mob_materials.py

Kyle: "add some bro and add some of it to crafting requirements. you can do it for other zones too....we have
so many", then "like everything else, the crafting will need to state where they are dropped. You can range
from lvl 1-58 if you want across multiple professions", and he asked for one art prompt "for upwards of 48
crafting items". So: 48 materials, levels 1-58, every one of them taken off particular creatures in particular
zones (like Un'Goro's guardian stones or WoW's scorpid scales), and every one of them asked for by real
recipes in two or more trades, near the skill a crafter has when they're in that zone.

Writes:
  data/gathering/materials.json            the 48 materials (material_type "mob_reagent")
  data/creatures/mob_materials.json        who drops what, and how often (entities/mob_materials.py reads it)
  data/crafting/mob_material_uses.json     which recipes now ask for which material, and how many
  the recipe files                         the inputs themselves
  assets/gathering_nodes/mob_reagents/     a placeholder icon per material until Kyle's sheet is sliced

THE TOOLTIP SAYS WHERE IT DROPS: world/material_sources.lines reads data/creatures/mob_materials.json, and the
recipe screen's ingredient line uses the same function, so a crafter short of Harpy Plumes is told which
harpies, and where. Hidden zones are never used as a source.

PICKING THE RECIPES. Within each trade, a material goes on finished things only (armour, weapons, potions,
meals, gadgets, enchanting scrolls), never on a bar, a bolt, a plank or a cut gem, so it can't cascade up a whole ladder. It prefers recipes
whose name or slot fits it (a plume on a cloak, a talon on a dagger), then the better ones (rare before green),
then the ones nearest the skill a crafter has in that zone. No recipe takes two creature materials.
"""
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

MATS = ROOT / "data/gathering/materials.json"
DROPS = ROOT / "data/creatures/mob_materials.json"
USES = ROOT / "data/crafting/mob_material_uses.json"
ICONS = ROOT / "assets/gathering_nodes/mob_reagents"
VT = ROOT / "assets/icons/vendor_trash"
QI = ROOT / "assets/icons/quest_items"

NESTED = ROOT / "data/crafting/recipes.json"
FLAT = {p: ROOT / f"data/{p}/recipes.json" for p in ("leatherworking", "blacksmithing", "jewelcrafting", "enchanting")}
FINISHED = {"armor", "weapon", "consumable"}

# (id, name, description, placeholder icon, level, [(zone, name regex)], chance,
#  [(trade, how many recipes, how many each, preferred words)])
#: level is where the creatures live; the recipes asked are near (level - 8) * 5 .. level * 5 + 10 skill.
M = [
    # ---------------------------------------------------------------- 1-20
    ("mob_scorpid_venom_gland", "Scorpid Venom Gland", "A soft sac of yellow venom, cut from a scorpid's tail.",
     "vt_egg_sac", 6, [("Valley of Trials", r"scorpid"), ("Durotar", r"scorpid")], 0.30,
     [("alchemy", 2, 1, "poison|venom|antidote|cure"), ("leatherworking", 2, 1, "scorpid|gloves|bracers")]),
    ("mob_coarse_boar_bristle", "Coarse Boar Bristle", "A fistful of stiff bristle off a boar's back. Brushes, "
     "padding, and the inside of a good pair of boots.", "vt_fur_tuft", 8,
     [("Valley of Trials", r"\bboar"), ("Durotar", r"\bboar"), ("Southern Barrens", r"mottled boar")], 0.30,
     [("leatherworking", 2, 2, "boots|belt"), ("tailoring", 2, 1, "boots|gloves")]),
    ("mob_whirling_grit", "Whirling Grit", "Sand that won't lie still, taken from the heart of a dust devil.",
     "vt_mote_air", 5, [("Valley of Trials", r"dust devil")], 0.35,
     [("enchanting", 2, 1, ""), ("engineering", 2, 1, "")]),
    ("mob_kolkar_war_bead", "Kolkar War-Bead", "A painted clay bead from a centaur's braid. Each one counts a "
     "kill.", "vt_idol", 14, [("Durotar", r"kolkar"), ("Northern Barrens", r"kolkar")], 0.30,
     [("jewelcrafting", 3, 1, "necklace|pendant|choker"), ("leatherworking", 1, 2, "")]),
    ("mob_raptor_tooth", "Raptor Tooth", "A curved tooth as long as your finger, still sharp.", "vt_fang", 12,
     [("Durotar", r"raptor|scythemaw"), ("Echo Isles", r"raptor")], 0.30,
     [("blacksmithing", 2, 1, "dagger|sword|axe"), ("leatherworking", 2, 1, "")]),
    ("mob_murloc_fin", "Slick Murloc Fin", "A webbed fin, slick and faintly fishy. Murlocs don't need it any more.",
     "vt_fin", 12, [("Durotar", r"murloc"), ("Echo Isles", r"murloc"), ("Northern Barrens", r"murloc"),
                    ("Ashenvale West", r"murloc")], 0.35,
     [("cooking", 2, 1, "soup|stew|fish|broth"), ("alchemy", 1, 1, "water|swim")]),
    ("mob_siren_scale", "Siren Scale", "A blue-green scale off a naga siren. It sings faintly when you tap it.",
     "vt_fish_scales", 22, [("Echo Isles", r"siren|naga"), ("Western Hillsbrad", r"siren"),
                            ("Eastern Hillsbrad", r"siren"), ("Ashenvale West", r"naga")], 0.30,
     [("jewelcrafting", 3, 1, "ring|band|pendant"), ("tailoring", 1, 1, "")]),
    ("mob_harpy_plume", "Harpy Plume", "A long barred feather pulled from a harpy's wing.", "vt_feathers", 17,
     [("Northern Barrens", r"harpy"), ("Durotar", r"harpy")], 0.35,
     [("woodworking", 1, 2, "bow|arrow|fletch"), ("tailoring", 2, 1, "cloak|cape|hat|hood|back"),
      ("leatherworking", 1, 1, "cloak|helm|cap")]),
    ("mob_bristleback_tusk", "Bristleback Tusk", "A yellowed quilboar tusk, notched where it's been sharpened.",
     "vt_horn_chunk", 19, [("Central Barrens", r"bristleback"), ("Southern Barrens", r"bristleback")], 0.30,
     [("leatherworking", 2, 1, "shoulder|helm|cap"), ("blacksmithing", 2, 1, "mace|axe|helm")]),
    ("mob_dreadmist_ichor", "Dreadmist Ichor", "Thick green ichor that came out of an imp. It's warm, and it "
     "smells like burnt hair.", "vt_ghost_vial", 16, [("Central Barrens", r"dreadmist|imp")], 0.30,
     [("enchanting", 2, 1, ""), ("alchemy", 1, 1, "shadow|fel|dark|curse")]),
    ("mob_crocolisk_scale", "Tough Crocolisk Scale", "A thick, ridged scale off a crocolisk's back.",
     "vt_dried_scales", 18, [("Northern Barrens", r"crocolisk"), ("Silverpine North", r"crocolisk")], 0.30,
     [("leatherworking", 3, 1, "scale|mail|chest|vest"), ("blacksmithing", 1, 1, "shield")]),
    ("mob_ghoul_sinew", "Ghoul Sinew", "A length of grey sinew, stretched and dried. It holds a stitch like "
     "nothing else.", "vt_bone", 15, [("Silverpine North", r"ghoul|husk"), ("Silverpine South", r"ghoul"),
                                       ("Western Tirisfal", r"ghoul")], 0.30,
     [("tailoring", 2, 1, "belt|sash|cord|gloves"), ("leatherworking", 2, 1, "belt|bracers")]),
    ("mob_cursed_worgen_fang", "Cursed Worgen Fang", "A long yellow fang. The curse is still in it, a little.",
     "vt_fang_t2", 18, [("Silverpine South", r"worgen"), ("Fenris Isle", r"worgen|cur\b|alpha cur")], 0.30,
     [("jewelcrafting", 3, 1, "ring|necklace|pendant"), ("leatherworking", 1, 2, "")]),
    ("mob_spiders_silk", "Spider's Silk Strand", "A coil of silk drawn from a big spider's spinnerets. Stronger "
     "than linen and half the weight.", "vt_egg_sac_t2", 14,
     [("Silverpine North", r"spider"), ("Western Hillsbrad", r"spider"), ("Ashenvale West", r"spider"),
      ("Eastern Tirisfal", r"venomweb|spider"), ("Deathknell", r"spider")], 0.30,
     [("tailoring", 3, 1, "robe|vest|shirt|silk"), ("engineering", 1, 2, "")]),
    ("mob_duskbat_wing", "Duskbat Wing", "A leathery wing, thin enough to see the light through.", "vt_raw_hide",
     6, [("Deathknell", r"bat"), ("Western Tirisfal", r"bat"), ("Eastern Tirisfal", r"bat")], 0.30,
     [("leatherworking", 2, 1, "gloves|cloak"), ("alchemy", 1, 1, "")]),
    ("mob_grave_dust", "Grave Dust", "Grey dust out of an old grave. It clings to your fingers and it's cold.",
     "vt_grave_dust", 8, [("Deathknell", r"skeleton|grave-dweller|grave wight|unburied"), ("Western Tirisfal", r"skeleton|wight"),
                          ("Eastern Tirisfal", r"skeleton|rotting")], 0.30,
     [("enchanting", 2, 1, ""), ("tailoring", 1, 1, "")]),
    # ---------------------------------------------------------------- 20-35
    ("mob_living_bark", "Living Bark", "A strip of bark that still flexes, pulled from a treant.", "vt_bark",
     25, [("Ashenvale West", r"treant|timberling|ancient protector"), ("Ashenvale East", r"timberling"),
          ("Silverpine North", r"treant|orchardkeeper")], 0.30,
     [("woodworking", 3, 1, "staff|bow|shield"), ("leatherworking", 2, 1, "chest|vest|tunic")]),
    ("mob_fel_ember", "Fel Ember", "A green coal that won't go out, even in water. Imps are full of them.",
     "vt_ash_fire", 23, [("Ashenvale East", r"imp|felstalker|demonspawn")], 0.30,
     [("enchanting", 2, 1, ""), ("blacksmithing", 2, 1, "sword|axe|mace")]),
    ("mob_satyr_horn", "Satyr Horn", "A curled black horn, sawn off at the root.", "vt_demon_horn", 24,
     [("Ashenvale East", r"satyr")], 0.30,
     [("blacksmithing", 2, 1, "helm|axe|mace"), ("jewelcrafting", 2, 1, "")]),
    ("mob_thick_yeti_fur", "Thick Yeti Fur", "A heavy white pelt-tuft. One handful's warmer than a blanket.",
     "vt_fur_tuft_t2", 24, [("Western Hillsbrad", r"yeti|icehide")], 0.35,
     [("leatherworking", 3, 1, "cloak|boots|gloves|chest"), ("tailoring", 2, 1, "cloak|back|boots")]),
    ("mob_kobold_candle", "Kobold Candle", "A stub of tallow candle, still warm. The kobold was very attached "
     "to it.", "vt_dice", 22, [("Western Hillsbrad", r"kobold")], 0.35,
     [("engineering", 2, 1, ""), ("alchemy", 1, 1, "")]),
    ("mob_elkhorn_antler", "Elkhorn Antler", "A tine of antler with the velvet rubbed off.", "vt_horn_chunk_t2",
     27, [("The Aspen Wilderness", r"elk|stag|goldcrown")], 0.30,
     [("woodworking", 2, 1, "bow|staff"), ("engineering", 2, 1, ""), ("leatherworking", 1, 1, "")]),
    ("mob_lynx_whisker", "Lynx Whisker", "A long, stiff whisker. Alchemists swear it steadies a hand.",
     "vt_claw", 28, [("The Aspen Wilderness", r"lynx|prowler"), ("Southern Thousand Needles", r"lynx")], 0.30,
     [("alchemy", 2, 1, "agility|elixir"), ("tailoring", 1, 1, "")]),
    ("mob_blowdown_ash", "Blowdown Ash", "Ash from the blast that flattened Stonetalon East, packed hard by "
     "whatever was walking around in it.", "vt_ash_fire_t2", 28,
     [("Stonetalon East", r"ash drifter"), ("Stonetalon West", r"ash wraith")], 0.30,
     [("blacksmithing", 2, 1, "plate|helm|breastplate"), ("enchanting", 2, 1, "")]),
    ("mob_sequoia_amber", "Sequoia Amber", "Clear golden amber from a living sequoia. There's light in it that "
     "isn't from outside.", "qi_amber", 31, [("Stonetalon West", r"sap ooze"),
                                               ("Stonetalon West", r"living sap|ambermaw")], 0.30,
     [("jewelcrafting", 3, 1, "ring|necklace|pendant"), ("alchemy", 1, 1, ""), ("woodworking", 1, 1, "staff")]),
    ("mob_basalt_heart", "Basalt Heart", "The dense black core of a rock elemental. It's heavier than it looks, "
     "and it looks heavy.", "vt_core_earth_t2", 31,
     [("Stonetalon West", r"basalt|magmacore|pumice"), ("Stonetalon East", r"pumice")], 0.30,
     [("blacksmithing", 2, 1, "shield|mace|plate"), ("engineering", 2, 1, "")]),
    ("mob_windshear_quill", "Windshear Quill", "A harpy's flight feather from Windshear Crag. It pulls a "
     "little toward the wind.", "vt_feathers_t2", 28, [("Stonetalon East", r"windshear|chimney harpy|shrieka")],
     0.35, [("woodworking", 2, 2, "bow|arrow"), ("tailoring", 2, 1, "cloak|hood|back")]),
    ("mob_saltpan_crystal", "Saltpan Crystal", "A cube of salt grown from an elemental, clear as glass.",
     "vt_shard", 31, [("Southern Thousand Needles", r"saltspite|^the thermal$")], 0.30,
     [("alchemy", 2, 1, ""), ("jewelcrafting", 2, 1, ""), ("cooking", 1, 1, "")]),
    ("mob_witherbark_hex_bead", "Witherbark Hex Bead", "A bone bead carved with a troll hex. It itches.",
     "vt_idol_t2", 32, [("Arathi West", r"witherbark"), ("Arathi Central", r"witherbark")], 0.30,
     [("enchanting", 2, 1, ""), ("jewelcrafting", 2, 1, "")]),
    ("mob_moor_adder_venom", "Moor Adder Venom", "A stoppered vial of milky venom, milked from an adder.",
     "vt_ghost_vial_t2", 30, [("Arathi West", r"adder")], 0.35,
     [("alchemy", 2, 1, "poison|elixir|potion"), ("leatherworking", 1, 1, "")]),
    ("mob_barrow_dust", "Barrow Dust", "Dust from inside a sealed barrow. It's dry no matter how wet the "
     "ground it came out of.", "vt_grave_dust_t2", 38, [("Arathi East", r"revenant|shade|barrow")], 0.30,
     [("enchanting", 3, 1, ""), ("tailoring", 1, 1, "")]),
    ("mob_jungle_raptor_talon", "Jungle Raptor Talon", "A hooked talon off a jungle raptor's foot.",
     "vt_claw_t2", 34, [("Northern Stranglethorn", r"raptor"), ("Central Stranglethorn", r"raptor"),
                        ("Southern Stranglethorn", r"raptor")], 0.30,
     [("leatherworking", 2, 1, "gloves|boots"), ("blacksmithing", 2, 1, "dagger|axe|sword")]),
    ("mob_coilvine_scale", "Coilvine Scale", "A glossy green-and-gold snake scale, big as a coin.",
     "vt_dried_scales_t2", 33, [("Northern Stranglethorn", r"python"), ("Central Stranglethorn", r"adder")],
     0.30, [("leatherworking", 2, 1, "belt|bracers|vest"), ("tailoring", 1, 1, "")]),
    ("mob_silverback_sinew", "Silverback Sinew", "A cord of gorilla sinew, strong enough to string a bow.",
     "vt_rags_t2", 36, [("Northern Stranglethorn", r"ape"), ("Central Stranglethorn", r"gorilla|drumhide"),
                        ("Southern Stranglethorn", r"gorilla")], 0.30,
     [("woodworking", 2, 1, "bow"), ("leatherworking", 2, 1, "")]),
    ("mob_luminous_spore", "Luminous Spore", "A pinch of spores that glow blue in the dark, and in your pocket.",
     "vt_seed_pod_t2", 34, [("The Crystalline Underdark", r"spore|myconid|capgorger|mycelial")], 0.30,
     [("alchemy", 2, 1, "mana|elixir"), ("tailoring", 2, 1, "robe|hood|mantle")]),
    ("mob_lattice_shard", "Lattice Shard", "A shard of living crystal from the Underdark's walls, still humming.",
     "vt_shard_t2", 35, [("The Crystalline Underdark", r"crystal|shard|lattice")], 0.30,
     [("jewelcrafting", 2, 1, ""), ("enchanting", 2, 1, "")]),
    # ---------------------------------------------------------------- 35-58
    ("mob_crustback_plate", "Crustback Scorpid Plate", "A plate of salt-white scorpid shell, hard as iron.",
     "vt_chitin_plate_t2", 38, [("The Shimmering Flats", r"scorpid|skitterer"),
                                ("Southern Thousand Needles", r"scorpid")], 0.30,
     [("leatherworking", 3, 1, "scorpid|chest|leggings|helm"), ("blacksmithing", 1, 1, "")]),
    ("mob_basilisk_eye", "Basilisk Eye", "A basilisk's eye, gone to stone. Don't look straight at it.",
     "vt_geode", 42, [("The Shimmering Flats", r"basilisk"), ("Northern Tanaris", r"basilisk"),
                      ("Glittervein", r"basilisk")], 0.30,
     [("alchemy", 2, 1, ""), ("jewelcrafting", 2, 1, "")]),
    ("mob_sunstone_shard", "Sunstone Shard", "A sliver of a sunstone elemental, hot enough to warm your hands.",
     "vt_geode_fire_t2", 43, [("Northern Tanaris", r"sunstone"), ("The Abyssal Sands", r"glasswall")], 0.30,
     [("jewelcrafting", 3, 1, ""), ("enchanting", 1, 1, "")]),
    ("mob_saltscale_pearl", "Saltscale Pearl", "A grey pearl a naga wore on a cord.", "vt_pearl_t2", 40,
     [("Southern Stranglethorn", r"saltscale"), ("The Ashen Reach", r"naga")], 0.30,
     [("jewelcrafting", 3, 1, "ring|necklace"), ("tailoring", 1, 1, "")]),
    ("mob_sinkhole_ichor", "Sinkhole Ichor", "Black ichor from something that lives at the bottom of a sink.",
     "vt_ghost_vial_t3", 45, [("The Abyssal Sands", r"ooze|lurker|horror")], 0.30,
     [("alchemy", 2, 1, ""), ("leatherworking", 1, 1, "")]),
    ("mob_veinlight_mote", "Veinlight Mote", "A drifting mote of light from Glittervein's crystal veins.",
     "vt_mote_arcane_t2", 48, [("Glittervein", r"vein-lit|shatterlight|lattice-grown|shardback")], 0.30,
     [("enchanting", 2, 1, ""), ("tailoring", 2, 1, "robe|mantle|hood")]),
    ("mob_ironbark_heartwood", "Ironbark Heartwood", "A billet of heartwood off an old treant, hard as iron and "
     "twice as old.", "vt_bark_t3", 52, [("South Felwood", r"treant|hollowbark"),
                                          ("North Felwood", r"ironbark")], 0.30,
     [("woodworking", 3, 1, "staff|bow|shield"), ("leatherworking", 1, 1, "")]),
    ("mob_jadefire_ember", "Jadefire Ember", "A jade-green coal from a Jadefire satyr's brazier. It burns cold.",
     "vt_brimstone_t3", 54, [("North Felwood", r"jadefire|felbrand")], 0.30,
     [("enchanting", 2, 1, ""), ("blacksmithing", 2, 1, "sword|axe|mace|plate")]),
    ("mob_hive_resin", "Hive Resin", "Amber resin from a silithid hive, tacky and sharp-smelling.",
     "vt_seed_pod_t3", 51, [("The Black Strand", r"hive")], 0.30,
     [("leatherworking", 2, 1, ""), ("engineering", 2, 1, "")]),
    ("mob_scoria_heart", "Scoria Heart", "The glowing heart of a fire elemental, cooled to scoria on the "
     "outside and molten in the middle.", "vt_core_fire_t3", 56,
     [("The Ashen Reach", r"scoria|ventborn|flame spirit|crag earth"), ("Tempest Shallows", r"flame spirit")],
     0.30, [("blacksmithing", 2, 1, "plate|sword|mace"), ("engineering", 2, 1, "")]),
    ("mob_drake_scale", "Caldera Drake Scale", "A black-and-orange scale off a caldera drake, still warm.",
     "vt_dried_scales_t3", 56, [("The Ashen Reach", r"drake"), ("Tempest Shallows", r"whelp|sootwing")], 0.30,
     [("leatherworking", 3, 1, "chest|leggings|helm|scale"), ("blacksmithing", 1, 1, "shield")]),
    ("mob_gorilla_mane", "Ashfur Mane", "A hank of grey-red mane off an ashfur gorilla, singed at the ends.",
     "vt_fur_tuft_t3", 53, [("Tempest Shallows", r"gorilla"), ("The Ashen Reach", r"gorilla")], 0.30,
     [("tailoring", 2, 1, "cloak|back|robe"), ("leatherworking", 2, 1, "")]),
]


def _load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def _save(p, d):
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _recipe_files():
    nested = _load(NESTED)
    flat = {p: _load(f) for p, f in FLAT.items()}
    return nested, flat


def _all_recipes(nested, flat):
    for prof, g in nested["professions"].items():
        for rid, r in g["recipes"].items():
            yield prof, rid, r
    for prof, d in flat.items():
        for rid, r in d["recipes"].items():
            yield prof, rid, r


def _finished(trade, r):
    """A finished thing: armour, a weapon, a potion or meal, or an enchanter's scroll (which goes on gear and
    stops there). Never a bar, bolt, plank or cut gem that other recipes are built from."""
    o = r.get("output") or {}
    if o.get("kind") in FINISHED:
        return True
    return trade == "enchanting" and o.get("kind") == "material" and str(o.get("material_id", "")).startswith("enchant_")


RARITY = {"epic": 4, "rare": 3, "uncommon": 2, "common": 1}


def _text_of(r):
    o = r.get("output") or {}
    return " ".join(str(x) for x in (r.get("name", ""), o.get("slot", ""), o.get("weapon_type", ""),
                                     o.get("armor_type", ""), o.get("consumable_id", "")))


def main():
    enc = _load(ROOT / "data/creatures/encounters.json")["zones"]
    creatures = _load(ROOT / "data/creatures/creatures.json")["creatures"]
    hidden = set(_load(ROOT / "data/world/hidden_zones.json").get("zones", {}))
    mats = _load(MATS)
    # SECRETS STAY SECRET: a creature that lives in a hidden zone is never a named source, even when it
    # sits in its parent's cave table (a hidden layer does).
    sys.path.insert(0, str(ROOT))
    from world.hidden_zones import creature_kinds
    secret = set(creature_kinds())
    nested, flat = _recipe_files()
    ids = [m[0] for m in M]
    assert len(ids) == len(set(ids)) == 48, f"{len(set(ids))} materials, not 48"

    # take every creature material back off every recipe first, so a rerun picks afresh
    mob_ids = set(ids) | {k for k, v in mats["materials"].items() if v.get("material_type") == "mob_reagent"}
    for _p, _rid, r in _all_recipes(nested, flat):
        for k in list((r.get("inputs") or {})):
            if k in mob_ids:
                del r["inputs"][k]
    for k in [k for k, v in mats["materials"].items() if v.get("material_type") == "mob_reagent" and k not in ids]:
        del mats["materials"][k]

    drops, uses, bad = {}, {}, []
    taken = set()
    ICONS.mkdir(parents=True, exist_ok=True)
    for (mid, name, desc, icon, level, sources, chance, trades) in M:
        # ---- who drops it
        who, where = [], []
        for zone, rx in sources:
            if zone in hidden:
                bad.append(f"{mid}: {zone} is a hidden zone")
                continue
            t = enc.get(zone)
            if not t:
                bad.append(f"{mid}: no encounter table for {zone}")
                continue
            names = set((t.get("open_zone") or {}).get("creatures", {}))
            for s in (t.get("subzones") or {}).values():
                names |= set(s["creatures"])
            for cave, s in (t.get("caves") or {}).items():
                if cave not in hidden:
                    names |= set(s["creatures"])
            names -= secret
            found = sorted(n for n in names if re.search(rx, n, re.I) and n in creatures)
            if not found:
                bad.append(f"{mid}: nothing matches {rx!r} in {zone}")
            for n in found:
                if n not in who:
                    who.append(n)
            if found and zone not in where:
                where.append(zone)
        lv = [creatures[n].get("level_range", [level, level]) for n in who]
        lo = min((a for a, _b in lv), default=level)
        hi = max((b for _a, b in lv), default=level)
        drops[mid] = {"name": name, "creatures": who, "zones": where, "levels": [lo, hi], "chance": chance,
                      "boss_qty": [1, 2]}

        # ---- the material itself
        tier = "early" if level < 20 else ("mid" if level < 40 else "late")
        rec = dict(name=name, material_type="mob_reagent", profession="trade_goods", tier=tier,
                   description=desc, stack_limit=20, sell_price=int(round(5 + level ** 1.6)),
                   icon_id=mid, source="creature")
        mats["materials"][mid] = rec
        dst = ICONS / f"{mid}.png"
        if not dst.exists() or (ICONS / f".placeholder_{mid}").exists():
            src = VT / f"{icon}.png"
            if not src.exists():
                src = QI / f"{icon}.png"
            if not src.exists():
                bad.append(f"{mid}: no placeholder art {icon}")
            else:
                shutil.copyfile(src, dst)
                (ICONS / f".placeholder_{mid}").write_text("placeholder until Kyle's sheet is sliced\n")

        # ---- which recipes ask for it
        s_lo, s_hi = max(1, (level - 8) * 5), level * 5 + 10
        centre = (s_lo + s_hi) / 2
        uses[mid] = []
        for (trade, n, qty, prefer) in trades:
            pool = [(p, rid, r) for p, rid, r in _all_recipes(nested, flat)
                    if p == trade and _finished(p, r) and rid not in taken and not rid.startswith("secret")]
            got = []
            for widen in (0, 20, 45, 80):
                cand = [(p, rid, r) for p, rid, r in pool
                        if s_lo - widen <= r.get("skill_required", 0) <= s_hi + widen and rid not in got]
                cand.sort(key=lambda x: (
                    0 if prefer and re.search(prefer, _text_of(x[2]), re.I) else 1,
                    -RARITY.get((x[2].get("output") or {}).get("rarity", "common"), 1),
                    abs(x[2].get("skill_required", 0) - centre), x[1]))
                for p, rid, r in cand:
                    if len(got) >= n:
                        break
                    got.append(rid)
                if len(got) >= n:
                    break
            if len(got) < n:
                bad.append(f"{mid}: only {len(got)} {trade} recipes near skill {s_lo}-{s_hi}")
            for p, rid, r in pool:
                if rid in got:
                    r.setdefault("inputs", {})[mid] = qty
                    taken.add(rid)
                    uses[mid].append({"trade": trade, "recipe": rid, "name": r.get("name"), "count": qty,
                                      "skill": r.get("skill_required", 0)})
        if len(uses[mid]) < 2:
            bad.append(f"{mid}: asked for by only {len(uses[mid])} recipes")

    if bad:
        print(f"FAILED ({len(bad)}):")
        for b in bad:
            print(f"  - {b}")
        return 1

    _save(MATS, mats)
    _save(NESTED, nested)
    for p, f in FLAT.items():
        _save(f, flat[p])
    _save(DROPS, {"_about": ("Crafting materials monsters drop (tools/build_mob_materials.py, entities/mob_materials.py). "
                             "Kyle, 15 Nov 2026: 'add some of it to crafting requirements' and 'the crafting will "
                             "need to state where they are dropped'."), "materials": drops})
    _save(USES, {"_about": "Which recipes ask for which creature material (tools/build_mob_materials.py).",
                 "uses": uses})
    by_trade = {}
    for u in uses.values():
        for x in u:
            by_trade[x["trade"]] = by_trade.get(x["trade"], 0) + 1
    print(f"{len(M)} creature materials, levels {min(m[4] for m in M)}-{max(m[4] for m in M)}, dropped by "
          f"{len({c for d in drops.values() for c in d['creatures']})} creatures in "
          f"{len({z for d in drops.values() for z in d['zones']})} zones")
    print(f"  {sum(len(u) for u in uses.values())} recipes now ask for one: {by_trade}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
