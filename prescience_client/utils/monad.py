import typing

class List(typing.NamedTuple):
    """
    Monad implementation for list
    """
    value: list

    def is_empty(self) -> bool:
        """
        Check if the list is empty
        :return: True if the list is empty, False otherwise
        """
        return not self.value

    def map(self, func) -> 'List':
        """
        Monadic map function implementation
        :param func: The transformation function
        :return: A copy of the current list in which all elements have been transformed by the given function
        """
        return List(list(map(func, self.value)))

    def head(self) -> any:
        """
        Access the head of the list
        :return: the head of the list
        """
        return self.value[0]

    def tail(self) -> any:
        """
        Access the tail of the list
        :return: the tail of the list
        """
        return self.value[-1]

    def length(self) -> int:
        """
        Access the length of the list
        :return: the length of the list
        """
        return len(self.value)

    def size(self) -> int:
        """
        Access the size of the list
        :return: the size of the list
        """
        return self.length()

    def head_option(self) -> 'Option':
        """
        Access the head of the list as an Option
        :return: Option(head) if the list is not empty, Option(None) otherwise
        """
        if not self.is_empty():
            return Option(self.head())
        else:
            return Option(None)

    def tail_option(self) -> 'Option':
        """
        Access the tail of the list as an Option
        :return: Option(tail) if the list is not empty, Option(None) otherwise
        """
        if not self.is_empty():
            return Option(self.tail())
        else:
            return Option(None)

    def to_dict(self) -> dict:
        """
        Convert the current list to dict
        :return: The dict of (elt[0] -> elt[1]) if all list elements are tuple, (index, element) otherwise
        """
        if self.is_empty():
            return {}
        elif type(self.head()) == tuple:
            return dict(self.value)
        else:
            return {v: k for v, k in enumerate(self.value)}

    def filter(self, predicate):
        """
        Filter the current on given predicate
        :param predicate: The filter predicate to use
        :return: A copy of the current list filtered by satisfying the given predicate
        """
        return List([x for x in self.value if predicate(x)])

    def count(self, predicate):
        """
        Count the number of elements in the list that match the given predicate
        :param predicate: The couting predicate
        :return: the number of elements in the list that match the given predicate
        """
        return self.filter(predicate).length()

    def find(self, predicate):
        """
        Find the first element of the list matching the predicate
        :param predicate: predicate used for element selection
        :return: The option containing the element matching the predicate if any, None option otherwise
        """
        return self.filter(predicate).head_option()

    def flatten(self):
        return List([item for sublist in self.value for item in sublist])

    def flat_map(self, func):
        return self.map(func).flatten()

class Option(typing.NamedTuple):
    """
    Monad implementation for Option
    """
    value: any

    def get_or_else(self, other:any) -> any:
        """
        Get the option content or return the other value if the option is None
        :param other: The default value if the option is None
        """
        if not self.is_empty():
            return self.value
        else:
            return other

    def is_empty(self) -> bool:
        """
        Check if the option is empty
        :return: True if the option in None, False otherwise
        """
        return self.to_list().is_empty()

    def to_list(self) -> 'List':
        """
        Convert the option to List Monad
        :return: The corresponding List NamedTuple
        """
        if self.value is None:
            return List([])
        else:
            return List([self.value])

    def map(self, func) -> 'Option':
        """
        Monadic map function implementation
        :param func: The transformation function
        :return: None if the option is None, the transformed content function result otherwise
        """
        return self.to_list().map(func).head_option()
