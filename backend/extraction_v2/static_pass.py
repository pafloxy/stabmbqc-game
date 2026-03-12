from __future__ import annotations

from .pauli_utils import combine_stabilizers, parse_pauli, pauli_to_sparse, xor_pauli
from .types import Evolution, PDDAG


def apply_static_pass(graph: PDDAG, stabilizers: list[str], extr_sol: dict[str, list[int]]) -> list[Evolution]:
    rewritten = []
    for node_id in graph.order:
        evo = graph.nodes[node_id]
        if node_id in extr_sol:
            r = combine_stabilizers(stabilizers, extr_sol[node_id])
            nq = max(len(parse_pauli(evo.pauli).x), len(parse_pauli(r).x))
            newp = pauli_to_sparse(xor_pauli(parse_pauli(evo.pauli, nq), parse_pauli(r, nq)))
            rewritten.append(Evolution(node_id=node_id, pauli=newp, angle_label=evo.angle_label, original_index=evo.original_index))
        else:
            rewritten.append(evo)
    return rewritten
