"""Границы нового backend."""

import ast
from pathlib import Path

from src.audit.schemas.audit import AuditResponse
from src.core.models import Base
from src.expertise.schemas.expertise import ExpertiseResponse

SOURCE_ROOT = Path(__file__).resolve().parents[2] / "src"


def test_source_has_no_legacy_imports() -> None:
    """Не зависеть от удаляемых модулей."""

    for path in SOURCE_ROOT.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))

        for node in ast.walk(tree):
            modules = []

            if isinstance(node, ast.ImportFrom) and node.module:
                modules.append(node.module)
            elif isinstance(node, ast.Import):
                modules.extend(alias.name for alias in node.names)

            for module in modules:
                assert module != "app" and not module.startswith("app."), path
                assert not module.startswith("src.service_requests"), path


def test_usecases_do_not_import_other_usecases() -> None:
    """Не соединять сценарии скрытой цепочкой."""

    for path in SOURCE_ROOT.glob("**/usecases/*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                assert ".usecases." not in node.module, path
            elif isinstance(node, ast.Import):
                assert all(".usecases." not in alias.name for alias in node.names), path


def test_repositories_do_not_commit() -> None:
    """Оставить завершение транзакции сценарию."""

    for path in SOURCE_ROOT.glob("**/repositories/*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                assert node.func.attr != "commit", path


def test_audit_and_expertise_have_independent_contracts() -> None:
    """Не смешивать две услуги в общей модели и ответе."""

    assert "service_requests" not in Base.metadata.tables
    assert "request_id" not in Base.metadata.tables["audits"].columns
    assert "request_id" not in Base.metadata.tables["expertises"].columns
    assert "expert_id" not in AuditResponse.model_fields
    assert "object_code" not in AuditResponse.model_fields
    assert "lead_id" not in ExpertiseResponse.model_fields
    assert "audit_plan" not in ExpertiseResponse.model_fields
