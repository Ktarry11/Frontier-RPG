"""Letters from the people you've helped: follow-ups, thank-you gifts, and quests that start in the mail.

Kyle, 15 Nov 2026: "With mail system now we can get quests in the mail or follow up from quest givers to update on
their findings or to request aid etc." His answers: follow-ups, mail-start quests and thank-you rewards, and yes,
letters can start new chains, hidden ones too; rare and special; a bit of everywhere; some send you toward places
nobody can find, and the writers "don't KNOW where the zones are", so there are no hints.

Letters live in data/mail/quest_letters.json:

    {"id": "...", "trigger": {"after_quest": "<quest id>"} | {"level": 30},
     "delay": 6,              market hours after the trigger before it arrives (world/market/market.py's clock)
     "chance": 1.0,           rolled once, when the trigger fires
     "sender": "Sergra Darkthorn", "subject": "...", "body": "...",
     "copper": 0,
     "gifts": [{"kind": "consumable"|"material", "id": "...", "qty": 1}, {"kind": "recipe", "id": "<recipe id>"}],
     "starts": {"item_id": "...", "name": "...", "description": "...", "quest_id": "..."}}

A letter that starts a quest carries the quest's starter item (the same thing a monster can drop: a LootItem with
starts_quest_id, opened from the bags or straight from the letter with Read the Request). The quest itself is an
ordinary quest whose giver is "item:<item_id>" (data/quests/mail_quests.json).

Each letter is sent at most once per character; the mailbox remembers which (Mailbox.sent_keys).
"""
import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data/mail/quest_letters.json"


@lru_cache(maxsize=1)
def letters():
    try:
        return json.loads(DATA.read_text(encoding="utf-8")).get("letters", [])
    except (OSError, ValueError):
        return []


@lru_cache(maxsize=1)
def by_quest():
    out = {}
    for L in letters():
        q = (L.get("trigger") or {}).get("after_quest")
        if q:
            out.setdefault(q, []).append(L)
    return out


def _goods(L):
    from world.market import goods as G
    out = []
    for g in L.get("gifts") or []:
        kind = g.get("kind")
        if kind == "material":
            from world.gathering_manager import get_gathering_node_manager
            m = get_gathering_node_manager().make_material_instance(g["id"])
            if m is not None:
                out.append(G.pack(m, g.get("qty", 1)))
        elif kind == "consumable":
            from entities.consumable_manager import get_consumable_manager
            c = get_consumable_manager().get_consumable(g["id"], 1)
            if c is not None:
                out.append(G.pack(c, g.get("qty", 1)))
        elif kind == "recipe":
            from world.recipe_manager import make_recipe_scroll
            it = make_recipe_scroll(g["id"])
            if it is not None:
                out.append(G.pack(it))
    s = L.get("starts")
    if s:
        from entities.loot_item import LootItem
        item = LootItem(s["item_id"], s["name"], category="quest", description=s.get("description", ""),
                        icon_id=s.get("icon_id", "qi_letter"), starts_quest_id=s["quest_id"])
        out.append(G.pack(item))
    return out


def _send(mail, L, now, rng):
    from world.mail import Letter
    if L["id"] in mail.sent_keys:
        return False
    mail.sent_keys.add(L["id"])
    if rng.random() >= float(L.get("chance", 1.0)):
        return False
    letter = Letter(L.get("sender", "Somebody"), L.get("subject", ""), body=L.get("body", ""),
                    copper=int(L.get("copper", 0) or 0), goods=_goods(L), kind="letter", sent_at=now,
                    arrives_at=now + float(L.get("delay", 6)), sender_kind="npc")
    letter.note = L["id"]
    mail.deliver(letter)
    return True


def on_quest_done(party, quest_id):
    """A quest was turned in: any letter waiting on it is posted (it arrives after its delay)."""
    todo = by_quest().get(quest_id)
    if not todo:
        return 0
    from world.market.market import market_of
    m = market_of(party)
    n = 0
    for L in todo:
        n += bool(_send(m.mail, L, m.clock, m.rng))
    return n


def on_tick(party, market):
    """Level-triggered letters, checked whenever the market clock moves (cheap: a handful of letters)."""
    level = int(getattr(getattr(party, "player", None), "level", 0) or 0)
    if not level or market.mail is None:
        return 0
    n = 0
    for L in letters():
        need = (L.get("trigger") or {}).get("level")
        if need and level >= int(need) and L["id"] not in market.mail.sent_keys:
            n += bool(_send(market.mail, L, market.clock, market.rng))
    return n
