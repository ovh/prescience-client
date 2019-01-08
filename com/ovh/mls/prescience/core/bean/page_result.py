# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

from com.ovh.mls.prescience.core.bean.metadata_page_result import MetadataPageResult
from com.ovh.mls.prescience.core.client.prescience_client import PrescienceClient
from com.ovh.mls.prescience.core.utils.table_printable import TablePrinter
from termcolor import colored

class PageResult(object):
    def __init__(self,
                 json: dict,
                 clazz,
                 factory_method = None,
                 prescience: PrescienceClient = None
                 ):
        self.page_class = clazz
        if factory_method is not None:
            self.factory_method = factory_method
        else:
            self.factory_method = clazz

        self.metadata = MetadataPageResult(json_dict=json['metadata'])
        self.content = [self.factory_method(x, prescience) for x in json['content']]

    def __str__(self):
        string = ','.join([str(x) for x in self.content])
        return f'PAGE[{self.metadata.page_number}]({string})'

    def show(self):
        table = TablePrinter.get_table(self.page_class, self.content)
        print(table.get_string(title=colored(self.metadata.elements_type.upper(), 'yellow', attrs=['bold'])))
        print(colored(f'page {self.metadata.page_number}/{self.metadata.total_pages}', 'yellow'))
        return self
