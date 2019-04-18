import json
from typing import List

import copy

from prescience_client.bean.config import Config
from prescience_client.bean.entity.local_file_input import LocalFileInput
from prescience_client.commands import get_args_or_prompt_input, get_args_or_prompt_confirm, get_args_or_prompt_list, \
    get_args_or_prompt_checkbox
from prescience_client.commands.command import Command
from prescience_client.config.constants import DEFAULT_PROBLEM_TYPE, DEFAULT_INPUT_TYPE
from prescience_client.enum.input_type import InputType
from prescience_client.enum.problem_type import ProblemType
from prescience_client.enum.scoring_metric import ScoringMetric
from prescience_client.utils.monad import List as UtilList
from prescience_client.utils.validator import IntegerValidator, FloatValidator


class StartCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='start',
            help_message='Start a task in prescience',
            prescience_client=prescience_client,
            sub_commands=[
                StartParseCommand(prescience_client),
                StartPreprocessCommand(prescience_client),
                StartTrainCommand(prescience_client),
                StartOptimizeCommand(prescience_client),
                StartEvaluateCommand(prescience_client),
                StartReTrainCommand(prescience_client),
                StartRefreshCommand(prescience_client),
                StartMaskCommand(prescience_client),
                StartAutoML(prescience_client)
            ]
        )


class StartParseCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='parse',
            help_message='Launch a parse task on prescience',
            prescience_client=prescience_client,
            sub_commands=[]
        )

    def init_from_subparser(self, subparsers, selector):
        super().init_from_subparser(subparsers, selector)
        self.cmd_parser.add_argument('--no-headers', default=True, dest='headers', action='store_false', help='Indicates that there is no header line on the csv file')
        self.cmd_parser.add_argument('--watch', default=False, action='store_true', help='Wait until the task ends and watch the progression')
        self.cmd_parser.add_argument('--input-type', type=InputType, choices=list(InputType), help=f"The input type of your local file (default: {DEFAULT_INPUT_TYPE})")
        self.cmd_parser.add_argument('--source-id', nargs='?', type=str, help='Identifier of your future source object.')
        self.cmd_parser.add_argument('input-filepath', nargs='?', type=str, help='Local input file to send and parse on prescience. If unset it will trigger the interactive mode.')

    def exec(self, args: dict):
        filepath = args.get('input-filepath')
        source_id = args.get('source_id')
        input_type = args.get('input_type')
        has_headers = args.get('headers')
        watch = args.get('watch')

        interactive_mode = filepath is None
        if interactive_mode:
            filepath = get_args_or_prompt_input(
                arg_name='input_filepath',
                args=args,
                message='Please indicate the path on your local file you want to parse',
                force_interactive=interactive_mode
            )
            input_type = get_args_or_prompt_list(
                arg_name='input_type',
                args=args,
                message='What is the type of your input file ?',
                choices_function=lambda: list(map(str, InputType)),
                force_interactive=interactive_mode
            )
            has_headers = get_args_or_prompt_confirm(
                arg_name='headers',
                args=args,
                message='Does your csv file has a header row ? (doesn\'t matter in case of a parquet file)',
                force_interactive=interactive_mode
            )
            source_id = get_args_or_prompt_input(
                arg_name='source_id',
                args=args,
                message='What will be the name of your source ? (should be unique in your project)',
                force_interactive=interactive_mode
            )
            watch = get_args_or_prompt_confirm(
                arg_name='watch',
                args=args,
                message='Do you want to keep watching for the task until it ends ?',
                force_interactive=interactive_mode
            )

        input_local_file = LocalFileInput(
            input_type=input_type,
            headers=has_headers,
            filepath=filepath,
            prescience=self.prescience_client
        )
        parse_task = input_local_file.parse(source_id=source_id)
        if watch:
            parse_task.watch()

class StartPreprocessCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='preprocess',
            help_message='Launch a preprocess task on prescience',
            prescience_client=prescience_client,
            sub_commands=[]
        )

    def init_from_subparser(self, subparsers, selector):
        super().init_from_subparser(subparsers, selector)
        self.cmd_parser.add_argument('source-id', nargs='?', type=str,
                                       help='Identifier of the source object to use for preprocessing. If unset it will trigger the interactive mode.')
        self.cmd_parser.add_argument('dataset-id', nargs='?', type=str,
                                       help='Identifier of your future dataset object. If unset it will trigger the interactive mode.')
        self.cmd_parser.add_argument('label', nargs='?', type=str,
                                       help='Identifier of the column to predict. If unset it will trigger the interactive mode.')
        self.cmd_parser.add_argument('--columns', type=List[str],
                                       help='Subset of columns to include in the dataset. (default: all)')
        self.cmd_parser.add_argument('--problem-type', type=ProblemType, choices=list(ProblemType),
                                       help=f"Type of problem for the dataset (default: {DEFAULT_PROBLEM_TYPE})",
                                       default=DEFAULT_PROBLEM_TYPE)
        self.cmd_parser.add_argument('--time-column', type=str,
                                       help='Identifier of the time column for time series. Only for forecasts problems.')
        self.cmd_parser.add_argument('--watch', default=False, action='store_true',
                                       help='Wait until the task ends and watch the progression')
        self.cmd_parser.add_argument('--nb-fold', type=int, help='How many folds the dataset will be splited')

    def exec(self, args: dict):
        interactive_mode = args.get('source-id') is None
        source_id = get_args_or_prompt_list(
            arg_name='id',
            args=args,
            message='Which source do you want to preprocess ?',
            choices_function=lambda: [x.source_id for x in self.prescience_client.sources(page=1).content],
            force_interactive=interactive_mode
        )
        selected_columns = get_args_or_prompt_checkbox(
            arg_name='columns',
            args=args,
            message='Select the columns you want to keep for your preprocessing',
            choices_function=lambda: [x.name() for x in self.prescience_client.source(source_id).schema().fields()],
            selected_function=lambda: [x.name() for x in self.prescience_client.source(source_id).schema().fields()],
            force_interactive=interactive_mode
        )
        problem_type = get_args_or_prompt_list(
            arg_name='problem_type',
            args=args,
            message='What kind of problem do you want to solve ?',
            choices_function=lambda: list(map(str, ProblemType)),
            force_interactive=interactive_mode
        )
        label = get_args_or_prompt_list(
            arg_name='label',
            args=args,
            message='What will be your label ? (the column you want to predict)',
            choices_function=lambda: copy.deepcopy(selected_columns),
            force_interactive=interactive_mode
        )
        time_column = None
        if ProblemType(problem_type) == ProblemType.TIME_SERIES_FORECAST:
            available_time_columns = copy.deepcopy(selected_columns)
            available_time_columns.remove(label)
            time_column = get_args_or_prompt_list(
                arg_name='time_column',
                args=args,
                message='What will be the column used for time ?',
                choices_function=lambda: copy.deepcopy(available_time_columns),
                force_interactive=interactive_mode
            )
        nb_fold = get_args_or_prompt_input(
            arg_name='nb_fold',
            args=args,
            message='How many folds do you want ?',
            force_interactive=interactive_mode
        )
        dataset_id = get_args_or_prompt_input(
            arg_name='dataset-id',
            args=args,
            message='What will be the name of your dataset ? (should be unique in your project)',
            force_interactive=interactive_mode
        )
        watch = get_args_or_prompt_confirm(
            arg_name='watch',
            args=args,
            message='Do you want to keep watching for the task until it ends ?',
            force_interactive=interactive_mode
        )
        task = self.prescience_client.preprocess(
            source_id=source_id,
            dataset_id=dataset_id,
            label_id=label,
            problem_type=problem_type,
            selected_column=selected_columns,
            time_column=time_column,
            nb_fold=int(nb_fold)
        )
        if watch:
            task.watch()

class StartOptimizeCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='optimize',
            help_message='Launch an optimize task on prescience',
            prescience_client=prescience_client,
            sub_commands=[]
        )

    def init_from_subparser(self, subparsers, selector):
        super().init_from_subparser(subparsers, selector)
        self.cmd_parser.add_argument('dataset-id', nargs='?', type=str,
                                     help='Dataset identifier to optimize on. If unset it will trigger the interactive mode.')
        self.cmd_parser.add_argument('scoring-metric', nargs='?', type=ScoringMetric, choices=list(ScoringMetric),
                                     help=f'The scoring metric to optimize on. If unset it will trigger the interactive mode.')
        self.cmd_parser.add_argument('--budget', type=int,
                                     help='Budget to allow on optimization (default: it will use the one configure on prescience server side)')
        self.cmd_parser.add_argument('--watch', default=False, action='store_true',
                                     help='Wait until the task ends and watch the progression')
        self.cmd_parser.add_argument('--forecast-horizon-steps', type=int,
                                     help='Number of steps forward to take into account as a forecast horizon for the optimization (Only in case of time series forecast)')
        self.cmd_parser.add_argument('--forecast-discount', type=float,
                                     help='Discount to apply on each time step before the horizon (Only in case of time series forecast)')


    def exec(self, args: dict):
        interactive_mode = args.get('dataset-id') is None
        dataset_id = get_args_or_prompt_list(
            arg_name='dataset-id',
            args=args,
            message='Which dataset do you want to preprocess ?',
            choices_function=lambda: [x.dataset_id() for x in self.prescience_client.datasets(page=1).content],
            force_interactive=interactive_mode
        )
        budget = get_args_or_prompt_input(
            arg_name='budget',
            args=args,
            message='Which budget do you want to allow on optimization ?',
            force_interactive=interactive_mode
        )
        scoring_metric = get_args_or_prompt_list(
            arg_name='scoring-metric',
            args=args,
            message='On which scoring metric do you want to optimize on ?',
            choices_function=lambda: list(map(str, ScoringMetric)),
            force_interactive=interactive_mode
        )
        if interactive_mode and self.prescience_client.dataset(dataset_id).problem_type() == ProblemType.TIME_SERIES_FORECAST:
            forecast_horizon_steps = get_args_or_prompt_input(
                arg_name='forecast_horizon_steps',
                args=args,
                message='How many steps do you expect as a forecast horizon ?',
                force_interactive=interactive_mode
            )
            forecast_discount = get_args_or_prompt_input(
                arg_name='forecast_discount',
                args=args,
                message='Which discount value fo you want to apply on your forecasted values ?',
                force_interactive=interactive_mode
            )
        else:
            forecast_horizon_steps = args.get('forecast_horizon_steps')
            forecast_discount = args.get('forecast_discount')

        watch = get_args_or_prompt_confirm(
            arg_name='watch',
            args=args,
            message='Do you want to keep watching for the task until it ends ?',
            force_interactive=interactive_mode
        )
        task = self.prescience_client.optimize(
            dataset_id=dataset_id,
            scoring_metric=scoring_metric,
            budget=budget,
            optimization_method=None,
            custom_parameter=None,
            forecasting_horizon_steps=forecast_horizon_steps,
            forecast_discount=forecast_discount
        )
        if watch:
            task.watch()

class StartTrainCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='train',
            help_message='Launch a train task on prescience',
            prescience_client=prescience_client,
            sub_commands=[]
        )

    def init_from_subparser(self, subparsers, selector):
        super().init_from_subparser(subparsers, selector)
        self.cmd_parser.add_argument('uuid', type=str, help='Chosen evaluation result uuid to train on')
        self.cmd_parser.add_argument('model-id', type=str, help='Identifier of your future model object')
        self.cmd_parser.add_argument('--watch', default=False, action='store_true', help='Wait until the task ends and watch the progression')


    def exec(self, args: dict):
        evaluation_result_uuid = args['uuid']
        model_id = args['model-id']
        watch = args['watch']
        task = self.prescience_client.train(evaluation_uuid=evaluation_result_uuid, model_id=model_id)
        if watch:
            task.watch()

class StartReTrainCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='retrain',
            help_message='Launch a retrain task on prescience',
            prescience_client=prescience_client,
            sub_commands=[]
        )

    def init_from_subparser(self, subparsers, selector):
        super().init_from_subparser(subparsers, selector)
        self.cmd_parser.add_argument('--watch', action='store_true',
                                    help='Wait until the task ends and watch the progression')
        self.cmd_parser.add_argument('model-id', type=str, help='Model to retrain')
        self.cmd_parser.add_argument('--input-filepath', type=str,
                                    help='Local input file to send in order to retrain the model on prescience')

    def exec(self, args: dict):
        file = args['input_filepath']
        model_id = args['model-id']
        watch = args['watch']
        task = self.prescience_client.retrain(model_id=model_id, filepath=file)
        if watch:
            task.watch()


class StartRefreshCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='refresh',
            help_message='Launch a refresh dataset task on prescience',
            prescience_client=prescience_client,
            sub_commands=[]
        )

    def init_from_subparser(self, subparsers, selector):
        super().init_from_subparser(subparsers, selector)
        self.cmd_parser.add_argument('--watch', action='store_true',
                                    help='Wait until the task ends and watch the progression')
        self.cmd_parser.add_argument('dataset-id', type=str, help='Dataset to refresh')
        self.cmd_parser.add_argument('--input-filepath', type=str,
                                    help='Local input file/directory to send in order to refresh the dataset on prescience')

    def exec(self, args: dict):
        file = args['input_filepath']
        dataset_id = args['dataset-id']
        watch = args['watch']
        task = self.prescience_client.refresh_dataset(dataset_id=dataset_id, filepath=file)
        if watch:
            task.watch()

class StartEvaluateCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='evaluate',
            help_message='Launch an evaluation of a custom algorithm configuration',
            prescience_client=prescience_client,
            sub_commands=[]
        )

    def init_from_subparser(self, subparsers, selector):
        super().init_from_subparser(subparsers, selector)
        self.cmd_parser.add_argument('dataset-id', nargs='?', type=str,
                                       help='Dataset to launch an evaluation on. If unset it will trigger the interactive mode.')
        self.cmd_parser.add_argument('custom-config', nargs='?', type=str,
                                       help='Configuration to use on the evaluation (in json format). If unset it will trigger the interactive mode.')
        self.cmd_parser.add_argument('--watch', action='store_true',
                                       help='Wait until the task ends and watch the progression')

    def exec(self, args: dict):
        interactive_mode = args.get('dataset-id') is None
        dataset_id = get_args_or_prompt_list(
            arg_name='dataset-id',
            args=args,
            message='Which dataset do you want to launch an evaluation on ?',
            choices_function=lambda: [x.dataset_id() for x in self.prescience_client.datasets(page=1).content],
            force_interactive=interactive_mode
        )
        interactive_mode = interactive_mode or args.get('custom-config') is None
        if not interactive_mode:
            prescience_config = Config(json_dict=json.loads(args.get('custom-config')))
        else:
            # Use interactive mode to create the configuration
            dataset = self.prescience_client.dataset(dataset_id=dataset_id)
            all_config_list = dataset.get_associated_algorithm()
            choice_function = lambda: UtilList(all_config_list).flat_map(lambda x: x.get_algorithm_list_names()).value
            algo_id = get_args_or_prompt_list(
                arg_name='algo_id',
                args=args,
                message='Which algorithm ID do you want to get ?',
                choices_function=choice_function
            )
            algorithm = UtilList(all_config_list) \
                .map(lambda x: x.get_algorithm(algo_id)) \
                .find(lambda x: x is not None) \
                .get_or_else(None)

            prescience_config = algorithm.interactive_kwargs_instanciation()
        watch = get_args_or_prompt_confirm(
            arg_name='watch',
            args=args,
            message='Do you want to keep watching for the task until it ends ?',
            force_interactive=interactive_mode
        )
        print(json.dumps(prescience_config.to_dict(), indent=4))
        task = self.prescience_client.custom_config(dataset_id=dataset_id, config=prescience_config)
        if watch:
            task.watch()

class StartMaskCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='mask',
            help_message='Create a mask from an existing dataset',
            prescience_client=prescience_client,
            sub_commands=[]
        )

    def init_from_subparser(self, subparsers, selector):
        super().init_from_subparser(subparsers, selector)
        self.cmd_parser.add_argument('dataset-id', type=str, nargs='?', help='Initial existing dataset')
        self.cmd_parser.add_argument('mask-id', type=str, nargs='?', help='Wanted name for the mask')
        self.cmd_parser.add_argument('columns', type=str, nargs='*', help='List of all initial columns to keep in the mask')

    def exec(self, args: dict):

        interactive_mode = args.get('dataset-id') is None
        dataset_id = get_args_or_prompt_list(
            arg_name='dataset-id',
            args=args,
            message='Which dataset do you want to mask ?',
            choices_function=lambda: [x.dataset_id() for x in self.prescience_client.datasets(page=1).content],
            force_interactive=interactive_mode
        )
        dataset = self.prescience_client.dataset(dataset_id)
        field_selection_function = lambda: [x.name() for x in dataset.schema().fields()]

        interactive_mode = interactive_mode or  args.get('mask-id') is None
        mask_id = get_args_or_prompt_input(
            arg_name='mask-id',
            args=args,
            message='What will be the name of you mask ?',
            force_interactive=interactive_mode
        )

        interactive_mode = interactive_mode or len(args.get('columns')) == 0
        columns = get_args_or_prompt_checkbox(
            arg_name='columns',
            args=args,
            message='Select the column in your initial dataset that you want to keep',
            choices_function=field_selection_function,
            selected_function=field_selection_function,
            force_interactive=interactive_mode
        )
        self.prescience_client.create_mask(
            dataset_id=dataset_id,
            mask_id=mask_id,
            selected_column=columns
        )

class StartAutoML(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='auto-ml',
            help_message='Start an Auto-ML task, which will chain all needed tasks until model deployment',
            prescience_client=prescience_client,
            sub_commands=[]
        )

    def init_from_subparser(self, subparsers, selector):
        super().init_from_subparser(subparsers, selector)
        self.cmd_parser.add_argument('source-id', type=str, nargs='?', help='The source from which you want to start a AutoML task')

        self.cmd_parser.add_argument('--dataset-id', type=str, help='Name you want for the created dataset')
        self.cmd_parser.add_argument('--model-id', type=str, help='Name you want for the created model')


        self.cmd_parser.add_argument('--problem-type', type=ProblemType, choices=list(ProblemType),
                                       help=f"Type of problem for the dataset (default: {DEFAULT_PROBLEM_TYPE})",
                                       default=DEFAULT_PROBLEM_TYPE)
        self.cmd_parser.add_argument('--time-column', type=str,
                                       help='Identifier of the time column for time series. Only for forecasts problems.')
        self.cmd_parser.add_argument('--nb-fold', type=int, help='How many folds the dataset will be splited')
        self.cmd_parser.add_argument('scoring-metric', nargs='?', type=ScoringMetric, choices=list(ScoringMetric),
                                     help=f'The scoring metric to optimize on. If unset it will trigger the interactive mode.')
        self.cmd_parser.add_argument('--budget', type=int,
                                     help='Budget to allow on optimization (default: it will use the one configure on prescience server side)')
        self.cmd_parser.add_argument('--watch', default=False, action='store_true',
                                     help='Wait until the task ends and watch the progression')
        self.cmd_parser.add_argument('--forecast-horizon-steps', type=int,
                                     help='Number of steps forward to take into account as a forecast horizon for the optimization (Only in case of time series forecast)')
        self.cmd_parser.add_argument('--forecast-discount', type=float,
                                     help='Discount to apply on each time step before the horizon (Only in case of time series forecast)')

    def exec(self, args: dict):

        interactive_mode = args.get('source-id') is None
        source_id = get_args_or_prompt_list(
            arg_name='id',
            args=args,
            message='Which source do you want to preprocess ?',
            choices_function=lambda: [x.source_id for x in self.prescience_client.sources(page=1).content],
            force_interactive=interactive_mode
        )
        dataset_id = get_args_or_prompt_input(
            arg_name='dataset_id',
            args=args,
            message='What will be the name of the generated dataset',
            force_interactive=interactive_mode
        )
        model_id = get_args_or_prompt_input(
            arg_name='model_id',
            args=args,
            message='What will be the name of the generated model',
            force_interactive=interactive_mode
        )
        selected_column = get_args_or_prompt_checkbox(
            arg_name='columns',
            args=args,
            message='Select the columns you want to keep for your preprocessing',
            choices_function=lambda: [x.name() for x in self.prescience_client.source(source_id).schema().fields()],
            selected_function=lambda: [x.name() for x in self.prescience_client.source(source_id).schema().fields()],
            force_interactive=interactive_mode
        )
        problem_type = get_args_or_prompt_list(
            arg_name='problem_type',
            args=args,
            message='What kind of problem do you want to solve ?',
            choices_function=lambda: list(map(str, ProblemType)),
            force_interactive=interactive_mode
        )
        label_id = get_args_or_prompt_list(
            arg_name='label',
            args=args,
            message='What will be your label ? (the column you want to predict)',
            choices_function=lambda: copy.deepcopy(selected_column),
            force_interactive=interactive_mode
        )
        time_column = args.get('time_column')
        forecasting_horizon_steps = args.get('forecast_horizon_steps')
        forecast_discount = args.get('forecast_discount')
        if ProblemType(problem_type) == ProblemType.TIME_SERIES_FORECAST:
            available_time_columns = copy.deepcopy(selected_column)
            available_time_columns.remove(label_id)
            time_column = get_args_or_prompt_list(
                arg_name='time_column',
                args=args,
                message='What will be the column used for time ?',
                choices_function=lambda: copy.deepcopy(available_time_columns),
                force_interactive=interactive_mode
            )
            forecasting_horizon_steps = get_args_or_prompt_input(
                arg_name='forecast_horizon_steps',
                args=args,
                message='How many steps do you expect as a forecast horizon ?',
                force_interactive=interactive_mode,
                validator=IntegerValidator,
                filter_func=int
            )
            forecast_discount = get_args_or_prompt_input(
                arg_name='forecast_discount',
                args=args,
                message='Which discount value fo you want to apply on your forecasted values ?',
                force_interactive=interactive_mode,
                validator=FloatValidator,
                filter_func=float
            )
        nb_fold = get_args_or_prompt_input(
            arg_name='nb_fold',
            args=args,
            message='How many folds do you want ?',
            force_interactive=interactive_mode,
            validator=IntegerValidator,
            filter_func=int
        )
        scoring_metric = get_args_or_prompt_list(
            arg_name='scoring-metric',
            args=args,
            message='On which scoring metric do you want to optimize on ?',
            choices_function=lambda: list(map(str, ScoringMetric)),
            force_interactive=interactive_mode
        )
        budget = get_args_or_prompt_input(
            arg_name='budget',
            args=args,
            message='Which budget do you want to allow on optimization ?',
            force_interactive=interactive_mode,
            validator=IntegerValidator,
            filter_func=int
        )
        watch = get_args_or_prompt_confirm(
            arg_name='watch',
            args=args,
            message='Do you want to keep watching for the task until it ends ?',
            force_interactive=interactive_mode
        )
        task, _, _ = self.prescience_client.start_auto_ml(
            source_id=source_id,
            dataset_id=dataset_id,
            label_id=label_id,
            model_id=model_id,
            problem_type=problem_type,
            scoring_metric=scoring_metric,
            time_column=time_column,
            nb_fold=nb_fold,
            selected_column=selected_column,
            budget=budget,
            forecasting_horizon_steps=forecasting_horizon_steps,
            forecast_discount=forecast_discount
        )
        if watch:
            task.watch()
