#!/usr/bin/env python3
"""Every table keyed by a class name must resolve from Character.char_class.

    PYTHONPATH=. python3 tools/qa_class_name_lookups.py

A class is written two ways: the id Character.char_class holds ("sun_cleric")
and the display name several hand-written tables are keyed by ("Sun Cleric").
Four separate lookups each normalised differently or not at all, and the ones
that only lowercased broke on exactly the four two-word classes, which is why
these kept turning up together:

    class icons              8 recruits drew an empty box with the file on disk
    spellbook tabs           EVERY class, CoA and classic nine alike, dumped its
                             whole book into Core
    class resource           Sun Cleric, Witch Doctor, Witch Hunter and Knight
                             of Xoroth all silently reported Mana
    spellbook tab labels     "Sun Cleric Blessings" instead of "Blessings"

They all go through core/class_names.py now. This checks each one against every
class in the game rather than against the four that were noticed.
"""
import glob
import json
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FAILS = []


def check(label, cond, detail=""):
    if cond:
        print(f"  ok   {label}")
    else:
        FAILS.append(label)
        print(f"  FAIL {label}  {detail}")


def main():
    import pygame
    pygame.init()
    pygame.display.set_mode((1280, 720))

    from core.class_names import class_key, lookup, strip_class_prefix
    from combat.abilities import CLASS_RESOURCE_MAP, _lookup_class_resource
    from entities.character import Character
    from ui.screens.skills_screen import SkillsScreen

    classes = sorted(os.path.basename(p)[:-5] for p in glob.glob("data/abilities/*.json"))
    classes = [c for c in classes if not c.startswith("_") and c != "asher_unique"]

    # ---- the key itself, including its negative control ---------------------
    check("class_key collapses both spellings",
          class_key("Sun Cleric") == class_key("sun_cleric") == "sun_cleric")
    check("class_key handles the three-word one",
          class_key("Knight of Xoroth") == "knight_of_xoroth")
    check("class_key does NOT collapse two different classes",
          class_key("Witch Doctor") != class_key("Witch Hunter"))

    # ---- 1. resource map ----------------------------------------------------
    bad = [c for c in classes if lookup(CLASS_RESOURCE_MAP, c) is None]
    check("every class resolves a resource", not bad, str(bad))
    # Negative control: a class that genuinely is not in the map must still miss.
    check("an unknown class still misses the resource map",
          lookup(CLASS_RESOURCE_MAP, "hearthsteel_invoker") is None)
    # And the real entry point agrees with the table.
    from combat.abilities import ResourceType
    mana_only = [c for c in classes
                 if _lookup_class_resource(c)[0] is ResourceType.MANA
                 and lookup(CLASS_RESOURCE_MAP, c)[0] is not ResourceType.MANA]
    check("no class silently falls back to Mana", not mana_only, str(mana_only))

    # ---- 2. spellbook tabs --------------------------------------------------
    coa = json.load(open("data/spellbook_tabs_coa.json"))
    unresolved = [c for c in classes
                  if any(class_key(c) == class_key(k) for k in coa)
                  and lookup(coa, c) is None]
    check("every CoA class resolves its tab table", not unresolved, str(unresolved))

    class _SM:
        pass
    sm = _SM()
    core_only = []
    dirty_labels = []
    for cls in classes:
        c = Character("T", cls, level=60)
        # Unlock the talent-granted abilities. Primalist's ENTIRE spec kit is
        # talent-gated, so with no points spent it legitimately has nothing but
        # Core - that is the talent system working, not a lookup failing, and
        # asserting on the untalented character would have flagged it forever.
        for ability in c.ability_book.get_all_abilities():
            if getattr(ability, "requires_talent", False):
                ability.talent_unlocked = True
                ability.refresh_rank_for_level(c.level, None)
        sm.player = c
        groups, order = SkillsScreen(sm)._build_tabs(c)
        if len(order) == 1:
            core_only.append(cls)
        for _key, label in order:
            if label != "Core" and class_key(label).startswith(class_key(cls).split("_")[0]):
                dirty_labels.append((cls, label))
    check("no class has its whole book in Core", not core_only, str(core_only))
    check("no tab label still carries part of the class name",
          not dirty_labels, str(dirty_labels[:6]))

    # ---- 3. tab label trimming, including the case that must NOT trim -------
    check("'Sun Cleric Blessings' -> 'Blessings'",
          strip_class_prefix("Sun Cleric Blessings", "sun_cleric") == "Blessings")
    check("'Witch Hunter Boltslinger' -> 'Boltslinger'",
          strip_class_prefix("Witch Hunter Boltslinger", "witch_hunter") == "Boltslinger")
    check("'Knight of Xoroth Hellfire' -> 'Hellfire'",
          strip_class_prefix("Knight of Xoroth Hellfire", "knight_of_xoroth") == "Hellfire")
    check("'Mage Fire' -> 'Fire'", strip_class_prefix("Mage Fire", "mage") == "Fire")
    check("a label that is only the class name is left alone, not blanked",
          strip_class_prefix("Mage", "mage") == "Mage")
    check("an unrelated label is untouched",
          strip_class_prefix("Shadow", "priest") == "Shadow")

    # ---- 4. class icons -----------------------------------------------------
    from ui.class_portrait import get_class_icon
    missing = [c for c in classes if get_class_icon(c) is None]
    check("every class resolves an icon from its id", not missing, str(missing))
    display_missing = [c for c in classes
                       if get_class_icon(c.replace("_", " ").title()) is None]
    check("...and from its display name", not display_missing, str(display_missing))

    print(f"\n{len(FAILS)} failed" if FAILS else "\nclass name lookups all resolve")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
