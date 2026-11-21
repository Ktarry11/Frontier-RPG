"""Links: short-range ways across a gap on the same map, with no bridge and no loading.

Kyle, 21 Nov 2026: "Can we do little short range portals that link islands instead of bridges? Like a new system", and
"If so it could open a lot of cool shit. Imagine an open sea raid where you hop boat from boat. Or this zone where all
the islands are broken and you use wind currents to move between them." And: "We can have 1 or 2 before the ff zone so
people see them a few times. But they are more heavily found later."

A link is a pair of pads on one map. Stand on a pad and press interact, the same as a portal, and you're put beside
the other pad: two tiles south of it, the way a portal's arrival works. No zone change, no loading screen. Each pad is
an interaction tile, "link", and the zone keeps them in `zone.links`:

    zone.links = {(x, y): {"to": (lx, ly), "pad": (px, py), "kind": "skipstone"}}

where (px, py) is the partner pad and (lx, ly) where you land beside it. A map module declares its pairs as

    LINKS = [("skipstone", (ax, ay), (bx, by)), ...]

and tools/ashenvale_engine.place_links lays them. Every flood-fill that asks "can you walk there" treats a pair as
joined (tools/ashenvale_engine.seal_unreachable and reachable_report, tools/qa_links.py), or the islands only a link
reaches would be sealed off as unreachable.

THE KINDS (what the player reads; the art is docs/caelora_link_art_prompts.md, sheet LK1):
  skipstone   the Aetherians' oldest links, older than Aurelion: round marble pads with a crystal at the heart
  wind        the sky's own currents: an updraft at one end, a landing at the other
  dusk_wind   the Firmament's currents, failing violet like everything there
"""

KINDS = {
    "skipstone": ("skip-stone", "The skip-stone takes you across."),
    "wind": ("wind current", "The current lifts you and sets you down across the gap."),
    "dusk_wind": ("dusk current", "The violet current carries you over the drop and sets you down on the far side."),
}

#: how far south of the partner pad you land (the same offset a portal's arrival uses)
LANDING_DY = 2


def landing_for(pad):
    return (pad[0], pad[1] + LANDING_DY)


def lay(zone, links):
    """Register a map's LINKS on its Tilemap: both pads become "link" interaction tiles, each leading to a landing beside
    the other. Returns the zone's link table."""
    table = dict(getattr(zone, "links", None) or {})
    for kind, a, b in links:
        if kind not in KINDS:
            raise ValueError(f"unknown link kind {kind!r}")
        for pad, other in ((a, b), (b, a)):
            table[tuple(pad)] = {"to": landing_for(other), "pad": tuple(other), "kind": kind}
            zone.collision_layer[pad[1]][pad[0]] = None
            zone.set_tile(pad[0], pad[1], "link", "interaction")
            lx, ly = landing_for(pad)
            zone.collision_layer[ly][lx] = None
    zone.links = table
    return table


def edges(zone):
    """Pad -> landing: the extra steps a flood-fill should take on this map."""
    return {pad: tuple(v["to"]) for pad, v in (getattr(zone, "links", None) or {}).items()}


def destination(zone, x, y):
    """(landing x, landing y, kind) for the pad at (x, y), or None."""
    v = (getattr(zone, "links", None) or {}).get((x, y))
    return (v["to"][0], v["to"][1], v["kind"]) if v else None


def message(kind):
    return KINDS.get(kind, ("link", "You're carried across."))[1]
