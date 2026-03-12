from backend.extraction_v2.distance import compute_distance_and_layers
from backend.extraction_v2.gf2 import solve_affine
from backend.extraction_v2.optimize import optimize_instance
from backend.extraction_v2.pddag import build_pddag
from backend.extraction_v2.reachability import predecessor_map, preceq_map, successor_map
from backend.extraction_v2.selector_system import build_selector_system, solve_all_extraction_strings
from backend.extraction_v2.static_pass import apply_static_pass
from backend.extraction_v2.types import Evolution, OptimizationInstance


def small_evos():
    return [
        Evolution("e0", "X0", "a0", 0),
        Evolution("e1", "Z0", "a1", 1),
        Evolution("e2", "X1", "a2", 2),
    ]


def test_pddag_construction():
    g = build_pddag(small_evos())
    assert "e1" in g.edges["e0"]
    assert "e2" not in g.edges["e0"]


def test_reachability_maps():
    g = build_pddag(small_evos())
    pred = predecessor_map(g)
    succ = successor_map(g)
    preceq = preceq_map(g)
    assert pred["e1"] == {"e0"}
    assert succ["e0"] == {"e1"}
    assert "e0" in preceq["e1"] and "e1" in preceq["e1"]


def test_distance_computation():
    g = build_pddag(small_evos())
    d = compute_distance_and_layers(g, {"e1"})
    assert d.d_m["e1"] == 0
    assert d.d_m["e0"] == 1


def test_selector_system_assembly_shapes():
    g = build_pddag(small_evos())
    sys = build_selector_system("e1", g, ["Z0", "X1"], ["X0"], {"e0", "e1", "e2"})
    assert len(sys.a) == len(sys.b)
    assert sys.a1 and sys.b1


def test_gf2_solver_metadata():
    res = solve_affine([[1, 0, 1], [0, 1, 1]], [1, 0])
    assert res.satisfiable
    assert res.rank == 2
    assert len(res.free_columns) == 1
    assert res.representative is not None


def test_static_pass_rewrites_selected_nodes():
    g = build_pddag(small_evos())
    evos2 = apply_static_pass(g, ["X0", "Z1"], {"e0": [1, 0]})
    changed = {e.node_id: e.pauli for e in evos2}
    assert changed["e0"] != "X0"
    assert changed["e1"] == "Z0"


def test_fixed_point_loop_runs_and_traces():
    inst = OptimizationInstance(
        stabilizers=["X0", "Z1"],
        evolutions=small_evos(),
        measurements=["Z0"],
    )
    result = optimize_instance(inst, with_trace=True)
    assert result.final_pddag is not None
    assert isinstance(result.traces, list)


def test_round_solves_against_same_snapshot_then_batch_rebuild():
    inst = OptimizationInstance(
        stabilizers=["X0", "Z0", "X1"],
        evolutions=[
            Evolution("e0", "Z0", "t0", 0),
            Evolution("e1", "X0", "t1", 1),
            Evolution("e2", "Z1", "t2", 2),
        ],
        measurements=["X0"],
    )
    result = optimize_instance(inst, with_trace=True)
    if result.traces:
        t0 = result.traces[0]
        before_nodes = [n["node_id"] for n in t0.snapshot_before["nodes"]]
        solved_nodes = [s.node_id for s in t0.selector_systems]
        assert before_nodes == ["e0", "e1", "e2"]
        assert solved_nodes == ["e0", "e1", "e2"]
        assert t0.rewrite_data["batch_rebuild"] is True


def test_regression_small_example_from_demo():
    inst = OptimizationInstance(
        stabilizers=["Z0 Z1", "X1 X2", "Z2"],
        evolutions=[
            Evolution("e0", "X0", "theta0", 0),
            Evolution("e1", "Z1", "theta1", 1),
            Evolution("e2", "X2", "theta2", 2),
        ],
        measurements=["X0", "Z2"],
    )
    all_sys = solve_all_extraction_strings(build_pddag(inst.evolutions), inst.stabilizers, inst.measurements, {"e0", "e1", "e2"})
    assert len(all_sys) == 3
