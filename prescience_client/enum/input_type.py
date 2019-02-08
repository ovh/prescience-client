# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

from enum import Enum, unique, auto

@unique
class InputType(Enum):
    CSV = auto()
    PARQUET = auto()
    TIME_SERIE = auto()

    def __str__(self):
        switch = {
            InputType.CSV: 'CSV',
            InputType.PARQUET: 'PARQUET',
            InputType.TIME_SERIE: 'TIME_SERIE'
        }
        return switch.get(self)
