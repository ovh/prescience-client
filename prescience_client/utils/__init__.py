# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.
import matplotlib
import pandas
import os

METRICS_MEASURE_COLUMN = 'label_theoric/label_predicted'
DIMENSION_FORWARD = 'forward_step'


def mae(serie: pandas.Series):
    all_theoric_predicted = serie.tolist()
    squared = [abs(x[0] - x[1]) for x in all_theoric_predicted]
    return sum(squared) / len(squared)


def mse(serie: pandas.Series):
    all_theoric_predicted = serie.tolist()
    squared = [(x[0] - x[1]) ** 2 for x in all_theoric_predicted]
    return sum(squared) / len(squared)


def metrics_regression():
    return {
        'mse': mse,
        'mae': mae
    }


def get_dataframe_real_predict_theoric(
        series_dict_input: dict,
        series_dict_predict: dict,
        time_feature_name: str,
        initial_dataframe: pandas.DataFrame,
        label_id: str,
        join: bool = True
):
    # Only filter on label for prediction (ex: remove quantiles)
    series_dict_predict = {k: v for k, v in series_dict_predict.items() if k in {label_id, time_feature_name}}

    last_input_points = {key: value[-1] for key, value in series_dict_input.items()}
    last_input_points_time = last_input_points[time_feature_name]

    forward_steps = len(series_dict_predict[time_feature_name])

    if join:
        # Adding last points of real to predict dict
        for key, _ in series_dict_predict.items():
            last_value = last_input_points.get(key)
            series_dict_predict[key].append(last_value)

    intersect = set(series_dict_predict.keys()).intersection(set(initial_dataframe.columns))
    df_theoric = initial_dataframe[list(intersect)]
    df_theoric = df_theoric\
        .set_index(time_feature_name)\
        .truncate(before=last_input_points_time)\
        .head(forward_steps + 1)\
        .reset_index()
    df_theoric['kind'] = 'theoric'
    df_theoric = df_theoric[[time_feature_name, label_id, 'kind']]
    df_theoric = df_theoric.set_index(time_feature_name).sort_index().reset_index()

    df_input = pandas.DataFrame(series_dict_input)
    df_input['kind'] = 'input'
    df_input = df_input[[time_feature_name, label_id, 'kind']]
    df_input = df_input.set_index(time_feature_name).sort_index().reset_index()

    df_predict = pandas.DataFrame(series_dict_predict)
    df_predict['kind'] = 'predict'
    df_predict = df_predict[[time_feature_name, label_id, 'kind']]
    df_predict = df_predict.set_index(time_feature_name).sort_index().reset_index()
    # To avoid different timescale between predicted time scale and the one present in source
    df_predict[time_feature_name] = df_theoric[time_feature_name]

    df_final = pandas.concat([df_input, df_predict, df_theoric]).groupby([time_feature_name, 'kind']).sum().unstack()
    return df_final


def filter_dataframe_on_index(
        df: pandas.DataFrame,
        index,
        min_bound,
        max_bound
):
    filtered = df[(df[index] >= min_bound) & (df[index] <= max_bound)]
    return filtered.set_index(keys=index, drop=False)


def dataframe_to_dict_series(df: pandas.DataFrame):
    return {k: list(v.values()) for k, v in df.to_dict().items()}


def compute_prediction_df(
        source_dataframe: pandas.DataFrame,
        time_column: str,
        label: str,
        grouping_keys: list,
        past_steps: int,
        forward_steps: int,
        selected_column: list,
        prediction_lambda
) -> pandas.DataFrame:
    my_dict = {}

    def rolling_lambda(x, column):
        if not my_dict.get(column):
            my_dict[column] = []
        my_dict[column].append(list(x))
        return 0

    agg_dict = {
        time_column: lambda x: rolling_lambda(x, time_column),
        label: lambda x: rolling_lambda(x, label)
    }

    prediction_df = source_dataframe \
        .set_index(time_column, drop=False) \
        .sort_index() \
        .groupby(grouping_keys) \
        .rolling(past_steps + forward_steps) \
        .agg(agg_dict) \
        .dropna()

    for k, v in my_dict.items():
        all_window = [(window[:past_steps], window[past_steps:]) for window in v]
        past_windows = [windows[0] for windows in all_window]
        forward_windows = [windows[1] for windows in all_window]
        prediction_df[(k, 'past')] = past_windows
        prediction_df[(k, 'forward_expected')] = forward_windows
        prediction_df.drop(columns=[k], inplace=True)

    prediction_df.reset_index(inplace=True)
    # Setting the time column to the time the prediction is made on
    prediction_df[time_column] = [x[-1] for x in prediction_df[(time_column, 'past')].values.tolist()]

    # Getting predictions from model
    prediction = {(label, 'forward_real'): []}
    for _, row in prediction_df.iterrows():
        query_payload = {
            time_column: row[(time_column, 'past')],
            label: row[(label, 'past')]
        }
        for key in grouping_keys:
            if key in selected_column:
                query_payload[key] = [row[key]] * past_steps

        series_dict_predict = prediction_lambda(query_payload)[label]
        prediction[(label, 'forward_real')].append(series_dict_predict)
        print(query_payload)

    # Add columns for predictions in dataframe
    for k, v in prediction.items():
        prediction_df[k] = v

    return prediction_df


def compute_cube_from_prediction(
        prediction_dataframe: pandas.DataFrame,
        label: str,
        time_column: str,
        forward_steps: int,
        grouping_keys: list
) -> pandas.DataFrame:
    cube = []
    for index, row in prediction_dataframe.iterrows():
        labels_theoric = row[(label, 'forward_expected')]
        labels_predicted = row[(label, 'forward_real')]
        expanded = [[labels_theoric[idx], labels_predicted[idx]] for idx in range(forward_steps)]
        for idx, label_row in enumerate(expanded):
            serie = {
                METRICS_MEASURE_COLUMN: label_row,
                time_column: row[time_column],
                DIMENSION_FORWARD: idx
            }
            for key in grouping_keys:
                serie[key] = row[key]
            cube.append(pandas.Series(serie))

    return pandas.DataFrame(cube)


def compute_cube_agg(df_or_path, dimensions: list, measure: str, unstack: bool = False) -> pandas.DataFrame:

    if isinstance(df_or_path, str):
        path = df_or_path
        df = pandas.read_parquet(path)
    else:
        df = df_or_path

    agg_lambda = metrics_regression()[measure]

    if dimensions is None or len(dimensions) == 0:
        atomic_result = agg_lambda(df[METRICS_MEASURE_COLUMN])
        agg_result = pandas.DataFrame([[atomic_result]], index=[measure])
    else:
        agg_result = df.groupby(dimensions).agg({METRICS_MEASURE_COLUMN: agg_lambda})
        if unstack and len(dimensions) > 1:
            agg_result = agg_result.unstack()
        agg_result.rename(columns={METRICS_MEASURE_COLUMN: measure}, inplace=True)

    return agg_result


def plot_df(df: pandas.DataFrame, kind: str = None, block: bool = False):
    df.plot(kind=kind)
    matplotlib.pyplot.show(block=block)
