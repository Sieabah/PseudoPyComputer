# Include Python Dependencies
import sys

# Inventory Client dependencies
import SimulatorConfig
import ComputerManager


def menu():
    """
    TODO: Create config customizer if no configuration is given
    :return:
    """
    options = [
        "Start Simulation"
    ]
    choice = None
    while True:
        for i, j in enumerate(options):
            print(str(i) + ":", j)

        choice = input("Do: ")
        if choice >= 0 and choice < len(options):
            return choice


def main():
    """
    Inventory Client Simulation
    :return:
    """
    config = None

    # Get configuration file
    if len(sys.argv) > 1:
        config = SimulatorConfig.Configurator(sys.argv[1])
    else:
        config = SimulatorConfig.Configurator()

    # Create manager
    mgr = ComputerManager.Manager(config)

    # Run simulation
    mgr.run()


main()
