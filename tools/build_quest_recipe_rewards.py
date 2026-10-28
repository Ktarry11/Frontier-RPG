#!/usr/bin/env python3
"""Hang a recipe off the end of a chain, where finishing one earns it. Idempotent.

    PYTHONPATH=. python3 tools/build_quest_recipe_rewards.py [--apply]

Kyle, 2026-10-28: "ensure there are nice rare drops of useful recipies to learn etc. or still reward
some through quests."

SO NOT EVERY QUEST - the ones where getting a pattern is the point of having finished. A chain finale
is the natural home: it already has a requirement behind it, the player has done several steps to
reach it, and a pattern is the kind of reward that keeps mattering after the gear it came with is
replaced. A finale here means a quest that requires other quests and has nothing after it.

WHICH RECIPE. Drop-source ones, matched to the zone: first by place name, since a lot of these were
authored for a particular zone and say so (Razorfen Tusk Bracers, Fenris Mail Spaulders), then by
level, so the recipe is something the player can realistically make soon rather than a trophy they
file away for twenty levels. A recipe stays in the drop pool too - earning it from a chain and
finding it on a corpse are both fine, and WoW does both for the same patterns.

ONE PER ZONE, ON PURPOSE. Two would make it feel like the standard chain payout rather than a thing
worth noticing, and there are 28 zone quest files, so one each is already 20-odd recipes with a home.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: Zone file stem -> words that might appear in a recipe authored for it.
ZONE_WORDS = {
    "ashenvale": ("astranaar", "moonleaf", "satyr", "ashenvale"),
    "southern_barrens": ("razorfen", "barrens", "taurajo"),
    "central_barrens": ("barrens", "crossroads", "stonemace"),
    "northern_barrens": ("barrens", "ratchet"),
    "durotar": ("durotar", "razor", "orgrimmar"),
    "orgrimmar": ("orgrimmar", "warsong"),
    "silverpine_north": ("silverpine", "shadowfang"),
    "silverpine_south": ("silverpine", "shadowfang", "fenris"),
    "fenris_isle": ("fenris",),
    "hillsbrad": ("hillsbrad", "tarren", "southpoint"),
    "undercity": ("undercity", "plague", "virulent"),
    "tirisfal": ("tirisfal", "brill", "mourne"),
    "sepulcher": ("sepulcher", "silverpine"),
    "deathknell": ("deathknell", "tirisfal"),
    "echo_isles": ("echo", "darkspear", "voodoo"),
    "aspen": ("aspen", "birch", "glacier", "stormcaller"),
    "southern_needles": ("needle", "freewind", "galak", "salt", "tide"),
    "underdark": ("geode", "crystal", "resonant", "underdark"),
    "valley_of_trials": ("valley", "durotar"),
    "razor_hill": ("razor", "durotar"),
    "forsaken_lands": ("forsaken", "undercity", "plague"),
}


def main():
    apply = "--apply" in sys.argv
    from world.recipe_manager import all_recipes_by_source

    pool = [(r.get("skill_required", 0), rid, r.get("name", rid), prof)
            for rid, (prof, r) in all_recipes_by_source("drop").items()]
    pool.sort()

    taken, pairs, skipped = set(), [], []
    for path in sorted((ROOT / "data/quests").glob("*.json")):
        doc = json.loads(path.read_text())
        quests = doc.get("quests") or []
        if not isinstance(quests, list):
            continue

        # A FINALE IS THE END OF A ROAD, AND THERE ARE TWO WAYS A ROAD IS BUILT HERE. Some chains
        # link forward with next_quest_id and some gate backward with requires_quests; the first
        # version of this only recognised the second kind and reported "no chain finale" for 16
        # zones including Ashenvale, Durotar and Orgrimmar, which between them have 21 chain ends.
        # Either link counts: something leads here, and nothing leads on.
        after = {q.get("next_quest_id") for q in quests if q.get("next_quest_id")}
        finales = [q for q in quests
                   if not q.get("next_quest_id")
                   and (q.get("requires_quests") or q["quest_id"] in after)]
        if not finales:
            skipped.append((path.stem, "no chain finale"))
            continue
        # the highest-level finale is the end of the zone's longest road
        quest = max(finales, key=lambda q: (q.get("level_min", 1), q["quest_id"]))
        if quest.get("reward_recipe"):
            pairs.append((path.stem, quest["quest_id"], quest["reward_recipe"], "already set"))
            taken.add(quest["reward_recipe"])
            continue

        target = max(1, quest.get("level_min", 1)) * 5
        words = ZONE_WORDS.get(path.stem, ())
        # A PLACE MATCH STILL HAS TO BE SOMETHING YOU CAN MAKE. Matching on the name alone handed
        # Durotar (a level-10 zone) a skill-178 pattern because it happened to say "Razorfang", and
        # handed Southern Thousand Needles a skill-52 one for saying "Saltcrusted". The name is a
        # strong hint about intent, not a licence to ignore the level, so a named match only wins
        # inside this much of the target skill.
        NAME_TOLERANCE = 40
        named = [p for p in pool if p[1] not in taken
                 and any(w in p[2].lower() for w in words)
                 and abs(p[0] - target) <= NAME_TOLERANCE]
        candidates = named or [p for p in pool if p[1] not in taken]
        if not candidates:
            skipped.append((path.stem, "nothing left in the pool"))
            continue
        skill, rid, name, prof = min(candidates, key=lambda p: abs(p[0] - target))
        taken.add(rid)
        pairs.append((path.stem, quest["quest_id"], rid, "by place" if named else "by level"))
        if apply:
            quest["reward_recipe"] = rid
            path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")

    print(f"{len(pairs)} chain finales given a recipe\n")
    from world.recipe_manager import get_recipe_info
    for stem, qid, rid, how in pairs:
        prof, r = get_recipe_info(rid)
        print(f"  {stem:<22}{qid:<34}{r['name']:<32}{prof:<15}skill {r['skill_required']:>3}  ({how})")
    if skipped:
        print(f"\n  no reward placed in {len(skipped)}: " + ", ".join(f"{s} ({w})" for s, w in skipped))
    if not apply:
        print("\n(dry run - pass --apply to write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
