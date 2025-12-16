# Task

Implement a robust, Stim-based function that **synthesizes one Clifford circuit** (H/S/CX plus optional swaps) consistent with a **partial symplectic frame** given as stabilizer–destabilizer pairs.

Concrete input example (n=5, m=4 pairs):

```python
pairs = [
  ('Z1 X3',           'Z3'),
  ('Z0 Z2 X4',        'X2'),
  ('Y0 Y1 Z3 Z4',     'Z0'),
  ('Z0 X1 X2 Z3 Z4',  'Z0 Z1'),
]
```

Each tuple is assumed to be `(S_i, D_i)` where:

* `S_i` is a stabilizer generator
* `D_i` is its destabilizer partner (anticommutes with `S_i`)

This is exactly the “stabilizer–destabilizer” structure described in `stabilizer_canonicalization.py`: stabilizers map to single-qubit Z’s and destabilizers map to single-qubit X’s in canonical form. fileciteturn2file3L61-L66

---

# Overview of the recommended approach

**Best practice (tableau synthesis + symplectic completion):**

1. Parse `(S_i, D_i)` into `stim.PauliString` with a fixed `num_qubits` using `parse_sparse_pauli`. fileciteturn2file8L22-L48
2. Validate they form a **partial symplectic frame**:

   * `S_i` anticommutes with `D_i` for each i
   * all other cross-pairs commute: `S_i` commutes with `S_j`, `D_j` (j≠i), and `D_i` commutes with `D_j` (i≠j)
3. Construct a `stim.Tableau T` such that:

   * `T Z_{q_i} T† = S_i`
   * `T X_{q_i} T† = D_i`
     for some chosen target qubits `q_i` (default `q_i=i`)
4. **Complete** the mapping for the remaining qubits to a full symplectic basis.
5. Build `T` using Stim’s “from conjugated generators” constructor (same technique already used in `stabilizer_canonicalization.py`). fileciteturn2file5L17-L18
6. If you want the Clifford `C` that maps your pairs to standard form (`C S_i C† = Z_{q_i}` and `C D_i C† = X_{q_i}`), then return `C = T.inverse()`.
7. Convert `C` to a circuit via `C.to_circuit()`.

This approach avoids fragile “gate guessing” and uses Stim for what it is best at: tableau Clifford synthesis.

---

# API specification

Implement a function (new file or in `stabilizer_canonicalization.py`):

```python
def synthesize_clifford_from_sd_pairs(
    pairs: list[tuple[str, str]],
    *,
    num_qubits: int,
    target_qubits: list[int] | None = None,
    direction: str = "pairs_to_standard",  # or "standard_to_pairs"
) -> dict:
    """Return a Clifford (tableau + circuit) consistent with the given (S_i, D_i) constraints."""
```

Return dict:

```python
{
  "tableau": stim.Tableau,
  "circuit": stim.Circuit,
  "target_qubits": list[int],
  "diagnostics": {...},
}
```

---

# Step 1 — Parsing and validation

Use the repo’s canonical sparse Pauli helpers:

* `parse_sparse_pauli` for robust parsing fileciteturn2file8L22-L48
* `stim_to_symplectic` / `gf2_rowspan_decompose` for symplectic checks or span operations (already present and opcode-correct) fileciteturn2file11L1-L68

### Parsing

```python
from pauli_handling import parse_sparse_pauli

S = [parse_sparse_pauli(s, num_qubits=num_qubits) for s, _ in pairs]
D = [parse_sparse_pauli(d, num_qubits=num_qubits) for _, d in pairs]
```

### Validation

```python
def validate_partial_frame(S, D):
    m = len(S)
    for i in range(m):
        if S[i].commutes(D[i]):
            raise ValueError(f"pair {i} invalid: S_i must anticommute with D_i")
    for i in range(m):
        for j in range(m):
            if i == j:
                continue
            if not S[i].commutes(S[j]):
                raise ValueError(f"frame invalid: S[{i}] must commute with S[{j}]")
            if not D[i].commutes(D[j]):
                raise ValueError(f"frame invalid: D[{i}] must commute with D[{j}]")
            if not S[i].commutes(D[j]):
                raise ValueError(f"frame invalid: S[{i}] must commute with D[{j}] for i!=j")
```

**Design rule:** treat failure as a *hard error*. Do not attempt to “fix” an invalid frame; it is almost always a user bug.

---

# Step 2 — Build a partial mapping for conjugated generators

We want to construct a tableau `T` such that:

* `T.z_output(q_i) == S_i`
* `T.x_output(q_i) == D_i`

Note: extracting `x_output` / `z_output` from a tableau is already used in `clifford_handling._tableau_to_maps`. fileciteturn2file7L11-L20

### Choose target qubits

Default: `q_i=i`.

```python
m = len(pairs)
if target_qubits is None:
    target_qubits = list(range(m))
if len(target_qubits) != m:
    raise ValueError("target_qubits length must match number of pairs")
if len(set(target_qubits)) != m:
    raise ValueError("target_qubits must be distinct")
```

### Prepare full arrays of images

Create arrays of length `num_qubits`:

```python
X_img = [None] * num_qubits
Z_img = [None] * num_qubits

for i, q in enumerate(target_qubits):
    Z_img[q] = S[i]
    X_img[q] = D[i]
```

At this point we have a **partial** definition of a Clifford. We must complete it.

---

# Step 3 — Complete to a full symplectic frame (robust method)

## Why completion is necessary

A Clifford on `n` qubits is determined by images of `{X_0..X_{n-1}, Z_0..Z_{n-1}}` under conjugation.

You only specified `m` pairs, so there are `n-m` pairs still free; we must choose a completion consistent with the symplectic commutation relations.

## Required commutation constraints

For all i,j:

* `X_i` commutes with `X_j` (i≠j)
* `Z_i` commutes with `Z_j` (i≠j)
* `X_i` commutes with `Z_j` (i≠j)
* `X_i` anticommutes with `Z_i`

In symplectic form, this is the standard symplectic basis constraint.

## Implementation option A (recommended): Linear-algebra completion over GF(2)

Use symplectic vectors and solve for new vectors satisfying linear constraints.

### Utilities to reuse

You already have a correct `stim_to_symplectic` and `gf2_rowspan_decompose` in `pauli_handling.py`. fileciteturn2file11L1-L68

Add two new helpers:

1. `symplectic_inner(v,w)`
2. `gf2_solve(A, b)` (Gaussian elimination over GF(2))

#### Symplectic inner

```python
import numpy as np
from pauli_handling import stim_to_symplectic

def symplectic_inner(v: np.ndarray, w: np.ndarray, n: int) -> int:
    vx, vz = v[:n], v[n:]
    wx, wz = w[:n], w[n:]
    return int((vx @ wz + vz @ wx) & 1)
```

#### GF(2) solver (row-reduction)

```python
def gf2_solve(A: np.ndarray, b: np.ndarray) -> np.ndarray | None:
    """Solve A x = b over GF(2). Return one solution or None if infeasible."""
    A = A.copy().astype(np.uint8)
    b = b.copy().astype(np.uint8)
    m, n = A.shape
    aug = np.concatenate([A, b.reshape(m, 1)], axis=1)

    row = 0
    pivots = [-1] * n
    for col in range(n):
        # find pivot
        pr = None
        for r in range(row, m):
            if aug[r, col]:
                pr = r
                break
        if pr is None:
            continue
        if pr != row:
            aug[[row, pr]] = aug[[pr, row]]
        pivots[col] = row
        # eliminate other rows
        for r in range(m):
            if r != row and aug[r, col]:
                aug[r] ^= aug[row]
        row += 1
        if row == m:
            break

    # check inconsistency
    for r in range(m):
        if aug[r, :-1].sum() == 0 and aug[r, -1] == 1:
            return None

    # set free vars to 0
    x = np.zeros(n, dtype=np.uint8)
    for col in range(n):
        r = pivots[col]
        if r != -1:
            x[col] = aug[r, -1]
    return x
```

### Completion logic

Represent each assigned image as `v = [x|z] ∈ GF(2)^{2n}`. For each missing qubit index `q`:

* choose a candidate `x_q` that is symplectically orthogonal to all existing `X_img` and `Z_img` (except its eventual partner)
* solve for `z_q` such that:

  * symplectic_inner(x_q, z_q)=1
  * z_q orthogonal to all previously assigned images

This becomes a linear system in the unknown `z_q` vector.

**Practical suggestion:** For n up to ~20, you can pick `x_q` by trying weight-1/2 Paulis, then solve for `z_q`.

---

## Implementation option B (simpler): low-weight enumeration completion

This is what `stabilizer_canonicalization.py` already does when padding missing logical operators: it searches simple Paulis, checks commutation constraints, and checks membership in spans using `gf2_rowspan_decompose`. fileciteturn2file5L23-L71

Refactor that search into a reusable `find_completion_pair(...)`.

### Candidate generator enumeration

```python
def enumerate_low_weight_paulis(n: int, max_w: int = 3):
    # yield stim.PauliString with weight <= max_w
    # implement: weight-1 then weight-2 then weight-3; try X,Z,Y on each position
    ...
```

### Completion check

Use symplectic commutation tests based on `stim_to_symplectic` (opcode-correct) fileciteturn2file11L1-L16.

---

# Step 4 — Construct the tableau using Stim

Once `X_img[q]` and `Z_img[q]` are fully populated for all qubits, build the tableau using Stim’s constructor.

This pattern is already used in `stabilizer_canonicalization.py`: “Build full tableau using Stim’s from_conjugated_generators”. fileciteturn2file5L17-L18

### Implementation note: constructor name may vary by Stim version

Do this defensively:

```python
ctor = None
if hasattr(stim.Tableau, "from_conjugated_generators"):
    ctor = stim.Tableau.from_conjugated_generators
elif hasattr(stim.Tableau, "from_conjugated_generators"):
    ctor = stim.Tableau.from_conjugated_generators
else:
    raise RuntimeError("Stim Tableau constructor for conjugated generators not found; check Stim version")

T = ctor(xs=X_img, zs=Z_img)
```

(Adjust keyword names if needed; introspect with `help(stim.Tableau.from_conjugated_generators)`.)

### Direction handling

* If `direction == "standard_to_pairs"`, return `T`.
* If `direction == "pairs_to_standard"`, return `T.inverse()`.

---

# Step 5 — Convert to a circuit

```python
C = T.inverse()  # if pairs_to_standard
circ = C.to_circuit()
```

Stim may emit `H`, `S`, `CX`, and sometimes `SWAP`/`CZ` depending on version.

If you **must** restrict to `{H, S, CX}` only, postprocess:

* `CZ a b  ==  H b; CX a b; H b`
* `SWAP a b == CX a b; CX b a; CX a b`

---

# Step 6 — Verification harness (must include in tests)

Verification should not rely on string matching; use Stim conjugation directly:

```python
from pauli_handling import parse_sparse_pauli

C_tab = C  # stim.Tableau

for i, q in enumerate(target_qubits):
    S_i = parse_sparse_pauli(pairs[i][0], num_qubits=num_qubits)
    D_i = parse_sparse_pauli(pairs[i][1], num_qubits=num_qubits)

    out_S = C_tab.conjugate_pauli_string(S_i)
    out_D = C_tab.conjugate_pauli_string(D_i)

    want_S = stim.PauliString(num_qubits)
    want_S[q] = 'Z'
    want_D = stim.PauliString(num_qubits)
    want_D[q] = 'X'

    assert out_S == want_S, (i, out_S, want_S)
    assert out_D == want_D, (i, out_D, want_D)
```

Add this as a regression test for the given example pairs.

---

# Concrete example: given pairs list (n=5)

### Input

```python
pairs = [
  ('Z1 X3',           'Z3'),
  ('Z0 Z2 X4',        'X2'),
  ('Y0 Y1 Z3 Z4',     'Z0'),
  ('Z0 X1 X2 Z3 Z4',  'Z0 Z1'),
]
num_qubits = 5
```

### Expected behavior

Running `synthesize_clifford_from_sd_pairs(pairs, num_qubits=5)` should return a Clifford circuit `C` such that:

* `C (Z1 X3) C† = Z0` (if mapping pair 0 to qubit 0)
* `C (Z3) C† = X0`
* `C (Z0 Z2 X4) C† = Z1`
* `C (X2) C† = X1`
* etc.

(The mapping of which pair goes to which qubit is `target_qubits`; default is `[0,1,2,3]`.)

---

# Hardening / design rules to prevent future bugs

1. **Always pass `num_qubits` explicitly**; do not infer from strings. Inference caused repeated length mismatches elsewhere.
2. Use **opcode-aware** conversion only. You already have this in `stim_to_symplectic`. fileciteturn2file11L1-L16
3. Centralize Pauli conversions:

   * `parse_sparse_pauli` fileciteturn2file8L22-L48
   * `paulistring_to_sparse` (already used in `stabilizer_canonicalization.py`) fileciteturn2file3L22-L27
4. Add tests for:

   * valid frame passes
   * invalid frame fails
   * synthesis satisfies conjugation constraints on the specified pairs
5. Keep the completion strategy **pluggable**:

   * `completion="algebra" | "search"`
     so you can upgrade from low-weight search to GF(2) completion later without touching the tableau logic.

---

# Implementation sketch (put this in code)

```python
import stim
import numpy as np
from pauli_handling import parse_sparse_pauli


def synthesize_clifford_from_sd_pairs(pairs, *, num_qubits, target_qubits=None, direction="pairs_to_standard"):
    # 1) parse
    S = [parse_sparse_pauli(s, num_qubits=num_qubits) for s, _ in pairs]
    D = [parse_sparse_pauli(d, num_qubits=num_qubits) for _, d in pairs]

    # 2) validate
    validate_partial_frame(S, D)

    # 3) choose targets
    m = len(pairs)
    if target_qubits is None:
        target_qubits = list(range(m))

    # 4) partial images
    X_img = [None] * num_qubits
    Z_img = [None] * num_qubits
    for i, q in enumerate(target_qubits):
        Z_img[q] = S[i]
        X_img[q] = D[i]

    # 5) complete remaining qubits
    complete_symplectic_frame_inplace(X_img, Z_img, num_qubits)

    # 6) build tableau
    T = stim.Tableau.from_conjugated_generators(xs=X_img, zs=Z_img)

    # 7) direction
    C = T.inverse() if direction == "pairs_to_standard" else T
    circ = C.to_circuit()

    return {"tableau": C, "circuit": circ, "target_qubits": target_qubits}
```

You must implement:

* `validate_partial_frame`
* `complete_symplectic_frame_inplace` (Option A or B)

---

# Notes about existing modules you can reuse

* `stabilizer_canonicalization.py` already contains logic for:

  * symplectic conversions and span tests fileciteturn2file3L22-L27
  * padding missing logical operator pairs (candidate search + commutation + span checks) fileciteturn2file5L23-L71
  * building a full tableau from conjugated generators fileciteturn2file5L17-L18

Refactor those parts rather than re-inventing them.

---

# Deliverables for the agent

1. New function `synthesize_clifford_from_sd_pairs` with unit tests.
2. Extract/implement `complete_symplectic_frame_inplace` (start with low-weight search; add algebraic completion later).
3. Add a regression test using the provided `pairs` list (n=5) and verify conjugation constraints.
4. Ensure output circuit is stable and printable; optionally add a gate-set normalization pass.
