#!/usr/bin/env python3
"""Trainer recipes are bought at the trainer, for money, once your skill reaches them. In every trade.

    PYTHONPATH=. python3 tools/qa_trainer_recipes_follow_skill.py

Playtest, 17 Nov 2026: Leatherworking at skill 1, 107 Scrap Leather, and "Missing materials for that recipe" on
the first three recipes. The trainer only ever handed recipes over at the moment a trade was learned or a tier
trained, so the skill 2+ recipes could never be had inside a tier, and a save that learned the trade back when
trades started at 0 (with first recipes at 1) had none. Kyle, the same morning: "You need to go to the trainer
and it costs money to learn!"

FIVE CLAIMS, for every crafting trade:
  1. NOTHING IS FREE. Learning the trade, training a tier and skilling up teach no recipe.
  2. THE TRAINER SELLS what the skill has reached: every trainer recipe at or below it, none above, none known.
  3. IT COSTS MONEY, rising with the skill, and buying one charges that price and teaches it. "Learn all" buys
     cheapest first and stops when the money does.
  4. PATTERNS ARE FOUND, NOT SOLD: drop, vendor and quest recipes never appear at the trainer.
  5. AN UNKNOWN RECIPE SAYS SO when clicked, instead of "Missing materials".
And the stuck save: a character who knows Leatherworking at skill 1 with no recipes is offered its first ones.
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
    from world import profession_manager as pm
    from world.recipe_manager import trainer_recipe_book

TRADES = ["blacksmithing", "leatherworking", "tailoring", "alchemy", "woodworking", "engineering", "cooking",
          "jewelcrafting", "enchanting", "runecrafting"]


class Purse:
    def __init__(self, copper):
        self.copper = copper

    def remove_currency(self, n):
        if n > self.copper:
            return False
        self.copper -= n
        return True


def fresh(level=30):
    with contextlib.redirect_stdout(io.StringIO()):
        return Character("Probe", "Hunter", level)


def main():
    problems = []
    for trade in TRADES:
        book = trainer_recipe_book(trade)
        if not book:
            problems.append(f"{trade}: no recipe book")
            continue
        # 1. learning the trade, training a tier, skilling up: nothing free
        c = fresh(60)
        ok, _msg = pm.learn(c, Purse(10 ** 9), trade)
        if not ok:
            problems.append(f"{trade}: could not learn it at the trainer")
            continue
        for _ in range(80):
            c.gain_profession_skill(trade, 1)
        pm.advance(c, Purse(10 ** 9), trade)
        free = [r for r in c.known_recipes if r in book]
        if free:
            problems.append(f"{trade}: learned free, without paying: {sorted(free)[:3]}")
        # 2. what the trainer sells
        skill = c.profession_skills[trade]
        want = {rid for rid, r in book.items()
                if r.get("source", "trainer") == "trainer" and r.get("skill_required", 0) <= skill}
        offers = pm.recipe_offers(c, trade)
        sold = {o["recipe_id"] for o in offers}
        if want - sold:
            problems.append(f"{trade}: at skill {skill} the trainer doesn't sell {sorted(want - sold)[:3]}")
        if sold - want:
            problems.append(f"{trade}: the trainer sells what it shouldn't: {sorted(sold - want)[:3]}")
        # 4. patterns are never sold
        pat = {rid for rid in sold if book[rid].get("source", "trainer") != "trainer"}
        if pat:
            problems.append(f"{trade}: the trainer sells patterns {sorted(pat)[:3]}")
        # 3. it costs money, and buying works
        if offers:
            o = offers[-1]
            if o["cost"] <= 0:
                problems.append(f"{trade}: {o['name']} is free")
            purse = Purse(o["cost"] - 1)
            ok, _ = pm.buy_recipe(c, purse, trade, o["recipe_id"])
            if ok or o["recipe_id"] in c.known_recipes:
                problems.append(f"{trade}: bought {o['name']} without the money")
            purse = Purse(o["cost"])
            ok, _ = pm.buy_recipe(c, purse, trade, o["recipe_id"])
            if not ok or purse.copper != 0 or o["recipe_id"] not in c.known_recipes:
                problems.append(f"{trade}: paying {o['cost']} for {o['name']} did not teach it")
            rest = pm.recipe_offers(c, trade)
            if len(rest) >= 2:
                budget = rest[0]["cost"] + rest[1]["cost"]
                purse = Purse(budget)
                pm.buy_all_recipes(c, purse, trade)
                if purse.copper != 0 or not {rest[0]["recipe_id"], rest[1]["recipe_id"]} <= c.known_recipes:
                    problems.append(f"{trade}: Learn all did not buy the two cheapest with money for two")

    prices = [pm.recipe_price({"skill_required": s}) for s in (0, 50, 150, 300)]
    if prices != sorted(prices) or len(set(prices)) != 4:
        problems.append(f"recipe prices do not rise with skill: {prices}")

    # the stuck save from the playtest
    c = fresh(10)
    c.known_professions.append("leatherworking")
    c.profession_skills["leatherworking"] = 1
    c.known_recipes = set()
    with contextlib.redirect_stdout(io.StringIO()):
        c = Character.from_dict(c.to_dict())
    if c.known_recipes & set(trainer_recipe_book("leatherworking")):
        problems.append("the stuck save was given recipes for free on load")
    firsts = {o["recipe_id"] for o in pm.recipe_offers(c, "leatherworking")}
    if not {"lw_light_armor_kit", "lw_cure_light_leather"} <= firsts:
        problems.append(f"the stuck save's trainer doesn't sell its first recipes: {sorted(firsts)}")

    # 5. clicking an unknown recipe says why
    from world.crafting_manager import get_crafting_manager
    from world.leatherworking_manager import get_leatherworking_manager
    cm = get_crafting_manager()
    c = fresh(10)
    c.known_professions.append("tailoring")
    c.profession_skills["tailoring"] = 1
    first = next(rid for rid, r in cm.all_recipes("tailoring").items()
                 if r.get("source", "trainer") == "trainer" and r.get("skill_required", 0) <= 1)
    ok, msg, _ = cm.craft(c, "tailoring", first)
    if ok or "Buy it from a Tailoring trainer" not in msg:
        problems.append(f"an unknown trainer recipe gave {ok}, {msg!r}")
    if get_leatherworking_manager().craft(c, "lw_cure_light_leather") is not None:
        problems.append("Leatherworking crafted a recipe nobody bought")

    print(f"  {len(TRADES)} trades checked; prices at skill 0/50/150/300: {prices}")
    for p in problems:
        print("  PROBLEM " + p)
    print("\nFAIL" if problems else "\nPASS")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
