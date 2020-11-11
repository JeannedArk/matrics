# -*- coding: utf-8 -*-
import csv

from util.modelutil import get_csv_dict_reader
from util.typeutil import convert_bool_python


class Rectangle(object):
    """
    Original class: org.droidmate.deviceInterface.exploration.Rectangle
    """

    def __init__(self, left_x, top_y, width, height):
        self.leftX = left_x
        self.topY = top_y
        self.width = width
        self.height = height

    @staticmethod
    def construct_from_str(_str):
        """
        Example:
            '0:0:0:0'
            '28:1292:1384:168'
        """
        s = _str.split(":")
        assert len(s) == 4, f"It was {len(s)}, {s}"
        return Rectangle(int(s[0]), int(s[1]), int(s[2]), int(s[3]))

    def is_not_empty(self):
        return self.width > 0 and self.height > 0

    def is_empty(self):
        return self.width <= 0 or self.height <= 0

    def area(self):
        return self.width * self.height

    def __str__(self):
        return f"{self.leftX}:{self.topY}:{self.width}:{self.height}"


class Widget(object):
    def __init__(self,
                 unique_id,
                 ui_class,
                 displayed_text,
                 hint_text,
                 alternative_text,
                 input_type,
                 checkable: bool,
                 covers_unique_area,
                 visible_boundaries: Rectangle,
                 defined_boundaries: Rectangle,
                 internal_child_ids,
                 is_clickable: bool,
                 can_be_visible: bool,
                 is_enabled: bool,
                 focus: bool,
                 internal_id,
                 image_id,
                 text_input_field: bool,
                 is_keyboard_element: bool,
                 password_field: bool,
                 is_long_clickable: bool,
                 package_name,
                 internal_parent_id,
                 resource_id,
                 is_scrollable: bool,
                 selected: bool,
                 visible_areas,
                 xpath,
                 has_clickable_descendant: bool):
        self.unique_id = unique_id
        self.ui_class = ui_class
        self.displayed_text = displayed_text
        self.hint_text = hint_text
        self.alternative_text = alternative_text
        self.input_type = input_type
        self.checkable = checkable
        self.covers_unique_area = covers_unique_area
        self.visible_boundaries = visible_boundaries
        self.defined_boundaries = defined_boundaries
        self.internal_child_ids = internal_child_ids
        self.is_clickable = is_clickable
        self.can_be_visible = can_be_visible
        self.is_enabled = is_enabled
        self.focus = focus
        self.internal_id = internal_id
        self.image_id = image_id
        self.text_input_field = text_input_field
        self.is_keyboard_element = is_keyboard_element
        self.password_field = password_field
        self.is_long_clickable = is_long_clickable
        self.package_name = package_name
        self.internal_parent_id = internal_parent_id
        self.resource_id = resource_id
        self.is_scrollable = is_scrollable
        self.selected = selected
        self.visible_areas = visible_areas
        self.xpath = xpath
        self.has_clickable_descendant = has_clickable_descendant
        # The state the widget belongs to
        self.state = None

    FIELDNAME_UNIQUE_ID = 'Unique Id'
    FIELDNAME_UI_CLASS = 'UI Class'
    FIELDNAME_DISPLAYED_TEXT = 'Displayed Text'
    FIELDNAME_HINT_TEXT = 'Hint Text'
    FIELDNAME_ALTERNATIVE_TEXT = 'Alternative Text'
    FIELDNAME_INPUT_TYPE = 'Input-Type'
    FIELDNAME_CHECKABLE = 'Checkable'
    FIELDNAME_COVERS_UNIQUE_AREA = 'Covers Unique Area'
    FIELDNAME_VISIBLE_BOUNDARIES = 'Visible Boundaries'
    FIELDNAME_DEFINED_BOUNDARIES = 'Defined Boundaries'
    FIELDNAME_INTERNAL_CHILD_IDS = 'Internal Child-Ids'
    FIELDNAME_IS_CLICKABLE = 'Is Clickable'
    FIELDNAME_CAN_BE_VISIBLE = 'Can be Visible'
    FIELDNAME_IS_ENABLED = 'Is Enabled'
    FIELDNAME_FOCUS = 'Focus'
    FIELDNAME_INTERNAL_ID = 'Internal Id'
    FIELDNAME_IMAGE_ID = 'Image Id'
    FIELDNAME_TEXT_INPUT_FIELD = 'Text Input-Field'
    FIELDNAME_IS_KEYBOARD_ELEMENT = 'Is Keyboard-Element'
    FIELDNAME_PASSWORD_FIELD = 'Password-Field'
    FIELDNAME_IS_LONG_CLICKABLE = 'Is Long-Clickable'
    FIELDNAME_PACKAGE_NAME = 'Package Name'
    FIELDNAME_INTERNAL_PARENTID = 'Internal ParentId'
    FIELDNAME_RESOURCE_ID = 'Resource Id'
    FIELDNAME_IS_SCROLLABLE = 'Is Scrollable'
    FIELDNAME_SELECTED = 'Selected'
    FIELDNAME_VISIBLE_AREAS = 'Visible Areas'
    FIELDNAME_XPATH = 'Xpath'
    FIELDNAME_HAS_CLICKABLE_DESCENDANT = 'Has Clickable Descendant'

    FIELDNAMES = [
        FIELDNAME_UNIQUE_ID,
        FIELDNAME_UI_CLASS,
        FIELDNAME_DISPLAYED_TEXT,
        FIELDNAME_HINT_TEXT,
        FIELDNAME_ALTERNATIVE_TEXT,
        FIELDNAME_INPUT_TYPE,
        FIELDNAME_CHECKABLE,
        FIELDNAME_COVERS_UNIQUE_AREA,
        FIELDNAME_VISIBLE_BOUNDARIES,
        FIELDNAME_DEFINED_BOUNDARIES,
        FIELDNAME_INTERNAL_CHILD_IDS,
        FIELDNAME_IS_CLICKABLE,
        FIELDNAME_CAN_BE_VISIBLE,
        FIELDNAME_IS_ENABLED,
        FIELDNAME_FOCUS,
        FIELDNAME_INTERNAL_ID,
        FIELDNAME_IMAGE_ID,
        FIELDNAME_TEXT_INPUT_FIELD,
        FIELDNAME_IS_KEYBOARD_ELEMENT,
        FIELDNAME_PASSWORD_FIELD,
        FIELDNAME_IS_LONG_CLICKABLE,
        FIELDNAME_PACKAGE_NAME,
        FIELDNAME_INTERNAL_PARENTID,
        FIELDNAME_RESOURCE_ID,
        FIELDNAME_IS_SCROLLABLE,
        FIELDNAME_SELECTED,
        FIELDNAME_VISIBLE_AREAS,
        FIELDNAME_XPATH,
        FIELDNAME_HAS_CLICKABLE_DESCENDANT,
    ]

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Widget):
            return self.unique_id == o.unique_id
        else:
            return False

    def __hash__(self) -> int:
        return hash(self.unique_id)

    @staticmethod
    def construct_from_state_file(state_file, state, uid_widget_map):
        """
        Check org.droidmate.deviceInterface.exploration.UiElementPropertiesI how the properties are persisted.
        Some names are different from their field names and confusing.
        """
        with open(state_file, newline='') as f:
            widgets = set()
            csvreader = get_csv_dict_reader(f)
            try:
                for row in csvreader:
                    uid = row[Widget.FIELDNAME_UNIQUE_ID]

                    widget = Widget(uid,
                                    row[Widget.FIELDNAME_UI_CLASS],
                                    row[Widget.FIELDNAME_DISPLAYED_TEXT],
                                    row[Widget.FIELDNAME_HINT_TEXT],
                                    row[Widget.FIELDNAME_ALTERNATIVE_TEXT],
                                    row[Widget.FIELDNAME_INPUT_TYPE],
                                    convert_bool_python(row[Widget.FIELDNAME_CHECKABLE], True),
                                    row[Widget.FIELDNAME_COVERS_UNIQUE_AREA],
                                    Rectangle.construct_from_str(row[Widget.FIELDNAME_VISIBLE_BOUNDARIES]),
                                    Rectangle.construct_from_str(row[Widget.FIELDNAME_DEFINED_BOUNDARIES]),
                                    row[Widget.FIELDNAME_INTERNAL_CHILD_IDS],
                                    convert_bool_python(row[Widget.FIELDNAME_IS_CLICKABLE]),
                                    convert_bool_python(row[Widget.FIELDNAME_CAN_BE_VISIBLE]),
                                    convert_bool_python(row[Widget.FIELDNAME_IS_ENABLED]),
                                    convert_bool_python(row[Widget.FIELDNAME_FOCUS], True),
                                    row[Widget.FIELDNAME_INTERNAL_ID],
                                    row[Widget.FIELDNAME_IMAGE_ID],
                                    convert_bool_python(row[Widget.FIELDNAME_TEXT_INPUT_FIELD]),
                                    convert_bool_python(row[Widget.FIELDNAME_IS_KEYBOARD_ELEMENT]),
                                    convert_bool_python(row[Widget.FIELDNAME_PASSWORD_FIELD]),
                                    convert_bool_python(row[Widget.FIELDNAME_IS_LONG_CLICKABLE]),
                                    row[Widget.FIELDNAME_PACKAGE_NAME],
                                    row[Widget.FIELDNAME_INTERNAL_PARENTID],
                                    row[Widget.FIELDNAME_RESOURCE_ID],
                                    convert_bool_python(row[Widget.FIELDNAME_IS_SCROLLABLE]),
                                    convert_bool_python(row[Widget.FIELDNAME_SELECTED], True),
                                    # TODO RectangleList
                                    row[Widget.FIELDNAME_VISIBLE_AREAS],
                                    row[Widget.FIELDNAME_XPATH],
                                    convert_bool_python(row[Widget.FIELDNAME_HAS_CLICKABLE_DESCENDANT]))
                    widget.state = state
                    uid_widget_map[uid] = widget
                    assert widget not in widgets, f"Widget: {widget} Found widget: {widgets}"
                    widgets.add(widget)
            except csv.Error as e:
                print(f"Could not process {state_file} : {e}")
                raise e

        return widgets

    def is_visible(self):
        """
        Copied from org.droidmate.explorationModel.interaction.Widget
        """
        return self.can_be_visible and self.visible_boundaries.is_not_empty()

    def is_interactable_and_visible(self):
        """
        A modified version of is_interactable. It checks that the widget is visible as well.
        """
        return self.is_enabled \
               and self.is_visible() \
               and (self.can_be_visible or (not self.is_visible() and self.defined_boundaries.is_not_empty())) \
               and (self.text_input_field or self.is_clickable or self.checkable or self.is_long_clickable)

    def is_interactable(self):
        """
        Check ExtendedWidget.computeInteractive
        enabled && ((definedAsVisible)||(!isVisible && boundaries.isNotEmpty())) && ( isInputField || clickable || checked != null || longClickable)
        """
        return self.is_enabled\
                and (self.can_be_visible or (not self.is_visible() and self.defined_boundaries.is_not_empty()))\
                and (self.text_input_field or self.is_clickable or self.checkable or self.is_long_clickable)

    def to_string_short(self):
        return f"Widget: {self.unique_id}\n" \
            f"UI Class: {self.ui_class}\n" \
            f"Displayed text: {self.displayed_text}"
