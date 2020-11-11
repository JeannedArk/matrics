# -*- coding: utf-8 -*-
import networkx as nx

from copy import deepcopy

import matplotlib.pyplot as plt
import networkx as nx


def main():
    home_state = 0
    transitions_orig = [
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 4),
        (1, 4),
        (4, 41),
        (41, 42),
        (42, 43),
        (43, 44),
        (7, 8),
        (8, 9),
    ]

    G = nx.DiGraph()

    for trans in transitions_orig:
        G.add_edge(trans[0], trans[1])

    print(nx.has_path(G, source=0, target=4))
    print(nx.has_path(G, source=0, target=8))
    print(nx.has_path(G, source=7, target=8))

    # nx.draw(G)
    # plt.show()

    transitions = []
    for trans in transitions_orig:
        src_node = trans[0]
        target_node = trans[1]
        if G.has_edge(src_node, target_node):
            if nx.has_path(G, source=home_state, target=src_node) and nx.has_path(G, source=home_state, target=target_node):
                transitions.append(trans)
            else:
                print(f"Remove {src_node} {target_node}")
                G.remove_edge(src_node, target_node)
                # G.remove_node(src_node)

    print(f"Transitions: {transitions}")

    nx.draw(G)
    plt.show()


if __name__ == '__main__':
    main()
