"""
A recipe scroll must never be destroyed by clicking it.

Kyle, 10 Nov: "Oh cool, i can click on it... and it vanishes. Did I learn it? I have no
crafting skills so i shouldnt be able to."

He had not learned it. The scroll was an entities.item.Item with slot "recipe"; Item had no
is_gear, so the inventory screen read it as gear and equipped it; Character.equip_item removed
it from the bag; Equipment.equip had no "recipe" slot and put it nowhere. Every pattern, plan,
recipe and schematic in the game went the same way.

  1. EVERY scroll  - is_gear is False, and equip_item refuses it and leaves it in the bag.
  2. NO ITEM AT ALL - equip_item never removes from the bag an item it has no slot for.
  3. THE CLICK     - without the profession the scroll stays and nothing is learned; with the
                     profession and the skill it is learned and the scroll is spent.
  4. THE TOOLTIP   - says what it makes and what it needs, in display names, and the bag
                     draws with a scroll in it.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PROBLEMS = []


def fail(msg):
    PROBLEMS.append(msg)
    print(f"  FAIL {msg}")


def ok(msg):
    print(f"  ok   {msg}")


def all_scroll_ids():
    from world.recipe_manager import _load_all_recipes
    ids = []
    # {recipe_id: (profession, recipe)}
    for rid, (profession, data) in _load_all_recipes().items():
        if isinstance(data, dict) and data.get("source") not in (None, "trainer"):
            ids.append(rid)
    return ids


def hero(cls="Warrior", level=60):
    from entities.character import Character
    return Character(name="Tester", char_class=cls, level=level)


def check_every_scroll():
    print("\n1. every scroll")
    from world.recipe_manager import make_recipe_scroll
    ids = all_scroll_ids()
    if not ids:
        fail("found no recipe scrolls to test - the rig is looking in the wrong place")
        return
    c = hero()
    made = eaten = geared = 0
    for rid in ids:
        scroll = make_recipe_scroll(rid)
        if scroll is None:
            continue
        made += 1
        if getattr(scroll, "is_gear", True):
            geared += 1
            fail(f"{scroll.name}: reads as gear")
            continue
        c.inventory.append(scroll)
        equipped = c.equip_item(scroll)
        if equipped or scroll not in c.inventory:
            eaten += 1
            fail(f"{scroll.name}: equip_item returned {equipped}, still in bag: {scroll in c.inventory}")
        if scroll in c.inventory:
            c.inventory.remove(scroll)
    if made == 0:
        fail("no scroll could be built")
    elif not eaten and not geared:
        ok(f"{made} scrolls: none reads as gear, none can be equipped, none leaves the bag")


def check_no_item_is_eaten():
    print("\n2. no item at all")
    from entities.item import Item
    c = hero()
    for slot in ("recipe", "quest", "nonsense_slot", "", None):
        odd = Item(item_id=f"odd_{slot}", name=f"Odd thing ({slot})", slot=slot, item_level=10,
                   rarity="common")
        c.inventory.append(odd)
        try:
            equipped = c.equip_item(odd)
        except Exception as exc:
            fail(f"slot {slot!r}: equip_item raised {type(exc).__name__}: {exc}")
            equipped = None
        if equipped or odd not in c.inventory:
            fail(f"slot {slot!r}: equip_item returned {equipped} and the item is "
                 f"{'gone' if odd not in c.inventory else 'still there'}")
        if odd in c.inventory:
            c.inventory.remove(odd)
    if not PROBLEMS:
        ok("an item with no equipment slot is refused and stays in the bag")
    # And a real piece of gear still equips.
    from entities.loot_generator import LootGenerator
    piece = LootGenerator().generate_armor_piece(slot="chest", armor_type="plate",
                                                 stat_template="str_tank", item_level=50, rarity="rare")
    c.inventory.append(piece)
    if not c.equip_item(piece) or piece in c.inventory:
        fail("real gear no longer equips - the refusal is too wide")
    else:
        ok("real gear still equips")


def screen_for(player):
    import pygame
    pygame.init()
    surface = pygame.display.set_mode((1280, 720))
    from ui.screens.inventory_screen import InventoryScreen

    class SM:
        pass
    sm = SM()
    sm.player = player
    return InventoryScreen(sm), surface


def check_click_and_tooltip():
    print("\n3-4. the click and the tooltip")
    from world.recipe_manager import make_recipe_scroll, get_recipe_info, _load_all_recipes
    # A scroll whose recipe makes gear, so the tooltip has something to describe.
    rid = None
    for r, (profession, data) in _load_all_recipes().items():
        if (isinstance(data, dict) and data.get("source") not in (None, "trainer")
                and (data.get("output") or {}).get("kind") == "armor"):
            rid, prof, rdata = r, profession, data
            break
    if rid is None:
        fail("no armour recipe scroll found to test the click with")
        return

    # Without the profession: stays, nothing learned.
    c = hero()
    scroll = make_recipe_scroll(rid)
    c.inventory.append(scroll)
    scr, surface = screen_for(c)
    scr._use_recipe_scroll(c, c, scroll)
    if scroll not in c.inventory or c.knows_recipe(rid):
        fail(f"no profession: scroll in bag={scroll in c.inventory}, learned={c.knows_recipe(rid)}")
    else:
        ok(f"no {prof}: the scroll stays and nothing is learned ({scr.equip_error!r})")

    # The bag draws with a scroll in it, and the tooltip says what it makes.
    drawn = []
    real = scr.renderer.draw_text

    def rec(surf, text, *a, **k):
        # Pass everything through untouched: forcing color=None in here made the screen
        # raise "invalid color argument" and blamed the game for the recorder.
        drawn.append(str(text))
        return real(surf, text, *a, **k)
    scr.renderer.draw_text = rec
    try:
        scr.render(surface)
    except Exception as exc:
        fail(f"the inventory screen raised drawing a bag with a scroll in it: "
             f"{type(exc).__name__}: {exc}")
    drawn.clear()
    scr._draw_item_tooltip(surface, scroll, (200, 200))
    text = "\n".join(drawn)
    if rdata["name"] not in text.replace("\n", " "):
        fail(f"tooltip does not name what it makes ({rdata['name']}): {drawn}")
    elif f"({rdata['skill_required']})" not in text:
        fail(f"tooltip does not give the skill needed: {drawn}")
    elif "Materials:" not in text:
        fail(f"tooltip lists no materials: {drawn}")
    else:
        raw = [i for i in (rdata.get("inputs") or {}) if any(i in line for line in drawn)]
        if raw:
            fail(f"tooltip shows raw material ids {raw}")
        elif any("Item Level" in line and str(rdata["output"].get("item_level")) not in line
                 for line in drawn):
            fail(f"tooltip still shows the scroll's proxy item level: {drawn}")
        else:
            ok("tooltip names the output, the skill needed and the materials, by display name")
            for line in drawn:
                print(f"         | {line}")

    # With the profession and the skill: learned, scroll spent.
    c.profession_skills[prof] = max(300, rdata.get("skill_required", 0))
    known = c.known_professions
    if prof not in known:
        known.add(prof) if isinstance(known, set) else known.append(prof)
    if not c.knows_profession(prof):
        fail(f"rig: could not give the tester {prof}")
        return
    scr._use_recipe_scroll(c, c, scroll)
    if scroll in c.inventory or not c.knows_recipe(rid):
        fail(f"with {prof}: scroll in bag={scroll in c.inventory}, learned={c.knows_recipe(rid)} "
             f"({scr.equip_error!r})")
    else:
        ok(f"with {prof}: the recipe is learned and the scroll is spent")


def main():
    check_every_scroll()
    check_no_item_is_eaten()
    check_click_and_tooltip()
    if PROBLEMS:
        print(f"\nFAILED - {len(PROBLEMS)} problem(s)")
        return 1
    print("\nrecipe scrolls OK - none can be destroyed by a click.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
