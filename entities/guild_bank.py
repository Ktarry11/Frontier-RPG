"""The guild bank - storage that crosses characters.

Kyle: "is there a way to make a bank that crosses over between characters. Like if I have a lvl 60
druid and a lvl 60 shaman, and we have a 24 slot 'guild bank' that any character can deposit items
and withdraw items. This way if I get an incredible 2H druid tank item on my shaman, I can put it
here."

THIS IS NOT THE BANK, AND THE DIFFERENCE IS WHERE IT LIVES. entities/bank.py belongs to the PARTY:
it is saved inside the character save, it grows by buying tabs, and everything in it belongs to the
one character whose file it sits in. This belongs to the PLAYER, across all fifteen save slots, so
it cannot live in any of them - it has its own file, and it is the only state in the game that
does.

ONE FIXED SIZE, NO TABS. 24 slots, as asked. The bank is the thing you buy more of; this is a
hand-off shelf between characters, and the moment it is big enough to be a second bank it stops
being obvious which one a thing should go in.

=========================  THE DUPE, AND WHY SAVING IS ARRANGED LIKE THIS  =========================

An account-wide vault next to a per-character save that can roll back is a duplication bug waiting
to be found, and it is worth being explicit about because the obvious implementation has it:

    deposit the sword  ->  guild bank writes its file immediately
    quit without saving the character
    load that character  ->  the sword is back in their bags, AND it is in the guild bank

Two swords. The player did nothing wrong and may not even notice; they just know the game is
generous. The cause is that the two halves of one transaction commit at different times.

So a transaction here is never half-committed: `transact()` takes the mutation, applies it, writes
this file, and then asks the host to save the character in the same breath. If the character save
fails, the guild bank write is rolled back and the whole thing is refused, which is the right way
round - refusing a deposit is a moment of friction, and a duplicated item is permanent.

That is also why `set_host_saver` exists rather than this module reaching for the game state
itself: this is an entity and knows nothing about screens or slots, so the host hands it a callable
once and the rule lives here where the storage is.
"""
import json
import os
import tempfile
from pathlib import Path

#: Kyle asked for 24 and 24 is the whole design - see the module docstring on why it does not grow.
SLOTS = 24

#: Beside the character saves, NOT inside one. data/saves/ is where SaveSystem already writes.
PATH = Path(__file__).resolve().parent.parent / "data" / "saves" / "guild_bank.json"

#: Set by the host (core/game_state) to a zero-argument callable that saves the CURRENT character
#: and returns True/False. Left None in tools and tests, where there is no character to keep in
#: step and the dupe cannot happen.
_host_saver = None


def set_host_saver(fn):
    """Register how to save the current character, so a transaction can commit both halves."""
    global _host_saver
    _host_saver = fn


def _item_from_dict(d):
    """Rebuild an item using the same 'slot' sniff Character.from_dict uses.

    Deliberately the same rule rather than a second one: an item that round-trips through a
    character but not through here would be a slow corruption nobody could reproduce.
    """
    from entities.item import Item
    try:
        from entities.loot_generator import LootItem
    except Exception:
        LootItem = None
    if LootItem is not None and not d.get("slot"):
        try:
            return LootItem.from_dict(d)
        except Exception:
            pass
    return Item.from_dict(d)


class GuildBank:
    """24 shared slots. Every character on this install sees the same ones."""

    def __init__(self, slots=None):
        self.slots = list(slots) if slots else [None] * SLOTS
        if len(self.slots) < SLOTS:
            self.slots += [None] * (SLOTS - len(self.slots))

    # ---------------------------------------------------------------- shape
    @property
    def capacity(self):
        return SLOTS

    @property
    def used(self):
        return sum(1 for s in self.slots if s is not None)

    def first_free(self):
        for i, s in enumerate(self.slots):
            if s is None:
                return i
        return None

    def get(self, index):
        if 0 <= index < SLOTS:
            return self.slots[index]
        return None

    # ---------------------------------------------------------------- moves
    def _deposit(self, item, index=None):
        if item is None:
            return False
        if index is None:
            index = self.first_free()
        if index is None or not (0 <= index < SLOTS) or self.slots[index] is not None:
            return False
        self.slots[index] = item
        return True

    def _withdraw(self, index):
        if not (0 <= index < SLOTS):
            return None
        item, self.slots[index] = self.slots[index], None
        return item

    # ------------------------------------------------------------ the rule
    def transact(self, mutate):
        """Apply `mutate()`, then commit this file AND the character together.

        Returns whatever mutate() returned, or None/False if it was refused. See the module
        docstring: the point is that the vault and the character never disagree about who holds an
        item, because a window where they do is a dupe.
        """
        before = list(self.slots)
        result = mutate()
        if result is False or result is None:
            self.slots = before
            return result
        if not self.save():
            self.slots = before
            return None
        if _host_saver is not None:
            try:
                ok = _host_saver()
            except Exception:
                ok = False
            if not ok:
                # Put it back and re-commit the rollback, so the file on disk matches memory.
                self.slots = before
                self.save()
                return None
        return result

    def deposit(self, item, index=None):
        """Put an item in. Returns the slot index, or None if refused."""
        box = {}

        def go():
            idx = index if index is not None else self.first_free()
            if idx is None:
                return None
            box["idx"] = idx
            return idx if self._deposit(item, idx) else None

        return self.transact(go)

    def withdraw(self, index):
        """Take an item out. Returns the item, or None."""
        box = {}

        def go():
            box["item"] = self._withdraw(index)
            return box["item"]

        return self.transact(go)

    # ----------------------------------------------------------- the file
    def to_dict(self):
        return {"version": 1,
                "slots": [s.to_dict() if s is not None else None for s in self.slots]}

    @classmethod
    def from_dict(cls, data):
        out = []
        for raw in (data or {}).get("slots", []):
            if not raw:
                out.append(None)
                continue
            try:
                out.append(_item_from_dict(raw))
            except Exception:
                # One unreadable row must not cost the player the other 23.
                out.append(None)
        return cls(out)

    def save(self):
        """Write atomically. A torn guild bank file is everybody's guild bank, not one save slot's."""
        try:
            PATH.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=str(PATH.parent), suffix=".tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            os.replace(tmp, PATH)
            return True
        except Exception as exc:
            print(f"Guild bank save failed: {exc}")
            return False


_guild_bank = None


def get_guild_bank():
    """The one guild bank, loaded from disk on first use."""
    global _guild_bank
    if _guild_bank is None:
        data = None
        try:
            if PATH.exists():
                data = json.loads(PATH.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"Guild bank unreadable ({exc}); starting empty.")
        try:
            # from_dict already skips a bad ROW; this catches a bad FILE - a top-level shape that
            # is not what we expect. Everything else in the game is one character's problem, but
            # this file is every character's, so it must never be the thing that stops the game
            # opening.
            _guild_bank = GuildBank.from_dict(data) if data else GuildBank()
        except Exception as exc:
            print(f"Guild bank could not be rebuilt ({exc}); starting empty.")
            _guild_bank = GuildBank()
    return _guild_bank


def reset_guild_bank():
    """Drop the cached instance so the next call re-reads the file (tests, and slot switches)."""
    global _guild_bank
    _guild_bank = None
