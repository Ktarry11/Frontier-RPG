"""EVERY FORM AND STANCE IS A BUFF YOU CAN SEE (Kyle, 27 Nov 2026).

    "Whenever ANY character enters a shapeshifted or alternate form, it must appear as a buff under their party
    buffs. This applies to ALL classes. Includes Shadow Form and other non-traditional shapeshifting abilities.
    Includes tank forms and Bloodmage forms. The buff should indicate which form is currently active. Players
    should be able to inspect the buff and see its effects."

A form, a tank stance, Earthen Guardian and a Warrior stance are not status effects - they live on the character
(current_form, tank_stance, guardian_stance_active, current_stance) and fold their stats in through
get_talent_effects. So they never reached a buff list. posture_effects builds a stand-in BUFF for each one that is
active, named for it, carrying its stat_mods (so the effect tooltip lists what it does) and the casting ability's id
(so it shows that ability's icon). shown_effects is what every buff list draws: postures first, then the real buffs.
The stand-ins are made fresh each call and never applied, so nothing ticks, saves or dispels them.
"""

from combat.status_effects import StatusEffect, EffectType, StatusEffectMixin, is_displayable_buff

PERMANENT = StatusEffectMixin._PERMANENT_DURATION


def _ability_for(member, pred):
    book = getattr(member, "ability_book", None)
    if book is None:
        return None
    try:
        for a in book.get_all_abilities():
            if pred(a):
                return a.ability_id
    except Exception:                                           # noqa: BLE001
        return None
    return None


def _stand_in(effect_id, name, mods, note, kind="Form"):
    e = StatusEffect(effect_id=effect_id, name=name, effect_type=EffectType.BUFF, duration=PERMANENT,
                     stat_mods=dict(mods or {}), source_name="", real_time_seconds=None)
    e.is_posture = True
    e.posture_kind = kind
    e.posture_note = note
    return e


def posture_effects(member):
    """Stand-in buffs for every form or stance `member` is in right now."""
    out = []
    form = getattr(member, "current_form", None)
    if form:
        from combat.forms import get_form
        data = get_form(form) or {}
        aid = _ability_for(member, lambda a: getattr(a, "shapeshift_form_id", None) == form) or f"form_{form}"
        out.append(_stand_in(aid, data.get("name", form.replace("_", " ").title()), data.get("stat_mods"),
                             data.get("description", ""), "Form"))
    sid = getattr(member, "tank_stance", None)
    if sid:
        from combat.tank_stance import stance_by_id
        s = stance_by_id(sid) or {"name": sid}
        aid = _ability_for(member, lambda a: a.effect_type == "tank_stance") or f"stance_{sid}"
        out.append(_stand_in(aid, s.get("name", sid), s.get("stat_mods"), s.get("description", ""), "Stance"))
    if getattr(member, "guardian_stance_active", False):
        from combat.guardian_stance import get_guardian_stance
        g = get_guardian_stance()
        out.append(_stand_in("shaman_earthen_guardian", g["name"], g.get("stat_mods"), g.get("description", ""),
                             "Stance"))
    stance = getattr(member, "current_stance", None)
    if stance and getattr(member, "char_class", None) == "Warrior":
        from combat.stances import STANCES
        s = STANCES.get(stance) or {}
        out.append(_stand_in(f"warrior_{stance}_stance", s.get("name", stance.title() + " Stance"),
                             s.get("stat_mods"), s.get("description", ""), "Stance"))
    return out


def shown_effects(member, include_over_time=False):
    """What a buff list draws for this member: forms and stances first, then the displayable buffs (and DoTs/HoTs
    when the list shows them)."""
    try:
        live = [e for e in member._effects()
                if is_displayable_buff(e) or (include_over_time and e.effect_type in (EffectType.DOT, EffectType.HOT))]
    except Exception:                                           # noqa: BLE001
        live = []
    return posture_effects(member) + live


def form_tag(member):
    """A short label for a party member's open-world name ('Bear Form'), or None."""
    p = posture_effects(member)
    return p[0].name if p else None


FRACTION_WORDS = {"all_damage": "damage dealt", "healing_done": "healing done",
                  "physical_damage": "physical damage dealt"}
#: cost cuts, shown as a cut (a positive fraction means cheaper)
COST_WORDS = {"hot_cost_pct": "heal-over-time Mana cost", "heal_cost_pct": "healing Mana cost",
              "all_ability_cost_pct": "ability costs"}


def describe_mods(mods):
    """A form's or stance's stat_mods as card text: '+250% Armor', '-15% damage dealt'. The ability card and the
    buff tooltip both use this, so they say the same thing."""
    from combat.stat_text import stat_text
    out = []
    for k, v in (mods or {}).items():
        if not isinstance(v, (int, float)) or isinstance(v, bool) or not v:
            continue
        if k in FRACTION_WORDS:
            out.append(f"{v * 100:+.0f}% {FRACTION_WORDS[k]}")
            continue
        if k in COST_WORDS:
            out.append(f"{-v * 100:+.0f}% {COST_WORDS[k]}")
            continue
        try:
            out.append(stat_text(k, v, value_first=True))
        except Exception:                                       # noqa: BLE001
            pass
    return out
