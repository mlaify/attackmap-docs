# CLI reference

Run `attackmap --help` or `attackmap <command> --help` for the authoritative,
version-specific list. This page summarizes the common surface.

## `analyze`

```bash
attackmap analyze <path> [options]
```

### Output

| Option | Description |
| --- | --- |
| `--output <dir>` | Directory for artifacts (default: current dir). |
| `--format {all,markdown,json}` | Output formats to emit (default `all`). |
| `--progress-format {auto,json,none}` | Progress reporting; `json` = NDJSON events on stderr. |
| `--no-progress` | Disable the progress bar (equivalent to `none`). |

### Analyzers

| Option | Description |
| --- | --- |
| `--module <name>` / `-m` | Restrict to specific analyzer(s); repeatable. Missing official analyzers auto-install. |

### Dependencies

| Option | Description |
| --- | --- |
| `--cve` | Cross-reference the SBOM against OSV.dev (network; 24h cache). |

### AI review

| Option | Description |
| --- | --- |
| `--llm` | Narrative defensive review. |
| `--hunt` | Ranked vulnerability-hypothesis hunt. |
| `--verify` | With `--hunt`: adjudicate each lead against source. |
| `--remediate` | Review-first remediation suggestions. |
| `--llm-provider {claude,openai}` | Provider (default `claude`). |
| `--llm-model <id>` | Model ID (pass-through). Defaults: `claude-opus-4-8` / `gpt-5-codex`. |
| `--llm-effort {low,medium,high,xhigh,max}` | Reasoning effort (default `high`). |
| `--llm-backend {auto,api,cli}` | Force a backend (default `auto`). |
| `--llm-speed {standard,fast}` | Fast mode (Claude Opus 4.8/4.7, API backend). |

See [AI review](llm.md) for details and credential resolution.

### Diff & CI

| Option | Description |
| --- | --- |
| `--baseline <report.json>` | Prior report to diff against. |
| `--diff-output <file>` | Where to write the Markdown diff. |
| `--fail-on-new-high` | Exit non-zero on new HIGH findings (needs `--baseline`). |
| `--pr-comment <file>` | Write a Markdown PR summary comment. |

## Other commands

| Command | Description |
| --- | --- |
| `attackmap modules [--json]` | List installed analyzer modules. |
| `attackmap suggest <path>` | Suggest which analyzers fit a repository. |
