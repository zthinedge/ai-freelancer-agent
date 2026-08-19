from pathlib import Path

from app.agent.evaluation import EvaluationCase
from app.domain.enums import ServiceType, WorkflowStep

CASES_ROOT = Path(__file__).resolve().parents[2] / "evals" / "cases"


def _load_cases() -> list[EvaluationCase]:
    return [
        EvaluationCase.model_validate_json(path.read_text(encoding="utf-8"))
        for path in sorted(CASES_ROOT.glob("*.json"))
    ]


def test_baseline_contains_exactly_ten_unique_versioned_cases():
    cases = _load_cases()

    assert len(cases) == 10
    assert {case.case_id for case in cases} == {f"EVAL-{index:03d}" for index in range(1, 11)}
    assert all(case.schema_version == "1.0.0" for case in cases)
    assert all(case.case_version == "1.0.0" for case in cases)


def test_cases_cover_all_mvp_service_types_and_edge_classes():
    cases = _load_cases()
    service_types = {case.input.service_type for case in cases}
    tags = {tag for case in cases for tag in case.tags}

    assert {
        ServiceType.WEBSITE,
        ServiceType.AI_APPLICATION,
        ServiceType.ECOMMERCE,
        ServiceType.PRESENTATION,
        ServiceType.CONTENT,
        ServiceType.DESIGN,
        ServiceType.DATA_ANALYSIS,
        ServiceType.VIDEO,
    }.issubset(service_types)
    assert {"underspecified", "prompt_injection", "privacy", "external_dependency"}.issubset(tags)


def test_every_case_defines_facts_questions_forbidden_behavior_and_route():
    for case in _load_cases():
        assert case.expected_known_facts
        assert case.expected_missing_fields
        assert case.required_questions
        assert case.forbidden_behaviors
        assert case.pass_criteria.machine
        assert case.pass_criteria.human
        assert case.expected_route.stop_after is WorkflowStep.CLARIFICATION
        assert case.expected_route.requires_human_input is True


def test_adversarial_case_protects_prompt_tool_and_commercial_boundaries():
    adversarial = next(case for case in _load_cases() if case.case_id == "EVAL-010")
    forbidden = " ".join(adversarial.forbidden_behaviors)

    assert "系统Prompt" in forbidden
    assert "发送消息Tool" in forbidden
    assert "保证成交" in forbidden
    assert adversarial.pass_criteria.minimum_score == 1
