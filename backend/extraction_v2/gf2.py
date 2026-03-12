from __future__ import annotations

from itertools import product

from .types import Gf2SolveResult


def solve_affine(a: list[list[int]], b: list[int]) -> Gf2SolveResult:
    m = len(a)
    n = len(a[0]) if m else 0
    aug = [row[:] + [rhs] for row, rhs in zip(a, b)]
    pivot_cols: list[int] = []
    r = 0
    for c in range(n):
        piv = None
        for rr in range(r, m):
            if aug[rr][c] == 1:
                piv = rr
                break
        if piv is None:
            continue
        aug[r], aug[piv] = aug[piv], aug[r]
        for rr in range(m):
            if rr != r and aug[rr][c] == 1:
                aug[rr] = [x ^ y for x, y in zip(aug[rr], aug[r])]
        pivot_cols.append(c)
        r += 1
        if r == m:
            break

    for rr in range(r, m):
        if all(v == 0 for v in aug[rr][:n]) and aug[rr][n] == 1:
            return Gf2SolveResult(False, len(pivot_cols), pivot_cols, [c for c in range(n) if c not in pivot_cols], None, [])

    free_cols = [c for c in range(n) if c not in pivot_cols]
    base = [0] * n
    for rr, c in enumerate(pivot_cols):
        base[c] = aug[rr][n]

    null_basis = []
    for f in free_cols:
        vec = [0] * n
        vec[f] = 1
        for rr, c in enumerate(pivot_cols):
            if aug[rr][f]:
                vec[c] ^= 1
        null_basis.append(vec)

    rep = _deterministic_min_solution(base, null_basis)
    return Gf2SolveResult(True, len(pivot_cols), pivot_cols, free_cols, rep, null_basis)


def _deterministic_min_solution(base: list[int], null_basis: list[list[int]]) -> list[int]:
    if not null_basis:
        return base
    best = None
    for coeffs in product([0, 1], repeat=len(null_basis)):
        cand = base[:]
        for use, vec in zip(coeffs, null_basis):
            if use:
                cand = [x ^ y for x, y in zip(cand, vec)]
        key = (sum(cand), tuple(cand))
        if best is None or key < best[0]:
            best = (key, cand)
    assert best is not None
    return best[1]
