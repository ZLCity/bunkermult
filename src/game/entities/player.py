import pygame
from game.crafting.inventory import Inventory
from game import assets
from game import settings

class Player:
    """Represents the player character in the game."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.inventory = Inventory()

    def move(self, dx, dy, grid):
        """Moves the player by dx and dy on the grid, with boundary checks."""
        new_x = self.x + dx
        new_y = self.y + dy
        if 0 <= new_x < grid.width and 0 <= new_y < grid.height:
            self.x = new_x
            self.y = new_y

    def mine(self, node):
        """Mines a resource node, adding items to inventory."""
        print(f"Mining {node.item.name}...")
        self.inventory.add(node.item, 1)
        node.amount -= 1
        print(f"Inventory: {self.inventory.items}")

    def draw(self, surface):
        """Draws the player on the given surface."""
        pixel_x = self.x * settings.CELL_SIZE
        pixel_y = self.y * settings.CELL_SIZE
        surface.blit(assets.PLAYER_SPRITE, (pixel_x, pixel_y))
