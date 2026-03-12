from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass(frozen=True)
class Evolution:
    node_id: str
    pauli: str
    angle_label: str
    original_index: int


@dataclass(frozen=True)
class OptimizationInstance:
    stabilizers: List[str]
    evolutions: List[Evolution]
    measurements: List[str]


@dataclass
class CanonicalizationResult:
    stabilizers: List[str]
    measurements: List[str]
    common_generators: List[str]
    stabilizer_only: List[str]
    measurement_only: List[str]


@dataclass
class PDDAG:
    nodes: Dict[str, Evolution]
    order: List[str]
    edges: Dict[str, Set[str]]
    reverse_edges: Dict[str, Set[str]]


@dataclass
class DistanceLayers:
    d_m: Dict[str, int]
    layers: Dict[int, List[str]]


@dataclass
class Gf2SolveResult:
    satisfiable: bool
    rank: int
    pivot_columns: List[int]
    free_columns: List[int]
    representative: List[int] | None
    nullspace_basis: List[List[int]]


@dataclass
class SelectorSystem:
    node_id: str
    pauli: str
    pred_gt0: List[str]
    non_pred_gt0: List[str]
    a1: List[List[int]]
    b1: List[int]
    a2: List[List[int]]
    b2: List[int]
    a3: List[List[int]]
    b3: List[int]
    a: List[List[int]]
    b: List[int]
    solve_result: Gf2SolveResult
    chosen_selector: List[int] | None
    chosen_stabilizer: str | None
    representative_policy: str


@dataclass
class RoundTrace:
    round_index: int
    snapshot_before: Dict[str, object]
    selector_systems: List[SelectorSystem]
    extr_sol: Dict[str, List[int]]
    rewrite_data: Dict[str, object]
    snapshot_after: Dict[str, object]


@dataclass
class OptimizeResult:
    final_pddag: PDDAG
    extracted: Set[str]
    unresolved: Set[str]
    traces: List[RoundTrace] = field(default_factory=list)
