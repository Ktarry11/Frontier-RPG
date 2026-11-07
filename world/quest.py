"""
Quest system - covers the real types Kyle asked for: kill X, gather X,
explore a zone, fetch quests, boss kills, multi-zone story quests, and
lore quests. Player-authored quests are a stated future goal, not built
yet.

Design decisions, made explicitly rather than guessed:
- One NPC can offer more than one quest, and quests CHAIN (complete A ->
  B becomes available from the same or a different giver). This is
  Kyle's literal example: "kill vile familiars" then "kill the boss".
- Rewards are XP + gold always, PLUS an optional fixed gear CHOICE - not
  a chance roll (Kyle explicitly ruled out random reward chance). A
  quest that offers gear presents exactly one option per relevant armor
  type (cloth/leather/mail/plate), pre-generated once when the quest is
  authored, and the player picks ONE. Not every quest offers gear - most
  don't, per Kyle's "not every quest gives items".
- Reusing the real LootGenerator (entities/loot_generator.py) to build
  those fixed options rather than inventing new item generation, so
  quest gear rolls through the same stat/armor-type/rarity system combat
  loot does and stays consistent as that system gets tuned down later
  (Kyle: "we will tone down equipment soon, it's too OP now" - quest
  gear inherits that tuning for free since it's the same generator).
"""
from enum import Enum


class QuestStatus(Enum):
    NOT_STARTED = "not_started"
    ACTIVE = "active"
    READY_TO_TURN_IN = "ready_to_turn_in"  # objectives complete, hasn't talked to the giver yet
    COMPLETED = "completed"


class ObjectiveType(Enum):
    KILL = "kill"            # kill N of a named monster (by Monster.name)
    KILL_BOSS = "kill_boss"  # kill a specific named boss (is_boss=True enemy)
    GATHER = "gather"        # hold N of a QuestItem/material in inventory (doesn't consume - see FETCH)
    FETCH = "fetch"          # same as gather, but consumed on turn-in (hand the items over)
    EXPLORE = "explore"      # step into a named zone/subzone at least once
    STORY = "story"          # no objective condition - completes immediately on accept,
                              # or is completed externally by a scripted event/cutscene trigger
    DIALOGUE = "dialogue"    # ask the giver NPC about every topic in `topics`, in order - see
                              # QuestObjective.topics/topics_asked and world/quest_dialogue.py
    DELIVER = "deliver"      # carry a quest item (usually handed over by the quest's grant_items) to the
                              # quest's turn_in_npc_id; counted from the bag like FETCH and consumed at turn-in
    CRAFT = "craft"          # make N of a profession recipe (target = recipe id; Blacksmithing recipe id or a
                              # Smelting output id); advanced by QuestManager.record_craft


class QuestObjective:
    """One objective within a quest. Most quests have exactly one;
    multi-part quests (rare, but real - "kill 5 boars AND explore the
    Scorpid Nest") can have more than one, all required."""

    def __init__(self, objective_type, target=None, count=1, zone=None,
                 target_x=None, target_y=None, radius=6, alt_targets=None,
                 topics=None, label=None):
        self.objective_type = objective_type
        #: Optional authored display name for the target (FETCH/GATHER/DELIVER item names, CRAFT recipe names) -
        #: otherwise display_label() derives one from the id.
        self.label = label
        #: For KILL/KILL_BOSS: the monster's real display name (Monster.name),
        #: e.g. "Vile Familiar" or "Yarrog Baneshadow". For GATHER/FETCH: the
        #: LootItem's item_id. For EXPLORE: the zone key. Unused for STORY.
        self.target = target
        self.count = count
        #: Optional additional monster names that ALSO count toward this
        #: same KILL objective's count, alongside `target` - real use
        #: case: "kill 6 Felstalkers" where either a Felstalker Whelp or
        #: a Fel Pup satisfies it, Kyle's explicit "either will count"
        #: spec. Kept separate from `target` (rather than always using a
        #: list) so single-target quests - the overwhelming majority -
        #: don't have to wrap one string in a list, and `target` still
        #: works as the natural "the" monster name for display purposes
        #: (journal summary, etc).
        self.alt_targets = alt_targets or []
        #: Optional zone restriction for KILL/KILL_BOSS - a kill only
        #: counts if it happened in this zone. None means "counts
        #: anywhere", which is correct for most simple kill quests but
        #: wrong for a quest specifically about a named cave's inhabitants
        #: if that monster name isn't unique to that cave.
        self.zone = zone
        #: Optional position gate for EXPLORE objectives - if set, simply
        #: entering `zone`/`target` isn't enough; the player must walk
        #: within `radius` tiles of (target_x, target_y). None means "any
        #: tile in the zone counts", the original simple behavior. Real
        #: use case: "Into the Den" was completing the instant you
        #: stepped through the entrance, since the whole zone was the
        #: explore target - Kyle wanted it to require actually reaching
        #: the connecting hallway deeper in, not just the entry room.
        self.target_x = target_x
        self.target_y = target_y
        self.radius = radius
        #: Live progress counter - how many of `count` are satisfied so
        #: far. Persisted per-quest-instance, not shared across quests
        #: that happen to target the same monster.
        self.progress = 0

        #: DIALOGUE-only. Ordered list of topic_id strings the player must
        #: ask the giver about, in order, to complete this objective - the
        #: actual topic text/branching content lives in
        #: world/quest_dialogue.py, keyed by these same topic_ids, not
        #: here (this is just the completion condition, same separation
        #: KILL keeps between "which monster" and the monster's own
        #: stats/kit). None/empty for every other objective type.
        self.topics = topics or []
        #: DIALOGUE-only. Which topic_ids have actually been asked so far,
        #: in the order asked - a list, not a set, so "asked out of
        #: order" is distinguishable from "asked correctly in order" if a
        #: future quest ever cares about sequence rather than just
        #: coverage. is_complete() only checks coverage (see below); nothing
        #: currently enforces strict ordering, matching Kyle's original
        #: phrasing ("when we ask about durotar, then razor hill, then
        #: maybe org") as a natural/suggested flow rather than a hard
        #: gate - a player who asks Orgrimmar first isn't punished for it,
        #: they just still need to cover the other two before turning in.
        self.topics_asked = []

    def is_complete(self):
        # STORY objectives carry no real condition to track (see
        # ObjectiveType.STORY's docstring) - progress/count default to
        # 0/1 like every other objective type, but nothing ever
        # increments progress for a STORY objective (no kill/fetch/
        # explore event applies), so the inherited progress>=count check
        # below would NEVER be true and the quest could never
        # auto-complete on accept as documented. Confirmed as a real bug
        # (Kyle, 2026-09-10): "A Real Town" (razorhill_welcome) accepted
        # fine but silently could never be turned in. STORY objectives
        # are complete unconditionally, by definition.
        if self.objective_type == ObjectiveType.STORY:
            return True
        if self.objective_type == ObjectiveType.DIALOGUE:
            # Complete once every topic in `topics` has been asked at
            # least once - order doesn't gate completion, see
            # topics_asked's docstring above for why.
            return all(t in self.topics_asked for t in self.topics)
        return self.progress >= self.count

    def ask_topic(self, topic_id):
        """Record that the player asked about topic_id, for a DIALOGUE
        objective. No-op (returns False) for any other objective type, or
        if topic_id isn't one this objective actually tracks - callers
        (world/quest_dialogue.py) can use the return value to decide
        whether to show a "makes no difference" vs a real acknowledgment
        line. Safe to call repeatedly with the same topic_id - re-asking
        something already covered doesn't double-count or break anything,
        it's just a no-op past the first time."""
        if self.objective_type != ObjectiveType.DIALOGUE:
            return False
        if topic_id not in self.topics:
            return False
        if topic_id not in self.topics_asked:
            self.topics_asked.append(topic_id)
        return True

    def matches_target(self, monster_name):
        """True if a kill of this monster should count toward this
        objective - the primary target OR any alt_targets. Centralized
        here rather than inlined at each of the (currently 2, likely
        more later) call sites that need this check, so the "either
        counts" logic only exists in one place."""
        return monster_name == self.target or monster_name in self.alt_targets

    def display_label(self):
        """Human-readable target name for UI (journal, dialog) - a plain
        "Vile Familiar" for a single-target objective, or "Felstalker
        Whelp/Fel Pup" for a multi-target one so the player can actually
        tell either monster counts, instead of the UI silently showing
        only the primary target and looking like the alt kills "don't
        count" when they actually do."""
        if self.objective_type == ObjectiveType.DIALOGUE:
            return "topics"
        if self.label:
            return self.label
        if not self.target:
            return "?"
        names = [self.target] + list(self.alt_targets)
        return "/".join(n.replace("_", " ").title() if "_" in n else n for n in names)

    def to_dict(self):
        return {
            "objective_type": self.objective_type.value,
            "target": self.target,
            "count": self.count,
            "zone": self.zone,
            "progress": self.progress,
            # DIALOGUE-only fields - see __init__'s docstrings. Persisted
            # so a mid-conversation quest (asked 1 of 3 topics, saved,
            # reloaded) doesn't lose that progress - topics itself is the
            # quest's own authored data (re-derivable from the quest JSON
            # on load), but topics_asked is live player state that only
            # exists here.
            "topics": list(self.topics),
            "topics_asked": list(self.topics_asked),
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls(
            objective_type=ObjectiveType(data["objective_type"]),
            target=data.get("target"),
            count=data.get("count", 1),
            zone=data.get("zone"),
            topics=data.get("topics"),
        )
        obj.progress = data.get("progress", 0)
        obj.topics_asked = data.get("topics_asked", [])
        return obj


class QuestRewardGearChoice:
    """One fixed gear reward option offered on a quest - pre-generated
    once (not rolled at turn-in time) so the SAME four options are shown
    every time this quest is viewed, and picking one is a real informed
    choice rather than a slot-machine pull. See build_reward_gear_set()
    for how the real four (cloth/leather/mail/plate) get generated."""

    def __init__(self, armor_type_label, item):
        #: Display label for the choice button ("Cloth (Int)", "Plate (Str)") -
        #: kept separate from item.armor_type since accessory/weapon
        #: choices don't map 1:1 onto an armor type.
        self.armor_type_label = armor_type_label
        self.item = item  # a real entities.item.Item


class Quest:
    """One quest definition + its live per-character progress state.

    A single Quest object represents both the authored template (title,
    giver, objectives-as-designed, reward rules) AND live progress once
    accepted - there's no separate "QuestTemplate vs QuestInstance"
    split, since this game has one save-file player (not a shared quest
    pool across multiple characters), so keeping them merged avoids a
    layer of indirection nothing here needs yet.
    """

    def __init__(self, quest_id, title, description, giver_npc_id, zone,
                 objectives, reward_exp=0, reward_gold=0,
                 gear_reward_gear_level=None, next_quest_id=None,
                 turn_in_text="", accept_text="", level_min=1, level_max=None,
                 gear_reward_slot="chest", gear_reward_rarity="uncommon",
                 gear_reward_choices_plan=None, unique_item_defs=None,
                 requires_quests=None, turn_in_npc_id=None, grant_items=None,
                 reward_recipe=None):
        self.quest_id = quest_id
        #: Extra prerequisites beyond the next_quest_id chain: quest ids (any zone) that must ALL be COMPLETED
        #: before this quest is offered - Linken's-Sword-style gates ("skip A in Durotar and C never opens").
        self.requires_quests = list(requires_quests or [])
        #: NPC who collects this quest, when that is NOT the giver (deliver / "report to" quests, possibly in
        #: another zone).  None = the giver.
        self.turn_in_npc_id = turn_in_npc_id
        #: Quest-item grants: {"on_accept": [item defs], "on_turn_in": [item defs]}; an item def is
        #: {item_id, name, description, count?, starts_quest_id?}.
        self.grant_items = grant_items or {}
        # A recipe id handed over on turn-in, as a learnable scroll. Separate from grant_items
        # because those are LootItems (quest tokens, materials) and a scroll is an Item with a
        # recipe_id - different class, different inventory behaviour, and the UI learns from it on
        # click. Kyle, 2026-10-28: "or still reward some through quests".
        self.reward_recipe = reward_recipe
        self.title = title
        self.description = description
        #: npc_id of the ambient/vendor NPC who offers and collects this
        #: quest - see world/ambient_npc_manager.py / vendor_manager.py.
        self.giver_npc_id = giver_npc_id
        self.zone = zone
        self.objectives = objectives  # list[QuestObjective]
        self.reward_exp = reward_exp
        self.reward_gold = reward_gold  # copper, matches Party.copper's unit
        #: Intended level range - level_min gates acceptance (see
        #: QuestManager.get_offerable_quests), level_max is the point
        #: above which reward scaling starts tapering (see
        #: get_scaled_rewards). level_max=None means "no taper ceiling" -
        #: appropriate for a late quest that should still feel worth
        #: doing well past its intended level. Kyle's explicit ruling:
        #: "you're not going to see a level 60 kill a level 5 boss and
        #: get the same exp as a level 2 doing it" - so reward scaling is
        #: real, not cosmetic.
        self.level_min = level_min
        self.level_max = level_max
        #: If set, this quest offers a fixed gear CHOICE on turn-in,
        #: generated once at gear_level via build_reward_gear_set() and
        #: cached in self.gear_choices - None means no gear reward at all
        #: (most quests, per Kyle's "not every quest gives items").
        self.gear_reward_gear_level = gear_reward_gear_level
        #: "chest" (armor-type choice: cloth/leather/mail/plate) or
        #: "weapon" (stat-template choice: str/agi/int) - which fixed
        #: 4-way set build_reward_gear_set builds. Kyle's ask: "One quest
        #: should give weapon options, we can keep the chest piece option
        #: for one" - so this needs to vary per quest, not always chest.
        self.gear_reward_slot = gear_reward_slot
        #: Real rarity for the reward set - defaults to "uncommon"
        #: (green) but a quest can specify "common" (white, armor-value
        #: only, no stats - real WoW convention) for early/minor quests.
        #: Kyle: "Not everything needs greens though. Whites are
        #: standard at the start."
        self.gear_reward_rarity = gear_reward_rarity
        #: Optional explicit (type_id, stat_template, label) list -
        #: overrides build_reward_gear_set's default plan for this
        #: quest's slot type, letting a specific quest offer a smaller
        #: or larger set than the default 4 (Kyle: "It can be 2, 3, 4,
        #: upwards of 6. It just needs to make sense"). None uses the
        #: sensible default plan for gear_reward_slot.
        self.gear_reward_choices_plan = gear_reward_choices_plan
        #: Optional list of hand-authored unique item dicts (see
        #: build_unique_reward_set) - when set, get_gear_choices uses
        #: THESE fixed items instead of calling the procedural
        #: LootGenerator at all. Kyle: "rewards for each quest should be
        #: unique, this will be where unique named stuff will start to
        #: appear. not always better than drops though, just specific."
        #: A quest can offer unique items alongside or instead of
        #: procedural ones - gear_reward_gear_level being set still
        #: drives get_gear_choices() being called, this just changes
        #: which generator function it calls internally.
        self.unique_item_defs = unique_item_defs
        self.gear_choices = None  # populated lazily - see get_gear_choices()
        #: Chains to another quest - completing this quest makes
        #: next_quest_id available (typically from the same giver, but
        #: not required to be - a chain CAN hand off to a different NPC).
        self.next_quest_id = next_quest_id
        #: Flavor text shown when accepting / when returning to turn in -
        #: separate from `description` (the journal's persistent summary).
        self.accept_text = accept_text
        self.turn_in_text = turn_in_text

        self.status = QuestStatus.NOT_STARTED

    @property
    def collector_npc_id(self):
        """Who this quest is handed in to."""
        return self.turn_in_npc_id or self.giver_npc_id

    def is_complete(self):
        return all(o.is_complete() for o in self.objectives)

    def get_scaled_exp_reward(self, player_level):
        """XP reward scaled by the quest's difficulty band against the
        party's average level - the same WoW con-colour system kills use
        (combat/difficulty.py), so a yellow quest and a yellow mob mean
        the same thing. Gold and gear rewards are NEVER scaled - Kyle's
        explicit ruling: only EXP adjusts for level difference.

        `player_level` is a misnomer kept for call compatibility: callers
        pass the PARTY AVERAGE (see QuestManager.turn_in). Kyle, 4 Nov:
        "this should be based on the average party level to simplify
        stuff."

        This used to hand-roll its own +-5 breakpoints and its docstring
        said they mirrored combat's. They are now one shared function
        instead of two copies that agreed by convention.

        A grey quest still pays difficulty.GREY_QUEST_MULTIPLIER rather
        than nothing - unlike a grey kill, which pays zero.

        The global QUEST_EXP_MULTIPLIER rate is applied once at the end,
        for the same reason combat applies its own at the end: so the
        level-difference bonus is scaled along with the base rather than
        escaping it. Restructured to a single return for that reason -
        three separate returns meant three places to remember to apply it.
        """
        from config import QUEST_EXP_MULTIPLIER
        from combat.difficulty import quest_xp_multiplier

        reward = self.reward_exp * quest_xp_multiplier(self.quest_level, player_level)
        return max(1, int(reward * QUEST_EXP_MULTIPLIER))

    @property
    def quest_level(self):
        """The level this quest cons at.

        level_max where set, else level_min - level_max represents where the
        quest stops being a real challenge, which is the more meaningful
        anchor for "was this a stretch for you" than the entry level.

        A property rather than a local, because the quest journal needs the
        same number to draw the same colour the XP was paid at. Two places
        deciding separately what level a quest "is" would let the badge and
        the payout disagree.
        """
        return self.level_max if self.level_max is not None else self.level_min

    def get_gear_choices(self, loot_generator, char_class):
        """Lazily build and cache this quest's fixed gear reward options.
        Cached on the Quest instance so re-opening the reward screen
        shows the exact same four items, not a fresh roll each time -
        real fixed choices, not a re-rollable slot machine.

        Unique hand-authored items (unique_item_defs) take priority over
        the procedural generator when both are somehow set - a quest
        with real named rewards shouldn't have them silently replaced by
        generic procedural ones."""
        if self.gear_reward_gear_level is None and not self.unique_item_defs:
            return []
        if self.gear_choices is None:
            if self.unique_item_defs:
                self.gear_choices = build_unique_reward_set(self.unique_item_defs)
            else:
                self.gear_choices = build_reward_gear_set(
                    loot_generator, self.gear_reward_gear_level,
                    slot=self.gear_reward_slot, rarity=self.gear_reward_rarity,
                    choices_plan=self.gear_reward_choices_plan)
        return self.gear_choices

    def to_dict(self):
        return {
            "quest_id": self.quest_id,
            "status": self.status.value,
            "objectives": [o.to_dict() for o in self.objectives],
        }

    def apply_saved_state(self, data):
        """Restore live progress from a save - the authored fields
        (title/description/rewards/chain) always come from the JSON
        definition, never from the save file, so a quest's design can be
        tuned after a save was made without corrupting that save's
        progress. Only status + objective progress round-trip."""
        self.status = QuestStatus(data.get("status", "not_started"))
        saved_objectives = {o["target"]: o for o in data.get("objectives", [])}
        for objective in self.objectives:
            saved = saved_objectives.get(objective.target)
            if saved:
                objective.progress = saved.get("progress", 0)


#: Quest rewards are meant to stand out from what a mob of the same level drops (Kyle: "quest rewards are unremarkable
#: in stats, level 10 rewards giving this?").  Authored quest items are built on the same stat budget as a drop of
#: their item level, so at runtime every unique reward is lifted: +2 item levels and, once rare gear exists
#: (item level 10+), one rarity tier above a drop - a green becomes a blue, like WoW's quest rewards.  Done here, not
#: in the data, so rebuilding a quest file never undoes it and the authored JSON stays the baseline.
QUEST_REWARD_ILVL_BONUS = 0   # retired, see apply_quest_reward_bonus
#: On top of the item-level/rarity lift, quest gear gets a flat premium on its stat budget so the numbers are obviously
#: better than a drop (a level-10 bracer was +1 Int/+1 Sta).  Stats are set from the REAL loot budget formula
#: (ilvl * 0.36 * rarity * slot weight * premium) and never go below what the item was authored with, so items that were
#: already generous aren't inflated further.  Armor takes a smaller premium; weapon damage none (weapon damage is the
#: dominant damage term, so quest weapons must not outrun boss weapons).
QUEST_STAT_PREMIUM = 1.0
QUEST_ARMOR_PREMIUM = 1.0
QUEST_WEAPON_PREMIUM = 1.0
_ITEM_DATA = None


def _item_data():
    global _ITEM_DATA
    if _ITEM_DATA is None:
        import json, os
        base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "items")
        try:
            def load(n):
                with open(os.path.join(base, n), encoding="utf-8") as fh:
                    return json.load(fh)
            _ITEM_DATA = {"rarity": {k: v["stat_budget_multiplier"] for k, v in load("rarity.json")["rarity_tiers"].items()},
                          "slots": load("slots.json"), "weapons": load("weapon_types.json")["weapon_types"]}
        except (OSError, ValueError, KeyError):
            _ITEM_DATA = {"rarity": {"uncommon": 1.3, "rare": 1.7}, "slots": None, "weapons": {}}
    return _ITEM_DATA


def _slot_weight(item_def):
    data = _item_data()
    wt = item_def.get("weapon_type")
    if wt:
        w = data["weapons"].get(wt, {})
        tier = "weapon_two_hand" if w.get("hand") == "two_hand" else "weapon_medium"
        weights = (data["slots"] or {}).get("weight_tiers", {})
        return weights.get(tier, 0.75) * w.get("budget_multiplier", 1.0)
    slots = (data["slots"] or {}).get("slots", {})
    tier = slots.get(item_def.get("slot"), {}).get("weight_tier", "minor")
    return (data["slots"] or {}).get("weight_tiers", {}).get(tier, 0.5)


def apply_quest_reward_bonus(item_def):
    """Quest rewards are used exactly as authored.  (Retired 2026-10-22: the old runtime lift - +2 item levels, green -> blue
    at ilvl 10, 1.5x stats - turned almost every quest into a blue.  Rarity and stats are now set in the data by
    tools/retier_quest_rewards.py, using the same stat budget as drops of that item level.)"""
    return dict(item_def)


def build_unique_reward_set(item_defs):
    """Fixed, hand-authored unique reward items - real named gear
    instead of the procedural generator's "Reinforced Breastplate"
    naming. Kyle: "rewards for each quest should be unique, this will be
    where unique named stuff will start to appear. not always better
    than drops though, just specific."

    item_defs: list of dicts, each with the real Item constructor fields
    needed for a fixed piece - at minimum name/slot/item_level/rarity,
    plus whichever of armor_type/weapon_type/stat_template/primary_stats/
    armor_value/weapon_damage_min/weapon_damage_max/attack_speed/
    flavor_text/required_level apply to that specific item. No stat
    rolling happens here at all - every value in item_defs is exactly
    what ends up on the item, which is the whole point of "unique": it
    doesn't vary between playthroughs or level up with item_level like
    procedural gear does.
    """
    import uuid
    from entities.item import Item

    choices = []
    for item_def in item_defs:
        item_def = apply_quest_reward_bonus(item_def)
        item_id = item_def.get("item_id") or f"unique_{item_def['name'].lower().replace(' ', '_')}_{uuid.uuid4().hex[:6]}"
        item = Item(
            item_id=item_id,
            name=item_def["name"],
            slot=item_def["slot"],
            item_level=item_def.get("item_level", 1),
            rarity=item_def.get("rarity", "rare"),
            armor_type=item_def.get("armor_type"),
            weapon_type=item_def.get("weapon_type"),
            stat_template=item_def.get("stat_template"),
            primary_stats=item_def.get("primary_stats"),
            secondary_stats=item_def.get("secondary_stats"),
            armor_value=item_def.get("armor_value", 0),
            required_level=item_def.get("required_level", 1),
            sell_price=item_def.get("sell_price", 0),
            flavor_text=item_def.get("flavor_text") or (
                get_weapon_flavor_text(item_def["weapon_type"]) if item_def.get("weapon_type") else ""
            ) or "",
            weapon_damage_min=item_def.get("weapon_damage_min", 0),
            weapon_damage_max=item_def.get("weapon_damage_max", 0),
            attack_speed=item_def.get("attack_speed", 0.0),
            block_value=item_def.get("block_value", 0),
            # SAME SEEDED PICK AS A FIXED BOSS DROP. A unique quest reward is
            # authored exactly like one, and it passed icon_id straight
            # through - which almost no entry sets, so these rendered as a
            # flat rarity-coloured box with the name written on it. Seeded on
            # the name so the reward shown in the quest dialog, the one in the
            # bag and the one on the character sheet are the same picture.
            icon_id=item_def.get("icon_id") or _reward_icon(item_def),
        )
        label = item_def.get("label", item.name)
        choices.append(QuestRewardGearChoice(label, item))
    return choices


def _reward_icon(item_def):
    """Stable icon for one authored quest reward, seeded on its name.

    None if the slot has no icon family, which keeps the old coloured-box
    rendering for anything gear_icons.py cannot match rather than inventing a
    wrong picture.
    """
    try:
        from gear_icons import pick_armor_icon, pick_weapon_icon
    except ImportError:
        return None
    seed = f"questreward:{item_def.get('name', '')}"
    weapon_type = item_def.get("weapon_type")
    if weapon_type:
        return pick_weapon_icon(weapon_type, seed=seed)
    return pick_armor_icon(item_def.get("slot"), item_def.get("armor_type"), seed=seed)


def build_reward_gear_set(loot_generator, item_level, slot="chest", rarity="uncommon", choices_plan=None):
    """A fixed gear reward choice, generated ONCE per call (callers -
    Quest.get_gear_choices - cache the result so this never re-rolls on
    UI redraw). Not limited to exactly four options (Kyle: "We don't
    need to limit rewards to just 4 items. It can be 2, 3, 4, upwards of
    6. It just needs to make sense") - the real count comes from
    choices_plan, or a sensible default plan per slot type if the caller
    doesn't specify one.

    slot: "chest" (or any real armor slot key) for an armor-type choice
    set, or "weapon" for a weapon-type choice set - these use genuinely
    different plans since armor varies by armor_type (cloth/leather/
    mail/plate) while weapons vary by weapon_type (sword/dagger/staff/...).

    rarity: real rarity tier for every option in the set - "uncommon"
    (green) by default, but Kyle's ruling applies: "Not everything needs
    greens though. Whites are standard at the start" - pass "common" for
    an early/minor quest's reward set. All options share one rarity;
    mixing rarities within a single choice set isn't a real use case.

    choices_plan: optional explicit list of (type_id, stat_template,
    label) tuples, letting a specific quest hand-author a smaller or
    larger set than the default (e.g. a caster-only quest offering just
    2 int-only options, or a general quest offering all 6 weapon types).
    None uses DEFAULT_ARMOR_PLAN or DEFAULT_WEAPON_PLAN based on `slot`.
    """
    DEFAULT_ARMOR_PLAN = [
        ("cloth", "int_caster", "Cloth (Int)"),
        ("leather", "agi_physical", "Leather (Agi)"),
        ("mail", "int_caster", "Mail (Int)"),
        ("plate", "str_physical", "Plate (Str)"),
    ]
    # Weapon plan mirrors the armor plan's "one option per stat
    # template" spirit, using broadly-compatible weapon_types (see
    # data/items/weapon_types.json's valid_stat_templates) rather than
    # armor_type, since weapons don't have an armor-type axis at all.
    DEFAULT_WEAPON_PLAN = [
        ("sword_1h", "str_physical", "Sword (Str)"),
        ("dagger", "agi_physical", "Dagger (Agi)"),
        ("staff", "int_caster", "Staff (Int)"),
        ("mace_1h", "str_physical", "Mace (Str)"),
    ]

    if choices_plan is None:
        choices_plan = DEFAULT_WEAPON_PLAN if slot == "weapon" else DEFAULT_ARMOR_PLAN

    choices = []
    for type_id, stat_template, label in choices_plan:
        if slot == "weapon":
            item = loot_generator.generate_weapon(
                slot="main_hand", weapon_type=type_id, stat_template=stat_template,
                item_level=item_level, rarity=rarity)
            # Real quest-flavor line per weapon_type (Kyle's Earth-arrival
            # one-liners, this session) - applies even to white/common
            # weapon rewards, not just green+ ones, per Kyle's explicit
            # "they need flavor text even if they're just white".
            item.flavor_text = get_weapon_flavor_text(type_id) or item.flavor_text
        else:
            item = loot_generator.generate_armor_piece(
                slot=slot, armor_type=type_id, stat_template=stat_template,
                item_level=item_level, rarity=rarity)
        choices.append(QuestRewardGearChoice(label, item))
    return choices


_weapon_flavor_text_cache = None


def get_weapon_flavor_text(weapon_type):
    """Real one-liner flavor text for a weapon_type, from
    data/items/weapon_flavor_text.json - cached at module level since
    this file doesn't change during a session. Returns None (not "") for
    an unmapped weapon_type, so a caller can tell "no flavor text
    defined for this" apart from "this weapon type's real flavor text IS
    an empty string", and fall back to whatever the item already had."""
    global _weapon_flavor_text_cache
    if _weapon_flavor_text_cache is None:
        import json
        from pathlib import Path
        path = Path(__file__).parent.parent / "data" / "items" / "weapon_flavor_text.json"
        try:
            with open(path, "r") as f:
                _weapon_flavor_text_cache = json.load(f).get("weapon_flavor_text", {})
        except (OSError, json.JSONDecodeError):
            _weapon_flavor_text_cache = {}
    return _weapon_flavor_text_cache.get(weapon_type)


class ItemQuestGiver:
    """Stand-in 'NPC' for a quest-starter item: opening the item in the bag opens the quest dialog as if the item
    were the giver (giver id 'item:<item_id>').  Duck-types the bits QuestDialogScreen reads from an NPC."""

    def __init__(self, item):
        self.npc_id = "item:" + item.item_id
        self.name = item.name
        self.greeting = item.description or f"{item.name} has nothing more to say."
        self.zone = None
