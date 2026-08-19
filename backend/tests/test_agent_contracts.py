from decimal import Decimal

import pytest
from app.agent.schemas import (
    ClarificationPlannerOutput,
    EstimatedTask,
    Money,
    PricingToolOutput,
    ProjectBrief,
    QuoteOption,
)
from app.domain.enums import QuestionPriority, QuoteTier
from pydantic import ValidationError


def test_contracts_reject_unknown_fields():
    with pytest.raises(ValidationError):
        Money.model_validate({"amount": "100.00", "currency": "CNY", "unknown": True})

    assert Money.model_json_schema()["additionalProperties"] is False


def test_money_serializes_decimal_as_json_string():
    money = Money(amount=Decimal("100.50"))

    assert money.model_dump(mode="json") == {"amount": "100.50", "currency": "CNY"}


def test_project_hourly_rate_must_be_positive():
    with pytest.raises(ValidationError):
        ProjectBrief(
            name="官网项目",
            client_request="需要制作一个支持手机访问的企业官方网站。",
            hourly_rate={"amount": "0.00", "currency": "CNY"},
        )


def test_clarification_requires_between_three_and_six_questions():
    question = {
        "question_id": "Q-1",
        "field": "goal",
        "question": "这个项目要解决什么核心问题？",
        "reason": "目标决定最小范围",
        "priority": QuestionPriority.CRITICAL,
    }

    with pytest.raises(ValidationError):
        ClarificationPlannerOutput(prompt_version="0.1.0", questions=(question, question))


def test_estimated_task_enforces_half_hour_units_and_ordered_range():
    common = {
        "task_id": "T-1",
        "title": "实现首页",
        "description": "完成响应式首页",
        "dependencies": (),
        "estimate_basis": "包含开发与自测",
        "acceptance_criteria": ("移动端与桌面端可访问",),
    }

    with pytest.raises(ValidationError):
        EstimatedTask(**common, min_hours="1.2", max_hours="2.0")

    with pytest.raises(ValidationError):
        EstimatedTask(**common, min_hours="3.0", max_hours="2.0")


def test_pricing_output_requires_each_quote_tier_once():
    def option(tier: QuoteTier, amount: str) -> QuoteOption:
        return QuoteOption(
            tier=tier,
            amount=Money(amount=Decimal(amount)),
            included_hours=Decimal("10.0"),
            calculation_summary="确定性报价策略结果",
        )

    valid = PricingToolOutput(
        policy_version="0.1.0",
        options=(
            option(QuoteTier.BASIC, "1000.00"),
            option(QuoteTier.STANDARD, "1500.00"),
            option(QuoteTier.PREMIUM, "2000.00"),
        ),
    )
    assert len(valid.options) == 3

    with pytest.raises(ValidationError):
        PricingToolOutput(
            policy_version="0.1.0",
            options=(
                option(QuoteTier.BASIC, "1000.00"),
                option(QuoteTier.BASIC, "1500.00"),
                option(QuoteTier.PREMIUM, "2000.00"),
            ),
        )
