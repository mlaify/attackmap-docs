"""Check that docs/analyzers.md stays in step with `attackmap modules --json`.

Every installed analyzer module must have a row in one of the page's module
tables, and the row's Priority, Runs (default / opt-in) and Experimental
columns must match the module's metadata.

Run it against core with all official plugins installed, so every plugin is
checked:

    pip install pytest "attackmap[all] @ git+https://github.com/mlaify/AttackMap.git"
    pytest tests/test_analyzers_table.py

Skipped when AttackMap isn't importable.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("attackmap")

ANALYZERS_PAGE = Path(__file__).resolve().parent.parent / "docs" / "analyzers.md"
OFFICIAL_PLUGIN_COUNT = 15


def _attackmap_cli() -> str:
    """The `attackmap` script installed next to this interpreter, else on PATH."""
    beside = Path(sys.executable).with_name("attackmap")
    if beside.exists():
        return str(beside)
    found = shutil.which("attackmap")
    if found is None:
        pytest.skip("attackmap CLI not found")
    return found


def _modules() -> list[dict]:
    proc = subprocess.run(
        [_attackmap_cli(), "modules", "--json"],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(proc.stdout)


def _cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _table_rows() -> dict[str, dict[str, str]]:
    """Rows of every Markdown table whose first column is "Module", keyed by
    the module name in that column's backticks."""
    rows: dict[str, dict[str, str]] = {}
    header: list[str] | None = None
    for line in ANALYZERS_PAGE.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            header = None
            continue
        cells = _cells(line)
        if header is None:
            header = cells if cells[0] == "Module" else []
            continue
        if not header or set(line) <= set("|-: "):
            continue
        match = re.fullmatch(r"`([^`]+)`", cells[0])
        if match:
            rows[match.group(1)] = dict(zip(header, cells))
    return rows


@pytest.fixture(scope="module")
def modules() -> list[dict]:
    return _modules()


@pytest.fixture(scope="module")
def rows() -> dict[str, dict[str, str]]:
    return _table_rows()


def test_every_module_has_a_row(modules: list[dict], rows: dict[str, dict[str, str]]) -> None:
    missing = sorted(m["name"] for m in modules if m["name"] not in rows)
    assert not missing, f"modules missing from docs/analyzers.md tables: {missing}"


def test_runs_column_matches_enabled_by_default(
    modules: list[dict], rows: dict[str, dict[str, str]]
) -> None:
    wrong = []
    for module in modules:
        row = rows.get(module["name"])
        if row is None:
            continue
        runs = row["Runs"]
        if module["enabled_by_default"]:
            ok = runs == "default"
        else:
            ok = runs == f"opt-in (`-m {module['name']}`)"
        if not ok:
            wrong.append((module["name"], module["enabled_by_default"], runs))
    assert not wrong, f"Runs column disagrees with enabled_by_default: {wrong}"


def test_priority_and_experimental_columns_match(
    modules: list[dict], rows: dict[str, dict[str, str]]
) -> None:
    wrong = []
    for module in modules:
        row = rows.get(module["name"])
        if row is None:
            continue
        expected = (str(module["priority"]), "yes" if module["experimental"] else "no")
        actual = (row["Priority"], row["Experimental"])
        if actual != expected:
            wrong.append((module["name"], expected, actual))
    assert not wrong, f"(priority, experimental) disagree with metadata: {wrong}"


def test_page_lists_all_official_plugins(rows: dict[str, dict[str, str]]) -> None:
    OFFICIAL_PLUGINS = pytest.importorskip("attackmap.plugins_lock").OFFICIAL_PLUGINS

    assert len(OFFICIAL_PLUGINS) == OFFICIAL_PLUGIN_COUNT
    page = ANALYZERS_PAGE.read_text(encoding="utf-8")
    for entry in OFFICIAL_PLUGINS:
        assert f"https://github.com/mlaify/{entry['repo']}" in page, entry["repo"]
    plugin_rows = [row for row in rows.values() if "Package / repo" in row]
    assert len(plugin_rows) == OFFICIAL_PLUGIN_COUNT
