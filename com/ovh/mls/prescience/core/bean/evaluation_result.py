# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

from com.ovh.mls.prescience.core.bean.config import Config
from com.ovh.mls.prescience.core.client.prescience_client import PrescienceClient
from com.ovh.mls.prescience.core.utils.table_printable import DictPrintable, TablePrintable

from termcolor import colored
import copy


class EvaluationResult(TablePrintable, DictPrintable):
    """
    Prescience EvaluationResult object
    Inherit from TablePrintable so that it can be easily printed as list on stdout
    Inherit from DictPrintable so that it can be easily printed as single dict object on stdout
    """

    def __init__(self,
                 json_dict: dict,
                 prescience: PrescienceClient = None
                 ):
        """
        Constructor of prescience EvaluationResult object
        :param json_dict: the source JSON dict received from prescience
        :param prescience: the prescience client (default: None)
        """
        self.json_dict = json_dict
        self.prescience = prescience

    @classmethod
    def table_header(cls) -> list:
        return ['config_name', 'steps', 'spent_time', 'status', 'f1_cost', 'roc_auc_cost', 'accuracy_cost', 'cohen_kappa_cost', 'average_precision_cost']

    @classmethod
    def table_formatter(cls, table: list) -> list:
        formatted_table = []
        for x in table:
            x_copy = copy.copy(x)
            for column_name in ['f1_cost', 'roc_auc_cost', 'accuracy_cost', 'cohen_kappa_cost', 'average_precision_cost']:
                max_column = max([x[column_name] for x in table])
                min_column = min([x[column_name] for x in table])
                if x[column_name] == max_column:
                    x_copy[column_name] = colored(max_column, 'red')
                if x[column_name] == min_column:
                    x_copy[column_name] = colored(min_column, 'green')
            formatted_table.append(x_copy)

        return formatted_table

    def table_row(self) -> dict:
        return {
            'config_name': self.config().name(),
            'steps': f'{self.current_step()}/{self.total_step()}',
            'spent_time': self.spent_time(),
            'status': self.status(),
            'f1_cost': round(self.costs().get('f1', None), 3),
            'roc_auc_cost': round(self.costs().get('roc_auc', None), 3),
            'accuracy_cost': round(self.costs().get('accuracy', None), 3),
            'cohen_kappa_cost': round(self.costs().get('cohen_kappa', None), 3),
            'average_precision_cost': round(self.costs().get('average_precision', None), 3)
        }

    def get_description_dict(self) -> dict:
        return self.json_dict

    def uuid(self):
        """
        Getter of the uuid attribute
        :return: the uuid attribute
        """
        return self.json_dict.get('uuid', None)

    def status(self):
        """
        Getter of the status attribute
        :return: the status attribute
        """
        return self.json_dict.get('status', None)

    def created_at(self):
        """
        Getter of the created_at attribute
        :return: the created_at attribute
        """
        return self.json_dict.get('created_at', None)

    def last_update(self):
        """
        Getter of the last_update attribute
        :return: the last_update attribute
        """
        return self.json_dict.get('last_update', None)

    def current_step(self):
        """
        Getter of the current_step attribute
        :return: the current_step attribute
        """
        return self.json_dict.get('current_step', None)

    def current_step_description(self):
        """
        Getter of the current_step_description attribute
        :return: the current_step_description attribute
        """
        return self.json_dict.get('current_step_description', None)

    def total_step(self):
        """
        Getter of the total_step attribute
        :return: the total_step attribute
        """
        return self.json_dict.get('total_step', None)

    def dataset_uuid(self):
        """
        Getter of the dataset_uuid attribute
        :return: the dataset_uuid attribute
        """
        return self.json_dict.get('dataset_uuid', None)

    def spent_time(self):
        """
        Getter of the spent_time attribute
        :return: the spent_time attribute
        """
        return self.json_dict.get('spent_time', None)

    def costs(self):
        """
        Getter of the costs attribute
        :return: the costs attribute
        """
        return self.json_dict.get('costs', None)

    def costs_std(self):
        """
        Getter of the costs_std attribute
        :return: the costs_std attribute
        """
        return self.json_dict.get('costs_std', None)

    def config(self):
        """
        Getter of the config attribute
        :return: the config attribute
        """
        config_dict = self.json_dict.get('config', None)
        if config_dict is not None:
            return Config(config_dict)
        else:
            return None

    def train(self,
              model_id: str,
              compute_shap_summary: bool = False,
              chain_metric_task: bool = True
              ):
        """
        Launch a train task from the current evaluation result for creating a model
        :param model_id: The id that we want for the model
        :param compute_shap_summary: should chain the train task with a compute shap summary task ? (default: false)
        :param chain_metric_task: should chain the train task with a metric task ? (default: true)
        :return: The Train Task object
        """
        return self.prescience.train(
            evaluation_uuid=self.uuid(),
            model_id=model_id,
            compute_shap_summary=compute_shap_summary,
            chain_metric_task=chain_metric_task
        )