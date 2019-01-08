# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

import copy
import json
from com.ovh.mls.prescience.core.bean.schema import Schema
from com.ovh.mls.prescience.core.client.prescience_client import PrescienceClient
from com.ovh.mls.prescience.core.config.constants import DEFAULT_LABEL_NAME, DEFAULT_PROBLEM_TYPE
from com.ovh.mls.prescience.core.enum.problem_type import ProblemType
from com.ovh.mls.prescience.core.enum.status import Status
from com.ovh.mls.prescience.core.utils.table_printable import TablePrintable, DictPrintable
from com.ovh.mls.prescience.core.utils.tree_printer import SourceTree
from termcolor import colored


class Source(TablePrintable, DictPrintable):

    def __init__(
            self,
            json_dict: dict,
            prescience: PrescienceClient = None):
        self.json_dict = json_dict
        self.uuid = json_dict.get('uuid', None)
        self.created_at = json_dict.get('created_at', None)
        self.last_update = json_dict.get('last_update', None)
        self.current_step_description = json_dict.get('current_step_description', None)
        self.source_id = json_dict.get('source_id', None)
        self.input_url = json_dict.get('input_url', None)
        self.input_type = json_dict.get('input_type', None)
        self.source_url = json_dict.get('source_url', None)
        self.headers = json_dict.get('headers', None)
        self.selected = False
        self.prescience = prescience

    def set_selected(self):
        self.selected = True

    def get_description_dict(self) -> dict:
        description_dict = copy.copy(self.json_dict)
        description_dict['status'] = self.status()
        return description_dict

    def schema(self):
        schema_dict = self.json_dict.get('schema', None)
        if schema_dict is not None:
            return Schema(json.loads(schema_dict))
        else:
            return None

    @classmethod
    def table_header(cls) -> list:
        return ['source_id', 'status', 'input_type', 'info']

    def table_row(self) -> dict:
        return {
            'source_id': self.source_id,
            'status': self.status(),
            'input_type': self.input_type,
            'info': self.current_step_description
        }

    def __str__(self):
        status = self.status()

        main_name = 'Source'
        if self.selected:
            main_name = colored(main_name, 'yellow')

        return f'{main_name}({colored(self.source_id, status.color())})'

    def status(self) -> Status:
        return Status[self.json_dict['status']]

    def delete(self):
        self.prescience.delete_source(self.source_id)

    def preprocess(self,
                   dataset_id: str,
                   label: str = DEFAULT_LABEL_NAME,
                   problem_type: ProblemType = DEFAULT_PROBLEM_TYPE,
                   selected_column: list = None,
                   time_column: str = None,
                   fold_size: int = -1):
        return self.prescience.preprocess(
            source_id=self.source_id,
            dataset_id=dataset_id,
            label_id=label,
            problem_type=problem_type,
            selected_column=selected_column,
            time_column=time_column,
            fold_size=fold_size
        )

    def tree(self) -> SourceTree:
        return SourceTree(source_id=self.source_id, selected_source=self.source_id)
