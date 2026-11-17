#!/usr/bin/env python3
"""Mailboxes and auction houses have their own icons on the map and in its legend.

    PYTHONPATH=. python3 tools/qa_map_mail_auction_icons.py [--shot DIR]

Kyle, 16 Nov 2026: "We should also add icons for mailbox and also auction house." Before this a mailbox and an
auctioneer were the same grey dot as everyone else in town. This opens the real map screen in Orgrimmar (it has
both), and checks:
  * every mailbox and every auctioneer on the map gets its glyph, at the tile it stands on;
  * a zone with neither shows neither (the negative control: the glyph isn't firing on every NPC);
  * the legend names both, and with every row showing (all four gathering trades known) the legend still ends
    above the footer.
--shot DIR saves a picture of Orgrimmar's map for a look.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)


def main():
    import contextlib
    import io
    import pygame
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    from config import SCREEN_HEIGHT
    from core.game_state import GameStateManager
    from entities.character import Character
    from ui.screens.map_screen import MapScreen
    from world.ambient_npc_manager import get_ambient_npc_manager
    from world.travel_manager import services_for_npc

    bad = []
    with contextlib.redirect_stdout(io.StringIO()):
        sm = GameStateManager(screen)
        sm.player = Character(name="Hero", char_class="Warrior", level=30)
        zm = sm._live_zone_manager()
    ms = MapScreen(sm)
    drawn = []
    real = ms._draw_service_icon
    ms._draw_service_icon = lambda scr, kind, cx, cy, scale=1.0: (drawn.append((kind, cx, cy, scale)),
                                                                 real(scr, kind, cx, cy, scale))[1]
    texts = []
    real_text = ms.renderer.draw_text
    ms.renderer.draw_text = lambda scr, text, *a, **k: (texts.append(str(text)), real_text(scr, text, *a, **k))[1]

    def show(zone):
        with contextlib.redirect_stdout(io.StringIO()):
            zm.transition_to_zone(zone, via_portal=False)
        drawn.clear()
        texts.clear()
        screen.fill((0, 0, 0))
        ms.render(screen)
        return [d for d in drawn if d[3] == 1.0]          # the map's glyphs, not the legend's samples

    def wanted(zone):
        mail, auction = set(), set()
        people = list(get_ambient_npc_manager().get_npcs_in_zone(zone))
        vm = getattr(zm, "vendor_manager", None)
        if vm is not None:
            people += list(vm.get_vendors_in_zone(zone))
        for p in people:
            if getattr(p, "hidden", False):
                continue
            if getattr(p, "is_mailbox", False):
                mail.add((p.x, p.y))
            elif "auction" in services_for_npc(p):
                auction.add((p.x, p.y))
        return mail, auction

    sm.player.known_professions = ["mining", "herbalism", "woodcutting", "fishing"]
    town = "Orgrimmar"
    mail, auction = wanted(town)
    if not mail or not auction:
        bad.append(f"rig: {town} should have a mailbox and an auctioneer (mail {len(mail)}, auction {len(auction)})")
    glyphs = show(town)
    tm = zm.current_zone
    rect = ms._map_rect(tm) if hasattr(ms, "_map_rect") else None
    for kind, spots in (("mail", mail), ("auction", auction)):
        got = sorted((cx, cy) for (k, cx, cy, _s) in glyphs if k == kind)
        if len(set(got)) < len(spots):
            bad.append(f"{town}: {len(spots)} {kind} spot(s), {len(set(got))} {kind} glyph(s) drawn")
        if rect is not None:
            want = sorted(ms._tile_to_screen(tm, rect, x, y) for (x, y) in spots)
            if sorted(set(got)) != sorted(set(want)):
                bad.append(f"{town}: {kind} glyphs at {got[:4]}, not at the tiles {want[:4]}")
    for label in ("Mailbox", "Auction house"):
        if label not in texts:
            bad.append(f"the legend has no '{label}' row")
    bottom = getattr(ms, "_legend_bottom", 0)
    if bottom > SCREEN_HEIGHT - 34:
        bad.append(f"with every row showing the legend runs to {bottom}, over the footer at {SCREEN_HEIGHT - 34}")
    if "--shot" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--shot") + 1]) / "map_orgrimmar.png"
        pygame.image.save(screen, str(out))
        print("saved", out)

    # NEGATIVE CONTROL: an open zone with neither
    quiet = next((z for z in ("Durotar", "Valley of Trials") if z in zm.zones and wanted(z) == (set(), set())), None)
    if quiet is None:
        bad.append("rig: no quiet zone for the control")
    else:
        stray = [k for (k, _x, _y, _s) in show(quiet) if k in ("mail", "auction")]
        if stray:
            bad.append(f"{quiet} has no mailbox or auctioneer but drew {len(stray)} of their glyphs")

    print(f"{town}: {len(mail)} mailbox(es), {len(auction)} auctioneer(s); control: {quiet}")
    if bad:
        print(f"FAIL ({len(bad)})")
        for b in bad:
            print("  -", b)
        return 1
    print("PASS - mailboxes and auction houses have their own glyphs, in the legend too, and nowhere else")
    return 0


if __name__ == "__main__":
    sys.exit(main())
