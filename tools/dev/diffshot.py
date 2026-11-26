import os, sys
os.environ["SDL_VIDEODRIVER"]="dummy"
import pygame
pygame.init(); pygame.display.set_mode((1280,720))
from ui.renderer import Renderer
from ui.screens.overworld_screen import OverworldScreen
from entities.party import Party
from world import player_difficulty as pd, xp_rate
class P: name="x"; level=30
party=Party.__new__(Party); party.xp_rate=1.5; party.difficulty=pd.fresh()
pd.bind(party); xp_rate.bind(party)
pd.set_step(party,"dungeon","health",1.5); pd.set_step(party,"dungeon","damage",0.75); pd.set_step(party,"skull","damage",2.0)
o=OverworldScreen.__new__(OverworldScreen); o.renderer=Renderer()
bg=pygame.image.load(sys.argv[1]).convert() if len(sys.argv)>3 else None
for tab,out in (("xp",sys.argv[1]),("dungeon",sys.argv[2])):
    scr=pygame.display.get_surface(); scr.fill((40,60,40))
    for i in range(0,1280,64):
        pygame.draw.line(scr,(60,90,60),(i,0),(i,720))
    o.difficulty_tab=tab; o.difficulty_rects=[]
    o.XP_TOGGLE_X, o.XP_TOGGLE_W, o.BADGE_Y = 840, 230, 668
    o._render_xp_toggle(scr)
    o._render_difficulty(scr)
    pygame.image.save(scr,out)
scr.fill((40,60,40)); o._render_xp_toggle(scr)
pygame.image.save(scr.subsurface(pygame.Rect(800,640,300,80)), sys.argv[1].replace(".png","_hud.png"))
