from .inventory import Inventory
from .recipe import Recipe

def craft(inventory: Inventory, recipe: Recipe) -> bool:
    """
    Attempts to craft an item based on a recipe and an inventory.
    Manages resource consumption and item production.
    """
    # 1. Check if there are enough resources
    if not inventory.has_items(recipe.inputs):
        print(f"Crafting failed: Not enough resources for recipe {recipe.outputs}.")
        for item, required in recipe.inputs.items():
            # Check current inventory amount, defaulting to 0 if not present
            current_amount = inventory.items.get(item, 0)
            if current_amount < required:
                print(f"  Missing {required - current_amount} of {item.name}")
        return False

    # 2. Consume input resources
    print("Consuming inputs...")
    for item, quantity in recipe.inputs.items():
        if inventory.remove(item, quantity):
             print(f"  -{quantity} {item.name}")

    # 3. Add output items
    print("Producing outputs...")
    for item, quantity in recipe.outputs.items():
        inventory.add(item, quantity)
        print(f"  +{quantity} {item.name} added. Total: {inventory.items[item]}.")

    print("Crafting successful!")
    return True
