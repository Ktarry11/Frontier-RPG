"""One way to spell a class name, for the four places that each invented their own.

A class is written two ways across this codebase and both reach lookup code:

    the id            sun_cleric, witch_hunter, knight_of_xoroth, necromancer
    the display name  Sun Cleric, Witch Hunter, Knight of Xoroth, Necromancer

Character.char_class holds the id. Several hand-written tables are keyed by the
display name. Every one of those lookups was doing its own normalising, or none,
and the ones that lowercased without collapsing the space failed on exactly the
four two-word classes - which is why they kept surfacing together:

    ui/class_portrait.py        Sun Cleric, Witch Doctor, Witch Hunter and
                                Knight of Xoroth recruits drew no class icon,
                                with the icon file sitting right there
    ui/spellbook_tree_map.py    data/spellbook_tabs_coa.json is keyed by display
                                name, so the lookup missed for ALL 21 CoA classes
                                and every single CoA ability fell through to the
                                Core tab
    combat/abilities.py         CLASS_RESOURCE_MAP missed for the same four, and
                                they silently defaulted to Mana - it printed a
                                warning nobody was reading
    ui/screens/skills_screen.py the spellbook tab label strips the class prefix
                                off a spec_name, by comparing against the id

class_key() is the single answer: lowercase, spaces and underscores collapsed.
lookup() applies it to both sides of a table so a table can stay keyed however
reads best.
"""


def class_key(name):
    """Canonical comparison key for a class name, in either spelling.

    "Sun Cleric", "sun_cleric", "SUN CLERIC" and "Sun  Cleric" all give
    "sun_cleric". Returns "" for a falsy name, so callers can test it.
    """
    if not name:
        return ""
    return "_".join(str(name).replace("_", " ").split()).lower()


def lookup(mapping, char_class, default=None):
    """mapping[char_class] regardless of which spelling either side used.

    Tries the literal key first so an exact hit costs nothing, then compares on
    class_key. The normalised index is rebuilt per call rather than cached,
    because these tables are small and a cache keyed on a mutable dict is a
    worse bug than the one it would save.
    """
    if char_class in mapping:
        return mapping[char_class]
    want = class_key(char_class)
    if not want:
        return default
    for key, value in mapping.items():
        if class_key(key) == want:
            return value
    return default


def strip_class_prefix(label, char_class):
    """"Sun Cleric Blessings" -> "Blessings", for a spellbook tab.

    Kyle, 2026-10-31: "why are trees for sun cleric named 'Cleric' x and witch
    hunter are 'hunter x' --- that'd be like 'Druid Feral' no...just feral"

    The old version compared the spec_name against char_class directly, so it
    worked for the one-word classes and left the two-word ones carrying half
    their class name. This eats whole words off the front for as long as they
    still form a prefix of the class key, so it is right for "Mage Fire",
    "Sun Cleric Blessings" and "Knight of Xoroth Hellfire" alike.

    Never returns an empty string: a spec literally named after its class keeps
    its name rather than becoming a blank tab.
    """
    want = class_key(char_class)
    if not want or not label:
        return label
    words = str(label).split()
    taken = 0
    for i in range(1, len(words)):
        if class_key(" ".join(words[:i])) == want:
            taken = i
    return " ".join(words[taken:]) if taken and words[taken:] else label
