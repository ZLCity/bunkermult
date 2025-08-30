import sys
import os

# Add the 'src' directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from game.world import Grid

# A placeholder class to test placing objects on the grid
class DummyObject:
    def __init__(self):
        self.x = 0
        self.y = 0

    def update(self):
        # In a real scenario, this would contain the object's logic for each tick
        pass

def run_grid_test():
    """Tests the basic functionality of the Grid class."""
    print("--- Testing Grid System ---")

    try:
        # 1. Test Grid creation
        print("\n1. Creating a 10x5 grid...")
        game_grid = Grid(width=10, height=5)
        game_grid.display()

        # 2. Test object placement
        print("\n2. Placing a DummyObject at (2, 2)...")
        dummy = DummyObject()
        game_grid.place_object(dummy, 2, 2)
        game_grid.display()

        # 3. Test getting an object
        print("\n3. Retrieving object at (2, 2)...")
        retrieved_obj = game_grid.get_object(2, 2)
        print(f"Retrieved: {retrieved_obj.__class__.__name__}")
        assert retrieved_obj is dummy

        # 4. Test placing in an occupied spot (should raise an error)
        print("\n4. Trying to place another object at (2, 2)...")
        try:
            game_grid.place_object(DummyObject(), 2, 2)
        except ValueError as e:
            print(f"Successfully caught expected error: {e}")

        # 5. Test placing out of bounds (should raise an error)
        print("\n5. Trying to place an object at (11, 5)...")
        try:
            game_grid.place_object(DummyObject(), 11, 5)
        except ValueError as e:
            print(f"Successfully caught expected error: {e}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return

    print("\n--- Grid System test completed successfully! ---")


if __name__ == "__main__":
    run_grid_test()
