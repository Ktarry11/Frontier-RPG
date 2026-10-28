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

    def _live_zone_manager(self):
        """The ZoneManager actually driving play (owned by OverworldScreen)."""
        overworld = self.states.get(GameState.OVERWORLD)
        return getattr(overworld, "zone_manager", None)

    def has_save(self, filename="character.json"):
        return self._save_system().has_save(filename)

    def describe_save(self, filename="character.json"):
        return self._save_system().describe_save(filename)

    def save_game(self, filename="character.json"):
        """
        Persist everything. Returns True on success.

        Refuses to write when there's no player, so a stray keypress at the
        main menu can't blank an existing save with an empty file.
        """
        if self.player is None:
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

        recruit_data = data.get("recruits")
        if recruit_data:
            get_recruit_manager().load_state(recruit_data)

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
