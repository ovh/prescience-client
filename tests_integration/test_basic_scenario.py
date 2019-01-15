# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

import unittest

from prescience_client import prescience
from tests.utils import get_resource_file_path


class TestBasicScenario(unittest.TestCase):

    def setUp(self):
        self.clean()

    def tearDown(self):
        self.clean()

    def clean(self):
        prescience.config().set_project_from_env()
        prescience.config().show()
        try:
            prescience.source('my-source-id').__delete()
        except RuntimeError:
            print(f'No pre-existing source to delete...')

    def test_scenario(self):
        print('01 - Creating local input...')
        input_path = get_resource_file_path('test.csv')
        input_file = prescience.csv_local_file_input(filepath=input_path, headers=True)
        print('02 - Launching parse task...')
        parse_task = input_file.parse(source_id='my-source-id').watch()
        print('03 - Showing sources...')
        prescience.sources().show()
        source = parse_task.source()
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
