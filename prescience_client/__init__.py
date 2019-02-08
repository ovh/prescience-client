# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

import argparse
import sys
import json
from typing import List

from prescience_client.client.prescience_client import PrescienceClient
from prescience_client.config.prescience_config import PrescienceConfig
from prescience_client.config.constants import DEFAULT_PROBLEM_TYPE, DEFAULT_SCORING_METRIC
from prescience_client.enum.problem_type import ProblemType
from prescience_client.enum.scoring_metric import ScoringMetric
from prescience_client.exception.prescience_client_exception import PrescienceException

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
    config_subparser.add_parser('get', help='Show information about specifics prescience objects')

    # config switch
    config_switch_parser = config_subparser.add_parser('switch', help='Change the currently selected prescience project')
    config_switch_parser.add_argument('project', type=str, default='default',  help='The project name you want to switch on')

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

    ## get sources
    sources_parser.add_argument('--page', type=int, default=1)
    ## get datasets
    datasets_parser.add_argument('--page', type=int, default=1)
    ## get models
    models_parser.add_argument('--page', type=int, default=1)
    ## get source
    source_parser.add_argument('id', type=str, default=None)
    source_parser.set_defaults(schema=False)
    source_parser.add_argument('--schema', action='store_true', help='Display the schema of the source')
    source_parser.add_argument('--download', type=str, default=None, help='Directory in which to download data files for this source')
    source_parser.set_defaults(cache=False)
    source_parser.add_argument('--cache', action='store_true', help='Cache the source data inside local cache directory')
    ## get dataset
    dataset_parser.add_argument('id', type=str, default=None)
    dataset_parser.set_defaults(schema=False)
    dataset_parser.set_defaults(eval=False)
    dataset_parser.add_argument('--schema', action='store_true', help='Display the schema of the dataset')
    dataset_parser.add_argument('--eval', action='store_true', help='Display the evaluation results of the dataset')
    dataset_parser.add_argument('--download-train', dest='download_train', type=str, default=None, help='Directory in which to download data files for this train dataset')
    dataset_parser.add_argument('--download-test', dest='download_test', type=str, default=None, help='Directory in which to download data files for this test dataset')
    dataset_parser.set_defaults(cache=False)
    dataset_parser.add_argument('--cache', action='store_true', help='Cache the dataset data inside local cache directory')
    # get model
    model_parser.add_argument('id', type=str, default=None)

    # start
    cmd_start_parser = subparsers.add_parser('start', help='Start a task on prescience')
    start_subparser = cmd_start_parser.add_subparsers(dest='subject')
    ## start parse
    parse_parser = start_subparser.add_parser('parse', help='Launch a parse task on prescience')
    parse_parser.add_argument('--no-headers', dest='headers', action='store_false', help='Indicates that there is no header line on the csv file')
    parse_parser.set_defaults(headers=True)
    parse_parser.set_defaults(watch=False)
    parse_parser.add_argument('--watch', action='store_true', help='Wait until the task ends and watch the progression')
    parse_parser.add_argument('input-filepath', type=str, help='Local input file to send and parse on prescience')
    parse_parser.add_argument('source-id', type=str, help='Identifier of your future source object')
    ## start preprocess
    preprocess_parser = start_subparser.add_parser('preprocess', help='Launch a preprocess task on prescience')
    preprocess_parser.add_argument('source-id', type=str, help='Identifier of the source object to use for preprocessing')
    preprocess_parser.add_argument('dataset-id', type=str, help='Identifier of your future dataset object')
    preprocess_parser.add_argument('label', type=str, help='Identifier of the column to predict')
    preprocess_parser.add_argument('--columns', type=List[str], help='Subset of columns to include in the dataset. (default: all)')
    preprocess_parser.add_argument('--problem-type', type=ProblemType, choices=list(ProblemType), help=f"Type of problem for the dataset (default: {DEFAULT_PROBLEM_TYPE})", default=DEFAULT_PROBLEM_TYPE)
    preprocess_parser.add_argument('--time-column', type=str, help='Identifier of the time column for time series. Only for forecasts problems.', default=None)
    preprocess_parser.add_argument('--watch', action='store_true', help='Wait until the task ends and watch the progression')
    preprocess_parser.set_defaults(watch=False, columns=None, time_column=None)
    ## start optimize
    optimize_parser = start_subparser.add_parser('optimize', help='Launch an optimize task on prescience')
    optimize_parser.add_argument('dataset-id', type=str, help='Dataset identifier to optimize on')
    optimize_parser.add_argument('budget', type=int, help='Budget to allow on optimization')
    optimize_parser.add_argument('--scoring-metric', choices=list(ScoringMetric), type=ScoringMetric, help='Scoring metric to optimize', default=DEFAULT_SCORING_METRIC)
    optimize_parser.set_defaults(watch=False)
    optimize_parser.add_argument('--watch', action='store_true', help='Wait until the task ends and watch the progression')
    ## start train
    train_parser = start_subparser.add_parser('train', help='Launch a train task on prescience')
    train_parser.add_argument('uuid', type=str, help='Chosen evaluation result uuid to train on')
    train_parser.add_argument('model-id', type=str, help='Identifier of your future model object')
    train_parser.set_defaults(watch=False)
    train_parser.add_argument('--watch', action='store_true', help='Wait until the task ends and watch the progression')

    ## start retrain
    retrain_parser = start_subparser.add_parser('retrain', help='Launch a retrain task on prescience')
    retrain_parser.add_argument('--watch', action='store_true', help='Wait until the task ends and watch the progression')
    retrain_parser.add_argument('model-id', type=str, help='Model to retrain')
    retrain_parser.add_argument('input-filepath', type=str, help='Local input file to send in order to retrain the model on prescience')

    ## start refresh dataset
    retrain_parser = start_subparser.add_parser('refresh', help='Launch a refresh dataset task on prescience')
    retrain_parser.add_argument('--watch', action='store_true', help='Wait until the task ends and watch the progression')
    retrain_parser.add_argument('dataset-id', type=str, help='Dataset to refresh')
    retrain_parser.add_argument('input-filepath', type=str, help='Local input file/directory to send in order to refresh the dataset on prescience')

    # predict
    cmd_predict_parser = subparsers.add_parser('predict', help='Make prediction(s) from a presience model')
    cmd_predict_parser.add_argument('model-id', type=str, help='Identifier if the source object to delete')
    cmd_predict_parser.add_argument('--json', type=str, default='{}', help='All arguments to send as input of prescience model (in json format)')
    cmd_predict_parser.set_defaults(validate=False)
    cmd_predict_parser.add_argument('--validate', action='store_true', help='Validate the prediction request and don\'t send it')

    # delete
    cmd_delete_parser = subparsers.add_parser('delete', help='Delete a prescience object')
    delete_subparser = cmd_delete_parser.add_subparsers(dest='subject')
    ## delete source
    delete_source_parser = delete_subparser.add_parser('source', help='Delete a prescience source object')
    delete_source_parser.add_argument('id', type=str, help='Identifier of the source object to delete')

    ## delete dataset
    delete_dataset_parser = delete_subparser.add_parser('dataset', help='Delete a prescience dataset object')
    delete_dataset_parser.add_argument('id', type=str, help='Identifier of the dataset object to delete')

    ## delete model
    delete_model_parser = delete_subparser.add_parser('model', help='Delete a prescience model object')
    delete_model_parser.add_argument('id', type=str, help='Identifier of the model object to delete')

    # plot
    cmd_plot_parser = subparsers.add_parser('plot', help='Plot a prescience object')
    plot_subparser = cmd_plot_parser.add_subparsers(dest='subject')

    ## plot source
    plot_source_parser = plot_subparser.add_parser('source', help='Plot a source data object')
    plot_source_parser.add_argument('id', type=str, help='Identifier of the source object')
    plot_source_parser.add_argument('--x', type=str, default=None, help='Plot the current source')
    plot_source_parser.add_argument('--kind', type=str, default='line', help='Kind of the plot figure. Default: line')

    ## plot dataset
    plot_dataset_parser = plot_subparser.add_parser('dataset', help='Plot a dataset data object')
    plot_dataset_parser.add_argument('id', type=str, help='Identifier of the source object')
    plot_dataset_parser.add_argument('--x', type=str, default=None, help='Plot the current source')
    plot_dataset_parser.add_argument('--kind', type=str, default='line', help='Kind of the plot figure. Default: line')
    plot_dataset_parser.set_defaults(test=False)
    plot_dataset_parser.add_argument('--test', action='store_true', help='Plot only the "test" part of the dataset and not the default "train" part')


    if len(sys.argv) == 1:
        if sys.stdin.isatty():
            parser.print_usage()
            sys.exit(2)

    args = vars(parser.parse_args())
    return args

def get_models(args: dict):
    """
    Show model list
    """
    page = args['page']
    prescience.models(page=page).show()

def get_model(args: dict):
    """
    Show single model
    """
    model_id = args['id']
    model = prescience.model(model_id)
    model.show()


def get_datasets(args: dict):
    """
    Show datasets list
    """
    page = args['page']
    prescience.datasets(page=page).show()

def get_dataset(args: dict):
    """
    Show single dataset
    """
    display_eval = args['eval']
    display_schema = args['schema']
    dataset_id = args['id']
    download_train_directory = args['download_train']
    download_test_directory = args['download_test']
    dataset = prescience.dataset(dataset_id)
    if display_eval:
        dataset.evaluation_results().show()
    elif display_schema:
        dataset.schema().show()
    elif download_train_directory is not None:
        prescience.download_dataset(dataset_id=dataset_id, output_directory=download_train_directory, test_part=False)
    elif download_test_directory is not None:
        prescience.download_dataset(dataset_id=dataset_id, output_directory=download_test_directory, test_part=True)
    else:
        dataset.show()

def get_sources(args: dict):
    """
    Show sources list
    """
    page = args['page']
    prescience.sources(page=page).show()

def get_source(args: dict):
    """
    Show single source
    """
    source_id = args['id']
    source = prescience.source(source_id)
    download_directory = args['download']
    cache = args['cache']
    if args['schema']:
        source.schema().show()
    elif download_directory is not None:
        prescience.download_source(source_id=source_id, output_directory=download_directory)
    elif cache:
        prescience.update_cache_source(source_id)
    else:
        source.show()


def get_cmd(args: dict):
    """
    Execute 'get' command
    """
    subject = args['subject']
    switch = {
        'source': get_source,
        'sources': get_sources,
        'dataset': get_dataset,
        'datasets': get_datasets,
        'model': get_model,
        'models': get_models
    }
    switch[subject](args)

def config_get(args: dict):
    """
    Execute 'config get' command
    """
    # Do nothing but make pylint happy
    args.get('', None)
    prescience.config().show()

def config_add(args: dict):
    """
    Execute 'config get' command
    """
    prescience.config().set_project(args['project'], args['token'])

def config_switch(args: dict):
    """
    Execute 'config switch' command
    """
    prescience.config().set_current_project(project_name=args['project'])

def start_parse(args: dict):
    """
    Execute 'start parse' command
    """
    filepath = args['input-filepath']
    has_headers = args['headers']
    watch = args['watch']
    source_id = args['source-id']
    input_local_file = prescience.csv_local_file_input(filepath=filepath, headers=has_headers)
    parse_task = input_local_file.parse(source_id=source_id)
    if watch:
        parse_task.watch()

def start_preprocess(args: dict):
    """
    Execute 'start preprocess' command
    """
    source_id = args['source-id']
    watch = args['watch']
    dataset_id = args['dataset-id']
    label = args['label']
    selected_columns = args['columns']
    time_column = args['time_column']
    problem_type = args['problem_type']
    source = prescience.source(source_id=source_id)
    task = source.preprocess(
        dataset_id=dataset_id,
        label=label,
        problem_type=problem_type,
        selected_columns=selected_columns,
        time_column=time_column
    )
    if watch:
        task.watch()

def start_optimize(args: dict):
    """
    Execute 'start optimize' command
    """
    dataset_id = args['dataset-id']
    budget = args['budget']
    scoring_metric = args['scoring_metric']
    watch = args['watch']
    dataset = prescience.dataset(dataset_id=dataset_id)
    task = dataset.optimize(budget=budget, scoring_metric=scoring_metric)
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
    file = args['input-filepath']
    model_id = args['model-id']
    watch = args['watch']
    task = prescience.retrain(model_id=model_id, filepath=file)
    if watch:
        task.watch()

def start_refresh(args: dict):
    """
    Execute 'start refresh dataset' command
    """
    file = args['input-filepath']
    dataset_id = args['dataset-id']
    watch = args['watch']
    task = prescience.refresh_dataset(dataset_id=dataset_id, filepath=file)
    if watch:
        task.watch()

def start_cmd(args: dict):
    """
    Execute 'start' command
    """
    subject = args['subject']
    switch = {
        'parse': start_parse,
        'preprocess': start_preprocess,
        'optimize': start_optimize,
        'train': start_train,
        'retrain': start_retrain,
        'refresh': start_refresh
    }
    switch[subject](args)

def config_cmd(args: dict):
    """
    Execute 'config' command
    """
    command = args['config_cmd']
    switch = {
        'get': config_get,
        'switch': config_switch,
        'add': config_add
    }
    switch[command](args)

def delete_cmd(args: dict):
    """
    Execute 'delete' command
    """
    subject = args['subject']
    switch = {
        'source': delete_source,
        'dataset': delete_dataset,
        'model': delete_model
    }
    switch[subject](args)

def delete_source(args: dict):
    """
    Execute 'delete source' command
    """
    source_id = args['id']
    prescience.delete_source(source_id=source_id)

def delete_dataset(args: dict):
    """
    Execute 'delete dataset' command
    """
    dataset_id = args['id']
    prescience.delete_dataset(dataset_id=dataset_id)

def delete_model(args: dict):
    """
    Execute 'delete model' command
    """
    model_id = args['id']
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


def plot_source(args: dict):
    source_id = args['id']
    kind = args['kind']
    x = args['x']
    prescience.plot_source(source_id=source_id, x=x, block=True, kind=kind)


def plot_dataset(args: dict):
    dataset_id = args['id']
    kind = args['kind']
    x = args['x']
    test = args['test']
    prescience.plot_dataset(dataset_id=dataset_id, x=x, block=True, kind=kind, plot_test=test)


def plot_cmd(args: dict):
    """
    Execute 'plot' command
    """
    subject = args['subject']
    switch = {
        'source': plot_source,
        'dataset': plot_dataset
    }
    switch[subject](args)


def main():
    """
    Main class, finding user filled values and launch wanted command
    """
    try:
        args = init_args()
        cmd = args['cmd']
        switch = {
            'get': get_cmd,
            'start': start_cmd,
            'config': config_cmd,
            'delete': delete_cmd,
            'predict': predict_cmd,
            'plot': plot_cmd
        }
        switch[cmd](args)
        exit(0)

    except PrescienceException as exception:
        exception.print()
        exit(1)