# -*- coding: utf-8 -*-
import metadata
from graph.path import Path
from model.tagger.basestatetagger import BaseStateTagger


class UCEStartTagger(BaseStateTagger):
    def tag_states(self, exploration_model):
        for uce in exploration_model.use_case_execution_manager.get_verified_use_case_executions():
            uce_computed: Path = uce.get_verified_computed_path()
            assert len(uce_computed.nodes) == len(uce_computed.meta_data),\
                f"Nodes: {len(uce_computed.nodes)} MetaData: {len(uce_computed.meta_data)}"
            start_idx = next(i for i, meta_data in enumerate(uce_computed.meta_data)
                             if meta_data.has(metadata.META_DATA_ATD))
            assert start_idx > 0, f"Index was: {start_idx}"
            uce.start_index = start_idx
