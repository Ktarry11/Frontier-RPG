"""
Creature manager - loads creature definitions and spawns Monster instances.
"""
import json
import random
from pathlib import Path
from entities.monster import Monster


class CreatureManager:
    """Manages creature definitions and spawning."""
    
    def __init__(self):
        self.creatures = {}
        self.encounters = {}
        #: Creature ability kits, read here only to work out which school a
        #: creature mainly casts (see _apply_cast_affinity). Monster loads
        #: the same file for the kits themselves.
        self.ability_kits = {}
        self._load_data()
    
    def _load_data(self):
        """Load creature data from JSON files."""
        data_dir = Path(__file__).parent.parent / "data" / "creatures"
        
        # Load creatures
        creatures_file = data_dir / "creatures.json"
        if creatures_file.exists():
            with open(creatures_file, 'r') as f:
                self.creatures = json.load(f).get("creatures", {})
            self._reject_dead_kit_key(creatures_file, self.creatures)

        # Ability kits, for the cast-affinity resistance derivation.
        kits_file = data_dir / "ability_kits.json"
        if kits_file.exists():
            with open(kits_file, "r") as f:
                blob = json.load(f)
            self.ability_kits = blob.get("kits", blob)

        # Load encounters
        encounters_file = data_dir / "encounters.json"
        if encounters_file.exists():
            with open(encounters_file, 'r') as f:
                self.encounters = json.load(f).get("zones", {})
    
    @staticmethod
    def _reject_dead_kit_key(path, creatures):
        """Hard-fail on the `"kit"` key, which spawn_creature does not read.

        DELIBERATELY LOUD, for the same reason entities/monster.py raises on
        an unknown template key rather than falling back to beast_basic: a
        silent substitution hides for months. spawn_creature reads
        `ability_kit`; `"kit"` is read by nothing and never was, so a creature
        carrying only `kit` fought with its TEMPLATE'S default kit instead of
        the one authored for it. Six zone build tools had each noticed this
        locally and stripped the key from their own creatures
        (build_southern_barrens_content.py's DROP_KEYS,
        build_silverpine_dungeon_content.py, build_central_barrens_content.py,
        build_northern_barrens_content.py, build_wailing_content.py,
        build_ashenvale_dungeon_content.py) without anything stopping the next
        author from writing it again - and 33 creatures were still carrying it
        when tools/audit_monster_combat.py put them in a real fight:
        Skeleton Archer fought as a generic `marksman`, Ancient Treant as a
        `large_beast`, Twisted Sapling as a `scorpid`, Zombie Bear as a
        `boar`. The kits named for them existed and loaded for nobody.

        Raising at load rather than reporting at spawn is on purpose: a
        creature's moveset being wrong is not visible in play (it still
        attacks, it just attacks with someone else's abilities), so the only
        moment anyone will notice is the moment the data is wrong.
        """
        stale = sorted(name for name, d in creatures.items() if "kit" in d)
        if stale:
            raise ValueError(
                f"{path}: {len(stale)} creature(s) carry a \"kit\" key, which "
                f"nothing reads - spawn_creature reads \"ability_kit\". Rename "
                f"the key (and delete it where an \"ability_kit\" is already "
                f"present, which wins). Affected: {', '.join(stale[:12])}"
                + (" ..." if len(stale) > 12 else ""))

    # A subzone roll blends its own table with the parent zone's open_zone
    # table at this fraction of a single open_zone entry's total weight -
    # "raptor grounds" should read as raptor TERRITORY within the Barrens,
    # not a sealed box where nothing else from the zone ever wanders
    # through (Kyle: "the Barrens can have raptors everywhere, but higher
    # chance in raptor grounds"). Caves are NOT blended - a cave is its
    # own separate instanced map with its own theme (Wailing Caverns
    # shouldn't have Barrens surface critters bleeding in), this is only
    # about open-world subzones inside a zone the player is already
    # walking through.
    SUBZONE_OPEN_ZONE_BLEND = 0.35

    def is_safe_subzone(self, zone_name, subzone_name):
        """True for a subzone flagged "safe": true in encounters.json.

        WHY THIS EXISTS. A subzone with no roster of its own falls straight through to the parent
        zone's open_zone table (see get_encounter_table), and subzones roll encounters at 5% per
        step against the open zone's 2% - so the quietest place on a map is the MOST dangerous one
        unless somebody says otherwise. That is fine for a shrine or a waypoint and wrong for a
        settlement: Lastwater is ten vendors and a dungeon doorway on an island at the bottom of
        the Glittervein, and without this the player gets jumped by level-49 Brinewrought between
        the innkeeper and the quartermaster.

        Towns are normally their own map, where zone.is_town covers this. A settlement that lives
        INSIDE an open zone has had no way to say it is a settlement until now.
        """
        if zone_name not in self.encounters or not subzone_name:
            return False
        sz = self.encounters[zone_name].get("subzones", {}).get(subzone_name)
        return bool(sz and sz.get("safe"))

    def get_encounter_table(self, zone_name, location_type="open_zone", subzone_name=None):
        """Get encounter table for a zone/subzone/cave.

        For a subzone, this BLENDS the subzone's own creatures with the
        parent zone's open_zone table rather than fully replacing it (see
        SUBZONE_OPEN_ZONE_BLEND) - real bug found + fixed this pass: every
        subzone before this was a 100% exclusive pool, so stepping into
        Harpy Roost meant literally nothing but harpies could ever spawn,
        not even a Plainstrider passing through. The subzone's own
        creatures keep their authored weights (so the "this IS harpy
        territory" read stays strong); the zone's open_zone creatures are
        added in at a flat fraction of the zone table's total weight, so
        a zone with many open_zone entries doesn't get diluted more than
        one with few just because it has more distinct species listed.
        """
        if zone_name not in self.encounters:
            return {}

        zone_data = self.encounters[zone_name]

        if location_type == "open_zone":
            return zone_data.get("open_zone", {}).get("creatures", {})
        elif location_type == "subzone" and subzone_name:
            if self.is_safe_subzone(zone_name, subzone_name):
                return {}
            subzone_table = dict(
                zone_data.get("subzones", {}).get(subzone_name, {}).get("creatures", {}))
            open_table = zone_data.get("open_zone", {}).get("creatures", {})
            subzone_total = sum(subzone_table.values())
            if not subzone_table or subzone_total <= 0:
                # A subzone with no roster of its own (or one that's all
                # weight-0 bosses, e.g. Shrine of the Fallen Warrior -
                # deliberately "a quiet, low-combat waypoint" per its own
                # generator comment) isn't a bug to special-case: it just
                # has nothing to blend INTO, so it falls straight through
                # to the parent zone's plain open_zone table instead of
                # returning empty.
                return dict(open_table)
            open_total = sum(open_table.values())
            if open_table and open_total > 0:
                blend_budget = subzone_total * self.SUBZONE_OPEN_ZONE_BLEND
                for name, weight in open_table.items():
                    if name in subzone_table:
                        # Already in the subzone's own table (its own
                        # entry there authoritatively sets how common it
                        # is here) - don't double it up with a second,
                        # separately-weighted open_zone contribution.
                        continue
                    share = blend_budget * (weight / open_total)
                    if share > 0:
                        subzone_table[name] = share
            return subzone_table
        elif location_type == "cave" and subzone_name:
            return zone_data.get("caves", {}).get(subzone_name, {}).get("creatures", {})

        return {}
    
    #: Resistance a creature gets in the school it mainly casts, and in a
    #: secondary school it also casts, on Character's -60..60 scale where a
    #: point is 1.25%.
    #:
    #: 60 IS KYLE'S WORKED EXAMPLE, 6 Nov: "a fireball hits an enemy for 100
    #: damage. On a fire elemental it will hit for 25 damage." That is 75%,
    #: which is the cap, which is 60 points - so a creature whose kit is
    #: mainly one school IS that example and gets the full number. It was 40
    #: when a point was half a percent and the cap was 30%; carrying 40 onto
    #: the new scale would have made the elemental 50% and quietly missed the
    #: one case the whole system exists to produce.
    #:
    #: A secondary school is half of it, 30 points for 37.5%.
    CAST_AFFINITY_PRIMARY = 60
    CAST_AFFINITY_SECONDARY = 30

    #: A VULNERABILITY COMES FROM WHAT A CREATURE IS, NOT WHAT IT CASTS, and
    #: it must be guessable on sight. Kyle, 6 Nov: "Not everything needs a
    #: vulnerability. But it should be obvious to the player. You see a
    #: tree. You use fireball. It hurts the tree."
    #:
    #: The first version of this derived the weakness from the opposite of
    #: whatever school the creature's KIT mostly cast, and that is a
    #: different thing wearing the same shape. It read a creature's magic
    #: rather than its body, so it gave 135 creatures a holy weakness
    #: including 56 humanoid casters, a Witchwing Harpy and a wolf called
    #: Alpha Fenris - nothing about a human cultist's appearance says holy
    #: hurts him more, and a tree, which is the clearest case in the game,
    #: got nothing at all because it casts nothing.
    #:
    #: So the rule is the creature's NATURE, and only where a player would
    #: already expect it:
    #:
    #:     undead  -> holy     a skeleton, a ghoul, a wraith
    #:     demon   -> holy     the other classic
    #:     plant   -> fire     wood burns. Kyle's own example
    #:     fire    -> frost    a thing made of fire
    #:     frost   -> fire     ...and a thing made of ice
    #:
    #: Everything else gets none, which is the "not everything needs a
    #: vulnerability" half. Nature and arcane are nobody's weakness here:
    #: neither has an opposite among the six that a player could reason
    #: about, and an invented one would be worse than none.
    #:
    #: -40 is Kyle's own figure: 150 damage from a 100-damage hit is 50%
    #: extra, which is 40 points of negative resistance. Deliberately short
    #: of the -60 floor, so the floor stays for a hand-authored creature
    #: whose entire point is a weakness. Clamped to -30 below level 60 like
    #: everything else (Character.clamp_resistance_for_level).
    VULNERABILITY = -40

    #: Template families whose whole body is the tell. Keyed on the template
    #: name's prefix, so the undead_warrior/undead_caster/undead_beast
    #: chassis added on 6 Nov are covered without listing each.
    FAMILY_VULNERABILITY = {"undead": "holy", "demon": "holy"}

    #: ...and the creatures whose nature is in their name rather than their
    #: template. HAND-CHECKED, because name matching cannot do this: a
    #: prefix rule for "stalk" claims every Stalker in the game (a Crag
    #: Stalker is a predator), "thorn" claims a Thornhide Boar, and
    #: "Kundaraz Vinecutter" is a man who cuts vines rather than a vine.
    #: Each of these was read and kept; the list is short on purpose.
    NATURE_VULNERABILITY = {
        # Wood and fungus burn - Kyle's worked example.
        "Corrupted Treant": "fire",
        "Bramblethorn the Ancient": "fire",
        "Oasis Tangle-Vine": "fire",
        "The Deep Bloom": "fire",
        "Rootbound": "fire",
        "Rootmaw": "fire",
        "Fenrot Creeper": "fire",
        "Mosshide the Gloomcap Elder": "fire",
        "Gloomcap Sporeling": "fire",
        "Spore-Drifter": "fire",
        "Plague Spore": "fire",
        "Mycelial Husk": "fire",
        "Bloom Thrall": "fire",
        "Queen Thistlewing": "fire",
        "Marsh Ooze": "fire",
        # Made of fire, so ice bites.
        "Ember Wisp": "frost",
        "Cinderfang": "frost",
        "Smolderhide": "frost",
        # Made of water or ice, so fire does.
        "Tidal Elemental": "fire",
        "Deep Seep": "fire",
        "Barrow Shade": "fire",
        "The Tidewrack": "fire",
    }

    def _kit_schools(self, kit_name):
        """How many abilities in this kit belong to each real school."""
        from collections import Counter
        from combat.status_effects import DamageSchool
        kit = self.ability_kits.get(kit_name) or []
        entries = kit if isinstance(kit, list) else kit.get("abilities", [])
        counts = Counter()
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            school = entry.get("school")
            if school in DamageSchool.ALL_SCHOOLS:
                counts[school] += 1
        return counts

    def _apply_cast_affinity(self, monster, kit_name):
        """Raise a spawned creature's resistance in the schools it casts.

        Takes the HIGHER of the template baseline and the affinity rather
        than adding them, so a demon that casts fire ends up resistant to
        fire once rather than twice, and nothing creeps past the cap by
        accident.

        AND LOWERS IT IN THE OPPOSITE SCHOOL. A creature whose kit is mainly
        fire is made vulnerable to frost and the reverse, holy against
        shadow likewise - which is the other half of Kyle's example and the
        thing that makes picking a school a decision rather than a flavour.
        THE KIT BEATS A GENERIC TEMPLATE FLOOR here. The first version only
        applied the vulnerability where the school sat at zero or below, and
        it fired on almost nothing: elemental_caster gives a flat 10 in all
        six schools, so an Ember Wisp and a Tidal Elemental - the two
        clearest cases in the game - both kept 10 in the school they should
        fear. A flat spread is filler, not a statement; a kit that is mainly
        fire is a statement. The only thing the vulnerability will not
        override is a school the creature ITSELF casts, so a creature with
        both fire and frost in its kit is vulnerable to neither.
        """
        from entities.character import Character
        counts = self._kit_schools(kit_name)
        if not counts:
            return
        ranked = counts.most_common()
        wanted = {ranked[0][0]: self.CAST_AFFINITY_PRIMARY}
        for school, _n in ranked[1:]:
            wanted.setdefault(school, self.CAST_AFFINITY_SECONDARY)
        for school, value in wanted.items():
            attr = f"{school}_resistance"
            current = getattr(monster, attr, 0) or 0
            setattr(monster, attr, min(Character.RESIST_MAX, max(current, value)))

    def _apply_vulnerability(self, monster, template_name=None, ability_kit=None):
        """Make a creature weak to what its own nature invites.

        See VULNERABILITY and the two tables above for the rule and why it
        reads the creature's BODY rather than its spell list.

        A school the creature resists is never also made a weakness, so a
        hand-authored exception (an undead whose whole point is holy magic)
        keeps its resistance rather than being handed a contradiction.
        """
        from entities.character import Character
        school = self.NATURE_VULNERABILITY.get(getattr(monster, "name", None))
        curated = school is not None
        if school is None:
            for family, sch in self.FAMILY_VULNERABILITY.items():
                if str(template_name or "").startswith(family):
                    school = sch
                    break
        if school is None:
            return
        # A school the creature CASTS is never also its weakness - that
        # holds for both tables, since nothing should resist and fear the
        # same element.
        if school in self._kit_schools(ability_kit):
            return
        attr = f"{school}_resistance"
        current = getattr(monster, attr, 0) or 0
        # A HAND-CHECKED ENTRY BEATS A GENERIC TEMPLATE FLOOR; a family rule
        # does not. elemental_caster hands out a flat 10 in all six schools,
        # which is filler rather than a statement, and it was silently
        # blocking every elemental on the curated list - an Ember Wisp kept
        # frost 10 and a Tidal Elemental kept fire 10, which are the two
        # clearest cases after the tree. Where the FAMILY rule is what
        # matched, a real positive resistance still wins, so a hand-authored
        # undead built to shrug off holy magic keeps that rather than being
        # handed a contradiction.
        if current > 0 and not curated:
            return
        setattr(monster, attr,
                max(Character.RESIST_MIN, min(current, self.VULNERABILITY)))

    def spawn_creature(self, creature_name, level=None, zone_name=None):
        """Spawn a creature (Monster instance).

        zone_name (optional): the encounter-table zone the roll came from.  A zone may carry
        ``"level_overrides": {creature: [lo, hi]}`` in encounters.json so one creature can sit at different
        levels in different zones (Ashenvale East 20-25 vs West 22-28 share most of their wildlife)."""
        if creature_name not in self.creatures:
            return None
        
        creature_def = self.creatures[creature_name]
        template_name = creature_def.get("template")
        
        # Determine level
        if level is None:
            level_range = creature_def.get("level_range", [1, 1])
            if zone_name:
                ov = self.encounters.get(zone_name, {}).get("level_overrides", {}).get(creature_name)
                if ov:
                    level_range = ov
            level = random.randint(level_range[0], level_range[1])
        
        # Get ability kit if specified, otherwise Monster uses template default
        ability_kit = creature_def.get("ability_kit")
        
        # Create Monster using template + ability kit
        monster = Monster(creature_name, template_name, level, kit=ability_kit)

        # A CREATURE RESISTS WHAT IT CASTS. The template gives a type
        # baseline (undead shrug off shadow, demons shrug off fire), but
        # the thing that makes Kyle's rule land - "a caster should be
        # punished if they use fireball against a flame elemental" - is
        # per-creature, and a template cannot express it: Molten Elemental
        # and Spraywater Elemental share elemental_bruiser.
        #
        # Derived from the creature's own ability kit rather than written
        # into creatures.json for 447 creatures, so it cannot drift: give a
        # kit a Fireball and the creature that casts it starts resisting
        # fire, with nothing else to remember to update.
        self._apply_cast_affinity(monster, ability_kit)

        # ...AND IS WEAK TO WHAT ITS BODY INVITES, which is a separate rule
        # on a separate signal - see _apply_vulnerability. Called here and
        # not inside _apply_cast_affinity because that returns early for a
        # kit with no real school, and the clearest case in the game is
        # exactly that: the Deathguard Captain's kit is entirely physical,
        # and he is still a Forsaken who should fear holy magic.
        self._apply_vulnerability(monster, template_name=template_name,
                                  ability_kit=ability_kit)
        
        # Apply boss multiplier if applicable
        if creature_def.get("is_boss", False):
            boss_multiplier = creature_def.get("boss_multiplier", 2.5)
            monster.is_boss = True
            monster.max_health = int(monster.max_health * boss_multiplier)
            monster.current_health = monster.max_health
            monster.attack_power = int(monster.attack_power * boss_multiplier * 0.75)
            if hasattr(monster, 'spell_power'):
                monster.spell_power = int(monster.spell_power * boss_multiplier * 0.75)
        
        return monster
    
    #: Chance per encounter roll, in a subzone with a real named rare in
    #: its table, that the rare appears instead of ordinary trash. Real
    #: WoW rares are an uncommon "oh, it's actually here" moment, not a
    #: guaranteed one-per-visit fixed spawn (subzones are open-world and
    #: always-on, unlike caves - there's no "clear it, it stays cleared"
    #: dungeon semantics to hang a fixed spawn point off of), so this is
    #: a genuine low-probability roll rather than a scaled-up weight.
    RARE_SPAWN_CHANCE = 0.06

    #: Weight multiplier for creatures an ACTIVE quest still needs killed.
    QUEST_TARGET_WEIGHT_BOOST = 4.0
    #: Chance a subzone roll is a named rare when the player is hunting that very rare for a quest.
    QUEST_RARE_SPAWN_CHANCE = 0.25

    #: beast_lure is the PERCENT a burning Beast Lure adds to every skinnable beast's weight:
    #: 25 (lesser), 50, or 100 (greater). True is read as 50.

    def get_random_creature(self, zone_name, location_type="open_zone", subzone_name=None, quest_targets=None,
                            beast_lure=False):
        """Get a random weighted creature from an encounter table.

        quest_targets (optional set of creature names): kill targets of the player's active, unfinished
        quests.  Those creatures are weighted up, and a quest-target rare appears far more often than
        the ordinary 6%, so a quest never turns into a 1000-step wait for its mob to turn up."""
        encounter_table = self.get_encounter_table(zone_name, location_type, subzone_name)
        quest_targets = set(quest_targets or ())

        if not encounter_table:
            return None

        # Bosses are excluded from the random roll, not just relied on to
        # carry a weight of 0. Weight-0 entries are effectively excluded
        # by random.choices already, but that's a convention, not a
        # guarantee - a random-roll cave's boss (see CaveSpawnManager's
        # place_trash=False caves) is meant to be encountered exactly
        # once, at its pinned chamber, never from this roll. Filtering by
        # is_boss here makes that a real guarantee instead of "don't
        # forget to set weight 0."
        trash_table = {
            name: weight for name, weight in encounter_table.items()
            if not self.creatures.get(name, {}).get("is_boss", False)
        }

        # Subzone rares: named is_boss creatures in a SUBZONE's table
        # (Verog the Dervish in Kolkar Plains, Supervisor Lugwizzle in
        # Sludge Fen, ...) have no cave-style fixed-chamber mechanism to
        # spawn from - subzones aren't discrete maps CaveSpawnManager can
        # place a marker tile in, they're a rectangle inside a bigger
        # always-on overworld map. Without this, marking them is_boss
        # (correctly, so they're not diluting ordinary trash odds) made
        # them completely unreachable: excluded from trash_table above,
        # and nothing else in the game ever rolls for them. This gives
        # them a real, low, independent chance to appear instead of
        # ordinary trash on any roll in their subzone.
        if location_type == "subzone":
            rare_names = [
                name for name in encounter_table
                if self.creatures.get(name, {}).get("is_boss", False)
            ]
            wanted_rares = [n for n in rare_names if n in quest_targets]
            rare_chance = self.QUEST_RARE_SPAWN_CHANCE if wanted_rares else self.RARE_SPAWN_CHANCE
            if rare_names and random.random() < rare_chance:
                chosen_creature = random.choice(wanted_rares or rare_names)
                creature = self.spawn_creature(chosen_creature, zone_name=zone_name)
                if creature:
                    creature.location_type = location_type
                return creature

        if not trash_table:
            return None

        # Weighted random selection
        creatures = list(trash_table.keys())
        weights = [w * (self.QUEST_TARGET_WEIGHT_BOOST if n in quest_targets else 1.0)
                   for n, w in trash_table.items()]
        if beast_lure:
            from entities.skinning_drops import SKINNABLE
            from entities.vendor_trash import classify
            boost = 1.0 + (50 if beast_lure is True else float(beast_lure)) / 100.0
            weights = [w * (boost if classify(n)[0] in SKINNABLE else 1.0)
                       for n, w in zip(creatures, weights)]
        chosen_creature = random.choices(creatures, weights=weights, k=1)[0]
        
        # Spawn creature
        creature = self.spawn_creature(chosen_creature, zone_name=zone_name)
        if creature:
            # Tag with location_type so combat can apply a dungeon/cave XP
            # bonus (see combat_engine._calculate_exp_reward). ZoneManager.
            # get_location_context() now genuinely detects when the player
            # is standing in a subzone or cave and requests the matching
            # table (see its own docstring for that fix's history) - this
            # location_type tag is live and does fire the bonus in actual
            # play, not just wired-but-dormant plumbing.
            creature.location_type = location_type

        return creature
    
    def get_available_subzones(self, zone_name):
        """Get list of subzone names in a zone."""
        if zone_name not in self.encounters:
            return []
        return list(self.encounters[zone_name].get("subzones", {}).keys())
    
    def get_available_caves(self, zone_name):
        """Get list of cave names in a zone."""
        if zone_name not in self.encounters:
            return []
        return list(self.encounters[zone_name].get("caves", {}).keys())
