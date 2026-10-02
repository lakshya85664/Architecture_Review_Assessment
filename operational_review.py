from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import List


VALID_STATUSES = {
    "implemented",
    "partial",
    "not_evidenced",
}

VALID_PRIORITIES = {
    "critical",
    "high",
    "medium",
    "low",
}


@dataclass(frozen=True)
class RiskItem:
    risk_id: str
    area: str
    priority: str
    status: str
    evidence: str
    impact: str
    recommended_action: str
    residual_risk: str


class OperationalReview:
    def __init__(self, risks: List[RiskItem]):
        self.risks = risks

    def validate(self) -> bool:
        if not self.risks:
            return False

        risk_ids = set()

        for risk in self.risks:
            if not risk.risk_id.strip():
                return False

            if risk.risk_id in risk_ids:
                return False

            if risk.priority not in VALID_PRIORITIES:
                return False

            if risk.status not in VALID_STATUSES:
                return False

            if not risk.area.strip():
                return False

            if not risk.evidence.strip():
                return False

            if not risk.impact.strip():
                return False

            if not risk.recommended_action.strip():
                return False

            if not risk.residual_risk.strip():
                return False

            risk_ids.add(risk.risk_id)

        return True

    def get(self, risk_id: str) -> RiskItem:
        for risk in self.risks:
            if risk.risk_id == risk_id:
                return risk

        raise KeyError(f"Risk not found: {risk_id}")

    def summary(self) -> dict:
        counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        }

        status_counts = {
            "implemented": 0,
            "partial": 0,
            "not_evidenced": 0,
        }

        for risk in self.risks:
            counts[risk.priority] += 1
            status_counts[risk.status] += 1

        return {
            "risk_count": len(self.risks),
            "priority_counts": counts,
            "status_counts": status_counts,
            "validation": self.validate(),
        }

    def to_dict(self) -> dict:
        return {
            "summary": self.summary(),
            "risks": [
                asdict(risk)
                for risk in self.risks
            ],
        }


def build_operational_review() -> OperationalReview:
    """
    Evidence-based operational review of the architecture established
    by the previous Tayana assessments.

    The ordering is a review priority, not a redesign plan.
    """

    risks = [
        RiskItem(
            risk_id="R1",
            area="Deployment / durable recovery",
            priority="high",
            status="partial",
            evidence=(
                "The reviewed architecture is demonstrated through local "
                "Python execution. Durable agent-state persistence was "
                "previously identified as partial and Task 3 added a local "
                "JSON persistence boundary."
            ),
            impact=(
                "A production interruption or multi-process deployment "
                "would require stronger durability and recovery semantics "
                "than the local JSON assessment implementation provides."
            ),
            recommended_action=(
                "Define a production persistence boundary with explicit "
                "durability, recovery, concurrency, and backup requirements "
                "before production deployment."
            ),
            residual_risk=(
                "The assessment-level JSON store does not provide the "
                "semantics of a production database or distributed store."
            ),
        ),
        RiskItem(
            risk_id="R2",
            area="Memory",
            priority="high",
            status="not_evidenced",
            evidence=(
                "Task 1 found no dedicated persistent long-term agent "
                "memory component in the reviewed projects."
            ),
            impact=(
                "The architecture does not currently establish explicit "
                "long-term memory retrieval, retention, or deletion "
                "semantics."
            ),
            recommended_action=(
                "If long-term memory becomes a requirement, define its "
                "storage, retrieval, retention, validation, and privacy "
                "boundary before implementation."
            ),
            residual_risk=(
                "No long-term memory behavior is claimed by this review."
            ),
        ),
        RiskItem(
            risk_id="R3",
            area="Tool authority",
            priority="medium",
            status="implemented",
            evidence=(
                "The Planner–Executor architecture separates planning from "
                "execution and uses an actions/tools registry. Tool inputs "
                "and outputs are subject to validation and secret hygiene."
            ),
            impact=(
                "A tool boundary remains security-sensitive because an "
                "executor can perform external actions on behalf of the "
                "workflow."
            ),
            recommended_action=(
                "Keep tool permissions explicit, validate inputs and outputs, "
                "and require additional approval boundaries for high-impact "
                "external actions."
            ),
            residual_risk=(
                "The assessment does not implement a production identity "
                "and authorization service for tools."
            ),
        ),
        RiskItem(
            risk_id="R4",
            area="Communication",
            priority="medium",
            status="implemented",
            evidence=(
                "Communication_Assessment implements message validation, "
                "routing, acknowledgements, dead-letter handling, and "
                "correlation tracing."
            ),
            impact=(
                "Malformed or failed messages can affect downstream "
                "workflow progress if communication boundaries are not "
                "validated."
            ),
            recommended_action=(
                "Retain schema validation, bounded transient retry, "
                "dead-letter handling, and correlation identifiers."
            ),
            residual_risk=(
                "A production distributed transport would require explicit "
                "authentication, durable delivery, and operational queue "
                "monitoring."
            ),
        ),
        RiskItem(
            risk_id="R5",
            area="Timeout",
            priority="medium",
            status="implemented",
            evidence=(
                "Planner–Executor documentation specifies per-action "
                "execution timeouts. Timeout is also represented as an "
                "explicit failure category."
            ),
            impact=(
                "Timeout boundaries prevent an individual operation from "
                "blocking execution indefinitely."
            ),
            recommended_action=(
                "Keep timeout values explicit and verify them against the "
                "actual production tool and service latency characteristics."
            ),
            residual_risk=(
                "The current architecture review does not independently "
                "benchmark production timeout values."
            ),
        ),
        RiskItem(
            risk_id="R6",
            area="Retry",
            priority="medium",
            status="implemented",
            evidence=(
                "Planner–Executor classifies transient failures separately "
                "and permits only bounded retries for transient failures."
            ),
            impact=(
                "Uncontrolled retries could amplify failures or repeat "
                "external actions."
            ),
            recommended_action=(
                "Continue retrying only classified transient failures and "
                "keep retry counts bounded."
            ),
            residual_risk=(
                "Production integrations may require idempotency controls "
                "for actions that can create external side effects."
            ),
        ),
        RiskItem(
            risk_id="R7",
            area="Validation",
            priority="low",
            status="implemented",
            evidence=(
                "The reviewed projects use explicit validation for state, "
                "plans, dependencies, messages, outputs, and other "
                "structured inputs."
            ),
            impact=(
                "Validation reduces the chance that malformed inputs or "
                "invalid workflow state reaches execution."
            ),
            recommended_action=(
                "Preserve validation at trust boundaries and validate "
                "outputs before passing them to downstream components."
            ),
            residual_risk=(
                "Validation must continue to evolve as new tools and data "
                "contracts are introduced."
            ),
        ),
        RiskItem(
            risk_id="R8",
            area="Secret hygiene",
            priority="low",
            status="implemented",
            evidence=(
                "The reviewed implementations reject secret-like content "
                "and exclude environment files and credential files through "
                "GitHub-safe repository configuration."
            ),
            impact=(
                "Secret leakage into source, state, traces, or outputs can "
                "create security exposure."
            ),
            recommended_action=(
                "Continue environment or managed-secret injection and "
                "repository scanning before submission or deployment."
            ),
            residual_risk=(
                "Pattern-based detection cannot guarantee detection of every "
                "possible credential format."
            ),
        ),
        RiskItem(
            risk_id="R9",
            area="Step limits",
            priority="low",
            status="implemented",
            evidence=(
                "Implement_Brain uses a hard step limit, and "
                "Planner–Executor provides maximum-step protection."
            ),
            impact=(
                "A bounded step count prevents uncontrolled growth of an "
                "agent execution loop."
            ),
            recommended_action=(
                "Retain explicit maximum-step limits for every autonomous "
                "execution loop."
            ),
            residual_risk=(
                "A poorly chosen limit can terminate a legitimate workflow "
                "too early, so values require workload-specific tuning."
            ),
        ),
        RiskItem(
            risk_id="R10",
            area="Observability",
            priority="low",
            status="implemented",
            evidence=(
                "The reviewed projects save structured JSON or JSONL traces "
                "containing operational events, state transitions, and "
                "execution outcomes."
            ),
            impact=(
                "Traceability supports debugging, review, and evidence of "
                "workflow behavior."
            ),
            recommended_action=(
                "Continue recording operational events while avoiding "
                "secrets and hidden chain-of-thought content."
            ),
            residual_risk=(
                "Local trace files do not by themselves provide centralized "
                "production observability."
            ),
        ),
    ]

    return OperationalReview(risks)


def save_operational_review(
    review: OperationalReview,
    path: str = "traces/task4_operational_review.json",
) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            {
                "task": "Task 4 - Operational Review",
                "review_type": "evidence_based",
                **review.to_dict(),
            },
            indent=2,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    review = build_operational_review()

    print("=" * 70)
    print("Topic 17 — Task 4: Operational Review")
    print("=" * 70)

    print("\nReview validation:", review.validate())

    print("\nPrioritized risk register:")

    for risk in review.risks:
        print(
            f"{risk.risk_id} | "
            f"{risk.priority:<8} | "
            f"{risk.status:<14} | "
            f"{risk.area}"
        )

    print("\nSummary:")
    print(json.dumps(review.summary(), indent=2))

    save_operational_review(review)

    print(
        "\nTrace saved to: "
        "traces/task4_operational_review.json"
    )