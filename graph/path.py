# -*- coding: utf-8 -*-
from typing import List

from metadata import MetaData
from model.trace import Trace


class Path(object):
    def __init__(self, nodes=None, meta_data_elements: List[MetaData] = None):
        if nodes is None:
            nodes = []
            assert meta_data_elements is None
            meta_data_elements = [MetaData() for node in nodes]
        else:
            assert meta_data_elements is not None
            assert len(nodes) == len(meta_data_elements)
        self.nodes: List[str] = []
        self.actual_length = 0
        self.meta_data: List[MetaData] = []
        self.append_path(nodes=nodes, meta_data_elements=meta_data_elements)
        self.trace = None

    def __lt__(self, other):
        if isinstance(other, Path):
            if self.actual_length == other.actual_length:
                meta_data_entries = [m for m in self.meta_data if not m.is_empty()]
                meta_data_entries_other = [m for m in other.meta_data if not m.is_empty()]
                # It is better if the overall path length is shorter, because it reduces the exploration time
                # if the actual length of both objects is the same
                return len(meta_data_entries) < len(meta_data_entries_other) or len(self.nodes) < len(other.nodes)
            else:
                # Smaller actual length is better
                return self.actual_length < other.actual_length
        else:
            raise RuntimeError("Other object was passed")

    def append_path(self, nodes: List[str], meta_data_elements: List[MetaData], count_dist=False):
        """
        :param count_dist: Only add the distance of the nodes into account when count_dist=True
                            This is necessary when we do not want to regard the path to the first
                            state of the use case.
        """
        assert len(nodes) == len(meta_data_elements)
        assert len(self.nodes) == len(self.meta_data)

        len_nodes = len(self.nodes)
        if len_nodes > 0:
            assert self.nodes[-1] == nodes[0]
            self.nodes = self.nodes[:len_nodes - 1] + nodes
            self.meta_data = self.meta_data[:len_nodes - 1] + meta_data_elements
            if count_dist:
                self.actual_length += len(nodes) - 1
        else:
            self.nodes = nodes
            self.meta_data = meta_data_elements
            if count_dist:
                self.actual_length += len(nodes)

    def prepend_path(self, nodes: List[str], meta_data_elements: List[MetaData] = None):
        """
        Do not count the distance.
        """
        assert self.nodes
        assert self.nodes[0] == nodes[-1]
        len_nodes = len(nodes)
        self.nodes = nodes[:len_nodes - 1] + self.nodes
        if meta_data_elements is None:
            meta_data_elements = [MetaData() for node in nodes]
        assert len(nodes) == len(meta_data_elements)
        self.meta_data = meta_data_elements[:len_nodes - 1] + self.meta_data

    def construct_trace(self, exploration_model):
        assert self.trace is None
        self.trace = Trace.construct_from_path(exploration_model=exploration_model, path=self)

    def get_filtered_meta_data_by_key(self, k):
        """
        Return the meta data entries of the meta data objects that have the key.
        """
        return [meta_data.get(k)
                for meta_data in self.meta_data
                if meta_data.has(k)]
