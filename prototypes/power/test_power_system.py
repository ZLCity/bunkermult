import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from game.world import Grid
from game.power import PowerGrid
from game.crafting import Item, Recipe
from game.structures import BioForge, PulsatingVein, BioElectricGenerator

def run_power_simulation():
    print("--- Power System Simulation ---")

    # 1. Define Items and Recipes
    biomass = Item("Biomass")
    raw_ore = Item("Raw Ore")
    metal_ingot = Item("Metal Ingot")
    ingot_recipe = Recipe(inputs={raw_ore: 1}, outputs={metal_ingot: 1})

    # 2. Setup Grids
    grid = Grid(width=5, height=4)
    power_grid = PowerGrid()

    # 3. Setup Structures
    # Generator: 10 MW output, 1 Biomass burns for 5 ticks
    generator = BioElectricGenerator(power_output=10, fuel_item=biomass, ticks_per_fuel=5)

    # Forge: Consumes 8 MW, outputs downwards
    forge = BioForge(recipe=ingot_recipe, processing_time=3, output_direction=(0, 1), power_consumption=8)

    # Conveyor: Consumes 1 MW, moves downwards
    conveyor = PulsatingVein(direction=(0, 1), power_consumption=1, speed=1)

    # Place structures on the grid
    grid.place_object(generator, 1, 1)
    grid.place_object(forge, 3, 1)
    grid.place_object(conveyor, 3, 2)

    # Add structures to the power grid
    power_grid.add_producer(generator)
    power_grid.add_consumer(forge)
    power_grid.add_consumer(conveyor)

    print("\nInitial Grid Layout:")
    grid.display()

    # 4. Start Simulation
    print("\n>>> Player adds 1 Biomass to Generator and 2 Raw Ore to Forge.")
    generator.add_fuel(1)
    forge.add_to_input(raw_ore, 2)

    # Run for 15 ticks to see power on, off, and on again
    for tick in range(1, 16):
        print(f"\n--- Tick {tick} ---")

        # In a real game, this would be the main game loop call
        grid.update_all(power_grid)

        grid.display()

        # Simulate adding more fuel after power goes out
        if tick == 7:
            print("\n>>> Player adds 2 more Biomass to Generator.")
            generator.add_fuel(2)

        time.sleep(0.2)

    print("\n--- Simulation Finished ---")

if __name__ == "__main__":
    run_power_simulation()
