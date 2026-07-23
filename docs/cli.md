# CLI reference

Run `attackmap --help` or `attackmap <command> --help` for the authoritative,
version-specific list. This page summarizes the common surface.

## `analyze`

```bash
attackmap analyze <path> [options]
attackmap analyze <repoA> <repoB> … [options]   # multi-repo fleet scan
```

Pass two or more paths for a **fleet scan**: each repo is analyzed into its own
`<output>/<repo>/` directory and a `fleet-summary.md` / `.json` (plus
`fleet-graph.md`) indexes the run with cross-repo links, cross-boundary flows,
trust-assumption gaps, and cross-repo anomalies. See
[Cross-repo / fleet analysis](scanning.md#cross-repo-fleet-analysis). Single-repo
invocation is unchanged; the single-repo-only options below (diff, `--llm`,
`--hunt`, `--remediate`, `--triage`) aren't yet fleet-aware.

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

### Recall / discovery

| Option | Description |
| --- | --- |
| `--recall` | Widen taint discovery (deeper import-hop depth, capability-reach enumeration). The extra reach is marked **speculative**, kept out of `--fail-on-new-high`, and left for `--hunt --verify` to adjudicate. See [Recall mode](scanning.md#recall-mode). |

### AI review

| Option | Description |
| --- | --- |
| `--llm` | Narrative defensive review. |
| `--hunt` | Ranked vulnerability-hypothesis hunt. |
| `--verify` | With `--hunt`: adjudicate each lead against source. |
| `--verify-votes <n>` | With `--verify`: majority vote of N independent skeptics (default 3; 1 = single pass). |
| `--hunt-lenses <n>` | With `--verify`: N failure-mode-specialist generation passes, deduped, then verified. |
| `--hunt-rounds <n>` | With `--verify`: loop-until-dry generation; a completeness critic seeds each round. |
| `--hunt-budget <tokens>` | With `--verify`: cap total hunt output tokens across rounds. |
| `--triage` | Cluster, de-duplicate, and rank existing findings into a shortlist (deterministic fallback when no LLM). |
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
| `--no-suppress` | Ignore all suppressions (baseline + inline) for a full audit. |
| `--suppress-file <file>` | Override the `.attackmap-suppress.yaml` location. |

See [Suppressing findings](ci.md#suppressing-findings) for the suppression file
format and inline `attackmap:ignore` directives.

## Other commands

| Command | Description |
| --- | --- |
| `attackmap modules [--json]` | List installed analyzer modules. |
| `attackmap suggest <path>` | Suggest which analyzers fit a repository. |
