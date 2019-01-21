# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

import io
import os
import yaml
from com.ovh.mls.prescience.core.config.constants import DEFAULT_PRESCIENCE_CONFIG_PATH, DEFAULT_PRESCIENCE_API_URL, \
    DEFAULT_WEBSOCKET_URL, \
    DEFAULT_PRESCIENCE_CONFIG_FILE, DEFAULT_EXCEPTION_HANDLING, EXCEPTION_HANDLING_PRINT, EXCEPTION_HANDLING_RAISE
from com.ovh.mls.prescience.core.exception.prescience_client_exception import PrescienceException
from com.ovh.mls.prescience.core.utils.table_printable import TablePrintable, TablePrinter
from termcolor import colored


class PrescienceConfig(object):
    """
    User specific prescience configuration object, read and save as a yaml file in the wanted directory
    """

    def __init__(self,
                 config_path: str = DEFAULT_PRESCIENCE_CONFIG_PATH,
                 config_file: str = DEFAULT_PRESCIENCE_CONFIG_FILE
                 ):
        """
        Construct a PrescienceConfig
        :param config_path: The path of the prescience configuration directory to use
        :param config_file: The name of the configuration file to use
        """
        self.config_path: str = config_path
        self.config_file: str = config_file
        self.projects = {}
        self.current_project = None
        self.exception_handling = None

    def load(self) -> 'PrescienceConfig':
        """
        Load the configuration depending on what's inside configuration file
        :return: self
        """
        PrescienceConfig.create_config_path_if_not_exist(config_path=self.config_path)
        full_config_path = f'{self.config_path}/{self.config_file}'
        if os.path.isfile(full_config_path):
            print(f'Loading configuration file {full_config_path}')
            with io.open(full_config_path, 'r') as stream:
                loaded_config = yaml.load(stream)
                self.projects = loaded_config['projects']
                self.current_project = loaded_config['current_project']
                self.exception_handling = loaded_config.get('exception_handling', DEFAULT_EXCEPTION_HANDLING)
        else:
            print(f'No configuration file found yet')

        return self

    def save(self) -> 'PrescienceConfig':
        """
        Save the current state of the configuration inside the configuration file (with the YAML formating)
        :return: self
        """
        PrescienceConfig.create_config_path_if_not_exist(config_path=self.config_path)
        full_config_path = f'{self.config_path}/{self.config_file}'
        print(f'Saving configuration file {full_config_path}')

        with io.open(full_config_path, 'w', encoding='utf8') as outfile:
            yaml.dump(
                data={
                    'projects': self.projects,
                    'current_project': self.current_project,
                    'exception_handling': self.exception_handling
                },
                stream=outfile,
                default_flow_style=False,
                allow_unicode=True
            )

        return self

    def set_project_from_env(self,
                             env_default_project_name: str = 'PRESCIENCE_DEFAULT_PROJECT',
                             env_default_token: str = 'PRESCIENCE_DEFAULT_TOKEN',
                             env_default_api_url: str = 'PRESCIENCE_DEFAULT_API_URL',
                             env_default_admin_api_url: str = 'PRESCIENCE_DEFAULT_ADMIN_API_URL',
                             env_default_websocket_url = 'PRESCIENCE_DEFAULT_WEBSOCKET_URL') -> 'PrescienceConfig':
        """
        Automatically set an entry in the configuration file for default values.
        Default values are read from environment variables.
        :param env_default_project_name: The environment variable name for project name
        :param env_default_token: The environment variable name for token
        :param env_default_api_url: The environment variable name for api url
        :param env_default_admin_api_url: The environment variable name for admin api url
        :param env_default_websocket_url: The environment variable name for websocket url
        :return: self
        """
        default_project_name = os.getenv(env_default_project_name, 'default')
        default_token = os.getenv(env_default_token, None)
        default_api_url = os.getenv(env_default_api_url, DEFAULT_PRESCIENCE_API_URL)
        default_api_admin_url = os.getenv(env_default_admin_api_url, None)
        default_websocket_url = os.getenv(env_default_websocket_url, DEFAULT_WEBSOCKET_URL)

        if default_token is None:
            raise Exception(f'Environement variable {env_default_token} is not set...')

        self.set_project(
            project_name=default_project_name,
            token=default_token,
            api_url=default_api_url,
            admin_api_url=default_api_admin_url,
            websocket_url=default_websocket_url
        )

        return self

    def enable_print_exception_handling(self):
        self.exception_handling = EXCEPTION_HANDLING_PRINT
        self.save()

    def enable_raise_exception_handling(self):
        self.exception_handling = EXCEPTION_HANDLING_RAISE
        self.save()

    def handle_exception(self, prescience_exception: PrescienceException):
        """
        Handle the given PrescienceException with the configured strategy
        - 'print' strategy will print the exception on the stdout
        - 'raise' strategy will raise the exception
        :param prescience_exception: The exception that we want to handle
        """
        if self.exception_handling == EXCEPTION_HANDLING_RAISE:
            raise prescience_exception
        else:
            print(f'--------------[{colored("ERROR", "red")}]--------------')
            if prescience_exception.message() is not None:
                print('Message: ' + colored(prescience_exception.message(), 'red'))
            else:
                print('Exception: ' + str(prescience_exception))
            if prescience_exception.resolution_hint() is not None:
                print('Resolution hint: ' + colored(prescience_exception.resolution_hint(), 'red'))
            print(f'-----------------------------------')
            raise prescience_exception


    def set_project(self,
                    project_name: str,
                    token: str,
                    api_url: str = DEFAULT_PRESCIENCE_API_URL,
                    admin_api_url: str = None,
                    websocket_url: str = DEFAULT_WEBSOCKET_URL
                    ) -> 'PrescienceConfig':
        """
        Add or update an entry in the configuration file corresponding to the given parameters
        :param project_name: The project name to add or to update
        :param token: The related token for this project name
        :param api_url: The related api url for this project name
        :param admin_api_url: The related admin api url for this project name (default: None)
        :param websocket_url: The related websocket url for this project name
        :return: self
        """
        self.projects[project_name] = {
            'token': token,
            'api_url': api_url,
            'websocket_url': websocket_url
        }

        # Setting admin url only if it exists
        if admin_api_url is not None:
            self.projects[project_name]['admin_api_url'] = admin_api_url

        self.current_project = project_name
        return self.save()

    def set_current_project(self, project_name: str) -> 'PrescienceConfig':
        """
        Switch the current working project.
        Also execute a 'save' of the configuration file
        :param project_name: The name of the project that we need to switch on
        :return: self
        """
        self.current_project = project_name
        return self.save()

    def get_current_project(self) -> str:
        """
        Access the current working project
        :return: The current project name
        """
        return self.current_project

    def get_current_token(self) -> str:
        """
        Access the token of the current working project
        :return: the token of the current working project
        """
        return self.projects[self.get_current_project()]['token']

    def get_current_api_url(self) -> str:
        """
        Access the api url of the current working project
        :return: the api url of the current working project
        """
        return self.projects[self.get_current_project()]['api_url']

    def get_current_websocket_url(self) -> str:
        """
        Access the websocket url of the current working project
        :return: the websocket url of the current working project
        """
        return self.projects[self.get_current_project()]['websocket_url']

    def get_current_admin_api_url(self) -> str:
        """
        Access the admin api url of the current working project
        :return: the api url of the current working project
        """
        return self.projects[self.get_current_project()].get('admin_api_url', None)

    def show(self):
        """
        Display the current configuration a a table in console standard output
        """
        all_line = [ConfigLine(k, v) for k, v in self.projects.items()]
        [line.set_seleted() for line in all_line if line.get_project() == self.get_current_project()]
        table = TablePrinter.get_table(ConfigLine, all_line)
        print(table)

    @staticmethod
    def create_config_path_if_not_exist(config_path: str = DEFAULT_PRESCIENCE_CONFIG_PATH) -> str:
        """
        Static method responsible for creating the configuration directory if it doesn't exist yet
        :param config_path: The configuration directory path to create if needed
        :return: The configuration directory path
        """
        if not os.path.exists(config_path):
            print(f'Directory \'{config_path}\' doesn\'t exists. Creating it...')
            os.makedirs(config_path)
        return config_path


class ConfigLine(TablePrintable):

    @classmethod
    def table_header(cls) -> list:
        return ['project', 'api_url', 'websocket_url', 'token']

    def table_row(self) -> dict:
        result = {
            'project': self.get_project(),
            'api_url': self.api_url(),
            'websocket_url': self.websocket_url(),
            'token': self.token()[:30] + '...'
        }

        for k, v in result.items():
            if self.is_selected:
                result[k] = colored(v, 'green')

        return result

    def __init__(self, project: str, line_dict: dict):
        self.project = project
        self.line_dict = line_dict
        self.is_selected = False

    def token(self):
        return self.line_dict.get('token', None)

    def api_url(self):
        return self.line_dict.get('api_url', None)

    def websocket_url(self):
        return self.line_dict.get('websocket_url', None)

    def get_project(self) -> str:
        return self.project

    def set_seleted(self):
        self.is_selected = True

    def get_is_selected(self) -> bool:
        return self.is_selected
