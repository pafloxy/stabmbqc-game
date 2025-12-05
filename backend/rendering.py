"""Rendering helpers: circuit and graph images.

The real implementation should:
- take the internal description of Bob's attack / Alice's code,
- build a Qiskit (or Stim→Qiskit) circuit,
- draw a PNG/SVG and save it into docs/assets/.

For now we just stub out the functions; you can fill them in as you go.
"""

from __future__ import annotations

from pathlib import Path


def render_circuit_png(attack_description, out_path: Path) -> str:
  """Render a circuit image and return its *relative* path for JSON.

  Parameters
  ----------
  attack_description: Any
      Whatever structure you decide to use to describe the CZ/rotation attack.
  out_path: Path
      Absolute or repo-root-relative path where the PNG will be written.
  """

  # TODO: implement with Qiskit once you wire up the circuits.
  out_path.parent.mkdir(parents=True, exist_ok=True)
  # For now you might write a placeholder PNG or leave it absent.

  # Return a path relative to docs/, e.g. "assets/level1-round01-circuit.png".
  return str(out_path)


def render_graph_png(graph_description, out_path: Path) -> str:
  """Render a graph image (e.g. code connectivity) and return relative path.

  Parameters
  ----------
  graph_description: Any
      Your preferred representation of the stabilizer graph / lattice.
  out_path: Path
      Where to save the graph image.
  """

  # TODO: implement using networkx/matplotlib if you want graph visuals.
  out_path.parent.mkdir(parents=True, exist_ok=True)
  return str(out_path)
