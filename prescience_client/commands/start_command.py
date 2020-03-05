import json
from typing import List

import copy

from prescience_client.bean.config import Config
from prescience_client.bean.entity.local_file_input import LocalFileInput
from prescience_client.bean.entity.w10_ts_input import Warp10TimeSerieInput, TimeSerieFeature, Warp10Scheduler
from prescience_client.commands import get_args_or_prompt_input, get_args_or_prompt_confirm, get_args_or_prompt_list, \
    get_args_or_prompt_checkbox
from prescience_client.commands.command import Command
from prescience_client.config.constants import DEFAULT_PROBLEM_TYPE, DEFAULT_INPUT_TYPE, DEFAULT_SEPARATOR
from prescience_client.enum.input_type import InputType
from prescience_client.enum.problem_type import ProblemType
from prescience_client.enum.sampling_strategy import SamplingStrategy
from prescience_client.enum.scoring_metric import ScoringMetric, ScoringMetricRegression, get_scoring_metrics
from prescience_client.enum.separator import Separator
from prescience_client.utils.monad import List as UtilList
from prescience_client.utils.validator import IntegerValidator, FloatValidator
from prescience_client.utils.warp10 import Warp10Util


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
                StartAutoML(prescience_client),
                StartAutoMLWarp(prescience_client)
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
        self.cmd_parser.add_argument('--no-headers', default=True, dest='headers', action='store_false',
                                     help='Indicates that there is no header line on the csv file')
        self.cmd_parser.add_argument('--watch', default=False, action='store_true',
                                     help='Wait until the task ends and watch the progression')
        self.cmd_parser.add_argument('--input-type', type=InputType, choices=list(InputType),
                                     help=f"The input type of your local file (default: {DEFAULT_INPUT_TYPE})")
        self.cmd_parser.add_argument('--separator', type=Separator, choices=list(Separator),
                                     help=f"The CSV Separator (default: {DEFAULT_SEPARATOR})")
        self.cmd_parser.add_argument('--source-id', nargs='?', type=str,
                                     help='Identifier of your future source object.')

        self.cmd_parser.add_argument('--w10-read-token', type=str, dest='w10token',
                                     help='In case the input type is WARP_SCRIPT, define the wharp script read token to use to fetch data')
        self.cmd_parser.add_argument('--w10-url', type=str, dest='w10url',
                                     help='In case the input type is WARP_SCRIPT, define the Warp10 backend url to use to fetch data')

        self.cmd_parser.add_argument('--w10-grouping-keys', nargs='*', type=str, dest='w10_grouping_keys',
                                     help='The grouping keys to use for separating several time-series')
        self.cmd_parser.add_argument('--w10-last-date', type=str, dest='w10_last_date',
                                     help='End date to use when fetching data. Will be set to $READTOKEN in warp script')
        self.cmd_parser.add_argument('--w10-span', type=str, dest='w10_span',
                                     help='Span to use when fetching data. Will be set to $SPAN in warp script')

        self.cmd_parser.add_argument('input-filepath', nargs='?', type=str,
                                     help='Local input file to send and parse on prescience. If unset it will trigger the interactive mode.')

    def exec(self, args: dict):
        filepath = args.get('input-filepath')
        source_id = args.get('source_id')
        input_type = args.get('input_type')
        separator = args.get('separator')
        has_headers = args.get('headers')
        w10_read_token = args.get('w10token')
        w10_url = args.get('w10url')
        watch = args.get('watch')
        w10_grouping_key = args.get('w10_grouping_keys')
        w10_last_date = args.get('w10_last_date')
        sample_span = args.get('w10_span')

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
            if str(input_type) == str(InputType.CSV):
                separator = get_args_or_prompt_list(
                    arg_name='separator',
                    args=args,
                    message='What is your CSV Separator ?',
                    choices_function=lambda: list(map(str, Separator)),
                    force_interactive=interactive_mode
                )
                has_headers = get_args_or_prompt_confirm(
                    arg_name='headers',
                    args=args,
                    message='Does your csv file has a header row ? (doesn\'t matter in case of a parquet file)',
                    force_interactive=interactive_mode
                )
            elif str(input_type) == str(InputType.PARQUET):
                separator = None
                has_headers = True
            elif str(input_type) == str(InputType.WARP_SCRIPT):
                w10_url = get_args_or_prompt_input(
                    arg_name='w10url',
                    args=args,
                    message='Please indicate the Warp10 url to use for fetching data',
                    force_interactive=interactive_mode
                )
                w10_grouping_key = get_args_or_prompt_input(
                    arg_name='w10_grouping_keys',
                    args=args,
                    message='Please indicate the grouping keys that will be used to identify several time series',
                    force_interactive=interactive_mode
                )
                w10_last_date = get_args_or_prompt_input(
                    arg_name='w10_last_date',
                    args=args,
                    message='Please indicate the last date to use to fetch data',
                    force_interactive=interactive_mode
                )
                sample_span = get_args_or_prompt_input(
                    arg_name='w10_span',
                    args=args,
                    message='Please indicate the span to use as $SPAN parameter in the warp script',
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

        if str(input_type) == str(InputType.WARP_SCRIPT):
            parse_task = self.prescience_client.parse_warp_script(
                source_id=source_id,
                backend_url=w10_url,
                read_token=w10_read_token,
                file_path=filepath,
                grouping_keys=w10_grouping_key,
                last_point_timestamp=w10_last_date,
                sample_span=sample_span
            )
        else:
            input_local_file = LocalFileInput(
                input_type=input_type,
                headers=has_headers,
                separator=separator,
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
        self.cmd_parser.add_argument('--date-format', type=str,
                                     help='The date format to use for your time column (if any)')

    def exec(self, args: dict):
        interactive_mode = args.get('source-id') is None
        source_id = get_args_or_prompt_list(
            arg_name='id',
            args=args,
            message='Which source do you want to preprocess ?',
            choices_function=lambda: [x.get_source_id() for x in self.prescience_client.sources(page=1).content],
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
        formatter = None
        exogenous = None
        granularity = None
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
            formatter = get_args_or_prompt_input(
                arg_name='date_format',
                args=args,
                message='What date format do you want to use ?',
                force_interactive=interactive_mode
            )
            granularity = get_args_or_prompt_list(
                arg_name='granularity',
                args=args,
                message='Which granularity is used for your date ?',
                choices_function=lambda: ['year', 'month', 'day', 'hour', 'minute'],
                force_interactive=interactive_mode
            )
            exogenous = get_args_or_prompt_checkbox(
                arg_name='exogenous',
                args=args,
                message='Which exogenous features do you want on your date ?',
                choices_function=lambda: ['year', 'month', 'dayofmonth', 'hour', 'minute'],
                selected_function=lambda: [],
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
            nb_fold=int(nb_fold),
            formatter=formatter,
            datetime_exogenous=exogenous,
            granularity=granularity
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

        dataset = self.prescience_client.dataset(dataset_id)
        scoring_metric = get_args_or_prompt_list(
            arg_name='scoring-metric',
            args=args,
            message='On which scoring metric do you want to optimize on ?',
            choices_function=lambda: get_scoring_metrics(dataset.problem_type(), dataset.label_id(), dataset.source()),
            force_interactive=interactive_mode
        )
        if interactive_mode and self.prescience_client.dataset(
                dataset_id).problem_type() == ProblemType.TIME_SERIES_FORECAST:
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
        self.cmd_parser.add_argument('--watch', default=False, action='store_true',
                                     help='Wait until the task ends and watch the progression')

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
        self.cmd_parser.add_argument('columns', type=str, nargs='*',
                                     help='List of all initial columns to keep in the mask')

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

        interactive_mode = interactive_mode or args.get('mask-id') is None
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
        self.cmd_parser.add_argument('source-id', nargs="?", type=str,
                                     help='The source from which you want to start a AutoML task')
        self.cmd_parser.add_argument('scoring-metric', nargs="?", type=ScoringMetric, choices=list(ScoringMetric),
                                     help=f'The scoring metric to optimize on. If unset it will trigger the interactive mode.')

        self.cmd_parser.add_argument('--dataset-id', type=str, help='Name you want for the created dataset')
        self.cmd_parser.add_argument('--model-id', type=str, help='Name you want for the created model')

        self.cmd_parser.add_argument('--problem-type', type=ProblemType, choices=list(ProblemType),
                                     help=f"Type of problem for the dataset (default: {DEFAULT_PROBLEM_TYPE})",
                                     default=DEFAULT_PROBLEM_TYPE)
        self.cmd_parser.add_argument('--time-column', type=str,
                                     help='Identifier of the time column for time series. Only for forecasts problems.')
        self.cmd_parser.add_argument('--nb-fold', type=int, help='How many folds the dataset will be splited')
        self.cmd_parser.add_argument('--label', type=str,
                                     help='Column of your source that you want to use as the label')
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
            arg_name='source-id',
            args=args,
            message='Which source do you want to preprocess ?',
            choices_function=lambda: [x.get_source_id() for x in self.prescience_client.sources(page=1).content],
            force_interactive=interactive_mode
        )
        if interactive_mode:
            dataset_id = get_args_or_prompt_input(
                arg_name='dataset_id',
                args=args,
                message='What will be the name of the generated dataset',
                force_interactive=interactive_mode
            )
        else:
            dataset_id = args.get('dataset_id')

        if interactive_mode:
            model_id = get_args_or_prompt_input(
                arg_name='model_id',
                args=args,
                message='What will be the name of the generated model',
                force_interactive=interactive_mode
            )
        else:
            model_id = args.get('model_id')

        if interactive_mode:
            selected_column = get_args_or_prompt_checkbox(
                arg_name='columns',
                args=args,
                message='Select the columns you want to keep for your preprocessing',
                choices_function=lambda: [x.name() for x in self.prescience_client.source(source_id).schema().fields()],
                selected_function=lambda: [x.name() for x in
                                           self.prescience_client.source(source_id).schema().fields()],
                force_interactive=interactive_mode
            )
        else:
            selected_column = args.get('columns')

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
        _problem_type = ProblemType(problem_type)
        if _problem_type == ProblemType.TIME_SERIES_FORECAST:
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
        if interactive_mode:
            nb_fold = get_args_or_prompt_input(
                arg_name='nb_fold',
                args=args,
                message='How many folds do you want ?',
                force_interactive=interactive_mode,
                validator=IntegerValidator,
                filter_func=int
            )
        else:
            nb_fold = args.get('nb_fold')

        scoring_metric = get_args_or_prompt_list(
            arg_name='scoring-metric',
            args=args,
            message='On which scoring metric do you want to optimize on ?',
            choices_function=lambda: get_scoring_metrics(_problem_type, label_id,
                                                         self.prescience_client.source(source_id)),
            force_interactive=interactive_mode
        )

        if interactive_mode:
            budget = get_args_or_prompt_input(
                arg_name='budget',
                args=args,
                message='Which budget do you want to allow on optimization ?',
                force_interactive=interactive_mode,
                validator=IntegerValidator,
                filter_func=int
            )
        else:
            budget = args.get('budget')

        if interactive_mode:
            watch = get_args_or_prompt_confirm(
                arg_name='watch',
                args=args,
                message='Do you want to keep watching for the task until it ends ?',
                force_interactive=interactive_mode
            )
        else:
            watch = args.get('watch')

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


class StartAutoMLWarp(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='auto-ml-warp',
            help_message='Start an Auto-ML Warp task, which will chain all needed tasks until model deployment',
            prescience_client=prescience_client,
            sub_commands=[]
        )

    def init_from_subparser(self, subparsers, selector):
        super().init_from_subparser(subparsers, selector)
        self.cmd_parser.add_argument('source-id', type=str, nargs='?', help='The source name')
        self.cmd_parser.add_argument('read-token', type=str, nargs='?', help='The warp10 read token')
        self.cmd_parser.add_argument('selector', type=str, nargs='?', help='The warp10 selector')
        self.cmd_parser.add_argument('sample-span', type=str, nargs='?',
                                     help='The span over which the sample is read.(e.g: 6w for 6 weeks)')
        self.cmd_parser.add_argument('sampling-interval', type=str, nargs='?',
                                     help='The size of the interval which is reduced to a single point.(e.g: 1d for 1 day)')

        self.cmd_parser.add_argument('--labels', type=str,
                                     help='The labels of the warp 10 Time Series in json (ex: {"label":"label1"})')

        self.cmd_parser.add_argument('--scoring-metric', nargs='?', default=ScoringMetricRegression.MSE,
                                     type=ScoringMetricRegression,
                                     choices=list(ScoringMetricRegression),
                                     help=f'The scoring metric to optimize on. If unset it will trigger the interactive mode.')

        self.cmd_parser.add_argument('--sampling-strategy', nargs='?', type=SamplingStrategy,
                                     choices=list(SamplingStrategy), default=SamplingStrategy.MEAN,
                                     help=f'The strategy to use to transform an interval into a point.')

        self.cmd_parser.add_argument('--dataset-id', type=str, help='Name you want for the created dataset')
        self.cmd_parser.add_argument('--model-id', type=str, help='Name you want for the created model')
        self.cmd_parser.add_argument('--backend-url', type=str,
                                     help='The Warp10 backend url (Default: https://warp10.gra1-ovh.metrics.ovh.net)',
                                     default='https://warp10.gra1-ovh.metrics.ovh.net')

        self.cmd_parser.add_argument('--nb-fold', type=int, help='How many folds the dataset will be splited',
                                     default=10)

        self.cmd_parser.add_argument('--budget', type=int,
                                     help='Budget to allow on optimization (default: it will use the one configure on prescience server side)',
                                     default=6)

        self.cmd_parser.add_argument('--watch', default=False, action='store_true',
                                     help='Wait until the task ends and watch the progression')
        self.cmd_parser.add_argument('--forecast-horizon-steps', type=int, default=1,
                                     help='Number of steps forward to take into account as a forecast horizon for the optimization (Only in case of time series forecast)')
        self.cmd_parser.add_argument('--forecast-discount', type=float, default=1,
                                     help='Discount to apply on each time step before the horizon (Only in case of time series forecast)')

        self.cmd_parser.add_argument('--scheduler', default=False, action='store_true',
                                     help='Add a scheduler to the model scheduled')

        self.cmd_parser.add_argument('--scheduler-frequency', type=int, default=1,
                                     help='Frequency for the prediction, linked to sampling interval. (Ex: 2 will predict every to sampling interval)')

        self.cmd_parser.add_argument('--write-token', type=str, help='The warp10 write token')

    def exec(self, args: dict):

        interactive_mode = args.get('source-id') is None

        source_id = get_args_or_prompt_input(
            arg_name='source-id',
            args=args,
            message='What will be the name of the generated source',
            force_interactive=interactive_mode
        )

        read_token = get_args_or_prompt_input(
            arg_name='read-token',
            args=args,
            message='What is your read token',
            force_interactive=interactive_mode
        )

        selector = get_args_or_prompt_input(
            arg_name='selector',
            args=args,
            message='What is your warp 10 selector, It must match only one GTS',
            force_interactive=interactive_mode
        )

        labels = get_args_or_prompt_input(
            arg_name='labels',
            args=args,
            message='What is your warp 10 labels, It must match only one GTS (ex: {"label":"label1"})',
            force_interactive=interactive_mode
        )

        sample_span = get_args_or_prompt_input(
            arg_name='sample-span',
            args=args,
            message='What is the span over which the sample is read.(e.g: 6w for 6 weeks)',
            force_interactive=interactive_mode
        )

        sampling_interval = get_args_or_prompt_input(
            arg_name='sampling-interval',
            args=args,
            message='The size of the interval which is reduced to a single point.(e.g: 1d for 1 day)',
            force_interactive=interactive_mode
        )

        if interactive_mode:
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
        else:
            dataset_id = args.get('dataset_id')
            model_id = args.get('model_id')

        sampling_strategy = get_args_or_prompt_list(
            arg_name='sampling_strategy',
            args=args,
            message='Wich strategy to use to transform an interval into a point ?',
            choices_function=lambda: list(map(str, SamplingStrategy)),
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
            arg_name='scoring_metric',
            args=args,
            message='On which scoring metric do you want to optimize on ?',
            choices_function=lambda: list(map(str, ScoringMetricRegression)),
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

        backend_url = args.get('backend_url')

        input_ts = TimeSerieFeature(selector, labels)
        warp_input = Warp10TimeSerieInput(
            value=input_ts,
            source_id=source_id,
            read_token=read_token,
            sample_span=sample_span,
            sampling_interval=sampling_interval,
            sampling_strategy=sampling_strategy,
            backend_url=backend_url,
            last_point_date=None
        )

        scheduler = args.get('scheduler')

        if interactive_mode:
            scheduler = get_args_or_prompt_confirm(
                arg_name='scheduler',
                args=args,
                message='Do you want to add a scheduler to the model generated ?',
                force_interactive=interactive_mode
            )

        if scheduler:
            write_token = get_args_or_prompt_input(
                arg_name='write_token',
                args=args,
                message='What is your write token',
                force_interactive=interactive_mode
            )

            scheduler_frequency = get_args_or_prompt_input(
                arg_name='scheduler_frequency',
                args=args,
                message='How many intervals you want to make a prediction ?',
                force_interactive=interactive_mode,
                validator=IntegerValidator,
                filter_func=int
            )

            # We keep the same labes and add predicted to the selector
            scheduler_output = Warp10Scheduler(
                write_token=write_token,
                frequency=scheduler_frequency,
                output_value=TimeSerieFeature(f'{selector}.predicted', labels),
                nb_steps=None
            )
        else:
            scheduler_output = None

        watch = get_args_or_prompt_confirm(
            arg_name='watch',
            args=args,
            message='Do you want to keep watching for the task until it ends ?',
            force_interactive=interactive_mode
        )

        task, _, _ = self.prescience_client.start_auto_ml_warp10(
            warp_input=warp_input,
            scheduler_output=scheduler_output,
            dataset_id=dataset_id,
            model_id=model_id,
            scoring_metric=scoring_metric,
            nb_fold=nb_fold,
            budget=budget,
            forecasting_horizon_steps=forecasting_horizon_steps,
            forecast_discount=forecast_discount
        )

        query = Warp10Util.generate_warp10_query(token=read_token, input_ts=input_ts,
                                                 interval=sampling_interval, horizon=forecasting_horizon_steps)

        print('You can find your results here:')
        print(Warp10Util.generate_warp10_quantum_query(query, backend_url))

        if watch:
            task.watch()
