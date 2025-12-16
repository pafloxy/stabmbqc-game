"""Stabilizer code canonicalization via Clifford diagonalization.

This module provides functions to:
1. Take a stabilizer group (via generators in sparse Pauli notation)
2. Find destabilizer pairs
3. Extract logical operators
4. Compute a Clifford map that diagonalizes the code into standard form:
   - Stabilizers → single-qubit Z operators
   - Destabilizers → single-qubit X operators

Uses Stim tableaux for Clifford operations and maintains compatibility with
the sparse Pauli notation ("X0 Z3 Y5") used throughout the backend.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from stim_import import stim
import numpy as np

from pauli_handling import (
    canonicalize_sparse_pauli,
    parse_sparse_pauli,
    paulistring_to_sparse,
    stim_to_symplectic,
)


def canonicalize_stabilizer_code(
    stabilizers: List[str],
    num_qubits: int | None = None,
) -> Dict[str, object]:
    """
    Canonicalize a stabilizer code by finding destabilizers, logical operators,
    and a Clifford map that diagonalizes the code into standard form.

    Args:
        stabilizers: List of stabilizer generators in sparse Pauli notation
            (e.g., ["Z0 Z1", "X1 X2", "Z2 Z3"]).
        num_qubits: Optional total qubit count; inferred from stabilizers if omitted.

    Returns:
        Dictionary with keys:
        - "num_qubits": int - Total number of qubits
        - "num_stabilizers": int - Number of independent stabilizers (k)
        - "num_logical": int - Number of logical qubits (n - k)
        - "stabilizers_sparse": List[str] - Original stabilizers (canonicalized)
        - "stabilizers_stim": List[stim.PauliString] - Stabilizers as Stim objects
        - "destabilizers_sparse": List[str] - Destabilizer pairs
        - "destabilizers_stim": List[stim.PauliString] - Destabilizers as Stim
        - "logical_x_sparse": List[str] - Logical X operators (if any)
        - "logical_z_sparse": List[str] - Logical Z operators (if any)
        - "logical_x_stim": List[stim.PauliString] - Logical X as Stim
        - "logical_z_stim": List[stim.PauliString] - Logical Z as Stim
        - "clifford_tableau": stim.Tableau - Clifford that diagonalizes the code
        - "clifford_circuit": stim.Circuit - Circuit representation of Clifford
        - "diagonalized_stabilizers": List[str] - Stabilizers after Clifford (Z0, Z1, ...)
        - "diagonalized_destabilizers": List[str] - Destabilizers after Clifford (X0, X1, ...)

    Notes:
        - The Clifford tableau maps the code into standard form where:
          * Stabilizer i → Z on qubit i
          * Destabilizer i → X on qubit i
          * Logical operators are on qubits k, k+1, ..., n-1
        - Uses Stim's symplectic formalism for robust Clifford operations
        - Phases are tracked but logical equivalence ignores overall phases
    """
    # Infer num_qubits if not provided
    if num_qubits is None:
        max_idx = -1
        for s in stabilizers:
            tokens = s.replace("*", " ").split()
            for tok in tokens:
                tok = tok.strip()
                if tok and tok[0].upper() in "XYZ" and tok[1:].isdigit():
                    max_idx = max(max_idx, int(tok[1:]))
        num_qubits = max_idx + 1 if max_idx >= 0 else 0

    n = num_qubits
    if n == 0:
        raise ValueError("Cannot canonicalize code with 0 qubits")

    # Parse stabilizers
    stab_stim = [parse_sparse_pauli(s, num_qubits=n) for s in stabilizers]
    k = len(stab_stim)
    if k == 0:
        raise ValueError("At least one stabilizer generator required")
    if k > n:
        raise ValueError(f"Cannot have more stabilizers ({k}) than qubits ({n})")

    # Canonicalize input stabilizers
    stab_sparse = [canonicalize_sparse_pauli(s) for s in stabilizers]

    # Find destabilizers and logical operators
    destab_stim, logical_x_stim, logical_z_stim = _find_destabilizers_and_logicals(stab_stim, n)
    
    destab_sparse = [paulistring_to_sparse(d) for d in destab_stim]
    
    # Logical operators are returned directly
    num_logical = n - k
    logical_x_sparse = [paulistring_to_sparse(lx) for lx in logical_x_stim]
    logical_z_sparse = [paulistring_to_sparse(lz) for lz in logical_z_stim]

    # Build diagonalizing Clifford circuit
    diagonalizing_circuit = _build_diagonalizing_circuit(stab_stim, destab_stim, n)
    diagonalizing_tableau = diagonalizing_circuit.to_tableau()

    # Apply the diagonalizing Clifford to verify
    diag_stabs = [paulistring_to_sparse(_conjugate_pauli(s, diagonalizing_tableau)) for s in stab_stim]
    diag_destabs = [paulistring_to_sparse(_conjugate_pauli(d, diagonalizing_tableau)) for d in destab_stim]

    return {
        "num_qubits": n,
        "num_stabilizers": k,
        "num_logical": num_logical,
        "stabilizers_sparse": stab_sparse,
        "stabilizers_stim": stab_stim,
        "destabilizers_sparse": destab_sparse,
        "destabilizers_stim": destab_stim,
        "logical_x_sparse": logical_x_sparse,
        "logical_z_sparse": logical_z_sparse,
        "logical_x_stim": logical_x_stim,
        "logical_z_stim": logical_z_stim,
        "clifford_tableau": diagonalizing_tableau,
        "clifford_circuit": diagonalizing_circuit,
        "diagonalized_stabilizers": diag_stabs,
        "diagonalized_destabilizers": diag_destabs,
    }


def _find_destabilizers_and_logicals(
    stabilizers: List[stim.PauliString],
    num_qubits: int,
) -> Tuple[List[stim.PauliString], List[stim.PauliString], List[stim.PauliString]]:
    """
    Find destabilizers and logical operators for a stabilizer code.
    
    Returns:
        (destabilizers, logical_x_ops, logical_z_ops) where:
        - destabilizers are Paulis that anticommute with their paired stabilizer
        - logical_x_ops and logical_z_ops are logical operators that commute with all stabilizers
    """
    k = len(stabilizers)
    n = num_qubits

    # Build symplectic matrix for stabilizers
    stab_x = []
    stab_z = []
    for s in stabilizers:
        x, z = stim_to_symplectic(s, n)
        stab_x.append(x)
        stab_z.append(z)

    # Find destabilizers via symplectic orthogonalization
    destab_x = []
    destab_z = []

    for i in range(k):
        # Find a Pauli that anticommutes with stab[i] and commutes with all others
        found = False
        # Try single-qubit Paulis first
        for q in range(n):
            for pauli_type in [1, 3]:  # X=1, Z=3
                dx = np.zeros(n, dtype=np.uint8)
                dz = np.zeros(n, dtype=np.uint8)
                if pauli_type == 1:  # X
                    dx[q] = 1
                else:  # Z
                    dz[q] = 1

                # Check commutation: symp(a, b) = a_x · b_z + a_z · b_x (mod 2)
                anticomm_with_i = (np.dot(dx, stab_z[i]) + np.dot(dz, stab_x[i])) % 2 == 1
                commutes_with_others = all(
                    (np.dot(dx, stab_z[j]) + np.dot(dz, stab_x[j])) % 2 == 0
                    for j in range(k)
                    if j != i
                )
                # Also ensure doesn't anticommute with previous destabilizers
                commutes_with_destabs = all(
                    (np.dot(dx, destab_z[j]) + np.dot(dz, destab_x[j])) % 2 == 0
                    for j in range(len(destab_x))
                )
                if anticomm_with_i and commutes_with_others and commutes_with_destabs:
                    destab_x.append(dx)
                    destab_z.append(dz)
                    found = True
                    break
            if found:
                break

        if not found:
            # Try two-qubit Paulis
            for q1 in range(n):
                for q2 in range(q1 + 1, n):
                    for ops in [(1, 0, 3, 0), (1, 0, 0, 3), (3, 0, 1, 0), (3, 0, 0, 1),
                                (0, 1, 0, 3), (0, 3, 0, 1), (1, 0, 1, 0), (3, 0, 3, 0)]:
                        dx = np.zeros(n, dtype=np.uint8)
                        dz = np.zeros(n, dtype=np.uint8)
                        if ops[0] == 1:
                            dx[q1] = 1
                        elif ops[0] == 3:
                            dz[q1] = 1
                        if ops[2] == 1:
                            dx[q2] = 1
                        elif ops[2] == 3:
                            dz[q2] = 1
                        
                        anticomm_with_i = (np.dot(dx, stab_z[i]) + np.dot(dz, stab_x[i])) % 2 == 1
                        commutes_with_others = all(
                            (np.dot(dx, stab_z[j]) + np.dot(dz, stab_x[j])) % 2 == 0
                            for j in range(k)
                            if j != i
                        )
                        commutes_with_destabs = all(
                            (np.dot(dx, destab_z[j]) + np.dot(dz, destab_x[j])) % 2 == 0
                            for j in range(len(destab_x))
                        )
                        if anticomm_with_i and commutes_with_others and commutes_with_destabs:
                            destab_x.append(dx)
                            destab_z.append(dz)
                            found = True
                            break
                    if found:
                        break
                if found:
                    break

        if not found:
            raise ValueError(f"Could not find destabilizer for stabilizer {i}")
    
    # Now find logical operators that commute with all stabilizers
    # and form anticommuting X/Z pairs
    num_logical = n - k
    logical_x_vecs = []
    logical_z_vecs = []
    
    for _ in range(num_logical):
        # Find logical X using binary enumeration of all Pauli operators
        # Try operators in order of increasing weight (number of non-identity terms)
        found_lx = False
        from pauli_handling import gf2_rowspan_decompose
        S_matrix = np.column_stack([
            np.concatenate([stab_x[i], stab_z[i]]) for i in range(k)
        ]).T
        if destab_x:
            D_matrix = np.column_stack([
                np.concatenate([destab_x[i], destab_z[i]]) for i in range(len(destab_x))
            ]).T
            SD_matrix = np.concatenate([S_matrix, D_matrix], axis=0)
        else:
            D_matrix = None
            SD_matrix = S_matrix
        
        # Enumerate Pauli operators by binary representation
        for weight in range(1, n + 1):  # Weight 1 to n
            if found_lx:
                break
            # Try all combinations of weight qubits
            from itertools import combinations, product
            for qubits in combinations(range(n), weight):
                if found_lx:
                    break
                # Try all Pauli types (X, Z, Y) on these qubits
                for paulis in product([1, 3, 2], repeat=weight):  # X=1, Z=3, Y=2
                    lx = np.zeros(n, dtype=np.uint8)
                    lz_x = np.zeros(n, dtype=np.uint8)
                    for q, p in zip(qubits, paulis):
                        if p == 1:  # X
                            lx[q] = 1
                        elif p == 3:  # Z
                            lz_x[q] = 1
                        else:  # Y
                            lx[q] = 1
                            lz_x[q] = 1
                    
                    # Must commute with all stabilizers
                    commutes_with_stabs = all(
                        (np.dot(lx, stab_z[j]) + np.dot(lz_x, stab_x[j])) % 2 == 0
                        for j in range(k)
                    )
                    if not commutes_with_stabs:
                        continue
                    
                    # Must commute with all previous logical Zs
                    commutes_with_prev_lz = all(
                        (np.dot(lx, logical_z_vecs[j][1]) + np.dot(lz_x, logical_z_vecs[j][0])) % 2 == 0
                        for j in range(len(logical_z_vecs))
                    )
                    if not commutes_with_prev_lz:
                        continue

                    # Must commute with all destabilizers (canonical form: only S_i vs D_i anticommute)
                    commutes_with_destabs = all(
                        (np.dot(lx, destab_z[j]) + np.dot(lz_x, destab_x[j])) % 2 == 0
                        for j in range(len(destab_x))
                    )
                    if not commutes_with_destabs:
                        continue
                    
                    # Must not be in stabilizer span
                    p_vec = np.concatenate([lx, lz_x])
                    in_stab_span, _ = gf2_rowspan_decompose(S_matrix, p_vec)
                    in_destab_span = False
                    if D_matrix is not None:
                        in_destab_span, _ = gf2_rowspan_decompose(D_matrix, p_vec)
                    in_combined_span, _ = gf2_rowspan_decompose(SD_matrix, p_vec)
                    if in_stab_span or in_destab_span or in_combined_span:
                        continue

                    logical_x_vecs.append((lx, lz_x))
                    found_lx = True
                    break
        
        if not found_lx:
            # No more independent logical operators
            break
        
        # Find logical Z that anticommutes with this logical X using binary enumeration
        found_lz = False
        lx, lz_x = logical_x_vecs[-1]
        
        for weight in range(1, n + 1):
            if found_lz:
                break
            from itertools import combinations, product
            for qubits in combinations(range(n), weight):
                if found_lz:
                    break
                for paulis in product([1, 3, 2], repeat=weight):
                    lz = np.zeros(n, dtype=np.uint8)
                    lz_z = np.zeros(n, dtype=np.uint8)
                    for q, p in zip(qubits, paulis):
                        if p == 1:
                            lz[q] = 1
                        elif p == 3:
                            lz_z[q] = 1
                        else:
                            lz[q] = 1
                            lz_z[q] = 1
                    
                    # Must commute with all stabilizers
                    commutes_with_stabs = all(
                        (np.dot(lz, stab_z[j]) + np.dot(lz_z, stab_x[j])) % 2 == 0
                        for j in range(k)
                    )
                    if not commutes_with_stabs:
                        continue
                    
                    # Must anticommute with the current logical X
                    anticomm_with_lx = (np.dot(lz, lz_x) + np.dot(lz_z, lx)) % 2 == 1
                    if not anticomm_with_lx:
                        continue
                    
                    # Must commute with previous logical X/Z pairs
                    commutes_with_prev = all(
                        (np.dot(lz, logical_x_vecs[j][1]) + np.dot(lz_z, logical_x_vecs[j][0])) % 2 == 0
                        and (np.dot(lz, logical_z_vecs[j][1]) + np.dot(lz_z, logical_z_vecs[j][0])) % 2 == 0
                        for j in range(len(logical_z_vecs))
                    )
                    if not commutes_with_prev:
                        continue

                    # Must commute with all destabilizers
                    commutes_with_destabs = all(
                        (np.dot(lz, destab_z[j]) + np.dot(lz_z, destab_x[j])) % 2 == 0
                        for j in range(len(destab_x))
                    )
                    if not commutes_with_destabs:
                        continue
                    
                    # Must not be in stabilizer span
                    p_vec = np.concatenate([lz, lz_z])
                    in_stab_span, _ = gf2_rowspan_decompose(S_matrix, p_vec)
                    in_destab_span = False
                    if D_matrix is not None:
                        in_destab_span, _ = gf2_rowspan_decompose(D_matrix, p_vec)
                    in_combined_span, _ = gf2_rowspan_decompose(SD_matrix, p_vec)
                    if in_stab_span or in_destab_span or in_combined_span:
                        continue

                    logical_z_vecs.append((lz, lz_z))
                    found_lz = True
                    break
        
        if not found_lz:
            # Could not complete this logical pair, remove the X
            logical_x_vecs.pop()
            break

    # Convert to PauliStrings
    def from_symp(x, z) -> stim.PauliString:
        p = stim.PauliString(n)
        for i in range(n):
            if x[i] and z[i]:
                p[i] = "Y"
            elif x[i]:
                p[i] = "X"
            elif z[i]:
                p[i] = "Z"
        return p

    destab_stim = [from_symp(destab_x[i], destab_z[i]) for i in range(k)]
    logical_x_stim = [from_symp(lx[0], lx[1]) for lx in logical_x_vecs]
    logical_z_stim = [from_symp(lz[0], lz[1]) for lz in logical_z_vecs]

    # Build full tableau using Stim's from_conjugated_generators
    # We need exactly n generators of each type, where X_i anticommutes with Z_i
    num_found_logical = len(logical_x_stim)
    
    # Pad logical operators if we found fewer than needed
    # For each missing logical qubit, find an anticommuting X/Z pair
    while len(logical_x_stim) < n - k:
        # Find an X operator that commutes with all stabilizers and all existing logical operators
        found_pair = False
        for q in range(n):
            if found_pair:
                break
            for pauli_type_x in [1, 3, 2]:  # X, Z, Y
                if found_pair:
                    break
                lx = np.zeros(n, dtype=np.uint8)
                lz_x = np.zeros(n, dtype=np.uint8)
                if pauli_type_x == 1:
                    lx[q] = 1
                elif pauli_type_x == 3:
                    lz_x[q] = 1
                else:
                    lx[q] = 1
                    lz_x[q] = 1
                
                # Check commutation with stabilizers
                commutes_with_stabs = all(
                    (np.dot(lx, stab_z[j]) + np.dot(lz_x, stab_x[j])) % 2 == 0
                    for j in range(k)
                )
                if not commutes_with_stabs:
                    continue

                # Check commutation with destabilizers
                commutes_with_destabs = all(
                    (np.dot(lx, destab_z[j]) + np.dot(lz_x, destab_x[j])) % 2 == 0
                    for j in range(len(destab_x))
                )
                if not commutes_with_destabs:
                    continue
                
                # Check not in stabilizer span
                from pauli_handling import gf2_rowspan_decompose
                S_matrix = np.column_stack([
                    np.concatenate([stab_x[i], stab_z[i]]) for i in range(k)
                ]).T
                D_matrix = np.column_stack([
                    np.concatenate([destab_x[i], destab_z[i]]) for i in range(len(destab_x))
                ]).T
                SD_matrix = np.concatenate([S_matrix, D_matrix], axis=0)
                p_vec = np.concatenate([lx, lz_x])
                in_stab_span, _ = gf2_rowspan_decompose(S_matrix, p_vec)
                in_destab_span, _ = gf2_rowspan_decompose(D_matrix, p_vec)
                in_combined_span, _ = gf2_rowspan_decompose(SD_matrix, p_vec)
                if in_stab_span or in_destab_span or in_combined_span:
                    continue
                
                # Check commutation with existing logical operators
                commutes_with_logical = all(
                    (np.dot(lx, logical_z_vecs[j][1]) + np.dot(lz_x, logical_z_vecs[j][0])) % 2 == 0
                    for j in range(len(logical_z_vecs))
                )
                if not commutes_with_logical:
                    continue
                
                # Find a Z that anticommutes with this X
                for q2 in range(n):
                    if found_pair:
                        break
                    for pauli_type_z in [1, 3, 2]:
                        lz = np.zeros(n, dtype=np.uint8)
                        lz_z = np.zeros(n, dtype=np.uint8)
                        if pauli_type_z == 1:
                            lz[q2] = 1
                        elif pauli_type_z == 3:
                            lz_z[q2] = 1
                        else:
                            lz[q2] = 1
                            lz_z[q2] = 1
                        
                        # Check commutes with stabilizers
                        commutes_with_stabs_z = all(
                            (np.dot(lz, stab_z[j]) + np.dot(lz_z, stab_x[j])) % 2 == 0
                            for j in range(k)
                        )
                        if not commutes_with_stabs_z:
                            continue

                        commutes_with_destabs_z = all(
                            (np.dot(lz, destab_z[j]) + np.dot(lz_z, destab_x[j])) % 2 == 0
                            for j in range(len(destab_x))
                        )
                        if not commutes_with_destabs_z:
                            continue
                        
                        # Check anticommutes with the X we found
                        anticomm = (np.dot(lz, lz_x) + np.dot(lz_z, lx)) % 2 == 1
                        if not anticomm:
                            continue
                        
                        # Check commutes with existing logical operators
                        commutes_with_logical_z = all(
                            (np.dot(lz, logical_x_vecs[j][1]) + np.dot(lz_z, logical_x_vecs[j][0])) % 2 == 0
                            and (np.dot(lz, logical_z_vecs[j][1]) + np.dot(lz_z, logical_z_vecs[j][0])) % 2 == 0
                            for j in range(len(logical_z_vecs))
                        )
                        if not commutes_with_logical_z:
                            continue
                        
                        # Check not in span
                        p_vec_z = np.concatenate([lz, lz_z])
                        in_stab_span_z, _ = gf2_rowspan_decompose(S_matrix, p_vec_z)
                        in_destab_span_z, _ = gf2_rowspan_decompose(D_matrix, p_vec_z)
                        in_combined_span_z, _ = gf2_rowspan_decompose(SD_matrix, p_vec_z)
                        if in_stab_span_z or in_destab_span_z or in_combined_span_z:
                            continue
                        
                        # Found a valid pair
                        logical_x_vecs.append((lx, lz_x))
                        logical_z_vecs.append((lz, lz_z))
                        logical_x_stim.append(from_symp(lx, lz_x))
                        logical_z_stim.append(from_symp(lz, lz_z))
                        found_pair = True
                        break
        
        if not found_pair:
            # Could not find more logical operators
            break
    
    return destab_stim, logical_x_stim, logical_z_stim


def _build_diagonalizing_circuit(
    stabilizers: List[stim.PauliString],
    destabilizers: List[stim.PauliString],
    num_qubits: int,
) -> stim.Circuit:
    """
    Build a Clifford circuit that maps:
    - stabilizers[i] -> Z on qubit i
    - destabilizers[i] -> X on qubit i

    Uses iterative single/two-qubit gate application.
    """
    circuit = stim.Circuit()
    n = num_qubits
    k = len(stabilizers)

    # Greedy algorithm: for each qubit i < k, find gates to diagonalize
    current_stabs = [s.copy() for s in stabilizers]
    current_destabs = [d.copy() for d in destabilizers]
    
    for i in range(k):
        # Goal: make current_destabs[i] = X_i and current_stabs[i] = Z_i
        
        # Step 1: Find which qubit has X or Y in destab[i]
        target_qubit = None
        for q in range(n):
            op = current_destabs[i][q]
            if op in (1, 2):  # X or Y
                target_qubit = q
                break
        
        if target_qubit is None:
            # destab[i] has only Z or I - need to convert
            # Find first Z
            for q in range(n):
                if current_destabs[i][q] == 3:  # Z
                    target_qubit = q
                    circuit.append("H", [q])
                    for j in range(k):
                        current_stabs[j] = _apply_h(current_stabs[j], q)
                        current_destabs[j] = _apply_h(current_destabs[j], q)
                    break
        
        if target_qubit is not None and target_qubit != i:
            # Swap logical qubits i and target_qubit
            circuit.append("SWAP", [i, target_qubit])
            for j in range(k):
                current_stabs[j] = _apply_swap(current_stabs[j], i, target_qubit)
                current_destabs[j] = _apply_swap(current_destabs[j], i, target_qubit)
        
        # Now destab[i] should have X or Y on qubit i
        # Apply single-qubit Clifford to make it pure X
        if i < n:
            op_i = current_destabs[i][i]
            if op_i == 2:  # Y -> apply S† to get X
                circuit.append("S_DAG", [i])
                for j in range(k):
                    current_stabs[j] = _apply_s_dag(current_stabs[j], i)
                    current_destabs[j] = _apply_s_dag(current_destabs[j], i)
            elif op_i == 3:  # Z -> apply H to get X
                circuit.append("H", [i])
                for j in range(k):
                    current_stabs[j] = _apply_h(current_stabs[j], i)
                    current_destabs[j] = _apply_h(current_destabs[j], i)
            
            # Clear other qubits in destab[i] using CX/CZ gates
            for q in range(n):
                if q == i:
                    continue
                op_q = current_destabs[i][q]
                if op_q == 1:  # X
                    circuit.append("CX", [i, q])
                    for j in range(k):
                        current_stabs[j] = _apply_cx(current_stabs[j], i, q)
                        current_destabs[j] = _apply_cx(current_destabs[j], i, q)
                elif op_q == 3:  # Z
                    circuit.append("CZ", [i, q])
                    for j in range(k):
                        current_stabs[j] = _apply_cz(current_stabs[j], i, q)
                        current_destabs[j] = _apply_cz(current_destabs[j], i, q)
                elif op_q == 2:  # Y
                    # Apply S†, then CX, then S
                    circuit.append("S_DAG", [q])
                    for j in range(k):
                        current_stabs[j] = _apply_s_dag(current_stabs[j], q)
                        current_destabs[j] = _apply_s_dag(current_destabs[j], q)
                    circuit.append("CX", [i, q])
                    for j in range(k):
                        current_stabs[j] = _apply_cx(current_stabs[j], i, q)
                        current_destabs[j] = _apply_cx(current_destabs[j], i, q)
                    circuit.append("S", [q])
                    for j in range(k):
                        current_stabs[j] = _apply_s(current_stabs[j], q)
                        current_destabs[j] = _apply_s(current_destabs[j], q)

    return circuit


def _conjugate_pauli(pauli: stim.PauliString, tableau: stim.Tableau) -> stim.PauliString:
    """Conjugate a Pauli string by a Clifford tableau: C * P * C^†."""
    n = min(len(pauli), len(tableau))
    result = stim.PauliString(len(pauli))
    for q in range(n):
        op = pauli[q]
        if op == 0:  # Identity
            continue
        elif op == 1:  # X
            term = tableau.x_output(q)
            # Extend term if needed
            if len(term) < len(pauli):
                extended = stim.PauliString(len(pauli))
                for i in range(len(term)):
                    extended[i] = term[i]
                term = extended
            result *= term
        elif op == 3:  # Z
            term = tableau.z_output(q)
            if len(term) < len(pauli):
                extended = stim.PauliString(len(pauli))
                for i in range(len(term)):
                    extended[i] = term[i]
                term = extended
            result *= term
        elif op == 2:  # Y
            term_x = tableau.x_output(q)
            term_z = tableau.z_output(q)
            if len(term_x) < len(pauli):
                extended = stim.PauliString(len(pauli))
                for i in range(len(term_x)):
                    extended[i] = term_x[i]
                term_x = extended
            if len(term_z) < len(pauli):
                extended = stim.PauliString(len(pauli))
                for i in range(len(term_z)):
                    extended[i] = term_z[i]
                term_z = extended
            result *= term_x * term_z
    result *= pauli.sign
    return result


def _apply_swap(p: stim.PauliString, i: int, j: int) -> stim.PauliString:
    """Apply SWAP(i, j) to Pauli string p."""
    result = p.copy()
    result[i], result[j] = result[j], result[i]
    return result


def _apply_h(p: stim.PauliString, i: int) -> stim.PauliString:
    """Apply H(i) to Pauli string p: X_i ↔ Z_i."""
    result = p.copy()
    op = result[i]
    if op == 1:  # X -> Z
        result[i] = 3
    elif op == 3:  # Z -> X
        result[i] = 1
    elif op == 2:  # Y -> -Y
        result *= -1
    return result


def _apply_s(p: stim.PauliString, i: int) -> stim.PauliString:
    """Apply S(i) to Pauli string p: X_i -> Y_i, Y_i -> -X_i."""
    result = p.copy()
    op = result[i]
    if op == 1:  # X -> Y
        result[i] = 2
    elif op == 2:  # Y -> -X
        result[i] = 1
        result *= -1
    return result


def _apply_s_dag(p: stim.PauliString, i: int) -> stim.PauliString:
    """Apply S†(i) to Pauli string p: X_i -> -Y_i, Y_i -> X_i."""
    result = p.copy()
    op = result[i]
    if op == 1:  # X -> -Y
        result[i] = 2
        result *= -1
    elif op == 2:  # Y -> X
        result[i] = 1
    return result


def _apply_cx(p: stim.PauliString, ctrl: int, targ: int) -> stim.PauliString:
    """Apply CX(ctrl, targ) to Pauli string p."""
    result = p.copy()
    op_c = result[ctrl]
    op_t = result[targ]
    
    # If ctrl has X or Y, target gains X
    if op_c in (1, 2):
        if op_t == 0:
            result[targ] = 1
        elif op_t == 1:
            result[targ] = 0
        elif op_t == 3:
            result[targ] = 2
        elif op_t == 2:
            result[targ] = 3
    
    # If target has Z or Y, ctrl gains Z
    if op_t in (3, 2):
        if op_c == 0:
            result[ctrl] = 3
        elif op_c == 3:
            result[ctrl] = 0
        elif op_c == 1:
            result[ctrl] = 2
        elif op_c == 2:
            result[ctrl] = 1
    
    return result


def _apply_cz(p: stim.PauliString, i: int, j: int) -> stim.PauliString:
    """Apply CZ(i, j) to Pauli string p."""
    result = p.copy()
    op_i = result[i]
    op_j = result[j]
    
    if op_i in (1, 2):  # i has X or Y
        if op_j == 0:
            result[j] = 3
        elif op_j == 3:
            result[j] = 0
        elif op_j == 1:
            result[j] = 2
        elif op_j == 2:
            result[j] = 1
    
    if op_j in (1, 2):  # j has X or Y
        if op_i == 0:
            result[i] = 3
        elif op_i == 3:
            result[i] = 0
        elif op_i == 1:
            result[i] = 2
        elif op_i == 2:
            result[i] = 1
    
    return result


__all__ = ["canonicalize_stabilizer_code"]
