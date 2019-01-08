# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

from com.ovh.mls.prescience.core.bean.task import Task
from com.ovh.mls.prescience.core.client.prescience_client import PrescienceClient
from com.ovh.mls.prescience.core.enum.input_type import InputType


class LocalFileInput(object):
    def __init__(self,
                 input_type: InputType,
                 headers: bool,
                 filepath: str,
                 prescience: PrescienceClient = None):
        self.prescience = prescience
        self.input_type = input_type
        self.headers = headers
        self.filepath = filepath

    def parse(self, source_id: str) -> Task:
        return self.prescience.upload_source(
            source_id=source_id,
            input_type=self.input_type,
            headers=self.headers,
            filepath=self.filepath
        )


class CsvLocalFileInput(LocalFileInput):
    def __init__(self, filepath: str, headers: bool = True, prescience: PrescienceClient = None):
        super(CsvLocalFileInput, self).__init__(
            input_type=InputType.CSV,
            headers=headers,
            filepath=filepath,
            prescience=prescience
        )
