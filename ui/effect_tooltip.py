"""What a buff or debuff IS, said the same way everywhere one is drawn.

Kyle, 10 Nov: "we need to be able to hover over enemy buffs and debuffs (THIS IS HUGE) - same
with OUR characters." And 12 Nov, for our own side: "hovering over OUR buff/debuff in combat
should say what it is (curse/poison? Disease?), the effects, turns left."

Until now an effect on screen was a coloured square or a chip with a name on it. What it did was
printed once, in the combat log, on the turn it landed, and then scrolled away.

Everything here is read off the effect's own fields - the ones the engine resolves it from - and
not from authored text, for the same reason the combat-log line is (see
StatusEffectMixin._describe_effect): hundreds of monster abilities carry no description, but
every one of them carries potency, stat_mods, absorb and duration.

Three things, used by the combat screen and the Party screen's Buffs tab:

    effect_lines(effect, holder)   the tooltip's text
    draw_effect_tooltip(...)       the box
    draw_effect_icon(...)          the square: the applying ability's real icon when there is
                                   one, otherwise a lettered tile in the effect's colour
"""
from pathlib import Path

import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_GOLD, COLOR_RED, COLOR_GREEN
from combat.status_effects import EffectType, StatusEffectMixin

_PERMANENT_DURATION = StatusEffectMixin._PERMANENT_DURATION

FONT_SIZE = 14
LINE_HEIGHT = 18
PADDING = 10
MAX_TEXT_WIDTH = 300

DEBUFF_PURPLE = (170, 100, 220)
MUTED = (165, 165, 175)

#: border, fill - gold buff / purple debuff / red DoT / green HoT, the convention the squares
#: already used.
KIND_COLORS = {
    EffectType.BUFF: (COLOR_GOLD, (50, 45, 20)),
    EffectType.DEBUFF: (DEBUFF_PURPLE, (45, 20, 50)),
    EffectType.DOT: (COLOR_RED, (50, 20, 20)),
    EffectType.HOT: (COLOR_GREEN, (20, 45, 25)),
}
KIND_NAMES = {
    EffectType.BUFF: "Buff",
    EffectType.DEBUFF: "Debuff",
    EffectType.DOT: "Damage over time",
    EffectType.HOT: "Heal over time",
}
#: Stats where the number is a percentage, so "+5 Crit" reads "+5% Crit".
_PCT_HINTS = ("_pct", "crit", "dodge", "parry", "block", "haste", "hit")

#: Stats that read better as a sentence than as "+1 Silenced".
_PLAIN_WORDS = {
    "silenced": "Silenced - basic attacks only",
    "next_hit_taken_pct": "{value}% damage from the next hit, then this is spent",
    "repeat_school_taken_pct": "{value}% damage from a hit of the same school as the last",
    "overheal_to_shield": "Healing past full health becomes a shield",
    "harmless_to_source": "Cannot damage whoever placed this",
    "weakest_school": "Spells strike as the school the target resists least",
    "miss_chance_pct": "{value}% chance to miss",
    "cc_immune": "Immune to crowd control",
}

_ICON_DIRS = [Path("assets/icons") / d for d in ("abilities", "talents", "consumables", "coa")]
_icon_cache = {}


def remaining_text(effect):
    """'3 turns left', '12 min left', or '' for something that does not run out."""
    secs = getattr(effect, "real_time_seconds", None)
    if secs is not None:
        if secs >= 60:
            return f"{int(secs // 60)} min left"
        return f"{max(0, int(secs))} sec left"
    turns = int(getattr(effect, "duration", 0) or 0)
    if turns >= _PERMANENT_DURATION // 2:
        return ""
    return f"{turns} turn{'s' if turns != 1 else ''} left"


def remaining_short(effect):
    """The number printed ON an icon: turns, minutes as '12m', or '' if permanent."""
    absorb = getattr(effect, "absorb", 0) or 0
    secs = getattr(effect, "real_time_seconds", None)
    if secs is not None:
        return f"{int(secs // 60)}m" if secs >= 60 else f"{max(0, int(secs))}s"
    turns = int(getattr(effect, "duration", 0) or 0)
    if turns >= _PERMANENT_DURATION // 2:
        return ""
    return str(turns)


def _fmt(value):
    return f"{value:.1f}".rstrip("0").rstrip(".") if isinstance(value, float) else str(value)


def _stat_lines(effect, holder):
    """One line per stat, with stacks and scaling already applied - the number in force NOW."""
    if holder is not None and hasattr(holder, "_status_mods_for"):
        mods = holder._status_mods_for(effect)
    else:
        mods = dict(getattr(effect, "stat_mods", None) or {})
    out = []
    for stat, value in mods.items():
        if not isinstance(value, (int, float)) or not value:
            continue
        if stat in _PLAIN_WORDS:                     # a state, not a number
            out.append(_PLAIN_WORDS[stat].format(value=_fmt(round(value, 1))))
            continue
        label = StatusEffectMixin.STAT_LABELS.get(stat, stat.replace("_", " ").title())
        pct = "%" if (any(h in stat for h in _PCT_HINTS) and "%" not in label) else ""
        out.append(f"{'+' if value > 0 else ''}{_fmt(round(value, 1))}{pct} {label}")
    return out


def effect_lines(effect, holder=None):
    """[(text, colour), ...] - name first."""
    border = KIND_COLORS.get(effect.effect_type, (COLOR_WHITE, None))[0]
    stacks = int(getattr(effect, "stacks", 1) or 1)
    cap = int(getattr(effect, "max_stacks", 1) or 1)
    name = effect.name or "Effect"
    if cap > 1:
        name += f"  ({stacks} of {cap} stacks)"
    lines = [(name, border)]

    # What KIND of thing it is - which is also what can take it off.
    kind = KIND_NAMES.get(effect.effect_type, "Effect")
    school = getattr(effect, "dispel_type", None)
    if school:
        lines.append((f"{kind} - {school.title()}", MUTED))
    elif effect.effect_type in (EffectType.DEBUFF, EffectType.DOT):
        lines.append((f"{kind} - cannot be dispelled", MUTED))
    else:
        lines.append((kind, MUTED))

    body = []
    if effect.effect_type == EffectType.DOT and effect.potency:
        s = getattr(effect, "damage_school", "") or "physical"
        body.append(f"{effect.tick_potency()} {s} damage each turn")
    elif effect.effect_type == EffectType.HOT and effect.potency:
        body.append(f"Heals {effect.tick_potency()} each turn")
    absorb = int(getattr(effect, "absorb", 0) or 0)
    if absorb:
        body.append(f"Absorbs the next {absorb} damage")
    if getattr(effect, "is_stun", False):
        body.append("Stunned - cannot act")
    if getattr(effect, "dot_immune", False):
        body.append("Immune to damage over time")
    body.extend(_stat_lines(effect, holder))
    if not body:
        body.append("No direct effect on stats")
    lines.extend((b, COLOR_WHITE) for b in body)

    left = remaining_text(effect)
    if left:
        lines.append((left, COLOR_WHITE))
    source = getattr(effect, "source_name", "") or ""
    if source and (holder is None or source != getattr(holder, "name", None)):
        lines.append((f"From {source}", MUTED))
    return lines


def draw_effect_tooltip(renderer, screen, effect, pos, holder=None):
    lines = effect_lines(effect, holder)
    font = renderer._get_font(font_size=FONT_SIZE)
    wrapped = []
    for text, color in lines:
        cur = ""
        for word in text.split(" "):
            cand = f"{cur} {word}" if cur else word
            if font.size(cand)[0] > MAX_TEXT_WIDTH and cur:
                wrapped.append((cur, color))
                cur = word
            else:
                cur = cand
        wrapped.append((cur, color))
    box_w = max(font.size(t)[0] for t, _ in wrapped) + PADDING * 2
    box_h = len(wrapped) * LINE_HEIGHT + PADDING * 2
    x, y = pos[0] + 16, pos[1] + 16
    x = min(x, SCREEN_WIDTH - box_w - 4)
    y = min(y, SCREEN_HEIGHT - box_h - 4)
    pygame.draw.rect(screen, (15, 15, 20), (x, y, box_w, box_h))
    pygame.draw.rect(screen, wrapped[0][1], (x, y, box_w, box_h), 2)
    ty = y + PADDING
    for text, color in wrapped:
        renderer.draw_text(screen, text, (x + PADDING, ty), font_size=FONT_SIZE, color=color)
        ty += LINE_HEIGHT
    return pygame.Rect(x, y, box_w, box_h)


def effect_icon_path(effect):
    """The real icon file for this effect, or None.

    An effect made by an ability carries that ability's id as its own (abilities.py builds
    every DoT, HoT, buff and shield with effect_id=self.ability_id), and ability art is named
    after the ability id, so most player-side effects already have their picture on disk.
    """
    eid = getattr(effect, "effect_id", "") or ""
    if eid in _icon_cache:
        return _icon_cache[eid]
    found = None
    for d in _ICON_DIRS:
        p = d / f"{eid}.png"
        if eid and p.exists():
            found = p
            break
    _icon_cache[eid] = found
    return found


_surface_cache = {}


def draw_effect_icon(renderer, screen, effect, rect, show_count=True):
    """Draw the effect's square into `rect`: art (or a lettered tile), coloured border, and the
    turns left in the corner."""
    border, fill = KIND_COLORS.get(effect.effect_type, (COLOR_WHITE, (30, 30, 30)))
    path = effect_icon_path(effect)
    surf = None
    if path is not None:
        key = (str(path), rect.w)
        surf = _surface_cache.get(key)
        if surf is None:
            try:
                img = pygame.image.load(str(path))
                img = img.convert_alpha() if pygame.display.get_surface() else img
                surf = pygame.transform.smoothscale(img, (rect.w, rect.h))
            except Exception:
                surf = False
            _surface_cache[key] = surf
    if surf:
        screen.blit(surf, rect.topleft)
    else:
        pygame.draw.rect(screen, fill, rect)
        if rect.w >= 16:
            letter = (effect.name or "?")[0].upper()
            f = renderer._get_font(font_size=max(10, rect.h - 8))
            g = f.render(letter, True, border)
            screen.blit(g, (rect.centerx - g.get_width() // 2, rect.centery - g.get_height() // 2))
    pygame.draw.rect(screen, border, rect, 2 if rect.w >= 20 else 1)

    if show_count and rect.w >= 16:
        absorb = int(getattr(effect, "absorb", 0) or 0)
        stacks = int(getattr(effect, "stacks", 1) or 1)
        f = renderer._get_font(font_size=10 if rect.w < 22 else 11)
        txt = remaining_short(effect)
        # On a small square only a TURN count is printed. "30m" does not fit in 20px and is not
        # something you need at a glance in a fight; the tooltip has it.
        if rect.w < 22 and getattr(effect, "real_time_seconds", None) is not None:
            txt = ""
        if txt:
            g = f.render(txt, True, COLOR_WHITE)
            bx, by = rect.right - g.get_width() - 1, rect.bottom - g.get_height() + 1
            pygame.draw.rect(screen, (0, 0, 0), (bx - 1, by, g.get_width() + 2, g.get_height() - 1))
            screen.blit(g, (bx, by))
        if stacks > 1:
            g = f.render(f"x{stacks}", True, COLOR_GOLD)
            pygame.draw.rect(screen, (0, 0, 0), (rect.x + 1, rect.y, g.get_width() + 1, g.get_height() - 2))
            screen.blit(g, (rect.x + 1, rect.y - 1))
