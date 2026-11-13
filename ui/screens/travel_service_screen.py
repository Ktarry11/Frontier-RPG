"""
TravelServiceScreen - the one screen behind every travel service NPC:

  flight  - Windrider/flight master: discovered nodes, gold cost, fly there (instant hop)
  riding  - Riding trainer: learn Apprentice (L20) / Journeyman (L30) Riding
  mounts  - Mount vendor: buy mounts your riding skill allows
  train_class - Class trainer: buy new abilities / higher ranks for your own class (world/training_manager.py)
  train_prof  - Profession trainer: learn a profession, train up its tiers, or unlearn it (world/profession_manager.py)

Opened from QuestDialogScreen's greeting buttons via open_service(kind, npc), then GameState.TRAVEL.
All rules live in world/travel_manager.py; this screen is only presentation + the gold/teleport glue.
"""
import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_GOLD
from core.game_states import GameState
from ui.screens.base_screen import BaseScreen
from world.travel_manager import get_travel_manager, format_copper

ROW_H = 62
ROW_GAP = 8
LIST_X = 40
LIST_W = SCREEN_WIDTH - 80
GREY = (150, 150, 160)
GREEN = (120, 220, 140)
RED = (230, 130, 130)


def _teach_trainer_recipes(character, profession: str) -> list:
    """Auto-teach all trainer-source recipes at/below the character's current skill.

    Called immediately after a successful prof_learn or prof_advance so that
    the trainer automatically hands over everything they know up to this skill level.
    Returns list of newly-learned recipe IDs (may be empty on advance if nothing new unlocked).
    """
    try:
        # CraftingManager covers tailoring, alchemy, woodworking
        from world.crafting_manager import get_crafting_manager
        cm = get_crafting_manager()
        if profession in cm.professions():
            return character.learn_trainer_recipes(profession, cm.all_recipes(profession))

        # BS and LW have their own managers
        if profession == "blacksmithing":
            from world.blacksmithing_manager import get_blacksmithing_manager
            return character.learn_trainer_recipes(profession, get_blacksmithing_manager().recipes)

        if profession == "leatherworking":
            from world.leatherworking_manager import get_leatherworking_manager
            return character.learn_trainer_recipes(profession, get_leatherworking_manager().recipes)
    except Exception:
        pass
    return []


class TravelServiceScreen(BaseScreen):
    TITLES = {"flight": "Windrider Flight Master", "riding": "Riding Trainer", "mounts": "Mount Vendor",
              "train_class": "Class Trainer", "train_prof": "Profession Trainer",
              "set_exchange": "Set Gear Exchange"}

    def __init__(self, state_manager):
        super().__init__(state_manager)
        self.kind = "flight"
        self.npc = None
        self.message = None
        self.message_color = GREEN
        self.close_button = pygame.Rect(SCREEN_WIDTH - 160, SCREEN_HEIGHT - 70, 120, 44)
        self._row_buttons = []   # [(rect, action, arg)] rebuilt every render
        self.scroll = 0          # first visible row (class trainers can list dozens)
        self._unlearn_armed = False   # "Unlearn" needs a second click to confirm

    # ------------------------------------------------------------------ opening
    def open_service(self, kind, npc):
        self.kind = kind
        self.npc = npc
        self.message = None
        self.scroll = 0
        self._unlearn_armed = False
        if kind == "flight":
            node_id = self._current_node()
            if node_id and get_travel_manager().discover_node(node_id):
                node = get_travel_manager().nodes()[node_id]
                self._say(f"New flight path discovered: {node['name']}!", GOLD_OK)

    def _say(self, text, color=GREEN):
        self.message, self.message_color = text, color

    # ------------------------------------------------------------------ helpers
    def _npc_id(self):
        return getattr(self.npc, "vendor_id", None) or getattr(self.npc, "npc_id", None)

    def _current_node(self):
        return get_travel_manager().node_for_master(self._npc_id())

    def _party(self):
        return self.state_manager.get_party()

    def _copper(self):
        party = self._party()
        return party.copper if party else 0

    # ------------------------------------------------------------------ rows
    def _rows(self):
        """[{name, sub, price, label, enabled, reason, action, arg}] for the current service."""
        travel = get_travel_manager()
        player = self.state_manager.player
        copper = self._copper()
        rows = []
        if self.kind == "flight":
            here = self._current_node()
            for node_id, node in travel.nodes().items():
                if node_id == here or not travel.can_fly_between(here, node_id):
                    continue
                known = node_id in travel.known_nodes
                cost = travel.flight_cost(here, node_id) if here else 0
                if not known:
                    rows.append(dict(name="???", sub="Not discovered - speak to the flight master there.",
                                     price=None, label="Locked", enabled=False, action="fly", arg=node_id))
                    continue
                ok = copper >= cost
                rows.append(dict(name=node["name"], sub=node["zone"], price=cost, label="Fly", enabled=ok,
                                 reason=None if ok else "Not enough gold", action="fly", arg=node_id))
        elif self.kind == "riding":
            nxt = travel.next_riding_skill()
            if nxt:
                rank, skill = nxt
                ok, reason = travel.can_learn_riding(player.level, copper)
                rows.append(dict(name=skill["name"], sub=f"Level {skill['level']}+  -  {skill['blurb']}",
                                 price=skill["price"], label="Learn", enabled=ok, reason=reason,
                                 action="learn", arg=rank))
        elif self.kind == "train_class":
            rows = self._train_rows(player, copper)
        elif self.kind == "train_prof":
            rows = self._prof_rows(player, copper)
        elif self.kind == "set_exchange":
            # One row per exchange on offer: a set piece somebody is wearing or carrying, and
            # another spec's version of it. Free (Kyle, 12 Nov) - respeccing must never mean
            # farming the set again.
            from world.gear_sets import exchangeable
            for member, item, where, key, label, name in exchangeable(self._party()):
                rows.append(dict(name=f"{item.name}  ->  {name}",
                                 sub=f"{label} version  -  {where}, {member.name}",
                                 price=None, label="Exchange", enabled=True, reason=None,
                                 action="set_exchange", arg=(member, item, key)))
            if not rows:
                rows.append(dict(name="Nothing to exchange",
                                 sub="Bring a class set piece that comes in more than one version.",
                                 price=None, label="-", enabled=False, reason=None,
                                 action="set_exchange", arg=None))
        elif self.kind == "mounts":
            for mount in travel.mounts_for_vendor(self._npc_id()):
                owned = mount["id"] in travel.owned_mounts
                ok, reason = travel.can_buy_mount(mount, copper)
                rows.append(dict(name=f"{mount['name']}  (Tier {mount['tier']})", sub=mount["blurb"],
                                 price=None if owned else mount["price"], label="Owned" if owned else "Buy",
                                 enabled=ok, reason=reason, action="buy", arg=mount["id"]))
        return rows

    def _trainer_class(self):
        from world.training_manager import class_for_trainer
        return class_for_trainer(self._npc_id())

    def _trainer_profession(self):
        from world.profession_manager import profession_for_trainer
        return profession_for_trainer(self._npc_id())

    def _trainer_professions(self):
        """Every profession this NPC teaches. Trainers are themed pairs, so this is usually 2-3."""
        from world.profession_manager import professions_for_trainer
        return professions_for_trainer(self._npc_id())

    def _prof_rows(self, player, copper):
        from world import profession_manager as pm
        rows = []
        # A trainer teaches a themed PAIR (gathering profession plus the craft that consumes it), so walk
        # all of them and concatenate. The gathering half is listed first because that is the order a
        # player meets them in.
        for prof in self._trainer_professions():
            rows.extend(self._prof_rows_for(player, copper, prof, pm))
        return rows

    def _prof_rows_for(self, player, copper, prof, pm):
        rows = []
        for o in pm.offers(player, prof):
            if o["kind"] == "unlearn":
                rows.append(dict(name=o["name"], sub="Click again to confirm - " + o["sub"] if self._unlearn_armed else o["sub"],
                                 price=None, label="Confirm?" if self._unlearn_armed else "Unlearn", enabled=True,
                                 action="prof_unlearn", arg=prof))
                continue
            ok = o["enabled"] and (o["cost"] is None or copper >= o["cost"])
            reason = o["reason"] or ("Not enough gold" if o["enabled"] and not ok else None)
            label = {"learn": "Learn", "advance": "Train", "info": "Locked"}.get(o["kind"], "Locked")
            rows.append(dict(name=o["name"], sub=o["sub"], price=o["cost"], label=label, enabled=ok, reason=reason,
                             action={"learn": "prof_learn", "advance": "prof_advance"}.get(o["kind"], "none"), arg=prof))
        return rows

    def _train_rows(self, player, copper):
        from world import training_manager as tm
        cls = self._trainer_class()
        # "*" is a universal class trainer - one per town, teaches every discipline. The per-class
        # trainers it replaced refused anyone who was not their class; a universal one never does.
        if cls not in ("*", player.char_class):
            return []
        offers = tm.offers(player)
        rows = []
        total = sum(o["cost"] for o in offers)
        if len(offers) > 1:
            affordable = [o for o in offers if o["cost"] <= copper]
            rows.append(dict(name="Learn everything you can afford",
                             sub=f"{len(affordable)} of {len(offers)} available  -  cheapest first",
                             price=total, label="Learn all", enabled=bool(affordable),
                             reason="Not enough gold", action="train_all", arg=None))
        for o in offers:
            if o["new"]:
                sub = f"New ability  -  requires level {o['level_req']}"
                # An ability you walked past: say so, and say for how long. Without this the only
                # hint that you skipped something is that the row quietly says a higher rank.
                if o.get("behind", 0) >= 3:
                    sub = (f"New ability  -  learnable since level {o['first_level']}"
                           f"  -  {o['behind']} levels overdue")
            else:
                sub = f"Rank {o['from_rank']} -> {o['rank']}  -  requires level {o['level_req']}"
            name = o["name"] if o["rank"] == 1 else f"{o['name']}  (Rank {o['rank']})"
            ok = copper >= o["cost"]
            # tip: the Ability itself, so hovering the row shows what it actually does.
            # Kyle, 2026-10-31: "when we go to learn something, is there a way to hover over it
            # and show what it does? like we can do that in our cast bar already." Buying a
            # spell off a name and a price alone is a guess.
            rows.append(dict(name=name, sub=sub, price=o["cost"], label="Learn", enabled=ok,
                             reason=None if ok else "Not enough gold", action="train",
                             arg=o["ability"].ability_id, tip=o["ability"]))
        for u in tm.upcoming(player, limit=4):
            what = u["name"] if u["rank"] == 1 else f"{u['name']}  (Rank {u['rank']})"
            rows.append(dict(name=what, sub=f"Available at level {u['level_req']}", price=None, label="Locked",
                             enabled=False, action="none", arg=None, tip=u.get("ability")))
        return rows

    # ------------------------------------------------------------------ actions
    def _act(self, action, arg):
        travel = get_travel_manager()
        party = self._party()
        if action == "set_exchange":
            from world.gear_sets import exchange
            member, item, key = arg
            before = item.name
            if exchange(item, key):
                member._recalculate_derived_stats()
                return self._say(f"{before} is now {item.name}.", GREEN)
            return self._say("That cannot be exchanged.", RED)
        if action in ("train", "train_all"):
            from world import training_manager as tm
            player = self.state_manager.player
            if action == "train":
                ok, msg = tm.train(player, party, arg)
                return self._say(msg, GREEN if ok else RED)
            learned = 0
            for o in tm.offers(player):
                ok, _ = tm.train(player, party, o["ability"].ability_id)
                learned += bool(ok)
            return self._say(f"You learned {learned} new skill{'s' if learned != 1 else ''}." if learned
                             else "You can't afford anything.", GREEN if learned else RED)
        if action in ("prof_learn", "prof_advance", "prof_unlearn"):
            from world import profession_manager as pm
            player = self.state_manager.player
            if action == "prof_unlearn":
                if not self._unlearn_armed:
                    self._unlearn_armed = True
                    return self._say("Click Unlearn again to forget this profession and lose its skill.", RED)
                self._unlearn_armed = False
                ok, msg = pm.unlearn(player, arg)
            else:
                self._unlearn_armed = False
                ok, msg = (pm.learn if action == "prof_learn" else pm.advance)(player, party, arg)
                if ok:
                    # Auto-teach all trainer-source recipes at/below current skill.
                    # Works for both initial learn AND tier advances (which raise the skill cap
                    # and may unlock recipes the trainer already had waiting).
                    newly_learned = _teach_trainer_recipes(player, arg)
                    if newly_learned:
                        recipes_word = "recipe" if len(newly_learned) == 1 else "recipes"
                        msg = f"{msg}  You learned {len(newly_learned)} {recipes_word}."
            return self._say(msg, GREEN if ok else RED)
        if action == "learn":
            ok, reason = travel.can_learn_riding(self.state_manager.player.level, self._copper())
            if not ok:
                return self._say(reason, RED)
            skill = travel.next_riding_skill()[1]
            party.remove_currency(skill["price"])
            travel.learn_riding()
            self._say(f"You have learned {skill['name']}. Buy a mount to ride it!")
        elif action == "buy":
            mount = travel.get_mount(arg)
            ok, reason = travel.can_buy_mount(mount, self._copper())
            if not ok:
                return self._say(reason, RED)
            party.remove_currency(mount["price"])
            travel.buy_mount(mount)
            self._say(f"You bought a {mount['name']}. Press R to ride.")
        elif action == "fly":
            self._fly(arg)

    def _fly(self, node_id):
        travel = get_travel_manager()
        here = self._current_node()
        node = travel.nodes().get(node_id)
        if node is None or node_id not in travel.known_nodes:
            return self._say("You haven't discovered that flight path.", RED)
        if not travel.can_fly_between(here, node_id):
            return self._say("There is no flight path across the sea.", RED)
        cost = travel.flight_cost(here, node_id) if here else 0
        if self._copper() < cost:
            return self._say("Not enough gold.", RED)
        zm = self.state_manager._live_zone_manager()
        # ONE lookup for "where is this node's flight master", shared with the map and the
        # QA. This used to look among ambient NPCs only, and two flight masters are vendors
        # (Hammerfall, Saltspur Landing) - so flying to either failed with "The windrider
        # can't find the landing."
        from world.travel_manager import find_flight_master
        master = find_flight_master(node, getattr(zm, "vendor_manager", None))
        if master is None or zm is None:
            return self._say("The windrider can't find the landing.", RED)
        self._party().remove_currency(cost)
        travel.force_dismount()
        # via_portal=False: a flight path is a teleport, not a walk out of a cave mouth
        zm.transition_to_zone(node["zone"], master.x, master.y, via_portal=False)
        self.state_manager.transition_to(GameState.OVERWORLD)
        overworld = self.state_manager.states.get(GameState.OVERWORLD)
        if overworld is not None and hasattr(overworld, "_notify"):
            overworld._notify(f"You fly to {node['name']}. ({format_copper(cost)})", GREEN)

    # ------------------------------------------------------------------ events
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state_manager.transition_to(GameState.OVERWORLD)
            return
        if event.type == pygame.MOUSEWHEEL:
            self.scroll = max(0, self.scroll - event.y)
            return
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        if self.close_button.collidepoint(event.pos):
            self.state_manager.transition_to(GameState.OVERWORLD)
            return
        for rect, action, arg, enabled, reason in self._row_buttons:
            if rect.collidepoint(event.pos):
                if enabled:
                    self._act(action, arg)
                elif reason:
                    self._say(reason, RED)
                return

    def update(self, dt):
        pass

    # ------------------------------------------------------------------ drawing
    def render(self, screen):
        screen.fill((10, 10, 15))
        title = self.TITLES.get(self.kind, "Travel")
        if self.kind == "flight" and get_travel_manager().continent_of(self._current_node()) == "eastern_kingdoms":
            title = "Forsaken Bat Handler"
        self.renderer.draw_text(screen, getattr(self.npc, "name", title), (40, 24), size="large", color=COLOR_GOLD)
        self.renderer.draw_text(screen, title, (40, 62), color=GREY)
        self.renderer.draw_text(screen, f"Your gold: {format_copper(self._copper())}", (SCREEN_WIDTH - 340, 30),
                                color=COLOR_GOLD)

        travel = get_travel_manager()
        if self.kind == "flight":
            here = self._current_node()
            hint = f"You are at {travel.nodes()[here]['name']}." if here else ""
        elif self.kind == "riding":
            hint = ("Riding makes you faster and shaves down random ambushes. Press R in the overworld to mount."
                    if travel.riding_rank < 2 else "You have mastered riding.")
        elif self.kind == "train_class":
            cls = self._trainer_class()
            player = self.state_manager.player
            if cls == "*":
                hint = ("I train every discipline, yours included. Each skill is taught at the highest "
                        "rank your level allows.")
            elif cls == player.char_class:
                hint = f"I train {cls}s. Each skill is taught at the highest rank your level allows."
            else:
                hint = f"I only train {cls}s. Find a {player.char_class} trainer."

        elif self.kind == "train_prof":
            from world import profession_manager as pm
            prof = self._trainer_profession()
            player = self.state_manager.player
            got = self._trainer_professions()
            names = [pm.professions()[k]["name"] for k in got if k in pm.professions()]
            if not names:
                shown = "a profession"
            elif len(names) == 1:
                shown = names[0]
            else:
                shown = ", ".join(names[:-1]) + " and " + names[-1]
            # Count only the professions that actually occupy a slot - a secondary trade
            # (Cooking) is free, and counting it here would tell the player they had one
            # fewer slot than they really do.
            hint = (f"I teach {shown}. You know {pm.primary_count(player)} of "
                    f"{pm.max_primary()} professions.")
        elif self.kind == "set_exchange":
            hint = ("Bring me a piece of your class set and I will trade it for another spec's "
                    "version of the same piece. No charge.")
        else:
            hint = (f"Riding skill: {travel.riding_skill(travel.riding_rank)['name']}" if travel.riding_rank
                    else "You need to learn riding first (level 20, any riding trainer).")
        self.renderer.draw_text(screen, hint, (40, 92), color=GREY)

        self._row_buttons = []
        hover_rows = []          # (panel rect, the thing to describe) for the tooltip pass below
        y = 130
        rows = self._rows()
        if not rows:
            self.renderer.draw_text(screen, "Nothing available here right now.", (LIST_X, y), color=GREY)
        visible = max(1, (SCREEN_HEIGHT - 90 - y) // (ROW_H + ROW_GAP))
        self.scroll = max(0, min(self.scroll, max(0, len(rows) - visible)))
        if len(rows) > visible:
            self.renderer.draw_text(screen, f"Scroll for more ({self.scroll + 1}-{min(len(rows), self.scroll + visible)} of {len(rows)})",
                                    (SCREEN_WIDTH - 420, 62), size="small", color=GREY)
        for row in rows[self.scroll:self.scroll + visible]:
            panel = pygame.Rect(LIST_X, y, LIST_W, ROW_H)
            pygame.draw.rect(screen, (24, 24, 34), panel)
            pygame.draw.rect(screen, (70, 70, 90), panel, 1)
            name_color = COLOR_WHITE if row["enabled"] or row["label"] in ("Owned",) else GREY
            self.renderer.draw_text(screen, row["name"], (panel.x + 14, panel.y + 8), color=name_color)
            self.renderer.draw_text(screen, row["sub"], (panel.x + 14, panel.y + 34), size="small", color=GREY)
            if row["price"] is not None:
                self.renderer.draw_text(screen, format_copper(row["price"]), (panel.right - 330, panel.y + 20),
                                        color=COLOR_GOLD if row["enabled"] else RED)
            btn = pygame.Rect(panel.right - 150, panel.y + 9, 130, ROW_H - 18)
            self.renderer.draw_button(screen, btn, row["label"],
                                      color=(30, 90, 110) if row["enabled"] else (50, 50, 56))
            self._row_buttons.append((btn, row["action"], row["arg"], row["enabled"], row.get("reason")))
            if row.get("tip") is not None:
                hover_rows.append((panel, row["tip"]))
            y += ROW_H + ROW_GAP

        # Drawn AFTER every row, so the tooltip is never painted over by the next panel down.
        mouse = pygame.mouse.get_pos()
        for panel, tip in hover_rows:
            if panel.collidepoint(mouse):
                from ui.ability_tooltip import draw_ability_tooltip
                draw_ability_tooltip(self.renderer, screen, tip, mouse,
                                     getattr(self.state_manager, "player", None))
                break

        if self.message:
            self.renderer.draw_text(screen, self.message, (40, SCREEN_HEIGHT - 70), color=self.message_color)
        self.renderer.draw_button(screen, self.close_button, "Close")


GOLD_OK = (240, 210, 110)
