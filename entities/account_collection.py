"""The Collection: what this player has learned, for every character they have.

Kyle, 18 Nov 2026: "have them tied to the player (like the guild bank is) so it'd be a seperate tab". The design and
his answers are in docs/collection_design.md; the catalogue is data/collection/collectables.json
(tools/build_collection.py); what each thing does is world/collection.py.

LIKE THE GUILD BANK, THIS LIVES OUTSIDE EVERY SAVE SLOT: data/saves/account_collection.json. A character save can be
rolled back (quit without saving) and this file can't, so learning is one transaction with the same rule the guild
bank uses (entities/guild_bank.py explains the dupe): the item leaves the bag, this file is written, and the character
is saved in the same breath. If the character save fails, this file is rolled back, so a collectable can never be
both learned and still in somebody's bags.

Learning is for good. A learned thing can't be unlearned or sold (Kyle picked "learn once, all have it").
"""
import json
import os
import tempfile
import time
from pathlib import Path

PATH = Path(__file__).resolve().parent.parent / "data" / "saves" / "account_collection.json"


class AccountCollection:
    def __init__(self, learned=None, prefs=None):
        #: collection id -> unix time it was learned (for the tab's "learned on" line and its order)
        self.learned = dict(learned or {})
        #: account-wide choices, e.g. the favourite form; per-character choices live in the save
        self.prefs = dict(prefs or {})

    def has(self, cid):
        return cid in self.learned

    def ids(self):
        return set(self.learned)

    # ------------------------------------------------------------------ the rule
    def transact(self, mutate):
        """Apply mutate(), then commit this file and the character together (entities/guild_bank.py's rule)."""
        before = dict(self.learned)
        result = mutate()
        if result is False or result is None:
            self.learned = before
            return result
        if not self.save():
            self.learned = before
            return None
        from entities import guild_bank
        saver = guild_bank._host_saver
        if saver is not None:
            try:
                ok = saver()
            except Exception:
                ok = False
            if not ok:
                self.learned = before
                self.save()
                return None
        return result

    def learn_from_bag(self, item, bag, party=None, player=None):
        """Learn the collectable `item` out of `bag` (a list). Returns (ok, message)."""
        from world.collection import get_entry
        cid = getattr(item, "collection_id", None)
        entry = get_entry(cid)
        if entry is None:
            return False, "That isn't something you can learn."
        if self.has(cid):
            return False, f"You already know {entry['name']}."
        if item not in bag:
            return False, "It isn't in your bags any more."

        def go():
            bag.remove(item)
            self.learned[cid] = int(time.time())
            return True

        if not self.transact(go):
            if item not in bag:
                bag.append(item)
            return False, "Couldn't save just now, so nothing was learned. Try again."
        from world.collection import on_learned
        on_learned(cid, party=party, player=player)
        return True, f"Learned: {entry['name']}. Every character has it now."

    # ------------------------------------------------------------------ the file
    def to_dict(self):
        return {"version": 1, "learned": self.learned, "prefs": self.prefs}

    @classmethod
    def from_dict(cls, data):
        data = data or {}
        return cls(data.get("learned"), data.get("prefs"))

    def save(self):
        """Write atomically: a torn file here is every character's collection."""
        try:
            PATH.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=str(PATH.parent), suffix=".tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(self.to_dict(), fh, indent=1)
            os.replace(tmp, PATH)
            return True
        except Exception as exc:
            print(f"Could not save the collection: {exc}")
            return False

    @classmethod
    def load(cls):
        try:
            return cls.from_dict(json.loads(PATH.read_text(encoding="utf-8")))
        except FileNotFoundError:
            return cls()
        except Exception as exc:
            print(f"Could not read the collection, starting empty in memory: {exc}")
            return cls()


_COLLECTION = None


def get_collection():
    global _COLLECTION
    if _COLLECTION is None:
        _COLLECTION = AccountCollection.load()
    return _COLLECTION


def reset_collection():
    """Drop the cached copy so the next get_collection() re-reads the file (tests, and loading another slot)."""
    global _COLLECTION
    _COLLECTION = None


def use_path(path):
    """Point the collection at another file (tests). Returns the old path."""
    global PATH
    old, PATH = PATH, Path(path)
    reset_collection()
    return old
