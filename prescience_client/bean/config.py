# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.
import copy

from prescience_client.utils.monad import Option
from prescience_client.utils.table_printable import DictPrintable


class Config(DictPrintable):
    """
    Prescience Config object
    Inherit from DictPrintable so that it can be easily printed as single dict object on stdout
    """
    @classmethod
    def from_attributes(cls,
                        name,
                        display_name,
                        class_identifier,
                        backend,
                        kwargs =None,
                        forecasting_horizon_steps: int=None,
                        forecasting_discount: float=None,
                        fit_dimension: int=None,
                        multioutput: bool=None
                        ) -> 'Config':
        """
        Construct a Config object from its attributes
        :param name: Name of the config
        :param display_name: The display name of the config
        :param class_identifier: The class identifier
        :param backend: The backend attributes
        :param forecasting_horizon_steps: The forecasting horizon steps
        :param forecasting_discount: The forecasting discount
        :param fit_dimension: The fit_dimension parameter
        :param kwargs: The kwargs dictionary for configuration
        :param multioutput: The multioutput parameter
        :return: The newly created Config object
        """
        config = Config(json_dict={})
        config.set_name(name)
        config.set_class_identfier(class_identifier)
        config.set_backend(backend)
        config.set_display_name(display_name)
        if kwargs is not None:
            for k, v in kwargs.items():
                config.add_kwargs(k, v)
        if forecasting_horizon_steps is not None:
            config.set_forecasting_horizon_steps(forecasting_horizon_steps)
        if forecasting_discount is not None:
            config.set_forecasting_discount(forecasting_discount)
        if fit_dimension is not None:
            config.set_fit_dimension(fit_dimension)
        if multioutput is not None:
            config.set_multioutput(multioutput)
        return config


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

    def get_display_name(self):
        """
        Getter of the display_name attribute
        :return: the display_name attribute
        """
        return self.json_dict.get('display_name')

    def set_display_name(self, display_name):
        """
        Setter for the display_name attribute
        :param display_name: new name value
        """
        self.json_dict['display_name'] = display_name

    def set_fit_dimension(self, fit_dimension):
        """
        Setter for the fit_dimension attribute
        :param fit_dimension: the dimension value for fitting
        """
        self.json_dict['fit_dimension'] = fit_dimension

    def get_fit_dimension(self):
        """
        Getter of the fit_dimension attribute
        :return: the fit_dimension attribute
        """
        return self.json_dict.get('fit_dimension')

    def get_backend(self):
        """
        Getter of the name attribute
        :return: the name attribute
        """
        return self.json_dict.get('backend')

    def set_backend(self, backend):
        """
        Setter for the backend attribute
        :param backend: new name value
        """
        self.json_dict['backend'] = backend

    def multioutput(self) -> bool:
        """
        Getter of the multioutput attribute
        :return: the multioutput attribute
        """
        return self.json_dict.get('multioutput')

    def set_multioutput(self, multioutput: bool):
        """
        Setter for the multioutput attribute
        :param multioutput: new multioutput value
        """
        self.json_dict['multioutput'] = multioutput

    def name(self):
        """
        Getter of the name attribute
        :return: the name attribute
        """
        return self.json_dict.get('name', None)

    def set_name(self, name: str):
        """
        Setter for the name attribute
        :param name: new name value
        """
        self.json_dict['name'] = name

    def class_identifier(self):
        """
        Getter of the class_identifier attribute
        :return: the class_identifier attribute
        """
        return self.json_dict.get('class_identifier', None)

    def set_class_identfier(self, class_identifier: str):
        """
        Setter for the class_identifier attribute
        :param class_identifier: new class_identifier value
        """
        self.json_dict['class_identifier'] = class_identifier

    def kwargs(self):
        """
        Getter of the kwargs attribute
        :return: the kwargs attribute
        """
        return self.json_dict.get('kwargs', None)

    def add_kwargs(self, parameter_name, parameter_value) -> 'Config':
        """
        Add a kwargs parameter from its name and its value
        :param parameter_name: the kwargs name
        :param parameter_value: the kwargs value
        """
        if self.kwargs() is None:
            self.json_dict['kwargs'] = {}
        self.kwargs()[parameter_name] = parameter_value
        return self

    def get_forecasting_horizon_steps(self):
        """
        Getter of the forecasting horizon steps
        :return: the forecasting horizon steps
        """
        return Option(self.kwargs())\
            .map(lambda x: x.get('forecasting_horizon_steps'))\
            .get_or_else(None)

    def set_forecasting_horizon_steps(self, forecasting_horizon_steps: int):
        """
        Setter for the forecasting_horizon_steps attribute
        :param forecasting_horizon_steps: new forecasting_horizon_steps value
        """
        self.add_kwargs('forecasting_horizon_steps', forecasting_horizon_steps)

    def get_forecasting_discount(self):
        """
        Getter of the forecasting discount
        :return: the forecasting discount
        """
        return Option(self.kwargs())\
            .map(lambda x: x.get('forecasting_discount'))\
            .get_or_else(None)

    def set_forecasting_discount(self, forecasting_discount: float):
        """
        Setter for the forecasting_discount attribute
        :param forecasting_discount: new forecasting_discount value
        """
        self.add_kwargs('forecasting_discount', forecasting_discount)

    def get_optimization_constants(self):
        """
        Return all constants used for optimization
        :return: all constants used for optimization
        """
        return {
            'forecasting_horizon_steps': self.get_forecasting_horizon_steps(),
            'forecasting_discount': self.get_forecasting_discount()
        }

    def to_dict(self):
        """
        Convert current config object into dictionary
        """
        return copy.deepcopy(self.json_dict)
