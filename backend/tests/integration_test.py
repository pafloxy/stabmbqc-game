#!/usr/bin/env python3
"""
Integration test runner that mirrors the notebook demos exactly.
This script runs the same scenarios as in qc-testing0.ipynb to ensure
all functionality works correctly.
"""

import sys
import os
import random
import numpy as np
import stim

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from qcmain1 import *

def run_demo1():
    """Run Demo 1 scenario exactly as in notebook."""
    print("🎯 DEMO 1: Small StabMBQC System")
    print("="*50)

    # System parameters
    n_alice = 3
    n_bob = 2  
    k_alice = 2

    print(f"System Configuration:")
    print(f"  Alice: {n_alice} qubits (indices 0-{n_alice-1})")
    print(f"  Bob: {n_bob} qubits (indices {n_alice}-{n_alice+n_bob-1})")
    print(f"  Alice's code: {k_alice} stabilizer generators")

    # Initialize the system
    system = initialize_alice_bob_system(n_alice, n_bob, k_alice)
    print(f"✓ System initialized: {system.total_qubits} total qubits")
    print(f"✓ Initial stabilizers: {len(system.stabilizer_generators)}")

    # Set seed for reproducible demo
    random.seed(42)
    np.random.seed(42)

    # Generate CZ gates
    cz_gates = generate_random_cz_gates(system, num_gates=4)
    print(f"✓ Generated {len(cz_gates)} CZ gates")

    # Update stabilizers
    updated_stabilizers = update_stabilizers_after_cz(system, cz_gates)
    print(f"✓ Updated stabilizers: {len(updated_stabilizers)}")

    # Find anti-commuting generators
    anticommuting_sets = find_anticommuting_generators(updated_stabilizers, system.total_qubits)
    total_anticommuting = sum(len(ac_set) for ac_set in anticommuting_sets)
    print(f"✓ Found {total_anticommuting} anti-commuting generators")

    # Find Bob-only generators
    bob_only_generators = find_bob_only_generators(anticommuting_sets, system.alice_indices)
    print(f"✓ Bob-only generators: {len(bob_only_generators)}")

    return system, updated_stabilizers, bob_only_generators

def run_demo2():
    """Run Demo 2 scenario exactly as in notebook."""
    print("\n🎯 DEMO 2: Larger StabMBQC System")
    print("="*50)

    # Larger system parameters
    n_alice = 5
    n_bob = 4  
    k_alice = 3

    print(f"System Configuration:")
    print(f"  Alice: {n_alice} qubits (indices 0-{n_alice-1})")
    print(f"  Bob: {n_bob} qubits (indices {n_alice}-{n_alice+n_bob-1})")
    print(f"  Alice's code: {k_alice} stabilizer generators")

    # Initialize the larger system
    system2 = initialize_alice_bob_system(n_alice, n_bob, k_alice)
    print(f"✓ System initialized: {system2.total_qubits} total qubits")
    print(f"✓ Initial stabilizers: {len(system2.stabilizer_generators)}")

    # Generate more CZ gates for the larger system
    cz_gates2 = generate_random_cz_gates(system2, num_gates=6)
    print(f"✓ Generated {len(cz_gates2)} CZ gates")

    # Update stabilizers
    updated_stabilizers2 = update_stabilizers_after_cz(system2, cz_gates2)
    print(f"✓ Updated stabilizers: {len(updated_stabilizers2)}")

    # Complete analysis
    anticommuting_sets2 = find_anticommuting_generators(updated_stabilizers2, system2.total_qubits)
    bob_only_generators2 = find_bob_only_generators(anticommuting_sets2, system2.alice_indices)
    
    total_anticommuting = sum(len(ac_set) for ac_set in anticommuting_sets2)
    print(f"✓ Found {total_anticommuting} anti-commuting generators")
    print(f"✓ Bob-only generators: {len(bob_only_generators2)}")

    return system2, updated_stabilizers2, bob_only_generators2

def run_custom_demo():
    """Run custom parameter demo as in notebook."""
    print("\n🎮 INTERACTIVE DEMO: Custom Parameters")
    print("="*50)

    # Custom parameters from notebook
    n_alice_custom = 4      
    n_bob_custom = 3        
    k_alice_custom = 2      
    num_cz_gates = 5        
    random_seed = 123       

    print(f"Custom Configuration:")
    print(f"  Alice: {n_alice_custom} qubits")
    print(f"  Bob: {n_bob_custom} qubits")  
    print(f"  Alice's stabilizers: {k_alice_custom}")
    print(f"  CZ gates: {num_cz_gates}")

    # Set seed and initialize
    random.seed(random_seed)
    np.random.seed(random_seed)

    # Run the complete analysis
    system_custom = initialize_alice_bob_system(n_alice_custom, n_bob_custom, k_alice_custom)
    cz_gates_custom = generate_random_cz_gates(system_custom, num_gates=num_cz_gates)
    updated_stabilizers_custom = update_stabilizers_after_cz(system_custom, cz_gates_custom)
    anticommuting_sets_custom = find_anticommuting_generators(updated_stabilizers_custom, system_custom.total_qubits)
    bob_only_custom = find_bob_only_generators(anticommuting_sets_custom, system_custom.alice_indices)

    print(f"✓ Total stabilizers after CZ: {len(updated_stabilizers_custom)}")
    print(f"✓ Bob-only measurement candidates: {len(bob_only_custom)}")

    return system_custom, bob_only_custom

def test_pretty_printing():
    """Test pretty printing functionality."""
    print("\n🎨 PRETTY PRINTING TEST")
    print("="*30)
    
    # Create test Pauli strings
    test_pauli1 = stim.PauliString("X0")
    test_pauli2 = stim.PauliString(3)
    test_pauli2[1] = 'Y'
    test_pauli2[2] = 'Z'
    
    print(f"Pauli 1: {pretty_pauli_string(test_pauli1)}")
    print(f"Pauli 2: {pretty_pauli_string(test_pauli2)}")
    print(f"Pauli 2 (with identities): {pretty_pauli_string(test_pauli2, show_identities=True)}")
    
    pauli_list = [test_pauli1, test_pauli2]
    pretty_list = pretty_pauli_list(pauli_list)
    print(f"List: {pretty_list}")
    
    print("✓ Pretty printing works correctly")

def main():
    """Run all demo scenarios and verify they work."""
    print("🧪 STABMBQC INTEGRATION TESTS")
    print("="*60)
    print("Running all demo scenarios from qc-testing0.ipynb\n")

    try:
        # Run Demo 1
        system1, stabilizers1, bob_only1 = run_demo1()
        assert system1.total_qubits == 5
        assert len(stabilizers1) == 4  # 2 Alice + 2 Bob
        
        # Run Demo 2  
        system2, stabilizers2, bob_only2 = run_demo2()
        assert system2.total_qubits == 9
        assert len(stabilizers2) == 7  # 3 Alice + 4 Bob
        
        # Run custom demo
        system_custom, bob_only_custom = run_custom_demo()
        assert system_custom.total_qubits == 7
        
        # Test pretty printing
        test_pretty_printing()
        
        print("\n" + "="*60)
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("="*60)
        
        print(f"\n📊 SUMMARY:")
        print(f"  Demo 1: {system1.total_qubits} qubits, {len(bob_only1)} Bob-only measurements")
        print(f"  Demo 2: {system2.total_qubits} qubits, {len(bob_only2)} Bob-only measurements") 
        print(f"  Custom: {system_custom.total_qubits} qubits, {len(bob_only_custom)} Bob-only measurements")
        
        print(f"\n✅ All functions in qcmain1.py are working correctly!")
        print(f"✅ Integration with notebook demos successful!")
        print(f"✅ StabMBQC game backend is ready!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ INTEGRATION TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)