# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

from prescience_client.bean.model_metric.base import Base
from prescience_client.enum.scoring_metric import ScoringMetricMulticlass


class Multiclass(Base):
    """
    Prescience Model metric object for multiclass scores
    """

    @classmethod
    def scoring_metrics(cls):
        return list(map(str, ScoringMetricMulticlass))
