from dataclasses import dataclass, field


@dataclass
class ResearchRequest:
    topic: str
    request_id: str


@dataclass
class ResearchStep:
    title: str
    description: str


@dataclass
class ResearchPlan:
    topic: str
    steps: list[ResearchStep]


@dataclass
class StepFindings:
    step_title: str
    findings: str


@dataclass
class ResearchSummary:
    topic: str
    summary: str
    steps_completed: int


@dataclass
class FactCheckResult:
    original_summary: str
    corrections: list[str]
    verified_summary: str


@dataclass
class PollingState:
    """State carried across continue-as-new boundaries."""
    pending_requests: list[ResearchRequest] = field(default_factory=list)
    completed_count: int = 0
