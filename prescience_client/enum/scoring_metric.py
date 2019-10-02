# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

from enum import Enum, unique


@unique
class ScoringMetric(Enum):

    # Classificaton
    ACCURACY = 'accuracy'
    COHEN_KAPPA = 'cohen_kappa'
    # Binary
    F1 = 'f1'
    ROC_AUC = 'roc_auc'
    PRECISION = 'precision'
    RECALL = 'recall'
    LOG_LOSS = 'log_loss'
    # Multiclass
    F1_MICRO = 'f1_micro'
    F1_MACRO = 'f1_macro'
    ROC_AUC_MICRO = 'roc_auc_micro'
    ROC_AUC_MACRO = 'roc_auc_macro'
    AVERAGE_PRECISION_MICRO = 'average_precision_micro'
    AVERAGE_PRECISION_MACRO = 'average_precision_macro'
    # Regression
    MAE = 'mae'
    MSE = 'mse'
    MAPE = 'mape'
    R2 = 'r2'

    def __str__(self):
        return self.value