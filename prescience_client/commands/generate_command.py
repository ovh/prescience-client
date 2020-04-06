import pandas
import os

from prescience_client.commands import prompt_for_model_id_if_needed
from prescience_client.commands.command import Command
from prescience_client.enum.output_format import OutputFormat
from prescience_client.utils import compute_prediction_df, compute_cube_from_prediction
from prescience_client.utils.table_printable import TablePrinter


class GenerateCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='generate',
            help_message='Generate JSON payload useful for other part of the prescience-client',
            prescience_client=prescience_client,
            sub_commands=[
                GeneratePredictCommand(prescience_client),
                GenerateCubeMetric(prescience_client)
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


class GenerateCubeMetric(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='cube-metric',
            help_message='Generate parquet dataframe representing the cube data needed to compute metrics',
            prescience_client=prescience_client,
            sub_commands=[]
        )

    def init_from_subparser(self, subparsers, selector):
        super().init_from_subparser(subparsers, selector)
        self.cmd_parser.add_argument('id', type=str, help='Identifier of the model object to generate the cube-metric on')
        self.cmd_parser.add_argument('-o', '--output', dest='output', type=str, help='Filename where to save the parquet dataframe')

    def exec(self, args: dict):
        # Save the json in the given file
        model_id = args.get('id')
        output = args.get('output')

        model = self.prescience_client.model(model_id=model_id)
        cube = model.generate_cube_metrics()

        if output is None:
            output = self.prescience_client.cache_cube_model_metrics_get_full_path(model_id)

        if os.path.exists(output):
            print(f'Path {output} already exist, removing it ...')
            os.remove(output)

        print(f'Saving cube model metrics on {output}')
        cube.to_parquet(output)
