#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.extraction_v2.optimize import optimize_instance
from backend.extraction_v2.trace_json import to_jsonable
from backend.extraction_v2.types import Evolution, OptimizationInstance


def main() -> None:
    inst = OptimizationInstance(
        stabilizers=["Z0 Z1", "X1 X2", "Z2"],
        evolutions=[
            Evolution("e0", "X0", "theta0", 0),
            Evolution("e1", "Z1", "theta1", 1),
            Evolution("e2", "X2", "theta2", 2),
        ],
        measurements=["X0", "Z2"],
    )
    result = optimize_instance(inst, with_trace=True)
    print(json.dumps(to_jsonable(result), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
