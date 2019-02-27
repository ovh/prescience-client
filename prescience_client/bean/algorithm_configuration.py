import json
import typing

from PyInquirer import prompt
from termcolor import colored

from prescience_client import PrescienceClient, OutputFormat, AlgorithmConfigurationCategory
from prescience_client.bean.config import Config
from prescience_client.bean.hyperparameter import Hyperparameter, AlgorithmCondition
from prescience_client.utils.monad import Option, List
from prescience_client.utils.table_printable import TablePrintable, TablePrinter
from prescience_client.utils.validator import FloatValidator, IntegerValidator


class AlgorithmConfiguration(TablePrintable):
    """
    Prescience configuration object for machine learning algorithms
    Inherit from TablePrintable so that it can be easily printed as list on stdout
    Inherit from DictPrintable so that it can be easily printed as single dict object on stdout
    """

    def __init__(self,
                json_dict: dict,
                category: AlgorithmConfigurationCategory,
                prescience: PrescienceClient = None):
        """
        Constructor of prescience configuration object for machine learning algorithms
        :param json_dict: the source JSON dict received from prescience
        :param prescience: the prescience client (default: None)
        """
        self.json_dict = json_dict
        self.category = category
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

    def get_fit_dimension(self) -> int:
        return self.json_dict.get('fit_dimension')

    def get_hyperparameters(self) -> list:
        hyperparameters_dict = self.json_dict.get('hyperparameters')
        return Option(hyperparameters_dict)\
            .map(lambda x: [Hyperparameter(param_id=k, json_dict=v) for k, v in x.items()])\
            .get_or_else(None)

    def get_conditions(self) -> list:
        condition_dict = self.json_dict.get('conditions')
        return [AlgorithmCondition(x) for x in condition_dict]

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


    @staticmethod
    def key_in_value(key, values):
        return lambda x: x.get(key) in values

    def interactive_kwargs_instanciation(self) -> Config:
        """
        Instanciate dictionary of 'kwargs' arguments from an interactive prompt
        :return: the 'kwargs' dictionary
        """
        questions = [x.get_pyinquirer_question() for x in self.get_hyperparameters()]
        conditions = self.get_conditions()

        # applying conditions if any
        for condition in conditions:
            child = condition.get_child()
            parent = condition.get_parent()
            condition_type = condition.get_type()
            values = condition.get_values()

            question = List([x for x in questions if x.get('name') == child])\
                .head_option()\
                .get_or_else(None)

            if question is not None and condition_type == 'IN':
                question['name'] = parent
                # Need to keep the double lambda because of python scope and closure stuff pb
                question['when'] = (lambda parent_key, values_value: lambda x: x.get(parent_key) in values_value)(parent, values)

        # Put the question with a 'when' value at the end
        questions = sorted(questions, key=lambda q: str(q.get('when') is not None))
                
        # In case of time series forecast, add horizon and discount
        if self.category == AlgorithmConfigurationCategory.TIME_SERIES_FORECAST:
            questions.append({
                'type': 'input',
                'name':  'forecasting_horizon_steps',
                'message': f'forecasting_horizon_steps must be at least 1',
                'default':  str(1),
                'validate': IntegerValidator,
                'filter': int
            })
            questions.append({
                'type': 'input',
                'name':  'forecasting_discount',
                'message': f'forecasting_discount must be between 0.0 (excluded) and 1.1 (included)',
                'default':  str(1.0),
                'validate': FloatValidator,
                'filter': float
            })
            

        # Prompting for answers
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
            class_identifier=self.get_class_identifier(),
            fit_dimension=self.get_fit_dimension(),
            multioutput=self.get_multioutput()
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
    """
    NamedTuple used for a list of AlgorithmConfiguration
    """
    json_dict: dict
    category: AlgorithmConfigurationCategory

    def get_algorithm_list_names(self) -> list:
        return [k for k, _ in self.json_dict.items()]

    def get_algorithm(self, name: str, prescience: PrescienceClient = None) -> AlgorithmConfiguration:
        return Option(self.json_dict.get(name))\
            .map(lambda x: AlgorithmConfiguration(json_dict=x, category=self.category, prescience=prescience))\
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

