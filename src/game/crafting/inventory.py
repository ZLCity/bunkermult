from collections import defaultdict
from .item import Item

class Inventory:
    """Stores items and manages quantities."""
    def __init__(self):
        # defaultdict makes it easier to add new items without checking if the key exists
        self.items = defaultdict(int)

    def add(self, item: Item, quantity: int = 1):
        """Adds a given quantity of an item to the inventory."""
        if quantity < 0:
            # For a real game, this might raise an error instead of printing
            print("Error: Cannot add a negative quantity.")
            return
        self.items[item] += quantity

    def remove(self, item: Item, quantity: int = 1) -> bool:
        """Removes a given quantity of an item. Returns False if not enough items."""
        if quantity < 0:
            print("Error: Cannot remove a negative quantity.")
            return False
        if self.items[item] >= quantity:
            self.items[item] -= quantity
            # Clean up the dictionary if an item's count reaches zero
            if self.items[item] == 0:
                del self.items[item]
            return True
        return False

    def has_items(self, items_to_check: dict[Item, int]) -> bool:
        """Checks if the inventory contains at least the required quantities of items."""
        for item, required_quantity in items_to_check.items():
            if self.items[item] < required_quantity:
                return False
        return True

    def __str__(self) -> str:
        if not self.items:
            return "Inventory is empty."
        # Creates a nicely formatted string of inventory contents
        item_strings = [f"- {item}: {quantity}" for item, quantity in self.items.items()]
        return "Inventory contents:\n" + "\n".join(item_strings)
