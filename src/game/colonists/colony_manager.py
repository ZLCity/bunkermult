from .colonist import Colonist

class ColonyManager:
    """
    Manages all colonists in the settlement, and orchestrates the
    update of their needs and behaviors.
    """
    def __init__(self, morale_decay_rate: float = 0.1, purpose_decay_rate: float = 0.05):
        self.colonists: list[Colonist] = []
        self.morale_decay_rate = morale_decay_rate
        self.purpose_decay_rate = purpose_decay_rate

    def add_colonist(self, name: str) -> Colonist:
        """Creates a new colonist and adds them to the colony."""
        new_colonist = Colonist(name)
        self.colonists.append(new_colonist)
        print(f"A new colonist, {name}, has joined the settlement.")
        return new_colonist

    def update(self):
        """
        The main update loop for the entire colony.
        Applies decay to colonist needs over time.
        """
        if not self.colonists:
            return

        # print("Updating colonist needs...")
        for colonist in self.colonists:
            colonist.change_morale(-self.morale_decay_rate)
            colonist.change_purpose(-self.purpose_decay_rate)

    def __str__(self) -> str:
        """Provides a string summary of the entire colony's status."""
        if not self.colonists:
            return "The colony is empty."

        header = "--- Colony Status ---\n"
        status_lines = [str(c) for c in self.colonists]
        return header + "\n".join(status_lines)
