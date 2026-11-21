#!/usr/bin/env python3
"""Heroic stage 2 (docs/heroic_design.md): the Frontier Mark, the Frontier Quartermasters and what they sell, and one
heroic-only item per dungeon. Idempotent.

    PYTHONPATH=. python3 tools/build_heroic_rewards.py

Kyle, 21 Nov 2026, in order: "Yeah build stage 2"; "the badge vendor can have multiple tabs. We can organize it by
armor slot and type and weapon slot. We will have heroic sales and maybe some more expensive buy only blues"; "Ensure
the vendor is well organized and sleek and sexy. Make the more expensive blues higher ilvl"; "Don't call them badge of
honor. We are Frontier RPG"; "So quartermaster to sell will be in capital cities only. Org, UC, and Auerlion".

THE MARK. Every boss killed on a heroic run drops one Frontier Mark (combat/combat_engine.py). It's a material, so it
stacks in the bag and the quartermasters barter for it (world/vendor_manager: a vendor's `barter`).

THE QUARTERMASTERS, one in each capital: Orgrimmar, the Undercity and Aurelion. Their shelf is tabbed by armour type
and weapon slot (a vendor's `tabs`, ui/screens/vendor_screen.py) and sorted by slot inside each tab. Two lines:
  * the Pathfinder line, item level 66 (a heroic boss's level): every armour slot in all four types, cloaks, necks,
    rings, and a weapon for every hand;
  * the Horizon line, item level 68 and dearer, sold nowhere else: the big armour slots, jewellery and weapons, each in
    the stat mix the Pathfinder piece in that slot doesn't have.

HEROIC-ONLY ITEMS. Each dungeon's last boss (the highest-level boss on its last floor) on a heroic run has a one-in-five chance at an item nothing else drops,
item level 66, worn at 60. The 26 highest dungeons' items wear Kyle's sheet HB1 (tools/slice_heroic_icons.py).

Nothing here goes on the auction house: quartermaster gear and heroic-only items are bound to whoever earned them
(world/market/goods._secret_names, world/market/catalog.py).
"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

OUT = ROOT / "data/items/heroic_rewards.json"
MATS = ROOT / "data/gathering/materials.json"
VENDORS = ROOT / "data/npcs/vendors.json"
MARK = "frontier_mark"
MARK_DEF = {
    "name": "Frontier Mark",
    "material_type": "reagent",
    "profession": "trade_goods",
    "tier": "endgame",
    "description": "A heavy medallion of bronze and gold, struck for whoever brings down a dungeon's master on a heroic "
                   "run. The Frontier Quartermasters in Orgrimmar, the Undercity and Aurelion trade for nothing else.",
    "stack_limit": 500,
    "vendor_price": 0,
    "sell_price": 0,
    "icon_id": MARK,
}
HEROIC_ILVL, HORIZON_ILVL = 66, 68
HEROIC_ONLY_CHANCE = 0.2

#: stat template -> the crafting identity that writes it (tools/build_crafted_gear.IDENTITIES)
IDENT = {"int_caster": "caster", "spi_healer": "healer", "agi_physical": "agility", "agi_int_hybrid": "hunter",
         "str_physical": "strength", "str_int_hybrid": "crusader"}
NOUN = {("cloth", "head"): "Hood", ("cloth", "shoulder"): "Mantle", ("cloth", "chest"): "Robe",
        ("cloth", "hands"): "Handwraps", ("cloth", "waist"): "Cord", ("cloth", "legs"): "Leggings",
        ("cloth", "feet"): "Slippers", ("cloth", "wrist"): "Cuffs",
        ("leather", "head"): "Cap", ("leather", "shoulder"): "Shoulderpads", ("leather", "chest"): "Jerkin",
        ("leather", "hands"): "Grips", ("leather", "waist"): "Belt", ("leather", "legs"): "Breeches",
        ("leather", "feet"): "Boots", ("leather", "wrist"): "Bracers",
        ("mail", "head"): "Coif", ("mail", "shoulder"): "Spaulders", ("mail", "chest"): "Hauberk",
        ("mail", "hands"): "Gauntlets", ("mail", "waist"): "Girdle", ("mail", "legs"): "Legguards",
        ("mail", "feet"): "Treads", ("mail", "wrist"): "Wristguards",
        ("plate", "head"): "Helm", ("plate", "shoulder"): "Pauldrons", ("plate", "chest"): "Breastplate",
        ("plate", "hands"): "Gauntlets", ("plate", "waist"): "Waistguard", ("plate", "legs"): "Legplates",
        ("plate", "feet"): "Sabatons", ("plate", "wrist"): "Vambraces"}
SLOTS = ("head", "shoulder", "chest", "hands", "waist", "legs", "feet", "wrist")
#: the Pathfinder line's stat mix, slot by slot, for each armour type; the Horizon piece in a slot takes the other one
PATH_MIX = {
    "cloth": {"head": "int_caster", "shoulder": "spi_healer", "chest": "int_caster", "hands": "int_caster",
              "waist": "spi_healer", "legs": "spi_healer", "feet": "int_caster", "wrist": "spi_healer"},
    "leather": {"head": "agi_physical", "shoulder": "agi_int_hybrid", "chest": "agi_physical",
                "hands": "agi_int_hybrid", "waist": "agi_int_hybrid", "legs": "agi_physical", "feet": "agi_physical",
                "wrist": "agi_int_hybrid"},
    "mail": {"head": "agi_physical", "shoulder": "spi_healer", "chest": "agi_physical", "hands": "agi_physical",
             "waist": "agi_int_hybrid", "legs": "spi_healer", "feet": "spi_healer", "wrist": "agi_int_hybrid"},
    "plate": {"head": "str_physical", "shoulder": "str_int_hybrid", "chest": "str_physical", "hands": "str_physical",
              "waist": "str_int_hybrid", "legs": "str_physical", "feet": "str_int_hybrid", "wrist": "str_int_hybrid"},
}
OTHER = {"int_caster": "spi_healer", "spi_healer": "int_caster", "agi_physical": "agi_int_hybrid",
         "agi_int_hybrid": "agi_physical", "str_physical": "str_int_hybrid", "str_int_hybrid": "str_physical"}
#: the mail Horizon pieces go to the hunter-and-shaman mix rather than the healer's twice
MAIL_OTHER = {"agi_physical": "spi_healer", "spi_healer": "agi_int_hybrid"}
SET_WORD = {("path", "cloth"): "Pathweaver", ("path", "leather"): "Pathstalker", ("path", "mail"): "Pathwarden",
            ("path", "plate"): "Pathbreaker", ("horizon", "cloth"): "Horizonweave",
            ("horizon", "leather"): "Horizonhide", ("horizon", "mail"): "Horizonlink",
            ("horizon", "plate"): "Horizonplate"}
FLAVOUR = {
    ("path", "cloth"): "Cut for the casters who go first into the dark places and come back out of them.",
    ("path", "leather"): "Oiled hide that doesn't creak, made for people who'd rather not be heard coming.",
    ("path", "mail"): "Close-linked mail that turns a blade and still lets you draw a bow.",
    ("path", "plate"): "Plate built to stand in a dungeon's doorway and not move.",
    ("horizon", "cloth"): "The quartermasters keep this silk for the few who've cleared the hardest halls more than once.",
    ("horizon", "leather"): "Hide from beasts nobody hunts twice, cured for months before a quartermaster will sell it.",
    ("horizon", "mail"): "Every ring is drawn and closed by hand. A quartermaster won't say how long a shirt takes.",
    ("horizon", "plate"): "Plate a quartermaster only sells to someone they've seen come back from a heroic.",
}
#: (line, item name, slot, kind, weapon or None, stat template, price in marks)
ACCESSORIES = [
    ("path", "Pathfinder's Pendant", "neck", "armor", None, "int_caster", 15),
    ("path", "Pathfinder's Choker", "neck", "armor", None, "str_physical", 15),
    ("path", "Pathfinder's Band", "ring", "armor", None, "agi_physical", 15),
    ("path", "Pathfinder's Loop", "ring", "armor", None, "spi_healer", 15),
    ("path", "Pathfinder's Cloak", "back", "armor", None, "agi_physical", 15),
    ("path", "Pathfinder's Shawl", "back", "armor", None, "int_caster", 15),
    ("path", "Pathfinder's Staff", "main_hand", "weapon", "staff", "int_caster", 45),
    ("path", "Pathfinder's Greatsword", "main_hand", "weapon", "sword_2h", "str_physical", 45),
    ("path", "Pathfinder's Dirk", "main_hand", "weapon", "dagger", "agi_physical", 30),
    ("path", "Pathfinder's Mace", "main_hand", "weapon", "mace_1h", "spi_healer", 30),
    ("path", "Pathfinder's Shield", "off_hand", "weapon", "shield", "str_physical", 20),
    ("path", "Pathfinder's Journal", "off_hand", "weapon", "tome", "int_caster", 20),
    ("path", "Pathfinder's Longbow", "ranged", "weapon", "bow", "agi_physical", 20),
    ("path", "Pathfinder's Wand", "ranged", "weapon", "wand", "int_caster", 20),
    ("horizon", "Horizon Pendant", "neck", "armor", None, "spi_healer", 30),
    ("horizon", "Horizon Signet", "ring", "armor", None, "str_int_hybrid", 30),
    ("horizon", "Horizon Band", "ring", "armor", None, "int_caster", 30),
    ("horizon", "Horizon Cloak", "back", "armor", None, "str_physical", 30),
    ("horizon", "Horizon Glaive", "main_hand", "weapon", "polearm", "str_physical", 75),
    ("horizon", "Horizon Blade", "main_hand", "weapon", "sword_1h", "agi_physical", 50),
    ("horizon", "Horizon Staff", "main_hand", "weapon", "staff", "spi_healer", 75),
    ("horizon", "Horizon Bulwark", "off_hand", "weapon", "shield", "str_int_hybrid", 35),
    ("horizon", "Horizon Rifle", "ranged", "weapon", "gun", "agi_physical", 35),
]
ACC_FLAVOUR = {"path": "Sold by the Frontier Quartermasters for Frontier Marks, and to nobody who hasn't earned them.",
               "horizon": "The best a Frontier Quartermaster keeps, and only for the most Frontier Marks."}
PRICE = {("path", "head"): 25, ("path", "chest"): 25, ("path", "legs"): 25, ("path", "shoulder"): 18,
         ("path", "hands"): 18, ("path", "feet"): 18, ("path", "waist"): 15, ("path", "wrist"): 15,
         ("horizon", "head"): 45, ("horizon", "chest"): 45, ("horizon", "legs"): 45, ("horizon", "shoulder"): 35}
HORIZON_SLOTS = ("head", "shoulder", "chest", "legs")

#: dungeon's last boss -> (item id, name, slot, kind, armour or weapon type, stat template, flavour, icon or None)
HEROIC_ONLY = {
    "Exarch Lucan Thessaly": ("hb_halo_of_floating_shards", "Halo of Floating Shards", "head", "armor", "plate",
                              "str_int_hybrid", "The ring of shards the Exarch wore over his helm, still turning "
                              "slowly when nobody's wearing it.", "hb_exarch"),
    "Echo of the Queen": ("hb_tear_of_zin_azshari", "Tear of Zin-Azshari", "neck", "armor", None, "spi_healer",
                          "Sea-glass with seawater sealed inside it. On a quiet night you can hear the tide.",
                          "hb_echo_of_the_queen"),
    "Baron Rivendare": ("hb_deathcharger_spurs", "Deathcharger's Spurs", "feet", "armor", "plate", "str_physical",
                        "Taken off the Baron's own boots. His horse never came back for them.", "hb_rivendare"),
    "Grand Crusader Victor Hale": ("hb_cloak_of_the_last_crusade", "Cloak of the Last Crusade", "back", "armor",
                                   None, "str_physical", "Hale's own cloak, the flame on it stitched by his "
                                   "mother before Hearthglen fell.", "hb_victor_hale"),
    "Darkmaster Gandling": ("hb_the_headmasters_register", "The Headmaster's Register", "off_hand", "weapon", "tome",
                            "int_caster", "Every student Gandling ever taught, and what became of them. Most of "
                            "the pages end the same way.", "hb_gandling"),
    "The Wound's Heart": ("hb_shard_of_the_wound", "Shard of the Wound", "neck", "armor", None, "str_int_hybrid",
                          "A sliver of the Heart, cooled and set in iron. It's warm against the skin all the time.",
                          "hb_wounds_heart"),
    "Grand Crusader Dathrohan": ("hb_dathrohans_broken_halo", "Dathrohan's Broken Halo", "head", "armor", "plate",
                                 "str_physical", "The Grand Crusader's gilded helm, cracked the night the thing "
                                 "inside him stopped pretending.", "hb_dathrohan"),
    "The Warheart": ("hb_governor_of_the_warheart", "Governor of the Warheart", "ring", "armor", None, "agi_physical",
                     "The crystal that told the Warheart how fast to burn, set in a ring by a deserter at the "
                     "Dawnspear.", "hb_warheart"),
    "Xavras the Gloomtender": ("hb_gloomtenders_pruning_knife", "Gloomtender's Pruning Knife", "main_hand",
                               "weapon", "dagger", "agi_physical", "Xavras cut her gardens with it. The spores on "
                               "the blade still glow.", "hb_xavras"),
    "The Caldera": ("hb_caldera_cracked_gauntlets", "Caldera-Cracked Gauntlets", "hands", "armor", "mail",
                    "agi_int_hybrid", "Dark iron that went into the Caldera's heart and came out with molten seams "
                    "through it.", "hb_caldera"),
    "Hive-Mother Ahn'thera": ("hb_royal_jelly_wristguards", "Royal Jelly Wristguards", "wrist", "armor", "leather",
                              "agi_physical", "Hide glazed with the Hive-Mother's royal jelly, which sets harder "
                              "than chitin.", "hb_ahnthera"),
    "Thane Morrun the Unmade": ("hb_hammer_of_the_unmade_thane", "Hammer of the Unmade Thane", "main_hand",
                                "weapon", "mace_2h", "str_physical", "Morrun's hammer, made before he was unmade. "
                                "The runes on it only light for a dwarf.", "hb_morrun"),
    "Zar'gothrax the Unbound": ("hb_unbound_felstaff", "Unbound Felstaff", "main_hand", "weapon", "staff",
                                "int_caster", "The staff Zar'gothrax was bound with, until he wasn't. The fel "
                                "crystal still remembers him.", "hb_zargothrax"),
    "Resonance": ("hb_band_of_three_tones", "Band of Three Tones", "ring", "armor", None, "spi_healer",
                  "Three thin bands that hum in a chord when they touch. The Cistern's water sang the same note.",
                  "hb_resonance"),
    "Pitboss Grebble Vask": ("hb_pitboss_gilded_pick", "Pitboss's Gilded Pick", "main_hand", "weapon", "axe_1h",
                             "agi_physical", "Grebble never swung it once. He had people for that.",
                             "hb_grebble_vask"),
    "Bosun Grell Tarpot": ("hb_tarpots_boarding_pistol", "Tarpot's Boarding Pistol", "ranged", "weapon", "gun",
                           "agi_physical", "Tarpot's pistol, loaded for one shot and kept that way for years.",
                           "hb_tarpot"),
    "High Inquisitor Whitemane": ("hb_whitemanes_last_psalter", "Whitemane's Last Psalter", "off_hand", "weapon",
                                  "tome", "spi_healer", "Her prayers, written in her own hand, with every name she "
                                  "ever raised in the margins.", "hb_whitemane"),
    "The Index": ("hb_cowl_of_the_index", "Cowl of the Index", "head", "armor", "cloth", "int_caster",
                  "Stitched with the Index's catalogue in letters too small to read without a lens.", "hb_the_index"),
    "Vek'tar the Unbeaten": ("hb_unbeaten_belt", "Belt of the Unbeaten", "waist", "armor", "plate", "str_physical",
                             "Vek'tar's champion's belt. He wore it for eleven years, and you're the reason he "
                             "doesn't now.", "hb_vektar"),
    "Herod": ("hb_herods_red_axe", "Herod's Red Axe", "main_hand", "weapon", "axe_2h", "str_physical",
              "The Scarlet Champion's axe, lacquered red so the blood wouldn't show.", "hb_herod"),
    "Arcanist Doan": ("hb_doans_scorched_robe", "Doan's Scorched Robe", "chest", "armor", "cloth", "int_caster",
                      "Doan's robe, burned at the hem from the night he tried the detonation indoors.", "hb_doan"),
    "Lord Falconcrest": ("hb_falconcrest_longbow", "Falconcrest Longbow", "ranged", "weapon", "bow", "agi_physical",
                         "A Stromgarde hunting bow with falcons carved down its length.", "hb_falconcrest"),
    "Dark Sorcerer Zul'keth": ("hb_zulketh_plague_sash", "Zul'keth's Plague Sash", "waist", "armor", "cloth",
                               "spi_healer", "Zul'keth wore it through the worst of the plague and never once "
                               "caught it.", "hb_zulketh"),
    "Charlga Razorflank": ("hb_razorflank_thornmail", "Razorflank Thornmail", "chest", "armor", "mail",
                           "agi_physical", "Mail woven through with the Kraul's thorns, which still grow a little "
                           "every spring.", "hb_razorflank"),
    "Bloodmage Thalnos": ("hb_thalnos_bloodstone_mantle", "Thalnos's Bloodstone Mantle", "shoulder", "armor",
                          "cloth", "int_caster", "A red crystal at each point, grown from what Thalnos spent "
                          "and never paid back.", "hb_thalnos"),
    "Lord Nightmare": ("hb_nightmare_stitched_boots", "Nightmare-Stitched Boots", "feet", "armor", "leather",
                       "agi_physical", "Black hide sewn with thread that moves when you aren't looking at it.",
                       "hb_lord_nightmare"),
    # the ships and the Eldest Sequoia, on the dungeon list since 21 Nov 2026 (Kyle: "ensure all Dungeons are counting
    # as Dungeons"), and the ten lowest dungeons, wear stock icons
    "Captain Ruel Scuttler": ("hb_scuttlers_sea_cutlass", "Scuttler's Sea Cutlass", "main_hand", "weapon", "sword_1h",
                              "agi_physical", "The captain's cutlass, salt-pitted and sharper than it looks. He named "
                              "it after his mother.", None),
    "Admiral Hedessa Crane": ("hb_admirals_long_coat", "The Admiral's Long Coat", "chest", "armor", "leather",
                              "agi_int_hybrid", "Crane's coat, cut long against the spray, with every ship she ever "
                              "took stitched inside the hem.", None),
    "The Eldest": ("hb_heartwood_staff_of_the_eldest", "Heartwood Staff of the Eldest", "main_hand", "weapon",
                   "staff", "spi_healer", "A limb the Eldest let fall when it was done fighting. It still puts out "
                   "leaves in the spring.", None),
    "Sergeant-at-Arms Varth": ("hb_varths_gate_shield", "Varth's Gate Shield", "off_hand", "weapon", "shield",
                               "str_physical", "Durnholde's gate shield. Varth held the door with it for nine "
                               "years.", None),
    "Aku'mai": ("hb_akumai_scale_leggings", "Aku'mai Scale Leggings", "legs", "armor", "mail", "spi_healer",
                "Scales off the old hydra, still cold from the deep water.", None),
    "Archmage Arugal": ("hb_arugals_moonlit_wand", "Arugal's Moonlit Wand", "ranged", "weapon", "wand", "int_caster",
                        "Arugal called the worgen with it. It only glows under a full moon.", None),
    "Archmage Atiesh": ("hb_amberglass_handwraps", "Amberglass Handwraps", "hands", "armor", "cloth", "int_caster",
                        "Silk dipped in the tower's amber and left to set.", None),
    "Alpha Fenris": ("hb_fenris_pelt_cloak", "Fenris Pelt Cloak", "back", "armor", None, "agi_physical",
                     "The alpha's own pelt. The pack still follows whoever wears it, a little way.", None),
    "Carapace Warden": ("hb_carapace_warden_bracers", "Carapace Warden's Bracers", "wrist", "armor", "plate",
                        "str_int_hybrid", "Plates of the Warden's shell, fitted to a wrist.", None),
    "Mutanus the Devourer": ("hb_mutanus_dreaming_staff", "Mutanus's Dreaming Staff", "main_hand", "weapon", "staff",
                             "spi_healer", "A druid's staff the Devourer swallowed. It came back out greener.", None),
    "Matriarch Velaxis": ("hb_widowsilk_leggings", "Widowsilk Leggings", "legs", "armor", "cloth", "spi_healer",
                          "Spun from the Matriarch's own silk, which is stronger than anything a loom makes.", None),
    "Taragaman the Hungerer": ("hb_taragamans_burning_knuckles", "Taragaman's Burning Knuckles", "main_hand",
                               "weapon", "fist_weapon", "agi_physical", "They're still warm. They're always warm.",
                               None),
    "Giant Crab": ("hb_grotto_pearl_ring", "Grotto Pearl Ring", "ring", "armor", None, "int_caster",
                   "A black pearl the size of a thumbnail, found inside the crab. Nobody asks how it got there.",
                   None),
}


def stock_rows():
    """[(id, line, name, slot, kind, type, template, price, flavour)] in shelf order."""
    rows = []
    for line in ("path", "horizon"):
        for armour in ("cloth", "leather", "mail", "plate"):
            word = SET_WORD[(line, armour)]
            for slot in (SLOTS if line == "path" else HORIZON_SLOTS):
                mix = PATH_MIX[armour][slot]
                if line == "horizon":
                    mix = (MAIL_OTHER.get(mix, OTHER[mix]) if armour == "mail" else OTHER[mix])
                name = f"{word} {NOUN[(armour, slot)]}"
                rows.append(("fq_" + name.lower().replace(" ", "_").replace("'", ""), line, name, slot, "armor",
                             armour, mix, PRICE[(line, slot)], FLAVOUR[(line, armour)]))
    for (line, name, slot, kind, typ, mix, price) in ACCESSORIES:
        rows.append(("fq_" + name.lower().replace(" ", "_").replace("'", ""), line, name, slot, kind, typ, mix, price,
                     ACC_FLAVOUR[line]))
    return rows


def build_items():
    import build_crafted_gear as C
    from crafted_icon_palette import Picker
    from build_faction_rewards import author_unique
    C.PICKER = Picker()
    items, bad, audit = {}, [], []
    for (iid, line, name, slot, kind, typ, mix, price, flav) in stock_rows():
        ilvl = HEROIC_ILVL if line == "path" else HORIZON_ILVL
        d, b = author_unique(iid, name, slot, kind, typ, IDENT[mix], ilvl, "rare", flav, 0)
        d.pop("price", None)
        d.update(frontier_line=line, frontier_price=price, bound=True)
        items[iid] = d
        bad += b
        audit.append((name, slot, kind, typ, mix))
    for boss, (iid, name, slot, kind, typ, mix, flav, icon) in HEROIC_ONLY.items():
        d, b = author_unique(iid, name, slot, kind, typ, IDENT[mix], HEROIC_ILVL, "rare", flav, 0)
        d.pop("price", None)
        d.update(heroic_only=boss, bound=True)
        if icon:
            d["icon_id"] = icon
        items[iid] = d
        bad += b
        audit.append((name, slot, kind, typ, mix))
    return items, bad, audit


def loot_spread(rows):
    """The quartermasters' shelf and the heroic-only items together lean on no armour type, weapon or stat mix."""
    from tools.build_return_voyage_content import loot_audit
    return loot_audit([(n, s, k, t if k == "weapon" or t else None, m) for (n, s, k, t, m) in rows])


#: capital -> (vendor id, name, race, gender, variant, facing, x, y, greeting)
QUARTERMASTERS = {
    "orgrimmar": ("fq_orgrimmar", "Frontier Quartermaster Gruka Ashmane", "orc", "female", 6, "down", 89, 87,
                  "Every capital pays for proof that a dungeon's master fell on a heroic run, and the proof is a "
                  "Frontier Mark. Bring me enough of them and you can have anything on this shelf."),
    "undercity": ("fq_undercity", "Frontier Quartermaster Lorran Wicke", "forsaken", "male", 3, "down", 78, 74,
                  "The Dark Lady doesn't hand out gear to anyone who asks. She hands it out for Frontier Marks, and "
                  "I keep the count. Show me yours."),
    "aurelion": ("fq_aurelion", "Frontier Quartermaster Ysane Corvell", "aetherian", "female", 3, "down", 147, 212,
                 "The council keeps a shelf for anyone who's come back from the hardest halls below. Frontier Marks "
                 "are how we know you have, and I'll trade for every one."),
}
TABS = [["cloth", "Cloth"], ["leather", "Leather"], ["mail", "Mail"], ["plate", "Plate"], ["jewelry", "Jewelry"],
        ["main_hand", "Main Hand"], ["off_hand", "Off Hand"], ["ranged", "Ranged"]]


def write_vendors(items):
    from world.zone_keys import zone_key
    raw = VENDORS.read_text(encoding="utf-8")
    vd = json.loads(raw)
    sells = [f"unique:{iid}" for iid, d in items.items() if d.get("frontier_line")]
    prices = {f"unique:{iid}": d["frontier_price"] for iid, d in items.items() if d.get("frontier_line")}
    by_id = {v["vendor_id"]: v for v in vd["vendors"]}
    for city, (vid, name, race, gender, var, facing, x, y, greet) in QUARTERMASTERS.items():
        rec = dict(vendor_id=vid, name=name, zone=zone_key(city), x=x, y=y, tile_sprite="npc", sells=sells,
                   buys_from_player=False, faction="neutral", gear_level=60, sells_gear=False, race=race,
                   gender=gender, appearance_variant=var, facing=facing, greeting=greet,
                   barter={"currency": MARK, "name": "Frontier Marks", "icon": "frontier_mark", "default": 20,
                           "prices": prices},
                   tabs=TABS, shelf="frontier")
        if vid in by_id:
            by_id[vid].clear()
            by_id[vid].update(rec)
        else:
            vd["vendors"].append(rec)
    VENDORS.write_text(json.dumps(vd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_mark():
    """Add the mark to data/gathering/materials.json as text, after the "materials" key: the file's formatting is mixed
    and json.dumps would rewrite every line of it."""
    raw = MATS.read_text(encoding="utf-8")
    if json.loads(raw)["materials"].get(MARK) == MARK_DEF:
        return
    if f'"{MARK}"' in raw:
        raise SystemExit(f"{MARK} is in materials.json already but differs; edit it there")
    block = json.dumps({MARK: MARK_DEF}, indent=2, ensure_ascii=False)[1:-1].strip("\n")
    block = "\n".join("  " + line for line in block.splitlines())
    anchor = '  "materials": {\n'
    assert anchor in raw
    MATS.write_text(raw.replace(anchor, anchor + block + ",\n", 1), encoding="utf-8")
    json.loads(MATS.read_text(encoding="utf-8"))


def check(items):
    bad = []
    cr = json.loads((ROOT / "data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"]
    for boss in HEROIC_ONLY:
        if boss not in cr:
            bad.append(f"{boss} isn't a creature")
    names = Counter(d["name"] for d in items.values())
    bad += [f"{n} is named twice" for n, c in names.items() if c > 1]
    existing = set()
    for p in list((ROOT / "data/loot").glob("*.json")) + [ROOT / "data/items/faction_rewards.json"]:
        txt = p.read_text(encoding="utf-8")
        for n in names:
            if f'"name": "{n}"' in txt:
                existing.add(n)
    bad += [f"{n} is already an item somewhere else" for n in sorted(existing)]
    for iid, d in items.items():
        icon = d.get("icon_id")
        if not icon or not (ROOT / f"assets/icons/gear/{icon}.png").exists():
            bad.append(f"{iid} has no icon on disk ({icon})")
    return bad


def main():
    items, bad, audit = build_items()
    bad += check(items)
    bad += loot_spread(audit)
    if bad:
        print("FAILED - fix the data, not the check:")
        for b in bad:
            print("  -", b)
        return 1
    write_mark()
    OUT.write_text(json.dumps({
        "_doc": "Heroic stage 2 (tools/build_heroic_rewards.py): the Frontier Quartermasters' gear (sold as "
                "unique:<id> for Frontier Marks) and each dungeon's heroic-only item (heroic_only: its last boss).",
        "mark": MARK, "heroic_only_chance": HEROIC_ONLY_CHANCE,
        "heroic_only": {boss: row[0] for boss, row in HEROIC_ONLY.items()},
        "items": items}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_vendors(items)
    lines = Counter(d.get("frontier_line") or "heroic_only" for d in items.values())
    print(f"{len(items)} items: {lines['path']} Pathfinder (66), {lines['horizon']} Horizon (68), "
          f"{lines['heroic_only']} heroic-only; {len(QUARTERMASTERS)} quartermasters")
    return 0


if __name__ == "__main__":
    sys.exit(main())
