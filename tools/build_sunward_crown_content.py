#!/usr/bin/env python3
"""The Sunward Crown's creatures, rares, encounter tables, loot, gathering and fishing (48-49). Idempotent.

    PYTHONPATH=. python3 tools/build_sunward_crown_content.py [--dry]

docs/worldtree_brief.md: "The threat from above: an Ascendancy landing to take the crown; storm elementals", and Kyle's
twenty answers (20 Nov 2026): the Ascendancy holds a beachhead (the Chainhold) and has taken the north arm of the crown
(the Taken Crown), the fighting is straining an old seal in the cloud, and sky beasts graze the islets. The sky stock
(Kyle's SK sheets) is worn here: the shelf's wolves and stalkers, the Goldenwood's stags and wisps, the falls' eels and
tortoises, the Ascendancy's legionaries, lancers, storm-callers, drones, artillerists, bombardiers and construct
hounds, the Kharad guardians and bound storms waking round the seal, the Stormbank's elementals and thunderbirds, and
the Driftlets' rays, jellies and whales.

    open crown             goats and beetles on the canopy between the places
    The Cloud Shelf        wolves and stalkers on the cloud
    The Goldenwood         stags, wisps and moths under the gold                          rare: Old Sunantler
    The Falls of Light     eels and tortoises at the falls                                rare: The Dewdrinker
    The Taken Crown        the Ascendancy's line on the north arm                         rare: Centurion Valeth Krane
    The Chainhold          the Ascendancy's islet, its guns and its hounds                rare: Lance-Captain Varos Thale
    The Sunken Seal        what's waking round the old ring                               rare: The Stone That Woke
    The Stormbank          elementals and thunderbirds in the dark cloud                  rare: The Hollow Storm
    The Driftlets          rays, jellies and whales over the open sky                     rare: Mother Greatfin
    Spearhold, the Annex, the Survey Dock, the Parley Stones, the Mural Gate, the Lookdown: safe

THE NUMBERS follow the tiers below (tools/build_upper_boughs_content.py): trash basic 4L - 10, a rare's 10L - 200 at
multiplier 2.2, item level = the rare's level + 3.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.build_return_voyage_content import (  # noqa: E402
    CREATURES, KITS, ENCOUNTERS, kit_slug, merge_json, _detect_format, dmg, dot, debuff, buff, loot_audit)
from tools.build_tempest_openworld import enrage, stun, shield  # noqa: E402

RARE_LOOT = ROOT / "data/loot/sunward_crown_rare_loot.json"
ZONE = "The Sunward Crown"
MAP_MODULE = "handbuilt_worldtree_sunward_crown"


def T(level):
    return 4 * level - 10


def B(level):
    return 10 * level - 200


#: name -> (template, lo, hi, rare multiplier or None, sprite, kit shape, school, [ability names])
ROSTER = {
    # ---------------------------------------------------------------- the open crown
    "Crown Goat":             ("beast_fast", 48, 48, None, "sk_sky_goat", "beast", "physical",
                               ["Horn Butt", "Headlong Charge", "Bruised"]),
    "Thistle Beetle":         ("vermin_swarm", 48, 48, None, "sk_thistle_beetle", "warrior", "nature",
                               ["Mandibles", "Thistle Spray", "Hard Shell"]),
    # ---------------------------------------------------------------- the Cloud Shelf
    "Cloudrunner Wolf":       ("beast_fast", 48, 49, None, "sk_cloud_wolf", "beast", "physical",
                               ["Bite", "Run Down", "Torn"]),
    "Shelf Stalker":          ("beast_fast", 48, 49, None, "sk_cloud_stalker", "beast", "frost",
                               ["Cold Claws", "Out of the Mist", "Chilled to the Bone"]),
    # ---------------------------------------------------------------- the Goldenwood
    "Sunlit Stag":            ("beast_large", 48, 48, None, "sk_golden_stag", "bruiser", "physical",
                               ["Antler Gore", "Stamping Hooves", "Knocked Flat"]),
    "Gold Wisp":              ("elemental_caster", 48, 48, None, "sk_gold_wisp", "caster", "holy",
                               ["Sunmote", "Flare", "Dazzled"]),
    "Gilded Moth":            ("beast_fast", 48, 48, None, "sk_sky_moth", "caster", "nature",
                               ["Gold Dust", "Wingbeat Cloud", "Itching Gold"]),
    "Old Sunantler":          ("beast_large", 49, 49, 2.2, "sk_golden_stag", "rare", "holy",
                               ["Sun-Crowned Antlers", "The Herd's Stampede", "Trampled", "The Old King's Pride"]),
    # ---------------------------------------------------------------- the Falls of Light
    "Falls Eel":              ("beast_fast", 48, 48, None, "sk_sky_eel", "beast", "nature",
                               ["Bite", "Coil and Strike", "Eel Venom"]),
    "Mossback Tortoise":      ("beast_large", 48, 49, None, "sk_moss_tortoise", "bruiser", "physical",
                               ["Shell Slam", "Snapping Jaws", "Ground Down"]),
    "The Dewdrinker":         ("beast_fast", 49, 49, 2.2, "sk_sky_eel", "rare", "frost",
                               ["Drowning Bite", "The Falls Come Down", "Held Under", "Thirst of Years"]),
    # ---------------------------------------------------------------- the Taken Crown
    "Ascendancy Legionary":   ("humanoid_warrior", 48, 49, None, "ae_legionary", "warrior", "physical",
                               ["Gladius", "Shield Bash", "Locked Shields"]),
    "Ascendancy Sky Lancer":  ("humanoid_rogue", 48, 49, None, "ae_sky_lancer", "warrior", "arcane",
                               ["Crystal Lance", "Lance Charge", "Lancer's Guard"]),
    "Ascendancy Storm-Caller": ("humanoid_caster", 48, 49, None, "ae_storm_caller", "caster", "nature",
                                ["Bolt", "Called Lightning", "Static Brand"]),
    "Ascendancy Shield Drone": ("humanoid_warrior", 48, 49, None, "ae_shield_drone", "bruiser", "arcane",
                                ["Pulse", "Shield Burst", "Dampened"]),
    "Centurion Valeth Krane": ("humanoid_warrior", 49, 49, 2.2, "ae_officer", "rare", "arcane",
                               ["Centurion's Blade", "Hold the Line", "Pinned by Orders", "No Retreat"]),
    # ---------------------------------------------------------------- the Chainhold
    "Ascendancy Artillerist": ("humanoid_caster", 48, 49, None, "ae_artillerist", "caster", "fire",
                               ["Shot", "Shell Burst", "Burning Shrapnel"]),
    "Ascendancy Bombardier":  ("humanoid_caster", 48, 49, None, "ae_bombardier", "caster", "arcane",
                               ["Arcane Charge", "Bombardment", "Arcane Burn"]),
    "Construct Hound":        ("beast_fast", 48, 49, None, "ae_construct_hound", "beast", "physical",
                               ["Steel Jaws", "Hunting Leap", "Shredded"]),
    "Lance-Captain Varos Thale": ("humanoid_rogue", 49, 49, 2.2, "ae_lancer_mounted", "rare", "arcane",
                                  ["Captain's Lance", "Charge of the Chainhold", "Ridden Down", "Crystal Bulwark"]),
    # ---------------------------------------------------------------- the Sunken Seal
    "Waking Guardian":        ("elemental_bruiser", 48, 49, None, "kh_waking_guardian", "bruiser", "physical",
                               ["Stone Fist", "Quake", "Shaken"]),
    "Unbound Storm":          ("elemental_caster", 48, 49, None, "kh_bound_storm", "caster", "nature",
                               ["Lash", "Storm Loosed", "Crackling Chains"]),
    "Seal-Touched Shade":     ("elemental_caster", 48, 49, None, "sk_void_touched", "caster", "shadow",
                               ["Cold Touch", "Leak of Dark", "Seeping Chill"]),
    "The Stone That Woke":    ("elemental_bruiser", 49, 49, 2.2, "kh_stonewarden", "rare", "physical",
                               ["Warden's Fist", "The Ring Shakes", "Buried", "Keep It Shut"]),
    # ---------------------------------------------------------------- the Stormbank
    "Stormbank Elemental":    ("elemental_bruiser", 48, 49, None, "sk_storm_elemental", "bruiser", "nature",
                               ["Thunderfist", "Downburst", "Rattled"]),
    "Bolt-Born Elemental":    ("elemental_caster", 48, 49, None, "sk_lightning_elemental", "caster", "nature",
                               ["Bolt", "Forked Lightning", "Charged"]),
    "Stormbank Thunderbird":  ("beast_fast", 48, 49, None, "sk_thunderbird", "beast", "nature",
                               ["Beak", "Thunder Dive", "Crackling Wound"]),
    "The Hollow Storm":       ("elemental_caster", 49, 49, 2.2, "sk_hollow_storm", "rare", "nature",
                               ["Hollow Thunder", "The Eye Opens", "Struck Still", "All the Storm at Once"]),
    # ---------------------------------------------------------------- the Driftlets
    "Drift Ray":              ("beast_fast", 48, 49, None, "sk_sky_ray", "beast", "physical",
                               ["Wing Slap", "Barbed Tail", "Barbed"]),
    "Cloud Jelly":            ("elemental_caster", 48, 49, None, "sk_cloud_jelly", "caster", "nature",
                               ["Sting", "Drifting Tendrils", "Numbing Venom"]),
    "Sky Whale":              ("beast_large", 48, 49, None, "sk_sky_whale", "bruiser", "physical",
                               ["Tail Sweep", "Body Slam", "Winded"]),
    "Mother Greatfin":        ("beast_large", 49, 49, 2.2, "sk_last_whale_rare", "rare", "frost",
                               ["Greatfin Sweep", "Song of the Deep Sky", "Swallowed by Cloud", "Old Mother's Wrath"]),
}
RARES = {n for n, r in ROSTER.items() if r[3]}
ALL = dict(ROSTER)


def sprite(name):
    return ALL[name][4]


RULES_START = "    # THE SUNWARD CROWN (generated by tools/build_sunward_crown_content.py; do not edit by hand)\n"
RULES_END = "    # END THE SUNWARD CROWN\n"


def write_sprite_rules():
    path = ROOT / "creature_sprites.py"
    s = path.read_text(encoding="utf-8")
    block = RULES_START + "".join(f'    (r"^{re.escape(n.lower())}$", "{sprite(n)}"),\n' for n in ALL) + RULES_END
    if RULES_START in s:
        a = s.index(RULES_START)
        b = s.index(RULES_END) + len(RULES_END)
        s = s[:a] + block + s[b:]
    else:
        anchor = "    # THE UPPER BOUGHS (generated by tools/build_upper_boughs_content.py; do not edit by hand)\n"
        assert anchor in s
        s = s.replace(anchor, block + anchor, 1)
    path.write_text(s, encoding="utf-8")


def kit(name):
    template, lo, hi, mult, _s, shape, school, names = ALL[name]
    t = T(hi)
    s = school
    dispel = {"nature": "poison", "shadow": "curse"}.get(s, "magic")
    if shape == "beast":
        return [dmg(names[0], t, school=s), dmg(names[1], int(t * 0.86), cooldown=3, school=s),
                dot(names[2], int(t * 0.27), 3, 3, school=s, **({"dispel_type": dispel} if s != "physical" else {}))]
    if shape == "warrior":
        return [dmg(names[0], t, school=s), dmg(names[1], int(t * 0.86), cooldown=3, school=s),
                buff(names[2], 6, 3, {"armor": 190})]
    if shape == "caster":
        return [dmg(names[0], t, school=s), dmg(names[1], int(t * 0.84), cooldown=5, school=s, is_aoe=True),
                dot(names[2], int(t * 0.27), 3, 3, school=s, dispel_type=dispel)]
    if shape == "bruiser":
        return [dmg(names[0], t + 8, school=s), dmg(names[1], int(t * 0.84), cooldown=4, school=s, is_aoe=True),
                debuff(names[2], 5, 2, {"dodge_rating": -20}, school=s)]
    b = B(hi)
    # an open-world rare: a heavy basic, a party hit, a stun with a hammer behind it, and its last stand
    last = (shield(names[3], int(b * 1.2), school=s) if s in ("arcane", "frost") else enrage(names[3], int(b * 0.15), s))
    return [dmg(names[0], b, school=s), dmg(names[1], int(b * 0.8), cooldown=4, school=s, is_aoe=True),
            stun(names[2], int(b * 0.85), cooldown=5, school=s), dmg(f"{names[0]}, Again", int(b * 1.7), cooldown=5,
                                                                   school=s), last]


TABLE = {
    "open_zone": {"Crown Goat": 5, "Thistle Beetle": 4},
    "subzones": {
        "The Cloud Shelf": {"Cloudrunner Wolf": 6, "Shelf Stalker": 4},
        "The Goldenwood": {"Sunlit Stag": 4, "Gold Wisp": 4, "Gilded Moth": 3, "Old Sunantler": 0},
        "The Falls of Light": {"Falls Eel": 5, "Mossback Tortoise": 4, "Crown Goat": 1, "The Dewdrinker": 0},
        "The Taken Crown": {"Ascendancy Legionary": 5, "Ascendancy Sky Lancer": 4, "Ascendancy Storm-Caller": 3,
                            "Ascendancy Shield Drone": 2, "Centurion Valeth Krane": 0},
        "The Chainhold": {"Ascendancy Artillerist": 4, "Ascendancy Bombardier": 4, "Construct Hound": 4,
                          "Ascendancy Legionary": 1, "Lance-Captain Varos Thale": 0},
        "The Sunken Seal": {"Waking Guardian": 5, "Unbound Storm": 4, "Seal-Touched Shade": 3,
                            "The Stone That Woke": 0},
        "The Stormbank": {"Stormbank Elemental": 5, "Bolt-Born Elemental": 4, "Stormbank Thunderbird": 3,
                          "The Hollow Storm": 0},
        "The Driftlets": {"Drift Ray": 5, "Cloud Jelly": 4, "Sky Whale": 2, "Mother Greatfin": 0},
        "The Parley Stones": None,
        "The Annex": None,
        "The Survey Dock": None,
        "Spearhold": None,
        "The Mural Gate": None,
        "The Lookdown": None,
    },
}

#: rare -> four (name, slot, suffix, (a|w, type) or None, template)
POOLS = {
    "Old Sunantler": [
        ("Sunantler Crown", "head", "of the Prophet", ("a", "leather"), "spi_healer"),
        ("Gold-Velvet Cloak", "back", "of the Sorcerer", None, "int_caster"),
        ("Stag-Hide Leggings", "legs", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Herd King's Hooves", "feet", "of the Bear", ("a", "plate"), "str_physical")],
    "The Dewdrinker": [
        ("Dewdrinker's Coils", "waist", "of the Wolf", ("a", "mail"), "agi_int_hybrid"),
        ("Falls-Wet Robe", "chest", "of the Prophet", ("a", "cloth"), "spi_healer"),
        ("Eelskin Gloves", "hands", "of the Tiger", ("a", "leather"), "agi_physical"),
        ("Held-Under Band", "ring", "of the Invoker", None, "int_caster")],
    "Centurion Valeth Krane": [
        ("Centurion's Crested Helm", "head", "of the Bear", ("a", "plate"), "str_physical"),
        ("Line-Holder's Shield", "off_hand", "of the Gorilla", ("w", "shield"), "str_int_hybrid"),
        ("Ascendancy Officer's Gladius", "main_hand", "of the Champion", ("w", "sword_1h"), "str_physical"),
        ("Orders in Crystal", "neck", "of the Sorcerer", None, "int_caster")],
    "Lance-Captain Varos Thale": [
        ("Chainhold Lance", "two_hand", "of the Champion", ("w", "polearm"), "str_physical"),
        ("Lance-Captain's Pauldrons", "shoulder", "of the Wolf", ("a", "mail"), "agi_int_hybrid"),
        ("Rider's Crystal Bracers", "wrist", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Captain's Signet", "ring", "of the Prophet", None, "spi_healer")],
    "The Stone That Woke": [
        ("Seal-Warden's Girdle", "waist", "of the Bear", ("a", "plate"), "str_physical"),
        ("Kharad Runestone", "off_hand", "of the Invoker", ("w", "tome"), "int_caster"),
        ("Stone-Woken Gauntlets", "hands", "of the Gorilla", ("a", "mail"), "str_int_hybrid"),
        ("Ring-Carved Maul", "two_hand", "of the Bear", ("w", "mace_2h"), "str_physical")],
    "The Hollow Storm": [
        ("Eye of the Hollow Storm", "trinket", "of the Sorcerer", None, "int_caster"),
        ("Stormbank Shroud", "shoulder", "of the Prophet", ("a", "cloth"), "spi_healer"),
        ("Thunderstruck Vest", "chest", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Charged Chain Leggings", "legs", "of the Wolf", ("a", "mail"), "agi_int_hybrid")],
    "Mother Greatfin": [
        ("Greatfin Mantle", "back", "of the Bear", None, "str_physical"),
        ("Song of the Deep Sky", "neck", "of the Prophet", None, "spi_healer"),
        ("Whalebone Staff", "two_hand", "of the Sorcerer", ("w", "staff"), "int_caster"),
        ("Cloudskin Boots", "feet", "of the Monkey", ("a", "leather"), "agi_physical")],
}

#: gathering at 48-49 on the crown: the high 40s herbs in the canopy, mithril and truesilver in the islets' rock, and
#: wood off the gold limbs. Fishing: the dew pools on the canopy (tools/build_fishing.window).
NODES = {"sunward_crown": {"slots": 40, "active_percent": 0.42, "table": {
    "herb_sungrass": 4, "herb_purple_lotus": 3, "herb_firebloom": 2, "herb_khadgar": 3,
    "ore_mithril": 3, "ore_truesilver": 2,
    "wood_thornveil_stump": 5}}}


def fishing():
    from tools.build_fishing import FISH, window
    s_lo, s_hi = window(48, 49)
    fits = sorted([(fid, sk) for fid, _n, sk, _i, _d in FISH if s_lo <= sk <= s_hi], key=lambda f: -f[1])[:4]
    return {"slots": 8, "active_percent": 0.6, "table": {fid: 3 if n else 2 for n, (fid, _s) in enumerate(fits)}}


def build_loot(pools, roster, lift, prefix):
    from tools.build_durotar_content import make
    from entities.item_budget import budget_ratio, fit_to_curve
    out, rows = {}, []
    for who, items in pools.items():
        ilvl = roster[who][2] + lift
        built = []
        for (name, slot, suffix, typ, template) in items:
            kw = {}
            if typ and typ[0] == "a":
                kw["armor_type"] = typ[1]
            elif typ:
                kw["weapon_type"] = typ[1]
            d = make(name, slot, suffix, ilvl, "", **kw)
            d.pop("flavor_text", None)
            d["stat_template"] = template
            d["item_id"] = prefix + kit_slug(name)
            r = budget_ratio(d)
            if r is not None and not 0.65 <= r <= 1.45:
                fit_to_curve(d)
            built.append(d)
            rows.append((name, slot, "weapon" if typ and typ[0] == "w" else "armor", typ[1] if typ else None,
                         template))
        out[who] = built
    return out, rows


def check(loot):
    import importlib
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    bad = []
    mod = importlib.import_module(f"tools.{MAP_MODULE}")
    declared = {s[0] for s in mod.SUBZONES}
    if set(TABLE["subzones"]) != declared:
        bad.append(f"subzones disagree with the map: {sorted(set(TABLE['subzones']) ^ declared)}")
    named = set(TABLE["open_zone"])
    if RARES & named:
        bad.append("a rare is in the open-zone table")
    for s in TABLE["subzones"].values():
        named |= set(s or {})
    if named != set(ROSTER) or set(POOLS) != RARES:
        bad.append(f"tables, roster and pools differ: {sorted(named ^ set(ROSTER))} {sorted(set(POOLS) ^ RARES)}")
    existing = json.loads(CREATURES.read_text(encoding="utf-8"))["creatures"]
    for name, r in ALL.items():
        if not (ROOT / "assets/creatures" / f"{sprite(name)}.png").exists():
            bad.append(f"{name}'s sprite {sprite(name)} is not on disk")
        prev = existing.get(name)
        if prev and (prev.get("ability_kit") != kit_slug(name) or list(prev.get("level_range") or [])[:2] != list(r[1:3])):
            bad.append(f"{name} is already a different creature in creatures.json")
    names = [i["name"] for v in loot.values() for i in v]
    dup = [n for n, c in Counter(names).items() if c > 1]
    if dup:
        bad.append(f"duplicate item names: {dup}")
    import creature_sprites as CS
    for name, r in ALL.items():
        if CS.sprite_for(name, r[0]) != sprite(name):
            bad.append(f"creature_sprites.py draws {name} as {CS.sprite_for(name, r[0])}, not {sprite(name)}")
    return bad


def main():
    write_sprite_rules()
    import importlib
    import creature_sprites
    importlib.reload(creature_sprites)
    rare_loot, rows = build_loot(POOLS, ROSTER, 3, "sci_")
    bad = check(rare_loot) + loot_audit(rows)
    if "--dry" in sys.argv or bad:
        print("\n".join(bad) if bad else f"dry run clean: {len(ALL)} creatures, {len(RARES)} rares")
        return 1 if bad else 0
    creatures = {}
    for name, (template, lo, hi, mult, *_rest) in ALL.items():
        e = {"template": template, "level_range": [lo, hi], "is_boss": bool(mult), "ability_kit": kit_slug(name)}
        if mult:
            e["boss_multiplier"] = mult
        creatures[name] = e
    merge_json(CREATURES, "creatures", creatures, "creatures.json")
    merge_json(KITS, "kits", {kit_slug(n): kit(n) for n in ALL}, "ability_kits.json")
    raw = ENCOUNTERS.read_text(encoding="utf-8")
    enc = json.loads(raw)
    indent, newline = _detect_format(json.loads(raw), raw)
    entry = enc["zones"].setdefault(ZONE, {})
    entry["name"] = ZONE
    entry["open_zone"] = {"name": ZONE, "creatures": dict(TABLE["open_zone"])}
    entry["subzones"] = {s: ({"name": s, "safe": True, "creatures": {}} if c is None else
                             {"name": s, "creatures": dict(c)}) for s, c in TABLE["subzones"].items()}
    # Lenswatch is a town: safe everywhere
    town = enc["zones"].setdefault("Lenswatch", {})
    town["name"] = "Lenswatch"
    town["open_zone"] = {"name": "Lenswatch", "safe": True, "creatures": {}}
    town["subzones"] = {"Lenswatch": {"name": "Lenswatch", "safe": True, "creatures": {}}}
    ENCOUNTERS.write_text(json.dumps(enc, indent=indent, ensure_ascii=False) + ("\n" if newline else ""),
                          encoding="utf-8")
    np_path = ROOT / "data/gathering/node_pools.json"
    nd = json.loads(np_path.read_text(encoding="utf-8"))
    nodes = json.loads(json.dumps(NODES))
    nodes["sunward_crown"]["fishing"] = fishing()
    nd["zones"].update(nodes)
    np_path.write_text(json.dumps(nd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out = {"_notes": ("The Sunward Crown's open-world rares (49). ONE item per kill from the rare's four; item_level = "
                      "the rare's level + 3. Hand-authored in tools/build_sunward_crown_content.py.")}
    out.update(rare_loot)
    RARE_LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "tools/whole_number_gear.py")], check=True, stdout=subprocess.DEVNULL)
    print(f"{len(ROSTER)} creatures ({len(RARES)} rares); {len(rows)} items; gathering and fishing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
