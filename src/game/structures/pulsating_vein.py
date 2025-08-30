import sys
import os
from collections import deque

# Add the 'src' directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from game.crafting import Item
# We cannot import Grid here due to circular dependency (Grid imports structures)
# Instead, the grid instance will be passed to the update method.

class PulsatingVein:
    """
    Represents a single segment of a conveyor belt (Pulsating Vein).
    It moves items in a specific direction.
    """
    def __init__(self, direction: tuple[int, int], speed: int = 1, capacity: int = 1):
        # Direction as a tuple, e.g., (0, 1) for South, (1, 0) for East
        self.direction = direction
        self.speed = speed # Not implemented yet, but good for future use
        self.capacity = capacity

        # A double-ended queue is efficient for adding/removing from both ends
        self.item_buffer = deque()

        # Position will be set by the Grid when placed
        self.x = -1
        self.y = -1

        # Cooldown to prevent items from moving every single tick if speed > 1
        self._move_cooldown = 0

    def accept_item(self, item: Item) -> bool:
        """
        Accepts an item if there is space in the buffer.
        Returns True if the item was accepted, False otherwise.
        """
        if len(self.item_buffer) < self.capacity:
            self.item_buffer.append(item)
            # When an item is accepted, start the cooldown before it can move again.
            self._move_cooldown = self.speed
            return True
        return False

    def update(self, grid): # grid is passed dynamically to avoid circular import
        """
        The core update logic for the conveyor. Tries to move an item to the next tile.
        """
        if self._move_cooldown > 0:
            self._move_cooldown -= 1
            return

        if not self.item_buffer:
            # Nothing to move
            return

        # Cooldown is over, let's try to move the item
        next_x = self.x + self.direction[0]
        next_y = self.y + self.direction[1]
        next_tile_obj = grid.get_object(next_x, next_y)

        if next_tile_obj and hasattr(next_tile_obj, 'accept_item'):
            item_to_move = self.item_buffer[0] # Peek at the item

            if next_tile_obj.accept_item(item_to_move):
                # Move was successful, remove item from our buffer
                self.item_buffer.popleft()
                print(f"Conveyor at ({self.x}, {self.y}) moved {item_to_move.name} to ({next_x}, {next_y}).")

    def __str__(self):
        item_name = self.item_buffer[0].name if self.item_buffer else " "
        dir_map = {(0, 1): "v", (0, -1): "^", (1, 0): ">", (-1, 0): "<"}
        dir_char = dir_map.get(self.direction, "?")
        # Pad with spaces for consistent grid display
        return f" {dir_char}{item_name[0]} "
