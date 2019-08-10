import json
import time

from . import Component
from . import FileSystem


class System:
    """
    Computer System

    This class deals with the entire concept of a computer, simulating the hardware and interacting
        with the inventory API
    """

    def __str__(self):
        """
        Json/String version of the object
        :return:
        """
        computron = {
            'modules': self.__modules.get_all(),
            'filesystem': self.__filesystem.get()
        }

        return json.dumps(computron)

    def __init__(self):
        """
        Initialize the computer
        :return:
        """
        self.__modules = Component.Modules()
        self.__lasttick = None
        self.__status = 'Off'
        self.__systime = time.time()

        self.__params = {
            "powered": False
        }

        # Systems
        self.__software = []
        self.__filesystem = FileSystem.FileSystem()

    @property
    def status(self):
        """
        Status property
        :return:
        """
        return self.__status

    @status.setter
    def status(self, v):
        """
        Set the status of the computer
        :param v:
        :return:
        """
        self.__status = v

    def addfile(self, filename=None, data=None):
        """
        Add file to filestorage
        :param filename: filename
        :param data: data
        :return:
        """
        if not data or not filename:
            return

        self.__filesystem.addfile(filename, data)

    def readfile(self, filename):
        """
        Read the file from the filestorage
        :param filename:
        :return:
        """
        return self.__filesystem[filename]

    @property
    def modules(self):
        """
        Get a list of all modules in the system
        :return:
        """
        return self.__modules.keys()

    @property
    def module(self):
        """
        Get the module holder
        :return:
        """
        return self.__modules

    def add_component(self, name, component):
        """
        Add a component to the system
        :param name: module name
        :param component: component
        :return:
        """
        self.__modules[name] = Component.Component(component)

    def get_component(self, name=None):
        """
        Get component module from the computer
        :param name:
        :return:
        """
        if name:
            return self.__modules.module[name]
        else:
            return None

    def install_software(self, software, args):
        """
        Install the software to the system
        :param software: software class
        :param args: arguments to be passed to class
        :return:
        """
        self.__software.append(software().install(self.__filesystem, *args))

    def get_bios(self):
        """
        Get the system bios
        :return:
        """
        return self.get_component('bios')

    def get_serial(self):
        """
        Get the serial of the computer
        :return:
        """
        return self.__modules['bios'][0]['serial']

    def lasttick(self):
        """
        Get when the computer ticked last
        :return:
        """
        if self.__lasttick:
            return self.__lasttick
        else:
            return 0

    def parameter(self, key):
        """
        Get system parameter by key (not components)
        :param key:
        :return:
        """
        return self.__params[key]

    def tick(self, tmr):
        """
        Simulation tick

        This handles multiple simulation cases such as updating hardware, interface with SQLite
            and interact with the API
        :param tmr: time of tick
        :return:
        """
        dtime = tmr

        # Keep delta time
        if self.__lasttick:
            dtime = tmr - self.__lasttick

        self.__lasttick = tmr

        # Don't process unless system in on
        if not self.parameter('powered'):
            return

        self.status = 'Running software'

        # For all programs in system
        for i, program in enumerate(self.__software):
            self.status = 'Tick ' + program.__class__.__name__
            time.sleep(0.1)

            # Tick them
            if not program.tick(tmr, dtime):
                self.__software.pop(i)
                self.status = program.__class__.__name__+' crashed'
                time.sleep(5)

        self.status = 'Idle'

    def boot(self):
        """
        Start the computer
        :return:
        """
        self.__params['powered'] = True
        self.status = 'Booting'

        time.sleep(1)

        # Start all software in system
        for i in self.__software:
            self.status = "Starting " + i.__class__.__name__
            i.start()
            time.sleep(1)

        self.status = 'Idle'

    def shutdown(self, crashed=False):
        """
        Shutdown the system
        :return:
        """
        print("Powered off", self.get_serial())
        self.__params['powered'] = False
        if crashed:
            self.status = "Crashed"
        else:
            self.status = 'Off'
