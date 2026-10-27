"""
TalentTree - represents one specialization's talent tree (hex grid with tier gating).
E.g., Warrior Arms, Shaman Elemental, etc.
"""
from entities.talent_node import TalentNode


class TalentTree:
    """A single talent tree for a spec (e.g., Warrior Arms)."""
    
    def __init__(self, spec_name, tree_id, description=""):
        """
        Args:
            spec_name: display name (e.g., "Warrior Arms")
            tree_id: unique identifier (e.g., "warrior_arms")
            description: flavor text
        """
        self.spec_name = spec_name
        self.tree_id = tree_id
        self.description = description
        
        # Tree structure
        self.nodes = {}  # talent_id -> TalentNode
        self.nodes_by_tier = {}  # tier -> list of TalentNode ids in that tier
        
        # Gating (how many points needed to unlock each tier)
        self.tier_requirements = {}  # tier -> required_points_in_tree
    
    def add_node(self, node):
        """Add a talent node to the tree."""
        if node.talent_id in self.nodes:
            print(f"WARNING: Talent {node.talent_id} already exists, replacing")
        
        self.nodes[node.talent_id] = node
        
        # Index by tier
        if node.tier not in self.nodes_by_tier:
            self.nodes_by_tier[node.tier] = []
        self.nodes_by_tier[node.tier].append(node.talent_id)
    
    def set_tier_requirement(self, tier, required_points):
        """
        Set how many points must be spent in the tree to unlock a tier.
        E.g., tier_requirement[1] = 5 means you need 5 points spent before accessing tier 1.
        """
        self.tier_requirements[tier] = required_points
    
    def can_spend_in_tier(self, tier, total_points_spent):
        """Check if player can spend points in a given tier based on gating."""
        required = self.tier_requirements.get(tier, 0)
        return total_points_spent >= required
    
    def get_node(self, talent_id):
        """Get a node by ID."""
        return self.nodes.get(talent_id)
    
    def get_nodes_in_tier(self, tier):
        """Get all nodes in a tier."""
        node_ids = self.nodes_by_tier.get(tier, [])
        return [self.nodes[nid] for nid in node_ids]
    
    def get_max_tier(self):
        """Return the deepest tier in this tree."""
        if not self.nodes_by_tier:
            return 0
        return max(self.nodes_by_tier.keys())
    
    def total_points_spent(self):
        """Count total talent points spent in this tree."""
        return sum(node.points_spent for node in self.nodes.values())
    
    def get_total_effects(self, active_form=None):
        """
        Return the combined effects of all talents at their current ranks.
        Returns dict like {'strength': 15, 'attack_power': 50, ...}

        active_form: the character's current shapeshift form id, or None.
        A node carrying require_form only contributes while that form is
        active - Druid's Cat Form mastery should do nothing in Bear Form.
        Nodes without require_form (all of them, before this existed) are
        unaffected, so passing nothing keeps the old behaviour exactly.

        Non-numeric values (currently just "unlock_ability": "<ability_id>",
        see TalentNode.get_effective_effects) collect into a list per key
        instead of being summed - `+=` on a string blew up the instant any
        talent used this, which Character.get_talent_effects() already
        correctly anticipated at the character level but this tree-level
        aggregator never did, so it crashed before that logic ever ran.
        """
        total_effects = {}
        for node in self.nodes.values():
            required = getattr(node, "require_form", None)
            if required and required != active_form:
                continue
            effects = node.get_effective_effects()
            for key, value in effects.items():
                if isinstance(value, (int, float)):
                    total_effects[key] = total_effects.get(key, 0) + value
                else:
                    total_effects.setdefault(key, [])
                    if isinstance(total_effects[key], list) and value not in total_effects[key]:
                        total_effects[key].append(value)
        return total_effects
    
    def reset_all(self):
        """Reset all talents in this tree to 0 points."""
        for node in self.nodes.values():
            node.reset()
    
    def to_dict(self):
        """Serialize for save/load."""
        return {
            "spec_name": self.spec_name,
            "tree_id": self.tree_id,
            "description": self.description,
            "nodes": {nid: node.to_dict() for nid, node in self.nodes.items()},
            "tier_requirements": self.tier_requirements,
        }
    
    @staticmethod
    def from_dict(data):
        """Deserialize from dict."""
        tree = TalentTree(data["spec_name"], data["tree_id"], data.get("description", ""))
        
        # Restore nodes
        for talent_id, node_data in data.get("nodes", {}).items():
            node = TalentNode.from_dict(node_data)
            tree.add_node(node)
        
        # Restore tier requirements
        tier_reqs = data.get("tier_requirements", {})
        # Convert string keys to ints (JSON serialization converts to strings)
        for tier_str, required in tier_reqs.items():
            tree.set_tier_requirement(int(tier_str), required)
        
        return tree
    
    def __repr__(self):
        total = self.total_points_spent()
        return f"<TalentTree {self.spec_name} ({total} points spent, {len(self.nodes)} talents)>"
