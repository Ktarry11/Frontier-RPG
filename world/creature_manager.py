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
    #: secondary school it also casts, on Character's 0-60 scale where a
    #: point is half a percent. 40 is 20% off a Fireball aimed at a fire
    #: caster; 60 (the cap, 30%) is reserved for the handful of creatures
    #: whose whole identity is one element, and is reachable by stacking
    #: the template baseline under the affinity.
    CAST_AFFINITY_PRIMARY = 40
    CAST_AFFINITY_SECONDARY = 20

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
        accident."""
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

    def get_random_creature(self, zone_name, location_type="open_zone", subzone_name=None, quest_targets=None):
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
