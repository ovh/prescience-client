import json

from prescience_client.commands import prompt_for_source_id_if_needed, prompt_for_dataset_id_if_needed, \
    get_args_or_prompt_list
from prescience_client.commands.command import Command
from prescience_client.enum.algorithm_configuration_category import AlgorithmConfigurationCategory
from prescience_client.enum.output_format import OutputFormat


class GetCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='get',
            help_message='Show information about specific prescience objects',
            prescience_client=prescience_client,
            sub_commands=[
                GetSourceCommand(prescience_client),
                GetSourceListCommand(prescience_client),
                GetDatasetCommand(prescience_client),
                GetDatasetListCommand(prescience_client),
                GetModelCommand(prescience_client),
                GetModelListCommand(prescience_client),
                GetTaskCommand(prescience_client),
                GetTaskListCommand(prescience_client),
                GetAlgorithmCommand(prescience_client),
                GetAlgorithmListCommand(prescience_client),
                GetEvaluationListCommand(prescience_client)
            ]
        )

class GetSourceCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='source',
            help_message='Show information about specific prescience source',
            prescience_client=prescience_client,
            sub_commands=[]
        )

    def init_from_subparser(self, subparsers, selector):
        super().init_from_subparser(subparsers, selector)
        self.cmd_parser.add_argument('id', nargs='?', type=str, help='The ID of the source. If unset if will trigger the interactive mode for selecting one.')
        self.cmd_parser.add_argument('--schema', default=False, action='store_true', help='Display the schema of the source')
        self.cmd_parser.add_argument('--download', type=str, help='Directory in which to download data files for this source')
        self.cmd_parser.add_argument('--cache', default=False, action='store_true', help='Cache the source data inside local cache directory')
        self.cmd_parser.add_argument('-o', '--output', dest='output', type=OutputFormat, choices=list(OutputFormat), help=f"Type of output to get on std out. (default: {OutputFormat.TABLE})")

    def exec(self, args: dict):
        source_id = prompt_for_source_id_if_needed(args, self.prescience_client)
        source = self.prescience_client.source(source_id)
        download_directory = args.get('download')
        cache = args.get('cache')
        output = args.get('output')
        if args.get('schema'):
            source.schema().show(output)
        elif download_directory is not None:
            self.prescience_client.download_source(source_id=source_id, output_directory=download_directory)
        elif cache:
            self.prescience_client.update_cache_source(source_id)
        else:
            source.show(output)

class GetSourceListCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='sources',
            help_message='Show all source objects on the current project',
            prescience_client=prescience_client,
            sub_commands=[]
        )

    def init_from_subparser(self, subparsers, selector):
        super().init_from_subparser(subparsers, selector)
        self.cmd_parser.add_argument('--page', type=int)
        self.cmd_parser.add_argument('-o', '--output', dest='output', type=OutputFormat, choices=list(OutputFormat),
                                    help=f"Type of output to get on std out. (default: {OutputFormat.TABLE})")

    def exec(self, args: dict):
        page = args.get('page') or 1
        output = args.get('output') or OutputFormat.TABLE
        self.prescience_client.sources(page=page).show(output)



class GetEvaluationListCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='evaluations',
            help_message='Show information about evaluations for a given dataset',
            prescience_client=prescience_client,
            sub_commands=[]
        )

    def init_from_subparser(self, subparsers, selector):
        super().init_from_subparser(subparsers, selector)
        self.cmd_parser.add_argument('id', nargs='?', type=str,
                                    help='The ID of the dataset. If unset if will trigger the interactive mode for selecting one.')
        self.cmd_parser.add_argument('--forecasting-horizon-steps', type=int)
        self.cmd_parser.add_argument('--forecasting-discount', type=float)
        self.cmd_parser.add_argument('-o', '--output', dest='output', type=OutputFormat, choices=list(OutputFormat),
                                    help=f"Type of output to get on std out. (default: {OutputFormat.TABLE})")

    def exec(self, args: dict):
        dataset_id = prompt_for_dataset_id_if_needed(args, self.prescience_client)
        output = args.get('output')
        forecasting_horizon_steps = args.get('forecasting_horizon_steps')
        forecasting_discount = args.get('forecasting_discount')
        evalution_results_page = self.prescience_client.get_evaluation_results(
            dataset_id=dataset_id,
            forecasting_horizon_steps=forecasting_horizon_steps,
            forecasting_discount=forecasting_discount,
            sort_column='config.name'
        )
        evalution_results_page.show(output)

class GetDatasetCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='dataset',
            help_message='Show information about specific prescience source',
            prescience_client=prescience_client,
            sub_commands=[]
        )

    def init_from_subparser(self, subparsers, selector):
        super().init_from_subparser(subparsers, selector)
        self.cmd_parser.add_argument('id', nargs='?', type=str,
                                    help='The ID of the dataset. If unset if will trigger the interactive mode for selecting one.')
        self.cmd_parser.add_argument('--schema', default=False, action='store_true',
                                    help='Display the schema of the dataset')
        self.cmd_parser.add_argument('--download-train', dest='download_train', type=str,
                                    help='Directory in which to download data files for this train dataset')
        self.cmd_parser.add_argument('--download-test', dest='download_test', type=str,
                                    help='Directory in which to download data files for this test dataset')
        self.cmd_parser.add_argument('--cache', default=False, action='store_true',
                                    help='Cache the dataset data inside local cache directory')
        self.cmd_parser.add_argument('-o', '--output', dest='output', type=OutputFormat, choices=list(OutputFormat),
                                    help=f"Type of output to get on std out. (default: {OutputFormat.TABLE})")

    def exec(self, args: dict):
        display_schema = args.get('schema')
        dataset_id = prompt_for_dataset_id_if_needed(args, self.prescience_client)
        output = args.get('output')
        download_train_directory = args.get('download_train')
        download_test_directory = args.get('download_test')
        if display_schema:
            self.prescience_client.dataset(dataset_id).schema().show(output)
        elif download_train_directory is not None:
            self.prescience_client.download_dataset(dataset_id=dataset_id, output_directory=download_train_directory,
                                        test_part=False)
        elif download_test_directory is not None:
            self.prescience_client.download_dataset(dataset_id=dataset_id, output_directory=download_test_directory, test_part=True)
        else:
            self.prescience_client.dataset(dataset_id).show(output)


class GetDatasetListCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='datasets',
            help_message='Show all dataset objects on the current project',
            prescience_client=prescience_client,
            sub_commands=[]
        )

    def init_from_subparser(self, subparsers, selector):
        super().init_from_subparser(subparsers, selector)
        self.cmd_parser.add_argument('--page', type=int)
        self.cmd_parser.add_argument('-o', '--output', dest='output', type=OutputFormat, choices=list(OutputFormat),
                                     help=f"Type of output to get on std out. (default: {OutputFormat.TABLE})")

    def exec(self, args: dict):
        page = args.get('page') or 1
        output = args.get('output') or OutputFormat.TABLE
        self.prescience_client.datasets(page=page).show(output)


class GetModelCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='model',
            help_message='Show information about a single model',
            prescience_client=prescience_client,
            sub_commands=[]
        )

    def init_from_subparser(self, subparsers, selector):
        super().init_from_subparser(subparsers, selector)
        self.cmd_parser.add_argument('id', nargs='?', type=str, help='The ID of the model. If unset it will trigger the interactive mode for selecting one.')
        self.cmd_parser.add_argument('-o', '--output', dest='output', type=OutputFormat, choices=list(OutputFormat),
                                   help=f"Type of output to get on std out. (default: {OutputFormat.TABLE})",
                                   default=OutputFormat.TABLE)

    def exec(self, args: dict):
        model_id = get_args_or_prompt_list(
            arg_name='id',
            args=args,
            message='Which model do you want to get ?',
            choices_function=lambda: [x.model_id() for x in self.prescience_client.models(page=1).content]
        )
        output = args.get('output') or OutputFormat.TABLE
        model = self.prescience_client.model(model_id)
        model.show(output)


class GetModelListCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='models',
            help_message='Show all model objects on the current project',
            prescience_client=prescience_client,
            sub_commands=[]
        )

    def init_from_subparser(self, subparsers, selector):
        super().init_from_subparser(subparsers, selector)
        self.cmd_parser.add_argument('--page', type=int)
        self.cmd_parser.add_argument('-o', '--output', dest='output', type=OutputFormat, choices=list(OutputFormat),
                                   help=f"Type of output to get on std out. (default: {OutputFormat.TABLE})")

    def exec(self, args: dict):
        page = args.get('page') or 1
        output = args.get('output') or OutputFormat.TABLE
        self.prescience_client.models(page=page).show(output)

class GetTaskCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='task',
            help_message='Show information about a single task',
            prescience_client=prescience_client,
            sub_commands=[]
        )

    def init_from_subparser(self, subparsers, selector):
        super().init_from_subparser(subparsers, selector)
        self.cmd_parser.add_argument('id', type=str)
        self.cmd_parser.add_argument('-o', '--output', dest='output', type=OutputFormat, choices=list(OutputFormat),
                                 help=f"Type of output to get on std out. (default: {OutputFormat.TABLE})")

    def exec(self, args: dict):
        output = args.get('output') or OutputFormat.TABLE
        task_id = get_args_or_prompt_list(
            arg_name='id',
            args=args,
            message='Which task uuid do you want to get ?',
            choices_function=lambda: [x.uuid() for x in self.prescience_client.tasks(page=1).content]
        )
        self.prescience_client.task(task_id).show(output)



class GetTaskListCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='tasks',
            help_message='Show all task objects on the current project',
            prescience_client=prescience_client,
            sub_commands=[]
        )

    def init_from_subparser(self, subparsers, selector):
        super().init_from_subparser(subparsers, selector)
        self.cmd_parser.add_argument('--page', type=int)
        self.cmd_parser.add_argument('--status', type=str)
        self.cmd_parser.add_argument('-o', '--output', dest='output', type=OutputFormat, choices=list(OutputFormat),
                                  help=f"Type of output to get on std out. (default: {OutputFormat.TABLE})")


    def exec(self, args: dict):
        page = args.get('page') or 1
        output = args.get('output') or OutputFormat.TABLE
        status = args.get('status')
        self.prescience_client.tasks(page=page, status=status).show(output)


class GetAlgorithmCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='algorithm',
            help_message='Show all available algorithms',
            prescience_client=prescience_client,
            sub_commands=[]
        )

    def init_from_subparser(self, subparsers, selector):
        super().init_from_subparser(subparsers, selector)
        self.cmd_parser.add_argument('category', nargs='?',
                                      help='Category of algorithms. If unset it will trigger the interactive mode',
                                      type=AlgorithmConfigurationCategory, choices=list(AlgorithmConfigurationCategory))
        self.cmd_parser.add_argument('id', nargs='?',
                                      help='ID of the algorithm. If unset it will trigger the interactive mode')
        self.cmd_parser.add_argument('-o', '--output', dest='output', type=OutputFormat, choices=list(OutputFormat),
                                      help=f"Type of output to get on std out. (default: {OutputFormat.TABLE})")
        self.cmd_parser.add_argument('--create', action='store_true', default=False,
                                      help='Create a json instance of a prescience configuration from the current algorithm specifications.')

    def exec(self, args: dict):
        category = get_args_or_prompt_list(
            arg_name='category',
            args=args,
            message='Which algorithm category do you want to get ?',
            choices_function=lambda: list(map(str, AlgorithmConfigurationCategory))
        )
        all_config = self.prescience_client.get_available_configurations(kind=category)
        algo_id = get_args_or_prompt_list(
            arg_name='id',
            args=args,
            message='Which algorithm ID do you want to get ?',
            choices_function=all_config.get_algorithm_list_names
        )
        output = args.get('output')
        create = args.get('create')
        algorithm = all_config.get_algorithm(algo_id)
        if create:
            algorithm_config = algorithm.interactive_kwargs_instanciation()
            print(json.dumps(algorithm_config.to_dict()))
        else:
            algorithm.show(ouput=output)


class GetAlgorithmListCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='algorithms',
            help_message='Show information about a single algorithms',
            prescience_client=prescience_client,
            sub_commands=[]
        )

    def init_from_subparser(self, subparsers, selector):
        super().init_from_subparser(subparsers, selector)
        self.cmd_parser.add_argument('category', nargs='?',
                                       help='Category of algorithms. If unset it will trigger the interactive mode',
                                       type=AlgorithmConfigurationCategory,
                                       choices=list(AlgorithmConfigurationCategory))
        self.cmd_parser.add_argument('-o', '--output', dest='output', type=OutputFormat, choices=list(OutputFormat),
                                       help=f"Type of output to get on std out. (default: {OutputFormat.TABLE})")

    def exec(self, args: dict):
        category = get_args_or_prompt_list(
            arg_name='category',
            args=args,
            message='Which algorithm category do you want to get ?',
            choices_function=lambda: list(map(str, AlgorithmConfigurationCategory))
        )
        output = args.get('output')
        self.prescience_client.get_available_configurations(kind=category).show(ouput=output)
