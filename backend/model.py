"""Typed models for campaign/level and round data.

These mirror the JSON schema consumed by the front-end (schema v1.0).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from pathlib import Path


@dataclass
class Option:
    """A single answer option for a step."""
    id: str
    label: str
    detail_markdown: str = ""


@dataclass
class StepAnswer:
    """The correct answer for a step."""
    correct_option_id: str


@dataclass
class StepTimer:
    """Timer configuration for a specific step."""
    enabled: bool = True
    seconds: int = 30


@dataclass
class StepFeedback:
    """Feedback messages for correct/wrong answers."""
    on_correct_markdown: str = "Correct!"
    on_wrong_markdown: str = "Wrong!"


@dataclass
class Step:
    """A single step within a round (one question)."""
    id: str
    kind: str  # e.g., "select_measurement", "select_correction", "select_clifford"
    prompt_markdown: str
    options: List[Option]
    answer: StepAnswer
    feedback: Optional[StepFeedback] = None
    timer: Optional[StepTimer] = None


@dataclass
class RoundAssets:
    """Asset paths for a round (relative to assets_base)."""
    circuit_image: Optional[str] = None
    graph_image: Optional[str] = None


@dataclass
class QCSpec:
    """Quantum circuit specification for rendering and validation."""
    n_qubits: int = 0
    alice_qubits: List[int] = field(default_factory=list)
    bob_qubits: List[int] = field(default_factory=list)
    cz_edges: List[List[int]] = field(default_factory=list)
    rotations: List[Dict[str, Any]] = field(default_factory=list)
    stabilizers: List[str] = field(default_factory=list)
    measurements: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class Round:
    """A single round containing one or more steps."""
    id: str
    title: str
    difficulty: int
    context_markdown: str
    steps: List[Step]
    assets: Optional[RoundAssets] = None
    qc_spec: Optional[QCSpec] = None


@dataclass
class IntroSlide:
    """An intro slide shown before the game starts."""
    id: str
    title: str
    body_markdown: str = ""
    images: List[str] = field(default_factory=list)


@dataclass
class TimerConfig:
    """Global timer configuration."""
    enabled: bool = True
    seconds_per_step: int = 30


@dataclass
class CheatConfig:
    """Cheat code configuration."""
    enabled: bool = False
    code: str = ""


@dataclass
class Config:
    """Campaign configuration."""
    timer: TimerConfig = field(default_factory=TimerConfig)
    cheat: CheatConfig = field(default_factory=CheatConfig)


@dataclass
class Meta:
    """Campaign metadata."""
    title: str = "Stabilizer Survival"
    subtitle: str = ""
    theme: str = "terminal"
    assets_base: str = "assets"


@dataclass
class Info:
    """Rulebook/info page content."""
    markdown: str = ""
    images: List[str] = field(default_factory=list)


@dataclass
class Campaign:
    """The top-level campaign/level structure."""
    schema_version: str
    meta: Meta
    config: Config
    info: Info
    intro_slides: List[IntroSlide]
    rounds: List[Round]


# ==========================
# Serialization helpers
# ==========================

def to_json_dict(obj: Any) -> Dict[str, Any]:
    """Convert a dataclass to a JSON-serializable dict."""
    if hasattr(obj, '__dataclass_fields__'):
        result = {}
        for key, value in asdict(obj).items():
            # Convert snake_case keys to camelCase for some fields if needed
            result[key] = value
        return result
    return obj


def campaign_to_json(campaign: Campaign) -> str:
    """Serialize a Campaign to JSON string."""
    return json.dumps(to_json_dict(campaign), indent=2)


def campaign_to_file(campaign: Campaign, path: Path) -> None:
    """Write a Campaign to a JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(campaign_to_json(campaign))


# ==========================
# Deserialization helpers
# ==========================

def option_from_dict(d: Dict[str, Any]) -> Option:
    return Option(
        id=d["id"],
        label=d["label"],
        detail_markdown=d.get("detail_markdown", "")
    )


def step_answer_from_dict(d: Dict[str, Any]) -> StepAnswer:
    return StepAnswer(correct_option_id=d["correct_option_id"])


def step_feedback_from_dict(d: Dict[str, Any]) -> StepFeedback:
    return StepFeedback(
        on_correct_markdown=d.get("on_correct_markdown", "Correct!"),
        on_wrong_markdown=d.get("on_wrong_markdown", "Wrong!")
    )


def step_timer_from_dict(d: Dict[str, Any]) -> StepTimer:
    return StepTimer(
        enabled=d.get("enabled", True),
        seconds=d.get("seconds", 30)
    )


def step_from_dict(d: Dict[str, Any]) -> Step:
    return Step(
        id=d["id"],
        kind=d["kind"],
        prompt_markdown=d["prompt_markdown"],
        options=[option_from_dict(o) for o in d.get("options", [])],
        answer=step_answer_from_dict(d["answer"]),
        feedback=step_feedback_from_dict(d["feedback"]) if d.get("feedback") else None,
        timer=step_timer_from_dict(d["timer"]) if d.get("timer") else None
    )


def round_assets_from_dict(d: Dict[str, Any]) -> RoundAssets:
    return RoundAssets(
        circuit_image=d.get("circuit_image"),
        graph_image=d.get("graph_image")
    )


def qc_spec_from_dict(d: Dict[str, Any]) -> QCSpec:
    return QCSpec(
        n_qubits=d.get("n_qubits", 0),
        alice_qubits=d.get("alice_qubits", []),
        bob_qubits=d.get("bob_qubits", []),
        cz_edges=d.get("cz_edges", []),
        rotations=d.get("rotations", []),
        stabilizers=d.get("stabilizers", []),
        measurements=d.get("measurements", [])
    )


def round_from_dict(d: Dict[str, Any]) -> Round:
    return Round(
        id=d["id"],
        title=d["title"],
        difficulty=d.get("difficulty", 1),
        context_markdown=d.get("context_markdown", ""),
        steps=[step_from_dict(s) for s in d.get("steps", [])],
        assets=round_assets_from_dict(d["assets"]) if d.get("assets") else None,
        qc_spec=qc_spec_from_dict(d["qc_spec"]) if d.get("qc_spec") else None
    )


def intro_slide_from_dict(d: Dict[str, Any]) -> IntroSlide:
    return IntroSlide(
        id=d["id"],
        title=d["title"],
        body_markdown=d.get("body_markdown", ""),
        images=d.get("images", [])
    )


def timer_config_from_dict(d: Dict[str, Any]) -> TimerConfig:
    return TimerConfig(
        enabled=d.get("enabled", True),
        seconds_per_step=d.get("seconds_per_step", 30)
    )


def cheat_config_from_dict(d: Dict[str, Any]) -> CheatConfig:
    return CheatConfig(
        enabled=d.get("enabled", False),
        code=d.get("code", "")
    )


def config_from_dict(d: Dict[str, Any]) -> Config:
    return Config(
        timer=timer_config_from_dict(d.get("timer", {})),
        cheat=cheat_config_from_dict(d.get("cheat", {}))
    )


def meta_from_dict(d: Dict[str, Any]) -> Meta:
    return Meta(
        title=d.get("title", "Stabilizer Survival"),
        subtitle=d.get("subtitle", ""),
        theme=d.get("theme", "terminal"),
        assets_base=d.get("assets_base", "assets")
    )


def info_from_dict(d: Dict[str, Any]) -> Info:
    return Info(
        markdown=d.get("markdown", ""),
        images=d.get("images", [])
    )


def campaign_from_dict(d: Dict[str, Any]) -> Campaign:
    return Campaign(
        schema_version=d.get("schema_version", "1.0"),
        meta=meta_from_dict(d.get("meta", {})),
        config=config_from_dict(d.get("config", {})),
        info=info_from_dict(d.get("info", {})),
        intro_slides=[intro_slide_from_dict(s) for s in d.get("intro_slides", [])],
        rounds=[round_from_dict(r) for r in d.get("rounds", [])]
    )


def campaign_from_json(json_str: str) -> Campaign:
    """Deserialize a Campaign from a JSON string."""
    return campaign_from_dict(json.loads(json_str))


def campaign_from_file(path: Path) -> Campaign:
    """Load a Campaign from a JSON file."""
    with path.open("r", encoding="utf-8") as f:
        return campaign_from_json(f.read())
