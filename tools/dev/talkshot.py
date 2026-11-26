import os, sys
os.environ["SDL_VIDEODRIVER"]="dummy"
import pygame
pygame.init(); pygame.display.set_mode((1280,720))
from ui.renderer import Renderer
from ui.screens.overworld_screen import OverworldScreen
from ui.banter_panel import BanterPanel
from world.banter_manager import BanterBeat
from world.conversations import get_conversations
from world.bond_manager import get_bond_manager
bm=get_bond_manager(); cv=get_conversations()
o=OverworldScreen.__new__(OverworldScreen); o.renderer=Renderer()
scr=pygame.display.get_surface()
def bg():
    scr.fill((40,60,40))
    for i in range(0,1280,64): pygame.draw.line(scr,(60,90,60),(i,0),(i,720))
# 1 talk window, before and after answering
cv.wants["sondre_stormbringer"]={"kind":"aftermath","sub":"wipe","about":None,"since":0,"reason":None}
conv=cv.open("sondre_stormbringer")
o.talk={"conv":conv,"reply":None}; bg(); o._render_party_talk(scr); pygame.image.save(scr,sys.argv[1]+"/talk1.png")
o.talk["reply"]=cv.choose("sondre_stormbringer","comfort"); bg(); o._render_party_talk(scr); pygame.image.save(scr,sys.argv[1]+"/talk2.png")
# 2 banter beat with the chip
arg=next(a for a in cv.arguments if a["id"]=="grill_upgrade")
lines=[(r,bm.name_of(r),f'"{t}"') for r,t in arg["lines"]]+[("sebastian_bloodmage",bm.name_of("sebastian_bloodmage"),'"Kyle, you tell him, you\'re the one with taste here, and then he eats his words with salt."')]
beat=BanterBeat(lines); beat.revealed=len(lines); beat.ask={"arg":"grill_upgrade","asker":"sebastian_bloodmage","other":"diego_tinker","witnesses":[]}
bg(); BanterPanel(o.renderer).render(scr, beat); pygame.image.save(scr,sys.argv[1]+"/chip.png")
# 3 argument window
o.arg_modal={"ask":beat.ask,"options":cv.ask_options(beat.ask),"reply":None,"line":lines[-1][2].strip('"')}
bg(); o._render_argument(scr); pygame.image.save(scr,sys.argv[1]+"/arg.png")
