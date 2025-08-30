from .item import Item

class Recipe:
    """Defines the inputs and outputs for a crafting process."""
    def __init__(self, inputs: dict[Item, int], outputs: dict[Item, int]):
        self.inputs = inputs
        self.outputs = outputs

    def __repr__(self) -> str:
        return f"Recipe(in: {self.inputs}, out: {self.outputs})"
