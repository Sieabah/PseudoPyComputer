import json


class Configurator:
    """
    Configuration object
    """
    def __init__(self, fp=None):
        """
        Generate a configuration from file or provide a default
        :param fp:
        :return:
        """
        if fp:
            self.config_file(fp)
        else:
            self.__config = {
              "store": "computers",
              "pool": "component_pool",
              "system_count": 5,
              "setup": 1,
              "simulation": True,
              "gui": True,
              "inv_path": "invconfig.json",
              "tickrate": 0.3
            }

    def config_file(self, fp):
        """
        Load configuration from file
        :param fp: filepath
        :return:
        """
        self.__config = json.load(open(fp))

    def __getitem__(self, item):
        """
        Get configuration using [] syntax
        :param item: configuration item
        :return:
        """
        return self.__config[item]

    def __setitem__(self, key, value):
        """
        Set configuration value using [] syntax
        :param key:
        :param value:
        :return:
        """
        self.__config[key] = value
