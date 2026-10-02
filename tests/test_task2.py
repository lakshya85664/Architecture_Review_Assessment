import json

from finding_reproduction import (
    AgentState,
    InMemoryStateBoundary,
    reproduce_persistence_loss,
    save_finding,
)


def test_state_exists_before_restart():
    boundary = InMemoryStateBoundary()

    state = AgentState(
        goal="review architecture",
        status="running",
        step_count=2,
    )

    boundary.save(state)

    loaded = boundary.load()

    assert loaded is not None
    assert loaded.goal == "review architecture"
    assert loaded.step_count == 2


def test_state_is_lost_after_restart():
    first_process = InMemoryStateBoundary()

    state = AgentState(
        goal="review architecture",
        status="running",
        step_count=2,
    )

    first_process.save(state)

    restarted_process = InMemoryStateBoundary()

    assert restarted_process.load() is None


def test_finding_is_reproduced():
    finding = reproduce_persistence_loss()

    assert finding.area == "persistence"
    assert finding.severity == "medium"
    assert "not durably persisted" in finding.finding
    assert "unavailable" in finding.observed


def test_reproduction_has_expected_impact():
    finding = reproduce_persistence_loss()

    assert "process interruption" in finding.impact
    assert "lost in-memory state" in finding.impact


def test_finding_is_saved(tmp_path):
    finding = reproduce_persistence_loss()

    trace_path = tmp_path / "task2_trace.json"
    report_path = tmp_path / "task2_report.json"

    save_finding(
        finding,
        trace_path=str(trace_path),
        report_path=str(report_path),
    )

    assert trace_path.exists()
    assert report_path.exists()

    trace = json.loads(
        trace_path.read_text(encoding="utf-8")
    )

    report = json.loads(
        report_path.read_text(encoding="utf-8")
    )

    assert trace["task"] == "Task 2 - Finding Reproduction"
    assert trace["reproduction_status"] == "reproduced"
    assert trace["severity"] == "medium"

    assert report["task"] == "Task 2 - Finding Reproduction"
    assert report["finding_statement"]


def test_reproduction_records_state_loss():
    finding = reproduce_persistence_loss()

    assert finding.observed.startswith(
        "Workflow state was present before restart"
    )


def test_reproduction_target_is_not_claimed_as_production_failure():
    finding = reproduce_persistence_loss()

    assert "reviewed architecture boundary" in finding.finding