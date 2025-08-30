class PowerGrid:
    """
    Manages the balance of power production and consumption in a network.

    This is a simplified model where all connected producers and consumers
    belong to a single grid. In a more complex game, there could be multiple,
    separate grids.
    """
    def __init__(self):
        self._producers = []
        self._consumers = []

        self.total_production = 0
        self.total_consumption = 0
        self.has_sufficient_power = True

    def add_producer(self, producer):
        """Adds a power-producing structure to the grid."""
        if hasattr(producer, 'get_power_output'):
            self._producers.append(producer)
        else:
            raise TypeError("Producer must have a 'get_power_output' method.")

    def add_consumer(self, consumer):
        """Adds a power-consuming structure to the grid."""
        if hasattr(consumer, 'get_power_consumption'):
            self._consumers.append(consumer)
        else:
            raise TypeError("Consumer must have a 'get_power_consumption' method.")

    def remove_producer(self, producer):
        """Removes a producer from the grid."""
        try:
            self._producers.remove(producer)
        except ValueError:
            # Object not in list, ignore silently
            pass

    def remove_consumer(self, consumer):
        """Removes a consumer from the grid."""
        try:
            self._consumers.remove(consumer)
        except ValueError:
            pass

    def update(self):
        """
        Calculates the power balance for the current tick.
        This should be called once per game tick, before updating consumers.
        """
        # Calculate total power produced this tick
        self.total_production = sum(p.get_power_output() for p in self._producers)

        # Calculate total power demanded this tick
        self.total_consumption = sum(c.get_power_consumption() for c in self._consumers)

        # Determine if the grid is stable
        self.has_sufficient_power = (self.total_production >= self.total_consumption)

    def __str__(self):
        status = "OK" if self.has_sufficient_power else "OVERLOAD"
        return (f"--- Power Grid Status ---\n"
                f"Production: {self.total_production} MW\n"
                f"Consumption: {self.total_consumption} MW\n"
                f"Status: {status}\n"
                f"-------------------------")
