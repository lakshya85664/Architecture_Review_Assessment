from finding_reproduction import (
    reproduce_persistence_loss,
    save_finding,
)


def main() -> None:
    finding = reproduce_persistence_loss()

    print("=" * 70)
    print("Topic 17 — Task 2: Finding Reproduction")
    print("=" * 70)

    print("\nFinding statement:")
    print(finding.finding)

    print("\nSeverity:", finding.severity)

    print("\nExpected behavior:")
    print(finding.expected)

    print("\nObserved behavior:")
    print(finding.observed)

    print("\nImpact:")
    print(finding.impact)

    print("\nReproduction steps:")
    print(finding.reproduction)

    save_finding(finding)

    print("\nEvidence:")
    print("REPRODUCED")
    print("traces\\task2_finding_trace.json")
    print("outputs\\task2_finding_report.json")


if __name__ == "__main__":
    main()