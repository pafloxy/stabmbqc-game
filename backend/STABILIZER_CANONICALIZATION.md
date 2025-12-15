# Stabilizer Code Canonicalization

## Overview

The `stabilizer_canonicalization.py` module provides Pythonic functions for analyzing and canonicalizing stabilizer codes using Stim-based Clifford operations.

## Main Function

### `canonicalize_stabilizer_code(stabilizers, num_qubits=None)`

Takes a stabilizer group (via generators) and produces:

1. **Destabilizer pairs** - Paulis that anticommute with their paired stabilizer
2. **Logical operators** - Logical X and Z operators for the encoded qubits
3. **Clifford diagonalization map** - Maps stabilizers to single-qubit Z operators and destabilizers to single-qubit X operators

## Input/Output Format

- **Input**: Sparse Pauli notation (e.g., `["Z0 Z1", "X1 X2"]`)
- **Output**: Dictionary with comprehensive code information

## Key Features

- Uses Stim tableaux for robust Clifford operations
- Compatible with sparse Pauli notation used throughout the backend
- Automatic destabilizer discovery via symplectic orthogonalization
- Clifford circuit synthesis for code diagonalization
- Full integration with `pauli_handling.py` and `clifford_handling.py`

## Return Dictionary Keys

- `num_qubits`: Total number of physical qubits
- `num_stabilizers`: Number of independent stabilizers (k)
- `num_logical`: Number of logical qubits (n - k)
- `stabilizers_sparse`: Original stabilizers (canonicalized)
- `stabilizers_stim`: Stabilizers as Stim PauliString objects
- `destabilizers_sparse`: Destabilizer pairs in sparse notation
- `destabilizers_stim`: Destabilizers as Stim objects
- `logical_x_sparse`: Logical X operators in sparse notation
- `logical_z_sparse`: Logical Z operators in sparse notation
- `logical_x_stim`: Logical X as Stim objects
- `logical_z_stim`: Logical Z as Stim objects
- `clifford_tableau`: Clifford tableau that diagonalizes the code
- `clifford_circuit`: Circuit representation of the Clifford
- `diagonalized_stabilizers`: Stabilizers after Clifford (ideally Z0, Z1, ...)
- `diagonalized_destabilizers`: Destabilizers after Clifford (ideally X0, X1, ...)

## Example Usage

```python
from stabilizer_canonicalization import canonicalize_stabilizer_code

# 3-qubit bit-flip code
stabilizers = ["Z0 Z1", "Z1 Z2"]
result = canonicalize_stabilizer_code(stabilizers)

print("Stabilizers:", result['stabilizers_sparse'])
print("Destabilizers:", result['destabilizers_sparse'])
print("Logical X:", result['logical_x_sparse'])
print("Logical Z:", result['logical_z_sparse'])
print("Clifford circuit:", result['clifford_circuit'])
```

### Example Output

```
Stabilizers: ['Z0 Z1', 'Z1 Z2']
Destabilizers: ['X0', 'X2']
Logical X: ['X2']
Logical Z: ['Z2']
Clifford circuit:
SWAP 1 2
```

## Implementation Details

### Destabilizer Discovery

The module finds destabilizers using symplectic orthogonalization:
- For each stabilizer S_i, finds a Pauli D_i such that:
  - D_i anticommutes with S_i
  - D_i commutes with all other stabilizers S_j (j ≠ i)
  - D_i commutes with all previously found destabilizers
- Search strategy: single-qubit Paulis first, then two-qubit combinations

### Clifford Diagonalization

The diagonalization circuit is built using a greedy algorithm:
1. For each stabilizer-destabilizer pair (S_i, D_i):
   - Apply gates to make D_i → X on qubit i
   - This automatically makes S_i → Z on qubit i
2. Uses H, S, SWAP, CX, CZ gates for transformation

### Symplectic Form

Internal representation uses symplectic GF(2) vectors:
- Pauli P represented as (x, z) where x, z ∈ {0,1}^n
- Commutation: [P, Q] = 0 ⟺ x_P·z_Q + z_P·x_Q = 0 (mod 2)
- Integration with `stim_to_symplectic` from `pauli_handling.py`

## Testing

Run the demo script:
```bash
python3 backend/demo_stabilizer_canon.py
```

Run tests:
```bash
python3 backend/tests/test_pauli_logicality.py
```

## Dependencies

- `stim`: For Clifford tableaux and Pauli operations
- `numpy`: For GF(2) linear algebra
- `pauli_handling.py`: For sparse Pauli parsing and conversion
- `clifford_handling.py`: For Clifford map utilities (optional integration)

## Future Enhancements

- Optimized circuit synthesis using graph state techniques
- Support for non-full-rank stabilizer sets
- Integration with MBQC pattern extraction
- Logical operator weight optimization
- Support for CSS codes with specialized handling

## References

- Aaronson & Gottesman, "Improved Simulation of Stabilizer Circuits" (2004)
- Gottesman, "Stabilizer Codes and Quantum Error Correction" (1997)
- Nielsen & Chuang, "Quantum Computation and Quantum Information" (2000)
