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

    def __init__(self,
                 json: dict,
                prescience: PrescienceClient = None):
        self.json_dict = json
        self.selected = False
        self.prescience = prescience

    def set_selected(self):
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
        return self.json_dict.get('uuid', None)

    def source(self):
        source_json = self.json_dict.get('source', None)
        source = None
        if source_json is not None:
            source = Source(source_json, self.prescience)
        return source

    def dataset(self):
        dataset_json = self.json_dict.get('dataset', None)
        dataset = None
        if dataset_json is not None:
            dataset = Dataset(json=dataset_json, prescience=self.prescience)
        return dataset

    def multiclass(self):
        return self.json_dict.get('multiclass', None)

    def created_at(self):
        return self.json_dict.get('created_at', None)

    def last_update(self):
        return self.json_dict.get('last_update', None)

    def status(self):
        return Status[self.json_dict['status']]

    def problem_type(self):
        return self.json_dict.get('problem_type', None)

    def label_id(self):
        return self.json_dict.get('label_id', None)

    def model_id(self):
        return self.json_dict.get('model_id', None)

    def config(self) -> Config:
        json_config = self.json_dict.get('config', None)
        config = None
        if json_config is not None:
            config = Config(json_config)
        return config

    def model_url(self):
        return self.json_dict.get('model_url', None)

    def shap_summary_file_url(self):
        return self.json_dict.get('shap_summary_file_url', None)

    def metrics_file_url(self):
        return self.json_dict.get('metrics_file_url', None)

    def evaluations_file_url(self):
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
        return self.prescience.retrain(
            model_id=self.model_id(),
            chain_metric_task=chain_metric_task
        )

    def tree(self) -> SourceTree:
        return SourceTree(source_id=self.source().source_id, selected_model=self.model_id())

    def delete(self):
        self.prescience.delete_model(self.model_id())
