# PHASE 6 DESIGN: CONSUMABLES & VENDOR SYSTEM
## Currency, Potions, Vendors, and Buy/Sell Economy

**Status:** Design phase (before code)  
**Scope:** Currency + Consumables + Vendor NPCs + UI  
**Not in scope:** Crafting (Phase 7+), transmog, AH simulation

---

## PART 1: CURRENCY SYSTEM

### Exchange Rates (WoW-Classic Style)
```
1 Gold = 100 Silver
1 Silver = 100 Copper
(Therefore: 1 Gold = 10,000 Copper)
```

### Character Currency Field
`Character` gains:
- `copper: int` (primary storage)
- `gold_amount: int` (computed property for convenience)
- `silver_amount: int` (computed property)
- `copper_amount: int` (computed property)

Methods:
- `add_currency(amount_copper)` — add copper (raw unit), returns True if successful
- `remove_currency(amount_copper)` — subtract copper, returns True if sufficient funds
- `get_currency_string()` — returns formatted display like "45g 30s 75c" or "45.3075g" (up to you)

### Where Currency Comes From (Phase 6 Launch)
1. **Loot drops** — creatures drop a copper amount on death (tied to creature level, rarity of gear dropped)
2. **Vendor sales** — selling items to vendors (each Item has `sell_price` in copper)
3. **(Phase 7+)** Quest rewards, dungeon loot chests, rare spawn treasure

### Typical Copper Values (rough ballpark for loot/vendor)
- Level 1 common mob: 10-30 copper (loose change)
- Level 10 rare mob: 150-300 copper (meaningful purchase)
- Level 20 epic mob: 500-1000 copper (real money)
- Level 60 boss: 5000-10000 copper (crafting material purchase or major vendor item)

Vendor items:
- Healing potion (restore 200 HP): 50 copper (level 5) → 500 copper (level 50)
- Mana potion (restore 200 mana): 50 copper (level 5) → 500 copper (level 50)
- Buff food (+50 STR for 30min): 75 copper (level 5) → 750 copper (level 50)
- Resurrection item (phoenix stone, brings you back at death): 5000 copper (one-time)

---

## PART 2: CONSUMABLES SYSTEM

### Consumable Types
| Type | Effect | Use Case | Stack Limit |
|------|--------|----------|-------------|
| **Health Potion** | Restore 200-500 HP (scales with level) | Combat & out-of-combat | 20 |
| **Mana Potion** | Restore 200-500 Mana | Combat & out-of-combat | 20 |
| **Stamina Potion** | Restore 100 stamina temporarily for 30s | Combat prep | 10 |
| **Rage Potion** | Restore 50 Rage instantly (Warriors only) | Combat | 5 |
| **Energy Elixir** | Restore 50 Energy instantly (Rogues only) | Combat | 5 |
| **Buff Food** | +50 primary stat for 30 min or until combat ends | Buff stacking | 10 |
| **Resurrection Stone** | Resurrection item: on death, auto-rez at 50% HP/mana instead of portal | Rare/quest | 1 |

### Item Data Structure (new `consumable_type.json`)
```json
{
  "consumable_id": "healing_potion_minor",
  "name": "Minor Healing Potion",
  "consumable_type": "health_potion",
  "description": "Restores 200 health.",
  "effect_value": 200,  // HP restored, or stat bonus amount, or duration
  "effect_duration": 0,  // 0 = instant, >0 = duration in seconds
  "level_multiplier": 1.0,  // scales effect with character level (1.0 = base, 1.05 = 5% per level)
  "required_level": 5,
  "cooldown_seconds": 5,  // potion share cooldown (WoW-style, same for all potions)
  "stack_limit": 20,
  "vendor_price": 50,  // copper to buy from vendor
  "sell_price": 10  // copper refund if sold
}
```

### Consumable Item Class
`entities/consumable.py` → `Consumable` class

Fields:
- `consumable_id`, `name`, `consumable_type`, `description`
- `effect_value`, `effect_duration`, `level_multiplier`
- `required_level`, `cooldown_seconds`, `stack_limit`
- `vendor_price`, `sell_price`
- `quantity: int` (how many of this consumable in the stack)

Methods:
- `can_use(character) → bool` — checks level req, cooldown timer
- `use(character) → bool` — applies effect, returns True if successful, starts cooldown
- `to_dict() / from_dict()` — serialization

### Consumables in Inventory
Currently inventory is `Character.inventory: List[Item]`. Add:
- `Character.consumables: List[Consumable]` — separate list, parallel to gear inventory
- `Character.consumable_cooldown: float` — shared potion cooldown timer (WoW-style: you can't spam potions, one every 5s)

Or merge them? (single inventory list, mixed Item + Consumable). **Recommendation: separate lists** for now — keeps Item and Consumable types clean and independent, UI can render them in different visual layouts without mixing concerns. Easier to refactor later if needed.

---

## PART 3: CONSUMABLES QUICKBAR

### Quickbar Architecture
New UI component: `ConsumablesQuickbar` (parallel to hotbar, but simpler)

- **5-slot quickbar** for most-used consumables (Health Potion, Mana Potion, Buff Food, Emergency Item, Custom Slot)
- **Keyboard shortcuts:** `H` for slot 1, `M` for slot 2, `K` for slot 3, etc. (or configurable)
- **Display:** Small bars/buttons at bottom-left of combat screen, showing item name + quantity remaining
- **Click to use:** Click the button or press hotkey, pops one item from inventory and uses it

### How Consumables Flow
1. **Pick up a potion** in a fight (from loot or pre-carried)
2. **Add to inventory** via `Character.add_consumable(consumable)`
3. **Drag from inventory grid to quickbar slot** (UI interaction) or **(Phase 6b)** auto-populate first 5 unique consumables on creation
4. **Press hotkey or click button** → `quickbar_slot.use(character)` → applies effect, decrements quantity, removes stack if empty
5. **Out of combat:** quickbar hidden, but can still use consumables from inventory screen if needed

### Quickbar UI Rendering (combat_screen.py)
```
[🧪 Health Pot ×8]  [💙 Mana Pot ×4]  [🥘 Buff Food ×2]  [⚫ Empty]  [⚫ Empty]
     H                  M                   K                 O            P
```

---

## PART 4: VENDOR SYSTEM

### Vendor NPCs
Each town (Valley of Trials, Durotar/Razor Hill, Echo Isles) has **one vendor NPC** positioned in a logical spot (town center, merchant stall sprite). These are:
- **Stationary** (don't move)
- **Clickable** (tile-based interaction, like portals)
- **One per town** for now (simplicity; Phase 8+ can add multiple)

### Vendor NPC Data (`data/npcs/vendors.json`)
```json
{
  "vendor_id": "razorhill_merchant",
  "name": "Khadgar",
  "zone": "razor_hill",
  "x": 30,
  "y": 25,
  "tile_sprite": "human_merchant",  // sprite ID, rendered like any NPC
  "sells": [
    "healing_potion_minor",
    "healing_potion_standard",
    "mana_potion_minor",
    "mana_potion_standard",
    "buff_food_strength",
    "buff_food_intellect",
    "resurrection_stone"
  ],
  "buys_from_player": true,  // all vendors buy all items from player
  "faction": "neutral"  // future: faction-locked vendors
}
```

### Vendor Interaction Flow
1. **Player walks onto vendor NPC tile** → triggers interaction check
2. **Press space/interact key** → `VendorScreen` opens
3. **VendorScreen layout:**
   - **Left panel:** Vendor's items for sale (with prices in copper)
   - **Right panel:** Player's inventory (with sell prices highlighted)
   - **Bottom:** Player's current copper display, transaction buttons (Buy / Sell)
4. **Click an item to select** → shows tooltip (name, effect, req level, price)
5. **Click Buy** → deducts copper, adds consumable to inventory
6. **Click Sell** → adds copper, removes item from inventory
7. **Close** → return to overworld

### Vendor UI Class (`ui/screens/vendor_screen.py`)
Parallel to `inventory_screen.py`, but focused on trading rather than equipping.

Similar layout:
- Vendor inventory on left (scrollable list, 10 items visible)
- Player inventory on right (grid or list, scrollable)
- Price tags, transaction buttons
- Currency display at top

---

## PART 5: CONSUMABLE USAGE IN COMBAT

### Combat Screen Integration
When `CombatScreen` renders, if player has consumables in quickbar slots, draw them at bottom-left (or wherever feels natural). Consumables can be used:
- **Anytime** (out of turn, like hotbar is for player abilities)
- **Once per potion cooldown** (shared 5s cooldown, WoW-style)
- **In combat or out** (same mechanics everywhere)

### Effect Application
When a consumable is used (via quickbar or inventory), `Consumable.use(character)` applies its effect:
```python
def use(self, character):
    if not self.can_use(character):
        return False
    
    if self.consumable_type == "health_potion":
        restore_amount = int(self.effect_value + character.level * self.level_multiplier)
        character.heal(restore_amount)
        self.combat_log.append(f"Used {self.name}: +{restore_amount} HP")
    
    elif self.consumable_type == "buff_food":
        character.apply_buff(self.consumable_id, duration=self.effect_duration)
        self.combat_log.append(f"Ate {self.name}: +{self.effect_value} {self.buff_stat} for {self.effect_duration}s")
    
    elif self.consumable_type == "resurrection_stone":
        character.add_buff("resurrection_shield", duration=None)
        self.combat_log.append(f"Activated {self.name}: Will resurrect on next death")
    
    self.character.consumable_cooldown = 5.0  # start cooldown
    self.quantity -= 1
    if self.quantity <= 0:
        self.character.consumables.remove(self)  # remove from inventory if empty
    
    return True
```

---

## PART 6: LOOT GENERATION & CURRENCY DROPS

### Creature Loot (modified from Phase 5)
When a creature is defeated, roll for:
1. **Gear drop** (35% chance, existing logic)
2. **Currency drop** (100% chance, new)

Copper dropped = `(creature_level * 10) + random(0, creature_level * 5)` (tunable)

Example:
- Level 1 boar: 10-15 copper
- Level 10 harpy: 100-150 copper
- Level 50 boss: 500-750 copper

### Quest Rewards (Phase 7)
Will include currency as part of reward pool. No changes needed in Phase 6.

---

## PART 7: IMPLEMENTATION CHECKLIST

### New Files
- `entities/consumable.py` — Consumable class
- `ui/screens/vendor_screen.py` — Vendor UI
- `ui/components/consumables_quickbar.py` — Quickbar rendering/interaction
- `world/vendor_manager.py` — Vendor NPC spawning/interaction logic
- `data/consumables/consumable_types.json` — All consumable definitions
- `data/npcs/vendors.json` — Vendor NPC definitions

### Modified Files
- `entities/character.py` — add `copper`, `consumables`, `consumable_cooldown`, methods
- `combat/combat_engine.py` — copper drop on creature death, consumable use in combat loop
- `ui/screens/combat_screen.py` — render consumables quickbar, handle quickbar hotkeys
- `ui/screens/overworld_screen.py` — handle vendor NPC interaction (click to open VendorScreen)
- `core/game_states.py` — add `VENDOR` state
- `core/game_state.py` — register VendorScreen
- `world/zone_generator.py` — place vendor NPC sprites in towns
- `world/creature_manager.py` — add currency drop on creature spawn
- `config.py` — add consumable config (cooldown duration, typical copper drops, etc.)

### Save System
- `SAVE_VERSION` bump to 3 (adds `copper`, `consumables`, `consumable_cooldown`)

---

## PART 8: OPEN QUESTIONS FOR YOU

1. **Consumable limit:** Should a player be able to carry unlimited potions (stacking to 20 each), or should there be an overall "consumables weight" limit? Keep it simple for now?

2. **Resurrection stone mechanics:** Should this be:
   - One-time use (consume it on death, item gone forever)?
   - Reusable (lasts until consumed)?
   - Cooldown-based (usable once per day)?
   - Or skip entirely in Phase 6 (add in Phase 8+ with proper death mechanics)?

3. **Buff food stacking:** Can a player stack multiple buff foods (e.g., +STR and +INT simultaneously)? Or do they replace each other (new buff cancels old buff)?

4. **Vendor prices:** Should potions scale with level (minor potion cheaper at level 5, major potion expensive at level 50)? Or are there just "standard" potions at fixed prices, and higher-level players buy in bulk?

5. **Quickbar population:** Auto-populate the first 5 consumables on inventory pickup, or make players manually drag/slot them?

---

**Next step:** Once you answer these questions, I'll start writing code. Estimated size: ~800-1200 LOC (new) + ~400 LOC (mods to existing files). Should be fast with all the architecture locked in.
