"""Build Qiskit circuits from sparse Pauli notation and operation lists.

Converts sparse Pauli strings like 'X1 Z3' into multi-qubit Pauli rotation gates.
Supports building circuits from operation lists with Hadamard, CZ, and Pauli evolutions.
"""

from __future__ import annotations

import re
from typing import List, Tuple, Union

from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit import Parameter
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.quantum_info import SparsePauliOp


def sparse_pauli_to_qiskit_label(pauli_spec: str, num_qubits: int) -> str:
    """
    Convert sparse Pauli notation to Qiskit label format.
    
    Args:
        pauli_spec: Sparse Pauli string like 'X1 Z3' or 'X0 X2 Z4'
        num_qubits: Total number of qubits in the circuit
        
    Returns:
        Qiskit Pauli label string in little-endian format (reversed)
        
    Example:
        sparse_pauli_to_qiskit_label('X1 Z3', 5) -> 'IIZXI'
    """
    label = ["I"] * num_qubits
    for tok in pauli_spec.replace("*", " ").split():
        tok = tok.strip()
        if not tok:
            continue
        op_sym = tok[0].upper()
        if op_sym not in ('X', 'Y', 'Z'):
            raise ValueError(f"Invalid Pauli operator in token '{tok}'")
        idx_str = tok[1:]
        if not idx_str.isdigit():
            raise ValueError(f"Invalid qubit index in token '{tok}'")
        idx = int(idx_str)
        if idx >= num_qubits:
            raise ValueError(f"Qubit index {idx} exceeds circuit size {num_qubits}")
        label[idx] = op_sym
    return "".join(reversed(label))


def append_pauli_exp_contiguous_span(
    qc: QuantumCircuit,
    term: str,
    theta: Union[float, Parameter],
    *,
    label: str = None,
) -> None:
    """
    Append a Pauli evolution gate only over the contiguous span of involved qubits.
    
    More efficient than applying to all qubits when only a few are involved.
    
    Args:
        qc: Target QuantumCircuit
        term: Sparse Pauli string like 'X1 Z3' or 'X0 X2'
        theta: Rotation angle (float or Parameter)
        label: Optional label for the gate (overrides default)
        
    Example:
        circuit = QuantumCircuit(5)
        append_pauli_exp_contiguous_span(circuit, 'X1 Z3', np.pi/4, label='X1 Z3(theta)')
        # Applies gate only to qubits [1, 2, 3] with pattern "XIZ"
    """
    ops = {}
    for tok in term.split():
        m = re.fullmatch(r"([IXYZ])(\d+)", tok)
        if not m:
            raise ValueError(f"Bad token {tok!r}")
        p, i = m.group(1), int(m.group(2))
        if p != "I":
            ops[i] = p

    if not ops:
        return

    lo, hi = min(ops.keys()), max(ops.keys())
    span = list(range(lo, hi + 1))
    pauli_label = "".join(ops.get(i, "I") for i in span)  # fills gaps with I

    # Create gate with custom label if provided
    gate = PauliEvolutionGate(SparsePauliOp(pauli_label), time=theta)
    if label:
        gate.label = label
    qc.append(gate, span)


def add_pauli_rotation(
    circuit: QuantumCircuit,
    pauli_spec: str,
    angle: Union[float, Parameter, str],
    qubit_register: QuantumRegister = None,
) -> None:
    """
    Add a Pauli rotation gate to a quantum circuit.
    
    Args:
        circuit: Target QuantumCircuit
        pauli_spec: Sparse Pauli string like 'X1 Z3' or 'X0 X2'
        angle: Rotation angle (float, Parameter object, or parameter name string)
        qubit_register: Optional register; uses circuit qubits if None
        
    Example:
        circuit = QuantumCircuit(5)
        add_pauli_rotation(circuit, 'X1 Z3', np.pi/4)
        add_pauli_rotation(circuit, 'X0 X2', 'theta1')
    """
    num_qubits = circuit.num_qubits
    if num_qubits == 0:
        raise ValueError("Cannot add Pauli rotation to empty circuit")
    
    # Convert angle to Parameter if given as string
    if isinstance(angle, str):
        angle = Parameter(angle)
    
    # Use contiguous span approach
    append_pauli_exp_contiguous_span(circuit, pauli_spec, angle)


def build_circuit_from_ops(
    ops: List[Tuple], n_alice: int = 3, n_bob: int = 2
) -> QuantumCircuit:
    """
    Build a quantum circuit from a list of operations.
    
    Args:
        ops: List of operations as tuples:
             - ('H', qubit_index) for Hadamard
             - ('CZ', (qubit_a, qubit_b)) for controlled-Z
             - (pauli_spec, angle) for Pauli rotation
               where pauli_spec is sparse notation like 'X1 Z3'
               and angle is float, Parameter, or parameter name string
        n_alice: Number of Alice qubits (default 3)
        n_bob: Number of Bob qubits (default 2)
    
    Returns:
        QuantumCircuit with Alice and Bob registers
        
    Example:
        ops = [
            ('H', 0),
            ('CZ', (1, 3)),
            ('X1 Z3', 'theta1'),
            ('X0 X2', np.pi/4),
        ]
        circuit = build_circuit_from_ops(ops, n_alice=3, n_bob=2)
    """
    A = QuantumRegister(n_alice, "A")
    B = QuantumRegister(n_bob, "B")
    qc = QuantumCircuit(A, B)
    
    # Initialize Bob qubits to |+>
    for qb in range(n_bob):
        qc.h(B[qb])
    qc.barrier()
    
    params = {}
    n_total = n_alice + n_bob
    
    def qref(idx: int):
        """Map global qubit index to register reference."""
        return A[idx] if idx < n_alice else B[idx - n_alice]
    
    def get_param(name: str) -> Parameter:
        """Get or create a Parameter with given name."""
        if name not in params:
            params[name] = Parameter(name)
        return params[name]
    
    for op in ops:
        if not isinstance(op, tuple) or len(op) != 2:
            raise ValueError(f"Invalid operation format: {op}")
        
        if op[0] == 'H':
            q = op[1]
            qc.h(qref(q))
            
        elif op[0] == 'CZ':
            pair = op[1]
            if not isinstance(pair, tuple) or len(pair) != 2:
                raise ValueError(f"CZ requires (a, b) tuple, got {pair}")
            qc.cz(qref(pair[0]), qref(pair[1]))
            
        else:
            # Assume Pauli rotation: (pauli_spec, angle)
            pauli_spec, angle = op
            
            # Validate that pauli_spec is a string
            if not isinstance(pauli_spec, str):
                raise ValueError(
                    f"Expected Pauli spec string, got {type(pauli_spec).__name__}: {pauli_spec}. "
                    f"Operation format should be (pauli_spec, angle), got {op}"
                )
            
            # Convert string angle to Parameter
            if isinstance(angle, str):
                angle = get_param(angle)
            
            # Create readable label - just use Pauli spec since Qiskit adds parameter automatically
            label = pauli_spec
            
            # Use contiguous span approach for efficiency
            append_pauli_exp_contiguous_span(qc, pauli_spec, angle, label=label)
    
    return qc


__all__ = [
    "sparse_pauli_to_qiskit_label",
    "append_pauli_exp_contiguous_span",
    "add_pauli_rotation",
    "build_circuit_from_ops",
]
