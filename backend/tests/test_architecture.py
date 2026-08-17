import ast
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[1] / "app"

FORBIDDEN_IMPORTS = {
    "domain": ("app.application", "app.agent", "app.infrastructure", "app.presentation"),
    "application": ("app.infrastructure", "app.presentation", "app.bootstrap"),
    "agent": ("app.infrastructure", "app.presentation", "app.bootstrap"),
}


def _absolute_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            imports.add(node.module)
    return imports


def test_inner_layers_do_not_import_outer_layers():
    violations: list[str] = []
    for layer, forbidden_prefixes in FORBIDDEN_IMPORTS.items():
        for path in (APP_ROOT / layer).rglob("*.py"):
            for imported in _absolute_imports(path):
                if imported.startswith(forbidden_prefixes):
                    violations.append(f"{path.relative_to(APP_ROOT)} -> {imported}")

    assert violations == []


def test_http_layer_does_not_import_infrastructure_directly():
    violations: list[str] = []
    for path in (APP_ROOT / "presentation").rglob("*.py"):
        for imported in _absolute_imports(path):
            if imported.startswith("app.infrastructure"):
                violations.append(f"{path.relative_to(APP_ROOT)} -> {imported}")

    assert violations == []
