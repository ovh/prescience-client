import json

import typing

import copy
from PyInquirer import prompt
from termcolor import colored

from prescience_client import PrescienceClient, OutputFormat
from prescience_client.bean.config import Config
from prescience_client.bean.hyperparameter import Hyperparameter
from prescience_client.utils.monad import Option
from prescience_client.utils.table_printable import TablePrintable, DictPrintable, TablePrinter


class AlgorithmConfiguration(TablePrintable):
    """
    Prescience configuration object for machine learning algorithms
    Inherit from TablePrintable so that it can be easily printed as list on stdout
    Inherit from DictPrintable so that it can be easily printed as single dict object on stdout
    """

    def __init__(self,
                json_dict: dict,
                prescience: PrescienceClient = None):
        """
        Constructor of prescience configuration object for machine learning algorithms
        :param json_dict: the source JSON dict received from prescience
        :param prescience: the prescience client (default: None)
        """
        self.json_dict = json_dict
        self.prescience = prescience

    def get_name(self) -> str:
        return self.json_dict.get('name')

    def get_display_name(self) -> str:
        return self.json_dict.get('display_name')

    def get_description_link(self) -> str:
        return self.json_dict.get('description_link')

    def get_backend(self) -> str:
        return self.json_dict.get('backend')

    def get_class_identifier(self) -> str:
        return self.json_dict.get('class_identifier')

    def get_multioutput(self) -> bool:
        return self.json_dict.get('multioutput')

    def get_hyperparameters(self) -> list:
        hyperparameters_dict = self.json_dict.get('hyperparameters')
        return Option(hyperparameters_dict)\
            .map(lambda x: [Hyperparameter(id=k, json_dict=v) for k, v in x.items()])\
            .get_or_else(None)

    def show(self, ouput: OutputFormat = OutputFormat.TABLE):
        """
        Display the current algorithm configuration on std out
        :param ouput: The output format
        """
        if ouput == OutputFormat.JSON:
            print(json.dumps(self.json_dict))
        else:
            description_dict = {k: v for k, v in self.json_dict.items() if k not in ['hyperparameters']}
            TablePrinter.print_dict('ALGORITHMS', description_dict)
            print(TablePrinter.get_table(Hyperparameter, self.get_hyperparameters()))

    def interactive_kwargs_instanciation(self) -> Config:
        """
        Instanciate dictionary of 'kwargs' arguments from an interactive prompt
        :return: the 'kwargs' dictionary
        """
        questions = [x.get_pyinquirer_question() for x in self.get_hyperparameters()]
        answers = prompt(questions)
        config = self.instance_config()
        for k, v in answers.items():
            config.add_kwargs(k, v)
        return config

    def instance_config(self) -> Config:
        """
        Instanciate a configuration object form the current algorithm configuration
        :return: a newly created Config object
        """
        return Config.from_attributes(
            name=self.get_name(),
            display_name=self.get_display_name(),
            backend=self.get_backend(),
            class_identifier=self.get_class_identifier()
        )

    @classmethod
    def table_header(cls) -> list:
        return ['id', 'display_name', 'backend', 'class_identifier']

    def table_row(self) -> dict:
        return {
            'id': self.get_name(),
            'display_name': self.get_display_name(),
            'backend': self.get_backend(),
            'class_identifier': self.get_class_identifier(),
            'description_link': self.get_description_link()
        }


class AlgorithmConfigurationList(typing.NamedTuple):
    json_dict: dict

    def get_algorithm_list_names(self) -> list:
        return [k for k, _ in self.json_dict.items()]

    def get_algorithm(self, name: str, prescience: PrescienceClient = None) -> AlgorithmConfiguration:
        return Option(self.json_dict.get(name))\
            .map(lambda x: AlgorithmConfiguration(json_dict=x, prescience=prescience))\
            .get_or_else(None)

    def get_algorithm_list(self, prescience: PrescienceClient = None):
        return [self.get_algorithm(name=k, prescience=prescience) for k, _ in self.json_dict.items()]

    def show(self, ouput: OutputFormat = OutputFormat.TABLE):
        """
        Show the current page on stdout
        """
        if ouput == OutputFormat.JSON:
            print(json.dumps(self.json_dict))
        else:
            table = TablePrinter.get_table(AlgorithmConfiguration, self.get_algorithm_list())
            print(table.get_string(title=colored('ALGORITHMS', 'yellow', attrs=['bold'])))
        return self

