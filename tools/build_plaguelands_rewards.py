#!/usr/bin/env python3
"""The Order of the Pale Flame's and the Argent Dawn's quartermasters, and the stones and insignia you earn them with.
Idempotent.

    PYTHONPATH=. python3 tools/build_plaguelands_rewards.py

Kyle, 16 Nov 2026: "we need the rep vendors and where the rep comes from. Pale Flame from killing Scarlet Crusade and
Argent Dawn from killing Scourge".

WHERE THE REP COMES FROM
  The Pale Flame   Scarlet kills in the open Plaguelands (5, up to Honored) and in the Scarlet Monastery (10, and 75 a
                   boss, up to Honored): tools/build_plaguelands_factions.py. Past Honored: CRUSADER'S INSIGNIA, which
                   every Scarlet in the Plaguelands carries, turned in at Sorrow Hill by the stack of ten, as often as
                   you like; the Order's quests; Hearthglen when it's built (uncapped).
  The Argent Dawn  Scourge kills in the Plaguelands (5, rares 25, up to Honored), from the same builder. Past Honored:
                   SCOURGESTONES at Light's Hope (Minion's from the western Scourge, Invader's from the eastern,
                   Corruptor's from the Scourge's rares), again and again; the Dawn's quests; Scholomance and
                   Stratholme's undead half when they're built.
  The stones and the insignia are materials, not quest items, so they drop whether or not you've a turn-in open and
  they stack (Classic's Scourgestones did the same). The turn-ins are REPEATABLE quests (world/quest_manager.py).

WHAT THEY SELL, the TBC way (tools/build_faction_rewards.py's model and rules, run here for these two only, because
that script rewrites every faction's exalted recipes bare and only tools/build_crafted_gear.py fills them back in,
and that script must not be re-run): friendly supplies; honored patterns; revered six ilvl 67 blues worn at 60;
exalted three ilvl 73 epics at 250-350g with flavour, and two recipes that craft ilvl 73 epics, AUTHORED HERE with
the same author() the crafted gear uses. A direction, not a cage: between them every role and armour type.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import build_faction_rewards as BFR  # noqa: E402

QM = {"pale_flame": "wpl_pf_quartermaster", "argent_dawn": "epl_lh_quartermaster"}

#: (id, name, slot, kind, type, identity, price in gold, flavour)
REVERED = {
    "pale_flame": [
        ("pf_sorrow_hill_bulwark_helm", "Sorrow Hill Bulwark Helm", "head", "armor", "plate", "tank", 70,
         "Plain grey plate. The Crusade's flame was ground off the brow and nothing was put back."),
        ("pf_flamewardens_mantle", "Flamewarden's Mantle", "shoulder", "armor", "cloth", "caster", 62,
         "The Order's pale flame, stitched white on grey over both shoulders."),
        ("pf_defectors_brigandine", "Defector's Brigandine", "chest", "armor", "leather", "agility", 68,
         "Crusade leather with the tabard torn off. The stitch holes are still there."),
        ("pf_uthers_vigil_gauntlets", "Uther's Vigil Gauntlets", "hands", "armor", "mail", "tide_healer", 52,
         "Worn by the Order's healers who keep the night watch at the tomb."),
        ("pf_ironworkers_girdle", "Ironworker's Girdle", "waist", "armor", "plate", "strength", 50,
         "The Flamekeeper makes a few of these himself in the evenings, and he won't say why."),
        ("pf_pale_flame_signet", "Pale Flame Signet", "ring", "armor", None, "hunter_crit", 55,
         "A white flame on a steel band. There was a red one there once."),
    ],
    "argent_dawn": [
        ("ad_argent_vanguard_breastplate", "Argent Vanguard Breastplate", "chest", "armor", "plate", "tank", 74,
         "Silvered plate for whoever stands at the front of the wall tonight."),
        ("ad_lightwardens_cord", "Lightwarden's Cord", "waist", "armor", "cloth", "healer", 48,
         "A chapel healer's cord, blessed so often the threads have gone pale."),
        ("ad_dawnstrider_leggings", "Dawnstrider Leggings", "legs", "armor", "leather", "feral", 66,
         "Cut for the Dawn's scouts, who run the dead roads between Light's Hope and the Crown Guard camp."),
        ("ad_chapel_ward_hauberk", "Chapel Ward Hauberk", "chest", "armor", "mail", "hunter", 70,
         "Argent mail with a sprig of holy thistle sewn into the collar."),
        ("ad_scourgebane_wristwraps", "Scourgebane Wristwraps", "wrist", "armor", "cloth", "caster", 44,
         "Silver thread, and the names of the Dawn's dead written along it."),
        ("ad_argent_crusaders_sabatons", "Argent Crusader's Sabatons", "feet", "armor", "plate", "crusader", 56,
         "Heavy boots for a paladin who means to walk into Stratholme and out again."),
    ],
}
EXALTED = {
    "pale_flame": [
        ("pf_callahans_rivet_maul", "Callahan's Rivet Maul", "main_hand", "weapon", "mace_2h", "strength", 340,
         "Rory Callahan forged it from the rivets of a Crusade gate he helped tear down."),
        ("pf_shield_of_the_walkout", "Shield of the Walkout", "off_hand", "weapon", "shield", "tank", 295,
         "Carried out of the Crusade the night the Order left, and never repainted."),
        ("pf_staff_of_the_pale_flame", "Staff of the Pale Flame", "main_hand", "weapon", "staff", "high_healer", 310,
         "A white flame burns at the head of it, and it has never once burned anyone."),
    ],
    "argent_dawn": [
        ("ad_light_hope_greatbow", "Light's Hope Greatbow", "ranged", "weapon", "bow", "hunter_crit", 300,
         "Strung with silvered gut. The Dawn's archers say the dead can hear it coming."),
        ("ad_argent_avengers_blade", "Argent Avenger's Blade", "main_hand", "weapon", "sword_1h", "rogue_crit", 290,
         "Light, quick and silvered. It was made for the ones who go over the wall at night."),
        ("ad_tome_of_the_last_vigil", "Tome of the Last Vigil", "off_hand", "weapon", "tome", "caster", 270,
         "The Dawn's book of every night the wall held. There's a page left at the back for tonight."),
    ],
}
#: patterns moved onto the shelf (only ones a vendor sold, so no trainer loses anything)
MOVED = {
    "pale_flame": {"honored": ["ench_bracer_major_healing", "jc_cut_smooth_truesilver_zircon"],
                   "revered": ["ench_gloves_major_healing", "jc_cut_quick_truesilver_zircon"]},
    "argent_dawn": {"honored": ["cookx_lifewarden_s_board", "rc_rune_warding_3"],
                    "revered": ["rc_capstone_holy_weapons_3"]},
}
#: (id, trade, name, slot, kind, type, identity, flavour)
EXALTED_RECIPES = {
    "pale_flame": [
        ("rep_pf_pale_warplate", "blacksmithing", "Pale Flame Warplate", "chest", "armor", "plate", "tank",
         "The Order's own warplate, grey steel with the flame left white."),
        ("rep_pf_mantle_of_the_walkout", "tailoring", "Mantle of the Walkout", "shoulder", "armor", "cloth",
         "caster_crit", "Grey silk with a white flame on each shoulder, for the casters who walked out with Rory."),
    ],
    "argent_dawn": [
        ("rep_ad_lightguard_greaves", "blacksmithing", "Argent Lightguard Greaves", "legs", "armor", "plate",
         "plate_healer", "Silvered greaves for the Dawn's paladins, who heal from the front of the wall."),
        ("rep_ad_dawnwatch_jerkin", "leatherworking", "Dawnwatch Jerkin", "chest", "armor", "leather", "agility",
         "Dark leather with silver at the seams, for the scouts who watch Stratholme's gate."),
    ],
}
#: each exalted recipe's epic gets an icon nothing else has, from Kyle's pack (installed by tools/install_epic_icons.py)
#: and recorded in data/items/crafted_icons.json so a rebuild keeps it
RECIPE_ICONS = {"rep_pf_pale_warplate": "gear_wow_plate_chest_pale",
                "rep_pf_mantle_of_the_walkout": "gear_wow_cloth_shoulder_walkout",
                "rep_ad_lightguard_greaves": "gear_wow_plate_legs_argent",
                "rep_ad_dawnwatch_jerkin": "gear_wow_leather_chest_dawnwatch"}
SUPPLIES = {"pale_flame": {"friendly": ["healing_potion_supreme"], "honored": ["elixir_icecap"]},
            "argent_dawn": {"friendly": ["mana_potion_supreme"], "honored": ["healing_potion_supreme"]}}

# ---------------------------------------------------------------------------------------------- the turn-ins
#: (item_id, name, description, icon)
MINION = ("pl_minions_scourgestone", "Minion's Scourgestone", "A sliver of dark crystal pulled out of one of the "
          "lesser dead. Light's Hope pays for these by the handful.", "qi_crystal")
INVADER = ("pl_invaders_scourgestone", "Invader's Scourgestone", "A heavier shard, carried by the Scourge that "
           "march in the east. It's cold enough to hurt.", "qi_heart_stone")
CORRUPTOR = ("pl_corruptors_scourgestone", "Corruptor's Scourgestone", "A stone the size of a fist, taken from "
             "something the Scourge thought worth naming.", "qi_gem")
INSIGNIA = ("pl_crusaders_insignia", "Crusader's Insignia", "A Scarlet Crusade badge, a red flame on a white "
            "field. The Order of the Pale Flame keeps count of every one that comes back.", "qi_signet")
#: quest id, giver, zone, title, item, how many, rep, level, description, accept, done
TURN_INS = [
    # each in the giver's own voice (Kyle, 16 Nov 2026; tools/plaguelands_quest_voice.py has the rest)
    ("pl_ts_minions_scourgestones", "epl_lh_scourgestones", "eastern_plaguelands_east", "Minion's Scourgestones",
     MINION, 10, 75, 51,
     "Bring Archmage Hale a handful of Minion's Scourgestones from the lesser dead of the western "
     "Plaguelands.",
     "The lesser dead carry Minion's Scourgestones, little slivers of the necromancy that keeps them "
     "walking. The ghouls and skeletons in the west have most of them.\n\nI break them down here, on holy "
     "ground, where it's safe to. The Dawn remembers who brings them, and so do I.\n\nBring me a handful "
     "whenever you have them. I'll take them as often as you've got them.",
     "That's a handful. The Dawn's grateful, and so am I.\n\nBring me more when you've got them."),
    ("pl_ts_invaders_scourgestones", "epl_lh_scourgestones", "eastern_plaguelands_east", "Invader's Scourgestones",
     INVADER, 10, 150, 55,
     "Bring Archmage Hale a handful of Invader's Scourgestones from the Scourge in the eastern "
     "Plaguelands.",
     "The Scourge that march in the east carry heavier shards. Invader's Scourgestones, we call them, and "
     "they're cold enough to hurt. The dead round Stratholme and Terrordale carry most of them.\n\nThe Dawn "
     "pays twice over for these. Every one is a little less of whatever moves the Scourge.\n\nBring me a "
     "handful whenever you can. Wear gloves, because they bite.",
     "These are heavy ones. Every shard here is one less thing walking toward the wall.\n\nCome back when "
     "you've got more."),
    ("pl_ts_corruptors_scourgestone", "epl_lh_scourgestones", "eastern_plaguelands_east", "A Corruptor's Scourgestone",
     CORRUPTOR, 1, 100, 51,
     "Bring Archmage Hale a Corruptor's Scourgestone from one of the Scourge's named horrors.",
     "The Scourge's named horrors carry Corruptor's Scourgestones, a fist of crystal that feels like it's "
     "watching you. I want every one of them destroyed, and the Dawn pays well for each.\n\nIf you've "
     "killed one of the Scourge's named horrors and you've got its stone, bring it to me and nobody else. "
     "Don't keep it in your pack overnight.",
     "I'll see it broken tonight. That one was watching you, I promise.\n\nThe Dawn won't forget it, and "
     "neither will the newcomers who hold the wall beside us."),
    ("pl_ts_crusaders_insignia", "wpl_pf_chaplain", "western_plaguelands_south", "Crusader's Insignia",
     INSIGNIA, 10, 75, 51,
     "Bring Chaplain Odile Marchand a handful of Crusader's Insignia from the Scarlets of the Plaguelands.",
     "Every Scarlet in the Plaguelands carries a Crusader's Insignia, a red flame on a white field. I "
     "keep count of the ones that come back to the Order, because every badge is one fewer fanatic "
     "burning somebody's farm.\n\nBring me a handful whenever you have them. I'll write each one down, and "
     "then I'll melt them. The Order pays its thanks for every handful.",
     "That's a handful of fanatics who won't be lighting anything tonight.\n\nI used to mark exams, back "
     "home. I never thought I'd be counting badges instead. Bring me more when you've got them."),
]


def drops():
    """creature -> [drop rows]: insignia from the Plaguelands' Scarlets, stones from its Scourge."""
    sys.path.insert(0, str(ROOT))
    import build_plaguelands_factions as PF
    ordinary, rares = PF.scourge()
    creatures = json.loads((ROOT / "data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"]
    out = {}

    def row(item, chance, amount=1):
        iid, name, desc, icon = item
        return {"item_id": iid, "name": name, "category": "material", "description": desc, "chance": chance,
                "amount": amount, "icon_id": icon, "sell_price": 25}
    for n in ordinary:
        lv = creatures[n]["level_range"][1]
        out[n] = [row(MINION, 0.25)] if lv < 56 else [row(INVADER, 0.15)]
    for n in rares:
        out[n] = [row(CORRUPTOR, 1.0)]
    for n in PF.OPEN_WORLD_SCARLETS:
        out[n] = [row(INSIGNIA, 0.35)]
    for n in PF.OPEN_WORLD_RARES:
        out[n] = [row(INSIGNIA, 1.0, 3)]
    return out


def main():
    import build_crafted_gear as C
    from crafted_icon_palette import Picker
    from tools.build_tempest_quests import voice_problems
    C.PICKER = Picker()
    bad = []

    # ---- the gear (merged into faction_rewards.json beside the other factions')
    fr_path = ROOT / "data/items/faction_rewards.json"
    fr = json.loads(fr_path.read_text(encoding="utf-8"))
    items = fr["items"]
    mine = set()
    for fid in QM:
        for (iid, name, slot, kind, typ, ident, price, flav) in REVERED[fid]:
            items[iid], b = BFR.author_unique(iid, name, slot, kind, typ, ident, BFR.BLUE_ILVL, "rare", flav, price)
            items[iid]["faction"] = fid
            from tools.reward_icons import unclash
            unclash(items[iid])          # an epic's icon stays its own
            mine.add(iid)
            bad += b
        for (iid, name, slot, kind, typ, ident, price, flav) in EXALTED[fid]:
            items[iid], b = BFR.author_unique(iid, name, slot, kind, typ, ident, BFR.EPIC_ILVL, "epic", flav, price)
            items[iid]["faction"] = fid
            mine.add(iid)
            bad += b

    # ---- the exalted recipes, authored here
    docs = {}
    for fid, rows in EXALTED_RECIPES.items():
        for rid, trade, name, slot, kind, typ, ident, flav in rows:
            path = ROOT / "data" / BFR.TRADE_FILE[trade] / "recipes.json"
            d = docs.setdefault(path, json.loads(path.read_text(encoding="utf-8")))
            book = d["professions"][trade]["recipes"] if "professions" in d else d["recipes"]
            inputs, tier = BFR.PLACEHOLDER[trade]
            out = {"kind": kind, "slot": slot, "stat_template": C.IDENTITIES[ident][1], "item_level": BFR.EPIC_ILVL,
                   "rarity": "epic", "material_tier": tier, "identity": ident, "flavor": flav,
                   "fixed_item_level": True, "required_level": BFR.WORN_AT, "armor_type": typ}
            item = C.author(rid, {"name": name, "output": dict(out)}, ident, flav)
            bad += C.audit_item("reputation recipe", rid, item)
            item["required_level"] = BFR.WORN_AT
            item["icon_id"] = RECIPE_ICONS[rid]
            out["item"] = item
            book[rid] = {"name": name, "inputs": dict(inputs), "skill_required": 300, "output": out,
                         "skill_range": [300, 305, 310, 315], "source": "vendor", "faction": fid,
                         "_rare_ingredients_todo": True}

    # ---- the turn-ins
    tq = []
    for (qid, giver, zone, title, item, n, _rep, lvl, desc, acc, done) in TURN_INS:
        for key, text in (("description", desc), ("accept_text", acc), ("turn_in_text", done)):
            bad += [f"{qid} {key}: {p}" for p in voice_problems(text)]
        tq.append(dict(quest_id=qid, title=title, giver_npc_id=giver, zone=zone, level_min=lvl, level_max=lvl,
                       description=desc, objectives=[{"type": "fetch", "target": item[0], "count": n,
                                                      "label": item[1]}],
                       accept_text=acc, turn_in_text=done, next_quest_id=None, repeatable=True,
                       reward_exp=0, reward_gold=0))
    if bad:
        print("FAILED - fix the data, not the check:")
        for b in bad:
            print("  -", b)
        return 1

    fr_path.write_text(json.dumps(fr, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ci_path = ROOT / "data/items/crafted_icons.json"
    ci = json.loads(ci_path.read_text(encoding="utf-8"))
    for fid, rows in EXALTED_RECIPES.items():
        for row in rows:
            ci["icons"][row[2]] = RECIPE_ICONS[row[0]]
    ci_path.write_text(json.dumps(ci, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for path, d in docs.items():
        path.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (ROOT / "data/quests/plaguelands_turnins.json").write_text(json.dumps(
        {"_doc": "Repeatable turn-ins for the Argent Dawn (Scourgestones) and the Order of the Pale Flame (Crusader's "
                 "Insignia). Written by tools/build_plaguelands_rewards.py.", "quests": tq},
        indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    dp = ROOT / "data/creatures/quest_drops.json"
    dd = json.loads(dp.read_text(encoding="utf-8"))
    ours = {MINION[0], INVADER[0], CORRUPTOR[0], INSIGNIA[0]}
    for cre, rows in dd["drops"].items():
        dd["drops"][cre] = [r for r in rows if r["item_id"] not in ours]
    for cre, rows in drops().items():
        dd["drops"].setdefault(cre, []).extend(rows)
    dd["drops"] = {k: v for k, v in dd["drops"].items() if v}
    dp.write_text(json.dumps(dd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # ---- the shoulder inscriptions (Kyle: "Shoulder enchants we can add, tabards are pointless"), sold at Revered
    from tools import plaguelands_inscriptions as INS
    n_ins = INS.install()

    # ---- the shelves, the moved patterns off the town shelves, the turn-ins' pay
    fp = ROOT / "data/factions/factions.json"
    fd = json.loads(fp.read_text(encoding="utf-8"))
    moved = {r for f in MOVED.values() for tier in f.values() for r in tier}
    for fid, qm in QM.items():
        f = fd["factions"][fid]
        rw = f.setdefault("rewards", {})
        rw["vendor_stock"] = {qm: {
            "friendly": list(SUPPLIES[fid]["friendly"]),
            "honored": list(SUPPLIES[fid]["honored"]) + MOVED[fid]["honored"],
            "revered": MOVED[fid]["revered"] + [f"unique:{r[0]}" for r in REVERED[fid]] + INS.ids(fid),
            "exalted": [f"unique:{r[0]}" for r in EXALTED[fid]] + [r[0] for r in EXALTED_RECIPES[fid]],
        }}
        rw["_comment"] = ["Gates, not a displayed ladder (the faction panel stays information only).",
                          "TBC-style shelves (tools/build_plaguelands_rewards.py, 16 Nov 2026): friendly supplies, "
                          "honored patterns, revered six ilvl 67 blues, exalted three ilvl 73 epics (250-350g) and "
                          "two epic recipes."]
        caps = f.setdefault("quest_rep", {}).setdefault("capstones", {})
        for (qid, giver, zone, *_r) in TURN_INS:
            if (fid == "argent_dawn") == (zone == "eastern_plaguelands_east"):
                caps[qid] = _r[3]
    fp.write_text(json.dumps(fd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    vp = ROOT / "data/npcs/vendors.json"
    vd = json.loads(vp.read_text(encoding="utf-8"))
    for v in vd["vendors"]:
        if v.get("sells") and v["vendor_id"] not in QM.values():
            v["sells"] = [s for s in v["sells"] if s not in moved]
    vp.write_text(json.dumps(vd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    from world.recipe_manager import _load_all_recipes
    srcs = _load_all_recipes()
    changed = {rid for rid in moved if srcs[rid][1].get("source") != "vendor"}
    print(f"{len(mine)} items for the Pale Flame and the Argent Dawn, "
          f"{sum(len(v) for v in EXALTED_RECIPES.values())} exalted recipes, {len(moved)} patterns moved "
          f"({len(changed)} not yet vendor recipes), {len(tq)} repeatable turn-ins, "
          f"{len(drops())} creatures carrying stones or insignia, {n_ins} shoulder inscriptions")
    if changed:
        print("  WARNING: these moved patterns aren't vendor recipes:", sorted(changed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
