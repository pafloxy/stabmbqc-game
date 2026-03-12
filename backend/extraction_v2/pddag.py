from __future__ import annotations

from .pauli_utils import support_overlap
from .types import Evolution, PDDAG


def build_pddag(evolutions: list[Evolution]) -> PDDAG:
    nodes = {e.node_id: e for e in evolutions}
    order = [e.node_id for e in evolutions]
    edges = {n: set() for n in nodes}
    reverse = {n: set() for n in nodes}
    for i, src in enumerate(evolutions):
        for dst in evolutions[i + 1 :]:
            if support_overlap(src.pauli, dst.pauli):
                edges[src.node_id].add(dst.node_id)
                reverse[dst.node_id].add(src.node_id)
    return PDDAG(nodes=nodes, order=order, edges=edges, reverse_edges=reverse)
