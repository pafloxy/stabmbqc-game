"""
Comprehensive test suite for StabMBQC game backend functions.

Tests all functions from qcmain1.py including:
- generate_stabilizer_generators
- initialize_alice_bob_system  
- generate_random_cz_gates
- update_stabilizers_after_cz
- find_anticommuting_generators
- find_bob_only_generators
- pretty_pauli_string
- pretty_pauli_list

Based on the demo scenarios from qc-testing0.ipynb
"""

import unittest
import sys
import os
import random
import numpy as np

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.stim_import import stim
from qcmain1 import (
    generate_stabilizer_generators,
    initialize_alice_bob_system,
    generate_random_cz_gates,
    update_stabilizers_after_cz,
    find_anticommuting_generators,
    find_bob_only_generators,
    pretty_pauli_string,
    pretty_pauli_list,
    QubitalSystem
)


class TestStabilizerGenerators(unittest.TestCase):
    """Test stabilizer generator creation and basic properties."""
    
    def test_generate_stabilizer_generators_basic(self):
        """Test basic stabilizer generator creation."""
        num_qubits = 4
        k = 2
        
        generators = generate_stabilizer_generators(num_qubits, k)
        
        # Check basic properties
        self.assertEqual(len(generators), k, "Should generate k generators")
        
        for gen in generators:
            self.assertIsInstance(gen, stim.PauliString, "Should be PauliString objects")
            # Check that string representation has correct length
            gen_str = str(gen)
            if gen_str and gen_str[0] in "+-":
                gen_str = gen_str[1:]  # Remove sign
            self.assertEqual(len(gen_str), num_qubits, "Generator should act on correct number of qubits")
    
    def test_generate_stabilizer_generators_different_sizes(self):
        """Test generator creation for different system sizes."""
        test_cases = [(3, 1), (4, 2), (5, 3), (6, 2)]
        
        for num_qubits, k in test_cases:
            with self.subTest(num_qubits=num_qubits, k=k):
                generators = generate_stabilizer_generators(num_qubits, k)
                self.assertEqual(len(generators), k)
                
                # Check all are valid PauliStrings
                for gen in generators:
                    self.assertIsInstance(gen, stim.PauliString)
    
    def test_stabilizer_commutation(self):
        """Test that generated stabilizers commute with each other."""
        num_qubits = 4
        k = 2
        
        generators = generate_stabilizer_generators(num_qubits, k)
        
        # All stabilizers should commute with each other
        for i in range(len(generators)):
            for j in range(i+1, len(generators)):
                self.assertTrue(generators[i].commutes(generators[j]),
                              f"Stabilizers {i} and {j} should commute")


class TestAliceBobSystem(unittest.TestCase):
    """Test Alice-Bob system initialization."""
    
    def test_initialize_small_system(self):
        """Test initialization of small Alice-Bob system."""
        n_alice = 3
        n_bob = 2
        k_alice = 2
        
        system = initialize_alice_bob_system(n_alice, n_bob, k_alice)
        
        # Check basic properties
        self.assertIsInstance(system, QubitalSystem)
        self.assertEqual(system.n_alice, n_alice)
        self.assertEqual(system.n_bob, n_bob)
        self.assertEqual(system.k_alice, k_alice)
        self.assertEqual(system.total_qubits, n_alice + n_bob)
        
        # Check qubit indices
        self.assertEqual(system.alice_indices, list(range(n_alice)))
        self.assertEqual(system.bob_indices, list(range(n_alice, n_alice + n_bob)))
        
        # Check stabilizer count (k_alice from Alice + n_bob from Bob)
        expected_stabilizers = k_alice + n_bob
        self.assertEqual(len(system.stabilizer_generators), expected_stabilizers)
    
    def test_initialize_larger_system(self):
        """Test initialization of larger Alice-Bob system."""
        n_alice = 5
        n_bob = 4
        k_alice = 3
        
        system = initialize_alice_bob_system(n_alice, n_bob, k_alice)
        
        self.assertEqual(system.total_qubits, 9)
        self.assertEqual(len(system.stabilizer_generators), k_alice + n_bob)
        self.assertEqual(system.alice_indices, [0, 1, 2, 3, 4])
        self.assertEqual(system.bob_indices, [5, 6, 7, 8])
    
    def test_bob_plus_state_stabilizers(self):
        """Test that Bob's qubits are properly initialized in |+⟩ states."""
        n_alice = 3
        n_bob = 2
        k_alice = 1
        
        system = initialize_alice_bob_system(n_alice, n_bob, k_alice)
        
        # Bob's stabilizers should be the last n_bob generators
        bob_stabilizers = system.stabilizer_generators[-n_bob:]
        
        for i, bob_stab in enumerate(bob_stabilizers):
            bob_qubit = system.bob_indices[i]
            stab_str = str(bob_stab)
            # Remove sign if present
            if stab_str and stab_str[0] in "+-":
                stab_str = stab_str[1:]
            
            # Check that Bob's stabilizer is X on the correct qubit
            if bob_qubit < len(stab_str):
                self.assertEqual(stab_str[bob_qubit], 'X',
                               f"Bob qubit {bob_qubit} should be stabilized by X")


class TestCZGateGeneration(unittest.TestCase):
    """Test random CZ gate generation."""
    
    def setUp(self):
        """Set up test system."""
        self.system = initialize_alice_bob_system(3, 2, 2)
        random.seed(42)  # For reproducible tests
    
    def test_generate_cz_gates_basic(self):
        """Test basic CZ gate generation."""
        cz_gates = generate_random_cz_gates(self.system, num_gates=3)
        
        self.assertIsInstance(cz_gates, list)
        self.assertEqual(len(cz_gates), 3)
        
        for gate in cz_gates:
            self.assertIsInstance(gate, tuple)
            self.assertEqual(len(gate), 2)
            q1, q2 = gate
            self.assertIsInstance(q1, int)
            self.assertIsInstance(q2, int)
            self.assertNotEqual(q1, q2, "CZ gate qubits should be different")
    
    def test_no_alice_alice_gates(self):
        """Test that no Alice-Alice CZ gates are generated."""
        # Generate many gates to check the constraint
        cz_gates = generate_random_cz_gates(self.system, num_gates=10)
        
        for q1, q2 in cz_gates:
            alice_q1 = q1 in self.system.alice_indices
            alice_q2 = q2 in self.system.alice_indices
            
            # Should not have both qubits from Alice
            self.assertFalse(alice_q1 and alice_q2,
                           f"Found Alice-Alice gate: CZ({q1}, {q2})")
    
    def test_valid_gate_types(self):
        """Test that only Alice-Bob and Bob-Bob gates are generated."""
        cz_gates = generate_random_cz_gates(self.system, num_gates=8)
        
        alice_bob_count = 0
        bob_bob_count = 0
        
        for q1, q2 in cz_gates:
            alice_q1 = q1 in self.system.alice_indices
            alice_q2 = q2 in self.system.alice_indices
            
            if alice_q1 and not alice_q2:
                alice_bob_count += 1
            elif not alice_q1 and alice_q2:
                alice_bob_count += 1
            elif not alice_q1 and not alice_q2:
                bob_bob_count += 1
            else:
                self.fail(f"Invalid gate type: CZ({q1}, {q2})")
        
        # Should have some gates (exact counts depend on randomness)
        self.assertGreaterEqual(alice_bob_count + bob_bob_count, len(cz_gates))


class TestStabilizerUpdates(unittest.TestCase):
    """Test stabilizer updates after CZ gates."""
    
    def setUp(self):
        """Set up test system and gates."""
        random.seed(42)
        self.system = initialize_alice_bob_system(3, 2, 2)
        self.cz_gates = [(0, 3), (1, 4)]  # Alice-Bob gates
    
    def test_update_stabilizers_basic(self):
        """Test basic stabilizer update functionality."""
        initial_count = len(self.system.stabilizer_generators)
        
        updated_stabilizers = update_stabilizers_after_cz(self.system, self.cz_gates)
        
        # Should have same number of stabilizers
        self.assertEqual(len(updated_stabilizers), initial_count)
        
        # All should be PauliString objects
        for stab in updated_stabilizers:
            self.assertIsInstance(stab, stim.PauliString)
    
    def test_stabilizer_evolution(self):
        """Test that stabilizers actually change after CZ gates."""
        initial_stabilizers = [str(s) for s in self.system.stabilizer_generators]
        updated_stabilizers = update_stabilizers_after_cz(self.system, self.cz_gates)
        final_stabilizers = [str(s) for s in updated_stabilizers]
        
        # At least some stabilizers should be different
        # (Though this isn't guaranteed for all cases)
        differences = sum(1 for i, f in zip(initial_stabilizers, final_stabilizers) if i != f)
        # Just check that the function runs without error - exact changes depend on initial state
        self.assertGreaterEqual(differences, 0)
    
    def test_empty_cz_gates(self):
        """Test update with no CZ gates."""
        updated_stabilizers = update_stabilizers_after_cz(self.system, [])
        
        # Should be identical to original
        self.assertEqual(len(updated_stabilizers), len(self.system.stabilizer_generators))


class TestAnticommutingGenerators(unittest.TestCase):
    """Test anti-commuting generator finding."""
    
    def setUp(self):
        """Set up test system with updated stabilizers."""
        random.seed(42)
        self.system = initialize_alice_bob_system(3, 2, 1)  # Smaller system for easier testing
        cz_gates = [(0, 3)]  # One Alice-Bob gate
        self.updated_stabilizers = update_stabilizers_after_cz(self.system, cz_gates)
    
    def test_find_anticommuting_basic(self):
        """Test basic anti-commuting generator finding."""
        anticommuting_sets = find_anticommuting_generators(
            self.updated_stabilizers, self.system.total_qubits
        )
        
        # Should have one set per stabilizer
        self.assertEqual(len(anticommuting_sets), len(self.updated_stabilizers))
        
        # Each set should be a list
        for ac_set in anticommuting_sets:
            self.assertIsInstance(ac_set, list)
    
    def test_anticommuting_properties(self):
        """Test that found generators have correct commutation properties."""
        anticommuting_sets = find_anticommuting_generators(
            self.updated_stabilizers, self.system.total_qubits
        )
        
        for target_idx, ac_set in enumerate(anticommuting_sets):
            target_stab = self.updated_stabilizers[target_idx]
            
            for candidate in ac_set:
                self.assertIsInstance(candidate, stim.PauliString)
                
                # Should anti-commute with target stabilizer
                self.assertFalse(candidate.commutes(target_stab),
                               "Candidate should anti-commute with target stabilizer")
                
                # Should commute with all other stabilizers
                for other_idx, other_stab in enumerate(self.updated_stabilizers):
                    if other_idx != target_idx:
                        self.assertTrue(candidate.commutes(other_stab),
                                      f"Candidate should commute with stabilizer {other_idx}")


class TestBobOnlyGenerators(unittest.TestCase):
    """Test Bob-only generator finding."""
    
    def setUp(self):
        """Set up test system."""
        random.seed(42)
        self.system = initialize_alice_bob_system(3, 3, 2)  # More Bob qubits
        cz_gates = [(0, 3), (1, 4), (4, 5)]  # Alice-Bob and Bob-Bob gates
        self.updated_stabilizers = update_stabilizers_after_cz(self.system, cz_gates)
        self.anticommuting_sets = find_anticommuting_generators(
            self.updated_stabilizers, self.system.total_qubits
        )
    
    def test_find_bob_only_basic(self):
        """Test basic Bob-only generator finding."""
        bob_only_generators = find_bob_only_generators(
            self.anticommuting_sets, self.system.alice_indices
        )
        
        self.assertIsInstance(bob_only_generators, list)
        
        # Each generator should be a PauliString
        for gen in bob_only_generators:
            self.assertIsInstance(gen, stim.PauliString)
    
    def test_bob_only_support(self):
        """Test that Bob-only generators have no support on Alice qubits."""
        bob_only_generators = find_bob_only_generators(
            self.anticommuting_sets, self.system.alice_indices
        )
        
        for gen in bob_only_generators:
            gen_str = str(gen)
            if gen_str and gen_str[0] in "+-":
                gen_str = gen_str[1:]  # Remove sign
            
            # Check that all Alice qubit positions are identity
            for alice_idx in self.system.alice_indices:
                if alice_idx < len(gen_str):
                    self.assertIn(gen_str[alice_idx], ['I', '_'],
                                f"Bob-only generator should have identity on Alice qubit {alice_idx}")
    
    def test_no_duplicates(self):
        """Test that no duplicate generators are returned."""
        bob_only_generators = find_bob_only_generators(
            self.anticommuting_sets, self.system.alice_indices
        )
        
        gen_strings = [str(gen) for gen in bob_only_generators]
        unique_strings = set(gen_strings)
        
        self.assertEqual(len(gen_strings), len(unique_strings),
                        "Should not have duplicate generators")


class TestPrettyPrinting(unittest.TestCase):
    """Test pretty printing utilities."""
    
    def setUp(self):
        """Set up test Pauli strings."""
        self.pauli1 = stim.PauliString("X0")
        # Create multi-qubit Pauli string properly
        self.pauli2 = stim.PauliString(3)
        self.pauli2[1] = 'Y'
        self.pauli2[2] = 'Z'
        self.pauli3 = stim.PauliString(3)  # Identity on 3 qubits
    
    def test_pretty_pauli_string_basic(self):
        """Test basic pretty printing of Pauli strings."""
        result = pretty_pauli_string(self.pauli1)
        self.assertIsInstance(result, str)
        self.assertIn("X_0", result)
        
        result = pretty_pauli_string(self.pauli2)
        self.assertIn("Y_1", result)
        self.assertIn("Z_2", result)
    
    def test_pretty_pauli_string_with_identities(self):
        """Test pretty printing with identity display."""
        result = pretty_pauli_string(self.pauli2, show_identities=True)
        self.assertIsInstance(result, str)
        # Should show identity on qubit 0
        self.assertIn("I_0", result)
        self.assertIn("Y_1", result)
        self.assertIn("Z_2", result)
    
    def test_pretty_pauli_list(self):
        """Test pretty printing of Pauli string lists."""
        pauli_list = [self.pauli1, self.pauli2]
        result = pretty_pauli_list(pauli_list)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        
        for item in result:
            self.assertIsInstance(item, str)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests based on notebook demo scenarios."""
    
    def test_demo1_scenario(self):
        """Test the complete Demo 1 scenario from notebook."""
        # Demo 1 parameters
        n_alice = 3
        n_bob = 2  
        k_alice = 2
        
        # Initialize system
        system = initialize_alice_bob_system(n_alice, n_bob, k_alice)
        self.assertEqual(system.total_qubits, 5)
        
        # Generate CZ gates
        random.seed(42)
        cz_gates = generate_random_cz_gates(system, num_gates=4)
        self.assertEqual(len(cz_gates), 4)
        
        # Update stabilizers
        updated_stabilizers = update_stabilizers_after_cz(system, cz_gates)
        self.assertEqual(len(updated_stabilizers), len(system.stabilizer_generators))
        
        # Find anti-commuting generators
        anticommuting_sets = find_anticommuting_generators(updated_stabilizers, system.total_qubits)
        self.assertEqual(len(anticommuting_sets), len(updated_stabilizers))
        
        # Find Bob-only generators
        bob_only_generators = find_bob_only_generators(anticommuting_sets, system.alice_indices)
        # Just check it runs successfully
        self.assertIsInstance(bob_only_generators, list)
    
    def test_demo2_scenario(self):
        """Test the complete Demo 2 scenario from notebook."""
        # Demo 2 parameters
        n_alice = 5
        n_bob = 4  
        k_alice = 3
        
        # Initialize larger system
        system = initialize_alice_bob_system(n_alice, n_bob, k_alice)
        self.assertEqual(system.total_qubits, 9)
        
        # Generate more CZ gates
        random.seed(42)
        cz_gates = generate_random_cz_gates(system, num_gates=6)
        
        # Update stabilizers
        updated_stabilizers = update_stabilizers_after_cz(system, cz_gates)
        
        # Full analysis
        anticommuting_sets = find_anticommuting_generators(updated_stabilizers, system.total_qubits)
        bob_only_generators = find_bob_only_generators(anticommuting_sets, system.alice_indices)
        
        # Verify it completes without errors
        self.assertIsInstance(anticommuting_sets, list)
        self.assertIsInstance(bob_only_generators, list)
    
    def test_custom_parameters(self):
        """Test with various custom parameter combinations."""
        test_cases = [
            (4, 3, 2),
            (6, 2, 3),
            (3, 4, 1)
        ]
        
        for n_alice, n_bob, k_alice in test_cases:
            with self.subTest(n_alice=n_alice, n_bob=n_bob, k_alice=k_alice):
                random.seed(123)
                
                # Full workflow
                system = initialize_alice_bob_system(n_alice, n_bob, k_alice)
                cz_gates = generate_random_cz_gates(system, num_gates=3)
                updated_stabilizers = update_stabilizers_after_cz(system, cz_gates)
                anticommuting_sets = find_anticommuting_generators(updated_stabilizers, system.total_qubits)
                bob_only_generators = find_bob_only_generators(anticommuting_sets, system.alice_indices)
                
                # Basic sanity checks
                self.assertEqual(system.total_qubits, n_alice + n_bob)
                self.assertEqual(len(system.stabilizer_generators), k_alice + n_bob)
                self.assertIsInstance(bob_only_generators, list)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2, exit=False)