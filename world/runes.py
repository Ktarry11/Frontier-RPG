"""Runes on the soul (Runecrafting).

Data: data/runecrafting/runes.json, written by tools/build_runecrafting.py (Kyle's calls are
there). A character's soul is `character.soul_runes`: four slots, the last one the Capstone's.
Every party member has their own.

WHERE EACH KIND OF RUNE TAKES HOLD
  effects    talent-pool keys (all_damage, healing_received_pct...), folded into
             Character.get_talent_effects, so every formula that reads talents reads runes too.
  procs      hung on the character by Character._sync_equipment_procs, beside item procs.
  Capstones  read at the point they change: landing_school() from Monster.take_damage and the DoT
             branch, gamble() from the damage rolls, and the heal/HoT/DoT branches of
             combat/abilities.py for Renewal, Surge and Detonation.

KYLE'S RULE FOR CONVERSION ("one rule I'd be very careful about"): separate ability identity from
damage identity. A Fireball converted to Frost is still Fireball for talents, bonuses and the
ability's own school; only where it LANDS changes, so the target's Frost resistance decides it.
That's why conversion happens in take_damage (landing) and never in _resolve_damage_school
(identity).

Ranks of a Capstone are how often it happens (30%, 70%, always), rolled per hit, per heal, or
per DoT/HoT when it's applied.
"""
import json
import random
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SLOTS = 4
CAPSTONE_SLOT = 3
ELEMENTS = ("fire", "frost", "nature", "shadow", "holy", "arcane")


@lru_cache(maxsize=1)
def data():
    path = ROOT / "data/runecrafting/runes.json"
    if not path.exists():
        return {"runes": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def rune(rune_id):
    return data()["runes"].get(rune_id) if rune_id else None


def is_rune(material_id):
    return material_id in data()["runes"]


def soul(character):
    """The character's four slots (rune ids or None), made on first use."""
    s = getattr(character, "soul_runes", None)
    if not isinstance(s, list) or len(s) != SLOTS:
        s = (list(s) if isinstance(s, list) else []) + [None] * SLOTS
        s = s[:SLOTS]
        try:
            character.soul_runes = s
        except Exception:
            pass
    return s


def _owner(who):
    """Whose soul counts for this attacker: a pet fights with its owner's runes."""
    owner = getattr(who, "owner", None)
    return owner if owner is not None and hasattr(owner, "soul_runes") else who


def worn(character):
    return [rune(r) for r in soul(character) if rune(r)]


def effects(character):
    """Talent-pool keys from every rune on the soul."""
    out = {}
    for rn in worn(character):
        for k, v in (rn.get("effects") or {}).items():
            out[k] = out.get(k, 0) + v
    return out


def procs(character):
    """[(key suffix, name, proc)] for every proc a rune hangs on the soul."""
    out = []
    for i, rid in enumerate(soul(character)):
        rn = rune(rid)
        if not rn:
            continue
        for j, p in enumerate(rn.get("procs") or []):
            out.append((f"soul{i}_{j}", rn["name"], p))
    return out


def capstone(who):
    """The Capstone's effect dict, or None."""
    who = _owner(who)
    if who is None or not hasattr(who, "soul_runes"):
        return None
    rn = rune(soul(who)[CAPSTONE_SLOT])
    return rn.get("capstone_effect") if rn else None


def _happens(cap, rng=None):
    return (rng or random).random() < cap.get("chance", 1.0)


# ------------------------------------------------------------------ Capstones at the point they act
def landing_school(attacker, school, rng=None):
    """The school a hit LANDS as, after the attacker's conversion or Chaos Capstone. The ability's
    own school (talents, bonuses) is never touched; this is only what resistance sees."""
    cap = capstone(attacker) if attacker is not None else None
    if not cap or school is None:
        return school
    kind = cap.get("kind")
    if kind == "chaos":
        return (rng or random).choice(ELEMENTS) if _happens(cap, rng) else school
    if kind != "convert":
        return school
    if isinstance(school, (list, tuple)):
        return type(school)(landing_school(attacker, s, rng) for s in school)
    src = cap.get("from")
    physical = school == "physical"
    matches = (src == "both") or (src == "physical" and physical) or (src == "magic" and not physical)
    if matches and school != cap["to"] and _happens(cap, rng):
        return cap["to"]
    return school


def gamble(caster, amount, rng=None):
    """The Gambler: a damage roll from the Capstone's range. Mostly under normal, sometimes the
    jackpot; a little under normal on average (Kyle's call). Damage only."""
    cap = capstone(caster)
    if not cap or cap.get("kind") != "gamble" or amount <= 0:
        return amount
    r = rng or random
    if r.random() < cap["jackpot"]:
        mult = r.uniform(cap["jackpot_low"], cap["jackpot_high"])
    else:
        mult = r.uniform(cap["low"], cap["high"])
    return max(1, int(amount * mult))


def gamble_mean(cap):
    if not cap or cap.get("kind") != "gamble":
        return 1.0
    j = cap["jackpot"]
    return (1 - j) * (cap["low"] + cap["high"]) / 2 + j * (cap["jackpot_low"] + cap["jackpot_high"]) / 2


def echo(caster, rng=None):
    """The Echo: does this crit land a second, uncritted time?"""
    cap = capstone(caster)
    return bool(cap and cap.get("kind") == "echo" and _happens(cap, rng))


def heal_to_hot(caster, rng=None):
    """(turns, multiplier) when Renewal turns this direct heal into a HoT, else None."""
    cap = capstone(caster)
    if cap and cap.get("kind") == "heal_to_hot" and _happens(cap, rng):
        return cap.get("turns", 3), cap.get("mult", 1.25)
    return None


def hot_now(caster, rng=None):
    """Surge: the multiplier when this HoT lands all at once, else None."""
    cap = capstone(caster)
    if cap and cap.get("kind") == "hot_to_heal" and _happens(cap, rng):
        return cap.get("mult", 0.85)
    return None


def dot_now(caster, rng=None):
    """Detonation: the multiplier when this DoT hits all at once, else None."""
    cap = capstone(caster)
    if cap and cap.get("kind") == "dot_to_hit" and _happens(cap, rng):
        return cap.get("mult", 0.9)
    return None


def shape_over_time(caster, duration, per_turn):
    """Condensing and Lingering on a DoT or HoT being applied: -> (duration, per_turn).

    Condensing: half the turns (rounded up), and the total grows by its share.
    Lingering: more turns, each tick a quarter softer, so it does more in all but slower."""
    fx = effects(_owner(caster)) if hasattr(_owner(caster), "soul_runes") else {}
    total = duration * per_turn
    cond = fx.get("rune_condense", 0)
    if cond:
        duration = max(1, (duration + 1) // 2)
        per_turn = max(1, int(round(total * (1 + cond) / duration)))
    linger = fx.get("rune_linger", 0)
    if linger:
        duration = max(1, int(round(duration * (1 + linger))))
        per_turn = max(1, int(round(per_turn * 0.75)))
    return duration, per_turn


# ------------------------------------------------------------------ imprinting
def can_imprint(character, slot, rune_id):
    """-> (ok, reason)."""
    rn = rune(rune_id)
    if rn is None:
        return False, "That isn't a rune."
    if not 0 <= slot < SLOTS:
        return False, "No such slot."
    if rn["capstone"] != (slot == CAPSTONE_SLOT):
        return False, ("Capstone runes go in the Capstone slot." if rn["capstone"]
                       else "Only a Capstone rune goes in the Capstone slot.")
    if getattr(character, "level", 1) < rn["level"]:
        return False, f"{character.name} needs to be level {rn['level']} for that rune."
    for i, other in enumerate(soul(character)):
        o = rune(other)
        if i != slot and o and o["family"] == rn["family"]:
            return False, f"{character.name} already carries a rune of that kind."
    return True, ""


def imprint(player, character, slot, rune_id):
    """Imprint a rune from the player's bags on a soul. The rune it replaces is destroyed (Rafa's
    default, the gem rule: changing a build costs materials). -> (ok, message)."""
    ok, why = can_imprint(character, slot, rune_id)
    if not ok:
        return False, why
    if player.get_material_quantity(rune_id) < 1:
        return False, "You don't have that rune."
    player.consume_material(rune_id, 1)
    s = soul(character)
    old = rune(s[slot])
    s[slot] = rune_id
    refresh(character)
    msg = f"{rune(rune_id)['name']} is imprinted on {character.name}'s soul."
    if old:
        msg += f" {old['name']} is gone."
    return True, msg


def refresh(character):
    fn = getattr(character, "_recalculate_derived_stats", None)
    if fn:
        fn()
