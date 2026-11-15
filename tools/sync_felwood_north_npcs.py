#!/usr/bin/env python3
"""Create and position North Felwood's people: the Talonbranch camp and the Timbermaw at their gate.
Idempotent; follows tools/npc_data_guard.py (creates who it names, moves people to the layout's spot,
deletes nobody).

    PYTHONPATH=. python3 tools/sync_felwood_north_npcs.py

claude/felwood_brief.md: Talonbranch Glade is "a small Sentinel quest camp (no inn, no flight; quest
givers only)". The Emerald Reclamation's four peoples are all here in miniature: Sentinels, a druid, a
Timbermaw scout and a transplant who came north with them. One supply keeper so nobody walks back
to the Sanctuary for water and a whetstone. Quests come later; these are the people who'll give them.

Every line is plain speech: whole sentences, contractions, the useful thing first.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from tools.handbuilt_felwood_north import NPC_POSITIONS  # noqa: E402
from tools.npc_data_guard import safe_update  # noqa: E402

ZONE = "north_felwood"
M, F = "male", "female"

#: id -> (name, race, gender, variant, facing, greeting)
AMBIENT = {
    "fn_talonbranch_captain": ("Captain Elanya Swiftbrook", "night_elf", F, 4, "down",
                               "This is as far north as the Reclamation holds. We're here so the Sanctuary "
                               "knows what's coming before it comes."),
    "fn_talonbranch_druid": ("Druid Arathel Greenvale", "night_elf", M, 3, "right",
                             "The ground inside the stakes is clean because I clean it every morning. Don't "
                             "bring anything green and glowing back with you."),
    "fn_talonbranch_scout": ("Scout Barrowpaw", "furbolg", M, 2, "left",
                             "Felpaw was my cousins' village. I still know every path in and out of it, and "
                             "I'll tell you which ones they're watching."),
    "fn_talonbranch_medic": ("Marcus Oyelaran", "human", M, 6, "down",
                             "I was a paramedic in Toronto. Up here it's burns, bites and things I don't "
                             "have names for yet. If it's spreading, show me now and not later."),
    "fn_timbermaw_guard": ("Gatewarden Thornclaw", "furbolg", M, 5, "down",
                           "The tunnel behind me goes home to Timbermaw Hold. It's closed to everyone until "
                           "the Elders say otherwise, and the Elders haven't said."),
}

#: id -> (name, race, gender, variant, facing, greeting, sells, sells_gear)
VENDORS = {
    "fn_talonbranch_supply": ("Supply Keeper Lyria Dawnleaf", "night_elf", F, 8, "down",
                              "I've got water, whetstones and potions, and not much else. If you need a "
                              "proper shop, the Sanctuary's back down the road.",
                              ["whetstone", "flux_strong", "kit_field_repair", "healing_potion_masterwork",
                               "mana_potion_masterwork", "drink_waterskin", "roasted_meat"], False),
}

GEAR_LEVEL = 54


def main():
    names = set(AMBIENT) | set(VENDORS)
    if names != set(NPC_POSITIONS):
        raise SystemExit(f"roster and layout disagree: {sorted(names ^ set(NPC_POSITIONS))}")
    from entities.consumable_manager import get_consumable_manager
    cm = get_consumable_manager()
    mats = json.loads((ROOT / "data/gathering/materials.json").read_text(encoding="utf-8"))["materials"]
    ap, vp = ROOT / "data/npcs/ambient_npcs.json", ROOT / "data/npcs/vendors.json"
    ad, vd = json.loads(ap.read_text(encoding="utf-8")), json.loads(vp.read_text(encoding="utf-8"))
    by_n = {r["npc_id"]: r for r in ad["npcs"]}
    by_v = {r["vendor_id"]: r for r in vd["vendors"]}
    made = moved = 0
    for nid, (name, race, gender, var, facing, greet) in AMBIENT.items():
        x, y = NPC_POSITIONS[nid]
        rec = dict(npc_id=nid, name=name, zone=ZONE, x=x, y=y, greeting=greet, gender=gender, race=race,
                   appearance_variant=var, facing=facing)
        if nid in by_n:
            moved += bool(safe_update(by_n[nid], rec))
        else:
            ad["npcs"].append(rec)
            made += 1
    for vid, (name, race, gender, var, facing, greet, sells, sg) in VENDORS.items():
        bad = [s for s in sells if not cm.has_consumable(s) and s not in mats]
        if bad:
            raise SystemExit(f"{vid} sells things that don't exist: {bad}")
        x, y = NPC_POSITIONS[vid]
        rec = dict(vendor_id=vid, name=name, zone=ZONE, x=x, y=y, tile_sprite="npc", sells=sells,
                   buys_from_player=True, faction="neutral", gear_level=GEAR_LEVEL, sells_gear=sg, race=race,
                   appearance_variant=var, gender=gender, greeting=greet, facing=facing)
        if vid in by_v:
            moved += bool(safe_update(by_v[vid], rec))
        else:
            vd["vendors"].append(rec)
            made += 1
    ap.write_text(json.dumps(ad, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    vp.write_text(json.dumps(vd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"North Felwood: {made} created, {moved} moved ({len(names)} people)")


if __name__ == "__main__":
    main()
