import json

import pytest

from architecture_inventory import (
    ArchitectureInventory,
    Component,
    build_existing_architecture_inventory,
    save_architecture_trace,
)


def test_architecture_inventory_success_case():
    inventory = build_existing_architecture_inventory()

    assert inventory.validate() is True
    assert len(inventory.components) == 10

    expected_components = {
        "Brain",
        "Planner",
        "Executor",
        "Memory",
        "Tools",
        "State",
        "Control Loop",
        "Communication",
        "Persistence",
        "Deployment",
    }

    actual_components = {
        component.name
        for component in inventory.components
    }

    assert actual_components == expected_components


def test_architecture_inventory_failure_case():
    invalid_component = Component(
        name="Broken Component",
        status="unknown_status",
        evidence="Evidence exists",
        boundary="Boundary exists",
        risk_note="Risk exists",
    )

    inventory = ArchitectureInventory([invalid_component])

    assert inventory.validate() is False


def test_memory_is_not_invented():
    inventory = build_existing_architecture_inventory()

    memory = inventory.get("Memory")

    assert memory.status == "not_evidenced"
    assert "No dedicated persistent agent-memory" in memory.evidence


def test_persistence_is_marked_partial():
    inventory = build_existing_architecture_inventory()

    persistence = inventory.get("Persistence")

    assert persistence.status == "partial"


def test_deployment_is_marked_partial():
    inventory = build_existing_architecture_inventory()

    deployment = inventory.get("Deployment")

    assert deployment.status == "partial"


def test_core_components_are_implemented():
    inventory = build_existing_architecture_inventory()

    for name in [
        "Brain",
        "Planner",
        "Executor",
        "Tools",
        "State",
        "Control Loop",
        "Communication",
    ]:
        assert inventory.get(name).status == "implemented"


def test_summary_counts_are_correct():
    inventory = build_existing_architecture_inventory()

    summary = inventory.summary()

    assert summary["component_count"] == 10
    assert summary["status_counts"]["implemented"] == 7
    assert summary["status_counts"]["partial"] == 2
    assert summary["status_counts"]["not_evidenced"] == 1
    assert summary["validation"] is True


def test_duplicate_component_names_are_rejected():
    component = Component(
        name="Brain",
        status="implemented",
        evidence="Evidence",
        boundary="Boundary",
        risk_note="Risk",
    )

    inventory = ArchitectureInventory([component, component])

    assert inventory.validate() is False


def test_empty_inventory_is_rejected():
    inventory = ArchitectureInventory([])

    assert inventory.validate() is False


def test_missing_evidence_is_rejected():
    component = Component(
        name="Example",
        status="implemented",
        evidence="",
        boundary="Boundary",
        risk_note="Risk",
    )

    inventory = ArchitectureInventory([component])

    assert inventory.validate() is False


def test_trace_is_saved(tmp_path):
    inventory = build_existing_architecture_inventory()

    trace_path = tmp_path / "task1_trace.json"

    save_architecture_trace(
        inventory,
        str(trace_path),
    )

    assert trace_path.exists()

    data = json.loads(
        trace_path.read_text(encoding="utf-8")
    )

    assert data["task"] == "Task 1 - Architecture Inventory"
    assert data["architecture_review"] == "evidence_based"
    assert data["summary"]["component_count"] == 10
    assert len(data["components"]) == 10