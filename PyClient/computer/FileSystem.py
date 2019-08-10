from json import dumps


class FileExists(Exception): pass
class FileDoesNotExist(Exception): pass


class FileSystem:
    """
    Virtual filesystem
    """

    def __init__(self):
        """
        Initialize the file storage
        :return:
        """
        self.__data = {}

    def __str__(self):
        """
        Return the json encoded string of the filestore
        :return:
        """
        return dumps(self.__data)

    def get(self):
        """
        Return the actual datastore
        :return:
        """
        return self.__data

    def fileexists(self, name):
        """
        Check whether a file exists on the system
        :param name: filenam
        :return: boolean
        """
        return name in self.__data

    def appendfile(self, name, data):
        """
        Append to file, returns None if file doesn't exist
        :param name: filename
        :param data: data to append
        :return:
        """
        if not self.fileexists(name):
            return None

        self.__data[name] += data
        return True

    def addfile(self, name, data):
        """
        Add the file to the file store
        :param name: filename
        :param data: data
        :return:
        """
        if self.fileexists(name):
            raise FileExists

        self.__data[name] = data

        return self.__data[name]

    def getfile(self, name):
        """
        Retrieve data from the file store
        :param name:
        :return:
        """
        if not self.fileexists(name):
            return None

        return self.__data[name]

    def delfile(self, name):
        """
        Delete file from system
        :param name: filename
        :return:
        """
        if not self.fileexists(name):
            raise FileDoesNotExist

        self.__data.pop(name, None)
        return True

    def __getitem__(self, item):
        """
        Get item in [] syntax
        :param item: attribute name
        :return:
        """
        return self.__data[item]

    def __setitem__(self, key, value):
        """
        Set item in [] syntax
        :param key: component name
        :param value: new attribute value
        :return:
        """
        self.__data[key] = value
