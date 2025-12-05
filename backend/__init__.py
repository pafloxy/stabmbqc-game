"""Backend package for the StabMBQC game.

This package is responsible for generating level/round data
and doing all quantum/stabilizer/stim logic.

Typical responsibilities:
- Construct Alice's stabilizer code.
- Apply Bob's CZ + Pauli-rotation attacks.
- Use Stim (and optionally Qiskit) to compute updated stabilizers.
- Propose candidate Pauli measurements and label which are safe.
- Render circuit/graph images for the front-end.
"""
