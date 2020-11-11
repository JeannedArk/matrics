# -*- coding: utf-8 -*-
from enum import Enum

from util import droidmateutil

ATD_ACTION_CLICK = "CLICK"
ATD_ACTION_TEXT_INSERT = "ENTER"
ATD_ACTION_GOTO = "GOTO"


class ActionType(Enum):
    Click = droidmateutil.ACTION_CLICK
    TextInsert = droidmateutil.ACTION_TEXT_INSERT
    # There is no equivalent
    Goto = ATD_ACTION_GOTO

    @staticmethod
    def get_action_type(action_type_str: str):
        action_type_str = action_type_str.strip()
        if action_type_str == ATD_ACTION_CLICK:
            return ActionType.Click
        elif action_type_str == ATD_ACTION_TEXT_INSERT:
            return ActionType.TextInsert
        elif action_type_str == ATD_ACTION_GOTO:
            return ActionType.Goto
        else:
            raise RuntimeError(f"Unknown action type: {action_type_str}")


class ATD(object):
    def __init__(self, action_type_str: str, target_descriptor, data=None):
        self.action_type = ActionType.get_action_type(action_type_str)
        self.target_descriptor = ATD.normalize(target_descriptor)
        self.data = data

    def __str__(self):
        return f"ATD(action_type='{self.action_type.value}' target_descriptor='{self.target_descriptor}' data='{self.data}')"

    def __eq__(self, o):
        if isinstance(o, ATD):
            return self.action_type == o.action_type and self.target_descriptor == o.target_descriptor
        else:
            raise RuntimeError("Not even the same instance")

    def __hash__(self):
        return hash((self.action_type.value, self.target_descriptor, self.data))

    @staticmethod
    def normalize(target_descriptor):
        return target_descriptor.lower() if target_descriptor is not None else target_descriptor

    def graph_info(self):
        return f"ATD('{self.action_type.value}', '{self.target_descriptor}', '{self.data}')"


class ATDRecord(object):
    def __init__(self,
                 atd: ATD,
                 label_text,
                 similarity,
                 weight,
                 parent_id,
                 id_of_label_w,
                 id_of_label_w_orig,
                 label_dist,
                 widget_string,
                 widget_o  # Added
                 ):
        self.atd = atd
        self.label_text = label_text
        self.similarity = similarity
        self.weight = weight
        self.parent_id = parent_id
        self.id_of_label_w = id_of_label_w
        self.id_of_label_w_orig = id_of_label_w_orig
        self.label_dist = label_dist
        self.widget_string = widget_string
        self.widget_o = widget_o
        # This id is generated during processing the ATD records and is unique within a state
        self.id = None

    def __hash__(self) -> int:
        return hash((hash(self.atd), self.label_text, hash(self.widget_o)))

    def __str__(self) -> str:
        return self.graph_info()

    def shortened_id_of_label_w(self, length=8):
        if self.id_of_label_w is None:
            return self.id_of_label_w
        else:
            wid = self.id_of_label_w
            return wid[:length] + "..." + wid[-length:]

    def similarity_str(self):
        return "{0:.2f}".format(self.similarity)

    def graph_info(self):
        return f"ATDRecord({self.id} - {self.atd.graph_info()}, " \
               f"label_text: '{self.label_text}', " \
               f"similarity: '{self.similarity_str()}', " \
               f"widget is_visible: '{False if self.widget_o is None else self.widget_o.is_visible()}', " \
               f"id_of_label_w: '{self.shortened_id_of_label_w()}')"

    def tooltip_info(self):
        return f"ATDRecord({self.id} - {self.atd.graph_info()}, " \
               f"l_text: '{self.label_text}', " \
               f"sim: '{self.similarity_str()}')"
