"""Main quantum logic for the StabMBQC game.

This is where you put the real physics:
- Stim tableaux and circuits
- stabilizer updates under CZ and Pauli rotations
- extractability checks for Level 2

The rest of the backend modules should call into functions defined here.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

# NOTE: import Stim/Qiskit here once installed, e.g.:
# import stim
# from qiskit import QuantumCircuit


@dataclass
class Candidate:
  """A candidate Pauli measurement offered to the player.

  label: human-readable with spaces, e.g. "Z I X I"
  pauli: compact form for the backend/frontend, e.g. "ZIXI"
  """

  label: str
  pauli: str


@dataclass
class RoundPhysicsResult:
  """Container for the raw physics result of one round.

  This is intentionally backend-facing and can be richer than what the
  front-end sees; `rounds.py` can convert it into the JSON-friendly
  structure used by the game.
  """

  num_qubits: int
  stabilizers: List[str]
  candidates: List[Candidate]
  # You can add more fields later, e.g. tableau, attack description, etc.


def generate_round_physics(level: int, round_index: int) -> RoundPhysicsResult:
  """Stub for the main physics generator for a single round.

  This is where you'll:
  - build Alice's code (using Stim/tableaux),
  - apply Bob's CZ + rotations,
  - compute the updated stabilizers,
  - generate candidate Pauli measurements and decide which are safe.

  For now this just returns a tiny dummy example; replace with real logic.
  """

  # TODO: replace this with Stim/Qiskit-based generation.
  num_qubits = 3
  stabilizers = ["ZZI", "IZZ"]
  candidates = [
    Candidate(label="Z I I", pauli="ZII"),
    Candidate(label="X I I", pauli="XII"),
    Candidate(label="X X X", pauli="XXX"),
  ]

  return RoundPhysicsResult(
    num_qubits=num_qubits,
    stabilizers=stabilizers,
    candidates=candidates,
  )
