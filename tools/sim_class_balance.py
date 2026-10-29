#!/usr/bin/env python3
"""Fight every class at every level through the real combat engine and compare how they do.

    PYTHONPATH=. python3 tools/sim_class_balance.py [--fights 40] [--levels 5,10,...] [--class Rogue]

Kyle, 2026-10-28: "i want to ensure that all classes are balanced from 1-60."

THIS SIMULATES, IT DOES NOT COMPARE STAT TABLES. Reading damage coefficients off 655 abilities and
adding them up would produce a confident number that has never been tested against armour,
mitigation, resources, cooldowns, crit, the turn meter or the order things actually resolve in. The
engine is the only thing that knows what a class does; everything else is me guessing at it. So each
data point is real fights, run turn by turn through CombatEngine.

ONE POLICY FOR ALL SEVENTEEN CLASSES, or the measurement is of my rotations rather than of the
classes. The policy is deliberately simple and identical: heal when badly hurt and a heal is
available, otherwise use the hardest-hitting thing that works, otherwise swing. Crucially it does
not decide what "works" means - it tries abilities in order and lets execute_ability refuse, so
cooldowns, resource costs, form and weapon requirements are all enforced by the engine's own gates
rather than re-derived here. Re-deriving game rules in a verifier is how most of this session's
false findings happened.

GEAR MATTERS MORE THAN ANYTHING. An ungeared level-40 Warrior loses to a level-40 boar, so every
class is dressed from LootGenerator at its own level before the bell: every slot, class-appropriate,
and routed through equip_item so proficiency rules apply - a Priest really cannot wear the plate.

WHAT IT REPORTS, and what counts as a problem: win rate against a same-level creature, turns to
kill, and health left at the end. A class that cannot beat its own level is broken; one that wins in
half the turns of everybody else is a different kind of broken. Both show up as outliers against the
spread, which is the only honest bar when there is no external reference to measure against.
"""
import argparse
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: Not real playable classes - a shared pool and one scripted companion.
NOT_A_CLASS = {"_universal", "asher_unique"}

#: Enemy templates a solo player meets in the open world, weighted by how ordinary they are.
#: A single template would measure each class against one damage profile, and classes differ a lot
#: in how they handle a caster versus a heavy hitter.
ENEMY_MIX = ["beast_basic", "beast_basic", "humanoid_warrior", "humanoid_caster", "beast_fast"]

#: Equipment slots to fill, in equip order. Two-handers displace the off-hand, which is fine.
GEAR_SLOTS = ["head", "shoulder", "chest", "wrist", "hands", "waist", "legs", "feet", "back",
              "main_hand", "off_hand", "ranged"]

#: dt per engine tick. Small enough that the turn meter resolves one actor at a time.
TICK = 0.05

#: Hard stop so a stalemate (two combatants who cannot kill each other) ends the fight rather
#: than the process.
MAX_TICKS = 20000


def enemy_level(level, above):
    """A FIXED LEVEL GAP IS NOT A FIXED DIFFICULTY. "Ten levels above" is a doubling at level 10 and
    a sixth at level 60, which made the first sweep read 0% for every class at level 10 and told us
    nothing except that a level-20 creature kills a level-10 character. The gap is proportional."""
    return max(level + 2, int(round(level * (1.0 + above))))


def classes():
    """(slug, display_name) for every class, with the display name LOOKED UP.

    char_class is the display name ("Sun Cleric"), the files are slugs
    ("sun_cleric"), and the obvious bridge - slug.replace("_", " ").title() -
    is wrong for exactly one class. 'knight_of_xoroth' title-cases to
    'Knight Of Xoroth' and the game's class is 'Knight of Xoroth'.

    Nothing raises on the mismatch, because three lookups all fail soft:
    Character.__init__ falls back to default stats (strength 39 instead of
    53, health 412 instead of 492), class_armor_map defaults to "cloth" so
    a plate class is dressed in cloth, and class_stat_template_map defaults
    to "int_caster" so its gear rolls caster stats as well.

    Every Knight of Xoroth number this sweep has ever produced carried all
    three faults at once, including the 10%/30% win rate at levels 5-10
    that the 28 Oct class audit reported as a balance problem and blamed on
    the class having no free Rage opener. That diagnosis needs re-taking
    now the class is being measured as itself.
    """
    import re
    text = (ROOT / "entities/character.py").read_text(encoding="utf-8")
    block = text.split("class_stats = {", 1)[1].split("\n        }", 1)[0]
    real = {n.lower().replace(" ", "_"): n
            for n in re.findall(r'^\s*"([^"]+)":\s*\{\s*#?', block, re.M)}
    names = sorted(p.stem for p in (ROOT / "data/abilities").glob("*.json")
                   if p.stem not in NOT_A_CLASS)
    out = []
    for slug in names:
        if slug not in real:
            raise KeyError(f"class slug {slug!r} is not in class_stats - fix the "
                           f"name rather than letting it fall back to defaults")
        out.append((slug, real[slug]))
    return out


def dps_specs_for(slug, srb):
    """EVERY damage spec of this class, as (spec_slug, role) pairs.

    This returned a single spec - the first in sorted order - until 29 Oct
    2026, with my own comment calling it "arbitrary, but stable". Arbitrary
    was the problem. A class with two damage specs got measured on whichever
    one sorted first, and for two classes that was the odd one:

      * chronomancer_artificer won 50% at level 20 where chronomancer_infinite
        won 81%. Artificer's talents amplify wand_of_time, artificers_wand,
        discordance and shatter_echo, while Chromatic Shard out-damages the
        wand roughly two to one per turn - so the rotation never casts the
        abilities the tree improves and its 56 points do close to nothing.
        "Chronomancer is the worst class in the game" was substantially a
        spec-choice artefact on top of that.
      * shaman_enhancement won 47%/62% against shaman_elemental's 65%/88%.

    So every damage spec is measured now. The class row reports its BEST
    build, which is what a player actually plays, and any spec well behind
    its own class's best is reported separately - a weak SPEC and a weak
    CLASS need different fixes and the old shape could not tell them apart.

    EVERY NUMBER THIS TOOL PRODUCED BEFORE 29 OCT 2026 WAS MEASURED WITH ZERO
    TALENT POINTS SPENT. main() built `Character("Sim", display, level)`,
    dressed it and fought - at level 60 that is 51 unspent points, and the
    tool had no mention of talents anywhere in it.

    That is not a uniform handicap. It falls hardest on exactly two kinds of
    class:

      * 325 nodes across 70 of the 97 trees carry an "unlock_ability" effect,
        so a talentless build is missing those abilities OUTRIGHT, not merely
        running them unimproved. Chronomancer has 13 across its three trees.

      * A hybrid's tree is what decides whether it is a healer or a damage
        dealer at all. Measured bare, Shaman and Chronomancer are neither.

    Those two came out worst in the game - Chronomancer an outlier at all
    seven levels sampled (40% at 60 against a 95% median) and Shaman at five
    of seven (35% at 40). Both read as slow killers (7.4 and 6.0 turns against
    a ~5.0 median) with no mitigation story to explain it, which is the shape
    of a kit with pieces missing rather than a kit that is weak.

    Role comes from sim_role_balance.SPEC_ROLES, which is the one place the
    spec-to-role mapping is maintained and has already been corrected against
    reference/coa_sidekick. A spec can hold two roles (Primalist Grovekeeper
    is melee_dps and healer); any damage role qualifies. Preferring the
    FIRST matching spec in sorted order keeps the pick stable run to run -
    an arbitrary-but-fixed choice, so the table is reproducible, and a class
    is judged on one real damage build rather than an average of three.
    """
    dps_roles = ("melee_dps", "ranged_dps")
    out = []
    for spec in sorted(s for s in srb.SPEC_ROLES if s.startswith(slug + "_")):
        roles = srb.roles_of(spec)
        role = next((r for r in roles if r in dps_roles), None)
        if role:
            out.append((spec, role))
    return out


def dress(char, gen, level):
    """Equip a level-appropriate set. Returns how many pieces went on."""
    worn = 0
    for slot in GEAR_SLOTS:
        rarity = "uncommon" if level < 20 else "rare"
        try:
            item = gen.generate_item_for_class(char.char_class, level, slot=slot, rarity=rarity)
        except Exception:                                      # noqa: BLE001
            continue
        if item is None:
            continue
        # equip_item requires the item to be in inventory, and enforces proficiency there - a
        # Priest handed plate is refused, which is the behaviour we want represented.
        char.inventory.append(item)
        if char.equip_item(item):
            worn += 1
        elif item in char.inventory:
            char.inventory.remove(item)
    return worn


#: The real effect_type vocabulary, counted out of data/abilities rather than assumed. The first
#: version of this guessed "damage", "damage_over_time" and "damage_aoe" - two of which do not
#: exist - and so excluded spell_damage (79 abilities) and spell_dot (48) outright. Every caster was
#: then fighting with its basic attack only, and the sweep that produced said a level-40 Priest had
#: ONE offensive ability. It has eight. Nothing about that measurement was real.
OFFENSIVE = {"damage", "spell_damage", "spell_dot", "dot", "ranged_damage",
             "damage_and_heal", "damage_and_restore_mana"}
RESTORATIVE = {"heal", "hot", "damage_and_heal", "damage_and_restore_mana"}


def plan(char):
    """(heals, attacks, setup) in preference order. Built once; the engine decides what is usable.

    SETUP IS THE THIRD LIST AND IT IS NOT OPTIONAL. Some classes have an
    ability that must be running before their rotation works at all, and this
    planner only ever collected heals and attacks - so it fought those
    classes with their core mechanic switched off.

    Paladin is the clear case: Judgement carries consumes_seal, so without a
    Seal up the cast is refused outright with "has no Seal active to Judge!".
    A geared level-50 Paladin therefore landed 0 damage from its biggest
    nuke on 15 of 15 attempts and won 0% of fights against a median of 100%,
    which this sweep reported as a class outlier. With a Seal up, Judgement
    deals 242. Nothing was wrong with the Paladin.

    Collected here: self-targeted buffs that either belong to an
    exclusive_group (Seals, stances, Presences, Formations, Quivers - the
    "one of these is always running" shape) or are named by some other
    ability's requires_form. Those are exactly the abilities a real player
    keeps up and never the ones they spam.
    """
    learned = char.get_learned_abilities()
    heals = [a for a in learned if getattr(a, "effect_type", "") in RESTORATIVE]
    attacks = [a for a in learned if getattr(a, "effect_type", "") in OFFENSIVE]

    needed_forms = set()
    for a in learned:
        rf = getattr(a, "requires_form", None)
        if rf:
            needed_forms.update(rf if isinstance(rf, (list, tuple)) else [rf])
    setup = [
        a for a in learned
        if getattr(a, "effect_type", "") == "buff"
        and getattr(a, "target_type", None) in (None, "self")
        and (getattr(a, "exclusive_group", None)
             or getattr(a, "shapeshift_form_id", None) in needed_forms)
    ]

    def per_turn(a):
        """Damage this ability delivers PER TURN SPENT CASTING IT.

        effect_value means two different things depending on effect_type: for
        a nuke it is one hit, and for a dot it is the TOTAL across every tick.
        Sorting the two together by raw effect_value therefore ranks a weak
        damage-over-time above a strong nuke - Chronomancer's Decomposition is
        66 over 3 turns (22 a turn) and sorted ABOVE Chromatic Shard, which is
        66 in a single turn and lands 115 with spell power behind it. The
        rotation opened on the dot and re-applied it the moment it fell off, so
        2 of every 5 turns went into a 22-a-turn spell while Mage spent all of
        its turns on a 95-a-turn one. Measured at level 10 against level 12,
        that was the difference between 20% and 95%: same health, same armour,
        comparable per-hit damage, but ~40% longer to kill and so ~40% more
        mob turns to survive. Chronomancer lost to every one of the four enemy
        templates and bottomed out at 5% against beast_fast.

        A dot still wins the slot whenever its per-turn figure genuinely beats
        the alternatives, which is the honest comparison and is how a player
        picks. The `live` guard in fight() keeps it from being re-applied while
        it ticks, so a dot that does win costs one turn and then pays out.
        """
        ev = getattr(a, "effect_value", 0) or 0
        dur = getattr(a, "duration", 0) or 0
        return ev / dur if dur > 1 else ev

    # DEFENSIVE COOLDOWNS, which this planner collected nowhere. A
    # self-targeted buff that reduces incoming damage is neither a heal nor an
    # attack, and `setup` only takes the stance-shaped buffs (an
    # exclusive_group or a required form) - so a button like Chronomancer's
    # Time Out!, a 30% damage reduction on a 10-turn cooldown, was never cast
    # in any fight this tool has ever run. Every class with a defensive
    # cooldown was measured without it, and the ones that depend on it most
    # are the squishy ones the tool then reports as fragile.
    #
    # The tank sim already rations defensives for exactly this reason (see
    # tank_axes' "DEFENSIVES HAVE TO BE RATIONED" note). This is the same idea
    # in the class sim, keyed on the same mitigation stats.
    #
    # Excludes anything already in `setup`: a stance is kept up permanently
    # and must not be spent as an emergency button.
    MITIGATION = {"damage_taken_pct", "physical_damage_taken_pct",
                  "magic_damage_taken_pct", "spell_damage_taken_pct",
                  "armor_pct", "armor", "block", "dodge", "parry",
                  "block_value_pct", "max_health_pct"}

    def mitigation_weight(a):
        mods = getattr(a, "stat_mods", {}) or {}
        w = sum(abs(v) for k, v in mods.items() if k in MITIGATION)
        # An absorb shield is mitigation and carries no stat_mods at all.
        w += (getattr(a, "absorb_pct_max_health", 0) or 0) * 100
        w += (getattr(a, "absorb", 0) or 0) / 20.0
        return w

    in_setup = {a.ability_id for a in setup}
    defensives = [
        a for a in learned
        if getattr(a, "effect_type", "") == "buff"
        and getattr(a, "target_type", None) in (None, "self")
        and a.ability_id not in in_setup
        and mitigation_weight(a) > 0
    ]
    defensives.sort(key=lambda a: -mitigation_weight(a))

    heals.sort(key=lambda a: -(getattr(a, "heal_value", 0) or 0))
    attacks.sort(key=lambda a: -per_turn(a))
    return heals, attacks, setup, defensives


def fight(char, enemy_template, level, gen, rng):
    """Run one fight to a conclusion. Returns (won, turns, health_fraction_left)."""
    from combat.combat_engine import CombatEngine
    from entities.monster import Monster
    from entities.party import Party

    char.current_health = char.health
    if getattr(char, "mana", 0):
        char.current_mana = char.mana
    enemy = Monster(f"{enemy_template} {level}", enemy_template, level)
    engine = CombatEngine(char, enemy, party=Party(char))

    heals, attacks, setup, defensives = plan(char)

    # STANCES GO UP BEFORE THE PULL, not during the fight. Every setup buff is
    # a long-duration stance (Chronomancer's Aeons and Continuums run 60
    # turns, Paladin's Seals and Hunter's Aspects likewise) and a player has
    # them running before engaging. Casting them inside the fight charged a
    # turn PER EXCLUSIVE GROUP out of a 4-5 turn fight, which is a 20-40%
    # penalty applied to exactly the classes with the richest stance systems -
    # Chronomancer Artificer has two groups, and paying two opening turns cost
    # it more than the +10% damage and +6% crit its Continuum grants.
    # Pre-casting is also how the existing in-loop maintenance was always
    # meant to behave: "it costs a turn at the start of the fight and never
    # again". It just cost one per group instead of none.
    #
    # The in-loop block below still re-applies anything that drops mid-fight.
    for _group_pass in range(len(setup)):
        mine = {getattr(fx, "effect_id", None)
                for fx in getattr(char, "active_effects", [])}
        names = {getattr(fx, "name", None)
                 for fx in getattr(char, "active_effects", [])}
        pending = [b for b in setup
                   if b.ability_id not in mine and b.name not in names]
        if not pending:
            break
        groups_up = set()
        for b in setup:
            if b.ability_id in mine or b.name in names:
                groups_up.add(getattr(b, "exclusive_group", None)
                              or getattr(b, "shapeshift_form_id", None)
                              or b.ability_id)
        progressed = False
        for b in pending:
            key = (getattr(b, "exclusive_group", None)
                   or getattr(b, "shapeshift_form_id", None) or b.ability_id)
            if key in groups_up:
                continue
            if engine.execute_ability(char, b.ability_id, char)[0]:
                groups_up.add(key)
                progressed = True
        if not progressed:
            break
    # Full resources for the fight itself - the pre-pull buffs are paid for
    # out of combat, so their cost must not come out of the opening rotation.
    char.current_health = char.health
    if getattr(char, "mana", 0):
        char.current_mana = char.mana
    turns = 0
    #: HEALING HAS TO BE RATIONED OR HEALERS HEAL-LOCK. With a bare "heal below 35%" rule, a class
    #: whose heal does not outpace incoming damage never climbs back over the threshold and so
    #: heals every remaining turn: the Shaman spent 17 of 28 turns casting Healing Wave and its
    #: win rate read 40%, which measured this loop rather than the class. A real player heals, gets
    #: back to work, and heals again when it is worth a turn. One heal every third turn at most.
    HEAL_EVERY = 3
    last_heal = -HEAL_EVERY
    #: A defensive is a cooldown, not a rotational button. Four turns apart is
    #: roughly how often a real one comes back up across the classes that have
    #: them, and it stops a 2-turn buff being held up permanently.
    DEFENSIVE_EVERY = 4
    last_defensive = -DEFENSIVE_EVERY
    for _ in range(MAX_TICKS):
        engine.update(TICK)
        if not engine.is_active:
            break
        actor = engine.current_actor
        if actor is None:
            continue
        if actor is not char:
            engine.execute_monster_action()
            continue

        turns += 1
        acted = False
        hurt = char.health and char.current_health / char.health < 0.35
        may_heal = hurt and heals and (turns - last_heal) >= HEAL_EVERY
        order = (heals + attacks) if may_heal else attacks
        # DON'T REAPPLY A DOT THAT IS STILL TICKING. Sorting by total effect value puts damage-over-
        # time first, since its total is the sum of its ticks, so a naive loop re-casts Rend or
        # Shadow Word: Pain every single turn and overwrites it. Some carry a cooldown and the engine
        # refuses, but not all of them do, and the ones that don't would have their class measured
        # as though its whole rotation were one spell cast repeatedly.
        # Keep the setup buff running before spending the turn attacking. One
        # cast, only when nothing from that exclusive group is already up, so
        # it costs a turn at the start of the fight and never again - exactly
        # how a player opens. Without this a Paladin never has a Seal and
        # Judgement is refused every turn of every fight.
        if setup:
            # ONE RUNNING BUFF PER EXCLUSIVE GROUP, not one in total. This
            # loop used to `break` the moment it found ANY setup buff already
            # active, on the comment "something from the group is up - good" -
            # which is only true when there is exactly one group.
            #
            # Chronomancer Artificer has two: chronomancer_aeon (the Aeons)
            # and chronomancer_continuum (Singularity Core, Flux Emitter). It
            # cast Aeon of Resilience on turn 1, and from turn 2 the Aeon was
            # up so the loop broke immediately and SINGULARITY CORE WAS NEVER
            # CAST IN ANY FIGHT - a permanent +10% damage and +6% crit that
            # the spec's own page says to keep up ("On a single boss, keep
            # Singularity Core and Decomposition up"). Measured with the
            # Continuum actually running, Artificer's Wand lands 154 from a
            # listed 90; without it the spec fought at a flat 10% deficit it
            # was never given the chance to close.
            #
            # Still one cast per turn, so opening a fight costs a turn per
            # group and nothing after that - which is how a player opens.
            mine = {getattr(fx, "effect_id", None)
                    for fx in getattr(char, "active_effects", [])}
            names = {getattr(fx, "name", None)
                     for fx in getattr(char, "active_effects", [])}
            groups = {}
            for buff in setup:
                key = (getattr(buff, "exclusive_group", None)
                       or getattr(buff, "shapeshift_form_id", None)
                       or buff.ability_id)
                groups.setdefault(key, []).append(buff)
            for _key, members in groups.items():
                if any(b.ability_id in mine or b.name in names for b in members):
                    continue                    # this group is covered
                for buff in members:
                    if engine.execute_ability(char, buff.ability_id, char)[0]:
                        acted = True
                        break
                if acted:
                    break
            if acted:
                continue

        # SPEND A DEFENSIVE WHEN IT MATTERS, once per DEFENSIVE_EVERY turns.
        # Same rationing logic as the heals above and for the same reason: "cast
        # one whenever it is available" turns a cooldown into a permanent buff
        # and measures the rationing rather than the class. Tried before
        # attacking, and only while hurt, which is when a player presses it.
        if defensives and hurt and (turns - last_defensive) >= DEFENSIVE_EVERY:
            mine = {getattr(fx, "effect_id", None)
                    for fx in getattr(char, "active_effects", [])}
            for d in defensives:
                if d.ability_id in mine:
                    continue
                if engine.execute_ability(char, d.ability_id, char)[0]:
                    last_defensive = turns
                    acted = True
                    break
            if acted:
                continue

        live = {getattr(fx, "effect_id", None) for fx in getattr(enemy, "active_effects", [])}
        for ability in order:
            if ability.ability_id in live:
                continue
            ok, _why = engine.execute_ability(char, ability.ability_id, enemy)
            if ok:
                acted = True
                if ability in heals:
                    last_heal = turns
                break
        if not acted:
            engine.execute_defend(char)

    won = bool(getattr(engine, "victory", False))
    left = (char.current_health / char.health) if char.health else 0.0
    return won, turns, max(0.0, left)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fights", type=int, default=20)
    ap.add_argument("--levels", default="5,10,20,30,40,50,60")
    ap.add_argument("--class", dest="only", default=None)
    # WHY THE BENCHMARK IS ONLY SLIGHTLY ABOVE THE PLAYER'S LEVEL.
    #
    # This defaulted to 0.25 on the reasoning that a same-level fight reads
    # 100% for everyone and separates nothing, so a big gap is needed to
    # make outcomes diverge. That reasoning holds at low level and breaks
    # badly at high level, because the gap is a PERCENTAGE: +2 levels at 5,
    # but +15 at 60. At +15 the test stops measuring damage and starts
    # measuring whether your armour class survives three hits, which cloth
    # never will. The level 60 table read:
    #
    #   physical   Hunter 83, Rogue 75, Cultist 58, Guardian 58, Warrior 50
    #   casters    Mage, Priest, Warlock, Shaman, Runemaster, Starcaller,
    #              Stormbringer, Sun Cleric, Paladin, Druid ALL 0%
    #
    # which reads as every caster in the game being broken. They are not:
    # traced directly, a level 60 Priest casts its whole kit successfully
    # (Smite 98, Shadow Word: Pain 99 over 4 turns, Holy Fire 96) and
    # nobody runs out of mana. It has 708 health in cloth and a level 75
    # creature kills it in three swings. The benchmark was the finding.
    #
    # At a fair gap win rate saturates, exactly as the old comment said -
    # and that is fine, because TURNS TO KILL is then the discriminator and
    # it separates cleanly: 2.1 for a Rogue to 5.2 for a Paladin at 60.
    # Win rate at a fair gap is a floor check ("can this class function"),
    # kill speed is the comparison. Pass --above 0.25 deliberately to ask
    # the different question of who survives an overwhelming pull.
    ap.add_argument("--above", type=float, default=0.05,
                    help="enemy level = character level x (1 + this), min +2 (default 0.05)")
    args = ap.parse_args()
    levels = [int(x) for x in args.levels.split(",")]

    from entities.character import Character
    from entities.loot_generator import LootGenerator
    # Lazy, by path, for the same reason sim_role_balance loads this module
    # that way: each tool is runnable on its own and neither may import the
    # other at module scope without a cycle. Loading srb's module body does
    # not run its main(), so this is safe in both directions.
    import importlib.util as _ilu
    _srb_spec = _ilu.spec_from_file_location("srb", ROOT / "tools/sim_role_balance.py")
    srb = _ilu.module_from_spec(_srb_spec)
    _srb_spec.loader.exec_module(srb)
    gen = LootGenerator()
    rng = random.Random(0)

    roster = [(s, d) for s, d in classes() if not args.only or d.lower() == args.only.lower()]
    if not roster:
        print(f"no class matching {args.only!r}. known: "
              + ", ".join(d for _s, d in classes()))
        return 1

    print(f"{len(roster)} classes x {len(levels)} levels x {args.fights} fights against "
          f"{len(set(ENEMY_MIX))} enemy templates, each at level x{1+args.above:.2f}\n"
          f"  enemy level by player level: " +
          ", ".join(f"{lv}->{enemy_level(lv, args.above)}" for lv in levels) +
          "\n  NOTE the gap widens with level (+2 at 5, +15 at 60), so win rates are only "
          "comparable WITHIN a level, never across them.\n")
    print("WIN RATE")

    results = {}
    spec_rows = {}                      # (slug, spec) -> row, for the findings
    for slug, display in roster:
        speclist = dps_specs_for(slug, srb) or [(None, None)]
        per_spec = {}
        for spec, dps_role in speclist:
            row = {}
            for level in levels:
                wins, turns, left, worn, points_spent = 0, [], [], 0, 0
                for i in range(args.fights):
                    if spec is None:
                        char = Character("Sim", display, level)
                        worn = dress(char, gen, level)
                        points_spent = 0
                    else:
                        # build() creates the character, dresses it with the
                        # callable passed in, and invests up to the level's
                        # talent budget. See dps_specs_for for why measuring
                        # without talents, or on one arbitrary spec, was wrong.
                        char, points_spent = srb.build(spec, level, gen, dress,
                                                       role=dps_role)
                        equipped = char.equipment.get_all_equipped()
                        if hasattr(equipped, "items"):
                            equipped = list(equipped.values())
                        worn = sum(1 for it in equipped if it)
                    won, t, hp = fight(char, ENEMY_MIX[i % len(ENEMY_MIX)],
                                       enemy_level(level, args.above), gen, rng)
                    wins += won
                    if won:
                        turns.append(t)
                        left.append(hp)
                row[level] = {
                    "win": wins / args.fights,
                    "turns": statistics.mean(turns) if turns else None,
                    "left": statistics.mean(left) if left else None,
                    "worn": worn,
                    "pts": points_spent,
                }
            per_spec[spec] = row
            if spec is not None:
                spec_rows[(slug, spec)] = row

        # THE CLASS IS REPORTED ON ITS BEST BUILD, averaged across the levels
        # sampled - what a player actually plays. A spec well behind its own
        # class's best is a separate finding below, because a weak spec and a
        # weak class need different fixes.
        def mean_win(r):
            return statistics.mean(r[l]["win"] for l in levels)
        best_spec = max(per_spec, key=lambda sp: mean_win(per_spec[sp]))
        row = per_spec[best_spec]
        results[slug] = (display, row)
        line = f"  {display:<14}"
        for level in levels:
            line += f"{row[level]['win']*100:>4.0f}% "
        # Strip the CLASS slug, not everything before the first underscore -
        # that turned sun_cleric_piety into "cleric_piety", witch_doctor_
        # shadowhunting into "doctor_shadowhunting" and
        # knight_of_xoroth_war into "of_xoroth_war".
        label = (best_spec[len(slug) + 1:] if best_spec and
                 best_spec.startswith(slug + "_") else (best_spec or "no tree"))
        print(line + f"   (gear {row[levels[-1]]['worn']}/{len(GEAR_SLOTS)}, "
                     f"{row[levels[-1]]['pts']} talent pts, best: {label})")

    print("\n  " + " " * 14 + "".join(f"lv{l:<4}" for l in levels))
    print("\nTURNS TO KILL (won fights only)")
    for slug, (display, row) in results.items():
        line = f"  {display:<14}"
        for level in levels:
            t = row[level]["turns"]
            line += f"{t:>5.1f}" if t else "    -"
        print(line)

    print("\nHEALTH LEFT AFTER WINNING")
    for slug, (display, row) in results.items():
        line = f"  {display:<14}"
        for level in levels:
            h = row[level]["left"]
            line += f"{h*100:>5.0f}" if h is not None else "    -"
        print(line)

    # ---- the two numbers that explain most of the spread above
    print("\nMITIGATION, which is where most of the spread comes from")
    print(f"  {'class':<14}{'armor':>7}{'physical reduced':>18}{'magic reduced':>15}")
    for slug, (display, _row) in results.items():
        c = Character("Probe", display, levels[-1])
        dress(c, gen, levels[-1])
        print(f"  {display:<14}{c.armor:>7}{c.get_physical_reduction_percent():>17.0f}%"
              f"{c.get_magic_reduction_percent():>14.0f}%")
    print(f"  Character.MITIGATION_CONSTANT is {Character.MITIGATION_CONSTANT}, flat - it does not "
          f"scale with\n  level or attacker, so armour climbs with gear forever while magic "
          f"resistance stays at zero.")

    # ---- outliers, measured against the spread rather than an invented target
    print("\nSPECS BEHIND THEIR OWN CLASS'S BEST BUILD")
    #: A spec this far below its class's best, in mean win rate across the
    #: levels sampled, is reported. 15 points is comfortably outside the
    #: run-to-run noise at the default fight count and is the gap at which a
    #: spec stops being a different playstyle and starts being a worse one.
    SPEC_GAP = 0.15
    gaps = []
    for slug, display in roster:
        mine = {sp: r for (sl, sp), r in spec_rows.items() if sl == slug}
        if len(mine) < 2:
            continue
        means = {sp: statistics.mean(r[l]["win"] for l in levels)
                 for sp, r in mine.items()}
        best = max(means, key=lambda sp: means[sp])
        for sp, m in sorted(means.items(), key=lambda kv: kv[1]):
            if means[best] - m >= SPEC_GAP:
                gaps.append(f"  - {sp} wins {m*100:.0f}% against "
                            f"{best[len(slug)+1:]}'s {means[best]*100:.0f}% "
                            f"- same class, same gear, same levels")
    print("\n".join(gaps) if gaps else "  none - every spec is within reach of its class's best")

    print("\nOUTLIERS")
    # JUDGE EACH LEVEL AGAINST ITS OWN MEDIAN, NEVER AGAINST A FIXED BAR.
    #
    # Two things were wrong here and together they manufactured a crisis.
    #
    # The wording claimed a class "cannot reliably beat its own level" when
    # the benchmark is deliberately ABOVE the player's level - see --above,
    # whose own comment explains that a same-level fight reads 100% for
    # everyone and separates nothing. Nobody fought their own level.
    #
    # And the gap is a PERCENTAGE, so the benchmark gets harder as the run
    # goes up: +2 levels at level 5, +5 at 20, +15 at 60. A fixed <50% bar
    # therefore means something different at every level, and the output
    # read as every caster collapsing from level 40 - Mage, Priest, Shaman,
    # Paladin, Runemaster, Stormbringer all at 0% - when what actually
    # changed was the difficulty of the test. enemy_level's own docstring
    # says "A FIXED LEVEL GAP IS NOT A FIXED DIFFICULTY"; a fixed percentage
    # is not either, and acting on that table would have meant "fixing"
    # eight classes that are fine.
    #
    # So: the only honest comparison is between classes at the SAME level,
    # which is the median test. The absolute bar is gone, and the header
    # now states the real enemy level so the numbers cannot be misread.
    problems = []
    for level in levels:
        wr = {d: row[level]["win"] for _s, (d, row) in results.items()}
        median = statistics.median(wr.values())
        foe = enemy_level(level, args.above)
        for d, w in sorted(wr.items(), key=lambda kv: kv[1]):
            if median - w > 0.3:
                problems.append(f"level {level} vs level {foe}: {d} wins {w*100:.0f}% "
                                f"against a median of {median*100:.0f}%")
            elif w == 0 and median >= 0.3:
                problems.append(f"level {level} vs level {foe}: {d} wins NOTHING while the "
                                f"median is {median*100:.0f}%")
        tk = {d: row[level]["turns"] for _s, (d, row) in results.items()
              if row[level]["turns"]}
        if len(tk) > 3:
            med = statistics.median(tk.values())
            for d, t in tk.items():
                if t < med * 0.55:
                    problems.append(f"level {level}: {d} kills in {t:.1f} turns against a "
                                    f"median of {med:.1f} - far ahead")
                elif t > med * 1.8:
                    problems.append(f"level {level}: {d} needs {t:.1f} turns against a median "
                                    f"of {med:.1f} - far behind")
    if problems:
        for p in problems:
            print(f"  - {p}")
    else:
        print("  none - every class is inside the spread at every level sampled")
    return 0


if __name__ == "__main__":
    sys.exit(main())
