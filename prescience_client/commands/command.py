from abc import ABC

from prescience_client.commands import get_args_or_prompt_list
from prescience_client.utils.monad import List


class Command(ABC):

    def __init__(self,
                 name: str,
                 help_message: str,
                 sub_commands: list,
                 prescience_client):
        self.name: str = name
        self.help: str = help_message
        self.sub_commands: list = sub_commands
        self.selector: str = None
        self.cmd_parser = None
        self.prescience_client = prescience_client

    def should_exec(self, args) -> bool:
        result = args.get(self.selector) == self.name
        return result

    def init_from_subparser(self, subparsers, selector):
        self.selector = selector
        self.cmd_parser = subparsers.add_parser(self.name, help=self.help)
        if len(self.sub_commands) != 0:
            sub_selector = f'{self.name}_subject'
            subparser = self.cmd_parser.add_subparsers(dest=sub_selector)
            for cmd in self.sub_commands:
                cmd.init_from_subparser(subparser, sub_selector)

    def exec(self, args):
        maybe_cmd = List(self.sub_commands)\
            .find(lambda cmd: cmd.should_exec(args))\
            .get_or_else(None)

        if maybe_cmd is None:
            subject = get_args_or_prompt_list(
                arg_name='subject',
                args=args,
                message='Please select an command to execute',
                choices_function=lambda: [cmd.name for cmd in self.sub_commands]
            )
            args[f'{self.name}_subject'] = subject
            maybe_cmd = List(self.sub_commands) \
                .find(lambda cmd: cmd.should_exec(args)) \
                .get_or_else(None)

        maybe_cmd.exec(args)