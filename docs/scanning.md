# Scanning & output

## The analyze command

```bash
attackmap analyze <path> [options]
```

`<path>` is the repository root. By default AttackMap resolves which analyzers
to run from the languages it finds, writes `all` output formats, and shows a
live progress bar when stderr is a terminal.

Common options (full list in the [CLI reference](cli.md)):

- `--output <dir>` — where artifacts are written (default: current directory).
- `--format {all,markdown,json}` — which output formats to emit.
- `--module <name>` — restrict to specific analyzers (repeatable). See [Analyzers](analyzers.md).
- `--cve` — cross-reference dependencies against OSV.dev.
- `--progress-format {auto,json,none}` — `json` emits newline-delimited progress events on stderr for tool/GUI front-ends.

## Output artifacts

A scan writes a monolithic report plus focused sub-artifacts:

- **`attackmap-report.json`** — the canonical structured report. Contains findings (with stable IDs), attack surfaces, attack paths, exploitability scores, dependencies, and taint chains.
- **`defensive-review.md`** and the other Markdown sub-reports — human-readable views.
- **LLM artifacts** (only with the AI modes) — `defensive-review-llm.md`, `vulnerability-hypotheses.md`, `remediation.md`, each with a `.meta.json` recording the backend, model, and token usage.

Findings carry **stable IDs**, which is what makes baseline diffing reliable.

## Baseline diffing & PR gating

Compare a fresh scan against a prior report to see what changed:

```bash
attackmap analyze . \
  --baseline prev/attackmap-report.json \
  --diff-output reports/attackmap-diff.md \
  --fail-on-new-high
```

- `--baseline <report.json>` — a prior `attackmap-report.json` to diff against.
- `--diff-output <file>` — where to write the Markdown diff (new / persisted / resolved).
- `--fail-on-new-high` — exit non-zero if the diff introduces any new HIGH-severity finding. Requires `--baseline`.

`--pr-comment <file>` writes a Markdown PR summary (diff + top exploitability)
for a bot to post. See [CI & pull requests](ci.md).
