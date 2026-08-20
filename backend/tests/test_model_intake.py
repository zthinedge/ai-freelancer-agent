from collections.abc import Sequence
from uuid import uuid4

import pytest
from app.agent.contracts import ModelRequest, ModelResponse
from app.agent.schemas import ProjectBrief
from app.infrastructure.ai.model_intake import ModelBackedIntakeAgent
from app.infrastructure.ai.openai_compatible import ModelGatewayError
from app.infrastructure.ai.rule_based_intake import RuleBasedIntakeAgent


class SequenceGateway:
    def __init__(self, responses: Sequence[ModelResponse]) -> None:
        self._responses = list(responses)

    async def complete(self, request: ModelRequest) -> ModelResponse:
        return self._responses.pop(0)


class FailingGateway:
    async def complete(self, request: ModelRequest) -> ModelResponse:
        raise ModelGatewayError("simulated failure")


def brief() -> ProjectBrief:
    return ProjectBrief(
        name="企业官网",
        client_request="需要制作中英文企业官网和移动端页面，希望三周内上线。",
        service_type="website",
        budget={"amount": "12000.00", "currency": "CNY"},
        deadline="三周内",
        hourly_rate={"amount": "150.00", "currency": "CNY"},
    )


@pytest.mark.anyio
async def test_model_agent_runs_intake_and_clarification_with_structured_outputs():
    intake = ModelResponse(
        model="deepseek-v4-flash",
        input_tokens=120,
        output_tokens=80,
        latency_ms=300,
        content={
            "project_type": "website",
            "goals": ["制作中英文企业官网"],
            "target_users": ["企业客户"],
            "confirmed_facts": [
                {
                    "field": "deadline",
                    "value": "三周内",
                    "source": "client_request",
                    "evidence": "希望三周内上线",
                }
            ],
            "missing_fields": ["content_owner", "cms", "acceptance"],
            "assumptions": [],
        },
    )
    clarification = ModelResponse(
        model="deepseek-v4-flash",
        input_tokens=90,
        output_tokens=60,
        latency_ms=240,
        content={
            "questions": [
                {
                    "question_id": "Q-1",
                    "field": "content_owner",
                    "question": "网站内容由谁提供？",
                    "reason": "影响内容准备工时",
                    "priority": "critical",
                },
                {
                    "question_id": "Q-2",
                    "field": "cms",
                    "question": "是否需要内容管理后台？",
                    "reason": "影响开发范围",
                    "priority": "important",
                },
                {
                    "question_id": "Q-3",
                    "field": "acceptance",
                    "question": "使用什么标准验收？",
                    "reason": "需要明确完成条件",
                    "priority": "important",
                },
            ],
            "requires_human_input": True,
        },
    )
    agent = ModelBackedIntakeAgent(
        SequenceGateway([intake, clarification]),
        RuleBasedIntakeAgent(),
        "deepseek-v4-flash",
    )

    state = await agent.analyze(uuid4(), uuid4(), brief())

    assert state.execution_mode == "model"
    assert state.model_name == "deepseek-v4-flash"
    assert state.intake is not None
    assert state.intake.prompt_version == "1.0.0"
    assert len(state.pending_questions) == 3
    assert state.fallback_reason is None
    assert state.model_input_tokens == 210
    assert state.model_output_tokens == 140
    assert state.model_latency_ms == 540


@pytest.mark.anyio
async def test_model_agent_falls_back_without_exposing_provider_error():
    agent = ModelBackedIntakeAgent(
        FailingGateway(),
        RuleBasedIntakeAgent(),
        "deepseek-v4-flash",
    )

    state = await agent.analyze(uuid4(), uuid4(), brief())

    assert state.execution_mode == "rule_fallback"
    assert state.model_name == "deepseek-v4-flash"
    assert state.fallback_reason == "模型输出不可用，已自动切换到规则模式"
    assert 3 <= len(state.pending_questions) <= 6


@pytest.mark.anyio
async def test_model_agent_stops_without_an_approvable_quote_when_downstream_model_fails():
    fallback = RuleBasedIntakeAgent()
    state = await fallback.analyze(uuid4(), uuid4(), brief())
    agent = ModelBackedIntakeAgent(
        FailingGateway(),
        fallback,
        "deepseek-v4-flash",
    )

    updated = await agent.submit_answers(
        state,
        {question.question_id: "已确认" for question in state.pending_questions},
    )

    assert updated.status == "failed"
    assert updated.current_step == "scope_designer"
    assert updated.clarification_approved is True
    assert updated.quote_approved is False
    assert updated.pricing is None
    assert updated.proposal is None
    assert updated.execution_mode == "model"
    assert updated.fallback_reason == (
        "scope_designer 调用或校验失败，已停止自动报价；请稍后新建分析重试"
    )


@pytest.mark.anyio
async def test_model_agent_orchestrates_analysis_skills_before_deterministic_pricing():
    responses = [
        ModelResponse(
            model="deepseek-v4-flash",
            content={
                "project_type": "website",
                "goals": ["制作企业官网"],
                "target_users": ["潜在客户"],
                "confirmed_facts": [
                    {
                        "field": "pages",
                        "value": "5个页面",
                        "source": "client_request",
                        "evidence": "首页、产品、案例、关于和联系",
                    }
                ],
                "missing_fields": ["content_owner", "cms", "acceptance"],
                "assumptions": [],
            },
        ),
        ModelResponse(
            model="deepseek-v4-flash",
            content={
                "questions": [
                    {
                        "question_id": "Q-1",
                        "field": "content_owner",
                        "question": "素材由谁提供？",
                        "reason": "影响内容工时",
                        "priority": "critical",
                    },
                    {
                        "question_id": "Q-2",
                        "field": "cms",
                        "question": "是否需要后台？",
                        "reason": "影响开发范围",
                        "priority": "important",
                    },
                    {
                        "question_id": "Q-3",
                        "field": "acceptance",
                        "question": "如何验收？",
                        "reason": "明确完成标准",
                        "priority": "important",
                    },
                ],
                "requires_human_input": True,
            },
        ),
        ModelResponse(
            model="deepseek-v4-flash",
            content={
                "must": [
                    {
                        "item_id": "S-1",
                        "title": "五页响应式官网",
                        "description": "完成五个已确认页面和联系表单",
                        "rationale": "客户明确页面数量与移动端要求",
                    }
                ],
                "should": [],
                "could": [],
                "wont": [
                    {
                        "item_id": "W-1",
                        "title": "内容后台",
                        "description": "本期不开发CMS",
                        "rationale": "澄清答案确认不需要",
                    },
                    {
                        "item_id": "W-2",
                        "title": "第三方费用",
                        "description": "域名和服务器另计",
                        "rationale": "费用依赖第三方",
                    },
                ],
                "blocked_by_missing_information": False,
            },
        ),
        ModelResponse(
            model="deepseek-v4-flash",
            content={
                "tasks": [
                    {
                        "task_id": "T-1",
                        "title": "信息架构与视觉规范",
                        "description": "确认五页结构和视觉组件",
                        "dependencies": [],
                        "min_hours": "4.0",
                        "max_hours": "6.0",
                        "estimate_basis": "5页结构和一套视觉规范",
                        "acceptance_criteria": ["页面结构经确认"],
                    },
                    {
                        "task_id": "T-2",
                        "title": "五页响应式开发",
                        "description": "实现五页和联系表单",
                        "dependencies": ["T-1"],
                        "min_hours": "12.0",
                        "max_hours": "22.0",
                        "estimate_basis": "5页、三个断点和一个表单",
                        "acceptance_criteria": ["桌面和手机端通过验收"],
                    },
                    {
                        "task_id": "T-3",
                        "title": "联调、测试与发布",
                        "description": "完成兼容性测试和上线",
                        "dependencies": ["T-2"],
                        "min_hours": "4.0",
                        "max_hours": "8.0",
                        "estimate_basis": "主流浏览器测试与一次发布",
                        "acceptance_criteria": ["线上页面和表单可用"],
                    },
                ],
                "buffer_hours": "4.0",
                "uncertainty_notes": ["素材到位时间可能影响排期"],
            },
        ),
        ModelResponse(
            model="deepseek-v4-flash",
            content={
                "risks": [
                    {
                        "risk_id": "R-1",
                        "category": "schedule",
                        "severity": "medium",
                        "cause": "素材可能延迟",
                        "impact": "压缩开发和测试时间",
                        "mitigation": "约定素材截止时间",
                        "requires_human_decision": True,
                    },
                    {
                        "risk_id": "R-2",
                        "category": "technical",
                        "severity": "high",
                        "cause": "表单邮件服务未确定",
                        "impact": "联系表单可能无法上线",
                        "mitigation": "开发前确认邮件服务和账号",
                        "requires_human_decision": True,
                    },
                ],
                "human_decisions": ["确认邮件服务"],
            },
        ),
        ModelResponse(
            model="deepseek-v4-flash",
            content={
                "project_summary": "五页响应式企业官网报价草案",
                "deliverables": ["五页响应式官网", "联系表单"],
                "exclusions": ["内容后台", "第三方费用"],
                "acceptance_criteria": ["桌面和手机端通过验收"],
                "disclaimers": [
                    "人工确认前不构成正式承诺",
                    "范围变化需要重新估算",
                ],
            },
        ),
    ]
    agent = ModelBackedIntakeAgent(
        SequenceGateway(responses),
        RuleBasedIntakeAgent(),
        "deepseek-v4-flash",
    )
    state = await agent.analyze(uuid4(), uuid4(), brief())

    updated = await agent.submit_answers(
        state,
        {"Q-1": "客户提供", "Q-2": "不需要", "Q-3": "多端页面和表单可用"},
    )

    assert updated.execution_mode == "model"
    assert updated.status == "waiting_approval"
    assert updated.scope is not None
    assert updated.estimate is not None
    assert len(updated.estimate.tasks) == 3
    assert updated.risk_review is not None
    assert updated.pricing is not None
    assert [option.amount.amount for option in updated.pricing.options] == [
        3000,
        4959,
        6600,
    ]
    assert updated.proposal is not None
    assert updated.proposal.quote_options == updated.pricing.options
