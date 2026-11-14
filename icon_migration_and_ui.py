"""
Icon System Migration and UI Integration
Handles schema updates and provides UI rendering utilities
"""

import json
from pathlib import Path
from typing import Optional, Dict, Tuple
from icon_system_core import IconRegistry, IconRenderer, IconSpec


class IconDataMigration:
    """
    Migrates existing ability/item data to include icon_id fields.
    Uses pattern matching and sensible defaults.
    """

    # Patterns to match in ability names for icon assignment
    ABILITY_ICON_PATTERNS = {
        # Healing
        "heal": "ability_heal",
        "restoration": "ability_heal",
        "holy light": "ability_heal",
        "renew": "ability_heal",
        
        # Protection/Buffs
        "shield": "ability_buff",
        "buff": "ability_buff",
        "shout": "ability_buff",
        "totem": "ability_buff",
        "blessing": "ability_buff",
        "aura": "ability_buff",
        "power": "ability_buff",
        
        # DoTs/Bleeds
        "dot": "ability_dot",
        "poison": "ability_dot",
        "bleed": "ability_dot",
        "wound": "ability_dot",
        "drain": "ability_dot",
        "fire": "ability_dot",
        "burn": "ability_dot",
        "rend": "ability_dot",
        
        # Melee/Physical
        "strike": "ability_melee",
        "attack": "ability_melee",
        "slash": "ability_melee",
        "swing": "ability_melee",
        "backstab": "ability_melee",
        "overpower": "ability_melee",
        "crush": "ability_melee",
        
        # Spells/Magic
        "bolt": "ability_spell",
        "ball": "ability_spell",
        "blast": "ability_spell",
        "smite": "ability_spell",
        "wrath": "ability_spell",
        "fireball": "ability_spell",
        "frostbolt": "ability_spell",
        "shadowbolt": "ability_spell",
        "spell": "ability_spell",
        
        # Debuffs/Control
        "stun": "ability_debuff",
        "slow": "ability_debuff",
        "freeze": "ability_debuff",
        "root": "ability_debuff",
        "silence": "ability_debuff",
        "fear": "ability_debuff",
        "taunt": "ability_debuff",
    }

    EFFECT_TYPE_ICON_MAP = {
        "damage": "ability_spell",
        "heal": "ability_heal",
        "buff": "ability_buff",
        "debuff": "ability_debuff",
        "dot": "ability_dot",
        "hot": "ability_heal",
    }

    def __init__(self, project_root: Path = Path(".")):
        self.project_root = project_root
        self.data_dir = project_root / "data"
        self.ability_dir = self.data_dir / "abilities"
        self.items_dir = self.data_dir / "items"
        self.stats = {"abilities_updated": 0, "items_updated": 0}

    def find_icon_for_ability(self, ability_name: str, effect_type: str) -> str:
        """Determine best icon_id for an ability based on name and type."""
        
        name_lower = ability_name.lower()
        
        # Try pattern matching on name
        for pattern, icon_id in self.ABILITY_ICON_PATTERNS.items():
            if pattern in name_lower:
                return icon_id
        
        # Fall back to effect_type
        return self.EFFECT_TYPE_ICON_MAP.get(effect_type, "ability_spell")

    def migrate_abilities(self, dry_run: bool = False):
        """
        Add icon_id to all abilities in data/abilities/*.json
        
        Args:
            dry_run: If True, don't write changes (just report what would change)
        """
        
        if not self.ability_dir.exists():
            print(f"Ability directory not found: {self.ability_dir}")
            return
        
        for ability_file in sorted(self.ability_dir.glob("*.json")):
            with open(ability_file, 'r', encoding="utf-8") as f:
                data = json.load(f)
            
            updated_count = 0
            for ability in data.get("abilities", []):
                if "icon_id" not in ability:
                    icon_id = self.find_icon_for_ability(
                        ability.get("name", ""),
                        ability.get("effect_type", "damage")
                    )
                    ability["icon_id"] = icon_id
                    updated_count += 1
            
            if updated_count > 0:
                print(f"  {ability_file.name}: {updated_count} abilities updated")
                self.stats["abilities_updated"] += updated_count
                
                if not dry_run:
                    with open(ability_file, 'w', encoding="utf-8") as f:
                        json.dump(data, f, indent=2)

    def migrate_items(self, dry_run: bool = False):
        """
        Add icon_id to items based on rarity and type.
        (Simplified; can be expanded based on actual item structure)
        """
        
        if not self.items_dir.exists():
            print(f"Items directory not found: {self.items_dir}")
            return
        
        rarity_icon_map = {
            "common": "rarity_common",
            "uncommon": "rarity_uncommon",
            "rare": "rarity_rare",
            "epic": "rarity_epic",
            "legendary": "rarity_legendary",
        }
        
        for item_file in sorted(self.items_dir.glob("*.json")):
            try:
                with open(item_file, 'r', encoding="utf-8") as f:
                    data = json.load(f)
            except:
                continue
            
            updated_count = 0
            
            # Handle different item file structures
            if "items" in data:
                # Direct items array
                for item in data["items"]:
                    if "icon_id" not in item:
                        rarity = item.get("rarity", "common")
                        icon_id = rarity_icon_map.get(rarity, "rarity_common")
                        item["icon_id"] = icon_id
                        updated_count += 1
            
            elif "armor_types" in data or "weapon_types" in data:
                # armor_types.json or weapon_types.json
                # These are category definitions, not individual items
                # So we'll add icon_id at the category level
                for category in data.get("armor_types", {}).values():
                    if "icon_id" not in category:
                        category["icon_id"] = "rarity_common"
                        updated_count += 1
                
                for weapon_type in data.get("weapon_types", {}).values():
                    if "icon_id" not in weapon_type:
                        weapon_type["icon_id"] = "rarity_common"
                        updated_count += 1
            
            if updated_count > 0:
                print(f"  {item_file.name}: {updated_count} items updated")
                self.stats["items_updated"] += updated_count
                
                if not dry_run:
                    with open(item_file, 'w', encoding="utf-8") as f:
                        json.dump(data, f, indent=2)

    def migrate_all(self, dry_run: bool = False):
        """Run all migrations."""
        print("=" * 60)
        print("ICON SYSTEM DATA MIGRATION")
        print("=" * 60)
        print()
        
        print("Migrating abilities...")
        self.migrate_abilities(dry_run=dry_run)
        
        print("\nMigrating items...")
        self.migrate_items(dry_run=dry_run)
        
        print("\n" + "=" * 60)
        print(f"Abilities updated: {self.stats['abilities_updated']}")
        print(f"Items updated: {self.stats['items_updated']}")
        
        if dry_run:
            print("\n[DRY RUN] No files were modified.")
            print("Run again with dry_run=False to apply changes.")
        else:
            print("\n✓ Migration complete!")
        print("=" * 60)


class IconUIHelper:
    """
    Helper methods for using icons in UI components.
    Integrates icon rendering into existing Pygame UI.
    """

    def __init__(self, icon_registry: IconRegistry, icon_renderer: IconRenderer):
        self.registry = icon_registry
        self.renderer = icon_renderer

    def get_ability_icon_surface(self, ability_data, size: int = 36):
        """
        Get Pygame surface for an ability.
        
        Args:
            ability_data: Either an ability dict from JSON, OR a real
                Ability instance (combat/abilities.py) - accepts both so
                callers don't have to hand-build a dict wrapper every time
                they just want to render an actual ability object's icon
                (the pattern skills_screen.py used before this).
            size: Icon size in pixels
        
        Returns:
            pygame.Surface or fallback surface
        """
        if isinstance(ability_data, dict):
            get = ability_data.get
        else:
            get = lambda k, default=None: getattr(ability_data, k, default)

        icon_id = get("icon_id")
        if not icon_id:
            # Real per-ability art (see IconRenderer.ABILITY_ICON_DIR) is
            # named after ability_id 1:1 by convention - druid_wrath.png
            # for the ability with ability_id "druid_wrath", etc. Rather
            # than hand-stamping icon_id into 79 JSON entries that would
            # just duplicate ability_id anyway, default to it here so any
            # ability dict or Ability object picks up its real icon
            # automatically.
            icon_id = get("ability_id")
        if icon_id:
            return self.renderer.get_icon_surface(icon_id, size)
        else:
            # Fallback based on effect_type
            effect_type = get("effect_type", "damage")
            fallback_icons = {
                "damage": "ability_spell",
                "heal": "ability_heal",
                "buff": "ability_buff",
                "debuff": "ability_debuff",
                "dot": "ability_dot",
            }
            fallback_id = fallback_icons.get(effect_type, "ability_spell")
            return self.renderer.get_icon_surface(fallback_id, size)

    def get_item_icon_surface(self, item_data: Dict, size: int = 36):
        """
        Get Pygame surface for an item.
        
        Args:
            item_data: Item dict from JSON
            size: Icon size in pixels
        
        Returns:
            pygame.Surface or fallback surface
        """
        icon_id = item_data.get("icon_id")
        if icon_id:
            return self.renderer.get_icon_surface(icon_id, size)
        # NO rarity_* FALLBACK. This used to map rarity -> "rarity_common",
        # "rarity_epic" and so on, which reads like a deliberate tier of
        # placeholder art. None of those five files has ever existed in any
        # searched directory, so every lookup fell straight through to
        # _make_fallback_surface - the coloured block - while the code
        # claimed otherwise. Asking for the block directly is the same
        # picture and an honest description of what happens.
        return self.renderer.get_icon_surface(
            f"__missing_{item_data.get('rarity', 'common')}", size)

    def get_class_icon_surface(self, class_name: str, size: int = 64):
        """
        Get Pygame surface for a class.
        
        Args:
            class_name: Class name (e.g., "Warrior", "Mage")
            size: Icon size in pixels
        
        Returns:
            pygame.Surface or fallback surface
        """
        # THE REAL CLASS ICONS LIVE SOMEWHERE ELSE. Kyle, 2026-10-31: "since we
        # dont have character portaits you can use the class icon" - and the
        # party roster was ALREADY asking for one here; it was getting a flat
        # blue square back.
        #
        # Two implementations of one rule, again. ui/class_portrait.py loads
        # assets/ui/class_icons/<class>.png - the authentic WoW class icons Kyle
        # specifically asked for, 30 of them on disk. This method instead asked
        # the icon registry for "class_<name>", and get_icon_surface only
        # searches the ability/talent/bag/gear/trash/quest/consumable/recipe
        # directories. Class icons are in none of them, so EVERY class fell
        # through to _make_fallback_surface and the roster drew a coloured
        # block. The real art is tried first now; the registry stays as the
        # fallback for a class with no icon file (the custom Frontier classes
        # that have no official art).
        try:
            from ui.class_portrait import get_class_icon
            icon = get_class_icon(class_name, size=size)
            if icon is not None:
                return icon
        except Exception:
            pass
        icon_id = f"class_{class_name.lower()}"
        return self.renderer.get_icon_surface(icon_id, size)

    def get_status_effect_icon_surface(self, status_effect_data: Dict, size: int = 24):
        """
        Get Pygame surface for a status effect.
        
        Args:
            status_effect_data: Status effect dict or StatusEffect object
            size: Icon size in pixels
        
        Returns:
            pygame.Surface or fallback surface
        """
        # Handle both dict and object
        if hasattr(status_effect_data, '__dict__'):
            status_effect_data = status_effect_data.__dict__
        
        icon_id = status_effect_data.get("icon_id")
        if icon_id:
            return self.renderer.get_icon_surface(icon_id, size)
        else:
            # Fallback based on effect_type
            effect_type = status_effect_data.get("effect_type", "buff")
            effect_icons = {
                "buff": "status_shield",
                "debuff": "status_poison",
                "dot": "status_poison",
                "hot": "status_shield",
            }
            fallback_id = effect_icons.get(effect_type, "status_poison")
            return self.renderer.get_icon_surface(fallback_id, size)

    def draw_icon_with_label(self, surface, icon_surface, label: str, x: int, y: int, 
                             icon_size: int = 32, font=None, color=(255, 255, 255)):
        """
        Draw an icon with a text label below it.
        
        Args:
            surface: Target pygame.Surface
            icon_surface: Icon pygame.Surface
            label: Text label
            x, y: Position
            icon_size: Size of icon area
            font: pygame.font.Font or None
            color: Text color RGB tuple
        """
        try:
            import pygame
            
            if icon_surface:
                # Scale icon if needed
                if icon_surface.get_size() != (icon_size, icon_size):
                    icon_surface = pygame.transform.scale(icon_surface, (icon_size, icon_size))
                
                surface.blit(icon_surface, (x, y))
            
            if font and label:
                text = font.render(label, True, color)
                text_rect = text.get_rect(center=(x + icon_size // 2, y + icon_size + 4))
                surface.blit(text, text_rect)
        except ImportError:
            pass


# ============ MIGRATION RUNNER ============

if __name__ == "__main__":
    import sys
    
    # Run migration
    migrator = IconDataMigration(Path("."))
    
    # First, do a dry run
    print("Running DRY RUN to show what would change...")
    print()
    migrator.migrate_all(dry_run=True)
    
    # Uncomment to actually apply changes:
    # migrator = IconDataMigration(Path("."))
    # migrator.migrate_all(dry_run=False)
