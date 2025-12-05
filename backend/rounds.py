"""High-level round construction.

This module glues together:
- the low-level physics in qc-main0.py
- the typed models in model.py
- the rendering helpers in rendering.py

so that you can easily generate LevelSpec instances and dump them to JSON.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from . import qc-main0 as qc
from .model import Candidate, RoundSpec
from .rendering import render_circuit_png, render_graph_png


def build_round(
  level: int,
  round_index: int,
  assets_dir: Path,
) -> RoundSpec:
  """Create a RoundSpec for the given level/round index.

  This function:
  - calls into the physics layer (qc-main0) to generate stabilizers/candidates,
  - optionally renders circuit/graph images,
  - wraps everything into a RoundSpec.
  """

  physics_result = qc.generate_round_physics(level=level, round_index=round_index)

  circuit_name = f"level{level}-round{round_index:02d}-circuit.png"
  graph_name = f"level{level}-round{round_index:02d}-graph.png"

  circuit_path = assets_dir / circuit_name
  graph_path = assets_dir / graph_name

  circuit_rel = render_circuit_png(attack_description=None, out_path=circuit_path)
  graph_rel = render_graph_png(graph_description=None, out_path=graph_path)

  candidates: List[Candidate] = [
    Candidate(label=c.label, pauli=c.pauli) for c in physics_result.candidates
  ]

  text = "Auto-generated round (dummy text for now)."

  return RoundSpec(
    id=round_index,
    label=f"Round {round_index + 1}",
    text=text,
    num_qubits=physics_result.num_qubits,
    stabilizers=physics_result.stabilizers,
    candidates=candidates,
    graph_image=str(graph_rel),
    circuit_image=str(circuit_rel),
  )
