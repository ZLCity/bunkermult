import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from game.colonists import ColonyManager

def run_colonist_simulation():
    """
    Simulates the life of a colony over time, focusing on the decay of needs.
    """
    print("--- Colonist Needs Simulation ---")

    # 1. Setup the Colony
    colony = ColonyManager(morale_decay_rate=0.2, purpose_decay_rate=0.1)

    print("\nFounding the colony...")
    colony.add_colonist("Zoe")
    colony.add_colonist("Alex")

    print("\nInitial colony status:")
    print(colony)

    # 2. Game Loop Simulation
    ticks_to_run = 50
    print(f"\n--- Starting Game Loop ({ticks_to_run} ticks) ---")

    for tick in range(1, ticks_to_run + 1):
        colony.update()

        # Print status every 10 ticks to observe the change
        if tick % 10 == 0:
            print(f"\n--- Status at Tick {tick} ---")
            print(colony)
            time.sleep(0.1)

    print(f"\n--- Simulation Finished after {ticks_to_run} ticks ---")
    print("Final colony status:")
    print(colony)


if __name__ == "__main__":
    run_colonist_simulation()
