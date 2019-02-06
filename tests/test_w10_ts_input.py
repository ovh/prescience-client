# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

import unittest
import datetime

from com.ovh.mls.prescience.core.bean.entity.w10_ts_input import Warp10TimeSerieInput, TimeSerieFeature, \
    AugmentationFeature
from com.ovh.mls.prescience.core.enum.augmentation_strategy import AugmentationStrategy
from com.ovh.mls.prescience.core.enum.sampling_strategy import SamplingStrategy


class TestPrescienceConfig(unittest.TestCase):

    def test_to_dict(self):
        input_payload = Warp10TimeSerieInput(
            source_id='my_source_id',
            read_token='AZERTY',
            value=TimeSerieFeature(
                selector='ml.kpi.global.selector',
                labels={
                    'kpi': 'label1'
                }
            ),
            last_point_date=datetime.datetime(2018,1,1,0,0,0,0),
            sample_span="100w",
            sampling_interval="1d",
            sampling_strategy=SamplingStrategy.MEAN,
        )

        input_payload = input_payload.add_augmentation_feature(
            AugmentationFeature(
            augmentationStrategy=AugmentationStrategy.MEAN,
            windowSize=5
            )
        )
        input_payload = input_payload.add_exogeneous_feature(
            TimeSerieFeature(
                selector='ml.kpi.global.selector2',
                labels={
                    'kpi2': 'label2'
                }
            )
        )

        expected_dict = {
            'source_id': 'my_source_id',
            'read_token': 'AZERTY',
            'type': 'TIME_SERIE',
            'value': {
                'selector': 'ml.kpi.global.selector',
                'labels': {
                    'kpi': 'label1'
                }
            },
            'last_point_date': '2018-01-01T00:00:00',
            'sample_span': '100w',
            'sampling_interval': '1d',
            'sampling_strategy': 'MEAN',
            'backend_url': 'https://warp10.gra1-ovh.metrics.ovh.net',
            'exogeneous_features': [{
                'selector': 'ml.kpi.global.selector2',
                'labels': {
                    'kpi2': 'label2'
                }
            }],
            'augmentation_features': [{
                'augmentation_strategy': 'MEAN',
                'window_size': 5
            }]
        }

        output_dict = input_payload.to_dict()
        self.assertEqual(expected_dict, output_dict)
