import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from game.crafting import Item, Inventory

class BioElectricGenerator:
    """
    A structure that produces power by consuming fuel (e.g., Biomass).
    """
    def __init__(self, power_output: int, fuel_item: Item, ticks_per_fuel: int):
        self._power_output = power_output
        self._fuel_item = fuel_item
        self._ticks_per_fuel = ticks_per_fuel

        self.fuel_inventory = Inventory()
        self.is_active = False
        self._ticks_remaining = 0

        # For grid placement
        self.x = -1
        self.y = -1

    def add_fuel(self, quantity: int):
        """Player-facing action to add fuel to the generator."""
        self.fuel_inventory.add(self._fuel_item, quantity)
        print(f"Added {quantity} {self._fuel_item.name} to generator at ({self.x}, {self.y}).")

    def get_power_output(self) -> int:
        """Returns the power generated this tick. Used by the PowerGrid."""
        return self._power_output if self.is_active else 0

    def _consume_fuel(self):
        """Internal method to try and consume one unit of fuel to start burning."""
        if self.fuel_inventory.remove(self._fuel_item, 1):
            self.is_active = True
            self._ticks_remaining = self._ticks_per_fuel
            print(f"Generator at ({self.x}, {self.y}) consumed 1 {self._fuel_item.name}, now active.")
        else:
            self.is_active = False

    def update(self, grid):
        """
        Core update logic. Manages fuel consumption and active state.
        The 'grid' argument is unused for the generator but required by the Grid's update loop.
        """
        if self.is_active:
            self._ticks_remaining -= 1
            if self._ticks_remaining <= 0:
                print(f"Generator at ({self.x}, {self.y}) ran out of fuel.")
                self.is_active = False
                # Try to refuel immediately for the next tick
                self._consume_fuel()
        else:
            # If not active, try to consume fuel to start up
            self._consume_fuel()

    def __str__(self):
        # Representation for the grid display
        return "[ G ]"
