# -*- coding: utf-8 -*-
import datetime
from typing import Optional

from model.atd import ActionType, ATDRecord
from model.har import HarPage
from util import droidmateutil


class Transition(object):
    """
    Equivalent to: org.droidmate.explorationModel.interaction.Interaction
    """
    def __init__(self,
                 source_state: str,  # Unique id
                 source_state_o,  # Corresponding object
                 action: str,
                 interacted_widget: str,
                 interacted_widget_o,  # Corresponding object
                 resulting_state: str,  # Unique id
                 resulting_state_o,  # Corresponding object
                 start_time,
                 end_time,
                 successful: bool,
                 exception: str,
                 data: str,
                 action_id: int,
                 has_result_screen: bool,
                 custom: str):
        self.source_state = source_state
        self.source_state_o = source_state_o
        self.action = action
        self.interacted_widget = interacted_widget
        self.interacted_widget_o = interacted_widget_o
        self.resulting_state = resulting_state
        self.resulting_state_o = resulting_state_o
        self.start_time = start_time
        self.end_time = end_time
        self.successful = successful
        self.exception = exception
        self.data = data
        self.action_id = action_id
        self.has_result_screen = has_result_screen
        self.custom = custom  # Meta

        self.network_page: Optional[HarPage] = None
        self.interacted_atd_record: Optional[ATDRecord] = None

    def __hash__(self) -> int:
        return hash((self.source_state, self.resulting_state, self.action_id, self.data, self.start_time))

    def __str__(self):
        return f"Transition: {self.source_state} -> {self.resulting_state}\n" \
               f"Action: {self.action}\n" \
               f"ActionId: {self.action_id}\n" \
               f"Interacted ATD Record: [ {self.interacted_atd_record} ]\n" \
               f"Interacted Widget: [ {self.interacted_widget_o and self.interacted_widget_o.to_string_short()} ]\n" \
               f"Data: {self.data}"

    @staticmethod
    def construct_terminate_transition(source_state_o, resulting_state_o):
        return Transition(source_state=source_state_o.unique_id,
                          source_state_o=source_state_o,
                          action=droidmateutil.ACTION_TERMINATE,
                          interacted_widget="null",
                          interacted_widget_o=None,
                          resulting_state=resulting_state_o.unique_id,
                          resulting_state_o=resulting_state_o,
                          start_time=str(datetime.datetime.now().isoformat()),
                          end_time=str(datetime.datetime.now().isoformat()),
                          successful=True,
                          exception="",
                          data="",
                          action_id=-1,
                          has_result_screen=True,
                          custom="")

    def set_interacted_atd_record(self, interacted_atd_record):
        # Can be set more once, because it is processed per ATD file
        # assert self.interacted_atd_record is None,\
        #     f"Transition: {str(self)}  Interacted atd record was: {str(self.interacted_atd_record)} tried to set: {str(interacted_atd_record)}"
        if interacted_atd_record.atd.action_type != ActionType.Goto:
            if self.interacted_atd_record is not None:
                assert self.interacted_atd_record.atd == interacted_atd_record.atd
                assert self.interacted_atd_record.label_text == interacted_atd_record.label_text
                # There was a case that the similarity differed nevertheless
                # assert self.interacted_atd_record.similarity == interacted_atd_record.similarity

            self.interacted_atd_record = interacted_atd_record

    def copy(self):
        trans_copy = Transition(source_state=self.source_state,
                                source_state_o=self.source_state_o,
                                action=self.action,
                                interacted_widget=self.interacted_widget,
                                interacted_widget_o=self.interacted_widget_o,
                                resulting_state=self.resulting_state,
                                resulting_state_o=self.resulting_state_o,
                                start_time=self.start_time,
                                end_time=self.end_time,
                                successful=self.successful,
                                exception=self.exception,
                                data=self.data,
                                action_id=self.action_id,
                                has_result_screen=self.has_result_screen,
                                custom=self.custom)
        return trans_copy

    def graph_info(self):
        return f"Transition: {self.source_state} -> {self.resulting_state}\n" \
               f"Action: {self.action}\n" \
               f"ActionId: {self.action_id}\n" \
               f"Successful: {self.successful}\n" \
               f"Data: {self.data}\n" \
               f"Interacted ATD Record: [ {self.interacted_atd_record} ]\n" \
               f"Interacted Widget: [ {self.interacted_widget_o and self.interacted_widget_o.to_string_short()} ]\n"
        # f"Network info----------------------\n" \
        # f"{self.network_page.graph_info() if self.network_page is not None else self.network_page}"
        # f"Interacted Widget: [ {self.interacted_widget_o and self.interacted_widget_o.to_string_short()} ]\n" \
