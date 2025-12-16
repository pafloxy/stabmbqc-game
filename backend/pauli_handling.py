
"""Helpers for sparse Pauli string notation like "X3 X1 X2".

Ordering of factors is ignored; indices are zero-based. Tokens must be of the
form X<i>, Y<i>, or Z<i> (case-insensitive). We canonicalize by sorting
qubit indices and build a Stim PauliString with identities elsewhere.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from backend.stim_import import stim


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


__all__ = [
    "canonicalize_sparse_pauli",
    "parse_sparse_pauli",
    "paulistring_to_sparse",
    "stim_to_symplectic",
    "gf2_rowspan_decompose",
    "is_logical_pauli_sparse",
]

# Stim opcodes for readability
_OPCODE_TO_CHAR = {0: "I", 1: "X", 2: "Y", 3: "Z"}
_CHAR_TO_OPCODE = {"I": 0, "X": 1, "Y": 2, "Z": 3}


def paulistring_to_sparse(p: stim.PauliString) -> str:
    """Convert a Stim PauliString to sparse \"X0 Z3\" notation."""
    tokens: List[str] = []
    for q in range(len(p)):
        op = _OPCODE_TO_CHAR.get(p[q], "I")
        if op in ("X", "Y", "Z"):
            tokens.append(f"{op}{q}")
    return " ".join(tokens)


def stim_to_symplectic(p: stim.PauliString, n: int):
    """Return (x, z) bit-vectors (lists of ints) for a Stim PauliString."""

    x = [0] * n
    z = [0] * n
    for i in range(n):
        op = p[i]
        if op == _CHAR_TO_OPCODE["X"]:
            x[i] = 1
        elif op == _CHAR_TO_OPCODE["Z"]:
            z[i] = 1
        elif op == _CHAR_TO_OPCODE["Y"]:
            x[i] = 1
            z[i] = 1
    return x, z


def gf2_rowspan_decompose(S, p):
    """
    Decide whether p is in rowspan(S) over GF(2), returning (in_span, coeffs).

    Args:
        S: matrix as list of rows, each a list of bits (m x d)
        p: list of length d

    Returns:
        (in_span, coeffs)
        - in_span: True iff p ∈ rowspan(S)
        - coeffs: length-m list; when in_span=True, coeffs^T S = p (mod 2)
    """

    m = len(S)
    d = len(S[0]) if m else len(p)
    S = [row.copy() for row in S]
    p = list(p)
    comb = [[1 if i == j else 0 for j in range(m)] for i in range(m)]

    pivot_row = 0
    pivots: List[Tuple[int, int]] = []
    for col in range(d):
        if pivot_row >= m:
            break
        pr = None
        for r in range(pivot_row, m):
            if S[r][col]:
                pr = r
                break
        if pr is None:
            continue
        if pr != pivot_row:
            S[pivot_row], S[pr] = S[pr], S[pivot_row]
            comb[pivot_row], comb[pr] = comb[pr], comb[pivot_row]
        for r in range(pivot_row + 1, m):
            if S[r][col]:
                S[r] = [(a ^ b) for a, b in zip(S[r], S[pivot_row])]
                comb[r] = [(a ^ b) for a, b in zip(comb[r], comb[pivot_row])]
        pivots.append((pivot_row, col))
        pivot_row += 1

    coeffs = [0] * m
    for r, col in pivots:
        if p[col]:
            p = [(a ^ b) for a, b in zip(p, S[r])]
            coeffs = [(a ^ b) for a, b in zip(coeffs, comb[r])]

    in_span = all(val == 0 for val in p)
    return in_span, coeffs


def is_logical_pauli_sparse(
    candidate: str,
    stabilizers: List[str],
    num_qubits: int | None = None,
) -> Tuple[str, Dict[str, object] | None]:
    """
    Determine if a sparse Pauli string is a logical operator with respect to a
    given commuting stabilizer generator set. Provides three types of information:
    1. If logical: returns "logical"
    2. If anticommuting: returns "anticommuting" with which generators
    3. If in stabilizer span: returns "stabilizer" with decomposition

    Args:
        candidate: sparse Pauli string, e.g. "X1 Z3" (indices are zero-based).
        stabilizers: list of sparse Pauli strings for an independent commuting
            stabilizer generator set.
        num_qubits: optional total qubits; inferred if omitted from the max index
            present across the candidate and stabilizers.

    Returns:
        (status, details)
        - If status is "logical": details is None.
        - If status is "anticommuting": details contains:
            - "anticommuting_with": List[int] indices of generators that anticommute.
        - If status is "stabilizer": details contains:
            - "generator_indices": List[int] indices of generators in decomposition.
            - "product_sparse": str sparse notation of the resulting product.
            - "note": str note on phase handling (overall phase ignored).

    Notes:
        - Overall phases (±1, ±i) are ignored; matching is on the operator
          pattern only.
        - Stabilizers are assumed mutually commuting and independent.
    """

    def _infer_num_qubits() -> int:
        if num_qubits is not None:
            return num_qubits
        max_idx = -1
        for spec in [candidate] + list(stabilizers):
            for idx in _parse_tokens(spec).keys():
                max_idx = max(max_idx, idx)
        return max_idx + 1 if max_idx >= 0 else 0

    n = _infer_num_qubits()

    # Parse with consistent length.
    p_cand = parse_sparse_pauli(candidate, num_qubits=n)
    gens = [parse_sparse_pauli(s, num_qubits=n) for s in stabilizers]
    m = len(gens)

    # Early exit when no stabilizers are provided.
    if m == 0:
        is_identity = all(p_cand[q] == _CHAR_TO_OPCODE["I"] for q in range(len(p_cand)))
        if is_identity:
            return "stabilizer", {
                "generator_indices": [],
                "product_sparse": "",
                "note": "No stabilizers; identity is trivial; phases ignored.",
            }
        return "logical", None

    # Build symplectic vectors
    x_c, z_c = stim_to_symplectic(p_cand, n)
    x_g, z_g = [], []
    for g in gens:
        x, z = stim_to_symplectic(g, n)
        x_g.append(x)
        z_g.append(z)

    # Commutation check via symplectic form
    anticommuting_indices = []
    for i, (x, z) in enumerate(zip(x_g, z_g)):
        comm_sum = 0
        for a, b in zip(x_c, z):
            comm_sum += a * b
        for a, b in zip(z_c, x):
            comm_sum += a * b
        comm = comm_sum % 2
        if comm == 1:
            anticommuting_indices.append(i)
    if anticommuting_indices:
        return "anticommuting", {
            "anticommuting_with": anticommuting_indices,
            "note": f"Anticommutes with generators {anticommuting_indices}; not logical and not in stabilizer group.",
        }

    S = [x + z for x, z in zip(x_g, z_g)]
    p_vec = x_c + z_c

    in_span, coeffs = gf2_rowspan_decompose(S, p_vec)
    if in_span:
        selected_indices = [int(i) for i, v in enumerate(coeffs) if v == 1]
        prod = stim.PauliString(n)
        for i in selected_indices:
            prod *= gens[i]
        product_sparse = paulistring_to_sparse(prod)
        return "stabilizer", {
            "generator_indices": selected_indices,
            "product_sparse": product_sparse,
            "note": "Overall phase ignored in decomposition.",
        }

    # Commutes with all stabilizers and not in their span -> logical.
    return "logical", None
