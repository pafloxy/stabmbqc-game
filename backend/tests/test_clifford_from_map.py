import pytest
import stim
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from clifford_from_map import synthesize_clifford_from_sd_pairs
from pauli_handling import parse_sparse_pauli


def test_pairs_to_standard_conjugation():
    pairs = [
        ("Z1 X3", "Z3"),
        ("Z0 Z2 X4", "X2"),
        ("Y0 Y1 Z3 Z4", "Z0"),
        ("Z0 X1 X2 Z3 Z4", "Z0 Z1"),
    ]
    num_qubits = 5
    res = synthesize_clifford_from_sd_pairs(pairs, num_qubits=num_qubits)
    C = res["tableau"]
    target_qubits = res["target_qubits"]

    for i, q in enumerate(target_qubits):
        S = parse_sparse_pauli(pairs[i][0], num_qubits=num_qubits)
        D = parse_sparse_pauli(pairs[i][1], num_qubits=num_qubits)
        out_S = C.conjugate_pauli_string(S)
        out_D = C.conjugate_pauli_string(D)

        want_S = stim.PauliString(num_qubits)
        want_S[q] = "Z"
        want_D = stim.PauliString(num_qubits)
        want_D[q] = "X"

        assert out_S == want_S
        assert out_D == want_D


def test_invalid_frame_raises():
    pairs = [("Z0", "Z0")]  # commute -> invalid
    with pytest.raises(ValueError):
        synthesize_clifford_from_sd_pairs(pairs, num_qubits=1)


def test_circuit_generation():
    pairs = [("Z0", "X0")]
    res = synthesize_clifford_from_sd_pairs(pairs, num_qubits=1)
    circ = res["circuit"]
    assert isinstance(circ, stim.Circuit)
    assert len(list(circ)) > 0  # has some operations
