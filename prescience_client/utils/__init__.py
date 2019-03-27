# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.
import pandas

def get_dataframe_from_series_dict(series_dict: dict, time_feature_name: str):
    index_serie = series_dict.pop(time_feature_name)
    df = pandas.DataFrame(series_dict, index=index_serie)
    return df

def get_dataframe_real_predict_theoric(
        series_dict_real: dict,
        series_dict_predict: dict,
        series_dict_theoric: dict,
        time_feature_name: str,
        labels_names: list,
        join: bool = True
):
    last_real_points = {key: value[-1] for key, value in series_dict_real.items()}

    if join:
        # # Adding last points of real to theoric dict
        # for key, _ in series_dict_theoric.items():
        #     last_value = last_real_points[key]
        #     series_dict_theoric[key].append(last_value)

        # Adding last points of real to predict dict
        for key, _ in series_dict_predict.items():
            last_value = last_real_points[key]
            series_dict_predict[key].append(last_value)

    df_real = get_dataframe_from_series_dict(series_dict_real, time_feature_name)
    # df_theoric = get_dataframe_from_series_dict(series_dict_theoric, time_feature_name)
    df_predict = get_dataframe_from_series_dict(series_dict_predict, time_feature_name)
    df_final = pandas.concat([df_real, df_predict], axis='columns', sort=True)
    return df_final