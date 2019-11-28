# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

import copy
from abc import ABC, abstractmethod

from prescience_client.utils.table_printable import TablePrintable, DictPrintable
from prescience_client.enum.output_format import OutputFormat


class Base(TablePrintable, DictPrintable, ABC):
    """
    Prescience Model metric object
    Inherit from TablePrintable so that it can be easily printed as list on stdout
    Inherit from DictPrintable so that it can be easily printed as single dict object on stdout
    """

    @abstractmethod
    @classmethod
    def scoring_metrics(cls):
        raise NotImplementedError

    def get_description_dict(self) -> dict:
        return copy.copy(self.json_dict)

    def table_row(self, output: OutputFormat) -> dict:
        return {
            scoring_metric: self.get_metric(scoring_metric) for scoring_metric in self.scoring_metrics()
        }

    @classmethod
    def table_header(cls) -> list:
        return cls.scoring_metrics()

    def __init__(self,
                 json: dict):
        """
        Constructor of prescience model metric object
        :param json: the source JSON dict received from prescience
        """
        self.json_dict = json

    def get_scores(self):
        return self.json_dict.get('scores')

    def get_metric(self, scoring_metric):
        return self.get_scores().get(str(scoring_metric)).get('value')
