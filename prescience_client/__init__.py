# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

import argparse
import json
from typing import List, Callable

import argcomplete
import copy

from prescience_client.bean.config import Config
from prescience_client.enum.algorithm_configuration_category import AlgorithmConfigurationCategory
from prescience_client.enum.scoring_metric import ScoringMetric

from prescience_client.client.prescience_client import PrescienceClient
from prescience_client.config.constants import DEFAULT_PROBLEM_TYPE, DEFAULT_SCORING_METRIC
from prescience_client.config.prescience_config import PrescienceConfig
from prescience_client.enum.output_format import OutputFormat
from prescience_client.enum.problem_type import ProblemType
from prescience_client.exception.prescience_client_exception import PrescienceException
from PyInquirer import prompt
from prescience_client.utils.monad import List as UtilList

config = PrescienceConfig().load()
prescience: PrescienceClient = PrescienceClient(config)

def init_args():
    """Parse and return the arguments."""
    parser = argparse.ArgumentParser(description='Python client for OVH Prescience project')
    # CMD
    subparsers = parser.add_subparsers(dest='cmd')

    # config
    cmd_config_parser = subparsers.add_parser('config', help='Manage your prescience-client configuration')
    config_subparser = cmd_config_parser.add_subparsers(dest='config_cmd')

    # config get
    config_get_parser = config_subparser.add_parser('get', help='Show information about specifics prescience objects')
    config_get_parser.add_argument('-o', '--output', dest='output', type=OutputFormat, choices=list(OutputFormat),
                                help=f"Type of output to get on std out. (default: {OutputFormat.TABLE})",
                                default=OutputFormat.TABLE)

    # config switch
    config_switch_parser = config_subparser.add_parser('switch', help='Change the currently selected prescience project')
    config_switch_parser.add_argument('project', nargs='?', type=str, help='The project name you want to switch on. If no project is indicated, it will turn on the interactive mode for selecting one.')

    # config set
    config_set_parser = config_subparser.add_parser('add', help='Add a new project and its token')
    config_set_parser.add_argument('project', type=str, help='The project name')
    config_set_parser.add_argument('token', type=str, help='The token linked to this project')

    # get
    cmd_get_parser = subparsers.add_parser('get', help='Show information about specific prescience objects')
    get_subparser = cmd_get_parser.add_subparsers(dest='subject')
    source_parser = get_subparser.add_parser('source', help='Show information about a single source')
    dataset_parser = get_subparser.add_parser('dataset', help='Show information about a single dataset')
    model_parser = get_subparser.add_parser('model', help='Show information about a single model')
    sources_parser = get_subparser.add_parser('sources', help='Show all source objects on the current project')
    datasets_parser = get_subparser.add_parser('datasets', help='Show all dataset objects on the current project')
    models_parser = get_subparser.add_parser('models', help='Show all model objects on the current project')
    tasks_parser = get_subparser.add_parser('tasks', help='Show all task objects on the current project')
    task_parser = get_subparser.add_parser('task', help='Show information about a single task')
    algorithms_parser = get_subparser.add_parser('algorithms', help='Show all available algorithms')
    algorithm_parser = get_subparser.add_parser('algorithm', help='Show information about a single algorithms')

    ## get sources
    sources_parser.add_argument('--page', type=int)
    sources_parser.add_argument('-o', '--output', dest='output', type=OutputFormat, choices=list(OutputFormat),
                                help=f"Type of output to get on std out. (default: {OutputFormat.TABLE})")
    ## get datasets
    datasets_parser.add_argument('--page', type=int)
    datasets_parser.add_argument('-o', '--output', dest='output', type=OutputFormat, choices=list(OutputFormat),
                                help=f"Type of output to get on std out. (default: {OutputFormat.TABLE})")
    ## get models
    models_parser.add_argument('--page', type=int)
    models_parser.add_argument('-o', '--output', dest='output', type=OutputFormat, choices=list(OutputFormat),
                                help=f"Type of output to get on std out. (default: {OutputFormat.TABLE})")

    ## get tasks
    tasks_parser.add_argument('--page', type=int)
    tasks_parser.add_argument('--status', type=str)
    tasks_parser.add_argument('-o', '--output', dest='output', type=OutputFormat, choices=list(OutputFormat),
                                help=f"Type of output to get on std out. (default: {OutputFormat.TABLE})")
    # Get task
    task_parser.add_argument('id', type=str)
    task_parser.add_argument('-o', '--output', dest='output', type=OutputFormat, choices=list(OutputFormat), help=f"Type of output to get on std out. (default: {OutputFormat.TABLE})")

    ## get source
    source_parser.add_argument('id', nargs='?', type=str, help='The ID of the source. If unset if will trigger the interactive mode for selecting one.')
    source_parser.add_argument('--schema', default=False, action='store_true', help='Display the schema of the source')
    source_parser.add_argument('--download', type=str, help='Directory in which to download data files for this source')
    source_parser.add_argument('--cache', default=False, action='store_true', help='Cache the source data inside local cache directory')
    source_parser.add_argument('-o', '--output', dest='output', type=OutputFormat, choices=list(OutputFormat), help=f"Type of output to get on std out. (default: {OutputFormat.TABLE})")
    ## get dataset
    dataset_parser.add_argument('id', nargs='?', type=str, help='The ID of the dataset. If unset if will trigger the interactive mode for selecting one.')
    dataset_parser.add_argument('--schema', default=False, action='store_true', help='Display the schema of the dataset')
    dataset_parser.add_argument('--eval', default=False, action='store_true', help='Display the evaluation results of the dataset')
    dataset_parser.add_argument('--forecasting-horizon-steps', type=int)
    dataset_parser.add_argument('--forecasting-discount', type=float)
    dataset_parser.add_argument('--download-train', dest='download_train', type=str, help='Directory in which to download data files for this train dataset')
    dataset_parser.add_argument('--download-test', dest='download_test', type=str, help='Directory in which to download data files for this test dataset')
    dataset_parser.add_argument('--cache', default=False, action='store_true', help='Cache the dataset data inside local cache directory')
    dataset_parser.add_argument('-o', '--output', dest='output', type=OutputFormat, choices=list(OutputFormat),
                               help=f"Type of output to get on std out. (default: {OutputFormat.TABLE})")
    # get model
    model_parser.add_argument('id', nargs='?', type=str, help='The ID of the model. If unset it will trigger the interactive mode for selecting one.')
    model_parser.add_argument('-o', '--output', dest='output', type=OutputFormat, choices=list(OutputFormat),
                               help=f"Type of output to get on std out. (default: {OutputFormat.TABLE})",
                               default=OutputFormat.TABLE)

    # get algorithms
    algorithms_parser.add_argument('category', nargs='?', help='Category of algorithms. If unset it will trigger the interactive mode', type=AlgorithmConfigurationCategory, choices=list(AlgorithmConfigurationCategory))
    algorithms_parser.add_argument('-o', '--output', dest='output', type=OutputFormat, choices=list(OutputFormat),
                                help=f"Type of output to get on std out. (default: {OutputFormat.TABLE})")

    # get algorithm
    algorithm_parser.add_argument('category', nargs='?', help='Category of algorithms. If unset it will trigger the interactive mode', type=AlgorithmConfigurationCategory, choices=list(AlgorithmConfigurationCategory))
    algorithm_parser.add_argument('id', nargs='?', help='ID of the algorithm. If unset it will trigger the interactive mode')
    algorithm_parser.add_argument('-o', '--output', dest='output', type=OutputFormat, choices=list(OutputFormat),
                                   help=f"Type of output to get on std out. (default: {OutputFormat.TABLE})")
    algorithm_parser.add_argument('--create', action='store_true', default=False, help='Create a json instance of a prescience configuration from the current algorithm specifications.')

    # start
    cmd_start_parser = subparsers.add_parser('start', help='Start a task on prescience')
    start_subparser = cmd_start_parser.add_subparsers(dest='subject')
    ## start parse
    parse_parser = start_subparser.add_parser('parse', help='Launch a parse task on prescience')
    parse_parser.add_argument('--no-headers', default=True, dest='headers', action='store_false', help='Indicates that there is no header line on the csv file')
    parse_parser.add_argument('--watch', default=False, action='store_true', help='Wait until the task ends and watch the progression')
    parse_parser.add_argument('--input-filepath', type=str, help='Local input file to send and parse on prescience')
    parse_parser.add_argument('source-id', nargs='?', type=str, help='Identifier of your future source object. If unset it will trigger the interactive mode.')
    ## start preprocess
    preprocess_parser = start_subparser.add_parser('preprocess', help='Launch a preprocess task on prescience')
    preprocess_parser.add_argument('source-id', nargs='?', type=str, help='Identifier of the source object to use for preprocessing. If unset it will trigger the interactive mode.')
    preprocess_parser.add_argument('dataset-id', nargs='?', type=str, help='Identifier of your future dataset object. If unset it will trigger the interactive mode.')
    preprocess_parser.add_argument('label', nargs='?', type=str, help='Identifier of the column to predict. If unset it will trigger the interactive mode.')
    preprocess_parser.add_argument('--columns', type=List[str], help='Subset of columns to include in the dataset. (default: all)')
    preprocess_parser.add_argument('--problem-type', type=ProblemType, choices=list(ProblemType), help=f"Type of problem for the dataset (default: {DEFAULT_PROBLEM_TYPE})", default=DEFAULT_PROBLEM_TYPE)
    preprocess_parser.add_argument('--time-column', type=str, help='Identifier of the time column for time series. Only for forecasts problems.')
    preprocess_parser.add_argument('--watch', default=False, action='store_true', help='Wait until the task ends and watch the progression')
    preprocess_parser.add_argument('--nb-fold', type=int, help='How many folds the dataset will be splited')
    ## start optimize
    optimize_parser = start_subparser.add_parser('optimize', help='Launch an optimize task on prescience')
    optimize_parser.add_argument('dataset-id', nargs='?', type=str, help='Dataset identifier to optimize on. If unset it will trigger the interactive mode.')
    optimize_parser.add_argument('scoring-metric', nargs='?', type=ScoringMetric, choices=list(ScoringMetric), help=f'The scoring metric to optimize on. If unset it will trigger the interactive mode.')
    optimize_parser.add_argument('--budget', type=int, help='Budget to allow on optimization (default: it will use the one configure on prescience server side)')
    optimize_parser.add_argument('--watch', default=False, action='store_true', help='Wait until the task ends and watch the progression')
    optimize_parser.add_argument('--forecast-horizon-steps', type=int, help='Number of steps forward to take into account as a forecast horizon for the optimization (Only in case of time series forecast)')
    optimize_parser.add_argument('--forecast-discount', type=float, help='Discount to apply on each time step before the horizon (Only in case of time series forecast)')
    ## start train
    train_parser = start_subparser.add_parser('train', help='Launch a train task on prescience')
    train_parser.add_argument('uuid', type=str, help='Chosen evaluation result uuid to train on')
    train_parser.add_argument('model-id', type=str, help='Identifier of your future model object')
    train_parser.add_argument('--watch', default=False, action='store_true', help='Wait until the task ends and watch the progression')
    ## start retrain
    retrain_parser = start_subparser.add_parser('retrain', help='Launch a retrain task on prescience')
    retrain_parser.add_argument('--watch', action='store_true', help='Wait until the task ends and watch the progression')
    retrain_parser.add_argument('model-id', type=str, help='Model to retrain')
    retrain_parser.add_argument('--input-filepath', type=str, help='Local input file to send in order to retrain the model on prescience')
    ## start refresh dataset
    retrain_parser = start_subparser.add_parser('refresh', help='Launch a refresh dataset task on prescience')
    retrain_parser.add_argument('--watch', action='store_true', help='Wait until the task ends and watch the progression')
    retrain_parser.add_argument('dataset-id', type=str, help='Dataset to refresh')
    retrain_parser.add_argument('--input-filepath', type=str, help='Local input file/directory to send in order to refresh the dataset on prescience')
    ## start evaluation
    evaluation_parser = start_subparser.add_parser('evaluation', help='Launch an evaluation of a custom algorithm configuration')
    evaluation_parser.add_argument('dataset-id', nargs='?', type=str, help='Dataset to launch an evaluation on. If unset it will trigger the interactive mode.')
    evaluation_parser.add_argument('custom-config', nargs='?', type=str, help='Configuration to use on the evaluation (in json format). If unset it will trigger the interactive mode.')
    evaluation_parser.add_argument('--watch', action='store_true',
                                help='Wait until the task ends and watch the progression')


    # predict
    cmd_predict_parser = subparsers.add_parser('predict', help='Make prediction(s) from a presience model')
    cmd_predict_parser.add_argument('model-id', type=str, help='Identifier if the model object to make prediction on')
    cmd_predict_parser.add_argument('--json', type=str, default='{}', help='All arguments to send as input of prescience model (in json format)')
    cmd_predict_parser.add_argument('--validate', default=False, action='store_true', help='Validate the prediction request and don\'t send it')

    # delete
    cmd_delete_parser = subparsers.add_parser('delete', help='Delete a prescience object')
    delete_subparser = cmd_delete_parser.add_subparsers(dest='subject')
    ## delete source
    delete_source_parser = delete_subparser.add_parser('source', help='Delete a prescience source object')
    delete_source_parser.add_argument('id', nargs='?', type=str, help='Identifier of the source object to delete')

    ## delete dataset
    delete_dataset_parser = delete_subparser.add_parser('dataset', help='Delete a prescience dataset object')
    delete_dataset_parser.add_argument('id', nargs='?', type=str, help='Identifier of the dataset object to delete')

    ## delete model
    delete_model_parser = delete_subparser.add_parser('model', help='Delete a prescience model object')
    delete_model_parser.add_argument('id', nargs='?', type=str, help='Identifier of the model object to delete')

    # plot
    cmd_plot_parser = subparsers.add_parser('plot', help='Plot a prescience object')
    plot_subparser = cmd_plot_parser.add_subparsers(dest='subject')

    ## plot source
    plot_source_parser = plot_subparser.add_parser('source', help='Plot a source data object')
    plot_source_parser.add_argument('id', nargs ='?', type=str, help='Identifier of the source object. If unset if will trigger the interactive mode for selecting one.')
    plot_source_parser.add_argument('--x', type=str, help='Plot the current source')
    plot_source_parser.add_argument('--kind', type=str, help='Kind of the plot figure. Default: line')

    ## plot dataset
    plot_dataset_parser = plot_subparser.add_parser('dataset', help='Plot a dataset data object')
    plot_dataset_parser.add_argument('id', nargs ='?', type=str, help='Identifier of the dataset object. If unset if will trigger the interactive mode for selecting one.')
    plot_dataset_parser.add_argument('--no-test', dest='plot_test', action='store_false', help='Won\'t plot the test part')
    plot_dataset_parser.add_argument('--no-train', dest='plot_train', action='store_false', help='Won\'t plot the train part')

    argcomplete.autocomplete(parser)
    args = vars(parser.parse_args())
    return args

def get_tasks(args: dict):
    """
    Show model list
    """
    page = args.get('page') or 1
    output = args.get('output') or OutputFormat.TABLE
    status = args.get('status')
    prescience.tasks(page=page, status=status).show(output)

def get_task(args: dict):
    """
    Show model list
    """
    output = args.get('output') or OutputFormat.TABLE
    task_id = get_args_or_prompt_list(
        arg_name='id',
        args=args,
        message='Which task uuid do you want to get ?',
        choices_function=lambda: [x.uuid() for x in prescience.tasks(page=1).content]
    )
    prescience.task(task_id).show(output)

def get_models(args: dict):
    """
    Show model list
    """
    page = args.get('page') or 1
    output = args.get('output') or OutputFormat.TABLE
    prescience.models(page=page).show(output)

def get_model(args: dict):
    """
    Show single model
    """
    model_id = get_args_or_prompt_list(
        arg_name='id',
        args=args,
        message='Which model do you want to get ?',
        choices_function=lambda: [x.model_id() for x in prescience.models(page=1).content]
    )
    output = args.get('output') or OutputFormat.TABLE
    model = prescience.model(model_id)
    model.show(output)


def get_datasets(args: dict):
    """
    Show datasets list
    """
    page = args.get('page') or 1
    output = args.get('output') or OutputFormat.TABLE
    prescience.datasets(page=page).show(output)

def get_dataset(args: dict):
    """
    Show single dataset
    """
    display_eval = args.get('eval')
    forecasting_horizon_steps = args.get('forecasting_horizon_steps')
    forecasting_discount = args.get('forecasting_discount')
    display_schema = args.get('schema')
    dataset_id = prompt_for_dataset_id_if_needed(args)
    output = args.get('output')
    download_train_directory = args.get('download_train')
    download_test_directory = args.get('download_test')
    if display_eval:
        evalution_results_page = prescience.get_evaluation_results(
            dataset_id=dataset_id,
            forecasting_horizon_steps=forecasting_horizon_steps,
            forecasting_discount=forecasting_discount,
            sort_column='config.name'
        )
        evalution_results_page.show(output)
    elif display_schema:
        prescience.dataset(dataset_id).schema().show(output)
    elif download_train_directory is not None:
        prescience.download_dataset(dataset_id=dataset_id, output_directory=download_train_directory, test_part=False)
    elif download_test_directory is not None:
        prescience.download_dataset(dataset_id=dataset_id, output_directory=download_test_directory, test_part=True)
    else:
        prescience.dataset(dataset_id).show(output)

def get_sources(args: dict):
    """
    Show sources list
    """
    page = args.get('page') or 1
    output = args.get('output') or OutputFormat.TABLE
    prescience.sources(page=page).show(output)

def get_source(args: dict):
    """
    Show single source
    """
    source_id = prompt_for_source_id_if_needed(args)
    source = prescience.source(source_id)
    download_directory = args.get('download')
    cache = args.get('cache')
    output = args.get('output')
    if args.get('schema'):
        source.schema().show(output)
    elif download_directory is not None:
        prescience.download_source(source_id=source_id, output_directory=download_directory)
    elif cache:
        prescience.update_cache_source(source_id)
    else:
        source.show(output)

def get_algorithms(args: dict):
    """
    Show all algorithms
    """
    category = get_args_or_prompt_list(
        arg_name='category',
        args=args,
        message='Which algorithm category do you want to get ?',
        choices_function=lambda: list(map(str, AlgorithmConfigurationCategory))
    )
    output = args.get('output')
    prescience.get_available_configurations(kind=category).show(ouput=output)

def get_algorithm(args: dict):
    category = get_args_or_prompt_list(
        arg_name='category',
        args=args,
        message='Which algorithm category do you want to get ?',
        choices_function=lambda: list(map(str, AlgorithmConfigurationCategory))
    )
    all_config = prescience.get_available_configurations(kind=category)
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

def get_cmd(args: dict):
    """
    Execute 'get' command
    """
    switch = {
        'source': get_source,
        'sources': get_sources,
        'dataset': get_dataset,
        'datasets': get_datasets,
        'model': get_model,
        'models': get_models,
        'tasks': get_tasks,
        'task': get_task,
        'algorithms': get_algorithms,
        'algorithm': get_algorithm
    }
    subject = get_args_or_prompt_list(
        arg_name='subject',
        args=args,
        message='Which prescience object do you want to get ?',
        choices_function=lambda: list(switch.keys())
    )
    switch[subject](args)

def config_get(args: dict):
    """
    Execute 'config get' command
    """
    output = args.get('output')
    prescience.config().show(output)

def config_add(args: dict):
    """
    Execute 'config get' command
    """
    prescience.config().set_project(args.get('project'), args.get('token'))

def get_args_or_prompt_list(
        arg_name: str,
        args: dict,
        message: str,
        choices_function: Callable,
        force_interactive: bool = False
):
    arg_value = args.get(arg_name)
    if arg_value is None or force_interactive:
        questions = [
            {
                'type': 'list',
                'name': arg_name,
                'message': message,
                'choices': choices_function()
            }
        ]
        answers = prompt(questions)
        arg_value = answers.get(arg_name)
    return arg_value

def get_args_or_prompt_checkbox(
        arg_name: str,
        args: dict,
        message: str,
        choices_function: Callable,
        selected_function: Callable = lambda: [],
        force_interactive: bool = False
):
    arg_value = args.get(arg_name)
    if arg_value is None or force_interactive:
        selected = selected_function()
        questions = [
            {
                'type': 'checkbox',
                'name': arg_name,
                'message': message,
                'choices': [{'name': x, 'checked': x in selected} for x in choices_function()]
            }
        ]
        answers = prompt(questions)
        arg_value = answers.get(arg_name)
    return arg_value

def get_args_or_prompt_confirm(
        arg_name: str,
        args: dict,
        message: str,
        force_interactive: bool = False
):
    arg_value = args.get(arg_name)
    if arg_value is None or force_interactive:
        question = {
            'type': 'confirm',
            'name': arg_name,
            'message': message,
        }
        if arg_value is True or arg_value is False:
            question['default'] = arg_value
        answers = prompt([question])
        arg_value = answers.get(arg_name)
    return arg_value

def get_args_or_prompt_input(
        arg_name: str,
        args: dict,
        message: str,
        force_interactive: bool = False
):
    arg_value = args.get(arg_name)
    if arg_value is None or force_interactive:
        questions = [
            {
                'type': 'input',
                'name': arg_name,
                'message': message,
            }
        ]
        answers = prompt(questions)
        arg_value = answers.get(arg_name)
    return arg_value


def config_switch(args: dict):
    """
    Execute 'config switch' command
    """
    project = get_args_or_prompt_list(
        arg_name='project',
        args=args,
        message='Which project do you want to switch on ?',
        choices_function=prescience.config().get_all_projects_names
    )
    prescience.config().set_current_project(project_name=project)

def start_parse(args: dict):
    """
    Execute 'start parse' command
    """
    interactive_mode = args.get('source-id') is None
    filepath = get_args_or_prompt_input(
        arg_name='input_filepath',
        args=args,
        message='Please indicate the path on your local file you want to parse',
        force_interactive=interactive_mode
    )
    has_headers = get_args_or_prompt_confirm(
        arg_name='headers',
        args=args,
        message='Does your csv file has a header row ?',
        force_interactive=interactive_mode
    )
    source_id = get_args_or_prompt_input(
        arg_name='source-id',
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
    input_local_file = prescience.csv_local_file_input(filepath=filepath, headers=has_headers)
    parse_task = input_local_file.parse(source_id=source_id)
    if watch:
        parse_task.watch()

def start_preprocess(args: dict):
    """
    Execute 'start preprocess' command
    """
    interactive_mode = args.get('source-id') is None
    source_id = get_args_or_prompt_list(
        arg_name='id',
        args=args,
        message='Which source do you want to preprocess ?',
        choices_function=lambda: [x.source_id for x in prescience.sources(page=1).content],
        force_interactive=interactive_mode
    )
    selected_columns = get_args_or_prompt_checkbox(
        arg_name='columns',
        args=args,
        message='Select the columns you want to keep for your preprocessing',
        choices_function=lambda: [x.name() for x in prescience.source(source_id).schema().fields()],
        selected_function=lambda: [x.name() for x in prescience.source(source_id).schema().fields()],
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
    task = prescience.preprocess(
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


def start_evaluation(args: dict):
    interactive_mode = args.get('dataset-id') is None
    dataset_id = get_args_or_prompt_list(
        arg_name='dataset-id',
        args=args,
        message='Which dataset do you want to launch an evaluation on ?',
        choices_function=lambda: [x.dataset_id() for x in prescience.datasets(page=1).content],
        force_interactive=interactive_mode
    )
    interactive_mode = interactive_mode or args.get('custom-config') is None
    if not interactive_mode:
        prescience_config = Config(json_dict=json.loads(args.get('custom-config')))
    else:
        # Use interactive mode to create the configuration
        dataset = prescience.dataset(dataset_id=dataset_id)
        all_config_list = dataset.get_associated_algorithm()
        choice_function = lambda: UtilList(all_config_list).flat_map(lambda x: x.get_algorithm_list_names()).value
        algo_id = get_args_or_prompt_list(
            arg_name='algo_id',
            args=args,
            message='Which algorithm ID do you want to get ?',
            choices_function=choice_function
        )
        algorithm = UtilList(all_config_list)\
            .map(lambda x: x.get_algorithm(algo_id))\
            .find(lambda x: x is not None)\
            .get_or_else(None)

        prescience_config = algorithm.interactive_kwargs_instanciation()
    watch = get_args_or_prompt_confirm(
        arg_name='watch',
        args=args,
        message='Do you want to keep watching for the task until it ends ?',
        force_interactive=interactive_mode
    )
    print(json.dumps(prescience_config.to_dict()))
    task = prescience.custom_config(dataset_id=dataset_id, config=prescience_config)
    if watch:
        task.watch()

def start_optimize(args: dict):
    """
    Execute 'start optimize' command
    """
    interactive_mode = args.get('dataset-id') is None
    dataset_id = get_args_or_prompt_list(
        arg_name='dataset-id',
        args=args,
        message='Which dataset do you want to preprocess ?',
        choices_function=lambda: [x.dataset_id() for x in prescience.datasets(page=1).content],
        force_interactive=interactive_mode
    )
    budget = get_args_or_prompt_input(
        arg_name='budget',
        args=args,
        message='Which budget do you want to allow on optimization ?',
        force_interactive=interactive_mode
    )
    # scoring_metric = args.get('scoring-metric')
    scoring_metric = get_args_or_prompt_list(
        arg_name='scoring-metric',
        args=args,
        message='On which scoring metric do you want to optimize on ?',
        choices_function=lambda: list(map(str, ScoringMetric)),
        force_interactive=interactive_mode
    )
    if interactive_mode and prescience.dataset(dataset_id).problem_type() == ProblemType.TIME_SERIES_FORECAST:
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
    task = prescience.optimize(
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

def start_train(args: dict):
    """
    Execute 'start train' command
    """
    evaluation_result_uuid = args['uuid']
    model_id = args['model-id']
    watch = args['watch']
    task = prescience.train(evaluation_uuid=evaluation_result_uuid, model_id=model_id)
    if watch:
        task.watch()

def start_retrain(args: dict):
    """
    Execute 'start train' command
    """
    file = args['input_filepath']
    model_id = args['model-id']
    watch = args['watch']
    task = prescience.retrain(model_id=model_id, filepath=file)
    if watch:
        task.watch()

def start_refresh(args: dict):
    """
    Execute 'start refresh dataset' command
    """
    file = args['input_filepath']
    dataset_id = args['dataset-id']
    watch = args['watch']
    task = prescience.refresh_dataset(dataset_id=dataset_id, filepath=file)
    if watch:
        task.watch()

def start_cmd(args: dict):
    """
    Execute 'start' command
    """
    switch = {
        'parse': start_parse,
        'preprocess': start_preprocess,
        'optimize': start_optimize,
        'train': start_train,
        'retrain': start_retrain,
        'refresh': start_refresh,
        'evaluation': start_evaluation
    }
    subject = get_args_or_prompt_list(
        arg_name='subject',
        args=args,
        message='Which prescience task do you want to start ?',
        choices_function=lambda: list(switch.keys())
    )
    switch[subject](args)

def config_cmd(args: dict):
    """
    Execute 'config' command
    """
    switch = {
        'get': config_get,
        'switch': config_switch,
        'add': config_add
    }
    command = get_args_or_prompt_list(
        arg_name='config_cmd',
        args=args,
        message='Which prescience command do you want to use on configuration ?',
        choices_function=lambda: list(switch.keys())
    )
    switch[command](args)

def delete_cmd(args: dict):
    """
    Execute 'delete' command
    """
    switch = {
        'source': delete_source,
        'dataset': delete_dataset,
        'model': delete_model
    }
    subject = get_args_or_prompt_list(
        arg_name='subject',
        args=args,
        message='Which kind of prescience object do you want to delete ?',
        choices_function=lambda: list(switch.keys())
    )
    switch[subject](args)

def delete_source(args: dict):
    """
    Execute 'delete source' command
    """
    source_id = prompt_for_source_id_if_needed(args)
    prescience.delete_source(source_id=source_id)

def delete_dataset(args: dict):
    """
    Execute 'delete dataset' command
    """
    dataset_id = prompt_for_dataset_id_if_needed(args)
    prescience.delete_dataset(dataset_id=dataset_id)

def delete_model(args: dict):
    """
    Execute 'delete model' command
    """
    model_id = prompt_for_model_id_if_needed(args)
    prescience.delete_model(model_id=model_id)

def predict_cmd(args: dict):
    """
    Execute 'predict' command
    """
    model_id = args['model-id']
    validate = args['validate']
    payload_json = args['json']
    payload_dict = json.loads(payload_json)
    from prescience_client.bean.model import Model
    model = Model.new(model_id=model_id, prescience=prescience)
    payload = model.get_model_evaluation_payload(arguments=payload_dict)
    if validate:
        payload.show()
    else:
        result = payload.evaluate()
        result.show()

def prompt_for_model_id_if_needed(args: dict):
    return get_args_or_prompt_list(
        arg_name='id',
        args=args,
        message='Which model do you want to get ?',
        choices_function=lambda: [x.model_id() for x in prescience.models(page=1).content]
    )

def prompt_for_source_id_if_needed(args: dict):
    return get_args_or_prompt_list(
        arg_name='id',
        args=args,
        message='Which source do you want to get ?',
        choices_function=lambda: [x.source_id for x in prescience.sources(page=1).content]
    )

def prompt_for_dataset_id_if_needed(args: dict):
    return get_args_or_prompt_list(
        arg_name='id',
        args=args,
        message='Which dataset do you want to get ?',
        choices_function=lambda: [x.dataset_id() for x in prescience.datasets(page=1).content]
    )


def plot_source(args: dict):
    source_id = prompt_for_source_id_if_needed(args)
    kind = args.get('kind') or 'line'
    x = args.get('x')
    prescience.plot_source(source_id=source_id, x=x, block=True, kind=kind)


def plot_dataset(args: dict):
    dataset_id = prompt_for_dataset_id_if_needed(args)
    plot_train = args.get('plot_train') or True
    plot_test = args.get('plot_test') or True
    prescience.plot_dataset(dataset_id=dataset_id, block=True, plot_train=plot_train, plot_test=plot_test)


def plot_cmd(args: dict):
    """
    Execute 'plot' command
    """
    switch = {
        'source': plot_source,
        'dataset': plot_dataset
    }
    subject = get_args_or_prompt_list(
        arg_name = 'subject',
        args=args,
        message='Which kind of object do you want to plot on ?',
        choices_function=lambda: list(switch.keys())
    )
    switch[subject](args)

def print_logo():
    logo = """
  _____                    _                     
 |  __ \\                  (_)                    
 | |__) | __ ___  ___  ___ _  ___ _ __   ___ ___ 
 |  ___/ '__/ _ \\/ __|/ __| |/ _ \\ '_ \\ / __/ _ \\
 | |   | | |  __/\\__ \\ (__| |  __/ | | | (_|  __/
 |_|   |_|  \\___||___/\\___|_|\\___|_| |_|\\___\\___|
 
    """
    print(logo)

def main():
    """
    Main class, finding user filled values and launch wanted command
    """
    try:
        args = init_args()
        switch = {
            'get': get_cmd,
            'start': start_cmd,
            'config': config_cmd,
            'delete': delete_cmd,
            'predict': predict_cmd,
            'plot': plot_cmd
        }
        # If interactive mode, print prescience logo
        if args.get('cmd') is None:
            print_logo()

        cmd = get_args_or_prompt_list(
            arg_name='cmd',
            args=args,
            message='Which prescience command fo you want to use ?',
            choices_function=lambda: list(switch.keys())
        )
        switch[cmd](args)
        exit(0)

    except PrescienceException as exception:
        exception.print()
        exit(1)