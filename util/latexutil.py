# -*- coding: utf-8 -*-
import numbers

import numpy as np


def texify(v):
    if isinstance(v, str):
        return v.replace("_", "\\_")
    elif isinstance(v, numbers.Number) or np.isreal(v):
        return texify_num(v)
    else:
        raise NotImplementedError(f"Unknown type: {v}")


def texify_num(v):
    """
    Num to str in tex
    """
    if np.isnan(v):
        return "NaN"
    # TODO think about that
    v_str = v if len(str(int(v))) < 4 else int(v)
    return f"\\num{{{v_str}}}"


def bool_to_latex_str(b: bool):
    if b:
        # return "$\\top$"
        return "$S$"
    else:
        # return "$\\bot$"
        return ""
