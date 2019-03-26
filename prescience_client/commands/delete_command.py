from prescience_client.commands import prompt_for_source_id_if_needed, prompt_for_dataset_id_if_needed, \
    prompt_for_model_id_if_needed
from prescience_client.commands.command import Command


class DeleteCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='delete',
            help_message='Delete a prescience object',
            prescience_client=prescience_client,
            sub_commands=[
                DeleteSourceCommand(prescience_client),
                DeleteDatasetCommand(prescience_client),
                DeleteModelCommand(prescience_client)
            ]
        )

class DeleteSourceCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='source',
            help_message='Delete a prescience source object',
            prescience_client=prescience_client,
            sub_commands=[]
        )

    def init_from_subparser(self, subparsers, selector):
        super().init_from_subparser(subparsers, selector)
        self.cmd_parser.add_argument('id', nargs='?', type=str, help='Identifier of the source object to delete')

    def exec(self, args: dict):
        source_id = prompt_for_source_id_if_needed(args, self.prescience_client)
        self.prescience_client.delete_source(source_id=source_id)

class DeleteDatasetCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='dataset',
            help_message='Delete a prescience dataset object',
            prescience_client=prescience_client,
            sub_commands=[]
        )

    def init_from_subparser(self, subparsers, selector):
        super().init_from_subparser(subparsers, selector)
        self.cmd_parser.add_argument('id', nargs='?', type=str, help='Identifier of the dataset object to delete')

    def exec(self, args: dict):
        dataset_id = prompt_for_dataset_id_if_needed(args, self.prescience_client)
        self.prescience_client.delete_dataset(dataset_id=dataset_id)

class DeleteModelCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='model',
            help_message='Delete a prescience model object',
            prescience_client=prescience_client,
            sub_commands=[]
        )

    def init_from_subparser(self, subparsers, selector):
        super().init_from_subparser(subparsers, selector)
        self.cmd_parser.add_argument('id', nargs='?', type=str, help='Identifier of the model object to delete')

    def exec(self, args: dict):
        model_id = prompt_for_model_id_if_needed(args, self.prescience_client)
        self.prescience_client.delete_model(model_id=model_id)

