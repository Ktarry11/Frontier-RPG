#!/usr/bin/env python3
"""A recipe on a vendor's shelf says what it makes, what that does, and the trade and skill it needs.

    PYTHONPATH=. SDL_VIDEODRIVER=dummy python3 tools/qa_recipe_tooltips.py [out.png]

Kyle, 16 Nov 2026, hovering "Recipe: Redpepper Haunch" and "Design: Piercing Felfire Shard" at a vendor, which said
"Common - Recipe, Requires level 1": "when buying recipes it should say what it does. Also what it requires! Like
not a level but a 'Jewelcrafting - 200' for example."

For a dish, a cut gem, a piece of armour, a weapon, an enchantment and an engineering gadget, sold on a shelf:
  1. the card says "Requires <Trade> (<skill>)" and never "Requires level 1";
  2. it says what the recipe teaches you to make, and something of what that does (a stat line or the effect);
  3. the bag's card says the same things (one source, ui/recipe_tooltip.py).
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
import pygame  # noqa: E402

BAD = []


def check(label, cond, detail=""):
    print(f"  {'ok  ' if cond else 'FAIL'} {label}" + (f"  {detail}" if not cond and detail else ""))
    if not cond:
        BAD.append(label)


class _SM:
    def __init__(self, player):
        self.player = player
        self.icon_ui_helper = None

    def get_party(self):
        return None

    def transition_to(self, _s):
        pass


#: recipe id -> (trade, a phrase the card must show about what it does)
CASES = {
    "cookx_redpepper_haunch": ("Cooking", None),
    "jc_cut_piercing_felfire_shard": ("Jewelcrafting", None),
    "cook_x16_tea_19": ("Cooking", "Restores mana"),
    "eng_x16_gun_32_tank_weapon": ("Engineering", "Defense Rating"),
    "ench_bracer_minor_stamina": ("Enchanting", "Stamina"),
}


def main():
    pygame.init()
    from config import SCREEN_WIDTH, SCREEN_HEIGHT
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    from entities.character import Character
    from ui.recipe_tooltip import recipe_lines
    from world.recipe_manager import make_recipe_scroll, get_recipe_info
    p = Character(name="T", char_class="Warrior", level=40)
    p.learn_profession("jewelcrafting")
    for rid, (trade, phrase) in CASES.items():
        scroll = make_recipe_scroll(rid)
        if scroll is None:
            check(f"{rid}: a scroll can be made", False)
            continue
        _prof, data = get_recipe_info(rid)
        text = [t for t, _c in recipe_lines(scroll, p)]
        joined = " | ".join(text)
        want = f"Requires {trade} ({data.get('skill_required', 0)})"
        check(f"{scroll.name}: '{want}'", want in text, joined[:200])
        check(f"{scroll.name}: never 'Requires level 1'", "Requires level 1" not in text)
        check(f"{scroll.name}: says what it makes", any(t.startswith("Teaches you to make") for t in text))
        made = [t for t in text if t and not t.startswith(("Requires", "Teaches", "Materials", "  ", "You ",
                                                                "Your skill", "Already"))]
        check(f"{scroll.name}: says what that does", bool(made) and (phrase is None or phrase in joined),
              joined[:240])

    # on the shelf: the vendor's card draws the same lines
    from ui.screens.vendor_screen import VendorScreen
    import ui.screens.vendor_screen as VS
    from world.vendor_manager import get_vendor_manager
    scr = None
    for vendor in get_vendor_manager().vendors.values():
        try:
            scr = VendorScreen(_SM(p), vendor)
            break
        except Exception:                                # noqa: BLE001
            continue
    check("a vendor screen opens", scr is not None)
    if scr is not None:
        drawn = []
        real = scr.renderer.draw_text

        def spy(surface, text, pos, *a, **kw):
            drawn.append(str(text))
            return real(surface, text, pos, *a, **kw)
        scr.renderer.draw_text = spy
        old = VS.pygame.mouse.get_pos
        VS.pygame.mouse.get_pos = lambda: (200, 200)
        try:
            scr._render_tooltip(screen, make_recipe_scroll("jc_cut_piercing_felfire_shard"), "buy")
        finally:
            VS.pygame.mouse.get_pos = old
            scr.renderer.draw_text = real
        _prof, data = get_recipe_info("jc_cut_piercing_felfire_shard")
        check("the vendor's card says 'Requires Jewelcrafting (skill)'",
              f"Requires Jewelcrafting ({data['skill_required']})" in drawn, str(drawn)[:200])
        check("the vendor's card says what it makes", any("Teaches you to make" in d for d in drawn))
        check("the vendor's card has no 'Requires level 1'", not any("Requires level 1" == d for d in drawn))
        if len(sys.argv) > 1:
            pygame.image.save(screen, sys.argv[1])
    if BAD:
        print(f"\nFAIL ({len(BAD)})")
        return 1
    print("\nPASS - a recipe says the trade and skill it needs, what it makes and what that does")
    return 0


if __name__ == "__main__":
    sys.exit(main())
