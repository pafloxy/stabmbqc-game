"""Core quantum logic helpers for the StabMBQC game.

This module provides lightweight Stim-based utilities for:
- Pauli string parsing and formatting
- Commutation and anti-commutation checks
- CZ conjugation of Pauli operators
- Safe measurement predicates

For more advanced functionality (system initialization, visualization, etc.),
see qcmain1.py.
"""

from __future__ import annotations

from typing import List, Tuple, Optional
import stim


# ==========================
# Pauli String Parsing
# ==========================

def pauli(s: str, n_qubits: Optional[int] = None) -> stim.PauliString:
    """
    Parse a Pauli string from various formats.
    
    Accepted formats:
    - "XZIY" (compact)
    - "X Z I Y" (spaced)
    - "X_0 Z_1 Y_3" (subscript notation)
    - "X0*Z1*Y3" (product notation)
    
    Args:
        s: The Pauli string to parse
        n_qubits: Number of qubits (auto-detected if None)
    
    Returns:
        stim.PauliString object
    """
    # Clean up the string
    s = s.strip().upper()
    
    # Handle empty string
    if not s:
        return stim.PauliString(n_qubits or 1)
    
    # Remove common separators
    s = s.replace("*", " ").replace("_", "")
    
    # Check if it's already compact (no spaces, no digits after letters)
    if " " not in s and not any(c.isdigit() for c in s):
        # Compact format: "XZIY"
        n = len(s)
        if n_qubits and n_qubits != n:
            # Pad with identities
            s = s + "I" * (n_qubits - n)
        result = stim.PauliString(len(s))
        for i, ch in enumerate(s):
            if ch in ['X', 'Y', 'Z']:
                result[i] = ch
        return result
    
    # Spaced format: "X Z I Y" or "X I I" 
    parts = s.split()
    
    # Check if parts have indices (like "X0", "Z1")
    has_indices = any(any(c.isdigit() for c in p) for p in parts)
    
    if has_indices:
        # Parse "X0 Z1 Y3" format
        max_idx = 0
        ops = {}
        for part in parts:
            if not part:
                continue
            # Extract operator and index
            op = ""
            idx_str = ""
            for ch in part:
                if ch in ['X', 'Y', 'Z', 'I']:
                    op = ch
                elif ch.isdigit():
                    idx_str += ch
            if op and idx_str:
                idx = int(idx_str)
                ops[idx] = op
                max_idx = max(max_idx, idx)
        
        n = n_qubits or (max_idx + 1)
        result = stim.PauliString(n)
        for idx, op in ops.items():
            if op in ['X', 'Y', 'Z'] and idx < n:
                result[idx] = op
        return result
    else:
        # Simple spaced format: "X Z I Y"
        n = len(parts)
        if n_qubits and n_qubits != n:
            parts = parts + ["I"] * (n_qubits - n)
        result = stim.PauliString(len(parts))
        for i, ch in enumerate(parts):
            ch = ch.strip()
            if ch in ['X', 'Y', 'Z']:
                result[i] = ch
        return result


def pauli_to_str(p: stim.PauliString, compact: bool = True) -> str:
    """
    Convert a Stim PauliString to a readable string.
    
    Args:
        p: The PauliString to convert
        compact: If True, use compact format "XZIY"; otherwise "X Z I Y"
    
    Returns:
        String representation
    """
    s = str(p)
    # Remove sign prefix if present
    if s and s[0] in "+-":
        s = s[1:]
    
    # Replace underscores with I
    s = s.replace("_", "I")
    
    if compact:
        return s
    else:
        return " ".join(s)


def pretty_pauli(p: stim.PauliString, show_identities: bool = False) -> str:
    """
    Pretty-print a PauliString with subscript notation.
    
    Example: "X_0 Z_2" for a Pauli with X on qubit 0 and Z on qubit 2.
    """
    s = str(p)
    if s and s[0] in "+-":
        sign, s = s[0], s[1:]
    else:
        sign = ""
    
    parts = []
    for i, ch in enumerate(s):
        if ch in ["_", "I"]:
            if show_identities:
                parts.append(f"I_{i}")
        else:
            parts.append(f"{ch}_{i}")
    
    body = " ".join(parts) if parts else ("I_0" if show_identities else "I")
    return (sign + " " + body).strip() if sign else body


# ==========================
# Commutation Checks
# ==========================

def commutes(p: stim.PauliString, q: stim.PauliString) -> bool:
    """Check if two Pauli operators commute."""
    return p.commutes(q)


def anticommutes(p: stim.PauliString, q: stim.PauliString) -> bool:
    """Check if two Pauli operators anti-commute."""
    return not p.commutes(q)


def count_anticommuting(p: stim.PauliString, generators: List[stim.PauliString]) -> int:
    """Count how many generators anti-commute with the given Pauli."""
    return sum(1 for g in generators if anticommutes(p, g))


# ==========================
# CZ Conjugation
# ==========================

def conjugate_by_cz(p: stim.PauliString, a: int, b: int) -> stim.PauliString:
    """
    Conjugate a Pauli operator by CZ(a, b).
    
    CZ conjugation rules:
    - X_a -> X_a Z_b
    - X_b -> Z_a X_b  
    - Z_a -> Z_a (unchanged)
    - Z_b -> Z_b (unchanged)
    - Y_a -> Y_a Z_b
    - Y_b -> Z_a Y_b
    
    Args:
        p: The Pauli operator to conjugate
        a: First qubit of CZ gate
        b: Second qubit of CZ gate
    
    Returns:
        The conjugated Pauli operator
    """
    n = len(p)
    result = stim.PauliString(p)  # Copy
    
    s = str(p)
    if s and s[0] in "+-":
        s = s[1:]
    
    # Apply CZ conjugation rules
    if a < len(s) and s[a] in ['X', 'Y']:
        # Multiply by Z_b
        z_op = stim.PauliString(n)
        z_op[b] = 'Z'
        result = result * z_op
    
    if b < len(s) and s[b] in ['X', 'Y']:
        # Multiply by Z_a
        z_op = stim.PauliString(n)
        z_op[a] = 'Z'
        result = result * z_op
    
    return result


def conjugate_by_cz_circuit(p: stim.PauliString, cz_edges: List[Tuple[int, int]]) -> stim.PauliString:
    """
    Conjugate a Pauli operator by a sequence of CZ gates.
    
    Args:
        p: The Pauli operator to conjugate
        cz_edges: List of (qubit_a, qubit_b) pairs for CZ gates
    
    Returns:
        The conjugated Pauli operator
    """
    result = stim.PauliString(p)
    for a, b in cz_edges:
        result = conjugate_by_cz(result, a, b)
    return result


def update_generators_under_cz(
    generators: List[stim.PauliString],
    cz_edges: List[Tuple[int, int]]
) -> List[stim.PauliString]:
    """
    Update a set of stabilizer generators after applying CZ gates.
    
    Args:
        generators: List of stabilizer generators
        cz_edges: List of (qubit_a, qubit_b) pairs for CZ gates
    
    Returns:
        Updated list of stabilizer generators
    """
    return [conjugate_by_cz_circuit(g, cz_edges) for g in generators]


# ==========================
# Safe Measurement Predicate
# ==========================

def is_safe_measurement(
    measurement: stim.PauliString,
    stabilizer_generators: List[stim.PauliString]
) -> bool:
    """
    Check if a measurement is "safe" (non-destructive).
    
    A measurement is safe if it anti-commutes with exactly one
    stabilizer generator (kills only that generator, not the logical info).
    
    Args:
        measurement: The Pauli measurement operator
        stabilizer_generators: List of stabilizer generators
    
    Returns:
        True if the measurement is safe
    """
    anti_count = count_anticommuting(measurement, stabilizer_generators)
    return anti_count == 1


def is_logical_measurement(
    measurement: stim.PauliString,
    stabilizer_generators: List[stim.PauliString]
) -> bool:
    """
    Check if a measurement is "logical" (destructive).
    
    A measurement is logical if it commutes with all stabilizer generators
    but is not in the stabilizer group itself.
    
    Note: This is a simplified check that only verifies commutation.
    For a full check, you would need to verify it's not in the stabilizer group.
    
    Args:
        measurement: The Pauli measurement operator
        stabilizer_generators: List of stabilizer generators
    
    Returns:
        True if the measurement commutes with all generators
    """
    return count_anticommuting(measurement, stabilizer_generators) == 0


def classify_measurement(
    measurement: stim.PauliString,
    stabilizer_generators: List[stim.PauliString]
) -> str:
    """
    Classify a measurement as 'safe', 'logical', or 'destructive'.
    
    - safe: anti-commutes with exactly 1 generator
    - logical: commutes with all generators (dangerous!)
    - destructive: anti-commutes with 2+ generators
    
    Returns:
        Classification string
    """
    anti_count = count_anticommuting(measurement, stabilizer_generators)
    
    if anti_count == 0:
        return "logical"
    elif anti_count == 1:
        return "safe"
    else:
        return "destructive"


# ==========================
# Convenience Functions
# ==========================

def make_stabilizers(stab_strs: List[str], n_qubits: Optional[int] = None) -> List[stim.PauliString]:
    """
    Create a list of stabilizer generators from string representations.
    
    Args:
        stab_strs: List of Pauli strings (e.g., ["ZZI", "IZZ"])
        n_qubits: Number of qubits (auto-detected if None)
    
    Returns:
        List of stim.PauliString objects
    """
    return [pauli(s, n_qubits) for s in stab_strs]


def find_safe_measurements(
    candidates: List[stim.PauliString],
    stabilizer_generators: List[stim.PauliString]
) -> List[stim.PauliString]:
    """
    Filter candidates to find only safe measurements.
    
    Args:
        candidates: List of candidate measurement operators
        stabilizer_generators: List of stabilizer generators
    
    Returns:
        List of safe measurement operators
    """
    return [m for m in candidates if is_safe_measurement(m, stabilizer_generators)]


# ==========================
# Demo / Testing
# ==========================

if __name__ == "__main__":
    print("=== qcmain0.py Demo ===\n")
    
    # Example: 3-qubit code with stabilizers ZZI and IZZ
    stabs = make_stabilizers(["ZZI", "IZZ"])
    print("Stabilizers:")
    for i, s in enumerate(stabs):
        print(f"  S{i+1} = {pauli_to_str(s)}")
    
    print("\nTesting measurements:")
    test_cases = ["XII", "IXI", "IIX", "XXX", "ZZZ", "ZII"]
    
    for m_str in test_cases:
        m = pauli(m_str)
        classification = classify_measurement(m, stabs)
        anti_count = count_anticommuting(m, stabs)
        print(f"  {m_str}: {classification} (anti-commutes with {anti_count} generators)")
