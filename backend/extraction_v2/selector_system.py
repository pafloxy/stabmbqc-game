from __future__ import annotations

from .gf2 import solve_affine
from .pauli_utils import combine_stabilizers, pauli_comm_vector
from .types import PDDAG, SelectorSystem


def build_selector_system(
    node_id: str,
    graph: PDDAG,
    stabilizers: list[str],
    measurements: list[str],
    unresolved: set[str],
) -> SelectorSystem:
    p = graph.nodes[node_id].pauli
    pred_gt0 = sorted([x for x in graph.reverse_edges[node_id] if x in unresolved], key=lambda nid: graph.nodes[nid].original_index)
    non_pred_gt0 = sorted([x for x in unresolved if x != node_id and x not in pred_gt0], key=lambda nid: graph.nodes[nid].original_index)

    pred_rows = [graph.nodes[n].pauli for n in pred_gt0]
    np_rows = [graph.nodes[n].pauli for n in non_pred_gt0]

    a1 = [pauli_comm_vector(stabilizers, m) for m in measurements]
    b1 = pauli_comm_vector(measurements, p)
    a2 = [pauli_comm_vector(stabilizers, q) for q in pred_rows]
    b2 = [0] * len(a2)
    a3 = [pauli_comm_vector(stabilizers, q) for q in np_rows]
    b3 = pauli_comm_vector(np_rows, p)

    a = a1 + a2 + a3
    b = b1 + b2 + b3
    solve = solve_affine(a, b)
    selector = solve.representative if solve.satisfiable else None
    chosen_stabilizer = combine_stabilizers(stabilizers, selector) if selector is not None else None

    return SelectorSystem(
        node_id=node_id,
        pauli=p,
        pred_gt0=pred_gt0,
        non_pred_gt0=non_pred_gt0,
        a1=a1,
        b1=b1,
        a2=a2,
        b2=b2,
        a3=a3,
        b3=b3,
        a=a,
        b=b,
        solve_result=solve,
        chosen_selector=selector,
        chosen_stabilizer=chosen_stabilizer,
        representative_policy="minimum-hamming-then-lexicographic",
    )


def solve_all_extraction_strings(
    graph: PDDAG,
    stabilizers: list[str],
    measurements: list[str],
    unresolved: set[str],
) -> list[SelectorSystem]:
    out = []
    for node_id in sorted(unresolved, key=lambda nid: graph.nodes[nid].original_index):
        out.append(build_selector_system(node_id, graph, stabilizers, measurements, unresolved))
    return out
