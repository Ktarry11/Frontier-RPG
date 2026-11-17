#!/usr/bin/env python3
"""The Eastern Plaguelands' open-world creatures, rares, encounter tables and rare loot. Idempotent.

    PYTHONPATH=. python3 tools/build_epl_openworld.py

docs/plaguelands_design.md. Where the plague went worst. The Scourge holds the west (Plaguewood's spiders, Terrordale's
dead, the carts at Corin's Crossing, Stratholme's gates), the Scarlet Crusade holds Tyr's Hand on the coast, and the
far north-east is what's left of the trolls and elves who held out longest.

    WEST EASTERN PLAGUELANDS (55-58)
      the open plains       plague hounds, carrion grubs, frenzied ghouls, gargoyles
      Terrordale            the dead of the vale: ghosts, skeletal mages, ghouls        rare: The Terror of the Dale
      The Marris Stead      the burned farm: risen farmhands, crows                     rare: Old Marris
      Plaguewood            Plaguewood spiders and crypt fiends in the webs             rare: The Plaguewood Matriarch
      Stratholme Gates      death knights and gargoyles at the gate                     rare: Gatekeeper Vorthas
      The Fungal Vale       plague slimes and spore-walkers                             rare: The Fungal Mass
      Corin's Crossing      the Cult of the Damned working the plague carts             rare: Cartmaster Corin
    EAST EASTERN PLAGUELANDS (56-60)
      the open plains       blighted horses, plague-rotted bears, carrion bats
      Darrowshire           the ghosts of the battle                                    rare: Captain Redpath's Shade
      Blackwood Lake        drowned dead and lake beasts                                rare: The Blackwood Drowner
      Tyr's Hand            the Scarlet Crusade's fortress town                         rare: Abbot Varenne
      Quel'Lithien Lodge    the elven lodge's restless rangers                          rare: Ranger-Lord Saelith
      Zul'Mashar            the Mossflayer trolls                                       rare: Zul'Mashar the Last
      The Pestilent Scar    the bone colossus's ground                                  rare: The Bone Colossus
      Crown Guard Tower     the empty tower on the road (its camp moved into Light's Hope)
      Light's Hope Gate     safe (the chapel is a town map now, tools/handbuilt_lights_hope.py)

THE PURE 60 RULE: neither map is pure 60, so nothing here drops or grows a post-game material.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.build_return_voyage_content import (  # noqa: E402
    CREATURES, KITS, ENCOUNTERS, kit_slug, merge_json, _detect_format,
    dmg, dot, debuff, buff, loot_audit,
)
from tools.build_tempest_openworld import enrage, stun, shield  # noqa: E402

LOOT = ROOT / "data/loot/plaguelands_east_rare_loot.json"
WEST = "Eastern Plaguelands West"
EAST = "Eastern Plaguelands East"

#: name -> (template, lo, hi, boss multiplier or None, sprite, zone)
ROSTER = {
    # ---- West EPL: the open plains
    "Plague Hound":             ("beast_fast",        55, 56, None, "worg_2", WEST),
    "Carrion Grub":             ("vermin_swarm",      55, 56, None, "slime_green_2", WEST),
    "Frenzied Ghoul":           ("undead_basic",      55, 56, None, "ghoul_2", WEST),
    "Stone-Winged Gargoyle":    ("undead_beast",      56, 57, None, "bat", WEST),
    # Terrordale
    "Terrordale Spirit":        ("undead_caster",     56, 57, None, "wraith_1", WEST),
    "Terrordale Skeletal Mage": ("undead_caster",     56, 57, None, "skeleton_marksman", WEST),
    "Terrordale Ghoul":         ("undead_basic",      56, 57, None, "ghoul_1", WEST),
    # the Marris Stead
    "Marris Farmhand":           ("undead_basic",      55, 56, None, "zombie_2", WEST),
    "Stead Crow":               ("beast_fast",        55, 56, None, "vulture_1", WEST),
    # Plaguewood
    "Plaguewood Spider":        ("beast_fast",        56, 57, None, "spider_4", WEST),
    "Plaguewood Crypt Fiend":   ("undead_beast",      57, 58, None, "spider_broodmother_2", WEST),
    # Stratholme Gates
    "Gate Death Knight":        ("undead_warrior",    57, 58, None, "skeleton_warrior_2", WEST),
    "Gate Gargoyle":            ("undead_beast",      57, 58, None, "bat", WEST),
    # the Fungal Vale
    "Vale Plague Slime":        ("elemental_bruiser", 56, 57, None, "slime_green_1", WEST),
    "Spore-Walker":             ("undead_basic",      56, 57, None, "zombie_6", WEST),
    # Corin's Crossing
    "Cult Plaguebringer":       ("humanoid_caster",   56, 57, None, "cultist_robed_6", WEST),
    "Cult Cart Driver":         ("humanoid_warrior",  56, 57, None, "cult_overseer", WEST),
    "Crossing Abomination":     ("undead_warrior",    57, 57, None, "abomination_1", WEST),
    # rares
    "The Terror of the Dale":   ("undead_caster",     57, 57, 2.2, "wraith_3", WEST),
    "Old Marris":               ("undead_warrior",    56, 56, 2.0, "scarecrow_golem", WEST),
    "The Plaguewood Matriarch": ("undead_beast",      58, 58, 2.3, "spider_broodmother_1", WEST),
    "Gatekeeper Vorthas":       ("undead_warrior",    58, 58, 2.3, "skeleton_warrior_1", WEST),
    "The Fungal Mass":          ("elemental_bruiser", 57, 57, 2.1, "ooze_acid_2", WEST),
    "Cartmaster Corin":         ("humanoid_caster",   57, 57, 2.2, "necromancer", WEST),
    # ---- East EPL: the open plains
    "Blighted Warhorse":        ("beast_large",       56, 57, None, "stag", EAST),
    "Plague-Rotted Bear":       ("beast_large",       56, 58, None, "bear_6", EAST),
    "Carrion Bat":              ("beast_fast",        56, 57, None, "bat", EAST),
    # Darrowshire
    "Darrowshire Spirit":       ("undead_caster",     57, 58, None, "wraith_pale", EAST),
    "Darrowshire Ghoul":        ("undead_basic",      57, 58, None, "ghoul_gaunt", EAST),
    # Blackwood Lake
    "Blackwood Drowned":        ("undead_basic",      56, 57, None, "zombie_3", EAST),
    "Blackwood Snapjaw":        ("beast_large",       56, 57, None, "turtle_snapping", EAST),
    # Tyr's Hand
    "Tyr's Hand Crusader":      ("humanoid_warrior",  58, 59, None, "scarlet_crusader", EAST),
    "Tyr's Hand Abbot":         ("humanoid_caster",   58, 59, None, "scarlet_priest", EAST),
    "Tyr's Hand Marksman":      ("humanoid_ranged",   58, 59, None, "scarlet_archer", EAST),
    "Tyr's Hand Houndmaster":   ("humanoid_warrior",  58, 59, None, "houndmaster", EAST),
    # Quel'Lithien Lodge
    "Restless Lodge Ranger":    ("undead_caster",     57, 58, None, "wraith_2", EAST),
    # Zul'Mashar
    "Mossflayer Warrior":       ("humanoid_warrior",  58, 59, None, "troll_axe_1", EAST),
    "Mossflayer Shadowhunter":  ("humanoid_caster",   58, 59, None, "troll_witchdoctor", EAST),
    "Mossflayer Scout":         ("humanoid_ranged",   58, 59, None, "troll_axe_2", EAST),
    # the Pestilent Scar
    "Scar Bone Construct":      ("undead_warrior",    58, 59, None, "skeleton_warrior_2", EAST),
    # rares
    "Captain Redpath's Shade":  ("undead_warrior",    58, 58, 2.2, "wraith_pale", EAST),
    "The Blackwood Drowner":    ("undead_basic",      57, 57, 2.0, "zombie_4", EAST),
    "Abbot Varenne":            ("humanoid_caster",   59, 59, 2.3, "scarlet_priest", EAST),
    "Ranger-Lord Saelith":      ("undead_caster",     59, 59, 2.2, "wraith_1", EAST),
    "Zul'Mashar the Last":      ("humanoid_warrior",  59, 59, 2.3, "troll_axe_3", EAST),
    "The Bone Colossus":        ("undead_warrior",    60, 60, 2.6, "abomination_2", EAST),
}
RARES = {n for n, r in ROSTER.items() if r[3]}


def _k(name, lvl):
    """A kit by shape, sized to the level: the same families the West's open world uses."""
    t = ROSTER[name][0]
    b = int(round(196 * (1 + 0.035 * (lvl - 55))))
    if ROSTER[name][3]:
        b = int(round(b * 1.62))
        if t.endswith("caster"):
            return [dmg("Death Bolt", b, school="shadow"),
                    dmg("Wail of the Dead", int(b * 0.8), cooldown=5, school="shadow", is_aoe=True),
                    dot("Withering Touch", int(b * 0.27), 3, 4, school="shadow"),
                    shield("Grave Ward", int(b * 2.9), school="shadow")]
        return [dmg("Crushing Blow", b), dmg("Sweeping Strike", int(b * 0.8), cooldown=4, is_aoe=True),
                stun("Knocked Flat", int(b * 0.74)), enrage("Rising Fury", 115)]
    if t.startswith("humanoid") and "Tyr's Hand" in name or name.startswith("Tyr"):
        if t.endswith("caster"):
            return [dmg("Smite", b, school="holy"), dmg("Holy Fire", int(b * 0.85), cooldown=4, school="holy"),
                    shield("Power Word: Shield", int(b * 2.1), school="holy")]
        return [dmg("Crusader Strike", b + 6), dmg("Holy Strike", int(b * 0.86), cooldown=4, school="holy"),
                buff("Devotion", 6, 4, {"armor": 126})]
    if t.endswith("caster"):
        return [dmg("Shadow Bolt", b, school="shadow"), dot("Unholy Rot", int(b * 0.27), 3, 4, school="shadow"),
                debuff("Enfeeble", 5, 3, {"attack_power": -46})]
    if t in ("undead_basic", "vermin_swarm"):
        return [dmg("Ghoulish Claw", b), dmg("Gnaw", int(b * 0.86), cooldown=3),
                dot("Grave Rot", int(b * 0.27), 3, 3, school="nature", dispel_type="disease")]
    if t == "undead_beast":
        return [dmg("Rending Claws", b + 4), dmg("Swoop", int(b * 0.86), cooldown=4),
                dot("Crypt Poison", int(b * 0.27), 3, 3, school="nature", dispel_type="poison")]
    if t == "elemental_bruiser":
        return [dmg("Acid Slap", b, school="nature"), dot("Corrosive Ooze", int(b * 0.27), 3, 3, school="nature"),
                debuff("Dissolve Armour", 5, 3, {"armor": -124})]
    if t == "humanoid_ranged":
        return [dmg("Aimed Shot", b + 4), dmg("Volley", int(b * 0.86), cooldown=5, is_aoe=True),
                debuff("Pinned", 5, 2, {"dodge_rating": -46})]
    if t.startswith("humanoid") or t == "undead_warrior":
        return [dmg("Heavy Blow", b + 8), dmg("Cleave", int(b * 0.86), cooldown=4, is_aoe=True),
                buff("Battle Fury", 6, 3, {"attack_power": 60})]
    return [dmg("Savage Bite", b), dmg("Lunge", int(b * 0.86), cooldown=3),
            dot("Plague Bite", int(b * 0.27), 3, 3, school="nature", dispel_type="disease")]


KITSETS = {n: _k(n, r[2]) for n, r in ROSTER.items()}


def _table(zone, open_zone, subzones):
    return {"open_zone": {"name": zone, "creatures": open_zone}, "subzones": subzones}


TABLES = {
    WEST: _table(WEST, {"Plague Hound": 5, "Carrion Grub": 3, "Frenzied Ghoul": 4, "Stone-Winged Gargoyle": 2}, {
        "Terrordale": {"name": "Terrordale", "creatures": {"Terrordale Spirit": 5, "Terrordale Skeletal Mage": 4,
                                                           "Terrordale Ghoul": 5, "The Terror of the Dale": 0}},
        "The Marris Stead": {"name": "The Marris Stead", "creatures": {"Marris Farmhand": 6, "Stead Crow": 4,
                                                                       "Old Marris": 0}},
        "Plaguewood": {"name": "Plaguewood", "creatures": {"Plaguewood Spider": 6, "Plaguewood Crypt Fiend": 3,
                                                           "The Plaguewood Matriarch": 0}},
        "Stratholme Gates": {"name": "Stratholme Gates", "creatures": {"Gate Death Knight": 4, "Gate Gargoyle": 4,
                                                                       "Gatekeeper Vorthas": 0}},
        "The Fungal Vale": {"name": "The Fungal Vale", "creatures": {"Vale Plague Slime": 5, "Spore-Walker": 5,
                                                                     "The Fungal Mass": 0}},
        "Corin's Crossing": {"name": "Corin's Crossing", "creatures": {"Cult Plaguebringer": 5, "Cult Cart Driver": 4,
                                                                       "Crossing Abomination": 2,
                                                                       "Cartmaster Corin": 0}},
    }),
    EAST: _table(EAST, {"Blighted Warhorse": 3, "Plague-Rotted Bear": 4, "Carrion Bat": 4}, {
        "Crown Guard Tower": {"name": "Crown Guard Tower", "creatures": {"Blighted Warhorse": 2, "Carrion Bat": 3}},
        "Light's Hope Gate": {"name": "Light's Hope Gate", "safe": True, "creatures": {}},
        "Darrowshire": {"name": "Darrowshire", "creatures": {"Darrowshire Spirit": 5, "Darrowshire Ghoul": 5,
                                                             "Captain Redpath's Shade": 0}},
        "Blackwood Lake": {"name": "Blackwood Lake", "creatures": {"Blackwood Drowned": 5, "Blackwood Snapjaw": 5,
                                                                   "The Blackwood Drowner": 0}},
        "Tyr's Hand": {"name": "Tyr's Hand", "creatures": {"Tyr's Hand Crusader": 5, "Tyr's Hand Abbot": 4,
                                                           "Tyr's Hand Marksman": 4, "Tyr's Hand Houndmaster": 3,
                                                           "Abbot Varenne": 0}},
        "Quel'Lithien Lodge": {"name": "Quel'Lithien Lodge", "creatures": {"Restless Lodge Ranger": 6,
                                                                           "Carrion Bat": 2,
                                                                           "Ranger-Lord Saelith": 0}},
        "Zul'Mashar": {"name": "Zul'Mashar", "creatures": {"Mossflayer Warrior": 5, "Mossflayer Shadowhunter": 4,
                                                           "Mossflayer Scout": 4, "Zul'Mashar the Last": 0}},
        "The Pestilent Scar": {"name": "The Pestilent Scar", "creatures": {"Scar Bone Construct": 5,
                                                                           "Plague-Rotted Bear": 2,
                                                                           "The Bone Colossus": 0}},
    }),
}

#: (item level, [(name, slot, kind, type, stat template)]). Item level = the rare's level + 3.
POOLS = {
    "The Terror of the Dale": (60, [("Dale-Haunt Cowl", "head", "armor", "cloth", "int_caster"),
                                    ("Terrordale Warboots", "feet", "armor", "plate", "str_physical"),
                                    ("Vale-Ghost Cloak", "back", "armor", "cloth", "agi_physical"),
                                    ("Wand of the Dale", "ranged", "weapon", "wand", "int_caster")]),
    "Old Marris": (59, [("Marris Stead Overalls", "legs", "armor", "leather", "agi_physical"),
                        ("Farmhand's Burial Shroud", "chest", "armor", "cloth", "spi_healer"),
                        ("Stead-Keeper's Gauntlets", "hands", "armor", "mail", "agi_int_hybrid"),
                        ("Marris Family Pitchfork", "main_hand", "weapon", "polearm", "str_physical")]),
    "The Plaguewood Matriarch": (61, [("Silk-Bound Leggings", "legs", "armor", "cloth", "int_caster"),
                                      ("Matriarch's Carapace", "chest", "armor", "mail", "agi_physical"),
                                      ("Webstrider Boots", "feet", "armor", "leather", "agi_physical"),
                                      ("Fang of the Plaguewood", "main_hand", "weapon", "dagger", "agi_physical")]),
    "Gatekeeper Vorthas": (61, [("Gatekeeper's Pauldrons", "shoulder", "armor", "plate", "str_physical"),
                                ("Stratholme Gate Girdle", "waist", "armor", "plate", "str_int_hybrid"),
                                ("Deathcharger's Reins Bracers", "wrist", "armor", "leather", "agi_physical"),
                                ("Vorthas' Runeblade", "main_hand", "weapon", "sword_2h", "str_physical")]),
    "The Fungal Mass": (60, [("Sporecap Hood", "head", "armor", "leather", "spi_healer"),
                             ("Vale-Rot Mantle", "shoulder", "armor", "cloth", "int_caster"),
                             ("Fungal Waders", "feet", "armor", "mail", "agi_int_hybrid"),
                             ("Mycelial Staff", "main_hand", "weapon", "staff", "spi_healer")]),
    "Cartmaster Corin": (60, [("Cartmaster's Robes", "chest", "armor", "cloth", "int_caster"),
                              ("Plague-Cart Driving Gloves", "hands", "armor", "leather", "agi_physical"),
                              ("Crossing Warden's Helm", "head", "armor", "plate", "str_physical"),
                              ("Corin's Plague Rod", "main_hand", "weapon", "staff", "int_caster")]),
    "Captain Redpath's Shade": (61, [("Redpath's Darrowshire Plate", "chest", "armor", "plate", "str_physical"),
                                     ("Shade-Touched Treads", "feet", "armor", "leather", "agi_int_hybrid"),
                                     ("Darrowshire Defender's Cloak", "back", "armor", "cloth", "str_physical"),
                                     ("Captain's Last Stand", "main_hand", "weapon", "sword_1h", "str_physical")]),
    "The Blackwood Drowner": (60, [("Drowner's Kelp Wraps", "wrist", "armor", "cloth", "spi_healer"),
                                   ("Blackwood Lakebed Boots", "feet", "armor", "mail", "agi_physical"),
                                   ("Waterlogged Leggings", "legs", "armor", "leather", "agi_physical"),
                                   ("Drowner's Hook", "main_hand", "weapon", "axe_1h", "str_physical")]),
    "Abbot Varenne": (62, [("Abbot's Crimson Vestments", "chest", "armor", "cloth", "spi_healer"),
                           ("Tyr's Hand Templar Helm", "head", "armor", "plate", "str_int_hybrid"),
                           ("Abbey Bell-Ringer's Gloves", "hands", "armor", "mail", "int_caster"),
                           ("Varenne's Censer", "main_hand", "weapon", "mace_1h", "spi_healer")]),
    "Ranger-Lord Saelith": (62, [("Quel'Lithien Ranger's Hood", "head", "armor", "leather", "agi_physical"),
                                 ("Lodge-Keeper's Mantle", "shoulder", "armor", "mail", "agi_physical"),
                                 ("Saelith's Spirit Wraps", "hands", "armor", "cloth", "int_caster"),
                                 ("Bow of the Last Lodge", "ranged", "weapon", "bow", "agi_physical")]),
    "Zul'Mashar the Last": (62, [("Mossflayer Warlord's Belt", "waist", "armor", "mail", "agi_physical"),
                                 ("Last Chieftain's Headdress", "head", "armor", "leather", "spi_healer"),
                                 ("Zul'Mashar Bonecage", "chest", "armor", "plate", "str_physical"),
                                 ("Zul'Mashar's Ritual Axe", "main_hand", "weapon", "axe_2h", "str_physical")]),
    "The Bone Colossus": (63, [("Colossus Bonecage Legplates", "legs", "armor", "plate", "str_physical"),
                               ("Pestilent Scar Robe", "chest", "armor", "cloth", "int_caster"),
                               ("Ossuary Grips", "hands", "armor", "leather", "agi_physical"),
                               ("Marrow-Splitter", "main_hand", "weapon", "mace_2h", "str_physical")]),
}


def main():
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import tools.handbuilt_epl_west as EW
    import tools.handbuilt_epl_east as EE
    for zone, mod in ((WEST, EW), (EAST, EE)):
        declared = {s[0] for s in mod.SUBZONES}
        if set(TABLES[zone]["subzones"]) != declared:
            print(f"FAILED: {zone} subzones disagree with the map: {sorted(set(TABLES[zone]['subzones']) ^ declared)}")
            return 1
    named = set()
    for t in TABLES.values():
        named |= set(t["open_zone"]["creatures"])
        if RARES & set(t["open_zone"]["creatures"]):
            print("FAILED: a rare is in an open-zone table")
            return 1
        for s in t["subzones"].values():
            named |= set(s["creatures"])
    if named != set(ROSTER) or set(POOLS) != RARES:
        print(f"FAILED: tables, roster and pools differ: {sorted(named ^ set(ROSTER))} {sorted(set(POOLS) ^ RARES)}")
        return 1
    existing = json.loads(CREATURES.read_text(encoding="utf-8"))["creatures"]
    kits_now = json.loads(KITS.read_text(encoding="utf-8"))["kits"]
    owners = {v.get("ability_kit"): n for n, v in existing.items()}
    for name in ROSTER:
        k = kit_slug(name)
        if k in kits_now and owners.get(k, name) != name:
            print(f"FAILED: {name}'s kit '{k}' already belongs to {owners[k]}; pick another name")
            return 1
    for name, (_t, lo, hi, mult, sprite, _z) in ROSTER.items():
        if mult and POOLS[name][0] != hi + 3:
            print(f"FAILED: {name} is level {hi} and its loot is item level {POOLS[name][0]}")
            return 1
        if not (ROOT / "assets/creatures" / f"{sprite}.png").exists():
            print(f"FAILED: {name}'s sprite {sprite} is not on disk")
            return 1
        prior = existing.get(name)
        if prior and prior.get("level_range") != [lo, hi]:
            print(f"FAILED: {name} already exists elsewhere ({prior.get('level_range')}); names never repeat")
            return 1

    creatures = {}
    for name, (template, lo, hi, mult, _sprite, _z) in ROSTER.items():
        e = {"template": template, "level_range": [lo, hi], "is_boss": bool(mult), "ability_kit": kit_slug(name)}
        if mult:
            e["boss_multiplier"] = mult
        creatures[name] = e
    merge_json(CREATURES, "creatures", creatures, "creatures.json")
    merge_json(KITS, "kits", {kit_slug(n): k for n, k in KITSETS.items()}, "ability_kits.json")

    raw = ENCOUNTERS.read_text(encoding="utf-8")
    enc = json.loads(raw)
    indent, newline = _detect_format(enc, raw)
    for zone, table in TABLES.items():
        entry = enc.setdefault("zones", {}).setdefault(zone, {})
        entry["open_zone"] = table["open_zone"]
        entry["subzones"] = table["subzones"]
    ENCOUNTERS.write_text(json.dumps(enc, indent=indent, ensure_ascii=False) + ("\n" if newline else ""),
                          encoding="utf-8")
    for zone, table in TABLES.items():
        print(f"  encounters.json: {zone}, open zone + {len(table['subzones'])} subzones")

    from entities.loot_generator import LootGenerator
    from entities.item_budget import fit_to_curve
    from tools.fit_rares_to_curve import give_lead
    gen = LootGenerator()
    out = {"_notes": ("The Eastern Plaguelands' open-world rares. Identity hand-authored in tools/build_epl_openworld.py; "
                      "stats from LootGenerator at rare budget.")}
    rows = []
    for boss, (ilvl, items) in POOLS.items():
        built = []
        for (name, slot, kind, atype, template) in items:
            if kind == "armor":
                it = gen.generate_armor_piece(slot, atype, template, ilvl, "rare")
            else:
                it = gen.generate_weapon(slot, atype, template, ilvl, "rare", strict=True)
            if it is None:
                print(f"FAILED: the generator would not build {name}")
                return 1
            d = it.to_dict()
            give_lead(d)        # on the item curve (tools/fit_rares_to_curve.py, Kyle 16 Nov)
            fit_to_curve(d)
            d["name"] = name
            d["item_id"] = "pl_" + name.lower().replace("'", "").replace(" ", "_").replace("-", "_")
            built.append(d)
            rows.append((name, slot, kind, atype, template))
        out[boss] = built
    problems = loot_audit(rows)
    if problems:
        print("\nFAILED - fix the pools, not the check:")
        for pr in problems:
            print(f"  - {pr}")
        return 1
    LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  {LOOT.relative_to(ROOT)}: {len(POOLS)} pools, {len(rows)} items")
    return 0


if __name__ == "__main__":
    sys.exit(main())
