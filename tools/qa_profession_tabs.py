"""Every crafting profession you can learn has a tab you can open and craft from.

Playtest, 12 Nov: "There is no tab for cooking or leather working professions." Engineering
had none either. All three could be learned, levelled and have recipes bought for them.
"""
import json
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
os.chdir(ROOT)

GATHERING = {"mining", "herbalism", "woodcutting", "skinning"}


def main():
    import pygame
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    from shot_screen import build, StubSM
    from ui.screens.professions_screen import ProfessionsScreen, CRAFT_TABS

    professions = json.load(open("data/professions/professions.json"))["professions"]
    crafting = [p for p in professions if p not in GATHERING]
    player, party = build("Warrior", 40)
    bad = []
    scr = ProfessionsScreen(StubSM(player, party))
    for prof in crafting:
        player.known_professions = [prof]
        player.profession_skills = {prof: 300}
        player.profession_tiers = {prof: 3}
        keys = [k for k, _ in scr._tab_list()]
        if prof not in keys:
            bad.append(f"{prof}: learned, and there is no tab for it")
            continue
        scr.active_tab = prof
        try:
            screen.fill((0, 0, 0))
            scr.render(screen)
        except Exception as e:
            bad.append(f"{prof}: the tab crashes - {e!r}")
            continue
        recipes = scr._craft_recipes(CRAFT_TABS[prof][0])
        if not recipes:
            bad.append(f"{prof}: the tab is empty")
        if len(scr.craft_recipe_rects) == 0:
            bad.append(f"{prof}: no recipe rows drawn")
        if len(sys.argv) > 2 and sys.argv[1] == prof:
            pygame.image.save(screen, sys.argv[2])
        print(f"  {prof:16s} {len(recipes):4d} recipes")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for b in bad:
            print("  -", b)
        return 1
    print("\nprofession tabs OK - every crafting profession opens and lists its recipes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
