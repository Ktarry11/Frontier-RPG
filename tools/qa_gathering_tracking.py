"""
The map shows gathering nodes for the trades you have learned - and only those.

Kyle, 10 Nov: gathering tracking, "WoW-style Find Minerals / Herbs / wood on the map."

With the real map screen in a real zone:
  1. a character with no gathering trade sees no nodes and no node rows in the legend
  2. a miner sees every ungathered ore vein in the zone and nothing else; a herbalist the
     herbs; a woodcutter the trees; all three, all of them
  3. gathering a node takes it off the map
  4. each tracked node is drawn where it is (its colour is at its tile's map position)
  5. the legend names exactly the tracked kinds
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

fails = []


def check(ok, msg):
    if not ok:
        fails.append(msg)
    return ok


def main():
    import pygame
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    from core.game_state import GameStateManager
    from entities.character import Character
    from ui.screens.map_screen import MapScreen

    sm = GameStateManager(screen)
    sm.player = Character(name="Hero", char_class="Warrior", level=30)
    zm = sm._live_zone_manager()
    gm = zm.gathering_manager

    def kinds_here():
        out = {}
        for n in gm.active_nodes:
            if not n.gathered:
                d = gm.materials.get(n.material_id) or {}
                out.setdefault(d.get("material_type"), []).append(n)
        return out

    # a zone with ore, herbs and wood all present
    zone = None
    for name in zm.zones:
        if name in zm.cave_names:
            continue
        zm.transition_to_zone(name, via_portal=False)
        k = kinds_here()
        if all(k.get(t) for t in ("ore", "herb", "wood")):
            zone = name
            break
    if not check(zone is not None, "rig: no overworld zone has ore, herbs and wood"):
        print("FAIL", fails)
        return 1
    tilemap = zm.current_zone
    ms = MapScreen(sm)
    texts = []
    real = ms.renderer.draw_text
    ms.renderer.draw_text = lambda scr, text, *a, **k: (texts.append(str(text)), real(scr, text, *a, **k))[1]

    def show(profs):
        sm.player.known_professions = list(profs)
        texts.clear()
        screen.fill((0, 0, 0))
        ms.render(screen)
        return list(ms._tracked_nodes), list(texts)

    here = kinds_here()
    nodes, text = show([])
    check(nodes == [], f"with no gathering trade the map tracks {len(nodes)} nodes")
    check(not any("Mining" in t or "Herbalism" in t or "Woodcutting" in t for t in text), "legend shows node rows with no trade learned")

    for prof, want, word in (("mining", ("ore", "crystal"), "Mining"), ("herbalism", ("herb",), "Herbalism"),
                             ("woodcutting", ("wood",), "Woodcutting")):
        nodes, text = show([prof])
        expect = sum(len(here.get(k, [])) for k in want)
        check(len(nodes) == expect, f"{prof}: {len(nodes)} nodes tracked, the zone has {expect}")
        check({k for k, _x, _y in nodes} <= set(want), f"{prof}: also tracking {set(k for k, _x, _y in nodes) - set(want)}")
        check(any(word in t for t in text), f"{prof}: the legend has no {word} row")
        others = {"Mining", "Herbalism", "Woodcutting"} - {word}
        check(not any(o in t for t in text for o in others), f"{prof}: the legend lists trades not learned")

    nodes, _ = show(["mining", "herbalism", "woodcutting", "tailoring"])
    total = sum(len(here.get(k, [])) for k in ("ore", "crystal", "herb", "wood"))
    check(len(nodes) == total, f"all three trades: {len(nodes)} tracked of {total}")

    # 4. drawn where it is
    rect = ms._map_rect(tilemap)
    hit = 0
    sample = nodes[:40]
    for kind, x, y in sample:
        px, py = ms._tile_to_screen(tilemap, rect, x, y)
        if tuple(screen.get_at((px, py)))[:3] == ms.TRACK_COLORS[kind]:
            hit += 1
    check(hit >= len(sample) * 0.8, f"only {hit} of {len(sample)} tracked nodes are drawn at their own position")

    # 3. gathering removes it
    victim = here["ore"][0]
    gm.gather(victim, tilemap)
    nodes2, _ = show(["mining"])
    check(not any((x, y) == (victim.x, victim.y) for _k, x, y in nodes2), "a gathered vein is still on the map")

    if "--shot" in sys.argv:
        show(["mining", "herbalism", "woodcutting"])
        pygame.image.save(screen, sys.argv[sys.argv.index("--shot") + 1])
    print(f"{zone}: {total} nodes tracked with all three trades ({ {k: len(v) for k, v in here.items()} })")
    if fails:
        print(f"FAIL {len(fails)}:")
        for f in fails[:20]:
            print("  ", f)
        return 1
    print("gathering tracking OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
