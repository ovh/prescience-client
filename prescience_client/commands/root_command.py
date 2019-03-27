import argparse

from prescience_client.commands.command import Command
from prescience_client.commands.config_command import ConfigCommand
from prescience_client.commands.delete_command import DeleteCommand
from prescience_client.commands.generate_command import GenerateCommand
from prescience_client.commands.get_command import GetCommand
from prescience_client.commands.plot_command import PlotCommand
from prescience_client.commands.predict_command import PredictCommand
from prescience_client.commands.start_command import StartCommand


class RootCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='root',
            help_message='Show information about specific prescience objects',
            prescience_client=prescience_client,
            sub_commands=[
                ConfigCommand(prescience_client),
                GetCommand(prescience_client),
                StartCommand(prescience_client),
                PlotCommand(prescience_client),
                PredictCommand(prescience_client),
                DeleteCommand(prescience_client),
                GenerateCommand(prescience_client)
            ]
        )
        self.selector = None
        self.cmd_parser = argparse.ArgumentParser(description='Python client for OVH Prescience project')
        if len(self.sub_commands) != 0:
            sub_selector = f'{self.name}_subject'
            subparser = self.cmd_parser.add_subparsers(dest=sub_selector)
            for cmd in self.sub_commands:
                cmd.init_from_subparser(subparser, sub_selector)

    def init_from_subparser(self, subparsers, selector):
        pass


    def should_exec(self, args) -> bool:
        return True