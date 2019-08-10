class Logger:
    """
    Logging application for Inventory
    Levels:
    0 - Fatal
    1 - Error
    2 - Warning
    3 - Notice
    4 - Info
    """

    def __init__(self, fs, filename=None, loglevel=3):
        """
        Initialize the logger with the required parameters
        :param fs: Filesystem
        :param filename: filename of the log
        :param loglevel: Up to what level should the log write
        """
        self.levels = {0: 'FATAL', 1: 'ERROR', 2: 'WARNING', 3: 'Notice', 4: 'Info'}
        self.__filesystem = fs
        self.__loglevel = loglevel
        self.__logfile = filename

        # If filename exists, make sure the file exists
        if filename:
            log = self.__filesystem.getfile(filename)
            if not log:
                self.__filesystem.addfile(filename, '')

    def log(self, msg, level=3):
        """
        Write to the log
        :param msg: Message to be written, pass error dictionary or string
        :param level: The log level to associate with log
        """

        # Log the message?
        if level > self.__loglevel:
            return

        # Is msg an error object
        if isinstance(msg, dict):
            readable = msg['code'], ' | ', msg['type'], ": ", msg['message']

            msg = (self.levels[level], "".join(readable))
        else:
            msg = (self.levels[level], " " + msg)

        # Write to logfile or print to console
        if self.__logfile:
            self.__filesystem.appendfile(self.__logfile, '\n' + "|".join(msg))
        else:
            print("|".join(msg))