# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

from enum import Enum, unique, auto

@unique
class FlowType(Enum):
    MODEL = auto()
    TRANSFORM = auto()
    TRANSFORM_MODEL = auto()

    def __str__(self):
        switch = {
            FlowType.MODEL: 'model',
            FlowType.TRANSFORM: 'transform',
            FlowType.TRANSFORM_MODEL: 'transform-model'
        }
        return switch.get(self)