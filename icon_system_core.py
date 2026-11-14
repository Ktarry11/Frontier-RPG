"""
Icon Management System for Frontier RPG
Handles icon loading, caching, and rendering with fallback support
Version: 1.0 (stable, self-contained)
"""

import json
from pathlib import Path
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class IconSpec:
    """Specification for an icon."""
    icon_id: str
    display_name: str
    category: str  # "ability", "item", "class", "status_effect", "ui"
    svg_data: str  # Embedded SVG markup or path reference
    fallback_color: str  # Hex color (e.g., "#FF0000") used if SVG fails
    source: str  # "embedded", "file", "external" 
    tags: list  # e.g., ["warrior", "melee", "damage"]


class IconRegistry:
    """
    Central registry for all game icons.
    Self-contained: embeds icon data directly, no external dependencies.
    """

    def __init__(self, data_dir: Path = Path("data")):
        self.data_dir = data_dir
        self.registry: Dict[str, IconSpec] = {}
        self.cache: Dict[str, any] = {}
        
        # Load built-in icons first
        self._load_builtin_icons()
        
        # Then load from data files if they exist
        self._load_from_files()

    def _load_builtin_icons(self):
        """Load the core icon set embedded in the system."""
        builtin_icons = {
            # ============ CLASS ICONS (9 original WoW classes) ============
            "class_warrior": IconSpec(
                icon_id="class_warrior",
                display_name="Warrior",
                category="class",
                svg_data=self._get_warrior_svg(),
                fallback_color="#C79C6E",
                source="embedded",
                tags=["warrior", "melee", "tank"]
            ),
            "class_shaman": IconSpec(
                icon_id="class_shaman",
                display_name="Shaman",
                category="class",
                svg_data=self._get_shaman_svg(),
                fallback_color="#0070DD",
                source="embedded",
                tags=["shaman", "hybrid", "elemental"]
            ),
            "class_rogue": IconSpec(
                icon_id="class_rogue",
                display_name="Rogue",
                category="class",
                svg_data=self._get_rogue_svg(),
                fallback_color="#FFF468",
                source="embedded",
                tags=["rogue", "melee", "stealth"]
            ),
            "class_priest": IconSpec(
                icon_id="class_priest",
                display_name="Priest",
                category="class",
                svg_data=self._get_priest_svg(),
                fallback_color="#FFFFFF",
                source="embedded",
                tags=["priest", "caster", "healer"]
            ),
            "class_hunter": IconSpec(
                icon_id="class_hunter",
                display_name="Hunter",
                category="class",
                svg_data=self._get_hunter_svg(),
                fallback_color="#A335EE",
                source="embedded",
                tags=["hunter", "ranged", "pet"]
            ),
            "class_mage": IconSpec(
                icon_id="class_mage",
                display_name="Mage",
                category="class",
                svg_data=self._get_mage_svg(),
                fallback_color="#69CCF0",
                source="embedded",
                tags=["mage", "caster", "elemental"]
            ),
            "class_warlock": IconSpec(
                icon_id="class_warlock",
                display_name="Warlock",
                category="class",
                svg_data=self._get_warlock_svg(),
                fallback_color="#9482CA",
                source="embedded",
                tags=["warlock", "caster", "affliction"]
            ),
            "class_druid": IconSpec(
                icon_id="class_druid",
                display_name="Druid",
                category="class",
                svg_data=self._get_druid_svg(),
                fallback_color="#FF7D0A",
                source="embedded",
                tags=["druid", "hybrid", "nature"]
            ),
            "class_paladin": IconSpec(
                icon_id="class_paladin",
                display_name="Paladin",
                category="class",
                svg_data=self._get_paladin_svg(),
                fallback_color="#F58CBA",
                source="embedded",
                tags=["paladin", "hybrid", "holy"]
            ),

            # ============ COMMON ABILITY ARCHETYPES ============
            "ability_melee": IconSpec(
                icon_id="ability_melee",
                display_name="Melee Attack",
                category="ability",
                svg_data=self._get_sword_svg(),
                fallback_color="#C79C6E",
                source="embedded",
                tags=["damage", "melee", "physical"]
            ),
            "ability_spell": IconSpec(
                icon_id="ability_spell",
                display_name="Spell",
                category="ability",
                svg_data=self._get_spellball_svg(),
                fallback_color="#69CCF0",
                source="embedded",
                tags=["damage", "magic", "caster"]
            ),
            "ability_heal": IconSpec(
                icon_id="ability_heal",
                display_name="Healing",
                category="ability",
                svg_data=self._get_heal_svg(),
                fallback_color="#00FF00",
                source="embedded",
                tags=["heal", "support", "priest"]
            ),
            "ability_buff": IconSpec(
                icon_id="ability_buff",
                display_name="Buff",
                category="ability",
                svg_data=self._get_buff_svg(),
                fallback_color="#FFD700",
                source="embedded",
                tags=["buff", "support", "enhancement"]
            ),
            "ability_debuff": IconSpec(
                icon_id="ability_debuff",
                display_name="Debuff",
                category="ability",
                svg_data=self._get_debuff_svg(),
                fallback_color="#FF0000",
                source="embedded",
                tags=["debuff", "crowd_control"]
            ),
            "ability_dot": IconSpec(
                icon_id="ability_dot",
                display_name="Damage Over Time",
                category="ability",
                svg_data=self._get_poison_svg(),
                fallback_color="#9482CA",
                source="embedded",
                tags=["dot", "damage", "bleed"]
            ),

            # ============ ITEM RARITY ============
            "rarity_common": IconSpec(
                icon_id="rarity_common",
                display_name="Common",
                category="item",
                svg_data=self._get_rarity_bg("#FFFFFF"),
                fallback_color="#FFFFFF",
                source="embedded",
                tags=["common", "gray"]
            ),
            "rarity_uncommon": IconSpec(
                icon_id="rarity_uncommon",
                display_name="Uncommon",
                category="item",
                svg_data=self._get_rarity_bg("#1EFF00"),
                fallback_color="#1EFF00",
                source="embedded",
                tags=["uncommon", "green"]
            ),
            "rarity_rare": IconSpec(
                icon_id="rarity_rare",
                display_name="Rare",
                category="item",
                svg_data=self._get_rarity_bg("#0070DD"),
                fallback_color="#0070DD",
                source="embedded",
                tags=["rare", "blue"]
            ),
            "rarity_epic": IconSpec(
                icon_id="rarity_epic",
                display_name="Epic",
                category="item",
                svg_data=self._get_rarity_bg("#A335EE"),
                fallback_color="#A335EE",
                source="embedded",
                tags=["epic", "purple"]
            ),
            "rarity_legendary": IconSpec(
                icon_id="rarity_legendary",
                display_name="Legendary",
                category="item",
                svg_data=self._get_rarity_bg("#FF8000"),
                fallback_color="#FF8000",
                source="embedded",
                tags=["legendary", "orange"]
            ),

            # ============ STATUS EFFECTS ============
            "status_poison": IconSpec(
                icon_id="status_poison",
                display_name="Poison",
                category="status_effect",
                svg_data=self._get_poison_svg(),
                fallback_color="#9482CA",
                source="embedded",
                tags=["poison", "dot", "debuff"]
            ),
            "status_bleed": IconSpec(
                icon_id="status_bleed",
                display_name="Bleed",
                category="status_effect",
                svg_data=self._get_bleed_svg(),
                fallback_color="#FF0000",
                source="embedded",
                tags=["bleed", "dot", "debuff"]
            ),
            "status_stun": IconSpec(
                icon_id="status_stun",
                display_name="Stun",
                category="status_effect",
                svg_data=self._get_stun_svg(),
                fallback_color="#FFD700",
                source="embedded",
                tags=["stun", "crowd_control", "debuff"]
            ),
            "status_shield": IconSpec(
                icon_id="status_shield",
                display_name="Shield",
                category="status_effect",
                svg_data=self._get_shield_svg(),
                fallback_color="#0070DD",
                source="embedded",
                tags=["shield", "buff", "protection"]
            ),
        }

        for icon_id, icon_spec in builtin_icons.items():
            self.registry[icon_id] = icon_spec

    def _load_from_files(self):
        """Load extended icons from data files (for future custom icons)."""
        icons_file = self.data_dir / "icons.json"
        if icons_file.exists():
            try:
                with open(icons_file, 'r', encoding="utf-8") as f:
                    data = json.load(f)
                    for icon_data in data.get("icons", []):
                        spec = IconSpec(**icon_data)
                        self.registry[spec.icon_id] = spec
            except Exception as e:
                print(f"Warning: Failed to load icons from {icons_file}: {e}")

    def get_icon(self, icon_id: str) -> Optional[IconSpec]:
        """Retrieve an icon specification by ID."""
        return self.registry.get(icon_id)

    def get_icon_or_fallback(self, icon_id: str, fallback_id: str = "ability_spell") -> IconSpec:
        """Get icon by ID, or return fallback if not found."""
        return self.get_icon(icon_id) or self.get_icon(fallback_id) or list(self.registry.values())[0]

    def list_icons(self, category: Optional[str] = None, tags: Optional[list] = None) -> list:
        """List all icons, optionally filtered by category or tags."""
        results = list(self.registry.values())
        
        if category:
            results = [i for i in results if i.category == category]
        
        if tags:
            results = [i for i in results if any(t in i.tags for t in tags)]
        
        return results

    def export_registry(self, output_path: Path):
        """Export registry to JSON for inspection/distribution."""
        data = {
            "version": "1.0",
            "icons": [asdict(icon) for icon in self.registry.values()]
        }
        with open(output_path, 'w', encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    # ============ SVG GENERATORS (embedded icon definitions) ============

    @staticmethod
    def _get_warrior_svg() -> str:
        return '''<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
            <rect width="64" height="64" fill="#C79C6E" rx="4"/>
            <path d="M32 16 L42 28 L32 35 L22 28 Z" fill="#FFF" stroke="#333" stroke-width="1"/>
            <rect x="28" y="40" width="8" height="15" fill="#FFF" stroke="#333" stroke-width="1"/>
            <circle cx="32" cy="20" r="6" fill="#FFD700" stroke="#333" stroke-width="1"/>
        </svg>'''

    @staticmethod
    def _get_shaman_svg() -> str:
        return '''<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
            <circle cx="32" cy="32" r="28" fill="#0070DD" stroke="#333" stroke-width="2"/>
            <path d="M32 8 L38 18 L32 22 L26 18 Z" fill="#FFD700"/>
            <path d="M32 42 L38 52 L32 56 L26 52 Z" fill="#FFD700"/>
            <circle cx="32" cy="32" r="8" fill="#FFF"/>
        </svg>'''

    @staticmethod
    def _get_rogue_svg() -> str:
        return '''<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
            <rect width="64" height="64" fill="#FFF468" rx="4"/>
            <path d="M20 40 L32 16 L44 40 Z" fill="#333" stroke="#000" stroke-width="1"/>
            <rect x="28" y="42" width="8" height="18" fill="#333" stroke="#000" stroke-width="1"/>
            <circle cx="32" cy="26" r="4" fill="#000"/>
        </svg>'''

    @staticmethod
    def _get_priest_svg() -> str:
        return '''<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
            <rect width="64" height="64" fill="#FFFFFF" rx="4"/>
            <rect x="24" y="12" width="16" height="24" fill="#E6E6FA" stroke="#333" stroke-width="1"/>
            <circle cx="32" cy="18" r="5" fill="#E6E6FA" stroke="#333" stroke-width="1"/>
            <path d="M20 36 L32 32 L44 36 L40 52 L24 52 Z" fill="#E6E6FA" stroke="#333" stroke-width="1"/>
            <path d="M32 32 L28 42 M32 32 L36 42" stroke="#FFD700" stroke-width="2"/>
        </svg>'''

    @staticmethod
    def _get_hunter_svg() -> str:
        return '''<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
            <rect width="64" height="64" fill="#A335EE" rx="4"/>
            <path d="M16 32 L48 24 L48 40 Z" fill="#FFF" stroke="#333" stroke-width="1"/>
            <circle cx="20" cy="32" r="4" fill="#FFD700" stroke="#333" stroke-width="1"/>
            <path d="M28 48 L32 60 L36 48" fill="#8B4513" stroke="#333" stroke-width="1"/>
        </svg>'''

    @staticmethod
    def _get_mage_svg() -> str:
        return '''<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
            <rect width="64" height="64" fill="#69CCF0" rx="4"/>
            <circle cx="32" cy="20" r="6" fill="#FFF" stroke="#333" stroke-width="1"/>
            <path d="M32 26 L20 48 L44 48 Z" fill="#E0FFFF" stroke="#333" stroke-width="1"/>
            <path d="M28 40 L36 40 M26 44 L38 44" stroke="#FFD700" stroke-width="2"/>
        </svg>'''

    @staticmethod
    def _get_warlock_svg() -> str:
        return '''<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
            <rect width="64" height="64" fill="#9482CA" rx="4"/>
            <circle cx="32" cy="20" r="6" fill="#000" stroke="#333" stroke-width="1"/>
            <path d="M32 26 L18 52 L46 52 Z" fill="#4B0082" stroke="#333" stroke-width="1"/>
            <circle cx="32" cy="32" r="3" fill="#FF0000"/>
            <path d="M24 42 L40 42 M24 46 L40 46" stroke="#FF0000" stroke-width="1"/>
        </svg>'''

    @staticmethod
    def _get_druid_svg() -> str:
        return '''<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
            <rect width="64" height="64" fill="#FF7D0A" rx="4"/>
            <circle cx="32" cy="28" r="12" fill="#228B22" stroke="#333" stroke-width="1"/>
            <path d="M20 40 L44 40 L40 56 L24 56 Z" fill="#8B4513" stroke="#333" stroke-width="1"/>
            <path d="M26 24 L28 12 M32 18 L32 8 M38 24 L36 12" stroke="#228B22" stroke-width="2"/>
        </svg>'''

    @staticmethod
    def _get_paladin_svg() -> str:
        return '''<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
            <rect width="64" height="64" fill="#F58CBA" rx="4"/>
            <circle cx="32" cy="22" r="7" fill="#FFD700" stroke="#333" stroke-width="1"/>
            <rect x="24" y="32" width="16" height="20" fill="#FFF" stroke="#333" stroke-width="1" rx="2"/>
            <path d="M28 28 L28 32 M36 28 L36 32" stroke="#333" stroke-width="2"/>
            <circle cx="32" cy="40" r="3" fill="#FFD700"/>
        </svg>'''

    @staticmethod
    def _get_sword_svg() -> str:
        return '''<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
            <path d="M32 8 L35 28 L40 58 L28 58 L33 28 Z" fill="#C0C0C0" stroke="#333" stroke-width="1"/>
            <path d="M32 8 L30 28 L24 58 L36 58 L35 28 Z" fill="#A9A9A9" stroke="#333" stroke-width="1"/>
            <rect x="26" y="36" width="12" height="4" fill="#8B4513" stroke="#333" stroke-width="1"/>
        </svg>'''

    @staticmethod
    def _get_spellball_svg() -> str:
        return '''<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
            <circle cx="32" cy="32" r="20" fill="#69CCF0" stroke="#0070DD" stroke-width="2"/>
            <circle cx="32" cy="32" r="14" fill="#E0FFFF" stroke="none"/>
            <path d="M32 20 Q38 28 32 36 Q26 28 32 20" fill="#FFD700" opacity="0.7"/>
            <circle cx="32" cy="32" r="4" fill="#FFD700"/>
        </svg>'''

    @staticmethod
    def _get_heal_svg() -> str:
        return '''<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
            <circle cx="32" cy="32" r="24" fill="#00FF00" stroke="#228B22" stroke-width="2"/>
            <rect x="28" y="18" width="8" height="28" fill="#FFF" stroke="#228B22" stroke-width="1"/>
            <rect x="18" y="28" width="28" height="8" fill="#FFF" stroke="#228B22" stroke-width="1"/>
        </svg>'''

    @staticmethod
    def _get_buff_svg() -> str:
        return '''<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
            <circle cx="32" cy="32" r="26" fill="#FFD700" stroke="#DAA520" stroke-width="2"/>
            <path d="M32 12 L38 24 L50 24 L40 32 L44 44 L32 36 L20 44 L24 32 L14 24 L26 24 Z" fill="#FFF" stroke="#DAA520" stroke-width="1"/>
        </svg>'''

    @staticmethod
    def _get_debuff_svg() -> str:
        return '''<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
            <circle cx="32" cy="32" r="26" fill="#FF0000" stroke="#8B0000" stroke-width="2"/>
            <circle cx="32" cy="32" r="20" fill="none" stroke="#8B0000" stroke-width="2"/>
            <path d="M20 32 L44 32 M32 20 L32 44" stroke="#FFF" stroke-width="2"/>
        </svg>'''

    @staticmethod
    def _get_poison_svg() -> str:
        return '''<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
            <path d="M32 12 L42 20 L40 35 Q32 42 24 35 L22 20 Z" fill="#9482CA" stroke="#4B0082" stroke-width="1"/>
            <circle cx="32" cy="26" r="3" fill="#FFD700"/>
            <path d="M26 38 Q32 45 38 38" stroke="#9482CA" stroke-width="1" fill="none"/>
        </svg>'''

    @staticmethod
    def _get_bleed_svg() -> str:
        return '''<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
            <circle cx="32" cy="32" r="24" fill="#FF6B6B" stroke="#8B0000" stroke-width="2"/>
            <path d="M32 20 L36 30 L32 35 L28 30 Z" fill="#8B0000"/>
            <path d="M32 38 L36 48 L32 53 L28 48 Z" fill="#8B0000"/>
        </svg>'''

    @staticmethod
    def _get_stun_svg() -> str:
        return '''<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
            <circle cx="32" cy="32" r="26" fill="#FFD700" stroke="#DAA520" stroke-width="2"/>
            <path d="M32 14 L36 28 L50 32 L36 36 L32 50 L28 36 L14 32 L28 28 Z" fill="#DAA520" stroke="#8B7500" stroke-width="1"/>
        </svg>'''

    @staticmethod
    def _get_shield_svg() -> str:
        return '''<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
            <path d="M32 10 L48 18 L48 38 Q48 50 32 56 Q16 50 16 38 L16 18 Z" fill="#0070DD" stroke="#003D99" stroke-width="2"/>
            <path d="M32 18 L42 22 L42 38 Q42 46 32 50 Q22 46 22 38 L22 22 Z" fill="#E0FFFF" stroke="none"/>
        </svg>'''

    @staticmethod
    def _get_rarity_bg(color: str) -> str:
        return f'''<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
            <rect x="4" y="4" width="56" height="56" fill="{color}" stroke="#333" stroke-width="2" rx="4"/>
            <rect x="8" y="8" width="48" height="48" fill="none" stroke="{color}" stroke-width="1" rx="2" opacity="0.5"/>
        </svg>'''


class IconRenderer:
    """
    Renders icons to Pygame surfaces.

    REAL ART, WITH A FALLBACK
    ==========================
    get_icon_surface() used to unconditionally draw a colored square
    (see the "For now, we'll create a fallback colored surface" comment
    that used to live here) - it never actually loaded an image file, even
    though real PNGs eventually existed on disk. Every ability, in every
    screen using this system, rendered as a flat color block forever.

    79 of the 9-original-class abilities now have real cropped Blizzard
    icon art (see assets/icons/abilities/, ability_id.png - Kyle sourced
    these from in-game spellbook screenshots, matched by hand). This
    renderer now looks for that file FIRST and only falls back to the
    colored square when no real file exists - which is still correct and
    useful for the 21 not-yet-built CoA classes, so nothing crashes or
    goes blank for content that isn't ready yet.
    """

    #: Real per-ability icon art lives here, one PNG per ability_id.
    ABILITY_ICON_DIR = Path("assets/icons/abilities")

    #: Real per-talent icon art, one PNG per talent_id. Talent icons are
    #: sourced the same way as ability icons (Kyle's in-game talent-tree
    #: screenshots) and share the same lookup mechanism - get_icon_surface
    #: checks both directories, in order, since talent_id and ability_id
    #: never collide (different naming schemes: "druid_feral_ferocity"
    #: vs "druid_wrath").
    TALENT_ICON_DIR = Path("assets/icons/talents")

    #: Real per-bag-item icon art, one PNG per icon_id (e.g.
    #: "teal_satchel", "traveler_satchel" for the innate starter bag).
    #: Same lookup convention as the two dirs above - added when the bag
    #: system got real cropped bag art (Kyle's 13-bag sheet + the base
    #: starter-bag icon) rather than the flat colored rects
    #: InventoryScreen was drawing for bag slots before.
    BAG_ICON_DIR = Path("assets/icons/bags")

    #: Real armor/weapon icon art for procedurally generated gear (Kyle's
    #: WoW Vanilla/Classic Icon Pack - see gear_icons.py for the full
    #: slot/armor_type/weapon_type -> icon_id mapping). Every item
    #: LootGenerator produces now stamps a real icon_id here instead of
    #: gear rendering as a bare rarity-colored box forever.
    GEAR_ICON_DIR = Path("assets/icons/gear")

    #: Vendor trash (vt_*) and general quest item (qi_*) art, sliced from the two 48-icon sheets by
    #: tools/slice_icon_sheet.py.  Item ids resolve to these via entities/vendor_trash.py and
    #: data/items/quest_item_icons.json.
    VENDOR_TRASH_ICON_DIR = Path("assets/icons/vendor_trash")
    QUEST_ITEM_ICON_DIR = Path("assets/icons/quest_items")

    #: Potion and elixir art, sliced from the 48-icon alchemy sheet by
    #: tools/slice_icon_sheet.py. Consumables resolve to these through
    #: entities/consumable_icons.py, which maps all 68 potions/elixirs onto
    #: the 48 files (each elixir family shares a lesser and a greater bottle).
    CONSUMABLE_ICON_DIR = Path("assets/icons/consumables")
    #: Recipe scrolls. One icon per profession, reused across all 192 learnable recipes, which is
    #: how WoW does it. Before this directory existed every scroll fell through to the rarity-box
    #: fallback, because slot "recipe" has no entry in gear_icons' prefix table and never will -
    #: a scroll is not a piece of gear.
    RECIPE_ICON_DIR = Path("assets/icons/recipes")

    def __init__(self, icon_registry: IconRegistry, cache_dir: Path = Path("assets/icons")):
        self.registry = icon_registry
        self.cache_dir = cache_dir
        self.surface_cache: Dict[Tuple[str, int], any] = {}
        
        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_icon_surface(self, icon_id: str, size: int = 36):
        """
        Get a Pygame surface for an icon.
        
        Args:
            icon_id: Icon ID to render
            size: Size in pixels (surface will be size x size)
        
        Returns:
            pygame.Surface or None if rendering fails
        """
        cache_key = (icon_id, size)
        
        # Check memory cache first
        if cache_key in self.surface_cache:
            return self.surface_cache[cache_key]

        # Real icon art first - this is the actual fix. icon_id matches
        # ability_id (or talent_id) 1:1 by convention (see
        # icon_migration_and_ui.py's get_ability_icon_surface, which
        # defaults icon_id to ability_id when the data doesn't specify one
        # explicitly). Check both directories - ability_id and talent_id
        # never collide, so trying abilities first then talents is safe.
        for icon_dir in (self.ABILITY_ICON_DIR, self.TALENT_ICON_DIR, self.BAG_ICON_DIR, self.GEAR_ICON_DIR,
                         self.VENDOR_TRASH_ICON_DIR, self.QUEST_ITEM_ICON_DIR, self.CONSUMABLE_ICON_DIR,
                         self.RECIPE_ICON_DIR):
            real_path = icon_dir / f"{icon_id}.png"
            if real_path.exists():
                try:
                    import pygame
                    surface = pygame.image.load(str(real_path)).convert_alpha()
                    if surface.get_width() != size or surface.get_height() != size:
                        surface = pygame.transform.smoothscale(surface, (size, size))
                    self.surface_cache[cache_key] = surface
                    return surface
                except Exception as e:
                    print(f"Warning: Failed to load real icon {real_path}: {e}")
                    # fall through and try the next dir / placeholder below

        icon = self.registry.get_icon_or_fallback(icon_id)
        
        if not icon:
            return self._make_fallback_surface(size, "#CCCCCC")
        
        try:
            # No real PNG on disk for this icon_id yet (unbuilt CoA class,
            # or an ability icon we haven't sourced) - colored square keeps
            # the UI functional and visually distinct rather than blank.
            surface = self._make_fallback_surface(size, icon.fallback_color)
            self.surface_cache[cache_key] = surface
            return surface
        except Exception as e:
            print(f"Warning: Failed to render icon {icon_id}: {e}")
            return self._make_fallback_surface(size, "#FF0000")

    @staticmethod
    def _make_fallback_surface(size: int, color_hex: str):
        """
        Create a colored square surface as fallback.
        (Requires pygame to be imported in calling context)

        A plain 1px BLACK border reads fine against most fallback colors,
        but disappears entirely against near-white ones (class_priest's
        real WoW color is #FFFFFF - correct, not a bug, but a solid white
        square with a near-invisible border just looks like a blank/broken
        tile in a dark-themed panel). A visible gold border matching the
        real icon frame WoW itself uses fixes this for every color, not
        just the white case, and reads as "icon slot" rather than "missing
        image" regardless of fill color.
        """
        try:
            import pygame
            
            # Convert hex to RGB
            color_hex = color_hex.lstrip('#')
            rgb = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
            
            surface = pygame.Surface((size, size))
            surface.fill(rgb)
            
            # Gold icon-frame border, 2px so it stays visible when scaled
            # down to the smaller icon sizes used in list rows.
            pygame.draw.rect(surface, (198, 166, 100), (0, 0, size, size), 2)
            
            return surface
        except ImportError:
            return None


# ============ USAGE EXAMPLE ============

if __name__ == "__main__":
    # Initialize registry
    registry = IconRegistry()
    
    # List all class icons
    print("=== CLASS ICONS ===")
    for icon in registry.list_icons(category="class"):
        print(f"  {icon.icon_id}: {icon.display_name}")
    
    # List all ability icons
    print("\n=== ABILITY ICONS ===")
    for icon in registry.list_icons(category="ability"):
        print(f"  {icon.icon_id}: {icon.display_name}")
    
    # Get specific icon
    warrior_icon = registry.get_icon("class_warrior")
    if warrior_icon:
        print(f"\n=== WARRIOR ICON ===")
        print(f"Display Name: {warrior_icon.display_name}")
        print(f"Tags: {', '.join(warrior_icon.tags)}")
        print(f"Fallback Color: {warrior_icon.fallback_color}")
    
    # Export registry for inspection
    registry.export_registry(Path("icon_registry_export.json"))
    print("\nRegistry exported to icon_registry_export.json")
