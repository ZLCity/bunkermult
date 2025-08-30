class Item:
    """Represents a unique item or resource in the game."""
    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        # Using name for representation to make inventory printouts cleaner
        return self.name

    # The following methods are crucial for using Item objects as dictionary keys
    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other) -> bool:
        return isinstance(other, Item) and self.name == other.name
