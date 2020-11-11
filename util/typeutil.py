# -*- coding: utf-8 -*-


def convert_bool_python(_str, deactivatable=False):
    """
    :param deactivatable: For PType.DeactivatableFlag in org.droidmate.deviceInterface.exploration.PType
    """
    if _str == "true":
        return True
    elif _str == "false" or deactivatable:
        return False
    else:
        raise ValueError(f"Conversion failed: _str={_str} deactivatable={deactivatable}")


def convert_bool_kotlin(b: bool) -> str:
    return "true" if b else "false"
