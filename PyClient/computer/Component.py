import random
import string


class BaseComponent:
    def __init__(self):
        pass


def string_generator(length):
    """
    Generate a random string of numbers and letters of length
    :param length: Length of the string returned
    :return:
    """
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))


class Component(BaseComponent):
    """
    Simulated hardware components
    """

    def __init__(self, component):
        """
        Initialize the component
        :param component: component to create
        :return:
        """
        super().__init__()
        self.__component = component
        if not self.__component.get('cid', None):
            self.__component['cid'] = string_generator(3)

    def __str__(self):
        """
        Stringified version of the module
        :return:
        """
        return str(self.__component)

    @property
    def component(self):
        """
        Return the component itself
        :return:
        """
        return self.__component

    @component.setter
    def component(self, value):
        """
        Set the component
        :param value:
        :return:
        """
        self.__component = value

    def __getitem__(self, item):
        """
        Get item in [] syntax
        :param item: attribute name
        :return:
        """
        return self.__component.get(item, None)

    def __setitem__(self, key, value):
        """
        Set item in [] syntax
        :param key: component name
        :param value: new attribute value
        :return:
        """
        self.__component[key] = value


class Modules(BaseComponent):
    """
    Component holder, such as cpu
    """

    def __init__(self):
        """
        Initialze the module store
        :return:
        """
        super().__init__()
        self.__components = {}

    def __str__(self):
        """
        Stringified version of the module
        :return:
        """
        return str(self.get_all())

    @property
    def module(self):
        """
        Return the set of componenets
        :return:
        """
        return self.__components

    def get_all(self):
        """
        Build a dictionary of all modules and components
        :return:
        """
        arr = {}
        # Get the list of lists of components
        for i in self.__components:
            lst = []
            # Break down the list and append components to master list
            for j in self.__components[i]:
                lst.append(j.component)

            arr[i] = lst

        return arr

    def __getitem__(self, item):
        """
        Get item in [] syntax
        :param item: component name
        :return:
        """
        return self.__components.get(item, None)

    def __setitem__(self, key, value):
        """
        Set item in [] syntax
        :param key: component name
        :param value: new component value
        :return:
        """
        if not self.__components.get(key, None):
            self.__components[key] = []

        self.__components[key].append(value)

    def keys(self):
        """
        Return keys of the modules installed
        :return:
        """
        return self.__components.keys()
