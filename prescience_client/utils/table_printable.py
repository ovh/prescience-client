# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

from abc import ABC, abstractmethod
from prettytable import PrettyTable
from termcolor import colored


class TablePrintable(ABC):
    """
    Abstract class to implement if you want a type of object to be part of a printable table list
    """

    @classmethod
    def table_formatter(cls, table: list) -> (list, list):
        """
        Default method which format the given table before printing it
        :param table: The table we want to format
        :return: The tuple2 of (final table header, table with specific format applied)
        """
        return cls.table_header(), table

    @classmethod
    @abstractmethod
    def table_header(cls) -> list:
        """
        :return: The header to use for printing the current object in console as a table
        """
        raise NotImplementedError

    @abstractmethod
    def table_row(self) -> dict:
        """
        :return: The table row for printing the current object in console as a table
        """
        raise NotImplementedError


class DictPrintable(ABC):
    """
    Abstract class to implement if you want a single object to be printable as a table of (key, value) in console with 'show' method
    """

    def table_title(self) -> str:
        """
        Title to use when printing the table
        :return:
        """
        return type(self).__name__.upper()

    @abstractmethod
    def get_description_dict(self) -> dict:
        """
        :return: The dict describing the current object
        """
        raise NotImplementedError

    def show(self) -> 'DictPrintable':
        """
        Print the 'description dict' as a table in console
        :return: The current object
        """
        description_dict = self.get_description_dict()
        TablePrinter.print_dict(self.table_title(), description_dict)
        return self


class TablePrinter(object):
    """
    Utils class containing static method for printing table in console with PrettyTable library
    """

    @staticmethod
    def get_table(clazz: type, table_printable_objects: list) -> PrettyTable:
        """
        Take a list of 'clazz' object and print this list as a table in console
        'clazz' should be a sub-class of 'TablePrintable'
        """
        if not issubclass(clazz, TablePrintable):
            raise TypeError(f'Classe {clazz} is not a sub-class of TablePrintable')
        table = PrettyTable()
        all_row_dict = [x.table_row() for x in table_printable_objects]
        header, all_row_dict_formatted = clazz.table_formatter(all_row_dict)
        final_header = [''] + list(header)
        all_row = [[x[y] for y in header] for x in all_row_dict_formatted]
        table.field_names = [colored(x, attrs=['bold']) for x in final_header]
        for i in range(len(all_row)):
            row = all_row[i]
            row.insert(0, i)
            table.add_row(row)

        return table

    @staticmethod
    def print_dict(title: str, json_dict: dict, max_value_length: int = 75) -> None:
        """
        Print the given 'json_dict' as a table in console
        :param title: Title to use for the table
        :param json_dict: The dict object that will be printed in console
        :param max_value_length: The max length of string that will be printed entirely
        """
        table = PrettyTable()

        for k, v in json_dict.items():
            if not isinstance(v, dict):
                str_value = str(v)
                if len(str_value) > max_value_length:
                    str_value = str_value[:max_value_length]
                    str_value = f'{str_value}...'

                table.add_row([k, str_value])

        for k, v in json_dict.items():
            if isinstance(v, dict):
                table.add_row(['', ''])
                table.add_row([colored(k, attrs=['bold']), ''])
                for k1, v1 in v.items():
                    str_value = str(v1)
                    if len(str_value) > max_value_length:
                        str_value = str_value[:max_value_length]
                        str_value = f'{str_value}...'

                    table.add_row([k1, str_value])

        print(table.get_string(header=False, title=colored(title, 'yellow', attrs=['bold'])))

