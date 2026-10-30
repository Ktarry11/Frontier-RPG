"""What gear each of the 97 SPECS wants - not each of the 30 classes.

Kyle, 29 Oct 2026: "we NEED to consider complex hybrid classes bro"

He is right, and the one-template-per-class model this replaces could not describe the game. Frontier
has 30 classes and 97 talent specs, and data/items/stat_templates.json's class_stat_template_map
gives each CLASS exactly one stat template. That is fine for a Mage, where all three specs want
intellect. It is useless for:

    Shaman          mail,  int_caster   - but Enhancement is a melee agility spec
    Starcaller      plate, int_caster   - but Moon Guard tanks and Warden is a melee weaver
    Runemaster      cloth, int_caster   - and BOTH its melee specs really are intellect, in cloth
    Witch Doctor    leather, agi_int    - but Voodoo is a pure caster and Shadowhunting is an archer
    Druid           leather, int_caster - but Feral is the agility cat-and-bear tree

Measured against the class map, an Enhancement Shaman had 455 mail/intellect items and not one piece
of the mail/agility gear it actually wants - a gap no budget audit can see, because every one of
those items is perfectly on curve. It is just not for them.

HOW EACH ENTRY WAS DECIDED, and the reason the provenance is written down per spec rather than
summarised here: the next person to read this will disagree with two or three of them, and they
should be able to see instantly whether they are arguing with Kyle, with a mechanical rule, or with
my guess.

  - Kyle ruled on nine of them directly, on 29 Oct 2026, and those say so.
  - The rest are derived from the spec's ROLE in tools/sim_role_balance.SPEC_ROLES plus the class's
    armour and weapon lists: healers want intellect and spirit; a ranged spec in a class that
    carries a bow, gun or crossbow is physical; any other ranged spec is a caster; melee and tank
    specs sit on their class's own template unless Kyle said otherwise.
  - Only SIX specs could not be derived at all, and Kyle answered five of those plus Druid Feral.

STORMBRINGER LIGHTNING IS NOT IN THE MELEE LIST, which is worth flagging because it was. It was
filed as melee_dps in SPEC_ROLES; Kyle: "strongbringer is basically ele shaman (pure caster)", and
its own tree reads "Pure elemental fury - channels raw electricity into fast, hard-hitting bolts".
That is the third Stormbringer spec in a row to be mis-roled from a tree description rather than
from what it does, so the correction is in SPEC_ROLES, not papered over here.

This module is data, deliberately. It states what a spec wants; it does not decide whether the game
provides it. tools/audit_class_gear_coverage.py answers that.
"""

#: spec_id -> (armour type, stat template it gears for, role, why that template)
SPEC_GEAR = {
    "barbarian_ancestry": ("leather", "str_physical", "melee_dps",
        "derived: melee or tank on the class's own template"),
    "barbarian_brutality": ("leather", "str_physical", "melee_dps",
        "derived: melee or tank on the class's own template"),
    "barbarian_headhunting": ("leather", "int_caster", "ranged_dps",
        "derived: ranged caster"),
    "bloodmage_accursed": ("leather", "agi_physical", "melee_dps",
        "derived: melee or tank on the class's own template"),
    "bloodmage_eternal": ("leather", "agi_physical", "tank",
        "derived: melee or tank on the class's own template"),
    "bloodmage_fleshweaver": ("leather", "int_caster", "ranged_dps",
        "derived: ranged caster"),
    "bloodmage_sanguine": ("leather", "int_caster", "ranged_dps",
        "derived: ranged caster"),
    "chronomancer_artificer": ("cloth", "int_caster", "ranged_dps",
        "derived: ranged caster"),
    "chronomancer_infinite": ("cloth", "int_caster", "ranged_dps",
        "derived: ranged caster"),
    "chronomancer_time": ("cloth", "int_caster", "healer",
        "derived: healers want intellect and spirit"),
    "cultist_corruption": ("plate", "str_int_hybrid", "ranged_dps",
        "derived: ranged caster"),
    "cultist_dreadnought": ("plate", "str_int_hybrid", "tank",
        "derived: melee or tank on the class's own template"),
    "cultist_godblade": ("plate", "str_int_hybrid", "melee_dps",
        "derived: melee or tank on the class's own template"),
    "cultist_heretic": ("plate", "int_caster", "healer",
        "derived: healers want intellect and spirit"),
    "druid_balance": ("leather", "int_caster", "ranged_dps",
        "derived: ranged caster"),
    "druid_feral": ("leather", "agi_physical", "tank/melee_dps",
        "Kyle 29 Oct: 'an agi 2H mace works for druid tanks'"),
    "druid_restoration": ("leather", "int_caster", "healer",
        "derived: healers want intellect and spirit"),
    "felsworn_infernal": ("leather", "agi_int_hybrid", "ranged_dps",
        "derived: ranged caster"),
    "felsworn_slayer": ("leather", "agi_int_hybrid", "melee_dps",
        "derived: melee or tank on the class's own template"),
    "felsworn_tyrant": ("leather", "agi_int_hybrid", "tank",
        "derived: melee or tank on the class's own template"),
    "guardian_gladiator": ("plate", "str_physical", "melee_dps",
        "derived: melee or tank on the class's own template"),
    "guardian_inspiration": ("plate", "str_physical", "melee_dps",
        "derived: melee or tank on the class's own template"),
    "guardian_vanguard": ("plate", "str_physical", "tank",
        "derived: melee or tank on the class's own template"),
    "hunter_beast_mastery": ("mail", "agi_physical", "ranged_dps",
        "derived: ranged physical - the class carries a bow, gun or crossbow"),
    "hunter_marksmanship": ("mail", "agi_physical", "ranged_dps",
        "derived: ranged physical - the class carries a bow, gun or crossbow"),
    "hunter_survival": ("mail", "agi_physical", "ranged_dps",
        "derived: ranged physical - the class carries a bow, gun or crossbow"),
    "knight_of_xoroth_defiance": ("plate", "str_int_hybrid", "tank",
        "derived: melee or tank on the class's own template"),
    "knight_of_xoroth_hellfire": ("plate", "str_int_hybrid", "melee_dps",
        "derived: melee or tank on the class's own template"),
    "knight_of_xoroth_war": ("plate", "str_int_hybrid", "melee_dps",
        "derived: melee or tank on the class's own template"),
    "mage_arcane": ("cloth", "int_caster", "ranged_dps",
        "derived: ranged caster"),
    "mage_fire": ("cloth", "int_caster", "ranged_dps",
        "derived: ranged caster"),
    "mage_frost": ("cloth", "int_caster", "ranged_dps",
        "derived: ranged caster"),
    "necromancer_animation": ("cloth", "int_caster", "ranged_dps",
        "derived: ranged caster"),
    "necromancer_death": ("cloth", "int_caster", "ranged_dps",
        "derived: ranged caster"),
    "necromancer_rime": ("cloth", "int_caster", "ranged_dps",
        "derived: ranged caster"),
    "paladin_holy": ("plate", "int_caster", "healer",
        "derived: healers want intellect and spirit"),
    "paladin_protection": ("plate", "str_int_hybrid", "tank",
        "derived: melee or tank on the class's own template"),
    "paladin_retribution": ("plate", "str_int_hybrid", "melee_dps",
        "derived: melee or tank on the class's own template"),
    "priest_discipline": ("cloth", "int_caster", "healer",
        "derived: healers want intellect and spirit"),
    "priest_holy": ("cloth", "int_caster", "healer",
        "derived: healers want intellect and spirit"),
    "priest_shadow": ("cloth", "int_caster", "ranged_dps",
        "derived: ranged caster"),
    "primalist_geomancy": ("mail", "str_int_hybrid", "ranged_dps",
        "derived: ranged caster"),
    "primalist_grovekeeper": ("mail", "int_caster", "melee_dps/healer",
        "derived: healers want intellect and spirit"),
    "primalist_mountain_king": ("mail", "str_int_hybrid", "tank",
        "derived: melee or tank on the class's own template"),
    "primalist_wildwalker": ("mail", "str_int_hybrid", "melee_dps",
        "derived: melee or tank on the class's own template"),
    "pyromancer_draconic": ("cloth", "int_caster", "ranged_dps",
        "derived: ranged caster"),
    "pyromancer_flameweaving": ("cloth", "int_caster", "healer",
        "derived: healers want intellect and spirit"),
    "pyromancer_incineration": ("cloth", "int_caster", "ranged_dps",
        "derived: ranged caster"),
    "ranger_archery": ("leather", "agi_physical", "ranged_dps",
        "derived: ranged physical - the class carries a bow, gun or crossbow"),
    "ranger_brigand": ("leather", "agi_physical", "melee_dps",
        "derived: melee or tank on the class's own template"),
    "ranger_farstrider": ("leather", "agi_physical", "ranged_dps",
        "derived: ranged physical - the class carries a bow, gun or crossbow"),
    "reaper_domination": ("mail", "agi_physical", "tank",
        "derived: melee or tank on the class's own template"),
    "reaper_harvest": ("mail", "agi_physical", "melee_dps",
        "derived: melee or tank on the class's own template"),
    "reaper_soul": ("mail", "agi_physical", "melee_dps",
        "derived: melee or tank on the class's own template"),
    "rogue_assassination": ("leather", "agi_physical", "melee_dps",
        "derived: melee or tank on the class's own template"),
    "rogue_combat": ("leather", "agi_physical", "melee_dps",
        "derived: melee or tank on the class's own template"),
    "rogue_subtlety": ("leather", "agi_physical", "melee_dps",
        "derived: melee or tank on the class's own template"),
    "runemaster_engravement": ("cloth", "int_caster", "melee_dps",
        "Kyle 29 Oct: 'runemaster is a melee int character'"),
    "runemaster_glyphic": ("cloth", "int_caster", "ranged_dps",
        "derived: ranged caster"),
    "runemaster_riftblade": ("cloth", "int_caster", "melee_dps",
        "Kyle 29 Oct: 'runemaster is a melee int character'"),
    "shaman_elemental": ("mail", "int_caster", "ranged_dps",
        "derived: ranged caster"),
    "shaman_enhancement": ("mail", "agi_physical", "melee_dps",
        "Kyle 29 Oct: 'enhancement 2H shamans use agi too. or dual wield enhancement shamans use agi weapons'"),
    "shaman_restoration": ("mail", "int_caster", "healer",
        "derived: healers want intellect and spirit"),
    "starcaller_moon_guard": ("plate", "str_int_hybrid", "tank",
        "Kyle 29 Oct, asked directly: str/int hybrid"),
    "starcaller_moon_priest": ("plate", "int_caster", "healer",
        "derived: healers want intellect and spirit"),
    "starcaller_sentinel": ("plate", "int_caster", "ranged_dps",
        "derived: ranged caster"),
    "starcaller_warden": ("plate", "str_int_hybrid", "melee_dps",
        "Kyle 29 Oct, asked directly: str/int hybrid"),
    "stormbringer_lightning": ("cloth", "int_caster", "ranged_dps",
        "derived: ranged caster"),
    "stormbringer_maelstrom": ("cloth", "int_caster", "ranged_dps",
        "derived: ranged caster"),
    "stormbringer_wind": ("cloth", "int_caster", "ranged_dps",
        "derived: ranged caster"),
    "sun_cleric_blessings": ("plate", "int_caster", "healer",
        "derived: healers want intellect and spirit"),
    "sun_cleric_piety": ("plate", "str_int_hybrid", "ranged_dps",
        "derived: ranged caster"),
    "sun_cleric_seraphim": ("plate", "str_int_hybrid", "tank",
        "derived: melee or tank on the class's own template"),
    "sun_cleric_valkyrie": ("plate", "str_int_hybrid", "melee_dps",
        "derived: melee or tank on the class's own template"),
    "templar_crusader": ("leather", "agi_physical", "melee_dps",
        "derived: melee or tank on the class's own template"),
    "templar_oathkeeper": ("leather", "agi_physical", "tank",
        "derived: melee or tank on the class's own template"),
    "templar_zealot": ("leather", "agi_physical", "melee_dps",
        "derived: melee or tank on the class's own template"),
    "tinker_demolition": ("mail", "agi_physical", "ranged_dps",
        "derived: ranged physical - the class carries a bow, gun or crossbow"),
    "tinker_invention": ("mail", "int_caster", "healer",
        "derived: healers want intellect and spirit"),
    "tinker_mechanics": ("mail", "agi_int_hybrid", "melee_dps",
        "derived: melee or tank on the class's own template"),
    "venomancer_fortitude": ("mail", "agi_int_hybrid", "tank",
        "derived: melee or tank on the class's own template"),
    "venomancer_stalking": ("mail", "agi_int_hybrid", "melee_dps",
        "derived: melee or tank on the class's own template"),
    "venomancer_venom": ("mail", "agi_physical", "ranged_dps",
        "derived: ranged physical - the class carries a bow, gun or crossbow"),
    "venomancer_vizier": ("mail", "int_caster", "healer",
        "derived: healers want intellect and spirit"),
    "warlock_affliction": ("cloth", "int_caster", "ranged_dps",
        "derived: ranged caster"),
    "warlock_demonology": ("cloth", "int_caster", "ranged_dps",
        "derived: ranged caster"),
    "warlock_destruction": ("cloth", "int_caster", "ranged_dps",
        "derived: ranged caster"),
    "warrior_arms": ("plate", "str_physical", "melee_dps",
        "derived: melee or tank on the class's own template"),
    "warrior_fury": ("plate", "str_physical", "melee_dps",
        "derived: melee or tank on the class's own template"),
    "warrior_protection": ("plate", "str_physical", "tank",
        "derived: melee or tank on the class's own template"),
    "witch_doctor_brewing": ("leather", "int_caster", "healer",
        "Kyle 29 Oct: 'leather + int as healer/caster'"),
    "witch_doctor_shadowhunting": ("leather", "agi_physical", "ranged_dps",
        "Kyle 29 Oct: 'leather + agi as a ranged dps (think like a hunter)'; its tree opens 'Ranged weapon and Serpent Wards'"),
    "witch_doctor_voodoo": ("leather", "int_caster", "ranged_dps",
        "Kyle 29 Oct: 'leather + int as healer/caster'; its tree is a 'Ranged Shadow, Nature and Fire caster'"),
    "witch_hunter_black_knight": ("mail", "agi_physical", "tank",
        "derived: melee or tank on the class's own template"),
    "witch_hunter_boltslinger": ("mail", "agi_physical", "ranged_dps",
        "derived: ranged physical - the class carries a bow, gun or crossbow"),
    "witch_hunter_houndmaster": ("mail", "agi_physical", "ranged_dps",
        "derived: ranged physical - the class carries a bow, gun or crossbow"),
    "witch_hunter_inquisition": ("mail", "agi_physical", "melee_dps",
        "derived: melee or tank on the class's own template"),
}


def wanted_stats(template):
    """The stats a spec with this template actually wants, best first."""
    import json
    from pathlib import Path
    path = Path(__file__).resolve().parent.parent / "data/items/stat_templates.json"
    stats = json.loads(path.read_text())["stat_templates"][template]["primary_stats"]
    return [s for s, _w in sorted(stats.items(), key=lambda kv: -kv[1])]


def niches():
    """(armour, template) -> list of spec_ids that gear for it."""
    out = {}
    for spec_id, (armour, template, _role, _why) in SPEC_GEAR.items():
        out.setdefault((armour, template), []).append(spec_id)
    return out
