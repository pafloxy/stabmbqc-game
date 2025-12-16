"""Synthesize a Clifford from stabilizer-destabilizer pairs using Stim.

This follows the design in clifford-from-map.md: given pairs (S_i, D_i) that
anticommute within each pair and commute across pairs, build a Clifford C that
maps them to standard form (or the inverse).
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Optional

import stim

from pauli_handling import (
    parse_sparse_pauli,
    paulistring_to_sparse,
    stim_to_symplectic,
    gf2_rowspan_decompose,
)


def _validate_partial_frame(S: List[stim.PauliString], D: List[stim.PauliString]) -> None:
    m = len(S)
    if len(D) != m:
        raise ValueError("S and D must have same length")
    for i in range(m):
        if S[i].commutes(D[i]):
            raise ValueError(f"pair {i} invalid: S_i must anticommute with D_i")
    for i in range(m):
        for j in range(m):
            if i == j:
                continue
            if not S[i].commutes(S[j]):
                raise ValueError(f"S[{i}] must commute with S[{j}]")
            if not D[i].commutes(D[j]):
                raise ValueError(f"D[{i}] must commute with D[{j}]")
            if not S[i].commutes(D[j]):
                raise ValueError(f"S[{i}] must commute with D[{j}] for i!=j")


def _symp_vec(p: stim.PauliString, n: int):
    x, z = stim_to_symplectic(p, n)
    return x + z


def _symp_commutes(v1, v2, n: int) -> bool:
    total = 0
    for i in range(n):
        total ^= (v1[i] & v2[n + i]) ^ (v1[n + i] & v2[i])
    return (total & 1) == 0


def _enumerate_paulis(n: int, max_weight: int = 3):
    """Yield stim.PauliString of weight up to max_weight."""
    from itertools import combinations, product

    ops = [1, 3, 2]  # X, Z, Y
    # weight 1..max_weight
    for w in range(1, max_weight + 1):
        for qubits in combinations(range(n), w):
            for pauli_ops in product(ops, repeat=w):
                p = stim.PauliString(n)
                for q, op in zip(qubits, pauli_ops):
                    p[q] = op
                yield p


def _enumerate_all_paulis(n: int):
    """Exhaustive generator over all non-identity Paulis on n qubits."""
    if n <= 0:
        return
    # Base-4 enumeration: 0=I,1=X,2=Y,3=Z
    total = 4 ** n
    for val in range(1, total):  # skip all-identity
        p = stim.PauliString(n)
        tmp = val
        for q in range(n):
            tmp, digit = divmod(tmp, 4)
            if digit == 1:
                p[q] = "X"
            elif digit == 2:
                p[q] = "Y"
            elif digit == 3:
                p[q] = "Z"
        yield p


def _gf2_solve(A, b):
    """Solve A x = b over GF(2); return one solution or None if inconsistent."""

    A = [row.copy() for row in A]
    b = list(b)
    m = len(A)
    n = len(A[0]) if m else 0
    aug = [row + [b[i]] for i, row in enumerate(A)]
    row = 0
    pivots = [-1] * n
    for col in range(n):
        if row >= m:
            break
        pivot = None
        for r in range(row, m):
            if aug[r][col]:
                pivot = r
                break
        if pivot is None:
            continue
        if pivot != row:
            aug[row], aug[pivot] = aug[pivot], aug[row]
        pivots[col] = row
        for r in range(m):
            if r != row and aug[r][col]:
                aug[r] = [(a ^ b) for a, b in zip(aug[r], aug[row])]
        row += 1
    for r in range(m):
        if all(val == 0 for val in aug[r][:-1]) and aug[r][-1] == 1:
            return None
    x = [0] * n
    for col in range(n):
        r = pivots[col]
        if r != -1:
            x[col] = aug[r][-1]
    return x


def _symp_to_pauli(v, n: int) -> stim.PauliString:
    p = stim.PauliString(n)
    x = v[:n]
    z = v[n:]
    for i in range(n):
        if x[i] and z[i]:
            p[i] = "Y"
        elif x[i]:
            p[i] = "X"
        elif z[i]:
            p[i] = "Z"
    return p


def _complete_symplectic_frame(
    X_img,
    Z_img,
    n: int,
    *,
    max_weight: int = 3,
    completion: str = "search",
) -> None:
    """Fill None entries of X_img/Z_img to complete a symplectic frame.

    completion:
        - "search": low-weight enumeration with GF(2) solving for partners
    """
    if completion != "search":
        raise ValueError("Unsupported completion strategy; only 'search' is implemented")

    for q in range(n):
        if X_img[q] is not None and Z_img[q] is not None:
            continue

        # Build existing vectors for commutation/span checks
        existing = []
        for v in X_img:
            if v is not None:
                existing.append(_symp_vec(v, n))
        for v in Z_img:
            if v is not None:
                existing.append(_symp_vec(v, n))
        existing_mat = [row[:] for row in existing]

        found_pair = False
        # Iterate over X candidates; for each, try to find matching Z
        for x_search_w in range(1, max_weight + 1):
            if found_pair:
                break
            x_candidates = list(_enumerate_paulis(n, max_weight=x_search_w))
            if x_search_w == n:
                x_candidates += list(_enumerate_all_paulis(n))
            for X_candidate in x_candidates:
                vX = _symp_vec(X_candidate, n)
                if any(not _symp_commutes(vX, e, n) for e in existing):
                    continue
                in_span, _ = gf2_rowspan_decompose(existing_mat, vX) if existing_mat else (False, None)
                if in_span:
                    continue

                # Update temporary existing with X_candidate
                temp_existing = existing + [vX]
                temp_mat = [row[:] for row in temp_existing]

                # Solve linear constraints for Z: commute with all temp_existing[:-1], anticommute with vX
                constraints = []
                rhs = []
                for e in temp_existing[:-1]:
                    constraints.append(e)
                    rhs.append(0)
                constraints.append(vX)
                rhs.append(1)
                A = [row[:] for row in constraints]
                bvec = list(rhs)
                sol = _gf2_solve(A, bvec)
                if sol is not None and temp_mat:
                    in_span_z, _ = gf2_rowspan_decompose(temp_mat, sol)
                    if in_span_z:
                        sol = None
                Z_candidate = _symp_to_pauli(sol, n) if sol is not None else None

                if Z_candidate is None:
                    z_found = False
                    for z_search_w in range(1, max_weight + 1):
                        if z_found:
                            break
                        z_candidates = list(_enumerate_paulis(n, max_weight=z_search_w))
                        if z_search_w == n:
                            z_candidates += list(_enumerate_all_paulis(n))
                        for cand in z_candidates:
                            v = _symp_vec(cand, n)
                            if _symp_commutes(v, vX, n):
                                continue
                            if any(not _symp_commutes(v, e, n) for e in temp_existing):
                                continue
                            in_span_z, _ = gf2_rowspan_decompose(temp_mat, v) if temp_mat else (False, None)
                            if in_span_z:
                                continue
                            Z_candidate = cand
                            z_found = True
                            break
                if Z_candidate is None:
                    continue

                # Success
                X_img[q] = X_candidate
                Z_img[q] = Z_candidate
                existing = temp_existing
                found_pair = True
                break

        if not found_pair:
            # Final fallback: brute-force over all commuting candidates and pick an anticommute pair
            commuting_candidates = []
            for cand in _enumerate_all_paulis(n):
                v = _symp_vec(cand, n)
                if any(not _symp_commutes(v, e, n) for e in existing):
                    continue
                in_span, _ = gf2_rowspan_decompose(existing_mat, v) if existing_mat else (False, None)
                if in_span:
                    continue
                commuting_candidates.append((cand, v))
            for i, (xcand, vX) in enumerate(commuting_candidates):
                for zcand, vZ in commuting_candidates[i + 1 :]:
                    if _symp_commutes(vX, vZ, n):
                        continue
                    # Ensure combined span independence
                    temp_mat = [row[:] for row in existing + [vX]]
                    in_span_z, _ = gf2_rowspan_decompose(temp_mat, vZ) if temp_mat else (False, None)
                    if in_span_z:
                        continue
                    X_img[q] = xcand
                    Z_img[q] = zcand
                    existing = existing + [vX, vZ]
                    found_pair = True
                    break
                if found_pair:
                    break
        if not found_pair:
            raise RuntimeError(f"Could not find symplectic pair for qubit {q}")


def synthesize_clifford_from_sd_pairs(
    pairs: List[Tuple[str, str]],
    *,
    num_qubits: int,
    target_qubits: Optional[List[int]] = None,
    direction: str = "pairs_to_standard",
    max_weight_search: int = 3,
    completion: str = "search",
) -> Dict[str, object]:
    """Return a Clifford tableau/circuit consistent with stabilizer–destabilizer pairs.

    This is the high-level entry point described in ``backend/clifford-from-map.md``. The
    inputs ``pairs`` are strings that describe stabilizer/destabilizer partners following
    the sparse format accepted by :func:`pauli_handling.parse_sparse_pauli` (e.g. ``"Z1 X3"``).
    Each tuple must anticommute within the pair and commute with all other tuples. The
    routine completes the partial symplectic frame, synthesizes a Stim tableau, and returns
    both the tableau and the corresponding Clifford circuit.

    Args:
        pairs: ``[(S_0, D_0), (S_1, D_1), ...]`` where each entry is a sparse Pauli string
            describing the stabilizer ``S_i`` and its destabilizer partner ``D_i``.
        num_qubits: Total number of qubits for the Clifford/tableau.
        target_qubits: Optional explicit mapping ``q_i`` where each pair should land in the
            canonical frame (default ``q_i=i``). Length must match ``pairs`` and qubits must
            be distinct.
        direction: If ``"pairs_to_standard"`` (default) the returned Clifford ``C`` maps the
            provided frame to canonical single-qubit Paulis: ``C S_i C† = Z_{q_i}``,
            ``C D_i C† = X_{q_i}``. If ``"standard_to_pairs"``, returns a tableau ``T`` that
            performs the inverse mapping ``Z_{q_i} -> S_i``, ``X_{q_i} -> D_i``.
        max_weight_search: Maximum Pauli weight when enumerating candidates to complete the
            symplectic basis.
        completion: Strategy for filling missing generators (currently only ``"search"``).

    Returns:
        dict with keys:
            "tableau": Stim tableau implementing the requested mapping.
            "circuit": Clifford circuit derived from the tableau.
            "target_qubits": The resolved target qubits used for the mapping.
            "diagnostics": Sparse representations of the completed symplectic frame.

    Example:
        >>> pairs = [
        ...     ("Z1 X3", "Z3"),
        ...     ("Z0 Z2 X4", "X2"),
        ...     ("Y0 Y1 Z3 Z4", "Z0"),
        ...     ("Z0 X1 X2 Z3 Z4", "Z0 Z1"),
        ... ]
        >>> result = synthesize_clifford_from_sd_pairs(pairs, num_qubits=5)
        >>> result["tableau"].verify()  # doctest: +ELLIPSIS
        ...
        >>> result["circuit"]  # doctest: +ELLIPSIS
        stim.Circuit(...)
    """
    if num_qubits <= 0:
        raise ValueError("num_qubits must be positive")
    if direction not in ("pairs_to_standard", "standard_to_pairs"):
        raise ValueError("direction must be 'pairs_to_standard' or 'standard_to_pairs'")
    m = len(pairs)
    if target_qubits is None:
        target_qubits = list(range(m))
    if len(target_qubits) != m:
        raise ValueError("target_qubits length must match pairs length")
    if len(set(target_qubits)) != m:
        raise ValueError("target_qubits must be distinct")

    S = [parse_sparse_pauli(s, num_qubits=num_qubits) for s, _ in pairs]
    D = [parse_sparse_pauli(d, num_qubits=num_qubits) for _, d in pairs]
    _validate_partial_frame(S, D)

    X_img: List[Optional[stim.PauliString]] = [None] * num_qubits
    Z_img: List[Optional[stim.PauliString]] = [None] * num_qubits
    for i, q in enumerate(target_qubits):
        Z_img[q] = S[i]
        X_img[q] = D[i]

    _complete_symplectic_frame(
        X_img,
        Z_img,
        num_qubits,
        max_weight=max_weight_search,
        completion=completion,
    )

    ctor = getattr(stim.Tableau, "from_conjugated_generators", None)
    if ctor is None:
        raise RuntimeError("Stim Tableau.from_conjugated_generators not found")
    T = ctor(xs=X_img, zs=Z_img)

    C = T.inverse() if direction == "pairs_to_standard" else T
    return {
        "tableau": C,
        "circuit": C.to_circuit(),
        "target_qubits": target_qubits,
        "diagnostics": {
            "xs_sparse": [paulistring_to_sparse(p) for p in X_img],
            "zs_sparse": [paulistring_to_sparse(p) for p in Z_img],
        },
    }

def conjugate(tableau, p):
    # Real Stim
    try:
        return tableau(p)
    except TypeError:
        pass
    # Stub / fallback
    if hasattr(tableau, "conjugate_pauli_string"):
        return tableau.conjugate_pauli_string(p)
    raise AttributeError("Tableau conjugation method not found.")
