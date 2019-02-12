# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.
import json

from prescience_client.enum.output_format import OutputFormat

from prescience_client.bean.metadata_page_result import MetadataPageResult
from prescience_client.client.prescience_client import PrescienceClient
from prescience_client.utils.table_printable import TablePrinter
from termcolor import colored

class PageResult(object):
    """
    Prescience PageResult object
    """
    def __init__(self,
                 json_dict: dict,
                 clazz,
                 factory_method = None,
                 prescience: PrescienceClient = None
                 ):
        """
        Constructor of PageResult object
        :param json_dict: the source JSON dict received from prescience
        :param clazz: the python class of object contained inside page
        :param factory_method: the factory method for constructing inside object from their dict
        :param prescience: the prescience client
        """
        self.page_class = clazz
        if factory_method is not None:
            self.factory_method = factory_method
        else:
            self.factory_method = clazz

        self.metadata = MetadataPageResult(json_dict=json_dict['metadata'])
        self.content = [self.factory_method(x, prescience) for x in json_dict['content']]
        self.json_dict = json_dict

    def __str__(self):
        string = ','.join([str(x) for x in self.content])
        return f'PAGE[{self.metadata.page_number}]({string})'

    def show(self, ouput: OutputFormat = OutputFormat.TABLE):
        """
        Show the current page on stdout
        """
        if ouput == OutputFormat.JSON:
            print(json.dumps(self.json_dict))
        else:
            table = TablePrinter.get_table(self.page_class, self.content)
            print(table.get_string(title=colored(self.metadata.elements_type.upper(), 'yellow', attrs=['bold'])))
            print(colored(f'page {self.metadata.page_number}/{self.metadata.total_pages}', 'yellow'))
        return self
