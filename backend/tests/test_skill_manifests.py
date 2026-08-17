from pathlib import Path

from app.agent.workflow import SKILL_NAMES

SKILLS_ROOT = Path(__file__).resolve().parents[1] / "app" / "agent" / "skills"


def test_each_registered_skill_has_a_versioned_manifest():
    for skill_name in SKILL_NAMES:
        manifest = SKILLS_ROOT / skill_name / "SKILL.md"
        assert manifest.exists(), f"missing manifest: {skill_name}"
        content = manifest.read_text(encoding="utf-8")
        assert f"name: {skill_name}" in content
        assert "version:" in content
        assert "## 输入" in content
        assert "## 输出" in content
        assert "## Guardrail" in content
        assert "## 评测" in content
