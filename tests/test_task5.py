import json

import pytest

from review_report import (
    ReviewReport,
    ReviewReportValidator,
    build_review_report,
    save_review_report,
)


def test_review_report_success_case():
    report = build_review_report()
    validator = ReviewReportValidator()

    assert validator.validate(report) is True


def test_review_report_failure_case():
    report = ReviewReport(
        finding="",
        severity="medium",
        evidence="Evidence",
        impact="Impact",
        fix="Fix",
        residual_risk="Residual risk",
        recommended_next_action="Action",
    )

    validator = ReviewReportValidator()

    assert validator.validate(report) is False


def test_invalid_severity_is_rejected():
    report = ReviewReport(
        finding="Finding",
        severity="unknown",
        evidence="Evidence",
        impact="Impact",
        fix="Fix",
        residual_risk="Residual risk",
        recommended_next_action="Action",
    )

    validator = ReviewReportValidator()

    assert validator.validate(report) is False


def test_report_contains_finding():
    report = build_review_report()

    assert "not durably persisted" in report.finding


def test_report_contains_evidence():
    report = build_review_report()

    assert "Task 2 reproduced the issue" in report.evidence


def test_report_contains_impact():
    report = build_review_report()

    assert "process interruption" in report.impact


def test_report_contains_fix():
    report = build_review_report()

    assert "DurableStateStore" in report.fix


def test_report_contains_residual_risk():
    report = build_review_report()

    assert "production persistence service" in report.residual_risk


def test_report_contains_recommended_action():
    report = build_review_report()

    assert "production deployment" in (
        report.recommended_next_action
    )


def test_report_is_saved(tmp_path):
    report = build_review_report()

    output_path = tmp_path / "task5_report.json"

    save_review_report(
        report,
        path=str(output_path),
    )

    assert output_path.exists()

    data = json.loads(
        output_path.read_text(
            encoding="utf-8"
        )
    )

    assert data["task"] == "Task 5 - Review Report"
    assert data["report_type"] == "engineering_review"
    assert data["validation"] is True


def test_report_has_all_required_sections():
    report = build_review_report()

    validator = ReviewReportValidator()

    assert validator.validate(report)

    assert report.finding
    assert report.severity
    assert report.evidence
    assert report.impact
    assert report.fix
    assert report.residual_risk
    assert report.recommended_next_action