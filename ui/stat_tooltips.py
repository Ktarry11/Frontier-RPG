"""What every stat on the character sheet does for this character, WoW style, on hover.

Kyle, 16 Nov 2026: "spellpower by school is weird.... lets do it wow style where you HOVER OVER the spell power and it
breaks it down by school", then: "we should be able to hover over ALL stats and see what they offer? Crit? mana?
HP....etc".

THE NUMBERS ARE MEASURED, NOT RESTATED. A tooltip that hard-codes "1 Stamina = 8 health" is right until the formula
moves and then lies forever. Instead `gives()` takes the stat away (the same bonus pool gear uses, so talents, set
bonuses and buffs all come through it as they do in play), recalculates, and reads what changed: "Your 140 Stamina
gives +1,120 health" is the difference the 140 actually makes. The character is put back exactly as it was.
"""
import contextlib

#: what the sheet calls each derived number, and how to print it
DERIVED = [
    ("health", "health", False), ("mana", "mana", False), ("attack_power", "Attack Power", False),
    ("ranged_attack_power", "Ranged Attack Power", False), ("spell_power", "Spell Power", False),
    ("healing_power", "Healing Power", False), ("crit_chance_physical", "physical crit", True),
    ("crit_chance_spell", "spell crit", True), ("dodge", "Dodge", True), ("parry", "Parry", True),
    ("block_chance", "Block chance", True), ("block_value", "Block value", False), ("armor", "Armor", False),
    ("haste", "Haste", True),
]
SCHOOLS = (("Arcane", "arcane"), ("Fire", "fire"), ("Frost", "frost"), ("Nature", "nature"),
           ("Shadow", "shadow"), ("Holy", "holy"))


def _snapshot(m):
    out = {k: float(getattr(m, k, 0) or 0) for k, _l, _p in DERIVED}
    with contextlib.suppress(Exception):
        out["mana_per_turn"] = float(m.mana_per_turn())
    with contextlib.suppress(Exception):
        out["hp5"] = float(m.hp5_total())
    return out


def gives(member, stat, amount=None):
    """{derived key: change} that `amount` of `stat` makes (default: all the member has of it)."""
    eq = getattr(member, "equipment", None)
    if eq is None or not hasattr(member, "_recalculate_derived_stats"):
        return {}
    if amount is None:
        amount = float(getattr(member, f"effective_{stat}", getattr(member, stat, 0)) or 0)
    if not amount:
        return {}
    keep = (getattr(member, "current_health", None), getattr(member, "current_mana", None))
    real = eq.get_total_stat_bonuses
    before = _snapshot(member)
    try:
        def less():
            b = dict(real())
            b[stat] = b.get(stat, 0) - amount
            return b
        eq.get_total_stat_bonuses = less
        member._recalculate_derived_stats()
        after = _snapshot(member)
    finally:
        eq.get_total_stat_bonuses = real
        member._recalculate_derived_stats()
        if keep[0] is not None:
            member.current_health = keep[0]
        if keep[1] is not None:
            member.current_mana = keep[1]
    return {k: before[k] - after[k] for k in before if abs(before[k] - after[k]) > 1e-6}


def _fmt(v, pct):
    if pct:
        return f"+{round(v * 100) / 100:g}%"
    return f"+{int(round(v)):,}"


def _gives_lines(member, stat, label):
    amount = float(getattr(member, f"effective_{stat}", getattr(member, stat, 0)) or 0)
    d = gives(member, stat, amount)
    names = {k: (lbl, pct) for k, lbl, pct in DERIVED}
    names["mana_per_turn"] = ("mana per turn", False)
    names["hp5"] = ("health per turn", False)
    lines = [(f"{label} {int(round(amount))}", "title")]
    if not d:
        lines.append((f"Your {label} adds nothing a {getattr(member, 'char_class', 'class')} uses.", "dim"))
        return lines
    lines.append((f"Your {int(round(amount))} {label} gives:", "body"))
    for k, _l, _p in DERIVED + [("mana_per_turn", "", False), ("hp5", "", False)]:
        if k in d and d[k] > 0:
            lbl, pct = names[k]
            lines.append((f"  {_fmt(d[k], pct)} {lbl}", "good"))
    return lines


def _school_lines(member):
    base = float(getattr(member, "spell_power", 0) or 0)
    heal = float(getattr(member, "healing_power", 0) or 0)
    lines = [(f"Spell Power {int(round(base))}", "title"),
             ("Adds to the damage of your spells. Some gear adds more to one school:", "body")]
    for name, key in SCHOOLS:
        extra = float(getattr(member, f"{key}_spell_power", 0) or 0)
        total = base + extra
        tail = f"  ({int(round(base))} + {int(round(extra))} {name})" if extra else ""
        lines.append((f"  {name}: {int(round(total))}{tail}", "good" if extra else "body"))
    lines.append((f"  Healing: {int(round(heal))}", "body"))
    return lines


def _pct(member, key):
    return float(getattr(member, key, 0) or 0)


def stat_tooltip(member, stat_id):
    """[(text, kind)] for one row of the sheet; kind is title / body / good / dim."""
    if stat_id in ("strength", "agility", "stamina", "intellect", "spirit"):
        label = stat_id.title()
        lines = _gives_lines(member, stat_id, label)
        return lines
    if stat_id == "spell_power":
        return _school_lines(member)
    if stat_id == "healing_power":
        return [(f"Healing Power {int(round(_pct(member, 'healing_power')))}", "title"),
                ("Adds to every heal and heal over time you cast.", "body")]
    if stat_id in ("attack_power", "ranged_attack_power"):
        name = "Attack Power" if stat_id == "attack_power" else "Ranged Attack Power"
        total = _pct(member, stat_id)
        lines = [(f"{name} {int(round(total))}", "title"),
                 ("Adds to the damage of your weapon attacks and the abilities that use them." if stat_id ==
                  "attack_power" else "Adds to the damage of your bows, guns, crossbows and thrown weapons.", "body")]
        parts = []
        for st in ("strength", "agility"):
            amt = gives(member, st).get(stat_id, 0)
            if amt > 0:
                parts.append((f"  {int(round(amt)):,} from {st.title()}", "body"))
        if parts:
            lines += parts
            rest = total - sum(gives(member, st).get(stat_id, 0) for st in ("strength", "agility"))
            if rest > 0.5:
                lines.append((f"  {int(round(rest)):,} from gear, talents and buffs", "body"))
        return lines
    if stat_id in ("crit_chance_physical", "crit_chance_spell"):
        kind = "physical" if stat_id.endswith("physical") else "spell"
        total = _pct(member, stat_id)
        src = "agility" if kind == "physical" else "intellect"
        from_stat = gives(member, src).get(stat_id, 0)
        lines = [(f"{'Physical' if kind == 'physical' else 'Spell'} crit {round(total * 100) / 100:g}%", "title"),
                 ("The chance your weapon attacks land a critical strike for extra damage." if kind == "physical"
                  else "The chance your spells land a critical strike: extra damage, and extra healing on a heal.",
                  "body")]
        if from_stat > 0:
            lines.append((f"  {round(from_stat * 100) / 100:g}% from {src.title()}", "body"))
            lines.append((f"  {round((total - from_stat) * 100) / 100:g}% base, gear, talents and buffs", "body"))
        return lines
    if stat_id == "haste":
        return [(f"Haste {round(_pct(member, 'haste') * 100) / 100:g}%", "title"),
                ("Your turns come around sooner: the higher it is, the more often you act.", "body")]
    if stat_id == "armor":
        lines = [(f"Armor {int(round(_pct(member, 'armor'))):,}", "title")]
        with contextlib.suppress(Exception):
            lines.append((f"Reduces physical damage taken by {member.get_physical_reduction_percent():.1f}% from an "
                          f"attacker of your level.", "body"))
        from_agi = gives(member, "agility").get("armor", 0)
        if from_agi > 0:
            lines.append((f"  {int(round(from_agi)):,} from Agility", "body"))
        return lines
    if stat_id in ("dodge", "parry", "block_chance"):
        name = {"dodge": "Dodge", "parry": "Parry", "block_chance": "Block chance"}[stat_id]
        what = {"dodge": "The chance to step aside from a physical attack and take nothing.",
                "parry": "The chance to turn a melee attack aside with your weapon and take nothing.",
                "block_chance": "The chance to catch a physical attack on your shield, taking your block value "
                                "less."}[stat_id]
        lines = [(f"{name} {round(_pct(member, stat_id) * 100) / 100:g}%", "title"), (what, "body")]
        from_agi = gives(member, "agility").get(stat_id, 0)
        if from_agi > 0:
            lines.append((f"  {round(from_agi * 100) / 100:g}% from Agility", "body"))
        return lines
    if stat_id == "block_value":
        return [(f"Block value {int(round(_pct(member, 'block_value')))}", "title"),
                ("How much damage a blocked attack loses.", "body")]
    if stat_id in ("mana_per_turn", "mana_per_turn_casting"):
        lines = [("Mana per turn", "title"),
                 ("Mana that comes back every turn. Spirit's share is smaller while you're casting; mp5 isn't.",
                  "body")]
        with contextlib.suppress(Exception):
            lines.append((f"  {int(round(member.mana_per_turn()))} a turn when you're not casting", "body"))
            lines.append((f"  {int(round(member.mana_per_turn(casting=True)))} a turn while casting", "body"))
        sp = gives(member, "spirit").get("mana_per_turn", 0)
        with contextlib.suppress(Exception):
            sp = min(sp, member.mana_per_turn())
        if sp > 0:
            lines.append((f"  {int(round(sp))} of it from Spirit", "good"))
        return lines
    if stat_id == "hp5":
        return [("Health per turn", "title"), ("Health that comes back every turn, in a fight or out of one.",
                                               "body")]
    if stat_id == "spell_penetration":
        return [(f"Spell penetration {int(round(_pct(member, 'spell_penetration')))}", "title"),
                ("Ignores that much of a target's resistance to your spells.", "body")]
    if stat_id.startswith("resist_"):
        school = stat_id[7:]
        lines = [(f"{school.title()} resistance", "title")]
        with contextlib.suppress(Exception):
            lines.append((f"Reduces {school} damage taken by {member.get_resistance_percent(school):.1f}% from an "
                          f"attacker of your level.", "body"))
        return lines
    return []
