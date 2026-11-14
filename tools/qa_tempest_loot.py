#!/usr/bin/env python3
"""Tempest Isle's bosses drop loot, and T0 tokens work from the kill to the Artifact Keeper.

    PYTHONPATH=. python3 tools/qa_tempest_loot.py

Kyle, 13 Nov 2026 (tools/build_tempest_loot.py has the quotes). SEVEN CLAIMS:
  1. All 19 bosses of Khaz Varun and the Emberdeep hand out one of their own three items.
  2. Every trinket among them carries a proc onto the Item the player gets.
  3. A normal boss drops a token about one kill in five; the last boss of each dungeon always
     drops one; and a boss only ever drops the slot and armour types it carries.
  4. Bracer tokens are on Khaz Varun's first floor, belts on its second, legs in the Emberdeep.
  5. At a keeper a token becomes the right class's piece: plate bracers for a Warrior, never for
     a Priest; the token is used up; the piece has its set, its level and its icon.
  6. A full bag refuses the trade and keeps the token. A token cannot be sold.
  7. The combat engine really rolls tokens (the hook is in the kill path), and the T0 pieces a
     token buys are levels 53-59 at item level three above.
"""
import contextlib
import io
import json
import os
import random
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        from entities.boss_loot import get_fixed_boss_loot_all
        from entities.character import Character
        from entities.loot_item import LootItem, add_loot_item, count_loot_items
        from entities.party import Party
        from world import gear_sets, set_tokens
    T = set_tokens.data()
    bad = []
    order = list(T["bosses"])
    # 19 on Tempest Isle and 5 in the Royal Hive (shoulders, 14 Nov 2026)
    if len(order) != 24:
        bad.append(f"{len(order)} bosses carry tokens, wanted 24")
    MULTI = {"Hive-Mother Ahn'thera": (3, 9)}         # the queen and her Consort: 3 of a pool of 9

    # 1, 2
    trinkets = 0
    for name in order:
        got = get_fixed_boss_loot_all(name)
        per_kill, pool = MULTI.get(name, (1, 3))
        if len(got) != per_kill:
            bad.append(f"{name} hands out {len(got)} items a kill, wanted {per_kill}")
            continue
        seen = set()
        for _ in range(60):
            for it in get_fixed_boss_loot_all(name):
                seen.add(it.name)
                if it.slot.startswith("trinket"):
                    if not getattr(it, "proc", None) or not it.proc.get("describe"):
                        bad.append(f"{it.name} reached the player with no proc")
        if len(seen) != pool:
            bad.append(f"{name}: {len(seen)} different items seen in 60 kills, wanted {pool}")
        trinkets += sum(1 for n in seen if n in {"Gatewarden's Horn", "Cinder-Prayer Beads",
                                                 "Alpha's Dewclaw", "Shard of the Mountain's Heart",
                                                 "Drop of Royal Amber", "Ahn'thera's Last Egg"})
    if trinkets != 6:
        bad.append(f"{trinkets} of the six proc trinkets were seen dropping")

    # 3, 4
    rng = random.Random(11)
    for name in order:
        spec = T["bosses"][name]
        n = 4000
        drops = [d for _ in range(n) for d in set_tokens.roll(name, rng)]
        rate = len(drops) / n
        if spec["guaranteed"]:
            if rate != 1.0:
                bad.append(f"{name} is a last boss and dropped a token {rate:.0%} of the time")
        elif abs(rate - 0.20) > 0.025:
            bad.append(f"{name} dropped a token {rate:.1%} of the time, wanted about 20%")
        kinds = {d["item_id"] for d in drops}
        allowed = {f"t0_token_{spec['slot']}_{t}" for t in spec["types"]}
        if not kinds <= allowed or (spec["guaranteed"] and kinds != allowed):
            bad.append(f"{name} dropped {sorted(kinds - allowed) or 'too few kinds'}")
    slots = [T["bosses"][n]["slot"] for n in order]
    if slots != ["wrist"] * 6 + ["waist"] * 6 + ["legs"] * 7 + ["shoulder"] * 5:
        bad.append(f"token slots by boss are {slots}")
    if [n for n in order if T["bosses"][n]["guaranteed"]] != ["Thane Morrun the Unmade", "The Caldera",
                                                                "Hive-Mother Ahn'thera"]:
        bad.append("the guaranteed bosses are not the three last bosses")

    # 5, 6
    with contextlib.redirect_stdout(io.StringIO()):
        player = Character("Tester", "Warrior", 58)
        priest = Character("Healer", "Priest", 58)
        party = Party(player)
        (getattr(party, "add_member", None) or party.members.append)(priest)
    for token_id in ("t0_token_wrist_plate", "t0_token_legs_cloth"):
        d = dict(set_tokens.token(token_id))
        add_loot_item(player, token_id, d["name"], category="material", description=d["description"],
                      icon_id=d.get("icon_id"), rarity="epic")
    stack = next(i for i in player.inventory if isinstance(i, LootItem) and i.item_id == "t0_token_wrist_plate")
    if stack.is_sellable:
        bad.append("a set token can be sold to a vendor")
    rows = set_tokens.redeemable(player, party)
    pairs = {(r[0], r[2].name) for r in rows}
    if pairs != {("t0_token_wrist_plate", "Tester"), ("t0_token_legs_cloth", "Healer")}:
        bad.append(f"the keeper offers {sorted(pairs)}")
    ok, msg = set_tokens.redeem(player, "t0_token_wrist_plate", priest)
    if ok:
        bad.append("a Priest was given plate bracers")
    ok, msg = set_tokens.redeem(player, "t0_token_wrist_plate", player)
    piece = next((i for i in player.inventory if getattr(i, "set_id", None) == "t0_warrior"), None)
    if not ok or piece is None:
        bad.append(f"the Warrior's trade failed: {msg}")
    else:
        if (piece.slot, piece.required_level, piece.item_level) != ("wrist", 53, 56):
            bad.append(f"the bracers are {piece.slot} level {piece.required_level} ilvl {piece.item_level}")
        if piece.icon_id != "t0_warrior_wrist":
            bad.append(f"the bracers' icon is {piece.icon_id!r}")
        if count_loot_items(player, "t0_token_wrist_plate") != 0:
            bad.append("the token was not used up")
    cap = player.inventory_capacity
    while len(player.inventory) < cap:
        player.inventory.append(gear_sets.make_piece("t0_warrior", "head"))
    ok, msg = set_tokens.redeem(player, "t0_token_legs_cloth", priest)
    if ok or count_loot_items(player, "t0_token_legs_cloth") != 1:
        bad.append("a full bag still took the token")

    # 7
    if "_set_tokens.roll(enemy.name)" not in (ROOT / "combat/combat_engine.py").read_text(encoding="utf-8"):
        bad.append("the combat engine does not roll set tokens")
    sets = json.loads((ROOT / "data/items/gear_sets.json").read_text(encoding="utf-8"))["sets"]
    for sid, d in sets.items():
        for slot, want in (("wrist", 53), ("waist", 54), ("legs", 57)):
            f = d["slots"][slot]
            if (f["required_level"], f["item_level"]) != (want, want + 3):
                bad.append(f"{sid} {slot}: level {f['required_level']} ilvl {f['item_level']}")

    print(f"{len(order)} bosses, {len(T['tokens'])} tokens, token chance {T['chance']:.0%}")
    for b in bad[:30]:
        print("  FAIL", b)
    print("\nTempest loot OK - every boss pays out, and a token becomes the right set piece."
          if not bad else f"\n{len(bad)} problems")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
