import re
from collections.abc import Sequence
from dataclasses import dataclass
from uuid import UUID

from app.agent.contracts import AgentState
from app.agent.ports import IntakeAgent
from app.agent.schemas import (
    ClarificationPlannerOutput,
    ClarificationQuestion,
    ConfirmedFact,
    ProjectBrief,
    RequirementIntakeOutput,
)
from app.agent.workflow_completion import complete_clarification_workflow
from app.domain.enums import (
    AgentRunStatus,
    FactSource,
    QuestionPriority,
    ServiceType,
    WorkflowStep,
)


@dataclass(frozen=True, slots=True)
class QuestionTemplate:
    field: str
    question: str
    reason: str
    priority: QuestionPriority


COMMON_QUESTIONS: tuple[QuestionTemplate, ...] = (
    QuestionTemplate(
        "target_users",
        "谁会使用最终成果，最核心的使用场景是什么？",
        "用户和场景决定功能边界",
        QuestionPriority.CRITICAL,
    ),
    QuestionTemplate(
        "must_have",
        "第一版必须完成的核心功能或交付物有哪些？",
        "先锁定最小可交付闭环",
        QuestionPriority.CRITICAL,
    ),
    QuestionTemplate(
        "acceptance",
        "你准备用什么标准验收这次交付？",
        "验收标准会直接影响任务和工时",
        QuestionPriority.IMPORTANT,
    ),
    QuestionTemplate(
        "deadline",
        "期望在哪个明确日期前完成？",
        "明确日期才能评估排期风险",
        QuestionPriority.IMPORTANT,
    ),
)

SERVICE_QUESTIONS: dict[ServiceType, tuple[QuestionTemplate, ...]] = {
    ServiceType.WEBSITE: (
        QuestionTemplate(
            "content_owner",
            "文案、图片和翻译由哪一方提供？",
            "内容准备会影响工期",
            QuestionPriority.CRITICAL,
        ),
        QuestionTemplate(
            "cms",
            "是否需要可以自行维护内容的后台？",
            "后台会显著改变开发范围",
            QuestionPriority.IMPORTANT,
        ),
        QuestionTemplate(
            "deployment",
            "域名、服务器和上线发布由哪一方负责？",
            "需要明确外部依赖和责任",
            QuestionPriority.IMPORTANT,
        ),
    ),
    ServiceType.AI_APPLICATION: (
        QuestionTemplate(
            "data_source",
            "AI需要使用哪些资料或数据，数量和格式是什么？",
            "数据决定AI方案与成本",
            QuestionPriority.CRITICAL,
        ),
        QuestionTemplate(
            "privacy",
            "资料是否含敏感信息，允许使用外部模型服务吗？",
            "需要先确定隐私与部署边界",
            QuestionPriority.CRITICAL,
        ),
        QuestionTemplate(
            "quality",
            "你会用哪些样例判断AI回答是否合格？",
            "AI功能必须有可执行的质量标准",
            QuestionPriority.IMPORTANT,
        ),
    ),
    ServiceType.ECOMMERCE: (
        QuestionTemplate(
            "credentials",
            "平台账号、认证和支付商户资质是否已经准备好？",
            "交易功能依赖第三方资质",
            QuestionPriority.CRITICAL,
        ),
        QuestionTemplate(
            "operations",
            "商品、库存、订单和退款由谁维护？",
            "运营流程决定后台范围",
            QuestionPriority.CRITICAL,
        ),
        QuestionTemplate(
            "delivery",
            "需要配送、到店自取还是两者都要？",
            "履约方式影响订单流程",
            QuestionPriority.IMPORTANT,
        ),
    ),
    ServiceType.PRESENTATION: (
        QuestionTemplate(
            "materials",
            "现有文案、数据、Logo和品牌模板是否可以立即提供？",
            "素材完整度决定紧急项目可行性",
            QuestionPriority.CRITICAL,
        ),
        QuestionTemplate(
            "format",
            "需要可编辑PPTX、PDF，还是两种格式？",
            "交付格式影响制作方式",
            QuestionPriority.IMPORTANT,
        ),
        QuestionTemplate(
            "revisions",
            "计划包含几轮修改，最晚反馈时间是什么？",
            "修改节奏必须纳入排期",
            QuestionPriority.IMPORTANT,
        ),
    ),
    ServiceType.CONTENT: (
        QuestionTemplate(
            "audience",
            "内容面向哪类人群，账号希望呈现什么语气？",
            "受众决定选题和表达",
            QuestionPriority.CRITICAL,
        ),
        QuestionTemplate(
            "product_facts",
            "有哪些可以验证的产品资料、禁词或合规要求？",
            "避免虚构功效和违规表达",
            QuestionPriority.CRITICAL,
        ),
        QuestionTemplate(
            "publishing",
            "只需要文案，还是包含配图建议和代发布？",
            "明确内容服务边界",
            QuestionPriority.IMPORTANT,
        ),
    ),
    ServiceType.DESIGN: (
        QuestionTemplate(
            "brand",
            "品牌名称、目标客群和希望传达的核心感觉是什么？",
            "品牌信息是设计依据",
            QuestionPriority.CRITICAL,
        ),
        QuestionTemplate(
            "deliverables",
            "需要哪些尺寸、格式和可编辑源文件？",
            "交付清单决定工作范围",
            QuestionPriority.IMPORTANT,
        ),
        QuestionTemplate(
            "revisions",
            "希望包含几套初稿和几轮修改？",
            "控制主观设计项目的返工风险",
            QuestionPriority.IMPORTANT,
        ),
    ),
    ServiceType.DATA_ANALYSIS: (
        QuestionTemplate(
            "data_sample",
            "可以提供脱敏样例、字段说明和大致数据量吗？",
            "需要先判断数据质量和清洗成本",
            QuestionPriority.CRITICAL,
        ),
        QuestionTemplate(
            "metrics",
            "判断表现好坏使用哪些指标和口径？",
            "指标口径决定分析结论",
            QuestionPriority.CRITICAL,
        ),
        QuestionTemplate(
            "privacy",
            "数据是否包含客户、员工或其他敏感信息？",
            "需要确定脱敏与访问方式",
            QuestionPriority.IMPORTANT,
        ),
    ),
    ServiceType.VIDEO: (
        QuestionTemplate(
            "materials",
            "素材总时长、分辨率、画面方向和可用程度如何？",
            "素材决定剪辑工作量",
            QuestionPriority.CRITICAL,
        ),
        QuestionTemplate(
            "creative_scope",
            "是否还需要脚本、配音、动画或封面？",
            "区分基础剪辑和创意制作",
            QuestionPriority.CRITICAL,
        ),
        QuestionTemplate(
            "copyright",
            "音乐、字体和素材的商用授权由谁负责？",
            "避免版权风险",
            QuestionPriority.IMPORTANT,
        ),
    ),
}

PLATFORM_PATTERN = re.compile(r"(小红书|闲鱼|微信小程序|抖音|视频号|网页|网站|App|APP)")


class RuleBasedIntakeAgent(IntakeAgent):
    async def analyze(self, run_id: UUID, project_id: UUID, brief: ProjectBrief) -> AgentState:
        facts = self._extract_facts(brief)
        templates = self._questions_for(brief.service_type)
        questions = tuple(
            ClarificationQuestion(
                question_id=f"Q-{index}",
                field=template.field,
                question=template.question,
                reason=template.reason,
                priority=template.priority,
            )
            for index, template in enumerate(templates, 1)
        )
        intake = RequirementIntakeOutput(
            prompt_version="0.1.0",
            project_type=brief.service_type,
            goals=(self._summarize(brief.client_request),),
            target_users=(),
            confirmed_facts=facts,
            missing_fields=tuple(template.field for template in templates),
            assumptions=(),
        )
        clarification = ClarificationPlannerOutput(
            prompt_version="0.1.0",
            questions=questions,
        )
        return AgentState(
            run_id=run_id,
            project_id=project_id,
            status=AgentRunStatus.WAITING_USER,
            current_step=WorkflowStep.CLARIFICATION,
            confirmed_facts=facts,
            pending_questions=questions,
            retrieved_context=brief.retrieved_context,
            intake=intake,
            clarification=clarification,
            execution_mode="rule_fallback",
        )

    async def submit_answers(self, state: AgentState, answers: dict[str, str]) -> AgentState:
        return complete_clarification_workflow(state, answers)

    def _questions_for(self, service_type: ServiceType) -> Sequence[QuestionTemplate]:
        specialized = SERVICE_QUESTIONS.get(service_type, ())
        return (*specialized, *COMMON_QUESTIONS)[:5]

    def _extract_facts(self, brief: ProjectBrief) -> tuple[ConfirmedFact, ...]:
        facts = [
            ConfirmedFact(
                field="project_name",
                value=brief.name,
                source=FactSource.SYSTEM,
                evidence="用户在项目表单中填写的项目名称",
            ),
            ConfirmedFact(
                field="client_goal",
                value=self._summarize(brief.client_request),
                source=FactSource.CLIENT_REQUEST,
                evidence=brief.client_request,
            )
        ]
        facts.append(
            ConfirmedFact(
                field="hourly_rate",
                value=f"{brief.hourly_rate.amount} {brief.hourly_rate.currency}",
                source=FactSource.SYSTEM,
                evidence="用户在项目表单中填写的接单时薪",
            )
        )
        if brief.service_type is not ServiceType.AUTO_DETECT:
            facts.append(
                ConfirmedFact(
                    field="service_type",
                    value=brief.service_type.value,
                    source=FactSource.SYSTEM,
                    evidence="用户在项目表单中选择的服务类型",
                )
            )
        if brief.budget is not None:
            facts.append(
                ConfirmedFact(
                    field="budget",
                    value=f"{brief.budget.amount} {brief.budget.currency}",
                    source=FactSource.CLIENT_REQUEST,
                    evidence="用户在项目表单中填写的预算",
                )
            )
        if brief.deadline:
            facts.append(
                ConfirmedFact(
                    field="deadline",
                    value=brief.deadline,
                    source=FactSource.CLIENT_REQUEST,
                    evidence="用户在项目表单中填写的期限",
                )
            )
        platforms = sorted(set(PLATFORM_PATTERN.findall(brief.client_request)))
        if platforms:
            facts.append(
                ConfirmedFact(
                    field="platforms",
                    value="、".join(platforms),
                    source=FactSource.CLIENT_REQUEST,
                    evidence="客户原话中明确出现的平台",
                )
            )
        return tuple(facts)

    @staticmethod
    def _summarize(client_request: str) -> str:
        normalized = " ".join(client_request.split())
        return normalized if len(normalized) <= 96 else f"{normalized[:96]}…"
