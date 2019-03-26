from prescience_client.commands import get_args_or_prompt_list
from prescience_client.commands.command import Command
from prescience_client.enum.output_format import OutputFormat


class ConfigCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='config',
            help_message='Manage your prescience-client configuration',
            prescience_client=prescience_client,
            sub_commands=[
                ConfigGetCommand(prescience_client),
                ConfigSwitchCommand(prescience_client),
                ConfigAddCommand(prescience_client)
            ]
        )


class ConfigGetCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='get',
            help_message='Show information about specifics prescience objects',
            prescience_client=prescience_client,
            sub_commands=[]
        )

    def init_from_subparser(self, subparsers, selector):
        super().init_from_subparser(subparsers, selector)
        self.cmd_parser.add_argument('-o', '--output', dest='output', type=OutputFormat, choices=list(OutputFormat),
                                       help=f"Type of output to get on std out. (default: {OutputFormat.TABLE})",
                                       default=OutputFormat.TABLE)

    def exec(self, args: dict):
        output = args.get('output')
        self.prescience_client.config().show(output)



class ConfigSwitchCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='switch',
            help_message='Change the currently selected prescience project',
            prescience_client=prescience_client,
            sub_commands=[]
        )

    def init_from_subparser(self, subparsers, selector):
        super().init_from_subparser(subparsers, selector)
        self.cmd_parser.add_argument('project', nargs='?', type=str,
                                          help='The project name you want to switch on. If no project is indicated, it will turn on the interactive mode for selecting one.')

    def exec(self, args: dict):
        project = get_args_or_prompt_list(
            arg_name='project',
            args=args,
            message='Which project do you want to switch on ?',
            choices_function=self.prescience_client.config().get_all_projects_names
        )
        self.prescience_client.config().set_current_project(project_name=project)


class ConfigAddCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='add',
            help_message='Add a new project and its token',
            prescience_client=prescience_client,
            sub_commands=[]
        )

    def init_from_subparser(self, subparsers, selector):
        super().init_from_subparser(subparsers, selector)
        self.cmd_parser.add_argument('project', type=str, help='The project name')
        self.cmd_parser.add_argument('token', type=str, help='The token linked to this project')

    def exec(self, args: dict):
        self.prescience_client.config().set_project(args.get('project'), args.get('token'))