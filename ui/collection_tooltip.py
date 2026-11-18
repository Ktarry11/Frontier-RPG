"""The card for a collectable in your bags, on the auction house or in a letter (docs/collection_design.md).

One function, shared, so the bag's card and the auction house's card can't drift apart.
"""

GREY, GREEN, GOLD, BLUE = (170, 170, 170), (120, 220, 140), (230, 200, 120), (130, 180, 220)
TAB_WORD = {"mount": "Mount", "form": "Form", "travel": "Travel", "tome": "Tome", "service": "Service",
            "heirloom": "Heirloom"}


def collection_lines(item):
    """[(text, colour)] for a collectable item."""
    from world.collection import get_entry, learned, art_ready
    cid = getattr(item, "collection_id", None)
    e = get_entry(cid) or {}
    try:
        colour = tuple(item.get_rarity_color())
    except Exception:
        colour = (255, 255, 255)
    out = [(getattr(item, "name", "Collectable"), colour),
           (f"Collection: {TAB_WORD.get(e.get('kind'), 'Collectable')}", BLUE),
           (e.get("blurb", ""), GREY)]
    if e.get("kind") == "mount":
        out.append(("Learned for every character. Still needs the riding skill.", GREY))
    elif e.get("kind") == "form":
        out.append(("The party leader walks the map in this form. Looks only.", GREY))
    elif e.get("kind") == "heirloom":
        out.append(("Any character can take a copy from the Collection.", GREY))
    if e.get("needs_art") and not art_ready(cid):
        out.append(("Its art isn't in the game yet: you can learn it now and use it when it lands.", GOLD))
    if learned(cid):
        out.append(("You already know this. It can still be sold.", GOLD))
    else:
        out.append(("Right-click to learn it for every character.", GREEN))
    return out
