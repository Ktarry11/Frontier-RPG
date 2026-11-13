"""
Consumable class - potions, elixirs, food buffs, etc.
Separate from Item (gear) to keep types clean and independent.
"""


#: How long a cooked meal leaves you well fed.
WELL_FED_SECONDS = 1800

#: Stat keys that do not read well title-cased ("Hp5", "Healing Power").
BONUS_LABELS = {"hp5": "Health per turn", "mp5": "Mana per turn", 
                "crit_chance_physical": "% Physical Crit", "crit_chance_spell": "% Spell Crit",
                "dodge": "% Dodge", "haste": "% Haste"}


def bonus_text(stat_bonuses):
    """'+3 Stamina, +2 Health per turn' - one wording for the log, the bag and the recipe list."""
    parts = []
    for key, value in (stat_bonuses or {}).items():
        label = BONUS_LABELS.get(key, key.replace("_", " ").title())
        parts.append(f"+{value}{label}" if label.startswith("%") else f"+{value} {label}")
    return ", ".join(parts)


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
        # NOTE: icon_id is a derived property further down, not a stored
        # field - see its docstring for why.
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
        if getattr(character, "current_health", 1) <= 0:
            return False   # no potion, bandage or meal raises the dead - only a res does
        # FOOD AND DRINK ARE NOT ON THE POTION COOLDOWN, and they do not set it. They fill different
        # bars and you are meant to be able to do both at once - the first build shared the cooldown,
        # so drinking while eating silently did nothing: no log line, no mana, no error. Their cost is
        # the twenty seconds of standing still, not a cooldown.
        if character.consumable_cooldown > 0 and self.consumable_type not in ("meal", "drink"):
            return False
        if self.buff_category == "guardian" and character.guardian_buff is not None:
            return False  # Can't stack two guardian elixirs
        if self.buff_category == "battle" and character.battle_buff is not None:
            return False  # Can't stack two battle elixirs
        # A cooked meal is a "meal" first: you can always start eating, even with a Well Fed buff
        # already up. The slot check only blocks a second STAT-ONLY food, which is what it was for.
        if (self.buff_category == "food" and character.food_buff is not None
                and self.consumable_type != "meal"):
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
            bonus_str = bonus_text(self.stat_bonuses)
            log_msg = f"Drank {self.name}: {bonus_str}"
        
        elif self.consumable_type == "food":
            # Food buffs go in the food slot - same flat-value treatment as elixirs.
            character.apply_consumable_buff("food", self)
            bonus_str = bonus_text(self.stat_bonuses)
            log_msg = f"Ate {self.name}: {bonus_str} for {self.effect_duration}s"
        
        elif self.consumable_type in ("meal", "drink"):
            # Sit down and get the bar back. effect_value is the TOTAL restored and effect_duration
            # is how long it takes - the slowness is the cost, and it is why this is cheap and a
            # potion is not.
            kind = "meal" if self.consumable_type == "meal" else "drink"
            character.start_consumable_regen(kind, self.effect_value, self.effect_duration, self.name)
            verb = "Eating" if kind == "meal" else "Drinking"
            bar = "health" if kind == "meal" else "mana"
            log_msg = (f"{verb} {self.name}: {self.effect_value} {bar} over "
                       f"{int(self.effect_duration)}s. Stops if you take a hit.")
            # A COOKED meal carries the Well Fed buff on top of the regen, which is the entire reason
            # to cook rather than buy. Vendor meals have no stat_bonuses and skip this.
            # WELL FED LASTS HALF AN HOUR, as every meal's description says. It was applied with
            # effect_duration - the twenty-odd seconds the meal takes to eat - so the buff was
            # gone before the next pull and cooked food looked like it gave nothing (Kyle, 12 Nov:
            # "Also food should give buffs!").
            if self.stat_bonuses and self.buff_category == "food":
                character.apply_consumable_buff("food", self, seconds=WELL_FED_SECONDS)
                log_msg += f" Well fed: {bonus_text(self.stat_bonuses)} for 30 minutes."

        elif self.consumable_type == "ammo":
            # Crafted arrows / bolts (Woodworking): a timed ranged-attack buff in its own slot, since the game has
            # no ammunition mechanic.  Same flat-value treatment as elixirs and food.
            character.apply_consumable_buff("ammo", self)
            bonus_str = bonus_text(self.stat_bonuses)
            log_msg = f"Nocked {self.name}: {bonus_str} for {int(self.effect_duration)}s"

        else:
            return False
        
        # Consume the item
        self.quantity -= 1
        if self.consumable_type not in ("meal", "drink"):
            character.consumable_cooldown = self.cooldown_seconds
        
        if combat_log is not None:
            combat_log.append(log_msg)
        
        return True

    @property
    def icon_id(self):
        """The icon file stem for this consumable, or None if it has no art.

        Derived from consumable_id rather than stored, for two reasons:

        1. No save migration. Every Consumable in every existing save picks
           up its art the moment the files land, including ones built by
           from_dict from a save written before the art existed.
        2. No drift. A stored icon_id in the JSON (68 entries) would have to
           be kept in step by hand every time a consumable is renamed or a
           power tier is added; deriving it means consumable_icons.py is the
           single place the mapping lives.

        The UI reads this through icon_ui_helper.get_item_icon_surface, which
        already does getattr(consumable, "icon_id", None), so nothing on the
        rendering side needed changing.
        """
        from entities.consumable_icons import icon_for
        return icon_for(self.consumable_id)

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
