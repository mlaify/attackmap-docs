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
