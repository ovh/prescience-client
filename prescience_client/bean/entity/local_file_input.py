# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

import os

from prescience_client.bean.task import Task
from prescience_client.client.prescience_client import PrescienceClient
from prescience_client.enum.input_type import InputType
from prescience_client.enum.separator import Separator
from prescience_client.exception.prescience_client_exception import PrescienceClientException


class LocalFileInput(object):
    """
    Local data file object that will be upload to prescience
    """

    def __init__(self,
                 input_type: InputType,
                 headers: bool,
                 separator: Separator,
                 filepath: str,
                 prescience: PrescienceClient = None):
        """
        Contructor of LocalFileInput
        :param input_type: The type of input
        :param headers: Has the input file header ?
        :param separator: CSV Separator
        :param filepath: The path of the input file
        :param prescience: The prescience client (default: None)
        """
        self.prescience = prescience
        self.input_type = input_type
        self.headers = headers
        self.filepath = filepath
        self.separator = separator

    @classmethod
    def default_source_id_and_type(cls, filepath) -> (str, InputType):
        if os.path.isdir(filepath):
            return os.path.dirname(filepath), InputType.PARQUET
        elif os.path.isfile(filepath):
            base = os.path.basename(filepath)
            split_text = os.path.splitext(base)
            extension = split_text[1]
            if extension == '.csv':
                file_type = InputType.CSV
            elif extension == '.parquet':
                file_type = InputType.PARQUET
            else:
                file_type = None
            return split_text[0], file_type
        else:
            raise PrescienceClientException(Exception(f'{filepath} is neither a file or a directory'))

    def parse(self, source_id: str = None) -> Task:
        """
        Upload the current local file input on prescience and launch a Parse Task on it for creating a source.
        :param source_id: The id that we want for the source
        :return: The task object of the Parse Task
        """
        if source_id is None:
            source_id, _ = LocalFileInput.default_source_id_and_type(self.filepath)

        sent_input_type = self.input_type
        if sent_input_type is None:
            _, guessed_input_type = LocalFileInput.default_source_id_and_type(self.filepath)
            sent_input_type = guessed_input_type
        if sent_input_type is None:
            raise PrescienceClientException(Exception(f'Unable to infer InputType for file {self.filepath}'))

        return self.prescience.upload_source(
            source_id=source_id,
            input_type=sent_input_type,
            separator=self.separator,
            headers=self.headers,
            filepath=self.filepath
        )

class CsvLocalFileInput(LocalFileInput):
    """
    Local data file of type CSV
    """

    def __init__(
            self,
            filepath: str,
            headers: bool = True,
            separator: Separator = Separator.COMMA,
            prescience: PrescienceClient = None
    ):
        super(CsvLocalFileInput, self).__init__(
            input_type=InputType.CSV,
            headers=headers,
            separator=separator,
            filepath=filepath,
            prescience=prescience
        )


class ParquetLocalFileInput(LocalFileInput):
    """
    Local data file of type Parquet
    """

    def __init__(self, filepath: str, prescience: PrescienceClient = None):
        super(ParquetLocalFileInput, self).__init__(
            input_type=InputType.PARQUET,
            headers=True,
            separator=None,
            filepath=filepath,
            prescience=prescience
        )
