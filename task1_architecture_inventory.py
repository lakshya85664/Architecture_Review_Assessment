import json

from architecture_inventory import (
    build_existing_architecture_inventory,
    save_architecture_trace,
)


def main() -> None:
    inventory = build_existing_architecture_inventory()

    print("=" * 70)
    print("Topic 17 — Task 1: Architecture Inventory")
    print("=" * 70)

    print("\nArchitecture validation:")
    print(inventory.validate())

    print("\nComponent inventory:")

    for component in inventory.components:
        print(
            f"{component.name:<18} "
            f"{component.status:<15} "
            f"| {component.evidence}"
        )

    print("\nArchitecture summary:")
    print(json.dumps(inventory.summary(), indent=2))

    save_architecture_trace(inventory)

    print("\nAnnotated diagram:")
    print("architecture_diagram.md")

    print("\nEvidence trace:")
    print("traces/task1_trace.json")


if __name__ == "__main__":
    main()