# CI & pull requests

AttackMap is built to run in CI and speak up on pull requests.

## GitHub Action

The repo ships a composite action (`action.yml`) that runs a scan, emits SARIF
(so findings show up in the GitHub Security tab), and can post a PR summary.

```yaml
name: AttackMap
on: [pull_request]
jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: mlaify/AttackMap@v0            # pin to a release tag in practice
        with:
          path: .
```

## PR summary bot

`--pr-comment <file>` writes a Markdown summary — the baseline diff plus top
exploitability — for a bot to post as a PR comment:

```bash
attackmap analyze . --pr-comment pr-comment.md
```

## Diff gating

Fail the build when a PR introduces new high-severity findings, comparing
against a baseline report from the target branch:

```bash
attackmap analyze . \
  --baseline baseline/attackmap-report.json \
  --diff-output attackmap-diff.md \
  --fail-on-new-high
```

Because findings carry stable IDs, the diff is reliable across runs — you gate
on *new* risk, not on the total count. See [Scanning & output](scanning.md).

## Suppressing findings

Silence a residual false positive **without going blind to new signal**. Two
mechanisms, both honored across every pass. Suppressed findings are *not
dropped*: they're excluded from `--fail-on-new-high` and the console summary,
but kept in `attackmap-report.json` under `suppressed_findings` (with reasons)
and marked with a SARIF `suppressions` array so GitHub Code Scanning shows them
as **suppressed**, not active. Suppression counts print in the run summary.

### Repo-level baseline

Drop a `.attackmap-suppress.yaml` at the repo root:

```yaml
version: 1
suppress:
  # by stable finding id (the 16-hex id in attackmap-report.json)
  - id: 1a2b3c4d5e6f7a8b
    reason: accepted risk, tracked in JIRA-1234

  # by rule (a slug of the finding title — the same string as the SARIF ruleId),
  # optionally scoped to paths
  - rule: hard-coded-secret-literals-were-found-in-source-or-config
    reason: example keys in docs, never shipped
    paths: ["docs/**", "examples/**"]

  # by path only — any finding whose evidence is *entirely* within these globs
  - path: "vendor/**"
    reason: third-party code, out of scope
```

Every entry needs a `reason`. A `path` selector matches a finding only when
**every** file its evidence cites falls under the glob, so a finding that also
touches live code is never silently hidden. `*` spans path separators
(`vendor/*` covers the whole subtree); `**` is accepted as a synonym.

### Inline directives

A comment on (or above) the flagged line, in any language:

```python
API_KEY = "AKIA…"  # attackmap:ignore[hard-coded-secret-literals-were-found-in-source-or-config] staging only
```

```javascript
const token = "…"; // attackmap:ignore[<rule-id>] rotated in prod
```

The bracketed rule is optional — a bare `# attackmap:ignore` matches any rule.
Because findings aggregate every site of an issue type, an inline directive
suppresses a finding only when *all* of its cited files carry a matching
directive (or are covered by a baseline `path` glob); for a multi-file finding,
prefer a baseline entry.

### Flags

| Flag | Effect |
| --- | --- |
| `--no-suppress` | Ignore all suppressions — a full, unfiltered audit. |
| `--suppress-file PATH` | Use a baseline elsewhere than the repo-root default. |

!!! tip "Finding the rule id"
    The `rule` key is the slug you see as the `ruleId` in SARIF / the GitHub
    Security tab, and the `id` is the 16-hex value in each finding of
    `attackmap-report.json`. Copy either straight from a prior run.
