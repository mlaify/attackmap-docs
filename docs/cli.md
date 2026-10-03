# CLI reference

Run `attackmap --help` or `attackmap <command> --help` for the authoritative,
version-specific list. This page summarizes the common surface.

`attackmap --version` prints the installed version (0.4.30+). Flags were
added over many releases; [Feature availability](feature-availability.md) lists
the minimum CLI version for each.

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
| `--output <dir>` / `-o` | Directory for artifacts (default: `reports`). |
| `--format {all,markdown,json}` | Which artifacts to write (default `all`). `json` = `attackmap-report.json`, `attackmap-report.sarif`, `defensive-review.json`, `review-context-pack.json` (fleet: `fleet-summary.json`). `markdown` = the `*.md` reports plus `*.dot` diagrams (fleet: `fleet-summary.md`, `fleet-graph.md`). Opt-in outputs (baseline diff, PR comment, LLM passes) are always written. Honored from 0.4.30; earlier versions always wrote everything. |
| `--progress-format {auto,tty,json,none}` | Progress reporting (default `auto`): `auto` = a bar when stderr is a terminal, `tty` = always the bar, `json` = NDJSON events on stderr, `none` = off. |
| `--no-progress` | Disable the progress bar (equivalent to `none`). |

### Analyzers

| Option | Description |
| --- | --- |
| `--module <name>` / `-m` | Run only the named analyzer(s); repeatable. Also the only way to run an opt-in analyzer (see below). A missing official analyzer is installed, pinned to the commit in AttackMap's plugin lock, only with `--install-missing` or after an interactive confirmation. An unknown name that isn't an official analyzer is an error. |
| `--install-missing` | Install missing official analyzers named by `--module` without prompting (0.4.31+). |
| `--trusted-analyzers-only` | Load only official AttackMap analyzer plugins and skip any other installed package that registers one. Also `ATTACKMAP_TRUSTED_ANALYZERS_ONLY=1` (0.4.31+). |
| `--strict-analyzers` | Fail fast if an analyzer raises or returns an invalid result, instead of skipping it and listing it under `scan.analyzer_errors`. For plugin development and CI (after 0.4.31). |

Without `--module`, every installed analyzer whose `detect()` matches the repo
runs, in `(priority, name)` order, except **opt-in** analyzers
(`enabled_by_default=False`). When an opt-in analyzer matches but isn't
selected, the CLI prints a hint on stderr:

```text
Opt-in analyzers match this repo but were not run: omeka-s. Enable with -m omeka-s.
```

If an analyzer fails, the scan continues without it. The console prints
`Analyzer '<name>' failed and was skipped: …` and `attackmap-report.json` lists
it under `scan.analyzer_errors`. Opt-in handling, run order and this failure
isolation ship in the first release after 0.4.31; earlier releases run every
matching analyzer and abort on the first failure.

### Dependencies

| Option | Description |
| --- | --- |
| `--cve` | Cross-reference the SBOM against OSV.dev (network; 24h cache). |
| `--secrets-history N` | Also scan the patches of the last N commits (all refs) for hard-coded secrets, reporting the introducing commit and whether each is still in `HEAD`. Off by default (`0`); capped at 5000 commits and 64 MB of patch text. Git runs with hooks, pagers, external diff and textconv disabled. |

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
| `--suppress-from-ref <ref>` | Trust only suppressions that already exist at this git ref, such as the PR's base branch. Suppress-file entries and inline directives added since then are reported as *pending* and not applied (after 0.4.31). |
| `--allow-pr-suppressions` | With `--suppress-from-ref`, apply suppressions added since the ref anyway. They are still listed (after 0.4.31). |
| `--strict-suppressions` | Exit 2 if any suppression has expired (past its `expires:` / `until=` date) (after 0.4.31). |
| `--fail-on-new-suppression` | Exit non-zero if a finding that was active in the baseline is suppressed in this run, for example by a suppression the PR added. Needs `--baseline` (after 0.4.31). |

See [Suppressing findings](ci.md#suppressing-findings) for the suppression file
format and inline `attackmap:ignore` directives.

## `suggest`

```bash
attackmap suggest [path] [--install] [--yes] [--show-installed]
```

Inspects a repository's manifests, file extensions and framework markers, and
recommends the official analyzer plugins that fit it (default path `.`). Each
missing plugin is listed with what matched and the exact `pip install` command,
pinned to the commit in AttackMap's plugin lock.

| Option | Description |
| --- | --- |
| `--install` | After printing, offer to `pip install` the missing recommended plugins. Asks for confirmation (default No). This is the supported way to install plugins for a repo. |
| `--yes` / `-y` | With `--install`, skip the confirmation prompt (for scripts). |
| `--show-installed` | Also list recommended plugins that are already installed, marked `(installed)`. |

`--install` refuses to install into a system (non-virtualenv) Python unless
`ATTACKMAP_ALLOW_SYSTEM_INSTALL=1` is set. Install AttackMap with Homebrew,
pipx or a venv so plugins land next to it. The command exits 1 if the path
isn't a directory, you decline the prompt, or a `pip install` fails.

## `bench`

```bash
attackmap bench [--benchmark <manifest>] [--root <dir>] [-o <dir>] [--fail-under <0-1>]
```

Scores AttackMap's findings against a labeled ground-truth corpus and prints
precision, recall and F1 per detector class. It's a contributor and CI tool:
the default manifest, `evals/benchmark/benchmark.json`, ships in a checkout of
the [AttackMap repo](https://github.com/mlaify/AttackMap), not in the installed
package, so run it from the repo root. See
[docs/benchmark.md](https://github.com/mlaify/AttackMap/blob/main/docs/benchmark.md)
for the corpus format.

| Option | Description |
| --- | --- |
| `--benchmark <path>` | Benchmark manifest (default `evals/benchmark/benchmark.json`). |
| `--root <dir>` | Directory the manifest's case paths are relative to (default `.`). |
| `--output <dir>` / `-o` | Also write `benchmark-results.md` and `benchmark-results.json` here. Results are always printed to stdout. |
| `--fail-under <float>` | Exit 1 if any scored detector class's precision or recall is below this value (0–1). For CI regression gating. |

Exit codes: 2 if the manifest isn't found, 1 if any case failed to scan or the
`--fail-under` gate fails, 0 otherwise.

## Other commands

| Command | Description |
| --- | --- |
| `attackmap modules [--json]` | List installed analyzer modules. |
| `attackmap rules [--json]` | List every core detector's stable rule id, the value for suppress `rule:` and `attackmap:ignore[...]` (after 0.4.31). |
