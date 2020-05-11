import pandas
from typing import List, NamedTuple

from prescience_client.utils import METRICS_MEASURE_COLUMN, DIMENSION_FORWARD, FOLD_COLUMN


class PredictionDataframe(NamedTuple):
    dataframe: pandas.DataFrame
    label: str
    time_column: str
    forward_steps: int
    grouping_keys: List[str]

    def compute_cube_from_prediction(self) -> pandas.DataFrame:
        cube = []
        only_test_df = self.dataframe[self.dataframe['fold'] == 'test']
        only_test_df = only_test_df[only_test_df[self.time_column] >= 1584883169670914.0]
        for _, row in only_test_df.iterrows():
            labels_theoric = row[f'{self.label}/forward_expected']
            labels_predicted = row[f'{self.label}/forward_real']
            expanded = [[labels_theoric[idx], labels_predicted[idx]] for idx in range(self.forward_steps)]
            for idx, label_row in enumerate(expanded):
                serie = {
                    METRICS_MEASURE_COLUMN: label_row,
                    self.time_column: row[self.time_column],
                    DIMENSION_FORWARD: idx,
                    FOLD_COLUMN: row[FOLD_COLUMN]
                }
                for key in self.grouping_keys:
                    serie[key] = row[key]
                cube.append(pandas.Series(serie))

        return pandas.DataFrame(cube)

    def get_predictions(self, date: int, query: str = None) -> pandas.DataFrame:
        wanted_date_df = self.dataframe[self.dataframe[self.time_column] == date]
        if query:
            wanted_date_df = wanted_date_df.query(query)
        all_rows = []
        for _, row in wanted_date_df.iterrows():
            base_serie = row[self.grouping_keys].to_dict()
            labels_theoric = row[f'{self.label}/forward_expected']
            labels_predicted = row[f'{self.label}/forward_real']
            labels_backward = row[f'{self.label}/past']
            time_forward = row[f'{self.time_column}/forward_expected']
            time_backward = row[f'{self.time_column}/past']
            for idx in range(self.forward_steps):
                serie_predicted = pandas.Series(base_serie)
                serie_predicted['kind'] = 'predicted'
                serie_predicted[self.time_column] = time_forward[idx]
                serie_predicted[self.label] = labels_predicted[idx]
                all_rows.append(serie_predicted)
                serie_theoric = pandas.Series(base_serie)
                serie_theoric['kind'] = 'theoric'
                serie_theoric[self.time_column] = time_forward[idx]
                serie_theoric[self.label] = labels_theoric[idx]
                all_rows.append(serie_theoric)
            for idx in range(len(time_backward)):
                serie_backward = pandas.Series(base_serie)
                serie_backward['kind'] = 'theoric'
                serie_backward[self.time_column] = time_backward[idx]
                serie_backward[self.label] = labels_backward[idx]
                all_rows.append(serie_backward)
        result = pandas.DataFrame(all_rows)
        groupby_keys = [self.time_column]
        groupby_keys.extend(self.grouping_keys)
        groupby_keys.append('kind')
        result = result.groupby(groupby_keys).sum().unstack()
        for _ in self.grouping_keys:
            result = result.unstack()
        return result

    def plot_prediction(self, date: int, query: str = None, block: bool = False) -> pandas.DataFrame:
        df_final = self.get_predictions(date, query=query)
        colors = []
        for column in df_final.columns.values:
            if 'theoric' in column[1]:
                colors.append('C0')
            else:
                colors.append('C1')
        df_final.plot(color=colors)
        return df_final
