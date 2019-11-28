# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.
from prescience_client.bean.model_metric.binary import Binary
from prescience_client.bean.model_metric.multiclass import Multiclass
from prescience_client.bean.model_metric.regression import Regression
from prescience_client.enum.problem_type import ProblemType

__all__ = ['Binary', 'Multiclass', 'Regression', 'get_model_metric']


def get_model_metric(json_scores, model):
    if model.problem_type() in [ProblemType.TIME_SERIES_FORECAST, ProblemType.REGRESSION]:
        return Regression(json_scores)
    else:
        if model.source().is_multiclass(model.label_id()):
            return Multiclass(json_scores)
        else:
            return Binary(json_scores)
