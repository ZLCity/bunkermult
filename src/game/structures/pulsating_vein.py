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
    It moves items in a specific direction and consumes power.
    """
    def __init__(self, direction: tuple[int, int], power_consumption: int, speed: int = 1, capacity: int = 1):
        self.direction = direction
        self.speed = speed
        self.capacity = capacity
        self._power_consumption = power_consumption

        self.item_buffer = deque()

        self.x = -1
        self.y = -1

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

    def get_power_consumption(self) -> int:
        """Returns power consumed. A conveyor consumes power only when an item is on it."""
        return self._power_consumption if self.item_buffer else 0

    def update(self, grid, has_power: bool):
        """
        The core update logic for the conveyor. Tries to move an item to the next tile.
        """
        if not has_power:
            return # No power, no movement

        if self._move_cooldown > 0:
            self._move_cooldown -= 1
            return

        if not self.item_buffer:
            return

        next_x = self.x + self.direction[0]
        next_y = self.y + self.direction[1]
        next_tile_obj = grid.get_object(next_x, next_y)

        if next_tile_obj and hasattr(next_tile_obj, 'accept_item'):
            item_to_move = self.item_buffer[0]

            if next_tile_obj.accept_item(item_to_move):
                self.item_buffer.popleft()
                print(f"Conveyor at ({self.x}, {self.y}) moved {item_to_move.name} to ({next_x}, {next_y}).")

    def __str__(self):
        item_name = self.item_buffer[0].name if self.item_buffer else " "
        dir_map = {(0, 1): "v", (0, -1): "^", (1, 0): ">", (-1, 0): "<"}
        dir_char = dir_map.get(self.direction, "?")
        # Pad with spaces for consistent grid display
        return f" {dir_char}{item_name[0]} "
