# -*- coding: utf-8 -*-


ACTION_QUEUE_START = "ActionQueue-START"
ACTION_QUEUE_END = "ActionQueue-End"

ACTION_TERMINATE = "Terminate"
ACTION_LAUNCH_APP = "LaunchApp"
ACTION_CLICK = "ClickEvent"
ACTION_TEXT_INSERT = "TextInsert"
ACTION_SWIPE = "Swipe"
ACTION_PRESS_BACK = "PressBack"
ACTION_CLOSE_KEYBOARD = "CloseKeyboard"


def is_queue_start(trans):
    return trans.action == ACTION_QUEUE_START


def is_queue_end(trans):
    return trans.action == ACTION_QUEUE_END


def is_queue_start_or_end(trans):
    return is_queue_start(trans) or is_queue_end(trans)


def is_terminate(trans):
    return trans.action == ACTION_TERMINATE


def is_launch_app(trans):
    return trans.action == ACTION_LAUNCH_APP


def is_press_back(trans):
    return trans.action == ACTION_PRESS_BACK


def is_close_keyboard(trans):
    return trans.action == ACTION_CLOSE_KEYBOARD
