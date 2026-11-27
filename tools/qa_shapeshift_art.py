#!/usr/bin/env python3
"""A shapeshifter walks the map as their form, turned four ways, in a Collection look if they've picked one.

    PYTHONPATH=. python3 tools/qa_shapeshift_art.py

Kyle, 18 Nov 2026: "shapeshift forms should have all 4 angles to move with. like mounts!", "We need basic forms for
shape shifting out of combat too for shifters" and "throw some of these in the collection for alternative forms!"
Checks, through the real code:
  1. every class form a character can hold out of combat (combat/forms.py) has all four facings in assets/forms
  2. world/collection.class_form_path: no form, no picture; a plain form gives its own facing; a learned look
     replaces it, an unlearned or wrong-form look doesn't
  3. every look in the Collection dresses a real class form, has all four facings, and isn't a wearable disguise
  4. the travel save keeps the chosen looks
  5. the map draws the form: the renderer's sprite for a Bear Form character is the bear, not the person
  6. the Bloodmage's three curses walk as the baseline worgen, and one curse look (worgen or bear) dresses all three
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
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
    pygame.display.set_mode((8, 8))
    from combat import forms
    from world import collection as C
    from entities.account_collection import AccountCollection

    facings = ("down", "left", "right", "up")
    # 1
    for fid in forms.FORMS:
        for d in facings:
            check((ROOT / f"assets/forms/{fid}_{d}.png").exists(), f"{fid} has no {d} facing")

    # 2 + 3, on a throwaway collection
    temp = AccountCollection()
    temp.save = lambda: True
    real = C.collection
    C.collection = lambda: temp
    try:
        check(C.class_form_path(None, "down") is None, "no form still gave a picture")
        check(C.class_form_path("bear", "left") == "assets/forms/bear_left.png",
              f"plain Bear Form facing left is {C.class_form_path('bear', 'left')}")
        looks = [e for e in C.entries() if e["kind"] == "form" and e["effect"].get("look_of")]
        check(len(looks) >= 18, f"only {len(looks)} looks")
        for e in looks:
            base = e["effect"]["look_of"]
            check(base in forms.FORMS, f"{e['id']} dresses {base}, which isn't a class form")
            check(C.art_ready(e["id"]), f"{e['id']} is missing a facing")
        look = "look_bear_frostmane"
        check(C.class_form_path("bear", "up", {"bear": look}) == "assets/forms/bear_up.png",
              "a look that isn't learned yet still showed")
        temp.learned[look] = 1
        check(C.class_form_path("bear", "up", {"bear": look}) == "assets/forms/bear_frostmane_up.png",
              f"a learned look didn't show: {C.class_form_path('bear', 'up', {'bear': look})}")
        check(C.class_form_path("cat", "up", {"cat": look}) == "assets/forms/cat_up.png",
              "a bear look dressed Cat Form")
        # the Bloodmage's curses share one look (Kyle, 27 Nov 2026): one learned curse look dresses all three
        curse = "look_curse_vampiric_bear"
        temp.learned[curse] = 1
        for f in ("cursed", "accursed", "eternal"):
            check(C.class_form_path(f, "left", {"cursed": curse}) == "assets/forms/curse_vampiric_bear_left.png",
                  f"a curse look didn't dress {f}: {C.class_form_path(f, 'left', {'cursed': curse})}")
            check(C.class_form_path(f, "down") == f"assets/forms/{f}_down.png", f"{f} has no baseline worgen")
        check(C.class_form_path("bear", "left", {"cursed": curse}) == "assets/forms/bear_left.png",
              "a curse look dressed a druid's Bear Form")
        for e in looks:
            temp.learned[e["id"]] = 1
        check(not set(C.form_ids()) & {e["id"] for e in looks}, "a look can be worn as a disguise")

        # 4
        from world.travel_manager import TravelManager
        tm = TravelManager()
        tm.form_looks = {"bear": look}
        tm2 = TravelManager()
        tm2.load_from_dict(tm.to_dict())
        check(tm2.form_looks == {"bear": look}, f"the chosen look didn't survive a save: {tm2.form_looks}")

        # 5. the renderer picks the form picture
        from ui.sprite_loader import get_form_sprite
        bear = get_form_sprite(C.class_form_path("bear", "down"), "down", 64)
        check(bear is not None and bear.get_height() == 64, "the bear picture doesn't load")
        src = (ROOT / "ui/tilemap_renderer.py").read_text(encoding="utf-8")
        check("class_form_path(_cf, player_facing, _tm.form_looks)" in src, "the map doesn't draw class forms")
    finally:
        C.collection = real

    print(f"{len(forms.FORMS)} class forms, {len(looks)} looks")
    if fails:
        print(f"FAIL {len(fails)}:")
        for x in fails[:25]:
            print("  ", x)
        return 1
    print("shapeshift art OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
