import json

from PyInquirer import prompt
import os
import io

from websocket._abnf import numpy

from prescience_client.bean.model import Model
from prescience_client.bean.serving.evaluator import Evaluator
from prescience_client.commands import prompt_for_model_id_if_needed, get_default_json_ouput
from prescience_client.commands.command import Command
from prescience_client.enum.problem_type import ProblemType
from prescience_client.utils.monad import Option


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
                                     type=int,
                                     help=f"Generate a prediction payload from an index in the initial data in case of a classification/regression problem or from the time value in case of a timeseries forecast problem")

    def exec(self, args: dict):
        default_output = get_default_json_ouput()
        full_output = Option(args.get('output'))\
            .get_or_else(default_output)

        model_id = prompt_for_model_id_if_needed(args, self.prescience_client)
        model = self.prescience_client.model(model_id)
        payload = model.get_model_evaluation_payload(arguments={})
        evaluator = payload.get_evaluator()
        problem_type = evaluator.get_problem_type()
        from_data = args.get('from_data')

        if from_data is None:
            # Fill the payload with full interactiv mode
            if problem_type == ProblemType.TIME_SERIES_FORECAST:
                final_dict = self.interactiv_ts_forecast_payload(evaluator)
            else:
                final_dict = self.interactiv_default_payload(evaluator)
        else:
            # Fill the payload from the data
            source_id = model.source_id()
            df = self.prescience_client.source_dataframe(source_id=source_id)
            if problem_type == ProblemType.TIME_SERIES_FORECAST:
                min_bound = from_data - (evaluator.get_max_steps() * evaluator.get_span())
                max_bound = from_data
                time_feature = evaluator.get_time_feature_name()
                filtered = df.loc[(df[time_feature] > min_bound) & (df[time_feature] <= max_bound)]
                final_dict = {k: list(v.values()) for k, v in filtered.to_dict().items()}
            else:
                final_dict = df.ix[from_data].to_dict()
                label_name = evaluator.get_label()
                final_dict.pop(label_name)

        # Print the JSON on std out
        print('Generating JSON selfpayload : ')
        # In some case numpy types are not serializable
        def default(o):
            if isinstance(o, numpy.int64): return int(o)
            if isinstance(o, numpy.int32): return int(o)
            raise TypeError
        print(json.dumps(final_dict, indent=4, default=default))
        # Save the json in the given file
        print(f'Saving json into `{full_output}`')
        with io.open(full_output, 'w', encoding='utf8') as outfile:
            json.dump(final_dict, outfile, indent=4, default=default)

    def interactiv_default_payload(self, evaluator: Evaluator) -> dict:
        final_dict = {}
        questions = []
        for einput in evaluator.get_inputs():
            validator, filter_arg = einput.get_validator_and_filter()
            questions.append({
                'type': 'input',
                'name': einput.get_name(),
                'message': f'`{einput.get_name()}` parameter ({einput.get_type()}) ?',
                'validate': validator,
                'filter': filter_arg
            })
        answers = prompt(questions)
        final_dict.update(answers)
        return final_dict

    def interactiv_ts_forecast_payload(self, evaluator: Evaluator) -> dict:
        final_dict = {}
        for einput in evaluator.get_inputs():
            questions = []
            validator, filter_arg = einput.get_validator_and_filter()
            for step_number in range(0, evaluator.get_max_steps()):
                t = evaluator.get_max_steps() - step_number - 1
                key = f'{einput.get_name()}_t'
                if t != 0:
                    key = f'{key}-{t}'
                questions.append({
                    'type': 'input',
                    'name': key,
                    'message': f'`{key}` parameter ({einput.get_type()}) ?',
                    'validate': validator,
                    'filter': filter_arg
                })
            answers = prompt(questions)
            final_dict[einput.get_name()] = list(answers.values())
        return final_dict




