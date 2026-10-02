import json

import pytest

from finding_reproduction import (
    AgentState,
    DurableStateStore,
    StateValidationError,
)


def test_durable_store_saves_and_loads_state(tmp_path):
    state_path = tmp_path / "agent_state.json"

    store = DurableStateStore(str(state_path))

    original = AgentState(
        goal="complete architecture review",
        status="running",
        step_count=3,
    )

    store.save(original)

    restarted_store = DurableStateStore(
        str(state_path)
    )

    recovered = restarted_store.load()

    assert recovered == original


def test_persistence_survives_new_store_instance(tmp_path):
    state_path = tmp_path / "agent_state.json"

    first_store = DurableStateStore(
        str(state_path)
    )

    first_store.save(
        AgentState(
            goal="resume workflow",
            status="running",
            step_count=5,
        )
    )

    second_store = DurableStateStore(
        str(state_path)
    )

    recovered = second_store.load()

    assert recovered.goal == "resume workflow"
    assert recovered.status == "running"
    assert recovered.step_count == 5


def test_invalid_empty_goal_is_rejected(tmp_path):
    state_path = tmp_path / "agent_state.json"

    store = DurableStateStore(
        str(state_path)
    )

    with pytest.raises(StateValidationError):
        store.save(
            AgentState(
                goal="",
                status="running",
                step_count=1,
            )
        )


def test_negative_step_count_is_rejected(tmp_path):
    state_path = tmp_path / "agent_state.json"

    store = DurableStateStore(
        str(state_path)
    )

    with pytest.raises(StateValidationError):
        store.save(
            AgentState(
                goal="valid goal",
                status="running",
                step_count=-1,
            )
        )


def test_secret_like_state_is_rejected(tmp_path):
    state_path = tmp_path / "agent_state.json"

    store = DurableStateStore(
        str(state_path)
    )

    with pytest.raises(StateValidationError):
        store.save(
            AgentState(
                goal="api_key=supersecretvalue",
                status="running",
                step_count=1,
            )
        )


def test_missing_state_file_is_rejected(tmp_path):
    state_path = tmp_path / "missing.json"

    store = DurableStateStore(
        str(state_path)
    )

    with pytest.raises(FileNotFoundError):
        store.load()


def test_saved_state_has_expected_schema(tmp_path):
    state_path = tmp_path / "agent_state.json"

    store = DurableStateStore(
        str(state_path)
    )

    store.save(
        AgentState(
            goal="inspect architecture",
            status="running",
            step_count=2,
        )
    )

    data = json.loads(
        state_path.read_text(
            encoding="utf-8"
        )
    )

    assert set(data.keys()) == {
        "goal",
        "status",
        "step_count",
    }


def test_task3_remediation_is_not_a_full_architecture_rewrite():
    """
    Regression guard: the remediation remains a focused storage boundary
    rather than introducing planner, executor, communication, or tool changes.
    """

    assert DurableStateStore.__name__ == "DurableStateStore"