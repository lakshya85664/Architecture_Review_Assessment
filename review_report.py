from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class ReviewReport:
    finding: str
    severity: str
    evidence: str
    impact: str
    fix: str
    residual_risk: str
    recommended_next_action: str


class ReviewReportValidator:
    REQUIRED_FIELDS = {
        "finding",
        "severity",
        "evidence",
        "impact",
        "fix",
        "residual_risk",
        "recommended_next_action",
    }

    def validate(self, report: ReviewReport) -> bool:
        values = asdict(report)

        if set(values.keys()) != self.REQUIRED_FIELDS:
            return False

        for value in values.values():
            if not isinstance(value, str):
                return False

            if not value.strip():
                return False

        return report.severity in {
            "critical",
            "high",
            "medium",
            "low",
        }


def build_review_report() -> ReviewReport:
    return ReviewReport(
        finding=(
            "Agent workflow state was not durably persisted across a "
            "process restart in the reviewed architecture boundary."
        ),
        severity="medium",
        evidence=(
            "Task 2 reproduced the issue: an AgentState existed before the "
            "simulated process restart, while a new in-memory state boundary "
            "returned no state afterward. Task 2 saved this result in "
            "traces/task2_finding_trace.json."
        ),
        impact=(
            "A process interruption can cause the workflow to lose its "
            "in-memory state and require recovery or restart from an earlier "
            "checkpoint. The impact is primarily a reliability and recovery "
            "boundary in the reviewed architecture."
        ),
        fix=(
            "Task 3 added a focused DurableStateStore using JSON persistence. "
            "State is validated before writing, a temporary file is written "
            "first, and the temporary file replaces the target state file "
            "after a successful write. A new store instance can then recover "
            "the same AgentState."
        ),
        residual_risk=(
            "The JSON persistence implementation is suitable for the "
            "assessment-level local workflow but does not provide the full "
            "durability, concurrency, backup, availability, or recovery "
            "semantics expected from a production persistence service."
        ),
        recommended_next_action=(
            "Before production deployment, define and validate a durable "
            "persistence boundary with explicit recovery, concurrency, "
            "backup, retention, and failure-handling requirements. Keep the "
            "current local JSON store as the assessment-level implementation."
        ),
    )


def save_review_report(
    report: ReviewReport,
    path: str = "outputs/task5_review_report.json",
) -> None:
    validator = ReviewReportValidator()

    if not validator.validate(report):
        raise ValueError(
            "Review report failed validation."
        )

    payload = {
        "task": "Task 5 - Review Report",
        "report_type": "engineering_review",
        "validation": True,
        "report": asdict(report),
    }

    output_path = Path(path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    report = build_review_report()
    validator = ReviewReportValidator()

    print("=" * 70)
    print("Topic 17 — Task 5: Review Report")
    print("=" * 70)

    print("\nReport validation:")
    print(validator.validate(report))

    print("\nFINDING")
    print(report.finding)

    print("\nSEVERITY")
    print(report.severity)

    print("\nEVIDENCE")
    print(report.evidence)

    print("\nIMPACT")
    print(report.impact)

    print("\nFIX")
    print(report.fix)

    print("\nRESIDUAL RISK")
    print(report.residual_risk)

    print("\nRECOMMENDED NEXT ACTION")
    print(report.recommended_next_action)

    save_review_report(report)

    print(
        "\nReport saved to: "
        "outputs\\task5_review_report.json"
    )


if __name__ == "__main__":
    main()