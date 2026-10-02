import json

from operational_review import (
    build_operational_review,
    save_operational_review,
)


def main() -> None:
    review = build_operational_review()

    print("=" * 70)
    print("Topic 17 — Task 4: Operational Review")
    print("=" * 70)

    print("\nReview validation:")
    print(review.validate())

    print("\nPrioritized risk register:")

    for risk in review.risks:
        print(
            f"{risk.risk_id} | "
            f"Priority={risk.priority} | "
            f"Status={risk.status} | "
            f"Area={risk.area}"
        )

    print("\nDetailed review:")

    for risk in review.risks:
        print(f"\n[{risk.risk_id}] {risk.area}")
        print(f"Priority: {risk.priority}")
        print(f"Status: {risk.status}")
        print(f"Evidence: {risk.evidence}")
        print(f"Impact: {risk.impact}")
        print(f"Recommended action: {risk.recommended_action}")
        print(f"Residual risk: {risk.residual_risk}")

    print("\nSummary:")
    print(json.dumps(review.summary(), indent=2))

    save_operational_review(review)

    print(
        "\nEvidence saved to: "
        "traces\\task4_operational_review.json"
    )


if __name__ == "__main__":
    main()