"""
Consumable class - potions, elixirs, food buffs, etc.
Separate from Item (gear) to keep types clean and independent.
"""


class Consumable:
    """A consumable item (potion, elixir, food buff) with quantity tracking."""
    
    def __init__(self, consumable_id, name, consumable_type, description, effect_value, 
                 effect_duration, level_multiplier, required_level, cooldown_seconds,
                 stack_limit, vendor_price, sell_price, buff_category=None,
                 stat_bonuses=None):
        """
        Args:
            consumable_id: unique identifier (e.g., "healing_potion_minor")
            name: display name
            consumable_type: "health_potion", "mana_potion", "elixir", "food", etc.
            description: flavor text / tooltip
            effect_value: HP restored or mana restored (health_potion/mana_potion only -
                           elixir/food buffs use stat_bonuses instead, see below)
            effect_duration: seconds (0 = instant, >0 = duration buff)
            level_multiplier: unused for elixir/food (Kyle's call: buffs are flat values,
                               not level-scaled - real scaling comes later from
                               crafting/quality tiers, not a formula). Still applies to
                               health/mana potions.
            required_level: minimum character level to use
            cooldown_seconds: shared potion cooldown (WoW-style, typically 5s)
            stack_limit: max quantity per stack (typically 20)
            vendor_price: copper cost to buy from vendor
            sell_price: copper refund if sold back
            buff_category: "guardian" | "battle" | "food" (for buff stacking rules -
                            one active per category, same as WoW's elixir/food slots)
            stat_bonuses: dict of {stat_name: amount} applied while the buff is active,
                          e.g. {"intellect": 12} or {"intellect": 8, "spell_power": 4}.
                          Keys are anything Character._recalculate_derived_stats() reads
                          from its gear-bonus pool (strength, stamina, intellect, spirit,
                          agility, spell_power, healing_power, attack_power, crit_chance_
                          physical/spell, hit_rating, dodge, parry, block, haste, mp5,
                          spell_penetration, school spell powers, ...) - same vocabulary
                          gear suffixes use, so a consumable buff and a gear stat are
                          indistinguishable to every downstream formula. Only used for
                          elixir/food; None for potions.
        """
        self.consumable_id = consumable_id
        self.name = name
        self.consumable_type = consumable_type
        self.description = description
        self.effect_value = effect_value
        self.effect_duration = effect_duration
        self.level_multiplier = level_multiplier
        self.required_level = required_level
        self.cooldown_seconds = cooldown_seconds
        self.stack_limit = stack_limit
        self.vendor_price = vendor_price
        self.sell_price = sell_price
        self.buff_category = buff_category  # "guardian", "battle", "food", or None
        self.stat_bonuses = stat_bonuses or {}
        
        self.quantity = 1  # number in this stack
    
    def can_use(self, character):
        """Check if character can use this consumable."""
        if character.level < self.required_level:
            return False
        if character.consumable_cooldown > 0:
            return False
        if self.buff_category == "guardian" and character.guardian_buff is not None:
            return False  # Can't stack two guardian elixirs
        if self.buff_category == "battle" and character.battle_buff is not None:
            return False  # Can't stack two battle elixirs
        if self.buff_category == "food" and character.food_buff is not None:
            return False  # Can't stack two food buffs
        if self.buff_category == "ammo" and character.ammo_buff is not None:
            return False  # One quiver at a time
        return True
    
    def use(self, character, combat_log=None):
        """
        Apply consumable effect to character. Returns True if successful.
        This is called from combat engine or inventory screen.
        """
        if not self.can_use(character):
            return False
        
        # Apply effect based on type
        if self.consumable_type == "health_potion":
            scaled_value = int(self.effect_value * (1.0 + character.level * self.level_multiplier))
            character.heal(scaled_value)
            log_msg = f"Used {self.name}: +{scaled_value} HP"
        
        elif self.consumable_type == "mana_potion":
            scaled_value = int(self.effect_value * (1.0 + character.level * self.level_multiplier))
            old_mana = character.current_mana
            character.current_mana = min(character.mana, character.current_mana + scaled_value)
            actual_restore = character.current_mana - old_mana
            log_msg = f"Used {self.name}: +{actual_restore} Mana"
        
        elif self.consumable_type == "elixir":
            # Elixirs are buffs - store them in the appropriate buff slot. Flat
            # values, no level scaling (Kyle's call - see stat_bonuses docstring).
            character.apply_consumable_buff(self.buff_category, self)
            bonus_str = ", ".join(f"+{v} {k.replace('_', ' ').title()}" for k, v in self.stat_bonuses.items())
            log_msg = f"Drank {self.name}: {bonus_str}"
        
        elif self.consumable_type == "food":
            # Food buffs go in the food slot - same flat-value treatment as elixirs.
            character.apply_consumable_buff("food", self)
            bonus_str = ", ".join(f"+{v} {k.replace('_', ' ').title()}" for k, v in self.stat_bonuses.items())
            log_msg = f"Ate {self.name}: {bonus_str} for {self.effect_duration}s"
        
        elif self.consumable_type == "ammo":
            # Crafted arrows / bolts (Woodworking): a timed ranged-attack buff in its own slot, since the game has
            # no ammunition mechanic.  Same flat-value treatment as elixirs and food.
            character.apply_consumable_buff("ammo", self)
            bonus_str = ", ".join(f"+{v} {k.replace('_', ' ').title()}" for k, v in self.stat_bonuses.items())
            log_msg = f"Nocked {self.name}: {bonus_str} for {int(self.effect_duration)}s"

        else:
            return False
        
        # Consume the item
        self.quantity -= 1
        character.consumable_cooldown = self.cooldown_seconds
        
        if combat_log is not None:
            combat_log.append(log_msg)
        
        return True
    
    def to_dict(self):
        """Serialize for save/load."""
        return {
            "consumable_id": self.consumable_id,
            "name": self.name,
            "consumable_type": self.consumable_type,
            "description": self.description,
            "effect_value": self.effect_value,
            "effect_duration": self.effect_duration,
            "level_multiplier": self.level_multiplier,
            "required_level": self.required_level,
            "cooldown_seconds": self.cooldown_seconds,
            "stack_limit": self.stack_limit,
            "vendor_price": self.vendor_price,
            "sell_price": self.sell_price,
            "buff_category": self.buff_category,
            "stat_bonuses": self.stat_bonuses,
            "quantity": self.quantity,
        }
    
    @staticmethod
    def from_dict(data):
        """Deserialize from save data."""
        c = Consumable(
            data["consumable_id"],
            data["name"],
            data["consumable_type"],
            data["description"],
            data["effect_value"],
            data["effect_duration"],
            data["level_multiplier"],
            data["required_level"],
            data["cooldown_seconds"],
            data["stack_limit"],
            data["vendor_price"],
            data["sell_price"],
            data.get("buff_category"),
            data.get("stat_bonuses"),
        )
        c.quantity = data.get("quantity", 1)
        return c
    
    def __repr__(self):
        return f"<Consumable {self.name} x{self.quantity}>"
