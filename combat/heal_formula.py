"""THE HEALING FORMULA (Kyle, 16 Nov 2026). docs/heal_formula.md has the measurements and the sign-off.

Kyle: "a spot heal from a non-spec'd character shouldn't heal 80% tank HP and like 200% boss damage", "we need an
actual formula and do it right". He set the shares: "20 unspecced is fine. 2 is fine with 40 and 25%".

Everything is a share of T(L), the max health of a geared Protection Warrior of level L
(data/balance/heal_reference.json, written by tools/calibrate_heal_reference.py):

    heal = ( BARE_SHARE x T(Lrank) x S x A x W          the rank: what training the spell gives you
           + healing power x COEF x S x A x W )         gear: rare gear at your level adds GEAR_SHARE of the base
           x spec                                       talents and the spec aura together, capped at SPEC_CAP
           x crit                                       x1.5 on a crit, with no crit-damage talents

  Lrank  the level the rank is learned at (an outlevelled rank falls behind as T grows; downranking keeps its
         penalty on the power part, combat/ability_scaling.py)
  S      cast speed: quick 0.6, normal 1.0, slow 1.5 (combat/abilities.CAST_SPEEDS)
  A      area: one target 1.0; the party 0.45 each, two or three 0.6 each, after combat's own AoE share
  W      cooldown weight: a heal you can only cast every few turns is bigger (ability_scaling.cooldown_weight)

  A HoT totals HOT_FACTOR of the heal it would be, over its whole duration. A heal riding on a damage spell
  (heal_value: Frostfall, the Cryotherapist's converted nukes) is HYBRID_FACTOR of a heal.

A SPELL KEEPS ITS CHARACTER. The formula sets the size; each spell's own authored size, against the authored line for
its shape, is kept as a nudge of IDENTITY_RANGE either way. So a heal the designer made deliberately small (it has a
rider) or big stays a little small or big, but nothing is 3x what its shape says any more.
"""
import json
from pathlib import Path

BARE_SHARE = 0.20       # a normal-speed, single-target, top-rank heal with no talents and no gear: 20% of the tank
GEAR_SHARE = 0.40       # rare gear at your level adds 40% of that
SPEC_CAP = 1.25         # every healing talent and the spec aura together: at most +25%
#: a HoT, in total over its duration. 1.2 in the sign-off; measured the same night, every healer whose kit rolls
#: several HoTs at once (Vizier's three, the Sun Cleric's two, the Chronomancer's Accelerated Recovery) out-healed the
#: rest by a quarter to a third, because each cast of a HoT was worth 1.2 heals and they stack. At 1.0 a HoT is a
#: heal delivered later, which is what it is in a turn-based fight.
HOT_FACTOR = 1.0
HYBRID_FACTOR = 0.75    # the heal on a damage spell
#: narrowed the night it went in (the every-healer pass): at 0.8-1.25 a class's core heal could sit a fifth under its
#: shape (Pyromancer's Ember Touch, the Witch Doctor's Loa's Brew) and a big cooldown heal a quarter over (Alkahest)
IDENTITY_RANGE = (0.9, 1.15)
EXPLICIT_RANGE = (0.75, 1.35)
HEAL_CRIT_MULTIPLIER = 1.5   # a critical heal, flat (damage crits 2.0x and takes crit-damage talents; heals don't)
#: the authored rank line (fix_rank_lines.py): a rank is (1 + AUTHORED_SLOPE x (level - 1)) of its rank-1 size
AUTHORED_SLOPE = 0.03636

_REF = None


def _ref():
    global _REF
    if _REF is None:
        try:
            _REF = json.loads((Path(__file__).resolve().parent.parent / "data/balance/heal_reference.json")
                              .read_text(encoding="utf-8"))
        except (OSError, ValueError):
            _REF = {}
    return _REF


def _at(table, level):
    if not table:
        return None
    lv = max(1, min(int(level or 1), max(int(k) for k in table)))
    return float(table.get(str(lv)) or table[max(table, key=lambda k: int(k))])


def tank(level):
    """T(L): a geared same-level tank's max health."""
    return _at(_ref().get("tank"), level)


def healing_power(level):
    """The median geared healer's healing power at this level (combat scale)."""
    return _at(_ref().get("healing_power"), level)


def coefficient():
    """COEF: healing power x COEF = GEAR_SHARE of the base, for rare gear at 60 (lower levels have less gear, so
    gear is a little under 40% of the heal there, as in WoW). 1.2 if the table is missing."""
    t, hp = tank(60), healing_power(60)
    if not t or not hp:
        return 1.2
    return GEAR_SHARE * BARE_SHARE * t / hp


def enabled():
    return bool(_ref().get("tank")) and bool(_ref().get("authored"))


#: per-target share of a heal that lands on several people, BEFORE combat's own 0.6 for a heal that reaches more than
#: one (Ability.AOE_DAMAGE_MULTIPLIER, heals and HoTs alike): the party 0.75 x 0.6 = 0.45 each, two or three 0.6 each
PARTY_AREA, SMALL_AREA = 0.75, 1.0


def area(entry):
    many = (entry.get("target_type") == "party" or entry.get("heal_scope") == "party")
    if not many:
        return 1.0
    n = entry.get("max_targets") or entry.get("max_recipients")
    return SMALL_AREA if n and n <= 3 else PARTY_AREA


def shape(entry):
    """S x A x W for this ability."""
    from combat.abilities import cast_speed_value
    from combat.ability_scaling import cooldown_weight
    return cast_speed_value(entry.get("cast_speed")) * area(entry) * cooldown_weight(entry.get("cooldown", 0))


KIND_FACTOR = {"heal": 1.0, "hot": HOT_FACTOR, "heal_value": HYBRID_FACTOR}


def rank_size(entry, level_req, authored, kind):
    """The formula's size for one rank of a heal (kind "heal", "hot" or "heal_value"), keeping a nudge of the
    authored value's identity. None when the table is missing (the caller keeps its old rule)."""
    if not enabled() or not authored:
        return None
    t = tank(level_req)
    line = (_ref()["authored"].get(kind) or 0) * (1 + AUTHORED_SLOPE * (max(1, level_req or 1) - 1))
    sh = shape(entry)
    target = BARE_SHARE * t * sh * KIND_FACTOR[kind]
    if line <= 0 or sh <= 0:
        return max(1, int(round(target)))
    identity = authored / (line * sh)
    lo, hi = IDENTITY_RANGE
    # A KIT FIXED BY HAND (the every-healer pass): an ability may name its own identity, "formula_identity", where its
    # class leans on it (Pyromancer's Ember Touch) and the authored number undersold it. Held to EXPLICIT_RANGE.
    if entry.get("formula_identity") is not None:
        identity, (lo, hi) = float(entry["formula_identity"]), EXPLICIT_RANGE
    return max(1, int(round(target * max(lo, min(hi, identity)))))


# ---- TALENT ECHOES COUNT AGAINST THE SAME +25% (Kyle: "spec +25%")
# A talent can add to a heal two ways: make the number bigger (inside Ability._damage_multiplier, capped at SPEC_CAP)
# or set off a second heal off the first ("Emergency Enhancer: heals your most wounded ally for 90% of the amount",
# Eureka!, Ancestral Awakening, the bonus_pct procs). Measured before the cap: a Tinker's Zap! plus its echoes landed
# 3.9x the Zap. So a heal cast opens a ROOM of what its talents have left under the cap, and every echo it sets off
# comes out of that room: (SPEC_CAP / the cast's own talent multiplier - 1) x what the cast healed.
ECHO_TRIGGERS = ("on_heal_cast", "on_crit", "on_cast")


def open_echo_room(caster, healed, spec_mult):
    """Called by a heal cast just before its procs fire."""
    try:
        caster._heal_echo_room = max(0.0, (SPEC_CAP / max(1e-6, spec_mult) - 1.0) * max(0, healed))
    except AttributeError:
        pass


def close_echo_room(caster):
    try:
        caster._heal_echo_room = None
    except AttributeError:
        pass


def take_echo(carrier, trigger, amount):
    """How much of an echo heal of `amount` may land. Unlimited outside a heal cast's own procs."""
    room = getattr(carrier, "_heal_echo_room", None)
    trig = getattr(trigger, "value", trigger)
    if room is None or trig not in ECHO_TRIGGERS:
        return amount
    allowed = int(min(amount, room))
    carrier._heal_echo_room = room - allowed
    return allowed


# ---- SHIELDS ON THE SAME SCALE (the every-healer pass). A shield cast on someone else soaks SHIELD_FACTOR of the
# heal of its shape: it can't overheal, so it's a little smaller. Before, an ally shield was a flat share of the
# recipient's health (Power Word: Shield 30%, Void Shield 18%, Inferno Barrier 16%), the same naked or geared, at 6
# or at 60, and with no healing power in it at all. A shield on yourself (Ice Barrier, Volcanic Shell) is a defensive
# cooldown, not healing, and keeps its share of your own health.
SHIELD_FACTOR = 0.9


def shield_size(ability, caster):
    """The absorb of a shield ability cast on an ally or the party. None when it isn't one (the caller keeps the
    share-of-health rule), or the table is missing."""
    if not enabled() or getattr(ability, "target_type", None) not in ("ally", "party"):
        return None
    if not hasattr(caster, "talent_trees"):          # a monster's or a pet's shield keeps its rule
        return None
    from combat.abilities import _heal_power, _scaling_coef
    try:
        lv = ability.current_rank.get("level_req", 1) or 1
    except Exception:                                   # noqa: BLE001
        lv = getattr(caster, "level", 1) or 1
    entry = {"cast_speed": getattr(ability, "cast_speed", 1.0) or 1.0, "target_type": ability.target_type,
             "heal_scope": getattr(ability, "heal_scope", None), "max_targets": getattr(ability, "max_targets", None),
             "cooldown": getattr(ability, "cooldown", 0)}
    sh = shape(entry)
    base = BARE_SHARE * tank(lv) * sh
    power = _heal_power(caster) * _scaling_coef(ability, "heal", caster)
    return max(1, int((base + power) * SHIELD_FACTOR))
