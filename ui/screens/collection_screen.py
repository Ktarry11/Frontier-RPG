"""The Collection: everything this player has learned, for every character (docs/collection_design.md).

Kyle, 18 Nov 2026: "This will need a new system tab that's account-wide", and "We should be able to see our stuff
from character. So anywhere. Not bank. Otherwise it defeats the purpose." So it opens from the overworld's tab column
(and U), wherever you are.

Six tabs: Mounts, Forms, Titles, Travel (feathers, hearths and the tomes), Services and Heirlooms. There are hundreds
(Kyle: "I'd want 100s to 1000s of fun collection stuff"), so each tab has a filter (all, learned, missing) and a
search you type into. A card for every
collectable: learned ones in their rarity colour with what you can do with them, the rest greyed with their name, so
you can see what's still out there. The buttons do the thing: ride a mount, wear a form, take the second hearth,
call a portable service (once per market day), or take an heirloom copy for this character.
"""
import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_GOLD
from core.game_states import GameState
from ui.screens.base_screen import BaseScreen
from ui.scrollbar import ScrollBar, GUTTER

TOP = 190
CARD_W, CARD_H, CARD_GAP = 590, 80, 8
COLS = 2
FILTERS = (("all", "All"), ("learned", "Learned"), ("missing", "Missing"))
LEFT = 30
GREY, DIM, GREEN, RED, GOLD = (170, 170, 180), (95, 95, 105), (140, 220, 160), (240, 160, 140), (230, 200, 120)
RARITY = {"common": (235, 235, 235), "uncommon": (30, 255, 0), "rare": (0, 112, 221), "epic": (163, 53, 238)}


def _hours(h):
    h = max(0, int(round(h)))
    return f"{h} market hour{'s' if h != 1 else ''}"


#: the class forms a look can dress, as players know them (combat/forms.py)
_FORM_NAME = {"bear": "Bear Form", "dire_bear": "Dire Bear Form", "cat": "Cat Form", "moonkin": "Moonkin Form",
              "tree_of_life": "Tree of Life", "spider": "Spider Form", "beetle": "Beetle Form"}


class CollectionScreen(BaseScreen):
    def __init__(self, state_manager, icon_ui_helper=None):
        super().__init__(state_manager)
        self.icon_ui_helper = icon_ui_helper or getattr(state_manager, "icon_ui_helper", None)
        self.tab = "mount"
        self.scroll = 0
        self.bar = ScrollBar()
        self.message, self.message_ok = "", True
        self.close_rect = pygame.Rect(SCREEN_WIDTH - 130, 20, 110, 46)
        self.tab_rects = []
        self.filter_rects = []
        self.filter = "all"
        self.search = ""
        self.buttons = []           # (rect, cid, action)
        self.cards = []             # (rect, entry)
        self._pics = {}

    # ------------------------------------------------------------ helpers
    def _travel(self):
        from world.travel_manager import get_travel_manager
        return get_travel_manager()

    def _clock(self):
        from world.market.market import market_of
        try:
            return market_of(self.state_manager.get_party()).clock
        except Exception:
            return 0.0

    def _in_cave(self):
        try:
            zm = self.state_manager._live_zone_manager()
            return bool(getattr(zm.current_zone, "is_cave", False))
        except Exception:
            return False

    def _say(self, ok, msg):
        self.message, self.message_ok = msg, ok

    def _rows(self):
        from world import collection as C
        rows = C.by_tab(self.tab)
        if self.filter == "learned":
            rows = [e for e in rows if C.learned(e["id"])]
        elif self.filter == "missing":
            rows = [e for e in rows if not C.learned(e["id"])]
        if self.search:
            q = self.search.lower()
            rows = [e for e in rows if (q in e["name"].lower() or q in e["blurb"].lower())
                    and not (e["kind"] == "keepsake" and not C.learned(e["id"]))]     # an ungiven keepsake stays hidden
        # learned first, then by rarity (the rarest last), then by name
        order = {"common": 0, "uncommon": 1, "rare": 2, "epic": 3}
        return sorted(rows, key=lambda e: (not C.learned(e["id"]), order.get(e["rarity"], 0), e["name"]))

    # ------------------------------------------------------------ what each card can do
    def _status(self, e):
        """(line, colour, [(label, action)]) for one card."""
        from world import collection as C
        cid, kind = e["id"], e["kind"]
        if kind == "keepsake":
            who = e["effect"]["from"].split()[0]
            if not C.learned(cid):
                return f"Something personal. {who} gives it to you when they swear to you.", DIM, []
            return f"Given to you by {e['effect']['from']}.", GREEN, []
        if not C.learned(cid):
            return "Not learned. Look for it on the auction house.", DIM, []
        tm = self._travel()
        if kind in ("mount", "form") and not C.art_ready(cid):
            return "Learned. Its art isn't in yet, so it can't be used until it lands.", GOLD, []
        if kind == "mount":
            if tm.riding_rank < 1:
                return "Learned. Every character can ride it once they've learned to ride.", GREEN, []
            if tm.active_mount == cid:
                return "Learned. It's the mount R summons.", GREEN, []
            return "Learned.", GREEN, [("Ride", "ride")]
        if kind == "form" and C.look_of(cid):
            base = C.look_of(cid)
            what = _FORM_NAME.get(base, base.replace("_", " ").title())
            if tm.form_looks.get(base) == cid:
                return f"Learned. It's how your {what} looks.", GREEN, [("Plain look", "look_off")]
            return f"Learned. A look for {what}, for every character who can take it.", GREEN, [("Use", "look_on")]
        if kind == "form":
            if tm.active_form == cid:
                return "Learned. You're wearing it on the map.", GREEN, [("Take off", "form_off")]
            return "Learned.", GREEN, [("Wear", "form_on")]
        if kind == "title":
            shown = C.titled_name(self.state_manager.player.name, cid)
            if getattr(tm, "active_title", None) == cid:
                return f"Learned. You're {shown}.", GREEN, [("Remove", "title_off")]
            return f"Learned. You'd be {shown}.", GREEN, [("Use", "title_on")]
        eff = e["effect"]
        if eff.get("feather"):
            from world.travel_manager import travel_data
            n = sum(1 for v in travel_data()["flight_nodes"].values()
                    if v.get("continent", "kalimdor") == eff["feather"])
            return f"Learned. All {n} flight paths there are open.", GREEN, []
        if eff.get("second_hearth"):
            reason = tm.second_hearth_block_reason()
            where = tm.bind2["name"] if tm.bind2 else "nowhere yet (ask any innkeeper)"
            return f"Learned. Bound to {where}." + (f" {reason}" if reason and tm.bind2 else ""), GREEN, \
                ([("Hearth", "hearth2")] if not reason else [])
        if kind == "service":
            ready, left = C.service_ready(tm, cid, self._clock())
            if ready:
                return "Learned. Ready.", GREEN, [(C.SERVICE_LABEL.get(eff["service"], "Use"), "service")]
            return f"Learned. Ready again in {_hours(left)}.", GOLD, []
        if kind == "heirloom":
            ok, why = C.can_take_heirloom(cid, self.state_manager.player, self.state_manager.get_party())
            return ("Learned." if ok else f"Learned. {why}"), GREEN, ([("Take a copy", "heirloom")] if ok else [])
        return "Learned. It works on every character.", GREEN, []

    def _do(self, cid, action):
        from world import collection as C
        e = C.get_entry(cid)
        tm = self._travel()
        sm = self.state_manager
        if action == "ride":
            ok, msg = tm.choose_mount(cid, self._in_cave())
            return self._say(True, msg)
        if action == "form_on":
            tm.active_form = cid
            tm.mounted = False
            return self._say(True, f"You're walking as a {e['effect'].get('form_name', e['name'])}. "
                                   f"Only the map sees it.")
        if action == "look_on":
            base = C.look_of(cid)
            tm.form_looks[base] = cid
            what = _FORM_NAME.get(base, base.replace("_", " ").title())
            return self._say(True, f"Your {what} looks like a {e['effect'].get('form_name', e['name'])} now.")
        if action == "look_off":
            tm.form_looks.pop(C.look_of(cid), None)
            return self._say(True, "Back to the plain look.")
        if action == "form_off":
            tm.active_form = None
            return self._say(True, "You're yourself again.")
        if action == "title_on":
            tm.active_title = cid
            return self._say(True, f"You're {C.titled_name(sm.player.name, cid)} now, on every screen with your name.")
        if action == "title_off":
            tm.active_title = None
            return self._say(True, "Just your name again.")
        if action == "hearth2":
            ow = sm.states.get(GameState.OVERWORLD)
            if ow is None or not hasattr(ow, "use_second_hearth"):
                return self._say(False, "You can't do that from here.")
            ok, msg = ow.use_second_hearth()
            if ok:
                return sm.transition_to(GameState.OVERWORLD)
            return self._say(False, msg)
        if action == "heirloom":
            player, party = sm.player, sm.get_party()
            ok, why = C.can_take_heirloom(cid, player, party)
            if not ok:
                return self._say(False, why)
            if len(player.inventory) >= player.inventory_capacity:
                return self._say(False, "Your bags are full.")
            item = C.make_heirloom(cid, player)
            if item is None:
                return self._say(False, f"A {player.char_class} can't use that.")
            player.inventory.append(item)
            return self._say(True, f"{item.name} is in your bags, made for a level {player.level} {player.char_class}.")
        if action == "service":
            ready, left = C.service_ready(tm, cid, self._clock())
            if not ready:
                return self._say(False, f"Ready again in {_hours(left)}.")
            return self._open_service(cid, e["effect"]["service"])

    def _open_service(self, cid, service):
        from world import collection as C
        sm = self.state_manager
        tm = self._travel()
        player = sm.player
        if service == "bank":
            sm.transition_to(GameState.BANK, current_banker=None)
        elif service == "peddler":
            sm.transition_to(GameState.VENDOR, current_vendor=C.peddler_vendor())
        elif service == "reagents":
            sm.transition_to(GameState.VENDOR, current_vendor=C.reagent_vendor())
        elif service == "mail":
            sm.transition_to(GameState.MAIL)
        elif service == "class_trainer":
            screen = sm.states.get(GameState.TRAVEL)
            screen.open_service("train_class", C.PortableTrainer("Book of the Wandering Master",
                                                                  portable_class=player.char_class))
            sm.transition_to(GameState.TRAVEL)
        elif service == "profession_trainer":
            # Kyle, 18 Nov 2026: "train professions or learn them. Basically a mobile class trainer or every
            # profession trainer": every profession, the ones you know first, so you can learn a new one too
            profs = sorted(C.all_professions(), key=lambda p: not player.knows_profession(p))
            screen = sm.states.get(GameState.TRAVEL)
            screen.open_service("train_prof", C.PortableTrainer("Book of Professions", portable_professions=profs))
            sm.transition_to(GameState.TRAVEL)
        else:
            return self._say(False, "That doesn't do anything yet.")
        C.mark_service_used(tm, cid, self._clock())

    # ------------------------------------------------------------ input
    def handle_event(self, event):
        new = self.bar.handle_event(event, self.scroll)
        if new is not None:
            self.scroll = new
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.search:
                    self.search, self.scroll = "", 0
                else:
                    self.state_manager.transition_to(GameState.OVERWORLD)
                return
            if event.key == pygame.K_BACKSPACE:
                self.search, self.scroll = self.search[:-1], 0
                return
            ch = getattr(event, "unicode", "") or ""
            if ch and (ch.isalnum() or ch in " '-") and len(self.search) < 24:
                self.search, self.scroll = self.search + ch, 0
                return
            if event.key == pygame.K_u and not self.search:
                self.state_manager.transition_to(GameState.OVERWORLD)
            return
        if event.type == pygame.MOUSEWHEEL:
            self.scroll = max(0, self.scroll - event.y)
            return
        if event.type != pygame.MOUSEBUTTONDOWN or getattr(event, "button", 1) != 1:
            return
        if self.close_rect.collidepoint(event.pos):
            self.state_manager.transition_to(GameState.OVERWORLD)
            return
        for rect, tab in self.tab_rects:
            if rect.collidepoint(event.pos):
                self.tab, self.scroll, self.message = tab, 0, ""
                return
        for rect, key in self.filter_rects:
            if rect.collidepoint(event.pos):
                self.filter, self.scroll = key, 0
                return
        for rect, cid, action in self.buttons:
            if rect.collidepoint(event.pos):
                self._do(cid, action)
                return

    # ------------------------------------------------------------ drawing
    def _icon(self, e, size):
        """A form shows its creature, a mount its own side view; everything else its bag icon."""
        key = (e["id"], size)
        if key in self._pics:
            return self._pics[key]
        pic = None
        try:
            if e["kind"] == "form" and e["effect"].get("sprite"):
                src = pygame.image.load(e["effect"]["sprite"]).convert_alpha()
            elif e["kind"] == "mount":
                from ui.sprite_loader import _mount_sheet
                src = _mount_sheet(e["effect"]["mount_id"], "right")
            else:
                src = None
            if src is not None:
                w, h = src.get_size()
                k = size / max(w, h)
                pic = pygame.transform.smoothscale(src, (max(1, int(w * k)), max(1, int(h * k))))
        except Exception:
            pic = None
        if pic is None:
            pic = self._bag_icon(e, size)
        self._pics[key] = pic
        return pic

    def _bag_icon(self, e, size):
        if not self.icon_ui_helper:
            return None
        try:
            return self.icon_ui_helper.get_item_icon_surface({"name": e["name"], "icon_id": e["icon_id"]},
                                                             size=size)
        except Exception:
            return None

    def render(self, screen):
        from world import collection as C
        screen.fill((10, 10, 16))
        everything = C.entries()
        have = sum(1 for e in everything if C.learned(e["id"]))
        self.renderer.draw_text(screen, "COLLECTION", (LEFT, 20), size="large", color=COLOR_GOLD)
        self.renderer.draw_text(screen, f"Shared by every character on this install.  {have} of {len(everything)} "
                                        f"learned.  Collectables turn up on the auction house.", (LEFT, 66),
                                color=GREY)
        self.filter_rects = []
        fx = LEFT
        for key, label in FILTERS:
            r = pygame.Rect(fx, 146, 110, 32)
            self.renderer.draw_button(screen, r, label, color=(70, 90, 130) if key == self.filter else (36, 40, 56))
            self.filter_rects.append((r, key))
            fx += 118
        box = pygame.Rect(fx + 12, 146, 360, 32)
        self.renderer.draw_rect(screen, box, (22, 22, 30))
        self.renderer.draw_rect(screen, box, (90, 90, 110), fill=False)
        self.renderer.draw_text(screen, (self.search + "_") if self.search else "Type to search...",
                                (box.x + 10, box.y + 6), color=COLOR_WHITE if self.search else DIM)
        self.renderer.draw_button(screen, self.close_rect, "Close (U)")

        self.tab_rects = []
        x = LEFT
        tab_w = min(186, (SCREEN_WIDTH - 2 * LEFT) // len(C.TABS) - 6)
        for tab, label in C.TABS:
            rows = C.by_tab(tab)
            n = sum(1 for e in rows if C.learned(e["id"]))
            rect = pygame.Rect(x, 98, tab_w, 38)
            self.renderer.draw_button(screen, rect, f"{label} {n}/{len(rows)}",
                                      color=(70, 90, 130) if tab == self.tab else (36, 40, 56))
            self.tab_rects.append((rect, tab))
            x += tab_w + 6

        rows = self._rows()
        per_page = ((SCREEN_HEIGHT - 60 - TOP) // (CARD_H + CARD_GAP)) * COLS
        lines = (len(rows) + COLS - 1) // COLS
        visible_lines = per_page // COLS
        self.scroll = max(0, min(self.scroll, max(0, lines - visible_lines)))
        self.bar.draw(screen, ScrollBar.track_for(pygame.Rect(LEFT, TOP, COLS * (CARD_W + CARD_GAP),
                                                               visible_lines * (CARD_H + CARD_GAP) - CARD_GAP)),
                      self.scroll, max(0, lines - visible_lines), visible_lines)
        self.buttons, self.cards = [], []
        start = self.scroll * COLS
        for k, e in enumerate(rows[start:start + per_page]):
            c, r = k % COLS, k // COLS
            rect = pygame.Rect(LEFT + c * (CARD_W + CARD_GAP), TOP + r * (CARD_H + CARD_GAP), CARD_W - GUTTER // 2,
                               CARD_H)
            self._card(screen, rect, e)

        if self.message:
            for i, line in enumerate(self.renderer.wrap_text(self.message, SCREEN_WIDTH - 60)[:2]):
                self.renderer.draw_text(screen, line, (LEFT, SCREEN_HEIGHT - 46 + i * 20),
                                        color=GREEN if self.message_ok else RED)

    def _card(self, screen, rect, e):
        from world import collection as C
        known = C.learned(e["id"])
        line, colour, actions = self._status(e)
        self.renderer.draw_rect(screen, rect, (28, 30, 40) if known else (18, 18, 24))
        self.renderer.draw_rect(screen, rect, RARITY.get(e["rarity"], COLOR_WHITE) if known else (50, 50, 60),
                                fill=False)
        icon = self._icon(e, 64)
        tx = rect.x + 12
        if icon is not None:
            if not known:
                icon = icon.copy()
                icon.fill((90, 90, 90, 255), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(icon, (rect.x + 12 + (64 - icon.get_width()) // 2, rect.y + (rect.height - icon.get_height()) // 2))
            tx = rect.x + 88
        bw = 0
        for label, action in reversed(actions):
            w = max(110, self.renderer._get_font(font_size=16).size(label)[0] + 24)
            b = pygame.Rect(rect.right - 12 - w - bw, rect.y + (rect.height - 36) // 2, w, 36)
            self.renderer.draw_button(screen, b, label, color=(60, 100, 70))
            self.buttons.append((b, e["id"], action))
            bw += w + 8
        width = rect.right - tx - 16 - bw
        name, blurb = e["name"], e["blurb"]
        if e["kind"] == "keepsake" and not known:
            name, blurb = f"A keepsake from {e['effect']['from']}", "You'll find out what it is when it's yours."
        self.renderer.draw_text(screen, self.renderer.truncate(name, width), (tx, rect.y + 6),
                                color=RARITY.get(e["rarity"], COLOR_WHITE) if known else DIM)
        self.renderer.draw_text(screen, self.renderer.truncate(blurb, width, font_size=14), (tx, rect.y + 31),
                                font_size=14, color=GREY if known else DIM)
        self.renderer.draw_text(screen, self.renderer.truncate(line, width, font_size=14), (tx, rect.y + 53),
                                font_size=14, color=colour)
        self.cards.append((rect, e))
