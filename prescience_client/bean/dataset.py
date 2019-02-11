# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

import copy

from termcolor import colored

from prescience_client.bean.config import Config
from prescience_client.bean.page_result import PageResult
from prescience_client.bean.source import Source
from prescience_client.bean.task import Task
from prescience_client.client.prescience_client import PrescienceClient
from prescience_client.config.constants import DEFAULT_SCORING_METRIC
from prescience_client.enum.scoring_metric import ScoringMetric
from prescience_client.enum.status import Status
from prescience_client.utils.table_printable import TablePrintable, DictPrintable
from prescience_client.utils.tree_printer import SourceTree


class Dataset(TablePrintable, DictPrintable):
    """
    Prescience dataset object
    Inherit from TablePrintable so that it can be easily printed as list on stdout
    Inherit from DictPrintable so that it can be easily printed as single dict object on stdout
    """

    def __init__(
            self,
            json: dict,
            prescience: PrescienceClient = None
    ):
        """
        Constructor of prescience dataset object
        :param json: the source JSON dict received from prescience
        :param prescience: the prescience client (default: None)
        """
        self.json_dict = json
        self.selected = False
        self.prescience = prescience

    def get_description_dict(self) -> dict:
        description_dict = copy.copy(self.json_dict)
        description_dict['status'] = self.status()
        return description_dict

    def uuid(self):
        """
        Getter of the uuid
        :return: the uuid
        """
        return self.json_dict.get('uuid', None)

    def source(self):
        """
        Getter of the related source object
        :return:
        """
        source_dict = self.json_dict.get('source', None)
        if source_dict is not None:
            return Source(source_dict, self.prescience)
        else:
            return None

    def set_selected(self):
        """
        Set the current dataset as selected (will be printed colored in stdout)
        """
        self.selected = True

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
        Getter if the last_update attribute
        :return: the last_update attribute
        """
        return self.json_dict.get('last_update', None)

    def status(self):
        """
        Getter of the status object attribute
        :return: the status object attribute
        """
        return Status[self.json_dict['status']]

    def dataset_id(self):
        """
        Getter of the dataset ID attribute
        :return: the dataset ID
        """
        return self.json_dict.get('dataset_id', None)

    def source_id(self):
        """
        Getter of the source ID attribute
        :return: the source ID
        """
        return self.json_dict.get('source_id', None)

    def dataset_url(self):
        """
        Getter of the dataset_url attribute
        :return: the dataset_url
        """
        return self.json_dict.get('dataset_url', None)

    def label_id(self):
        """
        Getter of the label_id attribute
        :return: the label_id
        """
        return self.json_dict.get('label_id', None)

    def problem_type(self):
        """
        Getter if the problem_type attribute
        :return: the problem_type attribute
        """
        return self.json_dict.get('problem_type', None)

    def nb_fold(self):
        """
        Getter of the nb_fold attribute
        :return: the nb_fold attribute
        """
        return self.json_dict.get('nb_fold', None)

    def selected_columns(self):
        """
        Getter of the selected_columns attribute
        :return: the selected_columns attribute
        """
        return self.json_dict.get('selected_columns', None)

    def test_dataset_file_url(self):
        """
        Getter of the test_dataset_file_url attribute
        :return: the test_dataset_file_url attribute
        """
        return self.json_dict.get('test_dataset_file_url', None)

    def root_uuid(self):
        """
        Getter of the root_uuid attribute
        :return: the root_uuid attribute
        """
        return self.json_dict.get('root_uuid', None)

    def root_id(self):
        """
        Getter of the root_id attribute
        :return: the root_id attribute
        """
        return self.json_dict.get('root_id', None)

    def schema(self):
        """
        Getter of the schema object attribute
        :return: the schema object attribute
        """
        source_schema = self.source().schema()
        return source_schema.set_mask(self.selected_columns())

    @classmethod
    def table_header(cls) -> list:
        return ['dataset_id', 'status', 'source_id', 'problem_type']

    def table_row(self) -> dict:
        return {
            'dataset_id': self.dataset_id(),
            'status': self.status(),
            'source_id': self.source_id(),
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
        """
        Delete the current dataset
        """
        self.prescience.delete_dataset(self.dataset_id())

    def optimize(self,
                 scoring_metric: ScoringMetric = DEFAULT_SCORING_METRIC,
                 budget: int = None,
                 optimization_method: str = None,
                 custom_parameter: dict = None,
                 ) -> Task:
        """
        Launch an optimize task from the current dataset object
        :param scoring_metric: The scoring metric that we want to optimize on
        :param budget: The budget to consume before stopping the optimization
        :return: The task object of the Optimize Task
        """
        return self.prescience.optimize(
            dataset_id=self.dataset_id(),
            scoring_metric=scoring_metric,
            budget=budget,
            optimization_method=optimization_method,
            custom_parameter=custom_parameter
        )

    def evaluate_custom_config(self, config: Config) -> Task:
        """
        Launch the evaluation of a single custom configuration from the current dataset
        :param config: The custom configuration that we want to evaluate
        :return: The evaluation task
        """
        return self.prescience.custom_config(dataset_id=self.dataset_id(), config=config)

    def evaluation_results(self, page: int = 1) -> PageResult:
        """
        Get the paginated list of related evaluation results for the current dataset
        :param page: The number of the page to get
        :return: the page object containing the evaluation results
        """
        return self.prescience.get_evaluation_results(dataset_id=self.dataset_id(), page=page)

    def create_mask(self,
                    mask_id: str,
                    selected_column: list) -> 'Dataset':
        """
        Create a Mask Dataset from the current Dataset
        :param mask_id: The new ID that we want to create for the Mask Dataset
        :param selected_column: The subset of the initial Dataset that we want to keep for the Mask Dataset
        :return: The new Mask Dataset
        """
        return self.prescience.create_mask(
            dataset_id=self.dataset_id(),
            mask_id=mask_id,
            selected_column=selected_column)

    def refresh_dataset(self):
        """
        Launch a refresh task on the current dataset
        :return: The refresh task object
        """
        return self.prescience.refresh_dataset(dataset_id=self.dataset_id())

    def tree(self) -> SourceTree:
        """
        Construct the SourceTree object of the current dataset (use for printing the tree structure on stdout)
        :return: The SourceTree object
        """
        return SourceTree(source_id=self.source().source_id, selected_dataset=self.dataset_id())
