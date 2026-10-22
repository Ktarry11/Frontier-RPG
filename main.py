import pygame
import sys
import ctypes
from pathlib import Path
from core.game_state import GameStateManager
from core.game_states import GameState
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from icon_system_core import IconRegistry, IconRenderer
from icon_migration_and_ui import IconUIHelper


def _set_windows_dpi_awareness():
    """Without this, Windows applies its own display scaling (125%/150%/
    etc at anything above 1080p-ish) to the WHOLE window before it ever
    reaches pygame - so a window created at exactly 1280x720 still renders
    physically smaller on screen than that, clipping UI that was laid out
    assuming the full 1280x720 was visible. This is Kyle's "opens small by
    default" bug: nothing in the pygame layout code was wrong, Windows was
    shrinking the finished window. Telling Windows this process handles its
    own scaling (per-monitor DPI aware) stops that shrink. No-op / silently
    skipped on non-Windows platforms.
    """
    if sys.platform != "win32":
        return
    try:
        # PROCESS_PER_MONITOR_DPI_AWARE = 2 - handles DPI changes when the
        # window moves between monitors with different scaling, not just a
        # one-time system-DPI snapshot (PROCESS_SYSTEM_DPI_AWARE = 1 would
        # only fix the initial launch monitor).
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except (AttributeError, OSError):
        # shcore.SetProcessDpiAwareness needs Windows 8.1+; fall back to
        # the older/coarser user32 call so pre-8.1 Windows still gets SOME
        # DPI awareness rather than none.
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except (AttributeError, OSError):
            pass  # Best-effort - never block launch over this.


def _compute_letterbox(display_size, logical_size):
    """Real shared geometry for aspect-correct fullscreen scaling - the
    SAME numbers used both to render (scale+center the logical surface
    onto the display) and to translate mouse input (display coords ->
    logical coords) MUST come from one place, or the two could drift
    apart (e.g. render uses a freshly computed target_w/h but input
    translation uses a slightly different formula) and clicks would
    silently land on the wrong logical position even though the visuals
    look correct. Returns (target_w, target_h, offset_x, offset_y).
    """
    dw, dh = display_size
    lw, lh = logical_size
    target_w = dw
    target_h = int(dw * lh / lw)
    if target_h > dh:
        target_h = dh
        target_w = int(dh * lw / lh)
    offset_x = (dw - target_w) // 2
    offset_y = (dh - target_h) // 2
    return target_w, target_h, offset_x, offset_y


def main():
    """Main game loop."""
    _set_windows_dpi_awareness()
    pygame.init()

    # Real fixed LOGICAL resolution every screen's pixel-math is written
    # against (cast_screen.py, background_screen.py, party_screen.py,
    # etc. all lay out real absolute pixel positions assuming exactly
    # 1280x720) - this surface is what every screen actually renders to,
    # completely unchanged from before fullscreen support existed. The
    # real DISPLAY surface (created below, toggleable between windowed
    # and fullscreen) is a separate, possibly-larger surface that the
    # logical surface gets scaled onto once per frame - so fullscreen
    # means "the same 1280x720 game, shown bigger," not "every screen's
    # layout math has to become resolution-independent." This is the
    # standard real pattern for adding fullscreen to a fixed-resolution
    # pygame game without a full UI rewrite.
    logical_screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    is_fullscreen = False
    display_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Frontier RPG")
    clock = pygame.time.Clock()
    
    # Initialize icon system (one-time)
    icon_registry = IconRegistry(data_dir=Path("data"))
    icon_renderer = IconRenderer(icon_registry, cache_dir=Path("assets/icons"))
    icon_ui_helper = IconUIHelper(icon_registry, icon_renderer)
    
    # Initialize game state manager - built against the LOGICAL surface,
    # so every screen's internal geometry (mouse hit-testing rects
    # included) is computed in the same fixed 1280x720 space it's always
    # used, regardless of what size the real window is.
    state_manager = GameStateManager(logical_screen)
    
    # Pass icon_ui_helper to state manager
    state_manager.icon_ui_helper = icon_ui_helper
    # Patch it onto every already-constructed screen that wants one.
    # GameStateManager builds all its screens in __init__, before this
    # icon_ui_helper exists (it needs `screen` from pygame.display.set_mode,
    # which doesn't happen until main() runs) - every screen gets
    # icon_ui_helper=None baked in at construction. This loop is the fix:
    # previously only GameState.SKILLS was patched by hand here, so every
    # OTHER screen wanting icons (InventoryScreen included) silently kept
    # a dead None reference and never rendered real icon art, no matter
    # what icon system work happened elsewhere. Loop over every
    # constructed screen instead of hand-listing them one at a time, so
    # adding icon support to a new screen later doesn't require
    # remembering to patch it here too.
    for game_screen in state_manager.states.values():
        if hasattr(game_screen, 'icon_ui_helper'):
            game_screen.icon_ui_helper = icon_ui_helper
    
    # Screens read pygame.mouse.get_pos() for hover / wheel hit-tests, but every screen
    # is laid out in the fixed 1280x720 LOGICAL space.  get_pos() reports real window
    # coordinates, which only match while the window is exactly 1280x720 (fullscreen,
    # F11, or a scaled window broke every get_pos() based hit-test, e.g. wheel
    # scrolling).  Replace it with a logical-space version for the whole game.
    _real_get_pos = pygame.mouse.get_pos
    _lb = {"geom": (SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0)}

    def _logical_mouse_pos():
        raw_x, raw_y = _real_get_pos()
        tw, th, ox, oy = _lb["geom"]
        lx = int((raw_x - ox) * SCREEN_WIDTH / tw)
        ly = int((raw_y - oy) * SCREEN_HEIGHT / th)
        return (max(0, min(SCREEN_WIDTH - 1, lx)), max(0, min(SCREEN_HEIGHT - 1, ly)))

    pygame.mouse.get_pos = _logical_mouse_pos

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds

        # Real mouse-position translation: every screen's click/hover
        # hit-testing reads pygame.mouse.get_pos() or event.pos directly,
        # both of which report REAL DISPLAY coordinates - correct for a
        # 1:1 windowed 1280x720 window, but wrong the moment the display
        # surface is scaled for fullscreen. Uses the SAME _compute_letterbox
        # geometry the render block below uses, so input and visuals can
        # never drift apart (see that function's docstring). A click that
        # lands in the letterbox dead-zone (the black bars on a non-16:9
        # display) has no valid logical position - clamped into the
        # nearest edge rather than producing a wildly out-of-range
        # coordinate that could accidentally hit-test something.
        target_w, target_h, offset_x, offset_y = _compute_letterbox(
            display_screen.get_size(), (SCREEN_WIDTH, SCREEN_HEIGHT))
        scale_x = SCREEN_WIDTH / target_w
        scale_y = SCREEN_HEIGHT / target_h
        _lb["geom"] = (target_w, target_h, offset_x, offset_y)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                # Real fullscreen toggle - per Kyle's ask, since he doesn't
                # have the option yet. F11 matches the near-universal
                # browser/app convention rather than inventing a new key.
                is_fullscreen = not is_fullscreen
                if is_fullscreen:
                    display_screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    display_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                continue
            if hasattr(event, "pos"):
                raw_x, raw_y = event.pos
                logical_x = int((raw_x - offset_x) * scale_x)
                logical_y = int((raw_y - offset_y) * scale_y)
                logical_x = max(0, min(SCREEN_WIDTH - 1, logical_x))
                logical_y = max(0, min(SCREEN_HEIGHT - 1, logical_y))
                event.pos = (logical_x, logical_y)
            state_manager.handle_event(event)
        
        # Update current state
        state_manager.update(dt)
        
        # Render current state to the fixed logical surface (unchanged
        # geometry), then scale that whole finished frame onto whatever
        # size the real display surface actually is.
        logical_screen.fill((20, 20, 20))  # Dark background
        state_manager.render(logical_screen)

        if display_screen.get_size() == (SCREEN_WIDTH, SCREEN_HEIGHT):
            display_screen.blit(logical_screen, (0, 0))
        else:
            # Real fix for two separate complaints:
            #   1. "Low quality" - transform.scale is a fast but crude
            #      nearest-neighbor-ish resize; smoothscale does real
            #      bilinear filtering, which is what actually matters
            #      when stretching a small 1280x720 surface up to a
            #      1440p/4K monitor in fullscreen (a large scale factor
            #      makes the blockiness far more visible than it was at
            #      windowed size).
            #   2. "Stretches" - scaling directly to display_screen.
            #      get_size() distorts the aspect ratio on any monitor
            #      that isn't exactly 16:9 (1280x720's ratio). Real fix:
            #      _compute_letterbox finds the largest 16:9 size that
            #      fits inside the real display (never distorting
            #      proportions) and centers it with real letterbox bars
            #      on whichever axis has leftover space - same geometry
            #      the input-translation block above uses, so clicks and
            #      visuals can never drift apart.
            target_w, target_h, offset_x, offset_y = _compute_letterbox(
                display_screen.get_size(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            scaled = pygame.transform.smoothscale(logical_screen, (target_w, target_h))
            display_screen.fill((0, 0, 0))
            display_screen.blit(scaled, (offset_x, offset_y))
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
