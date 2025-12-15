import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from clifford_handling import build_cz_clifford_maps, conjugate_pauli_via_map
from pauli_handling import is_logical_pauli_sparse
import pytest
import sys
import traceback


def test_reported_example_not_misclassified():
    # Regression for the notebook scenario: logical operator should not be
    # marked as a stabilizer with an empty decomposition.
    cz_edges = [(0, 1), (0, 4), (1, 3), (2, 4)]
    maps = build_cz_clifford_maps(cz_edges, num_qubits=5)

    stablist = ["X3", "X4", "X0 X1", "X1 X2"]
    loglist = ["X0 X1 X2", "Z0 Z1 Z2"]

    stablist_ = [conjugate_pauli_via_map(p, maps, as_dict=False) for p in stablist]
    loglist_ = [conjugate_pauli_via_map(p, maps, as_dict=False) for p in loglist]

    status, details = is_logical_pauli_sparse("Z0 Z1 Z2", stablist_, num_qubits=5)
    assert status != "stabilizer" or (details and details.get("generator_indices"))
    assert status == "logical"

    # Keep sanity: conjugated stabilizers stay stabilizers.
    for idx, s in enumerate(stablist_):
        s_status, s_details = is_logical_pauli_sparse(s, stablist_, num_qubits=5)
        assert s_status == "stabilizer"
        assert s_details and set(s_details["generator_indices"]) == {idx}


def test_identity_returns_empty_decomposition():
    status, details = is_logical_pauli_sparse("", ["X0"], num_qubits=1)
    assert status == "stabilizer"
    assert details is not None
    assert details["generator_indices"] == []
    assert details["product_sparse"] == ""


def test_commutation_and_span_basic():
    stabs = ["Z0", "Z1"]

    status, details = is_logical_pauli_sparse("X0", stabs, num_qubits=2)
    assert status == "anticommuting"
    assert details and details["anticommuting_with"] == [0]

    status, details = is_logical_pauli_sparse("Z0", stabs, num_qubits=2)
    assert status == "stabilizer"
    assert details and set(details["generator_indices"]) == {0}

    status, details = is_logical_pauli_sparse("X0 X1", stabs, num_qubits=2)
    assert status == "anticommuting"
    assert details and details["anticommuting_with"] == [0, 1]

    status, details = is_logical_pauli_sparse("Z0 Z1", stabs, num_qubits=2)
    assert status == "stabilizer"
    assert details and set(details["generator_indices"]) == {0, 1}

if __name__ == "__main__":

    failures = 0
    for name, obj in list(globals().items()):
        if callable(obj) and name.startswith("test_"):
            try:
                obj()
                print(f"{name}: OK")
            except Exception:
                failures += 1
                print(f"{name}: FAILED", file=sys.stderr)
                traceback.print_exc()

    raise SystemExit(0 if failures == 0 else 1)