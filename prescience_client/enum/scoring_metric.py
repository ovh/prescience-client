# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.
from enum import Enum, unique

from prescience_client.enum.problem_type import ProblemType

@unique
class ScoringMetric(Enum):
    def __str__(self):
        return self.value

@unique
class ScoringMetricBinary(ScoringMetric):
    # Classification
    ACCURACY = 'accuracy'
    COHEN_KAPPA = 'cohen_kappa'
    # Binary
    F1 = 'f1'
    ROC_AUC = 'roc_auc'
    PRECISION = 'precision'
    RECALL = 'recall'
    LOG_LOSS = 'log_loss'


@unique
class ScoringMetricMulticlass(ScoringMetric):
    # Classification
    ACCURACY = 'accuracy'
    COHEN_KAPPA = 'cohen_kappa'
    # MulticlassScoringMetric
    F1_MICRO = 'f1_micro'
    F1_MACRO = 'f1_macro'
    ROC_AUC_MICRO = 'roc_auc_micro'
    ROC_AUC_MACRO = 'roc_auc_macro'
    AVERAGE_PRECISION_MICRO = 'average_precision_micro'
    AVERAGE_PRECISION_MACRO = 'average_precision_macro'


@unique
class ScoringMetricRegression(ScoringMetric):
    # RegressionScoringMetric
    MAE = 'mae'
    MSE = 'mse'
    MAPE = 'mape'
    R2 = 'r2'


def get_scoring_metrics(problem_type, label_id, source):
    if problem_type == ProblemType.REGRESSION or problem_type == ProblemType.TIME_SERIES_FORECAST:
        return list(map(str, ScoringMetricRegression))
    else:
        if source.is_multiclass(label_id):
            return list(map(str, ScoringMetricMulticlass))
        else:
            return list(map(str, ScoringMetricBinary))
