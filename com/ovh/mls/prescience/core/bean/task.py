# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

from com.ovh.mls.prescience.core.client.prescience_client import PrescienceClient
from com.ovh.mls.prescience.core.enum.status import Status
from com.ovh.mls.prescience.core.utils.table_printable import TablePrintable

class TaskFactory:
    @staticmethod
    def construct(task_dict: dict, prescience: PrescienceClient = None):
        generic_task = Task(task_dict)
        switch = {
            'parse': ParseTask,
            'preprocess': PreprocessTask,
            'train': TrainTask
        }
        constructor = switch.get(generic_task.type(), Task)
        return constructor(task_dict, prescience)


class Task(TablePrintable):

    def __init__(self,
                 json: dict,
                prescience: PrescienceClient = None):
        self.initial_payload:dict = json
        self.prescience = prescience

    @classmethod
    def table_header(cls) -> list:
        return ['uuid', 'type', 'steps', 'info', 'status']

    def table_row(self) -> dict:
        return {
            'uuid': self.uuid(),
            'type': self.type(),
            'steps': f'{self.current_step()}/{self.total_step()}',
            'info': self.current_step_description(),
            'status': self.status()
        }

    def uuid(self):
        return self.initial_payload.get('uuid', None)

    def status(self):
        return Status[self.initial_payload['status']]

    def type(self):
        return self.initial_payload.get('type', None)

    def created_at(self):
        return self.initial_payload.get('created_at', None)

    def last_update(self):
        return self.initial_payload.get('last_update', None)

    def current_step(self):
        return self.initial_payload.get('current_step', None)

    def current_step_description(self):
        return self.initial_payload.get('current_step_description', None)

    def total_step(self):
        return self.initial_payload.get('total_step', None)

    def execution_info(self):
        return self.initial_payload.get('execution_info', None)

    def watch(self):
        return self.prescience.wait_for_task_done_or_error(self)

    def interrupt(self):
        return self.prescience.interrupt(task_id=self.uuid())

    def __str__(self):
        return f'Task({self.type()}, {self.status()}, {self.uuid()}, {self.current_step()}/{self.total_step()})'

class ParseTask(Task):
    def __init__(self,
                 json: dict,
                prescience: PrescienceClient = None):
        super(ParseTask, self).__init__(json=json, prescience=prescience)
        if self.type() != 'parse':
            raise Exception(f'ParseTask should be of type "parse" got "{self.type()}"')

    def source(self):
        from com.ovh.mls.prescience.core.bean.source import Source
        return Source(json_dict=self.initial_payload.get('source'), prescience=self.prescience)

class PreprocessTask(Task):
    def __init__(self,
                 json: dict,
                 prescience: PrescienceClient = None):
        super(PreprocessTask, self).__init__(json=json, prescience=prescience)
        if self.type() != 'preprocess':
            raise Exception(f'PreprocessTask should be of type "preprocess" got "{self.type()}"')

    def dataset(self):
        from com.ovh.mls.prescience.core.bean.dataset import Dataset
        return Dataset(json=self.initial_payload.get('dataset'), prescience=self.prescience)

class TrainTask(Task):
    def __init__(self,
                 json: dict,
                 prescience: PrescienceClient = None):
        super(TrainTask, self).__init__(json=json, prescience=prescience)
        if self.type() != 'train':
            raise Exception(f'TrainTask should be of type "train" got "{self.type()}"')

    def model(self):
        from com.ovh.mls.prescience.core.bean.model import Model
        return Model(json=self.initial_payload.get('model'), prescience=self.prescience)
