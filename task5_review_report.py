import json

from review_report import (
    ReviewReportValidator,
    build_review_report,
    save_review_report,
)


def main() -> None:
    report = build_review_report()
    validator = ReviewReportValidator()

    print("=" * 70)
    print("Topic 17 — Task 5: Review Report")
    print("=" * 70)

    print("\nValidation:")
    print(validator.validate(report))

    print("\n1. FINDING")
    print(report.finding)

    print("\n2. IMPACT")
    print(report.impact)

    print("\n3. FIX")
    print(report.fix)

    print("\n4. RESIDUAL RISK")
    print(report.residual_risk)

    print("\n5. RECOMMENDED NEXT ACTION")
    print(report.recommended_next_action)

    save_review_report(report)

    print("\nReport evidence:")
    print("outputs\\task5_review_report.json")


if __name__ == "__main__":
    main()