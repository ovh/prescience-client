# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.
import json
import typing
from datetime import datetime

from prescience_client.enum.augmentation_strategy import AugmentationStrategy
from prescience_client.enum.input_type import InputType
from prescience_client.enum.sampling_strategy import SamplingStrategy


class TimeSerieFeature:
    selector: str
    labels: dict

    def __init__(self, selector: str, labels: str):
        self.selector = selector
        if labels:
            self.labels = json.loads(labels)
        else:
            self.labels = {}

    def to_dict(self):
        return {
            'selector': self.selector,
            'labels': self.labels
        }


class AugmentationFeature(typing.NamedTuple):
    augmentationStrategy: AugmentationStrategy
    windowSize: int

    @classmethod
    def from_dict(cls, inputdict: dict) -> 'AugmentationFeature':
        return AugmentationFeature(
            augmentationStrategy=inputdict.get('augmentation_strategy', None),
            windowSize=inputdict.get('window_size', None)
        )

    def to_dict(self):
        return {
            'augmentation_strategy': str(self.augmentationStrategy),
            'window_size': self.windowSize
        }


class WarpScriptInput(typing.NamedTuple):
    source_id: str
    backend_url: str
    read_token: str
    warp_script: str
    grouping_keys: list
    last_point_timestamp: int
    sample_span: str

    def to_dict(self) -> dict:
        """
        Convert the WarpScriptInput into payload dictionary
        :return: the payload dictionary
        """
        default_dict = {
            'type': str(InputType.WARP_SCRIPT),
            'source_id': str(self.source_id),
            'backend_url': str(self.backend_url),
            'read_token': str(self.read_token),
            'warp_script': str(self.warp_script),
            'sample_span': str(self.sample_span)
        }
        if self.grouping_keys:
            default_dict['grouping_keys'] = self.grouping_keys

        if self.last_point_timestamp:
            default_dict['last_point_timestamp'] = self.last_point_timestamp

        return default_dict

    @staticmethod
    def from_file(
            source_id: str,
            backend_url: str,
            read_token: str,
            file_path: str,
            sample_span: str,
            grouping_keys: list = None,
            last_point_timestamp: int = None,
    ) -> 'WarpScriptInput':
        with open(file_path, 'r') as file:
            data = file.read()

        if type(grouping_keys) == str:
            grouping_keys = grouping_keys.split(',')

        return WarpScriptInput(
            source_id=source_id,
            backend_url=backend_url,
            read_token=read_token,
            warp_script=data,
            grouping_keys=grouping_keys,
            last_point_timestamp=last_point_timestamp,
            sample_span=sample_span
        )


class Warp10TimeSerieInput(typing.NamedTuple):
    source_id: str
    read_token: str
    value: TimeSerieFeature
    last_point_date: datetime
    sample_span: str
    sampling_interval: str
    sampling_strategy: SamplingStrategy
    backend_url: str = 'https://warp10.gra1-ovh.metrics.ovh.net'
    exogeneous_features: list = []
    augmentation_features: list = []

    @staticmethod
    def get_type() -> InputType:
        return InputType.TIME_SERIE

    def to_dict(self) -> dict:
        """
        Convert the Warp10TimeSerieInput into payload dictionary
        :return: the payload dictionary
        """
        return {
            'source_id': self.source_id,
            'type': str(self.get_type()),
            'read_token': self.read_token,
            'value': self.value.to_dict(),
            'last_point_timestamp': datetime.timestamp(self.last_point_date) * 1000000 if self.last_point_date else None,
            'sample_span': self.sample_span,
            'sampling_interval': self.sampling_interval,
            'sampling_strategy': str(self.sampling_strategy),
            'backend_url': self.backend_url,
            'exogeneous_features': [x.to_dict() for x in self.exogeneous_features],
            'augmentation_features': [x.to_dict() for x in self.augmentation_features]
        }

    def add_exogeneous_feature(self, feature: TimeSerieFeature) -> 'Warp10TimeSerieInput':
        """
        Copy the current Warp10TimeSerieInput object while adding another exogenous feature
        :param feature: The new exogenous feature
        :return: A new Warp10TimeSerieInput object
        """
        return self._replace(exogeneous_features=self.exogeneous_features + [feature])

    def add_augmentation_feature(self, feature: AugmentationFeature) -> 'Warp10TimeSerieInput':
        """
        Copy the current Warp10TimeSerieInput object while adding another augmentation feature
        :param feature: The new augmentation feature
        :return: A new Warp10TimeSerieInput object
        """
        return self._replace(augmentation_features=self.augmentation_features + [feature])


class Warp10Scheduler(typing.NamedTuple):
    write_token: str
    frequency: str
    nb_steps: str
    output_value: TimeSerieFeature

    def to_dict(self) -> dict:
        """
        Convert the Warp10Scheduler into payload dictionary
        :return: the payload dictionary
        """
        return {
            'write_token': self.write_token,
            'frequency': self.frequency,
            'nb_steps': self.nb_steps,
            'output_value': self.output_value.to_dict(),
        }
