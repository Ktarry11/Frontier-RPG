"""Frontier Dark - the single source of truth for the game's UI look.

Kyle picked this over Dragon Quest and Final Fantasy styling (2026-10-26)
after seeing all three rendered. It is Final Fantasy's STRUCTURE - serif
type, gradient window body, bevelled frame, real text hierarchy - in the
palette the game already uses, because two things already constrain the
art direction:

  * The icon art is painterly semi-realistic WoW-style (the 48 potion icons,
    the gear and material sheets). A pixel/bitmap font beside painterly icons
    reads as two games stapled together, which is what ruled out the Dragon
    Quest look.
  * Rarity colours are WoW's - green uncommons, blue rares, purple epics.
    They go muddy on Final Fantasy's bright blue window. On charcoal they pop.

WHY A THEME MODULE AND NOT COLOURS IN EACH SCREEN
-------------------------------------------------
26 screens draw their own UI. Before this, every panel colour was a literal
tuple at the call site, so a restyle meant touching all of them. Everything
visual now resolves here, which is also what makes a future second theme (or
Kyle changing his mind about the gold) a one-file change.

Text is already fully centralised - all 365 draw_text calls in the UI go
through Renderer - so the font swap alone restyles every screen at once.
Panels are only partly centralised (57 through Renderer, 150 raw
pygame.draw.rect calls), so those migrate screen by screen; see
Renderer.draw_panel.
"""
from pathlib import Path

_FONT_DIR = Path(__file__).parent.parent / "assets" / "fonts"

#: Lora, an OFL-licensed serif, vendored into the repo rather than resolved
#: from the system so the game looks the same on every machine. The previous
#: font was pygame.font.Font(None, ...) - the built-in default - which is the
#: single biggest reason the UI read as an unfinished prototype.
FONT_REGULAR = str(_FONT_DIR / "Lora-Regular.ttf")
FONT_BOLD = str(_FONT_DIR / "Lora-Bold.ttf")
FONT_ITALIC = str(_FONT_DIR / "Lora-Italic.ttf")

#: Pixel sizes for the three named fonts.
#:
#: These are NOT the old numbers. pygame's default font and a real TTF measure
#: `size` differently: Lora at the old 20px renders ~45% wider, which would
#: have overflowed panels across every screen. These sizes were chosen by
#: measuring both fonts on the same string until the WIDTHS matched - width is
#: the dimension that breaks a layout, since a too-wide string runs out of its
#: panel while a slightly taller one only tightens line spacing.
#:
#:     old default 20px -> Lora 14px   (200px wide vs 206px)
#:     old default 16px -> Lora 12px   (170px wide vs 178px)
#:     old default 40px -> Lora 29px   (422px wide vs 425px)
FONT_SIZE_LARGE = 29
FONT_SIZE_NORMAL = 14
FONT_SIZE_SMALL = 12

# ── Palette ───────────────────────────────────────────────────────────────
#: Window body, top and bottom of its vertical gradient. The gradient is what
#: separates this from the old flat pygame.draw.rect fill more than any other
#: single thing.
PANEL_TOP = (38, 36, 44)
PANEL_BOTTOM = (20, 19, 25)
#: A darker body for panels that sit INSIDE another panel (a list row inside a
#: list), so nesting reads without a second frame.
PANEL_INSET_TOP = (28, 27, 33)
PANEL_INSET_BOTTOM = (16, 15, 20)

FRAME = (150, 124, 62)          # the gold frame line
FRAME_INNER = (92, 76, 40)      # the dimmer inner keyline
FRAME_CORNER = (214, 180, 96)   # corner studs
FRAME_SELECTED = (236, 206, 130)  # frame colour when a row is selected
FRAME_DISABLED = (78, 74, 70)

SCREEN_BG = (14, 13, 17)

TEXT = (222, 218, 210)          # body
TEXT_HEADING = (236, 214, 158)  # panel titles, warm off-gold
TEXT_DIM = (140, 134, 124)      # secondary / requirements / flavour
TEXT_DISABLED = (96, 92, 88)
ACCENT = (214, 180, 96)         # gold, for emphasis and currency

OK = (140, 220, 160)
WARN = (236, 196, 110)
BAD = (240, 140, 140)

#: Button fills, by state.
BTN_TOP = (48, 45, 54)
BTN_BOTTOM = (28, 26, 33)
BTN_TOP_HOVER = (64, 60, 70)
BTN_BOTTOM_HOVER = (38, 36, 44)

# ── Metrics ───────────────────────────────────────────────────────────────
PANEL_PAD = 14          # inside a panel, from frame to content
ROW_H = 44              # a standard list row
CORNER_STUD = 3         # radius of the corner dots
