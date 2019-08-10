# Inventory Client Dep
from computer.System import System
from computer.invsys.InvSys import InvSys
from Simulation import Simluation, GUISim

# Python Dep
import sys
import os
import string
import random
import json


class Manager:
    def __init__(self, config):
        """
        Initialize the manager
        :param config: configuration object
        :return:
        """

        self.__systems = {}
        self.__config = config

        setup = self.__config['setup']
        store = self.__config['store']

        # Make storage folder if no folder exists
        if not os.path.isdir(store):
            os.makedirs(store)

        # Remove all previous computers
        if setup == 1:
            for f in os.listdir(store):
                fp = os.path.join(store, f)
                if os.path.isfile(fp):
                    try:
                        os.unlink(fp)
                    except PermissionError:
                        print("Cannot delete files!")

        # Load as many computers as we can
        elif setup == 2 or setup == 3:
            comps = 0
            for i, f in enumerate(os.listdir(store)):
                # Only load .computer files
                if f.endswith('computer'):
                    if comps + 1 <= self.__config['system_count'] or setup == 3:
                        system = self.load_computer(os.path.join(store, f))
                        self.__systems[system.get_serial()] = system
                        comps += 1

        # Read inventory software
        f = open(self.__config['inv_path'])
        invconf = f.read()
        f.close()

        # Create computers up to the limit
        if self.__config['system_count'] - len(self.__systems) > 0 and not setup == 3:
            for i in range(self.__config['system_count']):
                system = self.create_computer(self.__config['pool'])

                # Add inventory config to computer
                system.addfile('invconf', invconf)
                self.__systems[system.get_serial()] = system

        # Check if there are computers to simulate
        if len(self.__systems) <= 0:
            print("No systems loaded or created to simulate")
            sys.exit(1)

        self.save_all_systems()

    @staticmethod
    def string_generator(length):
        """
        Generate a random string of numbers and letters of length
        :param length: Length of the string returned
        :return:
        """
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))

    def create_computer(self, pool):
        """
        Create a computer using the component pool given
        :param pool: filepath of the components
        :return:
        """

        serial = None

        # Generate a serial number which is not present
        while True:
            serial = self.string_generator(6)
            if serial not in self.__systems:
                break

        system = System()

        # Get list of modules
        modules = os.listdir(pool)

        for component in modules:
            loc = os.path.join(pool, component)
            locs = os.listdir(loc)
            comploc = []

            # Specifically load more than 1 component for partitions
            if component == 'partitions':
                for i in locs:
                    comploc.append(os.path.join(loc, i))
            else:
                # Component location
                comploc.append(os.path.join(loc, random.choice(locs)))

            # For all comonents load them into system
            for i in comploc:
                # Load components
                f = open(i)
                block = json.load(f)
                f.close()

                if 'serial' in block:
                    if block['serial'] == 'GEN':
                        block['serial'] = self.string_generator(7)

                # If it's the bios, give it our custom serial
                if component == 'bios':
                    block['serial'] = serial

                system.add_component(component, block)

        return system

    @staticmethod
    def load_computer(fp):
        """
        Load computer from the filepath
        :param fp: filepath of .computer files
        :return:
        """
        if not fp.endswith('.computer'):
            return None

        # Load up the computer from file
        f = open(fp)
        computer = json.load(f)
        f.close()

        system = System()

        # Load system components
        for i in computer['modules']:
            for j in computer['modules'][i]:
                system.add_component(i, j)

        # Load all files into computers
        for x in computer['filesystem']:
            system.addfile(x, computer['filesystem'][x])

        return system

    def save(self, system):
        """
        Save system to .computer file
        :param system: system to save to the filestore
        :return:
        """
        filename = os.path.join(self.__config['store'], system.get_serial() + '.computer')

        fp = open(filename, "w")
        fp.write(str(system))
        fp.close()

    def save_all_systems(self):
        """
        Mass save all systems
        :return:
        """
        for i in self.__systems:
            self.save(self.__systems[i])

    def run(self):
        """
        Start simulation of computers
        :return:
        """

        threads = {}
        ticktime = self.__config['tickrate']

        # Generate the threads for each system
        for i, comp in enumerate(self.__systems):
            system = self.__systems[comp]

            # Install software
            system.install_software(InvSys, [system])

            threads[system.get_serial()] = Simluation(i, system.get_serial(), ticktime, system)

        # Start processing each computer independently
        for i in threads:
            threads[i].start()

        # Start the GUI
        gui = GUISim(0, "Inventory Simulation", self.__systems, ticktime)
        gui.start()

        # While GUI is open, keep simulating
        while True:
            if gui.stopped():
                for t in threads:
                    threads[t].stop()

                break

        # Wait for threads to exit
        for t in threads:
            threads[t].join()

        self.save_all_systems()
