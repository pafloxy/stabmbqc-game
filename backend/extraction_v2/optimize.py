from __future__ import annotations

from .canonicalize import canonicalize_generators
from .pddag import build_pddag
from .selector_system import solve_all_extraction_strings
from .static_pass import apply_static_pass
from .trace import pddag_snapshot
from .types import OptimizeResult, OptimizationInstance, RoundTrace


def optimize_instance(instance: OptimizationInstance, with_trace: bool = True, max_rounds: int = 50) -> OptimizeResult:
    canon = canonicalize_generators(instance.stabilizers, instance.measurements)
    graph = build_pddag(instance.evolutions)
    extracted = set()
    traces: list[RoundTrace] = []

    for ridx in range(max_rounds):
        unresolved = {n for n in graph.nodes if n not in extracted}
        snapshot_before = pddag_snapshot(graph, extracted)
        selector_systems = solve_all_extraction_strings(graph, canon.stabilizers, canon.measurements, unresolved)
        extr_sol = {
            s.node_id: s.chosen_selector
            for s in selector_systems
            if s.solve_result.satisfiable and s.chosen_selector is not None
        }
        if not extr_sol:
            break

        old_nodes = {nid: graph.nodes[nid].pauli for nid in graph.nodes}
        rewritten_evos = apply_static_pass(graph, canon.stabilizers, extr_sol)
        graph = build_pddag(rewritten_evos)
        extracted.update(extr_sol.keys())
        rewrite_rows = []
        for nid in sorted(extr_sol):
            rewrite_rows.append({"node_id": nid, "old_pauli": old_nodes[nid], "new_pauli": graph.nodes[nid].pauli})

        if with_trace:
            traces.append(
                RoundTrace(
                    round_index=ridx,
                    snapshot_before=snapshot_before,
                    selector_systems=selector_systems,
                    extr_sol=extr_sol,
                    rewrite_data={"rewrites": rewrite_rows, "batch_rebuild": True},
                    snapshot_after=pddag_snapshot(graph, extracted),
                )
            )

    unresolved = {n for n in graph.nodes if n not in extracted}
    return OptimizeResult(final_pddag=graph, extracted=extracted, unresolved=unresolved, traces=traces)
