"""Lightweight Stim emulator for offline testing.

Implements only the subset of the API required by the stabilizer utilities
and unit tests in this repository. Arithmetic is over GF(2) with global
phases tracked up to ±1.
"""
from __future__ import annotations

from typing import List, Sequence, Tuple

_OPCODE_TO_CHAR = {0: "I", 1: "X", 2: "Y", 3: "Z"}
_CHAR_TO_OPCODE = {"I": 0, "X": 1, "Y": 2, "Z": 3, "_": 0}


def _symplectic_inner(v1: List[int], v2: List[int]) -> int:
    n = len(v1) // 2
    total = 0
    for i in range(n):
        total ^= (v1[i] & v2[n + i]) ^ (v1[n + i] & v2[i])
    return total & 1


def _gf2_inv(mat: List[List[int]]) -> List[List[int]]:
    n = len(mat)
    aug = [row[:] + [1 if i == j else 0 for j in range(n)] for i, row in enumerate(mat)]
    row = 0
    for col in range(n):
        pivot = None
        for r in range(row, n):
            if aug[r][col]:
                pivot = r
                break
        if pivot is None:
            continue
        if pivot != row:
            aug[row], aug[pivot] = aug[pivot], aug[row]
        for r in range(n):
            if r != row and aug[r][col]:
                aug[r] = [(a ^ b) for a, b in zip(aug[r], aug[row])]
        row += 1
    left = [row[:n] for row in aug]
    if any(left[i][i] != 1 or any(left[i][j] for j in range(n) if j != i) for i in range(n)):
        raise ValueError("Matrix not invertible over GF(2)")
    return [row[n:] for row in aug]


def _vec_to_pauli(v: List[int]) -> "PauliString":
    n = len(v) // 2
    p = PauliString(n)
    for i in range(n):
        x = v[i]
        z = v[n + i]
        if x and z:
            p[i] = "Y"
        elif x:
            p[i] = "X"
        elif z:
            p[i] = "Z"
    return p


class PauliString:
    def __init__(self, spec: int | str | "PauliString" = 0):
        if isinstance(spec, PauliString):
            self.ops = spec.ops.copy()
            self.sign = spec.sign
            return
        self.sign = 1
        if isinstance(spec, int):
            self.ops: List[int] = [0] * spec
        elif isinstance(spec, str):
            if all(ch in "IXYZ_" for ch in spec):
                self.ops = [_CHAR_TO_OPCODE.get(ch, 0) for ch in spec]
            else:
                tokens = spec.replace("*", " ").split()
                max_idx = -1
                parsed: List[Tuple[int, int]] = []
                for tok in tokens:
                    op = tok[0].upper()
                    idx = int(tok[1:]) if tok[1:].isdigit() else 0
                    parsed.append((idx, _CHAR_TO_OPCODE[op]))
                    max_idx = max(max_idx, idx)
                self.ops = [0] * (max_idx + 1)
                for idx, code in parsed:
                    self.ops[idx] = code
        else:
            raise TypeError("Unsupported PauliString initializer")

    def __len__(self):  # type: ignore[override]
        return len(self.ops)

    def __getitem__(self, idx: int) -> int:
        return self.ops[idx]

    def __setitem__(self, idx: int, op):
        if isinstance(op, str):
            op = _CHAR_TO_OPCODE.get(op.upper(), 0)
        self.ops[idx] = int(op)

    def copy(self) -> "PauliString":
        return PauliString(self)

    def commutes(self, other: "PauliString") -> bool:
        n = max(len(self), len(other))
        return _symplectic_inner(self._to_symp(n), other._to_symp(n)) == 0

    def _to_symp(self, n: int) -> List[int]:
        x = [0] * n
        z = [0] * n
        for i, op in enumerate(self.ops):
            if op == 1:
                x[i] = 1
            elif op == 3:
                z[i] = 1
            elif op == 2:
                x[i] = 1
                z[i] = 1
        return x + z

    def __eq__(self, other):  # type: ignore[override]
        return isinstance(other, PauliString) and self.ops == other.ops

    def __imul__(self, other):
        res = self * other
        self.ops = res.ops
        self.sign = res.sign
        return self

    def __mul__(self, other):
        if isinstance(other, int):
            out = self.copy()
            out.sign *= -1 if other < 0 else 1
            return out
        if not isinstance(other, PauliString):
            return NotImplemented
        n = max(len(self), len(other))
        out = PauliString(n)
        phase = 1
        combo = {
            (1, 3): (2, 1), (3, 1): (2, -1),
            (1, 2): (3, 1), (2, 1): (3, -1),
            (2, 3): (1, 1), (3, 2): (1, -1),
        }
        for i in range(n):
            a = self.ops[i] if i < len(self.ops) else 0
            b = other.ops[i] if i < len(other.ops) else 0
            if a == 0:
                out.ops[i] = b
            elif b == 0:
                out.ops[i] = a
            elif a == b:
                out.ops[i] = 0
            else:
                op, ph = combo.get((a, b), (0, 1))
                out.ops[i] = op
                phase *= ph
        out.sign = self.sign * other.sign * phase
        return out

    def __repr__(self):
        return "".join(_OPCODE_TO_CHAR.get(op, "I") for op in self.ops)


class Circuit:
    def __init__(self):
        self.operations: List[Tuple[str, List[int]]] = []

    def append(self, name: str, targets: Sequence[int]):
        self.operations.append((name, list(targets)))

    def __iter__(self):
        return iter(self.operations)

    def __len__(self):  # type: ignore[override]
        return len(self.operations)


class Tableau:
    def __init__(self, xs: List[PauliString], zs: List[PauliString]):
        self.xs = xs
        self.zs = zs
        self.n = len(xs)

    @classmethod
    def from_conjugated_generators(cls, *, xs: List[PauliString], zs: List[PauliString]):
        return cls(xs=list(xs), zs=list(zs))

    def _matrix(self) -> List[List[int]]:
        return [p._to_symp(self.n) for p in self.xs + self.zs]

    def x_output(self, q: int) -> PauliString:
        return self.xs[q]

    def z_output(self, q: int) -> PauliString:
        return self.zs[q]

    def __call__(self, p: PauliString) -> PauliString:
        """Conjugate a PauliString by this Clifford (real stim API)."""
        v = p._to_symp(self.n)
        M = self._matrix()
        out = [0] * (2 * self.n)
        for j, val in enumerate(v):
            if val:
                out = [(a ^ b) for a, b in zip(out, M[j])]
        return _vec_to_pauli(out)

    # Alias for backward compatibility
    def conjugate_pauli_string(self, p: PauliString) -> PauliString:
        return self(p)

    def inverse(self) -> "Tableau":
        M = self._matrix()
        Minv = _gf2_inv(M)
        xs = [_vec_to_pauli(Minv[i]) for i in range(self.n)]
        zs = [_vec_to_pauli(Minv[i]) for i in range(self.n, 2 * self.n)]
        return Tableau(xs, zs)

    def to_circuit(self) -> Circuit:
        circ = Circuit()
        for q in range(self.n):
            circ.append("X_OUTPUT", [q])
            circ.append("Z_OUTPUT", [q])
        return circ

    def __len__(self):  # type: ignore[override]
        return self.n


__all__ = ["PauliString", "Tableau", "Circuit"]
