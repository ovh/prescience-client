# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

import json
import pycurl
import re
import urllib.parse
from io import BytesIO
import os

from progress.bar import ChargingBar
from websocket import create_connection

from com.ovh.mls.prescience.core.bean.config import Config
from com.ovh.mls.prescience.core.bean.project import Project
from com.ovh.mls.prescience.core.config.constants import DEFAULT_LABEL_NAME, DEFAULT_PROBLEM_TYPE
from com.ovh.mls.prescience.core.config.prescience_config import PrescienceConfig
from com.ovh.mls.prescience.core.enum.flow_type import FlowType
from com.ovh.mls.prescience.core.enum.input_type import InputType
from com.ovh.mls.prescience.core.enum.problem_type import ProblemType
from com.ovh.mls.prescience.core.enum.scoring_metric import ScoringMetric
from com.ovh.mls.prescience.core.enum.status import Status
from com.ovh.mls.prescience.core.enum.web_service import PrescienceWebService
from com.ovh.mls.prescience.core.exception.prescience_client_exception import PyCurlExceptionFactory, \
    HttpErrorExceptionFactory


class PrescienceClient(object):
    """
    Prescience HTTP client allowing us to interact directly with prescience api.
    Prescience API is describe here https://prescience-api.ai.ovh.net/
    """
    def __init__(self,
                 prescience_config: PrescienceConfig,
                 verbose: bool = True):
        self.prescience_config = prescience_config
        self.verbose = verbose

    def login(self):
        """
        Method used for login into prescience
        :return: The cookie token used to connect to the web-socket
        """
        _, _, cookie = self.__get(path='/session/login')
        return cookie['token']

    def config(self) -> PrescienceConfig:
        """
        Getter of the prescience configuration object
        :return: The prescience configuration object
        """
        return self.prescience_config

    def new_project_token(self) -> dict:
        """
        ADMIN ONLY METHOD
        This method needs admin right to be authorized on prescience server
        It allow you to create a new prescience project and give you back the bearer token for this project
        :return:
        """
        current_config = self.config()

        _, result, _ = self.__post(
            path='/project',
            call_type = PrescienceWebService.ADMIN_API,
            data={'name': current_config.get_current_project_name()}
        )
        return result

    def upload_source(self,
                      source_id: str,
                      input_type: InputType,
                      headers: bool,
                      filepath: str
                      ) -> 'Task':
        """
        Upload a local input file on prescience and launch a Parse Task on it for creating a source.
        :param source_id: The id that we want for the source
        :param input_type: The input type of the given local input file
        :param headers: Has the local input file headers ?
        :param filepath: The path of the local input file
        :return: The task object of the Parse Task
        """

        parse_input = {
            'source_id': source_id,
            'type': str(input_type),
            'headers': headers
        }

        multipart = [
            ('input', (pycurl.FORM_CONTENTS, json.dumps(parse_input), pycurl.FORM_CONTENTTYPE, 'application/json')),
            ('input-file', (pycurl.FORM_FILE, filepath))
        ]
        _, result, _ = self.__post(path='/ml/upload/source', multipart=multipart)

        from com.ovh.mls.prescience.core.bean.task import TaskFactory
        return TaskFactory.construct(result, self)

    def delete_source(self, source_id: str):
        """
        Delete a source from its ID
        :param source_id: The source ID
        """
        self.__delete(path=f'/source/{source_id}')

    def delete_dataset(self, dataset_id: str):
        """
        Delete a dataset from its ID
        :param dataset_id: The dataset ID
        """
        self.__delete(path=f'/dataset/{dataset_id}')

    def delete_model(self, model_id: str):
        """
        Delete a model from its ID
        :param model_id: The model ID
        """
        self.__delete(path=f'/model/{model_id}')

    def preprocess(
            self,
            source_id: str,
            dataset_id: str,
            label_id: str = DEFAULT_LABEL_NAME,
            problem_type: ProblemType = DEFAULT_PROBLEM_TYPE,
            selected_column: list = None,
            time_column: str = None,
            fold_size: int = -1
    ):
        """
        Launch a Preprocess Task from a Source for creating a Dataset
        :param source_id: The initial Source ID
        :param dataset_id: The id that we want for the Dataset
        :param label_id: The name of the Source column that we want to predict (the label)
        :param problem_type: The type of machine learning problem that we want to solve
        :return: The task object of the Preprocess Task
        """
        body = {
            'dataset_id': dataset_id,
            'label_id': label_id,
            'problem_type': str(problem_type)
        }

        if selected_column is not None:
            body['selected_columns'] = selected_column

        if time_column is not None:
            body['time_column_id'] = time_column

        if fold_size >= 0:
            body['fold_size'] = fold_size

        _, result, _ = self.__post(path=f'/ml/preprocess/{source_id}', data=body)
        from com.ovh.mls.prescience.core.bean.task import TaskFactory
        return TaskFactory.construct(result, self)

    def optimize(self,
                 dataset_id: str,
                 scoring_metric: ScoringMetric,
                 budget: int = None,
                 nb_fold: int = None,
                 optimization_method: str = None,
                 custom_parameter: dict = None
                 ) -> 'Task':
        """
        Launch an optimize task from a dataset object
        :param dataset_id: The Id of the initial dataset
        :param scoring_metric: The scoring metric that we want to optimize on
        :param budget: The budget to consume before stopping the optimization
        :return: The task object of the Optimize Task
        """

        optimize_input = {
            'scoring_metric': str(scoring_metric),
            'budget': budget,
            'nb_fold': nb_fold,
            'optimization_method': optimization_method,
            'custom_parameters': custom_parameter
        }

        _, result, _ = self.__post(
            path=f'/ml/optimize/{dataset_id}',
            data={k: v for k, v in optimize_input.items() if v is not None}  # Delete None value in dict
        )

        from com.ovh.mls.prescience.core.bean.task import TaskFactory
        return TaskFactory.construct(result, self)

    def custom_config(self,
                      dataset_id: str,
                      config: Config
                      ) -> 'Task':
        """
        Launch the evaluation of a single custom configuration from a dataset
        :param dataset_id: The initial dataset ID
        :param config: The custom configuration that we want to evaluate
        :return: The evaluation task
        """
        _, result, _ = self.__post(path=f'/ml/custom-config/{dataset_id}', data=config.json_dict)
        from com.ovh.mls.prescience.core.bean.task import TaskFactory
        return TaskFactory.construct(result, self)

    def train(self,
              evaluation_uuid: str,
              model_id: str,
              compute_shap_summary: bool = False,
              chain_metric_task: bool = True
              ) -> 'TrainTask':
        """
        Launch a train task from an evaluation result for creating a model
        :param evaluation_uuid: The initial evaluation result uuid
        :param model_id: The id that we want for the model
        :param compute_shap_summary: should chain the train task with a compute shap summary task ? (default: false)
        :param chain_metric_task: should chain the train task with a metric task ? (default: true)
        :return: The Train Task object
        """
        query_parameters = {
            'model_id': model_id,
            'evaluation_uuid': evaluation_uuid,
            'enable_shap_summary': compute_shap_summary,
            'chain_metric_task': chain_metric_task
        }
        _, result, _ = self.__post(path=f'/ml/train', query_parameters=query_parameters)
        from com.ovh.mls.prescience.core.bean.task import TaskFactory
        return TaskFactory.construct(result, self)

    def retrain(self,
                model_id: str,
                chain_metric_task: bool = True
                ) -> 'TrainTask':
        """
        Launch a Re-Train task on a model
        :param model_id: The initial model ID
        :param chain_metric_task: should chain the train task with a metric task ? (default: True)
        :return:
        """
        query_parameters = {
            'chain_metric_task': chain_metric_task
        }
        _, result, _ = self.__post(path=f'/ml/retrain/{model_id}', query_parameters=query_parameters)
        from com.ovh.mls.prescience.core.bean.task import TaskFactory
        return TaskFactory.construct(result, self)

    def interrupt(self,
                  task_id: str):
        """
        Interrupt a task on prescience
        :param task_id: The task ID to interrupt
        """
        _, _, _ = self.__post(path=f'/task/{task_id}/interrupt')

    def create_mask(self,
                    dataset_id: str,
                    mask_id: str,
                    selected_column: list) -> 'Dataset':
        """
        Create a Mask Dataset from a Dataset
        :param dataset_id: The initial Dataset ID
        :param mask_id: The new ID that we want to create for the Mask Dataset
        :param selected_column: The subset of the initial Dataset that we want to keep for the Mask Dataset
        :return: The new Mask Dataset
        """
        query_parameters = {'mask_id': mask_id}
        _, result, _ = self.__post(path=f'/dataset/mask/{dataset_id}', data=selected_column,
                                   query_parameters=query_parameters)

        from com.ovh.mls.prescience.core.bean.dataset import Dataset
        return Dataset(json=result, prescience=self)

    def refresh_dataset(self,
                        dataset_id: str) -> 'Task':
        """
        Launch a refresh task on a dataset
        :param dataset_id: The ID of the dataset we want to launch a refresh on
        :return: The refresh task object
        """
        _, result, _ = self.__post(path=f'/ml/refresh/{dataset_id}')
        from com.ovh.mls.prescience.core.bean.task import TaskFactory
        return TaskFactory.construct(result, self)

    def get_project(self):
        """
        Get the current prescience project we are working on
        :return: the current prescience project we are working on
        """
        _, project, _ = self.__get(path='/project')
        return Project(project)

    def tasks(self, page: int = 1):
        """
        Get the paginated list of prescience tasks for the current project
        :param page: The number of the page to get
        :return: the page object containing prescience tasks
        """
        query_parameters = {'page': page}
        _, page, _ = self.__get(path='/task', query_parameters=query_parameters)
        from com.ovh.mls.prescience.core.bean.task import Task
        from com.ovh.mls.prescience.core.bean.task import TaskFactory
        from com.ovh.mls.prescience.core.bean.page_result import PageResult
        return PageResult(json=page, clazz=Task, factory_method=TaskFactory.construct, prescience=self)

    def sources(self, page: int = 1):
        """
        Get the paginated list of created prescience sources for the current project
        :param page: The number of the page to get
        :return: the page object containing prescience sources
        """
        query_parameters = {'page': page}
        _, page, _ = self.__get(path='/source', query_parameters=query_parameters)
        from com.ovh.mls.prescience.core.bean.source import Source
        from com.ovh.mls.prescience.core.bean.page_result import PageResult
        return PageResult(page, Source, prescience=self)

    def source(self, source_id: str):
        """
        Get a single source from its ID
        :param source_id: The source ID
        :return: The source object
        """
        from com.ovh.mls.prescience.core.bean.source import Source
        _, source, _ = self.__get(path=f'/source/{source_id}')
        return Source(json_dict=source, prescience=self)

    def datasets(self, page: int = 1, source_id_filter: str = None):
        """
        Get the paginated list of prescience datasets for the current project
        :param page: The number of the page to get
        :param source_id_filter: The filter to use on source ID (default: None)
        :return: the page object containing prescience datasets
        """
        query_parameters = {'page': page}
        if source_id_filter is not None:
            query_parameters['source_id'] = source_id_filter
        _, page, _ = self.__get(path='/dataset', query_parameters=query_parameters)
        from com.ovh.mls.prescience.core.bean.page_result import PageResult
        from com.ovh.mls.prescience.core.bean.dataset import Dataset
        return PageResult(page, Dataset, prescience=self)

    def dataset(self, dataset_id: str):
        """
        Get a single dataset from its ID
        :param dataset_id: The dataset ID
        :return: The dataset object
        """
        _, source, _ = self.__get(path=f'/dataset/{dataset_id}')
        from com.ovh.mls.prescience.core.bean.dataset import Dataset
        return Dataset(json=source, prescience=self)

    def get_evaluation_results(self, dataset_id: str, page: int = 1) -> 'PageResult':
        """
        Get the paginated list of evaluation results
        :param dataset_id: The dataset ID
        :param page: The number of the page to get
        :return: the page object containing the evaluation results
        """
        query_parameters = {'dataset_id': dataset_id, 'page': page}
        _, page, _ = self.__get(path='/evaluation-result', query_parameters=query_parameters)
        from com.ovh.mls.prescience.core.bean.page_result import PageResult
        from com.ovh.mls.prescience.core.bean.evaluation_result import EvaluationResult
        return PageResult(page, EvaluationResult, prescience=self)

    def models(self, page: int = 1, dataset_id_filter: str = None):
        """
        Get the paginated list of models
        :param page: The number of the page to get
        :param dataset_id_filter: The filter to use on dataset ID (default: None)
        :return: the page object containing the models
        """
        query_parameters = {'page': page}
        if dataset_id_filter is not None:
            query_parameters['dataset_id'] = dataset_id_filter
        _, page, _ = self.__get(path='/model', query_parameters=query_parameters)
        from com.ovh.mls.prescience.core.bean.page_result import PageResult
        from com.ovh.mls.prescience.core.bean.model import Model
        return PageResult(page, Model, prescience=self)

    def model(self, model_id: str):
        """
        Get a single model from its ID
        :param model_id: The model ID
        :return: The model object
        """
        _, model, _ = self.__get(path=f'/model/{model_id}')
        from com.ovh.mls.prescience.core.bean.model import Model
        return Model(json=model, prescience=self)

    def download_source(self, source_id:str, output_directory: str):
        """
        Download all source related files into the given directory
        :param source_id: The source id to download
        :param output_directory: The output directory (will be created if it doesn't exist)
        """
        _, response, _ = self.__get(path=f'/download/source/{source_id}')

        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        for output in response:
            _, file, _ = self.__get(path=f'/download/source/{source_id}/{output}', accept='application/octet-stream')
            full_output_path = os.path.join(output_directory, output)
            with open(full_output_path, 'wb') as stream:
                stream.write(file)
                stream.close()

    def download_dataset(self, dataset_id:str, output_directory: str):
        """
        Download all dataset related files into the given directory
        :param dataset_id: The dataset id to download
        :param output_directory: The output directory (will be created if it doesn't exist)
        """
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        # Download train files
        _, all_train_files, _ = self.__get(path=f'/download/dataset/{dataset_id}/train')
        for output in all_train_files:
            _, file, _ = self.__get(path=f'/download/dataset/{dataset_id}/train/{output}', accept='application/octet-stream')
            full_output_path = os.path.join(output_directory, f'train-{output}')
            with open(full_output_path, 'wb') as stream:
                stream.write(file)
                stream.close()

        # Download test files
        _, all_test_files, _ = self.__get(path=f'/download/dataset/{dataset_id}/test')
        for output in all_test_files:
            _, file, _ = self.__get(path=f'/download/dataset/{dataset_id}/test/{output}', accept='application/octet-stream')
            full_output_path = os.path.join(output_directory, f'test-{output}')
            with open(full_output_path, 'wb') as stream:
                stream.write(file)
                stream.close()



    def __get(self, path: str, query_parameters: dict = None, accept: str='application/json'):
        """
        Generic HTTP GET call
        :param path: the http path to call
        :param query_parameters: The dict of query parameters, None if any
        :param accept: accept header
        :return: The tuple3 : (http response code, response content, cookie token)
        """
        return self.call(method='GET', path=path, query_parameters=query_parameters, accept=accept)

    def __post(self,
               path: str,
               data=None,
               multipart: list = None,
               query_parameters: dict = None,
               call_type: PrescienceWebService = PrescienceWebService.API):
        """
        Generic HTTP POST call
        :param path: the http path to call
        :param data: The body json data to send (as dict). None if any
        :param multipart: The list of multipart part to send. None of any
        :param query_parameters: The dict of query parameters, None if any
        :param call_type: The prescience web service called
        :return: The tuple3 : (http response code, response content, cookie token)
        """

        content_type = 'application/json'
        if multipart is not None:
            content_type = 'multipart/form-data'
        return self.call(
            method='POST',
            path=path,
            data=data,
            multipart=multipart,
            content_type=content_type,
            query_parameters=query_parameters,
            call_type=call_type
        )

    def __delete(self, path: str):
        """
        Generic HTTP DELETE call
        :param path: The http path to call
        """
        return self.call(
            method='DELETE',
            path=path,
            accept=''
        )

    def call(
            self,
            method: str,
            path: str,
            query_parameters: dict = None,
            data: dict = None,
            multipart: list = None,
            content_type: str='application/json',
            timeout_seconds: int=5,
            call_type: PrescienceWebService=PrescienceWebService.API,
            accept: str='application/json'
    ):
        """
        Generic HTTP call wrapper for pyCurl
        :param method: The HTTP method to call
        :param path: The path to call
        :param query_parameters: The dict of query parameters, None if any
        :param data: The body json data to send (as dict). None if any
        :param multipart: The list of multipart part to send. None of any
        :param content_type: The content type header to use (default: application/json)
        :param timeout_seconds: The timeout of the http request
        :param call_type: The prescience web service called
        :param accept: accept header
        :return: The tuple3 : (http response code, response content, cookie token)
        """
        switch = {
            PrescienceWebService.API:  f'{self.prescience_config.get_current_api_url()}{path}',
            PrescienceWebService.ADMIN_API: f'{self.prescience_config.get_current_admin_api_url()}{path}',
            PrescienceWebService.SERVING: f'{self.prescience_config.get_current_serving_url()}{path}'
        }
        complete_url = switch.get(call_type)

        if query_parameters is not None and len(query_parameters) != 0:
            encoded_parameter = urllib.parse.urlencode(query_parameters)
            complete_url = f'{complete_url}?{encoded_parameter}'

        buffer = BytesIO()

        http_headers = [
            f'Authorization: Bearer {self.prescience_config.get_current_token()}',
            f'Content-Type: {content_type}',
            f'User-Agent: OVH-Prescience-Python-Client'
        ]

        if accept != '':
            http_headers.append(f'accept: {accept}')

        curl = pycurl.Curl()
        curl.setopt(pycurl.TIMEOUT, timeout_seconds)
        curl.setopt(pycurl.URL, complete_url)
        curl.setopt(pycurl.HTTPHEADER, http_headers)
        curl.setopt(pycurl.CUSTOMREQUEST, method)

        if self.verbose:
            curl.setopt(pycurl.VERBOSE, 1)

        if data is not None:
            curl.setopt(pycurl.POSTFIELDS, json.dumps(data))

        if multipart is not None:
            curl.setopt(pycurl.HTTPPOST, multipart)

        curl.setopt(pycurl.WRITEDATA, buffer)

        # Catch token cookie if any
        cookie_token = []

        # closure to capture Set-Cookie
        def _catch_cookie_token(header):
            match = re.match("^Set-Cookie: .*token=(.+?);.*$", header.decode("utf-8"))
            if match:
                cookie_token.append(('token', match.group(1)))

        # use closure to collect cookies sent from the server
        curl.setopt(pycurl.HEADERFUNCTION, _catch_cookie_token)

        try:
            curl.perform()
        except pycurl.error as error:
            prescience_error = PyCurlExceptionFactory.construct(error)
            self.config().handle_exception(prescience_error)

        status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        response_content = buffer.getvalue()
        if accept != 'application/octet-stream':
            response_content = response_content.decode('UTF-8')

        curl.close()

        if status_code // 100 != 2:
            prescience_error =  HttpErrorExceptionFactory.construct(status_code, response_content)
            self.config().handle_exception(prescience_error)
        else:
            if accept == 'application/json':
                json_response = json.loads(response_content)
                if self.verbose:
                    print(f'[{status_code}] {json_response}')
                return status_code, json_response, dict(cookie_token)
            else:
                return status_code, response_content, dict(cookie_token)

    ############################################
    ############### SERVING METHODS ############
    ############################################

    def serving_model_evaluator(self, model_id: str):
        """
        Access the evaluator of a model on prescience-serving api
        :param model_id: The id of the model
        :return: The answered json dictionary for the evaluator
        """
        _, result, _ = self.call(
            method='GET',
            path=f'/evaluator/{model_id}',
            call_type=PrescienceWebService.SERVING
        )
        return result

    def serving_model_evaluate(self,
                               model_id: str,
                               flow_type: FlowType,
                               request_data):
        """
        Evaluate a model from a single request
        :param model_id: The id of the model to evaluate
        :param flow_type: The flow type of the evaluation
        :param request_data: The json dictionary or list of dictionary containing evaluation parameters
        :return: The json dictionary of the answer
        """
        path = f'/eval/{model_id}/{str(flow_type)}'
        if isinstance(request_data, list):
            path = f'/eval/{model_id}/{str(flow_type)}/batch/json'

        _, result, _ = self.call(
            method='POST',
            path=path,
            call_type=PrescienceWebService.SERVING,
            data=request_data
        )
        return result

    ############################################
    ########### WEB-SOCKET METHODS #############
    ############################################

    def __init_ws_connection(self):
        """
        Initialize the web-socket connection :
        - Log into prescience with the configured Bearer token for getting the cookie token
        - Create the web-socket connection with the previous cookie token
        :return: The web-socket connection
        """
        token = self.login()
        ws = create_connection(self.prescience_config.get_current_websocket_url(), cookie=f'token={token}')
        ws.send('')
        return ws

    # Wait for the next message related to the given task
    def __wait_for_task_message(self, ws, initial_task: 'Task'):
        """
        Wait until the next related task
        :param ws: The web socket connection
        :param initial_task: the initial task
        :return: The related task catch from WS connection
        """
        task_message = None
        while task_message is None or task_message.uuid() != initial_task.uuid() or task_message.type() != initial_task.type():
            rcv_message = ws.recv()
            message = json.loads(rcv_message)['entity']
            from com.ovh.mls.prescience.core.bean.task import TaskFactory
            task_message = TaskFactory.construct(message, self)

        return task_message

    def wait_for_task_done_or_error(self, initial_task: 'Task'):
        """
        Wait until the given task is DONE or ERROR
        :param initial_task:
        :return: The last state of the Task
        """
        # Initialize web-socket connection
        websocket = self.__init_ws_connection()
        current_task = initial_task
        bar = ChargingBar(current_task.type(), max=current_task.total_step())
        bar.next(0)
        if current_task.current_step_description() is not None:
            bar.message = current_task.current_step_description()
        while current_task.status() != Status.DONE and current_task.status() != Status.ERROR:
            current_task = self.__wait_for_task_message(websocket, initial_task)
            bar.next()
            bar.message = current_task.current_step_description()
        bar.finish()
        # Closing web-socket
        websocket.close()
        return current_task

    ############################################
    ############### FACTORY METHODS ############
    ############################################

    def csv_local_file_input(self, filepath: str, headers: bool = True) -> 'CsvLocalFileInput':
        """
        Create a csv local input file
        :param filepath: The path of your csv
        :param headers: Does the csv file has header ? (default: True)
        :return: The CsvLocalFileInput object
        """
        from com.ovh.mls.prescience.core.bean.entity.local_file_input import CsvLocalFileInput
        return CsvLocalFileInput(filepath=filepath, headers=headers, prescience=self)
