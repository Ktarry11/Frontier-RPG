# Icon System Integration Guide

## Overview
This document covers integrating the icon system into Frontier RPG's existing data structures.

**Core Principle**: Icons are _optional_ fields in ability/item data. If an icon_id is missing, the system falls back to a category-based default.

---

## Schema Changes

### 1. Abilities (data/abilities/*.json)

Add optional `icon_id` field to each ability:

```json
{
  "ability_id": "warrior_heroic_strike",
  "name": "Heroic Strike",
  "icon_id": "ability_melee",  // NEW: Reference to icon registry
  "resource_type": "rage",
  "cooldown": 0,
  "effect_type": "damage",
  ...
}
```

**Icon ID Mapping Strategy:**
- Use ability-specific IDs where they exist (e.g., "ability_fireball", "ability_shield_block")
- Fall back to archetype IDs for generic abilities:
  - Damage abilities → `ability_melee` or `ability_spell`
  - Healing abilities → `ability_heal`
  - Buff abilities → `ability_buff`
  - Debuff abilities → `ability_debuff`
  - DoT abilities → `ability_dot`

**For 9 Original WoW Classes**, suggested icon mapping:

#### Warrior
- `warrior_heroic_strike` → `ability_melee`
- `warrior_battle_shout` → `ability_buff`
- `warrior_rend` → `ability_dot`

#### Shaman
- `shaman_lightning_bolt` → `ability_spell`
- `shaman_heal` → `ability_heal`
- `shaman_totem` → `ability_buff`

#### Rogue
- `rogue_backstab` → `ability_melee`
- `rogue_poison` → `ability_dot`

#### Priest
- `priest_heal` → `ability_heal`
- `priest_shield` → `ability_buff`
- `priest_smite` → `ability_spell`

#### Hunter
- `hunter_shoot` → `ability_melee`
- `hunter_pet_attack` → `ability_melee`

#### Mage
- `mage_fireball` → `ability_spell`
- `mage_frostbolt` → `ability_spell`

#### Warlock
- `warlock_shadowbolt` → `ability_spell`
- `warlock_drain_life` → `ability_dot`

#### Druid
- `druid_wrath` → `ability_spell`
- `druid_heal` → `ability_heal`
- `druid_entangle` → `ability_debuff`

#### Paladin
- `paladin_holy_light` → `ability_heal`
- `paladin_shield` → `ability_buff`
- `paladin_smite` → `ability_melee`

---

### 2. Items (data/items/*)

Add optional `icon_id` field to item definitions:

```json
{
  "item_id": "leather_boots",
  "name": "Leather Boots",
  "icon_id": "item_leather_boots",  // NEW: Specific icon or rarity-based fallback
  "slot": "feet",
  "armor_type": "leather",
  "rarity": "uncommon",
  ...
}
```

**Icon ID Mapping Strategy:**
- Prefer specific item IDs: `item_iron_sword`, `item_cloth_robe`
- Fall back to slot-based: `item_armor_chest`, `item_weapon_staff`
- Final fallback to rarity: `rarity_uncommon`, `rarity_rare`

---

### 3. Classes (character creation)

Add class icon references to class definitions:

```json
{
  "class_id": "warrior",
  "name": "Warrior",
  "icon_id": "class_warrior",  // NEW: Class icon for UI display
  "description": "...",
  ...
}
```

Mapping:
- Warrior → `class_warrior`
- Shaman → `class_shaman`
- Rogue → `class_rogue`
- Priest → `class_priest`
- Hunter → `class_hunter`
- Mage → `class_mage`
- Warlock → `class_warlock`
- Druid → `class_druid`
- Paladin → `class_paladin`

---

### 4. Status Effects (combat/status_effects.py)

Extend `StatusEffect` dataclass to include icon_id:

```python
@dataclass
class StatusEffect:
    name: str
    effect_id: str
    effect_type: str  # "buff", "debuff", "dot", "hot"
    icon_id: str = "status_poison"  # NEW: Icon reference
    duration: int = 0
    potency: float = 1.0
    ...
```

**Mapping:**
- Poison effects → `status_poison`
- Bleed effects → `status_bleed`
- Crowd control (stun, freeze) → `status_stun`
- Protection buffs → `status_shield`

---

## Implementation Plan

### Phase 1: Data Migration (Schema Update)
1. Add `icon_id` as optional field to ability JSON schemas
2. Add `icon_id` as optional field to item JSON schemas
3. Generate migration script to auto-populate sensible defaults
4. Manually review and refine mappings for edge cases

### Phase 2: Code Integration
1. Import `IconRegistry` and `IconRenderer` into UI modules
2. Update `CombatUIPanel` to display ability icons in hotbar
3. Update `InventoryScreen` to display item icons
4. Update `CharacterCreationScreen` to show class icons
5. Update `CombatScreen` to show status effect icons

### Phase 3: Testing
1. Verify all icons render without errors
2. Test fallback behavior (missing icon_id → default icon)
3. Performance test: check surface caching works
4. Visual polish: adjust icon sizes/positioning as needed

---

## File Structure

```
frontier_rpg/
├── icon_system_core.py              # NEW: Core icon system
├── data/
│   ├── icons.json                   # NEW: Extended icon definitions (initially empty)
│   ├── abilities/
│   │   ├── warrior.json             # UPDATED: Add icon_id fields
│   │   ├── shaman.json
│   │   └── ... (all 9 classes)
│   ├── items/
│   │   ├── armor_types.json         # UPDATED: Add icon_id
│   │   ├── weapon_types.json        # UPDATED: Add icon_id
│   │   └── stat_templates.json      # UPDATED: Add icon_id
│   └── classes.json                 # NEW: Class icon mappings
├── ui/
│   ├── combat_ui_panel.py           # UPDATED: Use icon renderer
│   └── screens/
│       ├── inventory_screen.py      # UPDATED: Use icon renderer
│       ├── character_screen.py      # UPDATED: Show class icons
│       └── combat_screen.py         # UPDATED: Show status effect icons
└── assets/
    └── icons/                       # NEW: Icon cache directory (auto-created)
```

---

## Data Migration Script

Run this to auto-populate icon_id fields in existing ability data:

```python
from pathlib import Path
import json
from icon_system_core import IconRegistry

def auto_populate_icons():
    """Scan ability data and populate icon_id fields with sensible defaults."""
    
    registry = IconRegistry()
    ability_dir = Path("data/abilities")
    
    # Mapping of ability patterns to icon IDs
    icon_mappings = {
        # Pattern matching (case-insensitive)
        "heal": "ability_heal",
        "shield": "ability_buff",
        "buff": "ability_buff",
        "shout": "ability_buff",
        "totem": "ability_buff",
        "dot": "ability_dot",
        "poison": "ability_dot",
        "bleed": "ability_dot",
        "drain": "ability_dot",
        "damage": "ability_spell",
        "strike": "ability_melee",
        "attack": "ability_melee",
        "smite": "ability_spell",
        "wrath": "ability_spell",
        "bolt": "ability_spell",
        "ball": "ability_spell",
        "stun": "ability_debuff",
        "slow": "ability_debuff",
    }
    
    for ability_file in ability_dir.glob("*.json"):
        with open(ability_file, 'r') as f:
            data = json.load(f)
        
        updated = False
        for ability in data.get("abilities", []):
            if "icon_id" not in ability:
                # Try pattern matching on name/description
                ability_name = ability.get("name", "").lower()
                matched_icon = None
                
                for pattern, icon_id in icon_mappings.items():
                    if pattern in ability_name:
                        matched_icon = icon_id
                        break
                
                # Default fallback based on effect_type
                if not matched_icon:
                    effect_type = ability.get("effect_type", "damage")
                    effect_mappings = {
                        "damage": "ability_melee",
                        "heal": "ability_heal",
                        "buff": "ability_buff",
                        "debuff": "ability_debuff",
                        "dot": "ability_dot",
                    }
                    matched_icon = effect_mappings.get(effect_type, "ability_spell")
                
                ability["icon_id"] = matched_icon
                updated = True
        
        if updated:
            with open(ability_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Updated {ability_file}")

if __name__ == "__main__":
    auto_populate_icons()
```

---

## Testing Checklist

- [ ] All built-in icons render without error
- [ ] Icon registry loads all built-in + extended icons
- [ ] Fallback color displayed when icon rendering fails
- [ ] Surface caching works (same icon/size uses cached surface)
- [ ] Icon IDs in ability/item data are valid
- [ ] UI screens display icons without crashes
- [ ] Performance is acceptable (no lag when rendering many icons)

---

## Future Enhancements

1. **SVG Rendering**: Use `cairosvg` or `Pillow` to render SVG → PNG at multiple scales
2. **Custom Icon Assets**: Import PNG/JPG icons and register them in `data/icons.json`
3. **Icon Editor**: Build a UI tool for authoring and previewing icons
4. **Dynamic Icons**: Generate icons procedurally based on ability stats/effects
5. **Icon Atlasing**: Pack multiple icons into a single texture atlas for performance

---

## Troubleshooting

**Q: Icon not showing up?**
A: Check that `icon_id` is a valid key in the registry. Use `IconRegistry.list_icons()` to debug available IDs.

**Q: Fallback color looks wrong?**
A: Adjust `fallback_color` in the `IconSpec`. Colors are hex strings (e.g., "#FF0000").

**Q: Rendering is slow?**
A: Check that surface caching is working. Icon surfaces should be cached by (icon_id, size) tuple.

**Q: SVG not displaying correctly?**
A: Built-in SVGs are simple and should work. For custom SVGs, use `viewBox="0 0 64 64"` and standard SVG syntax.

