"""
Game state machine. Manages transitions between different game states.
"""
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from core.game_states import GameState
from ui.screens.menu_screen import MenuScreen
from ui.screens.character_screen import CharacterCreationScreen
from ui.screens.character_sheet_screen import CharacterSheetScreen
from ui.screens.skills_screen import SkillsScreen
from ui.screens.professions_screen import ProfessionsScreen
from ui.screens.map_screen import MapScreen
from ui.screens.inventory_screen import InventoryScreen
from ui.screens.vendor_screen import VendorScreen
from ui.screens.quest_dialog_screen import QuestDialogScreen
from ui.screens.quest_journal_screen import QuestJournalScreen
from ui.screens.talent_tree_screen import TalentTreeScreen
from ui.screens.overworld_screen import OverworldScreen
from ui.screens.party_screen import PartyScreen
from ui.screens.combat_screen import CombatScreen
from ui.screens.pet_screen import PetScreen
from ui.screens.totem_screen import TotemScreen
from ui.screens.form_screen import FormScreen
from ui.screens.guardian_screen import GuardianScreen
from ui.screens.cast_screen import CastScreen
from ui.screens.background_screen import BackgroundScreen
from ui.screens.bond_test_screen import BondTestScreen
from ui.screens.travel_service_screen import TravelServiceScreen
from config import save_slot_filename


class GameStateManager:
    """Manages game state transitions and delegates updates/renders to active state."""
    
    def __init__(self, screen):
        self.screen = screen
        # MapScreen reads the live ZoneManager, which is owned by
        # OverworldScreen. Published here on construction so the map works
        # even if opened before the overworld has handled its first keypress.
        self.zone_manager = None
        self.current_state = GameState.MENU
        self._entered_state_fresh = False  # True for exactly one _ensure_*_screen() call right after a transition_to
        self.player = None
        # Which save file this session is playing; set by load_game/save_game.
        # The guild bank commits against it - see _remember_slot.
        #
        # NONE, NOT "character.json". A character that has never been saved
        # OWNS NO SLOT, and the difference is the whole of the save-clobber
        # bug Kyle's tester hit on 7 Nov: "I just made a shaman and used the
        # +5 level thing and saved it but it over wrote my level 13 druid."
        #
        # Defaulting to a filename meant a brand-new character was born
        # already pointing at a real save file - either slot 1 (which
        # config.save_slot_filename maps "character.json" to) or, worse,
        # whatever slot the PREVIOUS character had loaded, because this
        # field survives character creation. Character creation then calls
        # save_game() with no filename, and the new level-1 shaman landed
        # on top of the level-13 druid before the player saw the world.
        #
        # The same root cause is the tester's second report, "I saved to
        # slot 3 and it saved it on slot 8": the character was written to
        # slot 8 at creation (the slot still current from the druid) and to
        # slot 3 when they asked for it, so it appeared in two places and
        # read as random.
        self.current_save_file = None
        #: Set by character creation; read once by MenuScreen, which opens
        #: the slot picker so the new character is given a home before the
        #: world is entered.
        self.pending_new_character = False
        self.current_enemy = None
        self.current_enemies = []
        self.current_vendor = None  # Phase 6: current vendor NPC for vendor screen
        self.current_quest_npc = None  # vendor/AmbientNPC object for QuestDialogScreen
        self.current_recruit_npc = None  # RecruitNPC object for RecruitDialogScreen
        self.current_banker = None  # AmbientNPC the bank screen is titled with
        self.party = None           # entities.Party - built lazily via get_party()
        self.icon_ui_helper = None  # Will be set by main.py after initialization
        
        # Initialize state screens
        self.states = {
            GameState.MENU: MenuScreen(self),
            GameState.CHARACTER_CREATION: CharacterCreationScreen(self),
            GameState.CHARACTER_SHEET: CharacterSheetScreen(self),
            GameState.SKILLS: SkillsScreen(self, icon_ui_helper=self.icon_ui_helper),
            GameState.PROFESSIONS: ProfessionsScreen(self),
            GameState.MAP: MapScreen(self),
            GameState.QUEST_JOURNAL: QuestJournalScreen(self),
            GameState.INVENTORY: InventoryScreen(self, icon_ui_helper=self.icon_ui_helper),
            # Pass `self` so the screen can transition back on ESC / Back button.
            # It was previously constructed with no state_manager reference at
            # all, which is why ESC silently did nothing - the handler looked
            # up self.state_manager via getattr(..., None) and always got None.
            GameState.TALENTS: TalentTreeScreen(SCREEN_WIDTH, SCREEN_HEIGHT, None, self),
            GameState.OVERWORLD: OverworldScreen(self),
            GameState.PARTY: PartyScreen(self),
            GameState.PET: PetScreen(self),
            GameState.TOTEM: TotemScreen(self),
            GameState.FORM: FormScreen(self),
            GameState.GUARDIAN: GuardianScreen(self),
            GameState.COMBAT: CombatScreen(self),
            GameState.CAST: CastScreen(self, icon_ui_helper=self.icon_ui_helper),
            GameState.BACKGROUND: BackgroundScreen(self),
            GameState.BOND_TEST: BondTestScreen(self),
            GameState.TRAVEL: TravelServiceScreen(self),
            # VendorScreen is created dynamically when entering vendor state
        }

        # OverworldScreen owns the live ZoneManager; publish it here now that
        # the screen exists so MapScreen can read it.
        self.zone_manager = getattr(
            self.states[GameState.OVERWORLD], "zone_manager", None)
    
    def transition_to(self, new_state, **kwargs):
        """Transition to a new game state."""
        if new_state == GameState.QUIT:
            raise SystemExit
        
        # Store any context data (like current enemy for combat)
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        self._prev_state = self.current_state
        self.current_state = new_state
        self._entered_state_fresh = True
    
    @property
    def player(self):
        return self._player

    @player.setter
    def player(self, value):
        self._player = value
        # Class trainers are only shown for the player's own class (world/ambient_npc_manager.py).
        from world.ambient_npc_manager import get_ambient_npc_manager
        get_ambient_npc_manager().set_viewer_class(getattr(value, "char_class", None))

    def get_party(self):
        """
        The player's Party, created on first use.

        Lazy rather than built alongside the player because the player can be
        created (new game) or loaded (save) through different paths, and both
        need to end up with exactly one Party wrapping the same Character.
        """
        from entities.party import Party
        if self.player is None:
            return None
        if self.party is None or self.party.player is not self.player:
            self.party = Party(self.player)
        return self.party

    # ------------------------------------------------------------------
    # Save / load
    #
    # These live here rather than on a screen because a save spans four
    # separate owners - the player, the Party, the RecruitManager and the
    # OverworldScreen's ZoneManager - and the state manager is the only
    # object that can reach all of them. Previously nothing in the game
    # called save at all after character creation, and Load Game was a
    # `print()` statement.
    # ------------------------------------------------------------------

    def _save_system(self):
        from core.save_system import SaveSystem
        if getattr(self, "_save_system_instance", None) is None:
            self._save_system_instance = SaveSystem()
        return self._save_system_instance

    def resolve_wipe(self):
        """The whole party is dead. Charge the price, stand everyone up, and put them back at
        the start of the dungeon or the nearest town entrance. Returns the lines to show.

        Kyle, 12 Nov 2026: "When people all die the entire group loses 15% of their EXP and
        they go back to either the start of the dungeon, start of the cave, or if theyre in
        open world then they go back to the nearest town entrance."
        """
        party = self.get_party()
        lost = party.wipe_penalty()
        zm = self._live_zone_manager()
        where = zm.send_to_respawn() if zm else "safety"
        total = sum(n for _m, n in lost)
        self.last_wipe = {"where": where, "xp_lost": total,
                          "lines": [f"The party was wiped out and wakes at {where}.",
                                    f"Everyone lost {int(party.WIPE_XP_LOSS * 100)}% of their "
                                    f"experience ({total} in all)."]}
        # FRIENDSHIP: each wipe wears on the people in the party, and a nervy one who has
        # already warned you can walk out at the dungeon door (world/bond_manager.py).
        from world.bond_manager import get_bond_manager
        from world.zone_classification import is_dungeon
        here = getattr(getattr(zm, "current_zone", None), "name", "") if zm else ""
        get_bond_manager().on_wipe(party, at_dungeon_door=bool(here and is_dungeon(here)))
        overworld = self.states.get(GameState.OVERWORLD)
        if overworld is not None and hasattr(overworld, "_notify"):
            overworld._notify(f"Wiped out. -{int(party.WIPE_XP_LOSS * 100)}% experience. "
                              f"You wake at {where}.", (240, 140, 140), duration=7.0)
        return self.last_wipe["lines"]

    def _live_zone_manager(self):
        """The ZoneManager actually driving play (owned by OverworldScreen)."""
        overworld = self.states.get(GameState.OVERWORLD)
        return getattr(overworld, "zone_manager", None)

    def delete_save(self, filename):
        """Erase a save slot. Returns True if a file was removed.

        If the deleted slot is the one being played, current_save_file is
        cleared so the session stops pointing at a file that no longer
        exists - otherwise the next autosave would quietly RECREATE it,
        which is the opposite of what the player just asked for.
        """
        removed = self._save_system().delete_save(filename)
        if removed and self.current_save_file == filename:
            self.current_save_file = None
        return removed

    def has_save(self, filename="character.json"):
        return self._save_system().has_save(filename)

    def describe_save(self, filename="character.json"):
        return self._save_system().describe_save(filename)

    @property
    def needs_save_slot(self):
        """True when there is a character to save and nowhere to put it.

        The state a newly created character is in until the player chooses
        a slot. Screens check this to send the player to the picker instead
        of reporting "Save failed", which would be both wrong and alarming -
        nothing failed, the game simply refuses to guess which of 15 slots
        the player meant.
        """
        return self.player is not None and not self.current_save_file

    def begin_new_character(self):
        """Forget which slot we were playing. Called before character creation.

        Without this the new character inherits the previous one's slot and
        the first autosave destroys it - see current_save_file's note in
        __init__. Clearing it on the way IN to creation rather than on the
        way out means an abandoned creation (player backs out) also cannot
        write anywhere.
        """
        self.current_save_file = None

    def _remember_slot(self, filename):
        """Which save file this session is playing.

        Nothing tracked this before: save_game and load_game were each handed a
        filename by the menu and the game never knew which slot it was in. The
        guild bank needs it - a deposit has to commit the character in the same
        breath or the item exists in both places (see entities/guild_bank.py).
        """
        self.current_save_file = filename
        from entities.guild_bank import set_host_saver
        set_host_saver(lambda: self.save_game(self.current_save_file))

    def save_game(self, filename=None):
        """
        Persist everything. Returns True on success.

        Refuses to write when there's no player, so a stray keypress at the
        main menu can't blank an existing save with an empty file.

        FILENAME DEFAULTS TO THE SLOT YOU ARE PLAYING, NOT SLOT 1. It used to
        default to the literal "character.json", which config.save_slot_filename
        maps to slot 1 - so every call site that did not pass a filename wrote
        over slot 1 regardless of which slot had been loaded. Three did: the F5
        quicksave, the post-combat autosave, and the character screen.

        Kyle, 2 Nov: "When I go to save anything in another file, like Save 2,
        or 3 etc - it saves in that slot AND overrides save 1." Exactly that -
        the menu wrote slot 3 because the menu passes a filename, and the next
        quicksave wrote the same character into slot 1 because it did not.
        Two saves, one of them silently destroying an unrelated character.

        self.current_save_file already tracked the right answer and was set on
        both load and save; nothing read it on the default path.
        """
        if self.player is None:
            return False
        if filename is None:
            filename = self.current_save_file
        # NO SLOT, NO WRITE. This used to fall back to "character.json",
        # which is slot 1 - so an unslotted character (one just created, or
        # one whose slot was cleared) autosaved itself over whatever lived
        # in slot 1. Refusing is the only safe answer: the player picks a
        # slot, and until they do nothing on disk is touched.
        #
        # Callers distinguish this from a real failure with needs_save_slot
        # rather than by comparing the return value, because both are False.
        if not filename:
            return False
        from world.recruit_manager import get_recruit_manager
        from world.quest_manager import get_quest_manager
        from world.travel_manager import get_travel_manager
        from world.faction_manager import get_faction_manager
        try:
            self._save_system().save_character(
                self.player,
                filename=filename,
                party=self.get_party(),
                recruit_manager=get_recruit_manager(),
                zone_manager=self._live_zone_manager(),
                quest_manager=get_quest_manager(),
                travel_manager=get_travel_manager(),
                faction_manager=get_faction_manager(),
            )
        except Exception as exc:
            print(f"Save failed: {exc}")
            return False
        # _remember_slot, not a bare assignment: a first save is also the
        # moment the guild bank learns which file to commit against. Before
        # this, only load_game rebound it, so a character created this
        # session had the PREVIOUS character's saver still installed and a
        # deposit committed into their file.
        self._remember_slot(filename)
        return True

    def load_game(self, filename="character.json"):
        """
        Restore a save into the live game. Returns True on success.

        Order matters: the player is rebuilt first, then the Party is built
        around that exact object (not a copy), then recruit state, then the
        world position. get_party() keys off identity, so assigning
        self.party after self.player is what stops it silently discarding
        the loaded companions and building a fresh solo party.
        """
        from entities.character import Character
        from entities.party import Party
        from world.recruit_manager import get_recruit_manager

        data = self._save_system().load_full_save(filename)
        if not data or not data.get("character"):
            return False
        # This slot is the one a guild bank transaction will commit alongside,
        # and the cached guild bank is dropped so switching characters re-reads
        # it from disk - otherwise the shaman would still be looking at the
        # druid's view of the shelf.
        self._remember_slot(filename)
        from entities.guild_bank import reset_guild_bank
        reset_guild_bank()

        try:
            player = Character.from_dict(data["character"])
        except Exception as exc:
            print(f"Could not rebuild character from save: {exc}")
            return False

        self.player = player
        self.current_enemy = None
        self.current_enemies = []
        self.current_vendor = None
        self.current_quest_npc = None
        self.current_recruit_npc = None

        party_data = data.get("party")
        if party_data:
            try:
                self.party = Party.from_dict(party_data, player)
            except Exception as exc:
                print(f"Could not rebuild party from save: {exc}")
                self.party = Party(player)
        else:
            self.party = Party(player)

        # ALWAYS from a fresh manager, never `if recruit_data:`. A save with
        # no recruit block (an early file, or one written while the bug
        # below was live) used to leave the PREVIOUS character's hires in
        # place, which deletes those companions out of the world for this
        # one - see reset_recruit_manager's docstring.
        from world.recruit_manager import reset_recruit_manager
        from world.faction_manager import reset_faction_manager
        reset_recruit_manager()
        reset_faction_manager()
        recruit_data = data.get("recruits")
        if recruit_data:
            get_recruit_manager().load_state(recruit_data)

        # SELF-REPAIR for saves already written with a poisoned recruit
        # block. A recruit flagged IN_PARTY who is not actually in the
        # loaded party is a ghost: the flag deletes them from the world and
        # there is no companion to show for it. That combination cannot
        # arise from legitimate play - hiring adds to both, dismissing
        # removes from both - so it is safe to read as damage and clear it.
        # Without this, the people who already made a character during the
        # bug would have to delete the save to get their world back.
        manager = get_recruit_manager()
        if manager.recruited_ids:
            in_party = {getattr(m, "recruit_id", None) for m in self.get_party().members}
            ghosts = {rid for rid in manager.recruited_ids if rid not in in_party}
            if ghosts:
                manager.recruited_ids -= ghosts
                print(f"Recruit state repaired: {len(ghosts)} companion(s) were "
                      f"flagged as hired but are not in the party; returned to the world.")

        # Quest state always starts from a genuinely fresh QuestManager
        # before applying anything saved - same reasoning as
        # CharacterCreationScreen's reset_to_start() call: the quest
        # manager is a process-lifetime singleton (see
        # world/quest_manager.get_quest_manager), so simply not
        # overwriting it here would leave whatever an EARLIER loaded
        # save's progress was sitting in memory. An old save with no
        # "quests" key (predates this feature) now correctly loads with
        # every quest at its real NOT_STARTED default, not leftover
        # progress from a previous load_game() call in this session.
        from world.quest_manager import get_quest_manager, QuestManager
        import world.quest_manager as _qm_module
        _qm_module._quest_manager = QuestManager()
        quest_data = data.get("quests")
        if quest_data:
            get_quest_manager().load_from_dict(quest_data)

        # Travel state (hearth bind, flight nodes, riding, mounts) - same fresh-singleton-then-apply pattern as
        # quests; a pre-v7 save has no "travel" block and simply loads with the defaults.
        from world.travel_manager import reset_travel_manager
        reset_travel_manager().load_from_dict(data.get("travel"))

        # Faction standing - same fresh-singleton-then-apply pattern as quests and travel, and for the same
        # reason: FactionManager is a process-lifetime singleton, so loading a second save in one session
        # would otherwise inherit the first one's reputation. A pre-v9 save has no "factions" block and
        # loads with everybody Unlisted, which is the correct starting state, so there is no migration.
        import world.faction_manager as _fm_module
        _fm_module._faction_manager = _fm_module.FactionManager()
        _fm_module.get_faction_manager().load_from_dict(data.get("factions"))

        world = data.get("world")
        zone_manager = self._live_zone_manager()
        if zone_manager:
            # Opened chests, BEFORE arriving anywhere: an old save has none recorded, and a
            # different character's opened chests must not carry over from the last load.
            chests = zone_manager.chest_manager
            for _name, _entry in zone_manager.zones.items():
                _map = _entry["tilemap"] if isinstance(_entry, dict) else _entry
                for (_z, _x, _y) in [k for k in chests._looted if k[0] == _name]:
                    if _map.get_tile(_x, _y, "interaction") is None:
                        _map.set_tile(_x, _y, "chest", "interaction")    # put back what the last game took
            chests.load_dict((world or {}).get("chests"))
            chests.apply_to_world({n: (e["tilemap"] if isinstance(e, dict) else e)
                                   for n, e in zone_manager.zones.items()})
        if world and zone_manager:
            if not zone_manager.transition_to_zone(
                    world.get("zone"), world.get("x"), world.get("y")):
                print(f"Saved zone '{world.get('zone')}' no longer exists; "
                      "starting from the default zone.")

        return True

    def _ensure_vendor_screen(self):
        """
        Build the vendor screen on demand. Rebuilt whenever the vendor changes
        so a second vendor never shows the first vendor's stock.
        """
        if self.current_state != GameState.VENDOR or not self.current_vendor:
            return
        screen = self.states.get(GameState.VENDOR)
        if screen is None or screen.vendor is not self.current_vendor:
            self.states[GameState.VENDOR] = VendorScreen(self, self.current_vendor)
        elif self._entered_state_fresh and hasattr(screen, "on_open"):
            # Same vendor reopened: keep the rolled stock (no re-roll exploit) but reset selection + run auto-sell.
            screen.on_open()
        self._entered_state_fresh = False

    def _ensure_bank_screen(self):
        """Build the bank screen on demand, same lazy pattern as the vendor screen.

        Rebuilt when the banker changes so the panel is titled with whoever you are standing in front
        of - which matters less than usual here, since it is the same troll in all three cities.
        """
        if self.current_state != GameState.BANK:
            return
        screen = self.states.get(GameState.BANK)
        if screen is None or screen.banker is not self.current_banker:
            from ui.screens.bank_screen import BankScreen
            self.states[GameState.BANK] = BankScreen(self, self.current_banker,
                                                     icon_ui_helper=self.icon_ui_helper)
        self._entered_state_fresh = False

    def _ensure_quest_dialog_screen(self):
        """
        Build the quest dialog screen on demand, same lazy pattern as
        _ensure_vendor_screen - rebuilt whenever current_quest_npc changes
        OR the player has left and come back (see _prev_state check
        below), so walking up to a second NPC never shows the first
        NPC's conversation state, AND leaving+returning to the SAME NPC
        never shows stale state either.

        Real bug this second condition fixes (Kyle, 2026-09-05): an NPC
        offering multiple simultaneously-ready turn-ins (e.g. Valley of
        Trials' vot_guard_1 with both Vile Familiars and Felstalkers
        ready at once) would get permanently stuck if the player closed
        the dialog mid gear-choice-picker (Close -> OVERWORLD) and walked
        back up to the SAME NPC - the old check only compared
        `screen.npc is not self.current_quest_npc`, which is False for
        the same NPC, so the screen was never rebuilt and _refresh() was
        never called. The player would be stuck re-seeing the picker for
        the ALREADY-COMPLETED first quest forever, with the second
        quest's turn-in permanently unreachable through the UI (the
        underlying QuestManager state was always correct - this was a
        pure UI staleness bug, not data corruption).
        """
        if self.current_state != GameState.QUEST_DIALOG or not self.current_quest_npc:
            return
        screen = self.states.get(GameState.QUEST_DIALOG)
        # _entered_state_fresh is a one-shot flag set by transition_to and
        # consumed (cleared) right here - True only on the very first
        # _ensure_*_screen() call after a real transition INTO
        # QUEST_DIALOG, False on every subsequent call made while still
        # sitting in this state (handle_event/update/render all call this
        # every frame). Reading screen.npc alone can't distinguish
        # "player just walked up to this NPC again after leaving" from
        # "we're still mid-conversation with them" when it's the SAME
        # NPC object either way - this flag is what makes that
        # distinction, without which a multi-turn-in NPC (two quests
        # ready at once) would get its gear-choice-in-progress state
        # wiped by every ordinary frame tick.
        returning_to_same_npc = (
            screen is not None
            and screen.npc is self.current_quest_npc
            and self._entered_state_fresh
        )
        if screen is None or screen.npc is not self.current_quest_npc or returning_to_same_npc:
            self.states[GameState.QUEST_DIALOG] = QuestDialogScreen(self, self.current_quest_npc)
        self._entered_state_fresh = False

    def _ensure_recruit_dialog_screen(self):
        """
        Build the recruit dialog screen on demand, same lazy-rebuild
        pattern as _ensure_quest_dialog_screen (including the
        _entered_state_fresh re-entry check - see that method's
        docstring for the exact staleness bug this avoids) - a stale
        screen instance would otherwise keep showing a PREVIOUS
        conversation's joined/result_message state if the player closed
        out and walked back up to the SAME recruit (e.g. after dismissing
        and re-approaching them), not just a different one.
        """
        if self.current_state != GameState.RECRUIT_DIALOG or not self.current_recruit_npc:
            return
        screen = self.states.get(GameState.RECRUIT_DIALOG)
        returning_to_same_recruit = (
            screen is not None
            and screen.recruit is self.current_recruit_npc
            and self._entered_state_fresh
        )
        if screen is None or screen.recruit is not self.current_recruit_npc or returning_to_same_recruit:
            from ui.screens.recruit_dialog_screen import RecruitDialogScreen
            self.states[GameState.RECRUIT_DIALOG] = RecruitDialogScreen(self, self.current_recruit_npc)
        self._entered_state_fresh = False

    def handle_event(self, event):
        """Delegate event handling to current state."""
        self._ensure_vendor_screen()
        self._ensure_quest_dialog_screen()
        self._ensure_recruit_dialog_screen()
        self._ensure_bank_screen()
        
        if self.current_state in self.states:
            self.states[self.current_state].handle_event(event)
    
    def update(self, dt):
        """Delegate update to current state."""
        self._ensure_vendor_screen()
        self._ensure_quest_dialog_screen()
        self._ensure_recruit_dialog_screen()
        self._ensure_bank_screen()
        
        if self.current_state in self.states:
            self.states[self.current_state].update(dt)
    
    def render(self, screen):
        """Delegate rendering to current state."""
        self._ensure_vendor_screen()
        self._ensure_quest_dialog_screen()
        self._ensure_recruit_dialog_screen()
        self._ensure_bank_screen()
        
        if self.current_state in self.states:
            self.states[self.current_state].render(screen)
