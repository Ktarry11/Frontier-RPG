"""
TalentNode - represents a single talent in a talent tree.
Talents are hex nodes that can be connected, ranked, and have costs.
"""

#: Effect keys that are a fixed configuration constant rather than a
#: real per-rank bonus, even when they live inside a multi-rank node's
#: `effects` dict alongside one. get_effective_effects() (below) passes
#: these through at their raw authored value regardless of points_spent,
#: instead of multiplying by rank count like every other numeric effect.
#: low_health_threshold_pct is the first real case: Venomancer's
#: Unbreakable and Tinker's Emergency Coolant each pair a genuine
#: per-rank "-2%/rank damage taken" bonus with a FIXED "while below
#: X% health" trigger condition that must stay the same number whether
#: 1 or 3 ranks are spent.
UNSCALED_EFFECT_KEYS = frozenset({"low_health_threshold_pct"})


class TalentNode:
    """A single talent node in a talent tree."""
    
    def __init__(self, talent_id, name, description, node_type, tier, 
                 max_points, cost_per_point, hex_x, hex_y, 
                 effects=None, connected_to=None, proc=None, require_form=None, **kwargs):
        """
        Args:
            talent_id: unique identifier (e.g., "warrior_arms_1")
            name: display name
            description: flavor text
            node_type: "passive" | "active" (for ability talents)
            tier: which tier of the tree (0 = top, gated by tier requirements)
            max_points: max ranks (1 = single talent, 3 = multi-rank)
            cost_per_point: how many talent points per rank
            hex_x, hex_y: position in hex grid (for rendering)
            effects: dict of stat effects (e.g., {"strength": 5, "attack_power": 10})
            connected_to: list of talent_ids this connects to
            proc: optional reactive-proc payload (same schema as StatusEffect.proc
                  in combat/status_effects.py: trigger/chance/icd + one of
                  grant_resource/bonus_pct/apply_effect/extra_attack). A talent
                  carrying this gets a permanent synthetic StatusEffect applied
                  to the character whenever this node has points_spent > 0 -
                  see Character._sync_talent_procs(). None (the default, and
                  every talent authored before this existed) means this node
                  is purely a passive stat contribution via `effects`, exactly
                  as before - this is additive, not a replacement for effects
                  (a talent can have BOTH a flat stat_mods-equivalent effect
                  AND a proc, e.g. Shamanistic Rage's real Armor bonus plus a
                  real on-hit mana-return proc).
        """
        self.talent_id = talent_id
        self.name = name
        self.description = description
        self.node_type = node_type  # "passive" or "active"
        self.tier = tier
        self.max_points = max_points
        self.cost_per_point = cost_per_point
        self.hex_x = hex_x
        self.hex_y = hex_y
        self.effects = effects or {}
        self.connected_to = connected_to or []
        self.proc = proc or None

        #: Shapeshift form id this talent's `effects` only apply in (see
        #: combat/forms.py - "cat", "bear", "beetle", "vizier_form", ...).
        #: None means always-on, which is every talent authored before this
        #: existed, so nothing changes for them.
        #:
        #: This mirrors the proc system's own require_form (see
        #: combat/status_effects.py), which already gated REACTIVE talents on
        #: the carrier's current form - Venomancer's Spider Lord is cited in
        #: its comments. PASSIVE talent effects had no equivalent, which is
        #: why Character.get_talent_effects had to hardcode a bespoke branch
        #: for Shaman Tank's Earthen Attunement, noting that "that path has no
        #: concept of 'conditional on X'". It does now.
        self.require_form = require_form

        # Runtime state
        self.points_spent = 0  # How many ranks the player has in this talent
    
    def can_spend_point(self):
        """Check if this talent can be ranked up."""
        return self.points_spent < self.max_points
    
    def spend_point(self):
        """Add a rank to this talent. Returns True if successful."""
        if self.can_spend_point():
            self.points_spent += 1
            return True
        return False
    
    def refund_point(self):
        """Remove a rank from this talent. Returns True if successful."""
        if self.points_spent > 0:
            self.points_spent -= 1
            return True
        return False
    
    def reset(self):
        """Reset this talent to 0 points."""
        self.points_spent = 0
    
    def get_effective_effects(self):
        """
        Return the effects scaled by current ranks.

        Effect values in JSON are defined PER RANK, matching how WoW talent
        tooltips read ("+5% crit chance per rank"). So the total is
        value * points_spent, NOT value * (points_spent / max_points).

        The old formula divided by max_points, which meant a fully-maxed 5/5
        talent granted exactly one rank's worth of its effect - every
        multi-rank talent in the game was silently divided by its own max
        rank. Fixed here; JSON effect values are unchanged and now mean what
        their descriptions always claimed.

        Non-numeric effect values (e.g. "unlock_ability": "bladestorm") pass
        through unscaled as long as at least one point is spent.
        """
        if self.points_spent == 0 or not self.effects:
            return {}

        scale = self.points_spent
        scaled = {}
        for key, value in self.effects.items():
            if isinstance(value, (int, float)) and key not in UNSCALED_EFFECT_KEYS:
                scaled[key] = value * scale
            else:
                # Non-numeric values (descriptions, unlock_ability, etc) AND
                # UNSCALED_EFFECT_KEYS both pass through at their raw value
                # regardless of rank. UNSCALED_EFFECT_KEYS exists for a real
                # configuration-constant effect that happens to share a
                # node with a genuine per-rank bonus (Venomancer's
                # Unbreakable, Tinker's Emergency Coolant: "low_health_
                # damage_reduction_pct": 0.02 [a real per-rank bonus] PLUS
                # "low_health_threshold_pct": 0.35 [a FIXED trigger
                # condition, "while below 35% health" - the same number no
                # matter how many of the node's ranks are spent]). Before
                # this existed, every numeric key in a node's effects dict
                # was multiplied by points_spent unconditionally, so a
                # 3-rank Unbreakable silently inflated its own 35% HP
                # threshold to 105% HP (i.e. "always active"), a real bug
                # caught via direct testing rather than assumed away.
                scaled[key] = value
        return scaled
    
    def to_dict(self):
        """Serialize for save/load."""
        return {
            "talent_id": self.talent_id,
            "name": self.name,
            "description": self.description,
            "node_type": self.node_type,
            "tier": self.tier,
            "max_points": self.max_points,
            "cost_per_point": self.cost_per_point,
            "hex_x": self.hex_x,
            "hex_y": self.hex_y,
            "effects": self.effects,
            "connected_to": self.connected_to,
            "proc": self.proc,
            "require_form": self.require_form,
            "points_spent": self.points_spent,
        }
    
    @staticmethod
    def from_dict(data):
        """Deserialize from dict."""
        node = TalentNode(
            data["talent_id"],
            data["name"],
            data["description"],
            data["node_type"],
            data["tier"],
            data["max_points"],
            data["cost_per_point"],
            data["hex_x"],
            data["hex_y"],
            data.get("effects", {}),
            data.get("connected_to", []),
            data.get("proc"),
            data.get("require_form"),
        )
        node.points_spent = data.get("points_spent", 0)
        return node
    
    def __repr__(self):
        return f"<TalentNode {self.name} ({self.points_spent}/{self.max_points})>"
