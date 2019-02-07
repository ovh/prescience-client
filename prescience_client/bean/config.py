# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

from prescience_client.utils.table_printable import DictPrintable


class Config(DictPrintable):
    """
    Prescience Config object
    Inherit from DictPrintable so that it can be easily printed as single dict object on stdout
    """

    def __init__(self, json_dict: dict):
        """
        Constructor of prescience Config object
        :param json_dict: the source JSON dict received from prescience
        """
        self.json_dict = json_dict

    def get_description_dict(self) -> dict:
        """
        Getter of the get_description_dict attribute
        :return: the get_description_dict attribute
        """
        return self.json_dict

    def name(self):
        """
        Getter of the name attribute
        :return: the name attribute
        """
        return self.json_dict.get('name', None)

    def class_identifier(self):
        """
        Getter of the class_identifier attribute
        :return: the class_identifier attribute
        """
        return self.json_dict.get('class_identifier', None)

    def kwargs(self):
        """
        Getter of the kwargs attribute
        :return: the kwargs attribute
        """
        return self.json_dict.get('kwargs', None)
