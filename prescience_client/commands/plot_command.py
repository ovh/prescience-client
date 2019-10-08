import matplotlib

from prescience_client.commands import prompt_for_source_id_if_needed, prompt_for_dataset_id_if_needed
from prescience_client.commands.command import Command
from prescience_client.enum.scoring_metric import ScoringMetric


class PlotCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='plot',
            help_message='Plot a prescience object',
            prescience_client=prescience_client,
            sub_commands=[
                PlotSourceCommand(prescience_client),
                PlotDatasetCommand(prescience_client),
                PlotPredictionCommand(prescience_client),
                PlotEvaluationsCommand(prescience_client),
                PlotRocCurveCommand(prescience_client)
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
        self.cmd_parser.add_argument('--x', type=str, help='Column that should be used as X axe')
        self.cmd_parser.add_argument('--y', type=str, help='Column that should be used as Y axe')
        self.cmd_parser.add_argument('--kind', type=str, help='Kind of the plot figure. Default: line')
        self.cmd_parser.add_argument('--class', type=str, help='Column that should be used as category if any (i.e class or label)')

    def exec(self, args: dict):
        source_id = prompt_for_source_id_if_needed(args, self.prescience_client)
        kind = args.get('kind')
        x = args.get('x')
        y = args.get('y')
        clss = args.get('class')
        self.prescience_client.plot_source(source_id=source_id, x=x, y=y, clss=clss, block=True, kind=kind)


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
        self.cmd_parser.add_argument('--fold', type=int, help='Fold number to plot')
        self.cmd_parser.add_argument('--no-test', default=True, dest='plot_test', action='store_false', help='Won\'t plot the test part')
        self.cmd_parser.add_argument('--no-train', default=True, dest='plot_train', action='store_false', help='Won\'t plot the train part')
        self.cmd_parser.add_argument('--x', type=str, help='Column that should be used as X axe')
        self.cmd_parser.add_argument('--y', type=str, help='Column that should be used as Y axe')
        self.cmd_parser.add_argument('--class', type=str, help='Column that should be used as category if any (i.e class or label)')

    def exec(self, args: dict):
        dataset_id = prompt_for_dataset_id_if_needed(args, self.prescience_client)
        plot_train = args.get('plot_train')
        plot_test = args.get('plot_test')
        fold = args.get('fold')
        x = args.get('x')
        y = args.get('y')
        clss = args.get('class')

        self.prescience_client.plot_dataset(
            dataset_id=dataset_id,
            block=True,
            plot_train=plot_train,
            plot_test=plot_test,
            fold_number=fold,
            x=x,
            y=y,
            clss=clss
        )



class PlotPredictionCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='predict',
            help_message='Plot a prediction made by a model',
            prescience_client=prescience_client,
            sub_commands=[]
        )

    def init_from_subparser(self, subparsers, selector):
        super().init_from_subparser(subparsers, selector)
        self.cmd_parser.add_argument('model-id', type=str,
                                     help='Identifier if the model object to make prediction on')
        self.cmd_parser.add_argument('--from-json', dest='from_json', type=str, default=None,
                                     help='Arguments to send as input of prescience model, it can be directly in json format, a filepath to a wanted payload. If unset as well as `--from-data` it will trigger the interactive mode.')
        self.cmd_parser.add_argument('--from-data',
                                     dest='from_data',
                                     type=int,
                                     help=f"Generate a prediction payload from an index in the initial data in case of a classification/regression problem or from the time value in case of a timeseries forecast problem. It will be saved as the default cached file for payload before sending to prescience-serving")
        self.cmd_parser.add_argument('--rolling', type=int, default=0, help='How many time do you want to roll on prediction (default: 0). It will only work if all inputs of your model are predicted by outputs.')


    def exec(self, args: dict):
        model_id = args.get('model-id')
        payload_json = args.get('from_json')
        from_data = args.get('from_data')
        rolling = args.get('rolling')

        payload_dict = self.prescience_client.generate_payload_dict_for_model(
            model_id=model_id,
            payload_json=payload_json,
            from_data=from_data
        )
        model = self.prescience_client.model(model_id)
        df_final = model.get_dataframe_for_plot_result(
            input_payload_dict=payload_dict,
            rolling_steps=rolling
        )
        df_final.plot()
        matplotlib.pyplot.show(block=True)

class PlotEvaluationsCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='evaluations',
            help_message='Plot the evolution of evaluations in an optimization process',
            prescience_client=prescience_client,
            sub_commands=[]
        )

    def init_from_subparser(self, subparsers, selector):
        super().init_from_subparser(subparsers, selector)
        self.cmd_parser.add_argument('id', type=str,
                                    help='The ID of the dataset. If unset if will trigger the interactive mode for selecting one.')
        self.cmd_parser.add_argument('scoring-metric', type=ScoringMetric, choices=list(ScoringMetric),
                                     help=f'The scoring metric to filter on. If unset it will trigger the interactive mode.')
        self.cmd_parser.add_argument('--forecasting-horizon-steps', type=int, help=f'The forecasting horizon steps to filter on (if any). If unset it will trigger the interactive mode.')
        self.cmd_parser.add_argument('--forecasting-discount', type=float, help=f'The forecasting discount to filter on (if any). If unset it will trigger the interactive mode.')


    def exec(self, args: dict):
        dataset_id = args.get('id')
        scoring_metric = args.get('scoring-metric')
        forecasting_horizon_steps = args.get('forecasting_horizon_steps')
        forecasting_discount = args.get('forecasting_discount')
        self.prescience_client.plot_evaluations(dataset_id, scoring_metric, forecasting_horizon_steps, forecasting_discount)


class PlotRocCurveCommand(Command):
    def __init__(self, prescience_client):
        super().__init__(
            name='roc',
            help_message='Plot the ROC curve of a wanted model',
            prescience_client=prescience_client,
            sub_commands=[]
        )

    def init_from_subparser(self, subparsers, selector):
        super().init_from_subparser(subparsers, selector)
        self.cmd_parser.add_argument('model-id', type=str, help='The ID of the model.')


    def exec(self, args: dict):
        model_id = args.get('model-id')
        self.prescience_client.plot_roc_curve(model_id=model_id, block=True)

