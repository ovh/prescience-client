# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2019 The Prescience-Client Authors. All rights reserved.

from asciitree import LeftAligned
from collections import OrderedDict as OD

class SourceTree(object):

    def __init__(self,
                 source_id: str,
                 selected_source: str= None,
                 selected_dataset: str=None,
                 selected_model=None):

        self.source_id = source_id
        self.tree_dict = TreePrinter.get_tree_for_source(
            source_id=source_id,
            selected_source=selected_source,
            selected_dataset=selected_dataset,
            selected_model=selected_model
        )

    def show(self):
        TreePrinter.print_tree(self.tree_dict)


class TreePrinter(object):

    @staticmethod
    def find_child_datasets(source_id: str, selected_dataset: str=None, selected_model=None):
        from com.ovh.mls.prescience.core.services.singletons import Singletons
        all_datasets = [x for x in Singletons.prescience.datasets(source_id_filter=source_id).content]
        [x.set_selected() for x in all_datasets if selected_dataset == x.dataset_id()]
        roots_dataset = [x for x in all_datasets if x.root_id() is None]
        mask_datasets = [x for x in all_datasets if x.root_id() is not None]
        return [(x, OD(TreePrinter.find_child_models(x.dataset_id(), mask_datasets, selected_model))) for x in roots_dataset]

    @staticmethod
    def find_child_models(dataset_id: str, mask_datasets: list, selected_model=None):
        from com.ovh.mls.prescience.core.services.singletons import Singletons
        dataset_list = [(x, OD(TreePrinter.find_child_models(x.dataset_id(), mask_datasets))) for x in mask_datasets if
                        x.root_id() == dataset_id]
        all_model = [x for x in Singletons.prescience.models(dataset_id_filter=dataset_id).content]
        [x.set_selected() for x in all_model if selected_model == x.model_id()]

        model_nodes = [(x, OD()) for x in all_model]
        merge = dataset_list + model_nodes
        return merge

    @staticmethod
    def get_tree_for_source(source_id: str, selected_source: str= None, selected_dataset: str=None, selected_model=None):
        from com.ovh.mls.prescience.core.services.singletons import Singletons
        root = {}
        source = Singletons.prescience.source(source_id)
        if selected_source == source_id:
            source.set_selected()
        root[str(source)] = OD(TreePrinter.find_child_datasets(
            source_id=source.source_id,
            selected_dataset=selected_dataset,
            selected_model=selected_model
        ))
        return root

    @staticmethod
    def print_tree(tree: dict):
        tr = LeftAligned()
        print(tr(tree))