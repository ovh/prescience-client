# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.
import pandas

def get_dataframe_from_series_dict(series_dict: dict, time_feature_name: str, suffix: str):
    index_serie = series_dict.pop(time_feature_name)
    df = pandas.DataFrame(series_dict, index=index_serie)

    return df.rename(columns={k: f'{k}{suffix}' for k, _ in series_dict.items()})

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
    last_predict_points = {key: value[-1] for key, value in series_dict_predict.items()}

    if join:
        # Adding last points of real to predict dict
        for key, _ in series_dict_predict.items():
            last_value = last_input_points.get(key)
            series_dict_predict[key].append(last_value)

    intersect = set(series_dict_predict.keys()).intersection(set(initial_dataframe.columns))
    df_theoric = initial_dataframe[list(intersect)]
    df_theoric = filter_dataframe_on_index(
        df=df_theoric,
        index=time_feature_name,
        min_bound=last_input_points[time_feature_name],
        max_bound=last_predict_points[time_feature_name]
    )
    df_theoric = df_theoric.set_index(time_feature_name)
    df_theoric = df_theoric.rename(columns={k: f'{k}_theoric' for k in list(df_theoric.columns)})

    df_input = get_dataframe_from_series_dict(series_dict_input, time_feature_name, '_input')
    df_predict = get_dataframe_from_series_dict(series_dict_predict, time_feature_name, '_predicted')


    df_final = pandas.concat([df_input, df_predict, df_theoric], axis='columns', sort=True)
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