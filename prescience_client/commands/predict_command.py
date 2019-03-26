import json

from prescience_client.commands.command import Command


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
        self.cmd_parser.add_argument('--json', type=str, default='{}',
                                        help='All arguments to send as input of prescience model (in json format)')
        self.cmd_parser.add_argument('--validate', default=False, action='store_true',
                                        help='Validate the prediction request and don\'t send it')

    def exec(self, args: dict):
        model_id = args['model-id']
        validate = args['validate']
        payload_json = args['json']
        payload_dict = json.loads(payload_json)
        from prescience_client.bean.model import Model
        model = Model.new(model_id=model_id, prescience=self.prescience_client)
        payload = model.get_model_evaluation_payload(arguments=payload_dict)
        if validate:
            payload.show()
        else:
            result = payload.evaluate()
            result.show()