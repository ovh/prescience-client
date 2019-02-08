# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

from enum import Enum, unique, auto

@unique
class ScoringMetric(Enum):
    ACCURACY = auto()

    def __str__(self):
        switch = {
            ScoringMetric.ACCURACY: 'accuracy',
        }
        return switch.get(self)
