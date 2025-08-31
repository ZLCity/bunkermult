import sys
import os
import time

# Add the 'src' directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from game.crafting import Item, Recipe
from game.structures.bio_forge import BioForge

def run_simulation():
    """
    Simulates a simple game loop to test the BioForge's functionality.
    """
    print("--- Bio-Forge Simulation ---")

    # 1. Setup Environment
    raw_ore = Item("Raw Ore")
    metal_ingot = Item("Metal Ingot")
    ingot_recipe = Recipe(inputs={raw_ore: 5}, outputs={metal_ingot: 1})

    # Create a Bio-Forge that takes 5 ticks to process one batch of ingots
    smelting_forge = BioForge(recipe=ingot_recipe, processing_time=5, output_direction=(0, 1), power_consumption=10)

    print("Created a Bio-Forge for smelting ore.")
    print(smelting_forge)

    # 2. Player Action: Add resources to the forge
    print("\n>>> Player adds 12 Raw Ore to the forge's input.")
    smelting_forge.add_to_input(raw_ore, 12)
    print(smelting_forge)

    # 3. Game Loop Simulation
    print("\n--- Starting Game Loop (20 ticks) ---")
    for tick in range(1, 21):
        print(f"\n--- Tick {tick} ---")
        # The test needs to provide the arguments the real method expects.
        # We can pass None for the grid as this test doesn't check complex ejection.
        smelting_forge.update(grid=None, has_power=True)

        # To make the simulation easier to follow
        time.sleep(0.1)

        # Let's try to add more resources mid-process
        if tick == 8:
            print("\n>>> Player adds another 5 Raw Ore to the forge.")
            smelting_forge.add_to_input(raw_ore, 5)

    print("\n--- Game Loop Finished ---\n")
    print("Final status of the forge:")
    print(smelting_forge)

    # 4. Player Action: Retrieve finished products
    print("\n>>> Player attempts to retrieve 2 Metal Ingots.")
    smelting_forge.take_from_output(metal_ingot, 2)

    print("\n>>> Player attempts to retrieve 1 more Metal Ingot (should fail).")
    smelting_forge.take_from_output(metal_ingot, 1)

    print("\nFinal status after retrieval:")
    print(smelting_forge)
    print("\n--- Simulation Complete ---")


if __name__ == "__main__":
    run_simulation()
