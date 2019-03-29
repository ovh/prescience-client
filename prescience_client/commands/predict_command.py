from prescience_client.commands.command import Command
from prescience_client.enum.output_format import OutputFormat


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
        self.cmd_parser.add_argument('--from-json', dest='from_json', type=str, default=None,
                                        help='Arguments to send as input of prescience model, it can be directly in json format, a filepath to a wanted payload. If unset it will take the default cached file for payload.')
        self.cmd_parser.add_argument('--validate', default=False, action='store_true',
                                        help='Validate the prediction request and don\'t send it')
        self.cmd_parser.add_argument('-o', '--output', dest='output', type=OutputFormat, choices=list(OutputFormat),
                                     help=f"Type of output to get on std out. (default: {OutputFormat.TABLE})")
        self.cmd_parser.add_argument('--from-data',
                                     dest='from_data',
                                     type=int,
                                     help=f"Generate a prediction payload from an index in the initial data in case of a classification/regression problem or from the time value in case of a timeseries forecast problem. It will be saved as the default cached file for payload before sending to prescience-serving")

    def exec(self, args: dict):
        model_id = args.get('model-id')
        validate = args.get('validate')
        payload_json = args.get('from_json')
        output = args.get('output')
        from_data = args.get('from_data')

        payload_dict = self.prescience_client.generate_payload_dict_for_model(
            model_id=model_id,
            payload_json=payload_json,
            from_data=from_data
        )
        from prescience_client.bean.model import Model
        model = Model.new(model_id=model_id, prescience=self.prescience_client)
        payload = model.get_model_evaluation_payload(arguments=payload_dict)

        if validate:
            payload.show(output)
        else:
            result = payload.evaluate()
            result.show(output)
