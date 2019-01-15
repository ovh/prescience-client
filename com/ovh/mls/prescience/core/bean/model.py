# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

import copy

from com.ovh.mls.prescience.core.bean.config import Config
from com.ovh.mls.prescience.core.bean.dataset import Dataset
from com.ovh.mls.prescience.core.bean.source import Source
from com.ovh.mls.prescience.core.client.prescience_client import PrescienceClient
from com.ovh.mls.prescience.core.enum.status import Status
from com.ovh.mls.prescience.core.utils.table_printable import TablePrintable, DictPrintable
from termcolor import colored

from com.ovh.mls.prescience.core.utils.tree_printer import SourceTree


class Model(TablePrintable, DictPrintable):
    """
    Prescience model object
    Inherit from TablePrintable so that it can be easily printed as list on stdout
    Inherit from DictPrintable so that it can be easily printed as single dict object on stdout
    """

    def __init__(self,
                 json: dict,
                prescience: PrescienceClient = None):
        """
        Constructor of prescience model object
        :param json: the source JSON dict received from prescience
        :param prescience: the prescience client (default: None)
        """
        self.json_dict = json
        self.selected = False
        self.prescience = prescience

    def set_selected(self):
        """
        Set the current model as selected (will be printed colored in stdout)
        """
        self.selected = True

    @classmethod
    def table_header(cls) -> list:
        return [
            'model_id',
            'status',
            'config_name',
            'dataset_id',
            'source_id'
        ]

    def table_row(self) -> dict:
        return {
            'model_id': self.model_id(),
            'status': self.status(),
            'config_name': self.config().name(),
            'dataset_id': self.dataset().dataset_id(),
            'source_id': self.source().source_id
        }

    def get_description_dict(self) -> dict:
        description_dict = copy.copy(self.json_dict)
        description_dict['status'] = self.status()
        return description_dict

    def uuid(self):
        """
        Getter of the uuid attribute
        :return: the uuid attribute
        """
        return self.json_dict.get('uuid', None)

    def source(self):
        """
        Getter of the linked source object
        :return: the source object
        """
        source_json = self.json_dict.get('source', None)
        source = None
        if source_json is not None:
            source = Source(source_json, self.prescience)
        return source

    def dataset(self):
        """
        Getter of the linked dataset object
        :return: the dataset object
        """
        dataset_json = self.json_dict.get('dataset', None)
        dataset = None
        if dataset_json is not None:
            dataset = Dataset(json=dataset_json, prescience=self.prescience)
        return dataset

    def multiclass(self):
        """
        Getter of the multiclass attribute
        :return: the multiclass attribute
        """
        return self.json_dict.get('multiclass', None)

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

    def status(self):
        """
        Getter of the status object attribute
        :return: the status object
        """
        return Status[self.json_dict['status']]

    def problem_type(self):
        """
        Getter of the problem_type attribute
        :return: the problem_type
        """
        return self.json_dict.get('problem_type', None)

    def label_id(self):
        """
        Getter of the label_id attribute
        :return: the label_id
        """
        return self.json_dict.get('label_id', None)

    def model_id(self):
        """
        Getter of the model_id attribute
        :return: the model_id
        """
        return self.json_dict.get('model_id', None)

    def config(self) -> Config:
        """
        Getter of the config object attribute
        :return: the config object
        """
        json_config = self.json_dict.get('config', None)
        config = None
        if json_config is not None:
            config = Config(json_config)
        return config

    def model_url(self):
        """
        Getter of the model_url object attribute
        :return: the model_url object
        """
        return self.json_dict.get('model_url', None)

    def shap_summary_file_url(self):
        """
        Getter of the shap_summary_file_url object attribute
        :return: the shap_summary_file_url object
        """
        return self.json_dict.get('shap_summary_file_url', None)

    def metrics_file_url(self):
        """
        Getter of the metrics_file_url object attribute
        :return: the metrics_file_url object
        """
        return self.json_dict.get('metrics_file_url', None)

    def evaluations_file_url(self):
        """
        Getter of the evaluations_file_url object attribute
        :return: the evaluations_file_url object
        """
        return self.json_dict.get('evaluations_file_url', None)

    def __str__(self):
        status = self.status()
        main_name = 'Model'
        if self.selected:
            main_name = colored(main_name, 'yellow')

        return f'{main_name}({colored(self.model_id(), status.color())})'

    def retrain(self,
                chain_metric_task: bool = True
                ):
        """
        Launch a Re-Train task on the current model
        :param chain_metric_task: should chain the train task with a metric task ? (default: True)
        :return:
        """
        return self.prescience.retrain(
            model_id=self.model_id(),
            chain_metric_task=chain_metric_task
        )

    def tree(self) -> SourceTree:
        """
        Construct the SourceTree object of the current model (use for printing the tree structure on stdout)
        :return: The SourceTree object
        """
        return SourceTree(source_id=self.source().source_id, selected_model=self.model_id())

    def delete(self):
        """
        Delete the current model
        """
        self.prescience.delete_model(self.model_id())
