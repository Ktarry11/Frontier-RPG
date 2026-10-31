#!/usr/bin/env python3
"""The guild bank crosses characters, and an item is never in two places at once.

    PYTHONPATH=. python3 tools/qa_guild_bank.py

Kyle: "is there a way to make a bank that crosses over between characters... if I get an incredible
2H druid tank item on my shaman, I can put it here."

FOUR CLAIMS:

  1. IT IS NOT IN A SAVE SLOT. The guild bank's file has to live beside the character saves rather
     than inside one, or it is not account-wide at all - it is just another per-character bank with
     a different name. Checked by path, and by confirming no character save holds it.
  2. WHAT ONE CHARACTER PUTS IN, ANOTHER TAKES OUT. The entire feature, tested the way Kyle
     described it: deposit on the shaman, re-read from disk as a different character, withdraw.
  3. A FAILED CHARACTER SAVE REFUSES THE WHOLE TRANSACTION. An account-wide vault that commits
     instantly, next to a character that can roll back, is a duplication bug: deposit the sword,
     quit without saving, and it is in the bags AND the vault. Both halves commit together or
     neither does.
  4. A CORRUPT ROW COSTS ONE SLOT, NOT TWENTY-FOUR. This is the one file in the game shared by
     every character, so a single unreadable item must not take the rest down with it.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()

from entities.guild_bank import (  # noqa: E402
    GuildBank, PATH, SLOTS, get_guild_bank, reset_guild_bank, set_host_saver)
from entities.loot_generator import LootGenerator  # noqa: E402


def main():
    bad = []
    backup = PATH.read_bytes() if PATH.exists() else None
    try:
        gen = LootGenerator()

        # ---- 1. its own file, outside the save slots
        from config import save_slot_filename, SAVE_SLOT_COUNT
        slot_files = {save_slot_filename(i) for i in range(1, SAVE_SLOT_COUNT + 1)}
        if PATH.name in slot_files:
            bad.append(f"the guild bank is stored as {PATH.name}, which is a save slot - it would "
                       f"belong to one character instead of all of them.")
        if PATH.parent.name != "saves":
            bad.append(f"guild bank lives in {PATH.parent}, expected the saves directory")

        if PATH.exists():
            PATH.unlink()
        reset_guild_bank()
        set_host_saver(lambda: True)

        # ---- 2. deposit on one character, withdraw on another
        g = get_guild_bank()
        axe = gen.generate_item_for_class("Druid", 60, slot="main_hand", rarity="epic")
        axe.name = "Incredible Druid Tank Axe"
        idx = g.deposit(axe)
        if idx is None:
            bad.append("deposit was refused on an empty guild bank")
        if not PATH.exists():
            bad.append("depositing did not write the guild bank file")

        reset_guild_bank()                  # a different character, fresh read from disk
        g2 = get_guild_bank()
        seen = g2.get(0)
        if seen is None or seen.name != axe.name:
            bad.append(f"another character sees {seen!r} in slot 0, expected {axe.name!r}")
        elif seen.rarity != axe.rarity or seen.item_level != axe.item_level:
            bad.append(f"the item changed crossing characters: {seen.rarity}/{seen.item_level} "
                       f"vs {axe.rarity}/{axe.item_level}")
        out = g2.withdraw(0)
        if out is None:
            bad.append("withdraw returned nothing")
        reset_guild_bank()
        if get_guild_bank().used != 0:
            bad.append("the withdrawal did not persist - the item is still on disk")

        # ---- 3. a failed character save refuses the whole transaction
        reset_guild_bank()
        g3 = get_guild_bank()
        set_host_saver(lambda: False)       # the character could not be saved
        r = g3.deposit(axe)
        if r is not None:
            bad.append("a deposit went through while the character save FAILED - that is the dupe: "
                       "the item would be in the bags and in the vault.")
        if g3.used != 0:
            bad.append(f"after a refused deposit the guild bank still holds {g3.used} item(s)")
        reset_guild_bank()
        if get_guild_bank().used != 0:
            bad.append("a refused deposit was still written to disk")
        set_host_saver(lambda: True)

        # ---- 4. one bad row costs one slot
        reset_guild_bank()
        g4 = get_guild_bank()
        for _ in range(3):
            g4.deposit(gen.generate_item_for_class("Shaman", 40, slot="chest", rarity="rare"))
        raw = json.loads(PATH.read_text(encoding="utf-8"))
        raw["slots"][1] = {"name": "corrupt", "slot": None, "nonsense": True}
        PATH.write_text(json.dumps(raw), encoding="utf-8")
        reset_guild_bank()
        g5 = get_guild_bank()
        if g5.used < 2:
            bad.append(f"one unreadable row cost {3 - g5.used} of 3 items - a corrupt entry must "
                       f"not take the rest of the shelf with it.")

        print(f"guild bank: {SLOTS} slots at {PATH.relative_to(ROOT)}")
        print(f"  survives a corrupt row: {g5.used} of 3 items still readable")
    finally:
        reset_guild_bank()
        if backup is not None:
            PATH.write_bytes(backup)
        elif PATH.exists():
            PATH.unlink()
        set_host_saver(None)

    if bad:
        print(f"\n{len(bad)} problem(s):")
        for b in bad:
            print("  -", b)
        return 1
    print("\nguild bank OK - its own file outside the save slots, one character's deposit is "
          "another's withdrawal, a failed character save refuses the whole transaction, and a "
          "corrupt row costs one slot rather than all of them.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
