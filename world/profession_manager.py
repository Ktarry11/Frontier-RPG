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
        _DATA = json.loads((Path(__file__).parent.parent / "data" / "professions" / "professions.json").read_text())
    return _DATA


def professions():
    return data()["professions"]


def tiers():
    return data()["tiers"]


def max_primary():
    return int(data().get("max_primary", 3))


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
        slots_left = max_primary() - len(character.known_professions)
        reason = None
        if slots_left <= 0:
            reason = f"You already know {max_primary()} professions. Unlearn one first."
        elif character.level < first["required_level"]:
            reason = f"Requires level {first['required_level']}"
        rows.append(dict(kind="learn", name=f"Learn {info['name']} ({first['name']})",
                         sub=f"{info['description']}  Skill cap {first['cap']}.  ({slots_left} of {max_primary()} slots free)",
                         cost=first["cost"], enabled=reason is None, reason=reason))
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
                             sub=f"Raises your skill cap from {cap} to {nxt['cap']}.", cost=nxt["cost"],
                             enabled=reason is None, reason=reason))
    else:
        rows.append(dict(kind="info", name=f"{info['name']} mastered", sub=f"{t[idx]['name']}  -  skill {skill} / {cap}",
                         cost=None, enabled=False, reason=None))
    rows.append(dict(kind="unlearn", name=f"Unlearn {info['name']}",
                     sub=f"You forget {info['name']} and lose your {skill} skill. This cannot be undone.",
                     cost=None, enabled=True, reason=None))
    return rows


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
