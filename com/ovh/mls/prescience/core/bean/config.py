# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

from com.ovh.mls.prescience.core.utils.table_printable import DictPrintable


class Config(DictPrintable):

    def __init__(self, json_dict: dict):
        self.json_dict = json_dict

    def get_description_dict(self) -> dict:
        return self.json_dict

    def name(self):
        return self.json_dict.get('name', None)

    def class_identifier(self):
        return self.json_dict.get('class_identifier', None)

    def kwargs(self):
        return self.json_dict.get('kwargs', None)