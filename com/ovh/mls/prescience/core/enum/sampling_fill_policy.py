# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

from enum import Enum, unique, auto

@unique
class SamplingFillPolicy(Enum):
    FILLPREVIOUS = auto()
    FILLNEXT = auto()
    INTERPOLATE = auto()

    def __str__(self):
        switch = {
            SamplingFillPolicy.FILLPREVIOUS: 'FILLPREVIOUS',
            SamplingFillPolicy.FILLNEXT: 'FILLNEXT',
            SamplingFillPolicy.INTERPOLATE: 'INTERPOLATE',
        }
        return switch.get(self)