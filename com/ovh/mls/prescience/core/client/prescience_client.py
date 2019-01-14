# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

import json
import pycurl
import re
import urllib.parse
from io import BytesIO

from progress.bar import ChargingBar
from websocket import create_connection

from com.ovh.mls.prescience.core.bean.config import Config
from com.ovh.mls.prescience.core.bean.project import Project
from com.ovh.mls.prescience.core.config.constants import DEFAULT_LABEL_NAME, DEFAULT_PROBLEM_TYPE
from com.ovh.mls.prescience.core.config.prescience_config import PrescienceConfig
from com.ovh.mls.prescience.core.enum.input_type import InputType
from com.ovh.mls.prescience.core.enum.problem_type import ProblemType
from com.ovh.mls.prescience.core.enum.scoring_metric import ScoringMetric
from com.ovh.mls.prescience.core.enum.status import Status


class PrescienceClient(object):
    def __init__(self,
                 prescience_config: PrescienceConfig,
                 verbose: bool = True):
        self.prescience_config = prescience_config
        self.verbose = verbose

    def login(self):
        _, _, cookie = self.get(path='/session/login')
        return cookie['token']

    def config(self) -> PrescienceConfig:
        return self.prescience_config

    def upload_source(self,
                      source_id: str,
                      input_type: InputType,
                      headers: bool,
                      filepath: str
                      ) -> 'Task':

        parse_input = {
            'source_id': source_id,
            'type': str(input_type),
            'headers': headers
        }

        multipart = [
            ('input', (pycurl.FORM_CONTENTS, json.dumps(parse_input), pycurl.FORM_CONTENTTYPE, 'application/json')),
            ('input-file', (pycurl.FORM_FILE, filepath))
        ]
        _, result, _ = self.post(path='/ml/upload/source', multipart=multipart)

        from com.ovh.mls.prescience.core.bean.task import TaskFactory
        return TaskFactory.construct(result, self)

    def delete_source(self, source_id: str):
        self.delete(path=f'/source/{source_id}')

    def delete_dataset(self, dataset_id: str):
        self.delete(path=f'/dataset/{dataset_id}')

    def delete_model(self, model_id: str):
        self.delete(path=f'/model/{model_id}')

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

        _, result, _ = self.post(path=f'/ml/preprocess/{source_id}', data=body)
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

        optimize_input = {
            'scoring_metric': str(scoring_metric),
            'budget': budget,
            'nb_fold': nb_fold,
            'optimization_method': optimization_method,
            'custom_parameters': custom_parameter
        }

        _, result, _ = self.post(
            path=f'/ml/optimize/{dataset_id}',
            data={k: v for k, v in optimize_input.items() if v is not None}  # Delete None value in dict
        )

        from com.ovh.mls.prescience.core.bean.task import TaskFactory
        return TaskFactory.construct(result, self)

    def custom_config(self,
                      dataset_id: str,
                      config: Config
                      ) -> 'Task':
        _, result, _ = self.post(path=f'/ml/custom-config/{dataset_id}', data=config.json_dict)
        from com.ovh.mls.prescience.core.bean.task import TaskFactory
        return TaskFactory.construct(result, self)

    def train(self,
              evaluation_uuid: str,
              model_id: str,
              compute_shap_summary: bool = False,
              chain_metric_task: bool = True
              ) -> 'TrainTask':
        query_parameters = {
            'model_id': model_id,
            'evaluation_uuid': evaluation_uuid,
            'enable_shap_summary': compute_shap_summary,
            'chain_metric_task': chain_metric_task
        }
        _, result, _ = self.post(path=f'/ml/train', query_parameters=query_parameters)
        from com.ovh.mls.prescience.core.bean.task import TaskFactory
        return TaskFactory.construct(result, self)

    def retrain(self,
                model_id: str,
                chain_metric_task: bool = True
                ) -> 'TrainTask':
        query_parameters = {
            'chain_metric_task': chain_metric_task
        }
        _, result, _ = self.post(path=f'/ml/retrain/{model_id}', query_parameters=query_parameters)
        from com.ovh.mls.prescience.core.bean.task import TaskFactory
        return TaskFactory.construct(result, self)

    def interrupt(self,
                  task_id: str):
        _, _, _ = self.post(path=f'/task/{task_id}/interrupt')

    def create_mask(self,
                    dataset_id: str,
                    mask_id: str,
                    selected_column: list) -> 'Dataset':
        query_parameters = {'mask_id': mask_id}
        _, result, _ = self.post(path=f'/dataset/mask/{dataset_id}', data=selected_column,
                                 query_parameters=query_parameters)

        from com.ovh.mls.prescience.core.bean.dataset import Dataset
        return Dataset(json=result, prescience=self)

    def refresh_dataset(self,
                        dataset_id: str) -> 'Task':

        _, result, _ = self.post(path=f'/ml/refresh/{dataset_id}')
        from com.ovh.mls.prescience.core.bean.task import TaskFactory
        return TaskFactory.construct(result, self)

    def get_project(self):
        _, project, _ = self.get(path='/project')
        return Project(project)

    def tasks(self, page: int = 1):
        query_parameters = {'page': page}
        _, page, _ = self.get(path='/task', query_parameters=query_parameters)
        from com.ovh.mls.prescience.core.bean.task import Task
        from com.ovh.mls.prescience.core.bean.task import TaskFactory
        from com.ovh.mls.prescience.core.bean.page_result import PageResult
        return PageResult(json=page, clazz=Task, factory_method=TaskFactory.construct, prescience=self)

    def sources(self, page: int = 1):
        query_parameters = {'page': page}
        _, page, _ = self.get(path='/source', query_parameters=query_parameters)
        from com.ovh.mls.prescience.core.bean.source import Source
        from com.ovh.mls.prescience.core.bean.page_result import PageResult
        return PageResult(page, Source, prescience=self)

    def source(self, source_id: str):
        from com.ovh.mls.prescience.core.bean.source import Source
        _, source, _ = self.get(path=f'/source/{source_id}')
        return Source(json_dict=source, prescience=self)

    def datasets(self, page: int = 1, source_id_filter: str = None):
        query_parameters = {'page': page}
        if source_id_filter is not None:
            query_parameters['source_id'] = source_id_filter
        _, page, _ = self.get(path='/dataset', query_parameters=query_parameters)
        from com.ovh.mls.prescience.core.bean.page_result import PageResult
        from com.ovh.mls.prescience.core.bean.dataset import Dataset
        return PageResult(page, Dataset, prescience=self)

    def dataset(self, dataset_id: str):
        _, source, _ = self.get(path=f'/dataset/{dataset_id}')
        from com.ovh.mls.prescience.core.bean.dataset import Dataset
        return Dataset(json=source, prescience=self)

    def get_evaluation_results(self, dataset_id: str, page: int = 1) -> 'PageResult':
        query_parameters = {'dataset_id': dataset_id, 'page': page}
        _, page, _ = self.get(path='/evaluation-result', query_parameters=query_parameters)
        from com.ovh.mls.prescience.core.bean.page_result import PageResult
        from com.ovh.mls.prescience.core.bean.evaluation_result import EvaluationResult
        return PageResult(page, EvaluationResult, prescience=self)

    def models(self, page: int = 1, dataset_id_filter: str = None):
        query_parameters = {'page': page}
        if dataset_id_filter is not None:
            query_parameters['dataset_id'] = dataset_id_filter
        _, page, _ = self.get(path='/model', query_parameters=query_parameters)
        from com.ovh.mls.prescience.core.bean.page_result import PageResult
        from com.ovh.mls.prescience.core.bean.model import Model
        return PageResult(page, Model, prescience=self)

    def model(self, model_id: str):
        _, model, _ = self.get(path=f'/model/{model_id}')
        from com.ovh.mls.prescience.core.bean.model import Model
        return Model(json=model, prescience=self)

    def get(self, path: str, query_parameters: dict = None):
        return self.call(method='GET', path=path, query_parameters=query_parameters)

    def post(self,
             path: str,
             data=None,
             multipart: list = None,
             query_parameters: dict = None):

        content_type = 'application/json'
        if multipart is not None:
            content_type = 'multipart/form-data'
        return self.call(
            method='POST',
            path=path,
            data=data,
            multipart=multipart,
            content_type=content_type,
            query_parameters=query_parameters
        )

    def delete(self, path: str):
        return self.call(
            method='DELETE',
            path=path,
            expect_json_response=False
        )

    def call(
            self,
            method: str,
            path: str,
            query_parameters: dict = None,
            data: dict = None,
            multipart: list = None,
            content_type='application/json',
            expect_json_response=True,
            timeout_seconds=20
    ):

        complete_url = f'{self.prescience_config.get_current_api_url()}{path}'
        if query_parameters is not None and len(query_parameters) != 0:
            encoded_parameter = urllib.parse.urlencode(query_parameters)
            complete_url = f'{complete_url}?{encoded_parameter}'

        buffer = BytesIO()

        curl = pycurl.Curl()
        curl.setopt(pycurl.TIMEOUT, timeout_seconds)
        curl.setopt(pycurl.URL, complete_url)
        curl.setopt(pycurl.HTTPHEADER, [
            f'Authorization: Bearer {self.prescience_config.get_current_token()}',
            f'Content-Type: {content_type}',
            'accept: application/json'
        ])
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

        curl.perform()

        status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        response_content = buffer.getvalue().decode('UTF-8')

        curl.close()

        if status_code // 100 != 2:
            raise RuntimeError(str(status_code) + response_content)
        else:
            if expect_json_response:
                json_response = json.loads(response_content)
                if self.verbose:
                    print(f'[{status_code}] {json_response}')
                return status_code, json_response, dict(cookie_token)
            else:
                return status_code, response_content, dict(cookie_token)

    ############################################
    ########### WEB-SOCKET METHODS #############
    ############################################

    def init_ws_connection(self):
        token = self.login()
        ws = create_connection(self.prescience_config.get_current_websocket_url(), cookie=f'token={token}')
        ws.send('')
        return ws

    # Wait for the next message related to the given task
    def wait_for_task_message(self, ws, initial_task: 'Task'):
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
        websocket = self.init_ws_connection()
        current_task = initial_task
        bar = ChargingBar(current_task.type(), max=current_task.total_step())
        bar.next(0)
        if current_task.current_step_description() is not None:
            bar.message = current_task.current_step_description()
        while current_task.status() != Status.DONE and current_task.status() != Status.ERROR:
            current_task = self.wait_for_task_message(websocket, initial_task)
            bar.next()
            bar.message = current_task.current_step_description()
        bar.finish()
        # Closing web-socket
        websocket.close()
        return current_task

    ############################################
    ############### SHOW METHODS ###############
    ############################################

    def show_sources(self, page: int = 1):
        self.sources(page=page).show()

    def show_datasets(self, page: int = 1):
        self.datasets(page=page).show()

    def show_tasks(self, page: int = 1):
        self.tasks(page=page).show()

    ############################################
    ############### FACTORY METHODS ############
    ############################################

    def csv_local_file_input(self, filepath: str, headers: bool = True) -> 'CsvLocalFileInput':
        from com.ovh.mls.prescience.core.bean.entity.local_file_input import CsvLocalFileInput
        return CsvLocalFileInput(filepath=filepath, headers=headers, prescience=self)
