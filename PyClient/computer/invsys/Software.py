
class Software:
    """
    Base software class, this describes the basic most software that can be installed on a system
    """

    def __init__(self):
        """
        Initialize the software
        :return:
        """
        self._filesystem = None
        self._logger = None
        self._params = {
            'started': False,
            'config': {},
            'ram': {}
        }

    def log(self, msg, level=4):
        """
        Log to the logger
        :param msg: Message sent to the logger
        :param level: log level to be sent to the logger
        :return:
        """
        if self._logger:
            self._logger.log(msg, level)
        else:
            print("NO LOGGER: ", msg)

    def start(self):
        """
        Virtually start the software
        :return:
        """
        self._params['started'] = True

    def stop(self):
        """
        Stop the application
        :return:
        """
        self._params['started'] = False

    def started(self):
        """
        Returns whether the software is online
        :return:
        """
        return self._params['started']

    def install(self, fs, *args):
        """
        Create an instance of the installed software and return
        :param fs: FileSystem instance
        :return:
        """
        self._filesystem = fs
        return self

    def tick(self, tmr, dtime):
        """
        The software simulation loop, what happens per tick
        :return:
        """
        if not self.started():
            return False

        return True

    @property
    def config(self):
        return self._params['config']

    @property
    def ram(self):
        return self._params['ram']

    def crash(self, err):
        """
        Application crash scenario
        :param err: The response object from api
        :return:
        """
        self.log("CRASHED", 0)

        if isinstance(err, dict):
            # For all errors we have, log them
            for i in err['errors']:
                self.log(i, 0)
        else:
            print(err)

        # Stop the application safely
        self.stop()

        return None
