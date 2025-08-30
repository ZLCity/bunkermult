from collections import defaultdict

# --- 1. Data Structures ---

class Item:
    """Represents a unique item or resource in the game."""
    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        # Using name for representation to make inventory printouts cleaner
        return self.name

    # The following methods are crucial for using Item objects as dictionary keys
    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other) -> bool:
        return isinstance(other, Item) and self.name == other.name

class Recipe:
    """Defines the inputs and outputs for a crafting process."""
    def __init__(self, inputs: dict[Item, int], outputs: dict[Item, int]):
        self.inputs = inputs
        self.outputs = outputs

    def __repr__(self) -> str:
        return f"Recipe(in: {self.inputs}, out: {self.outputs})"

class Inventory:
    """Stores items and manages quantities."""
    def __init__(self):
        # defaultdict makes it easier to add new items without checking if the key exists
        self.items = defaultdict(int)

    def add(self, item: Item, quantity: int = 1):
        """Adds a given quantity of an item to the inventory."""
        if quantity < 0:
            print("Error: Cannot add a negative quantity.")
            return
        self.items[item] += quantity
        print(f"+{quantity} {item.name} added. Total: {self.items[item]}.")

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

# --- 2. Crafting Logic ---

def craft(inventory: Inventory, recipe: Recipe) -> bool:
    """
    Attempts to craft an item based on a recipe and an inventory.
    Manages resource consumption and item production.
    """
    # 1. Check if there are enough resources
    if not inventory.has_items(recipe.inputs):
        print(f"Crafting failed: Not enough resources for recipe {recipe.outputs}.")
        # For more detailed feedback, we could specify which resource is missing
        for item, required in recipe.inputs.items():
            if inventory.items[item] < required:
                print(f"  Missing {required - inventory.items[item]} of {item.name}")
        return False

    # 2. Consume input resources
    print("Consuming inputs...")
    for item, quantity in recipe.inputs.items():
        inventory.remove(item, quantity)
        print(f"  -{quantity} {item.name}")

    # 3. Add output items
    print("Producing outputs...")
    for item, quantity in recipe.outputs.items():
        inventory.add(item, quantity)

    print("Crafting successful!")
    return True

# --- 3. Demonstration ---

if __name__ == "__main__":
    # --- Item Definitions (from GDD) ---
    # Tier 0
    biomass = Item("Biomass")
    fibrous_flora = Item("Fibrous Flora")
    raw_ore = Item("Raw Ore")
    water = Item("Water")

    # Tier 1
    chitinous_plate = Item("Chitinous Plate")
    conductive_gel = Item("Conductive Gel")
    metal_ingot = Item("Metal Ingot")

    # --- Recipe Definitions ---
    # Let's assume some ratios for the prototype
    plate_recipe = Recipe(inputs={biomass: 10}, outputs={chitinous_plate: 1})
    gel_recipe = Recipe(inputs={fibrous_flora: 5, water: 2}, outputs={conductive_gel: 1})
    ingot_recipe = Recipe(inputs={raw_ore: 5}, outputs={metal_ingot: 1}) # A simple smelting recipe

    # --- Gameplay Simulation ---
    print("--- Astromorph Crafting Prototype ---")
    player_inventory = Inventory()
    player_inventory.add(biomass, 25)
    player_inventory.add(fibrous_flora, 12)
    player_inventory.add(water, 5)

    print("\n--- Initial State ---")
    print(player_inventory)

    print("\n--- Attempting to craft 1 Chitinous Plate ---")
    craft(player_inventory, plate_recipe)
    print("\nInventory after crafting:")
    print(player_inventory)

    print("\n--- Attempting to craft another Chitinous Plate ---")
    craft(player_inventory, plate_recipe)
    print("\nInventory after crafting:")
    print(player_inventory)

    print("\n--- Attempting to craft a third Plate (should fail) ---")
    craft(player_inventory, plate_recipe)
    print("\nInventory state (should be unchanged):")
    print(player_inventory)

    print("\n--- Attempting to craft Conductive Gel ---")
    craft(player_inventory, gel_recipe)
    print("\nInventory after crafting:")
    print(player_inventory)

    print("\n--- Prototype simulation finished. ---")
