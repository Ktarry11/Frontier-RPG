#!/usr/bin/env python3
"""Creatures, encounter tables and boss loot for the three Arathi zones and their seven interiors.

    PYTHONPATH=. python3 tools/build_arathi_content.py

Idempotent - rerunning overwrites the Arathi entries and leaves everything else alone.

THE BANDS ARE THE POINT. Kyle sited Arathi across the game's two measured content troughs, so the
levels have to land exactly: West 28-33, Central 33-37, East 37-40, with the two dungeons tuned a
step above their zones (Stromgarde 31-34, Drywhisker 37-40) because a dungeon is something you come
back for. Everything below derives its level_range from its zone band, and _check() at the bottom
fails the build if anything drifts out of it.

ROSTER RULE (playbook): 6+ distinct kits per zone, named rares per subzone, no reskins. Faithful
inland and original at sea, per Kyle - Boulderfist, Witherbark, the Syndicate and the Drywhisker
kobolds are Arathi's own cast; the Wrackline are not, because the Bloodsail are a Stranglethorn
fixture three zones south and a second pirate crew with the same name would be a reskin of a faction.

LOOT RULE: one item per kill from a hand-crafted pool of 3-4, spread across armour types, slots,
weapon types and the Str/Agi/Int/Sta/Spirit/healing/spell-power blends, covering the original nine
classes AND the 21 CoA ones. item_level = creature level + 3.
"""
import collections
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

CREATURES = "data/creatures/creatures.json"
ENCOUNTERS = "data/creatures/encounters.json"
LOOT = "data/loot/arathi_boss_loot.json"

#: zone -> (lo, hi). Every creature's level_range must sit inside its zone's band.
BANDS = {
    "Arathi West": (28, 33), "Arathi Central": (33, 37), "Arathi East": (37, 40),
    "Boulder'gor": (29, 33), "Boulderfist Hall": (34, 37), "The Drowned Barrow": (37, 40),
    "Wrackline Hold": (38, 40), "The Tidewrack": (38, 40),
    "Stromgarde Keep": (31, 34), "Drywhisker Deeps": (37, 40),
}

# (name, template, kit, lo, hi, is_boss)
ROSTER = [
    # ---------------- Arathi West, 28-33 ----------------
    ("Syndicate Footpad", "humanoid_rogue", "syndicate_footpad", 28, 31, False),
    ("Syndicate Watchman", "humanoid_warrior", "syndicate_watchman", 29, 32, False),
    ("Syndicate Shadowmage", "humanoid_caster", "syndicate_shadowmage", 29, 32, False),
    ("Syndicate Prowler", "humanoid_rogue", "syndicate_prowler", 30, 33, False),
    ("Boulderfist Ogre", "humanoid_warrior", "boulderfist_ogre", 29, 32, False),
    ("Boulderfist Brute", "humanoid_warrior", "boulderfist_brute", 30, 33, False),
    ("Witherbark Headhunter", "humanoid_warrior", "witherbark_headhunter", 29, 32, False),
    ("Witherbark Shadowcaster", "humanoid_caster", "witherbark_shadowcaster", 30, 33, False),
    ("Highland Fleshripper", "beast_fast", "highland_fleshripper", 28, 31, False),
    ("Moor Adder", "vermin_sneaky", "moor_adder", 28, 31, False),
    ("Carrion Kite", "beast_fast", "carrion_kite", 29, 32, False),
    ("Highland Stag", "beast_large", "highland_stag", 28, 31, False),
    ("Highland Elk", "beast_large", "highland_elk", 33, 37, False),
    ("Coastal Erne", "beast_fast", "coastal_erne", 37, 40, False),
    ("Shorewrack Hound", "beast_fast", "shorewrack_hound", 37, 40, False),
    # West rares - one per subzone that needs one
    ("Gruln Stonejaw", "beast_large", "gruln_stonejaw", 32, 33, True),
    ("Harbinger Veska", "humanoid_caster", "witherbark_hollow_rare", 32, 33, True),
    ("Overseer Mull", "humanoid_warrior", "goshek_overseer", 32, 33, True),

    # ---------------- Arathi Central, 33-37 ----------------
    ("Boulderfist Mauler", "humanoid_warrior", "boulderfist_mauler", 34, 37, False),
    ("Boulderfist Shaman", "humanoid_caster", "boulderfist_shaman", 33, 36, False),
    ("Witherbark Berserker", "humanoid_warrior", "witherbark_berserker", 34, 37, False),
    ("Witherbark Venomweaver", "humanoid_caster", "witherbark_venomweaver", 33, 36, False),
    ("Bound Sentinel", "elemental_bruiser", "bound_sentinel", 34, 37, False),
    ("Ring Wisp", "elemental_caster", "ring_wisp", 33, 36, False),
    ("Mere Crawler", "aquatic_basic", "mere_crawler", 33, 36, False),
    ("Drywhisker Digger", "vermin_swarm", "drywhisker_digger", 34, 37, False),
    # Central rares
    ("The Ring Warden", "elemental_bruiser", "ring_warden", 36, 37, True),
    ("Silt-Mother Ooga", "aquatic_basic", "mere_matriarch", 36, 37, True),

    # ---------------- Arathi East, 37-40 ----------------
    ("Wrackline Cutter", "humanoid_rogue", "wrackline_cutter", 37, 40, False),
    ("Wrackline Gunner", "humanoid_ranged", "wrackline_gunner", 37, 40, False),
    ("Wrackline Bosun", "humanoid_warrior", "wrackline_bosun", 38, 40, False),
    ("Wrackline Wrecklamp", "humanoid_caster", "wrackline_wrecklamp", 38, 40, False),
    ("Tidecrawler", "aquatic_basic", "tidecrawler", 37, 40, False),
    ("Reefmaw", "aquatic_basic", "reefmaw", 38, 40, False),
    ("Storm Petrel Swarm", "vermin_swarm", "storm_petrel_swarm", 37, 39, False),
    ("Barrow Shade", "undead_basic", "barrow_shade", 37, 40, False),
    ("Arathor Revenant", "undead_basic", "arathor_revenant", 38, 40, False),
    # East rares
    ("The Saltquern", "elemental_bruiser", "saltquern_rare", 39, 40, True),
    ("Old Bonepicker", "beast_fast", "bonepicker_rare", 39, 40, True),

    # ---------------- interiors ----------------
    ("Gor'mok the Pit Chief", "humanoid_warrior", "gormok_pit_chief", 32, 33, True),
    ("Boulderfist Hal'dun", "humanoid_warrior", "boulderfist_haldun", 36, 37, True),
    ("Mauler Krakk", "humanoid_warrior", "mauler_krakk", 35, 37, True),
    ("The Barrow Warden", "undead_basic", "the_barrow_warden", 39, 40, True),
    ("Thane Aldric's Shade", "undead_basic", "thane_aldrics_shade", 39, 40, True),
    ("Captain Mory Vane", "humanoid_warrior", "captain_mory_vane", 39, 40, True),
    ("Ledger-Keeper Ashkin", "humanoid_rogue", "ledger_keeper_ashkin", 38, 40, True),
    ("The Wrack-Drowned", "undead_basic", "the_wrack_drowned", 39, 40, True),
    ("Brinemaw", "aquatic_basic", "brinemaw", 38, 40, True),
    # Stromgarde Keep, 31-34
    ("Cursed Vaultkeeper", "undead_basic", "cursed_vaultkeeper", 32, 34, False),
    ("Grevan the Gatekeeper", "humanoid_warrior", "grevan_gatekeeper", 32, 33, True),
    ("Sister Mollis", "humanoid_caster", "sister_mollis", 33, 34, True),
    ("Lord Falconcrest", "humanoid_warrior", "lord_falconcrest", 34, 34, True),
    ("The Vault-Thing", "undead_basic", "the_vault_thing", 34, 34, True),
    # Drywhisker Deeps, 37-40
    ("Drywhisker Tunneler", "humanoid_warrior", "drywhisker_tunneler", 37, 39, False),
    ("Drywhisker Geomancer", "humanoid_caster", "drywhisker_geomancer", 37, 39, False),
    ("Brine-Choked Digger", "undead_basic", "brine_choked_digger", 39, 40, False),
    ("Deep Seep", "elemental_caster", "deep_seep", 39, 40, False),
    ("Grubbis Tallow", "humanoid_caster", "grubbis_tallow", 37, 38, True),
    ("Overseer Ratch", "humanoid_warrior", "overseer_ratch", 38, 39, True),
    ("The Pick-Mother", "vermin_swarm", "the_pick_mother", 39, 40, True),
    ("What They Dug Into", "elemental_caster", "what_they_dug_into", 40, 40, True),
]

#: zone -> (open-zone table, {subzone key: table}). Subzone keys MUST match the SUBZONES names in
#: the handbuilt modules - a key that does not match is a table that never rolls.
ZONES = {
    "Arathi West": (
        ("The Arathi Road", {"Highland Fleshripper": 4, "Moor Adder": 3, "Carrion Kite": 2,
                             "Syndicate Footpad": 2}),
        {
            "Thoradin's Wall": {"Syndicate Footpad": 4, "Highland Fleshripper": 3, "Moor Adder": 2},
            "The Lowland Oaks": {"Highland Stag": 4, "Highland Fleshripper": 3, "Moor Adder": 2,
                                 "Carrion Kite": 2},
            "Stromgarde Keep": {"Syndicate Watchman": 4, "Syndicate Footpad": 4,
                                "Syndicate Shadowmage": 3, "Syndicate Prowler": 2},
            "Refuge Pointe": {"Carrion Kite": 3, "Highland Stag": 2, "Moor Adder": 2},
            "The High Moor": {"Boulderfist Ogre": 4, "Highland Fleshripper": 3, "Carrion Kite": 3,
                              "Highland Stag": 2},
            "Boulder'gor Crags": {"Boulderfist Ogre": 4, "Boulderfist Brute": 3,
                                  "Highland Fleshripper": 2, "Gruln Stonejaw": 0},
            "Witherbark Hollow": {"Witherbark Headhunter": 4, "Witherbark Shadowcaster": 3,
                                  "Moor Adder": 2, "Harbinger Veska": 0},
            "Go'Shek Farm": {"Syndicate Prowler": 4, "Syndicate Watchman": 3,
                             "Syndicate Shadowmage": 2, "Overseer Mull": 0},
        }),
    "Arathi Central": (
        ("The Basin", {"Boulderfist Mauler": 3, "Witherbark Berserker": 3, "Highland Elk": 2,
                       "Ring Wisp": 2}),
        {
            "The Ring Road": {"Bound Sentinel": 4, "Ring Wisp": 4, "Witherbark Berserker": 2,
                              "The Ring Warden": 0},
            "Boulderfist Hall": {"Boulderfist Mauler": 4, "Boulderfist Shaman": 3,
                                 "Bound Sentinel": 2},
            "Witherbark Village": {"Witherbark Berserker": 4, "Witherbark Venomweaver": 3,
                                   "Boulderfist Shaman": 2},
            "Hammerfall": {"Highland Elk": 2, "Mere Crawler": 1},
            "The Sunken Mere": {"Mere Crawler": 4, "Ring Wisp": 2, "Silt-Mother Ooga": 0},
            "The Refuge Road": {"Boulderfist Mauler": 3, "Witherbark Berserker": 3,
                                "Highland Elk": 3, "Bound Sentinel": 2},
            "Drywhisker Gorge": {"Drywhisker Digger": 4, "Boulderfist Shaman": 2,
                                 "Witherbark Venomweaver": 2, "Highland Elk": 1},
            "The North Shelf": {"Boulderfist Mauler": 3, "Highland Elk": 3, "Ring Wisp": 2},
        }),
    "Arathi East": (
        ("The Drowned Coast", {"Wrackline Cutter": 3, "Tidecrawler": 3, "Coastal Erne": 2,
                               "Reefmaw": 2}),
        {
            "The Last Highland": {"Shorewrack Hound": 3, "Coastal Erne": 3, "Barrow Shade": 2},
            "The Drowned Barrow": {"Barrow Shade": 4, "Arathor Revenant": 3, "Tidecrawler": 2},
            "Saltspur Landing": {"Storm Petrel Swarm": 3, "Coastal Erne": 2},
            "The Southern Moor": {"Shorewrack Hound": 4, "Coastal Erne": 3, "Barrow Shade": 2},
            "The Wrackline Shore": {"Tidecrawler": 4, "Wrackline Cutter": 3, "Storm Petrel Swarm": 2},
            "The Wrack": {"Wrackline Cutter": 4, "Tidecrawler": 3, "Storm Petrel Swarm": 2},
            "Gallowmast Isle": {"Wrackline Cutter": 4, "Wrackline Gunner": 3, "Wrackline Bosun": 3,
                                "Wrackline Wrecklamp": 2},
            "The Far Cairn": {"Arathor Revenant": 3, "Barrow Shade": 3, "Coastal Erne": 2},
            "Bothy Rock": {"Reefmaw": 3, "Tidecrawler": 3, "Storm Petrel Swarm": 2},
            "The Tidewrack": {"Reefmaw": 4, "Tidecrawler": 3, "Wrackline Cutter": 2},
            "The Bonepicker": {"Storm Petrel Swarm": 4, "Coastal Erne": 3, "Old Bonepicker": 0},
            "The Teeth": {"Tidecrawler": 4, "Reefmaw": 2, "Storm Petrel Swarm": 2},
            "The Middenstone": {"Wrackline Gunner": 3, "Wrackline Cutter": 3, "Tidecrawler": 2},
            "Saltquern": {"Wrackline Bosun": 3, "Wrackline Wrecklamp": 2, "The Saltquern": 0},
            "The Spindrift": {"Reefmaw": 3, "Tidecrawler": 3, "Wrackline Cutter": 2},
        }),
}

#: CAVE TABLES NEST UNDER THEIR PARENT ZONE, not at the top level of encounters.json.
#: CreatureManager reads encounters["zones"][parent]["caves"][cave], so a block written at the top
#: level is dead data - the cave rolls nothing and nothing anywhere says so. Keyed here by the cave
#: name with its parent beside it so the nesting cannot be got wrong by hand.
#:
#: Single-boss caves roll these for trash; the boss and the rare are pinned on the map by the
#: handbuilt module, which is why they carry weight 0.
CAVE_PARENT = {
    "Boulder'gor": "Arathi West", "Stromgarde Keep": "Arathi West",
    "Boulderfist Hall": "Arathi Central", "Drywhisker Deeps": "Arathi Central",
    "The Drowned Barrow": "Arathi East", "Wrackline Hold": "Arathi East",
    "The Tidewrack": "Arathi East",
}
CAVES = {
    "Boulder'gor": {"Boulderfist Ogre": 4, "Boulderfist Brute": 4, "Highland Fleshripper": 2,
                    "Gor'mok the Pit Chief": 0, "Gruln Stonejaw": 0},
    "Boulderfist Hall": {"Boulderfist Mauler": 4, "Boulderfist Shaman": 3, "Bound Sentinel": 2,
                         "Boulderfist Hal'dun": 0, "Mauler Krakk": 0},
    "The Drowned Barrow": {"Barrow Shade": 4, "Arathor Revenant": 4, "Tidecrawler": 2,
                           "The Barrow Warden": 0, "Thane Aldric's Shade": 0},
    "Wrackline Hold": {"Wrackline Cutter": 4, "Wrackline Gunner": 3, "Wrackline Bosun": 3,
                       "Wrackline Wrecklamp": 2, "Captain Mory Vane": 0, "Ledger-Keeper Ashkin": 0},
    "The Tidewrack": {"Tidecrawler": 4, "Reefmaw": 4, "Storm Petrel Swarm": 2,
                      "The Wrack-Drowned": 0, "Brinemaw": 0},
    # The two DUNGEONS have hand-placed trash, so these tables exist only for the quest locator and
    # for anything that asks "what lives here" - the spawner never rolls them (fixed_spawns True).
    "Stromgarde Keep": {"Syndicate Footpad": 4, "Syndicate Watchman": 4, "Syndicate Shadowmage": 3,
                        "Cursed Vaultkeeper": 2, "Grevan the Gatekeeper": 0, "Sister Mollis": 0,
                        "Lord Falconcrest": 0, "The Vault-Thing": 0},
    "Drywhisker Deeps": {"Drywhisker Digger": 4, "Drywhisker Tunneler": 4, "Drywhisker Geomancer": 3,
                         "Brine-Choked Digger": 2, "Deep Seep": 2, "Grubbis Tallow": 0,
                         "Overseer Ratch": 0, "The Pick-Mother": 0, "What They Dug Into": 0},
}


def _creatures():
    data = json.load(open(CREATURES), object_pairs_hook=collections.OrderedDict)
    block = data.get("creatures", data)
    for (name, tpl, kit, lo, hi, boss) in ROSTER:
        block[name] = collections.OrderedDict([
            ("template", tpl), ("level_range", [lo, hi]), ("is_boss", boss), ("ability_kit", kit)])
    json.dump(data, open(CREATURES, "w"), indent=2)
    return len(ROSTER)


def _encounters():
    data = json.load(open(ENCOUNTERS), object_pairs_hook=collections.OrderedDict)
    zones = data["zones"]
    for zname, (open_z, subs) in ZONES.items():
        zones[zname] = collections.OrderedDict([
            ("open_zone", collections.OrderedDict([("name", open_z[0]),
                                                   ("creatures", open_z[1])])),
            ("subzones", collections.OrderedDict(
                (k, collections.OrderedDict([("name", k), ("creatures", v)]))
                for k, v in subs.items())),
        ])
    for cname, tbl in CAVES.items():
        parent = zones[CAVE_PARENT[cname]]
        parent.setdefault("caves", collections.OrderedDict())[cname] = collections.OrderedDict(
            [("name", cname), ("creatures", tbl)])
    json.dump(data, open(ENCOUNTERS, "w"), indent=2)
    return len(ZONES), len(CAVES)


def _check():
    """Every roster entry inside its band, every table name a real creature, every subzone key real."""
    import importlib
    errs = []
    names = {r[0] for r in ROSTER}
    existing = set(json.load(open(CREATURES)).get("creatures", {}))
    # 1. bands
    zone_of = {}
    for zname, (open_z, subs) in ZONES.items():
        for n in list(open_z[1]) + [m for t in subs.values() for m in t]:
            zone_of.setdefault(n, zname)
    for cname, tbl in CAVES.items():
        for n in tbl:
            zone_of.setdefault(n, cname)
    for (name, _t, _k, lo, hi, _b) in ROSTER:
        z = zone_of.get(name)
        if z and z in BANDS:
            blo, bhi = BANDS[z]
            # A creature may appear in several zones; check against the WIDEST band it is used in,
            # since a stag on the West moor and the same stag in Central is correct reuse.
            allz = [zz for zz, (o, s) in ZONES.items()
                    if name in o[1] or any(name in t for t in s.values())]
            allz += [c for c, t in CAVES.items() if name in t]
            lo_ok = min(BANDS[zz][0] for zz in allz if zz in BANDS)
            hi_ok = max(BANDS[zz][1] for zz in allz if zz in BANDS)
            if lo < lo_ok - 1 or hi > hi_ok + 1:
                errs.append(f"{name} is {lo}-{hi} but its zones allow {lo_ok}-{hi_ok}")
    # 2. every table name resolves
    for zname, (open_z, subs) in ZONES.items():
        for n in list(open_z[1]) + [m for t in subs.values() for m in t]:
            if n not in names and n not in existing:
                errs.append(f"{zname}: '{n}' is in a table but is not a creature")
    for cname, tbl in CAVES.items():
        for n in tbl:
            if n not in names and n not in existing:
                errs.append(f"{cname}: '{n}' is in a table but is not a creature")
    # 3. SUBZONE KEYS MUST MATCH THE MAP. A table keyed to a subzone the zone does not have is a
    # table that never rolls, and nothing anywhere reports it.
    # every cave nested under a zone that exists, and every Arathi interior covered
    enc = json.load(open(ENCOUNTERS))["zones"]
    for cname, parent in CAVE_PARENT.items():
        if cname not in enc.get(parent, {}).get("caves", {}):
            errs.append(f"{cname} is not nested under {parent} - its table will never roll")
    mods = {"Arathi West": "tools.handbuilt_arathi_west",
            "Arathi Central": "tools.handbuilt_arathi_central",
            "Arathi East": "tools.handbuilt_arathi_east"}
    for zname, modname in mods.items():
        real = {s[0] for s in importlib.import_module(modname).SUBZONES}
        for k in ZONES[zname][1]:
            if k not in real:
                errs.append(f"{zname}: subzone table '{k}' does not exist on the map")
        for k in real:
            if k not in ZONES[zname][1]:
                errs.append(f"{zname}: map subzone '{k}' has NO encounter table")
    return errs


def main():
    n = _creatures()
    nz, nc = _encounters()
    print(f"{n} creatures, {nz} zone tables, {nc} interior tables")
    errs = _check()
    for e in errs:
        print("  !!", e)
    if errs:
        print(f"{len(errs)} problems")
        return 1
    print("bands, names and subzone keys all check out")
    return 0


if __name__ == "__main__":
    sys.exit(main())
