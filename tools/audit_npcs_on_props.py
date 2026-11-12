"""AUDIT (not a QA suite - it reports, it does not gate): NPCs with a prop drawn over them.

    python3 tools/audit_npcs_on_props.py

Kyle, 10 Nov: "NPCs on props." Nobody stands on a BLOCKING tile (checked: 0 of 777). What he
is seeing is art: a building's or a tree's picture is much bigger than its footprint, and an
NPC placed just behind the footprint is drawn on the roof, in the banner, in the canopy.

For every NPC tile in every zone this samples the opaque pixels of each prop sprite over
that tile and reports the NPC when more than half the tile is covered.

Measured 12 Nov: 103 of 777 NPCs. 8 are under small clutter, 12 stand at the foot of a
building (in front of the door - fine), 83 are higher up on a building or tree and read as
standing on it. Worst towns: Silverpine South, Booty Bay, Astranaar, Splintertree Post,
Brill, Freewind Post, Grom'gol.

Fixing these means moving the NPC, and an NPC's position lives in whichever of four places
put it there (vendors, ambient NPCs, recruits, and literals in world/zone_generator.py), so
it belongs with the per-town layout pass rather than an automatic nudge.
"""
import os, sys, collections
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); os.chdir(ROOT)
import pygame; pygame.init(); screen = pygame.display.set_mode((1280, 720))
from PIL import Image
from core.game_state import GameStateManager
from entities.character import Character
sm = GameStateManager(screen); sm.player = Character(name="H", char_class="Warrior", level=60)
zm = sm._live_zone_manager()
cache = {}
def cover(path, w, h, cx, cy):
    """share of tile (cx,cy) within a w x h tile sprite that is opaque"""
    key = (path, w, h)
    if key not in cache:
        try:
            im = Image.open(path).convert("RGBA").resize((w * 16, h * 16))
            cache[key] = im.getchannel("A")
        except Exception:
            cache[key] = None
    a = cache[key]
    if a is None: return 0.0
    box = a.crop((cx * 16, cy * 16, cx * 16 + 16, cy * 16 + 16))
    px = list(box.get_flattened_data()) if hasattr(box, 'get_flattened_data') else list(box.getdata())
    return sum(1 for v in px if v > 128) / len(px)
hits = []; by = collections.Counter(); zc = collections.Counter(); n_npc = 0
for name, e in zm.zones.items():
    t = e["tilemap"] if isinstance(e, dict) else e
    lms = [l for l in (getattr(t, "landmarks", []) or [])]
    npcs = [(x, y) for y in range(t.height) for x in range(t.width) if t.interaction_layer[y][x] == "npc"]
    n_npc += len(npcs)
    for (x, y) in npcs:
        for l in lms:
            ax, ay, w, h = l["anchor_x"], l["anchor_y"], l["width_tiles"], l["height_tiles"]
            if ax <= x < ax + w and ay <= y < ay + h:
                cv = cover(l["sprite_key"], w, h, x - ax, y - ay)
                if cv > 0.5:
                    sp = os.path.basename(l["sprite_key"])[:-4]
                    hits.append((name, x, y, sp, round(cv, 2), (ax, ay, w, h))); by[sp] += 1; zc[name] += 1
                    break
print(n_npc, "npcs;", len(hits), "have a prop's solid pixels over their tile")
print(by.most_common(40))
print(zc.most_common(25))
for h in sorted(hits):
    print("  ", h[0], (h[1], h[2]), "under", h[3])
