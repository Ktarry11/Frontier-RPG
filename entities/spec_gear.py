"""Per-spec gear profiles: what a spec's gear should actually be.

Reads data/items/spec_gear.json, which tools/build_spec_gear.py derives
from the talent trees, the ability schools and the proficiency tables.
That file is generated, so fix a wrong profile by fixing the tool or the
data it reads - not by hand-editing the JSON, which the next --check run
will flag as stale.

WHY A SPEC LAYER AT ALL. Gear was itemized by CLASS, which is right for
armour (a Shaman wears mail in every spec) and wrong for everything else:
one stat template per class made an Enhancement Shaman a caster and a Holy
Paladin a Strength hybrid, and one shared set of all six
<school>_spell_power stats let a Fire Mage roll +Holy spell power.

The profile answers four questions a class cannot:

    role            tank / healer / melee_dps / ranged_dps
    stat_template   which of stat_templates.json's six to itemize as
    school          the only school whose spell power may roll
    weapons         main_hand / off_hand / ranged, by weapon type
"""
import json
from pathlib import Path

_PATH = Path(__file__).resolve().parent.parent / "data/items/spec_gear.json"
_CACHE = None

#: What a recruit with no spec at all falls back to. Only one does - Asher
#: Coleman, whose gear_theme is null and whose kit is hash-locked and built
#: by hand anyway, so this never actually fires for him either.
_DEFAULT = {
    "role": "melee_dps",
    "stat_template": None,
    "armor_type": None,
    "school": None,
    "dual_wield": False,
    "weapons": {"main_hand": None, "off_hand": None, "ranged": None},
}


def _load():
    global _CACHE
    if _CACHE is None:
        try:
            _CACHE = json.loads(_PATH.read_text())
        except Exception:
            # Fails soft to an empty table: gear then falls back to the
            # class-level itemization it used before this existed, which is
            # worse but not broken. A missing data file should not stop a
            # companion being recruitable.
            _CACHE = {}
    return _CACHE


def profile(spec):
    """The gear profile for `spec`, or the fallback if it has none."""
    if not spec:
        return dict(_DEFAULT)
    return _load().get(spec) or dict(_DEFAULT)


def all_specs():
    return dict(_load())


def weapon_for(spec, slot):
    """The weapon type this spec wants in `slot`, or None."""
    return profile(spec).get("weapons", {}).get(slot)
