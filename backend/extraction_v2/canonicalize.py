from __future__ import annotations

from .types import CanonicalizationResult


def canonicalize_generators(stabilizers: list[str], measurements: list[str]) -> CanonicalizationResult:
    s = sorted(set(stabilizers))
    m = sorted(set(measurements))
    common = sorted(set(s).intersection(m))
    return CanonicalizationResult(
        stabilizers=s,
        measurements=m,
        common_generators=common,
        stabilizer_only=sorted(set(s) - set(common)),
        measurement_only=sorted(set(m) - set(common)),
    )
