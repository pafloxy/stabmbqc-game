from __future__ import annotations

from .distance import compute_distance_and_layers
from .types import PDDAG


def pddag_snapshot(graph: PDDAG, extracted: set[str]) -> dict[str, object]:
    dist = compute_distance_and_layers(graph, extracted)
    unresolved = sorted([n for n in graph.nodes if n not in extracted], key=lambda nid: graph.nodes[nid].original_index)
    return {
        "nodes": [
            {
                "node_id": n,
                "pauli": graph.nodes[n].pauli,
                "angle_label": graph.nodes[n].angle_label,
                "original_index": graph.nodes[n].original_index,
            }
            for n in graph.order
        ],
        "edges": {k: sorted(v) for k, v in graph.edges.items()},
        "extracted": sorted(extracted),
        "unresolved": unresolved,
        "d_m": dist.d_m,
        "layers": dist.layers,
    }
