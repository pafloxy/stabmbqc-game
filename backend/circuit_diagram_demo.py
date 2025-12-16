#!/usr/bin/env python3
"""
Circuit Diagram Demonstration Script
Shows both text-mode and SVG-mode circuit diagrams for StabMBQC systems
"""

import sys
import os
import random
from backend.stim_import import stim

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from qcmain1 import *

def demo_text_circuit_diagram():
    """Demonstrate text-mode circuit diagram."""
    print("📝 TEXT-MODE CIRCUIT DIAGRAM DEMO")
    print("="*50)

    # Create a simple system
    system = initialize_alice_bob_system(3, 2, 2)
    cz_gates = [(0, 3), (1, 4), (2, 3), (3, 4)]  # Simple CZ gates

    print(f"System: {system.total_qubits} qubits")
    print(f"CZ gates: {cz_gates}")
    print()

    # Create Stim circuit
    circuit = stim.Circuit()
    for q1, q2 in cz_gates:
        circuit.append("CZ", [q1, q2])

    print("Circuit as text:")
    print(circuit)
    print()

    # Show circuit diagram in text mode
    print("Circuit diagram (text mode):")
    try:
        text_diagram = circuit.diagram("timeline-text")
        print(text_diagram)
    except Exception as e:
        print(f"Text diagram not available: {e}")

    print()

def demo_svg_circuit_diagram():
    """Demonstrate SVG-mode circuit diagram."""
    print("🎨 SVG-MODE CIRCUIT DIAGRAM DEMO")
    print("="*50)

    # Create a more complex system
    system = initialize_alice_bob_system(4, 3, 2)
    random.seed(42)
    cz_gates = generate_random_cz_gates(system, num_gates=6)

    print(f"System: {system.total_qubits} qubits")
    print(f"Alice qubits: {system.alice_indices}")
    print(f"Bob qubits: {system.bob_indices}")
    print(f"Generated CZ gates: {cz_gates}")
    print()

    # Create Stim circuit
    circuit = stim.Circuit()
    for q1, q2 in cz_gates:
        circuit.append("CZ", [q1, q2])

    print("Circuit as text:")
    print(circuit)
    print()

    # Show circuit diagram in SVG mode
    print("Circuit diagram (SVG mode):")
    try:
        svg_diagram = circuit.diagram("timeline-svg")
        svg_string = str(svg_diagram)  # Convert to string

        # Save to file
        filename = "demo_circuit_diagram.svg"
        with open(filename, "w") as f:
            f.write(svg_string)

        print(f"✅ SVG diagram saved to: {filename}")
        print(f"SVG content length: {len(svg_string)} characters")

        # Show first few lines of SVG for inspection
        print("\nFirst 10 lines of SVG content:")
        lines = svg_string.split('\n')[:10]
        for i, line in enumerate(lines, 1):
            print("2d")

        print("...")
        print(f"(Total {len(svg_string.split(chr(10)))} lines)")

    except Exception as e:
        print(f"SVG diagram not available: {e}")

    print()

def demo_visualizer_integration():
    """Demonstrate the StimVisualizer integration."""
    print("🎯 STIMVISUALIZER INTEGRATION DEMO")
    print("="*50)

    # Create visualizer
    viz = StimVisualizer()

    # Create system
    system = initialize_alice_bob_system(3, 3, 2)
    random.seed(123)
    cz_gates = generate_random_cz_gates(system, num_gates=4)

    print(f"System: {system.total_qubits} qubits")
    print(f"CZ gates: {cz_gates}")
    print()

    # Use the visualizer's timeline method
    print("Using StimVisualizer.visualize_circuit_timeline():")
    viz.visualize_circuit_timeline(system.total_qubits, cz_gates, "Demo Circuit")

    print()

def main():
    """Run all demonstrations."""
    print("🧪 CIRCUIT DIAGRAM DEMONSTRATION")
    print("="*60)
    print("This script demonstrates Stim circuit diagrams in both text and SVG modes")
    print("using examples from the StabMBQC system.")
    print()

    # Demo 1: Text mode
    demo_text_circuit_diagram()

    # Demo 2: SVG mode
    demo_svg_circuit_diagram()

    # Demo 3: Visualizer integration
    demo_visualizer_integration()

    print("🎉 DEMONSTRATION COMPLETE!")
    print("="*60)
    print("Check the generated SVG files to see the visual circuit diagrams.")
    print("The text mode shows circuit structure, while SVG provides graphical timelines.")

if __name__ == "__main__":
    main()