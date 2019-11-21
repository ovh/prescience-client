# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

import copy
from datetime import datetime

from prescience_client.bean.config import Config
from prescience_client.bean.dataset import Dataset
from prescience_client.bean.serving.evaluator import Evaluator
from prescience_client.bean.serving.serving_payload import ServingPayload
from prescience_client.bean.source import Source
from prescience_client.client.prescience_client import PrescienceClient
from prescience_client.enum.flow_type import FlowType
from prescience_client.enum.output_format import OutputFormat
from prescience_client.enum.problem_type import ProblemType
from prescience_client.enum.status import Status
from prescience_client.exception.prescience_client_exception import PrescienceClientException
from prescience_client.utils import get_dataframe_real_predict_theoric
from prescience_client.utils.table_printable import TablePrintable, DictPrintable
from termcolor import colored

from prescience_client.utils.tree_printer import SourceTree


class Model(TablePrintable, DictPrintable):
    """
    Prescience model object
    Inherit from TablePrintable so that it can be easily printed as list on stdout
    Inherit from DictPrintable so that it can be easily printed as single dict object on stdout
    """

    @classmethod
    def new(cls, model_id, prescience: PrescienceClient = None):
        """
        Construct a simple Model from a model_id
        :param model_id: 'The model_id'
        :param prescience: The prescience client
        """
        return Model(json={'model_id': model_id}, prescience=prescience)

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
        self.model_evaluator = None

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

    def table_row(self, output: OutputFormat) -> dict:
        return {
            'model_id': self.model_id(),
            'status': self.status().to_colored(output),
            'config_name': self.config().name() if self.config() is not None else None,
            'dataset_id': self.dataset_id(),
            'source_id': self.source_id()
        }

    def get_description_dict(self) -> dict:
        description_dict = copy.copy(self.json_dict)
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
        pb_type = self.json_dict.get('problem_type')
        return ProblemType(pb_type)

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

    def dataset_id(self):
        """
        Getter of the dataset_id attribute
        :return: the dataset_id
        """
        return self.json_dict.get('dataset_id', None)

    def source_id(self):
        """
        Getter of the source_id attribute
        :return: the source_id
        """
        return self.json_dict.get('source_id', None)

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
                chain_metric_task: bool = True,
                enable_shap_summary: bool = None,
                last_point_date: datetime = None,
                sample_span: str = None
                ):
        """
        Launch a Re-Train task on the current model
        :param chain_metric_task: should chain the train task with a metric task ? (default: True)
        :return:
        """
        return self.prescience.retrain(
            model_id=self.model_id(),
            chain_metric_task=chain_metric_task,
            enable_shap_summary = enable_shap_summary,
            last_point_date = last_point_date,
            sample_span = sample_span
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

    def get_evaluation_payload(self,
                               flow_type: FlowType,
                               evaluation_id: str = None,
                               arguments: dict = None
                               ) -> ServingPayload:
        """
        Create a serving payload for requesting the current model
        :param flow_type: The type of the needed evaluation
        :param evaluation_id: The wanted id for the needed evaluation
        :param arguments: The arguments to fill in the payload
        :return: A new serving payload for the current model
        """
        evaluator = self.get_model_evaluator()
        return ServingPayload.new(
            model_id=self.model_id(),
            flow_type=flow_type,
            payload_id=evaluation_id,
            arguments=arguments,
            model_evaluator=evaluator,
            prescience=self.prescience
        )

    def get_model_evaluation_payload(self,
                                     evaluation_id: str = None,
                                     arguments: dict = None
                                     ) -> ServingPayload:
        """
        Create a serving payload to evaluate the current model with the flow type 'TRANSFORM_MODEL'
        (Chain the transformation evaluation and model evaluation)
        :param evaluation_id: The wanted id for the needed evaluation
        :param arguments: The arguments to fill in the payload
        :return: A new serving payload for the current model
        """
        return self.get_evaluation_payload(
            flow_type=FlowType.TRANSFORM_MODEL,
            evaluation_id=evaluation_id,
            arguments=arguments
        )

    def get_transformation_evaluation_payload(self,
                                              evaluation_id: str = None,
                                              arguments: dict = None
                                              ) -> ServingPayload:
        """
        Create a serving payload for evaluate the current model with the flow type 'TRANSFORM'
        (Execute the transformation evaluation only and not the model evaluation)
        :param evaluation_id: The wanted id for the needed evaluation
        :param arguments: The arguments to fill in the payload
        :return: A new serving payload for the current model
        """
        return self.get_evaluation_payload(
            flow_type=FlowType.TRANSFORM,
            evaluation_id=evaluation_id,
            arguments=arguments
        )

    def get_model_only_evaluation_payload(self,
                                          evaluation_id: str = None,
                                          arguments: dict = None
                                          ) -> ServingPayload:
        """
        Create a serving payload for evaluate the current model with the flow type 'MODEL'
        (Execute the model evaluation only and not the transform evaluation)
        :param evaluation_id: The wanted id for the needed evaluation
        :param arguments: The arguments to fill in the payload
        :return: A new serving payload for the current model
        """
        return self.get_evaluation_payload(
            flow_type=FlowType.MODEL,
            evaluation_id=evaluation_id,
            arguments=arguments
        )

    def get_model_evaluator(self) -> Evaluator:
        """
        Find prescience evaluators for the current model
        :return: the prescience evaluator for the current model
        """
        if self.model_evaluator is None:
            json_dict = self.prescience.serving_model_evaluator(model_id=self.model_id())
            self.model_evaluator = Evaluator(json_dict=json_dict, prescience=self.prescience)

        return self.model_evaluator

    def get_metric(self):
        """
        Get the model metric of a wanted model
        :return: The model metric object
        """
        return self.prescience.model_metric(self.model_id())

    def get_test_evaluation(self):
        """
        Get the test evaluation of a wanted model
        :return: The test evaluation object
        """
        return self.prescience.model_test_evaluation(self.model_id())

    def get_dataframe_for_plot_result(self, input_payload_dict: dict, rolling_steps: int=0):
        input_payload_dict = copy.deepcopy(input_payload_dict)
        if self.problem_type() != ProblemType.TIME_SERIES_FORECAST:
            raise PrescienceClientException(
                Exception('`get_dataframe_for_plot_result` method is only allowed for TIME_SERIES_FORECAST')
            )

        payload = self.get_model_evaluation_payload(arguments=input_payload_dict)
        evaluator = payload.get_evaluator()
        time_feature_name = evaluator.get_time_feature_name()
        result = payload.evaluate()
        series_dict_predict = result.get_result_dict()

        # Rolling evaluation if any
        copy_input_payload = copy.deepcopy(input_payload_dict)
        for _ in range(rolling_steps):
            for key in input_payload_dict.keys():
                # In case the input type is not the same as the output type, need to convert
                convert_function = [x.get_validator_and_filter()[1] for x in evaluator.get_inputs() if x.get_name() == key]
                converted_value = [convert_function[0](x) for x in result.get_result_dict()[key]]
                copy_input_payload[key].extend(converted_value)
            payload = self.get_model_evaluation_payload(arguments=copy_input_payload)
            for key in series_dict_predict:
                result = payload.evaluate()
                series_dict_predict[key].extend(result.get_result_dict()[key])

        # Compute Dataframe from inputs, theorics and predictions
        df_final = get_dataframe_real_predict_theoric(
            series_dict_input=input_payload_dict,
            series_dict_predict=series_dict_predict,
            time_feature_name=time_feature_name,
            label_id=self.label_id(),
            initial_dataframe=self.prescience.source_dataframe(self.source_id())
        )
        return df_final
