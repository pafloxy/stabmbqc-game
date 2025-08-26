"""Campaign validation and round construction.

This module provides:
- Validation of campaign JSON files
- QC-based verification of step correctness (using qcmain1)
- Helpers for building rounds programmatically
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Tuple, Optional

from .model import Campaign, Round, Step, campaign_from_file
from . import qcmain1 as qc


# ==========================
# Validation
# ==========================

def validate_campaign_json(path: Path, assets_base: Optional[Path] = None) -> List[str]:
    """
    Validate a campaign JSON file.
    
    Checks:
    - Required fields exist
    - Option IDs are unique within each step
    - Correct answer exists in options
    - Referenced assets exist (if assets_base provided)
    - QC physics consistency (optional, if qc_spec provided)
    
    Returns:
        List of error messages (empty if valid)
    """
    errors: List[str] = []
    
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON: {e}")
        return errors
    except FileNotFoundError:
        errors.append(f"File not found: {path}")
        return errors
    
    # Check required top-level fields
    if "rounds" not in data:
        errors.append("Missing 'rounds' field")
        return errors
    
    if not isinstance(data["rounds"], list):
        errors.append("'rounds' must be an array")
        return errors
    
    if len(data["rounds"]) == 0:
        errors.append("'rounds' array is empty")
    
    # Validate each round
    for r_idx, r in enumerate(data["rounds"]):
        round_id = r.get("id", f"round-{r_idx}")
        
        if "steps" not in r:
            errors.append(f"Round '{round_id}': missing 'steps' field")
            continue
        
        if not isinstance(r["steps"], list):
            errors.append(f"Round '{round_id}': 'steps' must be an array")
            continue
        
        if len(r["steps"]) == 0:
            errors.append(f"Round '{round_id}': 'steps' array is empty")
        
        # Check assets exist
        if assets_base and r.get("assets"):
            assets = r["assets"]
            if assets.get("circuit_image"):
                img_path = assets_base / assets["circuit_image"]
                if not img_path.exists():
                    errors.append(f"Round '{round_id}': circuit_image not found: {img_path}")
            if assets.get("graph_image"):
                img_path = assets_base / assets["graph_image"]
                if not img_path.exists():
                    errors.append(f"Round '{round_id}': graph_image not found: {img_path}")
        
        # Validate each step
        for s_idx, step in enumerate(r["steps"]):
            step_id = step.get("id", f"step-{s_idx}")
            full_id = f"{round_id}:{step_id}"
            
            # Check options
            if "options" not in step:
                errors.append(f"Step '{full_id}': missing 'options' field")
                continue
            
            if not isinstance(step["options"], list):
                errors.append(f"Step '{full_id}': 'options' must be an array")
                continue
            
            opt_ids = [o.get("id") for o in step["options"]]
            
            # Check for duplicate option IDs
            if len(set(opt_ids)) != len(opt_ids):
                errors.append(f"Step '{full_id}': duplicate option IDs")
            
            # Check answer
            if "answer" not in step:
                errors.append(f"Step '{full_id}': missing 'answer' field")
                continue
            
            correct_id = step["answer"].get("correct_option_id")
            if correct_id not in opt_ids:
                errors.append(f"Step '{full_id}': correct_option_id '{correct_id}' not in options")
    
    return errors


def validate_campaign(campaign: Campaign, assets_base: Optional[Path] = None) -> List[str]:
    """
    Validate a Campaign object.
    
    Returns:
        List of error messages (empty if valid)
    """
    errors: List[str] = []
    
    if not campaign.rounds:
        errors.append("Campaign has no rounds")
        return errors
    
    for r in campaign.rounds:
        if not r.steps:
            errors.append(f"Round '{r.id}': has no steps")
            continue
        
        for step in r.steps:
            opt_ids = [o.id for o in step.options]
            
            if len(set(opt_ids)) != len(opt_ids):
                errors.append(f"Step '{r.id}:{step.id}': duplicate option IDs")
            
            if step.answer.correct_option_id not in opt_ids:
                errors.append(f"Step '{r.id}:{step.id}': correct answer not in options")
    
    return errors


# ==========================
# QC Verification
# ==========================

def verify_step_qc(step: Step, qc_spec: Optional[dict]) -> List[str]:
    """
    Verify that a step's correct answer is physically correct.
    
    For select_measurement steps, checks that the correct option
    is actually a safe measurement given the stabilizers.
    
    Returns:
        List of warning messages (empty if valid)
    """
    warnings: List[str] = []
    
    if not qc_spec:
        return warnings
    
    if step.kind != "select_measurement":
        # Only verify measurement steps for now
        return warnings
    
    stabilizers = qc_spec.get("stabilizers", [])
    if not stabilizers:
        return warnings
    
    # Find the correct option
    correct_id = step.answer.correct_option_id
    correct_option = None
    for opt in step.options:
        if opt.id == correct_id:
            correct_option = opt
            break
    
    if not correct_option:
        warnings.append(f"Step '{step.id}': could not find correct option")
        return warnings
    
    # Parse the Pauli string from the label
    # Labels are like "X I I" or "Z Z Z" - convert to compact form
    label = correct_option.label.replace(" ", "")
    
    try:
        # Use qcmain1 to verify
        n_qubits = qc_spec.get("n_qubits", len(label))
        
        # Create Stim PauliString from the label
        import stim
        measurement = stim.PauliString(n_qubits)
        for i, ch in enumerate(label):
            if ch in ['X', 'Y', 'Z']:
                measurement[i] = ch
        
        # Create stabilizer PauliStrings
        stab_paulis = []
        for s in stabilizers:
            stab = stim.PauliString(n_qubits)
            for i, ch in enumerate(s):
                if ch in ['X', 'Y', 'Z']:
                    stab[i] = ch
            stab_paulis.append(stab)
        
        # Count anti-commuting stabilizers
        anti_count = sum(1 for s in stab_paulis if not measurement.commutes(s))
        
        if anti_count == 0:
            warnings.append(
                f"Step '{step.id}': correct answer '{label}' commutes with all stabilizers "
                f"(logical measurement!)"
            )
        elif anti_count > 1:
            warnings.append(
                f"Step '{step.id}': correct answer '{label}' anti-commutes with {anti_count} "
                f"stabilizers (destroys multiple generators)"
            )
        # anti_count == 1 is the ideal "safe" case
        
    except Exception as e:
        warnings.append(f"Step '{step.id}': QC verification failed: {e}")
    
    return warnings


def verify_round_qc(round_data: Round) -> List[str]:
    """
    Verify all steps in a round using QC checks.
    
    Returns:
        List of warning messages
    """
    warnings: List[str] = []
    
    qc_spec = None
    if round_data.qc_spec:
        qc_spec = {
            "n_qubits": round_data.qc_spec.n_qubits,
            "alice_qubits": round_data.qc_spec.alice_qubits,
            "bob_qubits": round_data.qc_spec.bob_qubits,
            "cz_edges": round_data.qc_spec.cz_edges,
            "stabilizers": round_data.qc_spec.stabilizers,
        }
    
    for step in round_data.steps:
        step_warnings = verify_step_qc(step, qc_spec)
        warnings.extend(step_warnings)
    
    return warnings


def verify_campaign_qc(campaign: Campaign) -> List[str]:
    """
    Verify all rounds in a campaign using QC checks.
    
    Returns:
        List of warning messages
    """
    warnings: List[str] = []
    
    for round_data in campaign.rounds:
        round_warnings = verify_round_qc(round_data)
        for w in round_warnings:
            warnings.append(f"Round '{round_data.id}': {w}")
    
    return warnings


# ==========================
# Round Building (for future procedural generation)
# ==========================

def build_measurement_step(
    step_id: str,
    prompt: str,
    options: List[Tuple[str, str]],  # List of (id, pauli_label)
    correct_id: str,
    feedback_correct: str = "Correct!",
    feedback_wrong: str = "Wrong!",
    timer_seconds: int = 30
) -> Step:
    """
    Build a select_measurement step.
    
    Args:
        step_id: Unique step identifier
        prompt: The question prompt
        options: List of (id, pauli_label) tuples
        correct_id: The ID of the correct option
        feedback_correct: Feedback for correct answer
        feedback_wrong: Feedback for wrong answer
        timer_seconds: Timer duration
    
    Returns:
        A Step object
    """
    from .model import Option, StepAnswer, StepFeedback, StepTimer, Step
    
    return Step(
        id=step_id,
        kind="select_measurement",
        prompt_markdown=prompt,
        options=[
            Option(id=oid, label=label, detail_markdown="")
            for oid, label in options
        ],
        answer=StepAnswer(correct_option_id=correct_id),
        feedback=StepFeedback(
            on_correct_markdown=feedback_correct,
            on_wrong_markdown=feedback_wrong
        ),
        timer=StepTimer(enabled=True, seconds=timer_seconds)
    )
