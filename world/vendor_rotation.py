"""Hidden sellers turn their shelves over every twelve market hours.

Kyle, 17 Nov 2026, at a hidden seller: "we have rotating stock in these secret vendors....like they have 6 or 7 blue
items but only 3 to 4 are at once. They can follow 12 hour rotations with the time passing like how the AH passes. So
it rewards returning to them."

THE CLOCK is the market's (world/market/market.py): it moves with play time (an hour per 150 seconds), quests, the
last boss of a dungeon and the hearthstone, so a seller's shelf turns over at the same pace the auction house does.

THE SHELF. A hidden seller carries a pool of one-of-a-kind items ("unique:..." in its sells list) and shows SHOWN of
them at a time. Which ones is decided by the seller and the twelve-hour window it's in, from a fixed seed: the same
window always shows the same items (close the shop and open it again, nothing reshuffles; load a save, the same),
and the next window draws again. Recipes, food and anything else on the shelf are always there; only the
one-of-a-kind gear rotates. A seller with SHOWN or fewer shows all of them.

Reputation quartermasters list "unique:" items too, and never rotate: a reward you earned is always for sale.
"""
import random
import zlib

ROTATION_HOURS = 12
SHOWN = 4


def window(clock):
    return int((clock or 0.0) // ROTATION_HOURS)


def hours_left(clock):
    """Market hours until this window's shelf turns over."""
    return ROTATION_HOURS - ((clock or 0.0) % ROTATION_HOURS)


def rotates(vendor):
    return bool(getattr(vendor, "hidden", False))


def shelf(vendor, stock, clock):
    """The sells list as the shelf shows it in this window: every non-unique entry, and SHOWN of the uniques."""
    stock = list(stock)
    if not rotates(vendor):
        return stock
    uniques = [s for s in stock if isinstance(s, str) and s.startswith("unique:")]
    if len(uniques) <= SHOWN:
        return stock
    seed = zlib.crc32(f"{getattr(vendor, 'vendor_id', '')}:{window(clock)}".encode("utf-8"))
    pick = set(random.Random(seed).sample(uniques, SHOWN))
    return [s for s in stock if not (isinstance(s, str) and s.startswith("unique:")) or s in pick]


def clock_for(state_manager):
    """The market clock, or 0 when there's no party yet (a test, the title screen)."""
    try:
        from world.market.market import market_of
        party = state_manager.get_party() if hasattr(state_manager, "get_party") else None
        return float(market_of(party).clock) if party is not None else 0.0
    except Exception:                                   # noqa: BLE001 - a shelf must open whatever the market is doing
        return 0.0
