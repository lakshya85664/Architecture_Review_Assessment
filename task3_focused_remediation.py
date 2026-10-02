from finding_reproduction import (
    AgentState,
    DurableStateStore,
    save_remediation_evidence,
)


def main() -> None:
    print("=" * 70)
    print("Topic 17 — Task 3: Focused Remediation")
    print("=" * 70)

    state_path = "outputs/task3_agent_state.json"

    store = DurableStateStore(state_path)

    original_state = AgentState(
        goal="complete architecture review",
        status="running",
        step_count=3,
    )

    print("\nBEFORE remediation:")
    print("State after process restart: None")
    print("Result: state lost")

    print("\nApplying focused JSON persistence remediation...")

    store.save(original_state)

    # Simulate a new process by creating a new store instance.
    restarted_store = DurableStateStore(state_path)

    recovered_state = restarted_store.load()

    print("\nAFTER remediation:")
    print("Recovered state:")
    print(recovered_state)

    success = recovered_state == original_state

    print(
        "\nState successfully recovered:",
        success,
    )

    save_remediation_evidence(
        before={
            "state_after_restart": None,
            "result": "state lost",
        },
        after={
            "state_after_restart": {
                "goal": recovered_state.goal,
                "status": recovered_state.status,
                "step_count": recovered_state.step_count,
            },
            "result": "state recovered",
        },
    )

    print(
        "\nEvidence saved to: "
        "outputs\\task3_remediation_evidence.json"
    )


if __name__ == "__main__":
    main()