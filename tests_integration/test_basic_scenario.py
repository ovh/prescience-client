# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

import unittest
import os

from prescience_client.exception.prescience_client_exception import PrescienceException
from prescience_client import prescience
from tests.utils import get_resource_file_path


class TestBasicScenario(unittest.TestCase):
    """
    For launching this integration test you need to set the following environment variables :
    PRESCIENCE_DEFAULT_API_URL : The prescience URL to test on
    PRESCIENCE_DEFAULT_WEBSOCKET_URL : The prescience websocket to test on
    PRESCIENCE_DEFAULT_TOKEN (optional) : The prescience token to test on
    PRESCIENCE_DEFAULT_ADMIN_API_URL (optional) : The the token is not set or fake, it will request a token from this given admin url
    """

    def setUp(self):
        os.environ['PRESCIENCE_DEFAULT_PROJECT'] = 'it-TestBasicScenario'
        prescience.config().set_default_project_from_env()

        # If token is not defined correctly, try to create a new project token
        current_token = prescience.config().get_current_token()
        if current_token is None or len(current_token) < 20:
            payload = prescience.new_project_token()
            token = payload['token']
            current_config = prescience.config()
            print(f'New token for project {current_config.get_current_project_name()} : {token}')
            current_config.set_token(
                project_name=current_config.get_current_project_name(),
                token=token
            )

        prescience.config().show()
        # Clean any previous existing sources
        self.clean()

    def tearDown(self):
        self.clean()

    def clean(self):
        try:
            prescience.source('my-source-id').delete()
        except PrescienceException:
            print(f'No pre-existing source to delete...')

    def test_scenario(self):
        print('01 - Creating local input...')
        input_path = get_resource_file_path('test.csv')
        input_file = prescience.csv_local_file_input(filepath=input_path, headers=True)
        print('02 - Launching parse task...')
        input_file.parse(source_id='my-source-id').watch()
        print('03 - Showing sources...')
        prescience.sources().show()
        source = prescience.source('my-source-id')
        print('04 - Showing source schema...')
        source.schema().show()
        print('05 - Launching preprocess task...')
        preprocess_task = source.preprocess(dataset_id='my-dataset_id').watch()
        print('06 - Showing datasets...')
        prescience.datasets().show()
        dataset = preprocess_task.dataset()
        print('07 - Showing dataset schema...')
        dataset.schema().show()
        print('08 - Launching optimize task...')
        dataset.optimize().watch()
        evaluation_results = dataset.evaluation_results()
        print('09 - Showing evaluation results...')
        evaluation_results.show()
        single_eval_result = evaluation_results.content[0]
        print('10 - Launching train task...')
        single_eval_result.train('my-model').watch()
        prescience.models().show()

        print('10 - Evaluate model...')
        evaluation_payload_input = prescience.model('my-model').get_model_evaluation_payload(
            evaluation_id='my-evaluation',
            arguments={
                'hours-per-week': 40,
                'capital-gain': 2174,
                'education-num': 13,
                'random-bool': 'True',
                'marital-status': 'Never-married',
                'age': 39,
                'sex': 'Male',
                'relationship': 'Not-in-family',
                'education': 'Bachelors',
                'race': 'White',
                'native-country': 'United-States',
                'fnlwgt': 77516,
                'workclass': 'State-gov',
                'capital-loss': 0,
                'occupation': 'Adm-clerical'
            }
        )
        evaluation_payload_input.show()
        validation_result, _ = evaluation_payload_input.validate()
        self.assertEqual(False, validation_result)

        evaluation_payload_input.add_payload_argument('random-bool', True)
        evaluation_payload_input.show()
        validation_result, _ = evaluation_payload_input.validate()
        self.assertEqual(True, validation_result)

        evaluation_payload_output = evaluation_payload_input.evaluate()
        evaluation_payload_output.show()
        final_label = evaluation_payload_output.get_result_label()
        self.assertIn(final_label, ['<=50K', '>50K'])
