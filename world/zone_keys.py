"""The one zone-key normalisation, shared.

WHY THIS FILE EXISTS. Six managers keyed data by zone and each one wrote its own normaliser:

    ambient_npc_manager   lower, spaces -> _
    vendor_manager        lower, spaces -> _, strip '
    forge_manager         lower, spaces -> _, strip '
    gathering_manager     lower, spaces -> _, strip '
    recruit_manager       lower, spaces -> _, strip '
    zone_manager          lower, spaces -> _, strip ', strip a leading "the_"

Three different answers to the same question, and every one of their docstrings claimed to match the
others. The disagreement is invisible until a zone's DISPLAY NAME and its DATA KEY differ by exactly
the character a given manager forgets about, and then that zone's entire roster goes quiet - no crash,
no warning, just an NPC you walk up to and nothing happens.

Found 29 Oct 2026, by auditing which towns had an inn:

    Grom'gol          "Grom'gol" -> grom'gol  vs roster gromgol          20 ambient NPCs unreachable
    Kael's Bastion    "Kael's Bastion" -> kael's_bastion vs kaels_bastion  17 unreachable
    The Sepulcher     "The Sepulcher" -> the_sepulcher vs sepulcher      22 ambient AND its vendors

Kael's Bastion is a faction capital with a Codex Master in it. The Sepulcher is a Silverpine hub. Both
had been shipping with invisible rosters.

THE RULE, and why each part of it is safe: lowercase, spaces to underscores, drop apostrophes, and drop
a leading "the_". The article never distinguishes two zones, and the apostrophe is a spelling of the
display name rather than part of the identity. Stripping is only safe when BOTH SIDES of a lookup go
through the same function - index and query - which is the actual invariant this file exists to hold.
A manager that indexes raw JSON keys and queries through a normaliser is the bug, not the normaliser;
GatheringNodeManager was doing exactly that and now normalises its keys at load.
"""


def zone_key(zone):
    """Normalise a zone display name or slug to the one canonical key.

    "Valley of Trials" / "valley_of_trials" -> valley_of_trials
    "Grom'gol"                              -> gromgol
    "The Sepulcher" / "sepulcher"           -> sepulcher
    """
    key = zone_slug(zone)
    return key[4:] if key.startswith("the_") else key


def zone_slug(zone):
    """The same key WITHOUT dropping a leading "the_".

    TWO CONVENTIONS EXIST AND THEY DISAGREE ON EVERY "The ..." ZONE. This
    is not a second normaliser of the kind the module docstring is about -
    it is the other half of the one above, pulled into this file so the
    disagreement is written down in one place instead of living as a
    duplicated .replace() chain at each call site.

    The quest system keys explore objectives on the UNSTRIPPED slug:
    QuestManager.record_zone_entered and record_position_reached compare
    objective.target to what world/zone_manager.py passes them, and the
    authored data says `the_crystalline_underdark`, `the_frostward_descent`,
    `the_hollow_geode`, `the_deep_bloom`. The managers (vendors, gathering,
    recruits, ambient NPCs) key on the STRIPPED one.

    Both halves work, because each side is internally consistent - index
    and query go through the same rule, which is the invariant this module
    exists to hold. What was wrong was the comment at zone_manager.py:554
    claiming the raw chain there was "same slug normalization every other
    zone-keyed lookup uses (VendorManager._zone_key, ...)". It is not: for
    any zone beginning with "The" the two differ by exactly four
    characters, and anyone who "unified" them on the strength of that
    comment would have silently broken ten Underdark explore objectives.
    Use zone_slug for anything the quest system compares, zone_key for
    anything a manager indexes, and never the raw chain.
    """
    return str(zone).strip().lower().replace(" ", "_").replace("'", "").replace("’", "")
