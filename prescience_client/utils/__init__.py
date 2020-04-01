# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.
import pandas

# def get_dataframe_from_series_dict(series_dict: dict, time_feature_name: str, suffix: str):
#     index_serie = series_dict.pop(time_feature_name)
#     df = pandas.DataFrame(series_dict, index=index_serie)
#     df['kind'] = suffix
#     return df
#
#     # return df.rename(columns={k: f'{k}{suffix}' for k, _ in series_dict.items()})

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