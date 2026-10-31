#!/usr/bin/env python3
"""Make every ability description state what the ability DOES.

Kyle has asked for this more than once: "a lot of the skills dont need these odd
AI flavor texts. theyre strange. all skills and spells should simply say WHAT
they do." And again, 2026-10-31: "Did you fix the weird written talents and
skills for the coa classes? ... Fix it fully."

MEASURED FIRST, because I had previously reported this as handled: 694 of 1274
ability descriptions state no mechanic at all. The barbarian kit is entirely
flavour - "Thick Skull: Your skull has been described, more than once, as a
structural feature", "Decapitate: Finish it. There is no second swing in this
one." The tooltip's mechanical lines sit above it and read fine; the last line
is the one Kyle keeps seeing.

AN EARLIER ATTEMPT AT THIS DELETED 683 DESCRIPTIONS AND WAS REVERTED, because it
threw away good ones too - including "Hurls a bolt of lightning at the target",
the exact wording from a tooltip Kyle had screenshotted approvingly. So:

  - a description that ALREADY names a mechanic is left completely alone
  - the rest are REPLACED, never emptied, with a sentence built from the
    ability's own fields (effect_type, target, school, duration, stat_mods,
    is_stun, is_aoe, absorb, execute_threshold, requires_form, generates)

Nothing is invented. If the data does not say it, the sentence does not claim
it, which is the whole reason this is generated rather than written by hand 694
times.
"""
import sys, os, json, glob, re, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from combat.abilities import _ability_from_data

#: A description is already fine if it names any mechanic. Deliberately broad -
#: the cost of keeping a so-so description is nil, the cost of destroying a good
#: one is what got the last attempt reverted.
MECH = re.compile(
    r'\d|%|chance|increase|reduce|decreas|damage|heal|threat|cooldown|mana|rage|energy'
    r'|stack|duration|turn|range|crit|armou?r|resist|generat|absor|speed|haste|taunt'
    r'|interrupt|stun|slow|silence|summon|revive|shield|cleanse|dispel|snare|root'
    r'|charge|combo|rune|power|restore|immune|form|bleed|poison|curse|aura|totem',
    re.I)

#: Descriptions whose flavour wording happens to contain a word the MECH guard
#: treats as mechanical ("bleed", "curse", "form"), so the broad guard protected
#: them when it should not have. Named explicitly rather than by narrowing the
#: guard, because narrowing it risks destroying real descriptions - which is
#: exactly what got the first attempt at this reverted.
FORCE = {
    "Warband", "Shadow Hemorrhage", "Blood Curse", "Hemal Excision", "Spear Throw",
    "Venom Bolt", "Wilt", "Hex of Malice", "Hexbreak", "Hexfire", "Witchblood Tonic",
}

WHO = {"self": "you", "ally": "an ally", "party": "your party",
       "enemy": "the target", "enemy_aoe": "all nearby enemies"}


def _who(a):
    if a.max_targets:
        return f"up to {a.max_targets} targets"
    if a.is_aoe and a.target_type not in ("party", "enemy_aoe"):
        return "all nearby enemies"
    return WHO.get(a.target_type, "the target")


def _names(v):
    """A school or dispel type may be a single string OR a list of them. Printing
    the list raw gave "Deals ['Shadow', 'Fire'] damage to the target"."""
    if v is None:
        return ""
    if isinstance(v, (list, tuple, set)):
        parts = [str(x).title() for x in v if x]
        return "/".join(parts)
    return str(v).title()


def _school(a):
    s = _names(getattr(a, "damage_school", None))
    if not s or s.lower() in ("physical", "none", ""):
        return ""
    return f" {s}"


def _turns(a):
    if not a.duration:
        return ""
    return f" for {a.duration} turn{'s' if a.duration != 1 else ''}"


#: Internal flags that _stat_mod_text renders as "Taunt +1". A player does not
#: act on "+1", they act on "taunts".
FLAG_WORDS = {"taunt": "Taunts the target", "cc_immune": "Immune to crowd control",
              "silenced": "Silences", "rooted": "Roots", "stealth": "Stealths you"}

#: A few keys whose auto-derived label is accurate but reads like a field name.
NICER = {"threat_generation_pct": "Threat generated",
         "stun_duration_reduction_pct": "Stun duration",
         "pushback_reduction_pct": "Casting pushback",
         "crit_chance_physical": "Physical crit chance",
         "crit_chance_spell": "Spell crit chance",
         "all_stats_pct": "All stats"}


def _mods(a):
    if not a.stat_mods:
        return ""
    from combat.abilities import Ability
    bits = []
    for k, v in a.stat_mods.items():
        if k in FLAG_WORDS:
            bits.append(FLAG_WORDS[k])
            continue
        text = Ability._stat_mod_text(k, v)
        if k in NICER:
            text = NICER[k] + text[len(k.replace("_", " ").title()):]
        bits.append(text)
    return ", ".join(bits)


def describe(a):
    """One plain sentence, built only from fields this ability actually carries."""
    et = a.effect_type
    who, school, turns = _who(a), _school(a), _turns(a)
    extra = []

    if a.requires_form:
        extra.append(f"Requires {str(a.requires_form).replace('_', ' ').title()} Form")
    if a.requires_ranged_weapon:
        extra.append("Requires a ranged weapon")
    if a.execute_threshold_pct:
        extra.append(f"Usable only below {a.execute_threshold_pct}% health")
    if a.generates:
        # {"resource": "insanity", "amount": 20} - joining it as an iterable gave
        # the KEYS, so the first run produced "Generates resource, amount."
        g = a.generates
        if isinstance(g, dict):
            res = str(g.get("resource", "")).replace("_", " ").title()
            amt = g.get("amount")
            if res:
                extra.append(f"Generates {amt} {res}" if amt else f"Generates {res}")
        elif isinstance(g, str):
            extra.append(f"Generates {g.replace('_', ' ').title()}")

    if et in ("damage", "spell_damage", "ranged_damage"):
        core = f"Deals{school} damage to {who}"
        if a.is_stun:
            core += f" and stuns {'them' if who != 'the target' else 'it'}{turns}"
        elif turns and a.applies_dot_pct:
            core += f", then damage over time{turns}"
    elif et in ("dot", "spell_dot"):
        core = f"Deals{school} damage to {who} over time{turns}"
    elif et in ("heal",):
        core = f"Heals {who}"
    elif et in ("hot",):
        core = f"Heals {who} over time{turns}"
    elif et == "damage_and_heal":
        core = f"Deals{school} damage to {who} and heals you for part of it"
    elif et == "damage_and_restore_mana":
        core = f"Deals{school} damage to {who} and restores some of your mana"
    elif et == "buff":
        m = _mods(a)
        core = (f"{m}{turns}" if m else f"Strengthens {who}{turns}")
        if m and a.target_type != "self":
            core = f"Grants {who}: {m}{turns}"
    elif et == "debuff":
        m = _mods(a)
        if a.is_stun:
            core = f"Interrupts and stuns {who}{turns}"
        elif m:
            core = f"Applies to {who}: {m}{turns}"
        else:
            core = f"Weakens {who}{turns}"
    elif et == "dispel":
        n = a.dispel_count or 1
        k = _names(a.dispel_type)
        kind = f" {k.lower()}" if k else ""
        core = f"Removes {n}{kind} effect{'s' if n != 1 else ''} from {who}"
    elif et == "revive":
        core = "Revives a fallen ally"
    elif et == "summon_pet":
        core = "Summons a pet to fight for you"
    elif et == "restore_resource":
        r = getattr(a, "restore_resource_type", None)
        core = f"Restores {str(r).replace('_',' ') if r else 'resource'} to {who}"
    elif et == "shapeshift":
        core = "Changes your form"
    elif et == "reset_cooldowns":
        core = "Resets your ability cooldowns"
    elif et == "enable_instant_cast":
        core = "Makes your next cast instant"
    elif et == "totem_loadout":
        core = "Sets out your totems"
    else:
        core = f"Affects {who}{turns}"

    if a.absorb or a.absorb_pct_max_health:
        core += f", absorbing damage{turns if not turns else ''}"

    out = core.rstrip(".")
    if extra:
        out += ". " + ". ".join(extra)
    return out + "."


def main():
    write = "--write" in sys.argv
    changed, kept, rows = 0, 0, []

    for path in sorted(glob.glob("data/abilities/*.json")):
        doc = json.load(open(path))
        entries = doc.get("abilities")
        iterable = entries if isinstance(entries, list) else list(entries.values())
        dirty = False
        for entry in iterable:
            if not isinstance(entry, dict) or "name" not in entry:
                continue
            old = entry.get("description", "") or ""
            if MECH.search(old) and entry["name"] not in FORCE:
                kept += 1
                continue
            try:
                a = _ability_from_data(entry)
            except Exception:
                kept += 1
                continue
            new = describe(a)
            if new and new != old:
                rows.append((os.path.basename(path), entry["name"], old, new))
                entry["description"] = new
                changed += 1
                dirty = True
        if dirty and write:
            json.dump(doc, open(path, "w"), indent=2)

    print(f"  {kept} descriptions already stated a mechanic and were LEFT ALONE")
    print(f"  {changed} rewritten{' (written)' if write else ' (dry run - pass --write)'}\n")
    for f, n, old, new in rows[:25]:
        print(f"  [{f}] {n}")
        print(f"      was: {old[:96]}")
        print(f"      now: {new[:96]}")
    if len(rows) > 25:
        print(f"  ... and {len(rows)-25} more")
    return 0


if __name__ == "__main__":
    sys.exit(main())
