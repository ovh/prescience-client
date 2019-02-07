# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

from prescience_client.bean.serving.evaluator import Evaluator
from prescience_client.bean.serving.serving_payload import ServingPayload
from prescience_client.client.prescience_client import PrescienceClient
from prescience_client.enum.flow_type import FlowType
from prescience_client.enum.valid import Valid
from termgraph import termgraph
from termgraph.termgraph import AVAILABLE_COLORS


class ServingPayloadBatch(object):
    """
    Prescience-client object used for requesting evaluation in batch
    """

    def __init__(self,
                 model_id: str,
                 flow_type: FlowType,
                 batch_serving_payload: list = None,
                 model_evaluator: Evaluator = None,
                 prescience: PrescienceClient = None
                 ):
        """
        Constructor of a batch serving payload
        :param model_id: The requested model id
        :param flow_type: The flow type of the request
        :param batch_serving_payload: The json list of dictionary of the batch payload
        :param model_evaluator: The current evaluator for model
        :param prescience: The prescience client
        """
        if batch_serving_payload is None:
            batch_serving_payload = []
        self.batch_serving_payload = batch_serving_payload

        self.model_id = model_id
        self.flow_type = flow_type
        self.prescience = prescience
        self.model_evaluator = model_evaluator

    def get_batch_payload(self) -> list:
        """
        Access the request payload dictionary
        :return: the request payload dictionary
        """
        return [x.get_payload() for x in self.batch_serving_payload]

    def get_model_id(self) -> str:
        """
        Access the model id
        :return: the model id
        """
        return self.model_id

    def add_payload_input(self, single_input: ServingPayload) -> 'ServingPayloadBatch':
        """
        Add a payload argument inside the current serving payload from a (key -> value)
        :param single_input: the ServingPayload to add inside the batch
        :return: The current serving batch payload
        """
        self.batch_serving_payload.append(single_input)
        return self

    def evaluate(self):
        """
        Evaluate the current serving payload by sending it to prescience-serving api
        :return: A new serving payload containing the result of evaluation
        """
        result_dict = self.prescience.serving_model_evaluate(
            model_id=self.model_id,
            flow_type=self.flow_type,
            request_data=self.get_batch_payload()
        )

        result_payloads = [ServingPayload(
            model_id = self.model_id,
            flow_type = self.flow_type,
            json_dict = single_payload,
            model_evaluator=self.model_evaluator,
            prescience = self.prescience
        ) for single_payload in result_dict]

        return ServingPayloadBatch(
            model_id = self.model_id,
            flow_type = self.flow_type,
            batch_serving_payload = result_payloads,
            model_evaluator=self.model_evaluator,
            prescience = self.prescience
        )

    def validate(self) -> (bool, list):
        """
        Validate all the current filled inputs value
        :return: the tuple2 of (is the payload valid ? / list of all inputs 'KO')
        """
        all_validate = [x.validate() for x in self.batch_serving_payload]
        all_ko = [x[0] for x in all_validate if x[0] == Valid.KO]
        all_ko_message = [x[1] for x in all_validate if x[0] == Valid.KO]
        return len(all_ko) == 0, all_ko_message

    def show_inputs(self) -> 'ServingPayloadBatch':
        """
        Display the filled inputs with their validations inputs on std out
        :return: The current batch serving payload
        """
        [x.show_arguments() for x in self.batch_serving_payload]
        return self

    def show_result(self) -> 'ServingPayloadBatch':
        """
        Display the result of the batch serving payload on std out
        :return: The current batch serving payload
        """
        probabilities = [x.get_result_probabilities() for x in self.batch_serving_payload]

        colors = [v for _, v in AVAILABLE_COLORS.items()][:len(probabilities[0])]
        labels = [f'{single_eval.get_payload_id()}: \'{single_eval.get_result_label()}\'' for single_eval in self.batch_serving_payload]
        categories = [k for k, _ in probabilities[0].items()]
        data = [[v * 100 for _, v in prob.items()] for prob in probabilities]

        args = {
            'width': 10,
            'format': '{:<5.2f}',
            'suffix': ' %',
            'no_labels': False,
            'color': None,
            'vertical': False,
            'stacked': False,
            'different_scale': False,
            'calendar': False,
            'start_dt': None,
            'custom_tick': '',
            'delim': '',
            'verbose': False,
            'version': False
        }
        print(f'PREDICTIONS RESULTS FROM \'{self.model_id}\'')
        print('\n')
        termgraph.chart(colors=colors, data=data, args=args, labels=labels)
        termgraph.print_categories(categories=categories, colors=colors)

        return self

    def show(self) -> 'ServingPayloadBatch':
        """
        Display the result of the batch serving payload on std out if it exists or display the filled inputs validation
        :return: The current batch serving payload
        """
        first_payload = self.batch_serving_payload[0]
        if first_payload.get_result_dict() is None or len(first_payload.get_result_dict()) == 0:
            return self.show_inputs()
        else:
            return self.show_result()
