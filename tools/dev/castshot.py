import contextlib, io, os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy"); os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, ".")
import pygame
pygame.init(); screen = pygame.display.set_mode((1280, 720))
from core.game_state import GameStateManager
from entities.character import Character
from combat.status_effects import StatusEffect, EffectType
from ui.screens.cast_screen import CastScreen
with contextlib.redirect_stdout(io.StringIO()):
    sm = GameStateManager(screen)
    sm.player = Character(name="DugorShaman", char_class="Shaman", level=30)
party = sm.get_party()
others = [Character(name="Diego Salazar", char_class="Tinker", level=30), Character(name="Sondre Haugen", char_class="Stormbringer", level=30)]
for c in others:
    try: party.add_member(c)
    except Exception as e: print("add", e)
buffs = [("shaman_lightning_shield","Lightning Shield",8),("druid_mark_of_the_wild","Mark of the Wild",None),
         ("priest_power_word_fortitude","Power Word: Fortitude",None),("well_fed","Well Fed",None),("food_buff_xyz","Spiced Chili",None)]
for m in party.living_members():
    for eid,name,turns in buffs:
        e = StatusEffect(eid, name, EffectType.BUFF, turns or 10, stat_mods={"stamina": 10},
                         real_time_seconds=None if turns else 1500)
        m._effects().append(e) if hasattr(m, "_effects") and isinstance(m._effects(), list) else m.add_status_effect(e)
cs = CastScreen(sm)
from icon_migration_and_ui import IconUIHelper
screen.fill((0,0,0)); cs.render(screen)
hits = cs._effect_hits; print(len(hits), "buff icons")
cs._pick_caster(party.living_members()[2]); r = hits[1][0]; cs.mouse_pos = (5,5)
screen.fill((0,0,0)); cs.render(screen)
pygame.image.save(screen, sys.argv[1]); print("saved")
