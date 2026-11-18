"""Colourways for the Collection's mounts, made from the mounts the game already has (docs/collection_design.md).

Kyle, 18 Nov 2026, picking what to mass-produce: "Creature forms, Mount colours, Titles". Then, on the first try (a
full recolour): "don't full colour shift mounts. Hue shift them. And I'll get art." So each colourway turns the hue
wheel by a fixed amount and keeps the art's own saturation and light. A grey wolf stays mostly grey (there's little
hue to turn), and its saddle, eyes and trappings take the new colour; Kyle's own art replaces these later.

They're made when first drawn (ui/sprite_loader.get_mount_sprite), not stored: 336 more images in the repo would be
tens of MB of the same twelve animals.
"""
from PIL import Image

BASE_MOUNTS = ["timber_wolf", "dire_wolf", "brown_kodo", "war_kodo", "razormane_raptor", "swift_raptor",
               "mire_hopper", "crag_lizard", "carrion_horse", "rune_saber", "plaguebone_charger", "veinlit_strider"]

#: colourway -> degrees the hue wheel turns
HUE_SHIFTS = {"rose": -30, "dawn": 30, "spring": 90, "jade": 150, "tide": 190, "dusk": 240, "twilight": 285}
#: kept for anything that imports the old name
COLOURWAYS = HUE_SHIFTS


def hue_shift(im, degrees):
    """A PIL image with its hue turned by `degrees`, saturation, brightness and alpha untouched."""
    im = im.convert("RGBA")
    alpha = im.getchannel("A")
    h, s, v = im.convert("RGB").convert("HSV").split()
    turn = int(round(degrees / 360.0 * 256)) % 256
    h = h.point(lambda x: (x + turn) % 256)
    out = Image.merge("HSV", (h, s, v)).convert("RGB")
    out.putalpha(alpha)
    return out


def colorize(im, colourway):
    """The mount picture in one of HUE_SHIFTS' colourways."""
    return hue_shift(im, HUE_SHIFTS[colourway])


def split_colourway(mount_id):
    """("rose", "timber_wolf") for "rose_timber_wolf", or None."""
    for colour in HUE_SHIFTS:
        if mount_id and mount_id.startswith(colour + "_") and mount_id[len(colour) + 1:] in BASE_MOUNTS:
            return colour, mount_id[len(colour) + 1:]
    return None
