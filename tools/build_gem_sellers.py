#!/usr/bin/env python3
"""Gem sellers: pre-cut gems for anyone, the WoW way. Idempotent.

    PYTHONPATH=. python3 tools/build_gem_sellers.py

Kyle, 14 Nov 2026: "Also make gem sellers! For weaker pre-cut gems. Wow style (if you're not a JC
you should still get some options)."

FOUR SELLERS, one for each stretch of the socket levels (gear has sockets from 30):

  Orgrimmar           Fizwick Gemstone, already standing at his locked stall in the market.
  Undercity           Gemcutter Voss, already in the Undercity market.
  Steamwheedle Port   a new gem-trader in the upper yard beside the smith.
  Onyxhollow          a new gem-trader on Forge Row beside the smith.

WEAKER THAN A JEWELCRAFTER'S. A seller only stocks cuts of the common stone in each vein (never
the rare one, which cuts into a rare-quality gem), and stops a band below the best a jewelcrafter
can cut. Each stone comes in its first few cuts, the main stats, not every specialist cut.

The two new sellers are added to their town's own NPC spots and roster too, so re-running a town's
sync tool keeps them. Run tools/vendor_trades.py after this (it knows the gem trade).
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

VENDORS = ROOT / "data/npcs/vendors.json"
AMBIENT = ROOT / "data/npcs/ambient_npcs.json"
CUTS_PER_STONE = 3

SELLERS = {
    "org_market_jewelcrafter": dict(
        name="Fizwick Gemstone", zone="orgrimmar", race="goblin", gender="male", variant=8,
        xy=(114, 81), faction="neutral", gear_level=30, from_ambient=True,
        stones=["garnet", "carnelian", "jet", "honey_amber", "jade", "citrine", "rime_opal"],
        greeting=("I sell gems that are already cut, so you don't need to know a thing about "
                  "jewelcrafting to use them. Pop one in a socket and you're done. If you want the "
                  "really good stones, you'll need a jewelcrafter.")),
    "uc_market_gems": dict(
        name="Gemcutter Voss", zone="Undercity", race="forsaken", gender="male", variant=6,
        xy=(87, 70), faction="forsaken", gear_level=32, from_ambient=True,
        stones=["lesser_moonstone", "garnet", "carnelian", "jet", "jade", "citrine", "rime_opal"],
        greeting=("Everything on this tray is cut and ready for a socket. They aren't the finest "
                  "stones, I sell those to jewellers, but they'll do the job on anything you're "
                  "wearing.")),
    "stw_gem_trader": dict(
        name="Gem-Trader Pixi Quartzwhistle", zone="steamwheedle_port", race="goblin",
        gender="female", variant=5, xy=(71, 45), faction="neutral", gear_level=44,
        roster="steamwheedle",
        stones=["topaz", "peridot", "aquamarine", "felfire_shard", "heartsblood_garnet"],
        greeting=("Cut gems, ready to go, no jeweller needed. Half of these came up out of the "
                  "Glittervein, and the other half came off a ship. I won't say which half.")),
    "oh_gem_trader": dict(
        name="Gem-Trader Brynja Facetstone", zone="onyxhollow", race="dwarf", gender="female",
        variant=2, xy=(21, 68), faction="neutral", gear_level=52, roster="onyxhollow",
        stones=["deepearth_geode", "huge_emerald", "black_diamond", "amethyst", "blue_sapphire"],
        greeting=("These are cut from what comes up out of the deep veins. They're ready for a "
                  "socket now. Garrun's people can cut you something better if you bring them the "
                  "rough stone.")),
}


def stock(stones):
    from world import jewelcrafting as J
    d = J.data()
    out = []
    for stone in stones:
        gid = f"gem_{stone}"
        raw = d["raw_gems"].get(gid)
        assert raw, f"no stone {gid}"
        assert raw["quality"] == "uncommon", f"{gid} is a rare stone; sellers only stock common ones"
        cuts = [cid for cid, c in d["cut_gems"].items() if c["raw"] == gid]
        out += cuts[:CUTS_PER_STONE]
    return out


def _roster_add(path, var, vid, s, sells, note="gem seller (tools/build_gem_sellers.py, 14 Nov 2026)"):
    """Add the seller to a town roster module's vendor dict, so its sync tool keeps them. A re-run
    replaces the entry and its comment line rather than stacking another copy."""
    text = path.read_text(encoding="utf-8")
    if f'"{vid}":' in text:
        text = re.sub(rf'(    # [^\n]*\n)?    "{vid}": \(\n.*?\),\n(?=    ["#]|}})', "", text, flags=re.S)
    entry = (f'    "{vid}": (\n        "{s["name"]}", "{s["race"]}", "{s["gender"]}", {s["variant"]},\n'
             f'        {json.dumps(sells)},\n        False,\n        {json.dumps(s["greeting"])}),\n')
    head = f"{var} = {{\n"
    assert head in text, f"{path.name} has no {var}"
    text = text.replace(head, head + f"    # {note}\n" + entry, 1)
    path.write_text(text, encoding="utf-8")


def _position_add(path, vid, xy, note="gem seller (tools/build_gem_sellers.py)"):
    text = path.read_text(encoding="utf-8")
    if f'"{vid}":' in text:
        text = re.sub(rf'    "{vid}": \(\d+, \d+\),[^\n]*\n', "", text)
    head = "NPC_POSITIONS = {\n"
    assert head in text
    text = text.replace(head, head + f'    "{vid}": {xy},          # {note}\n', 1)
    path.write_text(text, encoding="utf-8")


def main():
    vd = json.loads(VENDORS.read_text(encoding="utf-8"))
    ad = json.loads(AMBIENT.read_text(encoding="utf-8"))
    vendors, ambient = vd["vendors"], ad["npcs"]
    for vid, s in SELLERS.items():
        sells = stock(s["stones"])
        if s.get("from_ambient"):
            ambient[:] = [a for a in ambient if a["npc_id"] != vid]
        vendors[:] = [v for v in vendors if v["vendor_id"] != vid]
        vendors.append({
            "vendor_id": vid, "name": s["name"], "zone": s["zone"], "x": s["xy"][0], "y": s["xy"][1],
            "tile_sprite": "npc", "sells": sells, "buys_from_player": True, "faction": s["faction"],
            "gear_level": s["gear_level"], "sells_gear": False, "race": s["race"],
            "gender": s["gender"], "appearance_variant": s["variant"], "greeting": s["greeting"]})
        if s.get("roster") == "steamwheedle":
            _roster_add(ROOT / "tools/steamwheedle_npc_roster.py", "STEAMWHEEDLE_VENDORS", vid, s, sells)
            _position_add(ROOT / "tools/handbuilt_steamwheedle_port.py", vid, s["xy"])
        elif s.get("roster") == "onyxhollow":
            _roster_add(ROOT / "tools/onyxhollow_npc_roster.py", "ONYXHOLLOW_VENDORS", vid, s, sells)
            _position_add(ROOT / "tools/handbuilt_onyxhollow.py", vid, s["xy"])
        print(f"{s['name']} ({s['zone']}): {len(sells)} gems")
    VENDORS.write_text(json.dumps(vd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    AMBIENT.write_text(json.dumps(ad, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    # the stall-holders' old ambient greetings would shadow the shop greeting
    for stem, vid in (("orgrimmar", "org_market_jewelcrafter"), ("undercity", "uc_market_gems")):
        p = ROOT / f"data/npcs/greetings/{stem}.json"
        if p.exists():
            g = json.loads(p.read_text(encoding="utf-8"))
            if vid in g:
                del g[vid]
                p.write_text(json.dumps(g, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
