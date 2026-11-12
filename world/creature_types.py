"""What KIND of creature something is, in WoW's terms - the thing crowd control cares about.

Kyle, 10 Nov: "why can i BANISH a naga?" Because nothing in the game knew a naga was not a
demon. A creature had a stat TEMPLATE (humanoid_caster, beast_fast, elemental_bruiser...) chosen
for how it fights, and no type at all, so every crowd-control spell worked on everything.

Resolution, first match wins:
    1. an explicit "creature_type" on the creature's entry in data/creatures/creatures.json
    2. its name (a Naga Siren on the aquatic template is a humanoid; a Whelp on a beast
       template is dragonkin)
    3. its stat template's family
"""
import re

BEAST, HUMANOID, UNDEAD, ELEMENTAL, DEMON = "beast", "humanoid", "undead", "elemental", "demon"
DRAGONKIN, GIANT, MECHANICAL, CRITTER, ABERRATION = "dragonkin", "giant", "mechanical", "critter", "aberration"

ALL = (BEAST, HUMANOID, UNDEAD, ELEMENTAL, DEMON, DRAGONKIN, GIANT, MECHANICAL, CRITTER, ABERRATION)

PLURAL = {
    BEAST: "Beasts", HUMANOID: "Humanoids", UNDEAD: "Undead", ELEMENTAL: "Elementals",
    DEMON: "Demons", DRAGONKIN: "Dragonkin", GIANT: "Giants", MECHANICAL: "Mechanicals",
    CRITTER: "Critters", ABERRATION: "Aberrations",
}

#: Stat-template family -> type, when the name says nothing.
_TEMPLATE_FAMILY = {
    "humanoid": HUMANOID, "beast": BEAST, "undead": UNDEAD, "elemental": ELEMENTAL,
    "demon": DEMON, "vermin": BEAST, "aquatic": BEAST,
}

#: Name rules, first match wins. NOUNS ONLY - what the creature is, never an adjective about
#: it. The first draft matched "thorn", "ancient", "bone", "giant" and "guard", and so called a
#: Thornhide Boar an elemental, a Giant Spider a giant and a Silithid Guardian a humanoid.
#: Anything a noun does not settle falls to the stat template's family, which is right for the
#: plain cases (a boar on a beast template, a Molten Elemental on an elemental one).
_NAME_RULES = [
    (BEAST, r"hydra"),
    (MECHANICAL, r"golem|shredder|harvester|automaton|construct|clockwork|sentry bot|turret|cannon"),
    (UNDEAD, r"skeleton\w*|skeletal|ghoul\w*|zombie\w*|ghost\w*|wraith\w*|banshee\w*|lich|"
             r"abomination\w*|spectre|specter|spectral|phantom\w*|shade|revenant|geist|wight|"
             r"forsaken|scourge|mummy|death knight|mourning spirit|rotting|"
             r"the drowned|drowned \w+"),
    (DEMON, r"imp|felhound|felguard|felstalker|fel pup|succubus|voidwalker|satyr|doomguard|"
            r"infernal|demon\w*|dreadlord|pit lord|void handmaiden"),
    (DRAGONKIN, r"dragon|dragonspawn|whelp|whelpling|drake|wyrm|wyrmkin|drakonid"),
    (ELEMENTAL, r"elemental|ooze|slime|treant|lasher|wisp|dust devil|bog beast"),
    (GIANT, r"sea giant|mountain giant|giant$|ettin|colossus|titan|gronn"),
    # Races that are people whatever stat block they were given (a Murloc on the aquatic
    # template, a Harpy on a beast one). Job words - guard, captain, mage - are deliberately
    # absent: they describe undead and demons just as often.
    (HUMANOID, r"naga|siren|myrmidon|murloc|kobold|gnoll|troll|ogre|harpy|furbolg|worgen|centaur|quilboar|yeti"),
]
_NAME_RULES = [(t, re.compile(r"\b(?:" + pat + r")\b", re.I)) for t, pat in _NAME_RULES]

_overrides = None


def _load_overrides():
    global _overrides
    if _overrides is None:
        import json
        from pathlib import Path
        _overrides = {}
        try:
            path = Path(__file__).resolve().parent.parent / "data" / "creatures" / "creatures.json"
            data = json.loads(path.read_text()).get("creatures", {})
            for name, entry in data.items():
                if isinstance(entry, dict) and entry.get("creature_type"):
                    _overrides[name] = entry["creature_type"]
        except (OSError, ValueError):
            pass
    return _overrides


def classify(name, template=""):
    """The creature type for a creature called `name` on stat template `template`."""
    explicit = _load_overrides().get(name)
    if explicit:
        return explicit
    for ctype, rx in _NAME_RULES:
        if rx.search(name or ""):
            return ctype
    family = (template or "").split("_")[0]
    return _TEMPLATE_FAMILY.get(family, BEAST)


def creature_type_of(combatant):
    """Type of anything that can be targeted. Player characters and recruits are humanoid;
    a summoned pet says what it is, or is classified like a monster."""
    explicit = getattr(combatant, "creature_type", None)
    if explicit:
        return explicit
    if not getattr(combatant, "is_monster", False):
        return HUMANOID
    return classify(getattr(combatant, "name", ""), getattr(combatant, "monster_type", ""))


# ---------------------------------------------------------------------------------------------
# Which crowd control works on what.
#
# One table, filled as abilities load (an ability's "creature_types" / "immune_creature_types"
# in its JSON), and asked in two places: Ability.use, which refuses a single-target cast up
# front so it costs nothing, and StatusEffectMixin.apply_status_effect, which is where an
# area effect, a proc or anything else that reaches a target some other way gets stopped.
# ---------------------------------------------------------------------------------------------
CC_RULES = {}


def register_rule(ability_id, only=None, never=None):
    if only or never:
        CC_RULES[ability_id] = (tuple(only or ()), tuple(never or ()))


def _join(types, word):
    names = [PLURAL.get(t, t.title()) for t in types]
    if len(names) <= 1:
        return "".join(names)
    return ", ".join(names[:-1]) + f" {word} " + names[-1]


def rule_text(ability_id):
    """The tooltip line: 'Only works on Demons and Elementals.' Empty when there is no rule."""
    only, never = CC_RULES.get(ability_id, ((), ()))
    if only:
        return f"Only works on {_join(only, 'and')}."
    if never:
        return f"Does not work on {_join(never, 'or')}."
    return ""


def blocked_reason(ability_id, ability_name, target):
    """Why this crowd control cannot land on `target`, or None if it can."""
    rule = CC_RULES.get(ability_id)
    if not rule or target is None:
        return None
    only, never = rule
    ctype = creature_type_of(target)
    label = ctype.title() if ctype != UNDEAD else "Undead"
    article = "an" if label[0] in "AEIOU" else "a"
    if (only and ctype not in only) or (never and ctype in never):
        return f"{ability_name} does not work on {target.name} - it is {article} {label}."
    # A boss shrugs off the kind of control that takes a creature out of the fight by what it
    # IS. A plain stun still lands on a boss exactly as it did before.
    if getattr(target, "is_boss", False):
        return f"{target.name} is too powerful for {ability_name}."
    return None
