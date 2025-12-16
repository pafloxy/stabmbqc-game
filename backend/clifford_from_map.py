"""Synthesize a Clifford from stabilizer-destabilizer pairs using Stim.

This follows the design in clifford-from-map.md: given pairs (S_i, D_i) that
anticommute within each pair and commute across pairs, build a Clifford C that
maps them to standard form (or the inverse).
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Optional

import stim
import numpy as np

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


def _symp_vec(p: stim.PauliString, n: int) -> np.ndarray:
    return np.concatenate(stim_to_symplectic(p, n)).astype(np.uint8)


def _symp_commutes(v1: np.ndarray, v2: np.ndarray, n: int) -> bool:
    x1, z1 = v1[:n], v1[n:]
    x2, z2 = v2[:n], v2[n:]
    return ((x1 @ z2 + z1 @ x2) & 1) == 0


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


def _gf2_solve(A: np.ndarray, b: np.ndarray) -> Optional[np.ndarray]:
    """Solve A x = b over GF(2); return one solution or None if inconsistent."""
    A = A.copy().astype(np.uint8)
    b = b.copy().astype(np.uint8)
    m, n = A.shape
    aug = np.concatenate([A, b.reshape(m, 1)], axis=1)
    row = 0
    pivots = [-1] * n
    for col in range(n):
        if row >= m:
            break
        pivot = None
        for r in range(row, m):
            if aug[r, col]:
                pivot = r
                break
        if pivot is None:
            continue
        if pivot != row:
            aug[[row, pivot]] = aug[[pivot, row]]
        pivots[col] = row
        for r in range(m):
            if r != row and aug[r, col]:
                aug[r] ^= aug[row]
        row += 1
    # Check inconsistency
    for r in range(m):
        if aug[r, :-1].sum() == 0 and aug[r, -1] == 1:
            return None
    x = np.zeros(n, dtype=np.uint8)
    for col in range(n):
        r = pivots[col]
        if r != -1:
            x[col] = aug[r, -1]
    return x


def _symp_to_pauli(v: np.ndarray, n: int) -> stim.PauliString:
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


def _complete_symplectic_frame(X_img, Z_img, n: int, max_weight: int = 3) -> None:
    """Fill None entries of X_img/Z_img to complete a symplectic frame."""
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
        existing_mat = np.vstack(existing) if existing else np.zeros((0, 2 * n), dtype=np.uint8)

        found_pair = False
        # Iterate over X candidates; for each, try to find matching Z
        for x_search_w in range(max_weight, n + 1):
            if found_pair:
                break
            x_candidates = list(_enumerate_paulis(n, max_weight=x_search_w))
            if x_search_w == n:
                x_candidates += list(_enumerate_all_paulis(n))
            for X_candidate in x_candidates:
                vX = _symp_vec(X_candidate, n)
                if any(not _symp_commutes(vX, e, n) for e in existing):
                    continue
                in_span, _ = gf2_rowspan_decompose(existing_mat, vX) if existing_mat.size else (False, None)
                if in_span:
                    continue

                # Update temporary existing with X_candidate
                temp_existing = existing + [vX]
                temp_mat = np.vstack(temp_existing) if temp_existing else np.zeros((0, 2 * n), dtype=np.uint8)

                # Solve linear constraints for Z: commute with all temp_existing[:-1], anticommute with vX
                constraints = []
                rhs = []
                for e in temp_existing[:-1]:
                    constraints.append(e)
                    rhs.append(0)
                constraints.append(vX)
                rhs.append(1)
                A = np.vstack(constraints) if constraints else np.zeros((0, 2 * n), dtype=np.uint8)
                bvec = np.array(rhs, dtype=np.uint8)
                sol = _gf2_solve(A, bvec)
                if sol is not None and temp_mat.size:
                    in_span_z, _ = gf2_rowspan_decompose(temp_mat, sol)
                    if in_span_z:
                        sol = None
                Z_candidate = _symp_to_pauli(sol, n) if sol is not None else None

                if Z_candidate is None:
                    z_found = False
                    for z_search_w in range(max_weight, n + 1):
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
                            in_span_z, _ = gf2_rowspan_decompose(temp_mat, v) if temp_mat.size else (False, None)
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
                in_span, _ = gf2_rowspan_decompose(existing_mat, v) if existing_mat.size else (False, None)
                if in_span:
                    continue
                commuting_candidates.append((cand, v))
            for i, (xcand, vX) in enumerate(commuting_candidates):
                for zcand, vZ in commuting_candidates[i + 1 :]:
                    if _symp_commutes(vX, vZ, n):
                        continue
                    # Ensure combined span independence
                    temp_mat = np.vstack(existing + [vX])
                    in_span_z, _ = gf2_rowspan_decompose(temp_mat, vZ) if temp_mat.size else (False, None)
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
) -> Dict[str, object]:
    """Return a Clifford tableau/circuit consistent with stabilizer-destabilizer pairs.

    direction:
        - "pairs_to_standard": return C s.t. C S_i C† = Z_q, C D_i C† = X_q
        - "standard_to_pairs": return T that sends Z_q->S_i, X_q->D_i
    """
    if num_qubits <= 0:
        raise ValueError("num_qubits must be positive")
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

    _complete_symplectic_frame(X_img, Z_img, num_qubits, max_weight=max_weight_search)

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
