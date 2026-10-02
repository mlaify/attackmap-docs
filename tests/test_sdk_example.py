"""Check that the Analyzer SDK page's example plugin works against core.

Extracts the ```python title="my_package/analyzer.py"``` block from
docs/sdk.md, loads it as a module and runs it the way core does. Also checks
that the page's metadata field table and signal model list stay in step with
the installed `attackmap.sdk`.

Needs AttackMap core in the environment:

    pip install pytest "attackmap @ git+https://github.com/mlaify/AttackMap.git"
    pytest tests/
"""

from __future__ import annotations

import re
import types
from pathlib import Path

import pytest

attackmap = pytest.importorskip("attackmap")

from attackmap import sdk  # noqa: E402
from attackmap.analyzers import _is_valid_analyzer, analyze_repository  # noqa: E402

SDK_PAGE = Path(__file__).resolve().parent.parent / "docs" / "sdk.md"
EXAMPLE_TITLE = "my_package/analyzer.py"


def _page() -> str:
    return SDK_PAGE.read_text(encoding="utf-8")


def _example_source() -> str:
    pattern = re.compile(
        r'^```python title="' + re.escape(EXAMPLE_TITLE) + r'"\n(.*?)^```$',
        re.DOTALL | re.MULTILINE,
    )
    blocks = pattern.findall(_page())
    assert len(blocks) == 1, f"expected one example block titled {EXAMPLE_TITLE!r}"
    return blocks[0]


@pytest.fixture(scope="module")
def analyzer_cls():
    module = types.ModuleType("my_package.analyzer")
    exec(compile(_example_source(), EXAMPLE_TITLE, "exec"), module.__dict__)
    return module.FlaskLiteAnalyzer


@pytest.fixture
def flask_repo(tmp_path: Path) -> Path:
    (tmp_path / "requirements.txt").write_text("Flask==3.0.0\n")
    (tmp_path / "app.py").write_text(
        "from flask import Flask\n"
        "app = Flask(__name__)\n"
        "\n"
        "@app.route('/items', methods=['GET', 'POST'])\n"
        "def items():\n"
        "    return 'ok'\n"
        "\n"
        '@app.route("/health")\n'
        "def health():\n"
        "    return 'ok'\n"
    )
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_app.py").write_text("@app.route('/only-in-tests')\ndef t():\n    pass\n")
    return tmp_path


def test_example_is_a_valid_analyzer(analyzer_cls):
    analyzer = analyzer_cls()
    assert _is_valid_analyzer(analyzer)
    assert analyzer.name == analyzer.metadata.name == "flask-lite"


def test_example_detects_and_analyzes(analyzer_cls, flask_repo: Path, tmp_path_factory):
    analyzer = analyzer_cls()
    assert analyzer.detect(flask_repo) is True
    assert analyzer.detect(tmp_path_factory.mktemp("empty")) is False

    result = analyzer.analyze(flask_repo)
    assert isinstance(result, sdk.ScanResult)
    routes = {(r.method, r.path, r.file, r.line) for r in result.routes}
    assert routes == {
        ("GET", "/items", "app.py", 4),
        ("POST", "/items", "app.py", 4),
        ("GET", "/health", "app.py", 8),
    }
    assert result.framework_hints and all(h.hint == "flask" for h in result.framework_hints)


def test_example_runs_through_core(analyzer_cls, flask_repo: Path):
    merged = analyze_repository(flask_repo, analyzers=[analyzer_cls()], strict=True)
    assert isinstance(merged, sdk.AnalyzerResult)
    assert merged.analyzer_errors == []
    flask_routes = [r for r in merged.routes if r.source_analyzer == "flask-lite"]
    assert {(r.method, r.path) for r in flask_routes} == {
        ("GET", "/items"),
        ("POST", "/items"),
        ("GET", "/health"),
    }


def test_analyzer_result_is_scan_result():
    assert sdk.AnalyzerResult is sdk.ScanResult


def test_metadata_table_lists_every_field():
    page = _page()
    for field in sdk.AnalyzerMetadata.model_fields:
        assert f"| `{field}` |" in page, f"AnalyzerMetadata.{field} missing from the field table"


def test_every_exported_signal_model_is_documented():
    page = _page()
    models = [
        name
        for name in sdk.__all__
        if name.endswith(("Hint", "Call")) or name == "Route"
    ]
    assert len(models) == 11
    for name in models:
        assert f"`{name}`" in page, f"{name} missing from the signal model table"
