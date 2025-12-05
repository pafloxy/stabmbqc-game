"""Typed models for level and round data.

These mirror (roughly) the JSON structure consumed by the front-end.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any


@dataclass
class Candidate:
  label: str
  pauli: str


@dataclass
class RoundSpec:
  id: int
  label: str
  text: str
  num_qubits: int
  stabilizers: List[str]
  candidates: List[Candidate]
  graph_image: Optional[str] = None
  circuit_image: Optional[str] = None


@dataclass
class LevelSpec:
  id: str
  title: str
  description: str
  round_time_limit_seconds: int
  intro_slides: List[Dict[str, Any]]
  rounds: List[RoundSpec]


def to_json_dict(level: LevelSpec) -> Dict[str, Any]:
  """Convert a LevelSpec into a JSON-serializable dict."""
  return asdict(level)
