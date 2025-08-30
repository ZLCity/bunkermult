class Grid:
    """
    Represents the game world as a 2D grid.
    Manages the placement and updating of objects within the world.
    """
    def __init__(self, width: int, height: int):
        if width <= 0 or height <= 0:
            raise ValueError("Grid dimensions must be positive.")
        self.width = width
        self.height = height
        # Using a dictionary for sparse storage of objects {(x, y): object}
        self._grid_objects = {}

    def place_object(self, obj, x: int, y: int):
        """
        Places an object on the grid at a specific coordinate.
        The object must have an `update` method to be part of the game loop.
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise ValueError(f"Position ({x}, {y}) is outside the grid boundaries.")
        if (x, y) in self._grid_objects:
            raise ValueError(f"Position ({x}, {y}) is already occupied.")
        if not hasattr(obj, 'update'):
            raise TypeError("Object must have an 'update' method to be placed on the grid.")

        # Assign position to the object itself for its own reference
        obj.x = x
        obj.y = y

        self._grid_objects[(x, y)] = obj
        print(f"Placed {obj.__class__.__name__} at ({x}, {y}).")

    def get_object(self, x: int, y: int):
        """Retrieves the object at a given coordinate, or None if empty."""
        return self._grid_objects.get((x, y))

    def remove_object(self, x: int, y: int):
        """Removes the object from a given coordinate."""
        if (x, y) in self._grid_objects:
            del self._grid_objects[(x, y)]
            print(f"Removed object at ({x}, {y}).")

    def update_all(self):
        """
        The main update loop for the entire grid.
        It calls the 'update' method on every object placed on the grid.
        """
        # We iterate over a copy of the values in case the update methods
        # modify the _grid_objects dictionary during iteration.
        for obj in list(self._grid_objects.values()):
            # Pass the grid itself to the object's update method
            obj.update(self)

    def display(self):
        """A simple text-based representation of the grid for debugging."""
        print("\n--- Grid State ---")
        for y in range(self.height):
            row_str = ""
            for x in range(self.width):
                obj = self.get_object(x, y)
                if obj:
                    # Use the object's own string representation
                    row_str += str(obj)
                else:
                    row_str += "[   ]"
            print(row_str)
        print("------------------")
