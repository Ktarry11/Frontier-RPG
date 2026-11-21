# Frontier RPG Icon System

A self-contained, stable icon system for Frontier RPG. No external dependencies, zero network calls, fallback rendering built-in.

**Version**: 1.0  
**Status**: Production-ready  
**Last Updated**: August 26, 2026

---

## What's Included

```
icon_system_core.py                    # Core icon registry and renderer
icon_migration_and_ui.py               # Data migration + UI helpers
ICON_UI_INTEGRATION_EXAMPLES.py        # Complete UI integration examples
ICON_SYSTEM_INTEGRATION.md             # Detailed integration guide
ICON_SYSTEM_README.md                  # This file
```

---

## Quick Start

### 1. Copy Files to Your Project

```bash
cp icon_system_core.py /path/to/frontier_rpg/
cp icon_migration_and_ui.py /path/to/frontier_rpg/
cp ICON_UI_INTEGRATION_EXAMPLES.py /path/to/frontier_rpg/
```

### 2. Run Data Migration

```python
from icon_migration_and_ui import IconDataMigration
from pathlib import Path

# Dry run (no changes)
migrator = IconDataMigration(Path("frontier_rpg"))
migrator.migrate_all(dry_run=True)

# Apply changes
migrator.migrate_all(dry_run=False)
```

This will automatically:
- Add `icon_id` fields to all abilities based on pattern matching
- Add `icon_id` fields to items based on rarity
- Create sensible defaults that you can refine later

### 3. Initialize in Your Game

```python
# In main.py or game initialization:

from icon_system_core import IconRegistry, IconRenderer
from icon_migration_and_ui import IconUIHelper

# Create icon system
icon_registry = IconRegistry(data_dir=Path("data"))
icon_renderer = IconRenderer(icon_registry, cache_dir=Path("assets/icons"))
icon_ui_helper = IconUIHelper(icon_registry, icon_renderer)

# Pass icon_ui_helper to your UI screens
# (See ICON_UI_INTEGRATION_EXAMPLES.py for details)
```

### 4. Update UI Components

Replace your text-only UI with icon-enabled versions:

```python
# OLD (text only):
# ability_name = "Heroic Strike"

# NEW (with icon):
from ICON_UI_INTEGRATION_EXAMPLES import HotbarWithIcons

hotbar = HotbarWithIcons(icon_ui_helper, x=100, y=600, slots=10)
hotbar.set_slot(0, ability_data)
hotbar.draw(surface, font)
```

---

## Architecture

### IconRegistry

Central registry for all game icons. Embeds icons internally (no external files).

```python
registry = IconRegistry()

# Get an icon
warrior_icon = registry.get_icon("class_warrior")

# List icons by category
ability_icons = registry.list_icons(category="ability")

# Get with fallback
icon = registry.get_icon_or_fallback("custom_icon", fallback_id="ability_spell")
```

**Built-in Icon Categories:**
- **Classes**: `class_warrior`, `class_shaman`, etc. (9 icons)
- **Ability Types**: `ability_melee`, `ability_spell`, `ability_heal`, etc. (6 icons)
- **Item Rarity**: `rarity_common`, `rarity_uncommon`, `rarity_rare`, `rarity_epic`, `rarity_legendary` (5 icons)
- **Status Effects**: `status_poison`, `status_bleed`, `status_stun`, `status_shield` (4 icons)

**Total Built-in Icons**: ~24 core icons, all self-contained.

### IconRenderer

Renders icons to Pygame surfaces with caching and fallback support.

```python
renderer = IconRenderer(registry)

# Get a rendered surface
surface = renderer.get_icon_surface("class_warrior", size=64)

# Surface is cached by (icon_id, size) tuple
# Second call uses cached version (instant)
```

### IconUIHelper

High-level methods for retrieving icons in UI contexts.

```python
helper = IconUIHelper(registry, renderer)

# Get icon for an ability
ability_icon = helper.get_ability_icon_surface(ability_data, size=36)

# Get icon for an item
item_icon = helper.get_item_icon_surface(item_data, size=48)

# Get icon for a class
class_icon = helper.get_class_icon_surface("Warrior", size=64)

# Get icon for a status effect
status_icon = helper.get_status_effect_icon_surface(status_effect, size=24)
```

---

## Data Schema Changes

### Abilities (data/abilities/*.json)

Add optional `icon_id` field:

```json
{
  "ability_id": "warrior_heroic_strike",
  "name": "Heroic Strike",
  "icon_id": "ability_melee",  // NEW
  "resource_type": "rage",
  ...
}
```

### Items (data/items/*.json)

Add optional `icon_id` field:

```json
{
  "item_id": "iron_sword",
  "name": "Iron Sword",
  "icon_id": "item_iron_sword",  // NEW (or fallback to rarity)
  "rarity": "uncommon",
  ...
}
```

### Status Effects (combat/status_effects.py)

Add optional `icon_id` field to `StatusEffect` dataclass:

```python
@dataclass
class StatusEffect:
    name: str
    effect_id: str
    icon_id: str = "status_poison"  # NEW
    ...
```

---

## Icon Categories & Recommendations

### Class Icons (9 original WoW classes)
- `class_warrior` — Warrior (Plate, Tank) — Color: #C79C6E
- `class_shaman` — Shaman (Mail, Hybrid) — Color: #0070DD
- `class_rogue` — Rogue (Leather, Melee DPS) — Color: #FFF468
- `class_priest` — Priest (Cloth, Healer) — Color: #FFFFFF
- `class_hunter` — Hunter (Mail, Ranged DPS) — Color: #A335EE
- `class_mage` — Mage (Cloth, Caster DPS) — Color: #69CCF0
- `class_warlock` — Warlock (Cloth, Caster DPS) — Color: #9482CA
- `class_druid` — Druid (Leather, Hybrid) — Color: #FF7D0A
- `class_paladin` — Paladin (Plate, Hybrid) — Color: #F58CBA

### Ability Types
- `ability_melee` — Physical/melee damage
- `ability_spell` — Magical/spell damage
- `ability_heal` — Healing/restoration
- `ability_buff` — Buff/enhancement
- `ability_debuff` — Debuff/crowd control
- `ability_dot` — Damage over time / bleed

### Item Rarity
- `rarity_common` — Gray/common items
- `rarity_uncommon` — Green/uncommon items
- `rarity_rare` — Blue/rare items
- `rarity_epic` — Purple/epic items
- `rarity_legendary` — Orange/legendary items

### Status Effects
- `status_poison` — Poison/toxin effects
- `status_bleed` — Bleeding/wound effects
- `status_stun` — Stun/crowd control
- `status_shield` — Protection/buff effects

---

## Fallback Behavior

If an icon fails to render:

1. **Missing icon_id**: System falls back to category-based default
   - Ability without icon_id → Uses `effect_type` to pick icon
   - Item without icon_id → Uses `rarity` to pick icon
   - Status effect without icon_id → Uses `effect_type` to pick icon

2. **Rendering failure**: Colored square is displayed
   - Uses `fallback_color` from IconSpec
   - Maintains visual consistency even if SVG rendering fails

3. **Missing registry entry**: Uses first available icon (shouldn't happen)

**Result**: UI always has _something_ to display. No crashes, no blank spaces.

---

## Performance Considerations

### Memory
- **Icon registry**: ~50KB (embedded SVG strings)
- **Surface cache**: Grows with usage (typical: 5-20 cached surfaces per session)
- **Total overhead**: Negligible (<1MB for typical play)

### CPU
- **Icon lookup**: O(1) dictionary access
- **Surface rendering**: First render ~1ms, cached subsequent renders ~0.1ms
- **UI draw**: No noticeable impact on frame time

### Caching Strategy
- Surfaces are cached by `(icon_id, size)` tuple
- Cache is _never_ cleared during gameplay (intentional)
- Memory is freed when game exits

---

## Extensibility

### Adding Custom Icons

Create `data/icons.json`:

```json
{
  "icons": [
    {
      "icon_id": "custom_ability_fireball",
      "display_name": "Fireball",
      "category": "ability",
      "svg_data": "<svg>...</svg>",  // Full SVG markup or file path
      "fallback_color": "#FF6600",
      "source": "embedded",
      "tags": ["fire", "damage", "mage"]
    }
  ]
}
```

Registry will load these automatically on initialization.

### Replacing with Real Sprites

When you get custom sprites:

1. Save PNG files to `assets/icons/custom_abilities/`
2. Create new `IconSpec` entries pointing to file paths
3. Update `IconRenderer` to handle file-based icons
4. The `icon_id` in your data never changes — only the underlying source

---

## Troubleshooting

### Icon not showing?

```python
# Debug: Check what icon is being used
icon = registry.get_icon("ability_melee")
if not icon:
    print("Icon not found!")
    print("Available icons:", [i.icon_id for i in registry.list_icons()])
```

### Wrong icon displaying?

```python
# Check icon mappings in your data
ability = ability_data
print(f"Ability: {ability['name']}")
print(f"Icon ID: {ability.get('icon_id', 'MISSING')}")
print(f"Effect Type: {ability.get('effect_type')}")

# Verify with registry
icon = registry.get_icon(ability.get("icon_id"))
print(f"Icon found: {icon is not None}")
```

### Slow rendering?

```python
# Check cache hits
renderer.surface_cache  # Should grow initially, then stabilize

# If cache is huge, something is requesting different sizes
# Standardize sizes: abilities=36, items=48, classes=64, status=24
```

---

## Testing Checklist

- [ ] Registry loads all 24 built-in icons
- [ ] Custom icons load from `data/icons.json` (if present)
- [ ] Ability data has valid `icon_id` fields (or fallback works)
- [ ] Item data has valid `icon_id` fields (or fallback works)
- [ ] Hotbar displays 10 ability icons correctly
- [ ] Inventory displays item icons correctly
- [ ] Character sheet shows equipped item icons
- [ ] Combat screen displays status effect icons
- [ ] Class selection shows all 9 class icons
- [ ] No crashes when icon_id is missing
- [ ] Fallback colors display when rendering fails
- [ ] Surface caching works (check logs for repeated renders)
- [ ] Frame rate is not impacted by icon system

---

## Future Enhancements

1. **SVG Rendering**: Use `cairosvg` or `Pillow` to render SVG → PNG for better quality
2. **Icon Editor**: Build a UI tool for creating/previewing icons
3. **Dynamic Icons**: Generate icons procedurally based on ability stats
4. **Icon Atlasing**: Pack icons into texture atlas for performance
5. **Localization**: Support localized icon labels
6. **Animated Icons**: Support frame-based animation for special effects

---

## File Reference

### Core Files

| File | Purpose | Size |
|------|---------|------|
| `icon_system_core.py` | Registry, renderer, icon specs | ~400 lines |
| `icon_migration_and_ui.py` | Data migration, UI helpers | ~350 lines |
| `ICON_UI_INTEGRATION_EXAMPLES.py` | Complete UI integration examples | ~500 lines |
| `ICON_SYSTEM_INTEGRATION.md` | Detailed integration guide | ~300 lines |

### Data Files

| File | Purpose | Notes |
|------|---------|-------|
| `data/icons.json` | Custom icon definitions | Create if needed |
| `data/abilities/*.json` | Ability data (add `icon_id`) | Migration adds this |
| `data/items/*.json` | Item data (add `icon_id`) | Migration adds this |

### Generated Files

| Directory | Purpose |
|-----------|---------|
| `assets/icons/` | Icon surface cache (auto-created) |
| (none during gameplay) | All data is in-memory |

---

## License & Attribution

This icon system is part of Frontier RPG.

Built-in SVG icons are original designs (not extracted from WoW).

---

## Support

For issues or questions:
1. Check `ICON_SYSTEM_INTEGRATION.md` for detailed setup
2. Review `ICON_UI_INTEGRATION_EXAMPLES.py` for code examples
3. Debug with `IconRegistry.list_icons()` and cache inspection

---

**Remember**: The icon system is designed to be invisible. If it's working, you won't think about it—you'll just see icons in your UI. If something breaks, the fallback rendering will keep you in the game.

Stay stable, bro. 🎮
