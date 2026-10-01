"""
Boss portrait icons for the zone map screen (ui/screens/map_screen.py).

Kyle uploaded 8 real creature spritesheets (spritesheets.zip, 2026-09-06)
and asked for them to become "boss icons in Dungeons and caves" on the
map overview (M key) - boss_marker tiles previously rendered as nothing
at all on that screen (not even a colored dot, unlike portal/npc/chest/
quest_marker interaction tiles, which all have one).

95 boss creatures exist in data/creatures/creatures.json, keyed off 12
distinct "template" archetype tags (humanoid_caster, beast_large, etc -
see CreatureManager). Hand-picking a bespoke portrait per boss NAME
wasn't practical with only 8 source sprites for 95 bosses, and Kyle's
ask was to "match sprite vibe to each named boss" - so this maps at the
TEMPLATE level (the thing that actually encodes what kind of creature a
boss is) rather than either a full 95-entry hand list or flat
round-robin with no thematic logic. Where multiple templates would
otherwise share an identical portrait, one of them wears a hue-shifted
tint (see boss_icon_tint.py) of the same base sprite so the map doesn't
show two unrelated boss types as the exact same picture.
"""
from pathlib import Path

BOSS_ICON_DIR = Path(__file__).parent / "assets" / "icons" / "bosses"

#: template -> icon filename (no extension), see assets/icons/bosses/.
#: Every template in creatures.json is covered; TEMPLATE_ICON's fallback
#: key "_default" is used for any future template not yet added here,
#: so a new boss template never silently draws nothing on the map.
TEMPLATE_ICON = {
    "vermin_sneaky":    "andromalius",           # tentacled horror - sneaky/ambush vibe
    "vermin_swarm":     "minion",                # smaller tentacled kin - swarm vibe
    "aquatic_basic":    "andromalius_aquatic",    # same tentacle horror, teal/purple-shifted for a wet/aquatic read
    "beast_large":      "gnu",                   # minotaur warrior - large beast, natural coloring
    "beast_fast":       "gnu_feral",              # same minotaur, warm-shifted - feral/fast variant
    "humanoid_warrior":  "gnu_warband",            # same minotaur, cool-shifted - reads as a different warband/unit
    "humanoid_caster":   "mage_1",                # plain robed caster - most common template (30 bosses), simplest sprite
    "humanoid_ranged":   "disciple",              # blue-robed cultist - distinct silhouette from the caster-robe sprites
    "demon_caster":      "mage_2_demonic",         # ornate robed caster, hot-red-shifted - demonic
    "elemental_bruiser": "mage_3_elemental",       # thorny caster, green-shifted - elemental/earthy
    "undead_basic":      "shadow",                # shadow wraith - natural undead read
    "demon_hound":       "shadow_demonic",         # same wraith, red-shifted - demonic variant

    "_default":          "shadow",
}


def get_boss_icon_path(template):
    """Full path to the boss portrait PNG for a given creature template
    string. Falls back to TEMPLATE_ICON["_default"] for any template not
    in the table (new creature template added to creatures.json before
    this map is updated) rather than returning None/crashing the map
    screen's render loop."""
    name = TEMPLATE_ICON.get(template, TEMPLATE_ICON["_default"])
    return BOSS_ICON_DIR / f"{name}.png"
