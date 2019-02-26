from prescience_client.utils.monad import Option
from prescience_client.utils.table_printable import DictPrintable, TablePrintable
from prescience_client.utils.validator import IntegerValidator, FloatValidator


class Hyperparameter(DictPrintable, TablePrintable):

    def __init__(self, id: str, json_dict: dict):
        self.id = id
        self.json_dict = json_dict

    def get_name(self):
        return self.json_dict.get('name')

    def get_type(self):
        return self.json_dict.get('type')

    def get_log(self):
        return self.json_dict.get('log')

    def get_lower(self):
        return self.json_dict.get('lower')

    def get_upper(self):
        return self.json_dict.get('upper')

    def get_default(self):
        return self.json_dict.get('default')

    def get_choices(self):
        return self.json_dict.get('choices')

    def get_value(self):
        return self.json_dict.get('value')

    def get_description_dict(self) -> dict:
        return self.json_dict

    @classmethod
    def table_header(cls) -> list:
        return ['id', 'name', 'type', 'log', 'lower', 'upper', 'default', 'choices', 'value']

    def table_row(self) -> dict:
        return {
            'id': str(self.id),
            'name': Option(self.get_name()).get_or_else('-'),
            'type': Option(self.get_type()).get_or_else('-'),
            'log': Option(self.get_log()).get_or_else('-'),
            'lower': Option(self.get_lower()).get_or_else('-'),
            'upper': Option(self.get_upper()).get_or_else('-'),
            'default': Option(self.get_default()).get_or_else('-'),
            'choices': Option(self.get_choices()).get_or_else('-'),
            'value': Option(self.get_value()).get_or_else('-')
        }

    def get_pyinquirer_question(self):
        if self.get_type() == 'categorical':
            return {
                'type': 'list',
                'name': str(self.get_name()),
                'message': f'{self.get_name()}',
                'choices': self.get_choices()
            }

        elif self.get_type() == 'constant':
            result_dict = {
                'type': 'list',
                'name':  str(self.get_name()),
                'message': f'{self.get_name()}',
                'choices': [str(self.get_value())]
            }
            if isinstance(self.get_value(), float):
                result_dict['filter'] = lambda val: float(val)
            elif isinstance(self.get_value(), int):
                result_dict['filter'] = lambda val: int(val)
            return result_dict

        elif self.get_type() == 'uniform_int':
            return {
                'type': 'input',
                'name':  str(self.get_name()),
                'message': f'{self.get_name()} between [{self.get_lower()} and {self.get_upper()}]',
                'default':  str(self.get_default()),
                'validate': IntegerValidator,
                'filter': lambda val: int(val)
            }

        elif self.get_type() == 'uniform_float':
            return {
                'type': 'input',
                'name':  str(self.get_name()),
                'message': f'{self.get_name()} between [{self.get_lower()} and {self.get_upper()}]',
                'default':  str(self.get_default()),
                'validate': FloatValidator,
                'filter': lambda val: float(val)
            }

        else:
            raise Exception(f'Unknown type {self.get_type()}')