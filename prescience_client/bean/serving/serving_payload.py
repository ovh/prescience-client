# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

import uuid

from prescience_client.bean.serving.evaluator import Evaluator, Input
from prescience_client.client.prescience_client import PrescienceClient
from prescience_client.enum.flow_type import FlowType
from prescience_client.utils.table_printable import TablePrinter


class ServingPayload(object):
    """
    Prescience-client object used for requesting model
    """

    @staticmethod
    def new(model_id: str,
            flow_type: FlowType,
            payload_id: str = None,
            arguments: dict = None,
            model_evaluator: Evaluator = None,
            prescience: PrescienceClient = None) -> 'ServingPayload':
        """
        Construct a serving payload from attributes
        :param model_id: The requested model id
        :param flow_type: The flow type of the request
        :param payload_id: The id to give to the payload (optional)
        :param arguments: The arguments of the model to fill on payload (optional)
        :param model_evaluator: The current evaluator for model
        :param prescience: The prescience client
        :return: The serving payload object
        """

        if payload_id is None:
            payload_id = str(uuid.uuid4())

        if arguments is None:
            arguments = {}

        return ServingPayload(
            model_id=model_id,
            flow_type=flow_type,
            json_dict={'id': payload_id, 'arguments': arguments},
            model_evaluator=model_evaluator,
            prescience=prescience
        )


    def __init__(self,
                model_id: str,
                flow_type: FlowType,
                json_dict: dict,
                model_evaluator: Evaluator = None,
                prescience: PrescienceClient = None
    ):
        """
        Constructor of a serving payload
        :param model_id: The requested model id
        :param flow_type: The flow type of the request
        :param json_dict: The json dictionary of the payload
        :param model_evaluator: The current evaluator for model
        :param prescience: The prescience client
        """
        self.model_id = model_id
        self.flow_type = flow_type
        self.json_dict = json_dict
        self.prescience = prescience
        self.model_evaluator = model_evaluator

    def get_payload(self) -> dict:
        """
        Access the request payload dictionary
        :return: the request payload dictionary
        """
        return self.json_dict

    def get_model_id(self) -> str:
        """
        Access the model id
        :return: the model id
        """
        return self.model_id

    def get_payload_id(self) -> str:
        """
        Access the payload id
        :return: the payload id
        """
        return self.json_dict.get('id', None)

    def add_payload_argument(self, key: str, argument) -> 'ServingPayload':
        """
        Add a payload argument inside the current serving payload from a (key -> value)
        :param key: the argument name
        :param argument: the argument value
        :return: The current serving payload
        """
        self.add_payload_arguments({key: argument})
        return self

    def add_payload_arguments(self, args: dict) -> 'ServingPayload':
        """
        Add payload arguments inside the current serving payload from a dictionary
        :param args: Dictionary of payload arguments for requesting the model
        :return: The current serving payload
        """
        self.get_payload_arguments().update(args)
        return self

    def get_payload_arguments(self) -> dict:
        """
        Access payload arguments
        :return: payload arguments
        """
        return self.json_dict.get('arguments', None)

    def get_result_dict(self) -> dict:
        """
        Access the request result dictionary if it exists
        :return: the request result dictionary if it exists, None otherwise
        """
        return self.json_dict.get('result', None)

    def get_result_label(self) -> str:
        """
        Access the label of the request result
        :return: the label of the request result
        """
        label_name = self.model_evaluator.get_label()
        return self.get_result_dict().get(label_name, None)

    def get_result_probabilities(self) -> dict:
        """
        Access the result probabilities if any
        :return: the result probabilities if any, an empty dictionary otherwise
        """
        return {k: v for k, v in  self.get_result_dict().items() if k.startswith('probability')}

    def get_flow_type(self):
        """
        Access the flow type of the serving payload
        :return: the flow type of the serving payload
        """
        return self.flow_type

    def evaluate(self):
        """
        Evaluate the current serving payload by sending it to prescience-serving api
        :return: A new serving payload containing the result of evaluation
        """
        result_dict = self.prescience.serving_model_evaluate(
            model_id=self.model_id,
            flow_type=self.flow_type,
            request_data=self.get_payload()
        )
        return ServingPayload(
            model_id = self.model_id,
            flow_type = self.flow_type,
            json_dict = result_dict,
            model_evaluator=self.model_evaluator,
            prescience = self.prescience
        )

    def validate(self) -> (bool, list):
        """
        Validate all the current filled inputs value
        :return: the tuple2 of (is the payload valid ? / list of all inputs 'KO')
        """
        evaluator_inputs = self.current_inputs_evaluators()
        all_kos = [x for x in evaluator_inputs if x.is_ko()]
        return len(all_kos) == 0, all_kos

    def show_arguments(self) -> 'ServingPayload':
        """
        Display the filled argument with there validations inputs on std out
        :return: The current serving payload
        """
        evaluator_inputs = self.current_inputs_evaluators()
        table = TablePrinter.get_table(Input, evaluator_inputs)
        print(table.get_string(title=f'ARGUMENTS ({self.get_payload_id()})'))
        return self

    def current_inputs_evaluators(self) -> list:
        """
        Find prescience evaluators for the current model and fill it with the current arguments value
        :return: The list of filled inputs
        """
        evaluator_inputs = self.get_evaluator().get_inputs()
        current_arguments = self.get_payload_arguments()
        for single_input in evaluator_inputs:
            if current_arguments.get(single_input.get_name(), None) is not None:
                single_input.set_placeholder(current_arguments[single_input.get_name()])
        return evaluator_inputs

    def get_evaluator(self) -> Evaluator:
        """
        Access the current model evaluator
        :return: the prescience evaluator for the current model
        """
        return self.model_evaluator

    def show_result(self) -> 'ServingPayload':
        """
        Display the result of the serving payload on std out
        :return: The current serving payload
        """
        if len(self.get_result_probabilities()) != 0:
            from prescience_client.bean.serving.serving_payload_batch import ServingPayloadBatch
            batch = ServingPayloadBatch(
                model_id=self.get_model_id(),
                flow_type=self.flow_type,
                batch_serving_payload=[self],
                model_evaluator=self.model_evaluator,
                prescience=self.prescience
            )
            batch.show_result()
        else:
            TablePrinter.print_dict(
                title=f'PREDICTIONS RESULTS FROM \'{self.get_model_id()}\'',
                json_dict=self.get_result_dict()
            )

        return self

    def show(self) -> 'ServingPayload':
        """
        Display the result of the serving payload on std out if it exists or display the filled arguments otherwise
        :return: The current serving payload
        """
        if self.get_result_dict() is None or len(self.get_result_dict()) == 0:
            return self.show_arguments()
        else:
            return self.show_result()
