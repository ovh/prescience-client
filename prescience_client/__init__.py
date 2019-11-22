# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

import argcomplete

from prescience_client.client.prescience_client import PrescienceClient
from prescience_client.commands.root_command import RootCommand
from prescience_client.config.prescience_config import PrescienceConfig
from prescience_client.exception.prescience_client_exception import PrescienceException

config = PrescienceConfig().load()
prescience: PrescienceClient = PrescienceClient(config)


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
        root_cmd = RootCommand(prescience)
        argcomplete.autocomplete(root_cmd.cmd_parser)
        args = vars(root_cmd.cmd_parser.parse_args())

        root_cmd.exec(args)
        exit(0)

    except PrescienceException:
        exit(1)
