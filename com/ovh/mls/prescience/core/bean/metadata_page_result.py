# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

import json

class MetadataPageResult(object):
    """
    Prescience MetadataPageResult object
    """
    def __init__(self, json_dict: dict):
        self.page_number = json_dict['page_number']
        self.total_pages = json_dict['total_pages']
        self.elements_on_page = json_dict['elements_on_page']
        self.elements_total = json_dict['elements_total']
        self.elements_type = json_dict['elements_type']

    def __str__(self):
        return json.dumps(self.__dict__)