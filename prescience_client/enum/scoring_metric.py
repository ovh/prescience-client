# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

from enum import Enum, unique


@unique
class ScoringMetric(Enum):
    ACCURACY = 'accuracy'
    LOG_LOSS = 'log_loss'

    def __str__(self):
        switch = {
            ScoringMetric.ACCURACY: 'accuracy',
            ScoringMetric.LOG_LOSS: 'log_loss',
        }
        return switch.get(self)
