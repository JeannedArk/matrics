# -*- coding: utf-8 -*-


def shorten_fl(val):
    if isinstance(val, float):
        return "{0:.2f}".format(val)
    else:
        return val
