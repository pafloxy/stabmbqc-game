# backend/ – Quantum Engine for the StabMBQC Game

This package contains the Python side of the project: all the quantum logic,
Stim/Qiskit integration, and level/round generation.

## Main modules

- `qc-main0.py` – **the main physics module**.
  - Put your stabilizer code, Stim circuits/tableaux, Pauli-rotation logic, and
    extractability checks here.
- `model.py` – dataclasses representing candidates, rounds, and levels.
- `rendering.py` – helpers to render circuit/graph images (to be implemented).
- `rounds.py` – high-level glue: turns physics results into `RoundSpec` objects
  and calls the rendering helpers.
- `cli_generate.py` – a small CLI tool to generate level JSON + assets.

## Example: generating one round (Python only)

You can work purely in Python while prototyping the physics.
For example, from a Python shell:

```python
from pathlib import Path
from backend.rounds import build_round

assets_dir = Path("docs/assets")
round_spec = build_round(level=1, round_index=0, assets_dir=assets_dir)

print("Num qubits:", round_spec.num_qubits)
print("Stabilizers:", round_spec.stabilizers)
for c in round_spec.candidates:
    print("Candidate:", c.label, "(pauli =", c.pauli + ")")
```

## Example: generating a full level JSON

Use the CLI helper from the repo root:

```bash
python -m backend.cli_generate \
  --level 1 \
  --num-rounds 5 \
  --out-json docs/levels/level-1.json \
  --assets-dir docs/assets
```

This will:

1. Call `build_round` `num-rounds` times.
2. Create a `LevelSpec` bundling all rounds and some dummy intro slides.
3. Write the JSON file expected by `docs/main.js`.

Once you plug in your actual Stim/Qiskit logic into `qc-main0.py` and
`rendering.py`, the front-end will instantly reflect the richer physics.
