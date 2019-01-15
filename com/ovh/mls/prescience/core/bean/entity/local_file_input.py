# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

from com.ovh.mls.prescience.core.bean.task import Task
from com.ovh.mls.prescience.core.client.prescience_client import PrescienceClient
from com.ovh.mls.prescience.core.enum.input_type import InputType


class LocalFileInput(object):
    """
    Local data file object that will be upload to prescience
    """
    def __init__(self,
                 input_type: InputType,
                 headers: bool,
                 filepath: str,
                 prescience: PrescienceClient = None):
        """
        Contructor of LocalFileInput
        :param input_type: The type of input
        :param headers: Has the input file header ?
        :param filepath: The path of the input file
        :param prescience: The prescience client (default: None)
        """
        self.prescience = prescience
        self.input_type = input_type
        self.headers = headers
        self.filepath = filepath

    def parse(self, source_id: str) -> Task:
        """
        Upload the current local file input on prescience and launch a Parse Task on it for creating a source.
        :param source_id: The id that we want for the source
        :return: The task object of the Parse Task
        """
        return self.prescience.upload_source(
            source_id=source_id,
            input_type=self.input_type,
            headers=self.headers,
            filepath=self.filepath
        )


class CsvLocalFileInput(LocalFileInput):
    """
    Local data file of type CSV
    """
    def __init__(self, filepath: str, headers: bool = True, prescience: PrescienceClient = None):
        super(CsvLocalFileInput, self).__init__(
            input_type=InputType.CSV,
            headers=headers,
            filepath=filepath,
            prescience=prescience
        )
