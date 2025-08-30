import sys
import os

# This is a temporary solution for the prototype to ensure imports work from other directories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from game.crafting import Inventory, Recipe, Item

class BioForge:
    """
    An automated structure that processes a specific recipe over time.
    It has an input inventory for raw materials and an output inventory for finished goods.
    """
    def __init__(self, recipe: Recipe, processing_time: int):
        if not recipe:
            raise ValueError("BioForge must be initialized with a valid recipe.")
        if processing_time <= 0:
            raise ValueError("Processing time must be a positive integer.")

        self.input_inventory = Inventory()
        self.output_inventory = Inventory()
        self.recipe = recipe
        self.processing_time = processing_time

        self.progress = 0
        self.is_processing = False

    def add_to_input(self, item: Item, quantity: int):
        """A player-facing action to add resources to the forge's input buffer."""
        self.input_inventory.add(item, quantity)
        print(f"Added {quantity} {item.name} to the Bio-Forge input.")

    def take_from_output(self, item: Item, quantity: int) -> bool:
        """A player-facing action to retrieve finished products from the forge."""
        if self.output_inventory.remove(item, quantity):
            print(f"Retrieved {quantity} {item.name} from the Bio-Forge output.")
            return True
        print(f"Failed to retrieve {quantity} {item.name}, not enough in output.")
        return False

    def update(self):
        """
        The core update logic for the machine, to be called once per game tick.
        Manages the processing state and crafting progress.
        """
        if not self.is_processing:
            # Check if we have enough resources to start a new job
            if self.input_inventory.has_items(self.recipe.inputs):
                self.is_processing = True
                self.progress = 0
                # Consume resources at the beginning of the process
                for item, quantity in self.recipe.inputs.items():
                    self.input_inventory.remove(item, quantity)
                print(f"Bio-Forge started processing: {self.recipe.outputs}.")
            else:
                # Not enough resources, do nothing this tick
                return

        if self.is_processing:
            self.progress += 1
            print(f"Bio-Forge processing... Progress: {self.progress}/{self.processing_time}")

            if self.progress >= self.processing_time:
                # Crafting is complete
                for item, quantity in self.recipe.outputs.items():
                    self.output_inventory.add(item, quantity)

                print(f"Bio-Forge finished processing. Output inventory: {self.output_inventory.items}")

                # Reset for the next job
                self.progress = 0
                self.is_processing = False

    def __str__(self):
        state = "Processing" if self.is_processing else "Idle"
        return (f"--- Bio-Forge Status ---\n"
                f"State: {state}\n"
                f"Recipe: {self.recipe.inputs} -> {self.recipe.outputs}\n"
                f"Progress: {self.progress}/{self.processing_time}\n"
                f"Input: {dict(self.input_inventory.items)}\n"
                f"Output: {dict(self.output_inventory.items)}\n"
                f"------------------------")
