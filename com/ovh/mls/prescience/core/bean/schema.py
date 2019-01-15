# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

from com.ovh.mls.prescience.core.utils.table_printable import TablePrintable, TablePrinter
from termcolor import colored
import copy

class Schema(object):
    """
    Prescience Schema object
    """
    def __init__(self, json: dict):
        """
        Constructor of Schema object
        :param json: the source JSON dict received from prescience
        """
        self.json = json
        self.mask = None

    def set_mask(self, selected_columns: list) -> 'Schema':
        """
        Copy the current Schema and apply only the given selected column
        :param selected_columns: the wanted subset of columns
        :return: the copy of the current schema with selected columns
        """
        schema_copy = copy.deepcopy(self)
        schema_copy.mask = selected_columns
        return schema_copy

    def type(self):
        """
        Getter of the type attribute
        :return: the type attribute
        """
        return self.json.get('type', None)

    def fields(self):
        """
        Getter if the field objects for the currents schema
        :return: the field objects
        """
        all_fields = [Field(x) for x in self.json.get('fields', None)]
        if self.mask is not None:
            for field in all_fields:
                if self.mask.__contains__(field.name()):
                    field.set_is_selected(True)
                else:
                    field.set_is_selected(False)

        return all_fields

    def show(self):
        """
        Show the current schema on stdout
        """
        print(TablePrinter.get_table(Field, self.fields()))
        return self


class Field(TablePrintable):
    """
    Schema Field object
    """

    def __init__(self, json: dict):
        self.json = json
        self.is_selected = None

    def set_is_selected(self, value: bool):
        self.is_selected = value

    @classmethod
    def table_header(cls) -> list:
        return ['name', 'type', 'nullable', 'n_cat', 'ratio', 'n_pop', 'median', 'mode', 'positive']

    def table_row(self) -> dict:
        return {
            'name': self.colored_name(),
            'type': self.type(),
            'nullable': self.nullable(),
            'n_cat': self.metadata().n_cat(),
            'ratio': self.metadata().ratio(),
            'n_pop': self.metadata().n_pop(),
            'median': self.metadata().median(),
            'mode': self.metadata().mode(),
            'positive': self.metadata().positive()
        }


    def name(self):
        """
        Getter of the name attribute
        :return: the name attribute
        """
        return self.json.get('name', None)

    def type(self):
        """
        Getter of the type attribute
        :return: the type attribute
        """
        return self.json.get('type', None)

    def nullable(self):
        """
        Getter of the nullable attribute
        :return: the nullable attribute
        """
        return self.json.get('nullable', None)

    def metadata(self):
        """
        Getter of the metadata object attribute
        :return: the metadata object attribute
        """
        return Metadata(self.json.get('metadata', None))

    def colored_name(self):
        result = self.name()
        if self.is_selected is not None and self.is_selected is True:
            result = colored(result, 'green')
        elif self.is_selected is not None and self.is_selected is False:
            result = colored(result, 'red')
        return result

class Metadata(object):
    """
    Metadata field object
    """
    def __init__(self, json: dict):
        self.json = json

    def n_cat(self):
        """
        Getter of the n_cat attribute
        :return: the n_cat attribute
        """
        return self.json.get('n_cat', None)

    def ratio(self):
        """
        Getter of the ratio attribute
        :return: the ratio attribute
        """
        return self.json.get('ratio', None)

    def n_pop(self):
        """
        Getter of the n_pop attribute
        :return: the n_pop attribute
        """
        return self.json.get('n_pop', None)

    def median(self):
        """
        Getter of the median attribute
        :return: the median attribute
        """
        return self.json.get('median', None)

    def mode(self):
        """
        Getter of the mode attribute
        :return: the mode attribute
        """
        return self.json.get('mode', None)

    def positive(self):
        """
        Getter of the positive attribute
        :return: the positive attribute
        """
        return self.json.get('positive', None)