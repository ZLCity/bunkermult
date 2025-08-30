import sys
import os

# This is a temporary solution for the prototype to ensure imports work from other directories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from game.crafting import Inventory, Recipe, Item

class BioForge:
    """
    An automated structure that processes a specific recipe over time.
    It can interact with other structures by accepting items and ejecting its output.
    """
    def __init__(self, recipe: Recipe, processing_time: int, output_direction: tuple[int, int]):
        if not recipe:
            raise ValueError("BioForge must be initialized with a valid recipe.")
        if processing_time <= 0:
            raise ValueError("Processing time must be a positive integer.")

        self.input_inventory = Inventory()
        self.output_inventory = Inventory()
        self.recipe = recipe
        self.processing_time = processing_time
        self.output_direction = output_direction

        self.progress = 0
        self.is_processing = False
        self.x = -1 # Position on grid, set by Grid
        self.y = -1

    def add_to_input(self, item: Item, quantity: int):
        """A player-facing action to add resources to the forge's input buffer."""
        self.input_inventory.add(item, quantity)

    def accept_item(self, item: Item) -> bool:
        """Allows other structures (like conveyors) to feed items into this forge."""
        self.add_to_input(item, 1)
        # For simplicity, we assume the forge always has space for input.
        return True

    def take_from_output(self, item: Item, quantity: int) -> bool:
        """A player-facing action to retrieve finished products from the forge."""
        return self.output_inventory.remove(item, quantity)

    def _start_processing(self):
        """Internal method to begin a new crafting job."""
        if self.input_inventory.has_items(self.recipe.inputs):
            self.is_processing = True
            self.progress = 0
            for item, quantity in self.recipe.inputs.items():
                self.input_inventory.remove(item, quantity)
            print(f"({self.x},{self.y}) Bio-Forge: Started processing {self.recipe.outputs}.")
            return True
        return False

    def _finish_processing(self, grid):
        """Internal method to handle a completed crafting job."""
        # Add the crafted items to the output buffer
        for item, quantity in self.recipe.outputs.items():
            self.output_inventory.add(item, quantity)
        print(f"({self.x},{self.y}) Bio-Forge: Finished processing. Output: {self.output_inventory.items}")

        # Reset for the next job
        self.progress = 0
        self.is_processing = False

        # Try to eject the output immediately
        self._eject_output(grid)

    def _eject_output(self, grid):
        """Try to move items from the output buffer to an adjacent tile."""
        if not self.output_inventory.items:
            return

        next_x = self.x + self.output_direction[0]
        next_y = self.y + self.output_direction[1]

        next_tile_obj = grid.get_object(next_x, next_y)

        if next_tile_obj and hasattr(next_tile_obj, 'accept_item'):
            # Get the first item from the output inventory to try and move
            item_to_move = next(iter(self.output_inventory.items.keys()))

            if next_tile_obj.accept_item(item_to_move):
                self.output_inventory.remove(item_to_move, 1)
                print(f"({self.x},{self.y}) Bio-Forge: Ejected {item_to_move.name} to ({next_x}, {next_y}).")


    def update(self, grid):
        """
        The core update logic for the machine, to be called once per game tick.
        """
        # 1. Try to eject any items waiting in the output buffer
        self._eject_output(grid)

        # 2. Handle processing logic
        if self.is_processing:
            self.progress += 1
            if self.progress >= self.processing_time:
                self._finish_processing(grid)
        else:
            # If not processing, try to start a new job
            self._start_processing()

    def __str__(self):
        # Provides a simple, single-character representation for the grid display
        return "[ B ]"
