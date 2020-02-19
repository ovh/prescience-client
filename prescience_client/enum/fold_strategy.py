# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

from enum import Enum, unique


@unique
class FoldStrategy(Enum):
    WINDOW = 'WINDOW'
    ROLLING = 'ROLLING'
    STRATIFIED = 'STRATIFIED'
    UNIFORM = 'UNIFORM'

    def __str__(self):
        return self.value
