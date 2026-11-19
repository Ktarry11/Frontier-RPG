"""Small widgets for the auction house and the mailbox: text boxes, a gold/silver/copper box, check boxes, a
dropdown, coins with their icons, good icons and tooltips.

Kept here rather than in either screen because both use all of them, and the auction house's Browse, Bids and
Auctions tabs use them three different ways.
"""
import pygame

from config import SCREEN_HEIGHT, SCREEN_WIDTH
from ui import theme

ICON_DIR = "assets/ui/auction/icons"
_ICONS = {}

RARITY_COLOUR = {
    "poor": (157, 157, 157), "common": (240, 240, 240), "uncommon": (30, 255, 0), "rare": (0, 112, 221),
    "epic": (163, 53, 238), "legendary": (255, 128, 0), "quest": (200, 30, 45),
}


def ui_icon(name, size):
    """One of Kyle's auction and mail icons (assets/ui/auction/icons/), scaled and cached."""
    key = (name, size)
    s = _ICONS.get(key)
    if s is None:
        try:
            raw = pygame.image.load(f"{ICON_DIR}/{name}.png").convert_alpha()
            s = pygame.transform.smoothscale(raw, (size, size))
        except Exception:
            s = pygame.Surface((size, size), pygame.SRCALPHA)
        _ICONS[key] = s
    return s


def coin_parts(copper):
    copper = max(0, int(copper))
    g, rem = divmod(copper, 10000)
    s, c = divmod(rem, 100)
    return g, s, c


def draw_coins(renderer, screen, copper, pos, right=False, colour=None, size="small", icon=14, show_zero=False):
    """'12 (gold) 40 (silver) 5 (copper)' with Kyle's coin icons. Returns the width drawn. right=True puts the
    right edge at pos."""
    g, s, c = coin_parts(copper)
    parts = []
    if g:
        parts.append((g, "coin_gold"))
    if s or (g and c):
        parts.append((s, "coin_silver"))
    if c or not parts or show_zero:
        parts.append((c, "coin_copper"))
    font = renderer._get_font(size)
    colour = colour or theme.TEXT
    pieces = []
    w = 0
    for n, ic in parts:
        surf = font.render(str(n), True, colour)
        pieces.append((surf, ic))
        w += surf.get_width() + 2 + icon + 5
    w -= 5
    x, y = pos
    if right:
        x -= w
    for surf, ic in pieces:
        screen.blit(surf, (x, y))
        x += surf.get_width() + 2
        screen.blit(ui_icon(ic, icon), (x, y + max(0, (surf.get_height() - icon) // 2)))
        x += icon + 5
    return w


# ------------------------------------------------------------------ inputs
class TextBox:
    """A one-line box. digits=True takes only numbers. Click to focus; Enter fires on_enter."""

    def __init__(self, rect, text="", digits=False, max_len=40, placeholder="", on_enter=None):
        self.rect = pygame.Rect(rect)
        self.text = str(text)
        self.digits = digits
        self.max_len = max_len
        self.placeholder = placeholder
        self.focus = False
        self.on_enter = on_enter

    @property
    def value(self):
        if self.digits:
            try:
                return int(self.text or 0)
            except ValueError:
                return 0
        return self.text

    def set(self, v):
        self.text = str(v)

    def handle(self, event):
        """True if the event was this box's."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            was = self.focus
            self.focus = self.rect.collidepoint(event.pos)
            return self.focus or was and False
        if event.type == pygame.KEYDOWN and self.focus:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if self.on_enter:
                    self.on_enter()
            elif event.key in (pygame.K_TAB, pygame.K_ESCAPE):
                self.focus = False
                return event.key == pygame.K_TAB
            else:
                ch = event.unicode or ""
                if ch and ch.isprintable() and len(self.text) < self.max_len:
                    if not self.digits or ch.isdigit():
                        self.text += ch
            return True
        return False

    def draw(self, renderer, screen, label=None):
        pygame.draw.rect(screen, (12, 11, 15), self.rect)
        pygame.draw.rect(screen, theme.FRAME_SELECTED if self.focus else theme.FRAME_INNER, self.rect, 1)
        shown = self.text if self.text or self.focus else self.placeholder
        colour = theme.TEXT if self.text else theme.TEXT_DIM
        font = renderer._get_font("small")
        surf = font.render(shown, True, colour)
        clip = screen.get_clip()
        screen.set_clip(self.rect.inflate(-4, -2))
        tx = self.rect.x + 5 if not self.digits else self.rect.right - 5 - surf.get_width()
        screen.blit(surf, (tx, self.rect.y + (self.rect.height - surf.get_height()) // 2))
        if self.focus and (pygame.time.get_ticks() // 500) % 2:
            cx = tx + surf.get_width() + 1 if self.text else self.rect.x + 5
            pygame.draw.line(screen, theme.TEXT, (cx, self.rect.y + 4), (cx, self.rect.bottom - 4))
        screen.set_clip(clip)
        if label:
            renderer.draw_text(screen, label, (self.rect.x, self.rect.y - 17), size="small", color=theme.TEXT_DIM)


class MoneyBox:
    """Three boxes, gold / silver / copper, each with its coin."""

    def __init__(self, x, y, gold_w=58):
        self.g = TextBox((x, y, gold_w, 24), digits=True, max_len=6)
        self.s = TextBox((x + gold_w + 22, y, 34, 24), digits=True, max_len=2)
        self.c = TextBox((x + gold_w + 22 + 34 + 22, y, 34, 24), digits=True, max_len=2)
        self.boxes = (self.g, self.s, self.c)

    @property
    def rect(self):
        return self.g.rect.union(self.c.rect.inflate(22, 0))

    @property
    def value(self):
        return self.g.value * 10000 + min(99, self.s.value) * 100 + min(99, self.c.value)

    def set(self, copper):
        g, s, c = coin_parts(copper)
        self.g.set(g if g else "")
        self.s.set(s if (s or g) else "")
        self.c.set(c)

    @property
    def focus(self):
        return any(b.focus for b in self.boxes)

    def handle(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            for i, b in enumerate(self.boxes):
                if b.focus:
                    b.focus = False
                    self.boxes[(i + 1) % 3].focus = True
                    return True
        hit = False
        for b in self.boxes:
            hit = b.handle(event) or hit
        return hit

    def draw(self, renderer, screen, label=None):
        for b, ic in zip(self.boxes, ("coin_gold", "coin_silver", "coin_copper")):
            b.draw(renderer, screen)
            screen.blit(ui_icon(ic, 16), (b.rect.right + 3, b.rect.y + 4))
        if label:
            renderer.draw_text(screen, label, (self.g.rect.x, self.g.rect.y - 17), size="small",
                               color=theme.TEXT_DIM)


class CheckBox:
    def __init__(self, rect, label, checked=False):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.checked = checked

    def hit_rect(self, renderer):
        w = renderer._get_font("small").size(self.label)[0]
        return pygame.Rect(self.rect.x, self.rect.y, self.rect.width + 6 + w, self.rect.height)

    def handle(self, event, renderer):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hit_rect(renderer).collidepoint(
                event.pos):
            self.checked = not self.checked
            return True
        return False

    def draw(self, renderer, screen):
        pygame.draw.rect(screen, (12, 11, 15), self.rect)
        pygame.draw.rect(screen, theme.FRAME, self.rect, 1)
        if self.checked:
            r = self.rect.inflate(-6, -6)
            pygame.draw.line(screen, theme.ACCENT, (r.x, r.centery), (r.centerx - 1, r.bottom), 2)
            pygame.draw.line(screen, theme.ACCENT, (r.centerx - 1, r.bottom), (r.right, r.y), 2)
        renderer.draw_text(screen, self.label, (self.rect.right + 6, self.rect.y + 1), size="small",
                           color=theme.TEXT)


class Dropdown:
    """A box that opens a list of options below it."""

    def __init__(self, rect, options, index=0):
        self.rect = pygame.Rect(rect)
        self.options = list(options)          # [(label, value, colour or None)]
        self.index = index
        self.open = False

    @property
    def value(self):
        return self.options[self.index][1]

    def _item_rect(self, i):
        return pygame.Rect(self.rect.x, self.rect.bottom + i * self.rect.height, self.rect.width, self.rect.height)

    def handle(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return False
        if self.open:
            for i in range(len(self.options)):
                if self._item_rect(i).collidepoint(event.pos):
                    self.index = i
                    self.open = False
                    return True
            self.open = False
            return self.rect.collidepoint(event.pos)
        if self.rect.collidepoint(event.pos):
            self.open = True
            return True
        return False

    def draw(self, renderer, screen):
        pygame.draw.rect(screen, (12, 11, 15), self.rect)
        pygame.draw.rect(screen, theme.FRAME, self.rect, 1)
        label, _v, col = self.options[self.index]
        renderer.draw_text(screen, label, (self.rect.x + 6, self.rect.y + 4), size="small", color=col or theme.TEXT)
        cx, cy = self.rect.right - 11, self.rect.centery
        pygame.draw.polygon(screen, theme.ACCENT, [(cx - 5, cy - 2), (cx + 5, cy - 2), (cx, cy + 4)])

    def draw_open(self, renderer, screen):
        """Drawn last, over everything else."""
        if not self.open:
            return
        for i, (label, _v, col) in enumerate(self.options):
            r = self._item_rect(i)
            hover = r.collidepoint(pygame.mouse.get_pos())
            pygame.draw.rect(screen, (40, 37, 46) if hover else (18, 17, 22), r)
            pygame.draw.rect(screen, theme.FRAME_INNER, r, 1)
            renderer.draw_text(screen, label, (r.x + 6, r.y + 4), size="small", color=col or theme.TEXT)


class Button:
    def __init__(self, rect, label, enabled=True):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.enabled = enabled

    def clicked(self, event):
        return (self.enabled and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                and self.rect.collidepoint(event.pos))

    def draw(self, renderer, screen):
        if self.enabled:
            hover = self.rect.collidepoint(pygame.mouse.get_pos())
            renderer.draw_button(screen, self.rect, self.label, color=theme.FRAME_SELECTED if hover else None)
        else:
            renderer.draw_button(screen, self.rect, self.label, color=theme.FRAME_DISABLED,
                                 text_color=theme.TEXT_DISABLED)


# ------------------------------------------------------------------ goods: icons and tooltips
def draw_icon(screen, icon_helper, icon, rect, rarity="common"):
    """icon is an Auction's (kind, icon_id, material_type, consumable_id), or an object in the bags."""
    size = min(rect.width, rect.height) - 4
    surf = None
    try:
        if isinstance(icon, (list, tuple)):
            kind, icon_id, mtype, cid = (list(icon) + ["", "", "", ""])[:4]
        else:
            from world.market import goods as G
            kind = G.kind_of(icon)
            icon_id = getattr(icon, "icon_id", "") or ""
            mtype = getattr(icon, "material_type", "") or ""
            cid = getattr(icon, "consumable_id", "") or ""
        if kind == "material" and icon_id:
            from world.gathering_manager import MATERIAL_TYPE_FOLDERS
            from ui.sprite_loader import get_icon_sprite
            folder = MATERIAL_TYPE_FOLDERS.get(mtype, mtype)
            surf = get_icon_sprite(f"assets/gathering_nodes/{folder}/{icon_id}.png", size)
        elif kind == "consumable":
            from entities.consumable_icons import icon_for
            iid = icon_for(cid) if cid else icon_id
            if iid and icon_helper:
                surf = icon_helper.get_item_icon_surface({"name": "", "icon_id": iid}, size=size)
        elif icon_helper:
            surf = icon_helper.get_item_icon_surface({"name": "", "icon_id": icon_id or None, "rarity": rarity},
                                                     size=size)
    except Exception:
        surf = None
    pygame.draw.rect(screen, (16, 15, 20), rect)
    if surf is not None:
        screen.blit(surf, (rect.x + (rect.width - size) // 2, rect.y + (rect.height - size) // 2))
    pygame.draw.rect(screen, RARITY_COLOUR.get(rarity, theme.FRAME_INNER), rect, 1)


def good_lines(good, subject=None):
    """Tooltip lines for a good: [(text, colour)]. subject: who's looking (the player), so a recipe can say whether
    they can learn it and whether they already know it."""
    from world.market import catalog as C
    from world.market import goods as G
    obj = G.unpack(good)
    rarity = C.rarity_of(good)
    col = RARITY_COLOUR.get(rarity, theme.TEXT)
    out = [(G.name(good) + (f" x{G.quantity(good)}" if G.quantity(good) > 1 else ""), col)]
    k = good["kind"]
    if k == G.GEAR:
        if getattr(obj, "recipe_id", None):
            # THE SAME CARD AS THE BAGS AND THE VENDORS (ui/recipe_tooltip.py). Kyle, 19 Nov 2026: "When hovering over
            # recipes in the AH we should be able to see what it does". It showed only the scroll's flavour line:
            # now the trade and skill it needs, what it makes and what that does, and the materials.
            from ui.recipe_tooltip import recipe_lines
            out.extend((t, c) for t, c in recipe_lines(obj, subject) if t is not None)
            sell = G.sell_price(good)
            if sell:
                out.append((f"__coins__{sell * G.quantity(good)}", theme.TEXT_DIM))
            return out
        from ui.item_kind import item_kind
        if getattr(obj, "bag_capacity", 0):
            out.append((f"{obj.bag_capacity} Slot Bag", theme.TEXT))
        else:
            kind = item_kind(obj)
            armor = getattr(obj, "armor_type", None)
            if armor in ("cloth", "leather", "mail", "plate") and not getattr(obj, "weapon_type", None):
                kind = f"{armor.title()} {str(obj.slot).replace('_', ' ').title()}"
            out.append((kind or str(obj.slot).replace("_", " ").title(), theme.TEXT))
        if getattr(obj, "armor_value", 0):
            out.append((f"{obj.armor_value} Armor", theme.TEXT))
        if getattr(obj, "weapon_damage_max", 0):
            out.append((f"{obj.weapon_damage_min} - {obj.weapon_damage_max} Damage    Speed {obj.attack_speed:.2f}",
                        theme.TEXT))
        for stat, val in (getattr(obj, "primary_stats", {}) or {}).items():
            out.append((f"+{val} {stat.replace('_', ' ').title()}", theme.TEXT))
        from entities.power_scale import item_stat_line
        for stat, val in (getattr(obj, "secondary_stats", {}) or {}).items():
            out.append((item_stat_line(stat, val), (30, 255, 0)))
        try:
            from world.enchanting import tooltip_lines as _ench
            for line in _ench(obj):
                out.append((line, (30, 255, 0)))
        except Exception:
            pass
        out.append((f"Item level {obj.item_level}", theme.TEXT_DIM))
        out.append((f"Requires level {obj.required_level}", theme.TEXT_DIM))
        from world.rep_items import requirement_text as _rep_text
        if _rep_text(obj):
            out.append((_rep_text(obj), theme.TEXT_DIM))
        if getattr(obj, "flavor_text", ""):
            out.append((f'"{obj.flavor_text}"', (255, 209, 0)))
    elif k == G.MATERIAL:
        out.append(((str(getattr(obj, "profession", "") or "").replace("_", " ").title() + " material").strip(),
                    theme.TEXT_DIM))
        if getattr(obj, "description", ""):
            out.append((obj.description, theme.TEXT))
        try:
            from world.material_sources import lines
            for line in lines(obj.material_id)[:2]:
                out.append((line, theme.TEXT_DIM))
        except Exception:
            pass
    elif k == G.CONSUMABLE:
        out.append((str(obj.consumable_type).replace("_", " ").title(), theme.TEXT_DIM))
        if getattr(obj, "description", ""):
            out.append((obj.description, theme.TEXT))
        if obj.required_level:
            out.append((f"Requires level {obj.required_level}", theme.TEXT_DIM))
    else:
        if getattr(obj, "description", ""):
            out.append((obj.description, theme.TEXT_DIM))
    sell = G.sell_price(good)
    if sell:
        out.append((f"__coins__{sell * G.quantity(good)}", theme.TEXT_DIM))
    return out


def draw_tooltip(renderer, screen, lines, pos, width=300, extra=None):
    """Lines of (text, colour); a line '__coins__N' draws 'Sells for' with coins. extra: more lines below."""
    lines = list(lines) + list(extra or [])
    wrapped = []
    for text, col in lines:
        if str(text).startswith("__coins__"):
            wrapped.append((text, col))
            continue
        for w in renderer.wrap_text(str(text), width - 16, size="small"):
            wrapped.append((w, col))
    h = 10 + 18 * len(wrapped)
    x = min(pos[0] + 16, SCREEN_WIDTH - width - 6)
    y = min(pos[1] + 12, SCREEN_HEIGHT - h - 6)
    box = pygame.Rect(x, y, width, h)
    pygame.draw.rect(screen, (14, 13, 20), box)
    pygame.draw.rect(screen, theme.FRAME, box, 1)
    for i, (text, col) in enumerate(wrapped):
        ty = y + 5 + 18 * i
        if str(text).startswith("__coins__"):
            renderer.draw_text(screen, "Sells to a vendor for", (x + 8, ty), size="small", color=col)
            draw_coins(renderer, screen, int(text[9:]), (x + width - 8, ty), right=True)
        elif str(text).startswith("__price__"):
            label, n = text[9:].split("|")
            renderer.draw_text(screen, label, (x + 8, ty), size="small", color=col)
            draw_coins(renderer, screen, int(n), (x + width - 8, ty), right=True)
        else:
            renderer.draw_text(screen, text, (x + 8, ty), size="small", color=col)
