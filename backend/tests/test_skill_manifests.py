import importlib
import re
from pathlib import Path

from app.agent.workflow import SKILL_NAMES
from pydantic import BaseModel

SKILLS_ROOT = Path(__file__).resolve().parents[1] / "app" / "agent" / "skills"
CASES_ROOT = Path(__file__).resolve().parents[2] / "evals" / "cases"


def _frontmatter_value(content: str, key: str) -> str:
    match = re.search(rf"^{key}:\s*(.+)$", content, flags=re.MULTILINE)
    assert match, f"missing manifest field: {key}"
    return match.group(1).strip()


def _resolve_model(dotted_path: str) -> type[BaseModel]:
    module_name, class_name = dotted_path.rsplit(".", 1)
    model = getattr(importlib.import_module(module_name), class_name)
    assert issubclass(model, BaseModel)
    return model


def test_each_registered_skill_has_a_versioned_manifest():
    for skill_name in SKILL_NAMES:
        manifest = SKILLS_ROOT / skill_name / "SKILL.md"
        assert manifest.exists(), f"missing manifest: {skill_name}"
        content = manifest.read_text(encoding="utf-8")
        assert f"name: {skill_name}" in content
        assert "version:" in content
        assert "triggers:" in content
        assert "do_not_use_when:" in content
        assert "input_schema:" in content
        assert "output_schema:" in content
        assert "allowed_tools:" in content
        assert "max_auto_repairs: 1" in content
        assert "fallback:" in content
        assert "human_checkpoint:" in content
        assert "evaluation_cases:" in content
        assert "## 触发条件" in content
        assert "## 禁用条件" in content
        assert "## 输入" in content
        assert "## 输出" in content
        assert "## Guardrail" in content
        assert "## 失败与降级" in content
        assert "## 评测" in content


def test_manifest_schema_references_resolve_to_strict_pydantic_models():
    for skill_name in SKILL_NAMES:
        content = (SKILLS_ROOT / skill_name / "SKILL.md").read_text(encoding="utf-8")
        for key in ("input_schema", "output_schema"):
            model = _resolve_model(_frontmatter_value(content, key))
            assert model.model_json_schema()["additionalProperties"] is False


def test_manifest_evaluation_references_exist():
    available_ids = {
        match.group(1)
        for path in CASES_ROOT.glob("*.json")
        if (match := re.search(r'"case_id":\s*"(EVAL-\d{3})"', path.read_text(encoding="utf-8")))
    }

    for skill_name in SKILL_NAMES:
        content = (SKILLS_ROOT / skill_name / "SKILL.md").read_text(encoding="utf-8")
        referenced_ids = set(
            re.findall(r"EVAL-\d{3}", _frontmatter_value(content, "evaluation_cases"))
        )
        assert referenced_ids
        assert referenced_ids <= available_ids
