import pygame
from game import assets
from game import settings

class ResourceNode:
    """Represents a mineable resource node in the game world."""
    def __init__(self, x, y, resource_item, amount):
        self.x = x
        self.y = y
        self.item = resource_item
        self.amount = amount

    def draw(self, surface):
        """Draws the resource node on the given surface."""
        pixel_x = self.x * settings.CELL_SIZE
        pixel_y = self.y * settings.CELL_SIZE
        sprite = assets.get_resource_sprite(self.item.name)
        surface.blit(sprite, (pixel_x, pixel_y))
