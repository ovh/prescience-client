from prescience_client.commands import prompt_for_source_id_if_needed, prompt_for_dataset_id_if_needed
from prescience_client.commands.command import Command
from prescience_client.utils.monad import Option


class PlotCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='plot',
            help_message='Plot a prescience object',
            prescience_client=prescience_client,
            sub_commands=[
                PlotSourceCommand(prescience_client),
                PlotDatasetCommand(prescience_client)
            ]
        )

class PlotSourceCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='source',
            help_message='Plot a source data object',
            prescience_client=prescience_client,
            sub_commands=[]
        )

    def init_from_subparser(self, subparsers, selector):
        super().init_from_subparser(subparsers, selector)
        self.cmd_parser.add_argument('id', nargs='?', type=str,
                                        help='Identifier of the source object. If unset if will trigger the interactive mode for selecting one.')
        self.cmd_parser.add_argument('--x', type=str, help='Plot the current source')
        self.cmd_parser.add_argument('--kind', type=str, help='Kind of the plot figure. Default: line')

    def exec(self, args: dict):
        source_id = prompt_for_source_id_if_needed(args, self.prescience_client)
        kind = args.get('kind') or 'line'
        x = args.get('x')
        self.prescience_client.plot_source(source_id=source_id, x=x, block=True, kind=kind)


class PlotDatasetCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='dataset',
            help_message='Plot a dataset data object',
            prescience_client=prescience_client,
            sub_commands=[]
        )

    def init_from_subparser(self, subparsers, selector):
        super().init_from_subparser(subparsers, selector)
        self.cmd_parser.add_argument('id', nargs ='?', type=str, help='Identifier of the dataset object. If unset if will trigger the interactive mode for selecting one.')
        self.cmd_parser.add_argument('--no-test', default=True, dest='plot_test', action='store_false', help='Won\'t plot the test part')
        self.cmd_parser.add_argument('--no-train', default=True, dest='plot_train', action='store_false', help='Won\'t plot the train part')

    def exec(self, args: dict):
        dataset_id = prompt_for_dataset_id_if_needed(args, self.prescience_client)
        plot_train = args.get('plot_train')
        plot_test = args.get('plot_test')
        self.prescience_client.plot_dataset(dataset_id=dataset_id, block=True, plot_train=plot_train, plot_test=plot_test)