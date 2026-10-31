"""Coin display. Kept as a name the UI already imports; entities/coins.py owns the arithmetic."""
from entities.coins import coins


def format_coins(copper):
    """"3s", "1g 5c", "0c" - zero parts skipped."""
    return coins(copper)
