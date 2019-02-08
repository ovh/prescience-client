# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

from enum import Enum, unique, auto

@unique
class SamplingStrategy(Enum):
    MEAN = auto()
    FIRST = auto()
    LAST = auto()
    MAX = auto()
    MIN = auto()
    MEDIAN = auto()

    def __str__(self):
        switch = {
            SamplingStrategy.MEAN: 'MEAN',
            SamplingStrategy.FIRST: 'FIRST',
            SamplingStrategy.LAST: 'LAST',
            SamplingStrategy.MAX: 'MAX',
            SamplingStrategy.MIN: 'MIN',
            SamplingStrategy.MEDIAN: 'MEDIAN',
        }
        return switch.get(self)
