#!/usr/bin/env python3
"""Writes docs/faction_art_prompts.md: a background painting for each faction's detail card.

    python3 tools/write_faction_art_prompts.py

Kyle, 19 Nov 2026: "when we get enough factions ... make some background art whenever we click on a faction card ...
kind of makes sense to make it less boring. Can i get a prompt". One landscape per faction, four to a sheet. The
secret faction gets none: its card says nothing on purpose (tools/qa_unnamed_faction.py).
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs/faction_art_prompts.md"

HEAD = ("Generate ONE image, 2048x1536, laid out as a strict 2 columns x 2 rows grid = 4 separate landscape paintings, "
        "each panel exactly 1024x768. COUNT THEM: exactly 2 across and 2 down. Each panel is COMPLETELY FILLED by its "
        "painting, edge to edge, with no border, no frame, no gutter, no grid lines, no text, no letters, no logos, no "
        "banners with writing, no numbers. Painterly semi-realistic fantasy art in the style of World of Warcraft "
        "loading screens: rich, atmospheric, soft painted edges, a sense of place.\n\n"
        "These are BACKGROUNDS for a game's faction card, so the composition matters: the place and its people fill "
        "the upper two-thirds of each panel; the lower third is calmer and darker (ground, shadow, mist or water) so "
        "white text can be read over it; a soft natural vignette toward the edges; no single face close to the "
        "viewer, figures small or seen from behind; nothing bright or busy in the lower third. Each panel is the "
        "faction's HOME and what it stands for, readable at a glance. Nothing from our real world appears unless the "
        "panel says so.")

#: (key, faction, panel description)
PANELS = [
    ("crimson_codex", "The Crimson Codex", "Kael's Bastion deep in the Crystalline Underdark: a blood elf arcanist "
     "citadel of crimson and gold built into a vast cavern of glowing blue and violet crystal, floating tomes and "
     "arcane sigils of light, robed magisters on a high balcony, the cavern falling away into darkness below."),
    ("orgrimmar", "Orgrimmar", "Orgrimmar at dusk: the orc capital of red stone and ship timber in a canyon, spiked "
     "iron walls, war banners of red and black, smoke from forges, wyverns circling, the great gate's tusks in "
     "silhouette, warm firelight against a red sky."),
    ("darkspear_tribe", "The Darkspear Tribe", "The Echo Isles at sunset: jungle troll huts on stilts over a turquoise "
     "lagoon, carved loa totems, torches and voodoo lanterns, palm trees, a war canoe pulled up on white sand, a "
     "witch doctor's green smoke rising."),
    ("the_forsaken", "The Forsaken", "The ruined throne city of Lordaeron above the Undercity's gate: broken pale "
     "towers, sickly green light glowing up from below, purple banners, plague cauldrons, bats against a grey-green "
     "sky, Forsaken sentries in silhouette."),
    ("steamwheedle_cartel", "The Steamwheedle Cartel", "Ratchet's harbour on the Barrens coast: a ramshackle goblin "
     "port of cranes, crates and leaning warehouses, a steam ship at the dock, gold coins and ledgers on a trading "
     "table in the foreground shadows, warm lamplight, the sea at golden hour."),
    ("thunder_bluff", "Thunder Bluff", "Camp Taurajo in exile at twilight: tauren tents and totems on the open "
     "savanna, a great memorial pole hung with feathers and carved tokens, kodo resting, and far away on the horizon "
     "the dark broken silhouette of the bluffs where Thunder Bluff once stood. Sorrowful and proud."),
    ("booty_bay_authority", "The Booty Bay Port Authority", "Booty Bay inside its sea arch: wooden goblin buildings "
     "stacked up the cliffs round a turquoise cove, the giant shark jaw over the entrance tunnel, pirate ships and "
     "merchant ships moored together, lanterns coming on at dusk."),
    ("the_ashclaim", "The Ashclaim", "Cinderwharf on Tempest Isle: a Dark Iron dwarf and goblin city of black stone "
     "and copper built round a volcanic harbour, glowing forges and lava channels, storm clouds and lightning over "
     "the sea, cranes hauling salvage."),
    ("emerald_reclamation", "The Emerald Reclamation", "Emerald Sanctuary in Felwood: a glade of healthy green and "
     "gold light pushing back a corrupted forest of black trees and green fel ooze, night elf druids, furbolgs and "
     "treants planting saplings, a moonwell glowing silver-blue."),
    ("pale_flame", "The Order of the Pale Flame", "The Bulwark at the edge of the Plaguelands: a fortified wall and "
     "gate, braziers burning with pale white-gold flame, soldiers in plain grey armour with white tabards (a few "
     "with a modern soldier's bearing, nothing modern in their gear), a plagued forest beyond under a bruised sky."),
    ("argent_dawn", "The Argent Dawn", "Light's Hope Chapel in the Eastern Plaguelands: a holy chapel of white stone "
     "on a hill, golden light streaming from its windows, argent banners of silver and blue, knights keeping watch, "
     "the dead lands grey and dark all round it."),
    ("timbermaw_hold", "Timbermaw Hold", "Timbermaw Hold, a furbolg city in a great caldera in Azshara: wooden "
     "lodges and totems carved into the crater's walls, a waterfall into a lake at the centre, autumn trees in red "
     "and gold, warm lantern light, furbolg elders round a fire."),
    ("sunreach_conclave", "The Sunreach Conclave", "Firstlight Spire on Dawnhaven, the Conclave's home since 21 "
     "Nov 2026 (redrawn as Dawnhaven's DH5): a slender white and gold spire with a blazing gold crystal at its top on "
     "a headland over a turquoise sea, a small elven town of crimson roofs round it, forever-autumn trees in red and "
     "gold, a short pier with an elven boat, and far off across the strait the Azshara coast at sunset."),
    ("the_liquidators", "The Liquidators", "Ariden's Watch in Deadwind Pass: a grim fortified camp of people from our "
     "world holding back a poisoned land, sandbag walls, lanterns, figures in heavy protective coats and respirator "
     "hoods made from leather and canvas, and on the dark horizon a giant rusted Ferris wheel against a sickly green "
     "sky (the Ferris wheel is the ONE thing from our world allowed in this panel)."),
    ("cenarion_circle", "The Cenarion Circle", "Nighthaven in Moonglade at night: night elf and tauren druid lodges "
     "round the moonlit Lake Elune'ara, ancient trees, the Shrine of Remulos glowing softly, hippogryphs and owls, "
     "silver moonlight on the water."),
    ("the_wakened", "The Wakened", "The Wakened's settlement on Moonglade's west shore: simple lodges built by "
     "transplants among tall grass and gentle hills, people sitting in the grass at dawn, a soft green-gold shimmer "
     "of the Emerald Dream in the air above the meadow, dreamlike and peaceful."),
    ("feathermoon_sentinels", "The Feathermoon Sentinels", "Feathermoon Stronghold on its island off Feralas: a night "
     "elf fortress of pale silver stone and violet roofs, crescent banners, a hippogryph roost, a Sentinel boat "
     "crossing the grey-green sea, giant trees on the mainland behind, moonrise."),
    ("highbough_tribes", "The Highbough Tribes", "The Great Settlement in the heart of the World Tree: a lantern-lit "
     "jungle troll city on bridges between giant trunks, pagoda-like roofs with upturned eaves in red, teal and gold, "
     "waterfalls falling through the city from the branches above, rope lifts, warm gold light."),
    ("aetherians", "The Aetherians", "Aurelion, the Aetherian capital above the clouds: a white-marble and gold city "
     "of soaring spires with blue crystal windows and wing-like fins, rings of floating stone, districts on floating "
     "islands pouring waterfalls into a golden cloud sea, elegant airships, a huge golden sun low on the horizon."),
    ("kyrvahl", "Kyr'vahl, the Last Updraft", "The Talon Spires: impossibly tall dark stone spires rising from a "
     "storm-cloud sea, a Veyr clan city carved into them and built across a giant stone arch, great woven nests, red "
     "and gold banners whipping in the wind, avian warriors diving, lightning striking a copper-crowned temple."),
    ("ulkharad", "Ul'Kharad, the First Stone", "The Elder Citadels: a massive floating citadel of cloud-white marble "
     "and grey granite in a cold clear sky, colossal statues of giant ancestors, suspended bridges on great chains, "
     "a gravity stone floating in a cradle, cloud giants walking a bridge, tiny against their works."),
]


def render():
    out = ["# Faction card backgrounds: art prompts", "",
           "**Status (21 Nov 2026): delivered and sliced.** The Sunreach Conclave's card is to be redrawn at its new "
           "home, as Dawnhaven's DH5 (`docs/dawnhaven_art_prompts.md`). See `docs/art_status.md` for every sheet.", "",
           "Written by `tools/write_faction_art_prompts.py` (edit the script, not this file).", "",
           "Kyle, 19 Nov 2026: background art for each faction's card, then \"like a 'background card' but on the faction "
           "page, very opaque and unique for each one\". So each faction's page is backed by its own painting, drawn "
           "solid (not a faint wash), with the page's text on a darker band over the painting's calm lower third. One "
           "landscape per faction, four to a sheet, each panel 1024x768. The secret faction "
           "gets none: its card says nothing on purpose. The three sky factions are drawn ahead of their zones.", "",
           "| Sheet | Panels |", "|---|---|"]
    sheets = [PANELS[i:i + 4] for i in range(0, len(PANELS), 4)]
    for n, sh in enumerate(sheets, 1):
        out.append(f"| FC{n} | " + ", ".join(p[1] for p in sh) + " |")
    out += ["", "Slice to `assets/ui/factions/bg_<faction id>.png` (the ids below).", ""]
    for n, sh in enumerate(sheets, 1):
        out += ["---", "", f"## SHEET FC{n}: " + ", ".join(p[1] for p in sh), "", "```"]
        if len(sh) == 4:
            out.append(HEAD)
            out += ["", "Panels, left to right, top to bottom:", ""]
            out.append("; ".join(f"{i} {p[1].upper()}: {p[2]}" for i, p in enumerate(sh, 1)))
        else:
            out.append("Generate ONE landscape painting, 1024x768. " + HEAD.split("\n\n", 1)[1].replace(
                "Each panel is the faction's", "It is the faction's").replace("each panel", "the painting")
                .replace("upper two-thirds of each panel", "upper two-thirds") + "\n\n" +
                "Painterly semi-realistic fantasy art in the style of World of Warcraft loading screens, no text, no "
                "letters, no logos, no border.\n\n" + f"{sh[0][1].upper()}: {sh[0][2]}")
        out += ["```", "", "Slice order: " + ", ".join(f"`bg_{p[0]}`" for p in sh), ""]
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    OUT.write_text(render(), encoding="utf-8")
    print(f"{len(PANELS)} factions -> {OUT.relative_to(ROOT)}")
