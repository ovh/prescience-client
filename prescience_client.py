# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

from com.ovh.mls.prescience.core.client.prescience_client import PrescienceClient
from com.ovh.mls.prescience.core.config.prescience_config import PrescienceConfig

config = PrescienceConfig().load()
prescience: PrescienceClient = PrescienceClient(config)