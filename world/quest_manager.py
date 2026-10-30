"""
QuestManager - loads quest definitions from data/quests/*.json, tracks
one player's live progress against them, and exposes the real hooks
other systems call into: record_kill() from combat victory,
record_zone_entered() from zone transitions, and gather/fetch progress
read directly off the player's live inventory via entities.loot_item.

Mirrors the load-once-index-by-something shape of VendorManager /
RecruitManager / AmbientNPCManager (see world/vendor_manager.py etc.)
for consistency, though quests differ enough (live per-character state,
not just static placement data) that this isn't a pure copy.
"""
import json
from pathlib import Path

from world.quest import Quest, QuestObjective, QuestStatus, ObjectiveType


class QuestManager:
    def __init__(self):
        self.quests = {}              # quest_id -> Quest (authored definition + live state)
        self.quests_by_giver = {}     # npc_id -> list[quest_id], in authored order
        self.quests_by_collector = {}  # npc_id -> list[quest_id] handed in to that NPC (usually the giver)
        self.last_error = None        # why the last accept_quest refused (shown by the dialog), else None
        # Set by turn_in_quest for one-off scripted companion departures
        # (currently just Asher Coleman's after the Baneshadow quest) -
        # None the rest of the time. See turn_in_quest's docstring.
        self.departure_message = None
        self._load_quests()

    def _load_quests(self):
        quests_dir = Path(__file__).parent.parent / "data" / "quests"
        if not quests_dir.exists():
            return
        for path in sorted(quests_dir.glob("*.json")):
            try:
                with open(path, "r") as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"ERROR: Failed to parse quest file {path.name}: {e}")
                continue

            for q_def in data.get("quests", []):
                quest = self._build_quest(q_def)
                self.quests[quest.quest_id] = quest
                self.quests_by_giver.setdefault(quest.giver_npc_id, []).append(quest.quest_id)
                self.quests_by_collector.setdefault(quest.collector_npc_id, []).append(quest.quest_id)

        # Text overlays: data/quests/text/*.json = {quest_id: {title?, description?, accept_text?, turn_in_text?}}.
        # Writing lives here (not in the generated zone files) so re-running a tools/build_*_quests.py never reverts a rewrite.
        for path in sorted((quests_dir / "text").glob("*.json")):
            try:
                with open(path, "r") as f:
                    overlay = json.load(f)
            except json.JSONDecodeError as e:
                print(f"ERROR: Failed to parse quest text overlay {path.name}: {e}")
                continue
            for quest_id, fields in overlay.items():
                quest = self.quests.get(quest_id)
                if quest is None:
                    print(f"WARNING: quest text overlay {path.name} names unknown quest {quest_id}")
                    continue
                for key in ("title", "description", "accept_text", "turn_in_text"):
                    if fields.get(key):
                        setattr(quest, key, fields[key])

    @staticmethod
    def _slug(s):
        """Zone slug used by every zone-keyed lookup (zone_manager,
        combat_screen): lower-case, spaces -> '_', apostrophes dropped.
        Quest data may be authored with display names ("Ashenvale West")."""
        if not isinstance(s, str):
            return s
        return s.lower().replace(" ", "_").replace("'", "")

    @staticmethod
    def _build_quest(q_def):
        _slug = QuestManager._slug
        objectives = [
            QuestObjective(
                objective_type=ObjectiveType(o["type"]),
                target=(_slug(o.get("target")) if o["type"] == "explore" else o.get("target")),
                count=o.get("count", 1),
                zone=_slug(o.get("zone")),
                target_x=o.get("target_x"),
                target_y=o.get("target_y"),
                radius=o.get("radius", 6),
                alt_targets=o.get("alt_targets"),
                topics=o.get("topics"),
                label=o.get("label"),
            )
            for o in q_def["objectives"]
        ]
        return Quest(
            quest_id=q_def["quest_id"],
            title=q_def["title"],
            description=q_def["description"],
            giver_npc_id=q_def["giver_npc_id"],
            zone=q_def["zone"],
            objectives=objectives,
            reward_exp=q_def.get("reward_exp", 0),
            reward_gold=q_def.get("reward_gold", 0),
            gear_reward_gear_level=q_def.get("gear_reward_gear_level"),
            gear_reward_slot=q_def.get("gear_reward_slot", "chest"),
            gear_reward_rarity=q_def.get("gear_reward_rarity", "uncommon"),
            gear_reward_choices_plan=[
                (c["type_id"], c["stat_template"], c["label"])
                for c in q_def["gear_reward_choices_plan"]
            ] if q_def.get("gear_reward_choices_plan") else None,
            # TWO SPELLINGS, ONE MEANING. Hand-authored reward gear was written under
            # `unique_item_defs` by some builders and `rewards` by others, and only the first was
            # ever read - so 166 quests across 13 zones handed out experience and gold and silently
            # dropped 531 authored items on the floor. Whole zones: hillsbrad 56/57, underdark
            # 30/31, aspen 20/21, southern_needles and underdark_dungeons 17 each. No crash, no
            # warning; you turn the quest in and there is simply no gear on the screen.
            #
            # Measured: quests offering gear went 633 -> 799 of 855. The 56 that still offer none
            # carry no authored gear under either key and pay experience and gold only, which is
            # how they were written.
            #
            # The two schemas are identical (`rewards` additionally carries secondary_stats, which
            # build_unique_reward_set already reads), so this is an alias, not a conversion.
            # `unique_item_defs` deliberately wins: where a quest carries both they are duplicates,
            # except aspen's asp_winch_house where the unique entry is a book and the rewards are
            # gear - so precedence here keeps every already-working quest byte-identical.
            unique_item_defs=q_def.get("unique_item_defs") or q_def.get("rewards"),
            next_quest_id=q_def.get("next_quest_id"),
            accept_text=q_def.get("accept_text", ""),
            turn_in_text=q_def.get("turn_in_text", ""),
            level_min=q_def.get("level_min", 1),
            level_max=q_def.get("level_max"),
            requires_quests=q_def.get("requires_quests"),
            turn_in_npc_id=q_def.get("turn_in_npc_id"),
            grant_items=q_def.get("grant_items"),
            reward_recipe=q_def.get("reward_recipe"),
        )

    # ---------- Giver-facing queries (what does this NPC have to offer right now) ----------

    def get_offerable_quests(self, npc_id):
        """Quests this NPC can currently START offering - NOT_STARTED
        quests whose chain prerequisite (if any) is already COMPLETED.
        A chained quest (next_quest_id points at it) won't appear here
        until its predecessor is turned in - see _is_unlocked.

        Deliberately NOT level-gated here - a quest below the player's
        level range still shows up (so the NPC's exclamation mark and
        the journal both display it), just visually marked as
        unavailable via is_quest_available_to_player. Level gating only
        blocks the actual accept_quest() call, not visibility - Kyle's
        spec calls for a grey marker on a too-low-level quest, which
        requires the quest to still be visible, not hidden."""
        result = []
        for quest_id in self.quests_by_giver.get(npc_id, []):
            quest = self.quests[quest_id]
            if quest.status == QuestStatus.NOT_STARTED and self._is_unlocked(quest_id):
                result.append(quest)
        return result

    def is_quest_available_to_player(self, quest, player_level):
        """Whether player_level actually meets this quest's level_min -
        the real gate accept_quest() enforces, and what the NPC
        indicator (gold vs grey exclamation mark) should be based on.
        level_max is NOT a hard gate (a level 20 can still do a level 5
        quest, just for less XP - see Quest.get_scaled_exp_reward) -
        only level_min blocks acceptance outright."""
        return player_level >= quest.level_min

    def get_turn_in_ready_quests(self, npc_id):
        """Active quests given by this NPC whose objectives are all
        complete and are waiting for the player to talk to this NPC to
        collect the reward."""
        return [
            self.quests[qid] for qid in self.quests_by_collector.get(npc_id, [])
            if self.quests[qid].status == QuestStatus.READY_TO_TURN_IN
        ]

    def get_in_progress_dialogue_quests(self, npc_id):
        """ACTIVE (accepted, not yet complete) quests at this giver that
        have a DIALOGUE objective still awaiting topics - lets the quest
        dialog screen offer topic buttons on a return visit, rather than
        falling through to a flat "nothing more to say" greeting the way
        every other in-progress quest type does (a KILL quest genuinely
        has nothing more to SAY until its kills are done; a DIALOGUE
        quest's entire content IS the conversation, so it needs its own
        mode - see QuestDialogScreen._refresh's "in_progress_dialogue"
        branch). Only returns quests with at least one DIALOGUE objective
        not yet fully asked - a quest that's ACTIVE for some OTHER
        unrelated reason (e.g. a multi-part quest with a still-incomplete
        KILL objective alongside an already-fully-asked DIALOGUE one)
        won't show here, since there's nothing left to ask."""
        result = []
        for qid in self.quests_by_giver.get(npc_id, []):
            quest = self.quests[qid]
            if quest.status != QuestStatus.ACTIVE:
                continue
            has_incomplete_dialogue = any(
                o.objective_type == ObjectiveType.DIALOGUE and not o.is_complete()
                for o in quest.objectives
            )
            if has_incomplete_dialogue:
                result.append(quest)
        return result

    def _is_unlocked(self, quest_id):
        """A quest with no predecessor is always unlocked. A quest that
        IS the next_quest_id of some other quest only unlocks once that
        predecessor is COMPLETED - real chain gating (Kyle's "kill vile
        familiars, then kill the boss" example).  `requires_quests` adds Linken's-Sword-style gates: every listed
        quest (any zone, any giver) must be COMPLETED too."""
        quest = self.quests.get(quest_id)
        if quest is not None:
            for req in quest.requires_quests:
                other = self.quests.get(req)
                if other is None or other.status != QuestStatus.COMPLETED:
                    return False
        # Faction standing gates. Authored in data/factions/factions.json under rewards.quests rather than
        # on the quest, so a faction owns its own unlock list in one place instead of scattering a
        # requires_standing field across other people's zone files.
        from world.faction_manager import get_faction_manager
        if not get_faction_manager().quest_requirement_met(quest_id):
            return False
        predecessor = self._find_predecessor(quest_id)
        if predecessor is None:
            return True
        return predecessor.status == QuestStatus.COMPLETED

    def _find_predecessor(self, quest_id):
        for quest in self.quests.values():
            if quest.next_quest_id == quest_id:
                return quest
        return None

    # ---------- Player-facing actions ----------

    @staticmethod
    def _grant(player, defs, quest_id):
        """Hand quest items to the player (LootItem category 'quest').  Returns False if the bag can't hold them."""
        from entities.loot_item import add_loot_item
        ok = True
        for d in defs or []:
            ok = add_loot_item(player, d["item_id"], d["name"], category="quest", amount=d.get("count", 1),
                               description=d.get("description", ""), icon_id=d.get("icon_id"), quest_id=quest_id,
                               starts_quest_id=d.get("starts_quest_id")) and ok
        return ok

    def accept_quest(self, quest_id, player_level=None, player=None):
        """Accept a quest. player_level is optional for backward
        compatibility with any test/script call that doesn't care about
        gating, but real UI call sites MUST pass it - an ungated accept
        would let a level 1 character take a level 40 quest outright."""
        self.last_error = None
        quest = self.quests.get(quest_id)
        if quest is None or quest.status != QuestStatus.NOT_STARTED:
            return False
        if player_level is not None and not self.is_quest_available_to_player(quest, player_level):
            return False
        on_accept = (quest.grant_items or {}).get("on_accept")
        if on_accept and player is not None:
            free = player.inventory_capacity - len(player.inventory)
            if free < len(on_accept) or not self._grant(player, on_accept, quest_id):
                self.last_error = "Your bag is full - make room for the quest item first."
                return False
        quest.status = QuestStatus.ACTIVE
        # A STORY objective with no real condition completes the instant
        # the quest is accepted, so the quest becomes turn-in-ready right
        # away rather than needing an external trigger that may never fire.
        if quest.is_complete():
            quest.status = QuestStatus.READY_TO_TURN_IN
        return True

    def abandon_quest(self, quest_id):
        """Drop an in-progress quest: back to NOT_STARTED with all objective progress
        wiped, so it can be picked up again from the giver.  Returns True on success.
        Completed quests (and ones never started) cannot be abandoned."""
        quest = self.quests.get(quest_id)
        if quest is None or quest.status not in (QuestStatus.ACTIVE, QuestStatus.READY_TO_TURN_IN):
            return False
        quest.status = QuestStatus.NOT_STARTED
        for objective in quest.objectives:
            objective.progress = 0
            if hasattr(objective, "topics_asked"):
                objective.topics_asked = []
        return True

    def turn_in_quest(self, quest_id, player, party):
        """Award XP/gold, consume any FETCH objective items, and mark
        complete. Does NOT hand out gear - gear choice is a separate
        step (see turn_in_and_pick_gear / the quest reward UI), since
        picking one of four options needs its own screen and this method
        needs to work standalone for gear-less quests (the common case).
        Returns True on success, False if the quest wasn't actually
        ready to turn in."""
        quest = self.quests.get(quest_id)
        if quest is None or quest.status != QuestStatus.READY_TO_TURN_IN:
            return False

        from entities.loot_item import remove_loot_items
        for objective in quest.objectives:
            if objective.objective_type in (ObjectiveType.FETCH, ObjectiveType.DELIVER):
                # Real removal, not just marking progress - a FETCH
                # objective hands the items over, they leave the bag.
                # GATHER objectives (the non-consuming variant) are left
                # alone here on purpose - see ObjectiveType docstring.
                remove_loot_items(player, objective.target, objective.count)

        # Quest-starter items (a drop that began this quest) are spent when it is handed in.
        for item in list(player.inventory):
            if getattr(item, "starts_quest_id", None) == quest_id:
                player.inventory.remove(item)
        on_turn_in = (quest.grant_items or {}).get("on_turn_in")
        if on_turn_in:
            self._grant(player, on_turn_in, quest_id)

        # RECIPE REWARD. Built here rather than in _grant because _grant makes LootItems and a
        # scroll is an Item. A full bag is not allowed to eat the reward silently - the message is
        # stashed for the dialog the same way the faction gain below is.
        self.recipe_reward_message = None
        if getattr(quest, "reward_recipe", None):
            from world.recipe_manager import make_recipe_scroll
            scroll = make_recipe_scroll(quest.reward_recipe)
            if scroll is None:
                print(f"[QuestManager] WARNING: quest {quest_id} rewards unknown recipe "
                      f"{quest.reward_recipe!r}")
            elif player.add_to_inventory(scroll):
                self.recipe_reward_message = f"You received {scroll.name}."
            else:
                self.recipe_reward_message = (
                    f"{scroll.name} could not fit in your bags - make room and speak to them again.")

        if quest.reward_exp:
            scaled_exp = quest.get_scaled_exp_reward(player.level)
            party.award_experience(scaled_exp)
        if quest.reward_gold:
            # Gold is NEVER scaled by level, per Kyle's explicit ruling -
            # only EXP adjusts for level difference (see
            # Quest.get_scaled_exp_reward's docstring for the full
            # reasoning and the formula it mirrors from combat).
            party.add_currency(quest.reward_gold)

        # Faction standing. The amount comes from the quest's ZONE rather than a per-quest field, so the
        # 48 quests already written needed no edit and a new quest in a faction's territory earns standing
        # by existing (world/faction_manager.quest_reward). Stashed on self the same way result_message and
        # departure_message are, for the dialog UI to render after this returns.
        from world.faction_manager import get_faction_manager
        self.faction_gain = get_faction_manager().award_for_quest(quest)

        quest.status = QuestStatus.COMPLETED

        # Asher Coleman leaves the party permanently the moment this
        # specific quest is turned in (Kyle, 2026-09-07: "after the
        # baneshadow quest he leaves the party to 'explore' the world").
        # Scripted here rather than as a general "companion leaves on
        # quest X" data-driven system - this is a one-off story beat for
        # one specific character, not a reusable mechanic, so a small
        # explicit check is more honest than building a generic system
        # for a single current use. self.departure_message is picked up
        # by the quest dialog UI (see ui/screens/quest_dialog_screen.py)
        # right after this call returns, the same way result_message
        # already works there - kept as a separate attribute rather than
        # changing this method's bool return type, so every existing
        # caller of turn_in_quest keeps working unmodified.
        self.departure_message = None
        if quest_id == "vot_yarrog_baneshadow":
            asher = next((m for m in party.members + party.bench
                          if getattr(m, "recruit_id", None) == "asher_coleman"), None)
            if asher is not None:
                party.remove_member(asher)
                self.departure_message = (
                    "Asher looks out past the ridge for a long moment before he "
                    "speaks. \"Whatever's out there, I expect it's got more of "
                    "what we just put down. Reckon I'll go looking for it myself, "
                    "if it's all the same to you.\" He doesn't wait for an answer. "
                    "Asher has left the party."
                )

        return True

    def grant_gear_choice(self, quest, choice_index, player):
        """Add the picked gear option to the player's inventory. Separate
        call from turn_in_quest so the reward screen can turn the quest
        in first (locking in XP/gold immediately) and then let the
        player deliberate on which gear piece to take, without losing
        the XP/gold if they back out of the gear screen. Returns True if
        it fit in the bag, False if the bag was full (Kyle's existing
        add_to_inventory contract - caller must check)."""
        choices = quest.gear_choices or []
        if not (0 <= choice_index < len(choices)):
            return False
        item = choices[choice_index].item
        return player.add_to_inventory(item)

    # ---------- Progress-tracking hooks (called by other systems) ----------

    def record_kill(self, monster_name, zone, is_boss=False):
        """Called from combat's victory resolution for every defeated
        enemy (see combat/combat_engine.py _resolve_victory). Advances
        every ACTIVE quest with a matching KILL or KILL_BOSS objective -
        a single kill can advance multiple quests at once if the player
        has more than one active quest targeting the same monster,
        exactly like real WoW kill-credit sharing."""
        for quest in self.quests.values():
            if quest.status != QuestStatus.ACTIVE:
                continue
            advanced = False
            for objective in quest.objectives:
                wants_boss = objective.objective_type == ObjectiveType.KILL_BOSS
                wants_normal = objective.objective_type == ObjectiveType.KILL
                if not (wants_boss or wants_normal):
                    continue
                # KILL_BOSS objectives require the creature to actually be a
                # boss (is_boss=True). Plain KILL objectives accept any kill -
                # boss or normal - so named boss mobs (e.g. "Broodmother Sarrix",
                # "Bramblethorn the Ancient") count toward kill objectives
                # authored as type="kill". The old check (wants_boss != is_boss)
                # silently blocked boss kills from satisfying plain KILL objectives.
                if wants_boss and not is_boss:
                    continue
                if not objective.matches_target(monster_name):
                    continue
                if objective.zone and objective.zone != zone:
                    continue
                if objective.is_complete():
                    continue
                objective.progress += 1
                advanced = True
            if advanced and quest.is_complete():
                quest.status = QuestStatus.READY_TO_TURN_IN

    def record_craft(self, recipe_id, count=1):
        """Called by the profession managers after a successful craft/smelt (recipe id or smelting output id).
        Advances every ACTIVE quest with a matching CRAFT objective."""
        for quest in self.quests.values():
            if quest.status != QuestStatus.ACTIVE:
                continue
            advanced = False
            for objective in quest.objectives:
                if objective.objective_type != ObjectiveType.CRAFT or objective.target != recipe_id:
                    continue
                if objective.is_complete():
                    continue
                objective.progress = min(objective.count, objective.progress + count)
                advanced = True
            if advanced and quest.is_complete():
                quest.status = QuestStatus.READY_TO_TURN_IN

    def record_zone_entered(self, zone):
        """Called on zone transition (see world/zone_manager.py). Advances
        any ACTIVE quest with a plain (non-position-gated) EXPLORE
        objective targeting this zone. Position-gated EXPLORE objectives
        (target_x/target_y set) are NOT advanced here - they need
        record_position_reached instead, since simply entering the zone
        isn't the real trigger for those (see QuestObjective's
        target_x/target_y docstring)."""
        for quest in self.quests.values():
            if quest.status != QuestStatus.ACTIVE:
                continue
            advanced = False
            for objective in quest.objectives:
                if objective.objective_type != ObjectiveType.EXPLORE:
                    continue
                if objective.target != zone:
                    continue
                if objective.target_x is not None:
                    continue  # position-gated - handled by record_position_reached
                if objective.is_complete():
                    continue
                objective.progress = objective.count  # explore is binary - visited or not
                advanced = True
            if advanced and quest.is_complete():
                quest.status = QuestStatus.READY_TO_TURN_IN

    def record_position_reached(self, zone, x, y):
        """Called on every successful player move (see
        world/zone_manager.py move_player) - advances any ACTIVE quest
        with a position-gated EXPLORE objective (target_x/target_y set)
        whose zone matches and whose target position is within radius of
        (x, y). Cheap no-op for the overwhelming majority of moves, since
        most quests have no active position-gated objective at all - the
        zone/target_x checks below short-circuit before any real
        distance math runs."""
        for quest in self.quests.values():
            if quest.status != QuestStatus.ACTIVE:
                continue
            advanced = False
            for objective in quest.objectives:
                if objective.objective_type != ObjectiveType.EXPLORE:
                    continue
                if objective.target != zone or objective.target_x is None:
                    continue
                if objective.is_complete():
                    continue
                dx = x - objective.target_x
                dy = y - objective.target_y
                if (dx * dx + dy * dy) ** 0.5 <= objective.radius:
                    objective.progress = objective.count
                    advanced = True
            if advanced and quest.is_complete():
                quest.status = QuestStatus.READY_TO_TURN_IN

    def refresh_gather_progress(self, player):
        """GATHER and FETCH objectives both track live inventory count
        rather than an incrementing counter, since the player could gain
        AND lose the item (selling it, bag pressure) between checks. The
        only difference between the two types is what happens AT
        turn-in (FETCH consumes the items, GATHER doesn't - see
        turn_in_quest) - progress display works identically for both, so
        both are refreshed here rather than needing two near-duplicate
        methods. Called whenever the quest journal is opened so displayed
        progress is always accurate to current bag contents, not whatever
        it was last time a kill/zone-entry event fired."""
        from entities.loot_item import count_loot_items
        for quest in self.quests.values():
            if quest.status not in (QuestStatus.ACTIVE, QuestStatus.READY_TO_TURN_IN):
                continue
            has_gather_or_fetch = any(
                o.objective_type in (ObjectiveType.GATHER, ObjectiveType.FETCH, ObjectiveType.DELIVER)
                for o in quest.objectives
            )
            if not has_gather_or_fetch:
                continue
            for objective in quest.objectives:
                if objective.objective_type not in (ObjectiveType.GATHER, ObjectiveType.FETCH, ObjectiveType.DELIVER):
                    continue
                have = count_loot_items(player, objective.target)
                objective.progress = min(have, objective.count)
            # Recompute status both ways - READY_TO_TURN_IN if everything
            # is now complete, but back down to ACTIVE if the player sold
            # or otherwise lost a required item after reaching the
            # threshold (e.g. a FETCH item accidentally vendored before
            # walking back to the giver). Never touches quests that were
            # already fully COMPLETED.
            if quest.status in (QuestStatus.ACTIVE, QuestStatus.READY_TO_TURN_IN):
                quest.status = QuestStatus.READY_TO_TURN_IN if quest.is_complete() else QuestStatus.ACTIVE

    def still_needs_item(self, player, item_id):
        """True if ANY active (or ready-to-turn-in) quest's GATHER/FETCH
        objective still wants more of this item_id than the player
        currently has. False once every such objective is already
        satisfied - the gate combat_engine's quest-item drop roll checks
        BEFORE rolling, so kills stop dropping an item the instant the
        player has enough for every quest that needs it (Kyle's bug
        report: killing Vile Familiars/Felstalkers past the required
        count kept dropping more quest items with no way to get rid of
        them, since quest-category LootItems are never sellable by
        design - see LootItem.is_sellable). Items dropped from OTHER
        sources (a non-quest kill, a chest) aren't affected by this at
        all; this only gates the quest_drops.json roll in
        combat_engine._resolve_victory.

        If NO active quest references this item_id the answer is False (changed 2026-10-23): quest items only drop for
        players who have actually accepted a quest that needs them."""
        from entities.loot_item import count_loot_items
        starter = self.quests_started_by_item(item_id)
        if starter:
            # A quest-starter drop: only while that quest is still open to this player and they don't hold it yet.
            return (any(q.status == QuestStatus.NOT_STARTED and self._is_unlocked(q.quest_id) for q in starter)
                    and count_loot_items(player, item_id) == 0)
        found_any_objective = False
        for quest in self.quests.values():
            if quest.status not in (QuestStatus.ACTIVE, QuestStatus.READY_TO_TURN_IN):
                continue
            for objective in quest.objectives:
                if objective.objective_type not in (ObjectiveType.GATHER, ObjectiveType.FETCH):
                    continue
                if objective.target != item_id:
                    continue
                found_any_objective = True
                have = count_loot_items(player, item_id)
                if have < objective.count:
                    return True
        # Kyle (2026-10-23): "mobs drop quest items without even picking up the quests". A quest item now drops ONLY while
        # an active quest still wants it - nothing active references it -> no drop (kills never clog bags with dead weight).
        return False

    def quests_started_by_item(self, item_id):
        """Quests whose giver is the starter item `item_id` (giver id 'item:<item_id>')."""
        return [self.quests[q] for q in self.quests_by_giver.get("item:" + item_id, [])]

    # ---------- Journal queries ----------

    def get_indicator_for_npc(self, npc_id, player_level):
        """What marker (if any) this NPC should show above their head in
        the overworld, per Kyle's spec: gold "!" when a quest is
        available and the player meets its level, grey "!" when
        available but too low level, gold "?" when ready to turn in,
        grey "?" reserved for a turn-in the player can't actually
        collect yet (not currently reachable - turn-in has no level
        gate - kept for symmetry/future use, e.g. a faction-gated
        turn-in later). Returns one of "gold_exclaim", "grey_exclaim",
        "gold_question", "grey_question", or None for nothing to show.

        Turn-in takes priority over offering a new quest - an NPC who
        both has a quest ready to collect AND a new quest to offer shows
        the "?" first, matching the real WoW convention of clearing what
        you're already holding before piling on more.
        """
        if self.get_turn_in_ready_quests(npc_id):
            return "gold_question"

        # An accepted-but-not-yet-complete DIALOGUE quest at this NPC
        # needs its own marker - previously fell through this whole
        # method with no check at all (neither turn-in-ready NOR
        # offerable, since it's already been accepted), so Grokk showed
        # NO indicator after accepting "A Real Town" but before asking
        # any topics - nothing on screen told the player there was an
        # unfinished conversation to go back to. Uses the same gold "!"
        # as an available new quest - a DIALOGUE quest in progress reads
        # the same as "come talk to me", which is accurate here.
        if self.get_in_progress_dialogue_quests(npc_id):
            return "gold_exclaim"

        offerable = self.get_offerable_quests(npc_id)
        if not offerable:
            return None
        # If ANY offerable quest is actually available at the player's
        # level, show gold - only show grey if EVERY offerable quest is
        # currently out of reach (matches "grey if you're too low level"
        # as a per-NPC summary rather than needing per-quest markers on
        # the overworld, which the journal handles instead).
        if any(self.is_quest_available_to_player(q, player_level) for q in offerable):
            return "gold_exclaim"
        return "grey_exclaim"

    def get_active_quests(self):
        return [q for q in self.quests.values()
                if q.status in (QuestStatus.ACTIVE, QuestStatus.READY_TO_TURN_IN)]

    def get_completed_quests(self):
        return [q for q in self.quests.values() if q.status == QuestStatus.COMPLETED]

    # ---------- Save/load ----------

    def to_dict(self):
        """Only live per-quest state round-trips (status + objective
        progress) - authored fields always reload from the JSON
        definition on the next launch, see Quest.apply_saved_state."""
        return {"quest_states": [q.to_dict() for q in self.quests.values()
                                  if q.status != QuestStatus.NOT_STARTED]}

    def load_from_dict(self, data):
        for q_state in data.get("quest_states", []):
            quest = self.quests.get(q_state["quest_id"])
            if quest:
                quest.apply_saved_state(q_state)


_quest_manager = None


def get_quest_manager():
    """Module-level singleton, same access pattern as
    world.recruit_manager.get_recruit_manager() /
    world.ambient_npc_manager.get_ambient_npc_manager()."""
    global _quest_manager
    if _quest_manager is None:
        _quest_manager = QuestManager()
    return _quest_manager
