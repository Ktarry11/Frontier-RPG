"""
Faction reputation.

Frontier's first faction is the Crimson Codex (Kyle, 2026-10-27: "factions are to start being introduced").
This module is the whole engine: standing per faction, tiers, the two earn hooks, and the gates other
systems ask it about. Everything the Codex specifically is lives in data/factions/factions.json, so a
second faction is a block of data and no code at all.

ONE LADDER FOR EVERY FACTION (Kyle, 2026-10-27: "keep the wow tiers of rep... there will be a lot"). The
eight WoW-standard tiers - Hated through Exalted - are defined once in the data file and shared by every
faction. A faction never carries its own scale. That is what lets one UI tab list fifty factions on the
same bar, and it means adding a faction is a block of data and no code.

WHERE REPUTATION COMES FROM, AND WHY IT IS NOT "DUNGEON MOBS"

Kyle asked for quests and maybe dungeon kills. Quests, yes - all 48 in the cluster, and together they land
you comfortably past Bound, which is the second-highest tier. That is the real path and it is the one that
tells the story.

Kills are deliberately NARROWER than "anything in a dungeon". A flat dungeon rule makes the optimal play
farming the easiest trash in the easiest room, which is the WoW rep grind and is mindless; it also pays you
Codex standing for killing a mushroom. So kill rep comes only from enemies the faction has an actual stake
in. The wildlife pays nothing however deep the cave it lives in.

DUNGEON BOSSES ARE THE THIRD SOURCE, AND THE ONLY ONE THAT REPEATS (Kyle, 2026-10-28: "A dungeon boss kill
should be 75 each in the Dungeons linked to that faction"). A faction lists the dungeons it cares about in
`dungeon_rep.dungeons`, and every BOSS killed in one of them pays `dungeon_rep.per_boss`. Trash in the same
room pays nothing, which is the point - the unit of progress is a boss, so the optimal play is to run the
dungeon rather than to farm a corridor.

THE THREE SOURCES DO DIFFERENT JOBS, and the quest band is what sets the pace. Kyle, 2026-10-28: "reaching
max rep should take time too. Most quests should give 150-250 rep. Even with the codex." So every quest in
the game now pays inside that band - boss quests at the top of it, ordinary ones below - and no faction
reaches Exalted on quests alone unless it genuinely owns hundreds of them. Everything else finishes in the
dungeons, repeatedly, with a party, which is what dungeons are for in this game.

NEGATIVE STANDING IS DEFINED BUT UNUSED. Unfriendly, Hostile and Hated exist on the ladder because the
first faction that can be angered should not have to rewrite the scale. Nothing currently drives standing
down, and award() refuses negative amounts until something is designed to.

PERSISTENCE. Standing round-trips through the save's "factions" block (SAVE_VERSION 9). Like every other
block it is optional, so a v8 save loads with everybody Unlisted - which is the correct starting state
anyway, so there is no migration to write.
"""
import json
from pathlib import Path

DATA = Path(__file__).parent.parent / "data" / "factions" / "factions.json"


def _zkey(zone):
    """The normalization every zone-keyed lookup in this codebase uses - lowercase, spaces to
    underscores, apostrophes dropped. Used here so "The Deep Bloom", "the_deep_bloom" and
    "Grom's Rest" / "groms_rest" all resolve to the same dungeon."""
    return str(zone).lower().replace(" ", "_").replace("'", "")


class Faction:
    """One faction's authored definition plus the player's standing in it."""

    def __init__(self, faction_id, d, tiers):
        self.faction_id = faction_id
        self.name = d["name"]
        self.description = d.get("description", "")
        self.home_zone = d.get("home_zone")
        #: THE SHARED LADDER, ascending. Every faction gets the same list object - a faction does not own
        #: a scale, which is the whole point of the restructure.
        self.tiers = tiers
        self.home_name = d.get("home_name", "")
        #: Shown on the detail panel. Paragraphs, authored, never generated from the mechanical data.
        self.lore = d.get("lore", [])
        #: {title, name, npc_id, location, line} - who runs this faction. Shown on the detail panel.
        self.leader = d.get("leader", {})
        self.quest_rep = d.get("quest_rep", {})
        self.kill_rep = d.get("kill_rep", {}).get("creatures", {})
        #: {"per_boss": int, "dungeons": [...]}. Dungeon names are stored BOTH as authored and normalized,
        #: because combat passes whatever zone key it was constructed with and the data file is written in
        #: display names ("The Deep Bloom"). Matching only one spelling is a silent no-pay.
        dr = d.get("dungeon_rep", {})
        self.dungeon_per_boss = int(dr.get("per_boss", 0))
        self.dungeons = {_zkey(z) for z in dr.get("dungeons", [])}
        self.rewards = d.get("rewards", {})
        self.standing = 0

    # ---------------------------------------------------------------- tiers
    @property
    def tier(self):
        """The highest tier whose threshold the player has reached.

        Starts at the FLOOR of the ladder rather than at Neutral, so that if negative standing is ever
        driven, Hostile and Hated resolve correctly instead of clamping to the bottom entry by accident.
        """
        out = self.tiers[0]
        for t in self.tiers:
            if self.standing >= t["at"]:
                out = t
        return out

    @property
    def tier_id(self):
        return self.tier["id"]

    def tier_index(self, tier_id=None):
        tid = tier_id if tier_id is not None else self.tier_id
        for i, t in enumerate(self.tiers):
            if t["id"] == tid:
                return i
        return -1

    def at_least(self, tier_id):
        """True if standing has reached `tier_id`. The question every gate asks."""
        want = self.tier_index(tier_id)
        return want >= 0 and self.tier_index() >= want

    @property
    def next_tier(self):
        i = self.tier_index()
        return self.tiers[i + 1] if 0 <= i < len(self.tiers) - 1 else None

    def progress(self):
        """(into, span) through the CURRENT tier, for a progress bar.

        At Exalted this returns (span, span) so a bar renders full rather than empty - the natural
        (standing - at, next - at) returns (0, 0) there and a renderer dividing by span would blow up.
        """
        nxt = self.next_tier
        if nxt is None:
            i = self.tier_index()
            span = max(1, self.tier["at"] - (self.tiers[i - 1]["at"] if i > 0 else 0))
            return span, span
        base = self.tier["at"]
        return self.standing - base, max(1, nxt["at"] - base)

    def __repr__(self):
        return f"<Faction {self.faction_id} {self.standing} ({self.tier['name']})>"


class FactionManager:
    """Singleton-ish holder: see get_faction_manager()."""

    def __init__(self):
        self.factions = {}
        self.tiers = []
        #: Set by award() so the UI can say "+250 The Crimson Codex" and announce a tier change.
        #: Callers read and clear it; it is never persisted.
        self.last_gain = None
        self.last_tier_up = None
        self._load()

    def _load(self):
        if not DATA.exists():
            return
        d = json.loads(DATA.read_text(encoding="utf-8"))
        #: One ladder, shared. Sorted here so the data file can list tiers in any order.
        self.tiers = sorted(d.get("tiers", []), key=lambda t: t["at"])
        for fid, fd in d.get("factions", {}).items():
            self.factions[fid] = Faction(fid, fd, self.tiers)

    # ---------------------------------------------------------------- queries
    def get(self, faction_id):
        return self.factions.get(faction_id)

    def standing(self, faction_id):
        f = self.factions.get(faction_id)
        return f.standing if f else 0

    def at_least(self, faction_id, tier_id):
        f = self.factions.get(faction_id)
        return bool(f and f.at_least(tier_id))

    def all_factions(self):
        """Every faction the UI should list, best standing first then alphabetical.

        Right now that is all of them - there is one - but the single reputation tab is going to hold a
        lot of factions, so the ordering the player reads lives here rather than in the screen.
        """
        return sorted(self.factions.values(), key=lambda f: (-f.standing, f.name))

    # ---------------------------------------------------------------- earning
    def award(self, faction_id, amount, reason=""):
        """Add standing. Returns (gained, tier_up_or_None)."""
        f = self.factions.get(faction_id)
        #: Negative awards are refused rather than silently applied: the ladder supports Hostile and Hated,
        #: but nothing in the game is designed to drive standing down yet, and a stray negative would be a
        #: very hard bug to notice.
        if f is None or amount <= 0:
            return 0, None
        before = f.tier_id
        f.standing += int(amount)
        tier_up = f.tier if f.tier_id != before else None
        self.last_gain = (faction_id, int(amount), reason)
        self.last_tier_up = (faction_id, tier_up) if tier_up else None
        return int(amount), tier_up

    def quest_reward(self, quest):
        """How much standing a quest is worth, and to whom. Returns (faction_id, amount) or (None, 0).

        Reads the quest's ZONE rather than carrying a per-quest field, so the 48 quests already written
        did not need touching and a new quest in the cluster earns Codex standing by existing. The named
        capstones and the boss rate are the only per-quest knobs.
        """
        qid = getattr(quest, "quest_id", None) or (quest.get("quest_id") if isinstance(quest, dict) else None)
        zone = getattr(quest, "zone", None) or (quest.get("zone") if isinstance(quest, dict) else None)

        # PRECEDENCE MATTERS AND USED TO BE ACCIDENTAL. A quest named explicitly - in `capstones` or in
        # `also` - beats a faction that merely owns the zone, and that has to be resolved across ALL
        # factions before any zone match is considered. Otherwise the answer depends on dict insertion
        # order: the two Hillsbrad quests that send a player down the fissure are listed by name under
        # the Crimson Codex, while the Hillsbrad ZONES belong to the Forsaken, and whichever faction
        # happened to be earlier in the file would have won.
        for fid, f in self.factions.items():
            if qid in f.quest_rep.get("capstones", {}):
                return fid, f.quest_rep["capstones"][qid]
        for fid, f in self.factions.items():
            if qid in f.quest_rep.get("also", []):
                return fid, self._shape_rate(f, quest)

        for fid, f in self.factions.items():
            qr = f.quest_rep
            if not qr:
                continue
            if zone in qr.get("zones", []):
                return fid, self._shape_rate(f, quest)
        return None, 0

    @staticmethod
    def _shape_rate(f, quest):
        """A quest's base rate: the boss rate if it kills a boss, otherwise the default.

        The rates are PER FACTION and they have to be, because factions own wildly different amounts of
        content. The Crimson Codex owns 53 quests; Orgrimmar owns the whole orc heartland and the Barrens,
        which is five times that. Paying the same per quest would take a player to Exalted with their own
        capital before leaving the starting zones.
        """
        objs = getattr(quest, "objectives", None)
        if objs is None and isinstance(quest, dict):
            objs = quest.get("objectives", [])
        is_boss = any(
            (getattr(o, "objective_type", None)
             and str(getattr(o, "objective_type")).lower().endswith("kill_boss"))
            or (isinstance(o, dict) and o.get("type") == "kill_boss")
            for o in (objs or []))
        return f.quest_rep.get("boss" if is_boss else "default", 0)

    def award_for_quest(self, quest):
        fid, amt = self.quest_reward(quest)
        if not fid or amt <= 0:
            return None, 0, None
        gained, tier_up = self.award(fid, amt, reason="quest")
        return fid, gained, tier_up

    def award_for_kill(self, creature_name, zone=None, is_boss=False):
        """Called once per defeated enemy. Most calls are a dict miss and return immediately - this runs
        inside the combat victory loop, so it stays cheap on the overwhelmingly common no-match path.

        Two sources, and a creature can qualify under both: its own entry in a faction's kill_rep, and
        the flat per-boss rate for a BOSS in a dungeon that faction is linked to. When both apply the
        LARGER wins and is paid once - a boss that a faction already named individually should not pay
        twice for being in the room it was always in.

        EVERY MATCHING FACTION IS PAID, not just the first. This used to return on the first hit, which
        quietly made a dungeon the property of whichever faction happened to be earlier in the dict - and
        that is wrong on the ground the game actually has. The Barrens is orc AND tauren country; the
        quilboar in Razorfen raid both. Wailing Caverns paying Orgrimmar and nothing to Thunder Bluff was
        an artefact of iteration order, not a design decision anybody made.

        Returns a list of (faction_id, gained, tier_up).
        """
        zk = _zkey(zone) if zone else None
        out = []
        for fid, f in self.factions.items():
            amt = f.kill_rep.get(creature_name, 0)
            if is_boss and zk and zk in f.dungeons:
                amt = max(amt, f.dungeon_per_boss)
            if amt:
                gained, tier_up = self.award(fid, amt, reason="kill")
                out.append((fid, gained, tier_up))
        return out

    # ---------------------------------------------------------------- gates
    def vendor_unlocks(self, vendor_id):
        """Extra stock this vendor offers at the player's current standing."""
        extra = []
        for f in self.factions.values():
            table = f.rewards.get("vendor_stock", {}).get(vendor_id, {})
            for tier_id, items in table.items():
                if f.at_least(tier_id):
                    extra.extend(items)
        return extra

    def quest_requirement_met(self, quest_id):
        """False only when a quest is explicitly standing-gated and the player is short."""
        for f in self.factions.values():
            need = f.rewards.get("quests", {}).get(quest_id)
            if need and not f.at_least(need):
                return False
        return True

    def recruit_requirement_met(self, recruit_id):
        for f in self.factions.values():
            r = f.rewards.get("recruit", {})
            if r.get("recruit_id") == recruit_id and not f.at_least(r.get("standing", "")):
                return False
        return True

    # ---------------------------------------------------------------- persistence
    def to_dict(self):
        return {"standing": {fid: f.standing for fid, f in self.factions.items() if f.standing}}

    def load_from_dict(self, data):
        for fid, v in (data or {}).get("standing", {}).items():
            f = self.factions.get(fid)
            if f:
                f.standing = int(v)

    def reset(self):
        for f in self.factions.values():
            f.standing = 0
        self.last_gain = self.last_tier_up = None


_faction_manager = None


def get_faction_manager():
    """Module-level singleton, same access pattern as world.quest_manager.get_quest_manager()."""
    global _faction_manager
    if _faction_manager is None:
        _faction_manager = FactionManager()
    return _faction_manager


def reset_faction_manager():
    """Fresh reputation for a new character / before applying a loaded save.

    Same process-lifetime singleton hazard as the recruit manager, and it
    reaches the same place: `rewards.recruit` in factions.json reserves
    companions behind a standing, and `RecruitNPC._faction_gate_met` asks
    this manager. One character's reputation deciding another character's
    gates is wrong on its own; silently unlocking or hiding a companion is
    how it would actually be noticed.
    """
    global _faction_manager
    _faction_manager = FactionManager()
    return _faction_manager
