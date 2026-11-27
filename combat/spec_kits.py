"""SPEC-LOCKED ABILITIES (Kyle, 27 Nov 2026).

    "A lot of them have their spells all over the place. Like there's no real split between coa specs....look at
    wind stormbringer learning lightning and maelstrom exclusive stuff etc."

In CoA every class has a shared Class list and one list per spec (the live client's CharacterAdvancementData tabs,
github.com/Bharph/coa-preservation-data). Here an ability whose data names `specs` is known only to a character in one
of them; an ability without it is the class's, for every spec.

WHAT "IN A SPEC" MEANS is unchanged (Kyle chose to keep it): entities/proficiency.active_spec - a recruit's locked spec,
else whichever tree holds the most talent points. Talent points start at level 10, so before then nobody has a spec;
a character with none keeps every spec's abilities learned below STARTER_LEVEL, so a level-5 Stormbringer still has
something to cast, and loses the ones outside its spec the moment it commits points.
"""

STARTER_LEVEL = 10


def allows(ability, spec):
    specs = getattr(ability, "specs", None)
    if not specs:
        return True
    if spec is None:
        try:
            return (ability.ranks[0].get("level_req", 1) or 1) < STARTER_LEVEL
        except Exception:                                       # noqa: BLE001
            return True
    return spec in specs


def apply(character):
    """Set spec_ok on every ability of `character`'s book for its current spec. Returns the spec."""
    try:
        from entities.proficiency import active_spec
        spec = active_spec(character)
    except Exception:                                           # noqa: BLE001
        spec = None
    book = getattr(character, "ability_book", None)
    if book is None:
        return spec
    for a in book.get_all_abilities():
        a.spec_ok = allows(a, spec)
    return spec
