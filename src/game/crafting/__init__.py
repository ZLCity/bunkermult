# This file makes the 'crafting' directory a Python package.

# We can also make the classes and functions easier to import by
# exposing them at the package level.
from .item import Item
from .recipe import Recipe
from .inventory import Inventory
from .core import craft

# This allows imports like: from game.crafting import Item
# instead of: from game.crafting.item import Item
