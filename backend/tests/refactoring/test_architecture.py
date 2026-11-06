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


def test_repositories_do_not_depend_on_http() -> None:
    """Репозитории не зависят от сайта, админки и HTTP."""

    for path in SOURCE_ROOT.glob("**/repositories/*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                assert ".site." not in node.module, path
                assert ".admin." not in node.module, path
                assert not node.module.startswith("fastapi"), path
                assert ".schemas." not in node.module, path


def test_site_and_admin_do_not_import_each_other() -> None:
    """Пользовательские и административные сценарии независимы."""

    for path in SOURCE_ROOT.rglob("*.py"):
        if "site" not in path.parts and "admin" not in path.parts:
            continue

        forbidden = ".admin." if "site" in path.parts else ".site."
        tree = ast.parse(path.read_text(encoding="utf-8"))

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                assert forbidden not in node.module, path


def test_schemas_have_explicit_fields_and_validate_data() -> None:
    """Запросы и ответы не наследуют другие схемы и не обходят валидацию."""

    for path in SOURCE_ROOT.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                assert node.func.attr != "model_construct", path

            if "schemas" in path.parts and isinstance(node, ast.ClassDef):
                assert [ast.unparse(base) for base in node.bases] == ["BaseModel"], path


def test_http_modules_are_in_their_folders() -> None:
    """Роуты и зависимости имеют одинаковое расположение."""

    for path in SOURCE_ROOT.rglob("*.py"):
        assert not path.name.endswith("_router.py"), path
        assert not path.name.endswith("_dependencies.py"), path
        assert path.name != "dependencies.py", path

        if path == SOURCE_ROOT / "router.py":
            continue

        tree = ast.parse(path.read_text(encoding="utf-8"))

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == "APIRouter":
                    assert path.parent.name == "routers", path


def test_request_and_response_schemas_are_together() -> None:
    """Запрос и JSON-ответ сценария находятся в одном модуле."""

    for path in SOURCE_ROOT.glob("**/routers/*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = {
            alias.asname or alias.name: node.module
            for node in tree.body
            if isinstance(node, ast.ImportFrom)
            for alias in node.names
        }

        for function in tree.body:
            if not isinstance(function, ast.AsyncFunctionDef) or function.returns is None:
                continue

            requests = [
                node.id
                for argument in function.args.args + function.args.kwonlyargs
                if argument.annotation is not None
                for node in ast.walk(argument.annotation)
                if isinstance(node, ast.Name) and node.id.endswith("Request")
            ]
            responses = [
                node.id
                for node in ast.walk(function.returns)
                if isinstance(node, ast.Name) and node.id.endswith("Response")
            ]

            for request in requests:
                for response in responses:
                    assert imports[request] == imports[response], (path, function.name)


def test_audit_and_expertise_have_independent_contracts() -> None:
    """Не смешивать две услуги в общей модели и ответе."""

    assert "service_requests" not in Base.metadata.tables
    assert "request_id" not in Base.metadata.tables["audits"].columns
    assert "request_id" not in Base.metadata.tables["expertises"].columns
    assert "expert_id" not in AuditResponse.model_fields
    assert "object_code" not in AuditResponse.model_fields
    assert "lead_id" not in ExpertiseResponse.model_fields
    assert "audit_plan" not in ExpertiseResponse.model_fields
