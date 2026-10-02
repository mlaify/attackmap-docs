"""docs/cli.md stays in sync with the real CLI (docs#14).

For `analyze`, `suggest` and `bench`, every long option the CLI accepts must
appear in that command's section, every option the section names must exist,
documented `{a,b,c}` choices must match what the CLI accepts, and a documented
`default \`X\`` must match the real default. Run against the installed
`attackmap` (CI installs AttackMap main).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

typer = pytest.importorskip("typer")
cli = pytest.importorskip("attackmap.cli")

CLI_MD = Path(__file__).resolve().parents[1] / "docs" / "cli.md"
COMMANDS = ("analyze", "suggest", "bench")
OPTION = re.compile(r"(?<![\w-])(--[a-z][a-z0-9-]*)")
ROW = re.compile(r"^\|\s*`(--[a-z][a-z0-9-]*)(?:\s*\{([^}`]*)\})?[^`]*`[^|]*\|(.*)\|\s*$", re.M)
DEFAULT = re.compile(r"\(default:?\s*`([^`]+)`")

# Options whose accepted values core validates itself (not click Choices).
CHOICES = {
    "--progress-format": lambda: cli.PROGRESS_FORMATS,
    "--format": lambda: tuple(cli.OUTPUT_FORMATS),
    "--llm-provider": lambda: cli.LLM_PROVIDERS,
    "--llm-speed": lambda: cli.LLM_SPEEDS,
    "--llm-effort": lambda: cli.LLM_EFFORTS,
    "--llm-backend": lambda: cli.LLM_BACKENDS,
}


def _section(name: str) -> str:
    text = CLI_MD.read_text(encoding="utf-8")
    match = re.search(rf"^## `{name}`\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    assert match, f"docs/cli.md has no '## `{name}`' section"
    return match.group(1)


def _params(name: str) -> dict[str, object]:
    command = typer.main.get_command(cli.app).commands[name]
    params: dict[str, object] = {}
    for param in command.params:
        if getattr(param, "hidden", False):
            continue
        for opt in [*getattr(param, "opts", []), *getattr(param, "secondary_opts", [])]:
            if opt.startswith("--") and opt != "--help":
                params[opt] = param
    return params


@pytest.mark.parametrize("name", COMMANDS)
def test_every_option_is_documented_and_no_stale_ones(name: str) -> None:
    real = set(_params(name))
    documented = set(OPTION.findall(_section(name)))
    assert not real - documented, f"undocumented `{name}` options: {sorted(real - documented)}"
    assert not documented - real, f"`{name}` section names options the CLI doesn't have: {sorted(documented - real)}"


@pytest.mark.parametrize("name", COMMANDS)
def test_documented_choices_and_defaults_match(name: str) -> None:
    params = _params(name)
    problems = []
    for opt, choices, description in ROW.findall(_section(name)):
        if opt not in params:
            continue
        if choices:
            documented = tuple(c.strip() for c in choices.split(","))
            actual = CHOICES[opt]() if opt in CHOICES else tuple(getattr(params[opt].type, "choices", ()))
            if actual and set(documented) != set(actual):
                problems.append(f"{opt}: docs list {{{','.join(documented)}}}, CLI accepts {{{','.join(actual)}}}")
        default = DEFAULT.search(description)
        if default:
            actual_default = getattr(params[opt], "default", None)
            # None means "resolved later" (e.g. --llm-effort → high); only
            # compare defaults the CLI actually declares.
            if actual_default is not None and str(actual_default) != default.group(1):
                problems.append(f"{opt}: docs say default `{default.group(1)}`, CLI default is {actual_default!r}")
    assert not problems, "\n".join(problems)
