"""
Class training (Oct 2026): abilities and their higher ranks are bought from class trainers for gold.

Rules (Kyle's call: "Classic: pay to learn"):
  * The starter kit (every rank with level_req <= Character.FREE_TRAINING_LEVEL) is free and automatic.
  * Everything else is learned from a trainer of YOUR class, one ability at a time. Training an ability teaches the highest
    rank your level allows right now, at that rank's price - so skipping lower ranks never costs extra.
  * Price of a rank = COPPER_PER_LEVEL_SQ * level_req^2 copper (L10 = 6s, L20 = 24s, L40 = 96s, L60 = 2g16s), unless the
    ability JSON carries an explicit "train_cost" on that rank.
  * Talent-granted abilities, Shoot/Wand and companions' abilities are not trained (they keep level-based learning).
  * Old saves are grandfathered with every rank they could already cast (Character.from_dict).

Pure rules - the screen (ui/screens/travel_service_screen.py) is presentation, the dialog wiring is services_for_npc.
"""
import json
from pathlib import Path

COPPER_PER_LEVEL_SQ = 6

_TRAINERS = None


def trainers():
    """data/training/trainers.json -> {"class_trainers": {npc_id: class_name}, ...}"""
    global _TRAINERS
    if _TRAINERS is None:
        path = Path(__file__).parent.parent / "data" / "training" / "trainers.json"
        _TRAINERS = json.loads(path.read_text()) if path.exists() else {"class_trainers": {}}
    return _TRAINERS


def reload_trainers():
    global _TRAINERS
    _TRAINERS = None


def class_for_trainer(npc_id):
    return trainers().get("class_trainers", {}).get(npc_id)


def rank_cost(ability, rank_number):
    rank = ability.ranks[rank_number - 1]
    if rank.get("train_cost") is not None:
        return int(rank["train_cost"])
    if rank["level_req"] <= 3:
        return 0
    return COPPER_PER_LEVEL_SQ * rank["level_req"] ** 2


def _highest_available_rank(ability, level):
    best = 0
    for number, rank in enumerate(ability.ranks, start=1):
        if level >= rank["level_req"]:
            best = number
    return best


def offers(character):
    """What a trainer of this character's class can teach right now, cheapest-level first.

    -> list of dicts: ability, name, rank (the rank that would be learned), from_rank (currently trained, 0 = new),
       cost, level_req, new (bool).  Only abilities with something to learn at the character's level are listed."""
    out = []
    if not getattr(character, "training_enabled", False):
        return out
    for ability in character.ability_book.get_all_abilities():
        if not getattr(ability, "trainable", False):
            continue
        have = character.trained_ranks.get(ability.ability_id, 0)
        top = _highest_available_rank(ability, character.level)
        if top > have:
            out.append({
                "ability": ability, "name": ability.name, "rank": top, "from_rank": have,
                "cost": rank_cost(ability, top), "level_req": ability.ranks[top - 1]["level_req"],
                "new": have == 0, "max_rank": len(ability.ranks),
            })
    out.sort(key=lambda o: (o["level_req"], o["name"]))
    return out


def upcoming(character, limit=6):
    """The next few things this character could train at a higher level (for the 'coming soon' rows)."""
    out = []
    if not getattr(character, "training_enabled", False):
        return out
    for ability in character.ability_book.get_all_abilities():
        if not getattr(ability, "trainable", False):
            continue
        have = max(character.trained_ranks.get(ability.ability_id, 0),
                   _highest_available_rank(ability, character.level))
        if have < len(ability.ranks):
            nxt = ability.ranks[have]
            # The ability object rides along so the trainer screen can show its tooltip on
            # hover - "what am I working toward" is the most useful place to be able to read
            # one, and a name and a level is not an answer to that.
            out.append({"name": ability.name, "rank": have + 1, "level_req": nxt["level_req"],
                        "new": have == 0, "ability": ability})
    out.sort(key=lambda o: (o["level_req"], o["name"]))
    return out[:limit]


def train(character, party, ability_id):
    """Buy the best currently-available rank of one ability. -> (ok, message)."""
    for offer in offers(character):
        if offer["ability"].ability_id == ability_id:
            break
    else:
        return False, "There is nothing more I can teach you of that."
    cost = offer["cost"]
    if party is None or party.copper < cost:
        return False, "You can't afford that."
    if cost and not party.remove_currency(cost):
        return False, "You can't afford that."
    character.train_ability(ability_id, offer["rank"])
    ab = offer["ability"]
    label = ab.name if offer["new"] and offer["rank"] == 1 else f"{ab.name} (Rank {offer['rank']})"
    return True, f"You have learned {label}."
