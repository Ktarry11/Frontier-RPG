"""Zone level bands, for the overworld banner.

    from world.zone_levels import banner
    banner("Valley of Trials")     -> "~ Valley of Trials - Level 1-6 ~"

The data is DERIVED, not hand-written: tools/build_zone_levels.py reads the band off the creatures
that actually spawn in each zone, so the label cannot drift from what the player meets. Re-run that
tool after any encounter-table change; do not edit the json.

A missing band is not an error. The banner falls back to the plain zone name, which is what it
showed before this existed - a new zone should look unfinished rather than broken while its
encounter table is still being written.
"""
import json
import os

_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "data", "zones", "zone_levels.json")
_BANDS = None


def _load():
    global _BANDS
    if _BANDS is None:
        try:
            with open(_PATH, encoding="utf-8") as fh:
                _BANDS = {k: tuple(v) for k, v in json.load(fh).get("zones", {}).items()}
        except (OSError, ValueError):
            # The label is cosmetic. A missing or malformed file must not stop the game drawing
            # the overworld, so this degrades to "no bands known" rather than raising.
            _BANDS = {}
    return _BANDS


def band(zone_name):
    """(level_min, level_max) for a zone, or None if it has no band."""
    return _load().get(zone_name)


def level_text(zone_name):
    """"Level 1-6", or "Level 60" where a zone is a single level, or None."""
    b = band(zone_name)
    if not b:
        return None
    lo, hi = b
    return f"Level {lo}" if lo == hi else f"Level {lo}-{hi}"


def banner(zone_name):
    """The overworld banner string, with the band if there is one."""
    lv = level_text(zone_name)
    return f"~ {zone_name} - {lv} ~" if lv else f"~ {zone_name} ~"
