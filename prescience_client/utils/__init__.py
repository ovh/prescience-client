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
        join: bool = True
):
    last_input_points = {key: value[-1] for key, value in series_dict_input.items()}
    last_predict_points = {key: value[-1] for key, value in series_dict_predict.items()}

    if join:
        # Adding last points of real to predict dict
        for key, _ in series_dict_predict.items():
            last_value = last_input_points[key]
            series_dict_predict[key].append(last_value)

    df_theoric = initial_dataframe[list(series_dict_predict.keys())]
    df_theoric = filter_dataframe_on_time_feature(
        df=df_theoric,
        time_feature=time_feature_name,
        min_bound=last_input_points[time_feature_name] -1, # -1 is because 'min_bound' is excluded
        max_bound=last_predict_points[time_feature_name]
    )
    df_theoric = df_theoric.set_index(time_feature_name)
    df_theoric = df_theoric.rename(columns={k: f'{k}_theoric' for k in list(df_theoric.columns)})

    df_input = get_dataframe_from_series_dict(series_dict_input, time_feature_name, '_input')
    df_predict = get_dataframe_from_series_dict(series_dict_predict, time_feature_name, '_predicted')


    df_final = pandas.concat([df_input, df_predict, df_theoric], axis='columns', sort=True)
    return df_final


def filter_dataframe_on_time_feature(
        df: pandas.DataFrame,
        time_feature: str,
        min_bound: int,
        max_bound: int
):
    filtered = df.loc[(df[time_feature] > min_bound) & (df[time_feature] <= max_bound)]
    return filtered

def dataframe_to_dict_series(df: pandas.DataFrame):
    return {k: list(v.values()) for k, v in df.to_dict().items()}