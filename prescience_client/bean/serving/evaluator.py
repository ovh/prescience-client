# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.
from PyInquirer import prompt

from prescience_client.client.prescience_client import PrescienceClient
from prescience_client.enum.problem_type import ProblemType
from prescience_client.enum.valid import Valid
from prescience_client.exception.prescience_client_exception import PrescienceClientException
from prescience_client.utils.table_printable import TablePrintable, DictPrintable
from termcolor import colored

from prescience_client.utils.validator import IntegerValidator, FloatValidator, StringValidator


class Evaluator(DictPrintable):
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

    def get_description_dict(self) -> dict:
        return self.json_dict

    def get_problem_type(self) -> ProblemType:
        """
        Access the problem type of the evaluator
        :return: the problem type of the evaluator
        """
        problem_type_str = self.json_dict.get('problem_type', None)
        return ProblemType(problem_type_str)

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

    def get_max_steps(self) -> int:
        """
        Access the max_steps attribute
        """
        return self.json_dict.get('max_steps')

    def get_forecasting_horizon_steps(self) -> int:
        """
        Access the forecasting_horizon_steps attribute
        """
        return self.json_dict.get('forecasting_horizon_steps')

    def get_time_feature_name(self) -> str:
        """
        Access the time_feature attribute
        """
        return self.json_dict.get('time_feature')

    def get_span(self) -> int:
        """
        Access the span attribute
        """
        return self.json_dict.get('span')

    def interactiv_ts_forecast_payload(self) -> dict:
        """
        Interactively generate a payload for TS
        """
        final_dict = {}
        for einput in self.get_inputs():
            questions = []
            validator, filter_arg = einput.get_validator_and_filter()
            for step_number in range(0, self.get_max_steps()):
                t = self.get_max_steps() - step_number - 1
                key = f'{einput.get_name()}_t'
                if t != 0:
                    key = f'{key}-{t}'
                questions.append({
                    'type': 'input',
                    'name': key,
                    'message': f'`{key}` parameter ({einput.get_type()}) ?',
                    'validate': validator,
                    'filter': filter_arg
                })
            answers = prompt(questions)
            final_dict[einput.get_name()] = list(answers.values())
        return final_dict

    def interactiv_default_payload(self) -> dict:
        """
        Interactively generate a payload for regression of classification
        """
        final_dict = {}
        questions = []
        for einput in self.get_inputs():
            validator, filter_arg = einput.get_validator_and_filter()
            questions.append({
                'type': 'input',
                'name': einput.get_name(),
                'message': f'`{einput.get_name()}` parameter ({einput.get_type()}) ?',
                'validate': validator,
                'filter': filter_arg
            })
        answers = prompt(questions)
        final_dict.update(answers)
        return final_dict

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

    def get_validator_and_filter(self):
        """
        Return the correct (validator, filter) tuple for the current input type
        """
        switch = {
            'integer': (IntegerValidator, int),
            'float': (FloatValidator, float),
            'string': (StringValidator, str),
            'double': (FloatValidator, float)
        }
        validator = switch.get(self.get_type())
        if validator is None:
            raise PrescienceClientException(Exception(f'Undefined type in prescience client : {self.get_type()}'))

        return validator

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
