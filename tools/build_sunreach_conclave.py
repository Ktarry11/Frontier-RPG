#!/usr/bin/env python3
"""The Sunreach Conclave: the faction, its quartermaster's shelf, and Azshara's field people. Idempotent.

    PYTHONPATH=. python3 tools/build_sunreach_conclave.py

docs/azshara_brief.md and docs/azshara_quest_plan.md. Kyle, 17 Nov 2026: "The Sunreach Conclave (new): the blood elf
magisters reclaiming what their ancestors lost. It gets its own TBC-style shelf", and its leader and quartermaster
stay quest-free so they can move to the elves' island later ("Don't tie leader or anything to a quest so they can be
moved"). On 18 Nov he picked the leader: "Proud, fair magister", an older magistrix who lost Quel'Thalas's last spires
in the Integration and wants her people's history back, not power. That's Grand Magister Velanthe Sunreach, who was
already standing in Talrendis Landing.

THE REPUTATION
  * The Landing's magisters' quests (and the Stormwatch ranger's) pay it, by giver (tools/build_azshara_quests.py).
  * The naga and the drowned dead in Azshara's open world: 10 a kill, to Honored. The Conclave wants them off its
    ancestors' coast.
  * The Drowned Palace: 75 a boss, and its trash 10 a kill to Revered (the dungeon is how you get past Honored).
THE SHELF, TBC-style like every other faction, authored with tools/build_faction_rewards.author_unique() and the
crafted gear's author() (neither of those scripts is re-run): friendly and honored supplies; revered six ilvl 67
blues; exalted three ilvl 73 epics and two recipes (tailoring and jewelcrafting, the Conclave's trades) that craft
ilvl 73 epics. Every role and armour type is somewhere on it.

THE FIELD PEOPLE: Captain Zarga Bloodfang and Ranger Thessaly Dawnsong at Stormwatch (East Azshara), and Grunt Okkar
at Valormok (West Azshara), the quest pass's givers out on the maps.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import build_faction_rewards as BFR  # noqa: E402

FID = "sunreach_conclave"
LANDING = "talrendis_landing"
QM = "tl_sunreach_quartermaster"
#: the open world's naga and drowned dead (tools/build_azshara_openworld.py): 10 a kill, to Honored
OPEN_WORLD = ["Ravencrest Shade", "Eldarath Shade", "Eldarath Construct", "Stormbay Tidehunter", "Stormbay Siren",
              "Stormbay Myrmidon", "Bitter Reaches Raider", "Bitter Reaches Wavecaller", "Bitter Reaches Brute",
              "Promenade Noble", "Promenade Handmaiden", "Court Sentinel", "Court Tormented", "Court Naga Guard",
              "Zin-Malor Priestess", "Zin-Malor Warden", "Zin-Malor Myrmidon"]
#: the Drowned Palace's trash (tools/build_drowned_palace_content.py): 10 a kill, to Revered
PALACE = ["Zin-Azshari Myrmidon", "Zin-Azshari Royal Guard", "Zin-Azshari Siren", "Zin-Azshari Tidecaller",
          "Hydra Spawn", "Drowned Highborne", "Moonguard Sentinel", "Highborne Spellbinder", "Queen's Handmaiden",
          "Tormented Courtier", "Vault Hound", "Arcane Sentry", "Mana Wyrm", "Ley Beast"]

FACTION = {
    "name": "The Sunreach Conclave",
    "description": ("Blood elf magisters who lit Firstlight Spire on Dawnhaven, and who mean to take back what their "
                    "ancestors lost on the Azshara coast now that the sea is giving Zin-Azshari back."),
    # HOME AT LAST (Kyle, 21 Nov 2026: "We do need to update the faction card now that they have a home too"). The
    # Conclave moved to Firstlight Spire on Dawnhaven (docs/dawnhaven_brief.md); Talrendis Landing is its field camp.
    "home_zone": "firstlight_spire",
    "home_name": "Firstlight Spire, on Dawnhaven off the Azshara coast (with a field camp at Talrendis Landing)",
    "leader": {
        "title": "Grand Magister",
        "name": "Velanthe Sunreach",
        "npc_id": "tl_sunreach_magister",
        "location": "The Conclave Hall, beside the spire, Firstlight Spire",
        "line": ("I watched the last spires of Quel'Thalas fall into a sea that wasn't there the day before. I won't "
                 "watch our history go the same way. I want it back, all of it, the good and the shameful."),
    },
    "_lore_note": ("Kyle, 17-18 Nov 2026: the Sunreach Conclave, its own TBC shelf, its leader quest-free and movable; "
                   "'Proud, fair magister'."),
    "lore": [
        "When the worlds merged, the sea came up over the last of Quel'Thalas's coast. The magisters who got out took "
        "ship south and found Azshara's shore rising instead: Zin-Azshari, the city their ancestors left ten thousand "
        "years ago, coming back up out of the water.",
        "Grand Magister Velanthe Sunreach gathered them into the Conclave. They mean to be standing on the shore when "
        "the city comes back, to take back what was theirs before anyone else can, and to learn what their ancestors "
        "did to make the gods sink it.",
        "Their home is Dawnhaven, an island off the coast that the old high elves hid behind wardstones long before "
        "the change. The Conclave found it empty, its outpost dead and its Lightwell dark, and took it back. They lit "
        "the spire at its head again after a thousand years and called it Firstlight, and anyone the sea washes up on "
        "its shore gets a room there, elf or not.",
        "The Grand Magister and her quartermaster keep the Conclave Hall beside the spire now. The work on the coast "
        "goes on from Talrendis Landing, which they share with Orgrimmar's salvage crews, because the Warchief has the "
        "muscle and they have the magic. Neither side likes the arrangement, and both sides keep two lists of "
        "everything that comes out of the ground.",
    ],
    "quest_rep": {
        "_comment": "Per quest, by shape. Paid by giver (tools/build_azshara_quests.FACTION_BY_GIVER).",
        "default": 325,
        "boss": 350,
        "capstones": {},
        "zones": [],
    },
    "kill_rep": {
        "_comment": ["Azshara's naga and drowned dead: 10 a kill to Honored. The Drowned Palace's trash: 10 a kill to "
                     "Revered, since the Palace is the road past Honored."],
        "creatures": {**{n: [10, "honored"] for n in OPEN_WORLD}, **{n: [10, "revered"] for n in PALACE}},
    },
    "dungeon_rep": {
        "_comment": "A boss kill in the Drowned Palace pays 75 (tools/build_drowned_palace_content.py).",
        "per_boss": 75,
        "dungeons": ["The Drowned Palace", "The Drowned Palace: The Queen's Vault"],
    },
}

#: (id, name, slot, kind, type, identity, price in gold, flavour)
REVERED = [
    ("sc_sunreach_spellweave_robe", "Sunreach Spellweave Robe", "chest", "armor", "cloth", "caster", 66,
     "Red and gold silk the Conclave brought by ship from Quel'Thalas, before there was no Quel'Thalas to sail from."),
    ("sc_dawnwatch_spaulders", "Dawnwatch Spaulders", "shoulder", "armor", "plate", "plate_healer", 62,
     "Plate for the magisters' guards, chased with a sunburst that warms in the light."),
    ("sc_leystriders_boots", "Leystrider's Boots", "feet", "armor", "leather", "agility", 58,
     "Soft boots for walking the leylines, soled with a leather that never quite touches the ground."),
    ("sc_tidewarders_hauberk", "Tidewarder's Hauberk", "chest", "armor", "mail", "tide_healer", 68,
     "Mail the Conclave's wardens wear on the coast, its rings blessed against the salt."),
    ("sc_spellbreakers_vambraces", "Spellbreaker's Vambraces", "wrist", "armor", "plate", "tank", 48,
     "Worn by the Spellbreakers who watch the Landing's gate, and the orcs who argue with them."),
    ("sc_sunreach_signet", "Sunreach Signet", "ring", "armor", None, "caster_crit", 55,
     "The Grand Magister's house mark, a sun rising over a line of sea."),
]
EXALTED = [
    ("sc_staff_of_the_last_spire", "Staff of the Last Spire", "main_hand", "weapon", "staff", "caster", 320,
     "Cut from the top of a spire that fell into the sea, and carried out of Quel'Thalas by the Grand Magister herself."),
    ("sc_dawnblade_of_the_conclave", "Dawnblade of the Conclave", "main_hand", "weapon", "sword_1h", "strength_crit", 300,
     "A Spellbreaker's sword, made for the Conclave's champion. The Conclave hasn't chosen one yet."),
    ("sc_tome_of_the_sunken_court", "Tome of the Sunken Court", "off_hand", "weapon", "tome", "high_healer", 275,
     "Highborne court records the dig brought up, rebound in Conclave red. The magisters still argue about what's in it."),
]
#: (id, trade, name, slot, kind, type, identity, flavour, icon): the icon is the pack's, for no crafted epic shares one
EXALTED_RECIPES = [
    ("rep_sc_sunreach_regalia", "tailoring", "Sunreach Regalia", "chest", "armor", "cloth", "spirit_healer",
     "The Conclave's formal robes, cut the way the Highborne court cut them before the Sundering.",
     "gear_wow_chest_cloth_11_1"),
    ("rep_sc_band_of_the_rising_sea", "jewelcrafting", "Band of the Rising Sea", "ring", "armor", None, "arcane_crit",
     "A gold band set with a pearl the dig found in Zin-Azshari's silt.", "gear_inv_jewelry_talisman_03"),
]
#: patterns moved onto the shelf from the town shelf that sold them (TBC rep patterns are sold only for standing): the
#: Conclave's tailors carry their bags
MOVED = {"honored": ["tail_shadowsilk_case"], "revered": ["tail_bloodsilk_trunk"]}
SUPPLIES = {"friendly": ["mana_potion_supreme", "healing_potion_supreme"],
            "honored": ["flask_mending", "elixir_purple_lotus"]}

#: the field people: npc_id -> (name, race, gender, variant, facing, zone, greeting)
FIELD = {
    "az_stormwatch_captain": ("Captain Zarga Bloodfang", "orc", "female", 4, "right", "east_azshara",
                              "Stormwatch sees the whole coast from here, and I don't like most of what I see. Something "
                              "came up out of the sea with that city, and it isn't done coming up."),
    "az_stormwatch_ranger": ("Ranger Thessaly Dawnsong", "blood_elf", "female", 2, "left", "east_azshara",
                             "The Conclave sent me to watch the Drowned Court. My grandmother's grandmother walked "
                             "those streets, and now there's seaweed growing on them."),
    "az_valormok_grunt": ("Grunt Okkar", "orc", "male", 3, "down", "west_azshara",
                          "The satyrs burned Valormok a month ago. I'm the last of the watch who didn't leave, and I'm "
                          "not leaving until somebody pays for it."),
}


def load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))


def save(p, d):
    (ROOT / p).write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    import build_crafted_gear as C
    from crafted_icon_palette import Picker
    from tools.build_tempest_quests import voice_problems
    from tools import handbuilt_azshara_east as AE, handbuilt_azshara_west as AW
    C.PICKER = Picker()
    bad = []

    # ---- the field people
    pos = {**AE.NPC_POSITIONS, **AW.NPC_POSITIONS}
    if set(pos) != set(FIELD):
        bad.append(f"the field people and the maps disagree: {sorted(set(pos) ^ set(FIELD))}")
    for k, v in FIELD.items():
        bad += [f"{k} greeting: {p}" for p in voice_problems(v[-1])]
    creatures = load("data/creatures/creatures.json")["creatures"]
    missing = [c for c in OPEN_WORLD + PALACE if c not in creatures]
    if missing:
        bad.append(f"kill rep for creatures that don't exist: {missing}")
    fd = load("data/factions/factions.json")
    for fid, f in fd["factions"].items():
        if fid == FID:
            continue
        theirs = set((f.get("kill_rep") or {}).get("creatures", {}))
        clash = theirs & set(OPEN_WORLD + PALACE)
        if clash:
            bad.append(f"{sorted(clash)} already pay {fid}; a creature pays one faction")

    # ---- the gear
    fr = load("data/items/faction_rewards.json")
    items = fr["items"]
    from tools.reward_icons import unclash
    for (iid, name, slot, kind, typ, ident, price, flav) in REVERED:
        items[iid], b = BFR.author_unique(iid, name, slot, kind, typ, ident, BFR.BLUE_ILVL, "rare", flav, price)
        items[iid]["faction"] = FID
        unclash(items[iid])
        bad += b
    for (iid, name, slot, kind, typ, ident, price, flav) in EXALTED:
        items[iid], b = BFR.author_unique(iid, name, slot, kind, typ, ident, BFR.EPIC_ILVL, "epic", flav, price)
        items[iid]["faction"] = FID
        bad += b

    # ---- the exalted recipes
    docs = {}
    picks = load("data/items/crafted_icons.json")
    for rid, trade, name, slot, kind, typ, ident, flav, icon in EXALTED_RECIPES:
        path = ROOT / "data" / BFR.TRADE_FILE[trade] / "recipes.json"
        d = docs.setdefault(path, json.loads(path.read_text(encoding="utf-8")))
        book = d["professions"][trade]["recipes"] if "professions" in d else d["recipes"]
        inputs, tier = BFR.PLACEHOLDER[trade]
        out = {"kind": kind, "slot": slot, "stat_template": C.IDENTITIES[ident][1], "item_level": BFR.EPIC_ILVL,
               "rarity": "epic", "material_tier": tier, "identity": ident, "flavor": flav,
               "fixed_item_level": True, "required_level": BFR.WORN_AT}
        if kind == "weapon":
            out["weapon_type"] = typ
            ident = C.weapon_identity(typ, ident)
        else:
            out["armor_type"] = typ                 # None for a ring, the way the jewelcrafting book has them
        item = C.author(rid, {"name": name, "output": dict(out)}, ident, flav)
        bad += C.audit_item("reputation recipe", rid, item)
        item["required_level"] = BFR.WORN_AT
        item["icon_id"] = icon
        out["item"] = item
        book[rid] = {"name": name, "inputs": dict(inputs), "skill_required": 300, "output": out,
                     "skill_range": [300, 305, 310, 315], "source": "vendor", "faction": FID,
                     "_rare_ingredients_todo": True}
        picks["icons"][name] = icon
    if bad:
        print("FAILED - fix the data, not the check:")
        for b in bad:
            print("  -", b)
        return 1

    # ---- write
    rec = fd["factions"].get(FID, {})
    keep_rewards = rec.get("rewards")
    keep_also = (rec.get("quest_rep") or {}).get("also")
    rec.update(json.loads(json.dumps(FACTION)))
    if keep_also:
        rec["quest_rep"]["also"] = keep_also
    rw = keep_rewards or {}
    rw["vendor_stock"] = {QM: {
        "friendly": list(SUPPLIES["friendly"]),
        "honored": list(SUPPLIES["honored"]) + MOVED["honored"],
        "revered": MOVED["revered"] + [f"unique:{r[0]}" for r in REVERED],
        "exalted": [f"unique:{r[0]}" for r in EXALTED] + [r[0] for r in EXALTED_RECIPES],
    }}
    rw["_comment"] = ["Gates, not a displayed ladder (the faction panel stays information only).",
                      "TBC-style shelves (tools/build_sunreach_conclave.py, 18 Nov 2026): friendly and honored "
                      "supplies, revered six ilvl 67 blues, exalted three ilvl 73 epics and two epic recipes."]
    rw.setdefault("quests", {})
    rec["rewards"] = rw
    fd["factions"][FID] = rec
    save("data/factions/factions.json", fd)
    save("data/items/faction_rewards.json", fr)
    save("data/items/crafted_icons.json", picks)
    for path, d in docs.items():
        path.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # the moved patterns leave the town shelves
    vd = load("data/npcs/vendors.json")
    moved = set(MOVED["honored"] + MOVED["revered"])
    for v in vd["vendors"]:
        if v.get("sells") and v["vendor_id"] != QM:
            v["sells"] = [x for x in v["sells"] if x not in moved]
    save("data/npcs/vendors.json", vd)

    ad = load("data/npcs/ambient_npcs.json")
    aby = {a["npc_id"]: a for a in ad["npcs"]}
    for nid, (name, race, gender, var, facing, zone, greet) in FIELD.items():
        x, y = pos[nid]
        r = aby.get(nid)
        if r is None:
            r = {"npc_id": nid}
            ad["npcs"].append(r)
        r.update(name=name, zone=zone, x=x, y=y, greeting=greet, gender=gender, race=race,
                 appearance_variant=var, facing=facing)
    save("data/npcs/ambient_npcs.json", ad)
    print(f"{FACTION['name']}: {len(OPEN_WORLD) + len(PALACE)} creatures pay it, the Drowned Palace's bosses 75; "
          f"shelf {len(REVERED)} blues, {len(EXALTED)} epics, {len(EXALTED_RECIPES)} recipes; "
          f"{len(FIELD)} field people")
    return 0


if __name__ == "__main__":
    sys.exit(main())
