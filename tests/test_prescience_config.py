# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

import shutil, tempfile
import os
import unittest

from com.ovh.mls.prescience.core.config.prescience_config import PrescienceConfig
from tests.utils import get_resource_file_path


class TestPrescienceConfig(unittest.TestCase):
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

        # Setting environnement variables
        os.environ['PRESCIENCE_DEFAULT_PROJECT'] = 'project-default'
        os.environ['PRESCIENCE_DEFAULT_TOKEN'] = 'token-default'
        os.environ['PRESCIENCE_DEFAULT_API_URL'] = 'https://default-api.ai.ovh.net'
        os.environ['PRESCIENCE_DEFAULT_WEBSOCKET_URL'] = 'wss://default-websocket.ai.ovh.net'

    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.config_path)

    def test_get_current_project(self):
        self.assertEqual('project-1', self.prescience_config.get_current_project(), 'project-1')
        self.prescience_config.set_current_project('project-2')
        self.assertEqual('project-2', self.prescience_config.get_current_project(), 'project-2')
        self.prescience_config.set_project('project-3', 'token-3')
        self.assertEqual('project-3', self.prescience_config.get_current_project(), 'project-3')
        self.prescience_config.set_project_from_env()
        self.assertEqual('project-default', self.prescience_config.get_current_project(), 'project-default')


    def test_get_current_token(self):
        self.assertEqual('token-1', self.prescience_config.get_current_token(), 'project-1 token')
        self.prescience_config.set_current_project('project-2')
        self.assertEqual('token-2', self.prescience_config.get_current_token(), 'project-2 token')
        self.prescience_config.set_project('project-3', 'token-3')
        self.assertEqual('token-3', self.prescience_config.get_current_token(), 'project-3 token')
        self.prescience_config.set_project_from_env()
        self.assertEqual('token-default', self.prescience_config.get_current_token(), 'project-default token')

    def test_get_current_api_url(self):
        self.assertEqual('https://prescience-api.ai.ovh.net', self.prescience_config.get_current_api_url(), 'project-1 api url')
        self.prescience_config.set_current_project('project-2')
        self.assertEqual('https://prescience-api-staging.ai.ovh.net', self.prescience_config.get_current_api_url(), 'project-2 api url')
        self.prescience_config.set_project('project-3', 'token-3')
        self.assertEqual('https://prescience-api.ai.ovh.net', self.prescience_config.get_current_api_url(), 'project-3 api url')
        self.prescience_config.set_project_from_env()
        self.assertEqual('https://default-api.ai.ovh.net', self.prescience_config.get_current_api_url(), 'project-default api url')

    def test_get_current_websocket_url(self):
        self.assertEqual('wss://prescience-websocket.ai.ovh.net', self.prescience_config.get_current_websocket_url(), 'project-1 websocket url')
        self.prescience_config.set_current_project('project-2')
        self.assertEqual('wss://prescience-websocket-staging.ai.ovh.net', self.prescience_config.get_current_websocket_url(), 'project-2 websocket url')
        self.prescience_config.set_project('project-3', 'token-3')
        self.assertEqual('wss://prescience-websocket.ai.ovh.net', self.prescience_config.get_current_websocket_url(), 'project-3 websocket url')
        self.prescience_config.set_project_from_env()
        self.assertEqual('wss://default-websocket.ai.ovh.net', self.prescience_config.get_current_websocket_url(), 'project-default websocket url')


if __name__ == '__main__':
    unittest.main()