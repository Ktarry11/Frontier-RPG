"""THE SUPPORT FORMULA: buffs and debuffs sized against what a character (or a monster) of the rank's level has.

Kyle, 16 Nov 2026: "get into the support skills and them not actually benefiting from ranking up and being
obsolete" and "Make sure support skills and buffs are actually properly done with proper skill levels too".

MEASURED FIRST. A buff's flat stats were authored once, in old-world units, and a rank only scaled them 33% -> 100%:
Power Word: Fortitude's top rank gave +3 Stamina (about 70 health on a level-60 tank with 4,400), Arcane Intellect
+3 Intellect, Blessing of Might +40 attack power against a level-60 Warrior's 1,350. And 165 of the 228 buffs and
debuffs that carry flat stats had ONE rank, so they never grew at all.

THE RULE. Every flat stat a class buff or debuff carries is a share of the same stat on a geared character of the
level its rank is learned at (data/balance/stat_reference.json, tools/calibrate_stat_reference.py). For a debuff on
an enemy, the median monster's armour or attack power. So a rank learned at 50 is sized for 50, and the next rank,
ten levels on, is a real step:

    value = SHARE[shape] x reference(stat, rank level)      sign kept: a debuff still takes away

  shape   a long buff on the party (Fortitude, Arcane Intellect, Kings, Mark of the Wild: survives between fights)
          LONG_PARTY 15%, or 8% a stat when it gives four or more core stats at once (Kings, Mark of the Wild)
          a short buff in a fight on the party (a shout, a cooldown aura)  COMBAT_PARTY 15%
          a short buff in a fight on yourself or one ally                 COMBAT_ONE 20%
          a debuff on an enemy (Sunder, Demoralizing Shout)               DEBUFF 15% of the monster's stat
  stats   stamina, strength, agility, intellect, spirit, attack power, spell power (any school), healing power,
          armour (at half the share: plate sets the reference), and mp5 (below). Percentages (crit, haste, dodge, damage taken) are the same at
          every level and keep their authored value. So do resistances (mitigation stays on the old line,
          combat/world_curve.py).
  mp5     (Kyle, 17 Nov 2026: "Real mp5, sized by level"). Gear barely carries mp5, so a share of the measured mp5
          would shrink every mana buff to nothing. Its reference is MP5_PER_SPIRIT x the Spirit reference instead,
          which puts a long buff's mp5 (LONG_PARTY, on yourself or the party) at about what a geared caster's Spirit
          gives back on a turn they cast (Spirit x 0.6 per turn x the 30% five-second rule). Both are multiplied by
          the world curve the same way (Character.mana_per_turn), so the comparison holds at every level.
  floor   never smaller than authored at the rank's scalar: the formula lifts what went obsolete, it doesn't cut
          what a designer made big on purpose

Talents that raise a buff's potency (ability_<id>_potency) apply on top, as before.
FRONTIER_SUPPORT_FORMULA=off puts the old rule back for before/after sims.
"""
import json
import os
from pathlib import Path

LONG_PARTY = 0.15
LONG_PARTY_MANY = 0.08
COMBAT_PARTY = 0.15
COMBAT_ONE = 0.20
DEBUFF = 0.15
#: armour is measured across every spec (plate tanks set the 75th percentile), so a share of it is half the size: a
#: cloth caster's armour buff should not double its armour (Demon Armor at 20% of the reference was +869)
ARMOR_FACTOR = 0.5

CORE = ("stamina", "strength", "agility", "intellect", "spirit")
SCHOOLS = ("fire", "frost", "arcane", "shadow", "nature", "holy")
#: stat key -> the reference it is a share of
REF_OF = {k: k for k in CORE + ("attack_power", "spell_power", "healing_power", "armor", "mp5")}
#: mp5's reference is this many times the Spirit reference (see "mp5" above): LONG_PARTY x 1.2 = 0.6 x 0.30
MP5_PER_SPIRIT = 1.2
REF_OF.update({f"{s}_spell_power": "spell_power" for s in SCHOOLS})
#: on an enemy, these two are sized against the median monster's
MONSTER_REF = {"armor": "monster_armor", "attack_power": "monster_attack_power"}

EXCLUDED_PREFIXES = ("personal_", "pet_", "recruit_", "universal_")

ENABLED = os.environ.get("FRONTIER_SUPPORT_FORMULA", "").lower() != "off"
_REF = None


def _table():
    global _REF
    if _REF is None:
        try:
            _REF = json.loads((Path(__file__).resolve().parent.parent / "data/balance/stat_reference.json")
                              .read_text(encoding="utf-8")).get("reference") or {}
        except (OSError, ValueError):
            _REF = {}
    return _REF


def enabled():
    return ENABLED and bool(_table())


def reference(stat, level):
    if stat == "mp5":
        spirit = reference("spirit", level)
        return spirit * MP5_PER_SPIRIT if spirit else None
    t = _table().get(stat)
    if not t:
        return None
    lv = max(1, min(int(level or 1), max(int(k) for k in t)))
    return float(t.get(str(lv)) or 0.0) or None


def scaled_keys(stat_mods):
    """The flat stats in a stat_mods dict this formula sizes."""
    return [k for k, v in (stat_mods or {}).items()
            if k in REF_OF and isinstance(v, (int, float)) and not isinstance(v, bool) and v != 0]


def share(effect_type, target_type, buff_scope, stat_mods):
    if effect_type == "debuff":
        return DEBUFF
    party = target_type in ("party", "raid")
    if buff_scope in ("raid", "party") and party:
        many = sum(1 for k in (stat_mods or {}) if k in CORE) >= 4
        return LONG_PARTY_MANY if many else LONG_PARTY
    return COMBAT_PARTY if party else COMBAT_ONE


def sized_mods(effect_type, target_type, buff_scope, stat_mods, level):
    """{key: value} for the keys this formula sizes, at this rank level; the rest are left to the caller.
    {} when there's nothing to size or the table is missing."""
    if not enabled():
        return {}
    keys = scaled_keys(stat_mods)
    if not keys:
        return {}
    sh = share(effect_type, target_type, buff_scope, stat_mods)
    out = {}
    for k in keys:
        ref_name = REF_OF[k]
        if effect_type == "debuff" and ref_name in MONSTER_REF:
            ref_name = MONSTER_REF[ref_name]
        ref = reference(ref_name, level)
        if not ref:
            continue
        sign = -1 if stat_mods[k] < 0 else 1
        # a long mana buff is sized as a long one whether it's on you or the party (Aspect of the Moonwell, Vow of
        # Grace): a thirty-minute self buff at the in-fight cooldown's share would out-give every party one
        sk = LONG_PARTY if (k == "mp5" and buff_scope == "raid" and effect_type == "buff") else sh
        out[k] = sign * max(1, int(round(sk * ref * (ARMOR_FACTOR if ref_name in ("armor", "monster_armor") else 1.0))))
    return out


def ability_mods(ability):
    """The sized stats for an Ability at its current rank ({} for one this formula doesn't size).

    NEVER SMALLER THAN AUTHORED: the formula lifts what had gone obsolete, it doesn't cut what a designer made big on
    purpose (an old-scale +40 spell power aura was already a big buff, and a Sunder of -160 armour already bit). Each
    key is the larger of the formula's size and the authored value at this rank's scalar."""
    aid = str(getattr(ability, "ability_id", "") or "")
    # class abilities only: a recruit's personal kit grows on its own ladder (15/30/45/60), and a pet's with the pet
    if not aid or aid.startswith(EXCLUDED_PREFIXES):
        return {}
    try:
        level = ability.current_rank.get("level_req", 1) or 1
    except Exception:                                   # noqa: BLE001
        return {}
    mods = getattr(ability, "stat_mods", None) or {}
    sized = sized_mods(getattr(ability, "effect_type", None), getattr(ability, "target_type", None),
                       getattr(ability, "buff_scope", None), mods, level)
    if not sized:
        return {}
    try:
        scalar = ability._stat_mod_scalar()
    except Exception:                                   # noqa: BLE001
        scalar = 1.0
    out = {}
    for k, v in sized.items():
        authored = mods[k] * scalar
        out[k] = v if abs(v) >= abs(authored) else authored
    return out
