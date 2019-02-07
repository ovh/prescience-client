# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

from enum import Enum, unique, auto

@unique
class AugmentationStrategy(Enum):
    MIN = auto()
    MAD = auto()
    MAX = auto()
    MEAN = auto()
    SD = auto()

    def __str__(self):
        switch = {
            AugmentationStrategy.MIN: 'MIN',
            AugmentationStrategy.MAD: 'MAD',
            AugmentationStrategy.MAX: 'MAX',
            AugmentationStrategy.MEAN: 'MEAN',
            AugmentationStrategy.SD: 'SD',
        }
        return switch.get(self)
