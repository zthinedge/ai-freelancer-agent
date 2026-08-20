from decimal import ROUND_HALF_UP, Decimal

from app.agent.schemas import (
    Money,
    PricingToolInput,
    PricingToolOutput,
    QuoteOption,
    RiskReviewerOutput,
)
from app.domain.enums import QuoteTier, RiskSeverity

POLICY_VERSION = "1.1.0"
_HALF_HOUR = Decimal("0.5")


def calculate_contingency_rate(
    risk_review: RiskReviewerOutput,
    uncertainty_count: int = 0,
) -> Decimal:
    severity_rates = {
        RiskSeverity.LOW: Decimal("0.01"),
        RiskSeverity.MEDIUM: Decimal("0.03"),
        RiskSeverity.HIGH: Decimal("0.05"),
    }
    # The model may describe the same risk several times. Only the highest severity
    # in each stable category contributes, so verbosity cannot inflate the quote.
    category_rates: dict[str, Decimal] = {}
    for risk in risk_review.risks:
        category_rates[risk.category] = max(
            category_rates.get(risk.category, Decimal("0")),
            severity_rates[risk.severity],
        )
    risk_rate = sum(category_rates.values(), Decimal("0.05"))
    uncertainty_rate = min(Decimal(uncertainty_count) * Decimal("0.01"), Decimal("0.03"))
    return min(risk_rate + uncertainty_rate, Decimal("0.25"))


def calculate_pricing(arguments: PricingToolInput) -> PricingToolOutput:
    """根据已验证工时执行纯函数报价，模型无权填写或修改金额。"""
    if arguments.max_hours < arguments.min_hours:
        raise ValueError("max_hours must be greater than or equal to min_hours")

    min_hours = _round_half(arguments.min_hours)
    max_hours = _round_half(arguments.max_hours)
    geometric_mean = (min_hours * max_hours).sqrt()
    pert_hours = _round_half((min_hours + Decimal("4") * geometric_mean + max_hours) / 6)
    standard_multiplier = Decimal("1") + arguments.contingency_rate
    # max_hours already includes task-level known risks and integration buffer.
    # Premium adds only a fixed delivery-assurance margin to avoid charging risk twice.
    premium_multiplier = Decimal("1.10")

    return PricingToolOutput(
        policy_version=POLICY_VERSION,
        options=(
            _option(
                QuoteTier.BASIC,
                min_hours,
                arguments.hourly_rate.amount,
                Decimal("1.00"),
                "乐观工时边界（相同交付范围，不含风险准备金）",
            ),
            _option(
                QuoteTier.STANDARD,
                pert_hours,
                arguments.hourly_rate.amount,
                standard_multiplier,
                f"PERT期望工时并计入{arguments.contingency_rate:.0%}风险准备金",
            ),
            _option(
                QuoteTier.PREMIUM,
                max_hours,
                arguments.hourly_rate.amount,
                premium_multiplier,
                "保守工时边界，按工时上界计入固定交付保障",
            ),
        ),
    )


def _option(
    tier: QuoteTier,
    hours: Decimal,
    hourly_rate: Decimal,
    multiplier: Decimal,
    label: str,
) -> QuoteOption:
    amount = (hours * hourly_rate * multiplier).quantize(Decimal("0.01"), ROUND_HALF_UP)
    return QuoteOption(
        tier=tier,
        amount=Money(amount=amount),
        included_hours=hours,
        calculation_summary=(
            f"{label}：{hours}小时 × ¥{hourly_rate}/小时 × {multiplier}系数"
        ),
    )


def _round_half(value: Decimal) -> Decimal:
    return (value / _HALF_HOUR).quantize(Decimal("1"), ROUND_HALF_UP) * _HALF_HOUR
