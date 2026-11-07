#!/usr/bin/env python3
"""
Saving must write ONE slot - the one you are playing.

    PYTHONPATH=. python3 tools/qa_save_slots.py

Kyle, 2 Nov 2026: "When I go to save anything in another file, like Save 2, or 3
etc - it saves in that slot AND overrides save 1."

He was exactly right, and the cause was a default argument. GameStateManager
.save_game(filename="character.json") defaulted to the literal slot-1 filename
rather than to the slot in play, so every call site that did not pass one wrote
slot 1 - the F5 quicksave, the post-combat autosave, and the character screen.
Save to slot 3 from the menu and you got two files: slot 3 from the menu call,
and slot 1 overwritten by the next quicksave, destroying whoever lived there.

This is a DATA LOSS bug, which is why it gets a test rather than just a fix. The
test is the behaviour, not the implementation: put a distinct character in every
slot, load one, save without naming a file, and assert that the other four are
byte-for-byte unchanged.
"""
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

SAVES = ROOT / "data" / "saves"


def main():
    import pygame
    from config import save_slot_filename
    from core.game_state import GameStateManager
    from entities.character import Character

    # GameStateManager needs a surface; it never draws in this test.
    pygame.init()
    screen = pygame.display.set_mode((320, 240))

    backup = SAVES.parent / "_saves_qa_backup"
    if backup.exists():
        shutil.rmtree(backup)
    shutil.copytree(SAVES, backup)
    fails = []
    try:
        # One identifiable character per slot.
        gsm = GameStateManager(screen)
        for slot in range(1, 6):
            gsm.player = Character(name=f"Slot{slot}Hero", char_class="Warrior", level=slot + 9)
            gsm.save_game(save_slot_filename(slot))

        before = {s: (SAVES / save_slot_filename(s)).read_text() for s in range(1, 6)}
        for slot, text in before.items():
            if f"Slot{slot}Hero" not in text:
                fails.append(f"slot {slot} did not contain its own character after setup")

        # Load slot 3 and quicksave the way F5 does - with NO filename.
        gsm2 = GameStateManager(screen)
        if not gsm2.load_game(save_slot_filename(3)):
            fails.append("could not load slot 3")
        else:
            if getattr(gsm2.player, "name", None) != "Slot3Hero":
                fails.append(f"slot 3 loaded {getattr(gsm2.player, 'name', None)!r}")
            gsm2.player.level += 1          # something worth saving
            if not gsm2.save_game():        # <- the bug: no filename
                fails.append("quicksave returned False")

        after = {s: (SAVES / save_slot_filename(s)).read_text() for s in range(1, 6)}
        for slot in (1, 2, 4, 5):
            if after[slot] != before[slot]:
                who = json.loads(after[slot]).get("character", {}).get("name")
                fails.append(f"quicksave on slot 3 MODIFIED slot {slot} "
                             f"(now holds {who!r})")
        if after[3] == before[3]:
            fails.append("quicksave on slot 3 did not write slot 3")
        else:
            lvl = json.loads(after[3]).get("character", {}).get("level")
            if lvl != 13:
                fails.append(f"slot 3 level is {lvl}, expected 13")

        # ------------------------------------------------------------------
        # A NEW CHARACTER MUST NOT INHERIT THE LAST ONE'S SLOT.
        #
        # Kyle's tester, 7 Nov: "I just made a shaman and used the +5 level
        # thing and saved it but it over wrote my level 13 druid." Same class
        # of bug as the one above and a worse version of it: current_save_file
        # survived character creation, and the save_game() call at the end of
        # creation wrote the brand-new level-1 character straight over the
        # loaded character's file before the player saw the world.
        #
        # Behaviour, not implementation: play a slot, start a new character,
        # and assert that every slot on disk is untouched until a slot is
        # explicitly chosen.
        # ------------------------------------------------------------------
        snapshot = {s: (SAVES / save_slot_filename(s)).read_text() for s in range(1, 6)}

        gsm3 = GameStateManager(screen)
        gsm3.load_game(save_slot_filename(2))
        gsm3.begin_new_character()          # what the New Game button does
        gsm3.player = Character(name="FreshShaman", char_class="Shaman", level=1)

        if not gsm3.needs_save_slot:
            fails.append("a newly created character reports a save slot it should not have")
        if gsm3.save_game():
            fails.append("an unslotted new character was allowed to save")

        touched = [s for s in range(1, 6)
                   if (SAVES / save_slot_filename(s)).read_text() != snapshot[s]]
        if touched:
            who = json.loads((SAVES / save_slot_filename(touched[0])).read_text())
            fails.append(f"creating a character WROTE slots {touched} "
                         f"(slot {touched[0]} now holds "
                         f"{who.get('character', {}).get('name')!r})")

        # And once a slot IS chosen, exactly that slot takes it.
        if not gsm3.save_game(save_slot_filename(5)):
            fails.append("could not save the new character to a chosen slot")
        moved = [s for s in (1, 2, 3, 4)
                 if (SAVES / save_slot_filename(s)).read_text() != snapshot[s]]
        if moved:
            fails.append(f"saving the new character to slot 5 also wrote {moved}")
        if "FreshShaman" not in (SAVES / save_slot_filename(5)).read_text():
            fails.append("slot 5 did not receive the new character")
    finally:
        shutil.rmtree(SAVES)
        shutil.copytree(backup, SAVES)
        shutil.rmtree(backup)

    if fails:
        for f in fails:
            print(f"  FAIL  {f}")
        return 1
    print("5 slots written, loaded slot 3, quicksaved with no filename.")
    print("Slots 1, 2, 4, 5 untouched; slot 3 updated.")
    print("\nPASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
