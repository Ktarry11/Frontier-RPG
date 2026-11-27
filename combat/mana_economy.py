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

1. TIGHTEN (combat/ability_scaling.curved_ranks): every mana cost is multiplied on top of the per-class table
   (data/balance/mana_costs.json, which sized each class's main spell at ~20 casts from a full bar): heals by
   HEAL_TIGHTEN, damage and everything else by DAMAGE_TIGHTEN. A main heal now lasts ~16 casts, a main nuke ~17,
   before regen.

2. THE HEAL LADDER (apply_heal_ladder, from get_class_abilities): within a class, the medium-cast single-target
   direct heal with the most ranks is the ANCHOR (Priest Heal; a class with no medium heal anchors on its main heal
   - Shaman Healing Wave, Paladin Holy Light). Every other single-target direct heal at another speed is priced off the anchor's rank at the same
   level, by its size and a healing-per-mana share for its speed:
        cost = anchor cost x (its heal / the anchor's heal) / HPM[speed]
   A short heal at 0.6 of the anchor's efficiency heals about 60% of it for about the same mana; a long one is
   slightly less efficient than the anchor. Heals on a cooldown longer than a turn, party heals and HoTs are left to
   the table: they are their own decisions.
"""

HEAL_TIGHTEN = 1.25
DAMAGE_TIGHTEN = 1.15

#: healing per mana against the anchor, by cast speed (combat/abilities.CAST_SPEEDS)
HPM = {0.25: 0.55, 0.5: 0.6, 0.75: 1.0, 1.0: 0.95}
ANCHOR_SPEED = 0.75


def tighten(effect_type):
    return HEAL_TIGHTEN if effect_type in ("heal", "hot", "damage_and_heal") else DAMAGE_TIGHTEN


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
    if len(heals) < 2:
        return
    anchors = [a for a in heals if _speed_key(getattr(a, "cast_speed", ANCHOR_SPEED)) == ANCHOR_SPEED] or heals
    anchor = max(anchors, key=lambda a: (len(a.ranks), a.ranks[-1].get("level_req", 1)))
    aranks = sorted(anchor.ranks, key=lambda r: r.get("level_req", 1))
    a_hpm = HPM[_speed_key(getattr(anchor, "cast_speed", ANCHOR_SPEED))]
    for a in heals:
        if a is anchor:
            continue
        hpm = HPM[_speed_key(getattr(a, "cast_speed", ANCHOR_SPEED))] / a_hpm
        for r in a.ranks:
            lv = r.get("level_req", 1)
            ref = next((x for x in reversed(aranks) if x.get("level_req", 1) <= lv), aranks[0])
            if not ref.get("effect_value") or not r.get("effect_value"):
                continue
            r["cost"] = max(1, int(round(ref["cost"] * (r["effect_value"] / ref["effect_value"]) / hpm)))
