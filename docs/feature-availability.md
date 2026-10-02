# Feature availability

The first `attackmap` CLI release that has each feature. An older CLI rejects
a flag it doesn't know with a usage error, so if a flag fails, compare against
this table and upgrade (`brew upgrade attackmap`, or
`pipx upgrade attackmap`). Check your version with `attackmap --version`
(0.4.30+); on older releases use `pip show attackmap`.

Versions come from the core
[CHANGELOG](https://github.com/mlaify/AttackMap/blob/main/CHANGELOG.md). The
**macOS app** column marks features the [macOS app](gui.md) uses: it detects
them from `attackmap analyze --help` and hides or drops what your CLI lacks.

## Released

| Feature | Command / flag | Minimum CLI | macOS app |
|---|---|---|---|
| AI narrative review | `--llm` | 0.1.0 | ✓ |
| SARIF output | `attackmap-report.sarif` (always written) | 0.2.0 | |
| Dependency CVE lookup (OSV.dev) | `--cve` | 0.2.0 | ✓ |
| Baseline diff and PR gate | `--baseline`, `--diff-output`, `--fail-on-new-high` | 0.2.0 | |
| Plugin recommendations | `attackmap suggest [--install] [--yes] [--show-installed]` | 0.2.0 | |
| Vulnerability-hypothesis hunt | `--hunt` | 0.3.0 | ✓ |
| Hunt verification | `--hunt --verify` | 0.4.0 | ✓ |
| Remediation suggestions | `--remediate` | 0.4.0 | ✓ |
| PR summary comment | `--pr-comment` | 0.4.0 | |
| NDJSON progress stream | `--progress-format json` | 0.4.1 | ✓ |
| OpenAI / Codex provider | `--llm-provider openai` | 0.4.3 | ✓ |
| Fast mode | `--llm-speed fast` | 0.4.3 | ✓ |
| Installed modules as JSON | `attackmap modules --json` | 0.4.4 | ✓ |
| Suppressions (baseline file, inline `attackmap:ignore`) | `--no-suppress`, `--suppress-file` | 0.4.7 | ✓ |
| Triage | `--triage` | 0.4.15 | ✓ |
| Verify jury: skeptic votes | `--verify-votes` | 0.4.16 | ✓ |
| Verify jury: failure-mode lenses | `--hunt-lenses` | 0.4.17 | ✓ |
| Verify jury: multi-round hunt and token budget | `--hunt-rounds`, `--hunt-budget` | 0.4.18 | ✓ |
| Recall mode | `--recall` | 0.4.20 | ✓ |
| Cross-repo / fleet scan | `attackmap analyze <repoA> <repoB> …` | 0.4.22 | ✓ |
| Detection benchmark | `attackmap bench` | 0.4.28 | |
| Version flag | `attackmap --version` | 0.4.30 | |
| Output filtering | `--format {all,json,markdown}` (accepted but ignored before 0.4.30) | 0.4.30 | ✓ |
| Pinned plugin auto-install | `--install-missing` | 0.4.31 | |
| Official plugins only | `--trusted-analyzers-only` | 0.4.31 | |

The macOS app treats the whole verify jury as one capability and enables it
when the CLI has `--verify-votes` (0.4.16). `--hunt-lenses`, `--hunt-rounds`
and `--hunt-budget` need 0.4.17 and 0.4.18, so on a 0.4.16 CLI leave those
at their defaults.

## Unreleased (on `main`, after 0.4.31)

These are in the changelog's `[Unreleased]` section and ship in the first
release after 0.4.31.

| Feature | Command / flag |
|---|---|
| Analyzer failure isolation; fail fast on request | `scan.analyzer_errors`; `--strict-analyzers` |
| Analyzer run order by `priority`; opt-in analyzers and the "Opt-in analyzers match this repo but were not run" hint | `enabled_by_default=False`, `-m` |
| Shared plugin walker | `attackmap.sdk.fs` (see [Analyzer SDK](sdk.md)) |
| Stable rule ids | `attackmap rules [--json]` |
| Trusted suppressions | `--suppress-from-ref`, `--allow-pr-suppressions` |
| Suppression expiry gate | `--strict-suppressions` |
| Newly-suppressed gate | `--fail-on-new-suppression` |
