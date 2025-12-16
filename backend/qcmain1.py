"""Advanced quantum logic for the StabMBQC game.

This module implements the core physics for Alice and Bob's quantum systems:
- Alice's stabilizer code initialization
- Bob's plus state initialization  
- Random CZ entangling operations between Alice and Bob
- Stabilizer generator updates after CZ gates
- Anti-commuting generator computation
- Support analysis for Bob-only measurements

Uses Stim for efficient stabilizer computations.
"""

from __future__ import annotations

"""Advanced quantum logic for the StabMBQC game with integrated visualization tools."""

import random
from typing import List, Tuple, Set
from backend.stim_import import stim
from dataclasses import dataclass

# Optional imports for visualization
try:
    import matplotlib.pyplot as plt
    from IPython.display import SVG, display
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False

# Export list for clear module interface
__all__ = [
    'QubitalSystem',
    'generate_stabilizer_generators', 
    'initialize_alice_bob_system',
    'generate_random_cz_gates',
    'update_stabilizers_after_cz',
    'find_anticommuting_generators',
    'find_bob_only_generators',
    'pretty_pauli_string',
    'pretty_pauli_list',
    'StimVisualizer'
]


@dataclass
class QubitalSystem:
    """Container for Alice and Bob's quantum system state."""
    n_alice: int
    n_bob: int
    k_alice: int
    stabilizer_generators: List[stim.PauliString]
    alice_indices: List[int]
    bob_indices: List[int]
    total_qubits: int


def generate_stabilizer_generators(num_qubits: int, k: int) -> List[stim.PauliString]:
    """
    Generate k independent stabilizer generators for a code on num_qubits qubits.
    
    Args:
        num_qubits: Number of qubits in the code
        k: Code dimension (number of independent generators)
    
    Returns:
        List of k independent stabilizer generators as stim.PauliString objects
    """
    generators = []
    
    # Create simple commuting stabilizers for demonstration
    # Use Z-Z stabilizers which always commute
    for i in range(k):
        pauli_string = stim.PauliString(num_qubits)
        
        # Create generators like ZZ_I, _ZZ_I, etc. (adjacent Z pairs)
        if i < num_qubits - 1:
            pauli_string[i] = 'Z'
            pauli_string[(i + 1) % num_qubits] = 'Z'
        else:
            # For additional generators, use single Z operators
            pauli_string[i % num_qubits] = 'Z'
        
        generators.append(pauli_string)
    
    return generators


def initialize_alice_bob_system(n_alice: int, n_bob: int, k_alice: int) -> QubitalSystem:
    """
    Initialize Alice and Bob's quantum system.
    
    Args:
        n_alice: Number of Alice's qubits (indices 0 to n_alice-1)
        n_bob: Number of Bob's qubits (indices n_alice to n_alice+n_bob-1)  
        k_alice: Number of stabilizer generators for Alice's code
        
    Returns:
        QubitalSystem containing all system information
    """
    total_qubits = n_alice + n_bob
    alice_indices = list(range(n_alice))
    bob_indices = list(range(n_alice, total_qubits))
    
    # Generate Alice's stabilizer generators (only on Alice's qubits)
    alice_generators = generate_stabilizer_generators(n_alice, k_alice)
    
    # Extend Alice's generators to full system (pad with identities on Bob's qubits)
    extended_alice_generators = []
    for gen in alice_generators:
        # Convert to full system representation by multiplying with single qubit operators
        extended_gen = stim.PauliString(total_qubits)
        gen_str = str(gen)
        if gen_str and gen_str[0] in "+-":
            gen_str = gen_str[1:]  # Remove sign
        
        for i in range(min(len(gen_str), n_alice)):
            if gen_str[i] in ['X', 'Y', 'Z']:
                single_op = stim.PauliString(total_qubits)
                single_op[i] = gen_str[i]
                extended_gen = extended_gen * single_op
        extended_alice_generators.append(extended_gen)
    
    # Generate Bob's stabilizer generators (Bob qubits in |+⟩ state)
    # For |+⟩ state, stabilizer is X_i for each qubit i
    bob_generators = []
    for i in bob_indices:
        bob_gen = stim.PauliString(total_qubits)
        bob_gen[i] = 'X'
        bob_generators.append(bob_gen)
    
    # Combine all stabilizer generators
    all_generators = extended_alice_generators + bob_generators
    
    return QubitalSystem(
        n_alice=n_alice,
        n_bob=n_bob, 
        k_alice=k_alice,
        stabilizer_generators=all_generators,
        alice_indices=alice_indices,
        bob_indices=bob_indices,
        total_qubits=total_qubits
    )


def generate_random_cz_gates(system: QubitalSystem, num_gates: int = None) -> List[Tuple[int, int]]:
    """
    Generate random CZ gates between Alice-Bob and Bob-Bob qubits (not Alice-Alice).
    
    Args:
        system: The QubitalSystem
        num_gates: Number of CZ gates to generate (if None, use random number)
        
    Returns:
        List of (qubit1, qubit2) tuples for CZ gates
    """
    if num_gates is None:
        # Random number of gates between 1 and min(n_alice * n_bob, 10)
        max_gates = min(system.n_alice * system.n_bob, 10)
        num_gates = random.randint(1, max(1, max_gates))
    
    valid_pairs = []
    
    # Alice-Bob pairs
    for alice_idx in system.alice_indices:
        for bob_idx in system.bob_indices:
            valid_pairs.append((alice_idx, bob_idx))
    
    # Bob-Bob pairs  
    for i, bob_idx1 in enumerate(system.bob_indices):
        for bob_idx2 in system.bob_indices[i+1:]:
            valid_pairs.append((bob_idx1, bob_idx2))
    
    # Sample random pairs
    selected_gates = random.sample(valid_pairs, min(num_gates, len(valid_pairs)))
    
    return selected_gates


def update_stabilizers_after_cz(system: QubitalSystem, cz_gates: List[Tuple[int, int]]) -> List[stim.PauliString]:
    """
    Compute updated stabilizer generators after applying CZ gates.
    
    Args:
        system: The QubitalSystem
        cz_gates: List of (qubit1, qubit2) tuples for CZ gates
        
    Returns:
        Updated list of stabilizer generators
    """
    # Create a tableau to track the evolution
    tableau = stim.Tableau(system.total_qubits)
    
    # Initialize tableau with current stabilizer generators
    # For a proper tableau initialization, we need to set up destabilizers too
    # For simplicity, we'll work directly with Pauli strings and conjugate them
    
    current_stabilizers = system.stabilizer_generators.copy()
    
    # Apply each CZ gate to update the stabilizers
    for q1, q2 in cz_gates:
        updated_stabilizers = []
        
        for stab in current_stabilizers:
            # Conjugate the stabilizer by CZ(q1, q2)
            # CZ conjugation rules:
            # X_i -> X_i Z_j (if gate is CZ(i,j) and stab has X on qubit i)
            # Z_i -> Z_i (unchanged)
            # Y_i -> Y_i Z_j (if gate is CZ(i,j) and stab has Y on qubit i)
            
            new_stab = stim.PauliString(stab)  # Copy
            
            # Apply CZ(q1, q2) conjugation
            stab_str = str(new_stab)
            if q1 < len(stab_str) and stab_str[q1] in ['X', 'Y']:
                # Multiply by Z on q2
                z_op = stim.PauliString(system.total_qubits)
                z_op[q2] = 'Z'
                new_stab = new_stab * z_op
            
            if q2 < len(stab_str) and stab_str[q2] in ['X', 'Y']:
                # Multiply by Z on q1  
                z_op = stim.PauliString(system.total_qubits)
                z_op[q1] = 'Z'
                new_stab = new_stab * z_op
            
            updated_stabilizers.append(new_stab)
        
        current_stabilizers = updated_stabilizers
    
    return current_stabilizers


def find_anticommuting_generators(stabilizer_generators: List[stim.PauliString], 
                                total_qubits: int) -> List[List[stim.PauliString]]:
    """
    Find sets of Pauli strings that anti-commute with exactly one stabilizer generator
    and commute with all others.
    
    Args:
        stabilizer_generators: List of stabilizer generators
        total_qubits: Total number of qubits in the system
        
    Returns:
        List of lists, where each inner list contains Pauli strings that anti-commute 
        with the corresponding stabilizer generator
    """
    anticommuting_sets = []
    
    for target_idx, target_stab in enumerate(stabilizer_generators):
        anticommuting_set = []
        
        # Generate candidate Pauli strings by systematically trying combinations
        # For efficiency, we'll focus on single-qubit Pauli operators first
        for qubit_idx in range(total_qubits):
            for pauli_op in ['X', 'Y', 'Z']:
                candidate = stim.PauliString(total_qubits)
                candidate[qubit_idx] = pauli_op
                
                # Check if it anti-commutes with target and commutes with others
                anticommutes_with_target = not candidate.commutes(target_stab)
                commutes_with_others = all(
                    candidate.commutes(stab) 
                    for i, stab in enumerate(stabilizer_generators) 
                    if i != target_idx
                )
                
                if anticommutes_with_target and commutes_with_others:
                    anticommuting_set.append(candidate)
        
        # Try two-qubit combinations if we need more generators
        if len(anticommuting_set) < 3:  # Arbitrary threshold
            for q1 in range(total_qubits):
                for q2 in range(q1+1, total_qubits):
                    for p1 in ['X', 'Y', 'Z']:
                        for p2 in ['X', 'Y', 'Z']:
                            candidate = stim.PauliString(total_qubits)
                            candidate[q1] = p1
                            candidate[q2] = p2
                            
                            anticommutes_with_target = not candidate.commutes(target_stab)
                            commutes_with_others = all(
                                candidate.commutes(stab) 
                                for i, stab in enumerate(stabilizer_generators) 
                                if i != target_idx
                            )
                            
                            if anticommutes_with_target and commutes_with_others:
                                anticommuting_set.append(candidate)
                                
                            if len(anticommuting_set) >= 5:  # Limit search
                                break
                        if len(anticommuting_set) >= 5:
                            break
                    if len(anticommuting_set) >= 5:
                        break
                if len(anticommuting_set) >= 5:
                    break
        
        anticommuting_sets.append(anticommuting_set)
    
    return anticommuting_sets


def find_bob_only_generators(anticommuting_sets: List[List[stim.PauliString]], 
                           alice_indices: List[int]) -> List[stim.PauliString]:
    """
    Find generators from the anti-commuting sets that have support only on Bob's qubits
    (identity on Alice's qubits).
    
    Args:
        anticommuting_sets: Sets of anti-commuting generators from previous function
        alice_indices: List of Alice's qubit indices
        
    Returns:
        List of Pauli strings with support only on Bob's qubits
    """
    bob_only_generators = []
    
    for anticommuting_set in anticommuting_sets:
        for generator in anticommuting_set:
            # Check if generator has identity on all Alice qubits
            gen_str = str(generator)
            has_alice_support = any(
                alice_idx < len(gen_str) and gen_str[alice_idx] not in ['I', '_'] 
                for alice_idx in alice_indices
            )
            
            if not has_alice_support:
                bob_only_generators.append(generator)
    
    # Remove duplicates while preserving order
    unique_bob_generators = []
    seen = set()
    for gen in bob_only_generators:
        gen_str = str(gen)
        if gen_str not in seen:
            unique_bob_generators.append(gen)
            seen.add(gen_str)
    
    return unique_bob_generators


# Pretty printing utility (reused from previous implementation)
def pretty_pauli_string(pauli: stim.PauliString, show_identities: bool = False) -> str:
    """Convert a Stim PauliString to a readable format."""
    s = str(pauli)
    sign = ""
    if s and s[0] in "+-":
        sign, s = s[0], s[1:]
    
    parts = []
    for i, ch in enumerate(s):
        if ch in ("_", "I"):
            if show_identities:
                parts.append(f"I_{i}")
        else:
            parts.append(f"{ch}_{i}")
    
    body = " ".join(parts) if parts else ("I_0" if show_identities else "I")
    return (sign + " " + body).strip()


def pretty_pauli_list(pauli_list: List[stim.PauliString], show_identities: bool = False) -> List[str]:
    """Convert a list of Stim PauliStrings to readable format."""
    return [pretty_pauli_string(p, show_identities) for p in pauli_list]


class StimVisualizer:
    """Helper class for visualizing Stim circuits and stabilizer states."""
    
    def __init__(self):
        self.circuit_counter = 0
        if not VISUALIZATION_AVAILABLE:
            print("Warning: Visualization dependencies not available. Install matplotlib and IPython for full functionality.")
    
    def pretty_stabilizers(self, stabilizers, show_identities=False, title="Stabilizer Generators"):
        """Pretty print stabilizer generators with numbering."""
        print(f"\n=== {title} ({len(stabilizers)} generators) ===")
        for i, stab in enumerate(stabilizers):
            pretty_str = pretty_pauli_string(stab, show_identities)
            print(f"  S_{i}: {pretty_str}")
        print()
    
    def pretty_anticommuting_sets(self, anticommuting_sets, max_show=3):
        """Pretty print anti-commuting generator sets."""
        print(f"\n=== Anti-commuting Generator Sets ===")
        for i, ac_set in enumerate(anticommuting_sets):
            if ac_set:  # Only show non-empty sets
                print(f"Anti-commuting with S_{i} ({len(ac_set)} found):")
                for j, gen in enumerate(ac_set[:max_show]):
                    print(f"    AC_{i}_{j}: {pretty_pauli_string(gen)}")
                if len(ac_set) > max_show:
                    print(f"    ... and {len(ac_set) - max_show} more")
        print()
    
    def create_circuit_from_cz_gates(self, total_qubits, cz_gates):
        """Create a Stim circuit from CZ gate list for visualization."""
        circuit = stim.Circuit()
        
        # Add all qubits to the circuit (implicit in Stim)
        for q1, q2 in cz_gates:
            circuit.append("CZ", [q1, q2])
        
        return circuit
    
    def visualize_circuit_timeline(self, total_qubits, cz_gates, title="CZ Gates Circuit"):
        """Visualize the CZ gates as a circuit diagram."""
        print(f"\n=== {title} ===")
        
        if not cz_gates:
            print("No CZ gates to visualize")
            return
            
        circuit = self.create_circuit_from_cz_gates(total_qubits, cz_gates)
        
        print(f"Circuit with {len(cz_gates)} CZ gates on {total_qubits} qubits:")
        print(circuit)
        
        # Create a timeline diagram
        try:
            # Stim's timeline diagram (if available)
            diagram_helper = circuit.diagram("timeline-svg")
            # Convert the diagram helper to string
            diagram_svg = str(diagram_helper)
            
            self.circuit_counter += 1
            filename = f"circuit_timeline_{self.circuit_counter}.svg"
            
            with open(filename, "w") as f:
                f.write(diagram_svg)
            print(f"Timeline diagram saved to {filename}")
            
            # Try to display in notebook
            if VISUALIZATION_AVAILABLE:
                try:
                    display(SVG(diagram_svg))
                except:
                    print("Could not display SVG inline, but saved to file")
            else:
                print("Install IPython to display diagrams inline")
                
        except Exception as e:
            print(f"Timeline diagram not available: {e}")
            # Fallback: show circuit as text
            print("Showing circuit as text instead:")
            for i, (q1, q2) in enumerate(cz_gates):
                print(f"  Step {i}: CZ({q1}, {q2})")
            
        print()
    
    def visualize_system_evolution(self, system, cz_gates, updated_stabilizers):
        """Show the complete system evolution."""
        print("="*60)
        print("QUANTUM SYSTEM EVOLUTION VISUALIZATION")
        print("="*60)
        
        print(f"Alice qubits: {system.alice_indices}")
        print(f"Bob qubits: {system.bob_indices}")
        print(f"Total qubits: {system.total_qubits}")
        
        # Initial state
        self.pretty_stabilizers(system.stabilizer_generators, 
                               title="Initial Stabilizer Generators")
        
        # CZ gates visualization
        print(f"\n=== Applied CZ Gates ===")
        for i, (q1, q2) in enumerate(cz_gates):
            alice_q1 = q1 in system.alice_indices
            alice_q2 = q2 in system.alice_indices
            gate_type = "Alice-Bob" if alice_q1 != alice_q2 else ("Bob-Bob" if not alice_q1 else "Alice-Alice")
            print(f"  CZ_{i}: CZ({q1}, {q2}) [{gate_type}]")
        
        self.visualize_circuit_timeline(system.total_qubits, cz_gates, 
                                       "CZ Entangling Operations")
        
        # Updated stabilizers
        self.pretty_stabilizers(updated_stabilizers, 
                               title="Updated Stabilizer Generators After CZ")
    
    def analyze_bob_only_measurements(self, bob_only_generators, system, updated_stabilizers):
        """Detailed analysis of Bob-only measurement candidates."""
        print(f"\n=== Bob-only Measurement Analysis ===")
        print(f"Found {len(bob_only_generators)} Bob-only generators")
        
        if not bob_only_generators:
            print("⚠️  No Bob-only generators found!")
            print("   Try increasing the number of CZ gates or changing system parameters.")
            return
        
        for i, gen in enumerate(bob_only_generators[:8]):  # Show first 8
            print(f"\nMeasurement candidate {i+1}: {pretty_pauli_string(gen)}")
            
            # Show support analysis
            gen_str = str(gen)
            support_qubits = []
            for j in range(len(gen_str)):
                if j < len(gen_str) and gen_str[j] not in ['I', '_']:
                    support_qubits.append(j)
            
            bob_qubits = [j - system.n_alice for j in support_qubits if j >= system.n_alice]
            print(f"  Support on Bob qubits: {bob_qubits}")
            
            # Find which stabilizer this anti-commutes with
            for stab_idx, stab in enumerate(updated_stabilizers):
                if not gen.commutes(stab):
                    print(f"  Anti-commutes with S_{stab_idx}: {pretty_pauli_string(stab)}")
                    break
        
        if len(bob_only_generators) > 8:
            print(f"\n... and {len(bob_only_generators) - 8} more Bob-only generators")
    
    def plot_scaling_analysis(self, scaling_results):
        """Plot performance scaling results."""
        if not VISUALIZATION_AVAILABLE:
            print("Matplotlib not available for plotting. Install matplotlib to see plots.")
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        qubits = [r['total_qubits'] for r in scaling_results]
        times = [r['time_seconds'] for r in scaling_results]
        bob_only_counts = [r['num_bob_only'] for r in scaling_results]
        
        # Performance plot
        ax1.plot(qubits, times, 'bo-', linewidth=2, markersize=8)
        ax1.set_xlabel('Total Qubits')
        ax1.set_ylabel('Time (seconds)')
        ax1.set_title('Computation Time vs System Size')
        ax1.grid(True, alpha=0.3)
        
        # Bob-only generators plot
        ax2.plot(qubits, bob_only_counts, 'ro-', linewidth=2, markersize=8)
        ax2.set_xlabel('Total Qubits')
        ax2.set_ylabel('Bob-only Generators Found')
        ax2.set_title('Bob-only Measurement Candidates')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        print("\n📈 Scaling Summary:")
        for r in scaling_results:
            print(f"  {r['total_qubits']} qubits: {r['time_seconds']:.3f}s, {r['num_bob_only']} Bob-only")


if __name__ == "__main__":
    # Enhanced demo with visualizations
    print("=== StabMBQC Game - Quantum System Demo with Visualizations ===")
    
    # Create visualizer instance
    viz = StimVisualizer()
    
    # Initialize system
    n_alice = 4
    n_bob = 3  
    k_alice = 2
    
    print(f"🎯 Initializing system: Alice has {n_alice} qubits, Bob has {n_bob} qubits")
    print(f"Alice's code has {k_alice} stabilizer generators")
    
    system = initialize_alice_bob_system(n_alice, n_bob, k_alice)
    
    print(f"\nAlice's qubit indices: {system.alice_indices}")
    print(f"Bob's qubit indices: {system.bob_indices}")
    print(f"Total qubits: {system.total_qubits}")
    
    # Use visualizer for initial state
    viz.pretty_stabilizers(system.stabilizer_generators, title="Initial System State")
    
    # Generate random CZ gates
    cz_gates = generate_random_cz_gates(system, num_gates=4)
    print(f"🔗 Generated {len(cz_gates)} random CZ gates: {cz_gates}")
    
    # Update stabilizers after CZ gates
    updated_stabilizers = update_stabilizers_after_cz(system, cz_gates)
    
    # Use visualizer for complete system evolution
    viz.visualize_system_evolution(system, cz_gates, updated_stabilizers)
    
    # Find anti-commuting generators with visualization
    anticommuting_sets = find_anticommuting_generators(updated_stabilizers, system.total_qubits)
    viz.pretty_anticommuting_sets(anticommuting_sets)
    
    # Find Bob-only generators with detailed analysis
    bob_only = find_bob_only_generators(anticommuting_sets, system.alice_indices)
    viz.analyze_bob_only_measurements(bob_only, system, updated_stabilizers)
    
    print("\n🎉 Demo completed! All visualization tools integrated.")