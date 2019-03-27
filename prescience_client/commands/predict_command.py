import json
import io
import os

import matplotlib

from prescience_client.commands import get_default_json_ouput
from prescience_client.commands.command import Command
from prescience_client.enum.output_format import OutputFormat
from prescience_client.utils import get_dataframe_real_predict_theoric


class PredictCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='predict',
            help_message='Make prediction(s) from a presience model',
            prescience_client=prescience_client,
            sub_commands=[]
        )

    def init_from_subparser(self, subparsers, selector):
        super().init_from_subparser(subparsers, selector)
        self.cmd_parser.add_argument('model-id', type=str,
                                        help='Identifier if the model object to make prediction on')
        self.cmd_parser.add_argument('--json', type=str, default=None,
                                        help='All arguments to send as input of prescience model (in json format)')
        self.cmd_parser.add_argument('--validate', default=False, action='store_true',
                                        help='Validate the prediction request and don\'t send it')
        self.cmd_parser.add_argument('-o', '--output', dest='output', type=OutputFormat, choices=list(OutputFormat),
                                     help=f"Type of output to get on std out. (default: {OutputFormat.TABLE})")

    def exec(self, args: dict):
        model_id = args['model-id']
        validate = args['validate']
        payload_json = args.get('json')
        output = args.get('output')
        if payload_json is None:
            payload_json = get_default_json_ouput()
        else:
            payload_json = payload_json.strip()

        if len(payload_json) > 0 and payload_json[0] == '{' and payload_json[-1] == '}':
            # In this case the user gives us a json string
            payload_dict = json.loads(payload_json)
        elif os.path.isfile(payload_json):
            # In this case it is probably a path
            with io.open(payload_json, 'r') as stream:
                payload_dict = json.load(stream)
        else:
            payload_dict = json.loads('{}')

        from prescience_client.bean.model import Model
        model = Model.new(model_id=model_id, prescience=self.prescience_client)
        payload = model.get_model_evaluation_payload(arguments=payload_dict)

        if validate:
            payload.show(output)
        else:
            result = payload.evaluate()
            result.show(output)

            ###############
            evaluator = payload.get_evaluator()
            df_final = get_dataframe_real_predict_theoric(
                series_dict_real=payload_dict,
                series_dict_predict=result.get_result_dict(),
                series_dict_theoric={},
                time_feature_name=evaluator.get_time_feature_name(),
                labels_names=[evaluator.get_label()]
            )
            df_final.plot()
            matplotlib.pyplot.show(block=True)
