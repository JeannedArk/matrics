# -*- coding: utf-8 -*-
import os

import dash_table
import pandas as pd

import colorconstants
from datatypes.orderedset import OrderedSet
from model.atd import ATD, ATDRecord
from model.widget import Widget
from util.configutil import ATD_IMG_SUBDIR, RESIZE_IMG_SUBDIR
from util.drawutil import draw_ATDs_on_img, dump_cv_img, resize_img
from util.modelutil import get_csv_writer
from util.pathutil import append_subdir
from util.typeutil import convert_bool_kotlin
from util.util import shorten_fl


HOME_SCREEN_FILE_SUFFIX = "_HS"
# This can take a lot of time
FORCE_REDRAWING = False


class State(object):
    def __init__(self, unique_id: str, is_home_screen: bool):
        """
        The implementation uses OrderedSet instead of standard sets to make the analysis
        deterministic.
        """
        self.unique_id = unique_id
        self.is_home_screen = is_home_screen
        self.widgets = set()  # Will be set later
        self.image_paths = OrderedSet()
        self.image_small_paths = OrderedSet()
        self.image_atds_paths = OrderedSet()
        # From the corresponding transitions, just for debugging purposes
        self.action_ids = OrderedSet()
        self.atd_records = OrderedSet()
        self.features = []
        self.unique_features = set()
        # The use cases the state belongs to
        self.use_cases = set()

        # TODO maybe use an ordered set
        self.outgoing_transitions = set()
        self.merged_states = set()

    def __eq__(self, o: object) -> bool:
        """
        Compares only the unique_id!
        """
        if isinstance(o, State):
            return self.unique_id == o.unique_id
        else:
            return False

    def __hash__(self) -> int:
        """
        Hashs only the unique_id!
        """
        return hash(self.unique_id)

    def __str__(self):
        return f"State(unique_id={self.unique_id}, is_home_screen={self.is_home_screen})"

    @staticmethod
    def construct_from_state_file(state_file, uid_widget_map):
        unique_id = os.path.basename(state_file)
        assert unique_id.endswith(".csv")
        unique_id = unique_id.replace(".csv", "")
        is_home_screen = False
        if unique_id.endswith(HOME_SCREEN_FILE_SUFFIX):
            is_home_screen = True
            unique_id = unique_id.replace(HOME_SCREEN_FILE_SUFFIX, "")
        state = State(unique_id, is_home_screen)
        widgets = Widget.construct_from_state_file(state_file, state, uid_widget_map)
        state.widgets = widgets
        return state

    def dump_to_file(self, target_dir):
        """
        State file header:
        Unique Id;UI Class;Displayed Text;Hint Text;Alternative Text;Input-Type;Checkable;Covers Unique Area;
        Visible Boundaries;Defined Boundaries;Internal Child-Ids;Is Clickable;Can be Visible;Is Enabled;Focus;
        Internal Id;Image Id;Text Input-Field;Is Keyboard-Element;Password-Field;Is Long-Clickable;Package Name;
        Internal ParentId;Resource Id;Is Scrollable;Selected;Visible Areas;Xpath;Has Clickable Descendant
        """
        trace_file = os.path.join(target_dir, self.get_state_file_name())
        with open(trace_file, mode='w') as f:
            csvwriter = get_csv_writer(f, Widget.FIELDNAMES)

            csvwriter.writeheader()
            for widget in self.widgets:
                csvwriter.writerow({
                    Widget.FIELDNAME_UNIQUE_ID: widget.unique_id,
                    Widget.FIELDNAME_UI_CLASS: widget.ui_class,
                    Widget.FIELDNAME_DISPLAYED_TEXT: widget.displayed_text,
                    Widget.FIELDNAME_HINT_TEXT: widget.hint_text,
                    Widget.FIELDNAME_ALTERNATIVE_TEXT: widget.alternative_text,
                    Widget.FIELDNAME_INPUT_TYPE: widget.input_type,
                    Widget.FIELDNAME_CHECKABLE: convert_bool_kotlin(widget.checkable),
                    Widget.FIELDNAME_COVERS_UNIQUE_AREA: widget.covers_unique_area,
                    Widget.FIELDNAME_VISIBLE_BOUNDARIES: str(widget.visible_boundaries),
                    Widget.FIELDNAME_DEFINED_BOUNDARIES: str(widget.defined_boundaries),
                    Widget.FIELDNAME_INTERNAL_CHILD_IDS: widget.internal_child_ids,
                    Widget.FIELDNAME_IS_CLICKABLE: convert_bool_kotlin(widget.is_clickable),
                    Widget.FIELDNAME_CAN_BE_VISIBLE: convert_bool_kotlin(widget.can_be_visible),
                    Widget.FIELDNAME_IS_ENABLED: convert_bool_kotlin(widget.is_enabled),
                    Widget.FIELDNAME_FOCUS: convert_bool_kotlin(widget.focus),
                    Widget.FIELDNAME_INTERNAL_ID: widget.internal_id,
                    Widget.FIELDNAME_IMAGE_ID: widget.image_id,
                    Widget.FIELDNAME_TEXT_INPUT_FIELD: convert_bool_kotlin(widget.text_input_field),
                    Widget.FIELDNAME_IS_KEYBOARD_ELEMENT: convert_bool_kotlin(widget.is_keyboard_element),
                    Widget.FIELDNAME_PASSWORD_FIELD: convert_bool_kotlin(widget.password_field),
                    Widget.FIELDNAME_IS_LONG_CLICKABLE: convert_bool_kotlin(widget.is_long_clickable),
                    Widget.FIELDNAME_PACKAGE_NAME: widget.package_name,
                    Widget.FIELDNAME_INTERNAL_PARENTID: widget.internal_parent_id,
                    Widget.FIELDNAME_RESOURCE_ID: widget.resource_id,
                    Widget.FIELDNAME_IS_SCROLLABLE: convert_bool_kotlin(widget.is_scrollable),
                    Widget.FIELDNAME_SELECTED: convert_bool_kotlin(widget.selected),
                    Widget.FIELDNAME_VISIBLE_AREAS: widget.visible_areas,
                    Widget.FIELDNAME_XPATH: widget.xpath,
                    Widget.FIELDNAME_HAS_CLICKABLE_DESCENDANT: convert_bool_kotlin(widget.has_clickable_descendant),
                })

    def get_state_file_name(self):
        assert self.unique_id is not None
        suffix = HOME_SCREEN_FILE_SUFFIX if self.is_home_screen else ""
        return f"{self.unique_id}{suffix}.csv"

    def process_atd_records(self, atd_records):
        for atd_rec in atd_records:
            self.add_atd_record(atd_rec)
            td = ATD.normalize(atd_rec.atd.target_descriptor)
            self.features.append(td)
            self.unique_features.add(td)
            for trans in self.outgoing_transitions:
                if atd_rec.widget_o == trans.interacted_widget_o:
                    trans.set_interacted_atd_record(atd_rec)

    def add_atd_record(self, atd_rec: ATDRecord):
        _id = len(self.atd_records)
        atd_rec.id = _id
        self.atd_records.add(atd_rec)

    def shortened_state_id(self, length=15):
        sid = self.unique_id
        return sid[:length] + "..." + sid[-length:]

    def add_image_path(self, image_path):
        # Create a downscaled image
        img_path_small = append_subdir(image_path, RESIZE_IMG_SUBDIR)
        if image_path not in self.image_paths:
            assert img_path_small not in self.image_small_paths, f"{img_path_small}"
            if FORCE_REDRAWING or not os.path.isfile(img_path_small):
                try:
                    cv_img = resize_img(image_path, 0.5)
                    dump_cv_img(cv_img, img_path_small)
                    self.image_small_paths.add(img_path_small)
                    self.image_paths.add(image_path)
                except IOError as e:
                    print(f"An error was handled: {e}")
            else:
                self.image_small_paths.add(img_path_small)
                self.image_paths.add(image_path)

    def draw_ATDs_on_img(self):
        # if self.image_path is not None:
        for image_path in self.image_paths:
            new_img_path = append_subdir(image_path, ATD_IMG_SUBDIR)
            if FORCE_REDRAWING or not os.path.isfile(new_img_path):
                cv_img = draw_ATDs_on_img(image_path, self.atd_records)
                dump_cv_img(cv_img, new_img_path)
            self.image_atds_paths.add(new_img_path)

    def get_atd_records_table(self):
        txt_length = 15
        data = {
            'Id': [atd_record.id for atd_record in self.atd_records],
            'ATD': [atd_record.atd.graph_info() for atd_record in self.atd_records],
            'label_text': [atd_record.label_text[:txt_length] + (atd_record.label_text[txt_length:] and '..')
                           for atd_record in self.atd_records],
            'similarity': [shorten_fl(atd_record.similarity) for atd_record in self.atd_records],
            'widget is_visible': [f"{atd_record.widget_o if atd_record.widget_o is None else atd_record.widget_o.is_visible()}" for atd_record in self.atd_records],
            'widget id_of_label_w': [atd_record.shortened_id_of_label_w() for atd_record in self.atd_records],
        }
        df = pd.DataFrame(data=data)
        return dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'id': c, 'name': c} for c in df.columns],
            style_cell={
                'textAlign': 'left',
            },
            style_header={
                'backgroundColor': colorconstants.RGB_COLOR_LIGHT_GREY
            },
        )

    def get_state_id_config(self):
        return self.unique_id.partition("_")[0]

    def merge_with_state(self, state_other):
        assert self.unique_id != state_other.unique_id, f"Self: {self.unique_id} Other: {state_other.unique_id}"
        assert self.is_home_screen == state_other.is_home_screen, f"Self: {self.is_home_screen} Other: {state_other.is_home_screen}"

        self.widgets.union(state_other.widgets)
        self.atd_records.union(state_other.atd_records)
        self.outgoing_transitions.union(state_other.outgoing_transitions)
        self.image_paths.union(state_other.image_paths)
        self.image_small_paths.union(state_other.image_small_paths)
        self.image_atds_paths.union(state_other.image_atds_paths)
        self.action_ids.union(state_other.action_ids)
        self.unique_features.union(state_other.unique_features)
        self.use_cases.union(state_other.use_cases)

        self.merged_states.union(state_other.merged_states)
        self.merged_states.add(state_other)
