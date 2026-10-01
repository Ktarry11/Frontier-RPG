"""
Turn meter system. Continuous meter-based turn order (Fear & Hunger style).
Characters accumulate turn meter at different rates based on AGI and Haste.
"""
from config import TURN_THRESHOLD, AGI_TO_TURN_SPEED


class TurnMeter:
    """Manages turn order for a group of combatants."""
    
    def __init__(self, combatants):
        """Initialize turn meter with list of characters."""
        self.combatants = combatants  # List of Character objects
        self.turn_queue = []  # Characters waiting for their turn
        self.current_turn_char = None
        
        # Initialize turn meters for all combatants
        for char in combatants:
            char.turn_meter = 0.0
            self._refresh_turn_speed(char)

    @staticmethod
    def _refresh_turn_speed(char):
        """Recompute char.turn_speed from current Agility/speed AND Haste.

        THE ACTUAL FIX: turn_speed used to be set ONCE here at combat
        start from Agility/speed alone and never touched again - so
        Haste (a real, displayed character stat computed from Intellect+
        Agility, see Character._recalculate_derived_stats) had genuinely
        no effect on anything. A Hunter stacking Haste talents (Icy
        Veins-style buffs, Improved Aspect of the Hawk, etc) gained a
        bigger number on their character sheet and nothing else.

        Haste is treated as a percentage bonus on top of the base
        Agility-derived speed, matching how it's already computed and
        displayed elsewhere (Character.haste is stored as a percentage-
        like value, e.g. "20" meaning +20%) - consistent with how
        stat_mods keys like "crit_chance_spell" already use a 0-100 scale
        rather than a 0.0-1.0 fraction.

        Called every tick (see update() below) rather than once, so a
        buff or debuff that changes Agility or Haste mid-fight (Icy
        Veins, a slow debuff, Frenzy) takes effect on the very next
        meter tick - not frozen at whatever it was when combat started.
        """
        if hasattr(char, "agility"):
            base_speed = 1.0 + (char.agility / 100.0)
        elif hasattr(char, "speed"):
            base_speed = char.speed
        else:
            base_speed = 1.0

        haste_pct = getattr(char, "haste", 0.0)
        # Status-effect haste mods (a debuff reducing Haste, e.g. this
        # session's Concussion Blow/Shockwave placeholders) stack on top
        # of the character's own computed Haste stat, same as any other
        # stat_mod.
        if hasattr(char, "get_status_stat_mod"):
            haste_pct += char.get_status_stat_mod("haste")

        char.turn_speed = base_speed * (1.0 + haste_pct / 100.0)
    
    def update(self, dt):
        """Advance turn meters. Returns character who should act next (or None)."""
        # Increment turn meters based on turn speed
        for char in self.combatants:
            if char.is_alive() and not getattr(char, "is_stunned", False):
                self._refresh_turn_speed(char)
                char.turn_meter += (char.turn_speed * AGI_TO_TURN_SPEED * 100.0 * dt)
        
        # Find next character to act
        next_char = None
        for char in self.combatants:
            if char.is_alive() and char.turn_meter >= TURN_THRESHOLD:
                if next_char is None or char.turn_meter > next_char.turn_meter:
                    next_char = char
        
        return next_char
    
    def consume_turn(self, char):
        """Character takes their turn. Reset their meter to whatever
        overflowed past the threshold, not a hard 0.

        A character with enough Haste can accumulate meter well past
        TURN_THRESHOLD in a single tick (e.g. two turns' worth at once) -
        resetting straight to 0 every time would throw away that
        overflow and silently cap effective haste at "one turn per
        threshold crossing," which defeats the point of building Haste
        in the first place. Carrying the remainder forward means a
        high-Haste character genuinely can end up acting again sooner,
        which is the real translation of "extra actions" into this
        meter-based (rather than fixed-round) turn system.
        """
        if char in self.combatants:
            char.turn_meter = max(0.0, char.turn_meter - TURN_THRESHOLD)
    
    def get_turn_order_preview(self):
        """Return sorted list of characters by turn meter (for UI display)."""
        alive_chars = [c for c in self.combatants if c.is_alive()]
        return sorted(alive_chars, key=lambda c: c.turn_meter, reverse=True)
