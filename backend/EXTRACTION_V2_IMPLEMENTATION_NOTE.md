# Extraction V2 implementation note (paper-aligned rebuild)

## Scope and scouting outcome
I first scouted this repository for the requested legacy modules:
- `extraction/`
- `pattern_viewer/server.py`
- `pattern_viewer_dynamic/server.py`
- `pattern_viewer_interactive_rewrite/server.py`

These directories/files are **not present** in this repo snapshot, so they could not be reused directly.

## What is reusable as-is
- `backend/pauli_handling.py`: token parsing ideas (`X3 Z1` sparse format) are useful as a format reference.
- Existing pytest layout under `backend/tests/` is reusable for new v2 tests.

## What is only partially reusable / semantically non-authoritative
- `backend/qcmain*.py` and game-specific modules are centered on random game generation and stabilizer demos, not on the paper's fixed-point extraction algorithm over `(S, P, M)`.
- `backend/stabilizer_canonicalization.py` provides symplectic manipulation ideas, but not the required PdDAG-centered extraction semantics.

## What was intentionally not reused for semantics
- Any game loop/frontier or ad-hoc mutation logic in existing backend files was not used to define optimizer semantics.
- The v2 code treats the current PdDAG as canonical state and recomputes graph-derived precedence after each static pass, following the paper-level requirements from the task description.

## New architecture
Implemented new backend package: `backend/extraction_v2/`
- `types.py`: domain dataclasses and trace containers.
- `pauli_utils.py`: parse/commutation/composition helpers.
- `canonicalize.py`: explicit canonicalized `(S,M)` partition with common generators.
- `pddag.py`: build PdDAG from strict input sequence.
- `reachability.py`: Pred/Succ/PrecEq helpers.
- `distance.py`: `d_M` and layer computation.
- `gf2.py`: affine GF(2) solve with rank/pivots/free vars/nullspace and deterministic representative.
- `selector_system.py`: exact stacked selector systems (`A1/A2/A3`, `B1/B2/B3`) per unresolved node.
- `static_pass.py`: batch rewrite against fixed round solution set.
- `optimize.py`: fixed-point loop (solve-all → static-pass → rebuild).
- `trace.py` + `trace_json.py`: rich inspectability snapshots and JSON serialization support.
- `reconstruction.py`: final sequence reconstruction metadata helper.

## Known deltas versus unavailable legacy viewer code
Because the viewer directories were unavailable in this repository, parser/state-prep/visualization hooks from them could not be directly harvested. A clean adapter layer can be added later once those modules are available.
