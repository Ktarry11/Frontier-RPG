"""Coin display: 100 copper = 1 silver, 100 silver = 1 gold. Zero parts are skipped ("3s", "1g 5c", "0c")."""


def format_coins(copper):
    g, rem = divmod(max(0, int(copper)), 10000)
    s, c = divmod(rem, 100)
    parts = ([f"{g}g"] if g else []) + ([f"{s}s"] if s else []) + ([f"{c}c"] if c else [])
    return " ".join(parts) or "0c"
