import sys
import os

# Add the 'src' directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from game.entities.player import Player
from game.crafting.item import Item

def run_build_test():
    """
    Tests the logic of checking and consuming resources for a build action.
    """
    print("--- Build Action Test ---")

    # 1. Define the cost to build a structure
    raw_ore = Item("Raw Ore")
    cost = {raw_ore: 10}
    print(f"Cost to build: {cost[raw_ore]} {raw_ore.name}")

    # 2. Create a player with an empty inventory
    player = Player(x=0, y=0)
    print("\nPlayer created with empty inventory.")
    print(f"Player inventory: {dict(player.inventory.items)}")

    # 3. Attempt to build with insufficient resources
    print("\nAttempting to build with empty inventory...")
    if player.inventory.has_items(cost):
        print("Test FAILED: Should not have enough resources.")
    else:
        print("Test PASSED: Correctly identified insufficient resources.")

    # 4. Add some, but not enough, resources
    print("\nAdding 5 Raw Ore to player inventory...")
    player.inventory.add(raw_ore, 5)
    print(f"Player inventory: {dict(player.inventory.items)}")

    print("\nAttempting to build again...")
    if player.inventory.has_items(cost):
        print("Test FAILED: Should not have enough resources.")
    else:
        print("Test PASSED: Correctly identified insufficient resources.")

    # 5. Add enough resources
    print("\nAdding 5 more Raw Ore (total 10)...")
    player.inventory.add(raw_ore, 5)
    print(f"Player inventory: {dict(player.inventory.items)}")

    # 6. Attempt to build with sufficient resources
    print("\nAttempting to build with sufficient resources...")
    if player.inventory.has_items(cost):
        print("Test PASSED: Correctly identified sufficient resources.")
        print("Now consuming resources...")
        player.inventory.remove_items(cost)
        print(f"Player inventory after build: {dict(player.inventory.items)}")

        # Verification
        if not player.inventory.items:
            print("Test PASSED: Inventory is empty as expected.")
        else:
            print(f"Test FAILED: Inventory should be empty but is {dict(player.inventory.items)}")
    else:
        print("Test FAILED: Should have had enough resources.")

    print("\n--- Build Action Test Finished ---")

if __name__ == "__main__":
    run_build_test()
