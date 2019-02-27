# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

import io
import json
import os
import yaml
from prescience_client.enum.output_format import OutputFormat

from prescience_client.config.constants import DEFAULT_PRESCIENCE_CONFIG_PATH, DEFAULT_PRESCIENCE_API_URL, \
    DEFAULT_WEBSOCKET_URL, DEFAULT_SERVING_URL, \
    DEFAULT_PRESCIENCE_CONFIG_FILE, DEFAULT_EXCEPTION_HANDLING, EXCEPTION_HANDLING_PRINT, EXCEPTION_HANDLING_RAISE, \
    DEFAULT_TIMEOUT_SECOND, DEFAULT_VERBOSE
from prescience_client.exception.prescience_client_exception import PrescienceException
from prescience_client.utils.table_printable import TablePrintable, TablePrinter
from termcolor import colored

KEY_PROJECTS = 'projects'
KEY_ENVIRONMENTS = 'environments'
KEY_CURRENT_PROJECT = 'current_project'
KEY_EXCEPTION_HANDLING = 'exception_handling'
KEY_VERBOSE = 'verbose'
KEY_TIMEOUT = 'timeout'

# Keys for projects
KEY_TOKEN = 'token'
KEY_ENVIRONMENT = 'environment'

# Keys for environments
KEY_API_URL = 'api_url'
KEY_WEBSOCKET_URL = 'websocket_url'
KEY_SERVING_URL = 'serving_url'
KEY_ADMIN_URL = 'admin_api_url'

VALUE_DEFAULT = 'default'

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
        self.environments = {}
        self.current_project_name = None
        self.exception_handling = None
        self.verbose = DEFAULT_VERBOSE
        self.timeout = DEFAULT_TIMEOUT_SECOND

    def is_verbose_activated(self) -> bool:
        """
        Getter of the verbose attribute
        :return: the verbose attribute
        """
        return self.verbose

    def set_verbose(self, verbose: bool):
        """
        Setter of the verbose mode
        :param verbose: verbose attribute value
        """
        self.verbose = verbose

    def get_timeout(self) -> int:
        """
        Getter of the timeout
        :return: the timeout in second
        """
        return self.timeout

    def set_timeout(self, timeout: int):
        """
        Setter of the timeout
        :param timeout: The new timeout to use
        """
        self.timeout = timeout

    def load(self) -> 'PrescienceConfig':
        """
        Load the configuration depending on what's inside configuration file
        :return: self
        """
        PrescienceConfig.create_config_path_if_not_exist(config_path=self.config_path)
        full_config_path = self.get_full_config_file_path()
        if os.path.isfile(full_config_path):
            if self.is_verbose_activated():
                print(f'Loading configuration file {full_config_path}')
            with io.open(full_config_path, 'r') as stream:
                loaded_config = yaml.load(stream)
                self.projects = loaded_config.get(KEY_PROJECTS, self.default_projects_dict())
                self.current_project_name = loaded_config.get(KEY_CURRENT_PROJECT, VALUE_DEFAULT)
                self.exception_handling = loaded_config.get(KEY_EXCEPTION_HANDLING, DEFAULT_EXCEPTION_HANDLING)
                self.environments = loaded_config.get(KEY_ENVIRONMENTS, self.default_environments_dict())
                self.set_verbose(verbose=loaded_config.get(KEY_VERBOSE, DEFAULT_VERBOSE))
                self.set_timeout(timeout=loaded_config.get(KEY_TIMEOUT, DEFAULT_TIMEOUT_SECOND))
        else:
            if self.is_verbose_activated():
                print(f'No configuration file found yet. Loading default one')
            self.projects = self.default_projects_dict()
            self.current_project_name = VALUE_DEFAULT
            self.exception_handling = DEFAULT_EXCEPTION_HANDLING
            self.environments = self.default_environments_dict()
            self.set_verbose(verbose=DEFAULT_VERBOSE)
            self.set_timeout(timeout=DEFAULT_TIMEOUT_SECOND)

        return self

    def save(self) -> 'PrescienceConfig':
        """
        Save the current state of the configuration inside the configuration file (with the YAML formating)
        :return: self
        """
        PrescienceConfig.create_config_path_if_not_exist(config_path=self.config_path)
        full_config_path = self.get_full_config_file_path()
        if self.is_verbose_activated():
            print(f'Saving configuration file {full_config_path}')

        with io.open(full_config_path, 'w', encoding='utf8') as outfile:
            yaml.dump(
                data={
                    KEY_ENVIRONMENTS: self.environments,
                    KEY_PROJECTS: self.projects,
                    KEY_CURRENT_PROJECT: self.current_project_name,
                    KEY_EXCEPTION_HANDLING: self.exception_handling,
                    KEY_VERBOSE: self.is_verbose_activated(),
                    KEY_TIMEOUT: self.get_timeout()
                },
                stream=outfile,
                default_flow_style=False,
                allow_unicode=True
            )

        return self

    def default_projects_dict(self):
        """
        Create a default dictionary for 'projects' configuration property
        :return: The default dictionary
        """
        return {VALUE_DEFAULT: self.project_dict()}

    def default_environments_dict(self):
        """
        Create a default dictionary for 'environmenrts' configuration property
        :return: The default dictionary
        """
        return {VALUE_DEFAULT: self.environment_dict()}

    def project_dict(self,
        token: str = None,
        environment_name: str = VALUE_DEFAULT
    ):
        """
        Construct a project dictionary from given values
        :param token: The token for the project
        :param environment_name: The name of the project's environment
        :return: The project dictionary
        """
        return {
            KEY_TOKEN: token,
            KEY_ENVIRONMENT: environment_name
        }


    @staticmethod
    def environment_dict(
            api_url: str = DEFAULT_PRESCIENCE_API_URL,
            websocket_url: str = DEFAULT_WEBSOCKET_URL,
            serving_url: str = DEFAULT_SERVING_URL,
            admin_url: str = None
    ) -> dict:
        """
        Construct an environment dictionary from given values
        :param api_url: The prescience api url to use for the environment
        :param websocket_url: The prescience web socket url to use for the environment
        :param serving_url: The prescience serving url to use for the environment
        :param admin_url: The prescience admin url to use for the environment
        :return: The environment dictionary
        """
        initial_env = {
            KEY_API_URL: api_url,
            KEY_WEBSOCKET_URL: websocket_url,
            KEY_SERVING_URL: serving_url
        }

        if admin_url is not None:
            initial_env[KEY_ADMIN_URL] = admin_url

        return initial_env


    def set_default_project_from_env(self,
                                     env_default_project_name: str = 'PRESCIENCE_DEFAULT_PROJECT',
                                     env_default_environment_name: str = 'PRESCIENCE_DEFAULT_ENVIRONMENT',
                                     env_default_token: str = 'PRESCIENCE_DEFAULT_TOKEN',
                                     env_default_api_url: str = 'PRESCIENCE_DEFAULT_API_URL',
                                     env_default_admin_api_url: str = 'PRESCIENCE_DEFAULT_ADMIN_API_URL',
                                     env_default_websocket_url = 'PRESCIENCE_DEFAULT_WEBSOCKET_URL',
                                     env_default_serving_url: str = 'PRESCIENCE_DEFAULT_SERVING_URL') -> 'PrescienceConfig':
        """
        Automatically set an entry in the configuration file for default values.
        Default values are read from environment variables.
        :param env_default_project_name: The environment variable name for project name
        :param env_default_environment_name: The environment variable for default environment name
        :param env_default_token: The environment variable name for token
        :param env_default_api_url: The environment variable name for api url
        :param env_default_admin_api_url: The environment variable name for admin api url
        :param env_default_websocket_url: The environment variable name for websocket url
        :param env_default_serving_url: The environment variable name for the serving url
        :return: self
        """
        default_project_name = os.getenv(env_default_project_name, VALUE_DEFAULT)
        default_environment_name = os.getenv(env_default_environment_name, VALUE_DEFAULT)
        default_token = os.getenv(env_default_token, None)
        default_api_url = os.getenv(env_default_api_url, DEFAULT_PRESCIENCE_API_URL)
        default_api_admin_url = os.getenv(env_default_admin_api_url, None)
        default_websocket_url = os.getenv(env_default_websocket_url, DEFAULT_WEBSOCKET_URL)
        default_serving_url = os.getenv(env_default_serving_url, DEFAULT_SERVING_URL)

        if default_token is None:
            raise Exception(f'Environement variable {env_default_token} is not set...')

        return self.set_environment(
            environment_name=default_environment_name,
            api_url=default_api_url,
            websocket_url=default_websocket_url,
            serving_url=default_serving_url,
            admin_api_url=default_api_admin_url
        ).set_project(
            project_name=default_project_name,
            token=default_token,
            environment_name=default_environment_name
        )

    def enable_print_exception_handling(self):
        """
        Enable the exeption handling of type 'print'
        """
        self.exception_handling = EXCEPTION_HANDLING_PRINT
        self.save()

    def enable_raise_exception_handling(self):
        """
        Enable the exeption handling of type 'raise'
        """
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
            prescience_exception.print()
            raise prescience_exception

    def set_token(self, project_name: str, token: str) -> 'PrescienceConfig':
        """
        Set a new token to a project
        :param project_name: The name of the project we want to set the new token on
        :param token: The new token for the project
        :return: The current configuration
        """
        self.projects[project_name][KEY_TOKEN] = token
        self.save()
        return self

    def get_current_environment(self) -> dict:
        """
        Get the environment used for the current project
        :return: The environment dict
        """
        current_project = self.get_current_project_name()
        return self.get_environment_for_project(current_project)

    def get_environment_for_project(self, project_name: str) -> dict:
        """
        Get the environment used for the given project
        :param project_name: The name of the project we want the environment from
        :return: The environment dict
        """
        self.get_current_project_dict()
        return self.projects[project_name][KEY_ENVIRONMENT]

    def get_all_projects_names(self) -> list:
        """
        Get the list of all projects names
        :return: the list of all projects names
        """
        return [k for k, _ in self.projects.items()]

    def get_environment(self, env_name: str) -> dict:
        """
        Get the environment if the specified name
        :param env_name: The name of the environment
        :return: The environment dict
        """
        return self.environments.get(env_name, None)

    def set_environment(self,
                        environment_name: str,
                        api_url: str = DEFAULT_PRESCIENCE_API_URL,
                        websocket_url: str = DEFAULT_WEBSOCKET_URL,
                        serving_url: str = DEFAULT_SERVING_URL,
                        admin_api_url: str = None,
                        ) -> 'PrescienceConfig':
        """
        Add or update an environment
        :param environment_name: The name of the environment
        :param api_url: The prescience api url
        :param websocket_url: The prescience websocket url
        :param serving_url: The prescience serving url
        :param admin_api_url: The prescience admin url
        :return: The current configuration object
        """
        self.environments[environment_name] = self.environment_dict(
            api_url=api_url,
            websocket_url=websocket_url,
            serving_url=serving_url,
            admin_url=admin_api_url
        )

        return self.save()


    def set_project(self,
                    project_name: str,
                    token: str,
                    environment_name: str = VALUE_DEFAULT
                    ) -> 'PrescienceConfig':
        """
        Add or update an entry in the configuration file corresponding to the given parameters
        :param project_name: The project name to add or to update
        :param token: The related token for this project name
        :param environment_name: The environment to use on this project
        :return: self
        """
        self.projects[project_name] = self.project_dict(token=token, environment_name=environment_name)
        self.current_project_name = project_name
        return self.save()

    def get_or_create_config_directory(self):
        """
        Access or create the prescience-client configuration directory
        :return: the prescience-client configuration directory
        """
        return self.create_config_path_if_not_exist(self.config_path)

    def get_or_create_config_cache_directory(self):
        """
        Access or create the prescience-client cache directory
        :return: the prescience-client cache directory
        """
        cache_directory = os.path.join(self.config_path, 'cache')
        return self.create_config_path_if_not_exist(cache_directory)

    def get_or_create_cache_sources_directory(self):
        """
        Access or create the prescience-client cache sources directory
        :return: the prescience-client cache sources directory
        """
        cache_directory = self.get_or_create_config_cache_directory()
        cache_sources = os.path.join(cache_directory, 'sources')
        return self.create_config_path_if_not_exist(cache_sources)

    def get_or_create_cache_datasets_directory(self):
        """
        Access or create the prescience-client cache datasets directory
        :return: the prescience-client cache datasets directory
        """
        cache_directory = self.get_or_create_config_cache_directory()
        cache_datasets = os.path.join(cache_directory, 'datasets')
        return self.create_config_path_if_not_exist(cache_datasets)

    def get_full_config_file_path(self):
        """
        Access the full path of the prescience-client configuration file
        :return: the full path of the prescience-client configuration file
        """
        config_directory = self.get_or_create_config_directory()
        return os.path.join(config_directory, self.config_file)

    def set_current_project(self, project_name: str) -> 'PrescienceConfig':
        """
        Switch the current working project.
        Also execute a 'save' of the configuration file
        :param project_name: The name of the project that we need to switch on
        :return: self
        """
        self.current_project_name = project_name
        return self.save()

    def get_current_project_name(self) -> str:
        """
        Access the current working project
        :return: The current project name
        """
        return self.current_project_name

    def get_current_project_dict(self) -> dict:
        """
        Access the current project dictionary
        :return: the project dictionary
        """
        current_project_name = self.get_current_project_name()
        return self.get_project_dict(project_name=current_project_name)

    def get_project_dict(self, project_name: str) -> dict:
        """
        Access project dictionary from a project name
        :param project_name: The name of the project
        :return: he project dictionary
        """
        return self.projects[project_name]

    def get_current_token(self) -> str:
        """
        Access the token of the current working project
        :return: the token of the current working project
        """
        return self.get_current_project_dict()[KEY_TOKEN]

    def get_current_api_url(self) -> str:
        """
        Access the api url of the current working project
        :return: the api url of the current working project
        """
        current_env = self.get_current_environment()
        return self.environments[current_env][KEY_API_URL]

    def get_current_websocket_url(self) -> str:
        """
        Access the websocket url of the current working project
        :return: the websocket url of the current working project
        """
        return self.environments[self.get_current_environment()][KEY_WEBSOCKET_URL]

    def get_current_admin_api_url(self) -> str:
        """
        Access the admin api url of the current working project
        :return: the api url of the current working project
        """
        return self.environments[self.get_current_environment()].get(KEY_ADMIN_URL, None)

    def get_current_serving_url(self) -> str:
        """
        Access the serving url of the current working project
        :return: the serving url of the current working project
        """
        return self.environments[self.get_current_environment()].get(KEY_SERVING_URL, None)

    def show(self, ouput: OutputFormat = OutputFormat.TABLE):
        """
        Display the current configuration a a table in console standard output
        """
        if ouput == OutputFormat.JSON:
            print(json.dumps(self.__dict__))
        else:
            all_line = [ConfigLine(k, v) for k, v in self.projects.items()]
            [line.set_seleted() for line in all_line if line.get_project() == self.get_current_project_name()]
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
        return ['project', 'environment', 'token']

    def table_row(self) -> dict:
        string_token = '- unset -'
        if self.token() is not None:
            string_token = self.token()[:30] + '...' + self.token()[-30:]

        result = {
            'project': self.get_project(),
            'environment': self.get_environment(),
            'token': string_token
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

    def get_environment(self):
        return self.line_dict.get('environment', None)

    def get_project(self) -> str:
        return self.project

    def set_seleted(self):
        self.is_selected = True

    def get_is_selected(self) -> bool:
        return self.is_selected
