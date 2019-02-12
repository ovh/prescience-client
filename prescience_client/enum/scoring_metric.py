# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

from enum import Enum, unique


@unique
class ScoringMetric(Enum):
    ACCURACY = 'accuracy'
    MSE = 'mse'
    LOG_LOSS = 'log_loss'

    def __str__(self):
        return self.value