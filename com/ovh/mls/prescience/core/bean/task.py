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
    """
    Generic task object, inherit from TablePrintable so that it can be easily printed as list on stdout
    """
    def __init__(self,
                 json: dict,
                prescience: PrescienceClient = None):
        """
        Constructor of Task
        :param json: the task JSON dict received from prescience
        :param prescience: the prescience client (default: None)
        """
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
        """
        Getter of the task uuid
        :return: the task uuid
        """
        return self.initial_payload.get('uuid', None)

    def status(self):
        """
        Getter of the task status
        :return: the task status
        """
        return Status[self.initial_payload['status']]

    def type(self):
        """
        Getter of the task type
        :return: the task type
        """
        return self.initial_payload.get('type', None)

    def created_at(self):
        """
        Getter of the task created_at
        :return: the task created_at
        """
        return self.initial_payload.get('created_at', None)

    def last_update(self):
        """
        Getter of the task last_update
        :return: the task last_update
        """
        return self.initial_payload.get('last_update', None)

    def current_step(self):
        """
        Getter of the task current step
        :return: the task current step
        """
        return self.initial_payload.get('current_step', None)

    def current_step_description(self):
        """
        Getter of the task current_step_description
        :return: the task current_step_description
        """
        return self.initial_payload.get('current_step_description', None)

    def total_step(self):
        """
        Getter of the task total step
        :return: the task total step
        """
        return self.initial_payload.get('total_step', None)

    def execution_info(self):
        """
        Getter of the task execution_info
        :return: the task execution_info
        """
        return self.initial_payload.get('execution_info', None)

    def watch(self):
        """
        Wait until the current task is DONE or ERROR
        :return: The last state of the Task (as a new Task object received from prescience)
        """
        return self.prescience.wait_for_task_done_or_error(self)

    def interrupt(self):
        """
        Interrupt the current task on prescience
        :return:
        """
        return self.prescience.interrupt(task_id=self.uuid())

    def __str__(self):
        return f'Task({self.type()}, {self.status()}, {self.uuid()}, {self.current_step()}/{self.total_step()})'

class ParseTask(Task):
    """
    Task of type 'parse'
    """
    def __init__(self,
                 json: dict,
                prescience: PrescienceClient = None):
        super(ParseTask, self).__init__(json=json, prescience=prescience)
        if self.type() != 'parse':
            raise Exception(f'ParseTask should be of type "parse" got "{self.type()}"')

    def source(self) -> 'Source':
        """
        Getter of the linked source for this task
        :return: the source object
        """
        from com.ovh.mls.prescience.core.bean.source import Source
        return Source(json_dict=self.initial_payload.get('source'), prescience=self.prescience)

class PreprocessTask(Task):
    """
    Task of type 'preprocess'
    """
    def __init__(self,
                 json: dict,
                 prescience: PrescienceClient = None):
        super(PreprocessTask, self).__init__(json=json, prescience=prescience)
        if self.type() != 'preprocess':
            raise Exception(f'PreprocessTask should be of type "preprocess" got "{self.type()}"')

    def dataset(self) -> 'Dataset':
        """
        Getter of the linked dataset for this task
        :return: the dataset object
        """
        from com.ovh.mls.prescience.core.bean.dataset import Dataset
        return Dataset(json=self.initial_payload.get('dataset'), prescience=self.prescience)

class TrainTask(Task):
    """
    Task of type 'train'
    """
    def __init__(self,
                 json: dict,
                 prescience: PrescienceClient = None):
        super(TrainTask, self).__init__(json=json, prescience=prescience)
        if self.type() != 'train':
            raise Exception(f'TrainTask should be of type "train" got "{self.type()}"')

    def model(self) -> 'Model':
        """
        Getter of the linked model for this task
        :return: the model object
        """
        from com.ovh.mls.prescience.core.bean.model import Model
        return Model(json=self.initial_payload.get('model'), prescience=self.prescience)
