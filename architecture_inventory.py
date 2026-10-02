from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import List


VALID_STATUSES = {
    "implemented",
    "partial",
    "not_evidenced",
}


@dataclass(frozen=True)
class Component:
    name: str
    status: str
    evidence: str
    boundary: str
    risk_note: str


class ArchitectureInventory:
    """
    Evidence-based inventory of the existing AI-agent architecture.

    This review deliberately distinguishes implemented components from
    components that are only partially evidenced or not evidenced.
    """

    def __init__(self, components: List[Component]):
        self.components = components

    def validate(self) -> bool:
        if not self.components:
            return False

        names = set()

        for component in self.components:
            if not component.name.strip():
                return False

            if component.status not in VALID_STATUSES:
                return False

            if not component.evidence.strip():
                return False

            if not component.boundary.strip():
                return False

            if not component.risk_note.strip():
                return False

            if component.name in names:
                return False

            names.add(component.name)

        return True

    def get(self, name: str) -> Component:
        for component in self.components:
            if component.name == name:
                return component

        raise KeyError(f"Component not found: {name}")

    def summary(self) -> dict:
        counts = {
            "implemented": 0,
            "partial": 0,
            "not_evidenced": 0,
        }

        for component in self.components:
            counts[component.status] += 1

        return {
            "component_count": len(self.components),
            "status_counts": counts,
            "validation": self.validate(),
        }

    def to_dict(self) -> dict:
        return {
            "summary": self.summary(),
            "components": [
                asdict(component)
                for component in self.components
            ],
        }

    def save(self, path: str) -> None:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        output_path.write_text(
            json.dumps(self.to_dict(), indent=2),
            encoding="utf-8",
        )


def build_existing_architecture_inventory() -> ArchitectureInventory:
    """
    Build the inventory from previously implemented Tayana architecture
    components.

    Evidence is intentionally conservative. Missing implementation evidence
    is recorded as 'not_evidenced' instead of being inferred.
    """

    components = [
        Component(
            name="Brain",
            status="implemented",
            evidence=(
                "Implement_Brain contains an explicit Brain component that "
                "consumes and updates AgentState and produces operational "
                "decision traces."
            ),
            boundary=(
                "Owns decision processing and state transitions inside the "
                "agent control loop."
            ),
            risk_note=(
                "Decision quality depends on the available structured state "
                "and bounded execution rules."
            ),
        ),
        Component(
            name="Planner",
            status="implemented",
            evidence=(
                "Planner_Executor_Assessment contains a Planner that creates "
                "structured plans and plan steps."
            ),
            boundary=(
                "Creates the plan; execution is handled separately by the "
                "Executor."
            ),
            risk_note=(
                "Planner output must remain validated before execution."
            ),
        ),
        Component(
            name="Executor",
            status="implemented",
            evidence=(
                "Planner_Executor_Assessment contains an Executor with "
                "validated step execution and action/tool integration."
            ),
            boundary=(
                "Executes validated plan steps and reports operational "
                "results."
            ),
            risk_note=(
                "Execution requires bounded retries, validation, and safe "
                "tool boundaries."
            ),
        ),
        Component(
            name="Memory",
            status="not_evidenced",
            evidence=(
                "No dedicated persistent agent-memory component was "
                "established by the reviewed architecture projects."
            ),
            boundary=(
                "No persistent long-term memory boundary is currently "
                "established."
            ),
            risk_note=(
                "Adding memory later would require explicit storage, "
                "retrieval, retention, and privacy boundaries."
            ),
        ),
        Component(
            name="Tools",
            status="implemented",
            evidence=(
                "Planner_Executor_Assessment includes an actions/tools "
                "registry used by the Executor."
            ),
            boundary=(
                "Tools are invoked through the execution layer rather than "
                "being directly embedded in the planning component."
            ),
            risk_note=(
                "Tool authority must remain bounded and tool inputs and "
                "outputs must be validated."
            ),
        ),
        Component(
            name="State",
            status="implemented",
            evidence=(
                "Implement_Brain defines AgentState with goal, plan, "
                "observations, status, and step_count."
            ),
            boundary=(
                "AgentState represents operational workflow state used by "
                "the control loop."
            ),
            risk_note=(
                "State changes must remain bounded and traceable."
            ),
        ),
        Component(
            name="Control Loop",
            status="implemented",
            evidence=(
                "Implement_Brain uses an Observe -> Decide -> Act -> "
                "State Update loop with a hard step limit."
            ),
            boundary=(
                "Controls progression between observation, decision, action, "
                "and state update."
            ),
            risk_note=(
                "Loop limits are required to prevent unbounded execution."
            ),
        ),
        Component(
            name="Communication",
            status="implemented",
            evidence=(
                "Communication_Assessment implements structured messages, "
                "routing, acknowledgements, dead-letter handling, and "
                "correlation tracing."
            ),
            boundary=(
                "Provides structured communication between agent components "
                "and preserves operational correlation."
            ),
            risk_note=(
                "Communication failures require validation, bounded retries, "
                "and dead-letter handling."
            ),
        ),
        Component(
            name="Persistence",
            status="partial",
            evidence=(
                "The reviewed projects persist operational traces and JSON "
                "artifacts, but no general durable agent-state database was "
                "established."
            ),
            boundary=(
                "Persistence currently focuses on review evidence and traces, "
                "not complete long-term agent state."
            ),
            risk_note=(
                "A production deployment would require explicit durability "
                "and recovery semantics."
            ),
        ),
        Component(
            name="Deployment",
            status="partial",
            evidence=(
                "The reviewed architecture is executable locally using "
                "Python virtual environments and command-line workflows."
            ),
            boundary=(
                "Current evidence covers local execution; no production "
                "service, container orchestration, or hosted deployment "
                "boundary was established."
            ),
            risk_note=(
                "Production deployment would require explicit service, "
                "network, authentication, and operational boundaries."
            ),
        ),
    ]

    return ArchitectureInventory(components)


def save_architecture_trace(
    inventory: ArchitectureInventory,
    path: str = "traces/task1_trace.json",
) -> None:
    trace = {
        "task": "Task 1 - Architecture Inventory",
        "architecture_review": "evidence_based",
        "summary": inventory.summary(),
        "components": inventory.to_dict()["components"],
    }

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(
        json.dumps(trace, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    inventory = build_existing_architecture_inventory()

    print("=" * 70)
    print("Topic 17 — Task 1: Architecture Inventory")
    print("=" * 70)

    print("\nValidation:", inventory.validate())

    print("\nComponents:")
    for component in inventory.components:
        print(
            f"- {component.name}: "
            f"{component.status}"
        )

    print("\nSummary:")
    print(json.dumps(inventory.summary(), indent=2))

    save_architecture_trace(inventory)

    print("\nTrace saved to: traces/task1_trace.json")