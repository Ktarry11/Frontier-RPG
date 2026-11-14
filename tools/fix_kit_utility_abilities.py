#!/usr/bin/env python3
"""The 19 kit dispels, summons and resource-restores that could never succeed.

    PYTHONPATH=. python3 tools/fix_kit_utility_abilities.py [--apply]

Idempotent: a row whose fields already match is skipped.

=============================================================================
WHY THEY FAILED - three different missing fields, one shape
=============================================================================

These are NOT the inert buffs (that is tools/apply_kit_mods.py). These have a
real effect_type the engine fully implements, a real effect_value, and a
cooldown. They cast, they charge a turn and a resource, and they cannot
possibly do anything, because the single field their effect_type reads was
never authored:

  12 DISPELS have dispel_type None. DispelType.NONE means "not dispellable by
     anything", so dispel_effect can never match. Liam's "A Calm Voice"
     reports "Mate has no Effect effect to remove!" - the engine rendering an
     unset type - even against a target loaded with debuffs.

   4 SUMMONS have no summon_pet_template. abilities.py:3487 reads the JSON's
     "summon_pet_template" key; every one of these authored nothing, so Diego
     gets "tries to summon a pet, but has none".

   3 RESOURCE RESTORES put their magnitude in effect_value, but the
     restore_resource branch reads mana_restore_pct (abilities.py:3541 -
     "Reuses mana_restore_pct's existing rank key"). effect_value is not
     consulted at all, so Ryan's 15 restored 0.

This was found by CASTING all 201 kit abilities against a real Monster and a
real hurt ally, not by reading the data - and only after giving each one
something to act on. A dispel with no debuff in front of it correctly does
nothing, and an earlier pass that topped every resource pool to full
correctly saw the restores do nothing too. Both looked exactly like these
bugs. See claude/value_conventions_and_dead_data_2026_10_29.md section 5.

=============================================================================
WHAT IS ASSIGNED FROM WHAT
=============================================================================

Every value below comes from the ability's OWN description, not from a
default. Tarek's "removes one poison and one disease" is the two specific
schools; Marco's "removes one harmful effect" is any of the four.

DISPELS AIMED AT AN ENEMY ARE PURGES, and work through the same path:
dispel_effect removes a match "regardless of whether it's harmful or
beneficial" (status_effects.py:894), which is how Devour Magic takes a buff
off an enemy. So Fiona's, Tomas's and Diego's "removes every buff from the
target" needs a type and a count, not a new mechanic.

Where a clause still cannot be expressed it is recorded in the ability's
`engine` note rather than approximated - the accompanying heals, the
reflected damage, "the STRONGEST effect", and restore_resource being
self-only while two of these say "each ally".
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KITS = ROOT / "data" / "npcs" / "personal_kits.json"

#: Any of the four schools - "removes one harmful effect", unqualified.
ANY = ["magic", "curse", "poison", "disease"]
#: "removes EVERY buff" - a count high enough to clear any real stack.
ALL_OF_THEM = 10

#: ability_id -> {fields to set} + what still cannot be expressed
TABLE = {
    # ---- DISPELS on allies -------------------------------------------------
    "personal_marco_he_fixes_other_things": (
        {"dispel_type": ANY, "dispel_count": 1},
        "removes one harmful effect of any school from every ally",
        "the small heal that accompanies it"),
    "personal_amber_she_works_the_rot": (
        {"dispel_type": ANY, "dispel_count": 1},
        "removes one harmful effect of any school from every ally",
        "the nature damage dealt back to whoever applied it"),
    "personal_liam_a_calm_voice": (
        # "fear and panic" is crowd control, and there is no fear DispelType -
        # magic is where WoW files fear removal, so that is the closest true
        # reading rather than an invented school.
        {"dispel_type": "magic", "dispel_count": 1},
        "removes a magic effect from the party",
        "fear and panic specifically (CC is not a dispel school), and the heal"),
    "personal_liam_four_lines_long": (
        {"dispel_type": ANY, "dispel_count": 1},
        "removes one damage-over-time effect from each ally", None),
    "personal_anjali_sick_in_a_patterned_way": (
        {"dispel_type": ANY, "dispel_count": 1},
        "removes one harmful effect from each ally",
        "choosing the STRONGEST effect rather than the first match"),
    "personal_tarek_which_springs_are_clean": (
        {"dispel_type": ["poison", "disease"], "dispel_count": 2},
        "removes one poison and one disease from each ally", None),
    "personal_esteban_he_asks_every_time": (
        {"dispel_type": ANY, "dispel_count": 1},
        "removes one harmful effect from an ally",
        "dealing the effect's remaining damage to whoever applied it"),
    "personal_yusuf_he_knows_doses": (
        {"dispel_type": ["poison", "disease"], "dispel_count": 1},
        "removes one poison or disease from each ally",
        "healing them for what it would have dealt"),
    "personal_skye_she_found_a_fire_and_put_it_out": (
        {"dispel_type": "magic", "dispel_count": ALL_OF_THEM},
        "removes burning (magic) effects from the party",
        "dealing their remaining damage to one enemy"),

    # ---- DISPELS aimed at an ENEMY - purges --------------------------------
    "personal_fiona_too_neat": (
        {"dispel_type": "magic", "dispel_count": ALL_OF_THEM},
        "strips the target's buffs",
        "dealing damage for each buff taken"),
    "personal_tomas_tie_off_badly": (
        {"dispel_type": "magic", "dispel_count": ALL_OF_THEM},
        "strips the target's buffs",
        "restricting it to DEFENSIVE buffs, and the 25% armour reduction"),
    "personal_diego_take_a_thing_apart": (
        {"dispel_type": "magic", "dispel_count": 2},
        "strips two buffs from the target",
        "the 30% armour reduction"),

    # ---- SUMMONS -----------------------------------------------------------
    "personal_bakyt_six_generations": (
        {"summon_pet_template": "war_falcon"},
        "summons Bakyt's eagle",
        "the +40% damage branch for when it is already alive"),
    "personal_khalid_took_food_from_his_hand": (
        {"summon_pet_template": "raptor"},
        "calls the hill raptor",
        "its attacking a RANDOM enemy rather than the chosen one"),
    "personal_diego_the_clockwork_beetle": (
        {"summon_pet_template": "clockwork_assistant"},
        "the beetle fights", None),
    "personal_stelios_who_a_body_was": (
        # A ghoul is the honest approximation. "The most recently slain enemy
        # at half its strength" means building a pet FROM a specific corpse,
        # which no template can express.
        {"summon_pet_template": "ghoul"},
        "raises an undead servant",
        "raising the ACTUAL slain enemy, at half its own strength"),

    # ---- RESOURCE RESTORES -------------------------------------------------
    # mana_restore_pct is the field the branch reads; the magnitude was sitting
    # in effect_value, which restore_resource never looks at.
    "personal_ryan_pays_on_time": (
        {"mana_restore_pct": 15},
        "restores 15% of his maximum mana",
        "spending 15% of his maximum health to pay for it"),
    "personal_bakyt_water_where_there_is_none": (
        {"mana_restore_pct": 20},
        "restores 20% of the caster's maximum resource",
        "reaching EACH ALLY - restore_resource is self-only by construction"),
    "personal_driss_the_water_allowance": (
        {"mana_restore_pct": 25},
        "restores 25% of the caster's maximum resource",
        "reaching each ally, and excluding those above half resource"),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    doc = json.loads(KITS.read_text(encoding="utf-8"))
    changed, already, unseen = [], [], set(TABLE)

    for kid, kit in doc.items():
        if kid.startswith("_") or not isinstance(kit, dict):
            continue
        for a in (kit.get("abilities") or []):
            aid = a.get("ability_id")
            if aid not in TABLE:
                continue
            unseen.discard(aid)
            fields, delivers, gap = TABLE[aid]

            def _present(key, value):
                if key == "mana_restore_pct":
                    ranks = a.get("ranks") or []
                    return bool(ranks) and all(r.get(key) == value for r in ranks)
                return a.get(key) == value

            if all(_present(k, v) for k, v in fields.items()):
                already.append((kit.get("name"), a.get("name")))
                continue
            changed.append((kit.get("name"), a.get("name"), fields, delivers, gap))
            if args.apply:
                # mana_restore_pct IS A RANK KEY, not an ability key:
                # Ability.mana_restore_pct is a property reading
                # self.current_rank.get("mana_restore_pct", 0)
                # (abilities.py:950). Setting it on the ability leaves the
                # property reading 0 from the rank and the restore still
                # delivers nothing, which is the same shape as the bug being
                # fixed - the field exists, it is just not where the engine
                # looks.
                rank_only = {k: v for k, v in fields.items()
                             if k == "mana_restore_pct"}
                for k, v in fields.items():
                    if k not in rank_only:
                        a[k] = v
                for rank in (a.get("ranks") or []):
                    rank.update(rank_only)
                if gap:
                    a["engine"] = f"needs: {gap}"
                # effect_value stays as authored: it is what the dispel and
                # summon branches never read, and overwriting it would lose
                # the number whoever wrote these had in mind.

    print(f"  {len(changed)} ability/abilities fixed"
          + (f", {len(already)} already correct" if already else ""))
    if unseen:
        print(f"  !! {len(unseen)} table row(s) matched nothing: {sorted(unseen)}")
    print()
    for who, name, fields, delivers, gap in changed:
        print(f"  {str(who)[:15]:17}{str(name)[:32]:34}{delivers}")
        print(f"  {'':17}{json.dumps(fields)}")
        if gap:
            print(f"  {'':17}still missing: {gap}")

    if args.apply:
        KITS.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\n  wrote {KITS.relative_to(ROOT)}")
    else:
        print("\n  dry run - pass --apply to write")
    return 1 if unseen else 0


if __name__ == "__main__":
    sys.exit(main())
