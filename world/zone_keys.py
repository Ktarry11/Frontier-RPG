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
    key = str(zone).strip().lower().replace(" ", "_").replace("'", "").replace("’", "")
    return key[4:] if key.startswith("the_") else key
