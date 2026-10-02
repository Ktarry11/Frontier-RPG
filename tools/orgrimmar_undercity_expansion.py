"""
MASSIVE Orgrimmar, Undercity, & Dungeon Expansion

Real scale dungeons (200x180) with proper multi-boss progression.
Capital cities (200x200+) with sprawling districts.

This is how actual WoW dungeons and cities FEEL - not tiny gimmicks.

FILE CONTENTS (the filename only names the two capitals - flagged since
it's misleading on its own, Kyle caught this): this file has FOUR
generators, not two - OrgrimmarMassive, UndercityMassive,
RagefireChasmMassive, and PlaguedepthsMassive. RFC and Plague Depths live
here because they're each physically inside their respective capital
(RFC under Orgrimmar's Cleft of Shadow, Plague Depths under Undercity),
not because of an oversight - but if you're searching for either dungeon
by a name that matches the file, you won't find it. Renaming/splitting
this file is a real candidate for cleanup, just not done yet - deferred
rather than done blind while Kyle couldn't review it live.
"""

import random
from world.tilemap import Tilemap
from world.zone_generator import ZoneGenerator


class OrgrimmarMassive:
    """Generate a MASSIVE Orgrimmar (200x200) - proper capital city scale."""
    
    @staticmethod
    def generate_orgrimmar_massive():
        """
        Orgrimmar (200x200) - MASSIVE Horde Capital
        
        Real scale with:
        - Outer defensive ring (walls, gates)
        - 8 major districts (each ~40x40)
        - Central plaza area (100x60)
        - Multiple quest hubs
        - Trade routes
        - Flight paths
        - Dungeon entry (Ragefire Chasm)
        
        District Layout (grid):
        [Wisdom NW] [Honor NE] [Magic NE]
        [Strength W] [CENTRAL PLAZA] [Warlock E]
        [Critter S]  [Craft Labs S]  [Stables S]
        
        """
        zone = Tilemap("Orgrimmar", 200, 200,
                       "The great orcish capital. Towering walls, forges burning, "
                       "war banners flying. A true seat of Horde power.")
        zone.region = "Durotar"
        
        # Base: volcanic stone
        zone.fill("stone", "base")
        
        # Scattered stone/dirt for visual variation. The old version rolled
        # a random check on EVERY tile independently (9% chance each), which
        # sprays isolated single dirt pixels evenly across all 40,000 tiles
        # with zero clustering - reads as scattered debris/dirt everywhere
        # rather than actual ground texture. Real worn stone has patches:
        # scatter a handful of soft-edged blobs instead of salt-and-pepper
        # noise, and skip anywhere a wall/district will go so it doesn't
        # bleed into the walled buildings themselves.
        for _ in range(12):
            bx = random.randint(10, zone.width - 10)
            by = random.randint(10, zone.height - 10)
            br = random.randint(2, 4)
            for dy in range(-br, br + 1):
                for dx in range(-br, br + 1):
                    if dx * dx + dy * dy <= br * br and random.random() < 0.45:
                        x, y = bx + dx, by + dy
                        if 0 <= x < zone.width and 0 <= y < zone.height:
                            zone.set_tile(x, y, "dirt", "base")
        
        # ===== OUTER DEFENSIVE WALLS (4 tiles thick) =====
        for x in range(zone.width):
            for y in range(4):
                zone.set_tile(x, y, "wall", "collision")
            for y in range(zone.height - 4, zone.height):
                zone.set_tile(x, y, "wall", "collision")
        
        for y in range(zone.height):
            for x in range(4):
                zone.set_tile(x, y, "wall", "collision")
            for x in range(zone.width - 4, zone.width):
                zone.set_tile(x, y, "wall", "collision")
        
        # South Gate (main entry from Durotar) - LARGE
        for x in range(85, 115):
            for y in range(zone.height - 4, zone.height):
                zone.collision_layer[y][x] = None
                zone.set_tile(x, y, "dirt", "base")

        # Real gate structure spanning the opening (Kyle: "these gates
        # should be much larger too to show off the entrance to org" -
        # this south wall breach had NO gate art at all before now, just
        # a bare collision gap in the wall). Same art as Durotar's own
        # gate landmark on the other side of this portal, so the entrance
        # reads as one continuous structure from both zones.
        zone.add_landmark("assets/buildings/orgrimmar_gate.png", 93, 188, 14, 11)

        # Dedicated Durotar-arrival portal tile, just inside the gate
        # opening - was MISSING entirely. portal_manager.py's Durotar ->
        # Orgrimmar entry used to point at (100,192), which is actually
        # the Zeppelin Tower platform's own portal tile 4 rows further
        # north (see ZEPPELIN TOWER section below) - walking in from
        # Durotar silently skipped the gate entirely and dropped the
        # player onto the zeppelin platform instead, reading as "stuck
        # arriving inside the gates." This tile is real open ground
        # (already cleared above) directly under the new gate art.
        zone.set_tile(100, 197, "portal", "interaction")  # -> Durotar (south gate arrival)

        # ===== CENTRAL PLAZA (massive open area) =====
        # 100x60 marketplace
        plaza_x1, plaza_x2 = 50, 150
        plaza_y1, plaza_y2 = 70, 130
        
        for y in range(plaza_y1, plaza_y2):
            for x in range(plaza_x1, plaza_x2):
                zone.collision_layer[y][x] = None
                zone.set_tile(x, y, "dirt", "base")
        
        # Vendor stall grid (12 vendors, arranged in marketplace)
        vendor_positions = [
            (60, 80), (80, 80), (100, 80), (120, 80),
            (70, 100), (90, 100), (110, 100), (130, 100),
            (60, 115), (80, 115), (100, 115), (120, 115),
        ]
        for vx, vy in vendor_positions:
            zone.set_tile(vx, vy, "npc", "interaction")
        
        # Central feature/fountain
        zone.set_tile(100, 100, "quest_marker", "interaction")

        # Small goblin-flavored corner of the market (Kyle: "a goblin
        # quarter too? Don't worry" then "keep a small amount of ratchet
        # buildings... nothing fancy. It's still org" - not a real Classic
        # Orgrimmar location (the actual Goblin Slums came in Cataclysm),
        # original content in the same spirit as this file's existing
        # "Craft Labs"/"Stables" districts. Deliberately light-touch: just
        # 2 buildings tucked into the north edge of the existing market
        # plaza rather than a full separate district, since the market
        # already has goblin-run stalls here (Grokka Fireforge, Fizwick
        # Gemstone) - reads as an extension of the city's trade quarter,
        # not a Ratchet clone dropped into Orgrimmar.
        for sprite_key, anchor_x, anchor_y, w, h in [
            ("assets/buildings/bazaar_stall_row.png", 51, 51, 15, 12),
        ]:
            zone.add_landmark(sprite_key, anchor_x, anchor_y, w, h)

        # gazlowes_office genuinely overlapped bazaar_stall_row here
        # (real footprint check, not eyeballed) - relocated to open
        # plaza space just south of this little goblin corner rather
        # than crammed alongside it.
        zone.add_landmark("assets/buildings/gazlowes_office.png", 48, 70, 12, 12)

        # ===== DISTRICT: VALLEY OF WISDOM (NW, 40x40) =====
        # Real Classic-era Orgrimmar (Kyle: full district rebuild, same
        # research-then-build pattern as Razor Hill). Confirmed via web
        # search: Valley of Wisdom houses Grommash Hold, Thrall's seat -
        # and in Classic specifically, the Shaman trainers Kardris
        # Dreamseeker (orc), Sagorne Creststrider (tauren), and Sian'tsu
        # (troll, not yet added) taught from "Thrall's Fortress, first
        # room" (confirmed via Chinese wowhead classic guide, matches
        # every English source's "Grommash Hold" naming for the same
        # building). Elder Torgun (org_elder_2) is NOT a real WoW NPC, but
        # is kept exactly as-is and NOT renamed: he's referenced by name in
        # 3 already-written central_barrens.json quest descriptions, so
        # renaming him would break narrative continuity even though the
        # npc_id itself is safe. The old fictional "Farseer Wolfheart" had
        # zero quest references and was safe to correct - see
        # data/npcs/ambient_npcs.json, npc_id org_shaman_trainer, now
        # renamed to the real Kardris Dreamseeker.
        OrgrimmarMassive._build_district(zone, 10, 15, 40, 40)
        zone.set_tile(29, 30, "npc", "interaction")  # Elder Torgun (org_elder_2) - quest-bound, kept as-is; moved from (25,25), which was buried inside BOTH warchiefs_hall's and generic_hut_a's landmark footprints (unreachable, caught via flood-fill from the south gate)
        zone.set_tile(31, 32, "npc", "interaction")  # Kardris Dreamseeker (org_shaman_trainer) - moved from (30,25), inside generic_hut_a's footprint
        zone.set_tile(27, 26, "npc", "interaction")  # Sagorne Creststrider (org_shaman_trainer_2)
        zone.set_tile(25, 35, "npc", "interaction")  # Ulvara Deepwind (vendor)
        zone.set_tile(13, 30, "npc", "interaction")  # Thrall (org_thrall) - stands at Grommash Hold's entrance; moved from (17,24), which sat INSIDE the hall's own 18x15 landmark footprint (x:8-26,y:13-28) and was permanently unreachable - caught via a real flood-fill from the south gate, not assumed fine because the tile "looked" like it was near the building
        # Inner courtyard clearing - widened on the west edge (was x:18-35)
        # to fully cover Grommash Hold's footprint (x:14-20) before its own
        # landmark collision stamps back on top, same ordering rule used
        # everywhere else in this codebase (clear first, add_landmark last).
        for y in range(18, 35):
            for x in range(13, 35):
                zone.collision_layer[y][x] = None

        # Real building placements - footprints hand-picked to match what
        # each source art depicts (Grommash Hold is the district's real
        # centerpiece, biggest footprint; everything else scaled down from
        # there), anchors verified via a headless collision scan (1-tile
        # margin, clear of every NPC position and every other building)
        # before being hardcoded, same standard as Valley of Trials/
        # Durotar/Razor Hill. Auction House + Inn added per Kyle's "don't
        # be shy... also the inn?" - confirmed via web search that Classic
        # Valley of Wisdom genuinely had its own Auction House (Wisdom
        # isn't just Valley of Strength's overflow), plus Miwana's
        # Longhouse as the district's inn - reusing crossroads_inn.png
        # since there's no dedicated Orgrimmar inn sprite.
        for sprite_key, anchor_x, anchor_y, w, h in [
            ("assets/buildings/warchiefs_hall.png", 26, 33, 18, 15),      # Grommash Hold - Thrall's seat
            ("assets/buildings/crossroads_inn.png", 32, 17, 12, 12),      # inn (stand-in for Miwana's Longhouse)
            ("assets/buildings/trainers_lodge.png", 16, 17, 12, 9),      # near Kardris/Sagorne
            ("assets/buildings/auction_house.png", 13, 31, 12, 9),       # Valley of Wisdom's own AH
            ("assets/buildings/shamans_hut.png", 13, 41, 12, 9),
            # Real building-overlap pass this session (Kyle: "ensure the
            # buildings are not so big they clip into each other" -
            # confirmed 52 real overlapping pairs citywide via a direct
            # footprint check, Grommash Hold alone had Trainers Lodge
            # drawn 2/3 on top of it). Coordinates below are resolved,
            # non-overlapping placements, verified via the same check -
            # not hand-eyeballed. Wisdom was the single most overcrowded
            # district (11 buildings in a 36x36 real interior once the
            # 2-tile wall margin is accounted for), so per Kyle's call
            # ("reduce buildings slightly... or move some to the
            # outskirts") plain_orc_house_a is dropped entirely here
            # (a duplicate filler - plain_orc_house_b already covers the
            # same "generic house" role in this district) and the rest
            # genuinely didn't fit inside the walls at all, relocated to
            # a real open street pocket just outside Wisdom's own gate
            # (near its breach-to-plaza connection) rather than forced
            # into an even-worse overlap.
        ]:
            zone.add_landmark(sprite_key, anchor_x, anchor_y, w, h)

        # Wisdom overflow - genuinely didn't fit inside the district's
        # own walls even after the resolve pass above; real open street
        # tiles just outside Wisdom's south gate (near the breach at
        # (47,27)-(47,33) that connects this district to the plaza).
        for sprite_key, anchor_x, anchor_y, w, h in [
            ("assets/buildings/generic_hut_a.png", 52, 15, 9, 9),       # Elder Torgun's research hut
            ("assets/buildings/generic_house_a.png", 63, 15, 9, 9),     # Ulvara Deepwind's stall
            ("assets/buildings/plain_orc_house_b.png", 52, 26, 9, 6),
            ("assets/buildings/generic_hut_b.png", 63, 26, 9, 9),
            ("assets/buildings/watchtower.png", 52, 37, 9, 12),
        ]:
            zone.add_landmark(sprite_key, anchor_x, anchor_y, w, h)

        # ===== DISTRICT: VALLEY OF HONOR (NE, 40x40) =====

        # Hunter/beast master grounds
        OrgrimmarMassive._build_district(zone, 155, 15, 40, 40)
        zone.set_tile(170, 25, "npc", "interaction")  # Hunter trainer
        zone.set_tile(175, 25, "npc", "interaction")  # Stablemaster
        zone.set_tile(170, 35, "npc", "interaction")  # Beast vendor
        # Inner courtyard - widened to cover the full building spread below
        # (was 18-35/158-180, too narrow once real city density landed).
        for y in range(18, 55):
            for x in range(155, 190):
                zone.collision_layer[y][x] = None

        for sprite_key, anchor_x, anchor_y, w, h in [
            ("assets/buildings/outpost_barracks.png", 176, 42, 15, 9),
            ("assets/buildings/watchtower.png", 157, 17, 9, 12),
            ("assets/buildings/crossroads_stable.png", 157, 38, 12, 9),
            ("assets/buildings/taurajo_granary.png", 182, 19, 9, 12),
            ("assets/buildings/plain_orc_house_b.png", 167, 26, 9, 9),
            ("assets/buildings/generic_house_a.png", 177, 32, 9, 9),
            ("assets/buildings/generic_house_b.png", 158, 29, 9, 9),
            # plain_orc_house_c was previously at (152,28) - OUTSIDE this
            # district's own west wall (x=155 is the wall start), a
            # separate real pre-existing bug the overlap-resolve pass
            # caught incidentally.
            ("assets/buildings/plain_orc_house_c.png", 167, 17, 9, 6),
        ]:
            zone.add_landmark(sprite_key, anchor_x, anchor_y, w, h)

        # Honor overflow - real open street tiles just outside this
        # district's own west gate.
        for sprite_key, anchor_x, anchor_y, w, h in [
            ("assets/buildings/generic_shack_a.png", 132, 50, 9, 9),
            ("assets/buildings/guard_post.png", 122, 40, 9, 9),
        ]:
            zone.add_landmark(sprite_key, anchor_x, anchor_y, w, h)

        # ===== DISTRICT: MAGIC QUARTER (N-Center, 40x35) =====
        OrgrimmarMassive._build_district(zone, 80, 10, 40, 35)
        zone.set_tile(95, 22, "npc", "interaction")  # Mage trainer (future expansion)
        zone.set_tile(100, 22, "npc", "interaction")  # Enchanter
        # Courtyard - widened to cover the full building spread below
        for y in range(13, 42):
            for x in range(80, 120):
                zone.collision_layer[y][x] = None

        for sprite_key, anchor_x, anchor_y, w, h in [
            ("assets/buildings/watchtower.png", 82, 12, 9, 12),
            ("assets/buildings/supply_cache_shed.png", 82, 30, 12, 9),
            ("assets/buildings/crossroads_town_hall.png", 106, 21, 12, 9),
            ("assets/buildings/mixed_trading_post.png", 95, 31, 12, 9),
            ("assets/buildings/plain_orc_house_b.png", 92, 12, 9, 9),
            ("assets/buildings/generic_hut_a.png", 108, 31, 9, 9),
            ("assets/buildings/generic_hut_b.png", 101, 12, 9, 9),
            ("assets/buildings/well_house.png", 95, 24, 6, 6),
            # generic_shack_b and trial_hut dropped entirely - Magic
            # Quarter's real interior (36x31 once the wall margin is
            # accounted for) genuinely couldn't fit all 10 original
            # buildings without overlap even after every other one was
            # repositioned; both were non-unique fillers with no NPC or
            # quest tie, matching Kyle's "reduce buildings slightly"
            # call for whichever district needed it.
        ]:
            zone.add_landmark(sprite_key, anchor_x, anchor_y, w, h)

        # ===== DISTRICT: VALLEY OF STRENGTH (W, 40x40) =====
        # Warrior/blacksmith grounds. Real Classic-era placement (confirmed
        # via web search): Valley of Strength is where the Bank of
        # Orgrimmar and the city's MAIN Auction House both live, run by
        # goblins - matches this district's existing smith/weaponsmith
        # NPCs perfectly, so no NPC changes needed here, just the missing
        # buildings. Grand Forge covers the smith flavor directly.
        OrgrimmarMassive._build_district(zone, 10, 75, 40, 40)
        zone.set_tile(25, 85, "npc", "interaction")  # Warrior trainer
        zone.set_tile(24, 85, "npc", "interaction")  # Blacksmith - moved from (30,85), buried inside a building footprint (unreachable, caught via a full-city interaction-tile sweep)
        zone.set_tile(25, 95, "npc", "interaction")  # Weaponsmith
        # Forge area (interior open) - widened for full building spread
        for y in range(78, 114):
            for x in range(10, 50):
                zone.collision_layer[y][x] = None

        for sprite_key, anchor_x, anchor_y, w, h in [
            ("assets/buildings/grand_forge.png", 26, 77, 15, 15),          # smith flavor, matches Krunk Anvilfist
            ("assets/buildings/taurajo_lodge.png", 21, 101, 15, 12),
            ("assets/buildings/valley_bank.png", 12, 77, 12, 12),          # Bank of Orgrimmar
            ("assets/buildings/auction_house.png", 12, 90, 12, 9),        # main Auction House
            ("assets/buildings/watchtower.png", 37, 93, 9, 12),
            ("assets/buildings/plain_orc_house_a.png", 26, 92, 9, 9),    # filler housing
            ("assets/buildings/generic_house_a.png", 12, 99, 9, 9),
            ("assets/buildings/plain_orc_house_b.png", 37, 106, 9, 6),
            ("assets/buildings/well_house.png", 42, 77, 6, 6),
        ]:
            zone.add_landmark(sprite_key, anchor_x, anchor_y, w, h)

        # Strength overflow - real open street tiles just outside this
        # district's own east gate.
        for sprite_key, anchor_x, anchor_y, w, h in [
            ("assets/buildings/elders_tent.png", 64, 105, 9, 9),
            ("assets/buildings/plain_orc_house_c.png", 57, 98, 9, 6),
        ]:
            zone.add_landmark(sprite_key, anchor_x, anchor_y, w, h)

        # ===== DISTRICT: WARLOCK QUARTER (E, 40x40) =====
        # Dark magic research
        OrgrimmarMassive._build_district(zone, 155, 75, 40, 40)
        zone.set_tile(170, 85, "npc", "interaction")  # Warlock trainer
        zone.set_tile(175, 85, "npc", "interaction")  # Summoning master
        zone.set_tile(170, 95, "npc", "interaction")  # Demonic vendor
        # Courtyard - widened for full building spread
        for y in range(76, 112):
            for x in range(158, 195):
                zone.collision_layer[y][x] = None

        for sprite_key, anchor_x, anchor_y, w, h in [
            ("assets/buildings/clan_hall.png", 178, 77, 15, 12),
            ("assets/buildings/trading_post.png", 178, 93, 15, 9),
            ("assets/buildings/watchtower.png", 157, 77, 9, 12),
            ("assets/buildings/shamans_hut.png", 174, 103, 12, 9),
            ("assets/buildings/plain_orc_house_b.png", 167, 86, 9, 9),
            ("assets/buildings/generic_hut_b.png", 164, 99, 9, 9),
            ("assets/buildings/generic_shack_a.png", 158, 89, 9, 9),
        ]:
            zone.add_landmark(sprite_key, anchor_x, anchor_y, w, h)

        # Warlock Quarter overflow - real open street tiles just outside
        # this district's own west gate.
        for sprite_key, anchor_x, anchor_y, w, h in [
            ("assets/buildings/generic_tent_a.png", 132, 105, 9, 9),
            ("assets/buildings/guard_post.png", 122, 101, 9, 9),
            ("assets/buildings/generic_tent_b.png", 132, 95, 9, 9),
        ]:
            zone.add_landmark(sprite_key, anchor_x, anchor_y, w, h)

        # ===== DISTRICT: CLEFT OF SHADOW (SW, 40x40) =====
        # ROGUE QUARTER + RAGEFIRE CHASM ENTRY
        OrgrimmarMassive._build_district(zone, 10, 145, 40, 40)
        zone.set_tile(25, 155, "npc", "interaction")  # Rogue trainer
        zone.set_tile(30, 155, "npc", "interaction")  # Poison vendor
        # Ragefire Chasm - prominent dungeon entrance (multiple portals)
        zone.set_tile(20, 170, "portal", "interaction")  # Main entry
        zone.set_tile(25, 170, "portal", "interaction")  # Secondary
        zone.set_tile(22, 165, "quest_marker", "interaction")  # Dungeon quest NPC
        # Shadowy courtyard - widened for full building spread
        for y in range(146, 182):
            for x in range(10, 44):
                zone.collision_layer[y][x] = None

        for sprite_key, anchor_x, anchor_y, w, h in [
            ("assets/buildings/clan_hall.png", 31, 147, 15, 12),
            ("assets/buildings/watchtower.png", 12, 147, 9, 12),
            ("assets/buildings/hide_tanners_hut.png", 12, 171, 12, 9),
            ("assets/buildings/plain_orc_house_b.png", 12, 160, 9, 9),
            ("assets/buildings/generic_shack_a.png", 23, 161, 9, 9),
            ("assets/buildings/generic_shack_b.png", 33, 160, 9, 9),
            ("assets/buildings/trial_hut.png", 33, 170, 9, 9),
            ("assets/buildings/guard_post.png", 24, 171, 9, 9),
        ]:
            zone.add_landmark(sprite_key, anchor_x, anchor_y, w, h)

        # Cleft of Shadow overflow - real open street tiles just outside
        # this district's own east gate.
        for sprite_key, anchor_x, anchor_y, w, h in [
            ("assets/buildings/generic_tent_b.png", 64, 140, 9, 9),
        ]:
            zone.add_landmark(sprite_key, anchor_x, anchor_y, w, h)

        # ===== DISTRICT: CRAFT LABS (S-Center, 40x40) =====
        OrgrimmarMassive._build_district(zone, 80, 145, 40, 40)
        zone.set_tile(95, 155, "npc", "interaction")  # Alchemist
        zone.set_tile(100, 155, "npc", "interaction")  # Leatherworker
        zone.set_tile(95, 165, "npc", "interaction")  # Tailor
        # Workshop area (open interior) - widened for full building spread
        for y in range(143, 184):
            for x in range(78, 118):
                zone.collision_layer[y][x] = None

        for sprite_key, anchor_x, anchor_y, w, h in [
            ("assets/buildings/outpost_barracks.png", 103, 148, 15, 9),
            ("assets/buildings/watchtower.png", 82, 147, 9, 12),
            ("assets/buildings/taurajo_stables.png", 104, 164, 12, 9),
            ("assets/buildings/mixed_trading_post.png", 82, 160, 12, 9),
            ("assets/buildings/supply_cache_shed.png", 82, 170, 12, 9),
            ("assets/buildings/plain_orc_house_b.png", 95, 174, 9, 9),
            ("assets/buildings/generic_house_a.png", 105, 174, 9, 9),
            ("assets/buildings/generic_hut_a.png", 94, 156, 9, 9),
            ("assets/buildings/plain_orc_house_a.png", 92, 149, 9, 6),
            ("assets/buildings/plain_orc_house_c.png", 94, 166, 9, 6),
        ]:
            zone.add_landmark(sprite_key, anchor_x, anchor_y, w, h)

        # ===== DISTRICT: STABLES (SE, 40x40) =====
        OrgrimmarMassive._build_district(zone, 155, 145, 40, 40)
        zone.set_tile(170, 155, "npc", "interaction")  # Mount vendor
        zone.set_tile(155, 153, "npc", "interaction")  # Stable master - moved from (175,155), buried inside a building footprint (unreachable, caught via a full-city interaction-tile sweep)
        zone.set_tile(170, 165, "npc", "interaction")  # Supplies
        # Stable yard (wide open) - widened for full building spread
        for y in range(143, 180):
            for x in range(155, 195):
                zone.collision_layer[y][x] = None

        for sprite_key, anchor_x, anchor_y, w, h in [
            ("assets/buildings/taurajo_lodge.png", 172, 149, 15, 12),
            ("assets/buildings/watchtower.png", 157, 147, 9, 12),
            ("assets/buildings/taurajo_stables.png", 164, 171, 12, 9),
            ("assets/buildings/crossroads_stable.png", 181, 170, 12, 9),
            ("assets/buildings/watchers_perch.png", 157, 159, 9, 12),
            ("assets/buildings/plain_orc_house_b.png", 171, 161, 9, 9),
            ("assets/buildings/elders_tent.png", 180, 161, 9, 9),
        ]:
            zone.add_landmark(sprite_key, anchor_x, anchor_y, w, h)

        # Stables overflow - real open street tiles just outside this
        # district's own west gate.
        for sprite_key, anchor_x, anchor_y, w, h in [
            ("assets/buildings/generic_house_b.png", 132, 166, 9, 9),
            ("assets/buildings/plain_orc_house_b.png", 125, 159, 9, 6),
        ]:
            zone.add_landmark(sprite_key, anchor_x, anchor_y, w, h)

        # ===== SPIRIT RISE (north flight master) =====
        OrgrimmarMassive._carve_landing(zone, 100, 8, radius=3)
        zone.set_tile(100, 8, "npc", "interaction")  # Flight master
        
        # ===== SOUTH PLAZA APPROACH (between the real gate and the
        # central plaza) =====
        # Large open stone platform - kept as walkable open ground
        # leading up from the gate. This used to carry its own "portal"
        # tile labeled "Zeppelin" at (100,192), but nothing in this file
        # or portal_manager.py ever gave it a real Zeppelin destination -
        # it silently routed back to Durotar, 4 tiles north of (and
        # functionally identical to) the real south gate arrival tile
        # added above. That mislabeled duplicate is what let players
        # "arrive inside the gates": walking in from Durotar landed here,
        # past the actual gate structure, rather than at it. Removed; the
        # real gate (see South Gate section) is now the only Durotar
        # entry/exit point.
        for x in range(85, 115):
            for y in range(190, 196):
                zone.collision_layer[y][x] = None
                zone.set_tile(x, y, "stone", "base")

        # ===== MAIN ENTRY PATH (from Durotar south gate) =====
        for y in range(zone.height - 4, 130):
            zone.collision_layer[y][100] = None

        # Same fix as Undercity: the random dirt-scatter pass at the top
        # only touches base tiles (never unwalkable ones here), but every
        # district's interior clearing loop still only ever reset the
        # collision layer, so any base tile that wasn't plain "stone" or
        # "dirt" underneath a "cleared" courtyard could silently block
        # movement. Sweep once at the end for consistency.
        OrgrimmarMassive._normalize_walkable_base(zone)

        # ===== DOORWAYS: every district was a fully sealed 40x40 box with
        # only its own interior courtyard cleared - no breach through its
        # own perimeter wall toward the central plaza or the main path, so
        # every district (including the Ragefire Chasm entrance in Cleft
        # of Shadow) was reachable on the minimap and impossible to walk
        # to. Breach + connect each one to the plaza. =====
        # Valley of Wisdom (NW) -> plaza
        OrgrimmarMassive._breach(zone, 47, 27, 47, 33)
        OrgrimmarMassive._carve_path(zone, 50, 30, 55, 75, width=3)
        # Valley of Honor (NE) -> plaza
        OrgrimmarMassive._breach(zone, 155, 27, 155, 33)
        OrgrimmarMassive._carve_path(zone, 155, 30, 145, 75, width=3)
        # Magic Quarter (N-center) -> plaza
        OrgrimmarMassive._breach(zone, 97, 45, 103, 45)
        OrgrimmarMassive._carve_path(zone, 100, 45, 100, 70, width=3)
        # Valley of Strength (W) -> plaza
        OrgrimmarMassive._breach(zone, 47, 87, 47, 93)
        OrgrimmarMassive._carve_path(zone, 50, 90, 55, 100, width=3)
        # Warlock Quarter (E) -> plaza
        OrgrimmarMassive._breach(zone, 155, 87, 155, 93)
        OrgrimmarMassive._carve_path(zone, 155, 90, 145, 100, width=3)
        # Cleft of Shadow / Ragefire entrance (SW) -> plaza
        OrgrimmarMassive._breach(zone, 47, 157, 47, 163)
        OrgrimmarMassive._carve_path(zone, 50, 160, 55, 125, width=3)
        # Craft Labs (S-center) -> plaza
        OrgrimmarMassive._breach(zone, 97, 145, 103, 145)
        OrgrimmarMassive._carve_path(zone, 100, 145, 100, 130, width=3)
        # Stables (SE) -> plaza
        OrgrimmarMassive._breach(zone, 155, 157, 155, 163)
        OrgrimmarMassive._carve_path(zone, 155, 160, 145, 125, width=3)

        # ------------------------------------------------------------------
        # CHUNKED FLOOR + WALL ART (Kyle, this session: the whole 200x200
        # capital had ZERO chunked art anywhere - confirmed directly, no
        # add_ground_chunk/add_obstacle_chunk calls in this entire
        # function before now - rendering on flat default tile colors
        # (solid gray "stone", solid brown "wall") the whole time. This
        # was the actual "nausea inducing 32x32 tiles" problem, not
        # something subtler. Real per-district ground variety (9 tiles,
        # one per district + the central plaza) plus a real seamless
        # fortress wall texture for every "wall" collision tile in the
        # zone - outer defensive walls AND every district's own
        # perimeter, both use the same wall art since they're the same
        # material (city fortifications), just different scale.
        # ------------------------------------------------------------------
        district_ground = "assets/tiles/orgrimmar"
        chunk_size = 20

        def floor_chunks(x0, y0, w, h, sprite):
            for gy in range(y0, y0 + h, chunk_size):
                for gx in range(x0, x0 + w, chunk_size):
                    gw = min(chunk_size, x0 + w - gx)
                    gh = min(chunk_size, y0 + h - gy)
                    if gw > 0 and gh > 0:
                        zone.add_ground_chunk(sprite, gx, gy, gw, gh)

        # Central plaza/market (real rect: 50,70 to 150,130).
        floor_chunks(plaza_x1, plaza_y1, plaza_x2 - plaza_x1, plaza_y2 - plaza_y1,
                     f"{district_ground}/districts/plaza.png")

        # Each district's real interior footprint, matching its own
        # _build_district(zone, x, y, w, h) call above exactly.
        floor_chunks(10, 15, 40, 40, f"{district_ground}/districts/wisdom.png")
        floor_chunks(155, 15, 40, 40, f"{district_ground}/districts/honor.png")
        floor_chunks(80, 10, 40, 35, f"{district_ground}/districts/magic_quarter.png")
        floor_chunks(10, 85, 40, 40, f"{district_ground}/districts/strength.png")
        floor_chunks(155, 75, 40, 40, f"{district_ground}/districts/warlock_quarter.png")
        floor_chunks(10, 145, 40, 40, f"{district_ground}/districts/cleft_of_shadow.png")
        floor_chunks(80, 145, 40, 40, f"{district_ground}/districts/craft_labs.png")
        floor_chunks(155, 145, 40, 40, f"{district_ground}/districts/stables.png")

        # Wall art - every "wall" collision tile in the zone (outer
        # defensive ring + every district's own perimeter) gets the
        # same real seamless fortress texture, replacing the flat
        # default brown color. 4-tile obstacle chunks, matching the
        # proven scale from every cave in this project.
        fortress_wall = f"{district_ground}/fortress_wall.png"
        obstacle_chunk_size = 4
        for cy in range(0, zone.height, obstacle_chunk_size):
            for cx in range(0, zone.width, obstacle_chunk_size):
                cw = min(obstacle_chunk_size, zone.width - cx)
                ch = min(obstacle_chunk_size, zone.height - cy)
                zone.add_obstacle_chunk(fortress_wall, cx, cy, cw, ch)

        # ------------------------------------------------------------------
        # LANDMARKS - real props from this session's batch. War banners
        # flanking the south gate (the main entry everyone actually
        # walks through), the skull/tusk cluster at Valley of Honor
        # (hunter district, matches its own trophy theme), an orc
        # brazier lighting the central plaza. Kept light-touch rather
        # than one per district - these are accent placements at real
        # focal points, not a full decoration pass.
        # ------------------------------------------------------------------
        zone.add_landmark(f"{district_ground}/props/war_banner.png",
                           88, 190, 4, 8, solid=False)
        zone.add_landmark(f"{district_ground}/props/war_banner.png",
                           108, 190, 4, 8, solid=False)
        zone.add_landmark(f"{district_ground}/props/skull_tusk_cluster.png",
                           170, 20, 7, 8, solid=False)
        zone.add_landmark(f"{district_ground}/props/orc_brazier.png",
                           97, 95, 5, 6, solid=False)

        return zone

    @staticmethod
    def _normalize_walkable_base(zone):
        """Wherever collision is already clear, make sure the base tile
        underneath is actually walkable too."""
        from world.tiles import is_walkable as _walk
        for y in range(zone.height):
            for x in range(zone.width):
                if zone.collision_layer[y][x] is None:
                    base_tile = zone.base_layer[y][x]
                    if base_tile and not _walk(base_tile):
                        zone.set_tile(x, y, "stone", "base")

    @staticmethod
    def _breach(zone, x0, y0, x1, y1):
        """Punch a door-width gap through a wall segment."""
        x, y = x0, y0
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(steps + 1):
            t = i / steps
            cx = round(x0 + (x1 - x0) * t)
            cy = round(y0 + (y1 - y0) * t)
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < zone.width and 0 <= ny < zone.height:
                        zone.collision_layer[ny][nx] = None
                        zone.set_tile(nx, ny, "stone", "base")

    @staticmethod
    def _carve_path(zone, x0, y0, x1, y1, width=2, base="stone"):
        """Carve a guaranteed-walkable corridor between two points."""
        from world.tiles import is_walkable as _walk
        x, y = x0, y0
        guard = 0
        while (x, y) != (x1, y1) and guard < 4000:
            guard += 1
            for dy in range(-width, width + 1):
                for dx in range(-width, width + 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < zone.width and 0 <= ny < zone.height:
                        if not _walk(zone.base_layer[ny][nx]):
                            zone.set_tile(nx, ny, base, "base")
                        zone.collision_layer[ny][nx] = None
            if abs(x1 - x) >= abs(y1 - y) and x != x1:
                x += 1 if x1 > x else -1
            elif y != y1:
                y += 1 if y1 > y else -1
            elif x != x1:
                x += 1 if x1 > x else -1

    @staticmethod
    def _build_district(zone, x, y, w, h):
        """Build a walled district with interior space."""
        # Perimeter walls (2 tiles thick)
        for i in range(w):
            zone.set_tile(x + i, y, "wall", "collision")
            zone.set_tile(x + i, y + 1, "wall", "collision")
            zone.set_tile(x + i, y + h - 2, "wall", "collision")
            zone.set_tile(x + i, y + h - 1, "wall", "collision")
        for i in range(h):
            zone.set_tile(x, y + i, "wall", "collision")
            zone.set_tile(x + 1, y + i, "wall", "collision")
            zone.set_tile(x + w - 2, y + i, "wall", "collision")
            zone.set_tile(x + w - 1, y + i, "wall", "collision")
    
    @staticmethod
    def _carve_landing(zone, cx, cy, radius=3):
        """Carve a large landing area."""
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < zone.width and 0 <= ny < zone.height:
                    zone.collision_layer[ny][nx] = None


class UndercityMassive:
    """Generate MASSIVE Undercity (200x200) - sprawling Forsaken capital."""
    
    @staticmethod
    def generate_undercity_massive():
        """
        Undercity (200x200) - VAST Forsaken Stronghold
        
        Multiple levels represented as zones:
        - Upper Catacombs (entry elevator)
        - Trade Quarter (central marketplace, 80x60)
        - Royal Quarter (north, throne halls)
        - Research Labs (south, alchemy/crafting)
        - Guard Stations (east/west wings)
        - Plague Depths entrance (southwest corner)
        
        Maze-like structure with interconnecting passages.
        """
        zone = Tilemap("Undercity", 200, 200,
                       "The vast Forsaken stronghold. Crypts and catacombs of "
                       "fallen Lordaeron. Plague hangs heavy in the air.")
        zone.region = "Tirisfal Glades"
        
        # Base: decay stone
        zone.fill("stone", "base")
        
        # Plague tint - visual patches, not salt-and-pepper noise on every
        # tile. Was rolling independently on all 40,000 tiles at 14% each,
        # which sprayed unwalkable "wall" onto the BASE layer everywhere in
        # isolated single pixels - that's the "scattered junk" look, and
        # also what forced the _normalize_walkable_base() cleanup pass
        # below to exist at all. Clustered blobs read as sickly stone
        # patches instead, and there's far less of it for normalize to
        # have to fix up after the fact.
        for _ in range(40):
            bx = random.randint(10, zone.width - 10)
            by = random.randint(10, zone.height - 10)
            br = random.randint(3, 6)
            for dy in range(-br, br + 1):
                for dx in range(-br, br + 1):
                    if dx * dx + dy * dy <= br * br and random.random() < 0.5:
                        x, y = bx + dx, by + dy
                        if 0 <= x < zone.width and 0 <= y < zone.height:
                            zone.set_tile(x, y, "wall", "base")
        
        # Perimeter walls
        for x in range(zone.width):
            for y in range(4):
                zone.set_tile(x, y, "wall", "collision")
            for y in range(zone.height - 4, zone.height):
                zone.set_tile(x, y, "wall", "collision")
        
        for y in range(zone.height):
            for x in range(4):
                zone.set_tile(x, y, "wall", "collision")
            for x in range(zone.width - 4, zone.width):
                zone.set_tile(x, y, "wall", "collision")
        
        # ===== CENTRAL TRADE QUARTER (massive marketplace) =====
        # 80x60 central area
        trade_x1, trade_x2 = 60, 140
        trade_y1, trade_y2 = 65, 125
        
        for y in range(trade_y1, trade_y2):
            for x in range(trade_x1, trade_x2):
                zone.collision_layer[y][x] = None
                zone.set_tile(x, y, "stone", "base")
        
        # Vendor grid (16 vendors in trade quarter!)
        vendor_positions = [
            (70, 75), (85, 75), (100, 75), (115, 75),
            (70, 90), (85, 90), (100, 90), (115, 90),
            (70, 105), (85, 105), (100, 105), (115, 105),
            (70, 120), (85, 120), (100, 120), (115, 120),
        ]
        for vx, vy in vendor_positions:
            zone.set_tile(vx, vy, "npc", "interaction")
        
        # Central feature
        zone.set_tile(100, 95, "quest_marker", "interaction")
        
        # ===== MAGIC QUARTER (north, 50x45) =====
        UndercityMassive._build_section(zone, 75, 10, 50, 45)
        zone.set_tile(95, 30, "npc", "interaction")  # Mage trainer
        zone.set_tile(100, 30, "npc", "interaction")  # Enchanter
        zone.set_tile(95, 40, "npc", "interaction")  # Spell vendor
        # Interior courtyard
        for y in range(20, 40):
            for x in range(85, 110):
                zone.collision_layer[y][x] = None

        # ===== ELEVATOR ENTRANCE (from Lordaeron above) =====
        # Carved AFTER the Magic Quarter's walls exist, not before - the old
        # order had this landing carved first and then _build_section wrote
        # solid wall tiles straight back over it (the section's own north
        # perimeter sits on row 10, exactly where the portal landing was),
        # sealing the elevator into a stone box the instant you spawned in.
        UndercityMassive._carve_landing(zone, 100, 10, radius=3)
        zone.set_tile(100, 10, "portal", "interaction")  # Up to Tirisfal

        # ===== DOORWAYS: every walled quarter needs a real breach through
        # its own perimeter into open ground, or the "courtyard" inside is
        # just a sealed room - reachable on the minimap, impossible to
        # actually walk to. =====

        # Entrance landing -> Magic Quarter courtyard (both sit in the same
        # section, but the section's south wall at y=54 still separates them)
        UndercityMassive._breach(zone, 98, 54, 104, 54)
        UndercityMassive._carve_path(zone, 100, 13, 100, 60, width=2)

        # Magic Quarter courtyard -> Trade Quarter (south wall of section)
        UndercityMassive._carve_path(zone, 100, 40, 100, 65, width=3)

        # ===== ROYAL QUARTER (north-center, 50x40) =====
        UndercityMassive._build_section(zone, 125, 15, 50, 40)
        zone.set_tile(145, 30, "npc", "interaction")  # Forsaken royalty
        zone.set_tile(150, 30, "npc", "interaction")  # Court historian
        zone.set_tile(145, 38, "quest_marker", "interaction")  # Throne area
        # Throne hall (open interior)
        for y in range(20, 38):
            for x in range(135, 160):
                zone.collision_layer[y][x] = None
        # Royal Quarter courtyard -> Trade Quarter (west wall breach + path)
        UndercityMassive._breach(zone, 125, 27, 125, 33)
        UndercityMassive._carve_path(zone, 138, 30, 138, 65, width=3)

        # ===== ROGUE QUARTER (west, 45x50) =====
        UndercityMassive._build_section(zone, 10, 60, 45, 50)
        zone.set_tile(30, 80, "npc", "interaction")  # Rogue trainer
        zone.set_tile(35, 80, "npc", "interaction")  # Poison master
        zone.set_tile(30, 95, "npc", "interaction")  # Black market
        # Shadowy courtyard
        for y in range(75, 100):
            for x in range(20, 40):
                zone.collision_layer[y][x] = None
        # Rogue Quarter courtyard -> Trade Quarter (east wall breach + path)
        UndercityMassive._breach(zone, 53, 82, 53, 88)
        UndercityMassive._carve_path(zone, 40, 85, 60, 85, width=3)

        # ===== WARLOCK QUARTER (east, 45x50) =====
        UndercityMassive._build_section(zone, 155, 60, 45, 50)
        zone.set_tile(175, 80, "npc", "interaction")  # Warlock trainer
        zone.set_tile(180, 80, "npc", "interaction")  # Demonic master
        zone.set_tile(175, 95, "npc", "interaction")  # Soul trader
        # Dark courtyard
        for y in range(75, 100):
            for x in range(165, 185):
                zone.collision_layer[y][x] = None
        # Warlock Quarter courtyard -> Trade Quarter (west wall breach + path)
        UndercityMassive._breach(zone, 155, 82, 155, 88)
        UndercityMassive._carve_path(zone, 165, 85, 140, 85, width=3)

        # ===== RESEARCH LABS (south, 80x50) =====
        UndercityMassive._build_section(zone, 60, 140, 80, 50)
        zone.set_tile(85, 160, "npc", "interaction")  # Alchemist
        zone.set_tile(100, 160, "npc", "interaction")  # Leatherworker
        zone.set_tile(115, 160, "npc", "interaction")  # Tailor
        zone.set_tile(85, 175, "npc", "interaction")  # Reagent vendor
        # Lab courtyard (wide open)
        for y in range(150, 175):
            for x in range(75, 135):
                zone.collision_layer[y][x] = None
        # Research Labs courtyard -> Trade Quarter (north wall breach + path)
        UndercityMassive._breach(zone, 97, 140, 103, 140)
        UndercityMassive._carve_path(zone, 100, 150, 100, 122, width=3)

        # ===== PLAGUE DEPTHS DUNGEON PORTAL (SW corner) =====
        UndercityMassive._carve_landing(zone, 30, 180, radius=3)
        zone.set_tile(30, 180, "portal", "interaction")  # Dungeon entry
        zone.set_tile(35, 180, "quest_marker", "interaction")  # Quest giver
        # Plague Depths landing -> Research Labs -> rest of the city, or the
        # dungeon entrance sat in its own sealed SW pocket same as everything
        # else here.
        UndercityMassive._carve_path(zone, 30, 177, 75, 160, width=3)

        # Final consistency pass: the random "plague tint" pass at the top
        # stamps unwalkable "wall" onto the BASE layer across the whole
        # zone (14% chance per tile), completely independent of collision.
        # Every courtyard/interior-clearing loop above only ever cleared
        # the collision layer, so roughly 1 in 7 tiles inside a "cleared"
        # room could still silently be an unwalkable wall tile underneath -
        # this is why NPCs and portals occasionally landed on dead ground
        # even though the surrounding room read as open on the minimap.
        # Sweep once at the end: anywhere collision is already clear, force
        # the base tile walkable too.
        UndercityMassive._normalize_walkable_base(zone)

        return zone

    @staticmethod
    def _normalize_walkable_base(zone):
        """Wherever collision is already clear, make sure the base tile
        underneath is actually walkable too."""
        from world.tiles import is_walkable as _walk
        for y in range(zone.height):
            for x in range(zone.width):
                if zone.collision_layer[y][x] is None:
                    base_tile = zone.base_layer[y][x]
                    if base_tile and not _walk(base_tile):
                        zone.set_tile(x, y, "stone", "base")

    @staticmethod
    def _breach(zone, x0, y0, x1, y1):
        """Punch a door-width gap through a wall segment between two points
        on the same wall (a short straight run), clearing collision only -
        this is for opening a doorway in an existing perimeter, not carving
        new ground, so it doesn't touch the base tile."""
        x, y = x0, y0
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(steps + 1):
            t = i / steps
            cx = round(x0 + (x1 - x0) * t)
            cy = round(y0 + (y1 - y0) * t)
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < zone.width and 0 <= ny < zone.height:
                        zone.collision_layer[ny][nx] = None
                        zone.set_tile(nx, ny, "stone", "base")
    
    @staticmethod
    def _build_section(zone, x, y, w, h):
        """Build a section with thick walls."""
        for i in range(w):
            zone.set_tile(x + i, y, "wall", "collision")
            zone.set_tile(x + i, y + 1, "wall", "collision")
            zone.set_tile(x + i, y + h - 2, "wall", "collision")
            zone.set_tile(x + i, y + h - 1, "wall", "collision")
        for i in range(h):
            zone.set_tile(x, y + i, "wall", "collision")
            zone.set_tile(x + 1, y + i, "wall", "collision")
            zone.set_tile(x + w - 2, y + i, "wall", "collision")
            zone.set_tile(x + w - 1, y + i, "wall", "collision")
    
    @staticmethod
    def _carve_landing(zone, cx, cy, radius=3):
        """Carve landing area. Clears collision AND resets the base tile to
        plain stone - the random "plague tint" pass earlier stamps a 14%
        chance of "wall" onto the BASE layer across the entire zone,
        independent of collision, so a landing with collision cleared could
        still land the player on an unwalkable wall-base tile."""
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < zone.width and 0 <= ny < zone.height:
                    zone.collision_layer[ny][nx] = None
                    if zone.base_layer[ny][nx] == "wall":
                        zone.set_tile(nx, ny, "stone", "base")

    @staticmethod
    def _carve_path(zone, x0, y0, x1, y1, width=2, base="stone"):
        """Carve a guaranteed-walkable corridor between two points, clearing
        both the collision layer and any non-walkable base tile (wall,
        water, etc) - this is what actually connects a walled section's
        interior to the rest of the map, since a breach in the perimeter
        alone still leaves a wall of untouched 'wall' base tiles just past
        it in the no-man's-land between sections."""
        from world.tiles import is_walkable as _walk
        x, y = x0, y0
        guard = 0
        while (x, y) != (x1, y1) and guard < 4000:
            guard += 1
            for dy in range(-width, width + 1):
                for dx in range(-width, width + 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < zone.width and 0 <= ny < zone.height:
                        if not _walk(zone.base_layer[ny][nx]):
                            zone.set_tile(nx, ny, base, "base")
                        zone.collision_layer[ny][nx] = None
            if abs(x1 - x) >= abs(y1 - y) and x != x1:
                x += 1 if x1 > x else -1
            elif y != y1:
                y += 1 if y1 > y else -1
            elif x != x1:
                x += 1 if x1 > x else -1


class RagefireChasmMassive:
    """Generate MASSIVE Ragefire Chasm (200x180) - Proper multi-boss dungeon."""
    
    @staticmethod
    def generate_ragefire_chasm_massive():
        """
        Ragefire Chasm (240x220) - real WoW Classic layout: entrance tunnel
        winds north from Orgrimmar's Cleft of Shadow, Oggleflint sits in a
        genuine side-cave DETOUR off the main path (not on critical path -
        matches "moved to be on the main path" only happening in Cataclysm;
        this is the Classic layout, side cave), then the path continues to
        Taragaman the Hungerer on a lava-bridge platform (his real WoW
        position: a demon on a center platform over a lava lake, crossed by
        interlocking bridges), then Jergosh the Invoker just past/behind
        him, then Bazzalan up an adjacent elevated walkway in the final
        room. Real boss roster only - Earthborer, Magmus, Pyromancer
        Loregrain, and "Ragefire Shaman Overlord" from the old generator
        were invented names that don't exist in the real dungeon and have
        been removed; Earthborer is a real RFC mob but a trash worm, never
        a boss.

        This used to be five ~9,000-tile filled-rectangle "chambers"
        connected by thin straight strips - reads as one open field with
        boss-marker labels stuck in it, not a dungeon. Rebuilt around
        actual corridors (ZoneGenerator._carve_path, width 3-5) connecting
        purpose-sized rooms, with a real branching point at Oggleflint's
        cave mouth instead of every room being reachable by walking in a
        straight line from the entrance.
        """
        zone = Tilemap("Ragefire Chasm", 240, 220,
                       "A volcanic cavern beneath Orgrimmar. Troggs and the "
                       "Searing Blade cult have made this their territory.")
        zone.is_cave = True
        zone.region = "Orgrimmar"

        # Base volcanic stone, whole map starts solid (wall) - corridors
        # and rooms carve INTO this, rather than starting open and adding
        # walls on top. This is the actual mechanism that makes a linear
        # dungeon read as linear: everywhere you haven't carved is a real
        # wall, not "technically walkable but decorated to look solid."
        zone.fill("stone", "base")
        for y in range(zone.height):
            for x in range(zone.width):
                zone.set_tile(x, y, "wall", "collision")

        def _room(cx, cy, w, h, lava_chance=0.0):
            """Carve a rectangular room centered on (cx, cy), clearing
            collision and normalizing base to stone. lava_chance scatters
            real lava tiles for hazard rooms (Taragaman's bridge chamber)."""
            for dy in range(-h // 2, h // 2 + 1):
                for dx in range(-w // 2, w // 2 + 1):
                    x, y = cx + dx, cy + dy
                    if 0 <= x < zone.width and 0 <= y < zone.height:
                        zone.collision_layer[y][x] = None
                        if lava_chance and random.random() < lava_chance:
                            zone.set_tile(x, y, "lava", "base")
                        else:
                            zone.set_tile(x, y, "stone", "base")

        def _corridor(x0, y0, x1, y1, width=3):
            ZoneGenerator._carve_path(zone, x0, y0, x1, y1, width=width, base="stone")

        # ===== ENTRANCE TUNNEL (from Orgrimmar's Cleft of Shadow) =====
        entrance = (120, 214)
        zone.set_tile(*entrance, "portal", "interaction")   # -> Orgrimmar
        _room(120, 200, 18, 14)
        # Connect the portal tile itself to the entrance room - the room
        # above is centered at y=200 (spans ~193-207), which doesn't reach
        # the portal at y=214 on its own. Missing this left the portal
        # tile surrounded by uncarved wall on all sides - a real "you
        # spawn inside a sealed box" bug caught by a flood-fill
        # reachability check, not just eyeballed.
        _corridor(120, 214, 120, 200, width=4)

        # ===== MAIN PATH NORTH - winding, not a straight line =====
        _corridor(120, 200, 100, 175, width=4)
        _room(95, 168, 26, 20)  # first trash pocket, Ragefire Troggs

        _corridor(95, 158, 120, 135, width=4)
        _room(122, 128, 24, 18)  # second trash pocket, Searing Blade cultists

        # ===== OGGLEFLINT'S SIDE CAVE (real branch off the main path -
        # this is the genuine detour: skippable, not required to progress,
        # matches "tucked away in a side cave" from every real guide) =====
        _corridor(122, 118, 75, 108, width=3)
        _room(60, 105, 30, 24)
        oggleflint_pos = (55, 100)
        zone.set_tile(*oggleflint_pos, "boss_marker", "interaction")
        zone.set_tile(65, 108, "npc", "interaction")  # Maur Grimtotem's corpse (quest)
        zone.add_subzone("Oggleflint's Den", 45, 93, 30, 24)

        # ===== MAIN PATH CONTINUES to Taragaman's bridge chamber =====
        # Corridor terminates at the room's south edge (taragaman_cy+20),
        # NOT inside the room itself - the room is carved with random lava
        # scatter after this, and a corridor endpoint landing inside that
        # scatter has a real chance of being repainted right back into
        # lava (caught by a flood-fill reachability check: Taragaman was
        # unreachable ~85% of the time depending on random seed). The
        # bridge cross below guarantees a safe walk from this doorway to
        # the boss platform once inside.
        taragaman_cx, taragaman_cy = 90, 60
        _corridor(122, 118, taragaman_cx, taragaman_cy + 20, width=4)

        # Taragaman's chamber: a real lava-lake room crossed by narrow
        # stone bridges, not just "a room with some lava tiles scattered
        # in it" - the bridges are the only safe path across, matching
        # "interlacing bridges over a large pool of lava" from every guide.
        _room(taragaman_cx, taragaman_cy, 46, 40, lava_chance=0.85)
        # Bridges: a cross of solid stone through the lava so the room
        # isn't just "avoid the red tiles", it's "walk the bridge." South
        # arm extended to y+20 (the room's own south edge, where the
        # corridor above terminates) rather than stopping at y+19, so the
        # doorway tile is always guaranteed stone regardless of the random
        # lava scatter the room carve above may have painted there.
        for dx in range(-22, 23):
            x, y = taragaman_cx + dx, taragaman_cy
            if 0 <= x < zone.width:
                zone.set_tile(x, y, "stone", "base")
                zone.collision_layer[y][x] = None
        for dy in range(-19, 21):
            x, y = taragaman_cx, taragaman_cy + dy
            if 0 <= y < zone.height:
                zone.set_tile(x, y, "stone", "base")
                zone.collision_layer[y][x] = None
        taragaman_pos = (taragaman_cx, taragaman_cy)
        zone.set_tile(*taragaman_pos, "boss_marker", "interaction")
        zone.add_subzone("Taragaman's Chamber", taragaman_cx - 23, taragaman_cy - 20, 46, 40)

        # ===== JERGOSH'S CHAMBER (just past/behind Taragaman) =====
        _corridor(90, 40, 70, 20, width=4)
        _room(65, 15, 30, 20)
        jergosh_pos = (62, 12)
        zone.set_tile(*jergosh_pos, "boss_marker", "interaction")
        zone.add_subzone("Jergosh's Chamber", 50, 5, 30, 20)

        # ===== BAZZALAN'S WALKWAY (final room, elevated, adjacent to and
        # above Jergosh's chamber per every real guide - reached by a
        # short ramp corridor rather than being a separate teleport) =====
        # width bumped 3->5: the original width=3 corridor's real carved
        # strip stopped 2 tiles short of Bazzalan's room boundary (his
        # room starts at x=102, the corridor's own endpoint painted out
        # to about x=99-100) - real, pre-existing disconnect caught by a
        # direct flood-fill from Bazzalan's own boss position, which
        # found his entire room totally isolated from the rest of the
        # dungeon. A wider corridor closes that real gap; the x1=100 ->
        # 102 endpoint also nudged to guarantee overlap with the room's
        # own left edge rather than trusting the width alone.
        _corridor(75, 15, 102, 15, width=5)
        _room(115, 15, 26, 16)
        bazzalan_pos = (120, 12)
        zone.set_tile(*bazzalan_pos, "boss_marker", "interaction")
        zone.add_subzone("Bazzalan's Walkway", 102, 7, 26, 16)

        # Quest NPCs near the entrance (Stone Guard Kurjack, Bovaal
        # Whitehorn - real RFC quest givers, both stationed just inside
        # the entrance per their real coordinates).
        zone.set_tile(112, 205, "npc", "interaction")  # Stone Guard Kurjack
        zone.set_tile(128, 205, "npc", "interaction")  # Bovaal Whitehorn

        zone.boss_positions = [
            (oggleflint_pos[0], oggleflint_pos[1], "Oggleflint"),
            (taragaman_pos[0], taragaman_pos[1], "Taragaman the Hungerer"),
            (jergosh_pos[0], jergosh_pos[1], "Jergosh the Invoker"),
            (bazzalan_pos[0], bazzalan_pos[1], "Bazzalan"),
        ]
        zone.boss_position = taragaman_pos  # legacy single-boss fallback - Taragaman is RFC's headline boss
        zone.add_subzone("Ragefire Chasm", 0, 0, zone.width, zone.height)

        # ------------------------------------------------------------------
        # CHUNKED FLOOR + WALL ART (Kyle, this session: "we just need to
        # tile and wall it" - shape confirmed fine as-is). This dungeon
        # had ZERO chunked art calls before now (confirmed directly, no
        # add_ground_chunk/add_obstacle_chunk anywhere in this function),
        # rendering on bare "stone"/"wall" tile_id default colors since
        # it was first built. Reuses Skull Rock's real Burning Blade
        # cave set - a deliberate, thematically correct reuse (Kyle
        # flagged this pairing earlier this session): RFC's Searing
        # Blade cultists and Skull Rock's Burning Blade cultists are
        # explicitly the same faction escalation per the bestiary, and
        # both caves are volcanic/troll-adjacent troggs-and-cultists
        # territory. Not a generic placeholder reuse.
        #
        # Per-room material logic, matching each room's real content:
        #   - Trash trogg pockets, Oggleflint's den, Bazzalan's walkway
        #     -> floor_cavern/wall_cave (plain volcanic rock)
        #   - Searing Blade cultist pocket, Jergosh's chamber
        #     -> floor_ritual (same cult-worked-stone read as Skull
        #        Rock's own ritual rooms)
        #   - Taragaman's lava-bridge chamber -> floor_molten/
        #     wall_scorched (the one room with a real lava hazard
        #     already carved in, so the scorched/glowing variant earns
        #     its place here specifically, not just applied everywhere)
        # ------------------------------------------------------------------
        cavern_floor = "assets/tiles/skull_rock/floor_cavern.png"
        cavern_wall = "assets/tiles/skull_rock/wall_cave.png"
        ritual_floor = "assets/tiles/skull_rock/floor_ritual.png"
        molten_floor = "assets/tiles/skull_rock/floor_molten.png"
        scorched_wall = "assets/tiles/skull_rock/wall_scorched.png"

        chunk_size = 20

        def floor_chunks(cx, cy, w, h, sprite):
            x0, y0 = cx - w // 2 - 2, cy - h // 2 - 2
            x1, y1 = cx + w // 2 + 2, cy + h // 2 + 2
            for gy in range(y0, y1, chunk_size):
                for gx in range(x0, x1, chunk_size):
                    gw = min(chunk_size, x1 - gx)
                    gh = min(chunk_size, y1 - gy)
                    if gw > 0 and gh > 0:
                        zone.add_ground_chunk(sprite, gx, gy, gw, gh)

        # Entrance room + winding corridor + first two trash pockets.
        floor_chunks(120, 200, 18, 14, cavern_floor)
        floor_chunks(95, 168, 26, 20, cavern_floor)
        floor_chunks(122, 128, 24, 18, ritual_floor)   # Searing Blade cultist pocket

        # Oggleflint's side-cave detour.
        floor_chunks(60, 105, 30, 24, cavern_floor)

        # Taragaman's lava-bridge chamber - the one molten room.
        floor_chunks(taragaman_cx, taragaman_cy, 46, 40, molten_floor)

        # Jergosh's chamber (cult caster - ritual floor) and Bazzalan's
        # elevated walkway (plain cavern - he's a rogue, not a cultist).
        floor_chunks(65, 15, 30, 20, ritual_floor)
        floor_chunks(115, 15, 26, 16, cavern_floor)

        # Wall art - scorched/glowing variant scoped to Taragaman's own
        # chamber boundary only (matches Skull Rock's own accent-ring
        # discipline for its most distinctive texture), plain cavern
        # wall everywhere else across the whole 240x220 map.
        obstacle_chunk_size = 4
        for cy in range(0, zone.height, obstacle_chunk_size):
            for cx in range(0, zone.width, obstacle_chunk_size):
                cw = min(obstacle_chunk_size, zone.width - cx)
                ch = min(obstacle_chunk_size, zone.height - cy)
                dx, dy = cx - taragaman_cx, cy - taragaman_cy
                in_taragaman_room = abs(dx) <= 25 and abs(dy) <= 22
                sprite = scorched_wall if in_taragaman_room else cavern_wall
                zone.add_obstacle_chunk(sprite, cx, cy, cw, ch)

        # ------------------------------------------------------------------
        # LANDMARKS - real reused Skull Rock props. Oggleflint's den gets
        # a bone pile (troggs, not cultists - matches Skull Rock's own
        # bone-pile placement logic). Taragaman's chamber gets lava
        # spikes flanking the bridge crossing (his real WoW fight is ON
        # a lava lake, so visible lava hazard props sell that beyond
        # just the floor texture). Jergosh's cultist chamber gets a
        # ritual brazier, matching his caster/invoker role.
        # ------------------------------------------------------------------
        zone.add_landmark("assets/tiles/skull_rock/props/bone_pile.png",
                           oggleflint_pos[0] - 4, oggleflint_pos[1] + 3, 4, 4, solid=False)
        zone.add_landmark("assets/tiles/skull_rock/props/lava_spikes.png",
                           taragaman_cx - 18, taragaman_cy - 14, 4, 4)
        zone.add_landmark("assets/tiles/skull_rock/props/lava_spikes.png",
                           taragaman_cx + 15, taragaman_cy + 12, 4, 4)
        zone.add_landmark("assets/tiles/skull_rock/props/ritual_brazier.png",
                           jergosh_pos[0] - 6, jergosh_pos[1] + 2, 4, 5, solid=False)

        return zone
    
    @staticmethod
    def _carve_chamber(zone, x, y, w, h):
        """Carve out a chamber.

        Clears collision AND normalizes the base layer to plain stone.
        Chambers are carved after the zone-wide plague-tint / lava scatter
        runs, which can leave non-walkable base tiles (wall-tint, lava)
        inside a "cleared" chamber - collision being None isn't enough,
        is_walkable() also checks the base tile, so a chamber could roll
        just enough hazard tiles along its only connecting corridor to
        seal a boss chamber off entirely depending on the random seed.
        """
        for dy in range(h):
            for dx in range(w):
                nx, ny = x + dx, y + dy
                if 0 <= nx < zone.width and 0 <= ny < zone.height:
                    zone.collision_layer[ny][nx] = None
                    if zone.base_layer[ny][nx] in ('wall', 'lava'):
                        zone.set_tile(nx, ny, 'stone', 'base')


class PlaguedepthsMassive:
    """Generate MASSIVE Plague Depths (200x180) - Epic 5-boss dungeon."""
    
    @staticmethod
    def generate_plague_depths_massive():
        """
        Plague Depths (200x180) - MASSIVE Forsaken conspiracy dungeon
        
        5 Boss Progression:
        1. Plagueweaver Vex (entry trash area)
        2. The Infected Noble (throne chamber)
        3. Plague Keeper Voss (library/archives)
        4. Vile Plague Abomination (biological vault)
        5. Dark Sorcerer Zul'keth (plague heart)
        
        Layout (sprawling map):
        - Entry → Quest hub
        - Central Atrium (4-way split)
        - Left: Throne → Archives path
        - Right: Vault chamber path
        - Up: Ascent to Plague Heart
        - Down: Secondary treasures
        """
        zone = Tilemap("Plague Depths", 240, 220,
                       "Deep Undercity plague vaults. Forsaken traitors cultivate blight "
                       "to weaponize against their own. The air reeks of corruption.")
        zone.is_cave = True
        zone.region = "Undercity"
        
        # Base: decay stone
        zone.fill("stone", "base")
        
        # Plague tint - sickly patches, denser than a plain stone floor.
        # Same fix as Undercity above: clustered blobs instead of
        # independent per-tile noise, so it reads as diseased ground
        # texture rather than scattered debris, and doesn't quietly seed
        # unwalkable wall tiles evenly across the whole dungeon floor.
        for _ in range(55):
            bx = random.randint(6, zone.width - 6)
            by = random.randint(6, zone.height - 6)
            br = random.randint(3, 6)
            for dy in range(-br, br + 1):
                for dx in range(-br, br + 1):
                    if dx * dx + dy * dy <= br * br:
                        x, y = bx + dx, by + dy
                        if 0 <= x < zone.width and 0 <= y < zone.height:
                            r = random.random()
                            if r < 0.6:
                                zone.set_tile(x, y, "wall", "base")
                            elif r < 0.85:
                                zone.set_tile(x, y, "bushes", "visual")
        
        # Perimeter
        for x in range(zone.width):
            for y in range(3):
                zone.set_tile(x, y, "wall", "collision")
            for y in range(zone.height - 3, zone.height):
                zone.set_tile(x, y, "wall", "collision")
        
        for y in range(zone.height):
            for x in range(3):
                zone.set_tile(x, y, "wall", "collision")
            for x in range(zone.width - 3, zone.width):
                zone.set_tile(x, y, "wall", "collision")
        
        # ===== ENTRY CHAMBER (south) =====
        PlaguedepthsMassive._carve_chamber(zone, 70, zone.height - 65, 100, 60)
        zone.set_tile(120, zone.height - 48, "npc", "interaction")  # Quest
        boss1 = (120, zone.height - 30)
        zone.set_tile(*boss1, "boss_marker", "interaction")  # Boss 1: Plagueweaver Vex

        # Exit portal back to Undercity
        PlaguedepthsMassive._carve_chamber(zone, 110, zone.height - 8, 20, 5)
        zone.set_tile(120, zone.height - 6, "portal", "interaction")  # -> Undercity
        
        # Entry corridor
        for y in range(zone.height - 3, zone.height - 65):
            for x in range(118, 123):
                zone.collision_layer[y][x] = None
                if zone.base_layer[y][x] in ("wall", "lava"):
                    zone.set_tile(x, y, "stone", "base")
        
        # ===== CENTRAL ATRIUM (massive hub) =====
        atrium_x, atrium_y = 65, 48
        PlaguedepthsMassive._carve_chamber(zone, atrium_x, atrium_y, 108, 108)
        zone.set_tile(120, 102, "quest_marker", "interaction")  # Central marker
        
        # ===== WEST-NORTH: THRONE CHAMBER =====
        PlaguedepthsMassive._carve_chamber(zone, 12, 18, 84, 84)
        boss2 = (42, 54)
        zone.set_tile(*boss2, "boss_marker", "interaction")  # Boss 2: The Infected Noble
        for x in range(12, 65):
            for y in range(58, 63):
                zone.collision_layer[y][x] = None
                if zone.base_layer[y][x] in ("wall", "lava"):
                    zone.set_tile(x, y, "stone", "base")
        
        # ===== ARCHIVES (north of throne) =====
        PlaguedepthsMassive._carve_chamber(zone, 24, 8, 72, 72)
        boss3 = (48, 36)
        zone.set_tile(*boss3, "boss_marker", "interaction")  # Boss 3: Plague Keeper Voss
        for y in range(8, 60):
            for x in range(46, 51):
                zone.collision_layer[y][x] = None
                if zone.base_layer[y][x] in ("wall", "lava"):
                    zone.set_tile(x, y, "stone", "base")
        
        # ===== EAST-SOUTH: BIOLOGICAL VAULT =====
        PlaguedepthsMassive._carve_chamber(zone, 156, 72, 84, 84)
        boss4 = (186, 102)
        zone.set_tile(*boss4, "boss_marker", "interaction")  # Boss 4: Abomination
        for x in range(174, 240):
            for y in range(100, 105):
                zone.collision_layer[y][x] = None
                if zone.base_layer[y][x] in ("wall", "lava"):
                    zone.set_tile(x, y, "stone", "base")
        
        # ===== NORTH-CENTRAL: PLAGUE HEART =====
        PlaguedepthsMassive._carve_chamber(zone, 72, 8, 96, 84)
        boss5 = (120, 36)
        zone.set_tile(*boss5, "boss_marker", "interaction")  # Boss 5: Dark Sorcerer (final)
        for y in range(8, 48):
            for x in range(118, 123):
                zone.collision_layer[y][x] = None
                if zone.base_layer[y][x] in ("wall", "lava"):
                    zone.set_tile(x, y, "stone", "base")
        
        # ===== TREASURE VAULT (north, dead-end) =====
        PlaguedepthsMassive._carve_chamber(zone, 96, 5, 48, 24)
        zone.set_tile(120, 15, "quest_marker", "interaction")  # Final loot
        
        # ===== SECONDARY CHAMBER (east wing) =====
        PlaguedepthsMassive._carve_chamber(zone, 180, 156, 48, 48)
        zone.set_tile(204, 180, "quest_marker", "interaction")  # Secondary treasure
        boss6 = (195, 165)
        zone.set_tile(*boss6, "boss_marker", "interaction")  # Boss 6: Rot Warden
        for x in range(180, 240):
            for y in range(178, 183):
                zone.collision_layer[y][x] = None
                if zone.base_layer[y][x] in ("wall", "lava"):
                    zone.set_tile(x, y, "stone", "base")

        # ===== WEST WING (mirrors the secondary chamber) =====
        PlaguedepthsMassive._carve_chamber(zone, 60, 156, 48, 48)
        boss7 = (60, 165)
        zone.set_tile(*boss7, "boss_marker", "interaction")  # Boss 7: Contagion Bearer
        for x in range(0, 65):
            for y in range(178, 183):
                zone.collision_layer[y][x] = None
                if zone.base_layer[y][x] in ("wall", "lava"):
                    zone.set_tile(x, y, "stone", "base")

        # ===== SUB-BASEMENT (a pocket behind the atrium) =====
        PlaguedepthsMassive._carve_chamber(zone, 120, 108, 40, 30)
        boss8 = (120, 108)
        zone.set_tile(*boss8, "boss_marker", "interaction")  # Boss 8: The Blighted Ossuary

        zone.boss_positions = [boss1, boss2, boss3, boss4, boss5, boss6, boss7, boss8]
        zone.boss_position = boss1
        zone.add_subzone("Plague Depths", 0, 0, zone.width, zone.height)

        # Safety sweep - same reasoning as Undercity/Orgrimmar: wherever
        # collision is clear, make sure the base tile underneath is
        # actually walkable, in case any carve step above missed cleaning
        # up a wall/lava tile it cleared collision over.
        from world.tiles import is_walkable as _walk
        for y in range(zone.height):
            for x in range(zone.width):
                if zone.collision_layer[y][x] is None:
                    base_tile = zone.base_layer[y][x]
                    if base_tile and not _walk(base_tile):
                        zone.set_tile(x, y, "stone", "base")

        return zone
    
    @staticmethod
    def _carve_chamber(zone, x, y, w, h):
        """Carve out a chamber.

        Clears collision AND normalizes the base layer to plain stone.
        Chambers are carved after the zone-wide plague-tint / lava scatter
        runs, which can leave non-walkable base tiles (wall-tint, lava)
        inside a "cleared" chamber - collision being None isn't enough,
        is_walkable() also checks the base tile, so a chamber could roll
        just enough hazard tiles along its only connecting corridor to
        seal a boss chamber off entirely depending on the random seed.
        """
        for dy in range(h):
            for dx in range(w):
                nx, ny = x + dx, y + dy
                if 0 <= nx < zone.width and 0 <= ny < zone.height:
                    zone.collision_layer[ny][nx] = None
                    if zone.base_layer[ny][nx] in ('wall', 'lava'):
                        zone.set_tile(nx, ny, 'stone', 'base')


# Entry functions for integration
def generate_orgrimmar_expanded():
    return OrgrimmarMassive.generate_orgrimmar_massive()

def generate_ragefire_chasm():
    return RagefireChasmMassive.generate_ragefire_chasm_massive()

def generate_undercity():
    return UndercityMassive.generate_undercity_massive()

def generate_plague_depths():
    return PlaguedepthsMassive.generate_plague_depths_massive()
