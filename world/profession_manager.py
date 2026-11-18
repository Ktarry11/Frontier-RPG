"""
Profession training (Oct 2026): learn a profession from its trainer, then train up through the tiers.

  * A character can know MAX_PRIMARY (3) professions.  Learning one costs the Apprentice price (skill cap 75).
  * When the skill reaches the tier cap, the trainer sells the next tier (Journeyman 150, Expert 225, Artisan 300) - needs a
    minimum character level and gold.
  * Unlearning forgets the profession and resets its skill to 0 (so re-learning starts over).
  * Gathering without the profession still picks things up, but never skills up; crafting needs the profession.

Data: data/professions/professions.json (list + tiers), data/training/trainers.json ("profession_trainers": npc_id -> LIST of professions).
Pure rules; the screen is ui/screens/travel_service_screen.py (kind "train_prof").
"""
import json
from pathlib import Path

_DATA = None


def data():
    global _DATA
    if _DATA is None:
        _DATA = json.loads((Path(__file__).parent.parent / "data" / "professions" / "professions.json").read_text(encoding="utf-8"))
    return _DATA


def professions():
    return data()["professions"]


def tiers():
    return data()["tiers"]


def max_primary(character=None):
    """Primary profession slots: the base (3), plus one for every Craftsman Codex the character has read
    (world/craftsman_codex.py). Without a character, the base."""
    base = int(data().get("max_primary", 3))
    return base + int(getattr(character, "codices", 0) or 0) if character is not None else base


def primary_total():
    """How many primary trades exist - a slot count past this would do nothing."""
    return sum(1 for d in professions().values() if isinstance(d, dict) and d.get("kind") != "secondary")


def is_secondary(profession):
    """True for a trade that does NOT cost a profession slot.

    Kyle, 2026-10-31, on Cooking: "it would be 'secondary' since i dont want it to take up
    profession space." The slot rule is the ONLY thing that differs - tiers, caps, trainers,
    skill-ups and recipes all behave exactly as a primary's do. Keeping it to one flag rather
    than a parallel secondary-profession system means there is nothing to keep in step.
    """
    return professions().get(profession, {}).get("kind") == "secondary"


def primary_count(character):
    """How many of the character's known professions actually occupy a slot."""
    return sum(1 for p in character.known_professions if not is_secondary(p))


def professions_for_trainer(npc_id):
    """-> list of profession ids this NPC teaches (possibly empty).

    Trainers come in THEMED PAIRS now (mining + blacksmithing, herbalism + alchemy, and so on), so the
    data value is a list. Old data stored a bare string for the single profession; that is still accepted
    so a stale trainers.json does not crash the service screen.
    """
    from world import training_manager
    v = training_manager.trainers().get("profession_trainers", {}).get(npc_id)
    if v is None:
        return []
    return [v] if isinstance(v, str) else list(v)


def profession_for_trainer(npc_id):
    """Back-compat: the FIRST profession this NPC teaches, or None.

    Kept because travel_manager only needs to know whether an NPC is a trainer at all. Anything that
    shows the player what is on offer must use professions_for_trainer instead.
    """
    got = professions_for_trainer(npc_id)
    return got[0] if got else None


def tier_name(index):
    t = tiers()
    return t[max(0, min(index, len(t) - 1))]["name"]


def offers(character, profession):
    """Rows a trainer of `profession` can sell this character right now.

    -> list of dicts: kind ("learn"|"advance"|"info"|"unlearn"), name, sub, cost, enabled, reason."""
    info = professions().get(profession)
    if info is None:
        return []
    rows = []
    t = tiers()
    if not character.knows_profession(profession):
        first = t[0]
        secondary = is_secondary(profession)
        # A secondary trade is free of the slot limit entirely - it neither needs a free slot
        # nor reports one, because telling the player "2 of 3 slots free" next to something that
        # costs no slot is exactly the kind of half-true the old line would have printed.
        slots_left = max_primary(character) - primary_count(character)
        reason = None
        if not secondary and slots_left <= 0:
            reason = f"You already know {max_primary(character)} professions. Unlearn one first."
        elif character.level < first["required_level"]:
            reason = f"Requires level {first['required_level']}"
        slot_note = ("  Secondary - costs you no profession slot."
                     if secondary else f"  ({slots_left} of {max_primary(character)} slots free)")
        rows.append(dict(kind="learn", name=f"Learn {info['name']} ({first['name']})",
                         sub=f"{info['description']}  Skill cap {first['cap']}.{slot_note}",
                         cost=_rep(first["cost"]), enabled=reason is None, reason=reason))
        return rows

    idx = min(character.profession_tiers.get(profession, 0), len(t) - 1)
    skill = character.profession_skills.get(profession, 0)
    cap = t[idx]["cap"]
    if idx + 1 < len(t):
        nxt = t[idx + 1]
        if skill < cap:
            rows.append(dict(kind="info", name=f"{nxt['name']} {info['name']}",
                             sub=f"Reach skill {cap} first  (you have {skill}).  Requires level {nxt['required_level']}.",
                             cost=None, enabled=False, reason=None))
        else:
            reason = f"Requires level {nxt['required_level']}" if character.level < nxt["required_level"] else None
            rows.append(dict(kind="advance", name=f"Train {nxt['name']} {info['name']}",
                             sub=f"Raises your skill cap from {cap} to {nxt['cap']}.", cost=_rep(nxt["cost"]),
                             enabled=reason is None, reason=reason))
    else:
        rows.append(dict(kind="info", name=f"{info['name']} mastered", sub=f"{t[idx]['name']}  -  skill {skill} / {cap}",
                         cost=None, enabled=False, reason=None))
    rows.append(dict(kind="unlearn", name=f"Unlearn {info['name']}",
                     sub=f"You forget {info['name']} and lose your {skill} skill. This cannot be undone.",
                     cost=None, enabled=True, reason=None))
    return rows


def _rep(copper):
    """A trainer's price after the town's reputation discount (world/faction_manager.rep_price)."""
    from world.faction_manager import rep_price
    return rep_price(copper)


def _pay(party, cost):
    if cost and (party is None or party.copper < cost or not party.remove_currency(cost)):
        return False
    return True


def learn(character, party, profession):
    rows = [r for r in offers(character, profession) if r["kind"] == "learn"]
    if not rows:
        return False, "You already know that profession."
    row = rows[0]
    if not row["enabled"]:
        return False, row["reason"]
    if not _pay(party, row["cost"]):
        return False, "You can't afford that."
    character.learn_profession(profession)
    return True, f"You have learned {professions()[profession]['name']}!"


def advance(character, party, profession):
    rows = [r for r in offers(character, profession) if r["kind"] == "advance"]
    if not rows:
        return False, "You can't advance further right now."
    row = rows[0]
    if not row["enabled"]:
        return False, row["reason"]
    if not _pay(party, row["cost"]):
        return False, "You can't afford that."
    character.profession_tiers[profession] = character.profession_tiers.get(profession, 0) + 1
    name = tier_name(character.profession_tiers[profession])
    return True, f"You are now a {name} {professions()[profession]['name']}!"


def unlearn(character, profession):
    if not character.unlearn_profession(profession):
        return False, "You don't know that profession."
    return True, f"You have unlearned {professions()[profession]['name']}."


# ------------------------------------------------------------------ recipes, bought at the trainer
# Kyle, 17 Nov 2026: "You need to go to the trainer and it costs money to learn!" A trainer recipe is
# never given away: not on a skill-up, not on learning the trade, not on training a tier. You walk to a
# trainer of the trade and pay for each recipe your skill has reached.

def recipe_price(recipe):
    """Copper to learn a trainer recipe: a few copper for the first ones, rising with the skill it needs,
    alongside the tier fees (5s, 2g, 15g, 60g). Skill 0: 10c. 50: 5s10c. 100: 20s. 150: 45s. 200: 80s.
    250: 1g25s. 300: 1g80s. A recipe may set its own "train_cost"."""
    if recipe.get("train_cost") is not None:
        return int(recipe["train_cost"])
    s = int(recipe.get("skill_required", 0) or 0)
    return 10 + (s * s) // 5


def recipe_offers(character, profession):
    """Every trainer recipe of `profession` the character's skill has reached and they don't know yet,
    cheapest first. -> [dict(recipe_id, name, skill, cost)]."""
    if not character.knows_profession(profession):
        return []
    from world.recipe_manager import trainer_recipe_book
    skill = character.profession_skills.get(profession, 0)
    out = []
    for rid, r in trainer_recipe_book(profession).items():
        if r.get("source", "trainer") != "trainer" or rid in character.known_recipes:
            continue
        if r.get("skill_required", 0) > skill:
            continue
        out.append(dict(recipe_id=rid, name=r.get("name", rid), skill=r.get("skill_required", 0),
                        cost=_rep(recipe_price(r))))
    return sorted(out, key=lambda o: (o["cost"], o["skill"], o["name"]))


def affordable(offers, copper):
    """The offers bought cheapest first until the money runs out."""
    got = []
    for o in sorted(offers, key=lambda o: o["cost"]):
        if o["cost"] > copper:
            break
        got.append(o)
        copper -= o["cost"]
    return got


def buy_recipe(character, party, profession, recipe_id):
    o = next((o for o in recipe_offers(character, profession) if o["recipe_id"] == recipe_id), None)
    if o is None:
        return False, "That recipe isn't for sale to you."
    if not _pay(party, o["cost"]):
        return False, "You can't afford that."
    character.known_recipes.add(recipe_id)
    return True, f"You learned {o['name']}."


def buy_all_recipes(character, party, profession):
    offers = recipe_offers(character, profession)
    got = affordable(offers, party.copper if party is not None else 0)
    learned = 0
    for o in got:
        if not _pay(party, o["cost"]):
            break
        character.known_recipes.add(o["recipe_id"])
        learned += 1
    if not learned:
        return False, "You can't afford any of them."
    return True, f"You learned {learned} recipe{'s' if learned != 1 else ''}."
