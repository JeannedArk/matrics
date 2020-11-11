# -*- coding: utf-8 -*-
from typing import List, Set

from model.widget import Widget


def filter_interactable_visible_buttons(widgets: List[Widget]) -> Set[Widget]:
    """
    Probably also filter for clickable

    Button classes in our dataset:
    android.widget.Button
    android.widget.ImageButton
    android.widget.RadioButton
    android.widget.ToggleButton
    """
    return set(w for w in widgets
               if ("Button" in w.ui_class or "Btn" in w.ui_class) and w.is_interactable_and_visible())
