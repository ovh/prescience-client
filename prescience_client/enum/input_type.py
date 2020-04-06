# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

from enum import Enum, unique


@unique
class InputType(Enum):
    CSV = 'CSV'
    PARQUET = 'PARQUET'
    TIME_SERIE = 'TIME_SERIE'
    WARP_SCRIPT = 'WARP_SCRIPT'

    def __str__(self):
        return self.value

    def is_time_serie(self):
        return self == InputType.TIME_SERIE or self == InputType.WARP_SCRIPT
