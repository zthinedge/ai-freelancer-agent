from decimal import Decimal

from app.agent.pricing import calculate_contingency_rate, calculate_pricing
from app.agent.schemas import PricingToolInput, RiskReviewerOutput


def test_pricing_uses_pert_hours_and_project_risk_instead_of_service_flat_rate():
    risk_review = RiskReviewerOutput(
        prompt_version="1.0.0",
        risks=(
            {
                "risk_id": "R-1",
                "category": "technical",
                "severity": "high",
                "cause": "第三方接口尚未验证",
                "impact": "可能增加联调工时",
                "mitigation": "先制作技术验证",
                "requires_human_decision": True,
            },
        ),
        human_decisions=("确认第三方接口账号",),
    )
    contingency_rate = calculate_contingency_rate(risk_review, uncertainty_count=2)

    pricing = calculate_pricing(
        PricingToolInput(
            min_hours="10.0",
            max_hours="30.0",
            hourly_rate={"amount": "200.00", "currency": "CNY"},
            contingency_rate=contingency_rate,
        )
    )

    assert contingency_rate == Decimal("0.12")
    assert pricing.options[0].amount.amount == 2000
    assert pricing.options[0].amount.amount < pricing.options[1].amount.amount
    assert pricing.options[1].amount.amount < pricing.options[2].amount.amount
    assert "PERT" in pricing.options[1].calculation_summary
    assert pricing.policy_version == "1.1.0"


def test_risk_wordiness_does_not_inflate_contingency_within_one_category():
    one_risk = RiskReviewerOutput(
        prompt_version="1.0.0",
        risks=(
            {
                "risk_id": "R-1",
                "category": "technical",
                "severity": "high",
                "cause": "接口未验证",
                "impact": "可能返工",
                "mitigation": "先做验证",
                "requires_human_decision": True,
            },
        ),
    )
    repeated_risks = one_risk.model_copy(
        update={
            "risks": (
                *one_risk.risks,
                one_risk.risks[0].model_copy(update={"risk_id": "R-2"}),
                one_risk.risks[0].model_copy(update={"risk_id": "R-3"}),
            )
        }
    )

    assert calculate_contingency_rate(one_risk) == Decimal("0.10")
    assert calculate_contingency_rate(repeated_risks) == Decimal("0.10")
