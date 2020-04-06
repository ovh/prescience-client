# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

import copy
import pandas
from datetime import datetime
from termcolor import colored

from prescience_client import PrescienceException
from prescience_client.bean.schema import Schema
from prescience_client.client.prescience_client import PrescienceClient
from prescience_client.config.constants import DEFAULT_LABEL_NAME, DEFAULT_PROBLEM_TYPE
from prescience_client.enum.fold_strategy import FoldStrategy
from prescience_client.enum.input_type import InputType
from prescience_client.enum.output_format import OutputFormat
from prescience_client.enum.problem_type import ProblemType
from prescience_client.enum.scoring_metric import ScoringMetric
from prescience_client.enum.status import Status
from prescience_client.utils.table_printable import TablePrintable, DictPrintable
from prescience_client.utils.tree_printer import SourceTree



class Source(TablePrintable, DictPrintable):
    """
    Prescience Source object
    Inherit from TablePrintable so that it can be easily printed as list on stdout
    Inherit from DictPrintable so that it can be easily printed as single dict object on stdout
    """

    def __init__(
            self,
            json_dict: dict,
            prescience: PrescienceClient = None):
        """
        Constructor of prescience source object
        :param json_dict: the source JSON dict received from prescience
        :param prescience: the prescience client (default: None)
        """
        self.json_dict = json_dict
        self.uuid = json_dict.get('uuid', None)
        self.created_at = json_dict.get('created_at', None)
        self.last_update = json_dict.get('last_update', None)
        self.current_step_description = json_dict.get('current_step_description', None)
        self.source_id = json_dict.get('source_id', None)
        self.input_url = json_dict.get('input_url', None)
        self.input_type = json_dict.get('input_type', None)
        self.source_url = json_dict.get('source_url', None)
        self.headers = json_dict.get('headers', None)
        self.selected = False
        self.prescience = prescience

    def get_input_type(self) -> InputType:
        return InputType(self.input_type)

    def get_grouping_keys(self) -> list:
        return self.json_dict.get('input_details').get('grouping_keys')

    def set_selected(self):
        """
        Set the current source as selected (will be printed colored in stdout)
        """
        self.selected = True

    def get_description_dict(self) -> dict:
        description_dict = copy.copy(self.json_dict)
        return description_dict

    def schema(self):
        """
        Getter of the schema object
        :return: the schema object
        """
        schema_dict = self.json_dict.get('schema', None)
        if schema_dict is not None:
            return Schema(schema_dict)
        else:
            return None

    def is_multiclass(self, field_name):
        for field in self.schema().fields():
            if field.name() == field_name:
                return field.metadata().n_cat() > 2
        raise PrescienceException(Exception("Field not found in source."))

    def get_total_row_count(self):
        """
        Access the total row number of your source
        """
        return self.json_dict.get('total_row_count')

    @classmethod
    def table_header(cls) -> list:
        return ['source_id', 'status', 'input_type', 'info']

    def table_row(self, output: OutputFormat) -> dict:
        return {
            'source_id': self.source_id,
            'status': self.status().to_colored(output),
            'input_type': self.input_type,
            'info': self.current_step_description
        }

    def __str__(self):
        status = self.status()

        main_name = 'Source'
        if self.selected:
            main_name = colored(main_name, 'yellow')

        return f'{main_name}({colored(self.source_id, status.color())})'

    def status(self) -> Status:
        """
        Getter of the status object of the current source
        :return: the status object
        """
        return Status[self.json_dict['status']]

    def delete(self):
        """
        Delete the current source on prescience
        """
        self.prescience.delete_source(self.source_id)

    def update(self, last_point_date: datetime = None, sample_span: str = None):
        """
        Update Warp10 source
        last_point_timestamp: The date of the last point to be considered in updating the time serie source. (in us) If not provided it is inferred to now.
        sample_span: The size of the sample to be used in updating the time serie source. If not provided it is inferred to the existing sample span.
        """

        return self.prescience.update_source(self.source_id, last_point_date, sample_span)

    def preprocess(self,
                   dataset_id: str,
                   label: str = DEFAULT_LABEL_NAME,
                   problem_type: ProblemType = DEFAULT_PROBLEM_TYPE,
                   log_enabled: bool = False,
                   selected_column: list = None,
                   time_column: str = None,
                   nb_fold: int = None,
                   fold_size: int = None,
                   fold_strategy: FoldStrategy = None,
                   test_ratio: float = None,
                   formatter: str = None,
                   datetime_exogenous: list = None,
                   granularity: str = None,
                   fold_strategy: FoldStrategy = None):
        """
        Launch a Preprocess Task from the current Source for creating a Dataset
        :param dataset_id: The id that we want for the Dataset
        :param label: The name of the Source column that we want to predict (the label)
        :param problem_type: The type of machine learning problem that we want to solve
        :param log_enabled: Preprocess numeric variable with log10
        :param selected_column: subset of the source column to use for preprocessing, by default it will use all
        :param time_column: Indicates the time column (or step column) for a time-series problem type
        :param nb_fold: The number of fold to create during the preprocessing of the source
        :param fold_size: The number of fold to use on cross-validation
        :param fold_strategy: For time series the way to split data in different fold
        :param test_ratio: The size of test ratio
        :param formatter: The formatter to use for parsing the time_column
        :param datetime_exogenous: (For TS only) The augmented features related to date to computing during preprocessing
        :param granularity: (For TS only) The granularity to use for the date
        :return: The task object of the Preprocess Task
        """
        return self.prescience.preprocess(
            source_id=self.source_id,
            dataset_id=dataset_id,
            label_id=label,
            problem_type=problem_type,
            log_enabled=log_enabled,
            selected_column=selected_column,
            time_column=time_column,
            fold_size=fold_size,
            fold_strategy=fold_strategy,
            nb_fold=nb_fold,
            test_ratio=test_ratio,
            formatter=formatter,
            datetime_exogenous=datetime_exogenous,
            granularity=granularity,
            fold_strategy=fold_strategy
        )

    def tree(self) -> SourceTree:
        """
        Construct the SourceTree object of the current source (use for printing the tree structure on stdout)
        :return: The SourceTree object
        """
        return SourceTree(source_id=self.source_id, selected_source=self.source_id)

    def get_source_id(self) -> str:
        """
        Access the source_id of the source
        """
        return self.source_id

    def start_auto_ml(
            self,
            label_id: str,
            problem_type: ProblemType,
            scoring_metric: ScoringMetric,
            log_enabled: bool = False,
            dataset_id: str = None,
            model_id: str = None,
            time_column: str = None,
            nb_fold: int = None,
            fold_strategy: FoldStrategy = None,
            selected_column: list = None,
            budget: int = None,
            forecasting_horizon_steps: int = None,
            forecast_discount: float = None,
            formatter: str = None,
            datetime_exogenous: list = None,
            granularity: str = None
    ) -> ('Task', str, str):
        """
        Start an auto-ml task from the current source
        :param label_id: ID of the label to predict
        :param problem_type: The type of the problem
        :param scoring_metric: The scoring metric to optimize on
        :param log_enabled: Preprocess numeric variable with log10
        :param dataset_id: The wanted dataset_id (will generate one if unset)
        :param model_id: The wanted model_id (will generate one if unset)
        :param time_column: The ID of the time column (Only in case of a time_series_forecast)
        :param nb_fold: The number of fold to create during the preprocessing of the source
        :param fold_strategy: For time series the way to split data in different fold
        :param selected_column: The column to keep (will keep everything if unset)
        :param budget: The budget to use during optimization
        :param forecasting_horizon_steps: The wanted forecasting horizon (in case of a time_series_forecast)
        :param forecast_discount: The wanted forecasting discount
        :param formatter: (For TS only) The string formatter that prescience should use for parsing date column (ex: yyyy-MM-dd)
        :param datetime_exogenous: (For TS only) The augmented features related to date to computing during preprocessing
        :param granularity: (For TS only) The granularity to use for the date
        :return: The tuple3 of (initial task, dataset id, model id)
        """
        return self.prescience.start_auto_ml(
            source_id=self.source_id,
            dataset_id=dataset_id,
            label_id=label_id,
            model_id=model_id,
            problem_type=problem_type,
            log_enabled=log_enabled,
            scoring_metric=scoring_metric,
            time_column=time_column,
            nb_fold=nb_fold,
            fold_strategy=fold_strategy,
            selected_column=selected_column,
            budget=budget,
            forecasting_horizon_steps=forecasting_horizon_steps,
            forecast_discount=forecast_discount,
            formatter=formatter,
            datetime_exogenous=datetime_exogenous,
            granularity=granularity
        )

    def plot(self, x: str = None, y: str = None, kind: str = None, clss: str = None, block=False):
        self.prescience.plot_source(
            source_id=self.get_source_id(),
            x=x,
            y=y,
            kind=kind,
            clss=clss,
            block=block
        )

    def dataframe(self) -> pandas.DataFrame:
        return self.prescience.source_dataframe(self.source_id)
