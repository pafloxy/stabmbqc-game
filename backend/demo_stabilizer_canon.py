"""Demo script for stabilizer code canonicalization."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from stabilizer_canonicalization import canonicalize_stabilizer_code

def demo_3qubit_bitflip_code():
    """3-qubit bit-flip code: S = {Z0 Z1, Z1 Z2}"""
    print("=" * 60)
    print("3-Qubit Bit-Flip Code")
    print("=" * 60)
    
    stabilizers = ["Z0 Z1", "Z1 Z2"]
    result = canonicalize_stabilizer_code(stabilizers)
    
    print(f"Number of qubits: {result['num_qubits']}")
    print(f"Number of stabilizers: {result['num_stabilizers']}")
    print(f"Number of logical qubits: {result['num_logical']}")
    print()
    print("Stabilizers (input):", result['stabilizers_sparse'])
    print("Destabilizers (found):", result['destabilizers_sparse'])
    print()
    print("Logical X operators:", result['logical_x_sparse'])
    print("Logical Z operators:", result['logical_z_sparse'])
    print()
    print("After Clifford diagonalization:")
    print("  Stabilizers  →", result['diagonalized_stabilizers'])
    print("  Destabilizers →", result['diagonalized_destabilizers'])
    print()
    print("Clifford circuit:")
    print(result['clifford_circuit'])
    print()


def demo_5qubit_code():
    """5-qubit perfect code"""
    print("=" * 60)
    print("5-Qubit Perfect Code (partial)")
    print("=" * 60)
    
    # Just use 2 stabilizers for demonstration
    stabilizers = ["X0 Z1 Z2 X3", "X1 Z2 Z3 X4"]
    try:
        result = canonicalize_stabilizer_code(stabilizers)
        
        print(f"Number of qubits: {result['num_qubits']}")
        print(f"Number of stabilizers: {result['num_stabilizers']}")
        print(f"Number of logical qubits: {result['num_logical']}")
        print()
        print("Stabilizers (input):", result['stabilizers_sparse'])
        print("Destabilizers (found):", result['destabilizers_sparse'])
        print()
        print("Logical X operators:", result['logical_x_sparse'])
        print("Logical Z operators:", result['logical_z_sparse'])
        print()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    print()


if __name__ == "__main__":
    demo_3qubit_bitflip_code()
    demo_5qubit_code()
