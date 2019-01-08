# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

import copy

from termcolor import colored

from com.ovh.mls.prescience.core.bean.config import Config
from com.ovh.mls.prescience.core.bean.page_result import PageResult
from com.ovh.mls.prescience.core.bean.source import Source
from com.ovh.mls.prescience.core.bean.task import Task
from com.ovh.mls.prescience.core.client.prescience_client import PrescienceClient
from com.ovh.mls.prescience.core.config.constants import DEFAULT_SCORING_METRIC
from com.ovh.mls.prescience.core.enum.scoring_metric import ScoringMetric
from com.ovh.mls.prescience.core.enum.status import Status
from com.ovh.mls.prescience.core.utils.table_printable import TablePrintable, DictPrintable
from com.ovh.mls.prescience.core.utils.tree_printer import SourceTree


class Dataset(TablePrintable, DictPrintable):

    def __init__(
            self,
            json: dict,
            prescience: PrescienceClient = None
    ):
        self.json_dict = json
        self.selected = False
        self.prescience = prescience

    def get_description_dict(self) -> dict:
        description_dict = copy.copy(self.json_dict)
        description_dict['status'] = self.status()
        return description_dict

    def uuid(self):
        return self.json_dict.get('uuid', None)

    def source(self):
        source_dict = self.json_dict.get('source', None)
        if source_dict is not None:
            return Source(source_dict, self.prescience)
        else:
            return None

    def set_selected(self):
        self.selected = True

    def multiclass(self):
        return self.json_dict.get('multiclass', None)

    def created_at(self):
        return self.json_dict.get('created_at', None)

    def last_update(self):
        return self.json_dict.get('last_update', None)

    def status(self):
        return Status[self.json_dict['status']]

    def dataset_id(self):
        return self.json_dict.get('dataset_id', None)

    def dataset_url(self):
        return self.json_dict.get('dataset_url', None)

    def label_id(self):
        return self.json_dict.get('label_id', None)

    def problem_type(self):
        return self.json_dict.get('problem_type', None)

    def nb_fold(self):
        return self.json_dict.get('nb_fold', None)

    def selected_columns(self):
        return self.json_dict.get('selected_columns', None)

    def test_dataset_file_url(self):
        return self.json_dict.get('test_dataset_file_url', None)

    def root_uuid(self):
        return self.json_dict.get('root_uuid', None)

    def root_id(self):
        return self.json_dict.get('root_id', None)

    def schema(self):
        source_schema = self.source().schema()
        return source_schema.set_mask(self.selected_columns())

    @classmethod
    def table_header(cls) -> list:
        return ['dataset_id', 'status', 'source_id', 'problem_type']

    def table_row(self) -> dict:
        return {
            'dataset_id': self.dataset_id(),
            'status': self.status(),
            'source_id': self.source().source_id,
            'problem_type': self.problem_type()
        }

    def __str__(self):
        status = self.status()
        main_name = 'Dataset'
        if self.root_id() is not None:
            main_name = 'Mask_Dataset'

        if self.selected:
            main_name = colored(main_name, 'yellow')

        return f'{main_name}({colored(self.dataset_id(), status.color())})'

    def delete(self):
        self.prescience.delete_dataset(self.dataset_id())

    def optimize(self,
                 scoring_metric: ScoringMetric = DEFAULT_SCORING_METRIC,
                 budget: int = None,
                 nb_fold: int = None,
                 optimization_method: str = None,
                 custom_parameter: dict = None,
                 ) -> Task:
        return self.prescience.optimize(
            dataset_id=self.dataset_id(),
            scoring_metric=scoring_metric,
            budget=budget,
            nb_fold=nb_fold,
            optimization_method=optimization_method,
            custom_parameter=custom_parameter
        )

    def evaluate_custom_config(self, config: Config) -> Task:
        return self.prescience.custom_config(dataset_id=self.dataset_id(), config=config)

    def evaluation_results(self, page: int = 1) -> PageResult:
        return self.prescience.get_evaluation_results(dataset_id=self.dataset_id(), page=page)

    def create_mask(self,
                    mask_id: str,
                    selected_column: list) -> 'Dataset':
        return self.prescience.create_mask(
            dataset_id=self.dataset_id(),
            mask_id=mask_id,
            selected_column=selected_column)

    def refresh_dataset(self):
        return self.prescience.refresh_dataset(dataset_id=self.dataset_id())

    def tree(self) -> SourceTree:
        return SourceTree(source_id=self.source().source_id, selected_dataset=self.dataset_id())
