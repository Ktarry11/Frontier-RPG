"""Cutscenes: the shots, where they trigger, and who has seen them. The game's first is the Crown (docs/crown_cutscene.md).

Kyle, 20 Nov 2026: "at the end of the ascent there is a mural, and when we get close it triggers. The mural has the 3
races on it, we go to touch it and it crumbles. Golden light floods into the room and we step out onto the crown of the
world tree and look over, we see a tiny STV as we are so high up, then we turn and see the countless islands and the
capital city."

HOW IT RUNS. A cutscene has its shots (ui/screens/cutscene_screen.py plays them), the tiles that trigger it, and where it
puts you when it ends. ZoneManager.move_player asks on_step() after every step; the first time a character steps on a
trigger tile the cutscene is marked seen (saved with the character, like found secrets) and handed to the overworld,
which plays it. Escape skips.

WHERE IT ENDS. The Crown's cutscene ends on the Sunward Crown, at the Mural Gate (tools/handbuilt_worldtree_sunward_
crown.py). After that the broken mural is the way through, both ways.

PROPS THAT CHANGE. A landmark can carry "cutscene_hide" (drawn until a cutscene is seen) or "cutscene_show" (drawn only
after): the Cloudbreak's mural, whole and then broken open (ui/tilemap_renderer.py asks shown()).
"""

#: cutscene id -> its shots and where it leaves you. A shot: (image, seconds, start rect, end rect, extras), the rects
#: being the part of the painting on screen as (x, y, w, h) fractions; extras: "shake", "flood_in" (light floods to white
#: over the end of the shot), "flood_out" (white fades down from the start), "text".
CS = "assets/ui/cutscenes/crown/"
CUTSCENES = {
    "crown": dict(
        shots=[
            (CS + "cs1_chamber.png", 4.0, (0.0, 0.0, 1.0, 1.0), (0.08, 0.06, 0.84, 0.84), {}),
            (CS + "cs2_touch.png", 3.0, (0.04, 0.04, 0.92, 0.92), (0.08, 0.08, 0.84, 0.84), {}),
            (CS + "cs3_crumble.png", 3.0, (0.06, 0.06, 0.88, 0.88), (0.08, 0.08, 0.84, 0.84),
             {"shake": True, "flood_in": 1.4}),
            (CS + "cs4_crown.png", 4.0, (0.05, 0.05, 0.9, 0.9), (0.0, 0.0, 1.0, 1.0), {"flood_out": 1.6}),
            (CS + "cs5_looking_down.png", 5.0, (0.1, 0.0, 0.8, 0.8), (0.1, 0.2, 0.8, 0.8), {}),
            (CS + "cs6_islands.png", 7.0, (0.0, 0.12, 0.75, 0.75), (0.25, 0.12, 0.75, 0.75), {}),
        ],
        then=("The Sunward Crown", 100, 169),         # the Mural Gate: south of the gate, facing the Lookdown
    ),
}

#: cutscene id -> the Collection keepsake that plays it again (docs/crown_cutscene.md, "Watching it again"): the account
#: learns it the first time any character sees the cutscene
KEEPSAKES = {"crown": "keepsake_mural_shard"}


def _learn_keepsake(cid, commit=True):
    kid = KEEPSAKES.get(cid)
    if not kid:
        return
    try:
        from world import collection as C
        C.grant(kid, commit=commit)
    except Exception:
        pass


#: zone -> [(cutscene id, trigger tiles)]: filled by the maps that hold them (tools/handbuilt_worldtree_cloudbreak.py)
TRIGGERS = {}


def register_trigger(zone, cutscene, tiles):
    TRIGGERS.setdefault(zone, []).append((cutscene, set(map(tuple, tiles))))


class CutsceneManager:
    def __init__(self):
        self.seen = set()
        self.pending = None

    def on_step(self, zone_name, x, y):
        """The player stepped on (x, y). Returns a cutscene id the first time one of its trigger tiles is stepped on."""
        for cid, tiles in TRIGGERS.get(zone_name, ()):
            if (x, y) in tiles and cid not in self.seen:
                self.seen.add(cid)
                _learn_keepsake(cid)
                return cid
        return None

    def shown(self, lm):
        hide = lm.get("cutscene_hide")
        if hide and hide in self.seen:
            return False
        show = lm.get("cutscene_show")
        return not show or show in self.seen

    def destination(self, cid, zones):
        """(zone, x, y) to put the player when the cutscene ends, or None to leave them where they are."""
        to, x, y = CUTSCENES[cid].get("then") or (None, None, None)
        if not to or to not in zones:
            return None
        if x is None:
            try:
                from world.portal_manager import get_portal_manager
                arr = getattr(get_portal_manager(), "arrival_for", None)
                spot = arr(to) if arr else None
            except Exception:
                spot = None
            if not spot:
                return None
            x, y = spot
        return (to, x, y)

    # ------------------------------------------------------------------ save
    def to_dict(self):
        return {"seen": sorted(self.seen)}

    def load_dict(self, data):
        self.seen = set((data or {}).get("seen") or [])
        self.pending = None
        for cid in self.seen:              # a character who saw it before the keepsake existed still earns it
            _learn_keepsake(cid, commit=False)


_cutscenes = None


def get_cutscenes():
    global _cutscenes
    if _cutscenes is None:
        _cutscenes = CutsceneManager()
    return _cutscenes
