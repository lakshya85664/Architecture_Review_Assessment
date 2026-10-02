import json

import pytest

from operational_review import (
    OperationalReview,
    RiskItem,
    build_operational_review,
    save_operational_review,
)


def test_operational_review_success_case():
    review = build_operational_review()

    assert review.validate() is True
    assert len(review.risks) == 10


def test_operational_review_failure_case():
    invalid_risk = RiskItem(
        risk_id="R1",
        area="",
        priority="high",
        status="implemented",
        evidence="Evidence",
        impact="Impact",
        recommended_action="Action",
        residual_risk="Residual risk",
    )

    review = OperationalReview([invalid_risk])

    assert review.validate() is False


def test_duplicate_risk_ids_are_rejected():
    risk = RiskItem(
        risk_id="R1",
        area="validation",
        priority="low",
        status="implemented",
        evidence="Evidence",
        impact="Impact",
        recommended_action="Action",
        residual_risk="Residual risk",
    )

    review = OperationalReview([risk, risk])

    assert review.validate() is False


def test_required_step_limit_review_exists():
    review = build_operational_review()

    risk = review.get("R9")

    assert risk.area == "Step limits"
    assert risk.status == "implemented"


def test_required_timeout_review_exists():
    review = build_operational_review()

    risk = review.get("R5")

    assert risk.area == "Timeout"
    assert risk.status == "implemented"


def test_required_retry_review_exists():
    review = build_operational_review()

    risk = review.get("R6")

    assert risk.area == "Retry"
    assert risk.status == "implemented"


def test_required_validation_review_exists():
    review = build_operational_review()

    risk = review.get("R7")

    assert risk.area == "Validation"
    assert risk.status == "implemented"


def test_required_secret_hygiene_review_exists():
    review = build_operational_review()

    risk = review.get("R8")

    assert risk.area == "Secret hygiene"
    assert risk.status == "implemented"


def test_memory_gap_is_explicitly_recorded():
    review = build_operational_review()

    memory = review.get("R2")

    assert memory.area == "Memory"
    assert memory.status == "not_evidenced"
    assert "No long-term memory behavior" in memory.residual_risk


def test_deployment_risk_is_present():
    review = build_operational_review()

    deployment = review.get("R1")

    assert deployment.area == "Deployment / durable recovery"
    assert deployment.priority == "high"
    assert deployment.status == "partial"


def test_communication_and_observability_are_reviewed():
    review = build_operational_review()

    communication = review.get("R4")
    observability = review.get("R10")

    assert communication.status == "implemented"
    assert observability.status == "implemented"


def test_summary_counts_are_correct():
    review = build_operational_review()

    summary = review.summary()

    assert summary["risk_count"] == 10
    assert summary["priority_counts"]["critical"] == 0
    assert summary["priority_counts"]["high"] == 2
    assert summary["priority_counts"]["medium"] == 4
    assert summary["priority_counts"]["low"] == 4

    assert summary["status_counts"]["implemented"] == 8
    assert summary["status_counts"]["partial"] == 1
    assert summary["status_counts"]["not_evidenced"] == 1

    assert summary["validation"] is True


def test_review_trace_is_saved(tmp_path):
    review = build_operational_review()

    trace_path = tmp_path / "task4_review.json"

    save_operational_review(
        review,
        path=str(trace_path),
    )

    assert trace_path.exists()

    data = json.loads(
        trace_path.read_text(
            encoding="utf-8"
        )
    )

    assert data["task"] == "Task 4 - Operational Review"
    assert data["review_type"] == "evidence_based"
    assert data["summary"]["risk_count"] == 10
    assert len(data["risks"]) == 10