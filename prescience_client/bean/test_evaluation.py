# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

import copy
from prescience_client.client.prescience_client import PrescienceClient
from prescience_client.utils.table_printable import TablePrintable, DictPrintable
from prescience_client.enum.output_format import OutputFormat

class TestEvaluations(TablePrintable, DictPrintable):

    def get_description_dict(self) -> dict:
        return copy.copy(self.json_dict)

    def table_row(self, output: OutputFormat) -> dict:
        return {}

    @classmethod
    def table_header(cls) -> list:
        return []

    def __init__(self,
                 json: dict,
                prescience: PrescienceClient = None):
        """
        Constructor of prescience test evaluation object
        :param json: the source JSON dict received from prescience
        :param prescience: the prescience client (default: None)
        """
        self.json_dict = json
        self.prescience = prescience