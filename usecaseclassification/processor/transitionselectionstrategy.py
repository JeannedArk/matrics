# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

import metadata
from metadata import MetaData
from model.transition import Transition
from util import droidmateutil


class TransitionSelectionStrategy(metaclass=ABCMeta):
    def __init__(self, exploration_model):
        self.exploration_model = exploration_model

    @abstractmethod
    def select(self, path):
        """
        Depending on the implemented strategy, choose transitions based on the passed path. A path only consists of
        nodes and meta data. The meta data could have additional information to chose a transition.
        """
        pass

    def post_process(self, transitions_orig):
        """
        Post process the generated transitions.
        - Copy the passed transitions, because we will change the action_id and therefore the corresponding network
        index won't match.
        - Set the transitions action ids to a continuous incremental id and overwrite the former value.
        """
        assert transitions_orig
        transitions = [trans.copy() for trans in transitions_orig]

        i = 0
        while i < len(transitions):
            trans = transitions[i]
            if droidmateutil.is_queue_start(trans):
                i += 1
                trans_cnt = transitions[i]
                while not droidmateutil.is_queue_end(trans_cnt):
                    trans_cnt.action_id = i
                    i += 1
                    trans_cnt = transitions[i]
                # Set queue start and end to the same index
                assert trans.action_id == trans_cnt.action_id
                trans.action_id = i
                trans_cnt.action_id = i
            else:
                assert not droidmateutil.is_queue_end(trans)
                trans.action_id = i

            i += 1

        return transitions


class TransitionSelectionBySequence(TransitionSelectionStrategy):
    """
    Simple transition selection strategy considering queues. This strategy selects by sequence elements. Sequence elements
    already aggregate queues.
    """
    def __init__(self, exploration_model):
        super().__init__(exploration_model)
        self.transition_use_case_exclusion_criterion = exploration_model.transition_use_case_exclusion_criterion

    def select(self, path):
        assert len(path.nodes) == len(path.meta_data)
        transitions = []
        transformed_meta_data = []
        # We don't iterate over the last node
        for i in range(len(path.nodes) - 1):
            start_node = path.nodes[i]
            assert start_node is not None
            resulting_node = path.nodes[i + 1]
            assert resulting_node is not None

            meta_data_start_node: MetaData = path.meta_data[i]
            selected_transitions = []

            if meta_data_start_node.is_empty():
                selected_transitions = self.get_transitions_from_node_by_seq(start_node=start_node, resulting_node=resulting_node)
                # Extend the new meta data by the old information
                transformed_meta_data.extend([meta_data_start_node for t in selected_transitions])
            else:
                # Select the transition by the provided meta data
                meta_data_trans = meta_data_start_node.get(metadata.META_DATA_TRANSITION)
                assert isinstance(meta_data_trans, Transition)
                selected_transitions = [meta_data_trans]
                # Extend the new meta data by the old information
                transformed_meta_data.append(meta_data_start_node)

            assert selected_transitions
            transitions.extend(selected_transitions)

        return transitions, transformed_meta_data

    def get_transitions_from_node_by_seq(self, start_node, resulting_node):
        # src_s = "8f14e45f-ceea-367a-9a36-dedd4bea2543_6512bd43-d9ca-36e0-ac99-0b0a82652dca"
        # res_s = "badce9d9-a638-3369-9856-132617277c00_a3b132cc-0ed1-3153-9969-4e46ad53aa3f"

        for seq_elem in self.exploration_model.use_case_base_graph.sequence.seq_elements:
            # if seq_elem.source_state_o.unique_id.startswith(src_s) and seq_elem.resulting_state_o.unique_id.startswith(res_s):
            #     print(f"{src_s} {res_s}")
            if seq_elem.source_state_o.unique_id == start_node and seq_elem.resulting_state_o.unique_id == resulting_node:
                # assert not self.transition_use_case_exclusion_criterion.decide(seq_elem)
                return seq_elem.transitions
        raise RuntimeError(f"Did not find a suiting transition for start_node={start_node} resulting_node={resulting_node}")


class SimpleTransitionSelection(TransitionSelectionStrategy):
    """
    NOT USED ANYMORE


    Very simple transition selection strategy. However, this strategy is too simple, because it does not regard
    queues and may generate transition sequences with QUEUE-START without a QUEUE-END and vice versa.
    """
    def __init__(self, exploration_model):
        super().__init__(exploration_model)

    def select(self, path):
        assert len(path.nodes) == len(path.meta_data)
        transitions = []
        # We don't iterate over the last node
        for i in range(len(path.nodes) - 1):
            start_node = path.nodes[i]
            assert start_node is not None
            resulting_node = path.nodes[i + 1]
            assert resulting_node is not None

            meta_data_start_node = path.meta_data[i]
            selected_trans = None
            if meta_data_start_node is None:
                selected_trans = self.get_first_transition_from_node(start_node=start_node, resulting_node=resulting_node)
            else:
                # Select this
                assert isinstance(meta_data_start_node, Transition)
                selected_trans = meta_data_start_node

            assert selected_trans is not None
            transitions.append(selected_trans)

        return transitions

    def get_first_transition_from_node(self, start_node: str, resulting_node: str):
        for trace in self.exploration_model.traces:
            for trans in trace.transitions:
                if trans.source_state == start_node and trans.resulting_state == resulting_node:
                    return trans
        raise RuntimeError(f"Did not find a suiting transition for start_node={start_node} resulting_node={resulting_node}")
