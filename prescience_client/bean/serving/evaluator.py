# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

from prescience_client.client.prescience_client import PrescienceClient
from prescience_client.enum.valid import Valid
from prescience_client.utils.table_printable import TablePrintable
from termcolor import colored


class Evaluator(object):
    """
    Prescience evaluator object
    """

    def __init__(self,
                json_dict: dict,
                prescience: PrescienceClient = None
    ):
        """
        Constructor for Evaluator object
        :param json_dict: The json dictionnary answered by prescience api
        :param prescience: The prescience client
        """
        self.json_dict = json_dict
        self.prescience = prescience

    def get_problem_type(self) -> str:
        """
        Access the problem type of the evaluator
        :return: the problem type of the evaluator
        """
        return self.json_dict.get('problem_type', None)

    def get_label(self) -> str:
        """
        Access the label of the evaluator
        :return: the label of the evaluator
        """
        return self.json_dict.get('label', None)

    def get_inputs(self) -> list:
        """
        Access inputs of the evaluator
        :return: The inputs of the evaluator
        """
        return [Input(x) for x in self.json_dict.get('inputs')]

class Input(TablePrintable):
    """
    Evaluator's input class, inherit from TablePrintable
    """

    @classmethod
    def table_header(cls) -> list:
        return ['attribute', 'type', 'value', 'valid']

    def table_row(self) -> dict:
        ok_ko, ok_ko_message  = self.is_valid()
        colored_placeholder = self.get_placeholder()
        if ok_ko == Valid.KO:
            colored_placeholder = colored(colored_placeholder, 'red')
        elif ok_ko == Valid.OK:
            colored_placeholder = colored(colored_placeholder, 'green')
        return {
            'attribute': self.get_name(),
            'type': self.get_type(),
            'value': colored_placeholder,
            'valid': ok_ko_message
        }

    def __init__(self,
                json_dict: dict,
                place_holder = None
    ):
        """
        Constructor of an evaluator's input
        :param json_dict: The JSON dictionary sent by prescience
        :param place_holder: The user given value for that input
        """
        self.json_dict = json_dict
        self.placeholder = place_holder

    def get_name(self):
        """
        Access the name of the input
        :return:
        """
        return self.json_dict.get('name', None)

    def get_type(self):
        """
        Access the type of the input
        :return: the type of the input
        """
        return self.json_dict.get('type', None)

    def get_value(self):
        """
        Access the values of the input
        :return: the values of the input
        """
        return self.json_dict.get('values', None)

    def get_placeholder(self):
        """
        Access the current user given value for that input
        :return: the current user given value for that input
        """
        return self.placeholder

    def set_placeholder(self, place_holder):
        """
        Set the current input value
        :param place_holder: the new current input value
        :return:
        """
        self.placeholder = place_holder
        return self

    def is_valid(self):
        """
        Test if the current input value is valid accordingly to the input's type
        :return: The tuple2 (Valid enum, Explanation message)
        """
        if self.get_placeholder() is None:
            return Valid.WARN, 'WARN: Value is not set'
        elif not self.is_correct_type(self.get_type(), self.get_placeholder()):
            return Valid.KO, colored(f'KO: Expected type is {self.get_type()}', 'red')
        else:
            return Valid.OK, colored('OK', 'green')

    def is_valid_message(self):
        """
        Return the "is_valid" message for the current input
        :return: the "is_valid" message for the current input
        """
        _, message = self.is_valid()
        return message

    def is_ko(self) -> bool:
        """
        Is the validation ko ?
        :return: true if the validation is KO false otherwise
        """
        valid, _ = self.is_valid()
        return valid == Valid.KO

    @staticmethod
    def is_correct_type(expected_type: str, value)-> bool:
        """
        Compare the type with the given value
        :param expected_type: The expected type
        :param value: The compared value
        :return: True if the value's type is correct with the expected one, false otherwise
        """
        if expected_type == 'integer':
            return isinstance(value, int)
        elif expected_type == 'boolean':
            return isinstance(value, bool)
        elif expected_type == 'string':
            return isinstance(value, str)
        else:
            return False
