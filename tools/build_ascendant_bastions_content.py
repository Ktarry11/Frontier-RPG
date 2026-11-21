#!/usr/bin/env python3
"""The Ascendant Bastions' creatures, rares, encounter tables, loot, gathering and fishing (54-57). Idempotent.

    PYTHONPATH=. python3 tools/build_ascendant_bastions_content.py [--dry]

docs/worldtree_brief.md: "The Ascendancy at home: sky lancers, storm artillery, arcane bombardiers, mechanical flying
constructs". The two dungeons in the citadel (the Gravity Foundry, 56-58, and the Ascendant Spire, 60) have their own
builder; this is the open zone round it.

    open zone               smoke-gale hawks and forge-ash wisps between the islands
    The Bastion of Ascent   the Bastion legionaries, lancers and shield drones             rare: Wall-Captain Hesper Drace
    The Ascent Causeway     legionaries and construct hounds on the causeway
    The Slipways            overseers, shipwrights, keel constructs and drones              rare: The Unlaunched
    The Proving Grounds     recruits, mounted lancers and proving constructs                rare: Lance-Master Varro Dain
    The Censor-Archive      censor-inquisitors, archive wardens and cinder-script wisps     rare: High Censor Ilsabet Morn
    The Gunline             storm artillerists, arcane bombardiers, gun constructs          rare: Battery-Master Ormund Krell
    The Storm Harvest       harvested storms, lightning elementals and thunderbirds         rare: Old Thunderhead
    The Firmament Road      storm callers and gunships on the road north
    The Ashwake             ash stalkers, smoke jellies and cinder rays in the cloud        rare: The Ash-Mother
    Dawnspear Wreck, the Yard Pens: safe

THE NUMBERS follow the tiers (tools/build_sunward_crown_content.py): trash basic 4L - 10, a rare's 10L - 200 at
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
from tools.build_scarlet_monastery_content import opener, stun_hit, heal  # noqa: E402

RARE_LOOT = ROOT / "data/loot/ascendant_bastions_rare_loot.json"
ZONE = "The Ascendant Bastions"
MAP_MODULE = "handbuilt_worldtree_ascendant_bastions"


def T(level):
    return 4 * level - 10


def B(level):
    return 10 * level - 200


#: name -> (template, lo, hi, rare multiplier or None, sprite, kit shape, school, [ability names])
ROSTER = {
    # ---------------------------------------------------------------- between the islands
    "Smoke-Gale Hawk":        ("beast_fast", 54, 55, None, "sk_gale_hawk", "beast", "nature",
                               ["Talons", "Smoke Dive", "Wind-Torn"]),
    "Forge-Ash Wisp":         ("elemental_caster", 54, 55, None, "sk_fading_wisp", "caster", "fire",
                               ["Cinder", "Ash Cloud", "Smouldering"]),
    # ---------------------------------------------------------------- the Bastion of Ascent's apron
    "Bastion Legionary":   ("humanoid_warrior", 56, 57, None, "ae_legionary", "warrior", "physical",
                               ["Crystal Blade", "Shield Wall Advance", "Braced"]),
    "Bastion Sky Lancer":  ("humanoid_warrior", 56, 57, None, "ae_sky_lancer", "warrior", "arcane",
                               ["Lance Thrust", "Skyward Charge", "Crystal-Tipped"]),
    "Bastion Shield Drone": ("elemental_caster", 56, 57, None, "ae_shield_drone", "caster", "arcane",
                                ["Pulse", "Projected Ward", "Arcane Burn"]),
    "Wall-Captain Hesper Drace": ("humanoid_warrior", 57, 57, 2.2, "ae_officer", "rare", "physical",
                                  ["Captain's Blade", "Man the Walls", "Thrown from the Wall", "No Retreat"]),
    # ---------------------------------------------------------------- the Ascent Causeway
    "Causeway Construct Hound": ("beast_fast", 56, 56, None, "ae_construct_hound", "beast", "physical",
                                 ["Bronze Bite", "Run Down", "Mauled"]),
    # ---------------------------------------------------------------- the Slipways
    "Yard Overseer":          ("humanoid_caster", 55, 56, None, "ae_officer", "caster", "arcane",
                               ["Overseer's Rod", "Work Faster", "Lashed"]),
    "Ascendancy Shipwright":  ("humanoid_caster", 55, 56, None, "ae_engineer", "caster", "fire",
                               ["Rivet Gun", "Hull Charge", "Scorched"]),
    "Keel Construct":         ("elemental_bruiser", 55, 56, None, "ae_siege_walker", "bruiser", "physical",
                               ["Keel Hammer", "Lay the Keel", "Pinned"]),
    "Slipway Repair-Drone":   ("elemental_caster", 55, 56, None, "ae_repair_drone", "caster", "arcane",
                               ["Cutting Beam", "Weld Sweep", "Weld-Burn"]),
    "The Unlaunched":         ("elemental_bruiser", 56, 56, 2.2, "ae_gunship", "rare", "fire",
                               ["Broadside", "Every Gun at Once", "Pinned Under the Hull", "Never Launched"]),
    # ---------------------------------------------------------------- the Proving Grounds
    "Lancer Recruit":         ("humanoid_warrior", 55, 55, None, "ae_sky_lancer", "warrior", "physical",
                               ["Practice Lance", "Eager Charge", "Steadied"]),
    "Mounted Sky Lancer":     ("humanoid_warrior", 55, 56, None, "ae_lancer_mounted", "bruiser", "arcane",
                               ["Mounted Thrust", "Wheeling Charge", "Trampled"]),
    "Proving Construct":      ("elemental_bruiser", 55, 56, None, "ae_sentinel", "bruiser", "physical",
                               ["Training Blow", "Drill Sweep", "Bruised"]),
    "Lance-Master Varro Dain": ("humanoid_warrior", 56, 56, 2.2, "ae_lancer_mounted", "rare", "arcane",
                                ["Lance-Master's Thrust", "The Grand Charge", "Unhorsed", "Never Unseated"]),
    # ---------------------------------------------------------------- the Censor-Archive
    "Censor-Inquisitor":      ("humanoid_caster", 55, 56, None, "ae_inquisitor", "caster", "holy",
                               ["Searing Word", "Redaction", "Condemned"]),
    "Archive Warden":         ("humanoid_warrior", 55, 56, None, "ae_warden", "warrior", "arcane",
                               ["Warden's Blade", "Seal the Stacks", "Warded"]),
    "Cinder-Script Wisp":     ("elemental_caster", 55, 56, None, "sk_fading_wisp", "caster", "fire",
                               ["Burning Word", "Ash of Pages", "Ink-Burn"]),
    "High Censor Ilsabet Morn": ("humanoid_caster", 56, 56, 2.2, "ae_inquisitor", "rare", "holy",
                                 ["Censure", "Strike It From the Record", "Silenced", "Unwritten"]),
    # ---------------------------------------------------------------- the Gunline
    "Storm Artillerist":      ("humanoid_caster", 56, 57, None, "ae_artillerist", "caster", "nature",
                               ["Crackling Rod", "Ranging Shot", "Static"]),
    "Arcane Bombardier":      ("humanoid_caster", 56, 57, None, "ae_bombardier", "caster", "arcane",
                               ["Bombard", "Shelling", "Arcane Burn"]),
    "Gun Construct":          ("elemental_bruiser", 56, 57, None, "ae_storm_construct", "bruiser", "nature",
                               ["Discharge Fist", "Overcharge", "Shocked"]),
    "Battery-Master Ormund Krell": ("humanoid_caster", 57, 57, 2.2, "ae_artillerist", "rare", "nature",
                                    ["Battery Bolt", "Fire for Effect", "Thrown Down", "Every Gun Loaded"]),
    # ---------------------------------------------------------------- the Storm Harvest
    "Harvested Storm":        ("elemental_caster", 56, 57, None, "sk_storm_elemental", "caster", "nature",
                               ["Storm Bolt", "Wild Discharge", "Static"]),
    "Lightning Elemental":    ("elemental_caster", 56, 57, None, "sk_lightning_elemental", "caster", "nature",
                               ["Lightning Lash", "Chain Lightning", "Crackling"]),
    "Harvest Thunderbird":    ("beast_fast", 56, 57, None, "sk_thunderbird", "beast", "nature",
                               ["Thunder Talons", "Stormdive", "Charged"]),
    "Old Thunderhead":        ("beast_large", 57, 57, 2.2, "sk_thunderbird", "rare", "nature",
                               ["Old Talons", "Thunderclap", "Struck Senseless", "The Storm Answers"]),
    # ---------------------------------------------------------------- the Firmament Road
    "Ascendancy Storm Caller": ("humanoid_caster", 57, 57, None, "ae_storm_caller", "caster", "nature",
                                ["Call Lightning", "Stormfront", "Static"]),
    "Ascendancy Gunship":     ("elemental_bruiser", 57, 57, None, "ae_gunship", "bruiser", "fire",
                               ["Deck Gun", "Strafing Run", "Burning"]),
    # ---------------------------------------------------------------- the Ashwake
    "Ash Stalker":            ("beast_fast", 54, 55, None, "sk_cloud_stalker", "beast", "physical",
                               ["Bite", "Out of the Smoke", "Torn"]),
    "Smoke Jelly":            ("elemental_caster", 54, 55, None, "sk_cloud_jelly", "caster", "nature",
                               ["Sting", "Smoke Pulse", "Choking Smoke"]),
    "Cinder Ray":             ("beast_fast", 54, 55, None, "sk_sky_ray", "beast", "fire",
                               ["Cinder Lash", "Glide", "Singed"]),
    "The Ash-Mother":         ("elemental_caster", 55, 55, 2.2, "sk_cloud_jelly", "rare", "nature",
                               ["Mother's Sting", "Smother", "Drowned in Ash", "The Smoke Thickens"]),
}
RARES = {n for n, r in ROSTER.items() if r[3]}
HEALER_BOSSES = set()
ALL = dict(ROSTER)

def sprite(name):
    return ALL[name][4]


RULES_START = "    # THE ASCENDANT BASTIONS (generated by tools/build_ascendant_bastions_content.py; do not edit by hand)\n"
RULES_END = "    # END THE ASCENDANT BASTIONS\n"


def write_sprite_rules():
    path = ROOT / "creature_sprites.py"
    s = path.read_text(encoding="utf-8")
    block = RULES_START + "".join(f'    (r"^{re.escape(n.lower())}$", "{sprite(n)}"),\n' for n in ALL) + RULES_END
    if RULES_START in s:
        a = s.index(RULES_START)
        b = s.index(RULES_END) + len(RULES_END)
        s = s[:a] + block + s[b:]
    else:
        anchor = "    # THE ANCHORFIELDS (generated by tools/build_anchorfields_content.py; do not edit by hand)\n"
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
    if shape == "boss":
        # a cave boss: an opener, a hard hit, a party hit, a stun, something dangerous, a heal or a flood, last stand
        kit_ = [opener(names[0], b, s), dmg(names[1], int(b * 0.88), cooldown=4, school=s),
                dmg(f"{names[0]}, Twice", int(b * 1.3), cooldown=4, school=s),
                dmg(names[3], int(b * 0.7), cooldown=5, school=s, is_aoe=True),
                stun_hit(names[2], int(b * 1.1), 6, school=s) if s != "physical" else stun_hit(names[2], int(b * 1.1), 6),
                dot(f"{names[1]}, Deep", int(b * 0.45), 5, 4, school=s, **({"dispel_type": dispel} if s != "physical"
                                                                            else {}))]
        if name in HEALER_BOSSES:
            kit_.append(heal("Last Orders", int(b * 1.1), 6, school=s))
        else:
            kit_.append(dmg("The Citadel Answers", int(b * 1.8), cooldown=4, school=s))
        kit_.append(dict(name="Last Stand", kind="buff", amount=0, cooldown=99, mana_cost=0, school=s,
                         duration=30, self_only=True, hp_below=0.3, stat_mods={"attack_power": int(b * 0.4)}))
        return kit_
    # an open-world rare: a heavy basic, a party hit, a stun with a hammer behind it, and its last stand
    last = (shield(names[3], int(b * 1.2), school=s) if s in ("arcane", "frost") else enrage(names[3], int(b * 0.15), s))
    return [dmg(names[0], b, school=s), dmg(names[1], int(b * 0.8), cooldown=4, school=s, is_aoe=True),
            stun(names[2], int(b * 0.85), cooldown=5, school=s), dmg(f"{names[0]}, Again", int(b * 1.7), cooldown=5,
                                                                   school=s), last]


TABLE = {
    "open_zone": {"Smoke-Gale Hawk": 5, "Forge-Ash Wisp": 4},
    "subzones": {
        "The Bastion of Ascent": {"Bastion Legionary": 5, "Bastion Sky Lancer": 4, "Bastion Shield Drone": 3,
                                  "Wall-Captain Hesper Drace": 0},
        "The Ascent Causeway": {"Bastion Legionary": 3, "Causeway Construct Hound": 5},
        "The Slipways": {"Yard Overseer": 3, "Ascendancy Shipwright": 4, "Keel Construct": 4,
                         "Slipway Repair-Drone": 3, "The Unlaunched": 0},
        "The Proving Grounds": {"Lancer Recruit": 5, "Mounted Sky Lancer": 4, "Proving Construct": 3,
                                "Lance-Master Varro Dain": 0},
        "The Censor-Archive": {"Censor-Inquisitor": 4, "Archive Warden": 4, "Cinder-Script Wisp": 4,
                               "High Censor Ilsabet Morn": 0},
        "The Gunline": {"Storm Artillerist": 4, "Arcane Bombardier": 4, "Gun Construct": 4,
                        "Battery-Master Ormund Krell": 0},
        "The Storm Harvest": {"Harvested Storm": 5, "Lightning Elemental": 4, "Harvest Thunderbird": 4,
                              "Old Thunderhead": 0},
        "The Firmament Road": {"Ascendancy Storm Caller": 4, "Ascendancy Gunship": 3},
        "The Ashwake": {"Ash Stalker": 5, "Smoke Jelly": 4, "Cinder Ray": 4, "The Ash-Mother": 0},
        "Dawnspear Wreck": None,
        "The Yard Pens": None,
    },
}

#: rare -> four (name, slot, suffix, (a|w, type) or None, template)
POOLS = {
    "Wall-Captain Hesper Drace": [
        ("Drace's Wall-Captain Blade", "main_hand", "of the Champion", ("w", "sword_1h"), "str_physical"),
        ("Rampart Warden's Helm", "head", "of the Bear", ("a", "plate"), "str_physical"),
        ("No-Retreat Girdle", "waist", "of the Wolf", ("a", "mail"), "agi_int_hybrid"),
        ("Bastion Watch Cloak", "back", "of the Prophet", None, "spi_healer")],
    "The Unlaunched": [
        ("Unlaunched Keel-Plate", "chest", "of the Gorilla", ("a", "plate"), "str_int_hybrid"),
        ("Broadside Gauntlets", "hands", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Hull-Rivet Signet", "ring", "of the Sorcerer", None, "int_caster"),
        ("Slipway Shipwright's Hammer", "two_hand", "of the Champion", ("w", "mace_2h"), "str_physical")],
    "Lance-Master Varro Dain": [
        ("Lance-Master's Crystal Spear", "two_hand", "of the Monkey", ("w", "polearm"), "agi_physical"),
        ("Never-Unseated Greaves", "legs", "of the Bear", ("a", "plate"), "str_physical"),
        ("Proving Grounds Spaulders", "shoulder", "of the Wolf", ("a", "mail"), "agi_int_hybrid"),
        ("Rider's Crystal Pendant", "neck", "of the Gorilla", None, "str_int_hybrid")],
    "High Censor Ilsabet Morn": [
        ("Censor's Redacting Rod", "main_hand", "of the Prophet", ("w", "mace_1h"), "spi_healer"),
        ("Robe of the Unwritten", "chest", "of the Sorcerer", ("a", "cloth"), "int_caster"),
        ("Ash-Stained Bindings", "wrist", "of the Prophet", ("a", "cloth"), "spi_healer"),
        ("Burned Index", "off_hand", "of the Invoker", ("w", "tome"), "int_caster")],
    "Battery-Master Ormund Krell": [
        ("Krell's Ranging Rifle", "ranged", "of the Monkey", ("w", "gun"), "agi_physical"),
        ("Battery-Master's Mantle", "shoulder", "of the Invoker", ("a", "cloth"), "int_caster"),
        ("Gunline Hauberk", "chest", "of the Wolf", ("a", "mail"), "agi_int_hybrid"),
        ("Every Gun Loaded", "trinket", "of the Sorcerer", None, "int_caster")],
    "Old Thunderhead": [
        ("Thunderhead Talon", "main_hand", "of the Tiger", ("w", "fist_weapon"), "agi_physical"),
        ("Storm-Feathered Cowl", "head", "of the Prophet", ("a", "cloth"), "spi_healer"),
        ("Stormcaught Boots", "feet", "of the Wolf", ("a", "mail"), "agi_int_hybrid"),
        ("Harvest Lightning Charm", "neck", "of the Sorcerer", None, "int_caster")],
    "The Ash-Mother": [
        ("Ash-Mother's Veil", "head", "of the Sorcerer", ("a", "cloth"), "int_caster"),
        ("Smother-Hide Leggings", "legs", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Ashwake Bulwark", "off_hand", "of the Bear", ("w", "shield"), "str_physical"),
        ("Drowned-in-Ash Band", "ring", "of the Prophet", None, "spi_healer")],
}

#: gathering at 54-57: the high herbs on the natural rocks, truesilver and thorium in the islands' stone, and wood off
#: the wind-bent stands. Fishing: the Proving Grounds' pool and the Storm Harvest's rain basin.
NODES = {"ascendant_bastions": {"slots": 34, "active_percent": 0.42, "table": {
    "herb_purple_lotus": 1, "herb_firebloom": 2, "herb_khadgar": 3, "herb_sungrass": 2,
    "ore_truesilver": 2, "ore_thorium": 4, "wood_thornveil_stump": 4}}}

def fishing():
    from tools.build_fishing import FISH, window
    s_lo, s_hi = window(54, 57)
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
    rare_loot, rows = build_loot(POOLS, ROSTER, 3, "abi_")
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
    ENCOUNTERS.write_text(json.dumps(enc, indent=indent, ensure_ascii=False) + ("\n" if newline else ""),
                          encoding="utf-8")
    np_path = ROOT / "data/gathering/node_pools.json"
    nd = json.loads(np_path.read_text(encoding="utf-8"))
    nodes = json.loads(json.dumps(NODES))
    nodes["ascendant_bastions"]["fishing"] = fishing()
    nd["zones"].update(nodes)
    np_path.write_text(json.dumps(nd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out = {"_notes": ("The Ascendant Bastions' open-world rares (55-57). ONE item per kill from the rare's four; "
                      "item_level = the rare's level + 3. Hand-authored in tools/build_ascendant_bastions_content.py.")}
    out.update(rare_loot)
    RARE_LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "tools/whole_number_gear.py")], check=True, stdout=subprocess.DEVNULL)
    print(f"{len(ROSTER)} open-world creatures ({len(RARES)} rares); {len(rows)} items; gathering and fishing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
