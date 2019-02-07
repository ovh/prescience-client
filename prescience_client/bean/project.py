# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

import json

class Project(object):
    """
    Prescience Project object
    """
    def __init__(self, json_dict: dict):
        """
        Constructor of Project object
        :param json_dict: the source JSON dict received from prescience
        """
        self.uuid = json_dict['uuid']
        self.name = json_dict['name']
        self.created_at = json_dict['created_at']
        self.last_update = json_dict['last_update']

    def __str__(self):
        return json.dumps(self.__dict__)
