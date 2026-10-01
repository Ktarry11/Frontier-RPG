"""
TalentManager - loads and manages all talent trees for all specs.
Parallel to CreatureManager and ConsumableManager.
"""
import json
from pathlib import Path
from entities.talent_tree import TalentTree
from entities.talent_node import TalentNode


class TalentManager:
    """Manages all talent trees for all classes and specs."""
    
    def __init__(self):
        """Load all talent trees from data/talents/."""
        self.trees = {}  # tree_id -> TalentTree
        self._load_all_trees()
    
    def _load_all_trees(self):
        """Load all JSON talent tree files from data/talents/."""
        talents_dir = Path(__file__).parent.parent / "data" / "talents"
        
        if not talents_dir.exists():
            print(f"WARNING: Talents directory not found at {talents_dir}")
            return
        
        # Load all .json files in the talents directory
        for json_file in talents_dir.glob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                # Each JSON file contains one talent tree
                tree = self._parse_tree_data(data)
                if tree:
                    self.trees[tree.tree_id] = tree
                    print(f"Loaded talent tree: {tree.spec_name}")
            
            except json.JSONDecodeError as e:
                print(f"ERROR: Failed to parse {json_file}: {e}")
            except Exception as e:
                print(f"ERROR: Failed to load {json_file}: {e}")
    
    def _parse_tree_data(self, data):
        """Parse a talent tree from JSON data."""
        try:
            tree = TalentTree(
                data["spec_name"],
                data["tree_id"],
                data.get("description", "")
            )
            
            # Add nodes
            for node_data in data.get("nodes", []):
                node = TalentNode(
                    node_data["talent_id"],
                    node_data["name"],
                    node_data["description"],
                    node_data.get("node_type", "passive"),
                    node_data["tier"],
                    node_data.get("max_points", 1),
                    node_data.get("cost_per_point", 1),
                    node_data["hex_x"],
                    node_data["hex_y"],
                    node_data.get("effects", {}),
                    node_data.get("connected_to", []),
                    node_data.get("proc"),
                )
                tree.add_node(node)
            
            # Set tier requirements
            for tier_str, required in data.get("tier_requirements", {}).items():
                tree.set_tier_requirement(int(tier_str), required)
            
            return tree
        
        except KeyError as e:
            print(f"ERROR: Missing required field in talent tree JSON: {e}")
            return None
    
    def get_tree(self, tree_id):
        """Get a talent tree by ID."""
        return self.trees.get(tree_id)
    
    def get_trees_for_class(self, class_name):
        """
        Get all talent trees for a class.
        E.g., get_trees_for_class("Warrior") returns [Arms, Fury, Protection trees]
        """
        class_lower = class_name.lower()
        return {
            tree_id: tree 
            for tree_id, tree in self.trees.items() 
            if tree.tree_id.startswith(class_lower + "_")
        }
    
    def get_all_trees(self):
        """Get all talent trees."""
        return self.trees
    
    def get_tree_ids(self):
        """Get list of all tree IDs."""
        return list(self.trees.keys())


# Global singleton
_talent_manager = None

def get_talent_manager():
    """Get or create the global TalentManager instance."""
    global _talent_manager
    if _talent_manager is None:
        _talent_manager = TalentManager()
    return _talent_manager
