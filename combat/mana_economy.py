"""THE MANA ECONOMY: how much a spell costs, against what it does (Kyle, 27 Nov 2026).

Kyle's test at 60: a naked Priest has 4,800 mana and Heal costs 313, so 15 Heals from a full bar before regen;
Flash Heal is faster AND cheaper (224) - "This creates an undesirable relationship where the faster emergency heal
is also cheaper." He asked for:
  * costs generally higher, so mana is a real decision in a long fight;
  * Flash/Lesser Heal: fast emergency healing, less efficient - about Heal's mana for less healing;
  * Heal: the standard heal, slower, the most efficient;
  * Greater Heal: a large heal, the longest cast, the highest cost;
  * the same relationship at every rank, levels 1-60.

TWO RULES, applied where abilities are built so they reach every class and every rank:

1. THE TABLES (data/balance/mana_costs.json). Per class, by level, a multiplier for its damage spells and one for its
   heals (tools/calibrate_mana_costs.py), then per SPEC (tools/calibrate_spec_mana.py, spec_factor below, applied in
   Ability.talented_cost) so every spec - not just its class's median - runs dry in about the same time: damage
   specs ~14 turns of their real rotation, healers ~12 casts of their main heal (Restoration Shaman 10), levels
   10-60, geared, regen counted. Measured after both (27 Nov 2026): damage 12.4-16.1 turns, heals 9.9-13.5 casts.
   HEAL_TIGHTEN / DAMAGE_TIGHTEN stay as a global knob at 1.0.

2. THE HEAL LADDER (apply_heal_ladder, from get_class_abilities): within a class, the medium-cast single-target
   direct heal with the most ranks is the ANCHOR (Priest Heal; a class with no medium heal anchors on its main heal
   - Shaman Healing Wave, Paladin Holy Light). Every other single-target direct heal at another speed is priced off the anchor's rank at the same
   level, by its size and a healing-per-mana share for its speed:
        cost = anchor cost x (its heal / the anchor's heal) / HPM[speed]
   A short heal at 0.6 of the anchor's efficiency heals about 60% of it for about the same mana; a long one is
   slightly less efficient than the anchor. A single-target HoT is priced at HOT_HPM of the anchor (its up-front heal
   and every tick counted). Heals on longer cooldowns and party heals are left to the table: their own decisions.
"""

#: 1.0 since the table was recalibrated to the tighter targets (tools/calibrate_mana_costs.py: ~14 turns of damage,
#: ~12 casts of a main heal); kept as the knob for a quick global nudge
HEAL_TIGHTEN = 1.0
DAMAGE_TIGHTEN = 1.0

#: healing per mana against the anchor, by cast speed (combat/abilities.CAST_SPEEDS)
HPM = {0.25: 0.55, 0.5: 0.6, 0.75: 1.0, 1.0: 0.95}
ANCHOR_SPEED = 0.75


def tighten(effect_type):
    return HEAL_TIGHTEN if effect_type in ("heal", "hot", "damage_and_heal") else DAMAGE_TIGHTEN


#: a single-target HoT's healing per mana against the anchor, counting its up-front heal and every tick. Before the
#: ladder took them in (27 Nov 2026) HoTs ran 1.7-2x the anchor's efficiency (Renew 4.1 healing a mana against Heal's
#: 2.4) on top of the table's own costs, which is how a healer never ran dry rolling HoTs.
HOT_HPM = 1.3


def _is_ladder_hot(a):
    return (a.effect_type == "hot" and (a.cooldown or 0) <= 2
            and getattr(a, "target_type", None) not in ("party", "all_allies")
            and getattr(a, "heal_scope", None) != "party"
            and getattr(getattr(a, "resource_type", None), "value", None) == "mana"
            and a.ranks and all(r.get("cost") for r in a.ranks))


def _is_ladder_heal(a):
    return (a.effect_type == "heal" and (a.cooldown or 0) <= 1
            and getattr(a, "target_type", None) not in ("party", "all_allies")
            and getattr(a, "heal_scope", None) != "party"
            and getattr(getattr(a, "resource_type", None), "value", None) == "mana"
            and a.ranks and all(r.get("cost") for r in a.ranks))


def _speed_key(speed):
    return min(HPM, key=lambda k: abs(k - (speed or ANCHOR_SPEED)))


def apply_heal_ladder(abilities):
    heals = [a for a in abilities if _is_ladder_heal(a)]
    if not heals or len(heals) + sum(1 for a in abilities if _is_ladder_hot(a)) < 2:
        return
    anchors = [a for a in heals if _speed_key(getattr(a, "cast_speed", ANCHOR_SPEED)) == ANCHOR_SPEED] or heals
    anchor = max(anchors, key=lambda a: (len(a.ranks), a.ranks[-1].get("level_req", 1)))
    aranks = sorted(anchor.ranks, key=lambda r: r.get("level_req", 1))
    a_hpm = HPM[_speed_key(getattr(anchor, "cast_speed", ANCHOR_SPEED))]
    hots = [a for a in abilities if _is_ladder_hot(a)]
    for a in heals + hots:
        if a is anchor:
            continue
        if a.effect_type == "hot":
            hpm = HOT_HPM
        else:
            hpm = HPM[_speed_key(getattr(a, "cast_speed", ANCHOR_SPEED))] / a_hpm
        for r in a.ranks:
            lv = r.get("level_req", 1)
            ref = next((x for x in reversed(aranks) if x.get("level_req", 1) <= lv), aranks[0])
            size = (r.get("effect_value") or 0) + (r.get("heal_value") or 0)
            if not ref.get("effect_value") or not size:
                continue
            r["cost"] = max(1, int(round(ref["cost"] * (size / ref["effect_value"]) / hpm)))


# ---- 3. SPEC FACTORS: data/balance/mana_costs.json "specs" (written by tools/calibrate_spec_mana.py): per spec, by
# level, a multiplier on its mana costs so every spec runs dry in about the same turns as its target, not just its
# class's median. A character with no spec yet pays 1.0.
_SPEC = None


def _spec_table():
    global _SPEC
    if _SPEC is None:
        try:
            import json
            from pathlib import Path
            _SPEC = json.loads((Path(__file__).resolve().parent.parent / "data/balance/mana_costs.json")
                               .read_text(encoding="utf-8")).get("specs", {})
        except (OSError, ValueError):
            _SPEC = {}
    return _SPEC


def spec_factor(caster, effect_type):
    if not hasattr(caster, "talent_trees"):
        return 1.0
    table = _spec_table()
    if not table:
        return 1.0
    try:
        from entities.proficiency import active_spec
        spec = active_spec(caster)
    except Exception:                                           # noqa: BLE001
        return 1.0
    row = (table.get(spec) or {}).get("heal" if effect_type in ("heal", "hot", "damage_and_heal") else "damage")
    if not row:
        return 1.0
    lv = getattr(caster, "level", 1) or 1
    if lv <= row[0][0]:
        return row[0][1]
    for (a, fa), (b, fb) in zip(row, row[1:]):
        if a <= lv <= b:
            return fa + (fb - fa) * (lv - a) / max(1, b - a)
    return row[-1][1]
