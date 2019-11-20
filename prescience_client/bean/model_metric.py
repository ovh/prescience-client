# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

import copy
from prescience_client.client.prescience_client import PrescienceClient
from prescience_client.utils.table_printable import TablePrintable, DictPrintable
from prescience_client.enum.output_format import OutputFormat
from prescience_client.enum.scoring_metric import ScoringMetric

class ModelMetric(TablePrintable, DictPrintable):
    """
    Prescience Model metric object
    Inherit from TablePrintable so that it can be easily printed as list on stdout
    Inherit from DictPrintable so that it can be easily printed as single dict object on stdout
    """

    def get_description_dict(self) -> dict:
        return copy.copy(self.json_dict)

    def table_row(self, output: OutputFormat) -> dict:
        return {
            str(ScoringMetric.ACCURACY): self.get_accuracy(),
            str(ScoringMetric.LOG_LOSS): self.get_log_loss(),
            str(ScoringMetric.ROC_AUC): self.get_roc()
        }

    @classmethod
    def table_header(cls) -> list:
        return [str(x) for x in [ScoringMetric.ACCURACY, ScoringMetric.LOG_LOSS, ScoringMetric.ROC_AUC]]

    def __init__(self,
                 json: dict,
                prescience: PrescienceClient = None):
        """
        Constructor of prescience model metric object
        :param json: the source JSON dict received from prescience
        :param prescience: the prescience client (default: None)
        """
        self.json_dict = json
        self.prescience = prescience

    def get_scores(self):
        return self.json_dict.get('scores')

    def get_roc(self):
        return self.get_scores().get(str(ScoringMetric.ROC_AUC)).get('value')

    def get_log_loss(self):
        return self.get_scores().get(str(ScoringMetric.LOG_LOSS)).get('value')

    def get_accuracy(self):
        return self.get_scores().get(str(ScoringMetric.ACCURACY)).get('value')