from __future__ import annotations

from .types import PDDAG


def topological_sequence(graph: PDDAG) -> list[tuple[str, str, str]]:
    return [(nid, graph.nodes[nid].pauli, graph.nodes[nid].angle_label) for nid in graph.order]
