class Colonist:
    """
    Represents a single colonist in the settlement, with their own needs and status.
    """
    def __init__(self, name: str):
        self.name = name

        # Core needs as described in the GDD, scaled from 0 to 100.
        self.health: float = 100.0
        self.morale: float = 80.0
        self.purpose: float = 50.0

    def _clamp_need(self, value: float) -> float:
        """Helper function to keep need values between 0 and 100."""
        return max(0.0, min(100.0, value))

    def change_health(self, amount: float):
        """Modifies health by a given amount, ensuring it stays within bounds."""
        self.health = self._clamp_need(self.health + amount)

    def change_morale(self, amount: float):
        """Modifies morale by a given amount."""
        self.morale = self._clamp_need(self.morale + amount)

    def change_purpose(self, amount: float):
        """Modifies purpose by a given amount."""
        self.purpose = self._clamp_need(self.purpose + amount)

    def __str__(self) -> str:
        """Provides a string summary of the colonist's status."""
        return (f"  - {self.name}: "
                f"Health={self.health:.1f}, "
                f"Morale={self.morale:.1f}, "
                f"Purpose={self.purpose:.1f}")
