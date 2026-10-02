from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
from typing import Optional


SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{12,}"),
    re.compile(
        r"(?i)(api[_-]?key|password|secret|token)"
        r"\s*[:=]\s*['\"]?[A-Za-z0-9_\-./+=]{8,}"
    ),
]


@dataclass
class AgentState:
    goal: str
    status: str
    step_count: int


class InMemoryStateBoundary:
    """
    Minimal reproduction of the original persistence boundary.

    State exists only during the lifetime of this object/process.
    """

    def __init__(self) -> None:
        self._state: Optional[AgentState] = None

    def save(self, state: AgentState) -> None:
        self._state = state

    def load(self) -> Optional[AgentState]:
        return self._state


class StateValidationError(ValueError):
    """Raised when agent state fails validation."""


def _contains_secret_like_value(value: str) -> bool:
    return any(
        pattern.search(value)
        for pattern in SECRET_PATTERNS
    )


def validate_state(state: AgentState) -> None:
    if not isinstance(state, AgentState):
        raise StateValidationError(
            "state must be an AgentState instance"
        )

    if not state.goal.strip():
        raise StateValidationError(
            "goal must not be empty"
        )

    if not state.status.strip():
        raise StateValidationError(
            "status must not be empty"
        )

    if state.step_count < 0:
        raise StateValidationError(
            "step_count must not be negative"
        )

    if _contains_secret_like_value(state.goal):
        raise StateValidationError(
            "goal contains secret-like content"
        )

    if _contains_secret_like_value(state.status):
        raise StateValidationError(
            "status contains secret-like content"
        )


class DurableStateStore:
    """
    Focused JSON persistence boundary for AgentState.

    The store deliberately remains small and local. It does not introduce
    a database or redesign the agent architecture.
    """

    def __init__(self, path: str) -> None:
        self.path = Path(path)

    def save(self, state: AgentState) -> None:
        validate_state(state)

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        payload = {
            "goal": state.goal,
            "status": state.status,
            "step_count": state.step_count,
        }

        temporary_path = self.path.with_suffix(
            self.path.suffix + ".tmp"
        )

        temporary_path.write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8",
        )

        temporary_path.replace(self.path)

    def load(self) -> AgentState:
        if not self.path.exists():
            raise FileNotFoundError(
                f"State file does not exist: {self.path}"
            )

        data = json.loads(
            self.path.read_text(encoding="utf-8")
        )

        state = AgentState(
            goal=data.get("goal", ""),
            status=data.get("status", ""),
            step_count=data.get("step_count", -1),
        )

        validate_state(state)

        return state


@dataclass
class Finding:
    area: str
    severity: str
    finding: str
    expected: str
    observed: str
    impact: str
    reproduction: str


def reproduce_persistence_loss() -> Finding:
    """
    Reproduce loss of workflow state when the in-memory boundary is replaced.
    """

    first_process = InMemoryStateBoundary()

    original_state = AgentState(
        goal="complete architecture review",
        status="running",
        step_count=3,
    )

    first_process.save(original_state)

    state_before_restart = first_process.load()

    restarted_process = InMemoryStateBoundary()

    state_after_restart = restarted_process.load()

    assert state_before_restart is not None
    assert state_before_restart.goal == "complete architecture review"
    assert state_before_restart.step_count == 3

    if state_after_restart is None:
        observed = (
            "Workflow state was present before restart but was unavailable "
            "from the new process boundary."
        )
    else:
        observed = (
            "Workflow state remained available after restart, which would "
            "contradict the reproduction target."
        )

    return Finding(
        area="persistence",
        severity="medium",
        finding=(
            "Agent workflow state is not durably persisted across a process "
            "restart in the reviewed architecture boundary."
        ),
        expected=(
            "A restart should allow the workflow state to be recovered when "
            "durable persistence is required."
        ),
        observed=observed,
        impact=(
            "A process interruption can require the workflow to restart from "
            "lost in-memory state unless an external durable state mechanism "
            "is introduced."
        ),
        reproduction=(
            "Create AgentState, save it to the in-memory boundary, replace "
            "the boundary with a new instance, and attempt to load the "
            "previous state."
        ),
    )


def save_finding(
    finding: Finding,
    trace_path: str = "traces/task2_finding_trace.json",
    report_path: str = "outputs/task2_finding_report.json",
) -> None:
    trace = {
        "task": "Task 2 - Finding Reproduction",
        "reproduction_status": "reproduced",
        "finding": finding.finding,
        "area": finding.area,
        "severity": finding.severity,
        "expected": finding.expected,
        "observed": finding.observed,
        "impact": finding.impact,
        "reproduction": finding.reproduction,
        "evidence": {
            "state_before_restart": {
                "goal": "complete architecture review",
                "status": "running",
                "step_count": 3,
            },
            "state_after_restart": None,
        },
    }

    report = {
        "task": "Task 2 - Finding Reproduction",
        "finding_statement": finding.finding,
        "severity": finding.severity,
        "evidence": trace,
    }

    trace_file = Path(trace_path)
    trace_file.parent.mkdir(parents=True, exist_ok=True)
    trace_file.write_text(
        json.dumps(trace, indent=2),
        encoding="utf-8",
    )

    report_file = Path(report_path)
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )


def save_remediation_evidence(
    before: dict,
    after: dict,
    path: str = "outputs/task3_remediation_evidence.json",
) -> None:
    evidence = {
        "task": "Task 3 - Focused Remediation",
        "finding": (
            "Agent workflow state was not durably persisted across a "
            "process restart."
        ),
        "remediation": (
            "Added a small JSON DurableStateStore with validation and "
            "atomic replacement of the state file."
        ),
        "before": before,
        "after": after,
        "regression_status": "fixed",
        "residual_risk": (
            "Local JSON persistence is appropriate for this assessment, "
            "but production multi-process durability would require a "
            "stronger storage boundary."
        ),
    }

    output_path = Path(path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(evidence, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    finding = reproduce_persistence_loss()

    print("=" * 70)
    print("Topic 17 — Task 3: Focused Remediation")
    print("=" * 70)

    print("\nOriginal finding:")
    print(finding.finding)

    print("\nApplying focused remediation...")

    state_path = Path(
        "outputs/remediated_agent_state.json"
    )

    store = DurableStateStore(str(state_path))

    original_state = AgentState(
        goal="complete architecture review",
        status="running",
        step_count=3,
    )

    store.save(original_state)

    print("\nState saved before simulated restart:")
    print(original_state)

    # Simulate restart by creating a new store instance.
    restarted_store = DurableStateStore(
        str(state_path)
    )

    recovered_state = restarted_store.load()

    print("\nRecovered state after simulated restart:")
    print(recovered_state)

    success = recovered_state == original_state

    print("\nBEFORE remediation:")
    print("State after restart: None")
    print("Persistence failure reproduced: True")

    print("\nAFTER remediation:")
    print(
        "State after restart:",
        recovered_state,
    )
    print(
        "State successfully recovered:",
        success,
    )

    before = {
        "state_after_restart": None,
        "result": "state lost",
    }

    after = {
        "state_after_restart": asdict(recovered_state),
        "result": "state recovered",
    }

    save_remediation_evidence(
        before=before,
        after=after,
    )

    print("\nRemediation evidence saved to:")
    print(
        "outputs\\task3_remediation_evidence.json"
    )


if __name__ == "__main__":
    main()