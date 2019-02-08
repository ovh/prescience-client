# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

import json
import shutil
import unittest
import tempfile
import os

import pycurl

from prescience_client.bean.evaluation_result import EvaluationResult
from prescience_client.bean.model import Model
from prescience_client.bean.dataset import Dataset
from prescience_client.bean.task import ParseTask, PreprocessTask
from prescience_client.bean.source import Source
from prescience_client.client.prescience_client import PrescienceClient
from prescience_client.config.prescience_config import PrescienceConfig
from prescience_client.enum.problem_type import ProblemType
from prescience_client.enum.scoring_metric import ScoringMetric
from prescience_client.enum.status import Status
from prescience_client.enum.web_service import PrescienceWebService
from tests.utils import get_resource_file_path
from unittest.mock import MagicMock


class TestPrescienceClient(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory
        self.config_path = tempfile.mkdtemp()
        self.config_file = 'config.yaml'
        self.config_fil_full_path = os.path.join(self.config_path, self.config_file)
        self.config_content = open(get_resource_file_path('default-config.yaml')).read()
        with open(self.config_fil_full_path, 'w') as stream:
            stream.write(self.config_content)

        # Creating prescience config
        self.prescience_config = PrescienceConfig(config_path=self.config_path, config_file=self.config_file)
        # Loading configuration
        self.prescience_config.load()
        # Creating prescience client
        self.presience_client = PrescienceClient(prescience_config=self.prescience_config)


    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.config_path)


    def test_get_sources(self):
        """
        Test the access of sources list
        """
        # Init
        output = {
            'metadata': {
                'page_number': 2,
                'total_pages': 2,
                'elements_on_page': 1,
                'elements_total': 1,
                'elements_type': 'Source'
            },
            'content': [{
                'source_id': 'my-source-id'
            }]
        }
        self.presience_client.call = MagicMock(return_value=(200, output, {}))

        # Test 1
        all_sources = self.presience_client.sources()
        self.presience_client.call.assert_called_with(method='GET', path='/source', query_parameters= {'page': 1}, accept='application/json')
        self.assertEqual(2, all_sources.metadata.page_number)
        self.assertEqual(2, all_sources.metadata.total_pages)
        self.assertEqual(1, all_sources.metadata.elements_on_page)
        self.assertEqual(1, all_sources.metadata.elements_total)
        self.assertEqual('Source', all_sources.metadata.elements_type)
        self.assertEqual(1, len(all_sources.content), 'Page containing only 1 source result')
        self.assertEqual('my-source-id', all_sources.content[0].source_id)

        # Test 2
        self.presience_client.sources(page=2)
        self.presience_client.call.assert_called_with(method='GET', path='/source', query_parameters={'page': 2}, accept='application/json')


    def test_get_datasets(self):
        """
        Test the access of datasets list
        """
        # Init
        output = {
            'metadata': {
                'page_number': 2,
                'total_pages': 2,
                'elements_on_page': 1,
                'elements_total': 1,
                'elements_type': 'Dataset'
            },
            'content': [{
                'dataset_id': 'my-dataset-id'
            }]
        }
        self.presience_client.call = MagicMock(return_value=(200, output, {}))

        # Test 1
        all_datasets = self.presience_client.datasets()
        self.presience_client.call.assert_called_with(method='GET', path='/dataset', query_parameters= {'page': 1}, accept='application/json')
        self.assertEqual(2, all_datasets.metadata.page_number)
        self.assertEqual(2, all_datasets.metadata.total_pages)
        self.assertEqual(1, all_datasets.metadata.elements_on_page)
        self.assertEqual(1, all_datasets.metadata.elements_total)
        self.assertEqual('Dataset', all_datasets.metadata.elements_type)
        self.assertEqual(1, len(all_datasets.content), 'Page containing only 1 source result')
        self.assertEqual('my-dataset-id', all_datasets.content[0].dataset_id())

        # Test 2
        self.presience_client.datasets(page=2)
        self.presience_client.call.assert_called_with(method='GET', path='/dataset', query_parameters={'page': 2}, accept='application/json')

    def test_get_models(self):
        """
        Test the access of models list
        """
        # Init
        output = {
            'metadata': {
                'page_number': 2,
                'total_pages': 2,
                'elements_on_page': 1,
                'elements_total': 1,
                'elements_type': 'Model'
            },
            'content': [{
                'model_id': 'my-model-id'
            }]
        }
        self.presience_client.call = MagicMock(return_value=(200, output, {}))

        # Test 1
        all_models = self.presience_client.models()
        self.presience_client.call.assert_called_with(method='GET', path='/model', query_parameters={'page': 1}, accept='application/json')
        self.assertEqual(2, all_models.metadata.page_number)
        self.assertEqual(2, all_models.metadata.total_pages)
        self.assertEqual(1, all_models.metadata.elements_on_page)
        self.assertEqual(1, all_models.metadata.elements_total)
        self.assertEqual('Model', all_models.metadata.elements_type)
        self.assertEqual(1, len(all_models.content), 'Page containing only 1 source result')
        self.assertEqual('my-model-id', all_models.content[0].model_id())

        # Test 2
        self.presience_client.models(page=2)
        self.presience_client.call.assert_called_with(method='GET', path='/model', query_parameters={'page': 2}, accept='application/json')

        # Test 3
        self.presience_client.models(page=2, dataset_id_filter='my-dataset-id')
        self.presience_client.call.assert_called_with(method='GET', path='/model', query_parameters={'page': 2, 'dataset_id': 'my-dataset-id'}, accept='application/json')

    def test_get_evaluation_results(self):
        """
        Test the access of evaluation results from a dataset
        """
        # Init
        output = {
            'metadata': {
                'page_number': 2,
                'total_pages': 2,
                'elements_on_page': 1,
                'elements_total': 1,
                'elements_type': 'EvaluationResult'
            },
            'content': [{
                'uuid': 'azerty'
            }]
        }
        self.presience_client.call = MagicMock(return_value=(200, output, {}))
        dataset = Dataset(json={'dataset_id': 'my-dataset-id'}, prescience=self.presience_client)
        dataset.evaluation_results(page=2)
        self.presience_client.call.assert_called_with(
            method='GET',
            path='/evaluation-result',
            query_parameters={'dataset_id': 'my-dataset-id', 'page': 2},
            accept='application/json'
        )

    def test_get_tasks(self):
        """
        Test the access of prescience tasks
        """
        # Init
        output = {
            'metadata': {
                'page_number': 2,
                'total_pages': 2,
                'elements_on_page': 1,
                'elements_total': 1,
                'elements_type': 'Task'
            },
            'content': [{
                'uuid': 'azerty'
            }]
        }
        self.presience_client.call = MagicMock(return_value=(200, output, {}))
        self.presience_client.tasks(page=2)
        self.presience_client.call.assert_called_with(
            method='GET',
            path='/task',
            query_parameters={'page': 2},
            accept='application/json'
        )

    def test_get_single_source(self):
        """
        Test the access of a source
        """
        output = {'source_id': 'my-source-id'}
        self.presience_client.call = MagicMock(return_value=(200, output, {}))

        # Test 1
        my_source = self.presience_client.source('my-source-id')
        self.presience_client.call.assert_called_with(method='GET', path='/source/my-source-id', query_parameters=None, accept='application/json')
        self.assertEqual('my-source-id', my_source.source_id)

    def test_delete_single_source(self):
        """
        Test the deletion of a source
        """
        self.presience_client.call = MagicMock(return_value=(200, {}, {}))
        source = Source(json_dict={'source_id': 'my-source-id'}, prescience=self.presience_client)

        # Test 1
        source.delete()
        self.presience_client.call.assert_called_with(method='DELETE', path='/source/my-source-id', accept='')

    def test_get_single_dataset(self):
        """
        Test the access of a dataset
        """
        output = {'dataset_id': 'my-dataset-id'}
        self.presience_client.call = MagicMock(return_value=(200, output, {}))

        # Test 1
        my_dataset = self.presience_client.dataset('my-dataset-id')
        self.presience_client.call.assert_called_with(method='GET', path='/dataset/my-dataset-id', query_parameters=None, accept='application/json')
        self.assertEqual('my-dataset-id', my_dataset.dataset_id())

    def test_delete_single_dataset(self):
        """
        Test the deletion of a dataset
        """
        self.presience_client.call = MagicMock(return_value=(200, {}, {}))
        dataset = Dataset(json={'dataset_id': 'my-dataset-id'}, prescience=self.presience_client)

        # Test 1
        dataset.delete()
        self.presience_client.call.assert_called_with(method='DELETE', path='/dataset/my-dataset-id', accept='')

    def test_get_single_model(self):
        """
        Test the access of a model
        """
        output = {'model_id': 'my-model-id'}
        self.presience_client.call = MagicMock(return_value=(200, output, {}))

        # Test 1
        my_model = self.presience_client.model('my-model-id')
        self.presience_client.call.assert_called_with(method='GET', path='/model/my-model-id', query_parameters=None, accept='application/json')
        self.assertEqual('my-model-id', my_model.model_id())

    def test_delete_single_model(self):
        """
        Test the deletion of a model
        """
        self.presience_client.call = MagicMock(return_value=(200, {}, {}))
        model = Model(json={'model_id': 'my-model-id'}, prescience=self.presience_client)

        # Test 1
        model.delete()
        self.presience_client.call.assert_called_with(method='DELETE', path='/model/my-model-id', accept='')

    def test_parse(self):
        """
        Test the launch of a simple Parse
        """
        # Init
        output = {'uuid': 'parse-task-uuid', 'type': 'parse', 'status': 'PENDING'}
        self.presience_client.call = MagicMock(return_value=(200, output, {}))

        # Test
        csv_path = get_resource_file_path('test.csv')
        input_file = self.presience_client.csv_local_file_input(filepath=csv_path, headers=True)
        task = input_file.parse('my-source-id')
        self.assertEqual('parse-task-uuid', task.uuid())
        self.assertEqual('parse', task.type())
        self.assertIsInstance(task, ParseTask)
        self.assertEqual(Status.PENDING, task.status())

        expected_parse_payload = {'source_id': 'my-source-id','type': 'CSV', 'headers': True}
        self.presience_client.call.assert_called_with(
            method='POST',
            path='/ml/upload/source',
            content_type='multipart/form-data',
            multipart=[
                ('input', (pycurl.FORM_CONTENTS, json.dumps(expected_parse_payload), pycurl.FORM_CONTENTTYPE, 'application/json')),
                ('input-file', (pycurl.FORM_FILE, csv_path))
            ],
            data=None,
            query_parameters=None,
            call_type=PrescienceWebService.API
        )

    def test_preprocess(self):
        """
        Test the launch of a simple PreprocessTask
        """
        # Init
        output = {'uuid': 'preprocess-task-uuid', 'type': 'preprocess', 'status': 'PENDING'}
        self.presience_client.call = MagicMock(return_value=(200, output, {}))
        source = Source(json_dict={'source_id': 'my-source-id'}, prescience=self.presience_client)

        # Test
        preprocess_task = source.preprocess(
            dataset_id='my-dataset-id',
            label='my-label',
            problem_type=ProblemType.REGRESSION
        )
        self.assertEqual('preprocess-task-uuid', preprocess_task.uuid())
        self.assertEqual('preprocess', preprocess_task.type())
        self.assertIsInstance(preprocess_task, PreprocessTask)
        self.assertEqual(Status.PENDING, preprocess_task.status())

        self.presience_client.call.assert_called_with(
            method='POST',
            path='/ml/preprocess/my-source-id',
            content_type='application/json',
            data={'dataset_id': 'my-dataset-id', 'label_id': 'my-label', 'problem_type': 'regression'},
            multipart=None,
            query_parameters=None,
            call_type=PrescienceWebService.API
        )

    def test_optimize(self):
        """
        Test the launch of a simple OptimizeTask
        """
        # Init
        output = {'uuid': 'optimize-task-uuid', 'type': 'optimize', 'status': 'PENDING'}
        self.presience_client.call = MagicMock(return_value=(200, output, {}))
        dataset = Dataset(json={'dataset_id': 'my-dataset-id'}, prescience=self.presience_client)

        # Test
        optimize_task = dataset.optimize(budget=10, scoring_metric=ScoringMetric.ACCURACY)
        self.assertEqual('optimize-task-uuid', optimize_task.uuid())
        self.assertEqual('optimize', optimize_task.type())
        self.assertEqual(Status.PENDING, optimize_task.status())

        self.presience_client.call.assert_called_with(
            method='POST',
            path='/ml/optimize/my-dataset-id',
            content_type='application/json',
            data={'scoring_metric': 'accuracy', 'budget': 10},
            multipart=None,
            query_parameters=None,
            call_type=PrescienceWebService.API
        )

    def test_train(self):
        """
        Test the launch of a simple TrainTask
        """
        # Init
        output = {'uuid': 'train-task-uuid', 'type': 'train', 'status': 'PENDING'}
        self.presience_client.call = MagicMock(return_value=(200, output, {}))
        evaluation_result = EvaluationResult(json_dict={'uuid': 'azerty'}, prescience=self.presience_client)

        # Test
        train_task = evaluation_result.train(model_id='my-model', compute_shap_summary=True, chain_metric_task=False)
        self.assertEqual('train-task-uuid', train_task.uuid())
        self.assertEqual('train', train_task.type())
        self.assertEqual(Status.PENDING, train_task.status())

        self.presience_client.call.assert_called_with(
            method='POST',
            path='/ml/train',
            query_parameters={
                'model_id': 'my-model',
                'evaluation_uuid': 'azerty',
                'enable_shap_summary': True,
                'chain_metric_task': False
            },
            content_type='application/json',
            data=None,
            multipart=None,
            call_type=PrescienceWebService.API
        )

    def test_create_dataset_mask(self):
        """
        Test the creation of a dataset mask
        """
        # Init
        self.presience_client.call = MagicMock(return_value=(200, {}, {}))
        dataset = Dataset(json={'dataset_id': 'my-dataset-id'}, prescience=self.presience_client)
        dataset.create_mask(mask_id='dataset-mask', selected_column=['col1', 'col2', 'label'])
        self.presience_client.call.assert_called_with(
            method='POST',
            path='/dataset/mask/my-dataset-id',
            query_parameters={'mask_id': 'dataset-mask'},
            content_type='application/json',
            data=['col1', 'col2', 'label'],
            multipart=None,
            call_type=PrescienceWebService.API
        )

    def test_model_evaluation(self):
        """
        Test the requesting of a model
        """
        # Init
        self.presience_client.call = MagicMock(return_value=(200, {}, {}))
        model = Model(json={'model_id': 'my-model-id'}, prescience=self.presience_client)
        evaluation_payload = model.get_model_evaluation_payload(
            evaluation_id='my-evaluation-1',
            arguments={'feature1': 1, 'feature2': 'toto'}
        )
        evaluation_payload.evaluate()
        self.presience_client.call.assert_called_with(
            method='POST',
            path=f'/eval/my-model-id/transform-model',
            data={'arguments': {'feature1': 1, 'feature2': 'toto'}, 'id': 'my-evaluation-1'},
            call_type=PrescienceWebService.SERVING
        )

    def test_model_only_evaluation(self):
        """
        Test the requesting of a model
        """
        # Init
        self.presience_client.call = MagicMock(return_value=(200, {}, {}))
        model = Model(json={'model_id': 'my-model-id'}, prescience=self.presience_client)
        evaluation_payload = model.get_model_only_evaluation_payload(
            evaluation_id='my-evaluation-1',
            arguments={'feature1': 1, 'feature2': 'toto'}
        )
        evaluation_payload.evaluate()
        self.presience_client.call.assert_called_with(
            method='POST',
            path=f'/eval/my-model-id/model',
            data={'arguments': {'feature1': 1, 'feature2': 'toto'}, 'id': 'my-evaluation-1'},
            call_type=PrescienceWebService.SERVING
        )

    def test_transformation_evaluation(self):
        """
        Test the requesting of a model
        """
        # Init
        self.presience_client.call = MagicMock(return_value=(200, {}, {}))
        model = Model(json={'model_id': 'my-model-id'}, prescience=self.presience_client)
        evaluation_payload = model.get_transformation_evaluation_payload(
            evaluation_id='my-evaluation-1',
            arguments={'feature1': 1, 'feature2': 'toto'}
        )
        evaluation_payload.evaluate()
        self.presience_client.call.assert_called_with(
            method='POST',
            path=f'/eval/my-model-id/transform',
            data={'arguments': {'feature1': 1, 'feature2': 'toto'}, 'id': 'my-evaluation-1'},
            call_type=PrescienceWebService.SERVING
        )
