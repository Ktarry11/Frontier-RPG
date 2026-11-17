#!/usr/bin/env python3
"""Trainer recipes arrive as the skill reaches them, and a stuck save is mended on load.

    PYTHONPATH=. python3 tools/qa_trainer_recipes_follow_skill.py

Playtest, 17 Nov 2026: Leatherworking at skill 1, 107 Scrap Leather, and "Missing materials for that recipe" on
the first three recipes. Trainer recipes were only taught at the trainer's counter, when a trade was learned or
a tier trained, so:
  - a save that learned the trade back when trades started at 0 (and the first recipes needed 1) knew nothing;
  - nothing taught the skill 2, 8, 10 ... recipes on the way up, so every trade stalled inside its first tier.

FOUR CLAIMS, for every crafting trade:
  1. A SAVE THAT KNOWS THE TRADE BUT NONE OF ITS RECIPES loads knowing every trainer recipe its skill reaches.
  2. A SKILL-UP TEACHES the trainer recipes at the new skill, and nothing above it.
  3. PATTERNS STAY FOUND: drop, vendor and quest recipes are never handed out.
  4. AN UNKNOWN RECIPE SAYS SO when clicked, instead of "Missing materials".
"""
import contextlib
import io
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

with contextlib.redirect_stdout(io.StringIO()):
    from entities.character import Character
    from world.recipe_manager import trainer_recipe_book

TRADES = ["blacksmithing", "leatherworking", "tailoring", "alchemy", "woodworking", "engineering", "cooking",
          "jewelcrafting", "enchanting", "runecrafting"]


def trainer_ids(book, skill):
    return {rid for rid, r in book.items() if r.get("source", "trainer") == "trainer" and r.get("skill_required", 0) <= skill}


def main():
    problems = []
    checked = 0
    for trade in TRADES:
        book = trainer_recipe_book(trade)
        if not book:
            problems.append(f"{trade}: no recipe book")
            continue
        with contextlib.redirect_stdout(io.StringIO()):
            c = Character("Probe", "Hunter", 30)
        c.known_professions.append(trade)
        c.profession_skills[trade] = 1
        c.known_recipes = set()
        # 1. the stuck save
        with contextlib.redirect_stdout(io.StringIO()):
            c2 = Character.from_dict(c.to_dict())
        want = trainer_ids(book, 1)
        have = {r for r in c2.known_recipes if r in book}
        if not want:
            problems.append(f"{trade}: no trainer recipe at skill 1 at all")
        if want - have:
            problems.append(f"{trade}: a stuck save loads without {sorted(want - have)[:3]}")
        # 2. skill-ups teach, and only up to the skill
        for _ in range(40):
            c2.gain_profession_skill(trade, 1)
        skill = c2.profession_skills[trade]
        want = trainer_ids(book, skill)
        have = {r for r in c2.known_recipes if r in book}
        if want - have:
            problems.append(f"{trade}: at skill {skill} still missing {sorted(want - have)[:3]}")
        above = {r for r in have if book[r].get("skill_required", 0) > skill}
        if above:
            problems.append(f"{trade}: taught recipes above skill {skill}: {sorted(above)[:3]}")
        # 3. patterns are found, not taught
        found = {r for r in have if book[r].get("source", "trainer") != "trainer"}
        if found:
            problems.append(f"{trade}: handed out patterns {sorted(found)[:3]}")
        checked += 1

    # 4. clicking an unknown recipe says why
    from world.crafting_manager import get_crafting_manager
    cm = get_crafting_manager()
    for trade in ("tailoring", "alchemy", "jewelcrafting"):
        book = cm.all_recipes(trade)
        pattern = next((rid for rid, r in book.items() if r.get("source") in ("drop", "vendor", "quest")), None)
        if pattern is None:
            continue
        with contextlib.redirect_stdout(io.StringIO()):
            c = Character("Probe", "Hunter", 60)
        c.known_professions.append(trade)
        c.profession_skills[trade] = 300
        ok, msg, _ = cm.craft(c, trade, pattern)
        if ok or "haven't learned that recipe" not in msg:
            problems.append(f"{trade}: an unknown pattern ({pattern}) gave {ok}, {msg!r}")

    print(f"  {checked} trades checked")
    for p in problems:
        print("  PROBLEM " + p)
    print("\nFAIL" if problems else "\nPASS")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
