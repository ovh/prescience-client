# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

from prescience_client.client.prescience_client import PrescienceClient
from prescience_client.config.prescience_config import PrescienceConfig


class Singletons:
    config = PrescienceConfig().load()

    prescience: PrescienceClient = PrescienceClient(config)


prescience: PrescienceClient = Singletons.prescience
