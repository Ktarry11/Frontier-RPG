import contextlib, io, os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy"); os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, "."); 
import pygame
pygame.init(); screen = pygame.display.set_mode((1280, 720))
from core.game_state import GameStateManager
from entities.character import Character
from ui.screens.map_screen import MapScreen
with contextlib.redirect_stdout(io.StringIO()):
    sm = GameStateManager(screen)
    sm.player = Character(name="Hero", char_class="Warrior", level=30)
    sm.player.known_professions = ["mining", "herbalism", "woodcutting", "fishing"]
    zm = sm._live_zone_manager()
ms = MapScreen(sm)
for zone, out in [a.split("=") for a in sys.argv[1:]]:
    with contextlib.redirect_stdout(io.StringIO()):
        zm.transition_to_zone(zone, via_portal=False)
    screen.fill((0, 0, 0)); ms.render(screen)
    pygame.image.save(screen, out); print("saved", out)
