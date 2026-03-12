from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Pauli:
    x: tuple[int, ...]
    z: tuple[int, ...]


def parse_pauli(spec: str, n_qubits: int | None = None) -> Pauli:
    tokens = spec.replace("*", " ").split()
    items: dict[int, str] = {}
    for tok in tokens:
        op = tok[0].upper()
        idx = int(tok[1:])
        if idx in items and items[idx] != op:
            raise ValueError(f"Conflicting Pauli on qubit {idx}")
        items[idx] = op
    inferred = max(items.keys(), default=-1) + 1
    nq = max(n_qubits or 0, inferred)
    x = [0] * nq
    z = [0] * nq
    for i, op in items.items():
        if op in ("X", "Y"):
            x[i] = 1
        if op in ("Z", "Y"):
            z[i] = 1
    return Pauli(tuple(x), tuple(z))


def pauli_to_sparse(p: Pauli) -> str:
    out = []
    for i, (x, z) in enumerate(zip(p.x, p.z)):
        if x == 0 and z == 0:
            continue
        op = "Y" if x and z else ("X" if x else "Z")
        out.append(f"{op}{i}")
    return " ".join(out)


def xor_pauli(a: Pauli, b: Pauli) -> Pauli:
    return Pauli(tuple((i ^ j) for i, j in zip(a.x, b.x)), tuple((i ^ j) for i, j in zip(a.z, b.z)))


def commute(a: Pauli, b: Pauli) -> bool:
    s = 0
    for ax, az, bx, bz in zip(a.x, a.z, b.x, b.z):
        s ^= (ax & bz) ^ (az & bx)
    return s == 0


def support_overlap(a: str, b: str) -> bool:
    pa = parse_pauli(a)
    pb = parse_pauli(b, len(pa.x))
    for ax, az, bx, bz in zip(pa.x, pa.z, pb.x, pb.z):
        if (ax or az) and (bx or bz):
            return True
    return False


def pauli_comm_vector(rows: list[str], target: str) -> list[int]:
    t = parse_pauli(target)
    return [0 if commute(parse_pauli(r, len(t.x)), t) else 1 for r in rows]


def combine_stabilizers(stabilizers: list[str], selector: list[int]) -> str:
    if len(stabilizers) != len(selector):
        raise ValueError("selector/stabilizers length mismatch")
    nq = max((int(tok[1:]) for s in stabilizers for tok in s.split()), default=-1) + 1
    acc = Pauli(tuple([0] * nq), tuple([0] * nq))
    for use, stab in zip(selector, stabilizers):
        if use:
            acc = xor_pauli(acc, parse_pauli(stab, nq))
    return pauli_to_sparse(acc)
