import sys
import os

# Add the 'src' directory to the Python path to allow for absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from game.crafting import Item, Recipe, Inventory, craft

def run_test():
    """
    Runs the same simulation as the original prototype to test the refactored code.
    """
    # --- Item Definitions (from GDD) ---
    biomass = Item("Biomass")
    fibrous_flora = Item("Fibrous Flora")
    raw_ore = Item("Raw Ore")
    water = Item("Water")
    chitinous_plate = Item("Chitinous Plate")
    conductive_gel = Item("Conductive Gel")
    metal_ingot = Item("Metal Ingot")

    # --- Recipe Definitions ---
    plate_recipe = Recipe(inputs={biomass: 10}, outputs={chitinous_plate: 1})
    gel_recipe = Recipe(inputs={fibrous_flora: 5, water: 2}, outputs={conductive_gel: 1})
    ingot_recipe = Recipe(inputs={raw_ore: 5}, outputs={metal_ingot: 1})

    # --- Gameplay Simulation ---
    print("--- Testing Refactored Astromorph Crafting ---")
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

    print("\n--- Refactoring test finished successfully. ---")

if __name__ == "__main__":
    run_test()
