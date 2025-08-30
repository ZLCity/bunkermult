import sys
import os
import time

# Add the 'src' directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from game.world import Grid
from game.crafting import Item, Recipe, Inventory
from game.structures import BioForge, PulsatingVein

class Chest:
    """A simple destination object for items, acting as a warehouse."""
    def __init__(self):
        self.inventory = Inventory()
        self.x = -1
        self.y = -1

    def accept_item(self, item: Item) -> bool:
        self.inventory.add(item, 1)
        print(f"Chest at ({self.x}, {self.y}) received {item.name}!")
        return True

    def update(self, grid):
        # Chests are passive, they don't do anything on their own
        pass

    def __str__(self):
        return "[ C ]"

def run_full_simulation():
    print("--- Full System Simulation (Forge -> Conveyor -> Chest) ---")

    # 1. Define Items and Recipes
    raw_ore = Item("Raw Ore")
    metal_ingot = Item("Metal Ingot")
    ingot_recipe = Recipe(inputs={raw_ore: 2}, outputs={metal_ingot: 1})

    # 2. Setup the Grid and Structures
    grid = Grid(width=5, height=6)

    # Forge will output downwards (0, 1)
    forge = BioForge(recipe=ingot_recipe, processing_time=3, output_direction=(0, 1))

    # Conveyors also point downwards
    conveyor1 = PulsatingVein(direction=(0, 1), speed=2)
    conveyor2 = PulsatingVein(direction=(0, 1), speed=2)

    chest = Chest()

    # Place objects on the grid
    grid.place_object(forge, 2, 1)
    grid.place_object(conveyor1, 2, 2)
    grid.place_object(conveyor2, 2, 3)
    grid.place_object(chest, 2, 4)

    print("\nInitial Grid Layout:")
    grid.display()

    # 3. Start the simulation
    print("\n>>> Player adds 5 Raw Ore to the Bio-Forge.")
    forge.add_to_input(raw_ore, 5)

    print("\n--- Starting Game Loop (15 ticks) ---")
    for tick in range(1, 16):
        print(f"\n--- Tick {tick} ---")
        # In a real game, the grid's update method would be the heart of the game loop
        grid.update_all()
        grid.display()
        time.sleep(0.2)

    print("\n--- Simulation Finished ---")
    print(f"Final Chest Inventory: {dict(chest.inventory.items)}")

    # Verify the result
    final_ingots = chest.inventory.items.get(metal_ingot, 0)
    print(f"Test Result: {'Success' if final_ingots == 2 else 'Failure'}")


if __name__ == "__main__":
    run_full_simulation()
