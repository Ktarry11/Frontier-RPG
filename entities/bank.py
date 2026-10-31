"""
The bank - shared, tabbed overflow storage.

Kyle, 2026-10-28: "i think we should add a bank bro. Since we are getting a lot of stuff... It can
originally start with 48 slots. We can buy new tabs that will each hold 48."

SHARED, NOT PER-CHARACTER. In WoW a bank belongs to one character; here it belongs to the PARTY, and it
sits next to the purse for exactly the reason the purse sits there. This game's party is a roster you
swap, not four separate people with separate lives - currency is already shared, companions already pass
gear around, and a per-character bank would mean the item you wanted was behind whichever companion you
left on the bench. Party is where "ours" lives, so the bank lives there.

TABS ARE BOUGHT, NOT EARNED. Seven of them at 48 slots each, the first free and the rest on Kyle's
price curve: 10g, 50g, 100g, 250g, 500g, 1000g. That is a 1910g lifetime cost for 336 slots, and the
shape of the curve is the point - the second tab is pocket change by the time you want it and the
seventh is a genuine goal. Prices are held in COPPER here, because that is the only currency unit the
rest of the game has (Party.copper; 10000 copper to the gold), and writing them in gold in one place and
copper everywhere else is how a pricing bug gets in.

Items are stored exactly as the inventory stores them - Item or LootItem, serialized with to_dict() and
rebuilt by the same "slot" key sniff Character.from_dict uses. A bank that invented its own item format
would be a second thing to keep in step with every future item field.
"""

#: Slots per tab. One number, used by the model, the UI and the QA - a bank whose UI believes in a
#: different grid size than its storage is a dupe bug waiting to happen.
SLOTS_PER_TAB = 48

#: Price of each tab in COPPER, index 0 being the first tab. 10000 copper = 1 gold (Party.copper).
#: Kyle's curve: free, 10g, 50g, 100g, 250g, 500g, 1000g.
TAB_PRICES = [0, 10 * 10000, 50 * 10000, 100 * 10000, 250 * 10000, 500 * 10000, 1000 * 10000]

MAX_TABS = len(TAB_PRICES)

#: Shown on the tab strip. Flavour only - MerchantTusk names his own shelves and nobody asked him to.
TAB_NAMES = [
    "Strongbox",
    "Second Shelf",
    "Third Shelf",
    "Back Room",
    "Deep Vault",
    "The Good Vault",
    "Tusk's Own",
]


def gold_str(copper):
    """'1000g' / '10g 50s'. entities/coins.py owns the split; this is the name the bank imports."""
    from entities.coins import coins
    return coins(copper)


class Bank:
    """Tabbed shared storage. Owns no UI and no currency - it is told what has been paid for."""

    def __init__(self, tabs_owned=1):
        self.tabs_owned = max(1, min(int(tabs_owned), MAX_TABS))
        #: One list per OWNED tab, each a sparse list of SLOTS_PER_TAB entries (None = empty slot).
        #: Sparse rather than append-only so an item keeps the slot the player put it in - a bank that
        #: reshuffles itself every time you withdraw something is a bank nobody organises.
        self.tabs = [[None] * SLOTS_PER_TAB for _ in range(self.tabs_owned)]

    # ---------------------------------------------------------------- capacity
    @property
    def capacity(self):
        return self.tabs_owned * SLOTS_PER_TAB

    @property
    def used(self):
        return sum(1 for t in self.tabs for s in t if s is not None)

    def next_tab_price(self):
        """Copper for the next tab, or None when every tab is owned."""
        if self.tabs_owned >= MAX_TABS:
            return None
        return TAB_PRICES[self.tabs_owned]

    def buy_tab(self, party):
        """Spend from the party purse and open the next tab.

        Returns (ok, message). Takes the PARTY rather than a number so the purse debit and the tab
        opening cannot drift apart - there is no path here that opens a tab without paying, or charges
        without opening one.
        """
        price = self.next_tab_price()
        if price is None:
            return False, "Every tab is already yours."
        if party is None or party.copper < price:
            return False, f"That tab costs {gold_str(price)}."
        if not party.remove_currency(price):
            return False, f"That tab costs {gold_str(price)}."
        self.tabs_owned += 1
        self.tabs.append([None] * SLOTS_PER_TAB)
        return True, f"Opened {TAB_NAMES[self.tabs_owned - 1]} for {gold_str(price)}."

    # ---------------------------------------------------------------- moving items
    def first_free(self, tab_index=None):
        """(tab, slot) of the first empty slot, searching one tab or all of them. None if full."""
        search = [tab_index] if tab_index is not None else range(self.tabs_owned)
        for t in search:
            if not 0 <= t < self.tabs_owned:
                continue
            for i, slot in enumerate(self.tabs[t]):
                if slot is None:
                    return t, i
        return None

    def deposit(self, item, tab_index=None):
        """Put an item in. Returns (tab, slot) or None if there was no room.

        The CALLER removes it from the inventory, and only on a non-None return - doing the removal in
        here would mean a full bank silently eats the item.
        """
        spot = self.first_free(tab_index)
        if spot is None:
            return None
        t, i = spot
        self.tabs[t][i] = item
        return spot

    def withdraw(self, tab_index, slot_index):
        """Take an item out and leave the slot empty. Returns the item, or None if the slot was."""
        if not 0 <= tab_index < self.tabs_owned:
            return None
        if not 0 <= slot_index < SLOTS_PER_TAB:
            return None
        item = self.tabs[tab_index][slot_index]
        self.tabs[tab_index][slot_index] = None
        return item

    def get(self, tab_index, slot_index):
        if not 0 <= tab_index < self.tabs_owned:
            return None
        if not 0 <= slot_index < SLOTS_PER_TAB:
            return None
        return self.tabs[tab_index][slot_index]

    # ---------------------------------------------------------------- save
    def to_dict(self):
        return {
            "tabs_owned": self.tabs_owned,
            # Sparse slots are preserved by storing index -> item rather than a list with nulls, which
            # keeps a mostly-empty 336-slot bank from writing 336 nulls into every save file.
            "tabs": [{str(i): s.to_dict() for i, s in enumerate(tab) if s is not None}
                     for tab in self.tabs],
        }

    @classmethod
    def from_dict(cls, data):
        from entities.item import Item
        from entities.loot_item import LootItem

        bank = cls(tabs_owned=(data or {}).get("tabs_owned", 1))
        for t, stored in enumerate((data or {}).get("tabs", [])):
            if t >= bank.tabs_owned:
                break
            for key, raw in (stored or {}).items():
                try:
                    i = int(key)
                except (TypeError, ValueError):
                    continue
                if 0 <= i < SLOTS_PER_TAB:
                    # Same "slot" sniff Character.from_dict uses to tell gear from loot items. Keeping
                    # the two in step matters more than it looks: a bank that rebuilt everything as
                    # Item would turn stored materials into unusable gear on load.
                    bank.tabs[t][i] = Item.from_dict(raw) if "slot" in raw else LootItem.from_dict(raw)
        return bank
