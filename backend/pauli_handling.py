
"""Helpers for sparse Pauli string notation like "X3 X1 X2".

Ordering of factors is ignored; indices are zero-based. Tokens must be of the
form X<i>, Y<i>, or Z<i> (case-insensitive). We canonicalize by sorting
qubit indices and build a Stim PauliString with identities elsewhere.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

import stim


def canonicalize_sparse_pauli(pauli_spec: str) -> str:
    """Return a canonical, index-sorted string (e.g., "X1 X2 X3")."""
    tokens = _parse_tokens(pauli_spec)
    sorted_tokens = [f"{op}{idx}" for idx, op in sorted(tokens.items())]
    return " ".join(sorted_tokens)


def parse_sparse_pauli(pauli_spec: str, num_qubits: int | None = None) -> stim.PauliString:
    """
    Parse a sparse Pauli specification like "X3 X1 X2" into a Stim PauliString.

    Args:
        pauli_spec: whitespace- or '*' separated tokens, each X<i>/Y<i>/Z<i>.
        num_qubits: optional total qubits; inferred as max index + 1 if omitted.

    Raises:
        ValueError on malformed tokens or conflicting operators on the same qubit.
    """
    tokens = _parse_tokens(pauli_spec)
    if not tokens and num_qubits is None:
        # Empty spec -> length 0 PauliString
        return stim.PauliString(0)

    max_idx = max(tokens.keys(), default=-1)
    n = num_qubits if num_qubits is not None else (max_idx + 1)
    if n <= max_idx:
        raise ValueError(f"num_qubits={n} is too small for max index {max_idx}")
    if n < 0:
        raise ValueError("num_qubits must be non-negative")

    p = stim.PauliString(n)
    for idx, op in tokens.items():
        p[idx] = op
    return p


def _parse_tokens(pauli_spec: str) -> Dict[int, str]:
    tokens: Dict[int, str] = {}
    raw_tokens = pauli_spec.replace("*", " ").split()
    for tok in raw_tokens:
        tok = tok.strip()
        if not tok:
            continue
        op = tok[0].upper()
        if op not in ("X", "Y", "Z"):
            raise ValueError(f"Invalid Pauli operator in token '{tok}'")
        idx_str = tok[1:]
        if not idx_str.isdigit():
            raise ValueError(f"Missing/invalid qubit index in token '{tok}'")
        idx = int(idx_str)
        prev = tokens.get(idx)
        if prev is not None and prev != op:
            raise ValueError(f"Conflicting operators on qubit {idx}: {prev} vs {op}")
        tokens[idx] = op
    return tokens


__all__ = ["canonicalize_sparse_pauli", "parse_sparse_pauli"]
