# -*- coding: utf-8 -*-


class TransitionsSet(dict):
    """
    Helper class to stringify transitions for the graph visualization.

    Use dict as super class, because it needs to be json serializable.
    """
    def __init__(self, transition):
        super().__init__()
        self.transitions = [transition]

    def __str__(self) -> str:
        s = set([f"{trans.action}{'' if trans.interacted_atd_record is None else ' ' + trans.interacted_atd_record.atd.target_descriptor}"
                 for trans
                 in self.transitions])
        return "<" + ','.join(s) + ">"

    def add(self, trans):
        self.transitions.append(trans)
