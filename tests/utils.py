# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

import os

RESOURCE_DIRECTORY = 'resources'

def get_resource_file_path(filename: str) -> str:
    return os.path.join(os.path.dirname(__file__), RESOURCE_DIRECTORY, filename)