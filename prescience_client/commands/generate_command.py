from prescience_client.commands import prompt_for_model_id_if_needed
from prescience_client.commands.command import Command


class GenerateCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='generate',
            help_message='Generate JSON payload useful for other part of the prescience-client',
            prescience_client=prescience_client,
            sub_commands=[
                GeneratePredictCommand(prescience_client)
            ]
        )

class GeneratePredictCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='predict',
            help_message='Generate JSON payload for making prediction with `prescience predict`',
            prescience_client=prescience_client,
            sub_commands=[]
        )

    def init_from_subparser(self, subparsers, selector):
        super().init_from_subparser(subparsers, selector)
        self.cmd_parser.add_argument('id', type=str, help='Identifier if the model object to make prediction on')
        self.cmd_parser.add_argument('-o', '--output', dest='output', type=str, help=f"Filename in with to save the json payload")
        self.cmd_parser.add_argument('--from-data',
                                     dest='from_data',
                                     type=str,
                                     help=f"Generate a prediction payload from an index in the initial data in case of a classification/regression problem or from the time value in case of a timeseries forecast problem")

    def exec(self, args: dict):
        # Save the json in the given file
        from_data = args.get('from_data')
        output = args.get('output')
        model_id = prompt_for_model_id_if_needed(args, self.prescience_client)
        self.prescience_client.generate_serving_payload(from_data, model_id, output)
