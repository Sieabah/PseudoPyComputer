import threading
import time
from tkinter import *


class GUISim(threading.Thread):
    """
    GUISim is a gui of the simulation of computers
    """

    def __init__(self, threadid, name, systems, ticktime):
        """
        Initialize the GUI thread
        :param threadid: thread id
        :param name: thread name
        :param systems: All computers in the simulation
        :param ticktime: How fast should they be ticking
        :return:
        """
        threading.Thread.__init__(self)
        self.__threadID = threadid
        self.__name = name
        self.__systems = systems
        self.__ticktime = ticktime
        self.__stop = False

    def stop(self):
        """
        Top the simulation
        :return:
        """
        self.__stop = True

    def stopped(self):
        """
        Has the simulation stopped
        :return:
        """
        return self.__stop

    def run(self):
        """
        Run the simulation
        :return:
        """
        print("Starting GUI")

        # Create the window
        root = Tk()
        root.title("Inventory Computer Simulation")
        root.protocol("WM_DELETE_WINDOW", self.stop)

        Label(root, text="Each red blip is a tick for that system").pack()

        # Create the canvas
        canvas = Canvas(root, width=200, height=20 * len(self.__systems) + 20)
        canvas.pack()

        elements = []
        systems = self.__systems

        # Generate tuples of related elements
        for i, s in enumerate(systems):
            ho = i * 20 + 20

            # Activity Indicator
            circle = canvas.create_rectangle(5, ho + 3, 15, ho + 13, fill="blue")

            #
            pcircle = canvas.create_rectangle(15, ho + 3, 25, ho + 13, fill="black")

            # Identifier
            text = canvas.create_text(30, ho, anchor="nw", text=s)

            # System Process
            status = canvas.create_text(90, ho, anchor="nw", text="null")

            # Add to elements list
            item = (text, circle, pcircle, status, systems[s])
            elements.append(item)

        # Update the gui
        while True:
            # Make sure we're not supposed to stop
            if self.stopped():
                break

            root.update()

            # Loop through indicators
            for i in elements:
                canvas.itemconfig(i[3], text=i[-1].status)

                cutoff = 0.1
                if float(self.__ticktime) / 2 < cutoff:
                    cutoff = float(self.__ticktime) / 2

                if i[-1].parameter('powered'):
                    canvas.itemconfig(i[2], fill="green")
                else:
                    canvas.itemconfig(i[2], fill="black")

                if cutoff < time.time() - i[-1].lasttick():
                    canvas.itemconfig(i[1], fill="black")
                else:
                    canvas.itemconfig(i[1], fill="red")

        print("Exiting GUI")


class Simluation(threading.Thread):
    """
    Computer Simulation thread
    """

    def __init__(self, threadid, name, tick, system):
        """
        Initialize the thread
        :param threadid: thread id number
        :param name: thread name
        :param tick: tick rate
        :param system: relevant system this thread is responsible for
        :return:
        """
        threading.Thread.__init__(self)
        self.threadid = threadid
        self.name = name
        self.system = system
        self.ticktime = tick
        self.__stop = False

    def stop(self):
        """
        Stop the simulation thread
        :return:
        """
        self.__stop = True

    def stopped(self):
        """
        Is the thread stopped
        :return:
        """
        return self.__stop

    def run(self):
        """
        Run the simulation
        :return:
        """
        print("Starting thread for", self.name)

        # Start up computer
        self.system.boot()

        # Loop through simulation until we need to stop
        while True:
            if self.stopped():
                break

            try:
                # Rate limit until we need to tick
                self.system.tick(time.time())
                time.sleep(self.ticktime)
            except:
                self.system.shutdown(True)
                raise

        print("Exiting", self.name)
